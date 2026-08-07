# Drafts (non-canonical)

Everything in this directory is **draft content**, not canonical knowledge. Nothing here is loaded by the validator in `/validators`, referenced by relationships in `/data`, or safe to treat as a fact until it has been promoted.

A draft is a candidate `Incident` captured from a source (news article, court judgment, etc.) via `/ingestion/schemas/draft-incident.schema.json`. It carries a `human_review` block that starts at `"status": "pending"`.

- `draft-incident-air-canada-chatbot-refund-2024.json` is an example draft, left `pending` on purpose, so this directory always shows what an unreviewed draft looks like.
- `promoted/` holds drafts that have already been promoted into `/data/incidents` — moved here by `ingest:promote` rather than deleted, so the canonical record stays traceable back to the exact draft and review decision that produced it.

See [`/docs/ingestion-pipeline.md`](../../docs/ingestion-pipeline.md) for the full workflow.
