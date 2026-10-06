"""Omi Voice Input Adapter for HELPmora.

Normalizes incoming Omi events into the standard HELPmora internal input schema.
Enforces:
- Webhook secret/token verification
- Malformed payload detection and validation
- Idempotency / duplicate event protection
- Redacted logging (no raw sensitive transcript content in logs)
"""

import hashlib
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("helpmora.integrations.omi")

# Cache to prevent duplicate event processing (TTL: 10 minutes)
_PROCESSED_EVENTS: Dict[str, float] = {}
DEDUP_TTL_SECONDS = 600.0


@dataclass
class NormalizedVoiceInput:
    session_id: str
    user_id: str
    text: str
    language: str
    timestamp: str
    source: str = "omi"
    event_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "text": self.text,
            "language": self.language,
            "timestamp": self.timestamp,
            "source": self.source,
            "event_id": self.event_id,
        }


def _prune_dedup_cache() -> None:
    now = time.time()
    stale = [k for k, v in _PROCESSED_EVENTS.items() if now - v > DEDUP_TTL_SECONDS]
    for k in stale:
        _PROCESSED_EVENTS.pop(k, None)


def compute_event_fingerprint(payload: Dict[str, Any]) -> str:
    """Create a deterministic hash for deduplication."""
    event_id = str(payload.get("event_id") or payload.get("id") or "")
    if event_id:
        return f"id:{event_id}"
    
    # Fingerprint by session + text content
    session_id = str(payload.get("session_id") or payload.get("uid") or "")
    text = ""
    if "transcript" in payload:
        text = str(payload["transcript"])
    elif "segments" in payload:
        text = " ".join(s.get("text", "") for s in payload["segments"] if isinstance(s, dict))
    elif "text" in payload:
        text = str(payload["text"])
    
    raw = f"{session_id}:{text.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_omi_auth(headers: Dict[str, str], query_token: str = "") -> bool:
    """Validate webhook secret from headers or query token."""
    expected = os.environ.get("OMI_WEBHOOK_SECRET", "").strip()
    if not expected:
        # If no secret is configured in environment, allow local/dev requests
        return True
    
    auth_header = headers.get("authorization", "") or headers.get("Authorization", "")
    if auth_header:
        parts = auth_header.split()
        token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else auth_header
        if token == expected:
            return True
            
    omi_sig = headers.get("x-omi-signature", "") or headers.get("x-omi-secret", "")
    if omi_sig == expected:
        return True
        
    if query_token and query_token == expected:
        return True
        
    return False


def normalize_omi_event(payload: Any) -> Tuple[bool, Optional[NormalizedVoiceInput], str]:
    """
    Normalizes a raw Omi event into a NormalizedVoiceInput object.
    
    Returns:
        (is_valid, normalized_input, error_reason)
    """
    _prune_dedup_cache()

    if not isinstance(payload, dict):
        return False, None, "Payload must be a JSON object"

    # Extract user ID
    user_id = (
        payload.get("user_id")
        or payload.get("uid")
        or payload.get("user")
        or "anonymous"
    )

    # Extract session ID
    session_id = (
        payload.get("session_id")
        or payload.get("conversation_id")
        or payload.get("id")
        or f"omi_sess_{int(time.time())}"
    )

    # Extract transcript text
    text = ""
    if "transcript" in payload and isinstance(payload["transcript"], str):
        text = payload["transcript"].strip()
    elif "text" in payload and isinstance(payload["text"], str):
        text = payload["text"].strip()
    elif "segments" in payload and isinstance(payload["segments"], list):
        parts = [s.get("text", "") for s in payload["segments"] if isinstance(s, dict) and s.get("text")]
        text = " ".join(parts).strip()
    elif "transcript_segments" in payload and isinstance(payload["transcript_segments"], list):
        parts = [s.get("text", "") for s in payload["transcript_segments"] if isinstance(s, dict) and s.get("text")]
        text = " ".join(parts).strip()

    if not text:
        return False, None, "No transcript text found in Omi payload"

    # Language detection or fallback
    language = str(payload.get("language") or "en").lower()
    if language.startswith("hi"):
        language = "hi"
    elif language.startswith("en"):
        language = "en"

    # Timestamp
    from datetime import datetime, timezone
    ts = str(payload.get("timestamp") or datetime.now(timezone.utc).isoformat())

    # Fingerprint and dedup check
    fingerprint = compute_event_fingerprint(payload)
    if fingerprint in _PROCESSED_EVENTS:
        logger.info(f"Duplicate Omi event ignored for session {session_id}")
        return False, None, "duplicate_event"

    _PROCESSED_EVENTS[fingerprint] = time.time()

    # Log safe telemetry without exposing sensitive content
    word_count = len(text.split())
    logger.info(f"Normalized Omi event: session={session_id}, user={user_id}, language={language}, words={word_count}")

    normalized = NormalizedVoiceInput(
        session_id=str(session_id),
        user_id=str(user_id),
        text=text,
        language=language,
        timestamp=ts,
        source="omi",
        event_id=fingerprint,
    )
    return True, normalized, ""
