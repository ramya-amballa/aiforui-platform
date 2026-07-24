# Daily Operating Workflow

The one repeatable cycle every AI employee runs, every day, starting
at 06:00. Each step names its exact inputs, its outputs, who it hands
off to, the decision points inside it, and what happens if it fails.
The cycle is written so it can be lifted directly into a scheduler
(GitHub Actions or otherwise) as a sequence of dependent jobs — see
`Automation Mapping` at the end.

Times below are illustrative spacing (15 minutes apart), not a
requirement that each step take that long; a step advances as soon as
its inputs are ready, and the scheduler should treat each time as "no
earlier than," not "exactly at."

## The Sequence

### 06:00 — Market Intelligence starts the cycle

Market Intelligence runs first because everything else in the business
reacts to the outside world before it reacts to itself.

- **Consumes**: external regulatory/standards/security sources listed
  in `05-Market-Intelligence/operating-manual.md`
- **Produces**: new entries in `regulatory-log.json`
- **Decision point**: is each development substantive (a real change)
  or noise (a duplicate, a minor edit, a rumor)? Only substantive
  entries proceed past this step.
- **Hands off to**: `02-Content-Director` (LinkedIn/newsletter idea),
  `03-Product-Manager` (product update), `opportunity-hunter`
  (consulting opportunity) — per the trigger rule, every substantive
  entry produces all three, even if one answer is "not applicable"
- **Failure handling**: if a source is unreachable, log it as
  `source-check-failed` in `regulatory-log.json` with a timestamp and
  continue to the next source. A single source outage never blocks the
  rest of the cycle. If every source fails, the cycle continues with
  an empty trigger set and flags "Market Intelligence check failed
  today" to the final Daily Brief.

### 06:15 — Opportunity Hunter

- **Consumes**: the nineteen sources in
  `opportunity-hunter/opportunity-sources.md`; any consulting-opportunity
  trigger from Market Intelligence's 06:00 run
- **Produces**: new/updated entries in `opportunity-schema.json`;
  new/updated entries in `companies.md`; new/updated records in
  `06-CRM/company-intelligence.json` for any company not already on file
- **Decision point**: score each candidate across all eleven dimensions
  and classify it, per `opportunity-scoring-engine.md`. `Immediate
  Proposal` gets a first-touch draft from `proposal-template.md`;
  `Ignore` is archived, not deleted.
- **Hands off to**: per classification, exactly as
  `opportunity-scoring-engine.md`'s routing table specifies —
  `08-Revenue-Hunter` (`Immediate Proposal`, `Partnership`), `06-CRM`
  (new company records, `Follow Recruiter`, `Relationship Building`),
  `03-Product-Manager` (`Convert into Product Idea`), `02-Content-Director`
  (`Convert into Content`)
- **Failure handling**: if a source is unreachable, skip it and record
  which source was skipped in today's
  `daily-opportunity-report-template.md` entry. If scoring cannot run
  (e.g. missing data on a candidate), log the candidate as `unscored`
  rather than dropping it, and flag it for manual review in the Daily
  Brief.

### 06:30 — Content Director

- **Consumes**: Market Intelligence's 06:00 triggers; recurring
  patterns from `06-CRM`; any Product Manager launch notification
  outstanding from the previous cycle
- **Produces**: new/updated `content-brief-template.md` entries;
  `content-calendar-template.md` updates
- **Decision point**: does this signal map to one of the five
  objectives (leads, sales, authority, subscribers, SEO) clearly enough
  to brief today, or does it need another occurrence before it's worth
  producing (see `content-conversion-map.md` — never publish a
  regulation summary with no distinct practitioner take)?
- **Hands off to**: `03-Product-Manager` (a brief that surfaces a
  recurring question is itself a product signal); `08-Revenue-Hunter`
  (a brief tied to a direct lead)
- **Failure handling**: if no signal from today's Market Intelligence
  run clears the bar in the decision point, Content Director produces
  no new brief and that is a valid, correctly-functioning result —
  logged as "no qualifying signal today," not a failure.

### 06:45 — Product Manager

- **Consumes**: Market Intelligence's product-update triggers;
  `06-CRM` patterns; Content Director's briefs; any flag left by
  `04-Sales-Director` from the previous cycle
- **Produces**: new/updated entries in `product-backlog.json`
- **Decision point**: run `product-evaluation-framework.md` — Step 1
  (is this reusable), Step 2 (match a format), Step 3 (score 0-40).
  30+ moves to `in-development`; 15-29 stays `candidate`; below 15 is
  `parked` but retained, never discarded.
- **Hands off to**: `02-Content-Director` (30+ scores need launch
  content); `08-Revenue-Hunter` (30+ scores with clear revenue
  potential)
- **Failure handling**: if a signal can't be scored because the demand
  evidence is incomplete, log it as `candidate` with a note rather than
  forcing a score, and flag it for the next cycle once more evidence
  exists.

### 07:00 — Revenue Hunter

- **Consumes**: `Priority` items from Opportunity Hunter;
  30+-scored items from Product Manager; existing-client upsell
  signals from `06-CRM`; stage changes reported by Sales Director in
  the previous cycle
