# AI Governance Workbench

A data-first, schema-driven knowledge graph for AI governance — organised around **Governance Decisions**, the way MDN Web Docs organises web platform knowledge, Refactoring.Guru organises design patterns, and MITRE ATT&CK organises adversary tactics. Not a new governance framework; a searchable, interconnected reference built from real-world governance decisions, incidents, patterns, controls, evidence, and board-level questions.

**This is independent of AOS.** AOS (elsewhere in this repository) is the flagship consulting operating system used to run engagements. The Workbench is a separate, public knowledge platform aimed at building industry authority — nothing here depends on AOS, and nothing in AOS should come to depend on this without a deliberate integration decision.

This is **Phase 1**: the data foundation only. No frontend, dashboard, search page, or graph visualisation is built yet — see [`/docs/architecture.md`](docs/architecture.md) for why that's deliberate.

## What's here

```
/workbench
  /schemas        JSON Schema for the 6 canonical entity types + shared building blocks
  /data           The canonical dataset (one JSON file per object)
  /relationships  The machine-readable relationship ontology
  /validators     The validation engine (TypeScript + ajv)
  /ingestion      The draft -> human review -> canonical pipeline for Incidents
  /search         Reserved for a future search index (empty in Phase 1)
  /docs           Full documentation set (start here for the "why" behind everything)
```

## Quick start

```sh
cd workbench
npm install
npm run validate       # validate the whole dataset
npm run typecheck      # type-check the validator/ingestion TypeScript
```

## The six canonical entity types

Governance Decision, Incident, Design Pattern, Framework Control, Evidence Type, Board Question — see [`/docs/schemas.md`](docs/schemas.md) for the full field reference.

## Documentation

- [`architecture.md`](docs/architecture.md) — the reasoning behind every major design decision
- [`schemas.md`](docs/schemas.md) — field-by-field reference for all six entity schemas
- [`relationship-model.md`](docs/relationship-model.md) — the relationship ontology and why each verb exists
- [`confidence-model.md`](docs/confidence-model.md) — the five confidence states and how they interact with status
- [`citation-model.md`](docs/citation-model.md) — the citation schema and when citations are mandatory
- [`ingestion-pipeline.md`](docs/ingestion-pipeline.md) — how a news article becomes a validated Incident
- [`contributing.md`](docs/contributing.md) — how to add or edit data and what a PR needs before merge

## Example dataset

The seed data in `/data` is one small, fully cross-linked example graph (an AI hiring-tool bias scenario) exercising all six entity types and all seven relationship verbs, so the schemas, ontology, and validator all have something real to run against from day one. See the `citations` on each object for sources.
