# Market Intelligence — Operating Manual

## Mission

Track every real development in AI and technology governance
regulation, standards and security news, and convert each one into a
concrete action, not just a note. A regulatory change that produces no
LinkedIn post, no newsletter issue, no product update and no
consulting angle has been noticed but not used.

## What's Tracked

- **EU AI Act** — implementation guidance, delegated acts, harmonised
  standards, enforcement actions
- **ISO 42001** — AI management system standard updates and
  certification-body guidance
- **NIST AI RMF** — profile updates, companion guidance (e.g.
  generative AI profile)
- **DORA** — regulatory technical standards, ICT third-party
  designations, supervisory guidance
- **GDPR** — enforcement decisions and guidance relevant to AI/data
  processing
- **CBUAE AI Principles** — UAE central bank AI governance guidance
- **RBI AI guidance** — Reserve Bank of India AI/fintech risk guidance
- **AI security news** — significant incidents, vulnerabilities or
  attack patterns relevant to AI systems in production

## Daily Workflow

1. Check each tracked source for anything published in the last 24
   hours.
2. Log every real development in `regulatory-log.json`: source, date,
   summary, link.
3. Apply the trigger rule (below) to each development.
4. Hand off the day's triggered actions to the relevant AI employee.

## The Trigger Rule

Every regulatory or standards change that is actually substantive (not
a minor edit or a duplicate report of something already logged) must
produce all four of the following, even if the answer for one of them
is "not applicable, here's why":

| Trigger | Owner | What it looks like |
|---|---|---|
| LinkedIn idea | `02-Content-Engine` | A post explaining what changed and what it actually means for a practitioner, not a summary of the text |
| Newsletter idea | `02-Content-Engine` | A longer treatment for the next AI for U&I newsletter issue |
| Product update | `03-Product-Factory` | Does this change an existing framework, playbook or the Executive Capability Overview? |
| Consulting opportunity | `01-Opportunity-Hunter` | Who does this create urgency for, and is it worth reaching out to them directly? |

## Daily Output

- Updated `regulatory-log.json`
- A "Regulations Published Today" entry for
  `07-Daily-Brief/daily-revenue-brief-template.md`, including the
  triggered actions and which AI employee owns each

## Success Metrics

- Time from publication to being logged
- Percentage of substantive developments that produced all four
  triggers
- Number of consulting opportunities that can be traced back to a
  specific regulatory development
- Zero missed developments in a tracked source, checked retrospectively
