import { buildAjv, compileEntityValidators, loadOntology } from "./load-schemas.js";
import { loadAllData } from "./load-data.js";
import { checkSchema } from "./rules/schema.js";
import { checkDuplicateIds, checkDuplicateSlugs } from "./rules/duplicate-ids.js";
import { checkRelationships } from "./rules/relationships.js";
import { checkCitations } from "./rules/citations.js";
import { checkCircularRelationships } from "./rules/circular.js";
import { printReport } from "./report.js";
import type { ValidationIssue } from "./types.js";

function main(): void {
  const ajv = buildAjv();
  const validators = compileEntityValidators(ajv);
  const ontology = loadOntology();
  const { entities, parseErrors } = loadAllData();

  const issues: ValidationIssue[] = [];

  for (const err of parseErrors) {
    issues.push({
      rule: "invalid_json",
      severity: "error",
      filePath: err.filePath,
      message: `File is not valid JSON: ${err.message}`,
    });
  }

  // Schema validation must pass before graph-level rules run, since those
  // rules assume fields like `id`, `relationships`, and `citations` exist
  // and are shaped correctly.
  issues.push(...checkSchema(entities, validators));

  if (issues.filter((i) => i.severity === "error").length === 0) {
    issues.push(...checkDuplicateIds(entities));
    issues.push(...checkDuplicateSlugs(entities));
    issues.push(...checkRelationships(entities, ontology));
    issues.push(...checkCitations(entities));
    issues.push(...checkCircularRelationships(entities, ontology));
  } else {
    console.error("Skipping graph-level checks (duplicate IDs/slugs, orphans, citations, cycles) until schema errors are fixed.\n");
  }

  printReport(issues, entities.length);
  const hasErrors = issues.some((i) => i.severity === "error");
  process.exit(hasErrors ? 1 : 0);
}

main();
