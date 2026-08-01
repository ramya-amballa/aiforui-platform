# CEO Advisor — Operating Manual

## Mission

Every morning, look across the entire business and choose exactly one
priority: the single highest-ROI action Ramya should take today. Not a
list, not a summary of everything happening, one answer, with the
reasoning shown.

**Since Sprint 5** (`ceo-advisor/runtime/generate.py`), this mission is
executed as code, as the final step of every Orchestrator run — after
every other employee, including Daily Brief, has already produced its
own output for the day. See `ceo-advisor/ceo-advisor-runtime-notes.md`
for exactly how; the workflow below still describes the model
correctly, with one change: step 5 no longer passes anything to Daily
Brief, since Daily Brief has already run by the time CEO Advisor does.
CEO Advisor's own output — the CEO Daily Report, CEO Weekly Report,
and CEO Monthly Business Review — is now the final artefact of each
day's run, not an input to one.

## What CEO Advisor Does Not Do

- Does not write LinkedIn posts, newsletters, or proposals
  (`02-Content-Director`)
- Does not score or source new opportunities
  (`demand-intelligence`, `08-Revenue-Hunter`)
- Does not draft outreach or manage follow-ups (`04-Sales-Director`)
- Does not track regulations or evaluate products
  (`05-Market-Intelligence`, `03-Product-Manager`)

CEO Advisor produces judgment, not content. Its only artefact is a
daily recommendation.

## Daily Workflow

1. Pull the candidate list:
   - Every `hot` or overdue item from `04-Sales-Director`'s follow-up
     queue — computed today by `crm/runtime/generate.py`'s
     `crm_follow_up_status()` (reused verbatim by
     `ceo-advisor/runtime/generate.py`) over
     `06-CRM/company-intelligence.json`'s Sales-Director-owned
     `relationshipTemperature`/`nextFollowUpDue` fields; CRM computes
     the queue, Sales Director still owns the fields it's computed
     from
   - Every `Priority`-band item from `08-Revenue-Hunter/pipeline.json`
     with a `nextActionDue` in the next 7 days
   - Any `Priority`-band item from `demand-intelligence/opportunity-schema.json`
   - Any candidate scoring 30+ in `03-Product-Manager/product-backlog.json`
     — documented here, but not yet read by `ceo-advisor/runtime/
     generate.py` v1, which implements exactly Sprint 5's named eight
     sources (Demand Intelligence, Market Intelligence, CRM, Revenue
     Hunter, Service Mapping Engine, Sales Director, Website Intake,
     Daily Brief); adding Product Manager and Content Director to the
     runtime is a future extension, not a redesign
   - Every entry in `output/05-Market-Intelligence/ceo-advisor-feed.json`
     — the six checks only (see `decision-model.md`); the underlying
     `regulatory-log.json` entry is never opened here
   - Every entry in `output/sales-director/ceo-advisor-feed.json`
     — its `status` only (`Ready To Send`, `Proposal Ready`, or
     `Needs Review`); the underlying package is never opened here
   - Every entry in `output/content-director/ceo-advisor-feed.json`
     — its `status` only (`Ready to Publish`, `Needs Review`, or
     `Low Value`); the drafts themselves are never opened here.
     Documented here for the same reason as Product Manager above —
     not yet read by the v1 runtime.
   - Every entry in `output/website-intake/ceo-advisor-feed.json`
     — its `urgency` only (`High`, `Medium`, or `Low`); the full lead
     record in `website-intake/leads.json` is never opened here
   - Any employee listed in `orchestrator/status.json`'s `failures` for
     that day's run — a broken pipeline is a candidate action in its
     own right
2. Run every candidate through `decision-model.md`.
3. Select exactly one action as today's highest-value action; list the
   next 2-3 as runners-up, not as co-priorities.
4. Produce today's entry using `daily-recommendation-template.md` — now
   embedded as the CEO Daily Report's "Top 3 Priorities" section,
   ranked rather than a single pick plus unranked runners-up.
5. Write the CEO Daily Report (and refresh the rolling CEO Weekly
   Report and CEO Monthly Business Review) to
   `output/ceo-advisor/`. Daily Brief has already run and
   produced its own dashboard for the day by this point — CEO Advisor
   reads it (its "## Daily Summary" section, quoted, never recomputed)
   rather than feeding it.

## Success Metrics

- The recommended action is completed the same day
- Estimated value of recommended actions vs. actual outcome, tracked
  over time
- No `hot` Sales Director item is ever missed because it wasn't
  surfaced
- Founder trust: is the daily recommendation actually being followed,
  or second-guessed and reworked most days (a sign the model needs
  recalibrating)
