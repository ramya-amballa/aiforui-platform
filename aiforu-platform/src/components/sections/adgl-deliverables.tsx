import { adglPhases } from "@/content/adgl";

/**
 * "What ADGL Produces." No deliverable counts anywhere — the names of
 * the deliverables communicate the value, a count does not. Each
 * phase's purpose sentence is always visible; only the grouped
 * artefact names themselves sit behind "View Deliverables."
 */
export function AdglDeliverables() {
  return (
    <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-2 lg:grid-cols-5">
      {adglPhases.map((phase) => (
        <details key={phase.step} className="group border-t border-border pt-6">
          <summary className="cursor-pointer list-none [&::-webkit-details-marker]:hidden">
            <span className="font-mono text-xs text-accent">{String(phase.step).padStart(2, "0")}</span>
            <p className="mt-2 font-serif text-title text-ink">{phase.name}</p>
            <p className="mt-3 text-sm leading-relaxed text-muted pretty">{phase.deliverablesSummary}</p>
            <span className="mt-4 inline-block text-xs text-accent underline underline-offset-4 group-open:hidden">
              View Deliverables &rarr;
            </span>
            <span className="mt-4 hidden text-xs text-muted group-open:inline-block">Hide Deliverables</span>
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
