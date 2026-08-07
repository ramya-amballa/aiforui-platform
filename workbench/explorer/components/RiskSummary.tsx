import type { GraphNode } from "@/lib/types";
import { riskSummaryForDecision } from "@/lib/data";
import { SeverityBadge } from "./Badge";

export function RiskSummary({ node }: { node: GraphNode }) {
  const summary = riskSummaryForDecision(node);
  return (
    <section id="risk-summary" className="scroll-mt-20 border-t border-ink-200 py-6">
      <h2 className="mb-3 text-base font-semibold text-ink-900">Risk summary</h2>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <div className="field-label mb-1">Incidents mitigated</div>
          <div className="text-2xl font-semibold tabular-nums text-ink-900">{summary.incidentCount}</div>
        </div>
        <div>
          <div className="field-label mb-1">Severity of those incidents</div>
          {summary.severityCounts.length === 0 ? (
            <div className="text-sm text-ink-400">—</div>
          ) : (
            <div className="flex flex-wrap gap-1">
              {summary.severityCounts.map(([sev, count]) => (
                <span key={sev} className="flex items-center gap-1">
                  <SeverityBadge value={sev} />
                  <span className="text-xs text-ink-400">×{count}</span>
                </span>
              ))}
            </div>
          )}
        </div>
        <div>
          <div className="field-label mb-1">Jurisdictions in play</div>
          <div className="text-sm text-ink-700">{summary.jurisdictions.length ? summary.jurisdictions.join(", ") : "—"}</div>
        </div>
        <div>
          <div className="field-label mb-1">Framework coverage</div>
          <div className="text-sm text-ink-700">{summary.frameworks.length ? summary.frameworks.join(", ") : "—"}</div>
        </div>
      </div>
      {summary.harmTypeCounts.length > 0 && (
        <div className="mt-4">
          <div className="field-label mb-1">Harm types observed</div>
          <div className="flex flex-wrap gap-1.5">
            {summary.harmTypeCounts.map(([harm, count]) => (
              <span key={harm} className="rounded border border-ink-200 px-1.5 py-0.5 text-xs text-ink-600">
                {harm.replace(/_/g, " ")} × {count}
              </span>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
