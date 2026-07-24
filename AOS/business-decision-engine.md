# Business Decision Engine

Whenever a new signal arrives, anywhere in the business, this is what
decides what happens to it. The output is not always a single action —
a strong recruiter lead should be added to the CRM, proposed to, and
followed up on all at once — so this engine runs as **one
classification step, then a set of independently-triggered actions**,
not a single branch.

## Step 1: Classify the Signal

Every incoming signal is one of five shapes before anything else
happens:

| Shape | Example | Goes to |
|---|---|---|
| Direct revenue opportunity | Recruiter message, RFP, referral, inbound inquiry | Step 2 (score it) |
| Recurring pattern, not a single deal | Same client question asked 3 times, a repeated LinkedIn theme | `03-Product-Manager` or `02-Content-Director` — skip Step 2 |
| Regulatory/standards development | New EU AI Act guidance, DORA update | `05-Market-Intelligence`'s trigger rule — skip Step 2 |
| Existing relationship activity | A past client reaches out, a warm contact replies | `04-Sales-Director` directly — skip Step 2, go to Step 4 |
| Unsolicited/cold, no prior context | A cold LinkedIn connection request, a generic mailer | Low-priority path — Step 2 with a fit-score cap (see Notes) |

Only the first (and the capped cold-inbound) shape needs the
confidence-scored decision tree below. The others already have a
defined home in an existing employee's trigger rule.

## Step 2: Score Fit and Confidence

Direct revenue opportunities are scored using
`opportunity-hunter/opportunity-scoring-engine.md` (0-100, eleven
weighted dimensions). That score **is** this engine's confidence
measure — it already answers "how confident are we this is worth
pursuing."

## Step 3: The Decision Tree

```
                    New direct-revenue signal
                              │
                  Score via opportunity-scoring-engine.md
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   Score < 30            Score 30-49           Score 50-79           Score 80-100
   (no real fit)        (weak signal)          (Active band)        (Priority band)
        │                     │                     │                     │
        ▼                     ▼                     ▼                     ▼
     IGNORE              ADD TO CRM             ADD TO CRM            ADD TO CRM
  (log, archived,      (log, monitor,        SCHEDULE FOLLOW-UP    CREATE PROPOSAL
   no other action)     no other action        + CONTACT           + CONTACT
                         unless it recurs)      RECRUITER            RECRUITER
                                                (if sourced via      (if applicable)
                                                 one)                      │
                                                                    APPLY (if it's
                                                                    a role/tender
                                                                    with a formal
                                                                    application step)
```

## Step 4: Orthogonal Triggers (Can Fire Regardless of Score)

These don't depend on the fit score above — they depend on a different
question entirely, and can stack on top of any branch in Step 3:

| Trigger condition | Action | Confidence threshold |
|---|---|---|
| This is the 3rd+ occurrence of a similar signal (client question, market gap, content theme) | **Build a product** → hand to `03-Product-Manager` | No score threshold — recurrence count is the signal (see `product-evaluation-framework.md` Step 1) |
| This signal is publishable insight (a regulatory change, a pattern worth writing about) | **Write content** → hand to `02-Content-Director` | No score threshold — content decisions use the five-objectives test in `content-conversion-map.md`, not a fit score |
| The organisation already has a CRM record with `relationshipTemperature` of hot or warm | **Schedule follow-up** → hand to `04-Sales-Director` | Always fires — an existing warm relationship is followed up on regardless of the new signal's own score |
| The organisation has no CRM record yet | **Add to CRM** | Always fires for any signal tied to a named organisation |

## Confidence Thresholds Summary

| Confidence (fit score) | Meaning | Minimum action | Maximum action set |
|---|---|---|---|
| 0-29 | Not a real fit | Log only | Ignore |
| 30-49 | Weak, unproven | Log and monitor | Add to CRM |
| 50-79 | Active, real potential | Log and pursue this week | Add to CRM, Schedule follow-up, Contact recruiter |
| 80-100 | Priority, pursue now | Same-day response | Add to CRM, Create proposal, Contact recruiter, Apply |

## Notes

- **Cold/unsolicited signals are capped at 49** regardless of what
  they claim, until a real signal (a reply, a specific ask, a warm
  introduction) raises them — this prevents generic outreach from
  ever auto-routing to "Create proposal."
- **Actions are additive, not exclusive.** The tree in Step 3 shows the
  typical path for a single opportunity; Step 4's triggers can add
  "Build a product" or "Write content" on top of any of them
  simultaneously if the recurrence or publishability condition is
  independently true.
- **Ignore is a real, final decision**, not a default. Everything
  below 30 is still logged (in `opportunity-schema.json`, archived) so
  it can be re-scored if new information arrives — nothing is silently
  discarded, per `opportunity-hunter/README.md`.
- This engine's output feeds directly into
  `daily-operating-workflow.md`'s 06:15 (Opportunity Hunter) and 06:45
  (Product Manager) steps — it is the logic those steps actually run,
  spelled out on its own because it's shared logic, not one employee's
  private rule.
