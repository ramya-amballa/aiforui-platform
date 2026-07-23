# Long-Term Memory System

Every interaction AOS has with a recruiter, a consulting firm, a
client, a product, a piece of published content, a regulation, or an
opportunity is retained as organisational knowledge — not just for the
day it happened, but as a permanent record any employee can query
before acting. The goal: no AI employee, and no future version of
Ramya, ever starts from scratch on something the business has already
learned.

This is not a new employee. It is the set of memory stores every
employee already reads and writes, described together in one place so
the retrieval rules are explicit rather than implicit in each
employee's own file.

## The Memory Stores

| Store | File | Retains | Owner (writes) |
|---|---|---|---|
| Opportunities | `01-Opportunity-Hunter/opportunities.json` | Every opportunity ever logged, including archived ones — never deleted | Opportunity Hunter |
| Companies (log) | `01-Opportunity-Hunter/companies.md` | A lightweight, human-readable pointer log; links to the CRM record | Opportunity Hunter |
| Company Intelligence | `06-CRM/company-intelligence.json` | The single enriched record per organisation: industry, AI maturity, regulations, relationship, recruiter, prior applications, positioning, relationship temperature, full outreach history | Opportunity Hunter, Sales Director, Market Intelligence |
| Revenue Pipeline | `08-Revenue-Hunter/pipeline.json` | Every revenue-shaped item across all nine types, at every stage, including won/lost/deferred | Revenue Hunter |
| Regulatory Log | `05-Market-Intelligence/regulatory-log.json` | Every substantive regulatory/standards/security development ever logged, and its triggered actions | Market Intelligence |
| Published Content | `02-Content-Director/published-content-log.json` | Every piece of content actually published, its objective, its trigger, and its measured result | Content Director |
| Product Backlog | `03-Product-Manager/product-backlog.json` | Every product candidate ever evaluated, at any score, including parked ones | Product Manager |
| Shipped Products | `03-Product-Manager/shipped-products-log.json` | Every product actually shipped, the signal that justified it, and its result since | Product Manager |

## Retention Principle

Nothing is ever deleted. An opportunity that scores low is `archived`,
not removed. A product candidate that scores low is `parked`, not
discarded. A cold CRM relationship stays on record. Status fields
(`band`, `stage`, `status`, `relationshipTemperature`) carry the
current state; the record itself is permanent. This is what makes
re-scoring possible when circumstances change, and it's what stops the
same dead-end being re-explored from zero a year later.

## Retrieval Rules — What Each Employee Must Check Before Acting

| Before this employee... | ...it must check | Why |
|---|---|---|
| Opportunity Hunter scores a new lead | `06-CRM/company-intelligence.json` for the organisation | Existing relationship context changes the score (relationship warmth is a scoring dimension) and prevents re-collecting facts already on file |
| Content Director briefs a piece | `02-Content-Director/published-content-log.json` | Don't repeat a trigger already covered from the same angle; do build on what worked |
| Product Manager evaluates a signal | `03-Product-Manager/product-backlog.json` and `shipped-products-log.json` | The same signal may already be a parked candidate (revisit rather than re-evaluate from zero) or already shipped (this is a demand-for-more-of-it signal, not a new product idea) |
| Sales Director drafts outreach | `06-CRM/company-intelligence.json`'s `outreachHistory` and `tailoredPositioning` | Every draft must reference something real; a generic draft is a memory-system failure, not a stylistic choice |
| Revenue Hunter scores a pipeline item | `06-CRM/company-intelligence.json` (for relationship context) and `sourceRef`'d origin record | Strategic value depends on relationship depth already on file |
| Market Intelligence logs a development | `05-Market-Intelligence/regulatory-log.json` | Avoid logging a duplicate of something already tracked under a different headline |
| CEO Advisor picks the daily action | All of the above, via each employee's own daily output | CEO Advisor's decision quality is bounded by how completely the memory system was consulted upstream |

## Freshness, Not Expiry

Records don't expire, but their usefulness to a same-day decision does
decay. Every store already carries a recency field for this reason
(`lastTouch`, `dateAdded`, `datePublished`, `dateShipped`) — no
separate "memory decay" mechanism is needed. `04-Sales-Director/follow-up-priority-model.md`
already uses this pattern (days-since-touch by relationship
temperature); the same logic — read the recency field, don't assume
freshness — applies anywhere a memory store is queried.

## Where This Plugs Into the Rest of AOS

- `daily-operating-workflow.md` is the schedule that reads from and
  writes to these stores every day
- `business-decision-engine.md` routes new signals into these stores
  as its "Add to CRM" and "Ignore (log, archived)" actions
- `interaction-architecture.md`'s data-flow map is, functionally, a map
  of who reads and writes each store above
