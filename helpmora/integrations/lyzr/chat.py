"""Direct inference with deployed Lyzr Agent Studio."""

import json
import logging
import os
import time
import urllib.request
from typing import Any, Dict

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

logger = logging.getLogger("helpmora.integrations.lyzr.chat")

_session = None


def _get_session():
    global _session
    if _HAS_REQUESTS:
        if _session is None:
            _session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=5,
                pool_maxsize=10,
                max_retries=1,
            )
            _session.mount("https://", adapter)
            _session.mount("http://", adapter)
        return _session
    return None


_LYZR_CACHE: Dict[str, Dict[str, Any]] = {}

FAST_DOMAIN_ANSWERS = {
    "food": (
        "I'm HELPmora. Under the **Pradhan Mantri Garib Kalyan Anna Yojana (PMGKAY)**, "
        "eligible families receive 5 kg of free food grains per person each month through the National Food Security Act (NFSA). "
        "Antyodaya Anna Yojana (AAY) cardholders receive 35 kg per family. "
        "You can collect your allocation from any Fair Price Shop using your Aadhaar-linked Ration Card."
    ),
    "housing": (
        "I'm HELPmora. Under the **Pradhan Mantri Awas Yojana (PMAY-Urban & PMAY-Gramin)**, "
        "eligible low-income and EWS families can receive financial subsidies for pucca house construction or interest subsidies under CLSS. "
        "Applications can be filed online at pmaymis.gov.in or through your nearest Common Service Centre (CSC) with your Aadhaar, bank details, and income certificate."
    ),
    "health": (
        "I'm HELPmora. Under **Ayushman Bharat PM-JAY**, eligible families receive cashless healthcare cover up to ₹5 Lakh per family per year "
        "across empaneled public and private hospitals nationwide. For immediate doctor consultations from home, you can also access **eSanjeevani Teleconsultation** (esanjeevani.mohfw.gov.in) for free OPD consultations."
    ),
    "legal": (
        "I'm HELPmora. Under the Legal Services Authorities Act (NALSA), free legal aid is guaranteed to women, children, SC/ST citizens, "
        "custody persons, and citizens whose annual income is within statutory limits. You can reach the **National Legal Aid Helpline at 15100** "
        "or visit your local District Legal Services Authority (DLSA) at the district court."
    ),
    "education": (
        "I'm HELPmora. For higher education support, the **PM Vidyalaxmi Scheme** and Central Sector Interest Subsidy (CSIS) provide collateral-free educational loans "
        "with interest subsidy for students from economically weaker sections. Applications can be submitted through the Vidya Lakshmi Portal (vidyalakshmi.co.in)."
    ),
    "pension": (
        "I'm HELPmora. Under the **National Social Assistance Programme (NSAP)**, the Indira Gandhi National Old Age Pension Scheme (IGNOAPS) provides monthly financial support "
        "to senior citizens aged 60 and above living below the poverty line. Applications can be submitted through your local Gram Panchayat or Municipal office."
    ),
    "citizenship": (
        "Understood! As an Indian citizen or resident with valid identity documentation (such as Aadhaar or Ration Card), "
        "you are eligible to access Central and State government welfare schemes, healthcare subsidies, and citizen services. "
        "Please select the welfare category or tell me what assistance you need."
    ),
    "hostel": (
        "Under the **Working Women Hostel Scheme (Sakhi Niwas)**, safe and affordable hostel accommodation is provided to working women, "
        "including women undergoing job training. You can apply directly through the Ministry of Women and Child Development or your local urban development authority."
    ),
}


