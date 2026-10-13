# HELPmora Security and Privacy Notes

This is an engineering checklist, not a claim of formal security certification. Verify these controls against the actual source and deployed configuration.

## Sensitive data

Treat transcripts, household information, income, location, medical-cost concerns, domestic-safety information and legal-aid requests as sensitive. Collect only what the workflow needs. Avoid saving raw audio by default and avoid putting full transcripts in application logs or telemetry.

## Secrets

- Store credentials in root `.env` for local work or a deployment secrets manager in production.
- Keep `.env` out of Git and retain only placeholders in `.env.example`.
- Never place keys in browser code, SVG assets, screenshots, issue descriptions or the README.
- Redact keys and token-bearing URLs from exception logs.
- Rotate any credential that is accidentally exposed.

## Identity and tenant isolation

- Bind the user and session identity to a validated application session or integration mapping.
- Do not authorize access based only on a `user_id` sent by an untrusted request body.
- Add a tenant filter to every Qdrant retrieve/delete path.
- Confirm that cross-user retrieval is denied by automated tests.

## Omi webhook

- Follow the actual Omi capability's documented auth/signature behavior.
- Validate request size, content type, schema and event identity.
- Deduplicate deliveries and protect against replay where the event protocol supports it.
- Accept the event safely and acknowledge quickly; perform slow processing asynchronously.
- Expose only the intended webhook route through the public gateway.

## External processing

Explain which data is sent to Omi, Lyzr, Qdrant Cloud or an optional transcription/model provider. Do not describe the full workflow as local-only if any of these services process the data remotely.

## Memory controls

- Respect memory-disabled settings.
- Store case summaries/confirmed facts instead of every raw transcript by default.
- Provide a user-controlled delete/forget path if memory persistence is enabled.
- Verify deletion across all supported stores, including graph state and Qdrant.

## Crisis behavior

Urgent crisis signals must use the project's deterministic escalation behavior. Keep contact details and official destinations current. Never allow an LLM to invent emergency numbers or imply that HELPmora itself is a crisis-response agency.
