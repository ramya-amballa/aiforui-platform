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
Website Intake Runtime (self-contained: assigns a Lead ID, invokes
      ingest.py/revenue-hunter's/service-mapping's own generate.py as
      subprocesses within its own run — not a dependsOn edge on any
      of them, since it doesn't wait for their separately scheduled
      steps below; it runs its own copy of the same handoff early)
      |
      v (opportunity-schema.json/pipeline.json/company-intelligence.json
         already contain today's website leads by the time every step
         below runs)

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
              |
              v
        CRM (company-intelligence.json, written by Opportunity Hunter;
             crm/runtime/generate.py additionally reads
             opportunity-schema.json and pipeline.json, read-only)
              |
              v
        Service Mapping Engine (reads opportunity-schema.json;
             optionally enriches from pipeline.json and
             company-intelligence.json, all read-only — see
             service-mapping/service-mapping-model.md)
              |
              v
        Sales Director (reads Opportunity Hunter, Revenue Hunter, CRM,
                        and Service Mapping Engine's recommendations)
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
| 2 | Website Intake Runtime | — | Self-contained: assigns a Lead ID, then invokes `opportunity-hunter/runtime/ingest.py`, `revenue-hunter/runtime/generate.py` and `service-mapping/runtime/generate.py` as its own subprocesses within its own run (all three are idempotent, so this is safe alongside their own separately scheduled steps below) — it doesn't wait on their steps below, it runs its own copy of the same handoff early so every step below already sees today's website leads |
| 3 | Opportunity Hunter | — | Self-contained: collects from its own sources, runs its own relevance filter and scoring |
| 4 | Revenue Hunter | Opportunity Hunter | `pipeline.json` is written by Opportunity Hunter's `ingest.py` (`route_to_revenue_hunter`) for `Immediate Proposal`/`Partnership` classifications; `revenue-hunter/runtime/generate.py` admits the `Active`/`Priority` opportunities that classification never routes there, applying `lead-scoring.md`'s own weights |
| 5 | CRM | Opportunity Hunter, Revenue Hunter | `company-intelligence.json` itself is written by `ingest.py` (`route_to_crm`) for `Follow Recruiter`/`Relationship Building`/`Partnership`/`Immediate Proposal`; `crm/runtime/generate.py` additionally cross-references `opportunity-hunter/opportunity-schema.json` and `08-Revenue-Hunter/pipeline.json` (both read-only, both already written earlier in the fixed order) to build real opportunity/pipeline history per company. It also reads `sales-director/runtime/processed-index.json` for proposal history, but Sales Director runs *after* CRM (step 7), so that read is one cycle behind, like Revenue Hunter's own read of Sales Director's state — not a `dependsOn` edge, since a step can't depend on one that hasn't run yet |
| 6 | Service Mapping Engine | Opportunity Hunter | `generate.py` reads `opportunity-schema.json` for every field its decision tables use (`domainTags`, `classification`, `scopedEngagement`, `sourceCategory`, `scores`, `title`/`description`); `pipeline.json` and `company-intelligence.json` are read too but only as optional enrichment (a real revenue figure or an active-client relationship overrides a heuristic default) — their absence never blocks a recommendation, so they aren't `dependsOn` edges |
| 7 | Sales Director | Opportunity Hunter, Revenue Hunter, CRM, Service Mapping Engine | `prepare.py` reads all four — the first three to build every proposal package as before, plus Service Mapping Engine's recommendation to surface the recommended template/engagement type/size/cross-sell in an additive section of each package |
| 8 | Product Manager | Market Intelligence | `generate.py` evaluates Market Intelligence's own unscored backlog candidates, plus Opportunity Hunter's `Convert into Product Idea` opportunities, a real recurring-domain-tag count from Sales Director's prepared proposals, and Content Director's queued signals, all read-only except filling in the score Market Intelligence's own schema reserved for it |
| 9 | Content Director | Market Intelligence | `generate.py` reads Market Intelligence's `content-brief-queue.json` as its primary input, plus Opportunity Hunter's `Convert into Content` opportunities, Product Manager's shipped products, and CEO Advisor's daily priority, all read-only |
| 10 | CEO Advisor | Sales Director, Revenue Hunter, Opportunity Hunter, CRM | Its decision model (`decision-model.md`) normalises a candidate from each of these, plus Website Intake Runtime's own feed (see below) |
| 11 | Daily Brief | Opportunity Hunter, Revenue Hunter, CRM, Sales Director, CEO Advisor | Aggregates every upstream output into one report, last |

A step only runs once every entry in its `dependsOn` has finished with
status `SUCCESS` or `NOT_EXECUTABLE` (see below — a documented-only
employee isn't a failure, it's a no-op). If any dependency is `FAILED`
(exhausted its retries) or itself `SKIPPED_DEPENDENCY_FAILED`, the
dependent step is marked `SKIPPED_DEPENDENCY_FAILED` and never runs —
this is the cascade that makes the graph real rather than decorative.

## What Actually Has a Runtime Today

Ten of the eleven employees have code the Orchestrator can invoke; one
does not yet, and is recorded honestly as `NOT_EXECUTABLE` rather than
simulated:

| Employee | Runtime | Status |
|---|---|---|
| Market Intelligence | `05-Market-Intelligence/runtime/monitor.py` | executable — checks every configured source, classifies every new development against six deterministic checks, and routes structured records to Content Director, Product Manager, Opportunity Hunter and CEO Advisor; see `market-intelligence-classification-model.md` |
| Website Intake Runtime | `website-intake/runtime/generate.py` | executable — new in Sprint 4, no prior spec folder to split from (like Service Mapping Engine); spec and runtime both live under `website-intake/`; see `website-intake/website-intake-model.md` |
| Opportunity Hunter | `opportunity-hunter/runtime/collect.py` | executable — this single entry point already chains collection → relevance filtering → scoring → routing (`ingest.py`'s `main()`), so invoking it is the entire Opportunity Hunter pipeline, not a partial one |
| Revenue Hunter | `revenue-hunter/runtime/generate.py` | executable — `08-Revenue-Hunter/` is where `lead-scoring.md`, `decision-tree.md` and `revenue-forecasting-engine.md` live; `revenue-hunter/` is where they run, the same split as Sales Director, Product Manager and Content Director; see `revenue-hunter/revenue-hunter-runtime-notes.md` |
| CRM | `crm/runtime/generate.py` | executable — `06-CRM/` is where the specification and `company-intelligence.json` (the relationship record itself) live; `crm/` is where the read-only report generator runs, the same split as Sales Director, Product Manager, Content Director and Revenue Hunter; see `crm/crm-runtime-notes.md` |
| Service Mapping Engine | `service-mapping/runtime/generate.py` | executable — new in Sprint 3, no prior spec folder to split from (unlike the founder's original nine employees); spec and runtime both live under `service-mapping/`; see `service-mapping/service-mapping-model.md` |
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
