import type { Metadata } from "next";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { FilterPills } from "@/components/ui/filter-pills";
import { Pagination } from "@/components/ui/pagination";
import { ResourceGrid } from "@/components/resource/resource-grid";
import { resources } from "@/content/resources";
import { buildMetadata } from "@/lib/metadata";
import { paginate, parseFilter, parsePage } from "@/lib/pagination";
import type { ResourceAccessTier, ResourceType } from "@/types";

export const metadata: Metadata = buildMetadata({
  title: "Resources",
  description: "Frameworks, playbooks, checklists, reference architectures and toolkits for AI governance, technology risk, cyber governance and third-party governance.",
  path: "/resources",
});

const types: ResourceType[] = [
  "Framework",
  "Checklist",
  "Whitepaper",
  "Template",
  "Briefing",
  "Playbook",
  "Reference Architecture",
  "Toolkit",
];
const tiers: ResourceAccessTier[] = ["Free", "Premium"];

interface PageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function ResourcesPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const type = parseFilter(params, "type");
  const tier = parseFilter(params, "tier");
  const page = parsePage(params);

  const filtered = resources.filter((resource) => {
    if (type && resource.type !== type) return false;
    if (tier && resource.accessTier !== tier) return false;
    return true;
  });
  const { items, currentPage, totalPages } = paginate(filtered, page);

  return (
    <>
      <PageHero
        eyebrow="Practitioner Resources"
        title="Resources"
        description="Frameworks, playbooks, checklists, reference architectures and toolkits, published as the practice develops them."
      />
      <section className="py-section-sm">
        <Container size="wide">
          <div className="space-y-4">
            <FilterPills
              label="Type"
              filterKey="type"
              options={types.map((value) => ({ label: value, value }))}
              searchParams={params}
              basePath="/resources"
            />
            <FilterPills
              label="Access"
              filterKey="tier"
              options={tiers.map((value) => ({ label: value, value }))}
              searchParams={params}
              basePath="/resources"
            />
          </div>
          <div className="mt-10">
            <ResourceGrid resources={items} />
          </div>
          <Pagination currentPage={currentPage} totalPages={totalPages} searchParams={params} basePath="/resources" />
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
