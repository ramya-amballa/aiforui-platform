import type { ValidateFunction } from "ajv";
import type { EntityType, LoadedEntity, ValidationIssue } from "../types.js";

export function checkSchema(
  entities: LoadedEntity[],
  validators: Record<EntityType, ValidateFunction>,
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  for (const entity of entities) {
    const validate = validators[entity.entityType];
    const valid = validate(entity.data);
    if (!valid) {
      for (const err of validate.errors ?? []) {
        issues.push({
          rule: "schema_violation",
          severity: "error",
          filePath: entity.filePath,
          entityId: typeof entity.data?.id === "string" ? entity.data.id : undefined,
          message: `${err.instancePath || "(root)"} ${err.message ?? "is invalid"}`,
        });
      }
    }
  }

  return issues;
}
