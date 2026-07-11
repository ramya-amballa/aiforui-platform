import type { Metadata } from "next";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { ResourceGrid } from "@/components/resource/resource-grid";
import { resources } from "@/content/resources";
import { buildMetadata } from "@/lib/metadata";

export const metadata: Metadata = buildMetadata({
  title: "Resources",
  description: "[Resources — Meta Description Placeholder]",
  path: "/resources",
});

export default function ResourcesPage() {
  return (
    <>
      <PageHero eyebrow="Practitioner Resources" title="Resources" description="[Resources — Page Description Placeholder]" />
      <section className="py-section-sm">
        <Container size="wide">
          <ResourceGrid resources={resources} />
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
