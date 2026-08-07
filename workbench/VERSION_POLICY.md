# Version Policy

This project versions three different things, and keeping them distinct is the point of this document: **object versions** (one JSON file's own history), **dataset editions** (a snapshot of the whole `/data` directory), and **structural stability** (the schemas, ontology, and validation rules everything else depends on). Confusing these — treating an object edit like a schema change, or an edition release like a breaking change — is the failure mode this policy exists to prevent.

## A note on terminology, resolved here

Phase 4 of this project's development was framed as preparing "Edition 1.0 for public release." Read literally against `/docs/releases/`, that would collide with the dataset edition already named 1.0 (the Foundational Twenty, 20 incidents, released 2026-08-04) and the current edition, 1.1 (35 incidents). No renumbering has happened as a result, and none should: **dataset editions and publication readiness are different axes**, defined separately below, and a phase focused on institutional governance does not retroactively rename a dataset snapshot that already shipped and was cited. Edition 1.1 is, as of this document, the first edition to be published *under* this governance layer — that is what "ready for public release" means here, not a new edition number.

## Object versions

Every canonical object carries its own semver-style `version` (`1.0.0`), independent of every other object's version and independent of the dataset edition. It bumps on any substantive edit, paired with a `history` entry (`/schemas/common/history-entry.schema.json`) naming the actor, date, and reason — see `EDITORIAL_POLICY.md`'s update policy. There is no cross-object coordination requirement here: `DEC-001` being at `1.0.3` while `INC-020` is still at `1.0.0` is normal and expected; it just means one has been edited more than the other.

## Dataset editions

The dataset ships as numbered editions (`/docs/releases/`) — 1.0, 1.1, 1.2, 2.0, and so on — each a fixed, citable snapshot of `/data` at a point in time, accompanied by a release note that is never rewritten after publication (see `METHODOLOGY.md`'s release methodology). Edition numbering to date has tracked incident-count milestones (20 → 35 → a planned 50 → a planned 100), and that convention continues:

- **Minor editions** (1.0 → 1.1 → 1.2) add canonical content — new incidents and the governance objects they connect to, or, as of this policy, non-structural improvements like the citation-depth and naming-consistency work described in `/docs/quality-audit-2026-08.md`. A minor edition never changes the ontology, schemas, or validation rules.
- **Major editions** (1.x → 2.0) are reserved for milestones the project considers a genuine step-change in what the dataset represents — the 100-incident milestone already planned for 2.0 is the current example. A major edition may also be warranted by a deliberate, documented ontology or schema change (see "Ontology and schema stability" below), in which case it is a major edition *because* the underlying structure changed, not merely because a round number was reached.
- **Patch releases** are not currently a distinct edition tier for the dataset as a whole — corrections happen continuously per `EDITORIAL_POLICY.md`'s correction policy and are captured in individual objects' own `history`, not as a separate numbered dataset release. If patch-level dataset releases become useful (e.g., a batch of corrections significant enough to warrant its own citable snapshot between editions), this policy should be amended to define one explicitly rather than one being introduced ad hoc.

An edition is not permitted to ship without passing `RELEASE_CHECKLIST.md` in full.

## Ontology and schema stability

The ontology (`/relationships/ontology.json`), the six entity schemas (`/schemas`), and the validation engine's structural rules (`/validators`) are the contract every other part of this project — the editorial tools, the Explorer, any future API — is built against. As of this phase, **they are considered stable** and are explicitly out of scope for casual change:

- **Adding** a new relationship verb, a new allowed `(verb, source_type, target_type)` triple, or a new optional field to an existing schema is a **backward-compatible** change: existing data remains valid, existing tooling keeps working. This is the lowest-friction category of structural change, but is still a deliberate act — see `/docs/relationship-model.md`'s "Extending the ontology" for the bar it must clear (a real-world relationship the current verbs can't express, not convenience).
- **Removing or narrowing** an existing verb, triple, required field, or enum value is a **breaking change**: it can invalidate existing canonical data. This requires: a written rationale, a migration plan for every existing object the change affects, and a major-edition-level release, never a quiet patch.
- **A new entity type** (drawing on one of the reserved prefixes in `ONTOLOGY.md` — `LAW-`, `STD-`, `ORG-`, `PER-`, `TAG-`) is the largest category of structural change this project anticipates and is deliberately not undertaken lightly: it touches the schema set, the ontology, every editorial tool, and the Explorer's information architecture at once. Reserving the prefixes now, unused, is exactly so this remains possible later without a numbering collision — see `ONTOLOGY.md`.

## Deprecation policy

Nothing in the ontology or schemas is deleted outright. Deprecating a verb, field, or entity type follows this sequence: (1) the change is proposed and documented with its rationale, same as any structural change; (2) the deprecated element is marked as such in `/relationships/ontology.json` or the relevant schema's description, and existing data using it continues to validate; (3) new content is discouraged from using it via `/docs` and `/editorial` guidance, not a hard validator error; (4) removal, if it ever happens, follows the breaking-change path above, at a major edition, with a stated migration for existing data. A deprecated element that still has canonical data depending on it is not removed — the data is migrated first, or the deprecation is reconsidered.

## Relationship evolution

Relationship *instances* (individual edges in `/data`) evolve constantly and require no special versioning beyond the object-version discipline above — an object's `relationships` array changing is a substantive edit like any other. Relationship *types* (the verbs and triples in the ontology) evolve rarely and only through the backward-compatible/breaking-change distinction above. The two should never be confused: adding a `RELATED_TO` edge to a new object this week is routine content work; adding an eighth verb to the ontology is a structural change subject to this policy.

## Explorer versioning

The Explorer (`/explorer`) is a static build derived entirely from `/data` and the ontology (`ONTOLOGY.md`'s Canonical Principle) and currently has no independent version number — it simply reflects whatever edition of the dataset it was last built against. This phase does not change that. If the Explorer's own architecture becomes complex enough to warrant independent versioning later, that is itself a structural decision this policy should be amended to cover, not one to make implicitly.

## Future-proofing summary

| Change type | Example | Requires |
|---|---|---|
| Object edit | Fixing a citation, updating a description | `version` bump + `history` entry |
| New canonical content | Adding an incident and its governance cluster | Normal review (`REVIEW_PROCESS.md`) |
| Minor edition | Edition 1.1 → 1.2 | `RELEASE_CHECKLIST.md` in full |
| Major edition | Edition 1.x → 2.0, or a deliberate structural change | Everything above, plus written rationale and (if structural) a migration plan |
| Backward-compatible ontology/schema addition | A new relationship verb | Written rationale in `/docs/relationship-model.md`, major-edition-level scrutiny per `GOVERNANCE_CHARTER.md` |
| Breaking ontology/schema change | Removing a verb or required field | Written rationale, migration plan for all affected data, major edition only |
| New entity type | Activating a reserved prefix (`LAW-`, etc.) | The full breaking-change path, treated as the largest structural change this project anticipates |
