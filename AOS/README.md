# AOS — AI for U&I Operating System

AOS (formerly "AI-COO") is the operating system behind AI for U&I. The
earlier name implied a single executive function; what's actually here
is closer to an enterprise operating system: nine coordinated AI
employees, a shared long-term memory, a decision engine that routes
every new signal, a daily execution cycle, and a CEO Advisor that
resolves all of it into one action a day. Where OPERA is the
methodology the practice sells to clients, AOS is the one that runs the
practice itself: finding revenue, producing content, building
products, running outreach, tracking the market, keeping records
straight, and reporting on all of it every day.

Each AI employee is run like a real employee, not a one-off prompt: a
defined mission, a daily workflow, explicit sources and inputs, a
scoring or decision model where relevant, a defined daily output, and
success metrics it is measured against. That structure lives in each
employee's `operating-manual.md`.

## AI Employees

| Folder | AI Employee | Responsibility |
|---|---|---|
| `opportunity-hunter` | Opportunity Hunter | Live operating component: monitors nineteen sources, scores every opportunity across eleven dimensions, classifies it and routes it downstream with no manual reformatting |
| `02-Content-Director` | Content Director | Live operating component: converts Market Intelligence signals, recurring opportunity patterns, shipped products and CEO Advisor's daily priority into publish-ready LinkedIn, newsletter, website-insight and product-announcement drafts — never publishes automatically |
| `03-Product-Manager` | Product Manager | Live operating component: evaluates real signals from Market Intelligence, Opportunity Hunter, Sales Director and Content Director into a real 0-40 score and one of nine formats (toolkit, checklist, executive guide, assessment, course, workshop, subscription, ADGL extension, OPERA module) |
| `04-Sales-Director` | Sales Director | Maintains every recruiter, consulting firm, prospect and client relationship after first touch; recommends follow-ups daily and drafts personalised outreach so nothing goes cold |
| `05-Market-Intelligence` | Market Intelligence | Live operating component: monitors thirteen regulatory/vendor/theme sources (EU AI Act, ISO 42001, NIST AI RMF, DORA, GDPR, CBUAE, RBI, Microsoft AI, OpenAI Enterprise, Anthropic, AI Security, AI Governance, Responsible AI), classifies every development against six checks, and routes structured signals to Content Director, Product Manager, Opportunity Hunter and CEO Advisor |
| `06-CRM` | CRM | Maintains the single record of contacts, companies and relationship status across the pipeline |
| `07-Daily-Brief` | Daily Brief | Assembles the Daily Revenue Brief from every other AI employee's output |
| `08-Revenue-Hunter` | Revenue Hunter | Live operating component: owns the full, unified revenue pipeline, admits new Active/Priority opportunities and CRM upsell signals, advances stage as Sales Director prepares proposals, and produces a real probability-weighted revenue dashboard and monthly forecast — no financial assumption fabricated |
| `09-CEO-Advisor` | CEO Advisor | Writes no content; every morning selects the single highest-ROI action across all other employees' output |

## Shared Structure

