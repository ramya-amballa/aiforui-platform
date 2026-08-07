import type { GraphNode, ResolvedRelationship } from "./types";
import { ENTITY_LABEL } from "./types";

function relLine(r: ResolvedRelationship): string {
  const dir = r.direction === "out" ? "→" : "←";
  return `- ${dir} **${r.type}** ${r.other_id} — ${r.other_title}\n  - Reason: ${r.reason}${r.confidence ? `\n  - Confidence: ${r.confidence}` : ""}`;
}

export function nodeToMarkdown(node: GraphNode): string {
  const lines: string[] = [];
  lines.push(`# ${node.id} — ${node.title}`);
  lines.push("");
  lines.push(`*${ENTITY_LABEL[node.entity_type]} · Status: ${node.status} · Confidence: ${node.confidence} · Version ${node.version}*`);
  lines.push("");
  lines.push("## Overview");
  lines.push("");
  lines.push(node.description);
  lines.push("");

  const typeFields: [string, string | undefined][] = [
    ["Decision statement", node.decision_statement],
    ["Decision type", node.decision_type],
    ["Governing body", node.governing_body],
    ["Decision context", node.decision_context],
    ["Problem statement", node.problem_statement],
    ["Decision rationale", node.decision_rationale],
    ["Outcome", node.outcome],
    ["Occurred date", node.occurred_date],
    ["AI system category", node.ai_system_category],
    ["Severity", node.severity],
    ["Root cause", node.root_cause],
    ["Problem", node.problem],
    ["Solution", node.solution],
    ["Applicability", node.applicability],
    ["Consequences", node.consequences],
    ["Maturity", node.maturity],
    ["Framework", node.framework_name],
    ["Control reference", node.control_reference],
    ["Control text", node.control_text],
    ["Control family", node.control_family],
    ["Evidence description", node.evidence_description],
    ["Collection method", node.collection_method],
    ["Retention period", node.retention_period],
    ["Artifact format", node.artifact_format],
    ["Question", node.question_text],
    ["Rationale", node.rationale],
  ];
  const presentFields = typeFields.filter(([, v]) => Boolean(v));
  if (presentFields.length) {
    lines.push("## Details");
    lines.push("");
    for (const [label, value] of presentFields) lines.push(`**${label}:** ${value}`);
    lines.push("");
  }

  const listFields: [string, string[] | undefined][] = [
    ["Jurisdiction", node.jurisdiction],
    ["Organizations involved", node.organizations_involved],
    ["Harm types", node.harm_types],
    ["Frameworks referenced", node.frameworks_referenced],
    ["Alternatives considered", node.alternatives_considered],
    ["Audience", node.audience],
    ["Follow-up actions", node.follow_up_actions],
    ["Tags", node.tags],
  ];
  const presentLists = listFields.filter(([, v]) => v && v.length > 0);
  if (presentLists.length) {
    lines.push("## Attributes");
    lines.push("");
    for (const [label, values] of presentLists) lines.push(`- **${label}:** ${values!.join(", ")}`);
    lines.push("");
  }

  const allRels = [...node.relationships_out, ...node.relationships_in];
  if (allRels.length) {
    lines.push("## Relationships");
    lines.push("");
    for (const r of allRels) lines.push(relLine(r));
    lines.push("");
  }

  if (node.citations?.length) {
    lines.push("## Citations");
    lines.push("");
    for (const c of node.citations) {
      lines.push(`- ${c.title} — ${c.publisher}${c.publication_date ? ` (${c.publication_date})` : ""}${c.url ? ` — ${c.url}` : ""}`);
      if (c.locator) lines.push(`  - Locator: ${c.locator}`);
      if (c.excerpt) lines.push(`  - Excerpt: "${c.excerpt}"`);
    }
    lines.push("");
  }

  if (node.history?.length) {
    lines.push("## History");
    lines.push("");
    for (const h of node.history) {
      lines.push(`- ${h.date} — ${h.event} (v${h.version}) by ${h.by}${h.note ? ` — ${h.note}` : ""}`);
    }
    lines.push("");
  }

  lines.push("---");
  lines.push(`Source: AI Governance Workbench · ${node.id} · Generated ${new Date().toISOString().slice(0, 10)}`);
  lines.push("");

  return lines.join("\n");
}

export function downloadMarkdown(node: GraphNode): void {
  const md = nodeToMarkdown(node);
  const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${node.id}-${node.slug}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
