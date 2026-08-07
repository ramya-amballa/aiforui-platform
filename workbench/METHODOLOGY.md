# Methodology

`ONTOLOGY.md` defines what things are called. This document explains why the architecture is shaped the way it is — the reasoning a maintainer, contributor, or auditor needs in order to extend the project correctly rather than just compliantly.

## Why Governance Decisions are the central abstraction

A dataset organized around incidents alone would be a chronicle: a list of things that went wrong, in the order they happened. That's a useful evidence base, but it doesn't, by itself, tell a practitioner what to do. A dataset organized around risks or requirements would be an inventory: complete, perhaps, but abstract — a "bias risk" entry doesn't imply an action the way "require disaggregated error-rate testing before deploying a risk-scoring algorithm" does.

A Governance Decision is a concrete, testable commitment (`decision_statement`) — the kind of sentence a policy or a contract could actually contain. Every other entity type earns its place in the graph by relating to one: an Incident is why a decision was needed, a Pattern is how it gets implemented, a Control is what external requirement it satisfies, an Evidence type is what would prove it happened, a Board Question is what oversight should ask about it. This is not a stylistic choice. It's what makes the graph answer "what should we decide, and why" instead of just "what happened" — see `/docs/relationship-model.md`'s "Why decisions sit at the centre" for the structural mechanics this produces.

## Why Incidents are evidence, not the primary object

It would be easy to build this dataset the other way around — incidents as the primary object, decisions as commentary on them. That inversion is deliberately avoided. An Incident's role in this dataset is to be the evidentiary basis *for* a Decision, not the subject the dataset is fundamentally about. Two consequences follow directly from this:

1. **Incidents are selected for the governance lesson they demonstrate, not their newsworthiness.** A well-known incident that doesn't cleanly imply a testable decision is a weaker candidate for inclusion than an obscure one that does — see the "Editorial Excellence" discipline in `VISION.md` and the six mandatory questions every incident must answer before promotion (below, "Canonical promotion process").
2. **Multiple incidents legitimately point at the same decision.** Because the decision, not the incident, is the organizing unit, the dataset expects and rewards this — see the "incident clustering" and "pattern reuse frequency" metrics in `editorial:insights`. A decision cited by three independent incidents is a stronger, more validated governance response than one inferred from a single event; the graph structure makes that visible rather than treating each incident as its own silo.

This is also why the `RESULTED_FROM` and `MITIGATED_BY` verbs both exist and both matter: a Decision `RESULTED_FROM` the Incident that provoked it (causal origin, backward-looking), while an Incident is `MITIGATED_BY` a Decision (risk reduction, forward-looking, and not necessarily limited to the one incident that originally provoked the decision). The same pair of facts, told from two directions, is exactly what lets one decision generalize across many incidents.

## Relationship semantics

The full ruleset lives in `/relationships/ontology.json` and is explained in `/docs/relationship-model.md`; the methodological point worth stating explicitly here is *why* relationships are typed and directional rather than a single generic "related" link. A typed verb encodes a specific claim (`SATISFIES_CONTROL` claims fulfillment; `MITIGATED_BY` claims risk reduction; `RESULTED_FROM` claims causation) that a reader — or, eventually, an automated consumer of the graph — can reason about differently. An untyped graph can tell you two things are connected; a typed one can tell you *how*, which is what makes it possible to ask a question as specific as "show every Decision that satisfies a NIST MEASURE-function control" and get a structurally correct answer rather than a keyword-matched guess.

The mandatory `reason` field on every relationship exists because the verb alone rarely explains the judgment call behind a specific edge — why *this* control, not a different one that's also topically related; why *this* pattern is the single primary mitigation rather than one of several plausible ones. `reason` is where that judgment is made visible and auditable, rather than left implicit in whoever drafted the edge.

## Confidence methodology

Confidence (`Verified` / `Reviewed` / `Draft` / `Community` / `Archived`, `/docs/confidence-model.md`) is deliberately a statement about **how the claim was checked**, not about how important or well-known it is. A famous incident with a single, unverified news source is `Draft` or `Reviewed` at best; an obscure regulatory order independently confirmed by two reviewers against the primary document is `Verified`, regardless of how few people have heard of it. This is what keeps confidence meaningful as the dataset grows — it tracks the project's own process, not the world's opinion of the subject matter.

Confidence is deliberately orthogonal to `status` (is this the current record) for the same reason evidence and conclusion are kept separate everywhere else in the methodology: collapsing "how much do we trust this" into "is this still in force" would make it impossible to express a `Verified` record that has since been formally retracted (e.g., a judgment overturned on appeal) without losing the fact that it was, at the time, thoroughly checked.

## Editorial review workflow

1. **Draft** — content is authored, human or AI-assisted (`created_by`, `history` event `created`). Nothing at this stage is canonical in the trust sense even if it is already merged to `/data`; `confidence: Draft` or `Community` says so explicitly.
2. **Review** — a maintainer checks the object's citations actually support its claims, checks its relationships are meaningfully reasoned rather than templated, and checks it against `EDITORIAL_POLICY.md` and `CITATION_POLICY.md`. This is a human judgment step that no amount of schema validation substitutes for — `/validators` confirms the object is well-formed; review confirms it is *right*.
3. **Promotion** — see "Canonical promotion process" below.
4. **Re-verification** — reaching `Verified` requires a second, independent reviewer beyond the one who moved the object to `Reviewed`. This is intentionally a higher bar than most content in the dataset currently clears (see `/docs/quality-audit-2026-08.md`'s confidence-maturity numbers) — `Verified` is meant to stay rare and meaningful, not become the default aspiration for every object.

The full procedural detail — reviewer responsibilities, timelines, appeal — lives in `REVIEW_PROCESS.md`; this section is the reasoning behind that procedure, not a restatement of it.

## Canonical promotion process

An object becomes canonical the moment it is merged into `/data` and passes `/validators` — but "canonical" in this dataset explicitly does not mean "true" or "final," only "structurally part of the graph, at a stated and honest confidence level." Promotion to a *higher* confidence level is the more meaningful gate, and for Incidents specifically, promotion is additionally gated on six questions every incident must answer before it's considered ready (see `VISION.md`'s editorial philosophy and the Phase 3 editorial discipline that introduced this): what Governance Decision was actually involved, what observable evidence demonstrates that decision, which single primary Pattern would most directly have mitigated the outcome, which Framework Controls are genuinely and directly applicable, what one Board Question follows, and what confidence — with a stated rationale — the object should carry. An incident that can only answer some of these is incomplete, not merely low-confidence; it isn't ready for promotion regardless of how well-documented the underlying event is.

For non-Incident entity types authored directly (Decisions, Patterns, Controls, Evidence, Board Questions), the same discipline applies without the dedicated ingestion pipeline: see `/docs/contributing.md` and `/docs/ingestion-pipeline.md` for the mechanical paths, and `REVIEW_PROCESS.md` for the review gate both paths share.

## Release methodology

The dataset ships as numbered, citable editions (`/docs/releases/`) rather than a continuously mutating feed, so that "AI Governance Workbench, Edition 1.1" remains a stable thing to cite even after Edition 1.2 exists — see "Why editions, not a rolling feed" in `/docs/releases/README.md`. Each edition's release note is itself append-only history: it documents what was added and what changed *since* the prior edition, and is never revised after publication to read differently than it did at release time (corrections to the underlying dataset are still made per this document's correction policy; the release note is a historical record of what shipped, not a live document). See `VERSION_POLICY.md` for exactly what triggers a patch, minor, or major edition, and `RELEASE_CHECKLIST.md` for the deterministic gate every edition passes through before publication.
