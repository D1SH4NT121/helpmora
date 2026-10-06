<div align="center">

# HELPmora

### Deterministic Social Welfare & Legal Aid Navigator with Omi Voice Intake, Qdrant Semantic Memory, and Lyzr Multi-Agent Orchestration
**A rules engine on an object-spatial knowledge graph that routes citizens in hardship to the housing, food, healthcare, and legal aid programs they qualify for — with zero hallucinations, complete explainability, and zero API keys required.**

[![Python](https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square)](https://www.python.org/)
[![Jaclang](https://img.shields.io/badge/jaclang-0.15.1-6366f1.svg?style=flat-square)](https://www.jac-lang.org/)
[![Qdrant](https://img.shields.io/badge/qdrant-vector%20memory-dc2626.svg?style=flat-square)](https://qdrant.tech/)
[![Lyzr](https://img.shields.io/badge/lyzr-agent%20api-7c3aed.svg?style=flat-square)](https://www.lyzr.ai/)
[![Omi](https://img.shields.io/badge/omi-voice%20intake-0284c7.svg?style=flat-square)](https://omi.me/)
[![Tests](https://img.shields.io/badge/tests-48%20passing-10b981?style=flat-square)](./helpmora/tests)
[![Privacy](https://img.shields.io/badge/privacy-scrubbed%20%C2%B7%20no%20tracking-0f766e?style=flat-square)](./PRIVACY.md)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](./LICENSE)

*Maintained by [@D1SH4NT121](https://github.com/D1SH4NT121) · [GitHub Repository](https://github.com/D1SH4NT121/helpmora)*

</div>

---

## The Problem

Millions of vulnerable individuals — single parents, daily wage earners, unhoused families, and elderly citizens — do not know which social welfare schemes they qualify for, what documents they must assemble, or which office to visit. In India, statutory programs such as **PMAY (Housing)**, **PMGKAY (Food Security)**, **Ayushman Bharat (Healthcare)**, and **NALSA (Free Legal Aid)** exist to guarantee fundamental rights, but they sit behind fragmented portals, complex income brackets, and bureaucratic red tape.

When citizens consult standard generative AI chatbots, those models frequently **hallucinate** eligibility criteria, quote outdated numbers, or give false hope.

**HELPmora** transforms conversational input — whether spoken aloud via **Omi wearable/mobile audio** or typed into the web interface — into an explainable, ranked action plan. It evaluates exact rules in closed form over a live knowledge graph in less than a millisecond, provides direct phone numbers and physical submission channels, and explains the plain-language reason for every recommendation.

---

## Key Pillars: What Makes HELPmora Different

### 1. Math First, LLM Last (Zero Hallucination Guarantee)
Every critical decision — who qualifies, why, what documents are required, and what to do first — is computed in closed form over a Jac graph without calling an external language model on the critical evaluation path. Language models are strictly auxiliary; the deterministic policy engine (`score.jac`) holds exclusive authority over eligibility determinations.

### 2. Comprehensive 40-Program Indian Welfare Catalog
HELPmora is pre-seeded with 40 authentic Indian central and state welfare programs across four domains:
- **Housing (10 Programs):** PMAY-Urban, PMAY-Gramin, Shelter for Urban Homeless (SUH-NULM), Shakti Sadan (Swadhar Greh), Affordable Rental Housing Complexes (ARHCs), Working Women Hostels (Sakhi Niwas), PM SVANidhi Vendor Support, Rashtriya Vayoshri Senior Living, SDRF Disaster Shelters, Slum Rehabilitation Authority (SRA).
- **Food Security (10 Programs):** Pradhan Mantri Garib Kalyan Anna Yojana (PMGKAY), Antyodaya Anna Yojana (AAY 35kg grain), One Nation One Ration Card (ONORC Portability), Mission Poshan 2.0 (ICDS Anganwadi), PM POSHAN (Mid-Day Meals), Subsidized Urban Canteens, PMMVY Maternity Nutrition, Annapurna Scheme for Seniors, Akshaya Patra Relief, Food Security Helpline 1967.
- **Healthcare (10 Programs):** Ayushman Bharat PM-JAY (₹5 Lakh Cover + 70+ Seniors), Jan Aushadhi Kendras (50-90% Generic Medicine Discount), Ayushman Arogya Mandirs (Health & Wellness Centres), Tele-MANAS (14416), Janani Suraksha Yojana & JSSK, Rashtriya Arogya Nidhi (RAN), National TB Elimination & Nikshay Poshan, ESIC Medical Benefits, NACO ART Centers (Free HIV Care), eSanjeevani Teleconsultations.
- **Legal Aid (10 Programs):** NALSA Free Legal Aid Clinics (Section 12), Tele-Law (CSCs / Dept of Justice), One Stop Centres (OSC Sakhi), DLSA Lok Adalat (Pre-Litigation Settlement), Childline 1098 & DCPU, National Cyber Crime Portal (1930), Senior Citizens Maintenance Tribunal (2007 Act), Labour Commissioner Conciliation & e-Shram, Consumer Disputes Redressal (e-Daakhil), National Human Rights Commission (NHRC).

### 3. Multi-Step Escape Path Pathfinder
When direct eligibility fails (for example, an applicant lacking formal land records or a permanent address), HELPmora does not simply return an "application denied" screen. The **PathfinderWalker** traverses 26 curated `leads_to` graph edges using bounded breadth-first search to find transition pathways:
> **Example:** Shelter for Urban Homeless (SUH) $\rightarrow$ Biometric Aadhaar & Job Card Enrollment $\rightarrow$ PMAY-Urban EWS In-situ Rehabilitation Allotment (estimated 60-day roadmap).

### 4. Deterministic Crisis & Emergency Routing
Messages indicating acute crisis, domestic abuse, child endangerment, or financial cyber fraud bypass normal queuing and immediately surface verified toll-free helplines:
- **112**: Emergency Response Support System (Police / Ambulance / Disaster)
- **181**: Women Helpline (24/7 Domestic Violence & Shelter Support)
- **1098**: Childline (Child Protection & Abuse Rescue)
- **14416**: Tele-MANAS (24/7 Mental Health Crisis Support)
- **1930**: National Cyber Crime Reporting Portal (Financial Fraud Lien Freezing)
- **1967**: National Food Security Helpline (Ration Grievances)

### 5. Multi-Session Episodic Memory (Qdrant)
Persistent citizen memory without tracking. HELPmora uses **Qdrant** vector storage to retain historical cases, prior application outcomes, and verified documents across sessions. If a citizen was previously rejected for PMAY-Urban due to missing documents, subsequent sessions immediately recognize the history and recommend the exact bridge pathway without starting from scratch.

### 6. Enterprise Multi-Agent Orchestration (Lyzr Agent API)
A directed acyclic graph (DAG) of 6 specialized autonomous agents coordinates case evaluation, contextual enrichment, deterministic eligibility validation, pathfinding, and actionable roadmap synthesis with full observable traces.

### 7. Safety & Privacy by Construction
- **Quick Exit:** A prominent red button and keyboard shortcut (pressing Shift three times) immediately redirects the browser to a neutral page.
- **Multi-Tenant Isolation:** Memory records in Qdrant are strictly isolated by `user_id == current_user_id`. Users can wipe their memory with a single click.
- **Zero Tracking:** No user names, Aadhaar numbers, or raw personal messages are written to persistent server logs.

---

## Unified Integration Architecture (Omi + Qdrant + Lyzr + HELPmora)

```
+---------------------------------------------------------------------------------------------------+
|                                        INTAKE LAYER                                               |
|   +---------------------------------------+       +-------------------------------------------+   |
|   |          Omi Voice Ingestion          |       |            Web Chat / Keyboard            |   |
|   |  - Audio Transcription Webhook        |       |  - Real-time Multi-lingual Chat           |   |
|   |  - HMAC Signature Verification        |       |  - Interactive Stepper / Manual Inputs    |   |
|   |  - SHA-256 Deduplication (10-min TTL) |       |  - Voice-to-Form Dynamic Parser           |   |
|   +-------------------+-------------------+       +---------------------+---------------------+   |
+-----------------------|-------------------------------------------------|-------------------------+
                        |                                                 |
                        +------------------------+------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                           SECURITY GATEWAY & RATE LIMITER (CMGuard)                               |
|   - Classify request: Static / Walker / Integration API (/api/omi/..., /api/memory/...)           |
|   - Token bucket rate limiting, payload byte caps, security header injection                      |
+------------------------------------------------+--------------------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                          QDRANT VECTOR STORE: EPISODIC CASE MEMORY                                |
|   - Multi-tenant collection: helpmora_memory (user_id partition filter)                           |
|   - 8 Typed records: Citizen Profile, Scheme Result, Application, Appeal, Follow-up, DocCheck     |
|   - Prior session retrieval -> Re-injected into CaseState context                                 |
+------------------------------------------------+--------------------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                             LYZR MULTI-AGENT SUPERFLOW ORCHESTRATOR                               |
|                                                                                                   |
|   +-------------------+      +--------------------+      +--------------------+                   |
|   |   ContextAgent    | ---> |   ResourceAgent    | ---> |  EligibilityAgent  |                   |
|   | (Enriches memory) |      | (Fetches catalog)  |      | (Calls score.jac)  |                   |
|   +-------------------+      +--------------------+      +---------+----------+                   |
|                                                                    |                              |
|   +-------------------+      +--------------------+                |                              |
|   |    ActionAgent    | <--- | VerificationAgent  | <--------------+                              |
|   | (Generates steps) |      | (Enforces checks)  |      +---------v----------+                   |
|   +-------------------+      +--------------------+      |  PathfinderAgent   | (If ineligible)   |
|                                                          | (26 escape edges)  |                   |
|                                                          +--------------------+                   |
|   [CrisisSafetyGate]: Evaluates high-risk keywords (112, 181, 1098, 14416 bypass)                |
+------------------------------------------------+--------------------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                          DETERMINISTIC KNOWLEDGE GRAPH & POLICY ENGINE                            |
|   - Closed-form mathematical evaluation: Hard Gates * Soft Gates                                  |
|   - 40 Indian Welfare Programs (resources.json) & 26 Escape Edges (transitions.json)              |
|   - Verification Gate: Zero hallucinations, statutory rule conformity                             |
+------------------------------------------------+--------------------------------------------------+
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                       TRACK 4: ADAPTIVE ASSISTANT (USER INTERACTION)                              |
|   - 5-Stage Stepper: Context -> Discovery -> Documents -> Escape Paths -> Submission              |
|   - Voice-to-Form Auto-Fill: Real-time confidence badges, transcript field extraction             |
|   - "Ask HELPmora": Plain-language statutory term explanations (EWS, LIG, Ration rules)           |
|   - Guided Recovery: Automated suggestions for missing documents or edge-case incomes             |
|   - Human-in-the-Loop Consent Gate: Citizen approval modal before writing applications to memory  |
|   - Accessibility Suite: High-Contrast mode, Dyslexia-Friendly font, Observable Trace drawer      |
+------------------------------------------------+--------------------------------------------------+
                                                 |
                                (Citizen Approves Application)
                                                 |
                                                 v
+---------------------------------------------------------------------------------------------------+
|                                QDRANT WRITE & STATE PERSISTENCE                                   |
|   Stores application submission, updates follow-up reminders, records telemetry trace             |
+---------------------------------------------------------------------------------------------------+
```

### The Seven-Walker Deterministic Pipeline
1. **SeedWalker (`walkers/seed.jac`)**: Idempotently seeds the 40 welfare schemes and 26 transition edges into the graph.
2. **IntakeWalker (`walkers/intake.jac`)**: Detects language, extracts category, urgency, and household financial context.
3. **EligibilityWalker (`walkers/eligibility.jac`)**: Evaluates all 40 programs against policy constraints in sub-millisecond execution.
4. **PathfinderWalker (`walkers/pathfinder.jac`)**: Traverses `leads_to` transition edges to find multi-step workarounds.
5. **NavigationWalker (`walkers/navigation.jac`)**: Compiles the ranked `ActionPlan`, required documents, and offline steps.
6. **EscalationWalker (`walkers/escalation.jac`)**: Deterministically routes crisis scenarios to verified national helplines.
7. **MemoryWalker & CritiqueWalker (`walkers/memory.jac`, `walkers/critique.jac`)**: Manages session insights and telemetry.

---

## Track 4: The Adaptive Assistant

HELPmora's **Adaptive Assistant** is specifically engineered for inclusive, accessible, and high-trust civic navigation. It features:

1. **Progressive Disclosure Stepper**: Breaks complex government schemes into five bite-sized steps:
   - **Step 1: Context & Profile** — Income, household size, category, location.
   - **Step 2: Scheme Discovery** — Eligible schemes ranked by statutory priority.
   - **Step 3: Document Verification** — Interactive checklist with status indicators.
   - **Step 4: Escape Paths** — Multi-step transition pathways if direct eligibility fails.
   - **Step 5: Review & Consent** — Summary preview with explicit human-in-the-loop consent.
2. **Voice-to-Form Auto-Fill**:
   - Parses natural spoken transcripts into structured eligibility parameters (e.g., *"I earn 12000 a month in Delhi with two children"* $\rightarrow$ `income: 144000/yr`, `household_size: 3`, `state: DL`).
   - Displays clear confidence badges on auto-filled fields.
3. **"Ask HELPmora" Contextual Explanations**:
   - Instant inline explanations for complex statutory terms like *EWS (Economically Weaker Section)*, *AAY (Antyodaya Anna Yojana)*, or *BPL Certificate*.
4. **Guided Recovery Engine**:
   - Detects when an applicant falls just outside a threshold or lacks mandatory proof (e.g., missing ration card).
   - Dynamically proposes recovery actions (e.g., apply for temporary urban shelter, obtain CSC income certificate).
5. **Human-in-the-Loop Approval Gate**:
   - No application or state record is persisted without explicit user confirmation.
   - Transparent modal allows citizens to inspect, edit, or reject the planned action before saving.
6. **Accessibility Controls**:
   - High-contrast toggle for low-vision users.
   - OpenDyslexic typography mode for readability.
   - Full keyboard navigation and quick exit emergency shortcut.

---

## API Endpoints Reference

The integration layer exposes RESTful APIs mounted through the `cmguard` reverse gateway:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/omi/events` | `POST` | Ingests Omi voice webhook transcripts with HMAC verification & deduplication. |
| `/api/helpmora/run` | `POST` | Executes the complete multi-agent workflow for a case intake. |
| `/api/helpmora/run/{run_id}` | `GET` | Retrieves run status, event traces, and synthesized action plan. |
| `/api/memory/retrieve` | `POST` | Queries Qdrant semantic memory filtered by `user_id`. |
| `/api/memory/store` | `POST` | Stores a typed memory record (`profile`, `application`, `appeal`, etc.). |
| `/api/memory/user/{user_id}` | `DELETE` | Wipes all stored memory for a user (Right to be Forgotten). |
| `/api/workflow/voice-to-form` | `POST` | Extracts form fields and confidence metrics from voice transcripts. |
| `/api/workflow/explain-field` | `POST` | Plain-language statutory explanations for form fields. |
| `/api/workflow/recovery` | `POST` | Proposes guided recovery steps for missing evidence or edge cases. |
| `/api/workflow/approve` | `POST` | Human-in-the-loop approval gate that commits application to memory. |
| `/api/integrations/health` | `GET` | Health status of Omi, Qdrant, Lyzr, and Core Engine. |

---

## Quick Start Guide

### Prerequisites
- **Python 3.12+** (configured in `.venv312`)
- **Git**

### Installation

```powershell
# 1. Clone repository
git clone https://github.com/D1SH4NT121/helpmora.git
cd helpmora

# 2. Set up virtual environment
python -m venv .venv312
.\.venv312\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the root directory (based on `.env.example`):

```bash
# Omi Webhook Configuration
OMI_WEBHOOK_SECRET=your_omi_webhook_secret_here

# Qdrant Vector Store Configuration
# If left empty, HELPmora automatically uses local on-disk / in-memory storage!
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_COLLECTION=helpmora_memory

# Lyzr Agent API Configuration
# If left empty, HELPmora automatically uses deterministic offline execution!
LYZR_API_KEY=
LYZR_ENVIRONMENT=production

# Policy Safety Invariants
HELPMORA_USE_LLM_ELIGIBILITY=0
```

> **Note:** HELPmora runs **100% locally and offline out-of-the-box**. No paid API keys are required to execute the engine, test the graph, or run the web interface.

### Running Locally

```powershell
# Launch via PowerShell
.\run.ps1

# Or launch via Command Prompt
run.bat
```

Open your browser at:
```
http://localhost:8000/
```

Navigate to the **"Adaptive Assistant (Track 4)"** tab to experience the full voice-to-form and stepper flow.

---

## Verification & Automated Tests

All tests execute locally without external cloud dependencies:

```powershell
$env:PYTHONPATH = ".;helpmora"

# 1. Integration Suite (Omi, Qdrant, Lyzr, Verification Gate, Track 4) - 20 Tests
.\.venv312\Scripts\python.exe -m unittest helpmora/tests/test_integrations.py

# 2. Reverse Gateway & Security Suite (Rate limiting, headers, payload caps) - 28 Tests
.\.venv312\Scripts\python.exe -m unittest helpmora/tests/test_cmguard.py

# 3. Schema & Seed Graph Smoke Test (Verifies 40 programs seed cleanly)
.\.venv312\Scripts\python.exe -m jaclang test helpmora/tests/test_schema.jac

# 4. Policy Engine Verification (Verifies statutory calculation rules)
.\.venv312\Scripts\python.exe -m jaclang run helpmora/tests/check_policy.jac

# 5. Message Catalogs Linting (Verifies 50 i18n language catalogs)
.\.venv312\Scripts\python.exe -m jaclang run helpmora/tests/check_messages.jac
```

---

## Project Structure

```
HELPmora/
├── .github/                      # CI workflows, codeowners, PR templates
├── docs/                         # Architecture, deployment, and demo docs
│   ├── architecture.md           # Comprehensive multi-agent & memory architecture
│   ├── demo.md                   # Step-by-step reproduction and demo guide
│   ├── DEMO_SCRIPT.md            # 3-minute video recording walkthrough
│   ├── DEPLOY.md                 # Render & Docker deployment instructions
│   ├── DEVPOST_WRITEUP.md        # Detailed project submission writeup
│   └── MAINTENANCE.md            # Engine architecture & portability guide
├── helpmora/                     # Core application package
│   ├── app.sv.jac                # Main Jaclang server entrypoint
│   ├── cmguard/                  # Reverse security gateway & rate limiters
│   ├── components/               # Client-side UI components (React / Jac)
│   │   ├── ActionPlan.cl.jac     # Step-by-step checklist & document guide
│   │   ├── AdaptiveAssistant.cl.jac # Track 4 Stepper, Voice-to-Form & Consent Gate
│   │   ├── ChatPane.cl.jac       # Conversational intake & voice button
│   │   ├── GraphViz.cl.jac       # Interactive decision graph visualization
│   │   ├── HELPmoraLogo.cl.jac   # Animated Guided Thread logo
│   │   └── LandingPage.cl.jac    # Landing page & CTA header
│   ├── data/                     # Social welfare program definitions
│   │   ├── resources.json        # 40 Indian Social Welfare Programs
│   │   ├── transitions.json      # 26 Multi-step escape transition edges
│   │   └── i18n/                 # Localized message catalogs (50 languages)
│   ├── engine/                   # Deterministic scoring, parsing, and policy
│   ├── graph/                    # Node and edge model definitions
│   ├── integrations/             # External integration adapters & routers
│   │   ├── api.py                # Unified REST API router
│   │   ├── lyzr/                 # Lyzr Agent API client & 6 specialized agents
│   │   ├── omi/                  # Omi webhook receiver & deduplication
│   │   └── qdrant/               # Qdrant client, schemas & multi-tenant store
│   ├── orchestration/            # Multi-agent SuperFlow DAG & CaseState contracts
│   ├── verification/             # Zero-hallucination verification gate
│   ├── tests/                    # Automated integration, smoke & security tests
│   └── walkers/                  # Jac walkers (Seed, Intake, Eligibility, etc.)
├── Dockerfile                    # Production Docker build container
├── LICENSE                       # MIT License
├── PRIVACY.md                    # Privacy guarantees & data scrubbing notice
├── README.md                     # Project documentation
├── requirements.txt              # Python runtime dependencies
├── run.bat                       # Windows CMD one-click launcher
└── run.ps1                       # Windows PowerShell one-click launcher
```

---

## License

This project is open-source and released under the [MIT License](./LICENSE).  
Maintained by **[@D1SH4NT121](https://github.com/D1SH4NT121)**.

