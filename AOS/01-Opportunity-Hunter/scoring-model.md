# Opportunity Scoring Model

Every opportunity in `opportunities.json` is scored 0-100 across six
weighted dimensions.

| Dimension | Weight | 0 | 10 (max) |
|---|---|---|---|
| Practice fit | 25% | Unrelated to AI governance, tech risk, GRC or TPRM | Squarely in-practice |
| Deal size / fee potential | 20% | Negligible or unclear | Meaningful engagement or day-rate |
| Urgency / decision timeline | 15% | No timeline, exploratory only | Active, near-term decision |
| Relationship warmth | 15% | Cold, no prior contact | Warm referral or existing relationship |
| Sector fit | 15% | Unregulated, low-assurance | Regulated / high-assurance (finance, government, critical infrastructure, healthcare, pharma) |
| Likelihood of close | 10% | Long shot | High probability |

Score each dimension 0-10, multiply by its weight, sum for a total out
of 100.

## Bands

- **80-100 — Priority**: respond same day, draft proposal immediately
- **50-79 — Active**: respond within 48 hours, log and monitor
- **Below 50 — Archived**: log for the record, no action unless
  circumstances change (e.g. a referral warms it up later)

## Notes

- Re-score an archived opportunity if new information arrives, don't
  just leave the original score standing.
- A high-urgency, high-fit opportunity with a small deal size can
  still land in Priority. Don't let deal size dominate the score.
