# Security Policy

**Project:** HELPmora  
**Repository:** [https://github.com/D1SH4NT121/helpmora](https://github.com/D1SH4NT121/helpmora)

HELPmora is designed for individuals in vulnerable situations: survivors of domestic violence, unhoused persons, and families in acute need. A security vulnerability or privacy leak could directly compromise someone's safety. Security reports are handled with high priority.

---

## Reporting a Vulnerability

Please **do not open a public issue** for suspected security or privacy vulnerabilities.

- Open a private security advisory report via the repository's **Security** tab: [https://github.com/D1SH4NT121/helpmora/security/advisories/new](https://github.com/D1SH4NT121/helpmora/security/advisories/new).
- Or email the maintainer directly at: `mohapatradishant@gmail.com` with the subject line `[HELPmora Security Advisory]`.

Please include:
1. Detailed description of the vulnerability and reproduction steps.
2. Affected endpoints, walkers, or components.
3. Potential impact on user privacy or system integrity.

Reports will be acknowledged promptly, followed by a status update and patch timeline.

---

## Built-In Security Architecture (`cmguard`)

- **Reverse Gateway Defense:** All requests pass through `cmguard/gateway.py` with strict HTTP route allowlists, JSON payload size caps, and per-IP / per-session rate limits.
- **Signed Tokens:** Session tokens are cryptographically signed using a strong random secret (`HELPMORA_JWT_SECRET`).
- **No PII Retention:** Raw conversational transcripts and personally identifiable data are scrubbed and excluded from server log outputs.
- **Deterministic Crisis Routing:** Emergency escalation paths are locked in deterministic Python/Jac code and cannot be bypassed or modified by user prompt injections.
- **Budget Circuit Breakers:** Model invocation budgets are strictly throttled by `cmguard/budget.py` to prevent denial-of-wallet or resource exhaustion attacks.
