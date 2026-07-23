# CEO Dashboard — AI for U&I Business Health

The single roll-up view across all nine AI employees. Where each
employee dashboard answers "is this function healthy," this dashboard
answers "is the business healthy," by combining them into six
composite reads.

## The Six Composite Reads

| Read | Rolls up | Green | Yellow | Red |
|---|---|---|---|---|
| **Top-of-Funnel Health** | Opportunity Hunter's weekly opportunities logged, Market Intelligence's consulting flags | 10+/week, growing | 5-9/week, flat | Under 5/week or falling |
| **Pipeline Health** | Revenue Hunter's total weighted pipeline value and type concentration | Growing, no type over 60% | Flat, or one type 60-80% | Falling, or one type over 80% |
| **Relationship Health** | Sales Director's overdue-record count and warm-to-active conversion | 0 overdue, converting | 1-2 overdue, some conversion | 3+ overdue or no conversions this month |
| **Authority & Demand Health** | Content Director's publish cadence and CRM record completeness | On cadence, all objectives covered | Behind cadence or one objective neglected | No publication in 2+ weeks |
| **Product Leverage Health** | Product Manager's candidates advanced and products shipped | 1+ shipped/quarter on pace | Candidates stuck at `candidate` for 2+ months | Nothing advanced in a quarter |
| **Decision Quality** | CEO Advisor's recommendations-followed rate | 80%+ followed | 50-79% | Under 50%, or missed `hot` escalations |

## Business Health Score

A simple composite for a single number to track week over week:
Green = 2, Yellow = 1, Red = 0, summed across the six reads (max 12).

- **10-12**: business is compounding — funnel, pipeline and
  relationships are all reinforcing each other
- **6-9**: functioning but with a specific gap; check which read is
  dragging the score down before assuming the whole system is off
- **0-5**: an employee's dashboard needs attention this week, not next
  month — a low score here almost always traces to one specific stuck
  read, not a general problem

## What This Dashboard Deliberately Does Not Do

It does not replace the per-employee dashboards or the Daily Brief. It
is a weekly/monthly review artefact for the founder to see the shape of
the whole business at a glance; day-to-day action still comes from
`09-CEO-Advisor/daily-recommendation-template.md` and
`07-Daily-Brief/daily-revenue-brief-template.md`.

## Review Cadence

- **Weekly**: update the six reads from that week's employee
  dashboards; note which read moved and why
- **Monthly**: recompute the Business Health Score, compare to the
  prior month, and feed any real trend (e.g. Pipeline Health green for
  3 months straight) into `revenue-forecasting-engine.md`'s
  highest-leverage action analysis
