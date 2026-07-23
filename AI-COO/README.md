# AI-COO

AI-COO is the operating system behind AI for U&I. Where OPERA is the
methodology the practice sells to clients, AI-COO is the one that runs
the practice itself: a team of AI employees responsible for finding
revenue, producing content, building products, running outreach,
tracking the market, keeping records straight, and reporting on all of
it every day.

Each AI employee is run like a real employee, not a one-off prompt: a
defined mission, a daily workflow, explicit sources and inputs, a
scoring or decision model where relevant, a defined daily output, and
success metrics it is measured against. That structure lives in each
employee's `operating-manual.md`.

## AI Employees

| Folder | AI Employee | Responsibility |
|---|---|---|
| `01-Opportunity-Hunter` | Opportunity Hunter | Scans external sources and scores individual revenue opportunities as they appear: consulting engagements, recruiter leads, freelance-platform contracts, speaking invitations, grants |
| `02-Content-Director` | Content Director | Runs the editorial operating system: converts regulatory changes, client questions and engagement patterns into LinkedIn posts, newsletters, website updates and downloadable resources |
| `03-Product-Manager` | Product Manager | Continuously evaluates whether a signal should become a product, and in which format: toolkit, checklist, executive guide, assessment, course, workshop, or subscription |
| `04-Sales-Director` | Sales Director | Maintains every recruiter, consulting firm, prospect and client relationship after first touch; recommends follow-ups daily and drafts personalised outreach so nothing goes cold |
| `05-Market-Intelligence` | Market Intelligence | Tracks regulatory, competitive and market developments (EU AI Act, ISO 42001, NIST AI RMF, DORA, GDPR, CBUAE, RBI, AI security news) and triggers content, product and consulting signals |
| `06-CRM` | CRM | Maintains the single record of contacts, companies and relationship status across the pipeline |
| `07-Daily-Brief` | Daily Brief | Assembles the Daily Revenue Brief from every other AI employee's output |
| `08-Revenue-Hunter` | Revenue Hunter | Owns the full, unified revenue pipeline across every opportunity type and prioritises it by expected revenue, probability, effort and strategic value |
| `09-CEO-Advisor` | CEO Advisor | Writes no content; every morning selects the single highest-ROI action across all other employees' output |

## Shared Structure

- `prompts/` — prompts shared across AI employees, rather than duplicated per folder
- `templates/` — templates shared across AI employees, including the Proposal Library (`templates/proposals/`)
- Each numbered folder is one AI employee: its own `README.md`, `operating-manual.md` (or equivalent), and working files
- `interaction-architecture.md` — how all nine employees communicate: triggers, dependencies, inputs, outputs and hand-offs

## Status

| AI Employee | Status |
|---|---|
| `01-Opportunity-Hunter` | Fully defined: operating manual, scoring model, working files |
| `02-Content-Director` | Fully defined: editorial operating system, conversion map, brief and calendar templates |
| `03-Product-Manager` | Fully defined: operating manual, evaluation framework, product backlog |
| `04-Sales-Director` | Fully defined: operating manual, follow-up priority model, outreach draft template |
| `05-Market-Intelligence` | Fully defined: operating manual, regulatory log |
| `06-CRM` | Fully defined: company intelligence knowledge base |
| `07-Daily-Brief` | Fully defined: daily revenue brief template |
| `08-Revenue-Hunter` | Fully defined: operating system, decision tree, lead scoring, pipeline |
| `09-CEO-Advisor` | Fully defined: operating manual, decision model, daily recommendation template |

`templates/proposals/` (the Proposal Library) is complete: nine
domain templates. `prompts/` is structure only.

Working files (`opportunities.json`, `regulatory-log.json`,
`company-intelligence.json`, `companies.md`, daily reports) start
empty, with their schema documented in the file itself, and are
populated as the AI employees actually run.
