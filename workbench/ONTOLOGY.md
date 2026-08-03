# Ontology — The Constitution

This is the single page that defines every core term in the AI Governance Workbench. If a document elsewhere in `/workbench` and this page ever disagree, this page wins — fix the other document, not this one, unless the ontology itself is deliberately changing.

## Canonical Principle

> **The Knowledge Graph is the product. Everything else is a view.**

```
Website  -> view
PDF      -> view
API      -> view
Search   -> view
Graph    -> view
LLM      -> view
```

**Nothing edits the data directly except the canonical repository.** Every one of those views is a read path, generated or served from `/data` — none of them is a second place facts can originate or be changed. A view that appears to "edit" something (a future contribution UI, an API write endpoint) is really just a front door back to the same PR-and-validation path everything else goes through; it does not get a shortcut around `/schemas`, `/relationships/ontology.json`, or `/validators`.

This is why Phase 1 built no views at all: the product is durable exactly to the extent that every future view can be deleted and rebuilt from `/data` alone without losing anything. See `/docs/architecture.md` for the fuller reasoning.

## No AI writes canonical data

> LLMs may assist draft creation. Only human-reviewed commits become canonical knowledge.

An AI tool (this project's own assistant included) may draft, extract, summarise, or propose content — the `extraction_method: "ai_assisted"` field in `/ingestion/schemas/draft-incident.schema.json` exists specifically to record when that happened, transparently. What an AI tool may never do is cause content to become canonical unsupervised. Concretely:

- `/ingestion/drafts` is not `/data`, and nothing in `/data` reads from it.
- `/ingestion/src/promote.ts`, the only script that writes into `/data/incidents`, hard-refuses to run unless `human_review.status === "approved"` with a named `reviewer` on record.
- For every other entity type, the same rule is enforced by ordinary PR review rather than a script — a maintainer merging a PR *is* the human review.

## Core definitions

**Decision** — see `/schemas/decision.schema.json`, `/docs/schemas.md`. The hub entity: a concrete, testable governance commitment (`decision_statement`) made by some `governing_body`. Everything else in the ontology is organised in relation to decisions — see "Why decisions sit at the centre" in `/docs/relationship-model.md`.

**Incident** — see `/schemas/incident.schema.json`. A real-world event where an AI system caused, or was alleged to cause, harm or a governance breach. The evidence base for why decisions get made. The only entity type with a dedicated capture pipeline — see `/docs/ingestion-pipeline.md`.

**Pattern** (Design Pattern) — see `/schemas/pattern.schema.json`. A reusable approach (`problem` + `solution`) for implementing a decision in practice.

**Control** (Framework Control) — see `/schemas/control.schema.json`. A specific requirement drawn from a named external framework, standard, or regulation (`framework_name` + `control_reference` + `control_text`). This is how the Workbench stays a *reference*, not a competing framework: every control traces back to something an outside body actually published.

**Evidence** (Evidence Type) — see `/schemas/evidence.schema.json`. A category of artifact (`evidence_description`) that demonstrates a decision or control has actually been satisfied, not just declared.

**Board Question** — see `/schemas/board_question.schema.json`. A question board-level oversight should ask (`question_text`) in light of a decision, incident, or control — the translation of graph knowledge into an oversight practitioner's actual job.

**Relationship** — see `/schemas/common/relationship.schema.json`, `/docs/relationship-model.md`. A typed, directed edge between two objects: a `type` (one of seven fixed verbs), a `target_id`/`target_type`, a mandatory `reason` (why this specific edge exists), and optional `confidence` and `citation_ids`. Arbitrary/untyped links are never permitted — every edge's `(verb, source_type, target_type)` triple must appear in `/relationships/ontology.json`.

**Confidence** — see `/docs/confidence-model.md`. One of `Verified` / `Reviewed` / `Draft` / `Community` / `Archived`, on every object (and optionally on every relationship). Answers "how much should this be trusted," distinct from `status`, which answers "is this current."

**Citation** — see `/schemas/common/citation.schema.json`, `/docs/citation-model.md`. A traceable pointer to one external source (`source_type`, `title`, `publisher`, `accessed_date`, optionally `url`/`locator`/`excerpt`), across seven source types (`regulator`, `legislation`, `court_judgment`, `company_statement`, `academic_paper`, `standards_body`, `news_publication`, plus `other`). Mandatory on every `Decision` and `Incident`, and on any object claiming `Verified`/`Reviewed` confidence.

**Status** — one of `draft` / `active` / `deprecated` / `superseded` / `retracted`. The record's lifecycle state, independent of confidence.

**Version** — a semver string (`1.0.0`), bumped on substantive edits, paired with an append-only `history` array (`/schemas/common/history-entry.schema.json`) logging every `created` / `updated` / `reviewed` / `approved` / `archived` / `retracted` event with its date, actor, and the version it applied to.

**ID vs. Slug** — every object has both. `id` is a deterministic, sequential, type-prefixed code (`DEC-001`) used for all internal cross-referencing. `slug` is a permanent, human-readable, kebab-case address unique within its entity type (`bias-audit-gate-for-hiring-ai`), meant to become a stable URL (`/decisions/<slug>`) once a frontend exists — never a UUID. See `/docs/schemas.md`.

## ID prefixes

| Prefix | Entity type |
|---|---|
| `DEC-` | Decision |
| `INC-` | Incident |
| `PAT-` | Pattern |
| `CTR-` | Control |
| `EVI-` | Evidence |
| `BRD-` | Board Question |

**Reserved, not yet implemented** — earmarked so future entity types never have to collide with or renumber the ones above:

| Prefix | Reserved for |
|---|---|
| `LAW-` | Legislation |
| `STD-` | Standard |
| `ORG-` | Organization |
| `PER-` | Person |
| `TAG-` | Tag/topic as a first-class node |

This table is generated by hand from `/relationships/ontology.json`'s `id_prefixes` and `reserved_prefixes` — if you add a prefix, update both.

## Designing for a future API

Phase 1 builds no API. It is designed so one is trivial later, without Phase 1 guessing at its shape prematurely:

- `/data` is already the contract: stable `id`s, stable `slug`s, one JSON object per file, one schema per entity type. A read-only API is close to a thin wrapper that walks `/data` and serves what's already there — no reshaping needed.
- The validator's invariants (no dangling references, no orphan nodes, no invalid relationship types) mean an API consumer can trust that traversing `relationships[].target_id` always resolves, without needing its own defensive error handling for a broken graph.
- `slug` exists specifically so a future API/site can expose clean, stable URLs (`/decisions/<slug>`) independent of the internal `id` scheme.
- Because the Canonical Principle holds every view to read-only, an API's only interesting design question later is *how to expose reads* (REST? GraphQL? both?) — never *how to reconcile writes from multiple sources*, since there's only ever one source: the canonical repository via PR.
