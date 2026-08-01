# Executive Brand Intelligence Engine (AOS Sprint 15)

## Objective

Manage AI for U&I's thought-leadership plan automatically. Every week,
generate a Weekly Brand Plan; every run, roll up a Monthly Authority
Report from the trailing weeks. Every section below is a read of real
data another employee already computed — never a second,
independently-invented signal, and never a fabricated name, figure or
event.

## Inputs (all read-only)

- `demand-intelligence/organisation-profiles.json` — this week's
  qualified organisations (windowed by `lastSeen`, same pattern
  Demand Intelligence's own top-organisations-this-week.json uses).
- `output/account-intelligence/account-intelligence-feed.json` —
  this week's Account Intelligence briefs (governance risks, service
  fit, outreach strategy).
- `relationship-intelligence/relationship-profiles.json` — real,
  founder-tracked people and their upcoming conferences.
- `account-intelligence/runtime/config/supporting-assets.json` and
  `.../account-intelligence-config.json`'s `categoryToDomainTags` —
  the same real product/resource catalogue and category-to-tag bridge
  Account Intelligence's own Supporting Assets section already uses.

## The Weekly Brand Plan

| Field | Sourced from |
|---|---|
| Companies to Engage | Top organisations this week by `buyingReadinessScore` (Demand Intelligence's own field, never re-scored) |
| Executives to Follow | Every real person in `relationship-profiles.json` — never a fabricated name |
| Topics to Write / Newsletter Themes | The most common governance risk across this week's Account Intelligence briefs, and the most common demand-signal category, each cited with its real count |
| Products to Update | The shared supporting-assets catalogue, re-ranked by domain-tag overlap with this week's trending category |
| Whitepapers to Publish | The same catalogue, filtered to Whitepaper/Playbook-type items |
| Conferences to Monitor | `relationship-profiles.json`'s own `upcomingConference` fields, deduplicated by name |
| GitHub Improvements | One honest, evidence-cited suggestion tied to this week's trending risk/domain — never a claim about the repo's actual state (no GitHub API integration) |
| LinkedIn Strategy | This week's most common Account Intelligence outreach strategy, cited with its real count |

**Estimates** (Visibility Impact, Lead Generation Potential, Expected
Consulting Influence) are explicit heuristics tiered from real counts
(companies this week, high-readiness companies, High-confidence
service-fit matches) — never an arbitrary number, and always labelled
a heuristic.

## Persistence

Every week's plan is appended to `brand-plan-history.json` (re-running
the same week replaces that week's own entry rather than duplicating
it). The Monthly Authority Report rolls up the trailing
`monthlyWindowDays` (30 by default) of history: weeks included, most
common domain/risk, and total distinct companies engaged. Honestly
reports "not enough weekly history yet" with fewer than one week.

## Dashboard

**Executive Brand Intelligence** page: this week's Weekly Brand Plan
in full, and a Monthly Authority Report rollup.

## What This Engine Does Not Do

- Does not invent a person, conference, product, or governance risk —
  every one of those is read from another employee's own real,
  already-computed or founder-maintained data.
- Does not claim knowledge of the actual GitHub repository's state
  (stars, issues, commit history) or the actual LinkedIn account's
  performance — AOS has no integration with either. Its GitHub/
  LinkedIn suggestions are evidence-cited editorial recommendations,
  not status reports.
- Does not modify any other employee's data — read-only across all
  four input sources.
