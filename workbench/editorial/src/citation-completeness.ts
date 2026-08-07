import { buildGraph } from "./lib/graph.js";
import { scoreCitations } from "./lib/citation-score.js";

/**
 * Citation Completeness Checker. Advisory tool, not a validation gate:
 * /validators already enforces "must a citation exist" (see
 * /docs/citation-model.md). This tool asks a different, editorial-judgment
 * question — "given citations exist, how complete/robust are they" — and
 * reports per-object scores plus a dataset summary so maintainers can see
 * where citation quality is weakest. It never modifies data.
 */
function main(): void {
  const graph = buildGraph();
  const today = new Date();

  const results = graph.entities
    .map((entity) => ({ entity, ...scoreCitations(entity, today) }))
    .sort((a, b) => a.score - b.score);

  console.log(`Citation Completeness Report — ${results.length} object(s)\n`);

  const threshold = 70;
  const weak = results.filter((r) => r.score < threshold);

  for (const { entity, score, findings } of results) {
    if (findings.length === 0) continue;
    console.log(`${entity.data.id}  (${entity.data.title})  — score ${score}/100`);
    for (const finding of findings) console.log(`  - ${finding}`);
    console.log("");
  }

  const average = results.reduce((sum, r) => sum + r.score, 0) / (results.length || 1);
  console.log("---");
  console.log(`Average citation completeness: ${average.toFixed(1)}/100`);
  console.log(`Objects below ${threshold}/100: ${weak.length} of ${results.length}`);
  if (weak.length > 0) {
    console.log(`  ${weak.map((r) => r.entity.data.id).join(", ")}`);
  }
}

main();
