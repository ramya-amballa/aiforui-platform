import type { LoadedEntity, ValidationIssue } from "../types.js";

export function checkDuplicateIds(entities: LoadedEntity[]): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const seen = new Map<string, string>();

  for (const entity of entities) {
    const id = entity.data?.id;
    if (typeof id !== "string" || id.length === 0) continue;

    const existingFile = seen.get(id);
    if (existingFile) {
      issues.push({
        rule: "duplicate_id",
        severity: "error",
        filePath: entity.filePath,
        entityId: id,
        message: `Duplicate id '${id}' also declared in ${existingFile}`,
      });
    } else {
      seen.set(id, entity.filePath);
    }
  }

  return issues;
}

/**
 * Slugs are the permanent public address for an object (e.g. '/decisions/<slug>'),
 * so they only need to be unique within their own entity type, not dataset-wide.
 */
export function checkDuplicateSlugs(entities: LoadedEntity[]): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const seenByType = new Map<string, Map<string, string>>();

  for (const entity of entities) {
    const slug = entity.data?.slug;
    if (typeof slug !== "string" || slug.length === 0) continue;

    const seen = seenByType.get(entity.entityType) ?? new Map<string, string>();
    const existingFile = seen.get(slug);
    if (existingFile) {
      issues.push({
        rule: "duplicate_slug",
        severity: "error",
        filePath: entity.filePath,
        entityId: typeof entity.data?.id === "string" ? entity.data.id : undefined,
        message: `Duplicate slug '${slug}' within entity type '${entity.entityType}', also declared in ${existingFile}`,
      });
    } else {
      seen.set(slug, entity.filePath);
    }
    seenByType.set(entity.entityType, seen);
  }

  return issues;
}
