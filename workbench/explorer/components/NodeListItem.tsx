import Link from "next/link";
import type { GraphNode } from "@/lib/types";
import { ENTITY_ROUTE } from "@/lib/types";
import { ConfidenceBadge, SeverityBadge, TagBadge } from "./Badge";

export function NodeListItem({ node }: { node: GraphNode }) {
  const href = `/${ENTITY_ROUTE[node.entity_type]}/${node.slug}/`;
  return (
    <Link
      href={href}
      className="card flex flex-col gap-1.5 p-4 hover:border-ink-400 transition-colors"
    >
      <div className="flex items-center justify-between gap-2">
        <span className="id-tag">{node.id}</span>
        <div className="flex items-center gap-1.5">
          {node.severity && <SeverityBadge value={node.severity} />}
          <ConfidenceBadge value={node.confidence} />
        </div>
      </div>
      <h3 className="text-sm font-semibold leading-snug text-ink-900">{node.title}</h3>
      <p className="line-clamp-2 text-sm leading-relaxed text-ink-500">{node.description}</p>
      {(node.jurisdiction?.length || node.tags?.length) && (
        <div className="mt-1 flex flex-wrap gap-1">
          {(node.jurisdiction ?? []).slice(0, 3).map((j) => (
            <TagBadge key={`j-${j}`} value={j} />
          ))}
          {(node.tags ?? []).slice(0, 4).map((t) => (
            <TagBadge key={`t-${t}`} value={t} />
          ))}
        </div>
      )}
    </Link>
  );
}
