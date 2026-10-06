"""Lyzr SuperFlow and Track 4 Adaptive Assistant Workflow Engine.

Executes the end-to-end agent workflow:
Omi Voice / Text -> Safety Gate -> Qdrant Retrieval -> Lyzr ContextAgent ->
ResourceAgent -> EligibilityAgent -> PathfinderAgent -> VerificationAgent ->
ActionAgent -> Track 4 Adaptive Guided Workflow -> Human Approval -> Qdrant Memory Write.
"""

import json
import logging
import re
import uuid
from typing import Any, Dict, List, Optional

from helpmora.integrations.lyzr.agents import (
    ContextAgent,
    ResourceAgent,
    EligibilityAgent,
    PathfinderAgent,
    VerificationAgent,
    ActionAgent,
    check_crisis_safety_gate,
)
from helpmora.integrations.qdrant.memory import get_memory_store
from helpmora.orchestration.case_state import CaseState

logger = logging.getLogger("helpmora.orchestration.workflow")

# In-memory registry for active workflow runs (keyed by run_id)
_ACTIVE_RUNS: Dict[str, CaseState] = {}


# Track 4 Adaptive Steps definition
GUIDED_STEPS = [
    {"id": "personal", "name": "Personal Information", "description": "Name, age, and location"},
    {"id": "household", "name": "Household Composition", "description": "Family members and dependents"},
    {"id": "income", "name": "Income Verification", "description": "Monthly and annual earnings"},
    {"id": "category", "name": "Program Category", "description": "Housing, food, healthcare, or legal aid"},
    {"id": "documents", "name": "Required Documents", "description": "Aadhaar, income certificate, ration card"},
    {"id": "review", "name": "Review & Approval", "description": "Verify entries and approve next steps"},
]

FIELD_EXPLANATIONS = {
    "income": "Total gross earnings of all family members living together. For EWS schemes in India, this must be under ₹3,00,000 per year.",
    "monthly_income": "Total earnings received each month from employment, daily wages, or small business.",
    "household_size": "Total number of people who share meals and live in the same residence, including children and elderly members.",
    "aadhaar": "12-digit biometric identity number issued by UIDAI, mandatory for Direct Benefit Transfer (DBT) schemes.",
    "ration_card": "Official state government document categorized as AAY, BPL, or PHH for subsidized foodgrains under NFSA.",
    "caste_certificate": "Official certificate confirming SC, ST, or OBC status for affirmative welfare benefits.",
    "residency": "Proof of residing in the state or municipal area, such as electricity bill, voter card, or domicile certificate.",
}


