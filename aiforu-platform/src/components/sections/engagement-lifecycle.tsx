const steps = [
  { name: "Conversation", description: "A working discussion about a specific problem." },
  { name: "Scoping", description: "Track, domain and depth of work agreed." },
  { name: "OPERA Delivery", description: "Structured through Opportunity, People, Evaluation, Response, Assurance." },
  { name: "Deliverables", description: "Operating models, ownership maps, evidence structures handed over." },
  { name: "Ongoing Assurance", description: "Evidence maintained as practice, not revisited only at audit." },
];

/**
 * How an engagement actually moves from first contact to ongoing
 * assurance. Distinct from OperaDiagram, which describes the
 * methodology used within the "OPERA Delivery" stage specifically.
 */
export function EngagementLifecycle() {
  return (
    <ol className="grid grid-cols-1 gap-8 sm:grid-cols-5 sm:gap-4">
      {steps.map((step, index) => (
        <li key={step.name} className="relative border-t border-border pt-4">
          <span className="font-mono text-xs text-signal">{String(index + 1).padStart(2, "0")}</span>
          <p className="mt-2 font-serif text-base text-ink">{step.name}</p>
          <p className="mt-1 text-sm leading-relaxed text-muted">{step.description}</p>
        </li>
      ))}
    </ol>
  );
}
