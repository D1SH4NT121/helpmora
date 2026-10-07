"""Shared structured CaseState contract for agent coordination.

The CaseState is the authoritative, serializable data contract used across:
- Omi normalization
- Qdrant persistent memory retrieval
- Lyzr agent delegation (ContextAgent, ResourceAgent, EligibilityAgent,
  PathfinderAgent, VerificationAgent, ActionAgent)
- HELPmora deterministic eligibility & Pathfinder graph walkers
- Verification gates
- Track 4 Adaptive Workflow execution and human approval
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def generate_id(prefix: str = "case") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def current_iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class VerificationState:
    status: str = "pending"  # "pending", "passed", "failed"
    issues: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    checks: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    @property
    def failed(self) -> bool:
        return self.status == "failed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "issues": list(self.issues),
            "evidence_ids": list(self.evidence_ids),
            "checks": list(self.checks),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "VerificationState":
        if not data:
            return cls()
        return cls(
            status=data.get("status", "pending"),
            issues=list(data.get("issues", [])),
            evidence_ids=list(data.get("evidence_ids", [])),
            checks=list(data.get("checks", [])),
        )


@dataclass
class CaseState:
    case_id: str = field(default_factory=lambda: generate_id("case"))
    user_id: str = ""
    session_id: str = field(default_factory=lambda: generate_id("sess"))
    source: str = "text"  # "text", "omi", "adaptive_form"
    raw_input_text: str = ""
    language: str = "en"
    timestamp: str = field(default_factory=current_iso_timestamp)

    profile: Dict[str, Any] = field(default_factory=dict)
    needs: List[str] = field(default_factory=list)
    retrieved_memories: List[Dict[str, Any]] = field(default_factory=list)
    candidate_resources: List[Dict[str, Any]] = field(default_factory=list)
    eligibility_results: List[Dict[str, Any]] = field(default_factory=list)
    pathways: List[Dict[str, Any]] = field(default_factory=list)
    documents: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    verification: VerificationState = field(default_factory=VerificationState)
    workflow: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "processing"  # "processing", "waiting_approval", "completed", "escalated", "failed"
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)

    def record_trace(self, event_type: str, component: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Structured internal execution event logging without leaking sensitive data."""
        event = {
            "case_id": self.case_id,
            "event_type": event_type,
            "component": component,
            "timestamp": current_iso_timestamp(),
            "details": details or {},
        }
        self.execution_trace.append(event)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "source": self.source,
            "raw_input_text": self.raw_input_text,
            "language": self.language,
            "timestamp": self.timestamp,
            "profile": dict(self.profile),
            "needs": list(self.needs),
            "retrieved_memories": list(self.retrieved_memories),
            "candidate_resources": list(self.candidate_resources),
            "eligibility_results": list(self.eligibility_results),
            "pathways": list(self.pathways),
            "documents": list(self.documents),
            "evidence": list(self.evidence),
            "verification": self.verification.to_dict() if isinstance(self.verification, VerificationState) else self.verification,
            "workflow": dict(self.workflow),
            "actions": list(self.actions),
            "status": self.status,
            "execution_trace": list(self.execution_trace),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CaseState":
        ver_raw = data.get("verification")
        verification = VerificationState.from_dict(ver_raw) if isinstance(ver_raw, dict) else (ver_raw or VerificationState())
        return cls(
            case_id=data.get("case_id") or generate_id("case"),
            user_id=data.get("user_id", ""),
            session_id=data.get("session_id") or generate_id("sess"),
            source=data.get("source", "text"),
            raw_input_text=data.get("raw_input_text", ""),
            language=data.get("language", "en"),
            timestamp=data.get("timestamp") or current_iso_timestamp(),
            profile=dict(data.get("profile", {})),
            needs=list(data.get("needs", [])),
            retrieved_memories=list(data.get("retrieved_memories", [])),
            candidate_resources=list(data.get("candidate_resources", [])),
            eligibility_results=list(data.get("eligibility_results", [])),
            pathways=list(data.get("pathways", [])),
            documents=list(data.get("documents", [])),
            evidence=list(data.get("evidence", [])),
            verification=verification,
            workflow=dict(data.get("workflow", {})),
            actions=list(data.get("actions", [])),
            status=data.get("status", "processing"),
            execution_trace=list(data.get("execution_trace", [])),
        )
