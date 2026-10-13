# HELPmora Five-Minute Hackathon Demo

Keep the recording under five minutes. Use synthetic test data and show the real running application and execution trace.

## 0:00–0:25 — Problem

“People often need welfare or legal aid at the same time they are dealing with job loss, healthcare costs, housing insecurity, or missing documents. Finding the right program and the next step can be confusing.”

## 0:25–0:50 — Product

“HELPmora is a voice-first civic welfare and free legal-aid navigator for India. It converts a person's story into structured case state, evaluates configured program rules deterministically, and guides the user toward a practical next step.”

## 0:50–1:35 — Omi

Speak a synthetic query through the configured Omi app. Show the actual Omi-originated event reaching the backend. Show the source/channel in the trace. Do not call browser voice Omi.

## 1:35–2:10 — Qdrant

Show user-scoped memory retrieval. If the first request finds no previous case, show an explicit empty result. Store a consented synthetic case milestone and later retrieve it in a fresh request/session.

## 2:10–2:55 — Lyzr

Show the actual Manager/agent calls and structured result. Explain what each agent is responsible for. Never show static agent names as proof of execution.

## 2:55–3:45 — Jac policy engine and Pathfinder

Show the actual deterministic Jac tool result. If a route is blocked, show the existing Pathfinder search over curated transitions. Emphasize that the LLM does not decide statutory eligibility.

## 3:45–4:25 — Guided action

Show a missing-fact question, document list, next-step explanation, and explicit user confirmation before any consequential action.

## 4:25–4:45 — Resume or forget

Demonstrate real memory retrieval on a subsequent turn, or demonstrate that the Forget action removes the synthetic case from the applicable stores.

## 4:45–5:00 — Close

“HELPmora connects voice, persistent memory and multi-agent orchestration to a deterministic civic policy engine—so the system can guide a person without allowing an LLM to make the authoritative eligibility decision.”

## Recording checklist

- [ ] Omi input is genuinely from Omi.
- [ ] Qdrant write and later retrieval are real.
- [ ] Lyzr execution is real and traceable.
- [ ] The Jac tool/result is real.
- [ ] No real user data or credentials appear on screen.
- [ ] The video is no longer than five minutes.
- [ ] URLs are tested before submission.
