# Relationship Model

The dataset is a graph, not a collection of isolated documents. Every edge in that graph is a typed, directed relationship declared inline on the source object's `relationships` array (see `/schemas/common/relationship.schema.json`). Arbitrary/untyped links are not permitted — every edge must carry one of a fixed set of verbs, and the machine-readable ruleset for which verbs may connect which entity types lives in [`/relationships/ontology.json`](../relationships/ontology.json).

## The six entity types

`decision`, `incident`, `pattern`, `control`, `evidence`, `board_question` — one for each canonical schema in `/schemas`.

## The seven verbs, and why each one exists

| Verb | Meaning | Allowed `source_type -> target_type` |
|---|---|---|
| `RESULTED_FROM` | The source object came into being as a direct consequence of the target. | `decision -> incident`, `decision -> decision`, `board_question -> incident` |
| `MITIGATED_BY` | The risk represented by the source is reduced by the target. | `incident -> decision`, `incident -> pattern`, `incident -> control` |
| `IMPLEMENTED_BY` | The source is put into practice through the target. | `decision -> pattern`, `control -> pattern` |
| `SATISFIES_CONTROL` | The source fulfils the requirement described by the target control. | `decision -> control`, `pattern -> control` |
| `REQUIRES_EVIDENCE` | The source cannot be considered satisfied without the target evidence type. | `decision -> evidence`, `control -> evidence`, `pattern -> evidence` |
| `RAISES_BOARD_QUESTION` | The source implies a question board-level oversight should ask. | `decision -> board_question`, `incident -> board_question`, `control -> board_question` |
| `RELATED_TO` | A general, non-hierarchical association that doesn't fit a more specific verb. | any -> any |

Every triple in that table is enumerated explicitly in `ontology.json`. A relationship whose `(verb, source_type, target_type)` isn't listed is rejected by the validator as an `invalid_relationship_type`, even when the verb itself is a recognised word — e.g. `board_question -SATISFIES_CONTROL-> control` is nonsensical (a question doesn't satisfy a control) and is rejected, even though `SATISFIES_CONTROL` is a real verb.

`RELATED_TO` is the deliberate escape hatch: it exists so contributors aren't forced to misuse a more specific verb just to express "these two things are relevant to each other." It is intentionally the *only* verb permitted between any pair of types, which keeps every other verb meaningfully constrained.

### Why decisions sit at the centre

Per the product's core organising principle, most verbs above either originate at or terminate at a `decision`. Reading the table as a graph: an `incident` typically flows into a `decision` (via `MITIGATED_BY` from the incident, or `RESULTED_FROM` from the decision back to the incident), a `decision` flows out to a `pattern` (`IMPLEMENTED_BY`), a `control` (`SATISFIES_CONTROL`), an `evidence` type (`REQUIRES_EVIDENCE`), and a `board_question` (`RAISES_BOARD_QUESTION`). `pattern` and `control` can also connect directly to each other and to `evidence`, because in practice an implementation pattern satisfying a control, or a control requiring evidence, doesn't always need a decision restated at every hop — but the decision is still reachable within one or two edges from everything else in a well-formed dataset.

### Why `decision RESULTED_FROM incident` and `incident MITIGATED_BY decision` can coexist

These are two distinct, simultaneously-true facts about the same pair of objects, not a contradiction: the decision was caused by the incident, *and* the decision (once implemented) reduces the risk of that class of incident recurring. See "Cycle detection is scoped per verb" below for why the validator does not treat this as a circular relationship.

## Validation the ontology enables

Given `ontology.json`, the validator (`/validators`) can mechanically reject:

- **Invalid relationship types** — a verb that doesn't exist, or a verb used between a pair of entity types not listed in its `allowed` array.
- **Dangling references** — a `target_id` that doesn't resolve to any object in the dataset.
- **Target-type mismatches** — a `target_id` that exists, but whose actual entity type doesn't match the `target_type` declared on the edge (catches stale references after an object's type is corrected, or simple copy-paste errors).
- **Orphan nodes** — any object with zero relationships pointing to it *and* zero relationships it points out to is disconnected from the graph and rejected. A well-formed dataset has no islands; if an object genuinely has nothing to connect to yet, it isn't ready to leave `draft` status.
- **Circular relationships** — see below.

## Cycle detection is scoped per verb

`ontology.json`'s `acyclic_verbs` list is every verb except `RELATED_TO`. For each of those verbs independently, the validator builds a directed graph using only edges of that one verb and looks for a cycle (e.g. `decision-A RESULTED_FROM decision-B RESULTED_FROM decision-A` — a decision cannot both cause and be caused by the same other decision; that's corrupted lineage data, not a real-world situation).

Cycle detection is deliberately **not** run across the union of all acyclic verbs at once, because two different verbs pointing in opposite directions between the same pair of objects encode two distinct facts rather than a loop — see the `decision RESULTED_FROM incident` / `incident MITIGATED_BY decision` example above. Combining verbs into one cycle check would make that ordinary, correct pattern impossible to express. `RELATED_TO` is excluded entirely because it's explicitly non-hierarchical and symmetric — a RELATED_TO "cycle" (A related to B related to A) isn't a modelling error, it's just two contributors independently noting the same association from each side.

## Extending the ontology

Adding a new verb or a new allowed triple means editing `ontology.json` and this document together — the JSON file is the enforced ruleset, this document is the explanation of why it looks the way it does, and they should never drift apart. Do not add a triple just to make a specific piece of data pass; if the ontology doesn't have a meaningful verb for the relationship you're trying to express, that's a sign either `RELATED_TO` is the right choice, or the ontology itself needs a considered addition (open an issue/PR discussing the new verb's meaning, not just its plumbing).
