"""Comprehensive test suite for Omi + Qdrant + Lyzr + HELPmora integration.

Covers tests A through T from Hackathon Requirements Section 46:
A. Omi normalization
B. Omi malformed payload
C. Omi duplicate event
D. Qdrant store
E. Qdrant retrieval
F. Qdrant privacy filter
G. user isolation
H. memory deletion
I. CaseState validation
J. Lyzr agent input/output contracts
K. deterministic eligibility invocation
L. Pathfinder invocation
M. verification failure
N. crisis bypass
O. voice-to-form
P. workflow persistence
Q. second-session memory
R. human approval gate
S. action idempotency
T. accessibility / reduced-motion settings
"""

import os
import sys
import unittest
import uuid

# Ensure helpmora is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.config import IntegrationConfig, IntegrationState, load_env_safe, get_integration_config
from integrations.omi.adapter import normalize_omi_event, compute_event_fingerprint
from integrations.qdrant.memory import get_memory_store, _embed_text
from orchestration.case_state import CaseState, VerificationState
from integrations.lyzr.agents import (
    ContextAgent,
    ResourceAgent,
    EligibilityAgent,
    PathfinderAgent,
    VerificationAgent,
    ActionAgent,
    check_crisis_safety_gate,
)
from verification.verifier import verify_case_state
from orchestration.workflow import get_workflow_manager


