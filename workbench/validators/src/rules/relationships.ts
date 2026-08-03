import type { EntityType, LoadedEntity, Ontology, ValidationIssue } from "../types.js";

function tripleAllowed(
  ontology: Ontology,
  verb: string,
  sourceType: EntityType,
  targetType: EntityType,
): boolean {
  const relType = ontology.relationship_types.find((r) => r.verb === verb);
  if (!relType) return false;
  return relType.allowed.some(
    (t) =>
      (t.source_type === "*" || t.source_type === sourceType) &&
      (t.target_type === "*" || t.target_type === targetType),
  );
}

export function checkRelationships(
  entities: LoadedEntity[],
  ontology: Ontology,
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const byId = new Map<string, LoadedEntity>();
  for (const entity of entities) {
    if (typeof entity.data?.id === "string") byId.set(entity.data.id, entity);
  }

  const knownVerbs = new Set(ontology.relationship_types.map((r) => r.verb));
  const degree = new Map<string, number>();
  const bump = (id: string) => degree.set(id, (degree.get(id) ?? 0) + 1);
  const outboundCount = new Map<string, number>();

  for (const entity of entities) {
    const sourceId = entity.data?.id;
    const relationships = entity.data?.relationships ?? [];
    if (typeof sourceId !== "string") continue;

    for (const rel of relationships) {
      if (!rel || typeof rel.type !== "string" || typeof rel.target_id !== "string") continue;

      if (rel.target_id === sourceId) {
        issues.push({
          rule: "self_relationship",
          severity: "error",
          filePath: entity.filePath,
          entityId: sourceId,
          message: `Relationship '${rel.type}' targets its own object (${sourceId}).`,
        });
        continue;
      }

      if (!knownVerbs.has(rel.type)) {
        issues.push({
          rule: "invalid_relationship_type",
          severity: "error",
          filePath: entity.filePath,
          entityId: sourceId,
          message: `Relationship type '${rel.type}' is not a verb defined in the ontology.`,
        });
        continue;
      }

      const target = byId.get(rel.target_id);
      if (!target) {
        issues.push({
          rule: "orphan_reference",
          severity: "error",
          filePath: entity.filePath,
          entityId: sourceId,
          message: `Relationship '${rel.type}' points to '${rel.target_id}', which does not exist in the dataset.`,
        });
        continue;
      }

      if (target.entityType !== rel.target_type) {
        issues.push({
          rule: "relationship_target_type_mismatch",
          severity: "error",
          filePath: entity.filePath,
          entityId: sourceId,
          message: `Relationship '${rel.type}' declares target_type '${rel.target_type}' for '${rel.target_id}', but that object is actually of type '${target.entityType}'.`,
        });
        continue;
      }

      if (!tripleAllowed(ontology, rel.type, entity.entityType, target.entityType)) {
        issues.push({
          rule: "invalid_relationship_type",
          severity: "error",
          filePath: entity.filePath,
          entityId: sourceId,
          message: `The ontology does not permit '${entity.entityType} -${rel.type}-> ${target.entityType}'. See /relationships/ontology.json.`,
        });
        continue;
      }

      bump(sourceId);
      bump(rel.target_id);
      outboundCount.set(sourceId, (outboundCount.get(sourceId) ?? 0) + 1);
    }
  }

  for (const entity of entities) {
    const id = entity.data?.id;
    if (typeof id !== "string") continue;
    if (!degree.has(id)) {
      issues.push({
        rule: "orphan_node",
        severity: "error",
        filePath: entity.filePath,
        entityId: id,
        message: `'${id}' has no valid incoming or outgoing relationships and is disconnected from the graph.`,
      });
    }

    const count = outboundCount.get(id) ?? 0;
    const { soft_limit: softLimit, hard_limit: hardLimit } = ontology.outbound_relationship_limits;
    if (count > hardLimit) {
      issues.push({
        rule: "outbound_relationship_hard_limit",
        severity: "error",
        filePath: entity.filePath,
        entityId: id,
        message: `'${id}' has ${count} outbound relationships, exceeding the hard limit of ${hardLimit}. Split this object or reconsider the relationships.`,
      });
    } else if (count > softLimit) {
      issues.push({
        rule: "outbound_relationship_soft_limit",
        severity: "warning",
        filePath: entity.filePath,
        entityId: id,
        message: `'${id}' has ${count} outbound relationships, above the recommended soft limit of ${softLimit}. Consider simplifying relationships.`,
      });
    }
  }

  return issues;
}
