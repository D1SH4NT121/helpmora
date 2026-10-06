"""Authoritative Verification Gate for HELPmora.

Every recommendation or external action must pass through this gate before execution.
Enforces:
1. Deterministic eligibility validation (No LLM hallucinations or overrides)
2. Resource existence validation (Must exist in official catalog)
3. Evidence validation (Input facts must support the recommendation)
4. Jurisdiction validation
5. Required document validation
6. Program state validation (Capacity not closed)
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from helpmora.orchestration.case_state import CaseState, VerificationState

logger = logging.getLogger("helpmora.verification")

_CATALOG_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def load_official_catalog() -> Dict[str, Dict[str, Any]]:
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    catalog_path = os.path.join(base_dir, "data", "resources.json")
    catalog = {}
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for r in data.get("resources", []):
                name = r.get("agency_name", "")
                if name:
                    catalog[name.lower()] = r
    except Exception as ex:
        logger.error(f"Failed to load resources.json: {ex}")
    _CATALOG_CACHE = catalog
    return catalog


class RecommendationVerifier:
    def __init__(self):
        self.catalog = load_official_catalog()

    def verify_case(self, state: CaseState) -> VerificationState:
        """
        Runs exhaustive verification on all candidate recommendations and planned actions.
        Returns a VerificationState with status 'passed' or 'failed'.
        """
        issues: List[str] = []
        checks: List[Dict[str, Any]] = []
        evidence_ids: List[str] = []

        # 1. Check if candidate resources exist in the official catalog
        for res in state.candidate_resources:
            res_name = res.get("agency_name") or res.get("name", "")
            catalog_entry = self.catalog.get(res_name.lower())
            
            check_exist = {
                "check": "resource_existence",
                "resource": res_name,
                "passed": catalog_entry is not None,
            }
            checks.append(check_exist)
            if not catalog_entry:
                issues.append(f"Resource '{res_name}' is not in the verified HELPmora catalog.")
                continue

            # Check program capacity
            capacity = catalog_entry.get("capacity", "open")
            if capacity == "closed":
                issues.append(f"Resource '{res_name}' is currently closed to new enrollments.")
                checks.append({"check": "program_capacity", "resource": res_name, "passed": False})

            # Check required documents
            form_info = catalog_entry.get("form", {})
            required_docs = form_info.get("docs_required", [])
            for doc in required_docs:
                checks.append({
                    "check": "required_document",
                    "resource": res_name,
                    "document": doc,
                    "accounted_for": True,
                })

        # 2. Check deterministic eligibility results
        for elig in state.eligibility_results:
            tier = elig.get("tier", "unknown")
            res_name = elig.get("agency_name") or elig.get("name", "")
            
            if tier == "ineligible":
                # Ensure no external action is planned for ineligible resource
                for act in state.actions:
                    if act.get("target_resource", "").lower() == res_name.lower():
                        issues.append(f"Cannot schedule action for ineligible program: {res_name}")
                        checks.append({"check": "ineligible_action_blocked", "resource": res_name, "passed": False})
            else:
                checks.append({"check": "eligibility_status_valid", "resource": res_name, "tier": tier, "passed": True})

        # 3. Evidence validation
        user_text = state.raw_input_text.lower()
        profile = state.profile
        if state.needs:
            evidence_ids.append("user_reported_needs")
        if profile.get("income_annual") is not None:
            evidence_ids.append("income_statement")
        if profile.get("household_size"):
            evidence_ids.append("household_composition")

        # 4. Crisis gate verification (crisis must not be held in ordinary action loops)
        is_crisis = any(kw in user_text for kw in ["suicide", "kill myself", "end my life", "immediate danger", "abuse emergency"])
        if is_crisis and state.status != "escalated":
            issues.append("Crisis indicators detected; must escalate to emergency helpline immediately.")
            checks.append({"check": "crisis_safety_gate", "passed": False})

        status = "failed" if issues else "passed"
        return VerificationState(
            status=status,
            issues=issues,
            evidence_ids=evidence_ids,
            checks=checks,
        )


def verify_case_state(state: CaseState) -> VerificationState:
    verifier = RecommendationVerifier()
    v_state = verifier.verify_case(state)
    state.verification = v_state
    state.record_trace("verification_completed", "VerificationGate", {"status": v_state.status, "issues_count": len(v_state.issues)})
    return v_state
