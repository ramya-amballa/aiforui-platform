# Repository Readiness Audit — August 2026 (Phase 4)

**Scope:** every Markdown document in the repository (31 files: 8 root-level governance documents, `README.md`, `ONTOLOGY.md`, `VISION.md`, 11 files under `/docs`, and the module-level `README.md`s in `/editorial`, `/explorer`, `/ingestion`, `/relationships`, `/search`, `/validators`). **Purpose:** confirm the documentation set is internally consistent, cross-linked, and free of contradictions or stale claims before treating the current edition as ready for public reference use.

This is a different audit from `quality-audit-2026-08.md`, and the two should not be conflated: that one checks the **canonical dataset** (`/data`) for naming, spelling, and citation-depth consistency. This one checks the **documentation set** — the governance layer readers rely on to trust the dataset in the first place.

## Method

Mechanical checks, not a subjective read-through alone:

1. Every Markdown-style link (`[text](path)`) in every file, resolved relative to its own location, checked for existence.
2. Every backtick-quoted file reference cross-checked against the repository's actual structure.
3. Every root-level and `/docs` document scanned for phase/edition/object-count claims, checked against the dataset's actual current state (139 objects, 35 incidents, Edition 1.1 published, Phase 4 governance layer in progress).
4. Every root-level governance document scanned for confidence-state vocabulary (`Verified`/`Reviewed`/`Draft`/`Community`/`Archived`), relationship-verb vocabulary, and entity-type naming, checked against `ONTOLOGY.md` for contradiction.
5. `README.md`'s "Documentation" index checked against the actual file list for completeness in both directions (every listed file exists; every reader-facing document is listed).

## Findings

### Cross-links: resolved

Zero broken `[text](path)`-style links across all 31 files, both before and after this audit's fixes. Backtick-quoted bare filenames (e.g. `` `ontology.json` `` used as shorthand inside a sentence that already gave the full path nearby, or inside a Markdown table cell) are not standalone links and were confirmed by manual review to be legitimate shorthand, not broken references.

### Stale references: found and fixed

- **`README.md`** stated "This spans Phase 1 through Phase 3" — stale as of Phase 4's governance layer. **Fixed**: now states "Phase 1 through Phase 4" and names the governance/publication layer explicitly.
- **`README.md`**'s "Documentation" section did not list any of the eight Phase 4 governance documents, and had no section for them. **Fixed**: added a "Governance & publication (Phase 4)" subsection listing all eight, plus this report.
- **`VISION.md`**'s Workstream 5 ("Community Trust") described `EDITORIAL_POLICY.md`, `CITATION_POLICY.md`, `VERSION_POLICY.md`, `REVIEW_PROCESS.md`, `CONFLICT_OF_INTEREST.md`, `METHODOLOGY.md`, and `GOVERNANCE_CHARTER.md` as documents the project still *needed* — written before Phase 4 produced them. **Fixed**: now states plainly that this scaffolding exists as of Phase 4, links each document, and clarifies that opening the project to outside contributors remains a distinct, future decision this workstream does not itself make.
- **`docs/architecture.md`** had no pointer to `VISION.md` or the Phase 4 governance documents, leaving a reader who starts there with no path to the institutional layer. **Fixed**: added a closing "Governance and publication (Phase 4)" section distinguishing architecture (why the codebase is shaped this way) from governance (why the project is run this way) and linking accordingly.

No other stale object/incident-count claims were found. Every count outside `/docs/releases/edition-*.md` (which are deliberately immutable historical snapshots per `METHODOLOGY.md`'s release methodology, and correctly describe their own edition's numbers, not the current ones) either states the current figures correctly (139 objects, 35 incidents, Edition 1.1) or explicitly frames earlier figures as historical ("started as... has since grown... currently").

### Ontology contradictions: none found

Confidence-state vocabulary, the seven relationship verbs, the six entity type names, and the six ID prefixes are used consistently with `ONTOLOGY.md` across every new Phase 4 document (`GOVERNANCE_CHARTER.md`, `EDITORIAL_POLICY.md`, `METHODOLOGY.md`, `CITATION_POLICY.md`, `VERSION_POLICY.md`, `REVIEW_PROCESS.md`, `CONFLICT_OF_INTEREST.md`, `RELEASE_CHECKLIST.md`) and the existing set. No document redefines a term `ONTOLOGY.md` already defines; each either cross-references it or extends it into policy territory `ONTOLOGY.md` doesn't itself cover (e.g., `CITATION_POLICY.md` builds editorial judgment on top of `docs/citation-model.md`'s schema definition, without restating or contradicting the schema).

### Terminology duplication: one instance, deliberately resolved by cross-reference rather than merging

`docs/citation-model.md` (schema mechanics) and `CITATION_POLICY.md` (editorial judgment) cover related ground by design — this is intentional layering, not duplication, and each document says so explicitly in its opening. The same applies to `docs/confidence-model.md` vs. `EDITORIAL_POLICY.md`'s confidence-states section, and `docs/contributing.md` vs. `REVIEW_PROCESS.md`. No document restates another's content in a way that could drift out of sync unnoticed; each points to its counterpart rather than re-defining shared terms independently.

### Two "audits" with similar names: disambiguated

This report and `quality-audit-2026-08.md` are easy to conflate by name alone. Both are cross-referenced against each other in their opening paragraphs, and this section exists specifically so a reader landing on either one understands the other exists and covers different ground.

### Naming-convention terminology (root-level governance files)

All eight new Phase 4 documents follow the `SCREAMING_SNAKE_CASE.md` convention already established by no prior file in this repository — a deliberate departure from the `kebab-case.md` convention `/docs` uses. This mirrors common practice for governance-tier documents in comparable open technical references (e.g., `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` conventions used broadly across open-source projects) and matches the root-level, constitution-tier placement of `ONTOLOGY.md`, `VISION.md`, and `README.md`, none of which use `/docs`' lowercase convention either. This is noted here as an intentional convention, not flagged as an inconsistency to fix.

## What this audit does not cover

This audit checks documentation consistency, not dataset content quality (see `quality-audit-2026-08.md`) and not whether the governance policies themselves are *good* policy — that judgment was made in writing them, following the constraints Phase 4 specified (institutional tone, no new data model, no AI-generated governance advice), and is properly a matter for maintainer and reader feedback over time, not something a mechanical audit can certify.

## Outcome

Zero broken links. Zero unresolved ontology contradictions. Four stale-reference findings, all fixed as part of this same pass (the same discipline `quality-audit-2026-08.md` applied to `/data`: measure, fix what's mechanical, document what isn't). The documentation set is internally consistent and fully cross-linked as of this report's publication.

This does not, on its own, make Edition 1.1 "done" — `CITATION_POLICY.md`'s 80/100 target is still open work, and `VISION.md`'s Workstreams 2–4 remain future work. What it does establish is that the institutional layer describing how the project handles that remaining work is itself accurate, navigable, and internally honest — which was Phase 4's actual objective.
