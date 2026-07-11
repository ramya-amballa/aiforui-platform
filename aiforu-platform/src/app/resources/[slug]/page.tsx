import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { ResourceDetail } from "@/components/resource/resource-detail";
import { CtaBand } from "@/components/sections/cta-band";
import { getResourceBySlug, resources } from "@/content/resources";
import { buildMetadata } from "@/lib/metadata";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export function generateStaticParams() {
  return resources.map((resource) => ({ slug: resource.slug }));
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
      <CtaBand />
    </>
  );
}
