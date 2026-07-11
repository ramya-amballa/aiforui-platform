import type { Metadata } from "next";
import Link from "next/link";
import { AdvisoryEngagementGrid } from "@/components/advisory/advisory-engagement-grid";
import { ArticleGrid } from "@/components/article/article-grid";
import { GovernanceDomainGrid } from "@/components/governance/governance-domain-grid";
import { CtaBand } from "@/components/sections/cta-band";
import { JsonLd } from "@/components/seo/json-ld";
import { organizationSchema, personSchema } from "@/components/seo/schema";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Eyebrow } from "@/components/ui/eyebrow";
import { Placeholder } from "@/components/ui/placeholder";
import { SectionHeading } from "@/components/ui/section-heading";
import { advisoryEngagements } from "@/content/advisory-engagements";
import { governanceDomains } from "@/content/governance-domains";
import { insights } from "@/content/insights";
import { buildMetadata } from "@/lib/metadata";
import { primaryCta, secondaryCta } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "[Homepage Title Placeholder]",
  description: "[Homepage Meta Description Placeholder]",
  path: "/",
});

const positioningStatements = [
  "Independent Advisory",
  "Digital Governance",
  "AI Governance",
  "Cyber Governance",
  "Technology Risk",
  "Third Party Governance",
  "Privacy & Data Governance",
  "DPDP Governance & Readiness",
  "Government Digital Governance",
  "Governance Transformation",
];

export default function HomePage() {
  const featuredEngagements = advisoryEngagements.filter((engagement) => engagement.featured).slice(0, 3);
  const featuredDomains = governanceDomains.filter((domain) => domain.featured).slice(0, 6);
  const featuredInsights = insights.filter((insight) => insight.featured).slice(0, 3);

  return (
    <>
      <JsonLd data={personSchema()} />
      <JsonLd data={organizationSchema()} />

      {/* Hero */}
      <section className="border-b border-border py-section-lg">
        <Container size="wide">
          <div className="grid grid-cols-1 items-end gap-12 lg:grid-cols-12">
            <div className="lg:col-span-8">
              <Eyebrow>Independent Advisory</Eyebrow>
              <h1 className="mt-6 max-w-4xl font-serif text-display-lg text-ink balance">
                [Hero Title Placeholder]
              </h1>
              <p className="mt-8 max-w-2xl text-lg leading-relaxed text-muted pretty">
                [Executive Introduction Placeholder — one to two sentences establishing independent advisory
                positioning across governance, risk and technology.]
              </p>
              <div className="mt-10 flex flex-col gap-4 sm:flex-row">
                <Button href={primaryCta.href} variant="primary" size="lg">
                  {primaryCta.label}
                </Button>
                <Button href={secondaryCta.href} variant="secondary" size="lg">
                  {secondaryCta.label}
                </Button>
              </div>
            </div>
            <div className="lg:col-span-4">
              <Placeholder label="Executive Portrait Placeholder" aspect="portrait" />
            </div>
          </div>
        </Container>
      </section>

      {/* Positioning strip */}
      <section className="border-b border-border py-8">
        <Container size="wide">
          <ul className="flex flex-wrap gap-x-8 gap-y-3 text-sm text-muted">
            {positioningStatements.map((item) => (
              <li key={item} className="whitespace-nowrap">
                {item}
              </li>
            ))}
          </ul>
        </Container>
      </section>

      {/* Executive introduction */}
      <section className="py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="lg:col-span-4">
              <SectionHeading eyebrow="About Ramya" title="[Executive Introduction Heading Placeholder]" />
            </div>
            <div className="lg:col-span-7 lg:col-start-6">
              <p className="text-lg leading-relaxed text-ink pretty">[Executive Biography Paragraph Placeholder 1]</p>
              <p className="mt-6 text-base leading-relaxed text-muted pretty">
                [Executive Biography Paragraph Placeholder 2]
              </p>
              <Link href="/about" className="mt-6 inline-block text-sm text-accent underline underline-offset-4">
                [Read Full Profile Placeholder]
              </Link>
            </div>
          </div>
        </Container>
      </section>

      {/* Selected advisory engagements */}
      <section className="border-t border-border py-section">
        <Container size="wide">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
            <SectionHeading
              eyebrow="Selected Work"
              title="Selected Advisory Engagements"
              description="[Selected Advisory Engagements Section Description Placeholder]"
            />
            <Button href="/selected-advisory-engagements" variant="ghost">
              View all engagements &rarr;
            </Button>
          </div>
          <div className="mt-12">
            <AdvisoryEngagementGrid engagements={featuredEngagements} />
          </div>
        </Container>
      </section>

      {/* Governance domains */}
      <section className="border-t border-border py-section">
        <Container size="wide">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
            <SectionHeading
              eyebrow="Areas of Practice"
              title="Governance Domains"
              description="[Governance Domains Section Description Placeholder]"
            />
            <Button href="/governance-domains" variant="ghost">
              View all domains &rarr;
            </Button>
          </div>
          <div className="mt-12">
            <GovernanceDomainGrid domains={featuredDomains} />
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
              description="[Insights Section Description Placeholder]"
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
        title="[Homepage Closing CTA Title Placeholder]"
        description="[Homepage Closing CTA Description Placeholder]"
      />
    </>
  );
}
