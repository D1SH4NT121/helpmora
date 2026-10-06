"""Persistent Scoped Semantic Memory using Qdrant.

Implements:
- Collection management (`helpmora_memory`)
- Scoped multi-tenant queries (Strict `user_id == current_user_id` isolation)
- Semantic vector indexing and payload indexing
- User privacy settings and write policies
- Full CRUD operations for memories and case events
"""

import hashlib
import json
import logging
import os
import uuid
from typing import Any, Dict, List, Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models

from .schemas import MemoryRecord, SUPPORTED_MEMORY_TYPES, UserPrivacySettings

logger = logging.getLogger("helpmora.integrations.qdrant")

COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME", "helpmora_memory")
VECTOR_DIMENSION = 256

# In-memory privacy cache per user
_USER_PRIVACY: Dict[str, UserPrivacySettings] = {}


def _embed_text(text: str, dim: int = VECTOR_DIMENSION) -> List[float]:
    """
    Deterministic semantic text embedding based on character n-gram and word feature hashing.
    Provides sub-millisecond semantic vector projection without external network calls or heavy weights.
    """
    if not text:
        return [0.0] * dim

    vec = np.zeros(dim, dtype=np.float32)
    words = text.lower().strip().split()
    
    # Word unigrams and bigrams
    for i, w in enumerate(words):
        h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % dim
        vec[h] += 2.0
        if i + 1 < len(words):
            bigram = f"{w}_{words[i+1]}"
            h_bi = int(hashlib.sha256(bigram.encode("utf-8")).hexdigest(), 16) % dim
            vec[h_bi] += 1.5

    # Character 3-grams for morphological/fuzzy similarity
    clean_text = " " + text.lower() + " "
    for i in range(len(clean_text) - 2):
        trigram = clean_text[i:i+3]
        h_tri = int(hashlib.md5(trigram.encode("utf-8")).hexdigest(), 16) % dim
        vec[h_tri] += 0.5

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


