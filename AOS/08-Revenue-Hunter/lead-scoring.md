# Revenue Hunter — Lead Scoring Model

Every pipeline item is scored 0-100 across four weighted dimensions.
This is a portfolio-prioritisation score, distinct from
`opportunity-hunter/opportunity-scoring-engine.md`, which qualifies whether an
individual lead is worth logging at all.

| Dimension | Weight | 0 | 10 (max) |
|---|---|---|---|
| Expected revenue | 35% | Negligible or unclear | Large, well-defined |
| Probability of success | 30% | Long shot, no signal | High confidence, strong signal (warm referral, active RFP, verbal agreement) |
| Effort required | 20% (inverted: lower effort scores higher) | Large, multi-week pursuit | Minutes to hours to advance |
| Strategic value | 15% | No spillover benefit | Opens a market, produces a case study, deepens a key relationship, or creates reusable IP |

Score each dimension 0-10, multiply by its weight, sum for a total out
of 100. Effort is inverted before weighting: a low-effort item scores
high on this dimension.

## Bands

- **80-100 — Priority**: pursue now, hand to Sales Director today
- **50-79 — Active**: pursue this week
- **Below 50 — Deferred**: log and revisit if circumstances change,
  don't drop it from the pipeline

## Worked Example

A recruiter re-opens a conversation about a role that would convert to
a ₹18L contract (Expected revenue 9/10), the recruiter has already
said the client wants to close within 48 hours (Probability 9/10),
replying takes fifteen minutes (Effort inverted: 10/10), and it is a
straightforward consulting placement with no additional strategic
spillover (Strategic value 3/10):

`(9 x 0.35) + (9 x 0.30) + (10 x 0.20) + (3 x 0.15) = 3.15 + 2.7 + 2.0 + 0.45 = 8.3 -> 83/100 -> Priority`

This is the kind of item that should reach `09-CEO-Advisor` as the
day's single highest-value action.
