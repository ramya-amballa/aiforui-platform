# Demand Intelligence (v2)

AI employee #1, and the first to be built as a live operating
component rather than a documented role. Formerly named "Opportunity
Hunter" — renamed 2026-07-25 because its job is no longer just finding
advertised vacancies. Its primary discovery mode, Demand Signals (see
`collectors/demand_signals.py`), answers a different, higher-value
question: which named organisation, in the world, is most likely to
need AI for U&I's services this week — inferred from real evidence
(an AI vendor reporting a named customer deployed its tool at scale),
not waited for in a job posting. Demand Intelligence continuously
feeds AOS with real opportunities: it monitors twenty sources, scores
every candidate across eleven dimensions, classifies it into one of
eight actions, and routes it downstream with no manual reformatting.

## What "v1" Means

Earlier AOS employees are specified as operating manuals: mission,
workflow, daily output. Demand Intelligence v1 is that plus a real
schema, a deterministic scoring and classification engine, and an
explicit routing contract to every downstream consumer — the
architecture a future GitHub Actions job (or any other scheduler) can
be wired directly against without redesigning anything. This build
defines that architecture; connecting it to live sources and a
scheduler is the next phase, not this one.

## Files

- `opportunity-sources.md` — the nineteen sources monitored, grouped by
  channel, with default domain tagging and the connector type each
  will eventually need
- `opportunity-scoring-engine.md` — the eleven-dimension weighted
  model, banding, the classification decision tree, and the exact
  field-level routing contract to every downstream file
- `opportunity-schema.json` — the live opportunity record: one entry
  per opportunity, schema documented in the file itself, starting empty
- `opportunity-backlog.md` — the weekly pipeline view: open
  opportunities by band, classification, source and domain, plus an
  aging list for anything stalled
- `daily-opportunity-report-template.md` — the day's findings, split
  into the views the business actually needs (highest revenue,
  highest strategic, ADGL, AI Deployment Governance, AI Governance),
  handed to `07-Daily-Brief`
- `companies.md` — a lightweight log of organisations encountered
  while sourcing; the full record lives in
  `06-CRM/company-intelligence.json`
- `proposal-template.md` — the first-touch note used for anything
  classified `Immediate Proposal`
- `opportunity-relevance-engine.md` — the second-stage filter that runs
  before scoring: a 0-100 relevance score with worked examples, the
  penalties, and the threshold below which an opportunity never reaches
  scoring at all
- `CONNECTOR-CONFIGURATION-GUIDE.md` — how to activate each Phase 1
  autonomous-collection connector (Upwork, LinkedIn Jobs, Wellfound,
  RemoteOK, Greenhouse, Lever, Ashby): what each needs, where to get
  it, and how to test it independently

Start with `opportunity-sources.md`, then `opportunity-scoring-engine.md`.

## Historical Migrations

`runtime/cleanup_relevance_v1.py` — a one-time, already-run migration
that reprocessed every opportunity logged before the relevance engine
existed. Fourteen false positives from the first live Collection
Engine run (all false-positive matches on the keyword `RAG`) were
removed from `opportunity-schema.json`, `08-Revenue-Hunter/pipeline.json`
and `06-CRM/company-intelligence.json`. Nothing was deleted — every
removed record, its relevance score, its rejection reason, and the run
timestamp are archived in `runtime/archive/relevance-cleanup-v1/`. Not
part of any ongoing workflow; kept for reproducibility and audit.

## Execution

`runtime/` is this specification running as code: drop manually
collected opportunities (Markdown or JSON) into `runtime/inbox/`, run
`python3 runtime/ingest.py`, and it runs every record through the
relevance filter first (`runtime/relevance.py`) — anything below the
threshold goes to `runtime/rejected/` with a reason and stops there.
Everything that clears it scores, classifies, routes to
`08-Revenue-Hunter/pipeline.json` and `06-CRM/company-intelligence.json`,
and writes the day's report to `runtime/output/` — the same logic
above, executed rather than described. See the docstring at the top of
`runtime/ingest.py` for the exact input format.

## Autonomous Collection

Manual entry into `runtime/inbox/` is no longer required. `runtime/collect.py`
runs one collector per source (`runtime/collectors/`), each searching
the keywords in `runtime/config/keywords.json`:

- **Live today, no config needed:** RemoteOK (single global feed)
- **Live once per-company tokens/slugs are added to `runtime/config/sources.json`:**
  Greenhouse, Lever, Ashby (each is a real, public, unauthenticated API —
  add the companies you want to watch)
