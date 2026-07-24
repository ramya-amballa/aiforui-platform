# CEO Advisor — Decision Model

CEO Advisor does not re-score opportunities from scratch. Each
employee already scores its own domain (`opportunity-hunter`,
`08-Revenue-Hunter`, `03-Product-Manager`, `04-Sales-Director`'s
follow-up priority). CEO Advisor's job is to compare across those
different scales and pick one winner, using urgency as the deciding
layer none of the individual models weigh on their own.

## Step 1: Normalise

Convert each candidate's native score to a 0-10 value score:

| Source | Native scale | Normalisation |
|---|---|---|
| `08-Revenue-Hunter/pipeline.json` | 0-100 | divide by 10 |
| `opportunity-hunter/opportunity-schema.json` (`priorityScore`) | 0-100 | divide by 10 |
| `03-Product-Manager/product-backlog.json` | 0-40 | divide by 4 |
| `04-Sales-Director` follow-up queue | Hot/Warm/Cooling + overdue | Hot+overdue = 9, Hot = 7, Warm+overdue = 6, Warm = 4 |

## Step 2: Apply the Urgency Overlay

Value alone doesn't decide the day. A large opportunity with no
deadline can wait a day; a smaller one that closes in 48 hours can't.
Multiply the normalised value by an urgency factor:

| Time-to-close or deadline | Urgency factor |
|---|---|
| Closes or expires within 48 hours | 1.5x |
| Due this week | 1.2x |
| Due this month | 1.0x |
| No deadline / evergreen | 0.8x |

## Step 3: Effort as Tie-Breaker

If two candidates land within 10% of each other after the urgency
overlay, the lower-effort one wins — CEO Advisor optimises for what
Ramya can actually finish today, not just what's biggest.

## Step 4: Select

- **Highest-value action**: the single top result
- **Runners-up**: the next 2-3, shown but explicitly not co-priorities
- Anything escalated by `04-Sales-Director` as at-risk (see
  `04-Sales-Director/follow-up-priority-model.md`) is always at least a
  runner-up, regardless of its raw value score — a relationship going
  cold is itself an urgency signal.

## Worked Example

A recruiter re-opens a conversation about a role that would convert to
a ₹18L contract. `08-Revenue-Hunter/lead-scoring.md` already scored
this item at 83/100 (Priority band) using its own worked example.
Normalised: 83 / 10 = 8.3. The recruiter has said the client wants to
close within 48 hours, so the urgency factor is 1.5x: 8.3 x 1.5 =
12.45. Even capped for comparison, this outranks same-day candidates
with no deadline, because effort is minutes and the window is nearly
closed.

**Today's highest-value action**
Reply to IBM recruiter.
**Estimated value:** ₹18L contract.
**Estimated effort:** 15 minutes.
**Reason:** Highest probability and closes in 48 hours.

This is the exact form `daily-recommendation-template.md` produces
every morning.
