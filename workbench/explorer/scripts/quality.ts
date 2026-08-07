// Computes the "Our Standards" Quality Dashboard's numbers by reusing the
// project's actual, frozen validation and editorial tooling — never by
// re-implementing a check. This mirrors the precedent already set by
// editorial/src/graph-health.ts, which imports the real /validators rule
// functions rather than duplicating their logic, specifically so the two
// can never silently drift apart. Every number here is either a direct
// function call into /validators and /editorial, or a subprocess call to
// the exact npm script a human would run — nothing is estimated or faked.
import { execSync } from "node:child_process";
import { buildAjv, compileEntityValidators, loadOntology, WORKBENCH_ROOT } from "../../validators/src/load-schemas.ts";
import { loadAllData } from "../../validators/src/load-data.ts";
import { checkSchema } from "../../validators/src/rules/schema.ts";
import { checkDuplicateIds, checkDuplicateSlugs } from "../../validators/src/rules/duplicate-ids.ts";
import { checkRelationships } from "../../validators/src/rules/relationships.ts";
import { checkCircularRelationships } from "../../validators/src/rules/circular.ts";
import { scoreCitations } from "../../editorial/src/lib/citation-score.ts";
import type { LoadedEntity } from "../../validators/src/types.ts";

export interface CheckResult {
  pass: boolean | null; // null = could not be verified in this environment, never assumed true
  detail: string;
}

export interface QualityReport {
  generated_at: string;
  canonical_objects: number;
  real_incidents: number;
  entity_types: number;
  checks: {
    schema_validation: CheckResult;
    zero_orphans: CheckResult;
    relationship_integrity: CheckResult;
    type_check: CheckResult;
    editorial_audit: CheckResult;
  };
  citation_completeness: {
    average: number;
    target: number;
  };
}

function runNpmScript(script: string): CheckResult {
  try {
    const output = execSync(`npm run ${script}`, {
      cwd: WORKBENCH_ROOT,
      encoding: "utf-8",
      stdio: "pipe",
      timeout: 120_000,
    });
    return { pass: true, detail: output.trim().split("\n").slice(-3).join(" ") };
  } catch (err) {
    const e = err as { status?: number; stdout?: string; stderr?: string; message?: string };
    if (typeof e.status === "number") {
      // The script ran and reported failure — that's a real, honest FAIL,
      // not an environment problem, so we can trust it.
      const tail = (e.stdout ?? "").trim().split("\n").slice(-3).join(" ");
      return { pass: false, detail: tail || e.message || "check reported failure" };
    }
    // The script could not even run (missing deps, sandboxed environment,
    // etc.) — this is unknown, not a pass. Never default to true.
    return { pass: null, detail: "could not run in this build environment" };
  }
}

export function computeQuality(): QualityReport {
  const { entities } = loadAllData();
  const ontology = loadOntology();
  const ajv = buildAjv();
  const validators = compileEntityValidators(ajv);

  const schemaIssues = checkSchema(entities, validators);
  const schemaErrors = schemaIssues.filter((i) => i.severity === "error");

  let orphanCount = 0;
  let relationshipIntegrityErrors = 0;

  if (schemaErrors.length === 0) {
    const relIssues = checkRelationships(entities, ontology);
    orphanCount = relIssues.filter((i) => i.rule === "orphan_node" && i.severity === "error").length;
    relationshipIntegrityErrors += relIssues.filter((i) => i.rule !== "orphan_node" && i.severity === "error").length;
    relationshipIntegrityErrors += checkCircularRelationships(entities, ontology).filter((i) => i.severity === "error").length;
    relationshipIntegrityErrors += checkDuplicateIds(entities).filter((i) => i.severity === "error").length;
    relationshipIntegrityErrors += checkDuplicateSlugs(entities).filter((i) => i.severity === "error").length;
  }

  const today = new Date();
  const scores = entities.map((e) => scoreCitations(e as LoadedEntity, today).score);
  const avgCitation = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;

  const incidents = entities.filter((e) => e.entityType === "incident");
  const entityTypes = new Set(entities.map((e) => e.entityType));

  return {
    generated_at: new Date().toISOString(),
    canonical_objects: entities.length,
    real_incidents: incidents.length,
    entity_types: entityTypes.size,
    checks: {
      schema_validation: {
        pass: schemaErrors.length === 0,
        detail: schemaErrors.length === 0 ? "0 schema errors across all canonical objects" : `${schemaErrors.length} schema error(s)`,
      },
      zero_orphans: {
        pass: schemaErrors.length === 0 ? orphanCount === 0 : null,
        detail: schemaErrors.length === 0 ? `${orphanCount} orphan node(s)` : "not checked (schema errors present)",
      },
      relationship_integrity: {
        pass: schemaErrors.length === 0 ? relationshipIntegrityErrors === 0 : null,
        detail:
          schemaErrors.length === 0
            ? `${relationshipIntegrityErrors} relationship/reference error(s)`
            : "not checked (schema errors present)",
      },
      type_check: runNpmScript("typecheck"),
      editorial_audit: runNpmScript("editorial:audit"),
    },
    citation_completeness: {
      average: Math.round(avgCitation * 10) / 10,
      target: 80,
    },
  };
}
