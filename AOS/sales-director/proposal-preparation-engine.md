# Proposal Preparation Engine

The model `runtime/prepare.py` executes. Covers three things: what goes
into every generated package, how recommended pricing is derived, and
how the proposal confidence score becomes the one-word status CEO
Advisor is allowed to see.

## Input

Every opportunity in `demand-intelligence/opportunity-schema.json` whose
`classification` is one of:

- `Immediate Proposal`
- `Apply`
- `Partnership`
- `Follow Recruiter`

`Ignore`, `Relationship Building`, `Convert into Content` and `Convert
into Product Idea` are out of scope — those are handled by, respectively,
nothing, `04-Sales-Director`'s ordinary follow-up cadence,
`02-Content-Director`, and `03-Product-Manager`.

Each opportunity is enriched, never re-decided, from two places already
holding real data about it:

- `08-Revenue-Hunter/pipeline.json`, matched by `sourceRef == opportunity.id`,
  when `Immediate Proposal` or `Partnership` routed one there — gives a
  real `expectedRevenue`, `probabilityOfSuccess`, `strategicValue`, and
  `type`
- `06-CRM/company-intelligence.json`, matched by `organisation`, when the
  company has a record already — gives `tailoredPositioning`,
  `outreachHistory`, `recruiter`, `existingRelationship`

## The Content Bank

Every generated document quotes from one place —
`runtime/config/practitioner-bank.json` — never from invented claims
about AI for U&I. It holds, verbatim from the live site and AOS itself:

- The practitioner-experience bullets (thirteen years across PwC, Wells
  Fargo, JPMorgan Chase and Viatris; TPRM across hundreds of vendor
  relationships; 300+ business-critical applications tested with a 35%
  residual-risk reduction; global KYC/sanctions operations;
  certifications; served sectors), each tagged with the domains and
  sectors it's actually relevant to, so a document only cites the
  experience that fits the opportunity in front of it
- The real product catalogue (ADGL Methodology, AI Governance Maturity
  Framework, AI Governance Decision Playbook, DPDP Readiness Briefing
  and Toolkit, Governance Operating Model Template, Technology Risk
  Whitepaper, Cyber Governance Reference Architecture, Government
  Digital Governance Artefact Pack, Audit Readiness Checklist, and the
  Executive Capability Overview), each tagged with the domain(s) it
  serves, pulled directly from `aiforu-platform/src/content/resources.ts`
- ADGL's five phases (Discover, Assess, Govern, Deploy, Operate) and
  OPERA's five phases (Opportunity, People, Evaluation, Response,
  Assurance), used only when the opportunity's `domainTags` actually
  include `ADGL`/`AI Deployment Governance` or general `AI Governance`
  respectively — never forced into a document where they don't fit

Selection is deterministic: match the opportunity's `domainTags` (and,
for practitioner bullets, its `location`/sector signal) against each
bank entry's own tags, and take every match. Nothing is picked at
random and nothing is invented per-opportunity.

## Recommended Pricing

1. **A real number already exists.** If the matched `pipeline.json`
   entry has an `expectedRevenue` that isn't the literal string "Not
   yet estimated", use it as-is. This is a founder-entered or
   Revenue-Hunter-estimated figure — the engine defers to it rather
   than computing a competing number.
2. **No real number exists yet** (true for every `Apply`/`Follow
   Recruiter` opportunity, since only `Immediate Proposal`/`Partnership`
   ever reach `pipeline.json`, and for any pipeline entry still
   "Not yet estimated"). Derive an estimate from
   `runtime/config/rate-card.json`:
   - Map the opportunity to an engagement type: the matched pipeline
     entry's `type` if one exists, else `Consulting Project` for
     `Apply`/`Immediate Proposal`, `Partnership` for `Partnership`, and
     `Consulting Project` for `Follow Recruiter` (a recruiter-mediated
     placement is priced the same as a direct consulting engagement
     until told otherwise).
   - Take that type's day rate and multiply by its `typicalDays` range
     to produce a low-high estimate.
   - Adjust by `scores.timeRequired` (already 0-10, inverted — 10 means
     least effort): below 4 scales the estimate up 15% (this will run
     long), above 7 scales it down 10% (this converts fast).
   - `Grant`, `Product Idea` and `Licensing` types have no day rate in
     the card — the engine returns the card's own note instead of a
     number for these, since none of them price by day.

Every rate-card-derived figure carries `basis: "rate-card-estimate"`
and the line "Confirm before sending — this is a starting-point
estimate, not a quoted price." A figure taken directly from
`pipeline.json` carries `basis: "revenue-hunter-pipeline"` and no such
warning, since a human or Revenue Hunter's own model already stood
behind it.

## Proposal Confidence Score

Four inputs, each already 0-10, weighted and summed exactly like every
other AOS scoring model, then multiplied by 10 for a score out of 100:

