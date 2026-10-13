# Integration Verification Checklist

Use this record before publishing a live demo. Fill the status with actual outcomes from the current build. Do not mark a check as passed merely because code or credentials exist.

## Status vocabulary

- `NOT_RUN` — not tested yet.
- `PASS` — test executed and evidence reviewed.
- `FAIL` — test executed and failed.
- `BLOCKED` — cannot run because credentials, network, service access, or setup is missing.
- `NOT_APPLICABLE` — genuinely not used by this build, with reason noted.

## Core application

| Test | Status | Evidence / notes |
|---|---|---|
| Existing app starts with documented command | NOT_RUN | |
| Existing text input works | NOT_RUN | |
| Existing deterministic eligibility path works | NOT_RUN | |
| Pathfinder uses configured graph transitions | NOT_RUN | |
| Crisis route remains deterministic | NOT_RUN | |
| Accessibility controls remain functional | NOT_RUN | |

## Omi

| Test | Status | Evidence / notes |
|---|---|---|
| Correct Omi capability configured | NOT_RUN | |
| Real transcript event reaches backend | NOT_RUN | |
| Authentication / callback protection validated | NOT_RUN | |
| Actual payload schema parsed | NOT_RUN | |
| Duplicate event does not duplicate a turn | NOT_RUN | |
| User/session association is validated | NOT_RUN | |
| Webhook acknowledges promptly after safe acceptance | NOT_RUN | |

## Qdrant

| Test | Status | Evidence / notes |
|---|---|---|
| Client connects to configured Qdrant mode | NOT_RUN | |
| Collection config matches embedding model | NOT_RUN | |
| Synthetic case memory write succeeds | NOT_RUN | |
| Retrieval works after transient state is cleared | NOT_RUN | |
| User isolation test passes | NOT_RUN | |
| Forget/delete removes the intended memory | NOT_RUN | |

## Lyzr and Jac boundary

| Test | Status | Evidence / notes |
|---|---|---|
| Real Lyzr Manager/agent call succeeds | NOT_RUN | |
| Specialist routing is visible in trace | NOT_RUN | |
| Structured response is schema-validated | NOT_RUN | |
| Existing Jac tool is invoked | NOT_RUN | |
| LLM cannot override deterministic eligibility result | NOT_RUN | |
| Missing/failed Lyzr does not create fake success state | NOT_RUN | |

## Response, approval and security

| Test | Status | Evidence / notes |
|---|---|---|
| Real response reaches the UI | NOT_RUN | |
| Browser TTS works where enabled | NOT_RUN | |
| Approval gate prevents unapproved side effects | NOT_RUN | |
| Qdrant/Lyzr/Omi failure states are clear | NOT_RUN | |
| `.env` is not tracked | NOT_RUN | |
| No secrets in tracked files, logs or demo capture | NOT_RUN | |
| README instructions work from a fresh checkout | NOT_RUN | |

Record test date, code revision and non-sensitive run ID if useful. Do not include real API keys, private webhook URLs with tokens, raw sensitive transcripts or personal identifiers.
