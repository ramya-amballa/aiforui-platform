import { loadAllData } from "../../../validators/src/load-data.js";
import { loadOntology } from "../../../validators/src/load-schemas.js";
import type { CanonicalEntity, EntityType, LoadedEntity, Ontology, Relationship } from "../../../validators/src/types.js";

export interface Edge {
  relationship: Relationship;
  sourceId: string;
  targetId: string;
}

export interface Graph {
  entities: LoadedEntity[];
  ontology: Ontology;
  byId: Map<string, LoadedEntity>;
  byType: Record<EntityType, LoadedEntity[]>;
  /** Only edges whose target actually resolves in the dataset. */
  outgoing: Map<string, Edge[]>;
  incoming: Map<string, Edge[]>;
}

/**
 * Shared loader for every editorial tool. Deliberately reuses the same
 * loaders the validation engine uses (/validators/src) so "the graph" means
 * the same thing everywhere in the codebase — one source of truth for what
 * counts as an entity, an edge, or the ontology.
 */
export function buildGraph(): Graph {
  const { entities } = loadAllData();
  const ontology = loadOntology();

  const byId = new Map<string, LoadedEntity>();
  for (const entity of entities) {
    if (typeof entity.data?.id === "string") byId.set(entity.data.id, entity);
  }

  const byType: Record<EntityType, LoadedEntity[]> = {
    decision: [],
    incident: [],
    pattern: [],
    control: [],
    evidence: [],
    board_question: [],
  };
  for (const entity of entities) byType[entity.entityType].push(entity);

  const outgoing = new Map<string, Edge[]>();
  const incoming = new Map<string, Edge[]>();
  for (const entity of entities) {
    const sourceId = entity.data?.id;
    if (typeof sourceId !== "string") continue;
    for (const relationship of entity.data?.relationships ?? []) {
      if (!relationship || typeof relationship.target_id !== "string") continue;
      if (!byId.has(relationship.target_id)) continue;
      const edge: Edge = { relationship, sourceId, targetId: relationship.target_id };
      const outList = outgoing.get(sourceId) ?? [];
      outList.push(edge);
      outgoing.set(sourceId, outList);
      const inList = incoming.get(relationship.target_id) ?? [];
      inList.push(edge);
      incoming.set(relationship.target_id, inList);
    }
  }

  return { entities, ontology, byId, byType, outgoing, incoming };
}

export function tripleAllowed(ontology: Ontology, verb: string, sourceType: EntityType, targetType: EntityType): boolean {
  const relType = ontology.relationship_types.find((r) => r.verb === verb);
  if (!relType) return false;
  return relType.allowed.some(
    (t) => (t.source_type === "*" || t.source_type === sourceType) && (t.target_type === "*" || t.target_type === targetType),
  );
}

export function edgeExists(graph: Graph, sourceId: string, targetId: string, verb?: string): boolean {
  const edges = graph.outgoing.get(sourceId) ?? [];
  return edges.some((e) => e.targetId === targetId && (!verb || e.relationship.type === verb));
}

export function outboundCount(graph: Graph, id: string): number {
  return (graph.outgoing.get(id) ?? []).length;
}

export function jaccard(a: string[] = [], b: string[] = []): number {
  const setA = new Set(a.map((s) => s.toLowerCase()));
  const setB = new Set(b.map((s) => s.toLowerCase()));
  if (setA.size === 0 || setB.size === 0) return 0;
  let intersection = 0;
  for (const item of setA) if (setB.has(item)) intersection += 1;
  const union = setA.size + setB.size - intersection;
  return union === 0 ? 0 : intersection / union;
}

export function sharedItems(a: string[] = [], b: string[] = []): string[] {
  const setB = new Set(b.map((s) => s.toLowerCase()));
  return a.filter((item) => setB.has(item.toLowerCase()));
}

export function title(entity: LoadedEntity | undefined): string {
  if (!entity) return "(unknown)";
  return `${entity.data.id} (${entity.data.title})`;
}

export type { CanonicalEntity, EntityType, LoadedEntity, Ontology, Relationship };
