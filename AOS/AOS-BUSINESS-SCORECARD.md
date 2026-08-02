# AOS Business Scorecard

Business metrics, not engineering metrics. This is the scoreboard for
the next phase of the practice — updated by hand at each Quarterly
Review (`AOS-PRACTICE-VALIDATION-ROADMAP.md`, §5), never automated.
Building a live query dashboard for this now would be exactly the kind
of platform work Operating Mode defers until real engagements justify
it — this document *is* the founder habit, not a stand-in for one.

**Status: Day Zero.** No real engagement has been won or closed yet.
Every "Current" cell below is an honest zero or "not yet" — not a
placeholder to be embarrassed about, a starting line to measure from.

## Refresh log

| Period | Updated by | Note |
|---|---|---|
| Day Zero | — | Baseline established; Cohort A (Engagements 1-5) not yet started |

## The Scorecard

| Metric | Target | Current | Source |
|---|---|---|---|
| Engagements completed | 20 (Cohorts A-D) | 0 | `delivery-log.json` entries at phase `Closed` |
| Proposal win rate | Track | — | `pipeline.json` `stage=="won"` ÷ proposals sent (`sales-director` output) |
| Average proposal preparation time | Reduce | — | Opportunity reaches `Immediate Proposal`/`Apply` (`opportunity-schema.json`) → proposal package generated (`sales-director`) |
| Average delivery preparation time | Reduce | — | `pipeline.json` `stage=="won"` → delivery kit generated (`delivery-intelligence`) |
| Reusable artifacts created | Increase | 0 | `artifact-index.json`'s `artifactCount`, quarter-over-quarter |
| Templates reused | Increase | 0 | Citations of `templates/proposals/` + `templates/delivery/` files in real proposals/kits |
| Founder hours saved | Estimate & refine | — | Self-reported weekly (Founder Productivity, see Roadmap §1) |
| Client satisfaction | Track manually | — | `delivery-log.json`'s `clientSatisfactionNote` — founder-written, never computed |
| Referral source | Track manually | — | `06-CRM/company-intelligence.json`'s `referredBy` — founder-written, never computed |
| Repeat business | Track | — | `delivery-log.json` `Closed` entries cross-referenced against `existingRelationship=="active client"` on a second SOW |

`clientSatisfactionNote` and `referredBy` are new fields, added directly
in response to this scorecard — both existed only as a documented gap
in the Roadmap until now; both are real fields in real founder-
maintained files today.

## How to update this

At each Quarterly Review: pull the numbers that come from real AOS
files (`artifactCount`, template citation counts, pipeline win/loss),
fill in the ones that are genuinely manual (satisfaction, referral,
founder hours), add one Refresh Log row, and move on. If a metric has
been "—" for three consecutive quarters, that itself is a finding for
the Review's own "which founder edits were repeatedly required" /
"which verification warnings mattered" questions — not a reason to
automate the field early.
