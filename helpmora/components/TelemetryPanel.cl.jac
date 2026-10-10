"""LLM telemetry dashboard.

All metrics shown here are derived from real walker_events emitted by the
chat pipeline. No demo defaults. When no chat session has run yet, the
panel shows an empty-state explanation.
"""

sv import from walkers.critique { ReflectionReadWalker }
import from "@jac/runtime" { jacSpawn, jacIsLoggedIn }

def:pub TelemetryPanel(walker_events: list, user_id: str = "") -> JsxElement {
    # Reflexion-style self-reflection panel state. Populated by
    # ReflectionReadWalker on mount and whenever walker_events grows
    # (i.e. when a new chat turn writes a fresh SessionInsight).
    has reflections: list = [],
        reflections_loading: bool = False,
        selected_walker: str = "ALL",
        selected_event_idx: int = -1,
        pinging: bool = False,
        ping_result: str = "";

    async def loadReflections -> None;
    async def runDiagnosticPing -> None;
    def selectWalker(name: str) -> None;
    def toggleEventDetail(idx: int) -> None;
    def renderReflectionTimeline -> JsxElement;
    def renderReflectionRow(ins: Any, idx: int) -> JsxElement;

    can with entry {
        loadReflections();
    }

    can with [walker_events] entry {
        if walker_events and len(walker_events) > 0 {
            loadReflections();
        }
    }

    walker_meta: dict = {
        "IntakeWalker":      {"icon": "🚪", "color": "#FFE500"},
        "EligibilityWalker": {"icon": "🔍", "color": "#4488FF"},
        "NavigationWalker":  {"icon": "🗺",  "color": "#00FF88"},
        "MemoryWalker":      {"icon": "🧠", "color": "#FFB344"},
        "EscalationWalker":  {"icon": "⚡", "color": "#FF4444"}
    };
    walker_order: list[str] = [
        "IntakeWalker", "EligibilityWalker", "NavigationWalker",
        "MemoryWalker", "EscalationWalker"
    ];

    # Count events per walker, derived from the live event stream.
    counts: dict = {
        "IntakeWalker": 0, "EligibilityWalker": 0, "NavigationWalker": 0,
        "MemoryWalker": 0, "EscalationWalker": 0
    };
    triggered: dict = {
        "IntakeWalker": False, "EligibilityWalker": False,
        "NavigationWalker": False, "MemoryWalker": False,
        "EscalationWalker": False
    };
    total_events = len(walker_events) if walker_events else 0;
    if walker_events {
        for i in range(total_events) {
            ev: Any = walker_events[i];
            w_raw = ev["walker"] if ev else "";
            w = str(w_raw) if w_raw else "";
            if w in counts {
                counts[w] = counts[w] + 1;
                triggered[w] = True;
            }
        }
    }

    def renderWalkerRow(name: str) -> JsxElement;
    def renderChainNode(name: str, is_triggered: bool, count: int) -> JsxElement;
    def renderEvent(ev: Any, idx: int) -> JsxElement;
    def renderCallCard(name: str) -> JsxElement;

    # Per-walker architectural breakdown — what the LLM was asked, what
    # structured type it returned, and whether the walker invoked any
    # tools mid-flight. This metadata is static (mirrors how the walkers
    # are defined in walkers/*.jac and llm/stubs.jac) so we don't need
    # the chat pipeline to round-trip prompt strings.
    walker_calls: dict = {
        "IntakeWalker": {
            "input": "Latest message + case carried from earlier turns",
            "output": "Profile{category, urgency, income, household, age, location, status} + evidence spans",
            "stub": "engine/i18n.jac + parse.jac (script + lexicon language ID, 75 languages) · understand_message() only if nothing routes, 3.5 s deadline",
            "tools": False
        },
        "EligibilityWalker": {
            "input": "Profile + every Resource→Rule→Form triple in your graph",
            "output": "Ranked matches{p_eligible, tier, Beta approval CI, criteria, counterfactual} + next question",
            "stub": "engine/score.jac — logistic income, hard gates, abstention, value of information",
            "tools": False
        },
        "NavigationWalker": {
            "input": "Ranked matches + urgency",
            "output": "Plan{steps[], shared_documents, total_minutes} + ApplicationNodes",
            "stub": "engine/plan.jac — Smith's weighted-shortest-processing-time rule",
            "tools": False
        },
        "MemoryWalker": {
            "input": "user_id + mode (read_session | update_status)",
            "output": "Session snapshot · Beta posterior before/after an outcome",
            "stub": "deterministic summary · Bayesian outcome learning",
            "tools": False
        },
        "EscalationWalker": {
            "input": "Risk flags (self-harm, DV) or no credible match",
            "output": "Crisis lead line + open crisis resources from the graph",
            "stub": "deterministic — a crisis reply never waits on a model",
            "tools": False
        }
    };

    # Empty state — no chat session has run yet.
    if total_events == 0 {
        return
            <div
                style={{
                    "padding": "48px 32px",
                    "textAlign": "center",
                    "background": "rgba(255,255,255,0.03)",
                    "backdropFilter": "blur(12px)",
                    "border": "0.5px solid rgba(255,255,255,0.08)",
                    "borderRadius": "16px",
                    "maxWidth": "600px",
                    "margin": "0 auto"
                }}
            >
                <div style={{"fontSize": "32px", "marginBottom": "10px"}}>📊</div>
                <div style={{"fontSize": "16px", "fontWeight": "600", "marginBottom": "8px", "color": "#FFE500"}}>
                    No telemetry yet
                </div>
                <div style={{"fontSize": "13px", "color": "rgba(255,255,255,0.55)", "lineHeight": "1.6", "marginBottom": "16px"}}>
                    Walker call counts, latency, and call-tree are computed live from the event stream emitted by chat turns. Send a message in the Chat tab and switch back here to see the multi-agent pipeline activity.
                </div>
                <div style={{
                    "padding": "12px 14px",
                    "background": "rgba(255,229,0,0.06)",
                    "border": "0.5px solid rgba(255,229,0,0.2)",
                    "borderRadius": "10px",
                    "fontSize": "11px",
                    "color": "rgba(255,255,255,0.6)",
                    "textAlign": "left",
                    "lineHeight": "1.55"
                }}>
                    <div style={{"color": "#FFE500", "fontWeight": "600", "marginBottom": "4px"}}>
                        Model calls on this server:
                    </div>
                    Per-call model traces stay private to the server. What the public Space shows is here and on the Impact tab: which walkers ran, how long they took, and whether a model was called at all (usually only the background summary).
                </div>
            </div>;
    }

    filtered_events: list = [walker_events[j] for j in range(total_events) if (selected_walker == "ALL" or str(walker_events[j]["walker"]) == selected_walker)];

    return
        <div>
            <div
                style={{
                    "fontSize": "11px",
                    "color": "rgba(255,255,255,0.62)",
                    "marginBottom": "12px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "gap": "10px",
                    "flexWrap": "wrap"
                }}
            >
                <div style={{"display": "flex", "alignItems": "center", "gap": "7px"}}>
                    <span
                        style={{
                            "width": "7px", "height": "7px",
                            "borderRadius": "50%",
                            "background": "#00FF88",
                            "boxShadow": "0 0 8px #00FF88",
                            "display": "inline-block"
                        }}
                    />
                    <span>Live data — {str(total_events)} walker events captured this session.</span>
                </div>
                <div style={{"display": "flex", "alignItems": "center", "gap": "10px"}}>
                    {ping_result and <span style={{"color": "#00FF88", "fontSize": "11px", "fontFamily": "ui-monospace, monospace"}}>{ping_result}</span>}
                    <button
                        onClick={lambda _e: MouseEvent { runDiagnosticPing(); }}
                        disabled={pinging}
                        style={{
                            "padding": "5px 12px",
                            "borderRadius": "7px",
                            "background": "rgba(255, 229, 0, 0.08)",
                            "border": "0.5px solid rgba(255, 229, 0, 0.3)",
                            "color": "#FFE500",
                            "fontSize": "11px",
                            "fontWeight": "600",
                            "cursor": "pointer",
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "5px"
                        }}
                    >
                        <span>{("⏳" if pinging else "⚡")}</span>
                        <span>{("Pinging pipeline..." if pinging else "Diagnostic Pipeline Ping")}</span>
                    </button>
                </div>
            </div>

            <div
                style={{
                    "display": "grid",
                    "gridTemplateColumns": "repeat(3,1fr)",
                    "gap": "10px",
                    "marginBottom": "14px"
                }}
            >
                <div
                    className="stat-enter"
                    style={{
                        "padding": "14px",
                        "background": "rgba(255,255,255,0.03)",
                        "backdropFilter": "blur(12px)",
                        "border": "0.5px solid rgba(255,255,255,0.07)",
                        "borderRadius": "12px",
                        "textAlign": "center"
                    }}
                >
                    <div style={{"fontSize": "20px", "marginBottom": "5px"}}>📞</div>
                    <div style={{"fontSize": "22px", "fontWeight": "600", "color": "#FFE500"}}>
                        {str(total_events)}
                    </div>
                    <div style={{"fontSize": "11px", "color": "rgba(255,255,255,0.62)", "marginTop": "3px"}}>
                        Walker events captured
                    </div>
                </div>
                <div
                    className="stat-enter"
                    style={{
                        "padding": "14px",
                        "background": "rgba(255,255,255,0.03)",
                        "backdropFilter": "blur(12px)",
                        "border": "0.5px solid rgba(255,255,255,0.07)",
                        "borderRadius": "12px",
                        "textAlign": "center"
                    }}
                >
                    <div style={{"fontSize": "20px", "marginBottom": "5px"}}>🤖</div>
                    <div style={{"fontSize": "22px", "fontWeight": "600", "color": "#FFE500"}}>
                        {str(len([w for w in walker_order if triggered[w]])) + " / " + str(len(walker_order))}
                    </div>
                    <div style={{"fontSize": "11px", "color": "rgba(255,255,255,0.62)", "marginTop": "3px"}}>
                        Walkers triggered
                    </div>
                </div>
                <div
                    className="stat-enter"
                    style={{
                        "padding": "14px",
                        "background": "rgba(255,255,255,0.03)",
                        "backdropFilter": "blur(12px)",
                        "border": "0.5px solid rgba(255,255,255,0.07)",
                        "borderRadius": "12px",
                        "textAlign": "center"
                    }}
                >
                    <div style={{"fontSize": "20px", "marginBottom": "5px"}}>⚡</div>
                    <div style={{"fontSize": "20px", "fontWeight": "600", "color": "#FFE500"}}>
                        gpt-oss-20b · Gemma 4
                    </div>
                    <div style={{"fontSize": "11px", "color": "rgba(255,255,255,0.62)", "marginTop": "3px"}}>
                        Active model · Deterministic-first
                    </div>
                </div>
            </div>

            <div
                style={{
                    "background": "rgba(255,255,255,0.03)",
                    "backdropFilter": "blur(12px)",
                    "border": "0.5px solid rgba(255,255,255,0.07)",
                    "borderRadius": "14px",
                    "overflow": "hidden",
                    "marginBottom": "14px"
                }}
            >
                <div
                    style={{
                        "padding": "10px 16px",
                        "borderBottom": "0.5px solid rgba(255,255,255,0.06)",
                        "fontSize": "10px",
                        "color": "rgba(255,255,255,0.62)",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.06em",
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center"
                    }}
                >
                    <span>Walker activity (Click row to inspect / filter)</span>
                    {selected_walker != "ALL" and <button
                        onClick={lambda _e: MouseEvent { selectWalker("ALL"); }}
                        style={{"background": "none", "border": "none", "color": "#FFE500", "fontSize": "10px", "cursor": "pointer", "textDecoration": "underline"}}
                    >
                        {"Clear filter (" + selected_walker + ")"}
                    </button>}
                </div>
                {[renderWalkerRow(walker_order[i]) for i in range(len(walker_order))]}
            </div>

            <div
                style={{
                    "padding": "16px",
                    "background": "rgba(255,255,255,0.03)",
                    "backdropFilter": "blur(12px)",
                    "border": "0.5px solid rgba(255,255,255,0.07)",
                    "borderRadius": "14px"
                }}
            >
                <div style={{"fontSize": "11px", "color": "rgba(255,255,255,0.62)", "marginBottom": "14px", "textTransform": "uppercase", "letterSpacing": "0.06em"}}>
                    Walker call tree — parent → child invocation (Click to inspect)
                </div>
                <div style={{"display": "flex", "alignItems": "center", "overflowX": "auto", "gap": "0", "padding": "4px 0"}}>
                    {[renderChainNode(walker_order[i], bool(triggered[walker_order[i]]), int(counts[walker_order[i]])) for i in range(len(walker_order))]}
                </div>
                <div style={{"marginTop": "16px", "paddingTop": "14px", "borderTop": "0.5px solid rgba(255,255,255,0.06)"}}>
                    <div style={{"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "10px", "flexWrap": "wrap", "gap": "8px"}}>
                        <div style={{"fontSize": "10px", "color": "rgba(255,255,255,0.62)", "textTransform": "uppercase", "letterSpacing": "0.06em"}}>
                            {"Recent events (" + str(len(filtered_events)) + " displayed)"}
                        </div>
                        <div style={{"display": "flex", "gap": "5px", "flexWrap": "wrap"}}>
                            <button
                                onClick={lambda _e: MouseEvent { selectWalker("ALL"); }}
                                style={{
                                    "padding": "2px 7px",
                                    "borderRadius": "5px",
                                    "border": ("1px solid #FFE500" if selected_walker == "ALL" else "0.5px solid rgba(255,255,255,0.1)"),
                                    "background": ("rgba(255,229,0,0.15)" if selected_walker == "ALL" else "rgba(255,255,255,0.02)"),
                                    "color": ("#FFE500" if selected_walker == "ALL" else "rgba(255,255,255,0.6)"),
                                    "fontSize": "10px",
                                    "cursor": "pointer"
                                }}
                            >
                                All
                            </button>
                            {[
                                <button
                                    key={"flt-" + str(w)}
                                    onClick={lambda _e: MouseEvent { selectWalker(w); }}
                                    style={{
                                        "padding": "2px 7px",
                                        "borderRadius": "5px",
                                        "border": ("1px solid " + str(walker_meta[w]["color"]) if selected_walker == w else "0.5px solid rgba(255,255,255,0.1)"),
                                        "background": (str(walker_meta[w]["color"]) + "20" if selected_walker == w else "rgba(255,255,255,0.02)"),
                                        "color": (str(walker_meta[w]["color"]) if selected_walker == w else "rgba(255,255,255,0.6)"),
                                        "fontSize": "10px",
                                        "cursor": "pointer"
                                    }}
                                >
                                    {str(walker_meta[w]["icon"]) + " " + w}
                                </button>
                                for w in walker_order
                            ]}
                        </div>
                    </div>
                    {len(filtered_events) == 0 and <div style={{"fontSize": "11px", "color": "rgba(255,255,255,0.45)", "padding": "8px 0"}}>
                        {"No events matching filter " + selected_walker + ". Click 'All' to view all events."}
                    </div>}
                    {[renderEvent(filtered_events[j], j) for j in range(max(0, len(filtered_events) - 10), len(filtered_events))]}
                </div>
            </div>

            <div
                style={{
                    "marginTop": "14px",
                    "background": "rgba(255,255,255,0.03)",
                    "backdropFilter": "blur(12px)",
                    "border": "0.5px solid rgba(255,255,255,0.07)",
                    "borderRadius": "14px",
                    "padding": "16px 18px"
                }}
            >
                <div
                    style={{
                        "fontSize": "10px",
                        "color": "rgba(255,255,255,0.62)",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.06em",
                        "marginBottom": "4px"
                    }}
                >
                    Agent reasoning transparency
                </div>
                <div
                    style={{
                        "fontSize": "11px",
                        "color": "rgba(255,255,255,0.62)",
                        "marginBottom": "14px",
                        "lineHeight": "1.45"
                    }}
                >
                    For each walker that ran this session: the input the LLM saw, the structured output type it produced, and whether it dispatched any tools mid-execution.
                </div>
                <div style={{"display": "flex", "flexDirection": "column", "gap": "10px"}}>
                    {[renderCallCard(walker_order[i]) for i in range(len(walker_order)) if triggered[walker_order[i]]]}
                </div>
            </div>

            {renderReflectionTimeline()}
        </div>;
}
