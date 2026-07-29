# Executive Memory (AOS Sprint 20)

## Objective

AOS scattered institutional memory into things that decay. CEO
Advisor's Top 3 Priorities and Strategic Alerts are recomputed fresh
every day and overwritten (`ceo-daily-report.md` is a stable
filename) — nothing tracked whether yesterday's advice repeated,
whether the founder acted on it, or how often the same pattern fires.
Delivery Intelligence's `project-closure-report.md` has a real
`## Lessons Learned` section the founder writes into by hand at the
end of every engagement — but nothing ever read it back once written.
Account Intelligence's governance risks come from a small, fixed
vocabulary (`categoryToGovernanceRisks`), so the same risk label
genuinely recurs across companies — but nothing surfaced that
recurrence. Executive Memory is the read-only aggregator that closes
these three gaps, computing nothing new.

## Relationship to `memory-system.md`

`memory-system.md` documents AOS's *operational* memory — the eight
stores (opportunities, CRM, pipeline, regulatory log, published
content, product backlog/shipped log) that keep each employee from
re-collecting a fact it already has. It does not cover *institutional*
memory — decisions, lessons, and patterns across engagements. This is
not a competing spec; `memory-system.md` should be (and has been)
extended with the three founder-maintained stores it was missing
(`relationship-profiles.json`, `touchpoint-log.json`,
`delivery-log.json`) plus this sprint's two new pieces
(`daily-priorities-log.json`, `decision-log.json`).

## The Three Sources, Read-Only

1. **CEO Advisor's own history.** `ceo-advisor/runtime/generate.py`
   gained `update_priorities_log()`, appending one compact entry per
   day (`{date, top3: [{label, organisation, source}], alertTypes}`)
   to `ceo-advisor/runtime/output/daily-priorities-log.json` —
   append-only, never deletes a past day, idempotent on a same-day
   re-run. Executive Memory counts, across that real history, which
   organisations recurred in Top 3 and which alert types fired more
   than once. It never recomputes a priority score — the counting is
   the only new thing.

2. **A real Lessons Learned Library.** For every engagement Delivery
   Intelligence has a kit for, Executive Memory reads the real
   `project-closure-report.md` file at its recorded path and extracts
   whatever text sits between `## Lessons Learned` and
   `## Recommended Next Steps`. If the file still shows the raw
   `{{LESSONS_LEARNED}}` token, the founder hasn't filled it in yet —
   that engagement contributes nothing, never a fabricated substitute.

3. **Recurring Governance Risk Patterns.** Account Intelligence's
   `governance_risk_assessment()` draws each risk's `risk` label from
   `categoryToGovernanceRisks`, a small, shared, fixed vocabulary — so
   grouping by exact string match across every brief in
   `account-intelligence-feed.json` finds genuine recurrence, not an
   approximate or invented similarity. A risk seen at only one
   organisation is not reported as recurring.

## Founder-Recorded Decisions

`executive-memory/decision-log.json` — the same founder-maintained,
read-only pattern as `relationship-profiles.json`/`touchpoint-log.json`/
`delivery-log.json`. A place to record a standalone institutional rule
or decision that isn't tied to one engagement's closure report (e.g.
"never price a fixed-scope ADGL assessment below the day-rate floor
again — the Q2 pushback taught us why"). Executive Memory reads it
read-only every run and surfaces it in the report; it never writes to
it.

## Regenerated in Full, Every Run

Like Company 360, nothing in an Executive Memory feed is founder-edited
by this engine — it's entirely re-derived from other employees' own
persisted output plus the founder's own decision log, so a re-run
simply reflects the latest state of every source.

## Ordering

Executive Memory cannot have a same-run `dependsOn` edge on CEO
Advisor: CEO Advisor's own `dependsOn` lists every other employee to
guarantee it runs genuinely last, so nothing can depend on it without
breaking that. Executive Memory instead reads
`daily-priorities-log.json` one cycle behind — the identical accepted-
lag pattern Delivery Intelligence already uses for Account
Intelligence's own feed.

## Dashboard

**Executive Memory** page: recurring priorities and alert types (with
day counts), the Lessons Learned Library (one expandable section per
organisation), recurring governance risk patterns, and the founder's
recorded decisions.

## What This Engine Does Not Do

- Does not compute a new priority score, risk score, or health metric.
  Every count is a literal tally over real, already-persisted history.
- Does not fabricate a Lessons Learned entry for an engagement the
  founder hasn't written one for yet.
- Does not treat a risk seen at only one organisation as a pattern.
- Does not write to any of its four sources. `decision-log.json` is
  founder-maintained; everything else is another employee's own
  output.
