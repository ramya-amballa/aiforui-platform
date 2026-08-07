import type { GraphNode } from "@/lib/types";
import { EntityTypeBadge } from "./EntityTypeBadge";
import { ConfidenceBadge, StatusBadge, SeverityBadge } from "./Badge";
import { ExportButtons } from "./ExportButtons";

export function DetailHeader({ node }: { node: GraphNode }) {
  return (
    <div className="mb-8 border-b border-ink-200 pb-6">
      <div className="flex flex-wrap items-center gap-2">
        <EntityTypeBadge type={node.entity_type} />
        <span className="id-tag">{node.id}</span>
        <StatusBadge value={node.status} />
        <ConfidenceBadge value={node.confidence} />
        {node.severity && <SeverityBadge value={node.severity} />}
      </div>
      <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
        <h1 className="max-w-3xl text-2xl font-semibold leading-snug text-ink-900 sm:text-[1.75rem]">{node.title}</h1>
        <ExportButtons node={node} />
      </div>
      <p className="prose-body mt-3 max-w-3xl">{node.description}</p>
      {node.tags?.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {node.tags.map((t) => (
            <span key={t} className="rounded border border-ink-200 px-1.5 py-0.5 text-xs text-ink-500">
              {t}
            </span>
          ))}
        </div>
      )}
      <p className="mt-3 text-xs text-ink-400">
        Last reviewed {node.updated_date} (v{node.version}) · Published in Edition {node.first_edition}
      </p>
    </div>
  );
}
