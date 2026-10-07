"""Safe Configuration Loader and State Management for HELPmora Integrations.

Provides robust, typed configuration management supporting four distinct states:
- CONFIGURED: Keys and endpoints present and verified.
- NOT_CONFIGURED: Clean fallback to local / deterministic / zero-credential mode.
- INVALID: Configuration supplied but malformed or invalid syntax.
- UNAVAILABLE: Configured but remote service / dependency is unreachable or missing.

Ensures:
- Safe loading of .env without hard dependency on python-dotenv.
- Zero secrets leaking in logs or API responses.
- Graceful degradation across Omi, Qdrant, and Lyzr.
"""

from enum import Enum
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger("helpmora.integrations.config")


class IntegrationState(str, Enum):
    CONFIGURED = "CONFIGURED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"


def load_env_safe(env_path: Optional[str] = None) -> Dict[str, str]:
    """
    Safely load key-value pairs from a .env file without external dependencies.
    Does NOT overwrite already-set environment variables.
    """
    loaded = {}
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    else:
        # Check current working directory, workspace root, and repo root
        cwd = Path.cwd()
        candidates.extend([
            cwd / ".env",
            cwd.parent / ".env",
            Path(__file__).resolve().parent.parent.parent / ".env",
            Path(__file__).resolve().parent.parent / ".env",
        ])

    target = None
    for c in candidates:
        if c.is_file():
            target = c
            break

    if not target:
        return loaded

    try:
        with open(target, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Strip wrapping quotes
                if len(val) >= 2 and (
                    (val.startswith('"') and val.endswith('"')) or
                    (val.startswith("'") and val.endswith("'"))
                ):
                    val = val[1:-1]
                
                # Set in os.environ if not already present or if currently empty
                if key and (key not in os.environ or not os.environ[key]):
                    os.environ[key] = val
                    loaded[key] = val

        # Ensure LiteLLM compatibility (litellm looks for NVIDIA_API_KEY or NVIDIA_NIM_API_KEY)
        if "NVIDIA_NIM_API_KEY" in os.environ and not os.environ.get("NVIDIA_API_KEY"):
            os.environ["NVIDIA_API_KEY"] = os.environ["NVIDIA_NIM_API_KEY"]
        elif "NVIDIA_API_KEY" in os.environ and not os.environ.get("NVIDIA_NIM_API_KEY"):
            os.environ["NVIDIA_NIM_API_KEY"] = os.environ["NVIDIA_API_KEY"]
    except Exception as ex:
        logger.warning(f"Failed to read .env file at {target}: {ex}")

    return loaded


# Run safe load on module import
load_env_safe()


class IntegrationConfig:
    """Manages typed configuration states for all external services."""

    def __init__(self):
        # Trigger safe env load
        load_env_safe()

    # --- Omi Configuration ---
    @property
    def omi_webhook_secret(self) -> str:
        return os.environ.get("OMI_WEBHOOK_SECRET", "").strip()

    @property
    def omi_api_key(self) -> str:
        return os.environ.get("OMI_API_KEY", "").strip()

    @property
    def public_base_url(self) -> str:
        return os.environ.get("PUBLIC_BASE_URL", "").strip()

    def get_omi_status(self) -> Dict[str, Any]:
        """Assess Omi configuration state."""
        url = self.public_base_url
        if url:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return {
                    "state": IntegrationState.INVALID.value,
                    "mode": "invalid_url",
                    "details": f"PUBLIC_BASE_URL '{url}' is not a valid URL (must include scheme like http:// or https://)",
                    "webhook_auth": bool(self.omi_webhook_secret),
                }

        if self.omi_webhook_secret:
            return {
                "state": IntegrationState.CONFIGURED.value,
                "mode": "authenticated_webhook",
                "details": "Omi webhook secret configured; signature validation active",
                "webhook_auth": True,
                "public_base_url": url or None,
            }

        return {
            "state": IntegrationState.NOT_CONFIGURED.value,
            "mode": "open_local_dev",
            "details": "No webhook secret configured; accepts local and development audio payloads",
            "webhook_auth": False,
            "public_base_url": url or None,
        }

    # --- Qdrant Configuration ---
    @property
    def qdrant_url(self) -> str:
        return os.environ.get("QDRANT_URL", "").strip()

    @property
    def qdrant_api_key(self) -> str:
        return os.environ.get("QDRANT_API_KEY", "").strip()

    @property
    def qdrant_collection_name(self) -> str:
        return os.environ.get("QDRANT_COLLECTION_NAME", "helpmora_memory").strip()

    @property
    def qdrant_storage_path(self) -> str:
        return os.environ.get("QDRANT_STORAGE_PATH", "").strip()

    def get_qdrant_status(self) -> Dict[str, Any]:
        """Assess Qdrant configuration state."""
        url = self.qdrant_url
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                return {
                    "state": IntegrationState.INVALID.value,
                    "mode": "cloud",
                    "collection": self.qdrant_collection_name,
                    "details": f"QDRANT_URL '{url}' is invalid (must start with http:// or https://)",
                }

            # Check if qdrant_client is installed
            try:
                import qdrant_client
                return {
                    "state": IntegrationState.CONFIGURED.value,
                    "mode": "remote_cluster",
                    "collection": self.qdrant_collection_name,
                    "details": f"Remote Qdrant configured at {parsed.netloc}",
                }
            except ImportError:
                return {
                    "state": IntegrationState.UNAVAILABLE.value,
                    "mode": "remote_cluster",
                    "collection": self.qdrant_collection_name,
                    "details": "qdrant-client package is not installed; remote connection unavailable",
                }

        # Check local persistent or in-memory
        storage_path = self.qdrant_storage_path
        if storage_path:
            return {
                "state": IntegrationState.CONFIGURED.value,
                "mode": "local_persistent",
                "collection": self.qdrant_collection_name,
                "storage_path": storage_path,
                "details": f"Local persistent disk storage configured at {storage_path}",
            }

        return {
            "state": IntegrationState.NOT_CONFIGURED.value,
            "mode": "local_embedded",
            "collection": self.qdrant_collection_name,
            "details": "Using default embedded/in-memory scoped vector memory",
        }

    # --- Lyzr Configuration ---
    @property
    def lyzr_api_key(self) -> str:
        return os.environ.get("LYZR_API_KEY", "").strip()

    @property
    def lyzr_environment_id(self) -> str:
        return os.environ.get("LYZR_ENVIRONMENT_ID", "").strip()

    @property
    def lyzr_manager_agent_id(self) -> str:
        return os.environ.get("LYZR_MANAGER_AGENT_ID", "").strip()

    def get_lyzr_status(self) -> Dict[str, Any]:
        """Assess Lyzr configuration state."""
        key = self.lyzr_api_key
        if key:
            # Check length or format heuristics
            if len(key) < 8 or " " in key:
                return {
                    "state": IntegrationState.INVALID.value,
                    "mode": "invalid_key",
                    "details": "LYZR_API_KEY format is invalid",
                    "cloud_enabled": False,
                }

            try:
                from lyzr_agent_api import AgentAPI
                return {
                    "state": IntegrationState.CONFIGURED.value,
                    "mode": "cloud_agent_api",
                    "details": "Lyzr Cloud Agent API configured and SDK available",
                    "cloud_enabled": True,
                    "environment_id": self.lyzr_environment_id or "default",
                }
            except ImportError:
                return {
                    "state": IntegrationState.UNAVAILABLE.value,
                    "mode": "cloud_agent_api",
                    "details": "LYZR_API_KEY set but lyzr-agent-api SDK is not installed",
                    "cloud_enabled": False,
                }

        return {
            "state": IntegrationState.NOT_CONFIGURED.value,
            "mode": "local_deterministic_orchestration",
            "details": "Running local multi-agent architecture with deterministic verification",
            "cloud_enabled": False,
        }

    # --- NVIDIA NIM Configuration ---
    @property
    def nvidia_api_key(self) -> str:
        return (os.environ.get("NVIDIA_NIM_API_KEY") or os.environ.get("NVIDIA_API_KEY") or "").strip()

    def get_nvidia_status(self) -> Dict[str, Any]:
        """Assess NVIDIA NIM configuration state."""
        key = self.nvidia_api_key
        if key:
            if not key.startswith("nvapi-") or len(key) < 20:
                return {
                    "state": IntegrationState.INVALID.value,
                    "mode": "nvidia_nim",
                    "details": "NVIDIA API key format invalid (should start with nvapi-)",
                }
            return {
                "state": IntegrationState.CONFIGURED.value,
                "status": "ready",
                "mode": "nvidia_nim",
                "details": "NVIDIA NIM API key configured for model pool and polyglot narration",
                "models": ["nvidia_nim/openai/gpt-oss-20b", "nvidia_nim/google/gemma-4-31b-it"],
            }
        return {
            "state": IntegrationState.NOT_CONFIGURED.value,
            "status": "ready",
            "mode": "deterministic_fallback",
            "details": "Running with zero-LLM deterministic fallback narration",
        }

    # --- HELPmora Core ---
    def get_core_status(self) -> Dict[str, Any]:
        return {
            "state": IntegrationState.CONFIGURED.value,
            "status": "ready",
            "resources": 40,
            "transitions": 26,
            "authority": "jac_deterministic_engine",
        }

    def get_all_statuses(self) -> Dict[str, Any]:
        """Collect sanitized status summary for all integrations."""
        return {
            "status": "ok",
            "integrations": {
                "omi": self.get_omi_status(),
                "qdrant": self.get_qdrant_status(),
                "lyzr": self.get_lyzr_status(),
                "nvidia_nim": self.get_nvidia_status(),
                "helpmora_core": self.get_core_status(),
            }
        }


_GLOBAL_CONFIG: Optional[IntegrationConfig] = None


def get_integration_config() -> IntegrationConfig:
    global _GLOBAL_CONFIG
    if _GLOBAL_CONFIG is None:
        _GLOBAL_CONFIG = IntegrationConfig()
    return _GLOBAL_CONFIG
