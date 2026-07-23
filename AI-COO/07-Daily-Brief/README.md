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
| New consulting opportunities, Recruiters, Upwork opportunities, Speaking opportunities, Grants | `01-Opportunity-Hunter/daily-report-template.md` |
| Product ideas | `03-Product-Factory` |
| LinkedIn content ideas | `02-Content-Engine` |
| Regulations published today | `05-Market-Intelligence/operating-manual.md` triggers |
| Existing follow-ups | `06-CRM/company-intelligence.json` |
| Highest priority revenue action | Daily Brief's own synthesis across every section above |
