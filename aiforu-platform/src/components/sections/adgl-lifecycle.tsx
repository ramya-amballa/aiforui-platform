import { adglPhases } from "@/content/adgl";

/**
 * The ADGL lifecycle diagram: the visual identity of ADGL across the
 * site and in future distribution (LinkedIn, the methodology PDF).
 * Uses the same connected-axis, node-on-a-line language as OperaDiagram
 * and GovernanceWorkflow, so ADGL reads as part of one governance
 * visual system rather than a competing graphic. Deliberately just a
 * name and a single line per phase, Gartner-diagram style — activities,
 * questions and gates belong to the accordion below, not here.
 */
export function AdglLifecycleDiagram() {
  return (
    <ol className="grid grid-cols-1 gap-x-6 gap-y-12 sm:grid-cols-5">
      {adglPhases.map((phase, index) => (
        <li
          key={phase.step}
          className="capability-node relative border-t-2 border-ink pt-8"
          style={{ "--stage-delay": `${index * 80}ms` } as React.CSSProperties}
        >
          <span className="absolute -top-4 left-0 flex h-8 w-8 items-center justify-center border border-accent bg-paper font-mono text-xs text-accent">
            {String(phase.step).padStart(2, "0")}
          </span>
          <p className="font-serif text-title text-ink">{phase.name}</p>
          <p className="mt-3 text-sm leading-relaxed text-muted pretty">{phase.purpose}</p>
        </li>
      ))}
    </ol>
  );
}
