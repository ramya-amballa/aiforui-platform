import type { Metadata } from "next";
import Link from "next/link";
import { AdvisoryEngagementGrid } from "@/components/advisory/advisory-engagement-grid";
import { ArticleGrid } from "@/components/article/article-grid";
import { GovernanceCapabilityMap } from "@/components/governance/governance-capability-map";
import { CtaBand } from "@/components/sections/cta-band";
import { CurrentPrioritiesSection } from "@/components/sections/current-priorities-section";
import { PointOfViewSection } from "@/components/sections/point-of-view-section";
import { JsonLd } from "@/components/seo/json-ld";
import { organizationSchema, personSchema } from "@/components/seo/schema";
import { FounderMark } from "@/components/sections/founder-mark";
import { OperaDiagram } from "@/components/sections/opera-diagram";
import { OperaHeroMark } from "@/components/sections/opera-hero-mark";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Eyebrow } from "@/components/ui/eyebrow";
import { SectionHeading } from "@/components/ui/section-heading";
import { advisoryEngagements } from "@/content/advisory-engagements";
import { currentPriorities } from "@/content/current-priorities";
import { getPointOfViewInsights, insights } from "@/content/insights";
import { buildMetadata } from "@/lib/metadata";
import { primaryCta, secondaryCta, site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "AIforU&I: Independent Advisory in AI and Technology Governance",
  description:
    "Independent advisory practice of Ramya Amballa, working across AI governance, digital governance, cyber governance, technology risk and third-party governance for regulated and high-assurance organisations.",
  path: "/",
});

export default function HomePage() {
  const featuredEngagements = advisoryEngagements.filter((engagement) => engagement.featured).slice(0, 3);
  const pointOfViewPieces = getPointOfViewInsights().filter((piece) => piece.featured).slice(0, 3);
  const featuredInsights = insights
    .filter((insight) => insight.featured && insight.format !== "Point of View")
    .slice(0, 3);

  return (
    <>
      <JsonLd data={personSchema()} />
      <JsonLd data={organizationSchema()} />

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border py-section-lg">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 -z-10 opacity-40"
          style={{
            backgroundImage:
              "linear-gradient(to right, hsl(var(--color-border)) 1px, transparent 1px), linear-gradient(to bottom, hsl(var(--color-border)) 1px, transparent 1px)",
            backgroundSize: "40px 40px",
            maskImage: "linear-gradient(to bottom, black, transparent)",
            WebkitMaskImage: "linear-gradient(to bottom, black, transparent)",
          }}
        />
        <Container size="wide">
          <div className="grid grid-cols-1 items-end gap-12 lg:grid-cols-12">
            <div className="lg:col-span-8">
              <Eyebrow>AI &amp; Digital Governance Advisory</Eyebrow>
              <h1 className="mt-6 max-w-4xl font-serif text-display-lg text-ink balance">
                Governance that holds up under audit, regulation and board scrutiny.
              </h1>
              <p className="mt-8 max-w-2xl text-lg leading-relaxed text-muted pretty">
                Independent advisory across AI governance, digital governance, cyber governance, technology
                risk and third-party governance, for boards, executives and public-sector leaders in regulated
                and high-assurance organisations.
              </p>
              <div className="mt-10 flex flex-wrap items-center gap-6">
                <Button href={primaryCta.href} variant="primary" size="lg">
                  {primaryCta.label}
                </Button>
                <Link href={secondaryCta.href} className="text-sm text-ink underline underline-offset-4 decoration-border hover:decoration-accent hover:text-accent">
                  {secondaryCta.label} &rarr;
                </Link>
              </div>
              <p className="mt-8 text-sm text-muted">
                An engagement with {site.name} means direct access to{" "}
                <Link href="/about" className="text-ink underline underline-offset-4 decoration-border hover:decoration-accent hover:text-accent">
                  Ramya Amballa
                </Link>
                , not a staffing pyramid.
              </p>
            </div>
            <div className="lg:col-span-4">
              <OperaHeroMark />
            </div>
          </div>
        </Container>
      </section>

      {/* Founder */}
      <section className="border-b border-border py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="lg:col-span-4">
              <FounderMark />
            </div>
            <div className="lg:col-span-7 lg:col-start-6">
              <Eyebrow>Founder</Eyebrow>
              <h2 className="mt-6 font-serif text-headline text-ink balance">{site.advisorName}</h2>
              <p className="mt-4 text-lg leading-relaxed text-ink pretty">
                Founder of {site.name} and creator of the OPERA methodology, built from work across AI
                governance, cyber governance, technology risk and third-party governance in regulated and
                high-assurance environments.
              </p>
              <Link href="/about" className="mt-6 inline-block text-sm text-accent underline underline-offset-4">
                Read the full profile &rarr;
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <CurrentPrioritiesSection snapshot={currentPriorities} />

      <PointOfViewSection pieces={pointOfViewPieces} />

      {/* Approach */}
      <section className="border-t border-border py-section">
        <Container size="wide">
          <SectionHeading
            eyebrow="Approach"
            title="The OPERA Methodology"
            description={`How ${site.advisorName} runs an engagement: five stages, from the real opportunity behind a decision to the assurance evidence that outlasts it.`}
          />
          <div className="mt-12">
            <OperaDiagram />
          </div>
        </Container>
      </section>

      {/* Governance domains: capability map */}
      <section className="border-t border-border py-section">
        <Container size="wide">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
            <SectionHeading
              eyebrow="Capability Map"
              title="Governance Domains"
              description={`Thirteen domains across four clusters, mapped from what ${site.advisorName} has advised on directly, each with a defined scope and the audience it serves.`}
            />
            <Button href="/governance-domains" variant="ghost">
              View the full map &rarr;
            </Button>
          </div>
          <div className="mt-12">
            <GovernanceCapabilityMap variant="compact" />
          </div>
        </Container>
      </section>

      {/* Selected engagement areas */}
      <section className="border-t border-border py-section">
        <Container size="wide">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
            <SectionHeading
              eyebrow="Selected Work"
              title="Selected Engagement Areas"
              description={`How ${site.advisorName} approaches an engagement and what it produces, from AI governance operating models to third-party governance frameworks.`}
            />
            <Button href="/selected-advisory-engagements" variant="ghost">
              View all engagement areas &rarr;
            </Button>
          </div>
          <div className="mt-12">
            <AdvisoryEngagementGrid engagements={featuredEngagements} />
          </div>
        </Container>
      </section>

      {/* Insights */}
      <section className="border-t border-border py-section">
        <Container size="wide">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
            <SectionHeading
              eyebrow="Perspective"
              title="Insights"
              description="Perspective on governance decisions, written for the people who have to make them."
            />
            <Button href="/insights" variant="ghost">
              View all insights &rarr;
            </Button>
          </div>
          <div className="mt-12">
            <ArticleGrid insights={featuredInsights} />
          </div>
        </Container>
      </section>

      <CtaBand
        title="Discuss a governance challenge"
        description="Most engagements begin with a working conversation about a specific governance, risk or AI oversight problem, not a formal proposal."
      />
    </>
  );
}
