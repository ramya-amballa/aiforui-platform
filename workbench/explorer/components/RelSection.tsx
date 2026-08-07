import Link from "next/link";
import type { ResolvedRelationship } from "@/lib/types";
import { ENTITY_ROUTE } from "@/lib/types";
import { EntityTypeBadge } from "./EntityTypeBadge";
import { ConfidenceBadge } from "./Badge";

export function RelSection({
  id,
  title,
  items,
  emptyText,
}: {
  id: string;
  title: string;
  items: ResolvedRelationship[];
  emptyText?: string;
}) {
  return (
    <section id={id} className="scroll-mt-20 border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
      <h2 className="mb-3 flex items-center gap-2 text-base font-semibold text-ink-900">
        {title}
        <span className="text-sm font-normal text-ink-400">({items.length})</span>
      </h2>
      {items.length === 0 ? (
        <p className="text-sm text-ink-400">{emptyText ?? "None recorded."}</p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((r, i) => (
            <Link
              key={`${r.other_id}-${i}`}
              href={`/${ENTITY_ROUTE[r.other_type]}/${r.other_slug}/`}
              className="card flex flex-col gap-1 p-3 hover:border-ink-400 transition-colors"
            >
              <div className="flex items-center gap-2">
                <EntityTypeBadge type={r.other_type} compact />
                <span className="id-tag">{r.other_id}</span>
                <span className="rounded border border-ink-200 px-1 py-0.5 font-mono text-[10px] leading-none text-ink-400">
                  {r.type.replace(/_/g, " ").toLowerCase()}
                  {r.direction === "in" ? " (inbound)" : ""}
                </span>
                {r.confidence && <ConfidenceBadge value={r.confidence} />}
              </div>
              <div className="text-sm font-medium text-ink-900">{r.other_title}</div>
              <div className="text-sm leading-snug text-ink-500">{r.reason}</div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
