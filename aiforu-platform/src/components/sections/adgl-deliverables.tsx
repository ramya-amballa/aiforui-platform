import { adglPhases } from "@/content/adgl";

/**
 * "What you walk away with," collapsed to a count per phase by
 * default. Nobody needs to see thirty artefact names on first look —
 * each phase's full list is one click away via native <details>, not
 * a wall of text.
 */
export function AdglDeliverables() {
  return (
    <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-2 lg:grid-cols-5">
      {adglPhases.map((phase) => (
        <details key={phase.step} className="group border-t border-border pt-6">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-3 [&::-webkit-details-marker]:hidden">
            <div>
              <p className="text-eyebrow uppercase tracking-widest text-muted">
                {String(phase.step).padStart(2, "0")} — {phase.name}
              </p>
              <p className="mt-2 text-sm text-ink">{phase.deliverables.length} Governance Artefacts</p>
            </div>
            <span className="shrink-0 text-xs text-accent underline underline-offset-4 group-open:hidden">View</span>
            <span className="hidden shrink-0 text-xs text-muted group-open:inline">Hide</span>
          </summary>
          <ul className="mt-4 space-y-2">
            {phase.deliverables.map((deliverable) => (
              <li key={deliverable} className="text-sm leading-relaxed text-ink">
                {deliverable}
              </li>
            ))}
          </ul>
        </details>
      ))}
    </div>
  );
}
