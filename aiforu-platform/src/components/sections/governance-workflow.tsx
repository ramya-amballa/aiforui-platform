import { governanceWorkflow, governanceWorkflowOutcomes } from "@/content/opera";

/**
 * The six-step governance workflow an AI use case actually moves
 * through under OPERA, from submission to evidence and assurance.
 * Distinct from the five OPERA stages: this is the operational
 * decision path within a single use case's lifecycle. Uses the same
 * single-axis, node-on-a-line language as OperaDiagram, so the two
 * diagrams read as one operating model rather than unrelated graphics.
 */
export function GovernanceWorkflow() {
  return (
    <div>
      <ol className="grid grid-cols-1 gap-x-6 gap-y-10 sm:grid-cols-3 lg:grid-cols-6">
        {governanceWorkflow.map((item, index) => (
          <li
            key={item.step}
            className="capability-node relative border-t-2 border-ink pt-8"
            style={{ "--stage-delay": `${index * 60}ms` } as React.CSSProperties}
          >
            <span className="absolute -top-3 left-0 flex h-6 w-6 items-center justify-center border border-signal bg-paper font-mono text-[10px] text-signal">
              {String(item.step).padStart(2, "0")}
            </span>
            <p className="font-serif text-base text-ink">{item.name}</p>
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
