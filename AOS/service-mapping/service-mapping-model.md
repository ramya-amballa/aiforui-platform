# Service Mapping Engine — Model

How every opportunity becomes a consulting-engagement recommendation:
Primary Service, Secondary Services, Recommended Engagement Type,
Estimated Project Size, Recommended Proposal Template, and Cross-Sell
Opportunities. Every rule below is implemented, in this order, in
`runtime/generate.py`; the actual lookup tables live in
`runtime/config/service-catalogue.json` so retuning any of this is a
config edit, never a code change.

**Deterministic by design.** Nothing here calls an LLM, makes a
network request, or uses randomness. The same opportunity, run twice,
always produces the same recommendation — a requirement stated
explicitly in the sprint that commissioned this engine, and enforced
by construction: every decision is a lookup against
`opportunity-schema.json`'s own real fields (`domainTags`,
`classification`, `scopedEngagement`, `sourceCategory`, `scores`,
`title`/`description`) plus, optionally, a real figure already present
in `pipeline.json` or `company-intelligence.json`.

## 1. Primary Service

First matching rule wins, checked in this order:

1. `Fractional Advisory` in `domainTags`, or the title/description
   matches a fractional/interim keyword → **Fractional AI Governance
   Lead**. This is about the *shape* of the engagement (an ongoing,
   part-time leadership role), not a domain, so it's checked before
   anything domain-specific.
2. `ADGL` or `AI Deployment Governance` in `domainTags` → **AI
   Deployment Governance (ADGL)**.
3. `Third-Party Risk` in `domainTags` → **AI Third-Party Risk Review**.
4. `DORA`, `EU AI Act`, or `Government/FedRAMP-GovRAMP-CMMC` in
   `domainTags` — a named regulatory regime is in play: **AI Policy &
   Control Framework** if `scopedEngagement` is true (they already
   know what needs building), else **AI Readiness Assessment** (find
   out where they stand first).
5. `GRC` in `domainTags` → **AI Governance Operating Model** (GRC's
   connotation across AI for U&I's own real engagement history is
   ownership and decision-rights work, not a standalone risk review).
6. `Security Governance` or `Technology Risk` in `domainTags` → **AI
   Risk Assessment**.
7. `AI Governance` in `domainTags` (nothing more specific already
   matched) → **Responsible AI Implementation** if `scopedEngagement`
   is true, else **AI Governance Advisory**.
8. `sourceCategory` is `Consulting Channel` (subcontracted/whitelabel
   capacity, no domain tag to go on) → **AI Governance Advisory**.
9. Title/description matches a workshop/keynote/training keyword →
   **Executive Workshop**.
10. Nothing above matched → **AI Readiness Assessment** — the
    conservative default: when nothing more specific is known yet,
    recommending a first assessment is always defensible, never an
    overreach.

Three classifications are explicitly excluded from Primary Service
mapping, not force-fit into one: `Ignore`, `Convert into Content`, and
`Convert into Product Idea`. The first isn't going anywhere; the other
two are Content Director's and Product Manager's own decisions
already — mapping them to a consulting service here would be a second,
possibly conflicting opinion about a signal another employee already
owns. These get a `notApplicable: true` record with a reason instead.

## 2. Secondary Services

A fixed, three-step chain per Primary Service
(`secondaryServiceChains` in the catalogue) — the natural *depth*
extensions of the same engagement, not a different sales pitch. The
ADGL chain (`AI Governance Operating Model → AI Control Library →
Fractional Governance Support`) is the founder's own example from the
sprint that commissioned this engine, used verbatim; the other nine
chains follow the same logic (an assessment leads to a framework, a
framework leads to fractional ongoing support) using AI for U&I's real
existing deliverable vocabulary (`templates/proposals/README.md`'s
Governance Charter/Operating Model/RACI Matrix/Risk Register/Evidence
Register/etc.) and the other nine Primary Services as candidates,
never an invented one-off term.

