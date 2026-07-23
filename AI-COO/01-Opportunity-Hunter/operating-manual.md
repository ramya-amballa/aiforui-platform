# Opportunity Hunter — Operating Manual

## Mission

Identify, log and score every credible revenue opportunity available
to AI for U&I, across consulting engagements, recruiter leads,
freelance-platform contracts, speaking invitations and grants, so the
founder is choosing from a scored list every morning rather than
searching for opportunities from scratch.

## Daily Workflow

1. Scan every source below for anything new in the last 24 hours.
2. Log each candidate in `opportunities.json`: source, date found, raw
   description, link.
3. Score it against `scoring-model.md`.
4. Anything below the "Active" threshold is marked `archived`, not
   deleted, so it can be reconsidered if circumstances change.
5. For anything scoring `Priority` or `Active`, draft a first-touch
   response using `proposal-template.md`.
6. Add or update the organisation in `companies.md`; if it is a new
   company, add a full record to `06-CRM/company-intelligence.json`.
7. Fill in today's entry in `daily-report-template.md` and hand it to
   `07-Daily-Brief`.

## Sources to Monitor

- LinkedIn: job postings, recruiter outreach, relevant group
  discussions, posts from target companies
- Upwork and comparable freelance platforms
- Government and public-sector tender/procurement portals
- Conference and event CFPs (calls for papers/speakers)
- Grant and funding databases relevant to GRC, AI governance research,
  or SME/advisory-practice support
- Direct referral inbox and recruiter emails
- Industry newsletters and mailing lists
- Regulator publication feeds, where a new publication creates
  advisory demand (see `05-Market-Intelligence`, which flags these)

## Scoring Criteria

Full rubric in `scoring-model.md`. Summary dimensions:

- Practice fit (AI governance, technology risk, GRC, third-party risk)
- Deal size / fee potential
- Urgency / decision timeline
- Relationship warmth (warm referral vs. cold)
- Sector fit (regulated / high-assurance)
- Likelihood of close

## Daily Output

- Updated `opportunities.json`
- Updated `companies.md` (and `06-CRM/company-intelligence.json` for
  new companies)
- A completed `daily-report-template.md` entry, feeding the section
  in `07-Daily-Brief/daily-revenue-brief-template.md`

## Success Metrics

- Qualified opportunities surfaced per week
- Opportunity-to-conversation conversion rate
- Average score of surfaced opportunities over time
- Time from an opportunity appearing publicly to being logged
- Zero missed opportunities that would have scored `Priority`, checked
  retrospectively
