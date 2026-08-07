import type { LoadedEntity } from "./graph.js";

export interface CitationScoreResult {
  score: number;
  findings: string[];
}

/**
 * Deterministic, rule-based citation quality score (0-100). This is
 * advisory, not a validation gate — /validators only requires "at least
 * one citation when the rules in /docs/citation-model.md say so." This
 * scorer answers a different question: given that citations exist, how
 * complete/robust are they? Used by both citation-completeness.ts (per-
 * object detail) and graph-health.ts (dataset-wide aggregate).
 */
export function scoreCitations(entity: LoadedEntity, today: Date): CitationScoreResult {
  const findings: string[] = [];
  const citations = entity.data.citations ?? [];
  const relationships = entity.data.relationships ?? [];

  if (citations.length === 0) {
    findings.push("No citations at all.");
    return { score: 0, findings };
  }

  let score = 40; // base: has at least one citation

  const withUrl = citations.filter((c) => c.url).length;
  const withLocator = citations.filter((c) => c.locator).length;
  const withExcerpt = citations.filter((c) => c.excerpt).length;
  const sourceTypes = new Set(citations.map((c) => c.source_type));

  if (withUrl > 0) score += 15;
  else findings.push("No citation has a url — harder for a reader to verify independently.");

  if (withLocator > 0) score += 10;
  else findings.push("No citation has a locator — a reader must search the whole source to find the supporting passage.");

  if (withExcerpt > 0) score += 15;
  else findings.push("No citation has an excerpt — the specific supporting text isn't captured.");

  if (sourceTypes.size >= 2) {
    score += 10;
  } else {
    findings.push(`Only one source_type ('${[...sourceTypes][0]}') represented — consider corroborating with an independent source type.`);
  }

  if (relationships.length > 0) {
    const withCitationIds = relationships.filter((r) => (r.citation_ids?.length ?? 0) > 0).length;
    const linkage = withCitationIds / relationships.length;
    if (linkage >= 0.5) {
      score += 10;
    } else {
      findings.push(
        `Only ${withCitationIds}/${relationships.length} relationship(s) cite a specific citation_id — most edges aren't traceable to a specific source.`,
      );
    }
  } else {
    score += 10; // nothing to link, don't penalize
  }

  const STALE_YEARS = 3;
  for (const citation of citations) {
    if (!citation.accessed_date) continue;
    const accessed = new Date(citation.accessed_date);
    const ageYears = (today.getTime() - accessed.getTime()) / (1000 * 60 * 60 * 24 * 365.25);
    if (ageYears > STALE_YEARS) {
      findings.push(`Citation '${citation.id}' was last accessed ${accessed.toISOString().slice(0, 10)} (${ageYears.toFixed(1)} years ago) — consider re-verifying the source is still live and accurate.`);
    }
  }

  return { score: Math.min(100, score), findings };
}
