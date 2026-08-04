# AI Governance Workbench

A data-first, schema-driven knowledge graph for AI governance — organised around **Governance Decisions**, the way MDN Web Docs organises web platform knowledge, Refactoring.Guru organises design patterns, and MITRE ATT&CK organises adversary tactics. Not a new governance framework; a searchable, interconnected reference built from real-world governance decisions, incidents, patterns, controls, evidence, and board-level questions.

**This is independent of AOS.** AOS (elsewhere in this repository) is the flagship consulting operating system used to run engagements. The Workbench is a separate, public knowledge platform aimed at building industry authority — nothing here depends on AOS, and nothing in AOS should come to depend on this without a deliberate integration decision.

This is **Phase 1 + Phase 2A**: the data foundation, the editorial tooling that keeps future contributions consistent, and a seed dataset (the "Foundational Twenty"). No frontend, dashboard, search page, or graph visualisation is built yet — see [`ONTOLOGY.md`](ONTOLOGY.md) for the Canonical Principle this is built on, and [`/docs/architecture.md`](docs/architecture.md) for the fuller reasoning.

## What's here

```
/workbench
  ONTOLOGY.md     The constitution: every core term defined in one place
  /schemas        JSON Schema for the 6 canonical entity types + shared building blocks
  /data           The canonical dataset (one JSON file per object)
  /relationships  The machine-readable relationship ontology
  /validators     The validation engine (TypeScript + ajv) — the merge gate
  /editorial      Deterministic authoring/QA tools for maintainers (wizard, suggestions, coverage, health)
  /ingestion      The draft -> human review -> canonical pipeline for Incidents
  /search         Reserved for a future search index (empty)
  /docs           Full documentation set (start here for the "why" behind everything)
```

## Quick start

```sh
cd workbench
npm install
npm run validate           # validate the whole dataset — the merge gate
npm run typecheck          # type-check the validator/ingestion/editorial TypeScript
npm run editorial:coverage # what governance concepts does the dataset cover, and where are the gaps?
npm run editorial:health   # is the graph structurally and qualitatively sound?
```

## The six canonical entity types

Governance Decision (`DEC-`), Incident (`INC-`), Design Pattern (`PAT-`), Framework Control (`CTR-`), Evidence Type (`EVI-`), Board Question (`BRD-`) — deterministic, sequential IDs, never UUIDs. Every object also carries a permanent, human-readable `slug` for future URLs. See [`ONTOLOGY.md`](ONTOLOGY.md) for the full glossary and [`/docs/schemas.md`](docs/schemas.md) for the field-by-field reference.

## Documentation

- [`ONTOLOGY.md`](ONTOLOGY.md) — the constitution: the Canonical Principle, the AI-authorship rule, and every core term defined in one place
- [`architecture.md`](docs/architecture.md) — the reasoning behind every major design decision
- [`schemas.md`](docs/schemas.md) — field-by-field reference for all six entity schemas
- [`relationship-model.md`](docs/relationship-model.md) — the relationship ontology, mandatory edge reasons, and outbound-edge limits
- [`confidence-model.md`](docs/confidence-model.md) — the five confidence states, how they interact with status, and edge-level confidence
- [`citation-model.md`](docs/citation-model.md) — the citation schema and when citations are mandatory
- [`ingestion-pipeline.md`](docs/ingestion-pipeline.md) — how a news article becomes a validated Incident
- [`contributing.md`](docs/contributing.md) — how to add or edit data and what a PR needs before merge
- [`foundational-twenty.md`](docs/foundational-twenty.md) — the seed dataset's selection rationale, governance-concept clusters, and known coverage gaps

## Editorial tooling (Phase 2A)

`/editorial` — deterministic, rule-based tools that improve contribution quality and consistency without automating editorial judgment: an Incident Authoring Wizard, a Relationship Suggestion Engine, a Citation Completeness Checker, a Coverage Metrics Dashboard, and a Graph Health Report (which enforces the Zero-Orphan Invariant as a hard gate). See [`/editorial/README.md`](editorial/README.md).

## Example dataset: the Foundational Twenty

The dataset in `/data` is 91 objects across 20 real, independently-verified AI governance incidents (`INC-001` through `INC-020`), organised into 13 governance-concept clusters and fully linked through Decisions, Patterns, Controls, Evidence, and Board Questions — selected to maximise breadth of governance concepts, not media popularity. Every relationship states its `reason`; see [`/docs/foundational-twenty.md`](docs/foundational-twenty.md) for the full map and known gaps, and the `citations` on each object for sources.
