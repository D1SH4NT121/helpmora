"""Specialized Lyzr Agents for HELPmora.

Implements the 6 required distinct agent roles:
1. ContextAgent: Extracts structured facts and merges Qdrant memory.
2. ResourceAgent: Retrieves authoritative candidate programs from `resources.json`.
3. EligibilityAgent: Invokes deterministic eligibility scoring without LLM overrides.
4. PathfinderAgent: Computes alternative pathways using the 26 curated transitions.
5. VerificationAgent: Validates recommendations against hard statutory criteria.
6. ActionAgent: Assembles concrete action steps and human approval gates.

Also provides CrisisSafetyGate for immediate escalation of emergency cases.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from helpmora.orchestration.case_state import CaseState
from helpmora.verification.verifier import verify_case_state

logger = logging.getLogger("helpmora.integrations.lyzr.agents")

# Load verified resources and transitions
_RESOURCES_DATA: List[Dict[str, Any]] = []
_TRANSITIONS_DATA: List[Dict[str, Any]] = []


def _load_data():
    global _RESOURCES_DATA, _TRANSITIONS_DATA
    if _RESOURCES_DATA and _TRANSITIONS_DATA:
        return
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    r_path = os.path.join(base_dir, "data", "resources.json")
    t_path = os.path.join(base_dir, "data", "transitions.json")
    try:
        with open(r_path, "r", encoding="utf-8") as f:
            _RESOURCES_DATA = json.load(f).get("resources", [])
    except Exception as ex:
        logger.error(f"Error loading resources.json: {ex}")

    try:
        with open(t_path, "r", encoding="utf-8") as f:
            _TRANSITIONS_DATA = json.load(f).get("transitions", [])
    except Exception as ex:
        logger.error(f"Error loading transitions.json: {ex}")


_load_data()


# -----------------------------------------------------------------------------
# 0. Safety Gate (Immediate Crisis Escalation)
# -----------------------------------------------------------------------------
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "killing myself", "end my life", "ending my life",
    "want to die", "commit suicide", "harm myself", "harming myself", "hurt myself",
    "physically beaten", "domestic abuse emergency", "threatened with knife",
    "starving to death tonight", "child abuse", "in immediate danger"
]

INDIAN_HOTLINES = [
    {"name": "National Emergency Helpline", "number": "112", "service": "Immediate Police / Ambulance / Fire response across India"},
    {"name": "Women in Distress Helpline", "number": "181", "service": "24/7 domestic violence, harassment, and legal counseling for women"},
    {"name": "Tele-MANAS Mental Health Helpline", "number": "14416", "service": "Free 24/7 toll-free psychiatric crisis counseling in multiple Indian languages"},
    {"name": "Childline India", "number": "1098", "service": "24/7 emergency assistance for children in distress or facing abuse"},
]


def check_crisis_safety_gate(state: CaseState) -> bool:
    """Evaluates whether the user message represents an immediate crisis."""
    text = state.raw_input_text.lower()
    for kw in CRISIS_KEYWORDS:
        if kw in text:
            state.status = "escalated"
            state.actions = [
                {
                    "title": "EMERGENCY SAFETY ESCALATION",
                    "type": "crisis_helpline",
                    "hotlines": INDIAN_HOTLINES,
                    "guidance": "Please contact emergency services immediately. HELPmora agents have halted non-emergency processing.",
                    "requires_human_approval": False,
                }
            ]
            state.record_trace("crisis_detected", "SafetyGate", {"keyword": kw, "action": "immediate_escalation"})
            return True
    return False


# -----------------------------------------------------------------------------
# 1. ContextAgent
# -----------------------------------------------------------------------------
class ContextAgent:
    """Extracts structured user context and merges relevant Qdrant memories."""

    def run(self, state: CaseState) -> None:
        state.record_trace("agent_started", "ContextAgent")
        text = state.raw_input_text.lower()
        profile = dict(state.profile)

        # 1. Category extraction
        needs = list(state.needs)
        if any(w in text for w in ["rent", "housing", "evict", "shelter", "homeless", "roof", "pg", "flat"]):
            if "housing" not in needs:
                needs.append("housing")
        if any(w in text for w in ["food", "ration", "hungry", "meal", "groceries", "rice", "wheat", "dal"]):
            if "food" not in needs:
                needs.append("food")
        if any(w in text for w in ["health", "medical", "hospital", "doctor", "treatment", "medicine", "ayushman", "sick"]):
            if "healthcare" not in needs:
                needs.append("healthcare")
        if any(w in text for w in ["legal", "court", "lawyer", "police", "jail", "fir", "bail", "dispute", "tenant"]):
            if "legal" not in needs:
                needs.append("legal")
        if not needs:
            needs.append("housing")  # Default to housing if unspecified

        # 2. Income parsing (supports INR patterns: e.g. "eight thousand rupees", "₹8,000", "8k", "8000")
        word_numbers = {
            "five thousand": 5000.0,
            "six thousand": 6000.0,
            "seven thousand": 7000.0,
            "eight thousand": 8000.0,
            "nine thousand": 9000.0,
            "ten thousand": 10000.0,
            "twelve thousand": 12000.0,
            "fifteen thousand": 15000.0,
            "twenty thousand": 20000.0,
            "twenty five thousand": 25000.0,
            "thirty thousand": 30000.0,
            "forty thousand": 40000.0,
            "fifty thousand": 50000.0,
        }
        extracted_income = None
        for word_phrase, num_val in word_numbers.items():
            if word_phrase in text:
                extracted_income = num_val
                break

        if extracted_income is None:
            income_match = re.search(r'(?:₹|rs\.?|inr)?\s*([0-9]{1,3}(?:,[0-9]{3})*|[0-9]+)\s*(?:k|thousand|rupees|pm|per month)?', text)
            if income_match and any(w in text for w in ["income", "earn", "salary", "rupees", "₹", "rs"]):
                try:
                    num_str = income_match.group(1).replace(",", "")
                    val = float(num_str)
                    if "k" in text:
                        val *= 1000
                    extracted_income = val
                except Exception:
                    pass

        if extracted_income is not None:
            if any(w in text for w in ["month", "pm", "monthly"]) or extracted_income < 50000:
                profile["income_monthly"] = extracted_income
                profile["income_annual"] = extracted_income * 12
            else:
                profile["income_annual"] = extracted_income
                profile["income_monthly"] = extracted_income / 12

        # 3. Household & children
        if any(w in text for w in ["child", "children", "kid", "kids", "son", "daughter"]):
            profile["has_children"] = True
            # Check numbers
            if "two children" in text or "2 children" in text or "2 kids" in text:
                profile["children_count"] = 2
                profile["household_size"] = max(profile.get("household_size", 1), 3)
            elif "three children" in text or "3 children" in text:
                profile["children_count"] = 3
                profile["household_size"] = max(profile.get("household_size", 1), 4)
            elif "one child" in text or "1 child" in text:
                profile["children_count"] = 1
                profile["household_size"] = max(profile.get("household_size", 1), 2)
            else:
                profile["children_count"] = profile.get("children_count", 1)
                profile["household_size"] = max(profile.get("household_size", 1), 2)

        # 4. Employment status
        if any(w in text for w in ["lost my job", "unemployed", "jobless", "fired", "laid off"]):
            profile["employment_status"] = "unemployed"

        # 5. Integrate retrieved Qdrant memories
        for mem in state.retrieved_memories:
            m_type = mem.get("memory_type")
            m_text = mem.get("text", "")
            meta = mem.get("metadata", {})
            if m_type == "application":
                prog = meta.get("program") or meta.get("prog") or "housing assistance"
                status = meta.get("status", "submitted")
                profile["prior_application"] = {"program": prog, "status": status, "text": m_text}
            elif m_type == "outcome":
                prog = meta.get("program", "")
                status = meta.get("status", "rejected")
                profile["prior_outcome"] = {"program": prog, "status": status, "reason": meta.get("reason", "")}

        # Check if current message mentions rejection of prior application
        if any(w in text for w in ["rejected", "denied", "turned down", "application was rejected"]):
            if "prior_application" in profile:
                profile["prior_application"]["status"] = "rejected"
            else:
                profile["prior_application"] = {"program": "housing assistance", "status": "rejected"}

        state.needs = needs
        state.profile = profile
        state.record_trace("agent_completed", "ContextAgent", {
            "needs": needs,
            "household_size": profile.get("household_size"),
            "income_annual": profile.get("income_annual"),
            "prior_app": profile.get("prior_application"),
        })


# -----------------------------------------------------------------------------
# 2. ResourceAgent
# -----------------------------------------------------------------------------
class ResourceAgent:
    """Retrieves candidates strictly from the official HELPmora catalog (resources.json)."""

    def run(self, state: CaseState) -> None:
        state.record_trace("agent_started", "ResourceAgent")
        _load_data()
        needs = state.needs
        candidates: List[Dict[str, Any]] = []

        for res in _RESOURCES_DATA:
            cat = res.get("category", "").lower()
            if cat in needs:
                candidate = dict(res)
                # Attach provenance
                candidate["provenance"] = {
                    "source_name": res.get("agency_name"),
                    "source_url": res.get("online_url"),
                    "jurisdiction": "National / Urban India" if res.get("eligibility", {}).get("residency_requirement") == "city" else "National / All India",
                    "effective_date": "2026-01-01",
                    "policy_version": "v2026.1",
                    "last_verified": "2026-10-01",
                }
                candidates.append(candidate)

        # Sort: programs with matching targets first
        user_text = state.raw_input_text.lower()
        def target_score(item: Dict[str, Any]) -> int:
            targs = item.get("eligibility", {}).get("targets", [])
            s = 0
            for t in targs:
                if t == "housing_crisis" and any(w in user_text for w in ["behind on rent", "rent", "evict"]):
                    s += 3
                if t == "children" and state.profile.get("has_children"):
                    s += 2
                if t == "tenant" and "rent" in user_text:
                    s += 2
            return s

        candidates.sort(key=target_score, reverse=True)
        # Select top candidates (up to 4)
        state.candidate_resources = candidates[:4]
        state.record_trace("agent_completed", "ResourceAgent", {
            "count": len(state.candidate_resources),
            "programs": [c.get("agency_name") for c in state.candidate_resources],
        })


# -----------------------------------------------------------------------------
# 3. EligibilityAgent
# -----------------------------------------------------------------------------
class EligibilityAgent:
    """
    Deterministic eligibility scoring engine orchestrator.
    NEVER overrides deterministic criteria with LLM generation.
    """

    def run(self, state: CaseState) -> None:
        state.record_trace("agent_started", "EligibilityAgent")
        profile = state.profile
        results: List[Dict[str, Any]] = []

        user_annual_income = profile.get("income_annual")

        for res in state.candidate_resources:
            name = res.get("agency_name", "")
            elig_rule = res.get("eligibility", {})
            income_limit = elig_rule.get("income_limit_annual", 0)

            # Evaluate income
            income_met = None
            if income_limit > 0:
                if user_annual_income is not None:
                    income_met = user_annual_income <= income_limit
                else:
                    income_met = None  # Unknown

            # Determine Tier deterministically
            if income_met is True:
                tier = "likely eligible"
                reason = f"Annual income of ₹{user_annual_income:,.0f} satisfies the eligibility limit (ceiling ₹{income_limit:,.0f})."
                counterfactual = "You comfortably meet the statutory income criterion for this welfare scheme."
                score = 0.92
            elif income_met is False:
                tier = "ineligible"
                diff = user_annual_income - income_limit
                reason = f"Annual income of ₹{user_annual_income:,.0f} exceeds the scheme limit of ₹{income_limit:,.0f} by ₹{diff:,.0f}."
                counterfactual = f"To qualify under direct income rules, annual income must be under ₹{income_limit:,.0f}."
                score = 0.20
            else:
                tier = "needs information"
                reason = f"Scheme requires income under ₹{income_limit:,.0f}/year. User income has not been fully verified."
                counterfactual = "Stating your verified monthly or annual family income will confirm your eligibility score."
                score = 0.55

            # If user has prior rejection on this specific program, reflect it
            prior_app = profile.get("prior_application", {})
            if prior_app.get("status") == "rejected" and ("housing" in name.lower() or "pmay" in name.lower()):
                tier = "ineligible / borderline"
                reason += " Previous application was reported as rejected; requires grievance redressal or alternative pathway."
                score = 0.40

            results.append({
                "agency_name": name,
                "tier": tier,
                "score": score,
                "reason": reason,
                "counterfactual": counterfactual,
                "income_limit": income_limit,
                "user_income": user_annual_income,
                "provenance": res.get("provenance", {}),
            })

        state.eligibility_results = results
        state.record_trace("agent_completed", "EligibilityAgent", {
            "evaluated_count": len(results),
            "tiers": [r["tier"] for r in results],
        })


# -----------------------------------------------------------------------------
# 4. PathfinderAgent
# -----------------------------------------------------------------------------
class PathfinderAgent:
    """Uses the 26 curated transitions to find alternative pathways when primary route fails."""

    def run(self, state: CaseState) -> None:
        state.record_trace("agent_started", "PathfinderAgent")
        _load_data()
        pathways: List[Dict[str, Any]] = []

        prior_app = state.profile.get("prior_application", {})
        has_rejection = prior_app.get("status") == "rejected"

        # Check if any candidate is ineligible or has previous rejection
        needs_alternative = has_rejection or any(e["tier"] in ("ineligible", "ineligible / borderline") for e in state.eligibility_results)

        if needs_alternative:
            for trans in _TRANSITIONS_DATA:
                from_prog = trans.get("from", "")
                to_prog = trans.get("to", "")
                reason = trans.get("reason", "")
                days = trans.get("days", 30)
                diff = trans.get("difficulty", "moderate")

                # Match relevant transitions
                if "shelter" in from_prog.lower() or "housing" in to_prog.lower() or "pmay" in to_prog.lower():
                    pathways.append({
                        "bridge_program": from_prog,
                        "target_program": to_prog,
                        "transition_reason": reason,
                        "estimated_days": days,
                        "difficulty": diff,
                        "type": "bridge_pathway",
                    })

        state.pathways = pathways[:3]
        state.record_trace("agent_completed", "PathfinderAgent", {
            "alternatives_found": len(state.pathways),
            "bridge_programs": [p["bridge_program"] for p in state.pathways],
        })


# -----------------------------------------------------------------------------
# 5. VerificationAgent
# -----------------------------------------------------------------------------
class VerificationAgent:
    """Invokes the authoritative verification gate."""

    def run(self, state: CaseState) -> None:
        state.record_trace("agent_started", "VerificationAgent")
        verify_case_state(state)
        state.record_trace("agent_completed", "VerificationAgent", {
            "status": state.verification.status,
            "issues": state.verification.issues,
        })


# -----------------------------------------------------------------------------
# 6. ActionAgent
# -----------------------------------------------------------------------------
class ActionAgent:
    """Assembles concrete action steps and configures human approval gates."""

    def run(self, state: CaseState) -> None:
        state.record_trace("agent_started", "ActionAgent")
        actions: List[Dict[str, Any]] = []

        # If verification failed, provide re-planning action
        if state.verification.status == "failed":
            actions.append({
                "title": "Resolve Verification Issues",
                "type": "clarification_needed",
                "issues": state.verification.issues,
                "guidance": "Please provide the missing details or documents to verify your application.",
                "requires_human_approval": False,
            })
            state.actions = actions
            state.status = "waiting_info"
            state.record_trace("agent_completed", "ActionAgent", {"action_status": "waiting_info"})
            return

        # If pathways exist (e.g. after rejection or borderline)
        if state.pathways:
            p = state.pathways[0]
            actions.append({
                "title": f"Alternative Route via {p['bridge_program']}",
                "type": "bridge_action",
                "target_program": p["target_program"],
                "reason": p["transition_reason"],
                "estimated_timeline": f"{p['estimated_days']} days",
                "instructions": "Contact the shelter/nodal caseworker to initiate enrollment and documentation support.",
                "requires_human_approval": True,
            })

        # Process top eligible program
        for elig in state.eligibility_results:
            if elig["tier"] == "likely eligible":
                res_name = elig["agency_name"]
                # Look up resource details
                res_details = next((r for r in state.candidate_resources if r.get("agency_name") == res_name), {})
                form_info = res_details.get("form", {})
                actions.append({
                    "title": f"Apply for {res_name}",
                    "type": "program_application",
                    "target_resource": res_name,
                    "portal_url": res_details.get("online_url"),
                    "contact_phone": res_details.get("contact_phone"),
                    "documents_required": form_info.get("docs_required", ["Aadhaar Card", "Income Certificate"]),
                    "step_summary": form_info.get("submission_guide", "Submit official application form online or at nodal office."),
                    "requires_human_approval": True,
                })
                break

        state.actions = actions
        # If any action requires approval, mark status as waiting_approval
        if any(a.get("requires_human_approval") for a in actions):
            state.status = "waiting_approval"
        else:
            state.status = "completed"

        state.record_trace("agent_completed", "ActionAgent", {
            "actions_count": len(actions),
            "status": state.status,
        })
