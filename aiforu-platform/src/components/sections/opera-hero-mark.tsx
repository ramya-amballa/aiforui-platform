import Link from "next/link";
import { operaStages } from "@/content/opera";

/**
 * The homepage hero's primary visual: a restrained, executive rendering
 * of the OPERA sequence, not the full stage detail (that lives in
 * OperaDiagram and on /methodology). Letters and connectors sit in
 * normal inline flow, not absolute positioning, deliberately: the
 * homepage OPERA diagram previously used absolute-positioned arrows
 * that collided with the following stage's letter.
 */
export function OperaHeroMark() {
  return (
    <div className="flex h-full flex-col justify-center border border-border bg-surface p-8 sm:p-10">
      <p className="text-eyebrow uppercase tracking-widest text-muted">Proprietary Methodology</p>

      <div className="mt-8 flex flex-nowrap items-center">
        {operaStages.map((stage, index) => (
          <span key={stage.letter} className="flex items-center">
            <span className="font-serif text-3xl text-accent">{stage.letter}</span>
            {index < operaStages.length - 1 && (
              <span aria-hidden className="mx-2 text-muted">
                &rarr;
              </span>
            )}
          </span>
        ))}
      </div>

      <p className="mt-8 font-serif text-title text-ink">Operational AI Governance Methodology</p>
      <p className="mt-4 text-sm leading-relaxed text-muted pretty">
        A structured implementation pathway that translates governance requirements into operational decisions,
        evidence, accountability and audit readiness.
      </p>

      <Link href="/methodology" className="mt-8 inline-block text-sm text-accent underline underline-offset-4">
        Explore the full methodology &rarr;
      </Link>
    </div>
  );
}
