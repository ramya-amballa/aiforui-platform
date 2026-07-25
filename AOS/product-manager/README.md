# Product Manager — Evaluation Runtime (v1.0)

The executable half of Product Manager: runs
`03-Product-Manager/product-evaluation-framework.md` — the existing,
already-specified four-dimension scoring model — against real signals
from Market Intelligence, Demand Intelligence, Sales Director and
Content Director, and decides `candidate` / `in-development` / `parked`
for each. Nothing here is a new framework; it's the existing one,
executed for the first time.

`03-Product-Manager/` remains the specification — mission, the format
list, `product-evaluation-framework.md`, `product-backlog.json`,
`shipped-products-log.json` — and keeps running exactly as documented
there. This folder is the newer, narrower half of the same employee.

## Files

- `product-manager-runtime-notes.md` — exactly which source answers
  which question, and why none of it is duplicated logic
- `runtime/` — the framework, running as code

## How It Fits AOS

- **Reads from:** `product-backlog.json` (its own unscored entries),
  `demand-intelligence/opportunity-schema.json`,
  `sales-director/runtime/processed-index.json`,
  `content-director/runtime/queue/content-queue.json`,
  `sales-director/runtime/config/practitioner-bank.json` — all
  read-only except one field Market Intelligence's own schema already
  reserved for this runtime to fill in
- **Writes to:** `03-Product-Manager/product-backlog.json` (evaluated
  entries only — never `shipped-products-log.json`, which stays a
  human decision), `runtime/queue/`, `runtime/output/`, `runtime/logs/`
- **Feeds:** `09-CEO-Advisor`, via the backlog's own existing
  `score`/`status` fields — already CEO Advisor's normalisation input
  per `decision-model.md`, unchanged by this build

## What This Is Not

Not a product-launch pipeline. Every evaluated candidate is a row in
`product-backlog.json` — the founder decides what actually gets built.

Start with `product-manager-runtime-notes.md`, then
`03-Product-Manager/product-evaluation-framework.md`'s "Runtime
Execution Notes" section.
