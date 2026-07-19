import Link from "next/link";
import { operaStages } from "@/content/opera";

interface OperaDiagramProps {
  showLink?: boolean;
}

/**
 * The OPERA operating model, rendered as a single connected axis: one
 * rule running under all five stages, with each stage's index badge
 * straddling it like a node on a timeline. This is deliberately not a
 * row of separate cards joined by arrows: the axis reads as one
 * system with five checkpoints, closer to a decision-architecture
 * diagram than an illustration. Shares this language with
 * GovernanceWorkflow. The full breakdown (governance decisions,
 * artefacts) lives on /methodology; this is a teaser, not a
 * duplicate.
 */
export function OperaDiagram({ showLink = true }: OperaDiagramProps) {
  return (
    <div>
      <ol className="grid grid-cols-1 gap-x-6 gap-y-10 sm:grid-cols-5">
        {operaStages.map((stage, index) => (
          <li
            key={stage.letter}
            className="capability-node relative border-t-2 border-ink pt-8"
            style={{ "--stage-delay": `${index * 70}ms` } as React.CSSProperties}
          >
            <span className="absolute -top-3 left-0 flex h-6 w-6 items-center justify-center border border-accent bg-paper font-mono text-[10px] text-accent">
              {stage.letter}
            </span>
            <p className="font-serif text-base text-ink">{stage.name}</p>
            <p className="mt-1 text-xs uppercase tracking-wide text-accent">{stage.outcome}</p>
            <ul className="mt-3 space-y-1">
              {stage.activities.map((activity) => (
                <li key={activity} className="text-sm leading-relaxed text-muted">
                  {activity}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ol>
      {showLink && (
        <Link href="/methodology" className="mt-10 inline-block text-sm text-accent underline underline-offset-4">
          View the full methodology &rarr;
        </Link>
      )}
    </div>
  );
}
