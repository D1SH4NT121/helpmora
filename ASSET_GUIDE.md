# HELPmora README Image Assets

This pack contains 10 separate diagrams. SVG files are the source of truth and are vector-scalable. Matching 2× PNG exports are supplied for previews, slides, and tools that do not render SVG.

## Files and intended placement

| File | README use | Content |
|---|---|---|
| `helpmora-hero.svg` | README top banner | Brand statement, scope counts, core design principle. |
| `helpmora-scope.svg` | Section 3 — Scope and inventory | 40 program entries, 26 transitions, 51 localization dictionaries listed, five support areas and appropriate caveat. |
| `helpmora-architecture.svg` | Section 4.1 — System overview | Input channels, cmguard, crisis branch, Qdrant, Lyzr, Jac, verification and guided delivery. |
| `helpmora-voice-sequence.svg` | Section 4.3 — Voice-to-response sequence | Omi event path, quick acknowledgement, memory retrieval, agent orchestration, Jac result and UI trace. |
| `helpmora-agent-boundary.svg` | Section 4.4 — Agent orchestration | Lyzr Manager, specialist roles, tool boundary, Jac policy authority. |
| `helpmora-graph-model.svg` | Section 5 — Jac graph model | Documented graph nodes and relationships. |
| `helpmora-walkers.svg` | Section 6 — Jac walkers | Documented walker/support module inventory grouped by responsibility. |
| `helpmora-security-privacy.svg` | Section 11 — Security and privacy | Trust boundary, validation, memory scoping, user-control safeguards. |
| `helpmora-runtime.svg` | Section 14 — Local development | Local laptop + tunnel path and deployed mode. |
| `helpmora-demo-flow.svg` | Section 17 — Demo scenario | Case demo steps, evidence to show judges, anti-fabrication guardrails. |

## How to use

1. Copy the whole `assets/` folder next to the README file.
2. The relative links should match the README: `assets/<filename>.svg`.
3. Use SVG for GitHub README rendering; use PNG exports when a tool requires raster images.
4. These are architecture/documentation illustrations, not proof that every integration is live. Verify implementation and service status before making live-operation claims.

## Accuracy notes

- “51” is labelled as localization dictionaries listed in the documented inventory, not a guarantee of fully validated spoken language support.
- Qdrant and Lyzr stages are labelled as conditional where the README says “when enabled/configured.”
- Browser microphone is labelled as optional and explicitly not equivalent to an Omi event.
- Eligibility authority remains with HELPmora's deterministic Jac policy logic.
- The images do not claim the example case is eligible or that any service has been live-tested.
