"""HELPmora chat — instant deterministic answers, narrated in the background.

Left: the conversation. Each agent reply is a structured result — the user's
own words highlighted where facts were extracted, explainable match cards
(eligibility, approval odds with a credible interval, per-criterion reasons,
"you'd qualify if…"), an ordered plan, escape routes, one follow-up question
with quick replies, and a latency waterfall of the turn.

Right: what the agent currently knows about the case, and each walker's
real timing from the last turn's trace.
"""
sv import from walkers.intake { IntakeWalker }
sv import from walkers.narrate { NarrateWalker }
sv import from walkers.forget { ForgetWalker }
import from "@jac/runtime" { jacSpawn, jacIsLoggedIn }

# The id of the chat request waiting for an answer (see sendMessage).
glob CM_INFLIGHT: dict = {"id": ""};

# Follow-up questions answered with a quick Yes / No (must live in the .cl.jac:
# globs in .impl.jac files don't reach the client bundle).
glob YES_NO_KEYS: list = ["homeless", "veteran", "disability", "dv", "young_child", "children", "eviction"];

def:pub ChatPane(
    user_id: str,
    on_walker_event: Any,
    auth_ready: Any = None,
    walker_events: list = [],
    platform: Any = None
) -> JsxElement {
    has messages: list[dict] = [],
        input_val: str = "",
        is_loading: bool = False,
        profile_ctx: Any = {},
        pending_question: str = "",
        last_trace: Any = {},
        open_key: str = "",
        waterfall_open: int = -1,
        narr_tick: float = 0.0,
        # Mutated in place by background narration; narr_tick forces a re-render.
        narrations: dict = {},
        # Local offices from HUD / HRSA open data, keyed by bot message id.
        locals: dict = {},
        lang_label: str = "",
        # Reply language picked by the user ("auto" = detect from the message).
        pref_lang: str = "auto",
        # Full-answer translations (LocalizeWalker), keyed by bot message id.
        localized: dict = {},
        # "Delete my data": "" | deleting | done | failed.
        forget_state: str = "",
        # Bot message id whose English original is expanded.
        en_open: str = "",
        # Private session: nothing stays in this browser after the tab closes.
        private_on: bool = False,
        is_listening: bool = False,
        voice_status: str = "",
        voice_modal_open: bool = False;

    can with entry {
        seed = [{
            "role": "bot",
            "kind": "text",
            "id": "welcome",
            "text": "Hi, I'm HELPmora. Tell me what's going on, in your own words and in your own language, and I'll find the housing, food, healthcare or legal programs you can use and show exactly why. In 51 languages the whole answer — programs, next steps and my follow-up questions — comes back in yours right away; in 60 more I add a translation a few seconds later, and for languages machines can't translate yet I give you an interpreter card. Pick yours at the top if I get it wrong.",
            "suggestions": [
                "I'm 72, on $1200/month Social Security, my landlord is trying to evict me illegally.",
                "Mi familia y yo no hemos comido en 2 días. Estamos en Texas.",
                "I'm a single mother with 2 kids in Houston. I earn $1,800/month and need housing help.",
                "我今天在哪里可以得到食物？我没有工作。"
            ]
        }];
        # Every visit opens on this welcome and its examples. Nothing about an
        # earlier case is put on screen unasked: on a shared device the next
        # person would see it. The saved case is in the Action Plan tab.
        messages = seed;
        try {
            saved = localStorage.getItem("cm_lang");
            if saved { pref_lang = saved; }
            if sessionStorage.getItem("cm_private") == "1" { private_on = True; }
        } except Exception as _ex {}
        try {
            if not window._cm_voice_bridge {
                window.eval("""
                    window._cm_voice_bridge = {
                        isListening: false,
                        status: '',
                        rec: null,
                        start: function(lang) {
                            var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
                            if (!SR) {
                                window._cm_voice_bridge.status = 'Microphone speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari, or click an Omi Voice preset.';
                                return false;
                            }
                            try {
                                if (window._cm_voice_bridge.rec) {
                                    try { window._cm_voice_bridge.rec.abort(); } catch(e) {}
                                }
                                var rec = new SR();
                                window._cm_voice_bridge.rec = rec;
                                window._cm_voice_bridge.isListening = true;
                                window._cm_voice_bridge.status = 'Listening... Speak now into your microphone';
                                rec.continuous = true;
                                rec.interimResults = true;
                                rec.maxAlternatives = 1;

                                var speechLang = 'en-US';
                                if (lang === 'hi') speechLang = 'hi-IN';
                                else if (lang === 'es') speechLang = 'es-ES';
                                else if (lang === 'zh') speechLang = 'zh-CN';
                                else if (lang === 'ta') speechLang = 'ta-IN';
                                else if (lang && lang.length === 2) speechLang = lang;
                                rec.lang = speechLang;

                                rec.onstart = function() {
                                    window._cm_voice_bridge.isListening = true;
                                    window._cm_voice_bridge.status = 'Listening... Speak now';
                                    if (window._cm_on_voice_status) { window._cm_on_voice_status('Listening... Speak now', true); }
                                };
                                rec.onresult = function(event) {
                                    var transcript = '';
                                    for (var i = 0; i < event.results.length; i++) {
                                        transcript += event.results[i][0].transcript;
                                    }
                                    if (transcript) {
                                        if (window._cm_on_voice) {
                                            window._cm_on_voice(transcript);
                                        }
                                        var inputEl = document.querySelector('.cm-input');
                                        if (inputEl) {
                                            if (inputEl._valueTracker) {
                                                inputEl._valueTracker.setValue('');
                                            }
                                            var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                                            nativeSetter.call(inputEl, transcript);
                                            inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                                            inputEl.dispatchEvent(new Event('change', { bubbles: true }));
                                        }
                                        window._cm_voice_bridge.status = 'Hearing: "' + transcript + '"';
                                    }
                                };
                                rec.onerror = function(event) {
                                    window._cm_voice_bridge.isListening = false;
                                    var err = event.error || 'error';
                                    var msg = 'Voice recognition: ' + err;
                                    if (err === 'not-allowed') {
                                        msg = 'Microphone access blocked. Please grant microphone permission in your browser address bar.';
                                    } else if (err === 'no-speech') {
                                        msg = 'No speech detected. Speak clearly into your microphone.';
                                    }
                                    window._cm_voice_bridge.status = msg;
                                    if (window._cm_on_voice_status) { window._cm_on_voice_status(msg, false); }
                                };
                                rec.onend = function() {
                                    window._cm_voice_bridge.isListening = false;
                                    if (window._cm_on_voice_status) { window._cm_on_voice_status('', false); }
                                };
                                rec.start();
                                return true;
                            } catch (err) {
                                window._cm_voice_bridge.isListening = false;
                                var msg = 'Microphone activation failed: ' + (err.message || err);
                                window._cm_voice_bridge.status = msg;
                                if (window._cm_on_voice_status) { window._cm_on_voice_status(msg, false); }
                                return false;
                            }
                        },
                        stop: function() {
                            window._cm_voice_bridge.isListening = false;
                            if (window._cm_voice_bridge.rec) {
                                try { window._cm_voice_bridge.rec.stop(); } catch(e) {}
                                window._cm_voice_bridge.rec = null;
                            }
                            if (window._cm_on_voice_status) { window._cm_on_voice_status('', false); }
                        }
                    };
                """);
            }
            window._cm_on_voice = lambda txt: str {
                input_val = txt;
                voice_status = 'Hearing: "' + txt + '"';
            };
            window._cm_on_voice_status = lambda st: str, listening: bool {
                voice_status = st;
                is_listening = listening;
            };
        } except Exception as _ex {}
    }

    # Keep the newest turn in view (also when a narration lands).
    can with [messages, narr_tick] entry {
        try {
            thread = document.querySelector(".cm-thread");
            if thread { thread.scrollTop = thread.scrollHeight; }
        } except Exception as _ex {}
    }

    # The input is disabled while a turn runs, which drops keyboard focus to
    # the page. Put it back when the answer lands, so a keyboard or screen-
    # reader user can reply without hunting for the box (not on first load).
    can with [is_loading] entry {
        try {
            if (not is_loading) and len(messages) > 1 and (document.activeElement == document.body or not document.activeElement) {
                box = document.querySelector(".cm-input");
                if box { box.focus(); }
            }
        } except Exception as _ex {}
    }

    async def sendMessage(text_override: str = "", answering: str = "", display: str = "", pin: bool = False) -> None;
    async def safeSpawn(walker_name: str, fields: dict) -> Any;
    async def narrate(msg_id: str, data: Any, user_text: str) -> None;
    async def findLocal(msg_id: str, data: Any) -> None;
    async def localize(msg_id: str, data: Any) -> None;
    def renderInterpreter(card: Any, open_default: bool) -> JsxElement;
    def renderLangPicker -> JsxElement;
    def renderLocal(loc: Any) -> JsxElement;
    def resetCase -> None;
    async def forgetMe -> None;
    def setPrivate(on: bool) -> None;
    def renderPrivacy -> JsxElement;
    def spansToEvents(spans: list) -> list;
    def fmtMs(ms: float) -> str;
    def tierStyle(tier: str, ui: Any) -> dict;
    def L(ui: Any, key: str, fallback: str) -> str;
    def renderRich(text: str) -> JsxElement;
    def renderUserText(text: str, evidence: list) -> JsxElement;
    def renderMessage(msg: dict, idx: int, is_last: bool) -> JsxElement;
    def renderResult(msg: dict, idx: int, is_last: bool) -> JsxElement;
    def renderMatchCard(m: Any, idx: int, j: int, ui: Any) -> JsxElement;
    def renderPlan(plan: Any, ui: Any) -> JsxElement;
    def renderRoute(route: Any, idx: int) -> JsxElement;
    def renderWaterfall(trace: Any, narration: Any, idx: int) -> JsxElement;
    def quickOptions(key: str, es: bool) -> list;
    def renderQuickReplies(q: Any, lang: str, labels: list, q_text: str, affects_text: str) -> JsxElement;
    async def localizeStrings(msg_id: str, data: Any) -> None;
    def renderChip(label: str, payload: str, answering: str) -> JsxElement;
    def renderProfilePanel -> JsxElement;
    def renderPipeline -> JsxElement;
    def toggleVoice -> None;
    def renderVoiceModal -> JsxElement;

    return
        <div className="cm-chat-grid">
            {renderVoiceModal()}
            <div className="cm-panel cm-chat-col">
                <div className="cm-chat-head">
                    <div style={{"flex": "1", "minWidth": "0"}}>
                        <h2 style={{"fontSize": "14px", "fontWeight": "600", "margin": "0"}}>HELPmora Navigator</h2>
                        <div className="cm-muted" style={{"fontSize": "11px", "marginTop": "2px"}}>
                            Deterministic eligibility engine · 2026 federal rules · 51 machine-drafted languages, 111 selectable · 1 LLM call per turn, off the critical path
                        </div>
                    </div>
                    {is_loading and <div className="cm-badge badge-glow"><span className="cm-dot-live"/>Scoring 40 programs…</div>}
                    {renderLangPicker()}
                    <button className="cm-ghost-btn" onClick={lambda _e: MouseEvent { resetCase(); }} title="Start a new case">New case</button>
                </div>
                <div className="cm-thread" role="log" aria-live="polite" aria-relevant="additions" aria-label="Conversation" aria-busy={is_loading} tabIndex={0}>
                    {[renderMessage(messages[i], i, (i == len(messages) - 1) and (not is_loading)) for i in range(len(messages))]}
                    {is_loading and <div className="cm-row">
                        <div className="cm-avatar">CM</div>
                        <div className="cm-typing" role="status"><span aria-hidden="true"/><span aria-hidden="true"/><span aria-hidden="true"/><span className="cm-sr-only">Working on your answer…</span></div>
                    </div>}
                </div>
                {(is_listening or voice_status) and <div style={{
                    "padding": "7px 14px",
                    "background": ("rgba(255, 68, 68, 0.14)" if is_listening else "rgba(255, 229, 0, 0.08)"),
                    "borderTop": ("0.5px solid rgba(255, 68, 68, 0.3)" if is_listening else "0.5px solid rgba(255, 229, 0, 0.2)"),
                    "fontSize": "12px",
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "color": ("#FF8080" if is_listening else "#FFE500")
                }}>
                    <span>
                        {(is_listening and <span className="cm-dot-live" style={{"background": "#FF4444", "display": "inline-block", "marginRight": "8px"}}/>)}
                        {voice_status}
                    </span>
                    <div style={{"display": "flex", "gap": "6px"}}>
                        {is_listening and <button
                            onClick={lambda _e: MouseEvent { toggleVoice(); }}
                            style={{"background": "#FF4444", "color": "#000", "border": "none", "borderRadius": "4px", "padding": "2px 8px", "fontSize": "11px", "fontWeight": "600", "cursor": "pointer"}}
                        >
                            Done
                        </button>}
                        <button
                            onClick={lambda _e: MouseEvent { voice_status = ""; }}
                            style={{"background": "none", "color": "rgba(255, 255, 255, 0.5)", "border": "none", "fontSize": "11px", "cursor": "pointer"}}
                        >
                            ✕
                        </button>
                    </div>
                </div>}
                <div className="cm-composer">
                    <input
                        aria-label="Your message"
                        value={input_val}
                        onChange={lambda e: ChangeEvent { input_val = e.target.value; }}
                        onKeyDown={lambda e: KeyboardEvent {
                            if e.key == "Enter" { sendMessage(); }
                        }}
                        placeholder={("Answer the question above, or describe anything else…" if pending_question else "Describe your situation in any language…")}
                        disabled={is_loading}
                        maxLength={4000}
                        className="cm-input"
                    />
                    <button
                        onClick={lambda _e: MouseEvent { toggleVoice(); }}
                        disabled={is_loading}
                        className={"cm-ghost-btn" + (" cm-voice-btn-active" if is_listening else "")}
                        style={{
                            "marginRight": "4px",
                            "padding": "6px 11px",
                            "fontSize": "13px",
                            "background": ("rgba(255, 68, 68, 0.22)" if is_listening else "rgba(255, 255, 255, 0.04)"),
                            "color": ("#FF4444" if is_listening else "rgba(255, 255, 255, 0.75)"),
                            "border": ("0.5px solid #FF4444" if is_listening else "0.5px solid rgba(255, 255, 255, 0.12)"),
                            "fontWeight": ("600" if is_listening else "400")
                        }}
                        aria-label={("Stop recording" if is_listening else "Voice input (Omi)")}
                        title={("Stop Listening" if is_listening else "Voice Input (Click to speak via Microphone)")}
                    >
                        {("🔴 Stop" if is_listening else "🎙️ Voice")}
                    </button>
                    <button
                        onClick={lambda _e: MouseEvent { voice_modal_open = not voice_modal_open; }}
                        className="cm-ghost-btn"
                        style={{"marginRight": "6px", "padding": "6px 8px", "fontSize": "12px"}}
                        aria-label="Omi voice presets"
                        title="Omi Voice Presets & Scenarios"
                    >
                        ⚡ Omi
                    </button>
                    <button
                        onClick={lambda _e: MouseEvent { sendMessage(); }}
                        disabled={is_loading}
                        className={("cm-send cm-send-on" if (input_val and (not is_loading)) else "cm-send")}
                        aria-label="Send message"
                        title="Send"
                    >
                        →
                    </button>
                </div>
                <p className="cm-safety-line">
                    {"In danger now: "}<a href="tel:112">112 (Emergency)</a>
                    {" · Women Helpline: "}<a href="tel:181">181</a>
                    {" · Childline: "}<a href="tel:1098">1098</a>
                    {" · Mental Health (Tele-MANAS): "}<a href="tel:14416">14416</a>
                    {" · Cyber Crime: "}<a href="tel:1930">1930</a>
                </p>
                {renderPrivacy()}
            </div>
            <div className="cm-side" role="region" aria-label="Case file and pipeline" tabIndex={0}>
                {renderProfilePanel()}
                {renderPipeline()}
            </div>
        </div>;
}
