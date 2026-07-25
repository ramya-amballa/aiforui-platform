# AOS Runtime Sprint 2 — Completion Report

Sprint 2 built the four remaining runtime AI employees — Content
Director, Product Manager, Revenue Hunter, CRM — in that order, each
fully completed, tested, integrated into the Orchestrator, committed,
and documented before the next began, per the founder's instruction.
This report is the required close-out: what was built, where it
plugs in, what's still manual, what's known-limited, and what a
Sprint 3 could reasonably cover next.

No architecture was redesigned. No new AI employee was created beyond
the four named. No runtime was modified except where a later runtime's
integration required a small, additive change to an earlier one (see
"Integration Points" below).

## What Was Built

### 1. Content Director Runtime (`content-director/`)

Converts approved signals into publish-ready drafts, never publishes.

- Consumes: Market Intelligence's `content-brief-queue.json`,
  Opportunity Hunter's `Convert into Content` opportunities, Product
  Manager's shipped products, CEO Advisor's daily priority.
- Determines, per signal: LinkedIn post / newsletter article / website
  insight / product announcement.
- Grounds every draft in `sales-director/runtime/config/practitioner-bank.json`
  (ADGL, OPERA, AI Governance, product catalogue, practitioner
  experience) — reused, not re-collected — with a hard grounding gate:
  no real match, no draft above `Low Value`.
- Outputs: `.md` drafts per format in `runtime/output/`, each with
  hashtags, hero-image-type, and CTA recommendation; a review queue
  feed for CEO Advisor (`Ready to Publish` / `Needs Review` /
  `Low Value`).
- Fixed bugs found in testing: missing `domainTags` on several
  candidate types (would have forced everything to `Low Value`
  regardless of real relevance); a cosmetic double-period bug in
  generated hook lines.

### 2. Product Manager Runtime (`product-manager/`)

Identifies recurring consulting demand and scores it as a product
candidate — never builds anything automatically.

- Consumes: Market Intelligence's unscored backlog candidates,
  Opportunity Hunter's `Convert into Product Idea` opportunities, a
  real recurring-domain-tag count from Sales Director's prepared
  proposals, Content Director's queued signals.
- Executes `03-Product-Manager/product-evaluation-framework.md`'s
  existing Steps 2-4 as code for the first time — a real 0-40 score,
  one of nine formats (Toolkit, Workbook, Checklist, Executive Guide,
  Workshop, Training, Subscription, ADGL Extension, OPERA Module),
  estimated revenue, build effort, business case.
- Extended `product-evaluation-framework.md` additively (2 new formats
  the founder's spec added, plus a "Runtime Execution Notes" section
  with a worked example) rather than rewriting it.
- Routes recommendations to CEO Advisor only.

### 3. Revenue Hunter Runtime (`revenue-hunter/`)

The financial intelligence engine — became AOS's honesty benchmark
for this sprint: **no financial assumption may be fabricated**.

- Consumes: Opportunity Hunter's unrouted `Active`/`Priority`
  opportunities, CRM's `hot`/`warm` relationships with no open pipeline
  item, Sales Director's prepared-proposal index (stage advancement),
  Product Manager's shipped/in-development products.
- Executes `lead-scoring.md`, `decision-tree.md`, and
  `revenue-forecasting-engine.md` as code for the first time — reused
  the exact same scoring weights `ingest.py` already applies, rather
  than inventing a second formula.
- Where no real `expectedRevenue` exists, writes the literal string
  `"Not yet estimated"` and excludes it from every dollar sum — still
  counted and surfaced, never guessed, not even a labelled estimate
  (deliberately more conservative than Sales Director's rate-card
  approach, since forecasting is a different context than a pricing
  conversation).
- Outputs: revenue dashboard, monthly/quarterly forecast, highest-ROI
  opportunities — verified byte-for-byte against
  `revenue-forecasting-engine.md`'s own worked example.

### 4. CRM Runtime (`crm/`)

Long-term relationship intelligence, strictly read-only.

- Consumes: `company-intelligence.json` (read-only), Opportunity
  Hunter's opportunity history per organisation, Sales Director's
  proposal history, Revenue Hunter's open-pipeline history.
- Never writes `relationshipTemperature`, `nextFollowUpDue`, or
  `outreachHistory` — `06-CRM/README.md` already reserves those to
  Sales Director exclusively; this runtime's read-only guarantee was
  verified with a before/after md5sum on `company-intelligence.json`.
- Reused `crm_follow_up_status()` and the currency parser verbatim
  from `executive-dashboard/runtime/generate.py`.
