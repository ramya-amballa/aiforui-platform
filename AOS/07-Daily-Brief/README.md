# Daily Brief

AI employee #7. Assembles the Daily Revenue Brief from every other AI
employee's daily output, so the founder gets one executive-level page
each morning rather than seven separate reports.

## Files

- `daily-revenue-brief-template.md` — the brief itself, one entry per
  day

## Inputs

| Section | Comes from |
|---|---|
| Highest priority revenue action | `09-CEO-Advisor/daily-recommendation-template.md` — CEO Advisor's daily pick is authoritative; Daily Brief surfaces it rather than re-deriving it |
| New consulting opportunities, Recruiters, Upwork opportunities, Speaking opportunities, Grants | `opportunity-hunter/daily-opportunity-report-template.md` |
| Pipeline view (by revenue type, priority items) | `08-Revenue-Hunter/revenue-dashboard-template.md` |
| Product ideas | `03-Product-Manager` |
| LinkedIn content ideas | `02-Content-Director` |
| Regulations published today | `05-Market-Intelligence/operating-manual.md` triggers |
| Existing follow-ups | `04-Sales-Director`'s follow-up queue, backed by `06-CRM/company-intelligence.json` |
