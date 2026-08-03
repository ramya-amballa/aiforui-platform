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