- `prompts/` — prompts shared across AI employees, rather than duplicated per folder
- `templates/` — templates shared across AI employees, including the Proposal Library (`templates/proposals/`)
- Each numbered folder is one AI employee: its own `README.md`, `operating-manual.md` (or equivalent), and working files
- `interaction-architecture.md` — how all nine employees communicate: triggers, dependencies, inputs, outputs and hand-offs
- `daily-operating-workflow.md` — the exact 06:00-start daily sequence every employee follows, written to be lifted directly into a scheduler (GitHub Actions or otherwise)
- `business-decision-engine.md` — how a new signal is classified and routed to one or more actions (ignore, apply, build a product, write content, contact recruiter, add to CRM, create proposal, schedule follow-up), with confidence thresholds
- `memory-system.md` — the long-term memory architecture: every store, who writes it, and the retrieval rules that keep any employee from starting from scratch
- `kpi-dashboards/` — one dashboard per employee, rolling up into `kpi-dashboards/ceo-dashboard.md`, AOS's single view of overall business health
- `08-Revenue-Hunter/revenue-forecasting-engine.md` — probability-weighted monthly revenue forecasting and highest-leverage-action analysis
- `executive-dashboard/` — the single entry point every morning: revenue, CEO Advisor's top priority, and everything needing attention across Opportunity Hunter, Revenue Hunter and CRM, generated read-only from their live outputs (`executive-dashboard/runtime/generate.py`)
- `sales-director/` — Sales Director's proposal preparation engine: turns every `Immediate Proposal`/`Apply`/`Partnership`/`Follow Recruiter` opportunity into a cover letter, proposal, recruiter/client outreach, clarifying questions, recommended pricing and a confidence score, preparation only, never sent (`sales-director/runtime/prepare.py`)
- `content-director/` — Content Director's draft-generation engine: turns Market Intelligence signals, recurring opportunity patterns, shipped products and CEO Advisor's daily priority into LinkedIn/newsletter/website-insight/product-announcement drafts grounded in real practitioner experience and the product catalogue, never publishes (`content-director/runtime/generate.py`)
- `product-manager/` — Product Manager's evaluation engine: runs `03-Product-Manager/product-evaluation-framework.md` (Steps 2-4) against real signals from Market Intelligence, Opportunity Hunter, Sales Director and Content Director, producing a real 0-40 score and format per candidate in `product-backlog.json` (`product-manager/runtime/generate.py`)
- `revenue-hunter/` — Revenue Hunter's financial-intelligence engine: runs `lead-scoring.md`, `decision-tree.md` and `revenue-forecasting-engine.md` against real pipeline, opportunity, CRM, Sales Director and Product Manager data, producing a real revenue dashboard and monthly forecast — no financial assumption is ever fabricated (`revenue-hunter/runtime/generate.py`)
- `orchestrator/` — the single entry point for daily operations: runs every employee with a live runtime in dependency order, retries failures, logs everything, and produces the Daily Execution Report (`orchestrator/orchestrator.py`) — see below

## Status

| AI Employee | Status |
|---|---|
| `opportunity-hunter` | v1 — live operating component: sources, scoring engine, relevance engine, schema, backlog, daily report, integration contract |
| `02-Content-Director` | Fully defined, plus a live draft-generation engine (`content-director/`): editorial operating system, conversion map, brief/calendar templates, published-content log, content-brief queue, drafts feed to CEO Advisor |
| `03-Product-Manager` | Fully defined, plus a live evaluation engine (`product-manager/`): operating manual, evaluation framework (nine formats), product backlog, shipped-products log |
| `04-Sales-Director` | Fully defined, plus a live proposal preparation engine (`sales-director/`): operating manual, follow-up priority model, outreach draft template, pricing/confidence model, prepared-proposal feed to CEO Advisor |
| `05-Market-Intelligence` | v1.0 — live operating component: thirteen tracked sources, classification model, regulatory log, runtime, routes to four downstream employees |
| `06-CRM` | Fully defined: company intelligence knowledge base |
| `07-Daily-Brief` | Fully defined: daily revenue brief template |
| `08-Revenue-Hunter` | Fully defined, plus a live financial-intelligence engine (`revenue-hunter/`): operating system, decision tree, lead scoring, pipeline, forecasting engine, real dashboard and forecast |
| `09-CEO-Advisor` | Fully defined: operating manual, decision model, daily recommendation template |

`templates/proposals/` (the Proposal Library) is complete: nine
domain templates. `prompts/` is structure only.

Working files (`opportunity-schema.json`, `regulatory-log.json`,
`company-intelligence.json`, `companies.md`, `pipeline.json`,
`product-backlog.json`, `published-content-log.json`,
`shipped-products-log.json`, daily reports) start empty, with their
schema documented in the file itself, and are populated as the AI
employees actually run.

## Running AOS

`python3 AOS/orchestrator/orchestrator.py` is the single command that
runs a day of AOS operations — the only thing GitHub Actions or a human
should invoke. See `orchestrator/README.md`.
