# Product Manager Runtime — Sources and Non-Duplication Notes

`runtime/generate.py` executes `03-Product-Manager/product-evaluation-framework.md`
against four real, already-existing signal sources. This file documents
which source answers which question, so it's clear that no other
employee's decision is ever second-guessed — only the framework's own
Step 3/4 scoring, which nothing else in AOS has ever executed before
this runtime existed.

## Sources Consumed (Read-Only, Except One Update-In-Place)

| Source | What's read | Why this isn't duplicated logic |
|---|---|---|
| `03-Product-Manager/product-backlog.json` entries with `score: null` | Candidates Market Intelligence already wrote (`signalSource: "Market Intelligence"`) | Market Intelligence deliberately left `proposedFormat`/`score` null, saying evaluation was this runtime's job — this is the hand-off completing, not a second decision |
| `opportunity-hunter/opportunity-schema.json`, filtered to `classification == "Convert into Product Idea"` | Opportunity Hunter's own decision tree, triggered when `recurrencePattern: "product"` was set at ingestion | The classification is already made; the runtime consumes the label, exactly as Content Director consumes `Convert into Content` |
| `sales-director/runtime/processed-index.json` | Every opportunity Sales Director has prepared a package for, cross-referenced against `opportunity-schema.json` for `domainTags` | A **count**, not a judgement: if 2+ real prepared packages share a domain tag, that's a real recurring pattern, not an invented one. Sales Director's own `Ready To Send`/`Proposal Ready`/`Needs Review` status is never read or re-interpreted here |
| `content-director/runtime/queue/content-queue.json` | Every queued content signal, as an additional raw candidate for Product Manager's own (different) evaluation | Content Director's content score answers "is this worth a draft"; Product Manager's four dimensions answer an entirely different question ("is this worth a product") — applying a second, different model to a shared real signal is normal cross-functional evaluation, not duplication |
| Website analytics | Not consumed — no analytics pipeline exists in AOS yet | Per the founder's own instruction: "Website analytics (when available)." Recorded here so a future build knows this is a real gap, not an oversight |

## Deduplication

- Market-Intelligence-sourced backlog entries are updated in place
  (the only write this runtime makes outside its own folder — filling
  in a field their own schema already reserved for it, not adding a
  new one).
- Opportunity, Sales-Director-pattern, and Content-Director-sourced
  candidates are tracked in `runtime/queue/processed-index.json`, this
  runtime's own file, so the same signal is never evaluated twice.

## A Known Limitation From the Fixed Execution Order

The Orchestrator's nine-step sequence runs Product Manager (step 6)
before Content Director (step 7). That means on any given day, Product
Manager sees Content Director's queue exactly as it stood at the start
of the run — anything Content Director queues later that same run
isn't picked up until the next day's run. This is a real, honest
consequence of the fixed order the founder specified, not a bug; it
self-corrects within one cycle, and it isn't the Orchestrator's or this
runtime's place to reorder the sequence to avoid it.

## What This Runtime Does Not Do

- Does not re-score an opportunity, re-classify a Market Intelligence
  development, or re-evaluate a Content Director draft's worth
  publishing.
- Does not build, launch, or ship a product. Every output is a
  `candidate`/`in-development`/`parked` row in `product-backlog.json`
  for the founder to act on by hand.
- Does not invent a demand count, a revenue figure, or a differentiation
  claim that isn't backed by a real record somewhere else in AOS.
