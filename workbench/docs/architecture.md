# Architecture

This document explains the *why* behind the AI Governance Workbench's foundation. For *what* each piece does, see the other files in `/docs` and the `README.md` in each subdirectory.

## What this is, and what it is not

The AI Governance Workbench is a public, open-source knowledge graph for AI governance — organised the way MDN Web Docs organises web platform knowledge, Refactoring.Guru organises design patterns, and MITRE ATT&CK organises adversary tactics: as a searchable, interconnected reference built from real-world material, not a new framework competing with NIST, ISO, or the EU AI Act.

It is **not** AOS. AOS is the flagship consulting operating system elsewhere in this repository, built for delivery engagements. The Workbench is independent of it: separate module (`/workbench`), separate audience (the public, not clients), separate goal (build industry authority through a durable reference asset, not run engagements). Nothing in `/workbench` depends on anything in `/AOS`, and nothing in `/AOS` should come to depend on `/workbench`'s data formats without a deliberate integration decision — they are allowed to evolve independently.

## The Canonical Principle

This is the single sentence every other decision in this document, and in `/ONTOLOGY.md`, exists to serve:

> **The Knowledge Graph is the product. Everything else is a view.**

A website, a PDF export, an API, a search index, a graph visualisation, an LLM-assisted authoring tool — every one of them is a *view*, generated or served from `/data`. None of them is a second place facts can originate or be edited. Nothing edits the data directly except the canonical repository (a PR against `/data`, passing `/validators`). This is the architectural guardrail against drift: as soon as a future team is tempted to let a dashboard "just quickly patch" a fact, or let an API accept writes that bypass schema/ontology validation, that's the Canonical Principle being violated, and the fix is to route the change back through the repository, not to special-case the view. See `/ONTOLOGY.md` for the full statement, including how this applies to AI-authored content.

## Why data-first

The instruction that shaped every other decision in Phase 1: **the data is the long-term asset, not the UI.** A knowledge graph about AI governance is valuable for as long as the underlying facts, relationships, and citations are accurate and current — UI frameworks will be rewritten many times over that lifespan. So Phase 1 deliberately builds *only* the data layer: schemas, sample data, an ontology, a validator, and an ingestion path. No frontend, no search index, no API. Anything built later (a static site, a graph explorer, a REST/GraphQL API, an LLM-assisted authoring tool) should be able to treat `/workbench/data` and `/workbench/schemas` as its single source of truth and be rebuilt from scratch without touching either.

## Why JSON Schema + flat files, not a database

- **Git-native.** Every fact, every edit, every relationship change goes through a pull request, a diff, and a commit history. That gives the dataset the same review, blame, and revert tooling as code — which matters enormously for a dataset whose credibility depends on traceability. A database with an admin UI would hide that history behind an opaque write path.
- **Static-site friendly.** Flat JSON files can be read directly by a static site generator, bundled into a search index, or served from a CDN with no runtime database. This keeps the eventual hosting cost near zero and the eventual frontend replaceable.
- **No infrastructure to operate.** A community contribution model (see "Build for community contribution" below) is much easier to support via GitHub PRs against JSON files than via write access to a hosted database.
- **JSON Schema (not a hand-rolled format)** gives us a standard, tool-supported way to express structure, and lets the same schema double as documentation, as an editor-autocomplete source, and as the input to the validation engine — one artifact serving three purposes.

The tradeoff is that flat JSON files don't give you database-style query performance or referential-integrity enforcement for free. That is exactly what `/validators` exists to provide instead, run on every change rather than continuously enforced by a database engine.

## Why Governance Decisions are the hub

The brief for this project is explicit: "the primary organizing principle is Governance Decisions. Everything else revolves around those decisions." Concretely, that shows up in the relationship ontology (`/relationships/ontology.json`): `Incident`, `Pattern`, `Control`, `Evidence`, and `Board Question` are all designed to connect back to a `Decision`, directly or via one hop (see `/docs/relationship-model.md`). This mirrors how governance actually works in practice — an incident matters because of the decision it provokes; a control matters because a decision needs to satisfy it; evidence matters because a decision requires it to be demonstrated. A knowledge graph organised around decisions answers the practitioner's real question — "what should we decide, and why" — rather than around abstractions like "risks" or "requirements" that don't by themselves imply an action.

## Repository structure

```
/workbench
  ONTOLOGY.md     The constitution: every core term defined in one place, plus the Canonical Principle
  /schemas        JSON Schema definitions for the 6 canonical entity types + shared building blocks
  /data           The canonical dataset itself, one JSON file per object, one directory per entity type
  /relationships  The machine-readable relationship ontology (allowed verbs and triples)
  /validators     The validation engine (TypeScript + ajv) that enforces schemas + graph-level rules
  /editorial      Deterministic authoring/QA tools for maintainers (Phase 2A) — see /editorial/README.md
  /ingestion      The draft -> human review -> canonical pipeline for turning news into Incidents
  /search         Superseded by /explorer's local search — see /search/README.md
  /explorer       The public interface: a static, search-first way to browse and traverse the graph (Phase 3)
  /docs           This documentation set
```