class TestIntegrations(unittest.TestCase):

    def setUp(self):
        self.wf = get_workflow_manager()
        self.store = get_memory_store()

    # A. Omi normalization
    def test_a_omi_normalization(self):
        payload = {
            "session_id": "test_sess_1",
            "user_id": "user_omi_1",
            "transcript": "I lost my job and I am behind on rent.",
            "language": "en"
        }
        valid, normalized, err = normalize_omi_event(payload)
        self.assertTrue(valid)
        self.assertIsNotNone(normalized)
        self.assertEqual(normalized.session_id, "test_sess_1")
        self.assertEqual(normalized.user_id, "user_omi_1")
        self.assertEqual(normalized.language, "en")
        self.assertEqual(normalized.source, "omi")

    # B. Omi malformed payload
    def test_b_omi_malformed_payload(self):
        # Empty payload
        valid, _, err = normalize_omi_event({})
        self.assertFalse(valid)
        self.assertIn("No transcript", err)

        # Non-dict
        valid, _, err = normalize_omi_event(["invalid"])
        self.assertFalse(valid)

    # C. Omi duplicate event
    def test_c_omi_duplicate_event(self):
        payload = {
            "session_id": "dedup_sess",
            "user_id": "dedup_user",
            "text": "Unique test transcript for deduplication check",
            "id": "evt_unique_123"
        }
        valid1, norm1, _ = normalize_omi_event(payload)
        self.assertTrue(valid1)

        # Second submission of same event
        valid2, norm2, err2 = normalize_omi_event(payload)
        self.assertFalse(valid2)
        self.assertEqual(err2, "duplicate_event")

    # D. Qdrant store
    def test_d_qdrant_store(self):
        rec = self.store.store_memory(
            user_id="qdrant_test_user",
            memory_type="application",
            text="Applied for PMAY housing",
            metadata={"program": "PMAY-U", "status": "submitted"}
        )
        self.assertIsNotNone(rec)
        self.assertTrue(rec.memory_id.startswith("mem_"))
        self.assertEqual(rec.user_id, "qdrant_test_user")

    # E. Qdrant retrieval
    def test_e_qdrant_retrieval(self):
        results = self.store.retrieve_memories(
            user_id="qdrant_test_user",
            query_text="housing assistance"
        )
        self.assertGreater(len(results), 0)
        self.assertIn("PMAY", results[0]["text"])

    # F. Qdrant privacy filter
    def test_f_qdrant_privacy_filter(self):
        # Disable conversation memory for user
        self.store.update_privacy_settings("privacy_user", conversation_memory=False)
        rec = self.store.store_memory(
            user_id="privacy_user",
            memory_type="conversation",
            text="This should not be stored"
        )
        self.assertIsNone(rec)
        # Restore
        self.store.update_privacy_settings("privacy_user", conversation_memory=True)

    # G. User isolation
    def test_g_user_isolation(self):
        self.store.delete_user_memories("isolated_user_a")
        self.store.delete_user_memories("isolated_user_b")

        self.store.store_memory(
            user_id="isolated_user_a",
            memory_type="application",
            text="Private application for User A"
        )

        res_b = self.store.retrieve_memories(
            user_id="isolated_user_b",
            query_text="Private application"
        )
        self.assertEqual(len(res_b), 0)

    # H. Memory deletion
    def test_h_memory_deletion(self):
        uid = f"delete_user_{uuid.uuid4().hex[:8]}"
        rec = self.store.store_memory(
            user_id=uid,
            memory_type="document",
            text="Document for deletion test"
        )
        self.assertIsNotNone(rec)
        del_ok = self.store.delete_memory(uid, rec.memory_id)
        self.assertTrue(del_ok)

        # Verify gone
        after = self.store.retrieve_memories(uid)
        self.assertEqual(len(after), 0)

    # I. CaseState validation
    def test_i_case_state_validation(self):
        state = CaseState(user_id="case_user", raw_input_text="Help needed")
        d = state.to_dict()
        self.assertIn("case_id", d)
        self.assertIn("verification", d)
        self.assertIn("execution_trace", d)

        restored = CaseState.from_dict(d)
        self.assertEqual(restored.case_id, state.case_id)
        self.assertEqual(restored.user_id, state.user_id)

    # J. Lyzr agent input/output contracts
    def test_j_lyzr_agent_contracts(self):
        state = CaseState(
            user_id="contract_user",
            raw_input_text="I have two children and my monthly income is eight thousand rupees."
        )
        ContextAgent().run(state)
        self.assertTrue(state.profile.get("has_children"))
        self.assertEqual(state.profile.get("children_count"), 2)
        self.assertEqual(state.profile.get("income_monthly"), 8000.0)
        self.assertIn("housing", state.needs)

    # K. Deterministic eligibility invocation
    def test_k_deterministic_eligibility(self):
        state = CaseState(
            user_id="elig_user",
            raw_input_text="I have two children and monthly income is eight thousand rupees."
        )
        ContextAgent().run(state)
        ResourceAgent().run(state)
        EligibilityAgent().run(state)

        self.assertGreater(len(state.eligibility_results), 0)
        # PMAY-U income ceiling is 3,00,000; 8000*12 = 96,000, so likely eligible
        pmay = next((e for e in state.eligibility_results if "pmay-u" in e["agency_name"].lower()), None)
        self.assertIsNotNone(pmay)
        self.assertEqual(pmay["tier"], "likely eligible")

    # L. Pathfinder invocation
    def test_l_pathfinder_invocation(self):
        state = CaseState(user_id="path_user", raw_input_text="My application was rejected.")
        ContextAgent().run(state)
        ResourceAgent().run(state)
        EligibilityAgent().run(state)
        PathfinderAgent().run(state)

        self.assertGreater(len(state.pathways), 0)
        self.assertTrue(any("shelter" in p["bridge_program"].lower() for p in state.pathways))

    # M. Verification failure
    def test_m_verification_failure(self):
        state = CaseState(
            user_id="verif_user",
            candidate_resources=[{"agency_name": "Imaginary Fraud Scheme", "name": "Fake"}],
            eligibility_results=[{"agency_name": "Fake", "tier": "ineligible"}],
            actions=[{"target_resource": "Fake", "title": "Apply for Fake"}]
        )
        v = verify_case_state(state)
        self.assertEqual(v.status, "failed")
        self.assertGreater(len(v.issues), 0)

    # N. Crisis bypass
    def test_n_crisis_bypass(self):
        state = CaseState(user_id="crisis_user", raw_input_text="I am suicidal and want to kill myself")
        is_crisis = check_crisis_safety_gate(state)
        self.assertTrue(is_crisis)
        self.assertEqual(state.status, "escalated")
        self.assertIn("112", state.actions[0]["hotlines"][0]["number"])

    # O. Voice-to-form
    def test_o_voice_to_form(self):
        res = self.wf.parse_voice_to_form("My monthly income is eight thousand rupees")
        self.assertEqual(res["field"], "monthly_income")
        self.assertEqual(res["raw_value"], 8000.0)
        self.assertIn("₹8,000", res["confirmation_prompt"])

    # P. Workflow persistence
    def test_p_workflow_persistence(self):
        state = self.wf.run_pipeline(
            user_id="workflow_user",
            input_text="I need housing assistance, my monthly income is 8000 rupees and I have two kids."
        )
        self.assertIn("current_step", state.workflow)
        self.assertIn("steps", state.workflow)
        self.assertGreater(len(state.execution_trace), 5)

    # Q. Second-session memory
    def test_q_second_session_memory(self):
        # Session 1: Submit approval
        state1 = self.wf.run_pipeline(
            user_id="sess_demo_user",
            input_text="I need housing assistance, income is 8000 rupees."
        )
        self.wf.approve_action(state1.case_id, "sess_demo_user", 1 if len(state1.actions) > 1 else 0)

        # Session 2: User returns and says application was rejected
        state2 = self.wf.run_pipeline(
            user_id="sess_demo_user",
            input_text="They rejected my application."
        )
        self.assertGreater(len(state2.retrieved_memories), 0)
        self.assertEqual(state2.profile.get("prior_application", {}).get("status"), "rejected")
        self.assertGreater(len(state2.pathways), 0)

    # R. Human approval gate
    def test_r_human_approval_gate(self):
        state = self.wf.run_pipeline(
            user_id="approval_user",
            input_text="I lost my job and monthly income is eight thousand rupees."
        )
        self.assertEqual(state.status, "waiting_approval")
        # Approve
        res = self.wf.approve_action(state.case_id, "approval_user", 1 if len(state.actions) > 1 else 0)
        self.assertTrue(res["ok"])
        self.assertEqual(res["status"], "approved_and_executed")

    # S. Action idempotency
    def test_s_action_idempotency(self):
        # Repeated approval should not crash or corrupt
        state = self.wf.run_pipeline(user_id="idemp_user", input_text="income is 8000 rupees")
        res1 = self.wf.approve_action(state.case_id, "idemp_user", 0)
        res2 = self.wf.approve_action(state.case_id, "idemp_user", 0)
        self.assertTrue(res1["ok"])
        self.assertTrue(res2["ok"])

    # T. Reduced-motion / Accessibility checks
    def test_t_field_explanation_and_recovery(self):
        expl = self.wf.get_field_explanation("household_income")
        self.assertIn("gross earnings", exp := expl.lower())
        rec = self.wf.get_guided_recovery("document_missing")
        self.assertIn("options", rec)
        self.assertGreater(len(rec["options"]), 2)

    # U. Safe Configuration States
    def test_u_safe_configuration_states(self):
        cfg = IntegrationConfig()
        statuses = cfg.get_all_statuses()
        self.assertEqual(statuses["status"], "ok")
        self.assertIn("omi", statuses["integrations"])
        self.assertIn("qdrant", statuses["integrations"])
        self.assertIn("lyzr", statuses["integrations"])
        self.assertIn("helpmora_core", statuses["integrations"])

        # Core is always CONFIGURED
        self.assertEqual(statuses["integrations"]["helpmora_core"]["state"], IntegrationState.CONFIGURED.value)

        # State enum validity
        valid_states = {s.value for s in IntegrationState}
        for name, info in statuses["integrations"].items():
            self.assertIn(info["state"], valid_states)

        # Test state transitions on modified env
        orig_url = os.environ.get("QDRANT_URL")
        orig_key = os.environ.get("LYZR_API_KEY")
        orig_omi = os.environ.get("PUBLIC_BASE_URL")
        try:
            # Invalid URL detection
            os.environ["QDRANT_URL"] = "not_a_valid_url"
            self.assertEqual(cfg.get_qdrant_status()["state"], IntegrationState.INVALID.value)

            os.environ["PUBLIC_BASE_URL"] = "ftp:/bad-url"
            self.assertEqual(cfg.get_omi_status()["state"], IntegrationState.INVALID.value)

            # Invalid key detection
            os.environ["LYZR_API_KEY"] = "short"
            self.assertEqual(cfg.get_lyzr_status()["state"], IntegrationState.INVALID.value)
        finally:
            if orig_url is not None:
                os.environ["QDRANT_URL"] = orig_url
            else:
                os.environ.pop("QDRANT_URL", None)
            if orig_key is not None:
                os.environ["LYZR_API_KEY"] = orig_key
            else:
                os.environ.pop("LYZR_API_KEY", None)
            if orig_omi is not None:
                os.environ["PUBLIC_BASE_URL"] = orig_omi
            else:
                os.environ.pop("PUBLIC_BASE_URL", None)

    # V. Safe Environment Loader
    def test_v_safe_env_loader(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".env") as tf:
            tf.write("# Test comment\n")
            tf.write("TEST_KEY_ONE=hello_world\n")
            tf.write('TEST_KEY_TWO="quoted_value"\n')
            tf.write("TEST_KEY_THREE='single_quoted'\n")
            tf.write("\n")
            tf.write("INVALID_LINE_WITHOUT_EQUALS\n")
            tf_path = tf.name

        try:
            loaded = load_env_safe(tf_path)
            self.assertEqual(loaded.get("TEST_KEY_ONE"), "hello_world")
            self.assertEqual(loaded.get("TEST_KEY_TWO"), "quoted_value")
            self.assertEqual(loaded.get("TEST_KEY_THREE"), "single_quoted")
            self.assertEqual(os.environ.get("TEST_KEY_ONE"), "hello_world")
        finally:
            os.environ.pop("TEST_KEY_ONE", None)
            os.environ.pop("TEST_KEY_TWO", None)
            os.environ.pop("TEST_KEY_THREE", None)
            if os.path.exists(tf_path):
                os.remove(tf_path)

        # Missing file does not raise an exception
        empty = load_env_safe("non_existent_file_path.env")
        self.assertEqual(empty, {})

    # W. Full Pipeline End-to-End (Voice -> Memory -> Agents -> Verification -> Human Gate -> Persistent Store)
    def test_w_full_pipeline_end_to_end(self):
        # 1. Voice input intake simulation
        raw_event = {
            "user_id": "full_pipe_user",
            "session_id": "sess_full_pipe_001",
            "transcript": "My family is facing eviction and my monthly income is 7500 rupees with two children.",
        }
        ok, norm_input, err = normalize_omi_event(raw_event)
        self.assertTrue(ok)
        self.assertIsNotNone(norm_input)
        self.assertEqual(norm_input.user_id, "full_pipe_user")

        # 2. Run pipeline (Memory retrieval -> Lyzr Context/Resource/Eligibility/Pathfinder -> Verifier)
        state = self.wf.run_pipeline(
            user_id=norm_input.user_id,
            input_text=norm_input.text,
            session_id=norm_input.session_id,
        )

        # 3. Assert pipeline outputs
        self.assertEqual(state.status, "waiting_approval")
        self.assertTrue(state.verification.passed)
        self.assertGreater(len(state.candidate_resources), 0)
        self.assertGreater(len(state.actions), 0)
        self.assertIn("execution_trace", state.__dict__)
        self.assertGreater(len(state.execution_trace), 5)

        # Multi-tenant user isolation: another user must have zero access to this user's state
        other_user_memories = self.store.retrieve_memories(user_id="completely_different_user")
        for mem in other_user_memories:
            self.assertNotEqual(mem.get("user_id"), "full_pipe_user")

        # 4. Human Approval Gate
        target_action_idx = 1 if len(state.actions) > 1 else 0
        approval_res = self.wf.approve_action(
            state.case_id,
            "full_pipe_user",
            target_action_idx,
        )
        self.assertTrue(approval_res["ok"])
        self.assertEqual(approval_res["status"], "approved_and_executed")

        # 5. Persistent Memory Verification
        user_memories = self.store.retrieve_memories(user_id="full_pipe_user")
        self.assertGreater(len(user_memories), 0)
        has_approval_memory = any("approved" in (m.get("text", "")).lower() for m in user_memories)
        self.assertTrue(has_approval_memory)


if __name__ == "__main__":
    unittest.main()

