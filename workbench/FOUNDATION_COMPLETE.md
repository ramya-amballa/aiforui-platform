# Foundation Complete

**Declared:** 2026-08-05 · **Dataset:** Edition 1.1 (139 canonical objects, 35 incidents, 248 relationships)

This document is a boundary marker, not an ending. It records what the AI Governance Workbench's foundation consists of, freezes the architectural invariants that foundation depends on, states the principles no future contribution — including one from the project's own maintainers — is permitted to break, and hands the project off from *building the platform* to *growing what's on it*. Read it alongside `VISION.md` (why the project exists) and `GOVERNANCE_CHARTER.md` (how it's governed); this document is the third leg: what, specifically, is now load-bearing.

## What has been achieved

**The data model.** Six canonical entity types — Governance Decision, Incident, Design Pattern, Framework Control, Evidence Type, Board Question — each with a dedicated JSON Schema, deterministic sequential IDs, permanent slugs, and a shared base schema (`version`, `status`, `confidence`, `history`, `citations`, `relationships`). Defined in `/schemas`, explained in `ONTOLOGY.md` and `docs/schemas.md`.

**The ontology.** Seven typed, directional relationship verbs, each with an explicit, enumerated set of allowed `(source_type, target_type)` triples, a mandatory `reason` on every edge, optional edge-level confidence, soft/hard outbound-relationship limits, and per-verb cycle detection. Defined in `/relationships/ontology.json`, explained in `docs/relationship-model.md`.

**The validation engine.** A TypeScript/ajv validator (`/validators`) enforcing schema conformance, referential integrity, the Zero-Orphan Invariant, relationship-type validity, and edge-count limits — the merge gate every canonical change passes through. `npm run validate` currently passes 139/139 objects with zero errors.

**The ingestion pipeline.** A draft → human review → canonical promotion path (`/ingestion`) that structurally prevents AI-assisted drafts from becoming canonical without a named human reviewer's approval.

**The editorial toolset.** Seven deterministic, read-only tools (`/editorial`) — an Incident Authoring Wizard, a Relationship Suggestion Engine, a Citation Completeness Checker, a Coverage Metrics Dashboard, a Graph Health Report (Zero-Orphan Invariant as a hard gate), an Editorial Analytics report, and a Repository Quality Audit — none of which can write to `/data`. Composite graph health as of this declaration: **82.2/100** (structural validity 100/100, connectivity 100/100, citation completeness 61/100, confidence maturity 46/100).

**The canonical dataset.** Edition 1.1: 139 objects — 22 Decisions, 35 Incidents, 20 Patterns, 22 Controls, 20 Evidence Types, 20 Board Questions — connected by 248 typed relationships, every one carrying a stated reason. Selected and curated under an explicit editorial discipline (precision over completeness, six mandatory questions per incident) documented in `VISION.md`, `METHODOLOGY.md`, and `docs/foundational-twenty.md`.

**The Explorer.** A public, search-first, statically-generated interface (`/explorer`, Next.js static export, no backend, no database) — universal search, per-entity browsing and filtering, executive-briefing node detail pages, a Governance Decision flagship dashboard, a Framework Explorer, a supplemental graph visualization, and deterministic Markdown/print export. 164 statically-generated pages as of Edition 1.1, rebuilt automatically from `/data` on every build.

**The governance and publication layer.** Ten root-level constitution-tier documents — `ONTOLOGY.md`, `VISION.md`, `GOVERNANCE_CHARTER.md`, `EDITORIAL_POLICY.md`, `METHODOLOGY.md`, `CITATION_POLICY.md`, `VERSION_POLICY.md`, `REVIEW_PROCESS.md`, `CONFLICT_OF_INTEREST.md`, `RELEASE_CHECKLIST.md` — plus eleven supporting documents under `/docs`, cross-linked and audited for internal consistency (`docs/readiness-audit-2026-08.md`).

Two numbered dataset editions shipped and cited (`/docs/releases/`), a documented repository-wide data-quality audit (`docs/quality-audit-2026-08.md`), and a documented repository-wide documentation-readiness audit (`docs/readiness-audit-2026-08.md`).

## Architectural invariants — now frozen

These do not change without the full breaking-change process in `VERSION_POLICY.md`: a written rationale, a migration plan for every affected object, and a major-edition-level release. They do not change to accommodate a specific piece of content, a specific feature idea, or a specific deadline.

