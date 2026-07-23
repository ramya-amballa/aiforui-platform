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
| `01-Opportunity-Hunter` | Opportunity Hunter | Finds, logs and scores new revenue opportunities: consulting engagements, recruiter leads, freelance-platform contracts, speaking invitations, grants |
| `02-Content-Engine` | Content Engine | Plans, drafts and maintains published content: Insights pieces, newsletter issues, LinkedIn posts |
| `03-Product-Factory` | Product Factory | Builds and maintains productised assets: frameworks, playbooks, workbooks, the Executive Capability Overview |
| `04-Sales-Agent` | Sales Agent | Runs outreach and follow-up on qualified opportunities, using the Proposal Library in `templates/proposals/` |
| `05-Market-Intelligence` | Market Intelligence | Tracks regulatory, competitive and market developments relevant to AI and technology governance |
| `06-CRM` | CRM | Maintains the record of contacts, companies and relationship status across the pipeline |
| `07-Daily-Brief` | Daily Brief | Assembles the Daily Revenue Brief from every other AI employee's output |

## Shared Structure

- `prompts/` — prompts shared across AI employees, rather than duplicated per folder
- `templates/` — templates shared across AI employees, including the Proposal Library (`templates/proposals/`)
- Each numbered folder is one AI employee: its own `README.md`, `operating-manual.md`, and working files

## Status

| AI Employee | Status |
|---|---|
| `01-Opportunity-Hunter` | Fully defined: operating manual, scoring model, working files |
| `02-Content-Engine` | Structure only, not yet defined |
| `03-Product-Factory` | Structure only, not yet defined |
| `04-Sales-Agent` | Structure only, not yet defined |
| `05-Market-Intelligence` | Fully defined: operating manual, regulatory log |
| `06-CRM` | Fully defined: company intelligence knowledge base |
| `07-Daily-Brief` | Fully defined: daily revenue brief template |

`templates/proposals/` (the Proposal Library) is complete: nine
domain templates. `prompts/` is structure only.

Working files (`opportunities.json`, `regulatory-log.json`,
`company-intelligence.json`, `companies.md`, daily reports) start
empty, with their schema documented in the file itself, and are
populated as the AI employees actually run.
