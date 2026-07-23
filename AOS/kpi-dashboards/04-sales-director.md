# KPI Dashboard — Sales Director

## Inputs

`06-CRM/company-intelligence.json` (`relationshipTemperature`,
`nextFollowUpDue`, `lastTouch`, `outreachHistory`), stage context from
Revenue Hunter.

## Outputs

Outreach drafts, a prioritised daily follow-up queue, updates to
`relationshipTemperature`, `nextFollowUpDue` and `outreachHistory` in
the CRM.

## Success Metrics

- Zero `hot` or `warm` records past their `nextFollowUpDue` at the end
  of any working day
- Median days between touches, by relationship temperature
- Follow-ups recommended vs. follow-ups actually sent
- Warm relationships converted to active engagements

## Weekly Targets

| Metric | Target |
|---|---|
| `hot`/`warm` records past due at week's end | 0 |
| Outreach drafts produced vs. sent | 90%+ sent within 2 days of draft |

## Monthly Targets

| Metric | Target |
|---|---|
| Warm-to-active conversions | 2+ |
| Escalated at-risk relationships recovered (not lost cold) | 80%+ |
| Median days between touches (hot) | Under 3 |

## Business Impact

This is the difference between a lead that was found once and a
relationship that's actually managed. Every AI employee upstream can
work perfectly and still lose the deal here if a warm relationship is
allowed to go quiet — this dashboard is the practice's single clearest
early-warning signal for lost revenue that was already within reach.
