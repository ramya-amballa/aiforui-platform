# Website Intake Runtime (v1.0)

AI for U&I's website — Contact/"Start a Conversation," and the ADGL,
OPERA/Methodology and Selected Engagement Areas pages that link
through to it — as a first-class Opportunity Hunter source. Every
enquiry becomes a Lead ID, a real opportunity record, a CRM record, a
Revenue Hunter pipeline entry, a Service Mapping recommendation, and a
CEO Advisor notification, automatically. No email is ever sent from
this runtime.

Introduced in AOS Sprint 4, after Service Mapping was already live.
This runtime hands off to Opportunity Hunter, Revenue Hunter, the
Service Mapping Engine, and CRM's own established writers — it does
not re-implement any of them.

## Files

- `website-intake-model.md` — the full model: how a submission
  reaches this runtime, Lead ID generation, Lead Classification,
  Qualification, why the Relevance Engine is deliberately bypassed for
  website-sourced records (and why that's safe), the Sales Package,
  and an explicit assumptions-vs-verified-behaviour section
- `leads.json` — the persisted lead record, one entry per lead, schema
  documented in the file itself
- `runtime/generate.py` — the engine
- `runtime/config/website-intake-config.json` — every lookup table
  (classification keywords, qualification heuristics, discovery call
  agenda, follow-up tasks) — edit to retune, no code change needed
- `runtime/tests/test_website_intake.py` — unit tests for every rule
  branch

## How It Fits AOS

- **Reads from:** raw submission files in `runtime/inbox/` (written by
  the website's `/api/contact` route — see `website-intake-model.md`)
- **Invokes** (as its own subprocess, never imported, exactly how the
  Orchestrator itself invokes every employee): `opportunity-hunter/
  runtime/ingest.py`, `revenue-hunter/runtime/generate.py`,
  `service-mapping/runtime/generate.py` — none of their scoring,
  forecasting or mapping logic is duplicated here
- **Writes to:** `opportunity-hunter/runtime/inbox/` (a new record for
  ingest.py to process), `06-CRM/company-intelligence.json` (only when
  a record doesn't already exist for the organisation — see the model
  doc's "Guaranteeing a CRM Record"), `leads.json`, `runtime/output/`,
  `runtime/logs/`
- **One change to `opportunity-hunter/runtime/ingest.py`**: records
  with `source == "Website"` are exempted from relevance scoring — see
  the model doc for exactly why, and why every other source is
  unaffected

## What This Is Not

Not a second scoring or classification engine — every real decision
(relevance, priority score, classification, routing, revenue
forecasting, service recommendation) is made by the existing script
it's handed to. Not an email sender — nothing here drafts or sends
anything to a prospect; the founder's own internal notification is the
website's pre-existing, unrelated Resend call. Not a redesign of CRM,
Revenue Hunter, or the Service Mapping Engine — all three are invoked
exactly as already built.

Start with `website-intake-model.md`.