"AI Control Library" and "Fractional Governance Support" are
deliberately *not* required to be verbatim Primary Service names —
they're one level more specific, matching the founder's own example,
which itself doesn't reuse the Primary Service list verbatim either
(compare "Fractional Governance Support" here against "Fractional AI
Governance Lead" as a Primary Service).

## 3. Recommended Engagement Type

Checked in this order:

1. A CRM record exists for this organisation with `existingRelationship
   == "active client"` → **Retainer** — an existing paying relationship
   overrides everything else about engagement shape, regardless of
   Primary Service.
2. Primary Service is **Fractional AI Governance Lead** → **Fractional
   consulting**.
3. Primary Service is **Executive Workshop** → **Training** if the
   title/description specifically matches a training keyword, else
   **Discovery workshop**.
4. Primary Service is **AI Readiness Assessment** → **Discovery
   workshop**.
5. `scopedEngagement` is true → **Fixed-price project**.
6. `classification` is `Relationship Building` → **Advisory
   engagement**.
7. Default → **Advisory engagement**.

## 4. Estimated Project Size

**Real revenue first.** If `08-Revenue-Hunter/pipeline.json` already
has a parseable `expectedRevenue` for this opportunity (via
`sourceRef`), that real figure — parsed with `parse_currency()`,
reused verbatim from `executive-dashboard/runtime/generate.py` — is
banded against `projectSizeRevenueThresholds` (adjustable, documented
defaults: ≤5,000 Small, ≤25,000 Medium, ≤100,000 Large, above
Enterprise). Thresholds apply to the raw parsed number regardless of
currency label — the same simplification `executive-dashboard`'s own
revenue section already accepts for mixed-currency figures, not a new
gap this engine introduces. `projectSizeBasis` is recorded as
`"pipeline-revenue"` whenever this path is taken.

**Heuristic fallback**, when no real figure exists yet (`projectSizeBasis:
"heuristic-estimate"`): each Primary Service has a documented, adjustable
default band (`projectSizeDefaultByPrimaryService` — e.g. Executive
Workshop defaults Small, Fractional AI Governance Lead defaults
Enterprise, reflecting each service's typical real-world scale), then
adjusted by the opportunity's own `scores.expectedRevenue` (the 0-10
dimension every opportunity already has, real or heuristic per its own
`autoScored` flag): a score of 8 or above bumps one band up, 2 or below
bumps one band down, capped at Small/Enterprise. This never invents a
dollar figure — it only ever reuses a 0-10 judgement that already
exists on the record.

## 5. Recommended Proposal Template

A domain-tag match to one of `templates/proposals/`'s nine real
templates is checked first and wins whenever present (`DORA` → the
DORA template, `EU AI Act` → the EU AI Act template, `Security
Governance` → the security governance template) — these are more
specific than any Primary Service default. Otherwise, a fixed
Primary-Service-to-template default applies
(`proposalTemplateByPrimaryService`). No template is invented — every
value is a real filename that already exists in
`templates/proposals/`.

## 6. Cross-Sell Opportunities

Two real sources, combined:

1. **One complementary Primary Service** (`crossSellComplement`), chosen
   to be genuinely different in shape from the current one (an
   assessment-led engagement cross-sells a workshop; a workshop
   cross-sells an assessment) rather than repeating the Secondary
   Services chain.
2. **Up to two real products** from
   `sales-director/runtime/config/practitioner-bank.json`'s existing
   product catalogue whose `domainTags` overlap this opportunity's own
   — the same tag-match selection `sales-director/runtime/prepare.py`
   already uses for its own content bank, reused rather than
   reinvented, so no product is ever invented here that doesn't
   already exist in that catalogue.

## Worked Example

An `Immediate Proposal`-classified opportunity tagged `["ADGL", "AI
Deployment Governance"]`, `scopedEngagement: true`, with no existing
pipeline entry and `scores.expectedRevenue: 9`:

- **Primary Service:** AI Deployment Governance (ADGL) — rule 2.
- **Secondary Services:** AI Governance Operating Model → AI Control
  Library → Fractional Governance Support.
- **Engagement Type:** Fixed-price project — `scopedEngagement` is
  true, no active-client CRM override.
- **Project Size:** no real pipeline revenue yet, so heuristic: ADGL's
  default is Large, and `scores.expectedRevenue` of 9 (≥8) bumps it to
  **Enterprise**.
- **Proposal Template:** no DORA/EU AI Act/Security Governance tag, so
  the Primary Service default applies: `ai-governance-proposal-template.md`.
- **Cross-Sell:** Executive Workshop, plus any real product in the
  bank tagged ADGL or AI Deployment Governance.

This is exactly the scenario `runtime/tests/test_service_mapping.py`
exercises, alongside every other rule branch, against realistic
fixtures rather than production data.

## Assumptions vs. Verified Behaviour

**Verified** (tested against fixtures covering every rule branch, and
against a full 9→11-step Orchestrator run): every rule listed above
fires exactly as documented; `service-recommendations.json` is
idempotent (a second run with no new opportunities changes nothing);
none of `opportunity-schema.json`, `pipeline.json`, or
`company-intelligence.json` is ever written to (confirmed by an
md5sum before/after check).

**Assumptions, not verified facts** — documented here so they're easy
to revisit, not silently baked in:

- The exact Primary Service decision order (e.g., that a `GRC` tag
  should default to Operating Model work rather than a Risk
  Assessment) reflects a reasonable reading of AI for U&I's real
  advisory-engagement history (`aiforu-platform/src/content/
  advisory-engagements.ts`), not a rule the founder has explicitly
  confirmed rule-by-rule.
- The project-size revenue thresholds (5,000 / 25,000 / 100,000) are a
  first, adjustable starting point, the same kind of documented
  default `sales-director/runtime/config/rate-card.json` already uses
  — not a verified pricing reality yet.
- The Secondary Services and Cross-Sell chains for the nine Primary
  Services other than ADGL are this engine's own reasonable extension
  of the founder's ADGL example, not independently confirmed for each
  of the other nine.

## What This Engine Does Not Do

- Does not change Opportunity Hunter's collection, relevance
  filtering, scoring, or classification — `ingest.py` is untouched.
- Does not change Revenue Hunter's scoring or forecasting logic —
  `pipeline.json` is read, never written.
- Does not change CRM — `company-intelligence.json` is read, never
  written.
- Does not send, publish, or build anything automatically — every
  output is a recommendation on disk for Sales Director and the
  founder to act on by hand.
