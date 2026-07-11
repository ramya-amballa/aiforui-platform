import type { Metadata } from "next";
import { ArticleGrid } from "@/components/article/article-grid";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { insights } from "@/content/insights";
import { buildMetadata } from "@/lib/metadata";

export const metadata: Metadata = buildMetadata({
  title: "Insights",
  description: "[Insights — Meta Description Placeholder]",
  path: "/insights",
});

export default function InsightsPage() {
  return (
    <>
      <PageHero eyebrow="Perspective" title="Insights" description="[Insights — Page Description Placeholder]" />
      <section className="py-section-sm">
        <Container size="wide">
          <ArticleGrid insights={insights} />
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
