import { buildGraph, outboundCount } from "./lib/graph.js";
import { scoreCitations } from "./lib/citation-score.js";
import { countBy, sortedEntries } from "./lib/format.js";
import { checkSchema } from "../../validators/src/rules/schema.js";
import { checkDuplicateIds, checkDuplicateSlugs } from "../../validators/src/rules/duplicate-ids.js";
import { checkRelationships } from "../../validators/src/rules/relationships.js";
import { checkCitations } from "../../validators/src/rules/citations.js";
import { checkCircularRelationships } from "../../validators/src/rules/circular.js";
import { buildAjv, compileEntityValidators } from "../../validators/src/load-schemas.js";
import { loadAllData } from "../../validators/src/load-data.js";

/**
 * Graph Health Report. Answers "is the graph structurally and qualitatively
 * sound" — the structural-integrity lens (contrast with
 * coverage-dashboard.ts, the topic-breadth lens). Reuses the actual
 * validator rules from /validators rather than re-implementing structural
 * checks, so this report can never silently disagree with `npm run
 * validate` about what counts as an error.
 */

function main(): void {
  const graph = buildGraph();
  const today = new Date();

  console.log(`# Graph Health Report`);
  console.log("");
  console.log(`Generated ${today.toISOString().slice(0, 10)} from ${graph.entities.length} object(s), ${[...graph.outgoing.values()].flat().length} edge(s).`);
  console.log("");

  // --- Structural validity, via the real validator rules ---
  const ajv = buildAjv();
  const validators = compileEntityValidators(ajv);
  const { entities } = loadAllData();
  const schemaIssues = checkSchema(entities, validators);
  const structuralIssues =
    schemaIssues.length === 0
      ? [
          ...checkDuplicateIds(entities),
          ...checkDuplicateSlugs(entities),
          ...checkRelationships(entities, graph.ontology),
          ...checkCitations(entities),
          ...checkCircularRelationships(entities, graph.ontology),
        ]
      : schemaIssues;
  const errorCount = structuralIssues.filter((i) => i.severity === "error").length;
  const warningCount = structuralIssues.filter((i) => i.severity === "warning").length;

  console.log(`## Structural validity`);
  console.log("");
  console.log(`- Errors: ${errorCount}`);
  console.log(`- Warnings: ${warningCount}`);
  console.log(errorCount === 0 ? "- \`npm run validate\` would pass." : "- \`npm run validate\` would FAIL — run it directly for details.");
  console.log("");

  // --- Zero-Orphan Invariant ---
  // A node with zero relationships is invisible in a knowledge graph: no
  // traversal, search, or view built on /data will ever reach it. This is
  // enforced here as its own explicit error-level rule, independent of and
  // in addition to /validators' own orphan_node check above, because it is
  // this report's job to make the invariant impossible to miss rather than
  // bury it as one line in a structural-issue count.
  const degrees = graph.entities.map((e) => {
    const id = e.data.id;
    const out = outboundCount(graph, id);
    const inn = graph.incoming.get(id)?.length ?? 0;
    return { entity: e, total: out + inn, out };
  });
  const orphans = degrees.filter((d) => d.total === 0);

  console.log(`## Zero-Orphan Invariant`);
  console.log("");
  if (orphans.length === 0) {
    console.log("- PASS — every object has at least one relationship.");
  } else {
    console.log(`- FAIL — ${orphans.length} orphan node(s) with zero relationships (ERROR):`);
    for (const d of orphans) {
      console.log(`  - ERROR: '${d.entity.data.id}' (${d.entity.data.title}) has zero relationships and is invisible in the graph.`);
    }
  }
  console.log("");

  // --- Connectivity fragility (near-orphans: exactly one relationship) ---
  console.log(`## Connectivity`);
  console.log("");
  const fragile = degrees.filter((d) => d.total === 1);
  console.log(`- Fragile nodes (exactly 1 relationship): ${fragile.length}${fragile.length > 0 ? ` — ${fragile.map((d) => d.entity.data.id).join(", ")}` : ""}`);

  const { soft_limit: softLimit, hard_limit: hardLimit } = graph.ontology.outbound_relationship_limits;
  const nearSoftLimit = degrees.filter((d) => d.out > softLimit * 0.8 && d.out <= softLimit);
  const overSoftLimit = degrees.filter((d) => d.out > softLimit);
  console.log(`- Nodes approaching the soft outbound limit (>${(softLimit * 0.8).toFixed(1)}, <=${softLimit}): ${nearSoftLimit.length}`);
  console.log(`- Nodes over the soft outbound limit (${softLimit}) or hard limit (${hardLimit}): ${overSoftLimit.length}${overSoftLimit.length > 0 ? ` — ${overSoftLimit.map((d) => `${d.entity.data.id} (${d.out})`).join(", ")}` : ""}`);
  console.log("");

  // --- Relationship verb balance ---
  console.log(`## Relationship verb usage`);
  console.log("");
  const allVerbs = graph.entities.flatMap((e) => (e.data.relationships ?? []).map((r) => r.type));
  const verbCounts = countBy(allVerbs.map((v) => ({ v })), (x) => x.v);
  const unusedVerbs = graph.ontology.relationship_types.map((r) => r.verb).filter((v) => !(verbCounts.get(v) ?? 0));
  for (const [verb, count] of sortedEntries(verbCounts)) console.log(`- ${verb}: ${count}`);
  console.log(unusedVerbs.length > 0 ? `- Unused ontology verbs: ${unusedVerbs.join(", ")}` : "- Every ontology verb is used at least once.");
  console.log("");

  // --- Confidence maturity ---
  console.log(`## Confidence maturity`);
  console.log("");
  const confidenceCounts = countBy(graph.entities, (e) => e.data.confidence as string | undefined);
  const total = graph.entities.length || 1;
  for (const [confidence, count] of sortedEntries(confidenceCounts)) {
    console.log(`- ${confidence}: ${count} (${((count / total) * 100).toFixed(0)}%)`);
  }
  const verifiedOrReviewed = (confidenceCounts.get("Verified") ?? 0) + (confidenceCounts.get("Reviewed") ?? 0);
  console.log(`- Verified+Reviewed share: ${((verifiedOrReviewed / total) * 100).toFixed(0)}%`);
  console.log("");

  // --- Citation health summary (aggregate; see citation-completeness.ts for per-object detail) ---
  console.log(`## Citation health (summary — run 'npm run editorial:citations' for per-object detail)`);
  console.log("");
  const citationScores = graph.entities.map((e) => scoreCitations(e, today).score);
  const avgCitationScore = citationScores.reduce((a, b) => a + b, 0) / (citationScores.length || 1);
  const weakCitations = citationScores.filter((s) => s < 70).length;
  console.log(`- Average citation completeness: ${avgCitationScore.toFixed(1)}/100`);
  console.log(`- Objects below 70/100: ${weakCitations} of ${citationScores.length}`);
  console.log("");

  // --- Composite health score ---
  const structuralScore = errorCount === 0 ? 100 : Math.max(0, 100 - errorCount * 10);
  const connectivityScore = Math.max(0, 100 - orphans.length * 25 - fragile.length * 5);
  const confidenceScore = (verifiedOrReviewed / total) * 100;
  const healthScore = structuralScore * 0.4 + connectivityScore * 0.2 + avgCitationScore * 0.25 + confidenceScore * 0.15;

  console.log(`## Composite health score`);
  console.log("");
  console.log(`**${healthScore.toFixed(1)} / 100**`);
  console.log("");
  console.log(`Weighted: structural validity 40% (${structuralScore.toFixed(0)}), connectivity 20% (${connectivityScore.toFixed(0)}), citation completeness 25% (${avgCitationScore.toFixed(0)}), confidence maturity 15% (${confidenceScore.toFixed(0)}).`);

  // The Zero-Orphan Invariant is a hard gate: this report exits non-zero if
  // it's violated, even if every other structural check passes.
  if (orphans.length > 0 || errorCount > 0) {
    console.log("");
    console.log(`✘ FAIL: ${orphans.length} orphan node(s), ${errorCount} structural error(s).`);
    process.exitCode = 1;
  }
}

main();
