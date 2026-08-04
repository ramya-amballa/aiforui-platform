import { writeFileSync } from "node:fs";
import { buildGraph, outboundCount } from "./lib/graph.js";
import { countBy, markdownTable, sortedEntries } from "./lib/format.js";

const SPARSE_AVG_DEGREE_THRESHOLD = 2;

/**
 * Coverage Metrics Dashboard. Answers "what governance concepts does the
 * dataset actually cover, and where are the gaps" — the breadth-of-content
 * lens (contrast with graph-health.ts, the structural-integrity lens).
 * Read-only: prints a report, optionally writes it to a file via --out.
 */

const ALL_HARM_TYPES = ["discrimination", "privacy_violation", "safety", "financial", "reputational", "misinformation", "security", "other"];

const WELL_KNOWN_FRAMEWORKS: { label: string; keywords: string[] }[] = [
  { label: "NIST AI RMF", keywords: ["NIST"] },
  { label: "EU AI Act", keywords: ["AI Act", "Artificial Intelligence Act"] },
  { label: "GDPR", keywords: ["GDPR", "General Data Protection Regulation"] },
  { label: "ISO/IEC 42001", keywords: ["ISO/IEC 42001", "ISO 42001"] },
  { label: "NYC Local Law 144", keywords: ["Local Law 144"] },
  { label: "BIPA", keywords: ["BIPA", "Biometric Information Privacy"] },
  { label: "FCRA", keywords: ["FCRA", "Fair Credit Reporting"] },
  { label: "FTC Act", keywords: ["FTC Act"] },
  { label: "EEOC", keywords: ["EEOC"] },
];

