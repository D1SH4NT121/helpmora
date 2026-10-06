<div align="center">

# HELPmora

### Deterministic Social Welfare & Legal Aid Navigator
**A rules engine on an object-spatial knowledge graph that routes citizens in hardship to the housing, food, healthcare, and legal aid programs they qualify for — with zero hallucinations, complete explainability, and zero API keys required.**

[![Python](https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square)](https://www.python.org/)
[![Jaclang](https://img.shields.io/badge/jaclang-0.15.1-6366f1.svg?style=flat-square)](https://www.jac-lang.org/)
[![Tests](https://img.shields.io/badge/tests-passing-10b981?style=flat-square)](./helpmora/tests)
[![Privacy](https://img.shields.io/badge/privacy-scrubbed%20%C2%B7%20no%20tracking-0f766e?style=flat-square)](./PRIVACY.md)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](./LICENSE)

*Maintained by [@D1SH4NT121](https://github.com/D1SH4NT121) · [GitHub Repository](https://github.com/D1SH4NT121/helpmora)*

</div>

---

## The Problem

Millions of vulnerable individuals — single parents, daily wage earners, unhoused families, and elderly citizens — do not know which social welfare schemes they qualify for, what documents they must assemble, or which office to visit. In India, statutory programs such as **PMAY (Housing)**, **PMGKAY (Food Security)**, **Ayushman Bharat (Healthcare)**, and **NALSA (Free Legal Aid)** exist to guarantee fundamental rights, but they sit behind fragmented portals, complex income brackets, and bureaucratic red tape.

When citizens consult standard generative AI chatbots, those models frequently **hallucinate** eligibility criteria, quote outdated numbers, or give false hope.

**HELPmora** transforms a single conversational message, in the person's own words and language, into an explainable, ranked action plan. It evaluates exact rules in closed form over a live knowledge graph in less than a millisecond, provides direct phone numbers and physical submission channels, and explains the plain-language reason for every recommendation.

---

## What Makes HELPmora Different

### 1. Math First, LLM Last (Zero Hallucination Guarantee)
Every critical decision — who qualifies, why, what documents are required, and what to do first — is computed in closed form over a Jac graph without calling an external language model on the critical evaluation path. Language models are strictly auxiliary (used optionally for summary or fallback drafting).

### 2. Comprehensive 40-Program Indian Welfare Catalog
HELPmora is pre-seeded with 40 authentic Indian central and state welfare programs across four domains:
- **Housing (10 Programs):** PMAY-Urban, PMAY-Gramin, Shelter for Urban Homeless (SUH-NULM), Shakti Sadan (Swadhar Greh), Affordable Rental Housing Complexes (ARHCs), Working Women Hostels (Sakhi Niwas), PM SVANidhi Vendor Support, Rashtriya Vayoshri Senior Living, SDRF Disaster Shelters, Slum Rehabilitation Authority (SRA).
- **Food Security (10 Programs):** Pradhan Mantri Garib Kalyan Anna Yojana (PMGKAY), Antyodaya Anna Yojana (AAY 35kg grain), One Nation One Ration Card (ONORC Portability), Mission Poshan 2.0 (ICDS Anganwadi), PM POSHAN (Mid-Day Meals), Subsidized Urban Canteens, PMMVY Maternity Nutrition, Annapurna Scheme for Seniors, Akshaya Patra Relief, Food Security Helpline 1967.
- **Healthcare (10 Programs):** Ayushman Bharat PM-JAY (₹5 Lakh Cover + 70+ Seniors), Jan Aushadhi Kendras (50-90% Generic Medicine Discount), Ayushman Arogya Mandirs (Health & Wellness Centres), Tele-MANAS (14416), Janani Suraksha Yojana & JSSK, Rashtriya Arogya Nidhi (RAN), National TB Elimination & Nikshay Poshan, ESIC Medical Benefits, NACO ART Centers (Free HIV Care), eSanjeevani Teleconsultations.
- **Legal Aid (10 Programs):** NALSA Free Legal Aid Clinics (Section 12), Tele-Law (CSCs / Dept of Justice), One Stop Centres (OSC Sakhi), DLSA Lok Adalat (Pre-Litigation Settlement), Childline 1098 & DCPU, National Cyber Crime Portal (1930), Senior Citizens Maintenance Tribunal (2007 Act), Labour Commissioner Conciliation & e-Shram, Consumer Disputes Redressal (e-Daakhil), National Human Rights Commission (NHRC).

### 3. Multi-Step Escape Path Pathfinder
When direct eligibility fails (for example, an applicant lacking formal land records or a permanent address), HELPmora does not simply return an "application denied" screen. The **PathfinderWalker** traverses 26 curated `leads_to` graph edges using bounded breadth-first search to find transition pathways:
> **Example:** Shelter for Urban Homeless (SUH) $ightarrow$ Biometric Aadhaar & Job Card Enrollment $ightarrow$ PMAY-Urban EWS In-situ Rehabilitation Allotment (estimated 60-day roadmap).

### 4. Deterministic Crisis & Emergency Routing
Messages indicating acute crisis, domestic abuse, child endangerment, or financial cyber fraud bypass normal queuing and immediately surface verified toll-free helplines:
- **112**: Emergency Response Support System (Police / Ambulance / Disaster)
- **181**: Women Helpline (24/7 Domestic Violence & Shelter Support)
- **1098**: Childline (Child Protection & Abuse Rescue)
- **14416**: Tele-MANAS (24/7 Mental Health Crisis Support)
- **1930**: National Cyber Crime Reporting Portal (Financial Fraud Lien Freezing)
- **1967**: National Food Security Helpline (Ration Grievances)

### 5. Zero API Keys Required
HELPmora runs **100% out-of-the-box locally** without requiring OpenAI, Anthropic, or any third-party paid API keys. The rules engine, graph traversals, and local templates provide complete functionality with zero cloud subscription costs.

### 6. Safety & Privacy by Construction
- **Quick Exit:** A prominent red button and keyboard shortcut (pressing Shift three times) immediately redirects the browser to a neutral page.
- **State Persistence:** Preserves chat state and active tab selections across browser reloads using `sessionStorage` and URL hash navigation.
- **Zero Tracking:** No user names, Aadhaar numbers, or raw personal messages are written to persistent server logs.

---

## Architecture Overview

HELPmora is built on **Jaclang** and Python 3.12, utilizing Jac's object-spatial programming paradigm (Nodes, Edges, Walkers):

```
+-------------------------------------------------------------------------+
|                              USER CHAT                                  |
|         "I am a single mother earning ₹8,000/mo needing food & rent"     |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  1. INTAKE & PROFILE EXTRACTION                         |
|   Extracts: Category (Food/Housing), Income (₹96k/yr), Flags (Single)   |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|              2. DETERMINISTIC GRAPH SCORING ENGINE                      |
|   Closed-form math: Hard gates (Age/Status) * Soft gates (Income/Need)  |
|   Zero LLM on critical path — 40 Indian schemes scored in < 1ms         |
+-------------------+--------------------------------+--------------------+
                    |                                |
       (Direct Eligible)                   (Ineligible / Need Info)
                    v                                v
+----------------------------+     +--------------------------------------+
| 3. PRIMARY ACTION PLAN     |     | 4. MULTI-STEP PATHFINDER             |
| - Scheme details & office  |     | - Traverses 26 graph escape edges    |
| - Exact checklist of docs  |     |   e.g., Night Shelter -> PMAY-U EWS  |
| - Form & offline deadline  |     | - Counterfactual: "₹1,200 over limit"|
+----------------------------+     +--------------------------------------+
                    ^                                ^
                    +----------------+---------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  5. PRESENTATION & AUDIT TELEMETRY                      |
|   Renders recommendation cards, chips, and crisis hotlines (112, 181)   |
+-------------------------------------------------------------------------+
```

### The Seven-Walker Pipeline
1. **SeedWalker (`walkers/seed.jac`)**: Idempotently seeds the 40 welfare schemes and 26 transition edges into the graph.
2. **IntakeWalker (`walkers/intake.jac`)**: Detects language, extracts category, urgency, and household financial context.
3. **EligibilityWalker (`walkers/eligibility.jac`)**: Evaluates all 40 programs against policy constraints in sub-millisecond execution.
4. **PathfinderWalker (`walkers/pathfinder.jac`)**: Traverses `leads_to` transition edges to find multi-step workarounds.
5. **NavigationWalker (`walkers/navigation.jac`)**: Compiles the ranked `ActionPlan`, required documents, and offline steps.
6. **EscalationWalker (`walkers/escalation.jac`)**: Deterministically routes crisis scenarios to verified national helplines.
7. **MemoryWalker & CritiqueWalker (`walkers/memory.jac`, `walkers/critique.jac`)**: Manages session insights and telemetry.

---

## Quick Start Guide

### Prerequisites
- **Python 3.12+** (configured in `.venv312`)
- **Git**

### Running Locally (Windows)
Clone the repository and launch via the provided startup script:

```powershell
# Clone the repository
git clone https://github.com/D1SH4NT121/helpmora.git
cd helpmora

# Launch via PowerShell
.un.ps1

# Or via Command Prompt
run.bat
```

Open your browser and navigate to:
```
http://localhost:8000/
```

### Running with Docker
```bash
docker build -t helpmora .
docker run -p 8000:8000 helpmora
```

---

## Verification & Automated Tests

All tests run locally without external cloud dependencies:

```powershell
$env:PYTHONPATH = "helpmora"

# 1. Schema & Seed Graph Smoke Test (Verifies 40 programs seed cleanly)
python -m jaclang test helpmora/tests/test_schema.jac

# 2. Policy Engine Verification (Verifies statutory calculation rules)
python -m jaclang run helpmora/tests/check_policy.jac

# 3. Message Catalogs Linting (Verifies 50 i18n language catalogs)
python -m jaclang run helpmora/tests/check_messages.jac

# 4. Gateway & Security Verification (Rate limiting, payload caps, JWTs)
python -m unittest helpmora/tests/test_cmguard.py
```

---

## Project Structure

```
HELPmora/
├── .github/                  # CI workflows, codeowners, PR templates
├── docs/                     # Architecture, deployment, and demo docs
│   ├── DEMO_SCRIPT.md        # 3-minute video recording walkthrough
│   ├── DEPLOY.md             # Render & Docker deployment instructions
│   ├── DEVPOST_WRITEUP.md    # Detailed project submission writeup
│   ├── MAINTENANCE.md        # Engine architecture & portability guide
│   └── TRANSLATION_REVIEW.md # Human translation review workflow
├── helpmora/                 # Core application package
│   ├── app.jac               # Main Jaclang server entrypoint
│   ├── cmguard/              # Reverse security gateway & rate limiters
│   ├── components/           # Client-side UI components (React / Jac)
│   │   ├── ActionPlan.cl.jac # Step-by-step checklist & document guide
│   │   ├── ChatPane.cl.jac   # Conversational intake & emergency footer
│   │   ├── GraphViz.cl.jac   # Interactive decision graph visualization
│   │   ├── HELPmoraLogo.cl.jac # Animated Guided Thread logo
│   │   └── LandingPage.cl.jac# Landing page & CTA header
│   ├── data/                 # Social welfare program definitions
│   │   ├── resources.json    # 40 Indian Social Welfare Programs
│   │   ├── transitions.json  # 26 Multi-step escape transition edges
│   │   └── i18n/             # Localized message catalogs (50 languages)
│   ├── engine/               # Deterministic scoring, parsing, and policy
│   ├── graph/                # Node and edge model definitions
│   ├── tests/                # Automated smoke, policy, and security tests
│   └── walkers/              # Jac walkers (Seed, Intake, Eligibility, etc.)
├── Dockerfile                # Production Docker build container
├── LICENSE                   # MIT License
├── PRIVACY.md                # Privacy guarantees & data scrubbing notice
├── README.md                 # Project documentation
├── SECURITY.md               # Responsible security disclosure policy
├── run.bat                   # Windows CMD one-click launcher
└── run.ps1                   # Windows PowerShell one-click launcher
```

---

## License

This project is open-source and released under the [MIT License](./LICENSE).  
Maintained by **[@D1SH4NT121](https://github.com/D1SH4NT121)**.
