"""Render helpers for LandingPage."""

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
                "overflow": "hidden"
            }}>
                <svg viewBox="0 0 24 24" width="22" height="22" xmlns="http://www.w3.org/2000/svg">
                    <path d="M5.5 23 C5.5 18 8 16.8 12 16.8 C16 16.8 18.5 18 18.5 23 Z" fill="#0A0A0A"/>
                    <rect x="10.8" y="14.5" width="2.4" height="2.5" fill="#E2A676"/>
                    <circle cx="12" cy="11" r="5" fill="#F8C291"/>
                    <circle cx="7" cy="11" r="0.9" fill="#F8C291"/>
                    <circle cx="17" cy="11" r="0.9" fill="#F8C291"/>
                    <path d="M6.5 10 C6.5 6 9 4 12 4 C15 4 17.5 6 17.5 10 C16.5 7.5 14.5 6.5 12 7 C9.5 6.5 7.5 7.5 6.5 10 Z" fill="#1E272E"/>
                    <circle cx="10" cy="10.8" r="0.9" fill="#1E272E"/>
                    <circle cx="14" cy="10.8" r="0.9" fill="#1E272E"/>
                    <circle cx="9.7" cy="10.5" r="0.3" fill="#FFFFFF"/>
                    <circle cx="13.7" cy="10.5" r="0.3" fill="#FFFFFF"/>
                    <circle cx="8.8" cy="12" r="0.8" fill="#E55039" opacity="0.45"/>
                    <circle cx="15.2" cy="12" r="0.8" fill="#E55039" opacity="0.45"/>
                    <path d="M10.3 12.8 C10.8 13.8 13.2 13.8 13.7 12.8" stroke="#1E272E" strokeWidth="0.75" strokeLinecap="round" fill="none"/>
                </svg>
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
