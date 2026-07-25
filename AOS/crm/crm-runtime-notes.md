# CRM Runtime — Sources, Reuse, and Ownership Rules

`runtime/generate.py` is a read-only relationship-intelligence report
generator. It never writes to `06-CRM/company-intelligence.json` — see
"The One Rule" below — and it reuses
`04-Sales-Director/follow-up-priority-model.md`'s due/overdue logic
exactly as `executive-dashboard/runtime/generate.py` already
implemented it, rather than deciding due/overdue a second, possibly
different way.

## The One Rule

**`06-CRM/company-intelligence.json`'s `relationshipTemperature`,
`nextFollowUpDue`, and `outreachHistory` belong to
`04-Sales-Director`, exclusively** — `06-CRM/README.md` already says
so ("it is the only employee that updates these fields"). This
runtime reads every field on every company record and writes none of
them back. Every output is a fresh report generated from current
state, not a mutation of the record itself.

## Sources Consumed (All Read-Only)

| Source | What's read | Why this isn't duplicated logic |
|---|---|---|
| `06-CRM/company-intelligence.json` | Every field on every company record | The relationship record itself — read, never written |
| `demand-intelligence/opportunity-schema.json` | Every opportunity, grouped by `organisation`, for a real opportunity history | A count and a most-recent date of real records, not a re-scored opinion about them |
| `sales-director/runtime/processed-index.json` | Every prepared package, cross-referenced to its opportunity's `organisation` | A real proposal history — which company, when, and Sales Director's own status, never re-interpreted |
| `08-Revenue-Hunter/pipeline.json` | Every open item, grouped by `organisation` | A real open-pipeline count and weighted value per company, using the same currency parser Revenue Hunter and Executive Dashboard already ship |

## Reused, Not Reinvented

The daily follow-up queue's due/overdue/cold-risk determination is
`executive-dashboard/runtime/generate.py`'s `crm_follow_up_status()`
function, copied verbatim (same `MAX_DAYS_BY_TEMPERATURE`, same
`days_since`/`days_until` helpers, same thresholds) rather than
re-derived. If that logic ever needs to change, it should change in
one place people know to look — for now, that means changing it
identically in both places until a future refactor gives AOS a shared
utilities location; see `revenue-hunter-runtime-notes.md`'s currency
parser for the same trade-off, made the same way, for the same reason.

## What's Genuinely New Here

`executive-dashboard`'s CRM section explicitly skips `cold` records
(`if temperature == "cold": continue`) — `follow-up-priority-model.md`
itself says cold records aren't tracked daily. Nobody in AOS has ever
looked at *how* cold, or flagged one for the monthly from-scratch
review `follow-up-priority-model.md` calls for. This runtime does
exactly that (see "Stale Relationship Alerts" below) — a genuinely new
capability, not a second version of an existing one.

It also builds the relationship health view `daily-workflow.md` and
`decision-model.md` assume exists somewhere: opportunity history,
proposal history and pipeline history per company, combined into one
row per relationship, real record counts throughout.

## Relationship Categorisation

The founder asked CRM to maintain six categories: Recruiters, Clients,
Consulting Firms, Prospects, Speaking Contacts, Partners.
`company-intelligence.json`'s schema has no category field, and this
runtime does not add one (that would modify a schema `06-CRM/README.md`
doesn't currently define). Instead, a best-effort category is inferred
from fields that already exist:

| Category | Inferred from |
|---|---|
| Recruiter | `recruiter` is set |
| Client | `existingRelationship` is `prior client` or `active client` |
| Consulting Firm | `industry` contains "consulting" or "advisory" |
| Prospect | Everything else with `existingRelationship` set (the default) |
| Speaking Contact | Not inferable from any existing field — reported as an honest gap below, not guessed |
| Partner | Not inferable from any existing field — reported as an honest gap below, not guessed |

## Stale Relationship Alerts

A `cold` company (the one temperature `crm_follow_up_status()` skips
entirely) whose `lastTouch` is more than 90 days ago is flagged: "past
the monthly review window `follow-up-priority-model.md` itself calls
for — consider a from-scratch re-approach, not a chase." 90 days is a
documented, adjustable default (roughly the "reviewed monthly" cadence
extended to an actual re-engagement trigger), not a discovered fact.

## What This Runtime Does Not Do

- Does not write to `company-intelligence.json`. Every output is a
  file in `crm/runtime/output/`.
- Does not draft or send an email, LinkedIn message, or any outreach —
  that remains `04-Sales-Director/outreach-draft-template.md`'s job,
  drafted by a human or by Sales Director's own runtime, never here.
- Does not re-decide `relationshipTemperature` or invent a category
  this data can't actually support (Speaking Contact, Partner) —
  reported as a gap, not guessed.
