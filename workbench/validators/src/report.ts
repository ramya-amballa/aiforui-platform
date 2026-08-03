import path from "node:path";
import { WORKBENCH_ROOT } from "./load-schemas.js";
import type { ValidationIssue } from "./types.js";

function printGroup(issues: ValidationIssue[]): void {
  const byFile = new Map<string, ValidationIssue[]>();
  for (const issue of issues) {
    const key = issue.filePath ? path.relative(WORKBENCH_ROOT, issue.filePath) : "(dataset-wide)";
    const list = byFile.get(key) ?? [];
    list.push(issue);
    byFile.set(key, list);
  }

  for (const [file, fileIssues] of [...byFile.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    console.error(file);
    for (const issue of fileIssues) {
      console.error(`  [${issue.rule}] ${issue.message}`);
    }
    console.error("");
  }
}

/**
 * Warnings never fail the build (see the soft/hard outbound-relationship
 * limits in /relationships/ontology.json); only errors do. The caller
 * decides the process exit code based on whether any errors were passed in.
 */
export function printReport(issues: ValidationIssue[], entityCount: number): void {
  const errors = issues.filter((i) => i.severity === "error");
  const warnings = issues.filter((i) => i.severity === "warning");

  if (issues.length === 0) {
    console.log(`✔ Validated ${entityCount} object(s). No issues found.`);
    return;
  }

  if (errors.length > 0) {
    console.error(`✘ Validated ${entityCount} object(s). ${errors.length} error(s), ${warnings.length} warning(s):\n`);
    printGroup(errors);
  } else {
    console.log(`✔ Validated ${entityCount} object(s). ${warnings.length} warning(s):\n`);
  }

  if (warnings.length > 0) {
    printGroup(warnings);
  }
}
