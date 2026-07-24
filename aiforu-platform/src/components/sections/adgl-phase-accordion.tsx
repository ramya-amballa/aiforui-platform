import { adglPhases } from "@/content/adgl";

/**
 * The five phases, collapsed by default. Uses native <details>/<summary>
 * with a shared `name` so opening one phase closes the others (a real
 * accordion, no client JS required) — a visitor sees one phase's
 * governance question, activities and gate at a time, not all five in
 * full at once.
 */
export function AdglPhaseAccordion() {
  return (
    <div>
      {adglPhases.map((phase) => (
        <details key={phase.step} name="adgl-phase" className="group border-t-2 border-ink py-6">
          <summary className="flex cursor-pointer list-none items-start justify-between gap-6 [&::-webkit-details-marker]:hidden">
            <div className="flex items-baseline gap-4">
              <span className="font-mono text-xs text-accent">{String(phase.step).padStart(2, "0")}</span>
              <div>
                <p className="font-serif text-title text-ink">{phase.name}</p>
                <p className="mt-1 text-sm leading-relaxed text-muted pretty">{phase.purpose}</p>
              </div>
            </div>
            <span aria-hidden className="mt-1 shrink-0 font-mono text-lg text-accent transition-transform duration-DEFAULT group-open:rotate-45">
              +
            </span>
          </summary>

          <div className="mt-8 grid grid-cols-1 gap-x-10 gap-y-6 pl-0 sm:grid-cols-3 sm:pl-12">
            <div>
              <p className="text-eyebrow uppercase tracking-widest text-muted">Governance Question</p>
              <p className="mt-3 text-sm leading-relaxed text-ink">{phase.question}</p>
            </div>
            <div>
              <p className="text-eyebrow uppercase tracking-widest text-muted">Activities</p>
              <ul className="mt-3 space-y-2">
                {phase.activities.map((activity) => (
                  <li key={activity} className="text-sm leading-relaxed text-muted">
                    {activity}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-eyebrow uppercase tracking-widest text-muted">Exit Criteria</p>
              <p className="mt-3 text-sm leading-relaxed text-ink">{phase.exitSummary}</p>
              <p className="mt-3 font-serif text-sm text-accent">{phase.gate}</p>
            </div>
          </div>
        </details>
      ))}
    </div>
  );
}