function main(): void {
  const graph = buildGraph();
  const lines: string[] = [];
  const log = (s = "") => lines.push(s);

  log(`# Coverage Metrics Dashboard`);
  log("");
  log(`Generated ${new Date().toISOString().slice(0, 10)} from ${graph.entities.length} object(s).`);
  log("");

  log(`## Objects per entity type`);
  log("");
  for (const [type, entities] of Object.entries(graph.byType)) {
    log(`- ${type}: ${entities.length}`);
  }
  log("");

  log(`## Coverage Matrix — connections per entity type`);
  log("");
  log(`How well-connected is each of the 6 entity types? A type is flagged **sparse** if its average degree (in + out relationships per object) is below ${SPARSE_AVG_DEGREE_THRESHOLD}, or it contains any orphan. Use this to see at a glance which entity types need more linking, not just more objects.`);
  log("");
  const matrixRows = Object.entries(graph.byType).map(([type, typeEntities]) => {
    const outboundTotal = typeEntities.reduce((sum, e) => sum + outboundCount(graph, e.data.id), 0);
    const inboundTotal = typeEntities.reduce((sum, e) => sum + (graph.incoming.get(e.data.id)?.length ?? 0), 0);
    const orphanCount = typeEntities.filter((e) => outboundCount(graph, e.data.id) + (graph.incoming.get(e.data.id)?.length ?? 0) === 0).length;
    const avgDegree = typeEntities.length > 0 ? (outboundTotal + inboundTotal) / typeEntities.length : 0;
    const sparse = typeEntities.length === 0 || avgDegree < SPARSE_AVG_DEGREE_THRESHOLD || orphanCount > 0;
    return [type, typeEntities.length, outboundTotal, inboundTotal, avgDegree.toFixed(2), orphanCount, sparse ? "⚠ SPARSE" : "✓ OK"];
  });
  log(markdownTable(["Entity Type", "Objects", "Outbound", "Inbound", "Avg Degree", "Orphans", "Status"], matrixRows));
  const sparseTypes = matrixRows.filter((r) => String(r[6]).includes("SPARSE")).map((r) => r[0]);
  log("");
  log(sparseTypes.length > 0 ? `**Gap:** sparsely-connected entity type(s): ${sparseTypes.join(", ")}.` : "All entity types are adequately connected.");
  log("");

  const incidents = graph.byType.incident;

  log(`## Incidents by harm type`);
  log("");
  const harmCounts = countBy(incidents, (i) => i.data.harm_types as string[] | undefined);
  for (const harmType of ALL_HARM_TYPES) {
    log(`- ${harmType}: ${harmCounts.get(harmType) ?? 0}`);
  }
  const uncoveredHarmTypes = ALL_HARM_TYPES.filter((h) => !(harmCounts.get(h) ?? 0));
  log("");
  log(uncoveredHarmTypes.length > 0 ? `**Gap:** no incidents cover: ${uncoveredHarmTypes.join(", ")}.` : "All harm types have at least one incident.");
  log("");

  log(`## Incidents by jurisdiction`);
  log("");
  const jurisdictionCounts = countBy(incidents, (i) => i.data.jurisdiction as string[] | undefined);
  for (const [jurisdiction, count] of sortedEntries(jurisdictionCounts)) log(`- ${jurisdiction}: ${count}`);
  log("");

  log(`## Incidents by AI system category`);
  log("");
  const categoryCounts = countBy(incidents, (i) => i.data.ai_system_category as string | undefined);
  for (const [category, count] of sortedEntries(categoryCounts)) log(`- ${category}: ${count}`);
  log("");

  log(`## Incidents by severity`);
  log("");
  const severityCounts = countBy(incidents, (i) => i.data.severity as string | undefined);
  for (const severity of ["critical", "high", "medium", "low"]) log(`- ${severity}: ${severityCounts.get(severity) ?? 0}`);
  log("");

  log(`## Framework Controls by framework`);
  log("");
  const frameworkCounts = countBy(graph.byType.control, (c) => c.data.framework_name as string | undefined);
  for (const [framework, count] of sortedEntries(frameworkCounts)) log(`- ${framework}: ${count} control(s)`);
  const missingFrameworks = WELL_KNOWN_FRAMEWORKS.filter(
    (wf) => ![...frameworkCounts.keys()].some((f) => wf.keywords.some((k) => f.includes(k))),
  );
  log("");
  log(missingFrameworks.length > 0 ? `**Gap:** no controls yet reference: ${missingFrameworks.map((f) => f.label).join(", ")}.` : "All well-known reference frameworks have at least one control.");
  log("");

  log(`## Confidence distribution (all entity types)`);
  log("");
  const confidenceCounts = countBy(graph.entities, (e) => e.data.confidence as string | undefined);
  for (const [confidence, count] of sortedEntries(confidenceCounts)) log(`- ${confidence}: ${count}`);
  log("");

  log(`## Status distribution`);
  log("");
  const statusCounts = countBy(graph.entities, (e) => e.data.status as string | undefined);
  for (const [status, count] of sortedEntries(statusCounts)) log(`- ${status}: ${count}`);
  log("");

  log(`## Relationship verb usage`);
  log("");
  const allVerbs = graph.entities.flatMap((e) => (e.data.relationships ?? []).map((r) => r.type));
  const verbCounts = countBy(allVerbs.map((v) => ({ v })), (x) => x.v);
  for (const verbType of graph.ontology.relationship_types.map((r) => r.verb)) {
    log(`- ${verbType}: ${verbCounts.get(verbType) ?? 0}`);
  }
  log("");

  log(`## Decisions with no incident grounding`);
  log("");
  const groundedDecisionIds = new Set(
    incidents.flatMap((i) => (i.data.relationships ?? []).filter((r) => r.target_type === "decision").map((r) => r.target_id)),
  );
  const ungroundedDecisions = graph.byType.decision.filter((d) => !groundedDecisionIds.has(d.data.id));
  if (ungroundedDecisions.length === 0) {
    log("Every decision is linked from at least one incident.");
  } else {
    for (const d of ungroundedDecisions) log(`- ${d.data.id} (${d.data.title})`);
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
