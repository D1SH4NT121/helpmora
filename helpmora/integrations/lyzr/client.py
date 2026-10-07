"""Lyzr Agent API client wrapper and configuration.

Uses the official `lyzr-agent-api` SDK to interact with Lyzr agent infrastructure,
with graceful degradation to deterministic local orchestration when keys are not configured.
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("helpmora.integrations.lyzr")

try:
    from lyzr_agent_api import AgentAPI, AgentConfig
    _LYZR_SDK_AVAILABLE = True
except ImportError:
    _LYZR_SDK_AVAILABLE = False
    AgentAPI = None
    AgentConfig = None

try:
    from helpmora.integrations.config import load_env_safe
except ImportError:
    try:
        from integrations.config import load_env_safe
    except ImportError:
        def load_env_safe(): pass


class LyzrClientManager:
    def __init__(self):
        load_env_safe()
        self.api_key = os.environ.get("LYZR_API_KEY", "").strip()
        self.environment_id = os.environ.get("LYZR_ENVIRONMENT_ID", "").strip()
        self.manager_agent_id = os.environ.get("LYZR_MANAGER_AGENT_ID", "").strip()
        self.client: Optional[Any] = None

        if self.api_key and _LYZR_SDK_AVAILABLE:
            try:
                self.client = AgentAPI(x_api_key=self.api_key)
                logger.info("Initialized official Lyzr Agent API client.")
            except Exception as ex:
                logger.warning(f"Could not initialize Lyzr Agent API: {ex}")
                self.client = None
        else:
            logger.info("Running in standard deterministic Lyzr agent execution mode.")

    def is_cloud_enabled(self) -> bool:
        return self.client is not None and bool(self.api_key)


_GLOBAL_LYZR: Optional[LyzrClientManager] = None


def get_lyzr_client() -> LyzrClientManager:
    global _GLOBAL_LYZR
    if _GLOBAL_LYZR is None:
        _GLOBAL_LYZR = LyzrClientManager()
    return _GLOBAL_LYZR
