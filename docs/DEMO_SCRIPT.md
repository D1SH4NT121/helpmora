# HELPmora — 3-Minute Demonstration Script

> **Architecture:** Deterministic graph-and-walker engine running on Jaclang / Python 3.12 with zero external API key requirements. 40 Indian welfare programs, 26 multi-step escape paths, and immediate crisis routing. See [README.md](../README.md) for full architecture and evaluation reports.

**Target Length:** 3:00. Recorded at 1080p, screen capture + clear voiceover. Cursor visible.

---

## 0:00 – 0:20 — Hook & The Core Problem

**On screen:** HELPmora landing page (`http://localhost:8000/`). The animated "Guided Thread" logo glows; the hero line reads *"Every bureaucratic wall has a door. HELPmora finds it."* The primary CTA *"Enter the Navigator"* is positioned above the fold.

**Voiceover:**
> "In India, hundreds of life-saving welfare programs exist — from affordable housing and grain rations to free healthcare and legal aid. But for an unorganized worker, a single mother, or an elderly citizen, navigating government portals is a maze of red tape, complex rules, and silent rejections."
>
> "Generative AI chatbots hallucinate eligibility rules. Caseworkers are overburdened. This is **HELPmora** — a deterministic, privacy-first social welfare and legal navigator that matches citizens with the exact schemes they qualify for in under a minute, with zero hallucinations and zero external API keys required."

**Action:** Hover over the *Enter the Navigator* button and click.

---

## 0:20 – 1:15 — Live Intake & Deterministic Scoring

**On screen:** The Navigator chat interface opens. The footer prominently displays verified national emergency helplines: **112 (Emergency)**, **181 (Women Helpline)**, **1098 (Childline)**, **14416 (Tele-MANAS)**, and **1930 (Cyber Crime)**.

**Action:** Type in the chat input:
> *"I am a single mother of two in Mumbai earning ₹8,000 a month. I'm struggling with rent and need food assistance for my family."*

**Press Enter.**

**Voiceover:**
> "Notice what happens behind the scenes. In less than a millisecond, the engine executes closed-form deterministic math across 40 seeded Indian welfare programs across Housing, Food, Healthcare, and Legal Aid."
>
> "Instead of letting an LLM guess, HELPmora applies calibrated logistic thresholds against official statutory rules: ₹96,000 annual income against PMAY-Urban EWS limits, Antyodaya Anna Yojana criteria, and Mission Poshan guidelines."

**On screen:** The chat returns ranked recommendations:
1. **Pradhan Mantri Garib Kalyan Anna Yojana (PMGKAY / NFSA)** — 5 kg free food grains per family member.
2. **Mission Poshan 2.0 (ICDS Anganwadi)** — Supplementary nutrition and hot cooked meals for young children.
3. **PMAY-Urban Housing for All** — EWS rental and construction subsidies with female head-of-household priority.

**Action:** Click the *Action Plan* tab. Show the step-by-step checklist of required documents (*Aadhaar Card*, *Ration Card*, *Income Certificate from Tehsildar*).

---

## 1:15 – 2:00 — Multi-Step Graph Pathfinder (Escape Paths)

**On screen:** Switch to the **Decision Flow / Graph tab**.

**Voiceover:**
> "Here is HELPmora’s signature innovation: **The Escape Path Pathfinder**."
>
> "What happens when a citizen doesn't directly qualify for permanent housing because they lack land title or a permanent address? Traditional systems return a cold 'Application Denied'."
>
> "HELPmora runs bounded graph traversal over 26 curated transition edges. It automatically identifies a multi-hop escape path: starting with **Shelter for Urban Homeless (SUH)** night shelter admission, progressing through biometric Aadhaar generation, and completing with an in-situ **PMAY-Urban** EWS rehabilitation allotment."

**Action:** Click on the graph nodes to highlight the active `leads_to` progression path.

---

## 2:00 – 2:30 — Safety & Crisis Escalation

**On screen:** Return to Chat. Demonstrate safety features.

**Action:** Type a simulated crisis distress message:
> *"I feel completely hopeless and have nowhere safe to stay tonight."*

**Voiceover:**
> "Safety is built by construction, not by model prompts. When a message indicates acute distress or violence risk, EscalationWalker immediately routes the user to official 24/7 helplines — such as Tele-MANAS at 14416 and Women Helpline 181 — with emergency shelter instructions."
>
> "And for users on shared or monitored devices, clicking **Quick Exit** (or pressing Shift three times) instantly clears the screen and redirects safely."

**Action:** Click the red **Quick Exit** button. Show instant redirection.

---

## 2:30 – 3:00 — Conclusion & Open Source Architecture

**On screen:** Return to homepage. Highlight repository badges and MIT license.

**Voiceover:**
> "HELPmora is 100% open-source, runs completely locally without paid API keys, and puts vulnerable citizens first."
>
> "Every bureaucratic wall has a door. HELPmora helps you find it."

---
