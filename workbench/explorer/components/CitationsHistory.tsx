import type { GraphNode } from "@/lib/types";
import { CONFIDENCE_EXPLANATION } from "@/lib/confidence-copy";

export function CitationsSection({ node }: { node: GraphNode }) {
  return (
    <section id="citations" className="scroll-mt-20 border-t border-ink-200 py-6">
      <h2 className="mb-3 text-base font-semibold text-ink-900">
        Citations <span className="text-sm font-normal text-ink-400">({node.citations?.length ?? 0})</span>
      </h2>
      {!node.citations?.length ? (
        <p className="text-sm text-ink-400">No citations recorded.</p>
      ) : (
        <ol className="flex flex-col gap-3">
          {node.citations.map((c) => (
            <li key={c.id} className="border-l-2 border-ink-200 pl-3 text-sm">
              <div className="font-medium text-ink-900">
                {c.url ? (
                  <a href={c.url} target="_blank" rel="noreferrer" className="hover:underline">
                    {c.title}
                  </a>
                ) : (
                  c.title
                )}
              </div>
              <div className="text-ink-500">
                {c.publisher}
                {c.publication_date ? ` · ${c.publication_date}` : ""} · <span className="capitalize">{c.source_type.replace(/_/g, " ")}</span>
              </div>
              {c.locator && <div className="mt-0.5 text-xs text-ink-400">Locator: {c.locator}</div>}
              {c.excerpt && <div className="mt-0.5 text-xs italic text-ink-500">&ldquo;{c.excerpt}&rdquo;</div>}
              <div className="mt-0.5 text-xs text-ink-400">Accessed {c.accessed_date}</div>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

export function HistorySection({ node }: { node: GraphNode }) {
  return (
    <section id="history" className="scroll-mt-20 border-t border-ink-200 py-6">
      <h2 className="mb-3 text-base font-semibold text-ink-900">History</h2>
      <ol className="flex flex-col gap-3 border-l border-ink-200 pl-4">
        {node.history?.map((h, i) => (
          <li key={i} className="relative text-sm">
            <span className="absolute -left-[1.35rem] top-1 h-2 w-2 rounded-full bg-ink-300" />
            <div className="text-ink-900">
              <span className="font-medium capitalize">{h.event}</span> · v{h.version} · {h.date}
            </div>
            <div className="text-ink-500">by {h.by}</div>
            {h.note && <div className="mt-0.5 text-ink-500">{h.note}</div>}
          </li>
        ))}
      </ol>
    </section>
  );
}

export function ConfidenceSection({ node }: { node: GraphNode }) {
  return (
    <section id="confidence" className="scroll-mt-20 border-t border-ink-200 py-6">
      <h2 className="mb-2 text-base font-semibold text-ink-900">Confidence</h2>
      <p className="text-sm text-ink-600">
        <span className="font-medium text-ink-900">{node.confidence}.</span> {CONFIDENCE_EXPLANATION[node.confidence]}
      </p>
      {(node.created_by || node.reviewed_by || node.approved_by) && (
        <dl className="mt-3 grid grid-cols-1 gap-2 text-sm sm:grid-cols-3">
          {node.created_by && (
            <div>
              <dt className="text-xs text-ink-400">Created by</dt>
              <dd className="text-ink-700">{node.created_by}</dd>
            </div>
          )}
          {node.reviewed_by && (
            <div>
              <dt className="text-xs text-ink-400">Reviewed by</dt>
              <dd className="text-ink-700">{node.reviewed_by}</dd>
            </div>
          )}
          {node.approved_by && (
            <div>
              <dt className="text-xs text-ink-400">Approved by</dt>
              <dd className="text-ink-700">{node.approved_by}</dd>
            </div>
          )}
        </dl>
      )}
    </section>
  );
}
