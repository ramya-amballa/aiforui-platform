import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ArticleDetail } from "@/components/article/article-detail";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { CtaBand } from "@/components/sections/cta-band";
import { JsonLd } from "@/components/seo/json-ld";
import { articleSchema } from "@/components/seo/schema";
import { getInsightBySlug, insights } from "@/content/insights";
import { buildMetadata } from "@/lib/metadata";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return insights.map((insight) => ({ slug: insight.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const insight = getInsightBySlug(slug);
  if (!insight) return buildMetadata({ title: "Insight Not Found", noIndex: true });

  return buildMetadata({
    title: insight.title,
    description: insight.excerpt,
    path: `/insights/${insight.slug}`,
    type: "article",
  });
}

export default async function InsightPage({ params }: PageProps) {
  const { slug } = await params;
  const insight = getInsightBySlug(slug);
  if (!insight) notFound();

  return (
    <>
      <JsonLd
        data={articleSchema({
          title: insight.title,
          description: insight.excerpt,
          path: `/insights/${insight.slug}`,
          datePublished: insight.date,
        })}
      />
      <Breadcrumbs
        items={[
          { label: "Insights", href: "/insights" },
          { label: insight.title, href: `/insights/${insight.slug}` },
        ]}
      />
      <ArticleDetail insight={insight} />
      <CtaBand />
    </>
  );
}
