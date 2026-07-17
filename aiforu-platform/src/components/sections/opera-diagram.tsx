import Link from "next/link";
import { cn } from "@/lib/utils";
import { operaStages } from "@/content/opera";

interface OperaDiagramProps {
  showLink?: boolean;
}

/**
 * Compact OPERA summary for the homepage and About page: letter, name
 * and the real activities per stage from content/opera.ts. The full
 * breakdown (governance decisions, artefacts, business outcomes) lives
 * on /methodology; this is a teaser, not a duplicate. Stages are
 * separated by a vertical rule rather than an arrow glyph, which
 * collided with the following stage's letter at this column width.
 */
export function OperaDiagram({ showLink = true }: OperaDiagramProps) {
  return (
    <div className="border-t border-border pt-8">
      <ol className="grid grid-cols-1 gap-8 sm:grid-cols-5 sm:gap-6">
        {operaStages.map((stage, index) => (
          <li key={stage.letter} className={cn(index > 0 && "sm:border-l sm:border-border sm:pl-6")}>
            <div className="flex items-baseline gap-3 sm:block sm:gap-0">
              <span className="font-serif text-3xl text-accent">{stage.letter}</span>
              <p className="font-serif text-base text-ink sm:mt-3">{stage.name}</p>
            </div>
            <ul className="mt-2 space-y-1">
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
        <Link href="/methodology" className="mt-8 inline-block text-sm text-accent underline underline-offset-4">
          View the full methodology &rarr;
        </Link>
      )}
    </div>
  );
}
