import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { AdvisoryEngagementDetail } from "@/components/advisory/advisory-engagement-detail";
import { CtaBand } from "@/components/sections/cta-band";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { advisoryEngagements, getAdvisoryEngagementBySlug } from "@/content/advisory-engagements";
import { governanceDomains } from "@/content/governance-domains";
import { buildMetadata } from "@/lib/metadata";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return advisoryEngagements.map((engagement) => ({ slug: engagement.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const engagement = getAdvisoryEngagementBySlug(slug);
  if (!engagement) return buildMetadata({ title: "Engagement Not Found", noIndex: true });

  return buildMetadata({
    title: engagement.title,
    description: engagement.summary,
    path: `/selected-advisory-engagements/${engagement.slug}`,
  });
}

export default async function AdvisoryEngagementPage({ params }: PageProps) {
  const { slug } = await params;
  const engagement = getAdvisoryEngagementBySlug(slug);
  if (!engagement) notFound();

  const relatedDomains = governanceDomains.filter((domain) => engagement.domainSlugs.includes(domain.slug));

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "Selected Advisory Engagements", href: "/selected-advisory-engagements" },
          { label: engagement.title, href: `/selected-advisory-engagements/${engagement.slug}` },
        ]}
      />
      <AdvisoryEngagementDetail engagement={engagement} relatedDomains={relatedDomains} />
      <CtaBand />
    </>
  );
}
