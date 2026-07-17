import Link from "next/link";
import { BlueprintPanel } from "@/components/sections/blueprint-panel";
import { operaStages } from "@/content/opera";

/**
 * The homepage hero's primary visual: a restrained, executive rendering
 * of the OPERA sequence, not the full stage detail (that lives in
 * OperaDiagram and on /methodology). Letters and connectors sit in
 * normal inline flow, not absolute positioning, deliberately: an
 * earlier version used absolute-positioned arrows that collided with
 * the following stage's letter.
 *
 * Attributed to Ramya Amballa by name, not presented as a standalone
 * product: OPERA is the methodology behind the advisory practice, and
 * the practice is the thing being engaged.
 */
export function OperaHeroMark() {
  return (
    <BlueprintPanel tone="ink" className="flex h-full flex-col justify-center p-8 sm:p-10">
      <p className="text-eyebrow uppercase tracking-widest text-brand-muted">Ramya Amballa&apos;s Methodology</p>

      <div className="mt-8 flex flex-nowrap items-center">
        {operaStages.map((stage, index) => (
          <span key={stage.letter} className="flex items-center">
            <span className="font-serif text-3xl text-brand-gold">{stage.letter}</span>
            {index < operaStages.length - 1 && (
              <span aria-hidden className="mx-2 text-brand-muted">
                &rarr;
              </span>
            )}
          </span>
        ))}
      </div>

      <p className="mt-8 font-serif text-title text-brand-paper">Operational AI Governance Methodology</p>
      <p className="mt-4 text-sm leading-relaxed text-brand-muted pretty">
        The structure behind every engagement: how Ramya turns a governance requirement into an operational
        decision, evidence, accountability and audit readiness, not just a policy document.
      </p>

      <Link href="/methodology" className="mt-8 inline-block text-sm text-brand-gold underline underline-offset-4">
        Explore the full methodology &rarr;
      </Link>
    </BlueprintPanel>
  );
}
