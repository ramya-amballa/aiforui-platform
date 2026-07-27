# Reverse Job Hunt Engine (AOS Sprint 9)

Turns AOS from a reactive opportunity finder into a proactive
consulting business development system. For every organisation
already qualified by Demand Intelligence (the same population Account
Intelligence, Sprint 8, already briefs), generates a Reverse Job Hunt
Strategy — an internal business development playbook, **not** a
proposal. Additive and downstream only: no existing scoring formula
anywhere in AOS (`ingest.py`, `demand_engine.py`,
`account_intelligence_engine.py`) is touched, recomputed, or replaced.
Implemented in `runtime/reverse_job_hunt_engine.py` (the section
builders) and `runtime/generate.py` (the orchestrator-invoked entry
point); lookup tables live in
`runtime/config/reverse-job-hunt-config.json`.

## Population

Same as Account Intelligence: every key in
`demand-intelligence/organisation-profiles.json`'s `organisations`
dict. Account Intelligence's own qualification criteria (Sprint 8)
never introduced a second, narrower population — so "identified by
Demand Intelligence or Account Intelligence" is, today, the same set
either way. This engine reads Account Intelligence's own feed
(`account-intelligence-feed.json`) as an optional, read-only
cross-reference when it exists, not as a second population source.

## The Ten Sections

