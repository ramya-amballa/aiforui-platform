const stages = [
  { name: "Ad Hoc", description: "Decisions made informally, no consistent owner." },
  { name: "Documented", description: "Policy exists, execution is inconsistent." },
  { name: "Owned", description: "Named owners for decisions and controls." },
  { name: "Operationalised", description: "Ownership is followed as daily practice." },
  { name: "Assured", description: "Evidence is maintained continuously, not assembled after the fact." },
];

/**
 * A five-stage maturity scale used to frame where a governance domain
 * actually stands, distinct from the OPERA methodology (which
 * describes how work is done, not how mature it currently is).
 */
export function MaturityScale() {
  return (
    <div>
      <div className="flex h-1.5 w-full overflow-hidden rounded-full bg-surface">
        {stages.map((stage, index) => (
          <div
            key={stage.name}
            className="flex-1 border-r border-paper last:border-r-0"
            style={{ backgroundColor: `hsl(var(--color-accent) / ${0.25 + index * 0.18})` }}
            aria-hidden
          />
        ))}
      </div>
      <ol className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-5 sm:gap-4">
        {stages.map((stage) => (
          <li key={stage.name}>
            <p className="font-serif text-base text-ink">{stage.name}</p>
            <p className="mt-1 text-sm leading-relaxed text-muted">{stage.description}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