- Genuinely new: stale-cold-relationship detection (a `cold` company
  past 90 days since `lastTouch` — a case
  `executive-dashboard`'s CRM section explicitly skips) and a combined
  relationship health view (opportunity + proposal + pipeline history
  per company) nothing else in AOS produced before.
- Relationship categorisation (Recruiter, Client, Consulting Firm,
  Prospect) inferred from existing fields; Speaking Contact and
  Partner reported as an honest gap — not guessed — since no existing
  field supports them.
- Outputs: daily follow-up queue, relationship health report,
  stale-relationship alerts.

## Integration Points

Every runtime above is wired into
`orchestrator/runtime/config/orchestrator-config.json` with a real
`script` path, `dependsOn` edges that match the fixed execution order,
and `outputPaths` the Orchestrator checks by existence after a
`SUCCESS`. No change was needed to `orchestrator.py` itself for any of
the four — this is the integration contract established when the
Orchestrator was first built, holding exactly as designed.

`dependency-map.md` and `AOS/README.md` were updated after each
runtime landed to keep the "what actually has a runtime today" table
and the AI Employees/Status tables accurate. As of this report:

| Employee | Runtime status |
|---|---|
| Market Intelligence | executable |
| Opportunity Hunter | executable |
| Revenue Hunter | executable |
| CRM | executable |
| Sales Director | executable |
| Product Manager | executable |
| Content Director | executable |
| CEO Advisor | `NOT_EXECUTABLE` — by design, its decision model already runs as a section of Daily Brief's own generator |
| Daily Brief | executable |

Eight of the nine employees now have code the Orchestrator can invoke.
A full 9-step Orchestrator run was executed against a fresh scratch
copy of the real repo after each runtime landed, most recently after
CRM: all eight executable employees returned `SUCCESS`, CEO Advisor
correctly reported `NOT_EXECUTABLE`, and the Daily Execution Report
generated cleanly.

A small number of additive-only changes were made to earlier runtimes
strictly to make a later runtime's integration real, never to redesign
them:

- `content-brief-queue.json` created under `02-Content-Director/` as
  the intake file Market Intelligence writes to and Content Director
  reads/updates — a new file, not a change to either runtime's logic.
- `product-evaluation-framework.md` extended with 2 new formats and a
  "Runtime Execution Notes" section (additive, Product Manager build).
- `opportunity-schema.json` and `regulatory-log.json` gained new
  fields (`relevanceScore`, `scopedEngagement`, `checks`, `routedTo`)
  earlier in the overall build, reused as-is by every runtime that
  reads them.

## Remaining Manual Activities

Nothing in AOS sends, publishes, or posts anything automatically —
that boundary was held throughout this sprint, as instructed:

- **Sales Director**: proposals, cover letters, and outreach are
  prepared, never sent. A human sends every message.
- **Content Director**: drafts are generated, never published. A human
  reviews the CEO Advisor queue and publishes manually.
- **Product Manager**: product recommendations are scored and
  reasoned, never built. A human decides what to actually build.
- **Revenue Hunter**: forecasts and dashboards are calculated, never
  acted on automatically — no deal is closed, won, or lost by this
  runtime.
- **CRM**: follow-up queues and alerts are surfaced, never actioned —
  no email, LinkedIn message, or other outreach is sent by this
  runtime.
- **CEO Advisor**: has no independent runtime; a human still reads its
  decision-model output (via Daily Brief) and decides the single
  highest-ROI action for the day.

## Known Limitations

- **CEO Advisor remains `NOT_EXECUTABLE`** — its decision model already
  runs as one section of Daily Brief's generator
  (`executive-dashboard/runtime/generate.py`), so it produces real
  output today, but the Orchestrator has no independent script to
  invoke for it as its own step.
- **"One cycle behind" reads, in three places** — because the
  Orchestrator's execution order is fixed, some runtimes read a file
  written by a runtime that executes *later* in the same day's
  sequence, so they only see the previous day's state for that
  specific input. This self-corrects the following run and is
  documented in each affected runtime's own notes:
  - Revenue Hunter (step 3) reads Sales Director's `processed-index.json` (step 5).
  - Product Manager (step 6) reads Content Director's queue state (step 7).
  - CRM (step 4) reads Sales Director's `processed-index.json` (step 5).
- **Speaking Contact and Partner are not inferable** in CRM's
  relationship categorisation — `company-intelligence.json`'s schema
  has no field that distinguishes them from a Prospect. Reported as an
  honest gap in every CRM report, not guessed.
- **CRM's 90-day stale-cold threshold** is a documented, adjustable
  default (roughly "reviewed monthly" extended to an actual
  re-engagement trigger), not a discovered fact from real data.
- **Utility functions are duplicated by necessity, not by choice** —
  `parse_currency`/`format_amount`, `crm_follow_up_status()`, and the
  lead-scoring weights are copied verbatim across
  `executive-dashboard/`, `revenue-hunter/`, and `crm/` because each
  runtime executes as its own subprocess with no shared Python import
  path. If any of these ever need to change, they must change
  identically in every copy until AOS has a shared utilities location.
- **All real business data files remain empty** on this repo today
  (no companies, no opportunities logged yet) — every runtime was
  fixture-tested in isolated scratch copies and separately smoke-tested
  against the real, currently-empty repo, where the honest behaviour
  is a clean no-op ("nothing to report") rather than a fabricated
  result. Real output will start appearing once collection begins.

## Recommended Runtime Sprint 3 Roadmap

Per the founder's explicit instruction, AOS stops here: no additional
AI employee, no automation beyond the existing Orchestrator, without
further direction. If a Sprint 3 is authorized in the future, in
priority order:

1. **A shared utilities module** — the single highest-leverage
   cleanup: dedupe `parse_currency`/`format_amount`,
   `crm_follow_up_status()`, and the lead-scoring weights into one
   location every runtime's subprocess can load, rather than three
   verbatim copies.
2. **CEO Advisor's own runtime** — give `decision-model.md` an
   independent script so it stops being a section of Daily Brief's
   generator and becomes its own Orchestrator step, closing the last
   `NOT_EXECUTABLE` gap.
3. **Resolve the "one cycle behind" reads** — once there's a real
   need, consider whether the Orchestrator should support a second
   pass for the three affected reads, rather than accepting same-day
   staleness indefinitely. Not urgent today since it self-corrects.
4. **Real data collection** — none of this sprint's work is visible
   in output until Opportunity Hunter's collection actually runs
   against live sources and accumulates real opportunities and
   companies; every runtime is ready and waiting on real input.

## Sign-off

All four runtimes are committed to `main`: Content Director
(`018241a`), Product Manager (`3bd8ee5`), Revenue Hunter (`a5df7b8`),
CRM (`79466a0`). Sprint 2 is complete as scoped. Stopping here per
instruction.
