import type { EntityType, LoadedEntity, ValidationIssue } from "../types.js";

const CITATION_REQUIRED_CONFIDENCE = new Set(["Verified", "Reviewed"]);
const ALWAYS_REQUIRE_CITATION: EntityType[] = ["decision", "incident"];

export function checkCitations(entities: LoadedEntity[]): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  for (const entity of entities) {
    const id = entity.data?.id;
    const citations = entity.data?.citations ?? [];
    const confidence = entity.data?.confidence;

    const mustHaveCitation =
      ALWAYS_REQUIRE_CITATION.includes(entity.entityType) ||
      (typeof confidence === "string" && CITATION_REQUIRED_CONFIDENCE.has(confidence));

    if (mustHaveCitation && citations.length === 0) {
      issues.push({
        rule: "missing_citation",
        severity: "error",
        filePath: entity.filePath,
        entityId: typeof id === "string" ? id : undefined,
        message:
          entity.entityType === "decision" || entity.entityType === "incident"
            ? `'${entity.entityType}' objects must always carry at least one citation; '${id}' has none.`
            : `Objects with confidence '${confidence}' must carry at least one citation; '${id}' has none.`,
      });
    }

    const citationIds = new Set<string>();
    for (const citation of citations) {
      if (!citation || typeof citation.id !== "string") continue;
      if (citationIds.has(citation.id)) {
        issues.push({
          rule: "duplicate_citation_id",
          severity: "error",
          filePath: entity.filePath,
          entityId: typeof id === "string" ? id : undefined,
          message: `Citation id '${citation.id}' is declared more than once within '${id}'.`,
        });
      }
      citationIds.add(citation.id);
    }

    for (const rel of entity.data?.relationships ?? []) {
      for (const citationId of rel?.citation_ids ?? []) {
        if (!citationIds.has(citationId)) {
          issues.push({
            rule: "dangling_citation_reference",
            severity: "error",
            filePath: entity.filePath,
            entityId: typeof id === "string" ? id : undefined,
            message: `Relationship '${rel.type}' -> '${rel.target_id}' references citation_id '${citationId}', which is not declared in this object's citations array.`,
          });
        }
      }
    }
  }

  return issues;
}
