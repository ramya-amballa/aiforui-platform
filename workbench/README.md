# AI Governance Workbench

A data-first, schema-driven knowledge graph for AI governance — organised around **Governance Decisions**, the way MDN Web Docs organises web platform knowledge, Refactoring.Guru organises design patterns, and MITRE ATT&CK organises adversary tactics. Not a new governance framework; a searchable, interconnected reference built from real-world governance decisions, incidents, patterns, controls, evidence, and board-level questions.

**This is independent of AOS.** AOS (elsewhere in this repository) is the flagship consulting operating system used to run engagements. The Workbench is a separate, public knowledge platform aimed at building industry authority — nothing here depends on AOS, and nothing in AOS should come to depend on this without a deliberate integration decision.

This spans **Phase 1 through Phase 4**: the data foundation, the editorial tooling that keeps contributions consistent, a growing curated dataset (Edition 1.1: 139 objects across 35 real, independently-verified incidents), the Explorer (a public, search-first interface for browsing and traversing the graph), and — as of Phase 4 — the governance and publication layer that makes this a maintained public reference rather than just a repository. Start with [`VISION.md`](VISION.md) for why this project exists and where it's going, and [`GOVERNANCE_CHARTER.md`](GOVERNANCE_CHARTER.md) for how it's governed; see [`ONTOLOGY.md`](ONTOLOGY.md) for the Canonical Principle this is built on, and [`/docs/architecture.md`](docs/architecture.md) for the fuller technical reasoning. **[`FOUNDATION_COMPLETE.md`](FOUNDATION_COMPLETE.md)** declares the architecture stable as of Edition 1.1 and states exactly what's frozen and what future contributors must not break — read it before proposing a structural change.

## What's here

```
/workbench
  ONTOLOGY.md     The constitution: every core term defined in one place
  /schemas        JSON Schema for the 6 canonical entity types + shared building blocks
  /data           The canonical dataset (one JSON file per object)
  /relationships  The machine-readable relationship ontology
  /validators     The validation engine (TypeScript + ajv) — the merge gate
  /editorial      Deterministic authoring/QA tools for maintainers (wizard, suggestions, coverage, health, insights)
  /ingestion      The draft -> human review -> canonical pipeline for Incidents
  /explorer       The public interface: search, browsing, node pages, framework pages, graph view (Phase 3)
  /search         Superseded by /explorer's local search — see /search/README.md
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

**Foundational** — what this project is and how its data is structured:

- [`VISION.md`](VISION.md) — why this project exists, who it serves, and the long-term roadmap
- [`ONTOLOGY.md`](ONTOLOGY.md) — the constitution: the Canonical Principle, the AI-authorship rule, and every core term defined in one place
- [`architecture.md`](docs/architecture.md) — the reasoning behind every major design decision
- [`schemas.md`](docs/schemas.md) — field-by-field reference for all six entity schemas
- [`relationship-model.md`](docs/relationship-model.md) — the relationship ontology, mandatory edge reasons, and outbound-edge limits
- [`confidence-model.md`](docs/confidence-model.md) — the five confidence states, how they interact with status, and edge-level confidence
- [`citation-model.md`](docs/citation-model.md) — the citation schema and when citations are mandatory
- [`ingestion-pipeline.md`](docs/ingestion-pipeline.md) — how a news article becomes a validated Incident
- [`contributing.md`](docs/contributing.md) — how to add or edit data and what a PR needs before merge
- [`foundational-twenty.md`](docs/foundational-twenty.md) — the seed dataset's selection rationale, governance-concept clusters, and known coverage gaps
- [`quality-audit-2026-08.md`](docs/quality-audit-2026-08.md) — repository-wide naming/terminology/citation-depth audit ahead of Edition 1.2

**Governance & publication** (Phase 4) — how the project is run, reviewed, and released, in the same spirit as NIST, MITRE, or OWASP's own governance documentation:

- [`GOVERNANCE_CHARTER.md`](GOVERNANCE_CHARTER.md) — mission, scope, editorial authority, maintainers, and long-term stewardship
- [`METHODOLOGY.md`](METHODOLOGY.md) — the reasoning behind the architecture: why Decisions are central, why Incidents are evidence not the primary object, the full review-to-release pipeline
- [`EDITORIAL_POLICY.md`](EDITORIAL_POLICY.md) — evidence standards, verification requirements, correction/update policy, neutrality, independence
- [`CITATION_POLICY.md`](CITATION_POLICY.md) — acceptable sources, how court judgments and regulatory publications are treated, how citation quality is measured
- [`REVIEW_PROCESS.md`](REVIEW_PROCESS.md) — draft through retirement, reviewer responsibilities, the appeal process
- [`VERSION_POLICY.md`](VERSION_POLICY.md) — object versions vs. dataset editions vs. structural (ontology/schema) stability, and what counts as a breaking change
- [`CONFLICT_OF_INTEREST.md`](CONFLICT_OF_INTEREST.md) — commercial relationships, vendor neutrality, disclosure and recusal
- [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) — the deterministic gate every edition passes before publication
- [`docs/readiness-audit-2026-08.md`](docs/readiness-audit-2026-08.md) — the repository-wide documentation consistency audit this phase produced
- [`FOUNDATION_COMPLETE.md`](FOUNDATION_COMPLETE.md) — what has been built, the architectural invariants now frozen, and the single test every future contribution is evaluated against

## Editorial tooling (Phase 2A)

`/editorial` — deterministic, rule-based tools that improve contribution quality and consistency without automating editorial judgment: an Incident Authoring Wizard, a Relationship Suggestion Engine, a Citation Completeness Checker, a Coverage Metrics Dashboard, a Graph Health Report (which enforces the Zero-Orphan Invariant as a hard gate), an Editorial Analytics report, and a Repository Quality Audit (naming/terminology/citation-depth consistency). See [`/editorial/README.md`](editorial/README.md).

## Example dataset: the Foundational Twenty, and beyond

The dataset in `/data` started as 91 objects across 20 real, independently-verified AI governance incidents (the "Foundational Twenty," `INC-001`–`INC-020`) and has since grown, edition by edition — see [`/docs/releases`](docs/releases/README.md) for the numbered, citable edition history (currently Edition 1.1: 139 objects, 35 incidents). Every relationship states its `reason`; see [`/docs/foundational-twenty.md`](docs/foundational-twenty.md) for the original selection rationale, and the `citations` on each object for sources.

## Explorer (Phase 3)

`/explorer` is the public, interactive interface onto the graph — universal search, per-entity browsing and filtering, executive-briefing node detail pages, a framework explorer, and a supplemental graph visualization, all statically generated from `/data` with no backend. See [`/explorer/README.md`](explorer/README.md) for the full architecture.

```sh
cd workbench/explorer
npm install
npm run dev      # regenerates data from /workbench/data, starts a dev server
```
