import type { LoadedEntity, Ontology, ValidationIssue } from "../types.js";

/**
 * Cycle detection is scoped per verb (see ontology.cycle_detection_scope):
 * two different verbs pointing in opposite directions between the same pair
 * of objects encode two distinct facts, not a loop. A real cycle is a chain
 * of edges that all share one verb and loop back on themselves.
 */
export function checkCircularRelationships(
  entities: LoadedEntity[],
  ontology: Ontology,
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const byId = new Map<string, LoadedEntity>();
  for (const entity of entities) {
    if (typeof entity.data?.id === "string") byId.set(entity.data.id, entity);
  }

  for (const verb of ontology.acyclic_verbs) {
    const adjacency = new Map<string, string[]>();
    for (const entity of entities) {
      const sourceId = entity.data?.id;
      if (typeof sourceId !== "string") continue;
      for (const rel of entity.data?.relationships ?? []) {
        if (rel?.type !== verb || typeof rel.target_id !== "string") continue;
        if (!byId.has(rel.target_id)) continue; // dangling refs are reported elsewhere
        const list = adjacency.get(sourceId) ?? [];
        list.push(rel.target_id);
        adjacency.set(sourceId, list);
      }
    }

    const WHITE = 0;
    const GRAY = 1;
    const BLACK = 2;
    const color = new Map<string, number>();
    const reported = new Set<string>();

    const visit = (nodeId: string, stack: string[]): void => {
      color.set(nodeId, GRAY);
      stack.push(nodeId);

      for (const neighbor of adjacency.get(nodeId) ?? []) {
        const neighborColor = color.get(neighbor) ?? WHITE;
        if (neighborColor === WHITE) {
          visit(neighbor, stack);
        } else if (neighborColor === GRAY) {
          const cycleStart = stack.indexOf(neighbor);
          const cyclePath = [...stack.slice(cycleStart), neighbor];
          const cycleKey = [...cyclePath].sort().join(">");
          if (!reported.has(cycleKey)) {
            reported.add(cycleKey);
            issues.push({
              rule: "circular_relationship",
              severity: "error",
              entityId: neighbor,
              message: `Circular '${verb}' chain detected: ${cyclePath.join(" -> ")}`,
            });
          }
        }
      }

      stack.pop();
      color.set(nodeId, BLACK);
    };

    for (const nodeId of adjacency.keys()) {
      if ((color.get(nodeId) ?? WHITE) === WHITE) {
        visit(nodeId, []);
      }
    }
  }

  return issues;
}
