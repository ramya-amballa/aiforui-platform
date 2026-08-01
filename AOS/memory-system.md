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
| Opportunities | `opportunity-hunter/opportunity-schema.json` | Every opportunity ever logged, including archived ones — never deleted | Opportunity Hunter |
| Companies (log) | `opportunity-hunter/companies.md` | A lightweight, human-readable pointer log; links to the CRM record | Opportunity Hunter |
| Company Intelligence | `06-CRM/company-intelligence.json` | The single enriched record per organisation: industry, AI maturity, regulations, relationship, recruiter, prior applications, positioning, relationship temperature, full outreach history | Opportunity Hunter, Sales Director, Market Intelligence |
| Revenue Pipeline | `08-Revenue-Hunter/pipeline.json` | Every revenue-shaped item across all nine types, at every stage, including won/lost/deferred | Revenue Hunter |
| Regulatory Log | `05-Market-Intelligence/regulatory-log.json` | Every substantive regulatory/standards/security development ever logged, and its triggered actions | Market Intelligence |
| Published Content | `02-Content-Director/published-content-log.json` | Every piece of content actually published, its objective, its trigger, and its measured result | Content Director |
| Product Backlog | `03-Product-Manager/product-backlog.json` | Every product candidate ever evaluated, at any score, including parked ones | Product Manager |
| Shipped Products | `03-Product-Manager/shipped-products-log.json` | Every product actually shipped, the signal that justified it, and its result since | Product Manager |
| Relationship Profiles | `relationship-intelligence/relationship-profiles.json` | Founder-maintained, per-person: meetings, calls, messages, shared interests, birthdays/work anniversaries | Founder only (Relationship Intelligence reads it read-only) |
| Touchpoint Log | `reverse-job-hunt/touchpoint-log.json` | Founder-maintained, per-organisation BD campaign status and every logged touchpoint | Founder only (Reverse Job Hunt reads it read-only) |
| Delivery Log | `delivery-intelligence/delivery-log.json` | Founder-maintained, per-organisation delivery phase (Kickoff through Closed) and free-text progress notes | Founder only (Delivery Intelligence and Company 360 read it read-only) |
| Daily Priorities Log | `output/ceo-advisor/daily-priorities-log.json` | One entry per day: CEO Advisor's own Top 3 and fired alert types — the one place its daily advice survives past tomorrow's overwrite | CEO Advisor (Executive Memory reads it read-only, one cycle behind) |
| Decision Log | `executive-memory/decision-log.json` | Founder-maintained, standalone institutional decisions/rules not tied to one engagement | Founder only (Executive Memory reads it read-only) |

Note: the five stores above are institutional/relationship memory — who
said what, what phase an engagement is in, what was decided — distinct
from the eight operational stores above them, which are the facts each
employee needs to avoid re-collecting. `executive-memory/executive-memory-engine.md`
covers institutional memory in more depth: recurring patterns across
CEO Advisor's own history, a real Lessons Learned library, and
governance risks recurring across organisations.

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
| Executive Memory aggregates a pattern | CEO Advisor's `daily-priorities-log.json`, Delivery Intelligence's completed closure reports, Account Intelligence's governance risks, and `decision-log.json` | A pattern is only reported once it's genuinely recurred in real, already-persisted history — never inferred from a single occurrence |

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
