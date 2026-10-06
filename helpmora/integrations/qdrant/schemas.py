"""Qdrant memory schemas and data models for HELPmora."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

SUPPORTED_MEMORY_TYPES = {
    "conversation",
    "profile_fact",
    "application",
    "recommendation",
    "document",
    "outcome",
    "preference",
    "case_event",
}


@dataclass
class UserPrivacySettings:
    user_id: str
    conversation_memory: bool = True
    application_history: bool = True
    documents: bool = True
    raw_voice_retention: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "conversation_memory": self.conversation_memory,
            "application_history": self.application_history,
            "documents": self.documents,
            "raw_voice_retention": self.raw_voice_retention,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPrivacySettings":
        return cls(
            user_id=data.get("user_id", ""),
            conversation_memory=bool(data.get("conversation_memory", True)),
            application_history=bool(data.get("application_history", True)),
            documents=bool(data.get("documents", True)),
            raw_voice_retention=bool(data.get("raw_voice_retention", False)),
        )


@dataclass
class MemoryRecord:
    memory_id: str = field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:12]}")
    user_id: str = ""
    case_id: str = ""
    memory_type: str = "conversation"
    text: str = ""
    language: str = "en"
    visibility: str = "private"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = "helpmora"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "user_id": self.user_id,
            "case_id": self.case_id,
            "memory_type": self.memory_type,
            "text": self.text,
            "language": self.language,
            "visibility": self.visibility,
            "created_at": self.created_at,
            "source": self.source,
            "metadata": self.metadata,
        }

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "MemoryRecord":
        return cls(
            memory_id=payload.get("memory_id", ""),
            user_id=payload.get("user_id", ""),
            case_id=payload.get("case_id", ""),
            memory_type=payload.get("memory_type", "conversation"),
            text=payload.get("text", ""),
            language=payload.get("language", "en"),
            visibility=payload.get("visibility", "private"),
            created_at=payload.get("created_at", ""),
            source=payload.get("source", "helpmora"),
            metadata=payload.get("metadata", {}),
        )
