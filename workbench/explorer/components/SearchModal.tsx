"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { getSearchIndex } from "@/lib/search";
import { ENTITY_LABEL_PLURAL, ENTITY_ROUTE, ENTITY_TYPES, type EntityType, type SearchDocument } from "@/lib/types";

const EXAMPLE_QUERIES = [
  "human oversight",
  "hallucination",
  "hiring",
  "GDPR",
  "board question",
  "facial recognition",
];

interface Grouped {
  type: EntityType;
  items: SearchDocument[];
}

export function SearchModal({ onClose, initialQuery = "" }: { onClose: () => void; initialQuery?: string }) {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState(initialQuery);
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const results = useMemo(() => {
    if (!query.trim()) return [];
    const idx = getSearchIndex();
    return idx.search(query).slice(0, 30) as unknown as (SearchDocument & { score: number })[];
  }, [query]);

  const grouped: Grouped[] = useMemo(() => {
    const map = new Map<EntityType, SearchDocument[]>();
    for (const r of results) {
      const list = map.get(r.entity_type) ?? [];
      list.push(r);
      map.set(r.entity_type, list);
    }
    return ENTITY_TYPES.filter((t) => map.has(t)).map((t) => ({ type: t, items: map.get(t)!.slice(0, 6) }));
  }, [results]);

  const flatItems = useMemo(() => grouped.flatMap((g) => g.items), [grouped]);

  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  function goTo(item: SearchDocument) {
    router.push(`/${ENTITY_ROUTE[item.entity_type]}/${item.slug}/`);
    onClose();
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((i) => Math.min(i + 1, flatItems.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      const item = flatItems[activeIndex];
      if (item) goTo(item);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-ink-950/40 px-4 pt-[8vh]" onClick={onClose}>
      <div
        className="w-full max-w-xl overflow-hidden rounded-lg border border-ink-200 bg-white shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-ink-200 px-4 py-3">
          <svg className="h-4 w-4 flex-shrink-0 text-ink-400" viewBox="0 0 20 20" fill="none" stroke="currentColor">
            <circle cx="9" cy="9" r="6" strokeWidth="1.5" />
            <path d="M17 17l-4-4" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Search decisions, incidents, patterns, controls, evidence, board questions…"
            className="w-full border-none bg-transparent text-sm text-ink-900 placeholder:text-ink-400 focus:outline-none"
          />
          <kbd className="hidden rounded border border-ink-200 bg-ink-50 px-1.5 py-0.5 text-[10px] font-medium text-ink-400 sm:inline">
            Esc
          </kbd>
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-2">
          {query.trim() === "" && (
            <div className="px-3 py-6">
              <div className="field-label mb-2">Try asking</div>
              <div className="flex flex-wrap gap-1.5">
                {EXAMPLE_QUERIES.map((q) => (
                  <button
                    key={q}
                    onClick={() => setQuery(q)}
                    className="rounded border border-ink-200 px-2 py-1 text-xs text-ink-600 hover:border-ink-400 hover:bg-ink-50"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {query.trim() !== "" && flatItems.length === 0 && (
            <div className="px-3 py-8 text-center text-sm text-ink-500">No results for &ldquo;{query}&rdquo;.</div>
          )}

          {grouped.map((group) => (
            <div key={group.type} className="mb-2">
              <div className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-ink-400">
                {ENTITY_LABEL_PLURAL[group.type]}
              </div>
              {group.items.map((item) => {
                const flatIdx = flatItems.indexOf(item);
                const active = flatIdx === activeIndex;
                return (
                  <button
                    key={item.id}
                    onMouseEnter={() => setActiveIndex(flatIdx)}
                    onClick={() => goTo(item)}
                    className={`flex w-full items-start gap-2 rounded px-3 py-2 text-left ${active ? "bg-accent-50" : "hover:bg-ink-50"}`}
                  >
                    <span className="id-tag mt-0.5 w-16 flex-shrink-0">{item.id}</span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm text-ink-900">{item.title}</span>
                    </span>
                  </button>
                );
              })}
            </div>
          ))}
        </div>
        <div className="flex items-center justify-between border-t border-ink-200 bg-ink-50 px-4 py-2 text-xs text-ink-400">
          <span>↑↓ to navigate · ↵ to open</span>
          <span>{flatItems.length} result{flatItems.length === 1 ? "" : "s"}</span>
        </div>
      </div>
    </div>
  );
}
