# Interaction Architecture

How all nine AI employees, plus the CRM and Daily Brief aggregation
layers, communicate. The objective this architecture serves: a
self-improving consulting business, where every signal that enters
anywhere in the system eventually produces a founder action, a piece
of content, a product, or a stronger record — not a dead end.

## The Nine Employees

| # | Employee | Role in one line |
|---|---|---|
| 01 | Opportunity Hunter | Sources and scores individual opportunities as they appear |
| 02 | Content Director | Converts signals into published content across five objectives |
| 03 | Product Manager | Converts signals into productised assets |
| 04 | Sales Director | Keeps every relationship warm after first touch |
| 05 | Market Intelligence | Watches regulation and standards, triggers the rest |
| 06 | CRM | The single record every employee reads and writes |
| 07 | Daily Brief | Assembles everything into one daily executive page |
| 08 | Revenue Hunter | Owns the unified, prioritised revenue pipeline |
| 09 | CEO Advisor | Picks the single highest-ROI action, daily |

## Data Flow Map

```
                    ┌────────────────────────┐
                    │  05-Market-Intelligence │
                    │  (regulatory-log.json)  │
                    └──────────┬──────────────┘
                               │ trigger rule: every substantive
                               │ change must produce all four ↓
             ┌─────────────────┼─────────────────┬─────────────────┐
             ▼                 ▼                 ▼                 ▼
   ┌──────────────────┐ ┌──────────────┐ ┌────────────────────┐ ┌────────────────────┐
   │ 02-Content-Director│ │03-Product-   │ │01-Opportunity-Hunter│ │  (logged, no       │
   │  LinkedIn/newsletter│ │  Manager     │ │ consulting angle    │ │   action needed)   │
   │  idea              │ │ product update│ │                     │ └────────────────────┘
   └──────────┬──────────┘ └──────┬───────┘ └──────────┬──────────┘
              │                   │                    │
              │                   │                    ▼
              │                   │           ┌───────────────────┐
              │                   │           │ 08-Revenue-Hunter  │◄───────┐
              │                   │           │  (pipeline.json)   │        │
              │                   │           └─────────┬──────────┘        │
              │                   │                     │                   │
              │                   ▼                     ▼                   │
              │          ┌──────────────────┐  ┌──────────────────┐         │
              │          │03-Product-Manager│  │  06-CRM           │◄───────┤
              │          │  (backlog.json)  │  │ (company-         │        │
              │          └────────┬─────────┘  │  intelligence.json)│       │
              │                   │            └─────────┬─────────┘       │
              │  30+ score        │                       │                │
              │  notifies         ▼                       ▼                │
              │          ┌──────────────────┐  ┌──────────────────────┐    │
              └─────────►│02-Content-Director│  │  04-Sales-Director   │────┘
                         │ (launch content)  │  │ (follow-up + outreach)│
                         └──────────┬─────────┘  └──────────┬───────────┘
                                    │                        │
                                    └───────────┬────────────┘
                                                ▼
                                     ┌─────────────────────┐
                                     │    09-CEO-Advisor    │
                                     │ (picks the one action)│
                                     └──────────┬────────────┘
                                                ▼
                                     ┌─────────────────────┐
                                     │    07-Daily-Brief     │
                                     │ (one executive page)  │
                                     └─────────────────────┘
```

## Triggers, Inputs, Outputs and Hand-offs

### 01-Opportunity-Hunter
- **Triggers on**: a new posting, referral, CFP, or grant appearing in
  its monitored sources; a consulting-opportunity flag from Market
  Intelligence's trigger rule
- **Inputs**: external sources; `05-Market-Intelligence`'s daily
  triggers
- **Outputs**: `opportunities.json`; new/updated entries in
  `companies.md` and `06-CRM/company-intelligence.json`
- **Hand-off**: `Priority`-scored items → `08-Revenue-Hunter/pipeline.json`

### 02-Content-Director
- **Triggers on**: any Market Intelligence trigger requiring a
  LinkedIn/newsletter idea; a client question or engagement pattern
  worth publishing; a Product Manager launch notification
- **Inputs**: `05-Market-Intelligence/regulatory-log.json`; `06-CRM`
  patterns; `03-Product-Manager` launches
