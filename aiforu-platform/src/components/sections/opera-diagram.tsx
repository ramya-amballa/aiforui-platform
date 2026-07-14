const stages = [
  { letter: "O", name: "Opportunity", description: "Identify the actual use case and its business intent." },
  { letter: "P", name: "People", description: "Assign a named owner to every governance decision." },
  { letter: "E", name: "Evaluation", description: "Apply a consistent risk model, calibrated to impact." },
  { letter: "R", name: "Response", description: "Define escalation paths and approval gates." },
  { letter: "A", name: "Assurance", description: "Maintain the evidence trail as a matter of course." },
];

interface OperaDiagramProps {
  compact?: boolean;
}

/**
 * Visual summary of the OPERA methodology: five stages, one owner-facing
 * action each. Used in place of a prose explanation on the homepage and
 * About page.
 */
export function OperaDiagram({ compact = false }: OperaDiagramProps) {
  return (
    <div className="border-t border-border pt-8">
      <ol className="grid grid-cols-1 gap-8 sm:grid-cols-5 sm:gap-4">
        {stages.map((stage, index) => (
          <li key={stage.letter} className="relative">
            <div className="flex items-baseline gap-3 sm:block sm:gap-0">
              <span className="font-serif text-3xl text-accent">{stage.letter}</span>
              <p className="font-serif text-base text-ink sm:mt-3">{stage.name}</p>
            </div>
            {!compact && (
              <p className="mt-2 text-sm leading-relaxed text-muted">{stage.description}</p>
            )}
            {index < stages.length - 1 && (
              <span aria-hidden className="hidden sm:block absolute right-[-1rem] top-2 text-muted">
                &rarr;
              </span>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
