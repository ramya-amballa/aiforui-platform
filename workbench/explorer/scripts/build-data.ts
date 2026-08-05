// Derived build step: reads the canonical dataset in /workbench/data and the
// ontology in /workbench/relationships/ontology.json and emits typed JSON
// consumed by the Explorer at build time. This directory is never a second
// source of truth — everything here is regenerated from /data on every build
// (see package.json "predev"/"prebuild"). Do not hand-edit generated output.
import { readFileSync, readdirSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type {
  EntityType,
  RawEntity,
  GraphNode,
  ResolvedRelationship,
  FrameworkGroup,
  SearchDocument,
  GraphData,
} from "../lib/types.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const WORKBENCH_ROOT = join(__dirname, "..", "..");
const DATA_ROOT = join(WORKBENCH_ROOT, "data");
const ONTOLOGY_PATH = join(WORKBENCH_ROOT, "relationships", "ontology.json");
const OUT_DIR = join(__dirname, "..", "data", "generated");

const ENTITY_DIRS: Record<EntityType, string> = {
  decision: "decisions",
  incident: "incidents",
  pattern: "patterns",
  control: "controls",
  evidence: "evidence",
  board_question: "board_questions",
};

const WELL_KNOWN_FRAMEWORKS: { slug: string; label: string; keywords: string[] }[] = [
  { slug: "nist-ai-rmf", label: "NIST AI Risk Management Framework", keywords: ["NIST"] },
  { slug: "eu-ai-act", label: "EU Artificial Intelligence Act", keywords: ["AI Act", "Artificial Intelligence Act"] },
  { slug: "gdpr", label: "General Data Protection Regulation (GDPR)", keywords: ["GDPR", "General Data Protection Regulation"] },
  { slug: "iso-42001", label: "ISO/IEC 42001", keywords: ["ISO/IEC 42001", "ISO 42001"] },
  { slug: "nyc-ll144", label: "NYC Local Law 144", keywords: ["Local Law 144"] },
  { slug: "bipa", label: "Illinois Biometric Information Privacy Act (BIPA)", keywords: ["BIPA", "Biometric Information Privacy"] },
  { slug: "fcra", label: "Fair Credit Reporting Act (FCRA)", keywords: ["FCRA", "Fair Credit Reporting"] },
  { slug: "ftc-act", label: "FTC Act Section 5", keywords: ["FTC Act"] },
  { slug: "eeoc", label: "EEOC Title VII AI Guidance", keywords: ["EEOC"] },
  { slug: "eu-platform-work-directive", label: "EU Platform Work Directive", keywords: ["Platform Work Directive", "2024/2831"] },
  { slug: "ilo-declaration", label: "ILO Declaration on Fundamental Principles and Rights at Work", keywords: ["ILO"] },
  { slug: "sr-11-7", label: "SR 11-7 Model Risk Management", keywords: ["SR 11-7"] },
  { slug: "aba-model-rules", label: "ABA Model Rules of Professional Conduct", keywords: ["ABA Model Rules"] },
];

function slugifyFramework(name: string): string {
  return name
    .toLowerCase()
    .replace(/[()]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")
    .slice(0, 60);
}

function classifyFramework(frameworkName: string): { slug: string; label: string } {
  const match = WELL_KNOWN_FRAMEWORKS.find((wf) => wf.keywords.some((k) => frameworkName.includes(k)));
  if (match) return { slug: match.slug, label: match.label };
  return { slug: slugifyFramework(frameworkName), label: frameworkName };
}

function loadEntities(): { type: EntityType; raw: RawEntity }[] {
  const all: { type: EntityType; raw: RawEntity }[] = [];
  for (const [type, dir] of Object.entries(ENTITY_DIRS) as [EntityType, string][]) {
    const full = join(DATA_ROOT, dir);
    const files = readdirSync(full).filter((f) => f.endsWith(".json"));
    for (const file of files) {
      const raw = JSON.parse(readFileSync(join(full, file), "utf-8")) as RawEntity;
      all.push({ type, raw });
    }
  }
  return all;
}

function main(): void {
  const entities = loadEntities();
  const ontology = JSON.parse(readFileSync(ONTOLOGY_PATH, "utf-8"));

  const byId = new Map<string, { type: EntityType; raw: RawEntity }>();
  for (const e of entities) byId.set(e.raw.id, e);

  const inboundByTarget = new Map<string, ResolvedRelationship[]>();

  const nodes: GraphNode[] = entities.map(({ type, raw }) => {
    const relationships_out: ResolvedRelationship[] = (raw.relationships ?? []).map((rel) => {
      const target = byId.get(rel.target_id);
      const resolved: ResolvedRelationship = {
        type: rel.type,
        direction: "out",
        reason: rel.reason,
        confidence: rel.confidence,
        citation_ids: rel.citation_ids,
        other_id: rel.target_id,
        other_type: rel.target_type,
        other_slug: target?.raw.slug ?? rel.target_id,
        other_title: target?.raw.title ?? rel.target_id,
      };
      const inboundEntry: ResolvedRelationship = {
        type: rel.type,
        direction: "in",
        reason: rel.reason,
        confidence: rel.confidence,
        citation_ids: rel.citation_ids,
        other_id: raw.id,
        other_type: type,
        other_slug: raw.slug,
        other_title: raw.title,
      };
      const list = inboundByTarget.get(rel.target_id) ?? [];
      list.push(inboundEntry);
      inboundByTarget.set(rel.target_id, list);
      return resolved;
    });

    return {
      ...raw,
      entity_type: type,
      relationships_out,
      relationships_in: [],
      related_frameworks: [],
    };
  });

  for (const node of nodes) {
    node.relationships_in = inboundByTarget.get(node.id) ?? [];
  }

  for (const node of nodes) {
    if (node.entity_type === "control") {
      node.related_frameworks = node.framework_name ? [node.framework_name] : [];
      if (node.framework_name) node.framework_slug = classifyFramework(node.framework_name).slug;
      continue;
    }
    const linkedControlIds = new Set<string>();
    for (const r of [...node.relationships_out, ...node.relationships_in]) {
      if (r.other_type === "control") linkedControlIds.add(r.other_id);
    }
    const names = [...linkedControlIds]
      .map((id) => byId.get(id)?.raw.framework_name)
      .filter((v): v is string => Boolean(v));
    node.related_frameworks = [...new Set(names)].sort();
  }

  // Framework grouping, derived from control.framework_name
  const frameworkMap = new Map<string, FrameworkGroup>();
  for (const wf of WELL_KNOWN_FRAMEWORKS) {
    frameworkMap.set(wf.slug, { slug: wf.slug, label: wf.label, control_ids: [], status: "gap" });
  }
  for (const node of nodes) {
    if (node.entity_type !== "control" || !node.framework_name) continue;
    const { slug, label } = classifyFramework(node.framework_name);
    const existing = frameworkMap.get(slug) ?? { slug, label, control_ids: [], status: "gap" };
    existing.control_ids.push(node.id);
    existing.status = "covered";
    frameworkMap.set(slug, existing);
  }
  const frameworks = [...frameworkMap.values()].sort((a, b) => b.control_ids.length - a.control_ids.length || a.label.localeCompare(b.label));

  // Search documents
  const search_documents: SearchDocument[] = nodes.map((node) => {
    const extraParts = [
      node.decision_statement,
      node.problem,
      node.solution,
      node.control_text,
      node.evidence_description,
      node.question_text,
      node.root_cause,
      node.governing_body,
      ...(node.organizations_involved ?? []),
    ].filter(Boolean);
    return {
      id: node.id,
      entity_type: node.entity_type,
      slug: node.slug,
      title: node.title,
      description: node.description,
      tags: node.tags ?? [],
      jurisdiction: node.jurisdiction ?? [],
      frameworks: node.related_frameworks,
      status: node.status,
      confidence: node.confidence,
      extra: extraParts.join(" • "),
    };
  });

  const counts = Object.fromEntries(
    (Object.keys(ENTITY_DIRS) as EntityType[]).map((t) => [t, nodes.filter((n) => n.entity_type === t).length]),
  ) as Record<EntityType, number>;

  const graph: GraphData = {
    generated_at: new Date().toISOString(),
    counts,
    nodes: nodes.sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true })),
    frameworks,
    search_documents,
    relationship_verbs: ontology.relationship_types.map((r: { verb: string; description: string }) => ({
      verb: r.verb,
      description: r.description,
    })),
  };

  mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(join(OUT_DIR, "graph.json"), JSON.stringify(graph, null, 2));
  console.log(`Wrote ${nodes.length} nodes, ${frameworks.length} framework groups, ${search_documents.length} search documents to ${OUT_DIR}/graph.json`);
}

main();
