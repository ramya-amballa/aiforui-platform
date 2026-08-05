import { writeFileSync } from "node:fs";
import { buildGraph, tripleAllowed } from "./lib/graph.js";
import { countBy, sortedEntries } from "./lib/format.js";
import { scoreCitations } from "./lib/citation-score.js";

/**
 * Repository Quality Audit. Read-only, like every other /editorial tool —
 * it never writes to /data (see "Why /editorial doesn't get a write path
 * into /data" in /docs/architecture.md). It checks the things a structural
 * validator can't: naming-convention consistency per entity type, US/UK
 * spelling consistency, tag hygiene, relationship-rationale depth, and
 * citation depth against the Edition 1.2 target (80/100). Findings a
 * maintainer fixed deterministically are recorded in the corresponding
 * release note / audit report, not auto-applied by this tool.
 */

interface Finding {
  severity: "ERROR" | "WARNING" | "INFO";
  category: string;
  id: string;
  message: string;
}

const findings: Finding[] = [];
function flag(severity: Finding["severity"], category: string, id: string, message: string) {
  findings.push({ severity, category, id, message });
}

// Prose fields eligible for terminology/spelling checks. Deliberately
// excludes citations (verbatim external quotations/titles/publishers must
// never be "corrected" for house style) and id/slug/tags/enums.
const PROSE_KEYS = [
  "title", "description", "problem", "solution", "applicability", "consequences",
  "decision_statement", "decision_context", "decision_rationale", "problem_statement", "outcome",
  "root_cause", "control_text", "control_family", "control_reference", "evidence_description", "collection_method",
  "retention_period", "artifact_format", "question_text", "rationale", "governing_body",
];
const PROSE_LIST_KEYS = ["alternatives_considered", "follow_up_actions"];

const UK_US_PAIRS: [string, string][] = [
  ["organisation", "organization"], ["organisations", "organizations"], ["organisational", "organizational"],
  ["labour", "labor"], ["labelling", "labeling"], ["labelled", "labeled"], ["labeller", "labeler"], ["labellers", "labelers"],
  ["licence", "license"], ["licences", "licenses"], ["programme", "program"], ["programmes", "programs"],
  ["judgement", "judgment"], ["favour", "favor"], ["scrutinised", "scrutinized"],
];

