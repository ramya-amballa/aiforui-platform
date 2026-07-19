import { Fragment } from "react";
import { governanceWorkflow, governanceWorkflowOutcomes } from "@/content/opera";

/**
 * The six-step governance workflow an AI use case actually moves
 * through under OPERA, from submission to evidence and assurance.
 * Distinct from the five OPERA stages: this is the operational
 * decision path within a single use case's lifecycle. Uses the same
 * index-badge, connected-node visual language as OperaDiagram, so the
 * two diagrams read as one operating model rather than unrelated
 * graphics.
 */
export function GovernanceWorkflow() {
  return (
    <div>
      <ol className="flex flex-col gap-8 sm:flex-row sm:items-start sm:gap-0">
        {governanceWorkflow.map((item, index) => (
          <Fragment key={item.step}>
            {index > 0 && (
              <li aria-hidden className="hidden shrink-0 items-start justify-center px-2 pt-3 text-muted sm:flex">
                &rarr;
              </li>
            )}
            <li
              className="capability-node flex-1 border-t border-border pt-4 sm:border-t-0"
              style={{ "--stage-delay": `${index * 60}ms` } as React.CSSProperties}
            >
              <span className="flex h-6 w-6 items-center justify-center border border-signal/40 font-mono text-[10px] text-signal">
                {String(item.step).padStart(2, "0")}
              </span>
              <p className="mt-3 font-serif text-base text-ink">{item.name}</p>
              <p className="mt-1 text-sm leading-relaxed text-muted">{item.detail}</p>
            </li>
          </Fragment>
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
