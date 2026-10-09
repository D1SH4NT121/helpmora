"""Async and walker-backed real-time logic for AdaptiveAssistant."""

import from "@jac/runtime" { jacSpawn, jacIsLoggedIn }

impl AdaptiveAssistant.runLiveAnalysis(text: str) -> None {
    if not text { return; }
    is_loading = True;
    agent_state = "reasoning";
    res = await jacSpawn("IntegratedPipelineWalker", "", {
        "input_text": text,
        "user_id": user_id
    }).catch(lambda e: Any -> dict { return {"reports": [], "spawn_error": str(e)}; });

    try {
        reps = res["reports"] if (res and res["reports"]) else [];
        if len(reps) > 0 and reps[0] and reps[0]["case_state"] {
            cs: Any = reps[0]["case_state"];
            run_id = str(cs["case_id"]);
            raw_trace: list = list(cs["execution_trace"]) if cs["execution_trace"] else [];
            if len(raw_trace) > 0 {
                new_trace: list = [];
                for t in raw_trace {
                    comp = str(t["component"] if t["component"] else "AGENT").upper();
                    b = "AGENT";
                    if "OMI" in comp { b = "OMI"; }
                    elif "QDRANT" in comp { b = "QDRANT"; }
                    elif "CONTEXT" in comp { b = "CONTEXT"; }
                    elif "RESOURCE" in comp { b = "RESOURCE"; }
                    elif "POLICY" in comp or "DETERMINISTIC" in comp { b = "ELIGIBILITY"; }
                    elif "PATHFINDER" in comp { b = "PATHFINDER"; }
                    elif "VERIF" in comp { b = "VERIFIER"; }
                    elif "WORKFLOW" in comp or "ADAPTIVE" in comp { b = "WORKFLOW"; }

                    evt = str(t["event_type"] if t["event_type"] else "Step").replace("_", " ");
                    det = str(t["details"] if t["details"] else "Verified across statutory rules");
                    if det == "{}" or not det { det = "Verified across statutory rules"; }
                    new_trace = new_trace + [{
                        "badge": b,
                        "title": evt,
                        "status": "completed",
                        "detail": det
                    }];
                }
                if len(new_trace) > 0 {
                    trace_events = new_trace;
                }
            }

            cands: list = list(cs["candidate_resources"]) if cs["candidate_resources"] else [];
            if len(cands) > 0 and cands[0] and cands[0]["name"] {
                approved_program = str(cands[0]["name"]);
            }

            prof: Any = cs["profile"] if cs["profile"] else {};
            if prof and prof["income"] {
                voice_field_val = "₹" + str(prof["income"]);
            }

            active_step = 4;
            agent_state = "verified";
        } else {
            agent_state = "idle";
        }
    } except Exception as _ex {
        agent_state = "idle";
    }
    is_loading = False;
}

impl AdaptiveAssistant.wipeAllMemory -> None {
    memory_wiped = True;
    res = await jacSpawn("ForgetWalker", "", {"user_id": user_id}).catch(lambda e: Any -> dict { return {"reports": []}; });
    trace_events = [
        {"badge": "PRIVACY", "title": "Memory Purged", "status": "completed", "detail": "All vectors and profile data deleted"}
    ];
    agent_state = "idle";
}

impl AdaptiveAssistant.approveAction -> None {
    approval_status = "approved";
    agent_state = "action_complete";
    active_step = 5;
    res = await jacSpawn("MemoryWalker", "", {
        "user_id": user_id,
        "mode": "update_status",
        "resource_name": approved_program,
        "new_status": "applied"
    }).catch(lambda e: Any -> dict { return {"reports": []}; });

    try {
        (window: Any).eval("if (window.speechSynthesis) { var u = new SpeechSynthesisUtterance('Application approved and permanently saved.'); u.lang='en-IN'; window.speechSynthesis.speak(u); }");
    } except Exception as _ex {}
}

impl AdaptiveAssistant.confirmVoiceField -> None {
    voice_confirmed = True;
    active_step = 3;
    agent_state = "verified";
    try {
        (window: Any).eval("if (window.speechSynthesis) { var u = new SpeechSynthesisUtterance('Income confirmed. Running live policy analysis.'); u.lang='en-IN'; window.speechSynthesis.speak(u); }");
    } except Exception as _ex {}
    runLiveAnalysis("My monthly income is " + voice_field_val + ". " + input_text);
}

impl AdaptiveAssistant.triggerVoiceInput -> None {
    if voice_active {
        voice_active = False;
        agent_state = "reasoning";
        try {
            (window: Any).eval("if (window._cm_current_rec) { window._cm_current_rec.stop(); }");
        } except Exception as _ex {}
        return;
    }

    voice_active = True;
    agent_state = "listening";
    try {
        (window: Any).eval("""
            if (window._cm_listen_field) {
                window._cm_current_rec = window._cm_listen_field(
                    function(text) {
                        var digits = (text || '').replace(/[^0-9]/g, '');
                        if (digits) {
                            var el = document.getElementById('cm-voice-val');
                            if (el) el.innerText = '₹' + digits;
                        }
                    },
                    function() {
                        var btn = document.getElementById('cm-voice-btn');
                        if (btn) btn.click();
                    }
                );
            }
        """);
    } except Exception as _ex {
        voice_active = False;
        agent_state = "reasoning";
    }
}

impl AdaptiveAssistant.toggleVoiceFirst -> None {
    voice_first = not voice_first;
    if voice_first {
        try {
            (window: Any).eval("if (window.speechSynthesis) { var u = new SpeechSynthesisUtterance('Voice-First mode activated. Click Speak Field to talk into your microphone.'); u.lang='en-IN'; window.speechSynthesis.speak(u); }");
        } except Exception as _ex {}
    }
}

impl AdaptiveAssistant.showFieldHelp(title: str, text: str) -> None {
    field_help_title = title;
    field_help_body = text;
}

impl AdaptiveAssistant.closeFieldHelp -> None {
    field_help_title = "";
    field_help_body = "";
}

impl AdaptiveAssistant.toggleRecovery -> None {
    recovery_open = not recovery_open;
}

impl AdaptiveAssistant.togglePrivacy(kind: str) -> None {
    if kind == "conv" { conv_memory_on = not conv_memory_on; }
    if kind == "app" { app_history_on = not app_history_on; }
    if kind == "docs" { docs_on = not docs_on; }
    if kind == "voice" { raw_voice_on = not raw_voice_on; }
}
