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
      +--> demand-intelligence/runtime/inbox/ (a normal inbox record,
      |    scored by Demand Intelligence's own unmodified pipeline —
      |    not a formal dependsOn edge, see below)
      |
Demand Intelligence (self-contained: collects, filters, scores, routes)
      |
      +--> Revenue Hunter (pipeline.json, written by Demand Intelligence)
              |
              v
        CRM (company-intelligence.json, written by Demand Intelligence;
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
        Sales Director (reads Demand Intelligence, Revenue Hunter, CRM,
                        and Service Mapping Engine's recommendations)
              |
              v
        Daily Brief (reads everything upstream)
              |
              v
        CEO Advisor (reads all eight named sources, including Daily
                     Brief's own summary — see below; genuinely the
                     final step, per Sprint 5's explicit instruction)
```

Market Intelligence has no formal `dependsOn` edge into Demand
Intelligence's branch, even though it can now write a real inbox record
there: the fixed execution order already runs Market Intelligence
first, so anything it writes is sitting in
`demand-intelligence/runtime/inbox/` before Demand Intelligence's step
starts. Making it a hard dependency would mean an unrelated Market
Intelligence failure could block Demand Intelligence's own, entirely
self-contained collection — the opposite of "continue where possible."
Demand Intelligence runs regardless of whether Market Intelligence
produced anything this run.

## Dependency Table (what the Orchestrator enforces)

| # | Employee | `dependsOn` | Why |
|---|---|---|---|
| 1 | Market Intelligence | — | No upstream dependency; earliest signal source |
| 2 | Website Intake Runtime | — | Self-contained: assigns a Lead ID, then invokes `demand-intelligence/runtime/ingest.py`, `revenue-hunter/runtime/generate.py` and `service-mapping/runtime/generate.py` as its own subprocesses within its own run (all three are idempotent, so this is safe alongside their own separately scheduled steps below) — it doesn't wait on their steps below, it runs its own copy of the same handoff early so every step below already sees today's website leads |
| 3 | Demand Intelligence | — | Self-contained: collects from its own sources, runs its own relevance filter and scoring |
| 4 | Revenue Hunter | Demand Intelligence | `pipeline.json` is written by Demand Intelligence's `ingest.py` (`route_to_revenue_hunter`) for `Immediate Proposal`/`Partnership` classifications; `revenue-hunter/runtime/generate.py` admits the `Active`/`Priority` opportunities that classification never routes there, applying `lead-scoring.md`'s own weights |
| 5 | CRM | Demand Intelligence, Revenue Hunter | `company-intelligence.json` itself is written by `ingest.py` (`route_to_crm`) for `Follow Recruiter`/`Relationship Building`/`Partnership`/`Immediate Proposal`; `crm/runtime/generate.py` additionally cross-references `demand-intelligence/opportunity-schema.json` and `08-Revenue-Hunter/pipeline.json` (both read-only, both already written earlier in the fixed order) to build real opportunity/pipeline history per company. It also reads `sales-director/runtime/processed-index.json` for proposal history, but Sales Director runs *after* CRM (step 7), so that read is one cycle behind, like Revenue Hunter's own read of Sales Director's state — not a `dependsOn` edge, since a step can't depend on one that hasn't run yet |
| 6 | Service Mapping Engine | Demand Intelligence | `generate.py` reads `opportunity-schema.json` for every field its decision tables use (`domainTags`, `classification`, `scopedEngagement`, `sourceCategory`, `scores`, `title`/`description`); `pipeline.json` and `company-intelligence.json` are read too but only as optional enrichment (a real revenue figure or an active-client relationship overrides a heuristic default) — their absence never blocks a recommendation, so they aren't `dependsOn` edges |
| 7 | Sales Director | Demand Intelligence, Revenue Hunter, CRM, Service Mapping Engine | `prepare.py` reads all four — the first three to build every proposal package as before, plus Service Mapping Engine's recommendation to surface the recommended template/engagement type/size/cross-sell in an additive section of each package |
| 8 | Account Intelligence | Demand Intelligence, CRM, Sales Director | New in Sprint 8. `generate.py` reads `organisation-profiles.json` (required — every qualified organisation) plus `opportunity-schema.json`, `company-intelligence.json` and `output/sales-director/ceo-advisor-feed.json` (all optional, read-only cross-references, same pattern as Service Mapping Engine's own optional enrichment reads); never writes to any of them. Purely additive/downstream — Demand Intelligence's own pipeline is unaffected whether or not this step has ever run |
| 9 | Reverse Job Hunt | Demand Intelligence, CRM, Sales Director, Account Intelligence | New in Sprint 9. `generate.py` reads `organisation-profiles.json` (required) plus `opportunity-schema.json`, `pipeline.json`, `company-intelligence.json` and `account-intelligence-feed.json` (all optional, read-only cross-references); never writes to any of them and never touches any existing scoring formula. Purely additive/downstream, same pattern as Account Intelligence |
| 10 | Recruiter Intelligence | Demand Intelligence, Revenue Hunter, CRM | New in Sprint 10. `generate.py` scans `opportunity-schema.json`'s Recruiter/Consulting Channel entries and `company-intelligence.json`'s recruiter-attributed companies (both read-only) to build `recruiter-profiles.json` and four generated views. Unlike Sprint 8/9, CEO Advisor genuinely *reads* this step's feed (see row 15) |
| 11 | Fractional Advisory Radar | Demand Intelligence, Revenue Hunter | New in Sprint 11. `generate.py` reuses Demand Intelligence's own five signal categories (`organisation-profiles.json`) rather than re-scanning the same public signals with a second taxonomy; classifies stage (Emerging/Growing/Enterprise/Urgent), Fractional Advisory Potential, engagement model, and expected consulting revenue. Purely additive/read-only |
| 12 | Product Manager | Market Intelligence | `generate.py` evaluates Market Intelligence's own unscored backlog candidates, plus Demand Intelligence's `Convert into Product Idea` opportunities, a real recurring-domain-tag count from Sales Director's prepared proposals, and Content Director's queued signals, all read-only except filling in the score Market Intelligence's own schema reserved for it |
| 13 | Content Director | Market Intelligence | `generate.py` reads Market Intelligence's `content-brief-queue.json` as its primary input, plus Demand Intelligence's `Convert into Content` opportunities, Product Manager's shipped products, and CEO Advisor's daily priority, all read-only |
| 14 | Daily Brief | Demand Intelligence, Revenue Hunter, CRM, Sales Director | Aggregates every upstream output into one report. No longer depends on CEO Advisor (see below) |
| 15 | CEO Advisor | Market Intelligence, Website Intake, Demand Intelligence, Revenue Hunter, CRM, Service Mapping Engine, Sales Director, Account Intelligence, Reverse Job Hunt, Recruiter Intelligence, Fractional Advisory Radar, Product Manager, Content Director, Daily Brief | `ceo-advisor/runtime/generate.py` genuinely depends on every other employee, to guarantee it is the final step per Sprint 5's explicit instruction. Reads Sprint 5's eight named sources plus Sprint 10's Recruiter Intelligence feed (genuinely read, for the Recruiter Follow-ups section) — Product Manager, Content Director, Account Intelligence, Reverse Job Hunt and Fractional Advisory Radar remain dependency-only, for ordering, not read |

A step only runs once every entry in its `dependsOn` has finished with
status `SUCCESS` or `NOT_EXECUTABLE` (see below — a documented-only
employee isn't a failure, it's a no-op). If any dependency is `FAILED`
(exhausted its retries) or itself `SKIPPED_DEPENDENCY_FAILED`, the
dependent step is marked `SKIPPED_DEPENDENCY_FAILED` and never runs —
this is the cascade that makes the graph real rather than decorative.

## What Actually Has a Runtime Today

All fifteen employees now have code the Orchestrator can invoke — CEO
Advisor was the last `NOT_EXECUTABLE` one, closed in Sprint 5; Account
Intelligence (Sprint 8), Reverse Job Hunt (Sprint 9), Recruiter
Intelligence (Sprint 10) and Fractional Advisory Radar (Sprint 11) are
all additive from day one:

| Employee | Runtime | Status |
|---|---|---|
| Market Intelligence | `05-Market-Intelligence/runtime/monitor.py` | executable — checks every configured source, classifies every new development against six deterministic checks, and routes structured records to Content Director, Product Manager, Demand Intelligence and CEO Advisor; see `market-intelligence-classification-model.md` |
| Website Intake Runtime | `website-intake/runtime/generate.py` | executable — new in Sprint 4, no prior spec folder to split from (like Service Mapping Engine); spec and runtime both live under `website-intake/`; see `website-intake/website-intake-model.md` |
| Demand Intelligence | `demand-intelligence/runtime/collect.py` | executable — this single entry point already chains collection → relevance filtering → scoring → routing (`ingest.py`'s `main()`), so invoking it is the entire Demand Intelligence pipeline, not a partial one |
| Revenue Hunter | `revenue-hunter/runtime/generate.py` | executable — `08-Revenue-Hunter/` is where `lead-scoring.md`, `decision-tree.md` and `revenue-forecasting-engine.md` live; `revenue-hunter/` is where they run, the same split as Sales Director, Product Manager and Content Director; see `revenue-hunter/revenue-hunter-runtime-notes.md` |
| CRM | `crm/runtime/generate.py` | executable — `06-CRM/` is where the specification and `company-intelligence.json` (the relationship record itself) live; `crm/` is where the read-only report generator runs, the same split as Sales Director, Product Manager, Content Director and Revenue Hunter; see `crm/crm-runtime-notes.md` |
| Service Mapping Engine | `service-mapping/runtime/generate.py` | executable — new in Sprint 3, no prior spec folder to split from (unlike the founder's original nine employees); spec and runtime both live under `service-mapping/`; see `service-mapping/service-mapping-model.md` |
| Sales Director | `sales-director/runtime/prepare.py` | executable — Sprint 12 added the Executive Proposal Generator: when a same-organisation Account Intelligence brief exists (read-only, one cycle behind — see this employee's own `dependsOn` note above), the proposal document is upgraded to an Executive Proposal traced back to that brief's own data; otherwise the original generic proposal is used; see `proposal-preparation-engine.md` |
| Account Intelligence | `account-intelligence/runtime/generate.py` | executable — new in Sprint 8, no prior spec folder to split from (like Service Mapping Engine/Website Intake); spec and runtime both live under `account-intelligence/`; see `account-intelligence/account-intelligence-engine.md` |
| Reverse Job Hunt | `reverse-job-hunt/runtime/generate.py` | executable — new in Sprint 9, no prior spec folder to split from; spec and runtime both live under `reverse-job-hunt/`; see `reverse-job-hunt/reverse-job-hunt-engine.md` |
| Recruiter Intelligence | `recruiter-intelligence/runtime/generate.py` | executable — new in Sprint 10, no prior spec folder to split from; spec and runtime both live under `recruiter-intelligence/`; see `recruiter-intelligence/recruiter-intelligence-engine.md` |
| Fractional Advisory Radar | `fractional-advisory-radar/runtime/generate.py` | executable — new in Sprint 11, no prior spec folder to split from; spec and runtime both live under `fractional-advisory-radar/`; see `fractional-advisory-radar/fractional-advisory-radar-engine.md` |
| Relationship Intelligence | `relationship-intelligence/runtime/generate.py` | executable — new in Sprint 13, no prior spec folder to split from; spec and runtime both live under `relationship-intelligence/`. Reads a founder-maintained, persistent, person-level record (`relationship-profiles.json`) — nothing here is auto-collected; see `relationship-intelligence/relationship-intelligence-engine.md` |
| Tender & RFP Intelligence | `tender-intelligence/runtime/generate.py` | executable — new in Sprint 14, no prior spec folder to split from; spec and runtime both live under `tender-intelligence/`. Self-contained (no dependsOn) — fetches real, founder-configured procurement RSS/Atom feeds directly, same "does nothing until configured" pattern as Demand Intelligence's Demand Signals connector; see `tender-intelligence/tender-intelligence-engine.md` |
| Executive Brand Intelligence | `executive-brand-intelligence/runtime/generate.py` | executable — new in Sprint 15, no prior spec folder to split from; spec and runtime both live under `executive-brand-intelligence/`. Read-only across Demand Intelligence, Account Intelligence and Relationship Intelligence's own already-computed data plus the shared supporting-assets.json catalogue — builds a Weekly Brand Plan and a persisted Monthly Authority Report; see `executive-brand-intelligence/executive-brand-intelligence-engine.md` |
| Delivery Intelligence | `delivery-intelligence/runtime/generate.py` | executable — new in Sprint 17 (the Consulting Delivery Engine), no prior spec folder to split from; spec and runtime both live under `delivery-intelligence/`. Triggers on Revenue Hunter's own `pipeline.json` `stage == "won"`; generates a ten-artifact delivery kit per engagement from the reusable ADGL/OPERA-aligned templates in `templates/delivery/`, cross-referencing Account Intelligence and Service Mapping read-only. Kits are generated once and never overwritten on a re-run; see `delivery-intelligence/delivery-intelligence-engine.md` |
| Company 360 | `company-360/runtime/generate.py` | executable — new in Sprint 19, no prior spec folder to split from; spec and runtime both live under `company-360/`. A pure read-only rollup — computes nothing new — joining Demand Intelligence, Account Intelligence, CRM, Relationship Intelligence, Reverse Job Hunt, Revenue Hunter's pipeline, Service Mapping and Delivery Intelligence into one view per organisation, regenerated in full every run; see `company-360/company-360-engine.md` |
| Executive Memory | `executive-memory/runtime/generate.py` | executable — new in Sprint 20, no prior spec folder to split from; spec and runtime both live under `executive-memory/`. A pure read-only aggregator over CEO Advisor's own new `daily-priorities-log.json` self-log (recurring priorities/alerts), Delivery Intelligence's completed closure reports (a real Lessons Learned Library), and Account Intelligence's already-fixed governance risk vocabulary (risks recurring across organisations), plus a founder-maintained `decision-log.json`; see `executive-memory/executive-memory-engine.md` |
| Market Positioning Intelligence | `market-positioning-intelligence/runtime/generate.py` | executable — new in Sprint 21, no prior spec folder to split from; spec and runtime both live under `market-positioning-intelligence/`. No real competitor/market-share/win-loss data exists anywhere in AOS (confirmed before this employee was designed), so it doesn't invent any — instead counts Service Mapping's own recommendations per catalogue service and Market Intelligence's own regulatory log per source, and states the same honest "Not tracked" competitive signal Sales Director's `competition_level()` already uses; see `market-positioning-intelligence/market-positioning-intelligence-engine.md` |
| Capacity Management | `capacity-management/runtime/generate.py` | executable — new in Sprint 22 (the sixth and final founder-ordered capability), no prior spec folder to split from; spec and runtime both live under `capacity-management/`. Sums active (pipeline `stage=='won'`, not yet Closed in `delivery-log.json`) and incoming (Sales Director's Ready To Send/Proposal Ready) workload via Sales Director's own rate-card `typicalDays`, banded against a new founder-tunable `capacity-config.json` into Available/Near/Over Capacity. `ceo-advisor/runtime/generate.py` reads this feed read-only, one cycle behind; see `capacity-management/capacity-management-engine.md` |
| Product Manager | `product-manager/runtime/generate.py` | executable — `03-Product-Manager/` is where the specification and `product-evaluation-framework.md` live; `product-manager/` is where it runs, the same split as Sales Director and Content Director; see `product-manager/product-manager-runtime-notes.md` |
| Content Director | `content-director/runtime/generate.py` | executable — `02-Content-Director/` is where Content Director's specification lives; `content-director/` is where it runs, exactly the same split as `04-Sales-Director`/`sales-director`; see `content-director/content-generation-model.md` |
| Daily Brief | `executive-dashboard/runtime/generate.py` | executable — `executive-dashboard/` is where Daily Brief's aggregation role and its own embedded "Today's Priorities" section both already live as code; see its own module docstring |
| Artifact Registry | `artifact-registry/runtime/registry_builder.py` | executable — infrastructure, not an employee (no business responsibility of its own); depends on every real employee so its index reflects a complete day's output, and runs before CEO Advisor rather than one cycle behind, since it depends on nothing CEO Advisor itself computes (unlike Capacity Management, which genuinely could create a cycle); see `artifact-registry/artifact-registry-model.md` |
| CEO Advisor | `ceo-advisor/runtime/generate.py` | executable — new in Sprint 5, the same split as Sales Director/Revenue Hunter/CRM/Product Manager/Content Director (`09-CEO-Advisor/` stays the specification, `ceo-advisor/` is where it runs); see `ceo-advisor/ceo-advisor-runtime-notes.md` for exactly what changed, including the Daily Brief/CEO Advisor position swap this required |

No employee is `NOT_EXECUTABLE` as of Sprint 5. When that was still
true of some employee, it was recorded honestly rather than
fabricating a step that would duplicate business logic that hadn't
been built yet — see git history for that convention if it's needed
again for a genuinely new future employee. Adding a real `runtime/`
script to an employee is always just a `script` path added to
`runtime/config/orchestrator-config.json` — no change to
`orchestrator.py` itself.
