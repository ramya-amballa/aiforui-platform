# Editions

The AI Governance Workbench's canonical dataset is released as numbered, citable editions rather than added to continuously and silently. Each edition is a snapshot: a fixed set of incidents and the governance objects linked to them, described in a release note that never changes after publication (later editions record what changed *since* it, not revise it).

| Edition | Incidents | Status |
|---|---|---|
| [1.0](edition-1.0.md) | 20 | Released 2026-08-04 |
| [1.1](edition-1.1.md) | 35 | Released 2026-08-04 |
| 1.2 | 50 | Planned |
| 2.0 | 100 | Planned |

## Why editions, not a rolling feed

A knowledge graph that grows by unstructured accretion is hard to cite, hard to audit, and hard to reason about ("which version of the dataset supports this claim?"). Numbered editions give the Workbench the same property a published reference work has: you can cite "AI Governance Workbench, Edition 1.1" the way you'd cite an edition of any reference text, and the citation stays meaningful even after Edition 1.2 ships.

## What every release note documents

Per edition: new incidents (with IDs), new Governance Decisions/Design Patterns/Framework Controls/Evidence Types/Board Questions, coverage improvements (jurisdictions, harm types, frameworks newly represented), and editorial changes (any refinement to how objects are curated, not just what was added). See [`edition-1.0.md`](edition-1.0.md) for the template this follows.

## Editions vs. product milestones

Editions above are strictly about canonical *content* — they don't grow when the software changes. Phase 3 shipped the [Explorer](../../explorer/README.md), the first public interface onto the graph (search, browsing, node detail pages, framework pages, a graph visualization) — a product milestone, not a new edition, since it added zero canonical objects. It sits on top of Edition 1.1 and will automatically reflect Edition 1.2 and later once they're published, with no Explorer code changes required.
