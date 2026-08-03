# Schemas Reference

All schemas are JSON Schema (2020-12 dialect) under `/schemas`. The six canonical entity schemas each `allOf`-compose the shared building blocks in `/schemas/common` and then add their own required, type-specific fields.

## Shared building blocks (`/schemas/common`)

- **`base-entity.schema.json`** — every field common to all six entity types: `id`, `title`, `description`, `version`, `status`, `confidence`, `created_date`, `updated_date`, `tags`, `citations`, `relationships`, and the optional `contributors`. See field-level rationale in `/docs/confidence-model.md` and `/docs/citation-model.md`.
- **`citation.schema.json`** — one external source reference. See `/docs/citation-model.md`.
- **`relationship.schema.json`** — one typed, directed edge to another object. See `/docs/relationship-model.md`.

Each entity schema's `id` pattern narrows the generic base pattern to its own type prefix (e.g. `decision.schema.json` requires `^decision-[a-z0-9]+(-[a-z0-9]+)*$`), so an object's ID is self-describing — you can tell an object's type from its ID alone, and the validator uses that prefix as a sanity check anywhere IDs are cross-referenced.

## The six entity schemas

### Governance Decision (`decision.schema.json`, id prefix `decision-`)
The hub entity — see `/docs/architecture.md` for why. Adds `decision_statement` (the concrete, testable commitment being made), `decision_type` (`policy` / `technical_control` / `risk_acceptance` / `process` / `organizational`), and optional `decision_context`, `governing_body`, `jurisdiction`, `frameworks_referenced`, `alternatives_considered`.

### Incident (`incident.schema.json`, id prefix `incident-`)
A real-world event where an AI system caused, or was alleged to cause, harm or a governance breach — the evidence base for why decisions get made. Adds required `occurred_date` (distinct from `created_date`, the record's own creation time), and optional `organizations_involved`, `harm_types`, `ai_system_category`, `jurisdiction`, `severity`, `root_cause`.

### Design Pattern (`pattern.schema.json`, id prefix `pattern-`)
A reusable approach for implementing a decision. Adds required `problem` and `solution`, and optional `applicability`, `consequences`, `maturity` (`experimental` / `emerging` / `established`).

### Framework Control (`control.schema.json`, id prefix `control-`)
A specific control drawn from a named external framework/standard/regulation. Adds required `framework_name`, `control_reference` (the framework's own identifier, e.g. `MEASURE 2.11`), `control_text`, and optional `control_family`.

### Evidence Type (`evidence.schema.json`, id prefix `evidence-`)
A category of artifact that demonstrates a control or decision has been satisfied. Adds required `evidence_description`, and optional `collection_method`, `retention_period`, `artifact_format`.

### Board Question (`board_question.schema.json`, id prefix `board_question-`)
A question board-level oversight should ask in light of a decision, incident, or control. Adds required `question_text`, and optional `audience`, `rationale`, `follow_up_actions`.

## Compiling and validating

`/validators` loads every schema above via `ajv` (2020-12 dialect, `ajv-formats` for `date`/`uri` format checks) and compiles one validator per entity type, registering the three common schemas first so `$ref`s to them resolve. See `/validators/README.md` for how to run it, and `/docs/relationship-model.md` for the graph-level rules it applies on top of schema validation.
