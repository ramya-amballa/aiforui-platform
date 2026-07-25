# Demand Intelligence v2 — Consulting Demand Engine (AOS Sprint 6)

How Demand Intelligence answers "which organisations are most likely
to need AI for U&I's services this week, and why" — built on top of
Sprint 5's Demand Signals connector without changing its architecture,
its RSS feeds, or the one non-deterministic step it already had
(Claude confirming a named organisation from an article). Everything
in this document is implemented in `runtime/demand_engine.py`; the
lookup tables live in `runtime/config/demand-signal-categories.json`.

## What Changed Versus Sprint 5

Sprint 5's `collectors/demand_signals.py` only ever looked for one
kind of event — a named organisation adopting an AI tool at scale —
and every signal that passed got the same fixed scores regardless of
strength. Sprint 6 replaces both of those:

- **Five deterministic categories**, not one (Part 1 below), decided
  by keyword matching against the article's own text — no model call
  needed to know *which* category applies, only to confirm *which
  organisation* the article is about.
- **Differentiated scoring**: a weak signal now genuinely scores lower
  through `ingest.py`'s existing, completely unmodified
  `compute_priority_score()`/`classify()` than a strong one — not a
  one-size-fits-all constant.

## Part 1 — Demand Signal Classification

Five categories, each with a base score and a keyword list
(`config/demand-signal-categories.json`'s `categories`), matched
case-insensitively, whole-phrase, against an article's title+summary —
the same convention `opportunity-relevance-engine.md` and Market
Intelligence's six checks already use:

| Category | Base Score | Example trigger |
|---|---|---|
| AI Adoption | 70 | Microsoft Copilot rollout, ChatGPT Enterprise deployment, RAG implementation |
| Governance Trigger | 85 | Chief AI Officer appointment, AI ethics committee, AI governance framework |
| Funding Trigger | 75 | Series A/B/C, AI expansion funding |
| Regulatory Trigger | 95 | EU AI Act preparation, ISO 42001, DORA, CBUAE AI Principles, NIST AI RMF |
| Failure Trigger | 100 | AI incident, AI bias, data leakage, AI lawsuit |

An organisation can match more than one category (from the same
article or across several, over time). **Overall Demand Score**
(`demand_engine.compute_overall_demand_score()`) is a weighted
aggregation: the highest-scoring matched category counts in full,
every additional matched category adds a smaller weighted share
(`aggregationWeights.additionalCategoryWeight`, default 0.35) — capped
at 100 — scaled by extraction confidence
(`confidenceMultiplier`) and Part 8's deterministic feedback
multiplier.

Classification into these five categories is 100% keyword-based, run
on every article regardless of whether Claude is even configured.
Claude only enters once a category has already matched, to confirm a
real, specific named organisation is what the article is about and
extract it (`claude_client.extract_demand_signal`) — the one
non-deterministic step, unchanged in kind from Sprint 5, just widened
in scope from "AI adoption articles only" to "any of the five
categories' matched articles."

## Part 2 — Opportunity Narrative

`demand_engine.build_opportunity_narrative()` — a fixed template, not
a second model call: the extracted factual event sentence, a
category-keyed "organisations at this stage typically require..."
clause (`governanceNeedByCategory`), the ranked service list from Part
3 as bullets, and a `Confidence:` line. No superlatives, no marketing
language — a unit test (`test_no_marketing_superlatives`) checks for
exactly that.

## Part 3 — Consulting Need Prediction

`demand_engine.predict_services()` ranks Service Mapping Engine's own
canonical `primaryServices`
(`service-mapping/runtime/config/service-catalogue.json`) — reused, not
a second taxonomy — per matched category
(`categoryToServices`), with services suggested by more than one
matched category ranking above a single-category mention. Where the
founder's brief used a close synonym of an existing canonical name
(e.g. "ADGL Readiness Assessment", "AI Compliance Assessment"), the
closest existing Service Mapping entry is used instead, so every part
of AOS names services the same way.

## Part 4 — Buying Readiness Score

`demand_engine.compute_buying_readiness_score()` — a 0-100 deterministic
weighted formula (`buyingReadinessWeights`) over deployment stage,
organisation size (from any scale figure Claude extracted, e.g.
"40,000 employees" — an honest neutral default when none is stated),
regulatory pressure, public AI maturity, whether a governance trigger
is present, strategic importance (derived from the Overall Demand
Score), and urgency (highest for Failure Trigger). Bucketed into Low /
Medium / High / Very High (`buyingReadinessBands`).

## Part 5 — Recommended Next Action

`demand_engine.recommend_next_action()` — deterministic rules, not a
drafted email: low-confidence signals always `Wait`; a Failure Trigger
always `Prepare Proposal` regardless of band (the highest-urgency
category warrants skipping straight past monitoring); a Regulatory
Trigger at High/Very High band gets `Schedule Outreach`; otherwise a
straight band → action lookup (`nextActionByBand`: Very High →
Schedule Outreach, High → Prepare Executive Brief, Medium → Prepare
Insight Article, Low → Monitor), each with a one-line, deterministically
constructed reason.

## Scores Handed to ingest.py's Unmodified Pipeline

`demand_engine.opportunity_scores_from_result()` builds the same
eleven-dimension `scores` dict every opportunity already has — a real
function of this signal's own Overall Demand Score, Buying Readiness
Score, and matched categories, not a fixed constant. Whether the
opportunity is `scopedEngagement: true` (which `ingest.py`'s existing
`classify()` then routes to "Immediate Proposal") is decided by
actually calling `ingest.compute_priority_score()` on these scores and
checking whether it clears the Priority band (>=80) — never an
independently-thresholded guess that could disagree with what
`ingest.py` itself computes. (An earlier version of this function
derived `scopedEngagement` from this module's own buying-readiness
band instead, and produced signals that satisfied neither of
`classify()`'s branches, silently falling through to the "Apply"
default meant for plain job postings —
`tests/test_demand_engine.py`'s `ScopedEngagementConsistencyTests`
exists specifically to catch that regression again.)

No change was made to `ingest.py`'s scoring formula, classification
decision tree, or routing — every dimension above is real input to
that same unmodified engine.

## Part 6 — CEO Advisor Integration

`demand_engine.write_top_organisations_feed()` writes every
organisation with a signal in the last 7 days to
`runtime/output/top-organisations-this-week.json` — raw, unranked.
`ceo-advisor/runtime/generate.py`'s new
`candidates_from_demand_intelligence_organisations()` +
`top_organisations_this_week()` do the actual ranking, reusing CEO
Advisor's own existing `rank_candidates()`/`top_priorities_with_reasons()`
(the same urgency-weighted, tie-break logic and "why this outranks the
next" reasoning every other candidate source already goes through —
not a second ranking algorithm). The result is a new, additive "## Top
10 Organizations This Week" section in the CEO Daily Report: rank,
organisation, demand signal, buying score, recommended service,
recommended action, estimated strategic value, and why it outranks the
next — plus each organisation's full Opportunity Narrative underneath.
This is a separate pool from CEO Advisor's existing Top 3 Priorities
(which already includes any Demand-Signal-sourced opportunity that
reached the Priority band in `opportunity-schema.json` via
`candidates_from_demand_intelligence()`) — Part 6 is organisation-level
consulting-demand analysis that file has no room for, not a duplicate
of what Top 3 Priorities already surfaces.

## Part 7 — Dashboard

The Command Center's Demand Intelligence page gained a "Consulting
Demand Engine" tab: every organisation ever identified, with filters
for Industry, Region, Signal Type, Buying Score band and Service, a
Top Organizations table, and each organisation's full Opportunity
Narrative on selection. Reads `organisation-profiles.json` directly
(read-only, same as every other dashboard page) — never re-derives or
duplicates the scoring above.

## Part 8 — Learning (Deterministic, Not Machine Learning)

Every organisation's profile in `organisation-profiles.json` tracks
`outreachHappened`, `proposalCreated`, `converted`, and
`revenueGenerated` — refreshed every run
(`demand_engine.refresh_feedback_for_all_profiles()`) by reading CRM's
`outreachHistory`, Sales Director's `ceo-advisor-feed.json`, and
Revenue Hunter's `pipeline.json` stage — read-only cross-references,
never a second copy of their data, and one cycle behind on the same
day those employees write it (the same limitation CRM's own read of
Sales Director's state already has, documented in
`crm-runtime-notes.md`).

The actual "improve future scoring" mechanism is
`demand_engine.category_conversion_multiplier()`: a bounded,
deterministic multiplier (0.7-1.20) on a *category's* future base
score, driven only by what genuinely happened to past organisations
matching that category — +0.05 per converted opportunity (capped
+0.20), -0.03 per opportunity where outreach happened but nothing
progressed for 90+ days (capped -0.15). No model is trained; the
multiplier is always fully auditable by reading
`organisation-profiles.json` alone, and every input to it already
exists as real, already-written AOS data.

## What This Sprint Deliberately Does Not Do

- Does not change `ingest.py`'s scoring formula, classification
  decision tree, or routing logic — every score Sprint 6 computes is
  input to that same unmodified engine.
- Does not introduce a second service taxonomy — Part 3's predictions
  are Service Mapping Engine's own canonical service names.
- Does not introduce a second ranking algorithm for CEO Advisor's Top
  10 Organizations — that reuses CEO Advisor's own existing
  `rank_candidates()`.
- Does not use machine learning for Part 8 — `category_conversion_multiplier()`
  is a fixed, auditable formula over real historical outcomes, not a
  trained model.
- Does not draft or send outreach — Part 5 recommends a next action
  and states why; a human still writes anything that gets sent.
