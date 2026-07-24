import type { Metadata } from "next";
import Link from "next/link";
import { AdglDeliverables } from "@/components/sections/adgl-deliverables";
import { AdglLifecycleDiagram } from "@/components/sections/adgl-lifecycle";
import { AdglPhaseAccordion } from "@/components/sections/adgl-phase-accordion";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { SectionHeading } from "@/components/ui/section-heading";
import { JsonLd } from "@/components/seo/json-ld";
import { breadcrumbSchema, organizationSchema } from "@/components/seo/schema";
import { adglDeploymentAgnosticNote, adglDeploymentTypes, adglOperaRelationship, adglWhyItExists } from "@/content/adgl";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "ADGL: The AI Deployment Governance Lifecycle",
  description:
    "ADGL is AI for U&I's AI deployment governance framework: five phases for governing Microsoft Copilot, ChatGPT Enterprise, RAG, agentic AI and other AI deployments before production, and operationally afterward.",
  path: "/adgl",
});

export default function AdglPage() {
  return (
    <>
      <JsonLd data={organizationSchema()} />
      <JsonLd
        data={breadcrumbSchema([
          { name: "Home", path: "/" },
          { name: "ADGL", path: "/adgl" },
        ])}
      />

      <PageHero
        eyebrow="ADGL"
        title="AI Deployment Governance Lifecycle (ADGL)"
        description="A practical governance methodology for taking AI safely from business approval to production deployment."
      />

      {/* The Lifecycle: name and one line per phase, nothing else. Detail lives in the accordion below. */}
      <section className="py-section-sm">
        <Container size="wide">
          <SectionHeading eyebrow="The Lifecycle" title="Discover, Assess, Govern, Deploy, Operate" />
          <div className="mt-14">
            <AdglLifecycleDiagram />
          </div>
        </Container>
      </section>

      <Divider />

      {/* Why ADGL Exists */}
      <section className="py-section-sm">
        <Container size="narrow">
          <p className="text-eyebrow uppercase tracking-widest text-accent">Why ADGL Exists</p>
          <blockquote className="mt-4 border-l-2 border-accent pl-6 text-lg leading-relaxed text-ink pretty">
            {adglWhyItExists}
          </blockquote>
        </Container>
      </section>

      <Divider />

      {/* Five Phases: collapsed by default, one phase's detail visible at a time */}
      <section className="py-section-sm">
        <Container size="wide">
          <SectionHeading eyebrow="Five Phases" title="Explore Each Phase" description="Click a phase for its governance question, activities and gate." />
          <div className="mt-10">
            <AdglPhaseAccordion />
          </div>
        </Container>
      </section>

      <Divider />

      {/* Typical AI Deployments Supported */}
      <section className="py-section-sm">
        <Container size="wide">
          <SectionHeading eyebrow="Deployment-Agnostic" title="Supported Deployments" description={adglDeploymentAgnosticNote} />
          <ul className="mt-8 grid grid-cols-1 gap-x-10 gap-y-3 border-t border-border pt-6 sm:grid-cols-2 lg:grid-cols-4">
            {adglDeploymentTypes.map((deployment) => (
              <li key={deployment.name} className="flex items-baseline gap-3 text-sm text-ink">
                <span aria-hidden className="block h-1 w-1 shrink-0 rounded-full bg-accent" />
                {deployment.name}
              </li>
            ))}
          </ul>
        </Container>
      </section>

      <Divider />

      {/* Deliverables: a count per phase, full list one click away */}
      <section className="py-section-sm">
        <Container size="wide">
          <SectionHeading eyebrow="Deliverables" title="What You Walk Away With" />
          <div className="mt-10">
            <AdglDeliverables />
          </div>
        </Container>
      </section>

      <Divider />

      {/* Get the framework */}
      <section className="py-section-sm">
        <Container size="narrow">
          <SectionHeading
            eyebrow="Get ADGL"
            title="Download the ADGL Framework"
            description="Five phases, eighteen operational controls, risk scoring, RACI and a twelve-week delivery schedule, in one reference document."
          />
          <div className="mt-8">
            <Button href="/downloads/adgl-methodology.pdf" target="_blank" rel="noopener noreferrer" variant="primary" size="lg">
              Download ADGL Framework
            </Button>
          </div>
        </Container>
      </section>

      <Divider />

      {/* Relationship to OPERA */}
      <section className="py-section-sm">
        <Container size="narrow">
          <p className="text-eyebrow uppercase tracking-widest text-accent">ADGL and OPERA</p>
          <p className="mt-4 text-sm leading-relaxed text-muted pretty">{adglOperaRelationship}</p>
          <Link href="/methodology" className="mt-4 inline-block text-sm text-accent underline underline-offset-4">
            See the OPERA methodology &rarr;
          </Link>
        </Container>
      </section>

      <CtaBand
        title="Deploying AI?"
        description={`Let's build governance before production. Start a working conversation about a specific AI deployment with ${site.advisorName}.`}
      />
    </>
  );
}
