"""HELPmora Logo — "The Guided Thread"

Single source of truth component for the HELPmora logo, wordmark, and motion system.
Preserves the exact master path geometry, node coordinates, brand colors, 6-phase
intro animation, periodic idle system, and reactive states (listening, reasoning,
memory, verified, action_complete).
"""

def:pub HELPmoraLogo(
    size: int = 40,
    show_wordmark: bool = False,
    show_tagline: bool = False,
    state: str = "idle",
    animated: bool = True,
    instance_id: str = "logo",
    class_name: str = ""
) -> JsxElement {
    has is_animating: bool = True,
        anim_key: int = 0;

    can with entry {
        if not animated {
            is_animating = False;
        } else {
            setTimeout(lambda { is_animating = False; }, 4200);
        }
    }

    def replay {
        anim_key = anim_key + 1;
        is_animating = True;
        setTimeout(lambda { is_animating = False; }, 4200);
    }

    thread_grad_id = instance_id + "_threadGrad_" + str(anim_key);
    beacon_grad_id = instance_id + "_beaconGrad_" + str(anim_key);
    glow_filter_id = instance_id + "_glowFilter_" + str(anim_key);

    wordmark_size = max(14, int(size * 0.44));
    tagline_size = max(11, int(size * 0.16));

    anim_class = "hm-animating" if is_animating else "hm-idle";
    state_class = "hm-state-" + state;

    return
        <div
            key={instance_id + "_" + str(anim_key)}
            className={"hm-logo-container " + anim_class + " " + state_class + " " + class_name}
            onClick={lambda _e: MouseEvent { replay(); }}
            title="HELPmora — From your problem to your next step (click to replay animation)"
            style={{
                "display": "inline-flex",
                "alignItems": "center",
                "cursor": "pointer",
                "gap": str(max(6, int(size * 0.22))) + "px"
            }}
        >
            <svg
                key={instance_id + "_svg_" + str(anim_key)}
                viewBox="0 0 200 200"
                width={str(size) + "px"}
                height={str(size) + "px"}
                className={"hm-logo-svg " + anim_class + " " + state_class}
                xmlns="http://www.w3.org/2000/svg"
                role="img"
                aria-label="HELPmora Guided Thread Logo"
                style={{
                    "display": "block",
                    "overflow": "visible",
                    "flexShrink": "0"
                }}
            >
                <defs>
                    <linearGradient id={thread_grad_id} x1="34" y1="154" x2="174" y2="62" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stopColor="#0B132B"/>
                        <stop offset="25%" stopColor="#034B75"/>
                        <stop offset="50%" stopColor="#0C847A"/>
                        <stop offset="75%" stopColor="#059669"/>
                        <stop offset="100%" stopColor="#10B981"/>
                    </linearGradient>

                    <linearGradient id={beacon_grad_id} x1="165" y1="49" x2="183" y2="67" gradientUnits="userSpaceOnUse">
                        <stop offset="0%" stopColor="#FBBF24"/>
                        <stop offset="50%" stopColor="#F59E0B"/>
                        <stop offset="100%" stopColor="#D97706"/>
                    </linearGradient>

                    <filter id={glow_filter_id} x="-30%" y="-30%" width="160%" height="160%">
                        <feGaussianBlur stdDeviation="3.5" result="blur"/>
                        <feComposite in="SourceGraphic" in2="blur" operator="over"/>
                    </filter>
                </defs>

                <g className="hm-h-discovery">
                    <line x1="48" y1="72" x2="48" y2="134" stroke="#38BDF8" strokeWidth="2.5" strokeLinecap="round" opacity="0.4"/>
                    <line x1="48" y1="102" x2="152" y2="102" stroke="#38BDF8" strokeWidth="2.8" strokeLinecap="round" strokeDasharray="4 4" opacity="0.6"/>
                    <line x1="152" y1="72" x2="152" y2="130" stroke="#38BDF8" strokeWidth="2.5" strokeLinecap="round" opacity="0.4"/>
                </g>

                <path
                    className="hm-guided-thread"
                    d="M 34,154 C 44,154 48,148 48,134 L 48,72 C 48,46 72,46 80,66 L 86,110 C 92,122 108,122 114,110 L 120,66 C 128,46 152,46 152,72 L 152,130 C 152,154 174,148 174,114 L 174,62"
                    fill="none"
                    stroke={"url(#" + thread_grad_id + ")"}
                    strokeWidth="6.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />

                <circle className="hm-signal-tracer" r="3.5" fill="#FFFFFF" filter={"url(#" + glow_filter_id + ")"}/>

                <g className="hm-human-group">
                    <circle className="hm-human-aura" cx="34" cy="154" r="14" fill="rgba(12, 132, 122, 0.22)"/>
                    <circle className="hm-human-outer" cx="34" cy="154" r="6" fill="#0B132B" stroke="#034B75" strokeWidth="1.5"/>
                    <circle className="hm-human-inner" cx="34" cy="154" r="2.5" fill="#FFFFFF"/>
                </g>

                <g className="hm-nodes-group">
                    <g className="hm-node hm-node-1">
                        <circle cx="48" cy="102" r="5" fill="#0C847A" stroke="#0B132B" strokeWidth="1"/>
                        <circle cx="48" cy="102" r="2" fill="#FFFFFF"/>
                    </g>

                    <g className="hm-node hm-node-2">
                        <circle className="hm-node-memory-aura" cx="86" cy="110" r="12" fill="rgba(56, 189, 248, 0)"/>
                        <circle cx="86" cy="110" r="5" fill="#0C847A" stroke="#0B132B" strokeWidth="1"/>
                        <circle cx="86" cy="110" r="2" fill="#FFFFFF"/>
                    </g>

                    <g className="hm-node hm-node-3">
                        <circle cx="114" cy="110" r="5" fill="#059669" stroke="#0B132B" strokeWidth="1"/>
                        <circle cx="114" cy="110" r="2" fill="#FFFFFF"/>
                    </g>

                    <g className="hm-node hm-node-4">
                        <circle cx="152" cy="102" r="5" fill="#10B981" stroke="#0B132B" strokeWidth="1"/>
                        <circle cx="152" cy="102" r="2" fill="#FFFFFF"/>
                    </g>

                    <g className="hm-node hm-node-5">
                        <circle cx="166" cy="140" r="5" fill="#10B981" stroke="#0B132B" strokeWidth="1"/>
                        <circle cx="166" cy="140" r="2" fill="#FFFFFF"/>
                    </g>
                </g>

                <g className="hm-beacon-group">
                    <circle className="hm-beacon-halo" cx="174" cy="58" r="17" fill="rgba(245, 158, 11, 0.22)" filter={"url(#" + glow_filter_id + ")"}/>
                    <circle className="hm-beacon-outer" cx="174" cy="58" r="9" fill={"url(#" + beacon_grad_id + ")"} stroke="#FFFFFF" strokeWidth="1.5"/>
                    <circle className="hm-beacon-core" cx="174" cy="58" r="3.5" fill="#FFFBEB"/>
                    <path
                        className="hm-beacon-check"
                        d="M 170.5,58 L 173,60.5 L 177.5,55.5"
                        fill="none"
                        stroke="#FFFFFF"
                        strokeWidth="1.7"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                </g>
            </svg>

            {show_wordmark and
                <div
                    className="hm-wordmark-wrapper"
                    style={{
                        "display": "flex",
                        "flexDirection": "column",
                        "justifyContent": "center",
                        "textAlign": "left"
                    }}
                >
                    <div
                        className="hm-wordmark"
                        style={{
                            "display": "flex",
                            "alignItems": "baseline",
                            "lineHeight": "1",
                            "gap": "1px"
                        }}
                    >
                        <span
                            className="hm-wordmark-help"
                            style={{
                                "fontSize": str(wordmark_size) + "px",
                                "fontWeight": "800",
                                "letterSpacing": "-0.03em",
                                "color": "#FFFFFF"
                            }}
                        >
                            HELP
                        </span>
                        <span
                            className="hm-wordmark-mora"
                            style={{
                                "fontSize": str(wordmark_size) + "px",
                                "fontWeight": "400",
                                "letterSpacing": "-0.02em",
                                "color": "rgba(255,255,255,0.88)"
                            }}
                        >
                            mora
                        </span>
                        <span
                            className="hm-wordmark-dot"
                            style={{
                                "fontSize": str(wordmark_size) + "px",
                                "fontWeight": "800",
                                "color": "#F59E0B",
                                "marginLeft": "1px"
                            }}
                        >
                            .
                        </span>
                    </div>
                    {show_tagline and
                        <span
                            className="hm-tagline"
                            style={{
                                "fontSize": str(tagline_size) + "px",
                                "color": "rgba(255,255,255,0.58)",
                                "marginTop": "4px",
                                "letterSpacing": "0.01em",
                                "whiteSpace": "nowrap"
                            }}
                        >
                            From your problem to your next step.
                        </span>
                    }
                </div>
            }
        </div>;
}
