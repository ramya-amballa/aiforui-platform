# CEO Advisor — Decision Engine Runtime (v1.0)

The executable half of CEO Advisor: `09-CEO-Advisor/` remains the
specification (mission, the decision model, the daily recommendation
format) — `ceo-advisor/` is where it runs, the same split as Sales
Director (`04-Sales-Director` + `sales-director/`), Revenue Hunter,
CRM, and Product Manager.

Every morning, after every other AOS employee has run, CEO Advisor
reads what each of them produced and answers: what should Ramya do
today, what's the revenue picture, what deserves attention this week,
and what's explicitly not worth the time.

## Files

- `ceo-advisor-runtime-notes.md` — exactly which source answers which
  question, what's reused from `executive-dashboard`/`crm` versus
  genuinely new here, a real bug this build's own testing caught and
  fixed in the effort tie-break logic, and why the Weekly/Monthly
  reports are rolling windows rather than calendar-gated
- `runtime/` — the reports, generated as code

## How It Fits AOS

- **Reads from** (all read-only): Opportunity Hunter, Market
  Intelligence, CRM, Revenue Hunter, Service Mapping Engine, Sales
  Director, Website Intake, Daily Brief, and `orchestrator/status.json`
- **Writes to:** `runtime/output/`, `runtime/logs/` only
- **Generates:** CEO Daily Report (Executive Summary, ranked Top 3
  Priorities with outranking reasons, Revenue Impact, Strategic
  Alerts, Ignore List, Weekly Strategic Recommendation), CEO Weekly
  Report, and CEO Monthly Business Review — the latter two rolling
  7-day/30-day windows, regenerated every run
- **Runs last** — the final step of every Orchestrator sequence, per
  Sprint 5's explicit instruction. See `ceo-advisor-runtime-notes.md`
  for why this required swapping Daily Brief's and CEO Advisor's
  positions in the fixed order, and why that doesn't duplicate Daily
  Brief's own, separate, unchanged "Today's Priorities" section.

## What This Is Not

Not a second scoring or classification engine — every number is read
from the employee that already computed it and cited to its source
file, never recomputed. Not an outreach or content tool — nothing here
drafts or sends anything; every report is a file on disk for the
founder to read. Not a redesign of any other employee — Opportunity
Hunter, Revenue Hunter, CRM, Sales Director, Market Intelligence,
Website Intake, Service Mapping, and Daily Brief are all read exactly
as they already exist.

Start with `09-CEO-Advisor/operating-manual.md`, then
`ceo-advisor-runtime-notes.md`.
