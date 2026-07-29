# Capacity Management (AOS Sprint 22)

## Objective

The sixth and final capability from the founder's ordered list. AI for
U&I is one person. A full-codebase search before this employee was
designed confirmed: CEO Advisor ranks priorities and recommends
pursuing new business with zero regard for how much delivery work is
already committed — every day is treated as if the founder has
unlimited bandwidth — and no config anywhere records her own available
days per week. Capacity Management closes both gaps, honestly, using
only real, already-computed effort estimates.

## The Only Real Effort Estimate in AOS

Sales Director's own `rate-card.json` `typicalDays.{min, max}` per
engagement type is the one place AOS already estimates how many days
an engagement actually takes. Capacity Management reuses it verbatim
in both directions — never a second, independently-invented number.

### Active Engagement Load

Every Revenue Hunter `pipeline.json` entry at `stage == "won"` is a
real, active engagement. Cross-referenced against Delivery
Intelligence's own `delivery-log.json` (read-only, founder-maintained):
an engagement whose phase is `"Closed"` is done and excluded; anything
else (including `"Not started"`, when the founder hasn't logged
progress yet) is still consuming time. Each entry's real `type` field
maps directly to `rate-card.json`'s `typicalDays` for that engagement
type. A type with no `typicalDays` (Grant, Partnership, Product Idea,
Licensing) is reported as honestly unestimated, never guessed.

### Incoming Pipeline Load

Every Sales Director package at status `"Ready To Send"` or
`"Proposal Ready"` (from `sales-director/runtime/output/ceo-advisor-feed.json`)
represents potential incoming work. Each opportunity's real
`recommendedEngagementType` from Service Mapping's own
`service-recommendations.json` maps to the same rate-card lookup. An
opportunity with no service-mapping recommendation yet (or one marked
`notApplicable`) is honestly unestimated, never guessed.

## The One Number AOS Cannot Observe: Available Capacity

There is no way for AOS to automatically know how many days per week
the founder actually has available — this has to come from her. Unlike
`delivery-log.json`/`decision-log.json` (founder-maintained *logs*,
empty until populated), `capacity-management/runtime/config/capacity-config.json`
is a founder-*tunable config*, the same pattern as `rate-card.json`
itself: it ships with a clearly labelled starting assumption
(`foundersAvailableDaysPerWeek: 4` — roughly one day/week reserved for
business development, admin and AOS review out of a five-day week),
which the founder edits directly to reflect her real bandwidth. No
code change is needed to retune it.

Total committed days (active + incoming) divided by
`foundersAvailableDaysPerWeek` gives **weeks of committed work at your
available pace** — banded by the same config's
`weeksOfCommittedWorkThresholds` into:

- **Available Capacity** — below the near-capacity threshold
- **Near Capacity** — at or above it
- **Over Capacity** — at or above the over-capacity threshold

Zero committed work with a real config value is genuinely "Available
Capacity" — not "no signal." "Not enough signal yet" is reserved for
when the ratio can't be computed at all (e.g.
`foundersAvailableDaysPerWeek` is unset or zero).

## Advisory Only

Capacity Status never blocks a proposal from being prepared, never
changes a Sales Director package's status, and never re-ranks CEO
Advisor's Top 3. It is read-only, informational context for a founder
deciding whether to pursue more work right now.

## CEO Advisor Integration

`ceo-advisor/runtime/generate.py` gained
`render_capacity_status_section()`, reading
`capacity-management/runtime/output/capacity-feed.json` read-only and
surfacing it as its own section in the daily report — one cycle
behind, the same accepted-lag pattern Executive Memory already uses
for CEO Advisor's own `daily-priorities-log.json` (Capacity Management
necessarily runs before CEO Advisor in the fixed orchestrator order to
keep CEO Advisor genuinely last). Purely informational: it never
changes candidate ranking or Top 3 selection.

## Regenerated in Full, Every Run

Like Company 360, Executive Memory and Market Positioning
Intelligence, nothing in a capacity feed is founder-edited by this
engine — every count is re-derived from other employees' own persisted
output, so a re-run simply reflects the latest state of every source.
`capacity-config.json` itself is edited by the founder directly, never
by this script.

## Dashboard

**Capacity Management** page: a colour-coded Capacity Status header,
weeks-of-committed-work metric, and side-by-side Active Engagements /
Incoming Pipeline tables with per-item effort estimates.

## What This Engine Does Not Do

- Does not invent an effort estimate for an engagement type the rate
  card has no `typicalDays` for, or an opportunity with no
  service-mapping recommendation yet.
- Does not observe or guess the founder's own available bandwidth —
  that number is founder-supplied, in `capacity-config.json`, exactly
  like her own day rates in `rate-card.json`.
- Does not block, gate, or re-rank anything. Every other employee's
  behaviour is entirely unaffected by this employee's status.
