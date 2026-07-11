import type { Metadata } from "next";
import { GovernanceDomainGrid } from "@/components/governance/governance-domain-grid";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { governanceDomains } from "@/content/governance-domains";
import { buildMetadata } from "@/lib/metadata";

export const metadata: Metadata = buildMetadata({
  title: "Governance Domains",
  description: "[Governance Domains — Meta Description Placeholder]",
  path: "/governance-domains",
});

export default function GovernanceDomainsPage() {
  return (
    <>
      <PageHero
        eyebrow="Areas of Practice"
        title="Governance Domains"
        description="[Governance Domains — Page Description Placeholder]"
      />
      <section className="py-section-sm">
        <Container size="wide">
          <GovernanceDomainGrid domains={governanceDomains} />
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
