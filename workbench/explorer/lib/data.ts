import graphJson from "@/data/generated/graph.json";
import type { EntityType, GraphData, GraphNode, Confidence, ResolvedRelationship } from "./types";

export const graph = graphJson as unknown as GraphData;

export function nodesByType(type: EntityType): GraphNode[] {
  return graph.nodes.filter((n) => n.entity_type === type);
}

export function getNode(type: EntityType, slug: string): GraphNode | undefined {
  return graph.nodes.find((n) => n.entity_type === type && n.slug === slug);
}

export function getNodeById(id: string): GraphNode | undefined {
  return graph.nodes.find((n) => n.id === id);
}

export function relatedByVerb(node: GraphNode, verb: string, direction: "out" | "in" = "out"): ResolvedRelationship[] {
  const list = direction === "out" ? node.relationships_out : node.relationships_in;
  return list.filter((r) => r.type === verb);
}

export function allTags(): string[] {
  const set = new Set<string>();
  for (const n of graph.nodes) for (const t of n.tags ?? []) set.add(t);
  return [...set].sort();
}

export function allJurisdictions(): string[] {
  const set = new Set<string>();
  for (const n of graph.nodes) for (const j of n.jurisdiction ?? []) set.add(j);
  return [...set].sort();
}

export function allFrameworkNames(): string[] {
  const set = new Set<string>();
  for (const n of graph.nodes) if (n.entity_type === "control" && n.framework_name) set.add(n.framework_name);
  return [...set].sort();
}

export const CONFIDENCE_RANK: Record<Confidence, number> = {
  Verified: 0,
  Reviewed: 1,
  Draft: 2,
  Community: 3,
  Archived: 4,
};

export function getFramework(slug: string) {
  return graph.frameworks.find((f) => f.slug === slug);
}

export function frameworkDetail(slug: string) {
  const framework = getFramework(slug);
  if (!framework) return undefined;

  const controls = framework.control_ids.map((id) => getNodeById(id)).filter((n): n is GraphNode => Boolean(n));
  const controlIdSet = new Set(controls.map((c) => c.id));

  const decisionsAndPatterns = new Map<string, GraphNode>();
  const directIncidents = new Map<string, GraphNode>();
  const evidence = new Map<string, GraphNode>();
  const boardQuestions = new Map<string, GraphNode>();

  for (const control of controls) {
    for (const r of control.relationships_in) {
      if (r.type === "SATISFIES_CONTROL") {
        const n = getNodeById(r.other_id);
        if (n) decisionsAndPatterns.set(n.id, n);
      }
      if (r.type === "MITIGATED_BY" && r.other_type === "incident") {
        const n = getNodeById(r.other_id);
        if (n) directIncidents.set(n.id, n);
      }
    }
    for (const r of control.relationships_out) {
      if (r.type === "REQUIRES_EVIDENCE") {
        const n = getNodeById(r.other_id);
        if (n) evidence.set(n.id, n);
      }
      if (r.type === "RAISES_BOARD_QUESTION") {
        const n = getNodeById(r.other_id);
        if (n) boardQuestions.set(n.id, n);
      }
    }
  }

  const decisionIds = new Set([...decisionsAndPatterns.values()].filter((n) => n.entity_type === "decision").map((n) => n.id));
  const indirectIncidents = graph.nodes.filter(
    (n) => n.entity_type === "incident" && n.relationships_out.some((r) => r.type === "MITIGATED_BY" && decisionIds.has(r.other_id)),
  );
  for (const inc of indirectIncidents) directIncidents.set(inc.id, inc);

  for (const decisionOrPattern of decisionsAndPatterns.values()) {
    for (const r of decisionOrPattern.relationships_out) {
      if (r.type === "RAISES_BOARD_QUESTION") {
        const n = getNodeById(r.other_id);
        if (n) boardQuestions.set(n.id, n);
      }
    }
  }

  return {
    framework,
    controls,
    decisions: [...decisionsAndPatterns.values()].filter((n) => n.entity_type === "decision"),
    patterns: [...decisionsAndPatterns.values()].filter((n) => n.entity_type === "pattern"),
    incidents: [...directIncidents.values()],
    evidence: [...evidence.values()],
    boardQuestions: [...boardQuestions.values()],
    controlIdSet,
  };
}

export function riskSummaryForDecision(node: GraphNode) {
  const incidents = relatedByVerb(node, "MITIGATED_BY", "in")
    .filter((r) => r.other_type === "incident")
    .map((r) => getNodeById(r.other_id))
    .filter((n): n is GraphNode => Boolean(n));

  const harmTypeCounts = new Map<string, number>();
  const severityCounts = new Map<string, number>();
  const jurisdictions = new Set<string>();
  for (const inc of incidents) {
    for (const h of inc.harm_types ?? []) harmTypeCounts.set(h, (harmTypeCounts.get(h) ?? 0) + 1);
    if (inc.severity) severityCounts.set(inc.severity, (severityCounts.get(inc.severity) ?? 0) + 1);
    for (const j of inc.jurisdiction ?? []) jurisdictions.add(j);
  }

  const controls = relatedByVerb(node, "SATISFIES_CONTROL", "out")
    .map((r) => getNodeById(r.other_id))
    .filter((n): n is GraphNode => Boolean(n));
  const frameworks = new Set(controls.map((c) => c.framework_name).filter((v): v is string => Boolean(v)));

  return {
    incidentCount: incidents.length,
    harmTypeCounts: [...harmTypeCounts.entries()].sort((a, b) => b[1] - a[1]),
    severityCounts: [...severityCounts.entries()].sort((a, b) => b[1] - a[1]),
    jurisdictions: [...jurisdictions].sort(),
    frameworks: [...frameworks].sort(),
  };
}