class QdrantMemoryStore:
    def __init__(self, client: Optional[QdrantClient] = None):
        self.collection_name = COLLECTION_NAME
        if client:
            self.client = client
        else:
            qdrant_url = os.environ.get("QDRANT_URL", "").strip()
            qdrant_api_key = os.environ.get("QDRANT_API_KEY", "").strip() or None
            storage_path = os.environ.get("QDRANT_STORAGE_PATH", "").strip()

            if qdrant_url:
                logger.info(f"Connecting to Qdrant cluster at {qdrant_url}")
                self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            elif storage_path:
                os.makedirs(storage_path, exist_ok=True)
                logger.info(f"Initializing persistent local Qdrant at {storage_path}")
                self.client = QdrantClient(path=storage_path)
            else:
                # Default to local path inside data directory
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                default_path = os.path.join(base_dir, "data", "qdrant_db")
                os.makedirs(default_path, exist_ok=True)
                try:
                    self.client = QdrantClient(path=default_path)
                    logger.info(f"Initializing local Qdrant at {default_path}")
                except Exception as lock_ex:
                    logger.warning(f"Local Qdrant storage locked ({lock_ex}); using in-memory instance")
                    self.client = QdrantClient(":memory:")

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create collection and payload indexes if they do not exist."""
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=VECTOR_DIMENSION,
                        distance=models.Distance.COSINE,
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")

                # Create payload indexes for frequent filters
                for field_name in ["user_id", "case_id", "memory_type", "visibility", "created_at"]:
                    try:
                        self.client.create_payload_index(
                            collection_name=self.collection_name,
                            field_name=field_name,
                            field_schema=models.PayloadSchemaType.KEYWORD,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to create index for {field_name}: {e}")
        except Exception as ex:
            logger.error(f"Error initializing Qdrant collection: {ex}")

    def get_privacy_settings(self, user_id: str) -> UserPrivacySettings:
        if not user_id:
            return UserPrivacySettings(user_id="anonymous")
        if user_id not in _USER_PRIVACY:
            _USER_PRIVACY[user_id] = UserPrivacySettings(user_id=user_id)
        return _USER_PRIVACY[user_id]

    def update_privacy_settings(self, user_id: str, **kwargs) -> UserPrivacySettings:
        settings = self.get_privacy_settings(user_id)
        for k, v in kwargs.items():
            if hasattr(settings, k):
                setattr(settings, k, bool(v))
        _USER_PRIVACY[user_id] = settings
        return settings

    def is_write_allowed(self, user_id: str, memory_type: str) -> bool:
        """Enforces explicit memory write policy based on user settings."""
        settings = self.get_privacy_settings(user_id)
        if memory_type == "conversation" and not settings.conversation_memory:
            return False
        if memory_type in ("application", "outcome") and not settings.application_history:
            return False
        if memory_type == "document" and not settings.documents:
            return False
        if memory_type == "raw_voice" and not settings.raw_voice_retention:
            return False
        return True

    def store_memory(
        self,
        user_id: str,
        memory_type: str,
        text: str,
        case_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        language: str = "en",
        visibility: str = "private",
        source: str = "helpmora",
    ) -> Optional[MemoryRecord]:
        """
        Store a structured memory in Qdrant with scoped user ownership.
        Respects user privacy settings.
        """
        if not user_id or not text.strip():
            return None

        if memory_type not in SUPPORTED_MEMORY_TYPES:
            memory_type = "conversation"

        if not self.is_write_allowed(user_id, memory_type):
            logger.info(f"Memory write disallowed by user privacy settings for {user_id}: {memory_type}")
            return None

        record = MemoryRecord(
            user_id=user_id,
            case_id=case_id,
            memory_type=memory_type,
            text=text.strip(),
            language=language,
            visibility=visibility,
            source=source,
            metadata=metadata or {},
        )

        vector = _embed_text(record.text)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, record.memory_id))

        point = models.PointStruct(
            id=point_id,
            vector=vector,
            payload=record.to_payload(),
        )

        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
            )
            return record
        except Exception as ex:
            logger.error(f"Failed to upsert memory point to Qdrant: {ex}")
            return None

    def store_case_event(
        self,
        user_id: str,
        case_id: str,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Optional[MemoryRecord]:
        """Convenience method to store workflow milestones and case events."""
        text = f"Case event {event_type} for case {case_id}: {json.dumps(details or {})}"
        return self.store_memory(
            user_id=user_id,
            memory_type="case_event",
            text=text,
            case_id=case_id,
            metadata={"event_type": event_type, "details": details or {}},
        )

    def retrieve_memories(
        self,
        user_id: str,
        query_text: Optional[str] = None,
        memory_type: Optional[str] = None,
        case_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Scoped memory retrieval.
        CRITICAL: All retrieval MUST be filtered by user_id == current_user_id.
        """
        if not user_id:
            return []

        # Strict user boundary
        must_conditions: List[models.Condition] = [
            models.FieldCondition(
                key="user_id",
                match=models.MatchValue(value=user_id),
            )
        ]

        if memory_type:
            must_conditions.append(
                models.FieldCondition(
                    key="memory_type",
                    match=models.MatchValue(value=memory_type),
                )
            )

        if case_id:
            must_conditions.append(
                models.FieldCondition(
                    key="case_id",
                    match=models.MatchValue(value=case_id),
                )
            )

        filter_condition = models.Filter(must=must_conditions)

        try:
            if query_text and query_text.strip():
                vector = _embed_text(query_text.strip())
                # Use query_points for modern Qdrant client
                search_results = self.client.query_points(
                    collection_name=self.collection_name,
                    query=vector,
                    query_filter=filter_condition,
                    limit=limit,
                ).points
                results = []
                for point in search_results:
                    payload = dict(point.payload or {})
                    payload["score"] = float(point.score) if hasattr(point, "score") and point.score is not None else 1.0
                    results.append(payload)
                return results
            else:
                # Scroll/filter query without vector
                scroll_results, _ = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=filter_condition,
                    limit=limit,
                )
                return [dict(p.payload or {}) for p in scroll_results]
        except Exception as ex:
            logger.error(f"Error retrieving memories from Qdrant: {ex}")
            return []

    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Deletes a specific memory belonging to user_id."""
        if not user_id or not memory_id:
            return False

        filter_condition = models.Filter(
            must=[
                models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id)),
                models.FieldCondition(key="memory_id", match=models.MatchValue(value=memory_id)),
            ]
        )
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(filter=filter_condition),
            )
            return True
        except Exception as ex:
            logger.error(f"Error deleting memory {memory_id}: {ex}")
            return False

    def delete_user_memories(self, user_id: str, case_id: Optional[str] = None) -> bool:
        """Deletes all memories or case-specific memories for a user."""
        if not user_id:
            return False

        must_conditions: List[models.Condition] = [
            models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))
        ]
        if case_id:
            must_conditions.append(
                models.FieldCondition(key="case_id", match=models.MatchValue(value=case_id))
            )

        filter_condition = models.Filter(must=must_conditions)
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(filter=filter_condition),
            )
            return True
        except Exception as ex:
            logger.error(f"Error deleting user memories: {ex}")
            return False

    def get_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """Provides an aggregate summary of stored user memories."""
        all_memories = self.retrieve_memories(user_id=user_id, limit=100)
        counts: Dict[str, int] = {}
        for m in all_memories:
            m_type = m.get("memory_type", "other")
            counts[m_type] = counts.get(m_type, 0) + 1

        return {
            "user_id": user_id,
            "total_memories": len(all_memories),
            "by_type": counts,
            "privacy_settings": self.get_privacy_settings(user_id).to_dict(),
        }


# Global singleton instance
_GLOBAL_STORE: Optional[QdrantMemoryStore] = None


def get_memory_store() -> QdrantMemoryStore:
    global _GLOBAL_STORE
    if _GLOBAL_STORE is None:
        _GLOBAL_STORE = QdrantMemoryStore()
    return _GLOBAL_STORE
