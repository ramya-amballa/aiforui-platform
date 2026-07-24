import type { Metadata } from "next";
import Link from "next/link";
import { AdglLifecycleDiagram } from "@/components/sections/adgl-lifecycle";
import { CtaBand } from "@/components/sections/cta-band";
import { PageHero } from "@/components/sections/page-hero";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { SectionHeading } from "@/components/ui/section-heading";
import { JsonLd } from "@/components/seo/json-ld";
import { breadcrumbSchema, organizationSchema } from "@/components/seo/schema";
import {
  adglDeploymentAgnosticNote,
  adglDeploymentTypes,
  adglOperaRelationship,
  adglPhases,
  adglWhyItExists,
} from "@/content/adgl";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "ADGL: The AI Deployment Governance Lifecycle",
  description:
    "ADGL is AI for U&I's AI deployment governance framework and methodology: five phases for governing Microsoft Copilot, ChatGPT Enterprise, RAG, agentic AI and other AI deployments before production, and operationally afterward.",
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
        description="A practical methodology for governing AI before production."
      />

      {/* Large lifecycle diagram: the visual identity of ADGL */}
      <section className="py-section">
        <Container size="wide">
          <SectionHeading
            eyebrow="The Lifecycle"
            title="Discover, Assess, Govern, Deploy, Operate"
            description="Five phases, each answering one governance decision and producing named deliverables, from the business request that opens a deployment to the assurance evidence that outlasts it."
          />
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

      {/* The Five Phases: detailed breakdown with deliverables */}
      <section className="py-section">
        <Container size="wide">
          <SectionHeading
            eyebrow="Five Phases"
            title="What Each Phase Answers, and What It Produces"
            description="Every phase is a governance decision, not a checkbox: a specific question, a defined set of activities, and deliverables a board or regulator can actually review."
          />
          <div className="mt-12 grid grid-cols-1 gap-x-6 gap-y-12 sm:grid-cols-2 lg:grid-cols-5">
            {adglPhases.map((phase) => (
              <div key={phase.step} className="relative border-t-2 border-ink pt-8">
                <span className="absolute -top-3 left-0 flex h-6 w-6 items-center justify-center border border-accent bg-paper font-mono text-[10px] text-accent">
                  {String(phase.step).padStart(2, "0")}
                </span>
                <Badge tone="accent">Phase {phase.step}</Badge>
                <h3 className="mt-3 font-serif text-title text-ink">{phase.name}</h3>

                <p className="mt-6 text-eyebrow uppercase tracking-widest text-muted">Governance Question</p>
                <p className="mt-3 text-sm leading-relaxed text-ink">{phase.question}</p>

                <p className="mt-6 text-eyebrow uppercase tracking-widest text-muted">Activities</p>
                <ul className="mt-3 space-y-2">
                  {phase.activities.map((activity) => (
                    <li key={activity} className="text-sm leading-relaxed text-muted">
                      {activity}
                    </li>
                  ))}
                </ul>

                <p className="mt-6 text-eyebrow uppercase tracking-widest text-muted">Key Deliverables</p>
                <p className="mt-3 text-sm leading-relaxed text-muted">{phase.deliverables.join(", ")}</p>

                <p className="mt-6 border-t border-border pt-4 font-serif text-sm text-accent">{phase.outcome}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <Divider />

      {/* Typical AI Deployments Supported */}
      <section className="py-section-sm">
        <Container size="wide">
          <SectionHeading
            eyebrow="Deployment-Agnostic"
            title="Typical AI Deployments Supported"
            description={adglDeploymentAgnosticNote}
          />
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

      {/* Download Methodology */}
      <section className="py-section-sm">
        <Container size="narrow">
          <SectionHeading
            eyebrow="Methodology"
            title="Download the Full ADGL Methodology"
            description="The complete five-phase methodology, with governance questions, activities and deliverables for every phase, as a single reference document."
          />
          <div className="mt-8">
            <Button href="/downloads/adgl-methodology.pdf" target="_blank" rel="noopener noreferrer" variant="primary" size="lg">
              Download Methodology (PDF)
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
