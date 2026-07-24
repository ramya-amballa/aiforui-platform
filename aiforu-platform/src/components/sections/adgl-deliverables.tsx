import { adglPhases } from "@/content/adgl";

/**
 * "What ADGL Produces." No deliverable counts anywhere — the names of
 * the deliverables communicate the value, a count does not. Each
 * phase's purpose sentence is always visible; only the grouped
 * artefact names sit behind the "+" toggle, matching the Five Phases
 * accordion's expand affordance rather than a "View Deliverables"
 * text link, so the phase name always renders on its own line.
 */
export function AdglDeliverables() {
  return (
    <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-2 lg:grid-cols-5">
      {adglPhases.map((phase) => (
        <details key={phase.step} className="group border-t border-border pt-6">
          <summary className="flex cursor-pointer list-none items-start justify-between gap-3 [&::-webkit-details-marker]:hidden">
            <div>
              <span className="font-mono text-xs text-accent">{String(phase.step).padStart(2, "0")}</span>
              <p className="mt-2 font-serif text-title text-ink">{phase.name}</p>
              <p className="mt-3 text-sm leading-relaxed text-muted pretty">{phase.deliverablesSummary}</p>
            </div>
            <span aria-hidden className="mt-1 shrink-0 font-mono text-lg text-accent transition-transform duration-DEFAULT group-open:rotate-45">
              +
            </span>
          </summary>

          <div className="mt-5">
            <p className="text-eyebrow uppercase tracking-widest text-muted">Key Deliverables</p>
            <div className="mt-4 space-y-5">
              {phase.deliverableGroups.map((group) => (
                <div key={group.label}>
                  <p className="font-serif text-sm text-ink">{group.label}</p>
                  <ul className="mt-2 space-y-1.5">
                    {group.items.map((item) => (
                      <li key={item} className="flex items-baseline gap-2 text-sm leading-relaxed text-muted">
                        <span aria-hidden className="block h-1 w-1 shrink-0 rounded-full bg-accent" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        </details>
      ))}
    </div>
  );
}
