"""Render helpers for LandingPage."""

glob BOT_AVATAR_SRC: str = "data:image/webp;base64,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";

impl LandingPage.renderPersonaPill(label: str, color: str) -> JsxElement {
    return
        <div
            key={label}
            className="lp-persona"
            style={{
                "padding": "7px 14px",
                "background": color + "10",
                "border": "0.5px solid " + color + "40",
                "color": color,
                "borderRadius": "999px",
                "fontSize": "12px",
                "fontWeight": "500",
                "letterSpacing": "0.005em",
                "cursor": "default"
            }}
        >
            {label}
        </div>;
}

impl LandingPage.renderStatTile(value: str, label: str, sub: str, accent: str, sub2: str = "") -> JsxElement {
    return
        <div
            key={label}
            className="lp-glass lp-stat"
            style={{
                "padding": "22px 20px",
                "position": "relative",
                "overflow": "hidden",
                "borderTop": "2px solid " + accent
            }}
        >
            <div
                className="lp-orb"
                style={{
                    "width": "140px",
                    "height": "140px",
                    "background": accent,
                    "top": "-50px",
                    "right": "-40px",
                    "opacity": "0.18"
                }}
            />
            <div style={{
                "fontSize": "44px",
                "fontWeight": "800",
                "letterSpacing": "-0.04em",
                "color": accent,
                "lineHeight": "1",
                "position": "relative",
                "zIndex": "1"
            }}>
                {value}
            </div>
            <div style={{
                "fontSize": "12px",
                "color": "rgba(255,255,255,0.7)",
                "marginTop": "10px",
                "fontWeight": "600",
                "letterSpacing": "0.01em",
                "position": "relative",
                "zIndex": "1"
            }}>
                {label}
            </div>
            <div style={{
                "fontSize": "10.5px",
                "color": "rgba(255,255,255,0.62)",
                "marginTop": "4px",
                "lineHeight": "1.45",
                "position": "relative",
                "zIndex": "1"
            }}>
                <div>{sub}</div>
                {sub2 and <div style={{"marginTop": "3px", "color": "rgba(255,255,255,0.48)"}}>{sub2}</div>}
            </div>
        </div>;
}

impl LandingPage.renderWalkerCard(idx: int, name: str, role: str, color: str, tilt: str) -> JsxElement {
    # `tilt` is passed as a CSS rotateY angle string ("-3deg", "2deg", ...).
    # The cards alternate left/right tilt so the row reads like a fanned
    # deck of cards rather than a tidy row of buttons. Hover undoes the
    # tilt and lifts the card; see .lp-walker-card in index.css.
    return
        <div
            key={name}
            className="lp-glass lp-walker-card"
            style={{
                "--tilt": tilt,
                "padding": "20px 18px",
                "display": "flex",
                "flexDirection": "column",
                "gap": "10px",
                "minHeight": "180px",
                "borderTop": "2px solid " + color,
                "boxShadow":
                    "inset 0 1px 0 0 rgba(255,255,255,0.08), "
                    + "0 18px 36px -16px " + color + "30"
            }}
        >
            <div style={{"display": "flex", "alignItems": "center", "justifyContent": "space-between"}}>
                <div style={{
                    "width": "26px",
                    "height": "26px",
                    "borderRadius": "8px",
                    "background": color + "20",
                    "border": "1px solid " + color + "60",
                    "color": color,
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "flexShrink": "0",
                    "fontFamily": "ui-monospace, monospace"
                }}>
                    {str(idx)}
                </div>
                <div style={{
                    "width": "8px",
                    "height": "8px",
                    "borderRadius": "50%",
                    "background": color,
                    "boxShadow": "0 0 8px " + color
                }}/>
            </div>
            <div style={{
                "fontSize": "16px",
                "fontWeight": "700",
                "color": color,
                "letterSpacing": "-0.01em",
                "marginTop": "4px"
            }}>
                {name}
            </div>
            <div style={{
                "fontSize": "10px",
                "color": "rgba(255,255,255,0.62)",
                "textTransform": "uppercase",
                "letterSpacing": "0.08em",
                "fontWeight": "600"
            }}>
                Walker
            </div>
            <div style={{
                "fontSize": "12px",
                "color": "rgba(255,255,255,0.62)",
                "lineHeight": "1.5",
                "marginTop": "4px"
            }}>
                {role}
            </div>
        </div>;
}

