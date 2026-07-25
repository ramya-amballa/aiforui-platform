# CEO Advisor Runtime — Sources, Reuse, and What Changed

`runtime/generate.py` is CEO Advisor's first executable runtime.
Before Sprint 5, `09-CEO-Advisor/decision-model.md`'s normalisation/
urgency/tie-break logic had no dedicated script — it ran, partially,
as one section of `executive-dashboard/runtime/generate.py` (Daily
Brief's own generator), which still produces its own lightweight
"Today's Priorities" section exactly as before, unchanged by this
build. This runtime is a separate, considerably more comprehensive
analysis — Executive Summary, ranked Top 3 Priorities with explicit
outranking reasons, Revenue Impact, Strategic Alerts, an Ignore List,
and a Weekly Strategic Recommendation — reusing decision-model.md's
actual normalisation values via config, not reinventing them, and
never re-scoring anything another employee already scored.

## The Architectural Correction This Sprint Required

`09-CEO-Advisor/operating-manual.md` previously said, as its Daily
Workflow's last step, "Pass it to `07-Daily-Brief` as the lead item" —
CEO Advisor feeding Daily Brief. Sprint 5 explicitly instructs the
opposite: **"CEO Advisor must become the final step of every AOS
execution cycle,"** with Daily Brief itself listed as one of CEO
Advisor's own inputs. Implementing this literally required swapping
Daily Brief's and CEO Advisor's positions in the Orchestrator's fixed
sequence — Daily Brief now runs second-to-last, CEO Advisor genuinely
last. `operating-manual.md` and `orchestrator/execution-plan.md` /
`dependency-map.md` were updated to describe the new order; see those
files rather than duplicating the reasoning here.

This does **not** create duplicated logic between Daily Brief and CEO
Advisor: Daily Brief's own "Today's Priorities" section is a distinct,
lighter-weight, at-a-glance feature that predates this sprint and
isn't touched by it; CEO Advisor's runtime is a separate, later,
deeper pass over the same underlying data, producing a different
artefact (the CEO Daily/Weekly/Monthly reports) for a different
purpose (comprehensive daily business review, not a dashboard
headline).

## Sources Consumed (All Read-Only) — Exactly Sprint 5's Eight

The sprint names eight input sources explicitly; this runtime reads
exactly those eight, no more (`decision-model.md`'s own normalisation
table additionally documents Product Manager and Content Director rows
from an earlier, broader draft of the model — those remain valid
documentation for a future extension, but are deliberately out of this
runtime's read scope, since Sprint 5 didn't name them):

| Source | File(s) | What's read |
|---|---|---|
| Opportunity Hunter | `opportunity-hunter/opportunity-schema.json` | Priority-band opportunities as candidates; every opportunity's `domainTags`/`dateFound`/`classification`/`sourceCategory` for Strategic Alerts; Archived-band opportunities for the Ignore List |
| Market Intelligence | `05-Market-Intelligence/runtime/output/ceo-advisor-feed.json` | The six booleans only, per `decision-model.md` — the underlying `regulatory-log.json` entry is never opened |
| CRM | `06-CRM/company-intelligence.json` | Every company record, via `crm_follow_up_status()` (reused verbatim, see below) for candidates and the Ignore List's stale-cold check |
| Revenue Hunter | `08-Revenue-Hunter/pipeline.json` | Priority-band pipeline items as candidates; every open item for Revenue Impact |
| Service Mapping Engine | `service-mapping/service-recommendations.json` | Enrichment only — attaches a recommended service/template to a candidate that already has an `opportunityId`, never an independent candidate source of its own |
| Sales Director | `sales-director/runtime/output/ceo-advisor-feed.json` | `status` only, per `decision-model.md` — the underlying package is never opened |
| Website Intake | `website-intake/runtime/output/ceo-advisor-feed.json`, `website-intake/leads.json` | The feed's `urgency` only for candidates (per `decision-model.md`); `leads.json`'s `dateReceived` for the website-silence Strategic Alert only — no other lead field is read |
| Daily Brief | `executive-dashboard/executive-dashboard.md` | Its own `## Daily Summary` paragraph, quoted verbatim into the Executive Summary — the same "quote, never recompute" convention `orchestrator.py` itself already uses for the Daily Execution Report's Business Impact section |

`orchestrator/status.json`'s `failures` list is also read (not one of
the eight named sources, but already an established CEO Advisor input
per `operating-manual.md` predating this sprint) — any failure is
always treated as urgent, since a broken daily run is itself a
same-day priority independent of any single opportunity's value.

## Reused, Not Reinvented

