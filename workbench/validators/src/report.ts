import path from "node:path";
import { WORKBENCH_ROOT } from "./load-schemas.js";
import type { ValidationIssue } from "./types.js";

export function printReport(issues: ValidationIssue[], entityCount: number): void {
  if (issues.length === 0) {
    console.log(`✔ Validated ${entityCount} object(s). No issues found.`);
    return;
  }

  const byFile = new Map<string, ValidationIssue[]>();
  for (const issue of issues) {
    const key = issue.filePath ? path.relative(WORKBENCH_ROOT, issue.filePath) : "(dataset-wide)";
    const list = byFile.get(key) ?? [];
    list.push(issue);
    byFile.set(key, list);
  }

  console.error(`✘ Validated ${entityCount} object(s). ${issues.length} issue(s) found:\n`);
  for (const [file, fileIssues] of [...byFile.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    console.error(file);
    for (const issue of fileIssues) {
      console.error(`  [${issue.rule}] ${issue.message}`);
    }
    console.error("");
  }
}
