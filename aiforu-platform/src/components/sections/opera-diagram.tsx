import { Fragment } from "react";
import Link from "next/link";
import { operaStages } from "@/content/opera";

interface OperaDiagramProps {
  showLink?: boolean;
}

/**
 * The OPERA operating model, rendered as a connected sequence of
 * governance capability nodes (index badge, stage, outcome, real
 * activities from content/opera.ts) rather than large decorative
 * letterforms. Shares the node/spine visual language of OperaHeroMark
 * and GovernanceWorkflow: an index mark, not a logotype, is what
 * identifies a stage. The full breakdown (governance decisions,
 * artefacts) lives on /methodology; this is a teaser, not a
 * duplicate.
 */
export function OperaDiagram({ showLink = true }: OperaDiagramProps) {
  return (
    <div className="border-t border-border pt-8">
      <ol className="flex flex-col gap-8 sm:flex-row sm:items-start sm:gap-0">
        {operaStages.map((stage, index) => (
          <Fragment key={stage.letter}>
            {index > 0 && (
              <li aria-hidden className="hidden shrink-0 items-start justify-center px-3 pt-3 text-muted sm:flex">
                &rarr;
              </li>
            )}
            <li
              className="capability-node flex-1"
              style={{ "--stage-delay": `${index * 70}ms` } as React.CSSProperties}
            >
              <span className="flex h-6 w-6 items-center justify-center border border-accent/40 font-mono text-[10px] text-accent">
                {stage.letter}
              </span>
              <p className="mt-3 font-serif text-base text-ink">{stage.name}</p>
              <p className="mt-1 text-xs uppercase tracking-wide text-accent">{stage.outcome}</p>
              <ul className="mt-3 space-y-1">
                {stage.activities.map((activity) => (
                  <li key={activity} className="text-sm leading-relaxed text-muted">
                    {activity}
                  </li>
                ))}
              </ul>
            </li>
          </Fragment>
        ))}
      </ol>
      {showLink && (
        <Link href="/methodology" className="mt-8 inline-block text-sm text-accent underline underline-offset-4">
          View the full methodology &rarr;
        </Link>
      )}
    </div>
  );
}
