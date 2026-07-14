import type { Metadata } from "next";
import { ArticleGrid } from "@/components/article/article-grid";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { FilterPills } from "@/components/ui/filter-pills";
import { Pagination } from "@/components/ui/pagination";
import { insights } from "@/content/insights";
import { buildMetadata } from "@/lib/metadata";
import { paginate, parseFilter, parsePage } from "@/lib/pagination";
import type { InsightFormat } from "@/types";

export const metadata: Metadata = buildMetadata({
  title: "Insights",
  description: "Original perspective on AI governance, technology risk and third-party governance decisions, from working advisory practice.",
  path: "/insights",
});

const formats: InsightFormat[] = ["Point of View", "Governance Note", "Briefing", "Field Note"];

interface PageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function InsightsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const format = parseFilter(params, "format");
  const page = parsePage(params);

  const filtered = format ? insights.filter((insight) => insight.format === format) : insights;
  const { items, currentPage, totalPages } = paginate(filtered, page);

  return (
    <>
      <PageHero
        eyebrow="Perspective"
        title="Insights"
        description="A perspective library: original thinking, governance notes and field observations from live advisory work, not a news feed."
      />
      <section className="py-section-sm">
        <Container size="wide">
          <FilterPills
            label="Format"
            filterKey="format"
            options={formats.map((value) => ({ label: value, value }))}
            searchParams={params}
            basePath="/insights"
          />
          <div className="mt-10">
            <ArticleGrid insights={items} />
          </div>
          <Pagination currentPage={currentPage} totalPages={totalPages} searchParams={params} basePath="/insights" />
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
