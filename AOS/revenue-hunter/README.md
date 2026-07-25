# Revenue Hunter — Financial Intelligence Runtime (v1.0)

The executable half of Revenue Hunter: runs `lead-scoring.md`,
`decision-tree.md`, and `revenue-forecasting-engine.md` — three
existing, fully-specified models that had never run as code — against
real pipeline, opportunity, CRM, Sales Director, and Product Manager
data, and produces a real revenue dashboard and forecast. No financial
assumption is ever fabricated; see `revenue-hunter-runtime-notes.md`.

`08-Revenue-Hunter/` remains the specification — mission, the nine
revenue types, `lead-scoring.md`, `decision-tree.md`,
`revenue-forecasting-engine.md`, `pipeline.json` — and keeps running
exactly as documented there. This folder is the newer, narrower half
of the same employee.

## Files

- `revenue-hunter-runtime-notes.md` — exactly which source answers
  which question, what's reused versus new, and the one rule
  ("no financial assumption may be fabricated") everything else follows
- `runtime/` — the three models, running as code

## How It Fits AOS

- **Reads from:** `demand-intelligence/opportunity-schema.json`,
  `06-CRM/company-intelligence.json`,
  `sales-director/runtime/processed-index.json`,
  `03-Product-Manager/product-backlog.json` and
  `shipped-products-log.json` — all read-only
- **Writes to:** `08-Revenue-Hunter/pipeline.json` (new items this
  runtime adds per `daily-workflow.md`, and `stage` advances for items
  Sales Director has prepared — the same file Demand Intelligence's
  `ingest.py` already writes to), `runtime/output/`, `runtime/logs/`
- **Feeds:** `09-CEO-Advisor`, which already reads `pipeline.json`
  directly (`decision-model.md`'s pre-existing 0-100 → divide-by-10
  row) — no new feed file, this build makes that existing integration
  real

## What This Is Not

Not a deal-closing engine. Every stage change reflects something that
already happened elsewhere in AOS (a proposal Sales Director prepared);
nothing here simulates or fabricates an outcome.

Start with `revenue-hunter-runtime-notes.md`, then
`08-Revenue-Hunter/revenue-forecasting-engine.md`.