1. **Why This Company Should Be Pursued** — a factual clause per
   matched category (e.g. "it has a named external regulatory
   obligation on record"), combined across every category the
   organisation has matched.
2. **Estimated Consulting Potential** — prefers a real
   `pipeline.json`/`opportunity-schema.json` figure when one exists
   (same "prefer the real record" pattern Account Intelligence's own
   Opportunity Scorecard already established); falls back to an
   honest, clearly-labelled scale-based heuristic (the organisation's
   own recorded size) only when neither exists.
3. **Why AI for U&I Is Relevant** — pairs each matched category with
   the specific AI for U&I practice area/methodology that addresses
   it, distinct from Section 1's pursuit-urgency framing.
4. **Current AI Maturity** — from the organisation's single strongest
   matched category (same baseScore-descending priority every other
   downstream reader of demand-intelligence's categories already
   uses); a credited, verbatim copy of Account Intelligence's own
   `categoryAiMaturityLabel` table, so both employees describe the
   same fact identically.
5. **Current Governance Maturity** — a genuinely distinct question
   from AI maturity, new in Sprint 9 (Account Intelligence, Sprint 8,
   only asked about AI maturity): how developed is this
   organisation's AI *governance* specifically, from a new
   `categoryGovernanceMaturityLabel` table.
6. **Recommended Entry Point** — a six-value vocabulary (LinkedIn
   relationship, Warm introduction, Conference, Executive briefing,
   Discovery workshop, Fractional advisory), decided deterministically:
   an existing CRM relationship always wins (a warm path beats any
   cold one); otherwise low confidence in the underlying signal always
   means the lightest-touch option; otherwise Buying Readiness Band
   plus whether an urgent category (governance/regulatory/failure
   trigger) is present decides the rest. All six values are genuinely
   reachable — see `tests/test_reverse_job_hunt_engine.py`'s
   `EntryPointTests` (the same design-smell guard Account Intelligence's
   Outreach Strategy tests already established).
7. **Estimated Probability of Engagement** — reuses Demand
   Intelligence's own Buying Readiness Score verbatim (0-100). Both
   ask essentially the same question ("how ready is this
   organisation"), so this is a re-labelling, never a second,
   independently-computed number that could disagree with it.
8. **Recommended Timeline** — when to *start* outreach (a Buying
   Readiness Band lookup), a distinct question from Account
   Intelligence's own Estimated Sales Cycle (how long the deal takes
   to close once started) — this engine does not duplicate that field.
9. **Recommended First Touch** — one concrete, low-risk next action
   per entry point, parameterised only by the organisation's own name
   and its strongest matched category label — never a drafted sales
   pitch.
10. **Suggested Sequence of Actions Over 90 Days** — a three-phase
    (Days 1-30 / 31-60 / 61-90) plan per entry point, deliberately
    conditional in phrasing ("if engaged... if not...") since this
    engine has no response-tracking data to branch on deterministically
    — a human decides which branch applies as it unfolds.

## Expected Consulting ROI (Dashboard Sort Key)

A new, honestly-labelled heuristic this engine introduces:
`Estimated Consulting Potential (0-10) x Estimated Probability of
Engagement (0-100) / 100`, an expected-value-style estimate on a 0-10
scale. Used only to sort the dashboard's Reverse Job Hunt page and the
daily report — never fed back into or replacing any existing score
elsewhere in AOS.

## Reuse, Not Duplication

- AI maturity labels are a credited, verbatim copy of Account
  Intelligence's own table.
- Probability of Engagement is Demand Intelligence's own Buying
  Readiness Score, unchanged.
- Estimated Consulting Potential prefers a real
  `pipeline.json`/`opportunity-schema.json` record's own figure over
  a heuristic, exactly like Account Intelligence's own Opportunity
  Scorecard already does.
- Every brief cross-references Account Intelligence's own Outreach
  Strategy (when a brief exists for that organisation) purely for
  consistency-checking — this engine's own Section 6 recommendation
  is never overridden by it, since the two answer different questions
  (Account Intelligence: how to *frame* the first touch; this engine:
  which *channel* to use and what to do over 90 days).

## Sprint 16 — Client Acquisition Engine (Consolidated Here)

Per explicit instruction ("consolidate into existing"), the requested
Client Acquisition Engine is not a new standalone employee — it is
Section 11 of this engine's own strategy, since five of its eight
requested capabilities were already this engine's or Account
Intelligence's own sections:

| Requested capability | Where it comes from |
|---|---|
| Research the company / decision-makers | Account Intelligence's own Company Profile and Decision Makers sections (unchanged) |
| Recommend which asset to share first | Account Intelligence's own already-ranked Supporting Assets — the top-ranked item, never a second ranking |
| Build a 30/60/90-day engagement plan | This engine's own Section 10 (unchanged) — the campaign's plan *is* that sequence |
| Predict conversion probability | This engine's own Section 7 (unchanged) |
| Draft LinkedIn connection requests | **New.** Uses a real, founder-tracked person from `relationship-intelligence/relationship-profiles.json` when one exists for that organisation; otherwise a generic-by-title draft from Account Intelligence's decision-maker titles (never an invented name) |
| Draft follow-up messages | **New.** Ties directly to Section 10's own first 90-day-sequence step — never a second, independently-invented cadence |
| Track every touchpoint until won/closed | **New.** A founder-maintained, persistent `touchpoint-log.json` (sibling to `organisation-profiles.json`'s own pattern — exactly like `company-intelligence.json`'s `outreachHistory` is founder-maintained, never auto-collected). Read-only; this engine reports the status/touchpoints on record, never invents one |

`touchpoint-log.json` schema: `{"campaigns": {organisation: {"status":
"Open"|"Won"|"Closed", "touchpoints": [{"date", "channel", "summary"}]}}}`.
An organisation with no campaign record shows `"Not started"`,
distinct from `"Open"`, so the two states are never confused.

## What This Sprint Deliberately Does Not Do

- Does not modify `organisation-profiles.json`, `opportunity-schema.json`,
  `company-intelligence.json`, `account-intelligence-feed.json`,
  `pipeline.json`, `relationship-profiles.json`, or any other
  employee's output — every read is read-only, including of its own
  `touchpoint-log.json` (founder-maintained, this engine never writes
  to it).
- Does not touch or recompute any existing scoring formula
  (`ingest.py`'s `compute_priority_score()`, `demand_engine.py`'s
  Overall Demand Score/Buying Readiness Score, Account Intelligence's
  Opportunity Scorecard) — Expected Consulting ROI is a new,
  separately-labelled number for this engine's own dashboard sort only.
- Does not send outreach — Section 9/10/11 draft/recommend an action,
  a sequence, and message text; a human still sends anything real.
- Does not invent a consulting-potential dollar figure, a stakeholder
  name, a touchpoint, or a probability beyond what an upstream
  employee's own already-computed field, a founder-maintained record,
  or this engine's own clearly-labelled heuristic already established.
- Does not wire into CEO Advisor's own report in this sprint — it is
  listed in CEO Advisor's `dependsOn` for run-ordering only, matching
  the same pattern Product Manager, Content Director and Account
  Intelligence already use.

## Dashboard

The Command Center's new **Reverse Job Hunt** page: a "Generate
Strategies" button, a table of every qualified organisation sorted by
Expected Consulting ROI (industry, buying-readiness band, entry point,
probability of engagement, recommended timeline, last seen, and —
Sprint 16 — campaign status, touchpoint count, and the asset recommended
to share first), searchable by company, and the full eleven-section
strategy for whichever organisation is selected, with a Download
button. Reads `reverse-job-hunt-feed.json` and the individual strategy
files directly (read-only, same as every other dashboard page) — never
re-derives or duplicates the scoring above.
