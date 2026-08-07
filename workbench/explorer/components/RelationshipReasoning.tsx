import Link from "next/link";
import type { GraphNode } from "@/lib/types";
import { ENTITY_ROUTE } from "@/lib/types";

const VERB_LABEL: Record<string, string> = {
  RESULTED_FROM: "resulted from",
  MITIGATED_BY: "mitigated by",
  IMPLEMENTED_BY: "implemented by",
  SATISFIES_CONTROL: "satisfies",
  REQUIRES_EVIDENCE: "requires evidence",
  RAISES_BOARD_QUESTION: "raises",
  RELATED_TO: "related to",
};

export function RelationshipReasoning({ node }: { node: GraphNode }) {
  const rows = [...node.relationships_out, ...node.relationships_in];
  return (
    <section id="relationship-reasoning" className="scroll-mt-20 border-t border-ink-200 py-6">
      <h2 className="mb-1 text-base font-semibold text-ink-900">Relationship reasoning</h2>
      <p className="mb-3 text-sm text-ink-500">
        Every edge in this graph carries an explicit reason. No relationship exists just because two concepts seemed related.
      </p>
      {rows.length === 0 ? (
        <p className="text-sm text-ink-400">No relationships recorded.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-ink-200 text-left text-xs font-semibold uppercase tracking-wide text-ink-400">
                <th className="py-2 pr-3">Direction</th>
                <th className="py-2 pr-3">Verb</th>
                <th className="py-2 pr-3">Node</th>
                <th className="py-2 pr-3">Reason</th>
                <th className="py-2 pr-3">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i} className="border-b border-ink-100 align-top">
                  <td className="py-2 pr-3 text-ink-400">{r.direction === "out" ? `${node.id} →` : `→ ${node.id}`}</td>
                  <td className="py-2 pr-3 font-mono text-xs text-ink-600">{VERB_LABEL[r.type] ?? r.type}</td>
                  <td className="py-2 pr-3">
                    <Link href={`/${ENTITY_ROUTE[r.other_type]}/${r.other_slug}/`} className="font-medium text-accent-600 hover:underline">
                      {r.other_id}
                    </Link>
                  </td>
                  <td className="py-2 pr-3 text-ink-600">{r.reason}</td>
                  <td className="py-2 pr-3 text-ink-400">{r.confidence ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
