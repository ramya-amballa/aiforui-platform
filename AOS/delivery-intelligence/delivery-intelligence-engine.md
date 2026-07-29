# Delivery Intelligence Engine (AOS Sprint 17 — Consulting Delivery Engine)

## Objective

AOS stopped at the proposal. This is the next capability: once an
engagement is real (signed), automatically generate the core AI
Governance delivery artifacts every engagement needs, built from
reusable, ADGL/OPERA-aligned templates so every engagement compounds
AI for U&I's own intellectual property instead of starting from a
blank page each time. This is optimised for consulting revenue, not
engineering elegance — the fastest path from "signed" to "the founder
is delivering, not drafting."

## The Trigger — a Real "Signed" Event, Never Invented

There is no separate "signed" flag anywhere in AOS. The real,
deterministic trigger is Revenue Hunter's own `08-Revenue-Hunter/pipeline.json`
`stage == "won"` — reused verbatim, never a second, independently
invented signal for the same fact.

## The Ten Artifacts

Each is rendered from its own reusable template in `templates/delivery/`
(see that folder's own README for the full mapping), aligned to ADGL's
five phases (Discover, Assess, Govern, Deploy, Operate) and OPERA's
five phases (Opportunity, People, Evaluation, Response, Assurance) —
the same phase vocabulary `practitioner-bank.json` already defines,
reused verbatim, never redefined a second time:

1. Kickoff Agenda
2. Discovery Questionnaire
3. AI Readiness Assessment Workbook
4. Governance Roadmap
5. RACI
6. Risk Register
7. Workshop Materials
8. Executive Status Report
9. Steering Committee Pack
10. Project Closure Report

## What Gets Filled In Automatically (and What Doesn't)

Only facts this engine has real, already-computed evidence for:
client name, date, an engagement reference, the primary service in
scope (Service Mapping's own recommendation, or Account Intelligence's
top-ranked service fit), industry and regulatory environment (Account
Intelligence's Company Profile), decision-maker *titles* (never
names — Account Intelligence never invents a name, and neither does
this engine), the governance risks already flagged from public signal
(pre-populated into the Risk Register and referenced throughout), and
the ADGL/OPERA phase names themselves.

Everything else — an actual kickoff date, a named attendee, a real
discovery answer, a workbook score, an actual status update, a real
decision — is deliberately left as an explicit `{{...}}` placeholder
for the founder to fill in during real delivery. **This engine never
fabricates the substance of delivery** — it only removes the blank-page
problem of the structure.

## Delivery Kits Are Living Documents — Generated Once, Never Overwritten

A kit is generated exactly once per engagement (the first run after
its pipeline entry reaches `stage == "won"`). Every subsequent run
leaves already-generated artifact files completely untouched — the
founder is expected to edit these files by hand during real delivery
(attendee names, discovery answers, workbook scores), and AOS
regenerating them would destroy that real work. A re-run only
backfills an artifact file a processed engagement is missing (e.g. a
new artifact type added to `ARTIFACT_SPECS` later) — the same
"repair, never re-fabricate the rest" pattern
`sales-director/runtime/prepare.py`'s own backfill mechanism already
established.

## Engagement Phase — Founder-Maintained, Read-Only

`delivery-log.json` (sibling to `relationship-profiles.json` and
`touchpoint-log.json` — the same founder-maintained pattern) tracks
each engagement's real phase (Not started, Kickoff, Discovery,
Assessment, Roadmap Delivered, In Delivery, Steering Committee,
Closed) and free-text progress notes. This engine reads it read-only
every run to refresh the feed's phase field — it never writes to it,
since only the founder knows the engagement's actual real-world state.

## Dashboard

**Delivery Intelligence** page: one row per won engagement (phase,
primary service, kit path), and — for the selected engagement — every
one of the ten artifacts with Preview/Download, so the founder can
open, edit and track each one from the Command Center.

## What This Engine Does Not Do

- Does not fabricate any delivery substance — every open placeholder
  (`{{...}}`) is exactly that, a structure for the founder to fill in,
  never invented content.
- Does not overwrite an already-generated artifact file — ever. See
  above.
- Does not write to `delivery-log.json`, `pipeline.json`,
  `account-intelligence-feed.json`, `opportunity-schema.json`, or
  `service-recommendations.json` — every read is read-only.
- Does not modify `templates/delivery/`'s own template files at
  runtime — they are the durable, hand-maintained IP asset; this
  engine only reads and fills them.
