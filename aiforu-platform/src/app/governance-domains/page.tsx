import type { Metadata } from "next";
import { GovernanceCapabilityMap } from "@/components/governance/governance-capability-map";
import { CtaBand } from "@/components/sections/cta-band";
import { MaturityScale } from "@/components/sections/maturity-scale";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { SectionHeading } from "@/components/ui/section-heading";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

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
        description={`Where ${site.advisorName} advises, grouped by cluster: emerging technology, risk and cyber, regulatory and third-party, and public sector governance.`}
      />
      <section className="py-section-sm">
        <Container size="wide">
          <SectionHeading eyebrow="Assessment" title="How Domain Maturity Is Assessed" />
          <div className="mt-10">
            <MaturityScale />
          </div>
        </Container>
      </section>
      <Divider />
      <section className="py-section-sm">
        <Container size="wide">
          <GovernanceCapabilityMap variant="full" />
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
