import { governanceWorkflow, governanceWorkflowOutcomes } from "@/content/opera";

/**
 * The six-step governance workflow an AI use case actually moves
 * through under OPERA, from submission to evidence and assurance.
 * Distinct from the five OPERA stages: this is the operational
 * decision path within a single use case's lifecycle.
 */
export function GovernanceWorkflow() {
  return (
    <div>
      <ol className="grid grid-cols-1 gap-8 sm:grid-cols-3 lg:grid-cols-6 sm:gap-6">
        {governanceWorkflow.map((item) => (
          <li key={item.step} className="border-t border-border pt-4">
            <span className="font-mono text-xs text-signal">{String(item.step).padStart(2, "0")}</span>
            <p className="mt-2 font-serif text-base text-ink">{item.name}</p>
            <p className="mt-1 text-sm leading-relaxed text-muted">{item.detail}</p>
          </li>
        ))}
      </ol>
      <div className="mt-10 border-t border-border pt-6">
        <p className="text-eyebrow uppercase tracking-widest text-muted">What the Workflow Produces</p>
        <ul className="mt-4 flex flex-wrap gap-x-8 gap-y-2">
          {governanceWorkflowOutcomes.map((outcome) => (
            <li key={outcome} className="text-sm text-ink">
              {outcome}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
