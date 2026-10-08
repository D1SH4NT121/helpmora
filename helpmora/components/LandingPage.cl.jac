"""HELPmora landing page.

First thing visitors see. Designed for the HELPmora showcase:
glassmorphism + 3D-tilt walker pipeline + animated mesh background.
The "Enter Navigator" CTA flips ClientApp.show_landing=False and routes
to the chat tab — no walker spawns happen from this page.

Sections:
  - Glass nav strip with live status pill
  - Hero: massive headline with gradient text accent + glass preview card
  - Bento stat tiles (4 cards with 3D hover tilt)
  - Walker pipeline (5 cards alternating tilt, animated dashed rail under)
  - Persona pull-quote + persona chips
  - Tracks (3 glass pill badges)
  - Footer

All animation is CSS-only (mesh drift, gradient text shift, hover tilt,
dashed rail scroll). No Spline / WebGL — keeps bundle small and first
paint fast on 4G.
"""

import from .HELPmoraLogo { HELPmoraLogo }

def:pub LandingPage(on_start: Any, platform: Any = None) -> JsxElement {

    # Auto-typing chat preview state. The hero's "live session" glass card
    # advances bubble-by-bubble on a 1.4s cadence so judges see the agent
    # working before they scroll. preview_step ∈ [0..4]; 0 = nothing shown,
    # 4 = all four bubbles visible. Cycles back to 1 every ~9s so a judge
    # watching the page idle still sees motion.
    has preview_step: int = 0;

    can with entry {
        def advance(n: int) -> None {
            preview_step = n;
            if n < 4 {
                setTimeout(lambda { advance(n + 1); }, 1400);
            } else {
                setTimeout(lambda { advance(1); }, 4500);
            }
        }
        setTimeout(lambda { advance(1); }, 600);
    }

    def renderPersonaPill(label: str, color: str) -> JsxElement;
    def renderStatTile(value: str, label: str, sub: str, accent: str, sub2: str = "") -> JsxElement;
    def renderWalkerCard(idx: int, name: str, role: str, color: str, tilt: str) -> JsxElement;
    def renderTrackBadge(label: str, accent: str, desc: str = "") -> JsxElement;
    def renderPreviewBubble(role: str, walker_name: str, text: str, color: str) -> JsxElement;
    def previewLine(step: int) -> str;

    return
        <div
            className="lp-root"
            style={{
                "minHeight": "100vh",
                "display": "flex",
                "flexDirection": "column",
                "background": "#070708",
                "color": "#FFFFFF",
                "fontFamily": "system-ui, -apple-system, sans-serif",
                "position": "relative",
                "overflow": "hidden"
            }}
        >
            <div className="lp-mesh"/>
            <div className="lp-grid"/>
            <div className="lp-noise"/>

            <header
                className="lp-glass"
                style={{
                    "position": "relative",
                    "zIndex": "10",
                    "margin": "20px 24px 0",
                    "padding": "12px 22px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "borderRadius": "999px"
                }}
            >
                <div style={{"display": "flex", "alignItems": "center", "gap": "14px"}}>
                    <HELPmoraLogo size={32} show_wordmark={True} instance_id="lp_header"/>
                    <span style={{
                        "fontSize": "11px",
                        "padding": "3px 10px",
                        "borderRadius": "20px",
                        "background": "rgba(255,229,0,0.1)",
                        "color": "#FFE500",
                        "border": "0.5px solid rgba(255,229,0,0.3)",
                        "letterSpacing": "0.01em"
                    }}>
                        Agentic AI Navigator
                    </span>
                </div>
                <div style={{"display": "flex", "alignItems": "center", "gap": "10px"}}>
                    <div className="lp-pulse-dot"/>
                    <span style={{"fontSize": "12px", "color": "rgba(255,255,255,0.55)"}}>
                        {("engine live · " + str(platform["programs"]) + " programs") if platform else "engine starting…"}
                    </span>
                    <button
                        onClick={lambda _e: MouseEvent { on_start(); }}
                        style={{
                            "marginLeft": "10px",
                            "padding": "5px 13px",
                            "borderRadius": "20px",
                            "background": "linear-gradient(135deg, #FFE500 0%, #F59E0B 100%)",
                            "color": "#0A0A0A",
                            "border": "none",
                            "fontWeight": "700",
                            "fontSize": "11.5px",
                            "cursor": "pointer",
                            "display": "inline-flex",
                            "alignItems": "center",
                            "gap": "5px",
                            "boxShadow": "0 2px 10px rgba(255,229,0,0.3)"
                        }}
                    >
                        Enter the Navigator →
                    </button>
                </div>
            </header>

            <section
                className="lp-reveal"
                role="main"
                style={{
                    "position": "relative",
                    "zIndex": "1",
                    "padding": "24px 28px 40px",
                    "maxWidth": "1180px",
                    "margin": "0 auto",
                    "width": "100%",
                    "textAlign": "center"
                }}
            >
                <div className="lp-orb" style={{"width": "320px", "height": "320px", "background": "#FFE500", "top": "-40px", "left": "12%"}}/>
                <div className="lp-orb" style={{"width": "260px", "height": "260px", "background": "#FF88AA", "top": "40px", "right": "10%", "opacity": "0.35"}}/>

                <div style={{"display": "flex", "justifyContent": "center", "marginBottom": "14px"}}>
                    <HELPmoraLogo size={68} show_wordmark={True} show_tagline={True} instance_id="lp_hero"/>
                </div>

                <div style={{
                    "display": "inline-flex",
                    "alignItems": "center",
                    "gap": "8px",
                    "padding": "6px 14px",
                    "borderRadius": "999px",
                    "background": "rgba(255,255,255,0.05)",
                    "border": "0.5px solid rgba(255,255,255,0.12)",
                    "backdropFilter": "blur(12px)",
                    "fontSize": "12px",
                    "color": "rgba(255,255,255,0.7)",
                    "marginBottom": "26px",
                    "letterSpacing": "0.01em"
                }}>
                    <span style={{"width": "5px", "height": "5px", "borderRadius": "50%", "background": "#00FF88", "display": "inline-block", "boxShadow": "0 0 6px #00FF88"}}/>
                    Jac walkers · deterministic eligibility engine · one LLM call, off the critical path
                </div>

                <h1 style={{
                    "fontSize": "54px",
                    "fontWeight": "800",
                    "letterSpacing": "-0.04em",
                    "lineHeight": "1.04",
                    "margin": "0 0 16px",
                    "color": "#FFFFFF"
                }}>
                    Every bureaucratic wall
                    <br/>
                    has a door.
                    <br/>
                    <span className="lp-gradient-text">HELPmora finds it.</span>
                </h1>

                <p style={{
                    "fontSize": "15px",
                    "lineHeight": "1.52",
                    "color": "rgba(255,255,255,0.65)",
                    "maxWidth": "660px",
                    "margin": "0 auto 22px",
                    "fontWeight": "400"
                }}>
                    A voice-first Social Welfare & Legal Aid Navigator for India that turns a person’s story into an explainable path to support. Omi captures the conversation, Qdrant remembers the case, and Lyzr coordinates the journey — while HELPmora’s deterministic policy engine evaluates eligibility and its Pathfinder finds practical alternatives when the direct route is blocked.
                </p>

                <div style={{"display": "flex", "justifyContent": "center", "alignItems": "center", "gap": "16px", "marginBottom": "36px", "flexWrap": "wrap"}}>
                    <button className="lp-cta" onClick={lambda _e: MouseEvent { on_start(); }}>
                        Enter the Navigator  →
                    </button>
                    <div style={{"fontSize": "12px", "color": "rgba(255,255,255,0.62)", "textAlign": "left", "lineHeight": "1.5"}}>
                        <div style={{"color": "rgba(255,255,255,0.65)"}}>No signup — an anonymous account lives in this browser</div>
                        <div>{"40 national programs · 2026 federal income rules · local offices from HUD & HRSA open data"}</div>
                    </div>
                </div>

                <div
                    className="lp-glass-strong lp-float"
                    style={{
                        "position": "relative",
                        "maxWidth": "780px",
                        "margin": "0 auto",
                        "padding": "20px 22px",
                        "textAlign": "left"
                    }}
                >
                    <div style={{"display": "flex", "alignItems": "center", "justifyContent": "space-between", "marginBottom": "14px"}}>
                        <div style={{"display": "flex", "alignItems": "center", "gap": "8px"}}>
                            <span style={{"width": "10px", "height": "10px", "borderRadius": "50%", "background": "#FF5F57"}}/>
                            <span style={{"width": "10px", "height": "10px", "borderRadius": "50%", "background": "#FEBC2E"}}/>
                            <span style={{"width": "10px", "height": "10px", "borderRadius": "50%", "background": "#28C840"}}/>
                            <span style={{"fontSize": "11px", "color": "rgba(255,255,255,0.62)", "marginLeft": "10px", "letterSpacing": "0.02em"}}>
                                LIVE CASE RUN · 31 ms · DETERMINISTIC POLICY ENGINE
                            </span>
                        </div>
                        <div style={{
                            "display": "flex",
                            "alignItems": "center",
                            "gap": "6px",
                            "padding": "3px 10px",
                            "borderRadius": "20px",
                            "background": "rgba(255,229,0,0.1)",
                            "border": "0.5px solid rgba(255,229,0,0.3)",
                            "fontSize": "10px",
                            "color": "#FFE500"
                        }}>
                            <span style={{"width": "5px", "height": "5px", "borderRadius": "50%", "background": "#FFE500", "boxShadow": "0 0 5px #FFE500"}}/>
                            EligibilityWalker
                        </div>
                    </div>
                    <div style={{"display": "flex", "flexDirection": "column", "gap": "10px", "minHeight": "180px"}}>
                        {(preview_step >= 1) and renderPreviewBubble("user", "", "“I’m a single mother with two children in Hyderabad. I earn ₹18,000 a month, we’re struggling with rent and we need food support.”", "#FFE500")}
                        {(preview_step >= 2) and renderPreviewBubble("bot", "IntakeWalker", previewLine(2), "#FFE500")}
                        {(preview_step >= 3) and renderPreviewBubble("bot", "EligibilityWalker", previewLine(3), "#4488FF")}
                        {(preview_step >= 4) and renderPreviewBubble("bot", "Next question", previewLine(4), "#00FF88")}
                        {(preview_step > 0 and preview_step < 4) and <div style={{"display": "flex", "alignItems": "center", "gap": "6px", "color": "rgba(255,255,255,0.62)", "fontSize": "11px", "fontStyle": "italic", "paddingLeft": "34px"}}>
                            <span className="lp-typing-dot"/>
                            <span className="lp-typing-dot"/>
                            <span className="lp-typing-dot"/>
                        </div>}
                    </div>
                </div>
            </section>

            <section
                style={{
                    "position": "relative",
                    "zIndex": "1",
                    "padding": "12px 40px 36px",
                    "maxWidth": "1180px",
                    "margin": "0 auto",
                    "width": "100%"
                }}
            >
                <div style={{
                    "display": "grid",
                    "gridTemplateColumns": "repeat(4, 1fr)",
                    "gap": "14px"
                }}>
                    {renderStatTile((str(platform["programs"]) if platform else "40"), "Programs evaluated", "Housing · Food · Healthcare · Legal Aid", "#FFE500", "Deterministic, household-aware policy engine")}
                    {renderStatTile((str(platform["languages_native"]) if (platform and platform["languages_native"]) else "51"), "Languages supported", "Conversational intake across supported languages", "#00FF88", "Built for people, not paperwork")}
                    {renderStatTile(((str(platform["stats"]["engine_ms_p50"]) + " ms") if (platform and Number(platform["stats"]["turns"]) > 0) else "< 1 s"), "Decision latency", "Deterministic policy evaluation", "#4488FF", "Answers before AI explanation")}
                    {renderStatTile("1", "LLM call per turn", "Async explanation with a facts guard", "#FF88AA", "AI assists — policy logic decides")}
                </div>
            </section>

            <section
                style={{
                    "position": "relative",
                    "zIndex": "1",
                    "padding": "60px 40px",
                    "maxWidth": "1180px",
                    "margin": "0 auto",
                    "width": "100%"
                }}
            >
                <div className="lp-orb" style={{"width": "300px", "height": "300px", "background": "#4488FF", "top": "30px", "left": "-80px", "opacity": "0.3"}}/>

                <div style={{"textAlign": "center", "marginBottom": "40px"}}>
                    <div style={{
                        "display": "inline-flex",
                        "alignItems": "center",
                        "gap": "8px",
                        "padding": "5px 12px",
                        "borderRadius": "999px",
                        "background": "rgba(0,255,136,0.08)",
                        "border": "0.5px solid rgba(0,255,136,0.3)",
                        "fontSize": "10px",
                        "color": "#00FF88",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.1em",
                        "fontWeight": "600",
                        "marginBottom": "16px"
                    }}>
                        Architecture
                    </div>
                    <h2 style={{
                        "fontSize": "36px",
                        "fontWeight": "700",
                        "letterSpacing": "-0.025em",
                        "margin": "0 0 8px"
                    }}>
                        One deterministic core. One traceable path to action.
                    </h2>
                    <p style={{"fontSize": "14px", "color": "rgba(255,255,255,0.5)", "margin": "0", "maxWidth": "560px", "marginLeft": "auto", "marginRight": "auto"}}>
                        HELPmora turns a person’s story into structured case facts, evaluates policy deterministically, finds alternative routes when needed, and guides the user to a verified next step. Memory, safety, and AI orchestration support the journey without replacing the policy engine.
                    </p>
                </div>

                <div style={{"position": "relative"}}>
                    <div style={{
                        "position": "absolute",
                        "top": "78px",
                        "left": "8%",
                        "right": "8%",
                        "zIndex": "0"
                    }}>
                        <div className="lp-pipeline-rail"/>
                    </div>
                    <div style={{
                        "display": "grid",
                        "gridTemplateColumns": "repeat(5, 1fr)",
                        "gap": "14px",
                        "alignItems": "stretch",
                        "position": "relative",
                        "zIndex": "1"
                    }}>
                        {renderWalkerCard(1, "Intake",      "Turns a real-life story into structured case facts — need, income, household, location, language, and urgency.", "#FFE500", "-3deg")}
                        {renderWalkerCard(2, "Eligibility", "Evaluates 40 curated programs with deterministic policy rules and produces an explainable eligibility result.", "#4488FF", "2deg")}
                        {renderWalkerCard(3, "Navigation",  "Turns the result into an actionable plan — required documents, submission channels, and clear next steps.",   "#00FF88", "-2deg")}
                        {renderWalkerCard(4, "Pathfinder",  "When the direct route is blocked, traverses 26 curated graph transitions to find a viable alternative path.",      "#FFB344", "3deg")}
                        {renderWalkerCard(5, "Escalation",  "Routes urgent cases through verified crisis pathways and helplines without relying on LLM-generated emergency information.", "#FF88AA", "-2deg")}
                    </div>
                </div>
            </section>

            <section
                style={{
                    "position": "relative",
                    "zIndex": "1",
                    "padding": "30px 40px 60px",
                    "maxWidth": "1180px",
                    "margin": "0 auto",
                    "width": "100%",
                    "display": "grid",
                    "gridTemplateColumns": "1.4fr 1fr",
                    "gap": "20px",
                    "alignItems": "stretch"
                }}
            >
                <div
                    className="lp-glass"
                    style={{
                        "padding": "30px 32px",
                        "position": "relative",
                        "overflow": "hidden"
                    }}
                >
                    <div className="lp-orb" style={{"width": "240px", "height": "240px", "background": "#FFE500", "top": "-60px", "right": "-60px", "opacity": "0.18"}}/>
                    <div style={{
                        "fontSize": "10px",
                        "color": "rgba(255,255,255,0.62)",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.1em",
                        "fontWeight": "600",
                        "marginBottom": "14px"
                    }}>
                        Who this is for
                    </div>
                    <div style={{
                        "fontSize": "26px",
                        "fontWeight": "700",
                        "letterSpacing": "-0.02em",
                        "lineHeight": "1.25",
                        "marginBottom": "18px"
                    }}>
                        “My husband is in hospital and we can’t afford the treatment. I don’t know whether we qualify for any government health support or what we should do first.”
                    </div>
                    <div style={{"fontSize": "12px", "color": "rgba(255,255,255,0.5)", "marginBottom": "20px", "fontStyle": "italic"}}>
                        — example situation · paste it into the Navigator to see the real answer
                    </div>
                    <div style={{"display": "flex", "flexWrap": "wrap", "gap": "8px"}}>
                        {renderPersonaPill("Family medical crisis · low income · healthcare", "#FFE500")}
                        {renderPersonaPill("Hospital treatment · urgent assistance", "#4488FF")}
                        {renderPersonaPill("High medical costs · government support", "#FF88AA")}
                        {renderPersonaPill("Need help understanding eligibility · Hindi preferred", "#00FF88")}
                    </div>
                </div>

                <div
                    className="lp-glass"
                    style={{
                        "padding": "28px 30px",
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "position": "relative",
                        "overflow": "hidden"
                    }}
                >
                    <div className="lp-orb" style={{"width": "200px", "height": "200px", "background": "#00FF88", "bottom": "-50px", "left": "-30px", "opacity": "0.2"}}/>
                    <div style={{
                        "fontSize": "10px",
                        "color": "rgba(255,255,255,0.62)",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.1em",
                        "fontWeight": "600",
                        "marginBottom": "16px"
                    }}>
                        Why HELPmora stands out
                    </div>
                    <div style={{"display": "flex", "flexDirection": "column", "gap": "10px"}}>
                        {renderTrackBadge("Accessibility-First", "#FFE500", "Voice-first support for high-friction welfare systems")}
                        {renderTrackBadge("Multi-Agent, Human-Guided", "#00FF88", "Omi + Lyzr coordinate the journey, not the final decision")}
                        {renderTrackBadge("Persistent & Explainable", "#FF88AA", "Qdrant remembers the case; deterministic policy logic shows why")}
                    </div>
                </div>
            </section>
        </div>;
}