`/schemas`, `/relationships`, and `/validators` together form the *rulebook*. `/data` is the *dataset* the rulebook governs. `/ingestion` is the *only sanctioned path* by which new, non-trivial content (starting with Incidents sourced from news) enters `/data`. Every other addition to `/data` (Decisions, Patterns, Controls, Evidence, Board Questions) goes in directly via a pull request, because those entity types are authored/curated judgement calls rather than facts extracted from a single external event — see `/docs/contributing.md`.

## Why `/editorial` doesn't get a write path into `/data`

`/editorial` (Phase 2A) exists to make contributions more consistent — a wizard that catches malformed drafts at entry time, a rule-based engine that suggests plausible relationships, checkers that score citation and graph quality. Every one of these is deliberately advisory: the wizard writes only to `/ingestion/drafts` (non-canonical by construction), and every other tool only prints a report. None of them can write to `/data`. This isn't an oversight to fix later — it's the Canonical Principle applied directly: a tool that suggests is a view onto the graph, and only a PR passing `/validators` is allowed to change the graph itself. See `/ONTOLOGY.md`.

## Why confidence and status are both first-class fields

`status` (draft / active / deprecated / superseded / retracted) is a *lifecycle* field — is this record the one currently in force? `confidence` (Verified / Reviewed / Draft / Community / Archived) is an *epistemic trust* field — how much should a reader trust this record's content? They are orthogonal: an `active` record can be `Community` confidence (published, in use, but not yet independently verified), and a `retracted` record can have been `Verified` at the time it was retracted. Collapsing them into one field would force every contributor to choose between "is this current" and "is this trustworthy," which are genuinely different questions. See `/docs/confidence-model.md`.

## Why every object requires citations (conditionally) rather than always

The brief says "every governance statement, mapping, recommendation, and incident must support citations" and separately asks the validator to reject "missing citations." Making `citations` structurally *supported* everywhere (it's part of the base schema all six entity types share) but only *mandatory* for `Incident` and `Decision` objects, or for any object claiming `Verified`/`Reviewed` confidence, reflects that some records (e.g. an early-stage `Draft` `Pattern` someone is still fleshing out) are legitimately uncited work-in-progress, while a fact about the world (an `Incident`) or a decision presented as guidance (a `Decision`) should never be uncited, regardless of how provisional its confidence is. See `/docs/citation-model.md` for the exact rule.

## Why AI-generated content cannot enter the canonical dataset directly

This is enforced structurally, not just as a policy statement: the ingestion pipeline's `draft-incident.schema.json` is a *separate* schema from `incident.schema.json`, drafts live in `/ingestion/drafts` rather than `/data`, nothing in `/data` is ever read from `/ingestion/drafts`, and the only script capable of writing into `/data/incidents` (`promote.ts`) hard-refuses to run unless a human reviewer's name and an explicit confidence assignment are present with `human_review.status == "approved"`. An LLM can help *draft* a candidate incident (that's what `extraction_method: "ai_assisted"` records), but it cannot become canonical without a named human approving it. `/ONTOLOGY.md` states this as one of the project's two constitutional rules, alongside the Canonical Principle above. See `/docs/ingestion-pipeline.md`.

## Designing for a future API without building one

Nothing in Phase 1 is exposed over an API, but nothing about `/data`'s design should have to change when one is added — see "Designing for a future API" in `/ONTOLOGY.md`. In short: `/data` already *is* the contract (stable `id`s and `slug`s, one schema per type), and the validator's invariants (no dangling references, no orphans, no invalid relationship types) mean an API built on top of it never has to defend against a broken graph. Building the API itself remains out of scope for Phase 1.

## What Phase 1 deliberately does not build

No frontend, dashboard, search page, or graph visualisation — per the brief. `/search` exists as a directory (matching the required repository structure) but contains only a placeholder explaining what it's reserved for, so a later phase has a clear landing spot without Phase 1 guessing at a search index design prematurely.

## The Explorer (Phase 3)

`/workbench/explorer` is the first public interface onto the graph: a static, search-first site (Next.js, `output: "export"` — no server, no database) with universal search, per-entity browsing and filtering, executive-briefing-style node detail pages, a framework explorer, and a supplemental graph visualization. It is built entirely on top of the Canonical Principle above: a build step (`explorer/scripts/build-data.ts`) reads `/data` and `/relationships/ontology.json` and emits a derived, gitignored JSON graph that every page and the client-side search index are generated from. Nothing in `/explorer` can write back to `/data` — it is a pure view, same as `/editorial`'s reports. See `/workbench/explorer/README.md` for the full architecture (routes, search, graph visualization, filtering, executive export).
