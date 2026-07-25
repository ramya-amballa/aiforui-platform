# Sales Director — Proposal Preparation Engine (Execution Mode)

The first outbound AI employee: it turns a classified opportunity into
a ready-to-review outreach package, without ever sending anything
itself.

`04-Sales-Director/` remains the relationship/follow-up specification —
mission, `follow-up-priority-model.md`, `outreach-draft-template.md` —
and keeps running exactly as documented there, owning
`relationshipTemperature`, `nextFollowUpDue` and `outreachHistory` on
every CRM record. This folder is the newer, narrower half of the same
employee: the moment an opportunity is classified `Immediate Proposal`,
`Apply`, `Partnership` or `Follow Recruiter`, it prepares the first full
package for that opportunity — cover letter, proposal, recruiter
outreach, client outreach, clarifying questions, recommended pricing,
and a confidence score — so nothing is drafted from scratch by hand.

## Files

- `proposal-preparation-engine.md` — the content bank, the pricing
  model, the confidence-score formula, and the three statuses this
  engine is allowed to report upward
- `runtime/` — this specification, running as code

## How It Fits AOS

- **Reads from:** `demand-intelligence/opportunity-schema.json` (which
  opportunities and their classification), `08-Revenue-Hunter/pipeline.json`
  (real revenue estimates, where one exists), `06-CRM/company-intelligence.json`
  (relationship context)
- **Writes to:** `runtime/output/` only — one prepared package per
  opportunity, plus a status feed
- **Feeds:** `09-CEO-Advisor`, and only one of three words per
  opportunity: `Proposal Ready`, `Needs Review`, or `Ready To Send`.
  CEO Advisor never sees the drafts themselves.

## What This Is Not

Not a send pipeline. Every package is preparation only — the founder
reviews and sends every message and every proposal by hand, exactly as
`04-Sales-Director/outreach-draft-template.md` already requires for
ordinary follow-ups. Automating preparation is the entire scope;
automating sending is explicitly out of scope.

Start with `proposal-preparation-engine.md`, then `runtime/prepare.py`'s
own docstring for the exact execution mechanics.