- **Outputs**: `content-brief-template.md` entries, calendar updates
- **Hand-off**: briefs may flag `03-Product-Manager` (a recurring
  question is a product signal) or `08-Revenue-Hunter` (content that
  surfaces a direct lead)

### 03-Product-Manager
- **Triggers on**: a Market Intelligence product-update trigger; a
  recurring signal identified via `product-evaluation-framework.md`
- **Inputs**: `05-Market-Intelligence`; `06-CRM`; `02-Content-Director`
  briefs; `04-Sales-Director` flags
- **Outputs**: `product-backlog.json`
- **Hand-off**: score 30+ → notifies `02-Content-Director` (launch
  content needed) and, if it has clear revenue potential, `08-Revenue-Hunter`

### 04-Sales-Director
- **Triggers on**: daily schedule (every `hot`/`warm` record checked
  against `follow-up-priority-model.md`); a stage change flagged by
  `08-Revenue-Hunter`
- **Inputs**: `06-CRM/company-intelligence.json`
- **Outputs**: outreach drafts; updates to `relationshipTemperature`,
  `nextFollowUpDue`, `outreachHistory` in `06-CRM`
- **Hand-off**: deal reaches a decision point → notifies
  `08-Revenue-Hunter` to update `pipeline.json` stage; at-risk
  relationships escalate to `09-CEO-Advisor`

### 05-Market-Intelligence
- **Triggers on**: daily schedule (24-hour check of every tracked
  source)
- **Inputs**: external regulatory/standards/security sources
- **Outputs**: `regulatory-log.json`
- **Hand-off**: every substantive entry fans out to
  `02-Content-Director`, `03-Product-Manager` and
  `01-Opportunity-Hunter` per the trigger rule

### 06-CRM
- **Triggers on**: any employee encountering a company for the first
  time, or touching one already on record
- **Inputs**: writes from `01-Opportunity-Hunter`, `04-Sales-Director`,
  `05-Market-Intelligence`
- **Outputs**: `company-intelligence.json` — the single source of truth
  no other employee duplicates
- **Hand-off**: read by every employee that needs company context
  before acting

### 07-Daily-Brief
- **Triggers on**: daily schedule, after every other employee's daily
  cycle completes
- **Inputs**: every other employee's daily output, `09-CEO-Advisor`'s
  recommendation
- **Outputs**: `daily-revenue-brief-template.md`, filled in
- **Hand-off**: none — this is the terminal aggregation point for the
  founder

### 08-Revenue-Hunter
- **Triggers on**: any new item from `01-Opportunity-Hunter`,
  `03-Product-Manager`, or `06-CRM` (existing-client upsell); any stage
  change from `04-Sales-Director`
- **Inputs**: `01-Opportunity-Hunter`, `03-Product-Manager`, `06-CRM`,
  `04-Sales-Director`
- **Outputs**: `pipeline.json`, `revenue-dashboard-template.md`
- **Hand-off**: `Priority`-band items with a near-term
  `nextActionDue` → surfaced to `09-CEO-Advisor` as candidates

### 09-CEO-Advisor
- **Triggers on**: daily schedule, after the other employees' daily
  cycles produce their candidates
- **Inputs**: `04-Sales-Director`'s follow-up queue,
  `08-Revenue-Hunter/pipeline.json`, `01-Opportunity-Hunter/opportunities.json`,
  `03-Product-Manager/product-backlog.json`,
  `05-Market-Intelligence` consulting flags
- **Outputs**: `daily-recommendation-template.md`, filled in
- **Hand-off**: feeds `07-Daily-Brief` as the lead item

## Why This Is Self-Improving

Every loop closes back into either the CRM (so the business never
re-learns the same fact about a company twice) or the pipeline (so no
revenue-shaped signal is evaluated once and forgotten). Market
Intelligence guarantees the system reacts to the outside world instead
of waiting to be asked. CEO Advisor guarantees that seven parallel,
locally-optimised functions still resolve to one clear action a day.
Nothing in this architecture requires the founder to remember what
happened yesterday — every employee's output is written down
somewhere another employee, or the founder, reads next.
