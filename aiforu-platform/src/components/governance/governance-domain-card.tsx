import { Card, CardDescription, CardEyebrow, CardTitle } from "@/components/ui/card";
import type { GovernanceDomain } from "@/types";

export function GovernanceDomainCard({ domain }: { domain: GovernanceDomain }) {
  return (
    <Card href={`/governance-domains/${domain.slug}`}>
      <CardEyebrow>{domain.eyebrow}</CardEyebrow>
      <CardTitle>{domain.name}</CardTitle>
      <CardDescription>{domain.summary}</CardDescription>
    </Card>
  );
}
