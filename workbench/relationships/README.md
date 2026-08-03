# Relationships

This directory holds the machine-readable relationship ontology (`ontology.json`) that the validation engine in `/validators` enforces.

`ontology.json` defines:

- The six canonical `entity_types` and their `id_prefixes` (`DEC`, `INC`, `PAT`, `CTR`, `EVI`, `BRD`), plus `reserved_prefixes` earmarked for future entity types (`LAW`, `STD`, `ORG`, `PER`, `TAG`) so the id namespace never collides as the ontology grows. See `/ONTOLOGY.md`.
- Every permitted `(verb, source_type, target_type)` triple. A relationship whose triple isn't listed here is rejected as an invalid relationship type, even if the verb itself is valid in general.
- `acyclic_verbs` — the subset of verbs that must not form a cycle when followed across the whole dataset. `RELATED_TO` is deliberately excluded, since it is a non-hierarchical, symmetric association.
- `outbound_relationship_limits` — the soft (5) and hard (7) caps on an object's outbound edges, enforced by `/validators`.

For the reasoning behind each verb and the full allowed-triples table in prose form, see [`/docs/relationship-model.md`](../docs/relationship-model.md).

Do not add a new verb or triple here without updating that document — the ontology file is the enforced ruleset, the doc is the explanation of *why* it looks the way it does.
