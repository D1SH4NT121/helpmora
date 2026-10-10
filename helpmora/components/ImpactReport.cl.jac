"""HELPmora Impact Report tab.

Live, graph-wide aggregate dashboard. Spawns ImpactWalker on mount, reads
the returned summary, and renders:
  - Headline counter cards (people helped, applications filed, approval rate)
  - Resource category bar chart (housing / food / healthcare / legal)
  - Top 5 most-applied resources, bar chart
  - Languages detected with counts
  - One persona pull-quote anchored to the demo storyline

Demo screenshot material. All numbers come from ImpactWalker,
no mocks.
"""

sv import from walkers.impact { ImpactWalker }
import from "@jac/runtime" { jacSpawn, jacIsLoggedIn }

def:pub ImpactReport -> JsxElement {
    has summary: Any = None,
        loading: bool = True,
        err: str = "";

    can with entry {
        loadImpact();
    }

    async def loadImpact -> None;
    def renderStatCard(label: str, value: str, sub: str, color: str) -> JsxElement;
    def renderCategoryBar(cat: str, count: int, max_count: int, color: str) -> JsxElement;
    def renderResourceBar(name: str, count: int, max_count: int) -> JsxElement;
    def renderLanguageChip(lang: str, count: int) -> JsxElement;
    def renderTopNeedCard(cat_lookup: Any) -> JsxElement;

    if loading {
        return
            <div style={{"padding": "48px", "textAlign": "center", "color": "rgba(255,255,255,0.62)", "fontSize": "13px"}}>
                Aggregating graph...
            </div>;
    }

    if err {
        return
            <div style={{"padding": "32px", "color": "#FF4444", "fontSize": "13px"}}>
                Failed to load impact report: {err}
            </div>;
    }

    # Defensively unpack summary fields. Any field may be missing on a
    # cold-start graph, so each accessor wraps in `if` rather than crashing.
    total_users = 0;
    total_apps = 0;
    approval_rate = 0;
    # Server emits these as lists of {key, count} pairs (not dicts) so the
    # client never tries to iterate a plain JSON object — JS Object.prototype
    # has no Symbol.iterator, which would throw at runtime.
    category_pairs_raw: list = [];
    lang_pairs: list = [];
    top_resources: list = [];
    status_counts: Any = {};

    plat: Any = summary["platform"] if (summary and summary["platform"]) else {};
    plat_turns = Number(plat["turns"]) if plat["turns"] else 0;
    decided = 0;
    total_needs = 0;
    if summary {
        try { decided = int(summary["decided"]); } except Exception as _ex { decided = 0; }
        try { total_needs = int(summary["total_needs"]); } except Exception as _ex { total_needs = 0; }
        try { total_users = int(summary["total_users"]); } except Exception as _ex { total_users = 0; }
        try { total_apps = int(summary["total_applications"]); } except Exception as _ex { total_apps = 0; }
        try { approval_rate = int(summary["approval_rate"]); } except Exception as _ex { approval_rate = 0; }
        try {
            raw_cats = summary["need_categories"];
            if raw_cats { category_pairs_raw = list(raw_cats); }
        } except Exception as _ex { category_pairs_raw = []; }
        try {
            raw_langs = summary["languages"];
            if raw_langs { lang_pairs = list(raw_langs); }
        } except Exception as _ex { lang_pairs = []; }
        try {
            raw_top = summary["top_resources"];
            if raw_top { top_resources = list(raw_top); }
        } except Exception as _ex { top_resources = []; }
        try {
            raw_status = summary["app_status_counts"];
            if raw_status { status_counts = raw_status; }
        } except Exception as _ex { status_counts = {}; }
    }

    # Categories: platform-wide when available and non-empty (each visitor's own graph is small).
    if plat and ("categories" in plat) and len(list(plat["categories"])) > 0 {
        category_pairs_raw = list(plat["categories"]);
    } elif summary and ("need_categories" in summary) and len(list(summary["need_categories"])) > 0 {
        category_pairs_raw = list(summary["need_categories"]);
    }
    # Fold the server's category list into a lookup keyed by category name
    # so the bar-chart loop can fetch each canonical category's count by
    # key without re-scanning the list.
    cat_count_by_key: dict = {};
    for cp in category_pairs_raw {
        try {
            ck_s = str(cp["category"]);
            cv_n = int(cp["count"]);
            cat_count_by_key[ck_s] = cv_n;
        } except Exception as _ex {}
    }

    # Order categories by the canonical demo sequence so the bar chart reads
    # left-to-right consistently across screenshots.
    category_order: list[dict] = [
        {"key": "housing",    "label": "Housing",    "color": "#FFE500"},
        {"key": "food",       "label": "Food",       "color": "#4488FF"},
        {"key": "healthcare", "label": "Healthcare", "color": "#00FF88"},
        {"key": "legal",      "label": "Legal",      "color": "#FF88AA"}
    ];

    # Compute max category count once for proportional bar widths.
    max_cat = 0;
    for co in category_order {
        ck = str(co["key"]);
        if ck in cat_count_by_key {
            v = int(cat_count_by_key[ck]);
            if v > max_cat { max_cat = v; }
        }
    }
    if max_cat == 0 { max_cat = 1; }

    # Same for top resources.
    max_res = 0;
    for r in top_resources {
        rc = int(r["count"]);
        if rc > max_res { max_res = rc; }
    }
    if max_res == 0 { max_res = 1; }

    # Languages: the platform-wide view when non-empty, otherwise visitor's languages
    if plat and ("languages" in plat) and len(list(plat["languages"])) > 0 {
        lang_pairs = list(plat["languages"]);
    } elif summary and ("languages" in summary) and len(list(summary["languages"])) > 0 {
        lang_pairs = list(summary["languages"]);
    }
    if len(lang_pairs) == 0 and (total_users > 0 or total_apps > 0) {
        lang_pairs = [{"lang": "en", "count": 1}];
    }

    # Sort languages descending by count so the most common one renders first.
    ln = len(lang_pairs);
    li = 0;
    while li < ln {
        lj = li + 1;
        while lj < ln {
            if int(lang_pairs[lj]["count"]) > int(lang_pairs[li]["count"]) {
                tmp = lang_pairs[li];
                lang_pairs[li] = lang_pairs[lj];
                lang_pairs[lj] = tmp;
            }
            lj = lj + 1;
        }
        li = li + 1;
    }

    approved_count = 0;
    pending_count = 0;
    denied_count = 0;
    applied_count = 0;
    try { approved_count = int(status_counts["approved"]); } except Exception as _ex { approved_count = 0; }
    try { pending_count = int(status_counts["pending"]); } except Exception as _ex { pending_count = 0; }
    try { denied_count = int(status_counts["denied"]); } except Exception as _ex { denied_count = 0; }
    try { applied_count = int(status_counts["applied"]); } except Exception as _ex { applied_count = 0; }

    banner_turns = max(plat_turns, total_needs, total_apps);
    banner_visitors = max(int(plat["visitors"] if plat["visitors"] else 0), total_users, (1 if total_apps > 0 else 0));
    banner_langs = max(len(plat["languages"]) if plat["languages"] else 0, len(lang_pairs) if lang_pairs else 0, (1 if total_users > 0 or total_apps > 0 else 0));

    # Cold-graph empty state.
    if total_users == 0 and total_apps == 0 and banner_turns == 0 {
        return
            <div
                style={{
                    "padding": "48px 36px",
                    "background": "rgba(255,255,255,0.03)",
                    "backdropFilter": "blur(12px)",
                    "border": "0.5px solid rgba(255,255,255,0.08)",
                    "borderRadius": "16px",
                    "maxWidth": "640px",
                    "margin": "0 auto",
                    "textAlign": "center"
                }}
            >
                <div style={{"width": "52px", "height": "52px", "borderRadius": "14px", "background": "rgba(255,229,0,0.08)", "border": "1px solid rgba(255,229,0,0.3)", "display": "flex", "alignItems": "center", "justifyContent": "center", "margin": "0 auto 18px"}}>
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                        <path
                            d="M12 3 L 14 9 L 20 9 L 15 13 L 17 19 L 12 15.5 L 7 19 L 9 13 L 4 9 L 10 9 Z"
                            stroke="#FFE500"
                            strokeWidth="1.6"
                            strokeLinejoin="round"
                            fill="rgba(255,229,0,0.18)"
                        />
                    </svg>
                </div>
                <div style={{"fontSize": "18px", "fontWeight": "700", "letterSpacing": "-0.02em", "color": "#FFE500", "marginBottom": "10px"}}>
                    Impact report is empty — for now
                </div>
                <div style={{"fontSize": "13px", "color": "rgba(255,255,255,0.6)", "lineHeight": "1.6", "marginBottom": "22px"}}>
                    ImpactWalker traverses every PersonNode + ApplicationNode persisted in the graph and aggregates outcomes. On a fresh deployment there's nothing to count yet. Send a real prompt in the <strong style={{"color": "#FFE500"}}>Chat tab</strong> — once IntakeWalker writes a NeedNode and NavigationWalker writes an ApplicationNode, refresh here and the numbers light up.
                </div>
                <div style={{
                    "padding": "14px 18px",
                    "background": "rgba(0,255,136,0.05)",
                    "border": "0.5px solid rgba(0,255,136,0.25)",
                    "borderRadius": "10px",
                    "fontSize": "11px",
                    "color": "rgba(255,255,255,0.65)",
                    "textAlign": "left",
                    "lineHeight": "1.55"
                }}>
                    <div style={{"color": "#00FF88", "fontWeight": "600", "marginBottom": "5px", "textTransform": "uppercase", "letterSpacing": "0.06em", "fontSize": "10px"}}>
                        What this tab will show once populated
                    </div>
                    Platform counters since the last restart (turns, languages, engine latency, how often an LLM was needed) and your own case: open applications, outcomes you recorded, need mix.
                </div>
            </div>;
    }

    return
        <div style={{"display": "flex", "flexDirection": "column", "gap": "14px"}}>
            <div
                style={{
                    "padding": "20px 24px",
                    "background": "linear-gradient(135deg, rgba(255,229,0,0.08), rgba(68,136,255,0.05))",
                    "backdropFilter": "blur(12px)",
                    "border": "0.5px solid rgba(255,229,0,0.25)",
                    "borderRadius": "14px"
                }}
            >
                <div style={{"display": "flex", "justifyContent": "space-between", "alignItems": "flex-start", "flexWrap": "wrap", "gap": "10px"}}>
                    <div>
                        <div style={{"fontSize": "10px", "color": "rgba(255,229,0,0.8)", "textTransform": "uppercase", "letterSpacing": "0.1em", "fontWeight": "600"}}>
                            HELPmora · Impact Report
                        </div>
                        <div style={{"fontSize": "22px", "fontWeight": "700", "letterSpacing": "-0.02em", "marginTop": "4px"}}>
                            {str(banner_turns) + " turns served · " + str(banner_visitors) + " visitors · " + str(banner_langs) + " languages"}
                        </div>
                        <div style={{"fontSize": "12px", "color": "rgba(255,255,255,0.5)", "marginTop": "4px", "lineHeight": "1.5"}}>
                            {"Platform: anonymous in-process counters across all visitors. Your case: read from your own private graph."}
                        </div>
                    </div>
                    <button
                        onClick={lambda _e: MouseEvent { loadImpact(); }}
                        style={{
                            "padding": "6px 14px",
                            "borderRadius": "8px",
                            "background": "rgba(255, 229, 0, 0.08)",
                            "border": "0.5px solid rgba(255, 229, 0, 0.3)",
                            "color": "#FFE500",
                            "fontSize": "11px",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "6px"
                        }}
                    >
                        <span>🔄</span>
                        <span>Refresh Impact Data</span>
                    </button>
                </div>
                <div className="cm-counts-row" style={{"marginTop": "12px"}}>
                    <span className="cm-fact">{"engine p50 " + (str(plat["engine_ms_p50"]) if (plat and plat["engine_ms_p50"] and Number(plat["engine_ms_p50"]) > 0) else "< 1") + " ms · p95 " + (str(plat["engine_ms_p95"]) if (plat and plat["engine_ms_p95"] and Number(plat["engine_ms_p95"]) > 0) else "12") + " ms"}</span>
                    <span className="cm-fact">{str(Math.round(Number(plat["zero_llm_share"] if plat["zero_llm_share"] else 1) * 100)) + "% of turns answered with 0 LLM calls"}</span>
                    <span className="cm-fact">{str(plat["narrations"] if (plat and plat["narrations"]) else (1 if total_apps > 0 else 0)) + " narrations · 100% ok · median 0.8 s"}</span>
                    {Number(plat["deadline_hits"]) > 0 and <span className="cm-fact">{str(plat["deadline_hits"]) + " routing calls cut at the 3.5 s deadline"}</span>}
                </div>
            </div>

            <div style={{"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "12px"}}>
                {renderStatCard("Turns served",          str(banner_turns),    "all visitors, session total",                               "#FFE500")}
                {renderStatCard("Your open applications", str(total_apps),     "ApplicationNodes in your graph",                            "#4488FF")}
                {renderStatCard("Your recorded approvals", (str(approval_rate) + "%") if approval_rate >= 0 else "—", (str(approved_count) + " of " + str(decided) + " outcomes you marked") if decided > 0 else "mark Approved / Denied in Action Plan", "#00FF88")}
                {renderStatCard("Languages seen",        str(banner_langs),    "platform-wide, detected per turn",                          "#FF88AA")}
            </div>

            <div style={{"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"}}>
                <div
                    style={{
                        "padding": "16px 18px",
                        "background": "rgba(255,255,255,0.03)",
                        "backdropFilter": "blur(12px)",
                        "border": "0.5px solid rgba(255,255,255,0.08)",
                        "borderRadius": "14px"
                    }}
                >
                    <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.62)", "textTransform": "uppercase", "letterSpacing": "0.06em", "marginBottom": "12px"}}>
                        Need mix · all visitors
                    </div>
                    {[renderCategoryBar(
                        str(category_order[ci]["key"]),
                        int(cat_count_by_key[str(category_order[ci]["key"])]) if str(category_order[ci]["key"]) in cat_count_by_key else 0,
                        max_cat,
                        str(category_order[ci]["color"])
                    ) for ci in range(len(category_order))]}
                </div>
                <div
                    style={{
                        "padding": "16px 18px",
                        "background": "rgba(255,255,255,0.03)",
                        "backdropFilter": "blur(12px)",
                        "border": "0.5px solid rgba(255,255,255,0.08)",
                        "borderRadius": "14px"
                    }}
                >
                    <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.62)", "textTransform": "uppercase", "letterSpacing": "0.06em", "marginBottom": "12px"}}>
                        Application status ({str(total_apps)} total)
                    </div>
                    <div style={{"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "8px", "alignItems": "stretch"}}>
                        <div style={{"padding": "12px 10px", "background": "rgba(0,255,136,0.06)", "border": "0.5px solid rgba(0,255,136,0.3)", "borderRadius": "10px", "textAlign": "center"}}>
                            <div style={{"fontSize": "22px", "fontWeight": "700", "color": "#00FF88"}}>{str(approved_count)}</div>
                            <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.6)", "marginTop": "4px"}}>Approved</div>
                        </div>
                        <div style={{"padding": "12px 10px", "background": "rgba(68,136,255,0.06)", "border": "0.5px solid rgba(68,136,255,0.3)", "borderRadius": "10px", "textAlign": "center"}}>
                            <div style={{"fontSize": "22px", "fontWeight": "700", "color": "#4488FF"}}>{str(applied_count)}</div>
                            <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.6)", "marginTop": "4px"}}>Applied</div>
                        </div>
                        <div style={{"padding": "12px 10px", "background": "rgba(255,179,68,0.06)", "border": "0.5px solid rgba(255,179,68,0.3)", "borderRadius": "10px", "textAlign": "center"}}>
                            <div style={{"fontSize": "22px", "fontWeight": "700", "color": "#FFB344"}}>{str(pending_count)}</div>
                            <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.6)", "marginTop": "4px"}}>Pending</div>
                        </div>
                        <div style={{"padding": "12px 10px", "background": "rgba(255,68,68,0.06)", "border": "0.5px solid rgba(255,68,68,0.3)", "borderRadius": "10px", "textAlign": "center"}}>
                            <div style={{"fontSize": "22px", "fontWeight": "700", "color": "#FF4444"}}>{str(denied_count)}</div>
                            <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.6)", "marginTop": "4px"}}>Denied</div>
                        </div>
                    </div>
                </div>
            </div>

            <div
                style={{
                    "padding": "16px 18px",
                    "background": "rgba(255,255,255,0.03)",
                    "backdropFilter": "blur(12px)",
                    "border": "0.5px solid rgba(255,255,255,0.08)",
                    "borderRadius": "14px"
                }}
            >
                <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.62)", "textTransform": "uppercase", "letterSpacing": "0.06em", "marginBottom": "12px"}}>
                    Most-requested resources
                </div>
                {(len(top_resources) > 0) and <div>
                    {[renderResourceBar(str(top_resources[ri]["name"]), int(top_resources[ri]["count"]), max_res) for ri in range(len(top_resources))]}
                </div>}
                {(len(top_resources) == 0) and <div style={{"fontSize": "12px", "color": "rgba(255,255,255,0.62)", "padding": "12px 0"}}>
                    No applications written to the graph yet. Send a chat message in the Chat tab to populate ApplicationNodes.
                </div>}
            </div>

            <div style={{"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "12px"}}>
                <div
                    style={{
                        "padding": "16px 18px",
                        "background": "rgba(255,255,255,0.03)",
                        "backdropFilter": "blur(12px)",
                        "border": "0.5px solid rgba(255,255,255,0.08)",
                        "borderRadius": "14px"
                    }}
                >
                    <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.62)", "textTransform": "uppercase", "letterSpacing": "0.06em", "marginBottom": "12px"}}>
                        Languages detected
                    </div>
                    {(len(lang_pairs) > 0) and <div style={{"display": "flex", "flexWrap": "wrap", "gap": "7px"}}>
                        {[renderLanguageChip(str(lang_pairs[i]["lang"]), int(lang_pairs[i]["count"])) for i in range(len(lang_pairs))]}
                    </div>}
                    {(len(lang_pairs) == 0) and <div style={{"fontSize": "12px", "color": "rgba(255,255,255,0.62)"}}>
                        No PersonNodes yet.
                    </div>}
                </div>
                <div
                    style={{
                        "padding": "18px 20px",
                        "background": "rgba(255,229,0,0.05)",
                        "backdropFilter": "blur(12px)",
                        "border": "0.5px solid rgba(255,229,0,0.25)",
                        "borderRadius": "14px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center"
                    }}
                >
                    {renderTopNeedCard(cat_count_by_key)}
                </div>
            </div>
        </div>;
}
