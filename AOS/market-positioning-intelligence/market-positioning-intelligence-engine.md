# Market Positioning Intelligence (AOS Sprint 21)

## Objective

The fifth capability from the founder's ordered list toward "operate
like an AI-native consulting firm, not just a client acquisition
platform." Before designing this, a full-codebase search confirmed:
**there is no real competitor, market-share, win/loss, or competitive-
pricing data anywhere in AOS.** Sales Director's own
`competition_level()` (Opportunity Qualification Engine, Sprint 18)
already says so honestly: *"Not tracked — AOS has no data source for
competitor activity on this opportunity."* Building a "competitive
positioning" engine on top of that would mean either inventing
competitor names and market-share numbers, or silently pretending a
gap doesn't exist — both violate the one rule every other employee in
AOS follows.

So Market Positioning Intelligence asks a narrower, fully honest
question instead: **where does AI for U&I's own service catalogue
stand relative to the real demand and regulatory signal AOS already
tracks?**

## The Three Sections, All Read-Only

### 1. Service Demand Coverage

`service-mapping/runtime/config/service-catalogue.json` defines AI for
U&I's own fixed list of 10 primary services. `service-mapping`'s own
`service-recommendations.json` already records, per real opportunity,
which of those 10 services was recommended. This section counts real
recommendations per service — reused verbatim, never a second,
independently-derived demand estimate.

A service with **zero** real recommendations isn't hidden or treated
as a failure — it's flagged plainly as *"not yet validated by any real
opportunity."* That's a genuine positioning question for the founder:
is the catalogue offering something the real market hasn't asked for
yet, or is it simply early?

### 2. Regulatory Tailwinds

`05-Market-Intelligence/regulatory-log.json` already tracks every
substantive regulatory/standards development across 13 sources (EU AI
Act, ISO 42001, NIST AI RMF, DORA, GDPR, and others). This section
counts substantive entries per source — a real, already-computed
signal of which regulatory pressure is actually generating logged
developments, reused verbatim.

### 3. Competitive Signal

States the same honest string Sales Director's `competition_level()`
already uses, plus the one real, non-fabricated data point AOS has: a
count of Revenue Hunter's own `pipeline.json` entries at
`stage == "lost"` — organisation and title only. No reason, no
competitor name, no fabricated narrative — because none of that exists
anywhere in AOS to reuse.

## Regenerated in Full, Every Run

Like Company 360 and Executive Memory, nothing here is founder-edited
— every count is re-derived from other employees' own persisted
output, so a re-run simply reflects the latest state of every source.

## Dashboard

**Market Positioning Intelligence** page: Service Demand Coverage
table, Regulatory Tailwinds table with a substantive-development
count, and a Competitive Signal section that shows the honest gap
alongside the real lost-opportunity count.

## What This Engine Does Not Do

- Does not invent a competitor name, a market-share percentage, a
  win-rate, or a competitive price benchmark. None of that data exists
  anywhere in AOS; inventing it here would be the first fabrication in
  a codebase that otherwise has none.
- Does not attach a reason or a competitor to a lost pipeline entry —
  `pipeline.json`'s own schema has no such field, so none is guessed.
- Does not re-score a service-mapping recommendation or a regulatory
  development. Every count is a literal tally over real,
  already-persisted data.
