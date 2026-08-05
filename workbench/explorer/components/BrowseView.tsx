"use client";

import { useEffect, useMemo, useState } from "react";
import type { EntityType, GraphNode } from "@/lib/types";
import { ENTITY_LABEL_PLURAL, CONFIDENCE_ORDER } from "@/lib/types";
import { EMPTY_FILTERS, parseFilters, filtersToSearch, toggleValue, type Filters } from "@/lib/filter-url";
import { NodeListItem } from "./NodeListItem";

type SortKey = "id" | "title" | "updated" | "severity";

const SEVERITY_RANK: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };

function FacetGroup({
  label,
  options,
  selected,
  onToggle,
}: {
  label: string;
  options: { value: string; count: number }[];
  selected: string[];
  onToggle: (v: string) => void;
}) {
  if (options.length === 0) return null;
  return (
    <div className="border-b border-ink-200 py-4">
      <div className="field-label mb-2">{label}</div>
      <div className="flex max-h-48 flex-col gap-1 overflow-y-auto pr-1">
        {options.map((opt) => (
          <label key={opt.value} className="flex cursor-pointer items-center justify-between gap-2 rounded px-1 py-0.5 text-sm hover:bg-ink-50">
            <span className="flex items-center gap-2 truncate">
              <input
                type="checkbox"
                checked={selected.includes(opt.value)}
                onChange={() => onToggle(opt.value)}
                className="h-3.5 w-3.5 rounded border-ink-300 text-accent-600 focus:ring-accent-500"
              />
              <span className="truncate text-ink-700">{opt.value}</span>
            </span>
            <span className="text-xs text-ink-400 tabular-nums">{opt.count}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

export function BrowseView({ type, nodes }: { type: EntityType; nodes: GraphNode[] }) {
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS);
  const [sort, setSort] = useState<SortKey>("id");
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setFilters(parseFilters(window.location.search));
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    const search = filtersToSearch(filters);
    const url = `${window.location.pathname}${search}`;
    window.history.replaceState(null, "", url);
  }, [filters, hydrated]);

  const facets = useMemo(() => {
    const count = (getter: (n: GraphNode) => string[]) => {
      const m = new Map<string, number>();
      for (const n of nodes) for (const v of getter(n)) m.set(v, (m.get(v) ?? 0) + 1);
      return [...m.entries()].sort((a, b) => b[1] - a[1]).map(([value, count]) => ({ value, count }));
    };
    return {
      tags: count((n) => n.tags ?? []),
      jurisdiction: count((n) => n.jurisdiction ?? []),
      framework: count((n) => n.related_frameworks ?? []),
      confidence: count((n) => [n.confidence]),
      status: count((n) => [n.status]),
    };
  }, [nodes]);

  const filtered = useMemo(() => {
    const q = filters.q.trim().toLowerCase();
    let list = nodes.filter((n) => {
      if (q) {
        const haystack = `${n.id} ${n.title} ${n.description} ${(n.tags ?? []).join(" ")}`.toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      if (filters.tags.length && !filters.tags.some((t) => n.tags?.includes(t))) return false;
      if (filters.jurisdiction.length && !filters.jurisdiction.some((j) => n.jurisdiction?.includes(j))) return false;
      if (filters.framework.length && !filters.framework.some((f) => n.related_frameworks?.includes(f))) return false;
      if (filters.confidence.length && !filters.confidence.includes(n.confidence)) return false;
      if (filters.status.length && !filters.status.includes(n.status)) return false;
      return true;
    });

    list = [...list].sort((a, b) => {
      if (sort === "title") return a.title.localeCompare(b.title);
      if (sort === "updated") return b.updated_date.localeCompare(a.updated_date);
      if (sort === "severity") return (SEVERITY_RANK[a.severity ?? ""] ?? 9) - (SEVERITY_RANK[b.severity ?? ""] ?? 9);
      return a.id.localeCompare(b.id, undefined, { numeric: true });
    });
    return list;
  }, [nodes, filters, sort]);

  const activeFacetCount =
    filters.tags.length + filters.jurisdiction.length + filters.framework.length + filters.confidence.length + filters.status.length;

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-[240px_1fr]">
      <details className="no-print lg:[&_summary]:hidden lg:[&_summary]:mb-0" open>
        <summary className="mb-3 cursor-pointer select-none text-sm font-semibold text-ink-900">
          Filters {activeFacetCount > 0 && <span className="text-accent-600">({activeFacetCount})</span>}
        </summary>
        <div className="mb-4">
          <input
            value={filters.q}
            onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value }))}
            placeholder={`Filter ${ENTITY_LABEL_PLURAL[type].toLowerCase()}…`}
            className="w-full rounded border border-ink-200 px-3 py-2 text-sm focus:border-accent-400 focus:outline-none"
          />
        </div>
        {activeFacetCount > 0 && (
          <button onClick={() => setFilters(EMPTY_FILTERS)} className="mb-2 text-xs font-medium text-accent-600 hover:underline">
            Clear {activeFacetCount} filter{activeFacetCount === 1 ? "" : "s"}
          </button>
        )}
        <FacetGroup label="Confidence" options={facets.confidence.sort((a, b) => CONFIDENCE_ORDER.indexOf(a.value as never) - CONFIDENCE_ORDER.indexOf(b.value as never))} selected={filters.confidence} onToggle={(v) => setFilters((f) => ({ ...f, confidence: toggleValue(f.confidence, v) }))} />
        <FacetGroup label="Status" options={facets.status} selected={filters.status} onToggle={(v) => setFilters((f) => ({ ...f, status: toggleValue(f.status, v) }))} />
        <FacetGroup label="Jurisdiction" options={facets.jurisdiction} selected={filters.jurisdiction} onToggle={(v) => setFilters((f) => ({ ...f, jurisdiction: toggleValue(f.jurisdiction, v) }))} />
        <FacetGroup label="Framework" options={facets.framework} selected={filters.framework} onToggle={(v) => setFilters((f) => ({ ...f, framework: toggleValue(f.framework, v) }))} />
        <FacetGroup label="Tags" options={facets.tags} selected={filters.tags} onToggle={(v) => setFilters((f) => ({ ...f, tags: toggleValue(f.tags, v) }))} />
      </details>

      <div>
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-ink-500">
            {filtered.length} of {nodes.length}
          </span>
          <label className="flex items-center gap-2 text-sm text-ink-500">
            Sort
            <select
              value={sort}
              onChange={(e) => setSort(e.target.value as SortKey)}
              className="rounded border border-ink-200 px-2 py-1 text-sm text-ink-700 focus:border-accent-400 focus:outline-none"
            >
              <option value="id">ID</option>
              <option value="title">Title A–Z</option>
              <option value="updated">Recently updated</option>
              {type === "incident" && <option value="severity">Severity</option>}
            </select>
          </label>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((n) => (
            <NodeListItem key={n.id} node={n} />
          ))}
        </div>
        {filtered.length === 0 && <div className="py-16 text-center text-sm text-ink-400">No results match these filters.</div>}
      </div>
    </div>
  );
}