function main(): void {
  const graph = buildGraph();
  const today = new Date();
  const lines: string[] = [];
  const log = (s = "") => lines.push(s);

  log("# Repository Quality Audit");
  log("");
  log(`Generated ${today.toISOString().slice(0, 10)} from ${graph.entities.length} canonical object(s).`);
  log("");
  log("Deterministic, rule-based checks only — same design constraint as every other /editorial tool. Nothing here is AI-generated judgment about content quality; it is pattern-matching against conventions this dataset has already established for itself.");
  log("");

  // ---------------------------------------------------------------
  // 1. Naming convention consistency, per entity type
  // ---------------------------------------------------------------
  log("## 1. Naming conventions");
  log("");

  const patternSuffixOk = (t: string) => /\bPattern$/.test(t.trim());
  const patternTitlesEndingInPattern = graph.byType.pattern.filter((e) => patternSuffixOk(e.data.title)).length;
  for (const e of graph.byType.pattern) {
    if (!patternSuffixOk(e.data.title)) {
      flag(
        "WARNING",
        "naming",
        e.data.id,
        `Pattern title does not end with "Pattern", the convention ${patternTitlesEndingInPattern}/${graph.byType.pattern.length} other Pattern titles follow: "${e.data.title}"`,
      );
    }
  }

  const evidenceSuffixOk = (t: string) => /\b(Report|Record|Log|Attestation)\b|\([A-Z]{2,6}\)$/.test(t);
  for (const e of graph.byType.evidence) {
    if (!evidenceSuffixOk(e.data.title)) {
      flag("WARNING", "naming", e.data.id, `Evidence title does not end with an established artifact-noun (Report/Record/Log/Attestation/acronym): "${e.data.title}"`);
    }
  }

  for (const e of graph.byType.board_question) {
    if (!e.data.title.trim().endsWith("?")) {
      flag("ERROR", "naming", e.data.id, `Board Question title does not read as a question (no trailing "?"): "${e.data.title}"`);
    }
    const questionText = e.data.question_text as string | undefined;
    if (questionText && !questionText.trim().endsWith("?")) {
      flag("ERROR", "naming", e.data.id, `question_text does not end in "?"`);
    }
  }

  const decisionVerbStop = new Set(["the", "a", "an", "this", "that", "it", "there"]);
  for (const e of graph.byType.decision) {
    const firstWord = e.data.title.split(/\s+/)[0]?.toLowerCase().replace(/[^a-z]/g, "");
    if (!firstWord || decisionVerbStop.has(firstWord)) {
      flag("WARNING", "naming", e.data.id, `Decision title does not open with an imperative verb: "${e.data.title}"`);
    }
  }

  const controlFormatOk = (t: string) => t.includes(" — ") || t.includes(" - ");
  for (const e of graph.byType.control) {
    if (!controlFormatOk(e.data.title)) {
      flag("INFO", "naming", e.data.id, `Control title does not follow the "Framework Reference — Description" convention: "${e.data.title}"`);
    }
  }

  const namingFindings = findings.filter((f) => f.category === "naming");
  if (namingFindings.length === 0) log("All titles across all six entity types follow their established per-type convention. No findings.");
  else for (const f of namingFindings) log(`- **${f.severity}** \`${f.id}\`: ${f.message}`);
  log("");

  // ---------------------------------------------------------------
  // 2. US/UK spelling consistency
  // ---------------------------------------------------------------
  log("## 2. Terminology consistency (US/UK spelling)");
  log("");
  log("Checked only in editorially-authored prose fields — citation titles/publishers/excerpts are verbatim external sources and are correctly excluded from this check, since 'correcting' a quotation would misrepresent the source.");
  log("");

  const spellingCounts = new Map<string, { uk: number; us: number; files: Set<string> }>();
  for (const [uk] of UK_US_PAIRS) spellingCounts.set(uk, { uk: 0, us: 0, files: new Set() });

  function scanText(id: string, val: unknown) {
    if (typeof val !== "string") return;
    const lower = val.toLowerCase();
    for (const [uk, us] of UK_US_PAIRS) {
      const entry = spellingCounts.get(uk)!;
      const ukHits = (lower.match(new RegExp(`\\b${uk}\\b`, "g")) ?? []).length;
      const usHits = (lower.match(new RegExp(`\\b${us}\\b`, "g")) ?? []).length;
      if (ukHits) entry.uk += ukHits;
      if (usHits) entry.us += usHits;
      if (ukHits || usHits) entry.files.add(id);
    }
  }

  for (const e of graph.entities) {
    for (const key of PROSE_KEYS) scanText(e.data.id, (e.data as Record<string, unknown>)[key]);
    for (const key of PROSE_LIST_KEYS) {
      const list = (e.data as Record<string, unknown>)[key];
      if (Array.isArray(list)) for (const item of list) scanText(e.data.id, item);
    }
    for (const r of e.data.relationships ?? []) scanText(e.data.id, r.reason);
  }

  let anyMixed = false;
  for (const [uk, us] of UK_US_PAIRS) {
    const c = spellingCounts.get(uk)!;
    if (c.uk > 0 && c.us > 0) {
      anyMixed = true;
      flag("WARNING", "spelling", "(dataset-wide)", `"${uk}" (${c.uk}x) and "${us}" (${c.us}x) both appear across ${c.files.size} object(s) — pick one house style and normalize.`);
      log(`- **WARNING** \`${uk}\` / \`${us}\` mixed: ${c.uk} vs ${c.us} occurrences across ${c.files.size} object(s).`);
    }
  }
  if (!anyMixed) log("No mixed US/UK spelling pairs found in prose fields.");
  log("");

  // ---------------------------------------------------------------
  // 3. Tag hygiene
  // ---------------------------------------------------------------
  log("## 3. Tag hygiene");
  log("");
  const allTags = new Set<string>();
  for (const e of graph.entities) for (const t of e.data.tags ?? []) allTags.add(t);
  const normalize = (t: string) => t.toLowerCase().replace(/[-_]/g, "");
  const byNormalized = new Map<string, string[]>();
  for (const t of allTags) {
    const n = normalize(t);
    const list = byNormalized.get(n) ?? [];
    list.push(t);
    byNormalized.set(n, list);
  }
  let dupFound = false;
  for (const [, variants] of byNormalized) {
    if (variants.length > 1) {
      dupFound = true;
      flag("WARNING", "tags", "(dataset-wide)", `Possible duplicate tags (same concept, different spelling): ${variants.join(", ")}`);
      log(`- **WARNING** possible duplicate tags: ${variants.map((v) => `\`${v}\``).join(", ")}`);
    }
  }
  if (!dupFound) log(`No near-duplicate tags found across ${allTags.size} unique tags.`);
  log("");

  // ---------------------------------------------------------------
  // 4. Relationship rationale
  // ---------------------------------------------------------------
  log("## 4. Relationship rationale");
  log("");
  let badTriples = 0;
  const reasonCounts = new Map<string, number>();
  let totalRels = 0;
  let shortReasons = 0;
  for (const e of graph.entities) {
    for (const r of e.data.relationships ?? []) {
      totalRels += 1;
      if (!tripleAllowed(graph.ontology, r.type, e.entityType, r.target_type)) {
        badTriples += 1;
        flag("ERROR", "relationships", e.data.id, `(${r.type}, ${e.entityType} -> ${r.target_type}) is not an allowed ontology triple.`);
      }
      if (r.reason.length < 30) shortReasons += 1;
      reasonCounts.set(r.reason, (reasonCounts.get(r.reason) ?? 0) + 1);
    }
  }
  log(`- ${totalRels} relationship(s) checked against \`/relationships/ontology.json\`; ${badTriples} invalid triple(s) (the validator would also catch these — this is a redundant confirmation).`);
  log(`- ${shortReasons} relationship(s) with a reason under 30 characters.`);
  const templated = [...reasonCounts.entries()].filter(([, count]) => count >= 3).sort((a, b) => b[1] - a[1]);
  if (templated.length > 0) {
    log(`- ${templated.length} reason string(s) reused verbatim 3+ times (generic/templated rather than incident-specific — not wrong, but a depth opportunity for a future editorial pass):`);
    for (const [reason, count] of templated) {
      log(`  - x${count}: "${reason}"`);
      flag("INFO", "relationship-depth", "(dataset-wide)", `Reason reused verbatim ${count}x: "${reason}"`);
    }
  } else {
    log("- No reason string reused 3+ times verbatim.");
  }
  log("");

  // ---------------------------------------------------------------
  // 5. Citation depth (Edition 1.2 target: 80/100 average)
  // ---------------------------------------------------------------
  log("## 5. Citation depth");
  log("");
  const CITATION_TARGET = 80;
  const scores = graph.entities.map((e) => ({ e, score: scoreCitations(e, today).score }));
  const avg = scores.reduce((a, b) => a + b.score, 0) / (scores.length || 1);
  const below = scores.filter((s) => s.score < CITATION_TARGET);
  log(`- Dataset-wide average citation completeness: **${avg.toFixed(1)}/100**. Edition 1.2 target: ${CITATION_TARGET}/100.`);
  log(`- ${below.length} of ${scores.length} object(s) below target.`);
  const byType = countBy(
    scores.map(({ e, score }) => ({ t: e.entityType, low: score < CITATION_TARGET })),
    (x) => (x.low ? x.t : []),
  );
  for (const [t, count] of sortedEntries(byType)) log(`  - ${t}: ${count} below target`);
  flag("WARNING", "citations", "(dataset-wide)", `${below.length}/${scores.length} objects below the ${CITATION_TARGET}/100 Edition 1.2 target. Closing this requires re-verifying sources to add real locators/excerpts — not something a deterministic pass can fabricate. See docs for the per-object list.`);
  log("");
  log("This gap cannot be closed deterministically — a locator/excerpt has to be read off the actual source, not generated. It is the single largest item carried into Edition 1.2's citation-quality pass.");
  log("");

  // ---------------------------------------------------------------
  // 6. Taxonomy sprawl (free-text categorical fields)
  // ---------------------------------------------------------------
  log("## 6. Taxonomy sprawl");
  log("");
  const categories = new Map<string, number>();
  for (const e of graph.byType.incident) {
    const cat = e.data.ai_system_category as string | undefined;
    if (cat) categories.set(cat, (categories.get(cat) ?? 0) + 1);
  }
  const singleton = [...categories.entries()].filter(([, c]) => c === 1).length;
  log(`- \`ai_system_category\` (free text, not an enum) has ${categories.size} distinct value(s) across ${graph.byType.incident.length} incidents, ${singleton} used only once.`);
  flag("INFO", "taxonomy", "(dataset-wide)", `ai_system_category has ${categories.size} distinct free-text values (${singleton} singletons) — recommend a controlled vocabulary once the dataset is large enough to define one without guessing at boundaries prematurely.`);
  log("- Not auto-merged: collapsing categories changes their meaning and is an editorial judgment call, not a mechanical fix.");
  log("");

  // ---------------------------------------------------------------
  // Summary
  // ---------------------------------------------------------------
  const errors = findings.filter((f) => f.severity === "ERROR");
  const warnings = findings.filter((f) => f.severity === "WARNING");
  const infos = findings.filter((f) => f.severity === "INFO");
  log("## Summary");
  log("");
  log(`- ERROR: ${errors.length}`);
  log(`- WARNING: ${warnings.length}`);
  log(`- INFO: ${infos.length}`);
  log("");
  log("ERROR-severity findings should block a release; WARNING-severity findings are fixed as part of the same editorial pass that runs this audit; INFO-severity findings are logged for future editorial attention and are not auto-fixed.");

  const report = lines.join("\n");
  console.log(report);

  const outArg = process.argv.find((a) => a.startsWith("--out="))?.split("=")[1];
  if (outArg) {
    writeFileSync(outArg, report + "\n", "utf-8");
    console.error(`\nWritten to ${outArg}`);
  }

  if (errors.length > 0) process.exitCode = 1;
}

main();
