# Relationships

This directory holds the machine-readable relationship ontology (`ontology.json`) that the validation engine in `/validators` enforces.

`ontology.json` defines:

- The six canonical `entity_types`.
- Every permitted `(verb, source_type, target_type)` triple. A relationship whose triple isn't listed here is rejected as an invalid relationship type, even if the verb itself is valid in general.
- `acyclic_verbs` — the subset of verbs that must not form a cycle when followed across the whole dataset. `RELATED_TO` is deliberately excluded, since it is a non-hierarchical, symmetric association.

For the reasoning behind each verb and the full allowed-triples table in prose form, see [`/docs/relationship-model.md`](../docs/relationship-model.md).

Do not add a new verb or triple here without updating that document — the ontology file is the enforced ruleset, the doc is the explanation of *why* it looks the way it does.
