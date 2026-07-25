# Service Mapping Engine (v1.0)

Turns "an opportunity was found" into "here is the consulting
engagement it should become." For every opportunity in
`demand-intelligence/opportunity-schema.json`, deterministically
computes: Primary Service, Secondary Services, Recommended Engagement
Type, Estimated Project Size, Recommended Proposal Template, and
Cross-Sell Opportunities.

Introduced in AOS Sprint 3, after Demand Intelligence, Revenue Hunter
and Sales Director were already live. This engine does not change any
of them — it reads Demand Intelligence's schema read-only, and Sales
Director reads this engine's output read-only in turn.

## Files

- `service-mapping-model.md` — the full decision model: every rule,
  in the exact order it's checked, a worked example, and which parts
  are verified behaviour versus a documented, adjustable assumption
- `service-recommendations.json` — the persisted record, one entry per
  opportunity, schema documented in the file itself
- `runtime/generate.py` — the engine
- `runtime/config/service-catalogue.json` — every lookup table
  (Primary Service keywords, Secondary Service chains, engagement type
  rules, project size bands and thresholds, proposal template mapping,
  cross-sell pairings) — edit this to retune recommendations, no code
  change needed
- `runtime/tests/test_service_mapping.py` — unit tests for every rule
  branch, run against fixtures, never against real data

## How It Fits AOS

- **Reads from:** `demand-intelligence/opportunity-schema.json`
  (required), `08-Revenue-Hunter/pipeline.json` and
  `06-CRM/company-intelligence.json` (both optional enrichment only —
  a real revenue figure or an active-client relationship, when
  present, overrides a heuristic default) — all three read-only
- **Writes to:** `service-recommendations.json`, `runtime/output/`,
  `runtime/logs/` only
- **Read by:** `sales-director/runtime/prepare.py`, which surfaces the
  recommended proposal template, engagement type, project size and
  cross-sell opportunities in every package it prepares — Sales
  Director's own cover-letter, proposal, pricing and confidence-score
  logic is unchanged; this is an additive section in its output

## What This Is Not

Not a second scoring or classification engine — `opportunity-schema.json`'s
own `priorityScore`, `band` and `classification` are read as-is, never
recomputed. Not a redesign of Revenue Hunter or CRM — both are read
read-only and never written to. Not an outbound tool — nothing here
drafts or sends anything; every recommendation is a label for Sales
Director and the founder to act on.

Start with `service-mapping-model.md`.
