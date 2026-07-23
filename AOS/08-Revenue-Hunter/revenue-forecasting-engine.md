# Revenue Forecasting Engine

Calculates expected monthly revenue from the unified pipeline in
`pipeline.json`, across all nine revenue types (consulting projects,
enterprise contracts, workshops, speaking engagements, paid advisory
calls, grants, partnerships, product ideas, licensing), and identifies
which single action would increase expected revenue the most.

This is Revenue Hunter's forecasting layer, not a separate employee —
it reads the same pipeline it already maintains.

## Step 1: Expected Value Per Item

Every open pipeline item's expected value is:

```
EV = expectedRevenue × (probabilityOfSuccess ÷ 10)
```

`probabilityOfSuccess` is already 0-10 in `pipeline.json`, so dividing
by 10 gives a working probability. An item at ₹10L with
`probabilityOfSuccess: 7` has an EV of ₹7L, not ₹10L — the forecast is
always probability-weighted, never face-value.

## Step 2: Monthly Bucketing

Group open items (`stage` not `won`, `lost`, or `deferred`) by
`expectedCloseDate`'s month. Sum EV per month, and separately per
revenue type within the month, so the forecast shows both a total and
a concentration read (is the month's number one large item away from
collapsing).

## Step 3: Three Scenarios Per Month

| Scenario | How it's calculated |
|---|---|
| **Committed** | Sum of `expectedRevenue` for items already `won` and closing that month — not probability-weighted, this already happened |
| **Expected** | Sum of EV (Step 1) for all open items with that `expectedCloseDate` month, plus Committed |
| **Best case** | Sum of full `expectedRevenue` (not weighted) for every `Priority`-band open item that month, plus Committed — "if everything currently likely actually closes" |

Report all three side by side. "Expected" is the number to plan
against; "Best case" and "Committed" bound how much confidence that
number deserves.

## Step 4: Highest-Leverage Actions

Not every action improves the forecast equally. For each open item,
calculate its **leverage**: how much total expected revenue would
increase if its `probabilityOfSuccess` moved up by 2 points (a
realistic result of one well-timed follow-up or proposal push):

```
Leverage = expectedRevenue × (2 ÷ 10)
```

Rank open items by leverage, not by raw deal size or by current EV.
This surfaces the item where a small, achievable probability increase
produces the largest forecast improvement — often a large,
mid-probability deal rather than the largest deal outright, and often
different from whatever `09-CEO-Advisor` picked as today's single
action (that's urgency-weighted; this is revenue-impact-weighted, and
both are worth knowing).

## Worked Example

Three open items closing next month:

| Item | Expected revenue | Probability | EV | Leverage (+2 probability) |
|---|---|---|---|---|
| A | ₹20L | 4/10 | ₹8L | ₹4L |
| B | ₹8L | 8/10 | ₹6.4L | ₹1.6L |
| C | ₹15L | 5/10 | ₹7.5L | ₹3L |

Expected monthly total: ₹21.9L. Item A has the highest leverage
(₹4L) — a mid-probability, large deal — even though Item C has a
higher current EV. Item A is the highest-leverage action this month,
not necessarily the highest-value one.

## Output

Produces `revenue-forecast-template.md`, refreshed whenever
`pipeline.json` changes materially (a new item, a stage change, or a
probability update), and reviewed monthly alongside
`kpi-dashboards/ceo-dashboard.md`.
