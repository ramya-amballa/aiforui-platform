# Editorial Tooling

Deterministic tools for maintainers authoring and reviewing canonical knowledge. These exist to improve the **quality and consistency** of contributions — none of them automate editorial judgment. Every tool either produces a non-canonical draft a human must review, or prints an advisory report; none of them writes to `/data` or decides confidence/status on a maintainer's behalf.

Run all commands from `/workbench` (after `npm install`).

## Incident Authoring Wizard

```sh
npm run editorial:wizard
```

Interactively builds a schema-valid draft incident (`/ingestion/drafts/draft-incident-<slug>.json`) by prompting for each field, validating dates/enums as you go, and running the full `draft-incident.schema.json` check before writing. It always leaves `human_review.status: "pending"` — it never approves anything. See `/docs/ingestion-pipeline.md` for what happens next.

## Relationship Suggestion Engine

```sh
npm run editorial:suggest [-- --id=DEC-001]
```

Rule-based (not generative) candidate-relationship finder. Every suggestion traces to one of a small set of named, explainable heuristics — tag overlap, incident harm-type matching a control's tags, shared `ai_system_category` between incidents implying a shared Decision/Pattern/Control, jurisdiction matching a control's framework, and orphan-risk prevention. It never proposes a triple the ontology wouldn't allow, and it never writes anything — it prints suggestions with a score and rationale for a maintainer to accept, reject, or use as a starting point (adding the real `reason` themselves).

## Citation Completeness Checker

```sh
npm run editorial:citations
```

Scores every object's citations (0-100) on completeness — not on whether a citation exists at all (`/validators` already enforces that), but on how usable it is: does it have a `url`, a `locator`, an `excerpt`; is more than one `source_type` represented; are relationships actually linked to a supporting `citation_id`; are any citations old enough to warrant re-verifying. Prints per-object findings plus a dataset average. Advisory only.

## Coverage Metrics Dashboard

```sh
npm run editorial:coverage [-- --out=coverage-report.md]
```

Reports what the dataset actually covers: entity counts, a **Coverage Matrix** (a markdown table, one row per entity type, showing objects/outbound/inbound/avg-degree/orphans and flagging any type as `⚠ SPARSE` when its average degree falls below 2 or it contains an orphan — so you can see at a glance which of the 6 entity types need more linking, not just more objects), incidents by harm type / jurisdiction / AI system category / severity, controls by framework (and which well-known frameworks — EU AI Act, GDPR, NIST AI RMF, ISO/IEC 42001, NYC LL144, BIPA, FCRA, FTC Act, EEOC — have zero controls yet), confidence and status distributions, relationship-verb usage, and decisions with no incident grounding them. This is the tool to run before selecting new incidents, to see which governance concepts are under-represented — see `/docs/foundational-twenty.md` for how it shaped that selection.

## Graph Health Report

```sh
npm run editorial:health
```

Reports whether the graph is structurally and qualitatively sound: re-runs the actual `/validators` rules (so it can never disagree with `npm run validate` about what's an error), a dedicated **Zero-Orphan Invariant** check (every object with zero relationships is listed individually as an `ERROR` — an isolated node is invisible in a knowledge graph, so this is a hard gate: the command exits non-zero if any orphan exists, independent of and in addition to `/validators`' own orphan check), near-orphan/fragility counts, outbound-edge-limit pressure, verb-usage balance (flags ontology verbs that are never used), confidence maturity (% Verified/Reviewed vs. Draft/Community), and a citation-completeness summary — combined into a single weighted composite health score. Contrast with the Coverage Dashboard: coverage asks "what topics do we cover," health asks "is the graph itself in good shape."

## Editorial Analytics

```sh
npm run editorial:insights [-- --out=insights-report.md]
```

The graph explaining itself, computed entirely from canonical `/data` — no generated commentary, no opinion layered on top. Reports: the most frequently invoked Governance Decisions (by incident count), Design Pattern reuse frequency (which patterns more than one Decision implements — the dataset's own signal for which governance responses are genuinely recurring, not one-off), highest-confidence Decisions (with an explicit note on why `Verified` is rare), weakly-covered governance areas (harm types, jurisdictions, AI system categories with thin representation), top tags by frequency as a proxy for emerging themes, cross-framework overlap (evidence types required by controls from more than one distinct framework — where independent regulators converge on the same observable artifact), and incident clusters (incidents grouped by the Decision they share). This is a reporting tool, not a platform feature — no UI, no visualization, no export engine, consistent with the Phase 2 infrastructure freeze.

## Design notes

- All six tools share `src/lib/graph.ts`, which reuses the exact loaders `/validators` uses (`loadAllData`, `loadOntology`) — "the graph" means the same thing everywhere in this codebase.
- `graph-health.ts` imports the real rule functions from `/validators/src/rules` rather than re-implementing structural checks, so the two can't silently drift apart.
- None of these tools has a write path into `/data`. The wizard writes only to `/ingestion/drafts`, which is non-canonical by construction (see `/docs/ingestion-pipeline.md`).
