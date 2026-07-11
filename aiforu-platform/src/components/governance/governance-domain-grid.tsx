import { GovernanceDomainCard } from "@/components/governance/governance-domain-card";
import type { GovernanceDomain } from "@/types";

export function GovernanceDomainGrid({ domains }: { domains: GovernanceDomain[] }) {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {domains.map((domain) => (
        <GovernanceDomainCard key={domain.slug} domain={domain} />
      ))}
    </div>
  );
}