class AdaptiveWorkflowManager:
    """Manages Track 4 Adaptive Assistant flows, field help, voice-to-form, and approval."""

    def __init__(self):
        self.memory_store = get_memory_store()
        self.context_agent = ContextAgent()
        self.resource_agent = ResourceAgent()
        self.eligibility_agent = EligibilityAgent()
        self.pathfinder_agent = PathfinderAgent()
        self.verification_agent = VerificationAgent()
        self.action_agent = ActionAgent()

    def run_pipeline(
        self,
        user_id: str,
        input_text: str,
        session_id: Optional[str] = None,
        source: str = "text",
        language: str = "en",
        run_id: Optional[str] = None,
    ) -> CaseState:
        """
        Executes the authoritative multi-agent pipeline.
        """
        rid = run_id or f"run_{uuid.uuid4().hex[:10]}"
        state = CaseState(
            case_id=rid,
            user_id=user_id or "user_anon",
            session_id=session_id or f"sess_{uuid.uuid4().hex[:8]}",
            source=source,
            raw_input_text=input_text,
            language=language,
        )

        state.record_trace("workflow_started", "SuperFlow", {"run_id": rid, "source": source})

        # 1. Safety Gate Check
        if check_crisis_safety_gate(state):
            _ACTIVE_RUNS[rid] = state
            return state

        # 2. Qdrant Memory Retrieval (Strictly scoped by user_id)
        state.record_trace("memory_retrieval_started", "QdrantMemory")
        retrieved = self.memory_store.retrieve_memories(
            user_id=state.user_id,
            query_text=input_text,
            limit=5,
        )
        state.retrieved_memories = retrieved
        state.record_trace("memory_retrieval_completed", "QdrantMemory", {"count": len(retrieved)})

        # 3. Lyzr ContextAgent
        self.context_agent.run(state)

        # 4. Lyzr ResourceAgent (Authoritative catalog)
        self.resource_agent.run(state)

        # 5. Lyzr EligibilityAgent (Deterministic calculation)
        self.eligibility_agent.run(state)

        # 6. Lyzr PathfinderAgent (Transitions graph)
        self.pathfinder_agent.run(state)

        # 7. Lyzr VerificationAgent (Hard verification gate)
        self.verification_agent.run(state)

        # 8. Lyzr ActionAgent
        self.action_agent.run(state)

        # 9. Build Track 4 Adaptive Workflow state
        self._attach_adaptive_workflow(state)

        # 10. Store conversation milestone in Qdrant (respects user privacy)
        self.memory_store.store_memory(
            user_id=state.user_id,
            memory_type="conversation",
            text=f"User: {input_text}",
            case_id=state.case_id,
            language=language,
            metadata={"needs": state.needs, "status": state.status},
        )

        _ACTIVE_RUNS[rid] = state
        state.record_trace("workflow_completed", "SuperFlow", {"status": state.status})
        return state

    def _attach_adaptive_workflow(self, state: CaseState) -> None:
        """Configures the step-by-step guided workflow for the UI."""
        completed_steps = []
        current_step = "personal"

        if state.profile.get("household_size"):
            completed_steps.append("personal")
            current_step = "household"

        if state.profile.get("income_annual") is not None or state.profile.get("income_monthly") is not None:
            completed_steps.append("household")
            completed_steps.append("income")
            current_step = "category"

        if state.candidate_resources:
            completed_steps.append("category")
            current_step = "documents"

        if state.verification.status == "passed":
            completed_steps.append("documents")
            current_step = "review"

        state.workflow = {
            "steps": GUIDED_STEPS,
            "current_step": current_step,
            "completed_steps": completed_steps,
            "step_index": next((i for i, s in enumerate(GUIDED_STEPS) if s["id"] == current_step), 0),
            "waiting_approval": state.status == "waiting_approval",
        }

    def parse_voice_to_form(self, text: str) -> Dict[str, Any]:
        """
        Voice-to-Form parser:
        e.g. 'My monthly income is eight thousand rupees' -> ₹8,000
        """
        result = {"field": "", "raw_value": None, "formatted_value": "", "confirmation_prompt": ""}
        t = text.lower()

        # Word numbers to digits
        words_to_num = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "thousand": 1000, "lakh": 100000, "crore": 10000000
        }

        # Monthly income check
        if any(w in t for w in ["income", "earn", "salary", "rupees", "₹", "rs"]):
            m = re.search(r'([0-9]{1,3}(?:,[0-9]{3})*|[0-9]+)', t)
            val = None
            if m:
                val = float(m.group(1).replace(",", ""))
            elif "eight thousand" in t:
                val = 8000.0
            elif "ten thousand" in t:
                val = 10000.0
            elif "fifteen thousand" in t:
                val = 15000.0
            elif "twenty thousand" in t:
                val = 20000.0

            if val is not None:
                if "k" in t and val < 1000:
                    val *= 1000
                formatted = f"₹{val:,.0f}"
                result = {
                    "field": "monthly_income",
                    "raw_value": val,
                    "formatted_value": formatted,
                    "confirmation_prompt": f"I've entered {formatted} for Monthly Income. Is that correct?",
                }
                return result

        # Household size check
        if any(w in t for w in ["household", "family member", "people living", "children", "kids"]):
            m = re.search(r'([0-9]+)', t)
            count = int(m.group(1)) if m else (2 if "two" in t else (3 if "three" in t else (4 if "four" in t else 1)))
            result = {
                "field": "household_size",
                "raw_value": count,
                "formatted_value": f"{count} members",
                "confirmation_prompt": f"I've noted {count} household members. Is that correct?",
            }
            return result

        return result

    def get_field_explanation(self, field_name: str) -> str:
        """Returns verified simple-language field definition."""
        norm_key = field_name.lower().strip()
        for k, expl in FIELD_EXPLANATIONS.items():
            if k in norm_key:
                return expl
        return f"This field represents {field_name} required by statutory welfare schemes."

    def get_guided_recovery(self, issue_type: str) -> Dict[str, Any]:
        """Provides helpful recovery options when user is stuck on a document or step."""
        if "document" in issue_type.lower() or "income" in issue_type.lower():
            return {
                "title": "Document Assistance",
                "message": "If you don't have your physical income certificate right now, here are your options:",
                "options": [
                    {"label": "Use Previously Uploaded Document", "action": "search_vault"},
                    {"label": "Apply Online via State e-District Portal", "action": "open_edistrict_link", "url": "https://services.india.gov.in"},
                    {"label": "Skip for now and continue", "action": "skip_step"},
                    {"label": "Connect with Local Caseworker", "action": "contact_caseworker", "phone": "1800-180-1551"},
                ]
            }
        return {
            "title": "Need Help?",
            "message": "You can skip this step and return later, or ask HELPmora to clarify.",
            "options": [
                {"label": "Skip for now", "action": "skip_step"},
                {"label": "Ask HELPmora", "action": "ask_help"},
            ]
        }

    def approve_action(self, run_id: str, user_id: str, action_index: int = 0) -> Dict[str, Any]:
        """
        Executes human approval gate for external side-effects.
        Writes persistent application/outcome memory to Qdrant upon approval.
        """
        state = _ACTIVE_RUNS.get(run_id)
        if not state:
            return {"ok": False, "error": f"No active workflow found for run_id {run_id}"}

        if state.user_id != user_id:
            return {"ok": False, "error": "Unauthorized user approval attempt."}

        if not state.actions or action_index >= len(state.actions):
            return {"ok": False, "error": "Invalid action index."}

        action = state.actions[action_index]
        action["approved"] = True
        state.status = "completed"
        state.record_trace("human_approval_granted", "SuperFlow", {"action_title": action.get("title")})

        # Persist application memory in Qdrant
        target_res = action.get("target_resource") or action.get("target_program") or "General Civic Welfare"
        rec = self.memory_store.store_memory(
            user_id=state.user_id,
            memory_type="application",
            text=f"User approved application workflow for {target_res}",
            case_id=state.case_id,
            metadata={
                "program": target_res,
                "status": "submitted",
                "income_annual": state.profile.get("income_annual"),
                "household_size": state.profile.get("household_size"),
            },
        )

        return {
            "ok": True,
            "status": "approved_and_executed",
            "action": action,
            "stored_memory_id": rec.memory_id if rec else None,
            "case_state": state.to_dict(),
        }

    def record_outcome(self, user_id: str, program: str, status: str, reason: str = "", case_id: str = "") -> Dict[str, Any]:
        """Records final outcome (approved/rejected) to improve future navigation."""
        rec = self.memory_store.store_memory(
            user_id=user_id,
            memory_type="outcome",
            text=f"Application outcome for {program}: {status}. Reason: {reason}",
            case_id=case_id,
            metadata={"program": program, "status": status, "reason": reason},
        )
        return {
            "ok": True,
            "memory_id": rec.memory_id if rec else None,
            "program": program,
            "status": status,
        }


_GLOBAL_WORKFLOW: Optional[AdaptiveWorkflowManager] = None


def get_workflow_manager() -> AdaptiveWorkflowManager:
    global _GLOBAL_WORKFLOW
    if _GLOBAL_WORKFLOW is None:
        _GLOBAL_WORKFLOW = AdaptiveWorkflowManager()
    return _GLOBAL_WORKFLOW
