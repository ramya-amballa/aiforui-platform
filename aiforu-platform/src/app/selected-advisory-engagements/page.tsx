import type { Metadata } from "next";
import Link from "next/link";
import { AdvisoryEngagementGrid } from "@/components/advisory/advisory-engagement-grid";
import { CtaBand } from "@/components/sections/cta-band";
import { EngagementLifecycle } from "@/components/sections/engagement-lifecycle";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { FilterPills } from "@/components/ui/filter-pills";
import { Pagination } from "@/components/ui/pagination";
import { advisoryEngagements } from "@/content/advisory-engagements";
import { buildMetadata } from "@/lib/metadata";
import { paginate, parseFilter, parsePage } from "@/lib/pagination";
import { site } from "@/lib/constants";
import type { EngagementTrack } from "@/types";

export const metadata: Metadata = buildMetadata({
  title: "Selected Engagement Areas",
  description:
    "Real methodology, approach and deliverables across AI governance, technology risk, cyber governance, third-party governance and government digital governance advisory work.",
  path: "/selected-advisory-engagements",
});

const tracks: EngagementTrack[] = ["Government", "Enterprise Advisory", "Strategic Programme"];

interface PageProps {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}

export default async function SelectedAdvisoryEngagementsPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const track = parseFilter(params, "track");
  const page = parsePage(params);

  const filtered = track ? advisoryEngagements.filter((engagement) => engagement.track === track) : advisoryEngagements;
  const { items, currentPage, totalPages } = paginate(filtered, page);

  return (
    <>
      <PageHero
        eyebrow="Selected Work"
        title="Selected Engagement Areas"
        description={`How ${site.advisorName} approaches an engagement and what it produces, across government, enterprise and strategic programmes.`}
      />
      <section className="py-section-sm">
        <Container size="wide">
          <EngagementLifecycle />
        </Container>
      </section>
      <Divider />
      <section className="py-section-sm">
        <Container size="wide">
          <FilterPills
            label="Track"
            filterKey="track"
            options={tracks.map((value) => ({ label: value, value }))}
            searchParams={params}
            basePath="/selected-advisory-engagements"
          />
          <div className="mt-10">
            <AdvisoryEngagementGrid engagements={items} />
          </div>
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            searchParams={params}
            basePath="/selected-advisory-engagements"
          />
          <p className="mt-10 border-t border-border pt-6 text-sm text-muted">
            For a single-document summary of these engagement areas,{" "}
            <Link href="/resources/executive-capability-overview" className="text-ink underline underline-offset-4 hover:text-accent">
              see the Executive Capability Overview
            </Link>
            .
          </p>
        </Container>
      </section>
      <CtaBand />
    </>
  );
}
