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
Market Intelligence
      |
      +--> Product Manager
      +--> Content Director
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
        CEO Advisor (reads Sales Director's feed + all upstream)
              |
              v
        Daily Brief (reads everything upstream, last)
```

Market Intelligence has no downstream dependency on Opportunity
Hunter's branch today, and vice versa — they are parallel in principle.
The fixed execution order in `execution-plan.md` runs Market
Intelligence first anyway, since it is intended to be the earliest
signal source once it has a runtime; this costs nothing today because
neither branch currently blocks on the other except where marked below.

## Dependency Table (what the Orchestrator enforces)

| # | Employee | `dependsOn` | Why |
|---|---|---|---|
| 1 | Market Intelligence | — | No upstream dependency; earliest signal source |
| 2 | Opportunity Hunter | — | Self-contained: collects from its own sources, runs its own relevance filter and scoring |
| 3 | Revenue Hunter | Opportunity Hunter | `pipeline.json` is written by Opportunity Hunter's `ingest.py` (`route_to_revenue_hunter`) for `Immediate Proposal`/`Partnership` classifications |
| 4 | CRM | Opportunity Hunter | `company-intelligence.json` is written by the same `ingest.py` (`route_to_crm`) for `Follow Recruiter`/`Relationship Building`/`Partnership`/`Immediate Proposal` |
| 5 | Sales Director | Opportunity Hunter, Revenue Hunter, CRM | `prepare.py` reads all three to build every proposal package |
| 6 | Product Manager | Market Intelligence | Product signals originate from tracked regulatory/market developments |
| 7 | Content Director | Market Intelligence | Content signals originate from the same tracked developments |
| 8 | CEO Advisor | Sales Director, Revenue Hunter, Opportunity Hunter, CRM | Its decision model (`decision-model.md`) normalises a candidate from each of these |
| 9 | Daily Brief | Opportunity Hunter, Revenue Hunter, CRM, Sales Director, CEO Advisor | Aggregates every upstream output into one report, last |

A step only runs once every entry in its `dependsOn` has finished with
status `SUCCESS` or `NOT_EXECUTABLE` (see below — a documented-only
employee isn't a failure, it's a no-op). If any dependency is `FAILED`
(exhausted its retries) or itself `SKIPPED_DEPENDENCY_FAILED`, the
dependent step is marked `SKIPPED_DEPENDENCY_FAILED` and never runs —
this is the cascade that makes the graph real rather than decorative.

## What Actually Has a Runtime Today

Four of the nine employees have code the Orchestrator can invoke;
five do not yet, and are recorded honestly as `NOT_EXECUTABLE` rather
than simulated:

| Employee | Runtime | Status |
|---|---|---|
| Market Intelligence | none | `NOT_EXECUTABLE` — `05-Market-Intelligence/operating-manual.md` is a manual process |
| Opportunity Hunter | `opportunity-hunter/runtime/collect.py` | executable — this single entry point already chains collection → relevance filtering → scoring → routing (`ingest.py`'s `main()`), so invoking it is the entire Opportunity Hunter pipeline, not a partial one |
| Revenue Hunter | none of its own | `NOT_EXECUTABLE` — its data is a side effect of Opportunity Hunter; there is no `08-Revenue-Hunter/runtime/` to run independently, and the Orchestrator does not invent one |
| CRM | none of its own | `NOT_EXECUTABLE` — same reasoning, `06-CRM/company-intelligence.json` is written by Opportunity Hunter |
| Sales Director | `sales-director/runtime/prepare.py` | executable |
| Product Manager | none | `NOT_EXECUTABLE` |
| Content Director | none | `NOT_EXECUTABLE` |
| CEO Advisor | none of its own | `NOT_EXECUTABLE` — `decision-model.md` has no dedicated script; it is already executed as one section of Daily Brief's own generator (see below), exactly as `09-CEO-Advisor/operating-manual.md` describes ("Pass it to `07-Daily-Brief` as the lead item") |
| Daily Brief | `executive-dashboard/runtime/generate.py` | executable — `executive-dashboard/` is where Daily Brief's aggregation role and CEO Advisor's decision model both already live as code; see its own module docstring, which documents this explicitly |

Treating an employee as `NOT_EXECUTABLE` is not a failure and does not
retry. It is the Orchestrator being honest that no runtime exists yet,
rather than fabricating a step that would duplicate business logic
that hasn't been built. When one of these employees gets a real
`runtime/` script in a future build, only `runtime/config/orchestrator-config.json`
needs a `script` path added — no change to `orchestrator.py` itself.
