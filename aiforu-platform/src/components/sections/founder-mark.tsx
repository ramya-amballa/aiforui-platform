import { BlueprintPanel } from "@/components/sections/blueprint-panel";
import { site } from "@/lib/constants";

/**
 * Replaces a personal portrait in the homepage Founder section with
 * the practice's own identity: this positions Ramya as the founder of
 * a methodology-led advisory practice, not as an individual consultant
 * fronted by a headshot.
 */
export function FounderMark() {
  return (
    <BlueprintPanel tone="paper" className="flex h-full flex-col justify-center p-8 sm:p-10">
      <p className="text-eyebrow uppercase tracking-widest text-muted">Independent Advisory Practice</p>
      <p className="mt-6 font-serif text-display text-ink">{site.name}</p>
      <p className="mt-4 text-sm leading-relaxed text-muted pretty">{site.tagline}</p>
    </BlueprintPanel>
  );
}
