# CRM — Relationship Intelligence Runtime (v1.0)

The executable half of CRM: a read-only report generator over
`06-CRM/company-intelligence.json`, enriched with real opportunity,
proposal, and pipeline history from Demand Intelligence, Sales Director
and Revenue Hunter. Never writes to the relationship record itself —
see `crm-runtime-notes.md`'s "The One Rule."

`06-CRM/` remains the specification and the relationship record itself
— `company-intelligence.json`, owned field-by-field exactly as its own
`README.md` already documents. This folder only reports on it.

## Files

- `crm-runtime-notes.md` — the one rule (never writes the relationship
  record), exactly which source answers which question, and what's
  genuinely new here versus reused from Executive Dashboard
- `runtime/` — the reports, generated as code

## How It Fits AOS

- **Reads from:** `06-CRM/company-intelligence.json`,
  `demand-intelligence/opportunity-schema.json`,
  `sales-director/runtime/processed-index.json`,
  `08-Revenue-Hunter/pipeline.json` — all read-only
- **Writes to:** `runtime/output/`, `runtime/logs/` only
- **Generates:** a daily follow-up queue (the same due/overdue logic
  Executive Dashboard already runs), a relationship health report
  (opportunity/proposal/pipeline history per company — genuinely new),
  and stale-relationship alerts (`cold` records past the monthly
  review window — a real gap nothing else in AOS covers)

## What This Is Not

Not an outreach tool. Nothing here drafts or sends a message — that
stays Sales Director's job. Not a second follow-up-priority model —
the due/overdue logic is reused verbatim from
`executive-dashboard/runtime/generate.py`, not redecided.

Start with `crm-runtime-notes.md`, then
`04-Sales-Director/follow-up-priority-model.md`.
