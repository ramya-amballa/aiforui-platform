import { adglPhases } from "@/content/adgl";

/**
 * "What you walk away with." The count and the one-sentence reason
 * the deliverables matter are always visible, so "6 Key Deliverables"
 * never sits there unexplained — only the grouped artefact names
 * themselves are behind the click.
 */
export function AdglDeliverables() {
  return (
    <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-2 lg:grid-cols-5">
      {adglPhases.map((phase) => {
        const deliverableCount = phase.deliverableGroups.reduce((count, group) => count + group.items.length, 0);

        return (
          <details key={phase.step} className="group border-t border-border pt-6">
            <summary className="flex cursor-pointer list-none items-start justify-between gap-3 [&::-webkit-details-marker]:hidden">
              <div>
                <p className="text-eyebrow uppercase tracking-widest text-muted">
                  {String(phase.step).padStart(2, "0")} — {phase.name}
                </p>
                <p className="mt-2 text-sm text-ink">{deliverableCount} Key Deliverables</p>
                <p className="mt-2 text-sm leading-relaxed text-muted pretty">{phase.deliverablesSummary}</p>
              </div>
              <span className="mt-1 shrink-0 text-xs text-accent underline underline-offset-4 group-open:hidden">View</span>
              <span className="mt-1 hidden shrink-0 text-xs text-muted group-open:inline">Hide</span>
            </summary>

            <div className="mt-5 space-y-5">
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
          </details>
        );
      })}
    </div>
  );
}
