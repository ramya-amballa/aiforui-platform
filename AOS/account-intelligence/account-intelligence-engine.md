# Account Intelligence Engine (AOS Sprint 8)

For every organisation Demand Intelligence has already qualified,
generates a ten-section Executive Account Intelligence Brief — an
internal strategic briefing to prepare AI for U&I before any outreach,
**not** a proposal. Additive and downstream only: it never modifies
`demand-intelligence/organisation-profiles.json` or any other
employee's output, and Demand Intelligence's own collection/scoring
pipeline is completely unaffected by whether this employee has ever
run. Implemented in `runtime/account_intelligence_engine.py` (the ten
section builders) and `runtime/generate.py` (the orchestrator-invoked
entry point); lookup tables live in
`runtime/config/account-intelligence-config.json` and
`runtime/config/supporting-assets.json`.

## What "Qualified" Means

Every key in `demand-intelligence/organisation-profiles.json`'s
`organisations` dict — the same high-confidence gate
`collectors/demand_signals.py` already applies before a signal is ever
recorded there. No second, independent qualification threshold is
invented; an organisation is qualified the moment Demand Intelligence
itself already considers it real.

## Regenerated in Full, Every Run

Unlike Sales Director's one-time-per-opportunity proposal packages, a
brief is meant to always reflect the *latest* signal picture for that
organisation, and regenerating one is cheap (no model call, no network
access) — so every qualified organisation's brief is rewritten on every
run, not gated by a processed-index.

## The Ten Sections

1. **Company Profile** — industry/scale/region read directly from the
   organisation's profile; regulatory environment inferred from region
   via a new lookup table; AI maturity level and business priorities
   both derived from its single strongest matched category (same
   baseScore-descending order `demand_engine.py`'s own
   `compute_overall_demand_score()` already uses to pick the "primary"
   category — never a second, independently-invented ranking).
   Headquarters is honestly reported as not captured, since Demand
   Signals' extraction never records it.
2. **AI Deployment Intelligence** — technologies/categories, stage and
   strategic objective from a new per-category label table; scale from
   the profile; vendors involved detected by a real text match against
   a credited, verbatim copy of `extractors/base.py`'s
   `VENDOR_BLOCKLIST` (reused for the opposite purpose here — detecting
   a vendor mentioned, not excluding one from being mistaken for the
   organisation); public announcements are literally the organisation's
   own recorded signals (date, summary, source URL), never rephrased.
3. **Governance Risk Assessment** — which of nine canonical risk items
   (Human oversight, Model governance, Operational controls, Privacy,
   Third-party AI risk, Monitoring, Incident management, Audit
   evidence, Regulatory readiness) are likely relevant, per matched
   category, each with a factual why-explanation naming the
   organisation. An organisation matching several categories gets the
   union, de-duplicated.
4. **Service Fit** — reuses `demand_engine.py`'s own
   `recommendedServices` verbatim (Sprint 6, Part 3's already-ranked,
   vote-count-based prediction) — never a second service-ranking
   algorithm. Confidence is a plain read of rank position: 1st = High,
   2nd = Medium, 3rd+ = Low.
5. **Decision Makers** — titles only, **never invented names**, from a
   new per-category stakeholder-title table (Chief AI Officer, Head of
   AI, Chief Data Officer, Chief Risk Officer, Head of Technology Risk,
   Director Responsible AI, Head Model Risk, Head Digital
   Transformation, CISO), aggregated across matched categories and
   de-duplicated.
6. **Outreach Strategy** — a six-value vocabulary (Wait, Connection
   first, Thought leadership, Discovery workshop, Direct proposal,
   Monitor) answering a different question than Demand Intelligence's
   own `recommendedAction`: that field is Demand Intelligence's next
   *internal pipeline* action; this is how the *first touch* with this
   organisation should be framed. Both are deterministic re-labellings
   of the exact same already-computed `buyingReadinessBand`/confidence/
   matched-categories fields — no new score is computed here. All six
   values are genuinely reachable (see
   `tests/test_account_intelligence_engine.py`'s `OutreachStrategyTests`
   — a design smell this suite specifically guards against is a
   vocabulary option that can never actually be produced).
