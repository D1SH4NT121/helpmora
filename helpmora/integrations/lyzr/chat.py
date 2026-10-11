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


def query_lyzr_agent(message: str, user_id: str = "futurexprime21@gmail.com", session_id: str = "") -> Dict[str, Any]:
    t0 = time.perf_counter()
    api_key = os.environ.get("LYZR_API_KEY", "sk-default-w7SoWn4HYhHolxzKNJsQoXiXHX302Op3").strip()
    agent_id = os.environ.get("LYZR_MANAGER_AGENT_ID", "6acb17ec038b7bf79ea36a00").strip()
    uid = user_id or "futurexprime21@gmail.com"
    sid = session_id or f"{agent_id}-default"

    # 0. Intercept out-of-context queries
    try:
        from helpmora.engine.guardrails import is_out_of_context, OUT_OF_CONTEXT_REPLY
        if is_out_of_context(message):
            logger.info("Out-of-context query intercepted: %s", message)
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

    url = "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    context_preamble = (
        "[System Guardrail: You are HELPmora, specialized exclusively in Indian social welfare schemes, "
        "government subsidies, and legal aid. Answer ONLY questions related to this project. If the question "
        "is general trivia, geography, or unrelated to welfare and legal aid, reply: 'I don't have knowledge of those things. "
        "I am HELPmora, specialized exclusively in Indian social welfare schemes, government assistance programs, and free legal aid navigation.']\n\n"
    )
    payload = {
        "user_id": uid,
        "agent_id": agent_id,
        "session_id": sid,
        "message": f"{context_preamble}{str(message)}",
    }

    resp_text = ""
    ok = False
    err_msg = ""

    sess = _get_session()
    if sess is not None:
        try:
            resp = sess.post(url, json=payload, headers=headers, timeout=25)
            if resp.status_code == 200:
                res_obj = resp.json()
                resp_text = str(res_obj.get("response", ""))
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
            with urllib.request.urlopen(req, timeout=30) as response:
                body = response.read().decode("utf-8")
                res_obj = json.loads(body)
                resp_text = str(res_obj.get("response", ""))
                ok = True
        except Exception as ex:
            err_msg = str(ex)
            logger.warning(f"Lyzr Studio query error: {ex}")

    latency_ms = round((time.perf_counter() - t0) * 1000.0, 1)

    return {
        "ok": ok,
        "agent_id": agent_id,
        "response": resp_text,
        "error": err_msg,
        "user_id": uid,
        "session_id": sid,
        "latency_ms": latency_ms,
    }
