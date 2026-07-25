# AOS Orchestrator — Dependency Map

What actually depends on what, and — separately — what has an
executable implementation today versus what is still a documented
process waiting on one. These are two different questions. The
execution order in `execution-plan.md` is fixed by the founder's
instruction; this file is what justifies that order in terms of real
data flow, and what the Orchestrator actually checks before running
each step.

## The Graph

```
Market Intelligence (runtime/monitor.py)
      |
      +--> Product Manager (product-backlog.json, unscored candidates)
      +--> Content Director (content-brief-queue.json, consumed by
      |    content-director/runtime/generate.py)
      +--> opportunity-hunter/runtime/inbox/ (a normal inbox record,
      |    scored by Opportunity Hunter's own unmodified pipeline —
      |    not a formal dependsOn edge, see below)
      |
Opportunity Hunter (self-contained: collects, filters, scores, routes)
      |
      +--> Revenue Hunter (pipeline.json, written by Opportunity Hunter)
      +--> CRM (company-intelligence.json, written by Opportunity Hunter)
              |
              v
        Sales Director (reads all three above)
              |
              v
        CEO Advisor (reads Sales Director's feed + Market
                     Intelligence's feed + all upstream)
              |
              v
        Daily Brief (reads everything upstream, last)
```

Market Intelligence has no formal `dependsOn` edge into Opportunity
Hunter's branch, even though it can now write a real inbox record
there: the fixed execution order already runs Market Intelligence
first, so anything it writes is sitting in
`opportunity-hunter/runtime/inbox/` before Opportunity Hunter's step
starts. Making it a hard dependency would mean an unrelated Market
Intelligence failure could block Opportunity Hunter's own, entirely
self-contained collection — the opposite of "continue where possible."
Opportunity Hunter runs regardless of whether Market Intelligence
produced anything this run.

## Dependency Table (what the Orchestrator enforces)

| # | Employee | `dependsOn` | Why |
|---|---|---|---|
| 1 | Market Intelligence | — | No upstream dependency; earliest signal source |
| 2 | Opportunity Hunter | — | Self-contained: collects from its own sources, runs its own relevance filter and scoring |
| 3 | Revenue Hunter | Opportunity Hunter | `pipeline.json` is written by Opportunity Hunter's `ingest.py` (`route_to_revenue_hunter`) for `Immediate Proposal`/`Partnership` classifications; `revenue-hunter/runtime/generate.py` admits the `Active`/`Priority` opportunities that classification never routes there, applying `lead-scoring.md`'s own weights |
| 4 | CRM | Opportunity Hunter | `company-intelligence.json` is written by the same `ingest.py` (`route_to_crm`) for `Follow Recruiter`/`Relationship Building`/`Partnership`/`Immediate Proposal` |
| 5 | Sales Director | Opportunity Hunter, Revenue Hunter, CRM | `prepare.py` reads all three to build every proposal package |
| 6 | Product Manager | Market Intelligence | `generate.py` evaluates Market Intelligence's own unscored backlog candidates, plus Opportunity Hunter's `Convert into Product Idea` opportunities, a real recurring-domain-tag count from Sales Director's prepared proposals, and Content Director's queued signals, all read-only except filling in the score Market Intelligence's own schema reserved for it |
| 7 | Content Director | Market Intelligence | `generate.py` reads Market Intelligence's `content-brief-queue.json` as its primary input, plus Opportunity Hunter's `Convert into Content` opportunities, Product Manager's shipped products, and CEO Advisor's daily priority, all read-only |
| 8 | CEO Advisor | Sales Director, Revenue Hunter, Opportunity Hunter, CRM | Its decision model (`decision-model.md`) normalises a candidate from each of these |
| 9 | Daily Brief | Opportunity Hunter, Revenue Hunter, CRM, Sales Director, CEO Advisor | Aggregates every upstream output into one report, last |

A step only runs once every entry in its `dependsOn` has finished with
status `SUCCESS` or `NOT_EXECUTABLE` (see below — a documented-only
employee isn't a failure, it's a no-op). If any dependency is `FAILED`
(exhausted its retries) or itself `SKIPPED_DEPENDENCY_FAILED`, the
dependent step is marked `SKIPPED_DEPENDENCY_FAILED` and never runs —
this is the cascade that makes the graph real rather than decorative.

## What Actually Has a Runtime Today

Seven of the nine employees have code the Orchestrator can invoke; two
do not yet, and are recorded honestly as `NOT_EXECUTABLE` rather than
simulated:

| Employee | Runtime | Status |
|---|---|---|
| Market Intelligence | `05-Market-Intelligence/runtime/monitor.py` | executable — checks every configured source, classifies every new development against six deterministic checks, and routes structured records to Content Director, Product Manager, Opportunity Hunter and CEO Advisor; see `market-intelligence-classification-model.md` |
| Opportunity Hunter | `opportunity-hunter/runtime/collect.py` | executable — this single entry point already chains collection → relevance filtering → scoring → routing (`ingest.py`'s `main()`), so invoking it is the entire Opportunity Hunter pipeline, not a partial one |
| Revenue Hunter | `revenue-hunter/runtime/generate.py` | executable — `08-Revenue-Hunter/` is where `lead-scoring.md`, `decision-tree.md` and `revenue-forecasting-engine.md` live; `revenue-hunter/` is where they run, the same split as Sales Director, Product Manager and Content Director; see `revenue-hunter/revenue-hunter-runtime-notes.md` |
| CRM | none of its own | `NOT_EXECUTABLE` — same reasoning, `06-CRM/company-intelligence.json` is written by Opportunity Hunter |
| Sales Director | `sales-director/runtime/prepare.py` | executable |
| Product Manager | `product-manager/runtime/generate.py` | executable — `03-Product-Manager/` is where the specification and `product-evaluation-framework.md` live; `product-manager/` is where it runs, the same split as Sales Director and Content Director; see `product-manager/product-manager-runtime-notes.md` |
| Content Director | `content-director/runtime/generate.py` | executable — `02-Content-Director/` is where Content Director's specification lives; `content-director/` is where it runs, exactly the same split as `04-Sales-Director`/`sales-director`; see `content-director/content-generation-model.md` |
| CEO Advisor | none of its own | `NOT_EXECUTABLE` — `decision-model.md` has no dedicated script; it is already executed as one section of Daily Brief's own generator (see below), exactly as `09-CEO-Advisor/operating-manual.md` describes ("Pass it to `07-Daily-Brief` as the lead item") |
| Daily Brief | `executive-dashboard/runtime/generate.py` | executable — `executive-dashboard/` is where Daily Brief's aggregation role and CEO Advisor's decision model both already live as code; see its own module docstring, which documents this explicitly |

Treating an employee as `NOT_EXECUTABLE` is not a failure and does not
retry. It is the Orchestrator being honest that no runtime exists yet,
rather than fabricating a step that would duplicate business logic
that hasn't been built. When one of these employees gets a real
`runtime/` script in a future build, only `runtime/config/orchestrator-config.json`
needs a `script` path added — no change to `orchestrator.py` itself.