7. **Conversation Starters** — exactly three, professional and
   non-salesy, from category-specific templates (falling back to
   generic templates when fewer than three categories are matched),
   parameterised only by the organisation's own name — never a drafted
   sales pitch.
8. **Supporting Assets** — ranked by real domain-tag overlap against a
   real, existing catalogue (`config/supporting-assets.json`, copied
   verbatim from `sales-director/runtime/config/practitioner-bank.json`'s
   products and `aiforu-platform/src/lib/constants.ts`'s real website
   routes/LinkedIn/Substack/GitHub links — the actual deployed site,
   not a placeholder). An asset with zero domain-tag overlap and not
   marked general is never shown; general assets (LinkedIn, Substack,
   GitHub, the Insights index) only fill out the list when fewer than
   the max show up from a genuine match, never ranked above one.
9. **Opportunity Scorecard** — reuses a real
   `opportunity-schema.json` record's own already-scored 11-dimension
   scores and `priorityScore` (from `ingest.py`'s unmodified scoring
   engine) when this organisation has one, rather than a second,
   independent estimate; falls back to a Buying-Readiness-Score-derived
   estimate, clearly labelled as such, when no opportunity record
   exists yet. Estimated Sales Cycle and Competition Risk are this
   engine's own honest heuristics (sales cycle from buying-readiness
   band; competition risk from how many public signals are on
   record) — documented as heuristics, not market-intelligence claims.
10. **Executive Summary** — a fixed template, always word-count-capped
    at 300 (enforced in code, not just usually satisfied by short
    templates — see `ExecutiveSummaryTests.test_never_exceeds_300_words`),
    designed so CEO Advisor (or the founder directly) can read it
    without opening the rest of the brief.

## Reuse, Not Duplication

- Service Fit is `demand_engine.py`'s own `recommendedServices`,
  unchanged.
- The vendor-detection list is a credited, verbatim copy of
  `extractors/base.py`'s `VENDOR_BLOCKLIST`.
- The Supporting Assets catalogue is a credited, verbatim copy of two
  real, already-existing sources (`practitioner-bank.json`,
  `constants.ts`), not an invented third content bank.
- The Opportunity Scorecard prefers a real `opportunity-schema.json`
  record's own scores over a second estimate whenever one exists.
- Outreach Strategy and AI maturity/deployment-stage labels are
  re-labellings of fields Demand Intelligence already computed
  (`buyingReadinessBand`, confidence, matched categories,
  `baseScore`-based category ordering) — no new score is computed by
  this employee anywhere.

## What This Sprint Deliberately Does Not Do

- Does not modify `demand-intelligence/organisation-profiles.json`,
  `opportunity-schema.json`, or any other employee's output — every
  read is read-only, exactly like CRM's read of Sales Director's feed
  or `demand_engine.py`'s own Part 8 feedback weighting.
- Does not invent a decision-maker's name — Section 5 is titles only.
- Does not draft or send outreach — Section 6/7 recommend an approach
  and suggest openers; a human still writes and sends anything real.
- Does not fabricate a supporting asset, an AI vendor, a headquarters
  location, or a regulatory jurisdiction beyond what the organisation's
  own signals and Demand Intelligence's own region inference already
  established — every "Not specified"/"Not enough signal" is left
  honest rather than guessed.
- Does not wire into CEO Advisor's own report in this sprint — it is
  listed in CEO Advisor's `dependsOn` for run-ordering only (so it
  finishes before CEO Advisor's own, unrelated, always-final run),
  matching the same pattern Product Manager and Content Director
  already use.

## Dashboard

The Command Center's new **Account Intelligence** page: a "Generate
Briefs" button, a searchable-by-company table of every qualified
organisation (industry, region, buying-readiness band, outreach
strategy, overall priority, last seen), and the full ten-section brief
for whichever organisation is selected, with a Download button. Reads
`account-intelligence-feed.json` and the individual brief files
directly (read-only, same as every other dashboard page) — never
re-derives or duplicates the scoring above.
