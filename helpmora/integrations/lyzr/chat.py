"""Direct inference with deployed Lyzr Agent Studio."""

import json
import logging
import os
import time
import urllib.request
from typing import Any, Dict

logger = logging.getLogger("helpmora.integrations.lyzr.chat")


def query_lyzr_agent(message: str, user_id: str = "futurexprime21@gmail.com", session_id: str = "") -> Dict[str, Any]:
    t0 = time.perf_counter()
    api_key = os.environ.get("LYZR_API_KEY", "sk-default-w7SoWn4HYhHolxzKNJsQoXiXHX302Op3").strip()
    agent_id = os.environ.get("LYZR_MANAGER_AGENT_ID", "6acb17ec038b7bf79ea36a00").strip()
    uid = user_id or "futurexprime21@gmail.com"
    sid = session_id or f"{agent_id}-default"

    url = "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    payload = {
        "user_id": uid,
        "agent_id": agent_id,
        "session_id": sid,
        "message": str(message),
    }

    resp_text = ""
    ok = False
    err_msg = ""

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
