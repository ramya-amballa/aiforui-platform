import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { ResourceDetail } from "@/components/resource/resource-detail";
import { BackLink } from "@/components/ui/back-link";
import { getResourceBySlug, resources } from "@/content/resources";
import { buildMetadata } from "@/lib/metadata";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  // "opera-executive-guide" has its own bespoke route (app/resources/opera-executive-guide/page.tsx),
  // which a static segment always takes precedence over; excluded here to avoid generating an
  // unreachable duplicate via this dynamic template.
  return resources.filter((resource) => resource.slug !== "opera-executive-guide").map((resource) => ({ slug: resource.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const resource = getResourceBySlug(slug);
  if (!resource) return buildMetadata({ title: "Resource Not Found", noIndex: true });

  return buildMetadata({
    title: resource.title,
    description: resource.description,
    path: `/resources/${resource.slug}`,
  });
}

export default async function ResourcePage({ params }: PageProps) {
  const { slug } = await params;
  const resource = getResourceBySlug(slug);
  if (!resource) notFound();

  return (
    <>
      <Breadcrumbs
        items={[
          { label: "Resources", href: "/resources" },
          { label: resource.title, href: `/resources/${resource.slug}` },
        ]}
      />
      <ResourceDetail resource={resource} />
      <BackLink href="/resources" label="All Resources" />
    </>
  );
}
