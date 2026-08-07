# Confidence Model

Every canonical object carries a `confidence` field (`/schemas/common/base-entity.schema.json`), one of exactly five states:

| State | Meaning |
|---|---|
| `Verified` | Independently corroborated against primary sources by more than one reviewer. The highest bar in the dataset. |
| `Reviewed` | Checked by at least one qualified human reviewer against its cited sources, but not independently re-verified by a second party. |
| `Draft` | Authored (by a human or AI-assisted) but not yet reviewed by anyone besides its author. |
| `Community` | Submitted by a community contributor; may be well-sourced, but hasn't been through the project's own review process. |
| `Archived` | Was previously `Verified` or `Reviewed`, but is retained for historical/traceability reasons rather than being current best knowledge (distinct from `status: retracted` — see below). |

## Confidence vs. status

`confidence` is not the same field as `status` (`draft` / `active` / `deprecated` / `superseded` / `retracted`), and the two are intentionally orthogonal:

- `status` answers "is this the record currently in force?"
- `confidence` answers "how much should a reader trust what this record says?"

A record can be `active` + `Community` (published and in use, not yet independently checked), or `retracted` + `Verified` (it was thoroughly checked at the time, and has since been formally withdrawn — e.g. a court judgment later overturned on appeal). Forcing these into a single field would erase exactly the distinction a governance practitioner needs: "should I rely on this" is a different question from "is this still the applicable answer."

## Who can move an object between confidence states

This is a project-governance question, not something the schema or validator enforces per se (the validator only enforces that the field has one of the five allowed values, plus the citation rule below). In practice:

- Anything entering via a pull request starts at `Draft` or `Community` (community-submitted) until a maintainer reviews it.
- A maintainer moving an object to `Reviewed` should be someone with subject-matter familiarity who has checked the object's citations resolve and support its claims.
- `Verified` is reserved for objects that have had a second, independent check — see `/docs/contributing.md` for the review workflow this implies.
- Only a maintainer should move an object to `Archived` or set `status: retracted`, and both should come with an explanation (e.g. a `description` update or PR description) of why.

## Interaction with the citation model

The validator's `missing_citation` rule (see `/docs/citation-model.md`) requires at least one citation whenever `confidence` is `Verified` or `Reviewed` — the idea being that a record claiming that level of trust must be able to point to why. `Draft` and `Community` objects are allowed to have zero citations (someone is allowed to sketch an idea before sourcing it), except for `Incident` and `Decision` objects, which always require at least one citation regardless of confidence, because an uncited "this happened" or "this is the decision to make" is not a safe thing to publish even provisionally.

## Confidence on relationships, not just nodes

A `relationship` can optionally carry its own `confidence`, using this same five-state vocabulary (see `/docs/relationship-model.md`). This exists because two well-verified nodes being connected doesn't make the specific *claim that they're connected* equally well-verified — the node's confidence describes the node's own content, not every inference drawn between it and something else. If an edge omits `confidence`, it's read as inheriting its source object's confidence.

## Who created, reviewed, and approved a record

Alongside `confidence`, an object can carry `created_by`, `reviewed_by`, and `approved_by` (names/handles), plus an append-only `history` array logging every `created` / `updated` / `reviewed` / `approved` / `archived` / `retracted` event with its date, actor, and the `version` it applied to. This is what makes a confidence level auditable rather than asserted: given an object claiming `Reviewed`, a reader can check *who* reviewed it and *when* via `reviewed_by` and `history`, not just take the field's word for it. See `/schemas/common/history-entry.schema.json` and `/ONTOLOGY.md`.