| Input | Weight | What it measures |
|---|---|---|
| `probabilityOfWinning` (from the opportunity's own scores) | 30% | Demand Intelligence's own read on how likely this is to convert |
| `priorityScore / 10` | 30% | The opportunity's overall fit, already computed |
| Data completeness | 25% | How many of five real-world facts are known: organisation, description, a domain tag, a contact/recruiter on record in the CRM, and a real (non-estimated) revenue figure. Each present fact is worth 2 points, 0-10 total. |
| Scoped-engagement bonus | 15% | 10 if `scopedEngagement` is true (a defined ask), 4 if not (a general lead) |

```
confidence = round(
    (probabilityOfWinning * 0.30)
  + (priorityScore / 10   * 0.30)
  + (dataCompleteness     * 0.25)
  + (scopedBonus          * 0.15)
) * 10
```

### Worked Example

A LinkedIn recruiter opens a fractional AI Governance advisory role,
already scoped to three months. Demand Intelligence scored it
`priorityScore: 82` (`probabilityOfWinning: 8`). The company is on
record in the CRM with a named recruiter, and Revenue Hunter has
already estimated `AED 45,000` in `pipeline.json`. All five data-
completeness facts are present (organisation, description, domain tag,
recruiter on record, real revenue figure) → `dataCompleteness: 10`.
`scopedEngagement: true` → `scopedBonus: 10`.

```
(8 x 0.30) + (8.2 x 0.30) + (10 x 0.25) + (10 x 0.15)
= 2.4 + 2.46 + 2.5 + 1.5 = 8.86 -> 89/100
```

## Status (the only thing CEO Advisor receives)

- **`Needs Review`** — always, whenever `autoScored` is true (the
  opportunity's scores are Collection Engine heuristics no human has
  verified yet), regardless of the confidence number. Also whenever
  confidence is below 50.
- **`Proposal Ready`** — confidence 50-74, or confidence 75+ but
  `scopedEngagement` is false (a real package exists, but the ask
  itself is still vague enough to warrant a look before it's treated as
  send-ready).
- **`Ready To Send`** — confidence 75+, `scopedEngagement` true, and
  `autoScored` false.

The worked example above (89, scoped, not auto-scored) is `Ready To
Send`. CEO Advisor's `decision-model.md` normalises this status
alongside its other three inputs — see that file for the exact
weighting.

## Executive Proposal Generator (Sprint 12)

`proposal_document()` above is the generic proposal, used whenever
`account-intelligence/`'s feed (`account-intelligence-feed.json`) has
no brief yet for the opportunity's organisation. When one exists,
`executive_proposal_document()` replaces it with a Tier-1-style
executive proposal — every fact-bearing section is a read of that
brief's own already-computed data, never a second, independent guess
at the same facts:

| Proposal section | Sourced from (Account Intelligence brief field) |
|---|---|
| Executive Summary | `executiveSummary` (already capped at 300 words there) |
| Business Context | `companyProfile` (industry, geographic footprint, approximate size, regulatory environment) and `deploymentStage` |
| Observed AI Initiatives | `aiInitiatives` |
| Likely Governance Challenges | `governanceRisks` |
| Recommended Engagement | `serviceFit` |
| Appendices | `supportingAssets` |

Deliverables, Timeline and Success Metrics are fixed, honest
boilerplate (a findings report, a roadmap, an executive briefing; a
short scoping call; that gaps get a named owner) — not claims that
require a data source, so they aren't drawn from anywhere per-brief.

**Commercial Options** are the four options every executive proposal
offers, each grounded in `rate-card.json`'s own real day-rate figures
(never a fabricated number): Discovery reuses the `Workshop` rate,
Assessment reuses `Consulting Project`, Implementation reuses
`Enterprise Contract`, and Retainer uses the new `Fractional Retainer`
entry (same day rate as `Consulting Project`, framed as an ongoing
monthly commitment instead of a fixed-scope project).

Any missing field in the brief renders honestly ("Not specified" /
"None recorded yet" / "Not enough signal yet to assess") — nothing is
invented to fill a section the brief hasn't populated.

**Read timing.** Account Intelligence's feed is read read-only and
optionally — Sales Director runs *before* Account Intelligence in the
Orchestrator's fixed order (see `orchestrator-config.json`), so this
read is one cycle behind (today's brief, if any, reflects yesterday's
run). This is the same accepted limitation as CRM's read of Sales
Director's own `processed-index.json` (see `crm-runtime-notes.md`),
not a `dependsOn` edge — Account Intelligence itself optionally reads
Sales Director's feed too, so a hard dependency either way would create
a circular ordering requirement.

## What This Engine Does Not Do

- Does not send anything. `channelOutreach` fields that don't fit the
  opportunity (a recruiter-outreach draft for a direct Greenhouse
  posting, or a client-outreach draft for a pure recruiter channel with
  no direct contact) are generated as an explicit "Not applicable" note,
  not omitted, so every package always has all seven fields the founder
  asked for — but nothing is fabricated to fill a field that doesn't
  apply.
- Does not re-score the opportunity. `priorityScore`, `probabilityOfWinning`
  and `classification` are read from `opportunity-schema.json` as-is.
- Does not touch `04-Sales-Director`'s existing relationship/follow-up
  workflow (`follow-up-priority-model.md`, `outreach-draft-template.md`).
  That cadence continues to run on `06-CRM/company-intelligence.json`
  exactly as before; this engine only prepares the first proposal
  package for a newly classified opportunity.