- **Produces**: new/updated entries in `pipeline.json`; a refreshed
  `revenue-dashboard-template.md`
- **Decision point**: score every item (new or updated) against
  `lead-scoring.md`; band as Priority (80-100), Active (50-79), or
  Deferred (below 50), per `decision-tree.md`
- **Hands off to**: `04-Sales-Director` (every item that needs an
  active relationship touch); `09-CEO-Advisor` (Priority-band items
  with a near-term `nextActionDue`)
- **Failure handling**: if a required upstream file
  (`opportunity-schema.json`, `product-backlog.json`, or
  `company-intelligence.json`) is malformed
  or unreadable, Revenue Hunter runs on the last known-good pipeline
  state, flags the read failure explicitly, and does not silently drop
  existing pipeline items.

### 07:15 — Sales Director

- **Consumes**: `06-CRM/company-intelligence.json` (`relationshipTemperature`,
  `nextFollowUpDue`, `lastTouch`, `outreachHistory`); stage context
  from Revenue Hunter's 07:00 run
- **Produces**: outreach drafts per `outreach-draft-template.md`; a
  prioritised follow-up queue per `follow-up-priority-model.md`
- **Decision point**: for every `hot`/`warm`/`cooling` record, is it
  due, due soon, or on track (per `follow-up-priority-model.md`)? Any
  `hot` record more than 3 days past tolerance, or any record tied to
  a `strategicValue: high` pipeline entry, escalates rather than
  joining the ordinary queue.
- **Hands off to**: `09-CEO-Advisor` (escalated at-risk relationships,
  which are always at least a runner-up); the founder (drafts await
  human review before sending — Sales Director drafts, it never sends
  unsupervised)
- **Failure handling**: if `company-intelligence.json` can't be read,
  Sales Director produces no drafts for that cycle rather than
  guessing, and flags "follow-up queue not generated today" to the
  Daily Brief so the gap is visible, not silent.

### 07:30 — CEO Advisor

- **Consumes**: Sales Director's follow-up queue and escalations;
  Revenue Hunter's `pipeline.json` (Priority band, near-term
  `nextActionDue`); Opportunity Hunter's `opportunity-schema.json`;
  Product Manager's `product-backlog.json`; Market Intelligence's
  consulting flags
- **Produces**: a completed `daily-recommendation-template.md`
- **Decision point**: run `decision-model.md` — normalise every
  candidate to a 0-10 value score, apply the urgency overlay, break
  ties on effort. Escalated at-risk relationships are always at least
  a runner-up regardless of raw score.
- **Hands off to**: `07-Daily-Brief` (its recommendation is the lead
  item)
- **Failure handling**: if an upstream employee's output is missing
  for the day (e.g. Sales Director produced no queue), CEO Advisor
  still runs on whatever inputs are available and explicitly notes
  which sources were unavailable, rather than blocking the whole
  recommendation on one missing input.

### 07:45 — Daily Brief (final assembly)

- **Consumes**: every output above — Opportunity Hunter's daily report,
  Revenue Hunter's dashboard, Content Director's ideas, Product
  Manager's candidates, Market Intelligence's regulatory summary,
  Sales Director's follow-up queue, and CEO Advisor's recommendation
- **Produces**: `daily-revenue-brief-template.md`, filled in for the
  day
- **Decision point**: none — Daily Brief assembles and formats, it
  does not re-decide anything CEO Advisor already decided
- **Hands off to**: the founder. This is the terminal node; nothing
  downstream consumes Daily Brief's output automatically
- **Failure handling**: if any upstream section is missing, Daily
  Brief still generates, with that section marked "not available
  today" rather than failing the whole brief. A partial brief at 08:00
  is always better than no brief.

### 08:00 — Delivery

The Daily Revenue Brief is delivered. The founder reviews Sales
Director's drafts and CEO Advisor's recommendation, sends what's
approved, and any sent touch is logged back to `outreachHistory` in
`06-CRM/company-intelligence.json`, closing the loop before the next
day's 06:00 run.

## Automation Mapping

This sequence is a dependency chain, not a fixed clock schedule — each
step's real dependency is "the step before it has produced its output
today," not "15 minutes have passed." Mapped to GitHub Actions:

```
schedule: cron '0 0 * * *'   # 06:00 in the target timezone

jobs:
  market-intelligence:        # no dependencies, runs first
  opportunity-hunter:
    needs: market-intelligence
  content-director:
    needs: market-intelligence
  product-manager:
    needs: [market-intelligence, content-director]
  revenue-hunter:
    needs: [opportunity-hunter, product-manager]
  sales-director:
    needs: revenue-hunter
  ceo-advisor:
    needs: [sales-director, revenue-hunter, opportunity-hunter, product-manager]
  daily-brief:
    needs: ceo-advisor        # transitively needs everything above
```

`content-director` and `opportunity-hunter` both only depend on
`market-intelligence`, so they can run in parallel; the chain only
serialises where a real data dependency exists. Each job should be
idempotent — safe to re-run against the same day's data without
duplicating entries — since a scheduler will retry a failed job, and
the JSON schemas already use unique `id` fields for exactly this
reason.
