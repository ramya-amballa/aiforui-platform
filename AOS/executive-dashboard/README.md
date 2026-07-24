# AOS Executive Dashboard

The single entry point into AI for U&I every morning: one page,
generated from live data, showing revenue, today's priority, and
everything that needs attention across Opportunity Hunter, Revenue
Hunter and CRM, before any other work begins.

## What This Is (and Isn't)

This is a read-only aggregation layer, not a new AI employee and not a
new data store. It consumes exactly three existing live outputs —
`opportunity-hunter/opportunity-schema.json`,
`08-Revenue-Hunter/pipeline.json`, and
`06-CRM/company-intelligence.json` — and renders them into one page.
Nothing here is a second copy of that data; regenerating is always
safe, and the source files are the only place any of these numbers
are actually stored.

It sits alongside `07-Daily-Brief`, not in place of it. Daily Brief
still assembles the full-organisation report (content, product,
regulations, every employee). The Executive Dashboard is narrower and
revenue-facing on purpose — a fast, four-source read for the moment
before the day's work starts, matching what the founder is asking each
morning: what's the money situation, what's the one thing to do today,
and what's about to go cold.

## Files

- `executive-dashboard.md` — the dashboard itself, regenerated in
  place every run. This is the file to open every morning.
- `runtime/generate.py` — the generator. Reads the three source files,
  computes the derived views below, writes `executive-dashboard.md`
  and a dated copy to `runtime/output/`.

Run it with `python3 runtime/generate.py` from this directory (or via
GitHub Actions, once wired to a schedule).

## What It Computes, and What It Doesn't Invent

Two sections apply logic that already exists elsewhere in AOS but
previously had no executable form:

- **Today's Priorities** runs `09-CEO-Advisor/decision-model.md`
  exactly as documented: normalise every Priority-band candidate from
  Revenue Hunter and Opportunity Hunter to a 0-10 value, apply the
  urgency overlay from `nextActionDue`/`nextFollowUpDue`, break ties on
  effort, and take the top result plus up to three runners-up. Any
  Sales Director escalation (per `04-Sales-Director/follow-up-priority-model.md`)
  is always at least a runner-up, per CEO Advisor's own rule.
- **CRM section** runs `04-Sales-Director/follow-up-priority-model.md`'s
  exact max-days-between-touches table (hot 3 days, warm 10, cooling
  21) to compute due/overdue and "becoming cold."

Everything else (Revenue, Opportunity Hunter's views, Revenue Hunter's
views) is a direct read, sort or filter over fields the source files
already carry — no new judgment, no new scoring model.

## Known Limitation

`pipeline.json`'s `expectedRevenue` is a free-text amount ("AED
180,000", "Not yet estimated"), not a number, since it's meant for
human reading. The generator parses it best-effort (handles common
`L`/`Cr`/`K`/`M` suffixes and simple ranges) to compute pipeline
totals, and flags mixed currencies explicitly rather than silently
summing them as if they were the same unit. Treat the Revenue section
as directional until every pipeline item carries a currency-normalised
figure.