- **Live once career-page URLs are added to `runtime/config/sources.json`:**
  UAE Recruiters, Consulting Firms (generic page scan — no API exists for
  these)
- **Connector-ready, awaiting credentials (real OAuth2 secrets):** Upwork
  — the OAuth2 token-refresh and GraphQL request code is real and wired
  (`runtime/collectors/upwork.py`); it activates the moment real
  credentials are supplied
- **Connector-ready, awaiting API access (no self-serve path exists):**
  LinkedIn Jobs (Talent Solutions/Jobs API partner approval required),
  Wellfound (no public or partner API documented today) — no scraping
  fallback was built for either, by design
- **Connector-ready, out of Phase 1 scope, unchanged:** Google Jobs,
  FlexJobs — same wiring, needs a provider/account before it returns
  anything

See `CONNECTOR-CONFIGURATION-GUIDE.md` for exactly how to activate each
Phase 1 connector, `runtime/config/credentials.template.env` for which
environment variables to set instead of committing real secrets, and
`runtime/integration-status-dashboard.md` for current status
(regenerated automatically every run).

Every discovered posting is normalised into `opportunity-schema.json`'s
shape, heuristically scored (flagged `autoScored: true`, since no human
has judged it yet — treat as a starting point to verify), deduplicated
against `runtime/dedupe-index.json`, and recorded in
`runtime/snapshots/` regardless of whether it was new. New postings are
written to `runtime/inbox/` and immediately handed to `ingest.py` — the
same relevance filter, scoring, classification and routing manual
entries go through, with no separate logic path. Run
`python3 runtime/collect.py` directly, or let the AOS Orchestrator
(`AOS/orchestrator/orchestrator.py`, invoked daily by
`.github/workflows/aos-daily-operations.yml`) run it as one step in its
fixed sequence — the Orchestrator is the only thing GitHub Actions
invokes directly.

## Daily Workflow

1. Check every source in `opportunity-sources.md` for anything new in
   the last 24 hours (or since its last check, per its cadence).
2. Log each candidate in `opportunity-schema.json`: source, date found,
   raw description, link, domain tags.
3. Score it across all eleven dimensions and compute its Priority
   Score, per `opportunity-scoring-engine.md`.
4. Classify it using the decision tree in `opportunity-scoring-engine.md`.
5. Route it: write the entry to every downstream file the routing
   table specifies for its classification (`08-Revenue-Hunter/pipeline.json`,
   `06-CRM/company-intelligence.json`, `02-Content-Director/content-brief-template.md`,
   `03-Product-Manager/product-backlog.json`), and record what it was
   routed to in the opportunity's own `routedTo` field.
6. For anything classified `Immediate Proposal`, draft a first-touch
   note using `proposal-template.md`.
7. Add or update the organisation in `companies.md`; if it's a new
   company, add a full record to `06-CRM/company-intelligence.json`.
8. Fill in today's entry in `daily-opportunity-report-template.md` and
   hand it to `07-Daily-Brief`.
9. Update `opportunity-backlog.md` if the weekly view is due for a
   refresh.

## Integration Contract

Demand Intelligence writes to, and is read by, every other employee
listed below. Field names are shared deliberately — see
`opportunity-scoring-engine.md`'s routing table for the exact mapping,
so nothing downstream needs reformatting:

| Employee | Relationship |
|---|---|
| `08-Revenue-Hunter` | Receives `Immediate Proposal` and `Partnership` classifications as new `pipeline.json` entries |
| `06-CRM` | Receives every opportunity tied to an organisation not yet on record, and relationship-temperature updates for `Follow Recruiter`/`Relationship Building` classifications |
| `09-CEO-Advisor` | Reads `Priority`-band opportunities as daily-recommendation candidates |
| `03-Product-Manager` | Receives `Convert into Product Idea` classifications as new `product-backlog.json` candidates |
| `02-Content-Director` | Receives `Convert into Content` classifications as new `content-brief-template.md` briefs |
| `04-Sales-Director` | Receives `Follow Recruiter` and `Relationship Building` classifications into its follow-up queue |
| `07-Daily-Brief` | Receives the daily report as its top-of-funnel input |

## Success Metrics

- Opportunities logged per week, by source
- Time from an opportunity appearing publicly to being logged and
  scored
- Classification accuracy: opportunities re-classified after the fact
  because the automatic call was wrong
- Percentage of `Priority`-band opportunities routed downstream within
  the same day
- Zero opportunities that would have scored `Priority` and were missed
  entirely, checked retrospectively against source archives
