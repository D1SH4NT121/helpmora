"""FastAPI / HTTP API endpoints for Omi, Qdrant, and Lyzr integrations."""

import json
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field

try:
    from helpmora.integrations.lyzr.client import get_lyzr_client
    from helpmora.integrations.omi.adapter import normalize_omi_event, validate_omi_auth
    from helpmora.integrations.qdrant.memory import get_memory_store
    from helpmora.orchestration.workflow import _ACTIVE_RUNS, get_workflow_manager
except ImportError:
    from integrations.lyzr.client import get_lyzr_client
    from integrations.omi.adapter import normalize_omi_event, validate_omi_auth
    from integrations.qdrant.memory import get_memory_store
    from orchestration.workflow import _ACTIVE_RUNS, get_workflow_manager

logger = logging.getLogger("helpmora.integrations.api")

router = APIRouter(prefix="/api")


# --- Pydantic Schemas ---

class HelpMoraRunRequest(BaseModel):
    user_id: str = Field(default="anonymous", description="User ID for multi-tenant isolation")
    text: str = Field(..., description="User query or voice transcript")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    language: Optional[str] = Field(default="en", description="Preferred language (en, hi)")


class MemoryRetrieveRequest(BaseModel):
    user_id: str
    query_text: Optional[str] = None
    memory_type: Optional[str] = None
    case_id: Optional[str] = None
    limit: Optional[int] = 10


class MemoryStoreRequest(BaseModel):
    user_id: str
    memory_type: str = "conversation"
    text: str
    case_id: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None
    language: Optional[str] = "en"
    visibility: Optional[str] = "private"


class WorkflowApproveRequest(BaseModel):
    run_id: str
    user_id: str
    action_index: Optional[int] = 0


class VoiceToFormRequest(BaseModel):
    text: str


class PrivacyUpdateRequest(BaseModel):
    user_id: str
    conversation_memory: Optional[bool] = None
    application_history: Optional[bool] = None
    documents: Optional[bool] = None
    raw_voice_retention: Optional[bool] = None


# --- Health Endpoint ---

@router.get("/integrations/health")
async def health_check():
    """Health check for external integrations without leaking secrets."""
    store = get_memory_store()
    lyzr = get_lyzr_client()

    qdrant_ok = False
    try:
        collections = store.client.get_collections().collections
        qdrant_ok = any(c.name == store.collection_name for c in collections)
    except Exception:
        qdrant_ok = False

    return {
        "status": "ok",
        "integrations": {
            "omi": {"status": "ready", "adapter": "active"},
            "qdrant": {"status": "ready" if qdrant_ok else "degraded", "collection": store.collection_name},
            "lyzr": {"status": "ready", "cloud_enabled": lyzr.is_cloud_enabled()},
            "helpmora_core": {"status": "ready", "resources": 40, "transitions": 26},
        }
    }


# --- Omi Endpoints ---

@router.post("/omi/events")
async def receive_omi_event(request: Request):
    """
    Omi webhook endpoint.
    Accepts raw Omi events, normalizes them, and runs the HELPmora pipeline.
    """
    headers = {k.decode("latin-1") if isinstance(k, bytes) else k: v.decode("latin-1") if isinstance(v, bytes) else v for k, v in request.headers.items()}
    token = request.query_params.get("token", "")

    if not validate_omi_auth(headers, token):
        raise HTTPException(status_code=401, detail="Unauthorized Omi webhook signature or secret.")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    is_valid, normalized, err_msg = normalize_omi_event(payload)
    if not is_valid:
        if err_msg == "duplicate_event":
            return {"ok": True, "status": "duplicate_ignored"}
        raise HTTPException(status_code=400, detail=f"Omi payload validation failed: {err_msg}")

    # Process normalized event through HELPmora pipeline
    wf = get_workflow_manager()
    state = wf.run_pipeline(
        user_id=normalized.user_id,
        input_text=normalized.text,
        session_id=normalized.session_id,
        source="omi",
        language=normalized.language,
    )

    return {
        "ok": True,
        "run_id": state.case_id,
        "session_id": state.session_id,
        "status": state.status,
        "normalized_input": normalized.to_dict(),
        "case_state": state.to_dict(),
    }


# --- Pipeline Execution Endpoints ---

@router.post("/helpmora/run")
async def run_helpmora_pipeline(req: HelpMoraRunRequest):
    """Runs the integrated pipeline from text or client voice input."""
    wf = get_workflow_manager()
    state = wf.run_pipeline(
        user_id=req.user_id,
        input_text=req.text,
        session_id=req.session_id,
        source="text",
        language=req.language or "en",
    )
    return {
        "ok": True,
        "run_id": state.case_id,
        "status": state.status,
        "case_state": state.to_dict(),
    }


