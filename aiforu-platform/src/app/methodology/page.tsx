import type { Metadata } from "next";
import { CtaBand } from "@/components/sections/cta-band";
import { GovernanceWorkflow } from "@/components/sections/governance-workflow";
import { PageHero } from "@/components/sections/page-hero";
import { Badge } from "@/components/ui/badge";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { SectionHeading } from "@/components/ui/section-heading";
import { operaDesignedFor, operaStages, operaWhyItExists } from "@/content/opera";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "The OPERA Methodology",
  description: operaWhyItExists,
  path: "/methodology",
});

export default function MethodologyPage() {
  return (
    <>
      <PageHero
        eyebrow="Methodology"
        title="The OPERA Methodology"
        description={`How ${site.advisorName} turns AI and technology governance requirements into operational decisions, at every ${site.name} engagement.`}
      />

      <section className="py-section-sm">
        <Container size="narrow">
          <blockquote className="border-l-2 border-accent pl-6 text-lg leading-relaxed text-ink pretty">
            {operaWhyItExists}
          </blockquote>
          <p className="mt-6 text-sm leading-relaxed text-muted pretty">
            OPERA is not a framework for sale or a certification standard. It is the working method {site.advisorName}{" "}
            built from advising on AI, digital, cyber and technology risk governance, and the structure behind
            every engagement she runs.
          </p>
        </Container>
      </section>

      <Divider />

      <section className="py-section">
        <Container size="wide">
          <SectionHeading
            eyebrow="Five Stages"
            title="Opportunity, People, Evaluation, Response, Assurance"
            description="Each stage answers a specific governance decision, produces named artefacts, and delivers one business outcome."
          />
          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-5">
            {operaStages.map((stage) => (
              <div key={stage.letter} className="border border-border p-6">
                <div className="flex items-center justify-between">
                  <span className="font-serif text-3xl text-accent">{stage.letter}</span>
                  <Badge tone="accent">Stage {operaStages.indexOf(stage) + 1}</Badge>
                </div>
                <h3 className="mt-3 font-serif text-title text-ink">{stage.name}</h3>

                <p className="mt-6 text-eyebrow uppercase tracking-widest text-muted">Governance Decision</p>
                <ul className="mt-3 space-y-2">
                  {stage.questions.map((question) => (
                    <li key={question} className="text-sm leading-relaxed text-ink">
                      {question}
                    </li>
                  ))}
                </ul>

                <p className="mt-6 text-eyebrow uppercase tracking-widest text-muted">Activities</p>
                <ul className="mt-3 space-y-2">
                  {stage.activities.map((activity) => (
                    <li key={activity} className="text-sm leading-relaxed text-muted">
                      {activity}
                    </li>
                  ))}
                </ul>

                <p className="mt-6 text-eyebrow uppercase tracking-widest text-muted">Produces</p>
                <p className="mt-3 text-sm leading-relaxed text-muted">{stage.artefacts.join(", ")}</p>

                <p className="mt-6 border-t border-border pt-4 font-serif text-sm text-accent">{stage.outcome}</p>
              </div>
            ))}
          </div>
        </Container>
      </section>

      <Divider />

      <section className="py-section">
        <Container size="wide">
          <SectionHeading
            eyebrow="Operational Workflow"
            title="From AI Governance Requirements to Operational Decisions"
            description="How a single AI use case actually moves through OPERA, from submission to evidence and assurance."
          />
          <div className="mt-12">
            <GovernanceWorkflow />
          </div>
        </Container>
      </section>

      <Divider />

      <section className="py-section-sm">
        <Container size="narrow">
          <p className="text-sm leading-relaxed text-muted">{operaDesignedFor}</p>
          <p className="mt-2 text-sm leading-relaxed text-muted">
            OPERA is developed and run by {site.advisorName}. Engaging {site.name} means engaging the person who
            built it, not a team applying it on her behalf.
          </p>
        </Container>
      </section>

      <CtaBand
        title="Apply OPERA to a real governance decision"
        description="See how the methodology maps to a specific engagement area, or start a conversation about your own use case."
      />
    </>
  );
}