- **`parse_currency`/`format_amount`** — copied verbatim from
  `executive-dashboard/runtime/generate.py` (already reused by
  `revenue-hunter/`, `crm/`, `service-mapping/`), so a pipeline figure
  parses the same way everywhere it's read in AOS.
- **`crm_follow_up_status()`** — copied verbatim from the same file,
  so CEO Advisor's hot/warm/overdue candidate scoring matches CRM's
  and Daily Brief's own categorisation exactly, never a second opinion
  about the same relationship.
- **decision-model.md's normalisation values** — every native-scale
  conversion (Sales Director's status values, Market Intelligence's
  six-check priority order, CRM's temperature/overdue combinations) is
  the same table already documented and already partially implemented
  in `executive-dashboard/runtime/generate.py`'s `ceo_advisor_candidates()`
  — moved into config (`runtime/config/ceo-advisor-config.json`), not
  redecided.

## What's Genuinely New

- **Top 3 with explicit outranking reasons** — `decision-model.md`
  always selected one winner plus unranked runners-up; this runtime
  produces a fully ranked top 3, each entry stating exactly which
  score it beat and by how much.
- **A corrected effort tie-break** — `decision-model.md`'s Step 3 reads
  as a two-candidate comparison ("if two candidates land within 10% of
  each other, the lower-effort one wins"). An early implementation of
  this runtime applied that check as a full bubble-sort pass down the
  entire ranked list, which a fixture test caught doing something
  wrong: a chain of narrow, unrelated adjacent ties let a
  meaningfully-lower-scored candidate end up ranked above a
  meaningfully-higher-scored one it was never actually competing
  against. The fix restricts the tie-break to the top pick versus its
  immediate challenger only — every other position stays in strict,
  unambiguous score order. See
  `runtime/tests/test_ceo_advisor.py`'s `RankingTests` for the
  regression coverage.
- **Revenue Impact** — revenue at risk (open pipeline value at
  organisations CRM's own `crm_follow_up_status()` already flags as
  cooling/going cold), revenue winnable today (open items due today or
  overdue in an active stage), and the highest-ROI opportunity
  (`amount x probability/10 x effort/10`, the same ROI heuristic
  `executive-dashboard`'s own "Highest ROI Opportunity" section
  already uses) — genuinely new synthesis, but built entirely from
  numbers Revenue Hunter and CRM already computed.
- **Strategic Alerts** — real trend detection using only fields every
  record already carries (`dateFound`, `dateReceived`, `domainTags`,
  `classification`, `sourceCategory`), comparing a trailing window
  against the window before it. No alert fires without a real,
  computed threshold crossing; "Website traffic but no enquiries" was
  deliberately narrowed to "no website enquiries received" — AOS has
  no analytics/traffic signal of any kind, and reporting on "traffic"
  would mean inventing a number that doesn't exist.
- **Ignore List** — Archived-band opportunities, stale-cold CRM
  relationships past the 90-day review window (the same threshold
  `crm/crm-runtime-notes.md` already documents), and Needs-Review Sales
  Director packages — every entry cites its source file.
- **Weekly Strategic Recommendation** — one recommendation per run,
  chosen from whichever real Strategic Alert is present (a fixed
  priority order among alert types when more than one fires), never a
  canned suggestion independent of the data. The same function
  produces the Daily Report's "Weekly Strategic Recommendation"
  section (computed over the rolling 7-day window) and the Weekly/
  Monthly reports' own "Strategic Recommendation" section (computed
  over their own windows) — a `period_label` parameter keeps the
  phrasing honest about which window actually produced it.

## Why the Weekly and Monthly Reports Are Rolling, Not Calendar-Gated

The Orchestrator runs once a day. Gating "produce the Weekly Report"
to a specific day of the week (or the Monthly Report to the 1st)
would mean six days out of seven the file is stale, and would add
date-arithmetic edge cases (which weekday, which timezone, month
boundaries) for no real benefit. Instead, both reports are regenerated
every run over a rolling window (7 and 30 days respectively) — always
current, never stale, and simpler to reason about. This is a
documented design decision, not a literal reading of "weekly"/
"monthly" as a fixed calendar cadence.

## What This Runtime Does Not Do

- Does not rewrite, re-score, or re-classify any other employee's
  output — every figure is read as-is and cited to its source file.
- Does not send anything. Every report is a file on disk.
- Does not read Product Manager's or Content Director's files (see
  above) — a future sprint extending CEO Advisor's scope to them is a
  config/code addition, not a redesign of this runtime.
- Does not gate the Weekly/Monthly reports to a calendar cadence — see
  above.
