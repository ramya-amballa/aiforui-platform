import type { GraphNode } from "@/lib/types";
import { ENTITY_LABEL } from "@/lib/types";
import { ENTITY_COLOR } from "@/lib/entity-colors";
import { ANCHOR_ID, CHAIN_ORDER } from "@/lib/anchors";

export function RelationshipChain({ node }: { node: GraphNode }) {
  const counts = new Map<string, number>();
  for (const r of [...node.relationships_out, ...node.relationships_in]) {
    counts.set(r.other_type, (counts.get(r.other_type) ?? 0) + 1);
  }

  return (
    <nav aria-label="Relationship chain" className="no-print mb-8 flex flex-wrap items-center gap-1 rounded-md border border-ink-200 bg-ink-50 p-2">
      {CHAIN_ORDER.map((type, i) => {
        const isCurrent = type === node.entity_type;
        const count = counts.get(type) ?? 0;
        const c = ENTITY_COLOR[type];
        const content = (
          <span
            className={`flex items-center gap-1.5 rounded px-2.5 py-1.5 text-xs font-medium ${
              isCurrent ? `${c.bg} ${c.text} border ${c.border}` : count > 0 ? "text-ink-600 hover:bg-white" : "text-ink-300"
            }`}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${c.dot} ${isCurrent || count > 0 ? "" : "opacity-30"}`} />
            {ENTITY_LABEL[type]}
            {!isCurrent && count > 0 && <span className="tabular-nums text-ink-400">({count})</span>}
            {isCurrent && <span className="font-semibold">· here</span>}
          </span>
        );
        return (
          <span key={type} className="flex items-center">
            {i > 0 && <span className="mx-0.5 text-ink-300">→</span>}
            {!isCurrent && count > 0 ? <a href={`#${ANCHOR_ID[type]}`}>{content}</a> : content}
          </span>
        );
      })}
    </nav>
  );
}
