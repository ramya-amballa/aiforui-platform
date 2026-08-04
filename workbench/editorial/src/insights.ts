import { writeFileSync } from "node:fs";
import { buildGraph } from "./lib/graph.js";
import { countBy, sortedEntries } from "./lib/format.js";

/**
 * Editorial Analytics. The graph explaining itself: every report here is
 * computed purely from canonical /data — no generative step, no opinion
 * layered on top. This is a reporting tool, not a platform feature: no UI,
 * no visualization, no export engine, consistent with the Phase 2
 * infrastructure freeze. Read-only; prints a report, optionally to a file
 * via --out.
 */

function incomingFrom(graph: ReturnType<typeof buildGraph>, targetId: string, verb: string, sourceType?: string) {
  return (graph.incoming.get(targetId) ?? []).filter((e) => {
    if (e.relationship.type !== verb) return false;
    if (!sourceType) return true;
    return graph.byId.get(e.sourceId)?.entityType === sourceType;
  });
}

function main(): void {
  const graph = buildGraph();
  const lines: string[] = [];
  const log = (s = "") => lines.push(s);

  log(`# Editorial Analytics`);
  log("");
  log(`Generated ${new Date().toISOString().slice(0, 10)} from ${graph.entities.length} canonical object(s). Computed entirely from /data — no generated commentary.`);
  log("");

  // --- Most frequently invoked Governance Decisions ---
  log(`## Most frequently invoked Governance Decisions`);
  log("");
  log(`Ranked by number of distinct incidents that cite the decision (an incident -MITIGATED_BY-> decision edge).`);
  log("");
  const decisionIncidentCounts = graph.byType.decision
    .map((d) => ({ d, count: incomingFrom(graph, d.data.id, "MITIGATED_BY", "incident").length }))
    .sort((a, b) => b.count - a.count || a.d.data.id.localeCompare(b.d.data.id));
  for (const { d, count } of decisionIncidentCounts) {
    log(`- ${d.data.id} (${d.data.title}): ${count} incident(s)`);
  }
  log("");

  // --- Pattern reuse frequency ---
  log(`## Design Pattern reuse frequency`);
  log("");
  log(`Ranked by number of distinct Decisions/Controls that implement the pattern (an -IMPLEMENTED_BY-> edge). A pattern reused by more than one decision indicates a governance concept the dataset has recognised as recurring, not just a one-off response.`);
  log("");
  const patternReuse = graph.byType.pattern
    .map((p) => ({ p, count: incomingFrom(graph, p.data.id, "IMPLEMENTED_BY").length }))
    .sort((a, b) => b.count - a.count || a.p.data.id.localeCompare(b.p.data.id));
  for (const { p, count } of patternReuse) {
    log(`- ${p.data.id} (${p.data.title}): reused by ${count} object(s)`);
  }
  const reusedPatterns = patternReuse.filter((r) => r.count > 1);
  log("");
  log(reusedPatterns.length > 0
    ? `${reusedPatterns.length} pattern(s) are reused by more than one decision: ${reusedPatterns.map((r) => r.p.data.id).join(", ")}.`
    : "No pattern is yet reused by more than one decision.");
  log("");

  // --- Highest-confidence Decisions ---
  log(`## Highest-confidence Governance Decisions`);
  log("");
  const verifiedDecisions = graph.byType.decision.filter((d) => d.data.confidence === "Verified");
  const reviewedDecisions = graph.byType.decision.filter((d) => d.data.confidence === "Reviewed");
  log(`- Verified: ${verifiedDecisions.length} — ${verifiedDecisions.map((d) => d.data.id).join(", ") || "(none)"}`);
  log(`- Reviewed: ${reviewedDecisions.length} — ${reviewedDecisions.map((d) => d.data.id).join(", ") || "(none)"}`);
  log("");
  log(`Note: most Decisions in this dataset are illustrative reference objects (\`Community\` confidence) modelling a plausible response to a real incident, not documented decisions of a real organisation — see /docs/confidence-model.md. A Decision reaching \`Verified\` requires independent, second-party review, which has not yet happened for any object in this dataset.`);
  log("");

  // --- Weakly-covered governance areas ---
  log(`## Weakly-covered governance areas`);
  log("");
  const incidents = graph.byType.incident;
  const harmCounts = countBy(incidents, (i) => i.data.harm_types as string[] | undefined);
  const jurisdictionCounts = countBy(incidents, (i) => i.data.jurisdiction as string[] | undefined);
  const categoryCounts = countBy(incidents, (i) => i.data.ai_system_category as string | undefined);
  const weakHarmTypes = sortedEntries(harmCounts).filter(([, c]) => c <= 2);
  const weakJurisdictions = sortedEntries(jurisdictionCounts).filter(([, c]) => c === 1);
  const weakCategories = sortedEntries(categoryCounts).filter(([, c]) => c === 1);
  log(`- Harm types with <=2 incidents: ${weakHarmTypes.map(([k, c]) => `${k} (${c})`).join(", ") || "none"}`);
  log(`- Jurisdictions with exactly 1 incident: ${weakJurisdictions.map(([k]) => k).join(", ") || "none"}`);
  log(`- AI system categories with exactly 1 incident: ${weakCategories.map(([k]) => k).join(", ") || "none"}`);
  log("");

  // --- Emerging regulatory themes (tag frequency) ---
  log(`## Emerging regulatory/topical themes`);
  log("");
  log(`Top tags by frequency across all canonical objects (deterministic count, not inferred).`);
  log("");
  const tagCounts = countBy(graph.entities, (e) => e.data.tags as string[] | undefined);
  for (const [tag, count] of sortedEntries(tagCounts).slice(0, 15)) log(`- ${tag}: ${count}`);
  log("");

  // --- Cross-framework overlap analysis ---
  log(`## Cross-framework overlap`);
  log("");
  log(`Evidence types required by controls from more than one distinct framework — where independent frameworks converge on the same observable artifact.`);
  log("");
  const evidenceFrameworks = new Map<string, Set<string>>();
  for (const control of graph.byType.control) {
    const frameworkName = String(control.data.framework_name ?? "");
    for (const edge of graph.outgoing.get(control.data.id) ?? []) {
      if (edge.relationship.type !== "REQUIRES_EVIDENCE") continue;
      const set = evidenceFrameworks.get(edge.targetId) ?? new Set<string>();
      set.add(frameworkName);
      evidenceFrameworks.set(edge.targetId, set);
    }
  }
  const overlaps = [...evidenceFrameworks.entries()].filter(([, frameworks]) => frameworks.size > 1);
  if (overlaps.length === 0) {
    log("No evidence type is yet required by controls from more than one framework.");
  } else {
    for (const [evidenceId, frameworks] of overlaps) {
      const evidence = graph.byId.get(evidenceId);
      log(`- ${evidenceId} (${evidence?.data.title}) satisfies controls from: ${[...frameworks].join("; ")}`);
    }
  }
  log("");

  // --- Incident clustering ---
  log(`## Incident clusters (grouped by shared Governance Decision)`);
  log("");
  const clusters = decisionIncidentCounts.filter((c) => c.count > 1);
  if (clusters.length === 0) {
    log("No decision is yet shared by more than one incident.");
  } else {
    for (const { d, count } of clusters) {
      const memberIds = incomingFrom(graph, d.data.id, "MITIGATED_BY", "incident").map((e) => e.sourceId);
      log(`- **${d.data.id}** (${d.data.title}) — ${count} incidents: ${memberIds.join(", ")}`);
    }
  }
  log("");

  const report = lines.join("\n");
  console.log(report);

  const outArg = process.argv.find((a) => a.startsWith("--out="))?.split("=")[1];
  if (outArg) {
    writeFileSync(outArg, report + "\n", "utf-8");
    console.error(`\nWritten to ${outArg}`);
  }
}

main();
