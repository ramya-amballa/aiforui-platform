import type { Metadata } from "next";
import { GovernanceCapabilityMap } from "@/components/governance/governance-capability-map";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { buildMetadata } from "@/lib/metadata";

export const metadata: Metadata = buildMetadata({
  title: "Governance Domains",
  description: "Thirteen governance domains across four clusters: emerging technology, risk and cyber, regulatory and third-party, and public sector governance.",
  path: "/governance-domains",
});

export default function GovernanceDomainsPage() {
  return (
    <>
      <PageHero
        eyebrow="Capability Map"
        title="Governance Domains"
        description="A structured map of the practice, grouped by cluster, so the taxonomy can grow without a redesign."
      />
      <section className="py-section-sm">
        <Container size="wide">
          <GovernanceCapabilityMap variant="full" />
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
