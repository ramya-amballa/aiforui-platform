# Product Manager — Operating Manual

## Mission

Continuously identify opportunities to create or improve products.
Every new regulation, client question, or LinkedIn discussion gets
evaluated for conversion into one of seven formats, rather than
letting good material stay locked inside a single conversation or
engagement.

## The Seven Formats

| Format | Best fit when | Example on the site |
|---|---|---|
| Toolkit | A recurring operational task needs several bundled artefacts (templates, checklists, trackers) | DPDP Compliance Toolkit |
| Checklist | A single, narrow, repeatable verification task | Third-Party Risk Assessment Checklist |
| Executive Guide | A board/executive-level overview of a topic, meant to be read in minutes | Executive Capability Overview |
| Assessment | A diagnostic a prospect can self-administer to see where they stand | AI Governance Maturity Framework |
| Course | A structured, multi-part educational sequence | Not yet built |
| Workshop | A live or cohort-based facilitated session | Not yet built |
| Subscription | Ongoing or recurring access to updated content or advisory time | Not yet built |

## Daily Workflow

1. Pull today's substantive entries from
   `05-Market-Intelligence/regulatory-log.json` where `productUpdate`
   is not null.
2. Pull recurring client questions from `06-CRM/company-intelligence.json`
   and anything flagged by `04-Sales-Director`.
3. Pull content-driven product flags from
   `02-Content-Director/content-brief-template.md` entries.
4. Run each signal through `product-evaluation-framework.md`.
5. Add or update candidates in `product-backlog.json`.
6. Flag the top candidate to `07-Daily-Brief` ("Product ideas") and, if
   it has clear revenue potential, to `08-Revenue-Hunter`.
7. When a product ships or is meaningfully updated, notify
   `02-Content-Director` (launch content is needed) and update
   `06-CRM` if the product resulted from a specific client's question.

## Success Metrics

- Signals evaluated per week
- Candidates advanced from `idea` to `in-development`
- Products shipped per quarter
- Revenue or lead-generation attributable to each product
- Coverage: is any one format being neglected relative to demand
  (e.g. no Course or Workshop exists yet despite repeated signal)
