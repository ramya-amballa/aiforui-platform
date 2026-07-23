# Revenue Hunter — Decision Tree

Applied to every pipeline item, after it has a score from
`lead-scoring.md`.

```
1. Is the item scored Priority (80-100)?
   YES -> 2. Can it be advanced in under one hour of effort today?
            YES -> Action now. Hand to Sales Director / CEO Advisor today.
            NO  -> Schedule the next step this week. Assign an owner and a date.
   NO  -> 3. Is the item scored Active (50-79)?
            YES -> 4. Has it been touched in the last 7 days?
                     YES -> Leave it, next scheduled touch stands.
                     NO  -> Flag for Sales Director follow-up this week.
            NO  -> 5. Is the item scored below 50 (Deferred)?
                     YES -> 6. Has anything changed since it was last scored?
                              YES -> Re-score using lead-scoring.md.
                              NO  -> Leave in the pipeline as Deferred. No action.
```

## Stage Definitions

Every item in `pipeline.json` also carries a `stage`, independent of
its score:

| Stage | Meaning |
|---|---|
| `identified` | Logged, not yet scored or actioned |
| `qualified` | Scored, decision made on priority |
| `in-progress` | Actively being pursued (proposal sent, call scheduled, negotiation underway) |
| `won` | Closed, revenue realised or contracted |
| `lost` | Did not convert |
| `deferred` | Scored below 50, parked, not abandoned |

## Escalation Rule

Any item that moves from Priority to `in-progress` and then sits
without a status change for more than 5 business days is escalated to
`09-CEO-Advisor` as an at-risk item, regardless of its current score.
A warm deal that stalls is a founder-level problem, not a
prioritisation problem.