1. **The six entity types and their schemas.** No new entity type is activated (`LAW-`, `STD-`, `ORG-`, `PER-`, `TAG-` remain reserved, not implemented) and no existing schema's required fields are removed or narrowed, outside the process above.
2. **The seven relationship verbs and their allowed triples.** `RESULTED_FROM`, `MITIGATED_BY`, `IMPLEMENTED_BY`, `SATISFIES_CONTROL`, `REQUIRES_EVIDENCE`, `RAISES_BOARD_QUESTION`, `RELATED_TO` — and specifically which entity-type pairs each may connect — are fixed.
3. **Deterministic IDs and permanent slugs.** Never UUIDs. A published slug is never changed.
4. **The five-state confidence vocabulary and five-state status vocabulary**, and their orthogonality — confidence and status never collapse into one field.
5. **Mandatory, reasoned relationships.** No untyped edge is ever permitted; no edge without a stated `reason` is ever permitted.
6. **The Canonical Principle.** The Knowledge Graph is the product; everything else — the Explorer, any future API, any future export — is a read-only view, rebuildable from `/data` and the ontology alone, never a second place facts can originate.
7. **No backend, no database, no authentication, no CMS, no community editing** without a deliberate, documented governance decision at the charter level, not as a feature-by-feature judgment call. The Explorer's static-export architecture is frozen on the same terms as the data model.
8. **The AI-authorship rule.** An AI tool may draft; it may never cause content to become canonical without a named human reviewer's approval. This applies to every future contribution, including ones this project's own assistant drafts.
9. **The editorial tooling's read-only constraint.** Nothing in `/editorial` gains a write path into `/data`. A tool that suggests remains a view; only a PR passing `/validators` changes the graph.

## Principles future contributors must not break

Distinct from the structural invariants above — these are editorial and governance commitments, enforced by review rather than by `/validators`, and are no less binding for that:

- **Evidence before inclusion.** A claim enters because a source supports it, not because it's plausible or useful to have (`EDITORIAL_POLICY.md`).
- **Precision over completeness.** A smaller, accurate graph beats a larger one padded with plausible-sounding connections. Quality over quantity in framework mappings; one primary pattern per decision, not every vaguely-relevant one.
- **Neutrality and independence.** No vendor ranking, no policy advocacy, no sponsored content, no commercial entity granted editorial influence (`EDITORIAL_POLICY.md`, `CONFLICT_OF_INTEREST.md`).
- **Confidence asserted honestly, never aspirationally.** `Verified` means independently re-checked by a second reviewer — not "seems solid" (`REVIEW_PROCESS.md`).
- **Corrections happen in the open.** Errors are expected and fixed transparently, with `history` recording what was wrong and why it changed — never quietly (`EDITORIAL_POLICY.md`'s correction policy).
- **Every relationship states why it exists.** A verb and a target are never sufficient on their own.
- **Free to use, not for sale.** No paywall, no subscription, no commercial product built on top of the canonical dataset itself.

## What "frozen" does not mean

The architecture is frozen. The project is not finished. Editions continue (`VERSION_POLICY.md`'s minor-edition path remains fully open — more incidents, more coverage, corrections). The citation-completeness score is expected to climb from its current 61.3/100 toward the stated 80/100 target — that is real, ongoing editorial work, not blocked by anything in this document. Executive-language and visual-identity refinement (`VISION.md` Workstreams 2 and 3) remain open. This document freezes the *scaffolding* specifically so the *content and utility* built on top of it can keep growing without the ground shifting under it.

## The single test for every future contribution

> Does this make the AI Governance Workbench more valuable to practitioners without compromising the stability, determinism, and editorial integrity of the foundation?

Any change — a new incident, a new tool, a new document, a new downstream product — is evaluated against this question before anything else. A change that fails it is out of scope regardless of how good an idea it is on its own terms; a change that passes it is worth doing regardless of how small it is.

## What comes next

This is a handoff point, not a stopping point. `VISION.md`'s long-term roadmap remains the standing reference for direction; two items on it are the immediate next work:

- **Practitioner Toolkit** (extending `VISION.md` Workstream 4): reusable assets *derived deterministically from the canonical graph* — Governance Playbooks (executive summary, common decisions, historical incidents, patterns, framework mapping, evidence checklist, board questions, audit checklist, assembled per topic, e.g. "Customer-Facing AI Governance"), Architecture Review Packs (decision checklist, required evidence, controls, common failure modes, historical incidents, e.g. "Generative AI Architecture Review"), Board Brief Packs (e.g. "AI Hiring Systems"), Risk Assessment Templates (e.g. "Vendor AI Due Diligence," generated from Decisions/Patterns/Controls/Evidence), and Audit Worksheets. Structured outputs only, assembled from what's already canonical — no generative content, same discipline as every export the Explorer already produces.
- **A public site for the umbrella brand** (AI for U&I, with the Workbench as its flagship open resource, alongside Research/Blog/Consulting) has been raised as a strategic direction. It is noted here as a live consideration, not started, and not implied by anything else in this document — it is a distinct, larger decision about how this project is presented alongside the rest of the organization's work, to be scoped deliberately when taken up, not folded into the foundation this document freezes.

Neither of these requires reopening anything this document freezes. That is the point of freezing it now.
