# Follow-Up Priority Model

Decides which relationships need attention today, using three fields
from each `06-CRM/company-intelligence.json` record: `lastTouch`,
`nextFollowUpDue` and `relationshipTemperature`.

## Step 1: Maximum Days Between Touches, By Temperature

| Temperature | Maximum days between touches |
|---|---|
| Hot | 3 |
| Warm | 10 |
| Cooling | 21 |
| Cold | Not tracked for daily follow-up |

`cold` records are not surfaced daily. They are reviewed monthly for
whether they should be re-approached from scratch, not chased.

## Step 2: Compute Status

For every `hot`, `warm` or `cooling` record:

- **Due today or overdue**: today's date is on or after
  `nextFollowUpDue`, or days since `lastTouch` exceeds the maximum for
  its temperature.
- **Due soon**: within 2 days of `nextFollowUpDue`.
- **On track**: neither of the above.

## Step 3: Priority Order

Within "due today or overdue," order by:

1. `relationshipTemperature` (hot before warm before cooling)
2. Days overdue (most overdue first)
3. Any linked `08-Revenue-Hunter/pipeline.json` entry with a high
   `expectedRevenue` or a `nextActionDue` in the next 7 days

## Step 4: Escalation

A `hot` record more than 3 days past its maximum tolerance, or any
record explicitly flagged `strategicValue: high` in its linked pipeline
entry, is escalated to `09-CEO-Advisor` as an at-risk item rather than
left for the ordinary daily queue.
