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
          <summary className="flex cursor-pointer list-none flex-col gap-2 [&::-webkit-details-marker]:hidden">
            <div className="flex items-baseline justify-between gap-3">
              <p className="text-eyebrow uppercase tracking-widest text-muted">
                {String(phase.step).padStart(2, "0")} — {phase.name}
              </p>
              <span className="shrink-0 text-xs text-accent underline underline-offset-4 group-open:hidden">
                View Deliverables
              </span>
              <span className="hidden shrink-0 text-xs text-muted group-open:inline">Hide</span>
            </div>
            <p className="text-sm leading-relaxed text-ink pretty">{phase.deliverablesSummary}</p>
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
