# HELPmora: Hackathon Demo Guide

Follow these exact steps to reproduce and verify the Omi + Qdrant + Lyzr + HELPmora integration end-to-end.

---

## 1. Prerequisites & Startup

### Step 1: Install Dependencies
```bash
powershell -ExecutionPolicy Bypass -File .\run.ps1
```
The application will launch automatically at `http://localhost:8000/`.

### Step 2: Verify Health Check
Open a terminal or browser and query:
```bash
curl http://localhost:8000/api/integrations/health
```
**Expected Response:**
```json
{
  "status": "ok",
  "integrations": {
    "omi": {"status": "ready", "adapter": "active"},
    "qdrant": {"status": "ready", "collection": "helpmora_memory"},
    "lyzr": {"status": "ready", "cloud_enabled": false},
    "helpmora_core": {"status": "ready", "resources": 40, "transitions": 26}
  }
}
```

---

## 2. Canonical Demo Scenario: Session 1

### Step 3: Trigger Voice Ingestion (Omi Webhook)
Simulate or speak the canonical problem through the Omi webhook:

```bash
curl -X POST http://localhost:8000/api/omi/events \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_sess_101",
    "user_id": "demo_citizen",
    "transcript": "I lost my job two months ago. I am behind on rent, I have two children, and my monthly income is eight thousand rupees.",
    "language": "en"
  }'
```

### Step 4: Observe the Multi-Agent Execution Trace
In the browser UI (or response payload), verify:
1. **Omi**: Audio normalized into `CaseState`.
2. **Qdrant**: Scoped search executed with `user_id == "demo_citizen"`.
3. **Lyzr Context Agent**: Extracted monthly income of ₹8,000, 2 children, 3 household members.
4. **Lyzr Resource Agent**: Filtered 40 official Indian programs to identify PMAY-U and SUH.
5. **Lyzr Eligibility Agent**: Deterministic policy engine evaluated against ₹3,00,000 annual EWS ceiling (₹8,000 × 12 = ₹96,000 -> `likely eligible`).
6. **Lyzr Verification Agent**: Verified catalog existence, income proofs, and program capacity (`status: passed`).
7. **Track 4 Guided Workflow**: Stepper paused at `waiting_approval`.

### Step 5: Human Approval Gate
Execute user approval for the planned application:

```bash
curl -X POST http://localhost:8000/api/workflow/approve \
  -H "Content-Type: application/json" \
  -d '{
    "run_id": "<RUN_ID_FROM_STEP_3>",
    "user_id": "demo_citizen",
    "action_index": 1
  }'
```
**Expected:** Application is approved and written into Qdrant as persistent memory.

---

## 3. Second-Session Demo: Session 2 (Persistent Memory & Rejection Recovery)

### Step 6: User Returns in a New Session
The user closes the browser or returns in a subsequent turn and states:
> *"They rejected my application."*

```bash
curl -X POST http://localhost:8000/api/helpmora/run \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_citizen",
    "text": "They rejected my application.",
    "session_id": "demo_sess_102"
  }'
```

### Step 7: Observe Qdrant Recall & Pathfinder Bridge
1. **Qdrant Memory Recall**: Automatically retrieves the prior PMAY-U application without asking the citizen to repeat their history.
2. **Lyzr Context Agent**: Detects the rejection of the previously applied program.
3. **Lyzr Eligibility Agent**: Flags PMAY-U as `ineligible / borderline` due to reported rejection.
4. **Lyzr Pathfinder Agent**: Automatically traverses the 26 curated transitions to find an alternative route:
   - **Bridge Program**: *Shelter for Urban Homeless (SUH)*
   - **Transition Reason**: *Shelter social workers assist in biometric documentation and guide re-application.*
   - **Difficulty / Timeline**: Moderate, ~60 days.

---

## 4. Track 4 Voice-to-Form & Accessibility Demo

### Step 8: Test Voice-to-Form
In the browser Adaptive Assistant tab, click **Speak Field** or send:
```bash
curl -X POST http://localhost:8000/api/workflow/voice-to-form \
  -H "Content-Type: application/json" \
  -d '{"text": "My monthly income is eight thousand rupees"}'
```
**Expected Output:**
```json
{
  "ok": true,
  "result": {
    "field": "monthly_income",
    "raw_value": 8000.0,
    "formatted_value": "₹8,000",
    "confirmation_prompt": "I've entered ₹8,000 for Monthly Income. Is that correct?"
  }
}
```

### Step 9: Field-Level Help ("Ask HELPmora")
Click **Ask HELPmora** on any difficult field, or query:
```bash
curl "http://localhost:8000/api/workflow/explain-field?field=household_income"
```
**Expected Output:** Plain-language definition explaining gross earnings and statutory criteria.

### Step 10: Privacy Controls & Memory Wiping
Wipe all personal vectors instantly:
```bash
curl -X DELETE http://localhost:8000/api/memory/user/demo_citizen
```
Verify memory is zeroed out:
```bash
curl -X POST http://localhost:8000/api/memory/retrieve \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_citizen"}'
```
**Count returned: 0.**
