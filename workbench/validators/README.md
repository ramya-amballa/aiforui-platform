# Validators

The validation engine. Run from `/workbench`:

```sh
npm install
npm run validate
```

Exits non-zero and prints a per-file report if anything fails. This is wired into CI (`.github/workflows/workbench-validate.yml`) on every push/PR touching `/workbench/**`, so it doubles as the merge gate for changes to the dataset.

## What it checks

1. **Schema validation** (`src/rules/schema.ts`) — every object in `/data` against its entity schema in `/schemas`, via `ajv`. This covers both "schema violations" generally and "missing mandatory fields" specifically (JSON Schema's `required` keyword).
2. **Duplicate IDs** (`src/rules/duplicate-ids.ts`) — no two objects anywhere in `/data` may share an `id`.
3. **Relationship integrity** (`src/rules/relationships.ts`) — every relationship's verb and `(source_type, target_type)` triple must be permitted by `/relationships/ontology.json`; every `target_id` must resolve to a real object; that object's actual type must match the declared `target_type`; and every object must have at least one valid relationship (incoming or outgoing) or it's rejected as an orphan node.
4. **Citations** (`src/rules/citations.ts`) — enforces the rule in `/docs/citation-model.md` (mandatory citations for `Incident`/`Decision` objects and for `Verified`/`Reviewed` confidence), plus duplicate citation IDs within an object and dangling `citation_ids` references from relationships.
5. **Circular relationships** (`src/rules/circular.ts`) — per-verb cycle detection across the whole dataset for every verb in `ontology.json`'s `acyclic_verbs`. See `/docs/relationship-model.md` for why this is scoped per verb rather than across all directional verbs combined.

Graph-level checks (2-5) only run once schema validation (1) is clean for every file, since they assume fields like `id`, `relationships`, and `citations` are already well-formed.

## Layout

```
src/
  types.ts           shared TypeScript types
  load-schemas.ts     compiles ajv validators, loads the ontology
  load-data.ts        walks /data and parses every JSON file
  rules/*.ts          one module per rule above
  report.ts           groups issues by file and prints them
  validate.ts         CLI entry point
```
