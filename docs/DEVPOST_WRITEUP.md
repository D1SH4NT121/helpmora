# HELPmora — Project Overview & Writeup

> **Repository:** [https://github.com/D1SH4NT121/helpmora](https://github.com/D1SH4NT121/helpmora)  
> **Maintainer:** [@D1SH4NT121](https://github.com/D1SH4NT121)  
> **License:** MIT Open Source

---

## Inspiration

Hundreds of millions of vulnerable citizens — daily wage earners, single mothers, elderly pensioners, and migrant workers — struggle to access social welfare benefits. In India, schemes like **PMAY (Housing)**, **PMGKAY (Food Security)**, **Ayushman Bharat (Healthcare)**, and **NALSA (Free Legal Aid)** are constitutionally established rights. Yet, they remain hidden behind bureaucratic complexity, fragmented departmental portals, and dense regulatory jargon.

When people turn to general generative AI chatbots for help, those models frequently hallucinate eligibility requirements, cite outdated income ceilings, or fail to explain why an application was rejected. We built **HELPmora** to solve this: a deterministic, privacy-first civic navigator that matches any citizen to verified social welfare programs in under a minute, with zero hallucinations and zero external API dependencies.

---

## What It Does

HELPmora accepts free-form messages in any language (English, Hindi, Bengali, Telugu, Tamil, Marathi, and 45+ other regional languages) and processes them through an explainable, graph-native pipeline running on **Jaclang** and Python 3.12.

### Three Key Architectural Innovations

1. **Deterministic Eligibility Engine (Math First, LLM Last)**
   - Instead of asking a large language model to judge eligibility, HELPmora computes eligibility in closed form over a typed knowledge graph in less than a millisecond.
   - It combines hard statutory gates (age, citizenship status) with calibrated logistic curves over household income:
     $$c = \sigma\left(k \cdot \frac{L - I}{L}\right)$$
     where $L$ is the policy threshold and $I$ is household income.
   - This prevents "cliff" rejections and generates clear, actionable counterfactuals (e.g., *"You would qualify if annual income was under ₹1,50,000 — you are ₹12,000 over"*).

2. **Escape Path Pathfinder (Multi-Hop Graph Traversal)**
   - When a citizen does not directly qualify for an end-state program, traditional portals simply reject them.
   - HELPmora traverses 26 curated `leads_to` graph edges using bounded breadth-first search to find transition pathways:
     - *Night Shelter (SUH)* $\rightarrow$ *Biometric Aadhaar Generation* $\rightarrow$ *PMAY-Urban EWS In-situ Allotment*
     - *Tele-MANAS Crisis Counseling* $\rightarrow$ *DLSA Legal Aid Advocate Appointment*
     - *Primary Health Wellness Centre* $\rightarrow$ *Jan Aushadhi 90% Generic Medicine Dispensation*
   - Returns estimated time-to-resolution (in days) and step difficulty.

3. **Outcome-Learning Prior & Reflexion Memory**
   - Every `EligibilityRuleNode` stores Bayesian priors based on real-world approval outcomes recorded by `MemoryWalker`.
   - After each turn, `CritiqueWalker` computes a session quality score without LLM overhead and records a `SessionInsight` node.
   - The system preserves session state locally via browser storage (`sessionStorage`) and URL hash routing, ensuring seamless page-reload persistence.

---

## The 4 Core Domains (40 Programs Catalog)

- **Housing (10 Programs):** PMAY-Urban, PMAY-Gramin, Shelter for Urban Homeless (SUH-NULM), Shakti Sadan (Swadhar Greh), Affordable Rental Housing Complexes (ARHCs), Sakhi Niwas (Working Women Hostels), PM SVANidhi Vendor Support, Rashtriya Vayoshri Senior Living, SDRF Disaster Shelters, Slum Rehabilitation Authority (SRA).
- **Food Security (10 Programs):** PM Garib Kalyan Anna Yojana (PMGKAY), Antyodaya Anna Yojana (AAY), One Nation One Ration Card (ONORC Portability), Mission Poshan 2.0 (ICDS Anganwadi), PM POSHAN (Mid-Day Meals), Subsidized Urban Canteens, PMMVY Maternity Nutrition, Annapurna Scheme for Seniors, Akshaya Patra Relief, Food Security Helpline 1967.
- **Healthcare (10 Programs):** Ayushman Bharat PM-JAY (₹5 Lakh Cover + 70+ Seniors), PMBJP Jan Aushadhi Kendras, Ayushman Arogya Mandirs (Health & Wellness Centres), Tele-MANAS (14416), Janani Suraksha Yojana & JSSK, Rashtriya Arogya Nidhi (RAN), NTEP TB Elimination & Nikshay Poshan, ESIC Medical Benefits, NACO ART Centers (Free HIV Care), eSanjeevani Teleconsultations.
- **Legal Aid (10 Programs):** NALSA Free Legal Aid Clinics, Tele-Law (CSCs / Dept of Justice), One Stop Centres (OSC Sakhi), DLSA Lok Adalat, Childline 1098 & DCPU, National Cyber Crime Portal (1930), Senior Citizens Maintenance Tribunal (2007 Act), Labour Commissioner Conciliation & e-Shram, Consumer Disputes Redressal (e-Daakhil), National Human Rights Commission (NHRC).

---

## Verified Safety & Privacy

- **National Emergency Lines:** Real-time routing to **112** (Emergency), **181** (Women Helpline), **1098** (Childline), **14416** (Tele-MANAS), and **1930** (Cyber Crime).
- **Quick Exit:** A dedicated quick-exit button and keyboard shortcut (Shift three times) instantly navigates to a neutral page.
- **Zero Tracking:** No user names or personal identifiers are stored. Server logs do not persist message transcripts.

---

## Running Locally

```bash
# Windows PowerShell
.\run.ps1

# Or Windows Command Prompt
run.bat
```
App boots locally at: `http://localhost:8000/`.
