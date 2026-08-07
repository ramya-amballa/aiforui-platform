export interface Filters {
  q: string;
  tags: string[];
  jurisdiction: string[];
  framework: string[];
  confidence: string[];
  status: string[];
}

export const EMPTY_FILTERS: Filters = { q: "", tags: [], jurisdiction: [], framework: [], confidence: [], status: [] };

export function parseFilters(search: string): Filters {
  const params = new URLSearchParams(search);
  return {
    q: params.get("q") ?? "",
    tags: params.getAll("tag"),
    jurisdiction: params.getAll("jurisdiction"),
    framework: params.getAll("framework"),
    confidence: params.getAll("confidence"),
    status: params.getAll("status"),
  };
}

export function filtersToSearch(filters: Filters): string {
  const params = new URLSearchParams();
  if (filters.q) params.set("q", filters.q);
  for (const t of filters.tags) params.append("tag", t);
  for (const j of filters.jurisdiction) params.append("jurisdiction", j);
  for (const f of filters.framework) params.append("framework", f);
  for (const c of filters.confidence) params.append("confidence", c);
  for (const s of filters.status) params.append("status", s);
  const str = params.toString();
  return str ? `?${str}` : "";
}

export function toggleValue(list: string[], value: string): string[] {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value];
}
