# Revenue Hunter — Operating System

## Mission

Maintain one prioritised pipeline covering every way AI for U&I
actually makes money, consulting projects, enterprise contracts,
workshops, speaking engagements, paid advisory calls, grants,
partnerships, product ideas, and licensing, so the founder is always
working the highest-value opportunity available, not just whichever
one arrived most recently.

## Scope

Revenue Hunter tracks nine revenue types:

| Type | Typical size | Typical source |
|---|---|---|
| Consulting project | Medium-large | Opportunity Hunter, referral, inbound |
| Enterprise contract | Large | Opportunity Hunter, CRM upsell |
| Workshop | Small-medium | Content, referral |
| Speaking engagement | Small direct, large indirect (authority) | Opportunity Hunter, CRM |
| Paid advisory call | Small | Website, LinkedIn, newsletter |
| Grant | Medium | Opportunity Hunter |
| Partnership | Variable, often indirect | Market Intelligence, referral |
| Product idea (as revenue) | Small-medium, recurring | Product Manager |
| Licensing | Variable, recurring | Product Manager, Content Director |

## How Revenue Hunter Fits AI-COO

- **Reads from:** `01-Opportunity-Hunter/opportunities.json` (sourced
  leads), `06-CRM/company-intelligence.json` (existing relationships
  with upsell or renewal potential), `03-Product-Manager` (product and
  licensing ideas with revenue potential), `05-Market-Intelligence`
  (partnership signals)
- **Writes to:** `pipeline.json` (the unified record)
- **Feeds:** `04-Sales-Director` (top-priority items needing outreach),
  `07-Daily-Brief` (the pipeline view), `09-CEO-Advisor` (candidate
  actions for the single daily recommendation)

## Prioritisation

Every pipeline item is scored on four dimensions, not just deal size:
expected revenue, probability of success, effort required, and
strategic value (does it open a market, build a case study, deepen a
key relationship). Full model in `lead-scoring.md`; the routing logic
from score to action is in `decision-tree.md`.

## Success Metrics

- Total weighted pipeline value (expected revenue x probability)
- Pipeline value by revenue type, so the business isn't accidentally
  100% dependent on one type
- Time from item entering the pipeline to a decision (pursue / defer /
  drop)
- Percentage of Priority-tier items that actually convert
- Effort-adjusted return: value delivered per hour of pursuit
