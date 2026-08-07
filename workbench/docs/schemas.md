# Schemas Reference

All schemas are JSON Schema (2020-12 dialect) under `/schemas`. The six canonical entity schemas each `allOf`-compose the shared building blocks in `/schemas/common` and then add their own required, type-specific fields.

## Shared building blocks (`/schemas/common`)

- **`base-entity.schema.json`** — every field common to all six entity types: `id`, `slug`, `title`, `description`, `version`, `status`, `confidence`, `created_date`, `updated_date`, `tags`, `citations`, `relationships`, and the optional `contributors`, `created_by`, `reviewed_by`, `approved_by`, `history`. See field-level rationale in `/docs/confidence-model.md`, `/docs/citation-model.md`, and `/ONTOLOGY.md`.
- **`citation.schema.json`** — one external source reference. See `/docs/citation-model.md`.
- **`relationship.schema.json`** — one typed, directed edge to another object, with a mandatory `reason`. See `/docs/relationship-model.md`.
- **`history-entry.schema.json`** — one append-only lifecycle log entry (`created` / `updated` / `reviewed` / `approved` / `archived` / `retracted`), each with `date`, `by`, and the `version` it applied to.

### `id` vs `slug`

Every object has two identifiers with different jobs:

- **`id`** — a deterministic, type-prefixed, sequentially-assigned code (`DEC-001`, `INC-001`, ...). Short, stable, and used everywhere internally: `relationships[].target_id`, cross-references, the validator's graph checks. Each entity schema narrows the base `id` pattern (`^[A-Z]{3}-\d{3,}$`) to its own prefix — see the table below and `/ONTOLOGY.md` for the full prefix list, including reserved future prefixes.
- **`slug`** — a permanent, human-readable, kebab-case address (e.g. `bias-audit-gate-for-hiring-ai`), unique within the object's own entity type, meant for URLs (`/decisions/<slug>`) once a frontend exists. Once published, a slug should not change — it's the public-facing address readers and other sites may link to, independent of the internal `id`.

Neither is a UUID, and that's deliberate: `id` is short and sortable for internal use, `slug` is descriptive and stable for external use. See `/ONTOLOGY.md`.

## The six entity schemas

| Type | Schema | `id` prefix |
|---|---|---|
| Governance Decision | `decision.schema.json` | `DEC-` |
| Incident | `incident.schema.json` | `INC-` |
| Design Pattern | `pattern.schema.json` | `PAT-` |
| Framework Control | `control.schema.json` | `CTR-` |
| Evidence Type | `evidence.schema.json` | `EVI-` |
| Board Question | `board_question.schema.json` | `BRD-` |

### Governance Decision (`decision.schema.json`, id prefix `DEC-`)
The hub entity — see `/docs/architecture.md` for why. Adds `decision_statement` (the concrete, testable commitment being made), `decision_type` (`policy` / `technical_control` / `risk_acceptance` / `process` / `organizational`), and optional `decision_context`, `governing_body`, `jurisdiction`, `frameworks_referenced`, `alternatives_considered`.

### Incident (`incident.schema.json`, id prefix `INC-`)
A real-world event where an AI system caused, or was alleged to cause, harm or a governance breach — the evidence base for why decisions get made. Adds required `occurred_date` (distinct from `created_date`, the record's own creation time), and optional `organizations_involved`, `harm_types`, `ai_system_category`, `jurisdiction`, `severity`, `root_cause`.

### Design Pattern (`pattern.schema.json`, id prefix `PAT-`)
A reusable approach for implementing a decision. Adds required `problem` and `solution`, and optional `applicability`, `consequences`, `maturity` (`experimental` / `emerging` / `established`).

### Framework Control (`control.schema.json`, id prefix `CTR-`)
A specific control drawn from a named external framework/standard/regulation. Adds required `framework_name`, `control_reference` (the framework's own identifier, e.g. `MEASURE 2.11`), `control_text`, and optional `control_family`.

### Evidence Type (`evidence.schema.json`, id prefix `EVI-`)
A category of artifact that demonstrates a control or decision has been satisfied. Adds required `evidence_description`, and optional `collection_method`, `retention_period`, `artifact_format`.

### Board Question (`board_question.schema.json`, id prefix `BRD-`)
A question board-level oversight should ask in light of a decision, incident, or control. Adds required `question_text`, and optional `audience`, `rationale`, `follow_up_actions`.

## Compiling and validating

`/validators` loads every schema above via `ajv` (2020-12 dialect, `ajv-formats` for `date`/`uri` format checks) and compiles one validator per entity type, registering the common schemas first so `$ref`s to them resolve. See `/validators/README.md` for how to run it, and `/docs/relationship-model.md` for the graph-level rules it applies on top of schema validation.
