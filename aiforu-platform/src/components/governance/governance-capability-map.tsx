import Link from "next/link";
import { GovernanceDomainGrid } from "@/components/governance/governance-domain-grid";
import { governanceClusters } from "@/content/governance-clusters";
import { governanceDomains } from "@/content/governance-domains";

interface GovernanceCapabilityMapProps {
  variant?: "compact" | "full";
}

/**
 * Renders the domain taxonomy grouped by cluster. `compact` (used on
 * the homepage) is a text index: four columns of links, no cards,
 * so thirteen domains read as a structured map rather than a wall of
 * tiles. `full` (used on /governance-domains) renders each cluster as
 * a heading followed by the standard domain card grid.
 */
export function GovernanceCapabilityMap({ variant = "full" }: GovernanceCapabilityMapProps) {
  if (variant === "compact") {
    return (
      <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4">
        {governanceClusters.map((cluster) => {
          const domains = governanceDomains.filter((domain) => domain.cluster === cluster.id);
          return (
            <div key={cluster.id}>
              <p className="text-eyebrow uppercase tracking-widest text-muted">{cluster.name}</p>
              <ul className="mt-4 space-y-2.5">
                {domains.map((domain) => (
                  <li key={domain.slug}>
                    <Link href={`/governance-domains/${domain.slug}`} className="text-sm text-ink hover:text-accent">
                      {domain.shortName}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="space-y-16">
      {governanceClusters.map((cluster) => {
        const domains = governanceDomains.filter((domain) => domain.cluster === cluster.id);
        if (domains.length === 0) return null;

        return (
          <div key={cluster.id}>
            <div className="max-w-2xl border-b border-border pb-6">
              <h2 className="font-serif text-title text-ink">{cluster.name}</h2>
              <p className="mt-2 text-sm text-muted">{cluster.description}</p>
            </div>
            <div className="mt-8">
              <GovernanceDomainGrid domains={domains} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
