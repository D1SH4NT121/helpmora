# HELPmora Hackathon Submission Checklist

Primary track recommendation: **Accessibility & Adaptive Assistants**.

The provided hackathon guide asks for the following:

- [ ] Project name: HELPmora.
- [ ] Project title.
- [ ] Primary build track named in README.
- [ ] Public GitHub repository with a clean structure and architecture diagram.
- [ ] Deployed demo URL that works for another person.
- [ ] Demo video no longer than five minutes.
- [ ] Omi usage explained and shown in a real run.
- [ ] Qdrant usage explained and shown through retrieval/persistence.
- [ ] Lyzr usage explained and shown through actual agent execution.
- [ ] Project description describing the problem, solution, and differentiator.
- [ ] `.env` and all secrets kept out of Git.
- [ ] Final tests and submission links checked.
- [ ] Jurisdiction consistency audit completed: no stray U.S./HUD/FPL/Houston/USD examples in an India-only demo unless those are deliberately supported and clearly separated.

## Suggested title

**HELPmora: Voice-to-Action Welfare Navigation with Memory-Backed Agents and Explainable Decisions**

## Suggested short description

HELPmora is a voice-first civic welfare and free legal-aid navigator for India. It structures a citizen's story into a case, uses Qdrant for consent-controlled semantic memory, and uses Lyzr to coordinate specialist workflow tasks. The existing Jac graph/policy engine remains authoritative for deterministic eligibility and curated alternative-path discovery. HELPmora guides the user through understandable next steps and preserves human approval for consequential actions.

Edit this description to reflect only the features demonstrated by the submitted build.

## Demo proof expected

1. Real Omi-originated input arrives.
2. Qdrant retrieves or writes real memory.
3. Lyzr runs a real agent/Manager path.
4. Existing Jac logic is invoked.
5. The user receives an explainable result/action.

A UI label or mocked test is not sufficient proof of a live integration.
