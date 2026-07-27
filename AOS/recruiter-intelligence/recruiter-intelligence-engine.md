# Recruiter Intelligence Engine (AOS Sprint 10)

Maintains a knowledge base of every recruiter and consulting contact
AOS has real evidence of. Unlike Sprints 8/9, this employee's output
is genuinely read by CEO Advisor (not just depended on for ordering) —
CEO Advisor now recommends recruiter follow-ups automatically, per
explicit instruction.

## Data Sources (Read-Only, Never a Second Collector)

- `demand-intelligence/opportunity-schema.json`: any opportunity whose
  `sourceCategory` is `Recruiter Channel` or `Consulting Channel`
  contributes a contact (its `source` field), a role hired (`title`),
  a location (feeding "countries"), and `domainTags` (feeding
  "specialisation").
- `crm/company-intelligence.json`: any company with a `recruiter` name
  set contributes that company's `industry`, `relationshipTemperature`,
  `lastTouch`, `nextFollowUpDue` and `outreachHistory` — CRM's own
  already-computed fields, reused verbatim (hottest temperature /
  soonest follow-up / most recent touch wins across multiple attributed
  companies), never recomputed independently.
- `08-Revenue-Hunter/pipeline.json`: a `won` stage for an organisation
  sourced from this contact counts toward Success Rate.

## The Eleven Tracked Fields

Recruiter, Firm (same as recruiter name — the current data model
doesn't distinguish a person from their agency), Specialisation
(ranked `domainTags`), Industries, Countries, Roles Hired, Response
History (CRM's own `outreachHistory` for attributed companies), Last
Interaction, Next Follow-up, Relationship Strength (CRM's own
`relationshipTemperature`, converted to a 0-100 score for sorting),
Response Rate (% of attributed companies with `existingRelationship`
beyond "none" — an honest proxy, since no explicit "recruiter
responded" event is tracked anywhere in AOS today), Success Rate (% of
sourced opportunities with a `won` pipeline stage).

## The Four Generated Views

- **Weekly Follow-up List** — contacts whose `nextFollowUp` falls
  within the next 7 days (configurable).
- **Dormant Relationships** — no interaction in 60+ days (configurable),
  or a known contact never actually touched.
- **Priority Recruiters** — top 10 by a documented weighted sum
  (`relationshipStrength x0.4 + responseRate x0.3 + successRate x0.3`),
  missing components treated as 0, never guessed.
- **Recruiters Hiring AI Governance / GRC / Fractional Consultants** —
  filtered by specialisation overlap with each domain's tag set.

## CEO Advisor Integration

`ceo-advisor/runtime/generate.py`'s new `recruiter_followups_this_week()`
reads `recruiter-intelligence-feed.json`'s own already-computed
`weeklyFollowUpList`/`dormantRelationships` read-only, and
`render_recruiter_followups_section()` adds a new, additive "Recruiter
Follow-ups" section to the CEO Daily Report, listing who's due this
week and who's gone dormant — no new scoring, every field is Recruiter
Intelligence's own.

## What This Sprint Deliberately Does Not Do

- Does not modify `opportunity-schema.json`, `company-intelligence.json`,
  or `pipeline.json` — every read is read-only.
- Does not invent a recruiter's specialisation/industries/countries
  beyond what real, already-collected opportunity/CRM data supports —
  "Not enough data yet" is left honest, never guessed.
- Does not change CRM's own relationship-scoring logic — Relationship
  Strength is CRM's own `relationshipTemperature`, converted to a
  number for sorting only.

## Dashboard

The Command Center's new **Recruiter Intelligence** page: a refresh
button, tabs for All Contacts / Weekly Follow-up List / Dormant
Relationships / Priority Recruiters / Hiring filters, and a per-contact
detail view with relationship score, priority score, next action due,
and a timeline of every recorded interaction.
