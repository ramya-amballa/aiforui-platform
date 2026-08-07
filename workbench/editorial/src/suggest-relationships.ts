import { buildGraph, edgeExists, jaccard, outboundCount, sharedItems, tripleAllowed, title, type LoadedEntity } from "./lib/graph.js";

/**
 * Relationship Suggestion Engine. Deliberately rule-based, not generative:
 * every suggestion traces to one of the named heuristics below, with a
 * human-readable rationale. It never writes to /data — it only prints
 * candidates for a maintainer to evaluate and add by hand (with their own
 * `reason`), per the project principle that these tools improve editorial
 * quality/consistency without automating editorial judgment.
 */

interface Suggestion {
  sourceId: string;
  verb: string;
  targetId: string;
  score: number;
  reason: string;
}

const HARM_TYPE_CONTROL_KEYWORDS: Record<string, string[]> = {
  discrimination: ["fairness", "bias"],
  privacy_violation: ["privacy"],
  safety: ["safety"],
  security: ["security"],
  misinformation: ["misinformation", "transparency"],
  financial: ["financial", "credit"],
  reputational: ["transparency", "accountability"],
  other: [],
};

function tagSimilarity(a: LoadedEntity, b: LoadedEntity): { score: number; reason: string } | null {
  const shared = sharedItems(a.data.tags ?? [], b.data.tags ?? []);
  const score = jaccard(a.data.tags ?? [], b.data.tags ?? []);
  if (shared.length === 0 || score < 0.15) return null;
  return { score, reason: `shares tag(s): ${shared.join(", ")}` };
}

function suggestForEntity(
  graph: ReturnType<typeof buildGraph>,
  entity: LoadedEntity,
): Suggestion[] {
  const suggestions: Suggestion[] = [];
  const sourceId = entity.data.id;
  const currentOutbound = outboundCount(graph, sourceId);
  const { soft_limit: softLimit } = graph.ontology.outbound_relationship_limits;

  const push = (verb: string, targetId: string, score: number, reason: string) => {
    if (targetId === sourceId) return;
    if (edgeExists(graph, sourceId, targetId)) return;
    const target = graph.byId.get(targetId);
    if (!target) return;
    if (!tripleAllowed(graph.ontology, verb, entity.entityType, target.entityType)) return;
    suggestions.push({ sourceId, verb, targetId, score, reason });
  };

  // Rule 1: tag overlap -> RELATED_TO, against every other entity.
  for (const other of graph.entities) {
    if (other.data.id === sourceId) continue;
    const sim = tagSimilarity(entity, other);
    if (sim) push("RELATED_TO", other.data.id, sim.score, `Tag overlap: ${sim.reason}.`);
  }

  // Rule 2: incident harm_type -> control tag keyword match (MITIGATED_BY).
  if (entity.entityType === "incident") {
    const harmTypes = (entity.data.harm_types as string[] | undefined) ?? [];
    for (const harmType of harmTypes) {
      const keywords = HARM_TYPE_CONTROL_KEYWORDS[harmType] ?? [];
      if (keywords.length === 0) continue;
      for (const control of graph.byType.control) {
        const tags = (control.data.tags ?? []).map((t) => t.toLowerCase());
        const matched = keywords.find((k) => tags.includes(k));
        if (matched) {
          push("MITIGATED_BY", control.data.id, 0.6, `Incident harm_type '${harmType}' matches control tag '${matched}'.`);
        }
      }
    }
  }

  // Rule 3: shared ai_system_category -> reuse edges from sibling incidents.
  if (entity.entityType === "incident" && entity.data.ai_system_category) {
    const category = entity.data.ai_system_category;
    const siblings = graph.byType.incident.filter(
      (i) => i.data.id !== sourceId && i.data.ai_system_category === category,
    );
    for (const sibling of siblings) {
      for (const edge of graph.outgoing.get(sibling.data.id) ?? []) {
        if (edge.relationship.type === "RELATED_TO") continue; // too generic to propagate
        push(
          edge.relationship.type,
          edge.targetId,
          0.5,
          `Sibling incident '${sibling.data.id}' (same ai_system_category '${category}') already has this edge.`,
        );
      }
    }
  }

  // Rule 4: jurisdiction -> framework control whose framework_name mentions it.
  const jurisdiction = (entity.data.jurisdiction as string[] | undefined) ?? [];
  if (entity.entityType === "incident" && jurisdiction.length > 0) {
    const jurisdictionHints: Record<string, string[]> = {
      EU: ["EU AI Act", "GDPR"],
      UK: ["UK"],
      US: ["NIST", "FTC", "EEOC", "FCRA"],
      "US-NY": ["NYC", "New York"],
    };
    for (const j of jurisdiction) {
      const hints = jurisdictionHints[j] ?? [];
      for (const control of graph.byType.control) {
        const frameworkName = String(control.data.framework_name ?? "");
        if (hints.some((h) => frameworkName.includes(h))) {
          push("MITIGATED_BY", control.data.id, 0.4, `Incident jurisdiction '${j}' matches control framework '${frameworkName}'.`);
        }
      }
    }
  }

  // Rule 5: orphan/near-orphan prevention — most similar entity overall.
  const totalDegree = currentOutbound + (graph.incoming.get(sourceId)?.length ?? 0);
  if (totalDegree === 0) {
    let best: { id: string; score: number } | null = null;
    for (const other of graph.entities) {
      if (other.data.id === sourceId) continue;
      const score = jaccard(entity.data.tags ?? [], other.data.tags ?? []);
      if (!best || score > best.score) best = { id: other.data.id, score };
    }
    if (best && best.score > 0) {
      push("RELATED_TO", best.id, best.score, "This object has zero relationships (orphan risk) — most tag-similar object as a starting point.");
    }
  }

  // Dedupe (verb, target) pairs keeping the highest score, then sort.
  const byKey = new Map<string, Suggestion>();
  for (const s of suggestions) {
    const key = `${s.verb}::${s.targetId}`;
    const existing = byKey.get(key);
    if (!existing || s.score > existing.score) byKey.set(key, s);
  }
  const deduped = [...byKey.values()].sort((a, b) => b.score - a.score);

  if (currentOutbound + deduped.length > softLimit) {
    // Not a hard stop — just a note appended by the caller — but trim
    // obviously low-value suggestions so the report stays actionable.
    return deduped.slice(0, Math.max(0, softLimit - currentOutbound) || 3);
  }
  return deduped;
}

function main(): void {
  const idArg = process.argv.find((a) => a.startsWith("--id="))?.split("=")[1];
  const graph = buildGraph();

  const targets = idArg ? graph.entities.filter((e) => e.data.id === idArg) : graph.entities;
  if (idArg && targets.length === 0) {
    console.error(`No entity with id '${idArg}' found.`);
    process.exit(1);
  }

  let totalSuggestions = 0;
  for (const entity of targets) {
    const suggestions = suggestForEntity(graph, entity);
    if (suggestions.length === 0) continue;
    totalSuggestions += suggestions.length;
    console.log(`${title(entity)}`);
    for (const s of suggestions) {
      const target = graph.byId.get(s.targetId);
      console.log(`  + ${s.verb} -> ${title(target)}  [score ${s.score.toFixed(2)}]`);
      console.log(`      ${s.reason}`);
    }
    console.log("");
  }

  console.log("---");
  console.log(`${totalSuggestions} candidate relationship(s) suggested across ${targets.length} object(s).`);
  console.log("These are suggestions only — nothing was written. Add any you accept by hand, each with its own 'reason'.");
}

main();
