import Link from "next/link";
import { operaStages } from "@/content/opera";

/**
 * A compact reference card in the homepage hero's right column, not a
 * second focal point: the H1 in the left column is the dominant
 * element on this page. Deliberately plain (no grid pattern, no
 * corner brackets) and short, so it reads as a briefing note next to
 * the headline rather than a competing cover panel. Stage names are
 * listed, not rendered as large decorative letterforms, so a visitor
 * can tell in one glance that OPERA is a five-stage method, not a
 * logotype.
 */
export function OperaHeroMark() {
  return (
    <div className="border border-brand-ink-quiet/10 bg-brand-ink-quiet px-6 py-6 sm:px-7 sm:py-7">
      <p className="text-eyebrow uppercase tracking-widest text-brand-muted">OPERA Methodology</p>

      <ol className="mt-5 space-y-2 border-t border-brand-paper/10 pt-5">
        {operaStages.map((stage) => (
          <li key={stage.letter} className="flex items-baseline gap-3 text-sm text-brand-paper">
            <span className="w-4 shrink-0 text-brand-gold">{stage.letter}</span>
            <span>{stage.name}</span>
          </li>
        ))}
      </ol>

      <Link
        href="/methodology"
        className="mt-5 inline-block text-xs text-brand-gold underline underline-offset-4"
      >
        View the methodology &rarr;
      </Link>
    </div>
  );
}