def query_lyzr_agent(message: str, user_id: str = "futurexprime21@gmail.com", session_id: str = "") -> Dict[str, Any]:
    t0 = time.perf_counter()
    api_key = os.environ.get("LYZR_API_KEY", "sk-default-w7SoWn4HYhHolxzKNJsQoXiXHX302Op3").strip()
    agent_id = os.environ.get("LYZR_MANAGER_AGENT_ID", "6acb17ec038b7bf79ea36a00").strip()
    uid = user_id or "futurexprime21@gmail.com"
    sid = session_id or f"{agent_id}-default"
    msg_clean = message.strip()
    msg_lower = msg_clean.lower()

    # 0. Intercept greetings with a welcoming message and overview of capabilities
    try:
        try:
            from engine.guardrails import is_greeting, GREETING_WELCOME_REPLY
        except ImportError:
            from helpmora.engine.guardrails import is_greeting, GREETING_WELCOME_REPLY
        if is_greeting(msg_clean):
            return {
                "ok": True,
                "agent_id": agent_id,
                "response": GREETING_WELCOME_REPLY,
                "error": "",
                "user_id": uid,
                "session_id": sid,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            }
    except Exception:
        pass

    # 0b. Intercept revert / step back / change requests
    try:
        try:
            from engine.guardrails import is_revert_intent, REVERT_WELCOME_REPLY
        except ImportError:
            from helpmora.engine.guardrails import is_revert_intent, REVERT_WELCOME_REPLY
        if is_revert_intent(msg_clean):
            return {
                "ok": True,
                "agent_id": agent_id,
                "response": REVERT_WELCOME_REPLY,
                "error": "",
                "user_id": uid,
                "session_id": sid,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            }
    except Exception:
        pass

    # 1. Intercept out-of-context queries
    try:
        try:
            from engine.guardrails import is_out_of_context, OUT_OF_CONTEXT_REPLY
        except ImportError:
            from helpmora.engine.guardrails import is_out_of_context, OUT_OF_CONTEXT_REPLY
        if is_out_of_context(msg_clean):
            return {
                "ok": True,
                "agent_id": agent_id,
                "response": OUT_OF_CONTEXT_REPLY,
                "error": "",
                "user_id": uid,
                "session_id": sid,
                "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
            }
    except Exception:
        pass

    # 2. Check LRU in-memory cache
    if msg_lower in _LYZR_CACHE:
        hit = dict(_LYZR_CACHE[msg_lower])
        hit["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return hit

    # 3. Fast-track high-frequency standard welfare queries
    fast_resp = None
    if any(k in msg_lower for k in ["food", "ration", "pmgkay", "grain", "hunger"]):
        fast_resp = FAST_DOMAIN_ANSWERS["food"]
    elif any(k in msg_lower for k in ["doctor", "health", "ayushman", "esanjeevani", "hospital", "medicine"]):
        fast_resp = FAST_DOMAIN_ANSWERS["health"]
    elif any(k in msg_lower for k in ["hostel", "sakhi niwas", "working women hostel"]):
        fast_resp = FAST_DOMAIN_ANSWERS["hostel"]
    elif any(k in msg_lower for k in ["housing", "shelter", "pmay", "house", "evict", "rent", "stay tonight", "nowhere to stay"]):
        fast_resp = FAST_DOMAIN_ANSWERS["housing"]
    elif any(k in msg_lower for k in ["lawyer", "legal", "nalsa", "dlsa", "court", "attorney"]):
        fast_resp = FAST_DOMAIN_ANSWERS["legal"]
    elif any(k in msg_lower for k in ["pension", "old age", "elderly", "ignaps", "senior citizen"]):
        fast_resp = FAST_DOMAIN_ANSWERS["pension"]
    elif any(k in msg_lower for k in ["study loan", "education loan", "vidyalaxmi", "college loan", "education", "study", "scholarship", "loan"]):
        fast_resp = FAST_DOMAIN_ANSWERS["education"]
    elif any(k in msg_lower for k in ["indian citizen", "citizen", "citizenship", "aadhaar", "aadhar card", "ration card"]):
        fast_resp = FAST_DOMAIN_ANSWERS["citizenship"]

    if fast_resp and len(msg_clean) < 60:
        result = {
            "ok": True,
            "agent_id": agent_id,
            "response": fast_resp,
            "error": "",
            "user_id": uid,
            "session_id": sid,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 1),
        }
        _LYZR_CACHE[msg_lower] = result
        return result

    # 4. Query Lyzr Cloud Agent with concise preamble
    url = "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    context_preamble = (
        "[System: You are HELPmora, expert in Indian social welfare schemes and legal aid. "
        "Keep answers concise, actionable, and strictly on Indian welfare/legal assistance.]\n\n"
    )
    payload = {
        "user_id": uid,
        "agent_id": agent_id,
        "session_id": sid,
        "message": f"{context_preamble}{msg_clean}",
    }

    resp_text = ""
    ok = False
    err_msg = ""

    sess = _get_session()
    if sess is not None:
        try:
            resp = sess.post(url, json=payload, headers=headers, timeout=12)
            if resp.status_code == 200:
                res_obj = resp.json()
                resp_text = str(res_obj.get("response", "")).strip()
                ok = True
            else:
                err_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as ex:
            err_msg = str(ex)
            logger.warning(f"Lyzr Studio query error: {ex}")
    else:
        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                body = response.read().decode("utf-8")
                res_obj = json.loads(body)
                resp_text = str(res_obj.get("response", "")).strip()
                ok = True
        except Exception as ex:
            err_msg = str(ex)
            logger.warning(f"Lyzr Studio query error: {ex}")

    latency_ms = round((time.perf_counter() - t0) * 1000.0, 1)

    result = {
        "ok": ok,
        "agent_id": agent_id,
        "response": resp_text or fast_resp or "",
        "error": err_msg,
        "user_id": uid,
        "session_id": sid,
        "latency_ms": latency_ms,
    }
    if ok and resp_text:
        _LYZR_CACHE[msg_lower] = result
    return result
