import Link from "next/link";
import { operaStages } from "@/content/opera";

/**
 * A compact governance operating model diagram in the homepage hero's
 * right column, not a second focal point: the H1 in the left column
 * stays dominant. Deliberately not a logo mark: OPERA is rendered as a
 * connected sequence of capability nodes (index, stage, outcome), the
 * same "spine and node" language other methodology diagrams
 * (OperaDiagram, GovernanceWorkflow) use, so the site reads as one
 * operating model rather than a set of unrelated graphics.
 */
export function OperaHeroMark() {
  return (
    <div className="border border-brand-ink-quiet/10 bg-brand-ink-quiet px-6 py-6 sm:px-7 sm:py-7">
      <p className="text-eyebrow uppercase tracking-widest text-brand-gold">Governance Operating Model</p>
      <p className="mt-2 font-mono text-[11px] uppercase tracking-wide text-brand-muted">
        OPERA &middot; Five Stages
      </p>

      <ol className="mt-6 space-y-5 border-t border-brand-paper/10 pt-6">
        {operaStages.map((stage, index) => (
          <li
            key={stage.letter}
            className="capability-node relative flex gap-4"
            style={{ "--stage-delay": `${index * 70}ms` } as React.CSSProperties}
          >
            {index < operaStages.length - 1 && (
              <span aria-hidden className="absolute left-3 top-6 -bottom-5 w-px bg-brand-paper/15" />
            )}
            <span className="relative z-10 flex h-6 w-6 shrink-0 items-center justify-center border border-brand-gold/40 bg-brand-ink-quiet font-mono text-[10px] text-brand-gold">
              {stage.letter}
            </span>
            <div>
              <p className="font-serif text-sm text-brand-paper">{stage.name}</p>
              <p className="mt-0.5 text-xs text-brand-muted">{stage.outcome}</p>
            </div>
          </li>
        ))}
      </ol>

      <Link
        href="/methodology"
        className="mt-6 inline-block border-t border-brand-paper/10 pt-5 text-xs text-brand-gold underline underline-offset-4"
      >
        View the full methodology &rarr;
      </Link>
    </div>
  );
}