@router.get("/helpmora/run/{run_id}")
async def get_run_status(run_id: str):
    """Returns the live status, execution trace, and state of a workflow run."""
    state = _ACTIVE_RUNS.get(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run ID not found.")
    return {
        "ok": True,
        "run_id": run_id,
        "status": state.status,
        "case_state": state.to_dict(),
    }


# --- Qdrant Memory Endpoints ---

@router.post("/memory/retrieve")
async def retrieve_memories(req: MemoryRetrieveRequest):
    """Scoped memory retrieval with strict user_id boundary."""
    store = get_memory_store()
    results = store.retrieve_memories(
        user_id=req.user_id,
        query_text=req.query_text,
        memory_type=req.memory_type,
        case_id=req.case_id,
        limit=req.limit or 10,
    )
    return {"ok": True, "count": len(results), "memories": results}


@router.post("/memory/store")
async def store_memory(req: MemoryStoreRequest):
    """Stores a structured memory in Qdrant respecting user privacy policy."""
    store = get_memory_store()
    rec = store.store_memory(
        user_id=req.user_id,
        memory_type=req.memory_type,
        text=req.text,
        case_id=req.case_id or "",
        metadata=req.metadata,
        language=req.language or "en",
        visibility=req.visibility or "private",
    )
    if not rec:
        return {"ok": False, "message": "Memory not stored (disallowed by privacy settings or invalid parameters)"}
    return {"ok": True, "memory_id": rec.memory_id, "record": rec.to_payload()}


@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str, user_id: str = Query(..., description="User ID for access control")):
    """Deletes a specific memory belonging to user_id."""
    store = get_memory_store()
    success = store.delete_memory(user_id=user_id, memory_id=memory_id)
    return {"ok": success}


@router.delete("/memory/user/{user_id}")
async def delete_user_memories(user_id: str, case_id: Optional[str] = Query(None)):
    """Deletes all memories or case-scoped memories for a user."""
    store = get_memory_store()
    success = store.delete_user_memories(user_id=user_id, case_id=case_id)
    return {"ok": success}


@router.get("/memory/summary/{user_id}")
async def get_memory_summary(user_id: str):
    """Aggregate memory summary for privacy dashboard."""
    store = get_memory_store()
    return store.get_memory_summary(user_id=user_id)


@router.post("/privacy/update")
async def update_privacy_settings(req: PrivacyUpdateRequest):
    """Updates user privacy settings for memory retention."""
    store = get_memory_store()
    kwargs = {}
    if req.conversation_memory is not None:
        kwargs["conversation_memory"] = req.conversation_memory
    if req.application_history is not None:
        kwargs["application_history"] = req.application_history
    if req.documents is not None:
        kwargs["documents"] = req.documents
    if req.raw_voice_retention is not None:
        kwargs["raw_voice_retention"] = req.raw_voice_retention

    updated = store.update_privacy_settings(req.user_id, **kwargs)
    return {"ok": True, "settings": updated.to_dict()}


# --- Track 4 Workflow & Human Approval Endpoints ---

@router.post("/workflow/approve")
async def approve_workflow_action(req: WorkflowApproveRequest):
    """Human approval gate: user reviews and approves external action."""
    wf = get_workflow_manager()
    res = wf.approve_action(run_id=req.run_id, user_id=req.user_id, action_index=req.action_index or 0)
    if not res.get("ok"):
        raise HTTPException(status_code=400, detail=res.get("error", "Approval failed."))
    return res


@router.post("/workflow/voice-to-form")
async def voice_to_form(req: VoiceToFormRequest):
    """Converts natural spoken voice phrases into structured form fields."""
    wf = get_workflow_manager()
    parsed = wf.parse_voice_to_form(req.text)
    return {"ok": True, "result": parsed}


@router.get("/workflow/explain-field")
async def explain_field(field_name: str = Query(..., alias="field")):
    """Field-level help ('Ask HELPmora') using verified statutory definitions."""
    wf = get_workflow_manager()
    explanation = wf.get_field_explanation(field_name)
    return {"ok": True, "field": field_name, "explanation": explanation}


@router.get("/workflow/recovery")
async def guided_recovery(issue: str = Query("document_missing")):
    """Guided recovery options when user is stuck on a document or step."""
    wf = get_workflow_manager()
    options = wf.get_guided_recovery(issue)
    return {"ok": True, "recovery": options}
