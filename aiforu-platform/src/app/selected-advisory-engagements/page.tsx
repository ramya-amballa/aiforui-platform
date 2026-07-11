import type { Metadata } from "next";
import { AdvisoryEngagementGrid } from "@/components/advisory/advisory-engagement-grid";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { advisoryEngagements } from "@/content/advisory-engagements";
import { buildMetadata } from "@/lib/metadata";

export const metadata: Metadata = buildMetadata({
  title: "Selected Advisory Engagements",
  description: "[Selected Advisory Engagements — Meta Description Placeholder]",
  path: "/selected-advisory-engagements",
});

export default function SelectedAdvisoryEngagementsPage() {
  return (
    <>
      <PageHero
        eyebrow="Selected Work"
        title="Selected Advisory Engagements"
        description="[Selected Advisory Engagements — Page Description Placeholder]"
      />
      <section className="py-section-sm">
        <Container size="wide">
          <AdvisoryEngagementGrid engagements={advisoryEngagements} />
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
