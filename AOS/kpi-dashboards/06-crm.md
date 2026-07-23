# KPI Dashboard — CRM

## Inputs

Every company/contact encounter reported by Opportunity Hunter, Sales
Director and Market Intelligence.

## Outputs

`company-intelligence.json` — the single, enriched record per
organisation.

## Success Metrics

- Percentage of encountered companies with a complete record (no
  missing `tailoredPositioning`, `industry`, or `aiMaturity`)
- Zero duplicate records for the same organisation
- Time from first encounter to a complete record
- Percentage of records touched (not stale) within their relationship
  temperature's tolerance window

## Weekly Targets

| Metric | Target |
|---|---|
| New encounters converted to complete records | 100% within 48 hours |
| Duplicate records found | 0 |

## Monthly Targets

| Metric | Target |
|---|---|
| Records with `tailoredPositioning` filled in | 100% of active/warm/hot records |
| Stale records reviewed (cold, 60+ days untouched) | 100% |

## Business Impact

The CRM is why the practice never starts from scratch on a company it
has already met. A gap here silently costs every other employee time
and quality — Sales Director drafts generically, Opportunity Hunter
re-qualifies from zero, Revenue Hunter under-values a relationship it
doesn't have context on.
