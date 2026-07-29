# Company 360 (AOS Sprint 19)

## Objective

AOS scattered per-organisation facts across eight employees, each with
its own field names and, in three cases, its own literal key field for
"which company." A founder trying to understand one organisation had
to open eight different dashboard pages and mentally merge them.
Company 360 is that merge, done once, read-only, computing nothing
new.

## What This Is Not

Not a new scoring engine. Not a ninth independently-computed number.
Every field in a Company 360 profile is reused verbatim from the
employee that already computed it, labelled by that employee's name.
Where two employees genuinely estimate the same kind of thing from two
different formulas, both are shown side by side — never averaged,
never reconciled into a third figure.

## The Key-Field Problem

Three different literal field names exist for "which company," across
files with no shared ID:

| Source | Field name |
|---|---|
| `demand-intelligence/organisation-profiles.json` (canonical), `account-intelligence-feed.json`, `reverse-job-hunt-feed.json`, `08-Revenue-Hunter/pipeline.json`, `delivery-log.json`/feed | `organisation` |
| `06-CRM/company-intelligence.json` | `companyName` |
| `relationship-intelligence/relationship-profiles.json` (via its own feed) | `company` |

The first group is machine-written — every one of those employees
copies the identical `organisation` string that `organisation-profiles.json`
originated, so those are matched by exact string equality. `companyName`
and `company` are fields the founder can enter independently (CRM
records, contact profiles), so those two are matched via a purely
internal `normalise()` (lowercase + trim) — never surfaced, never
persisted as a new canonical id other employees would need to adopt.

## The Universe

Every organisation `demand-intelligence/organisation-profiles.json`
already knows about gets a Company 360 profile — that file is the
broadest, canonical per-organisation store every other employee's own
`organisation` string traces back to. A company with no Account
Intelligence brief yet, no CRM record yet, or no pipeline entry yet
still gets a profile, honestly stating what doesn't exist rather than
being silently skipped.

## Where the Same Kind of Fact Is Computed Twice — Shown, Never Merged

1. **"What to do next"** — three separately-computed, differently-named
   recommendations, each answering a genuinely different question:
   `recommendedAction` (Demand Intelligence — next pipeline action),
   `outreachStrategy` (Account Intelligence — first-touch framing),
   `entryPoint` (Reverse Job Hunt — which channel). All three are
   surfaced, labelled by source.
2. **"How big is this deal" before a real pipeline record exists** —
   Account Intelligence's `overallPriority` (a demand-score-derived
   estimate) and Reverse Job Hunt's `consultingPotentialEstimate` (a
   separate, scale-threshold-derived estimate) are two independent
   numbers for the same underlying question. Both are shown, explicitly
   labelled as not the same figure — never averaged.
3. **"Relationship health"** — CRM's `relationshipTemperature` (company-
   level, deal-relationship), Relationship Intelligence's `healthScore`/
   `healthBand` (person-level, individual-contact relationship) and
   Reverse Job Hunt's own `touchpoint-log.json`/`campaignStatus` (BD-
   campaign-specific outreach) are three legitimately different facts.
   All three are shown, never blended into one "temperature."
4. **Buying readiness** is the one case that is genuinely a single fact,
   not a duplicate: `buyingReadinessScore`/`Band` is computed once in
   Demand Intelligence and reused verbatim everywhere else (Account
   Intelligence copies the band; Reverse Job Hunt's
   `probabilityOfEngagement` is the same demand-intelligence number,
   just renamed). Company 360 reads it once from Demand Intelligence.

## What Gets Joined

Per organisation: Demand Intelligence's own profile (buying readiness,
demand score, recommended action); Account Intelligence's brief
(executive summary, deployment stage, governance risks, service fit,
decision-maker titles, outreach strategy, overall priority); CRM's
relationship record (existing relationship, temperature, recruiter,
prior applications, last touch, next follow-up); every Relationship
Intelligence contact matched to that company (health score/band, risk,
reconnect recommendation); Reverse Job Hunt's BD strategy (entry point,
consulting potential estimate, campaign status, touchpoints); every
Revenue Hunter pipeline entry for that organisation; every Service
Mapping recommendation for that organisation's opportunities (joined
through `opportunity-schema.json`); Delivery Intelligence's engagement
phase; and (Sprint 23 — Engagement Templates) every real `domainTag`
already recorded across that organisation's own opportunities, so the
founder can see at a glance which regulatory framework annex and
proposal template — DORA, EU AI Act, Security Governance, Third-Party
Risk, GRC, Technology Risk — already applies, without opening Sales
Director or Delivery Intelligence separately.

## Regenerated in Full, Every Run

Unlike Sales Director's proposals or Delivery Intelligence's kits —
both living documents the founder edits by hand — nothing in a Company
360 profile is founder-edited. It's entirely re-derived from other
employees' own persisted output, so there is nothing to protect from
being overwritten; a re-run simply reflects the latest state of every
source.

## Dashboard

**Company 360** page: one row per organisation (industry, buying
readiness, existing relationship, delivery phase, pipeline entry
count), and — for the selected organisation — the full printable 360
profile with a download button.

## What This Engine Does Not Do

- Does not compute a new score, verdict, or "health" number of its own.
  Every figure is reused verbatim from the employee that produced it.
- Does not reconcile two independently-computed estimates into a third.
  See "Where the Same Kind of Fact Is Computed Twice" above.
- Does not write to any of the eight sources it reads. Every read is
  read-only.
- Does not introduce a new canonical company ID. `normalise()` is a
  purely internal join key for this engine's own matching, never
  persisted or exposed to any other employee.