impl LandingPage.renderTrackBadge(label: str, accent: str, desc: str = "") -> JsxElement {
    return
        <div
            key={label}
            style={{
                "padding": "12px 16px",
                "background": "linear-gradient(135deg, " + accent + "18 0%, " + accent + "08 100%)",
                "border": "0.5px solid " + accent + "55",
                "borderRadius": "12px",
                "display": "flex",
                "alignItems": "flex-start",
                "gap": "10px",
                "boxShadow": "inset 0 1px 0 rgba(255,255,255,0.05), 0 6px 14px -8px " + accent + "40"
            }}
        >
            <span style={{
                "width": "6px",
                "height": "6px",
                "borderRadius": "50%",
                "background": accent,
                "boxShadow": "0 0 6px " + accent,
                "marginTop": "6px",
                "flexShrink": "0"
            }}/>
            <div style={{"display": "flex", "flexDirection": "column", "gap": "3px"}}>
                <div style={{
                    "color": accent,
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "letterSpacing": "0.005em"
                }}>
                    {label}
                </div>
                {desc and <div style={{
                    "fontSize": "11.5px",
                    "color": "rgba(255,255,255,0.65)",
                    "lineHeight": "1.4"
                }}>
                    {desc}
                </div>}
            </div>
        </div>;
}

impl LandingPage.renderPreviewBubble(role: str, walker_name: str, text: str, color: str) -> JsxElement {
    # Mock chat bubbles rendered inside the hero's "live session" glass
    # card. Pure decoration — no walker spawns happen from this page.
    is_user = role == "user";
    return
        <div
            key={text}
            style={{
                "display": "flex",
                "alignItems": "flex-start",
                "gap": "10px",
                "justifyContent": ("flex-end" if is_user else "flex-start")
            }}
        >
            {(not is_user) and <div style={{
                "width": "24px",
                "height": "24px",
                "borderRadius": "50%",
                "background": color,
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "flexShrink": "0",
                "marginTop": "1px",
                "boxShadow": "0 4px 10px -2px " + color + "60",
                "overflow": "hidden",
                "border": "1.5px solid " + color
            }}>
                <img
                    src=BOT_AVATAR_SRC
                    alt="Assistant"
                    style={{
                        "width": "100%",
                        "height": "100%",
                        "borderRadius": "50%",
                        "objectFit": "cover",
                        "display": "block"
                    }}
                />
            </div>}
            <div style={{"maxWidth": "82%"}}>
                {((not is_user) and walker_name) and <div style={{
                    "fontSize": "9px",
                    "color": color,
                    "marginBottom": "3px",
                    "fontWeight": "600",
                    "letterSpacing": "0.04em",
                    "textTransform": "uppercase",
                    "fontFamily": "ui-monospace, monospace"
                }}>
                    {walker_name}
                </div>}
                <div style={{
                    "padding": "9px 13px",
                    "borderRadius": ("14px 14px 4px 14px" if is_user else "4px 14px 14px 14px"),
                    "background": ("rgba(255,229,0,0.95)" if is_user else "rgba(255,255,255,0.05)"),
                    "color": ("#0A0A0A" if is_user else "rgba(255,255,255,0.85)"),
                    "fontSize": "12.5px",
                    "lineHeight": "1.5",
                    "border": ("none" if is_user else "0.5px solid rgba(255,255,255,0.08)"),
                    "borderLeft": ("none" if (is_user or (not walker_name)) else ("2px solid " + color)),
                    "fontWeight": ("500" if is_user else "400"),
                    "whiteSpace": "pre-line"
                }}>
                    {text}
                </div>
            </div>
        </div>;
}

impl LandingPage.previewLine(step: int) -> str {
    if step == 2 {
        return "Understood: food + housing · household of 3 · ₹18,000/month · Hyderabad · single parent. Structured into a case profile for policy evaluation.";
    }
    if step == 3 {
        return "Evaluated 10 relevant programs using deterministic policy rules: PMGKAY — likely eligible · PM POSHAN — likely eligible · Food Security Helpline — recommended next step";
    }
    if step == 4 {
        return "“Do you currently have a ration card or access to One Nation One Ration Card? This is the one fact that could change several of your food-support matches. You can say ‘I don’t know.’”";
    }
    return "";
}
