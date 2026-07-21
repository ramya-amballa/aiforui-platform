import type { Metadata } from "next";
import Link from "next/link";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";
import { CtaBand } from "@/components/sections/cta-band";
import { EngagementLifecycle } from "@/components/sections/engagement-lifecycle";
import { GovernanceWorkflow } from "@/components/sections/governance-workflow";
import { OperaDiagram } from "@/components/sections/opera-diagram";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { getResourceBySlug } from "@/content/resources";
import { governanceWorkflowOutcomes, operaStages } from "@/content/opera";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

const guide = getResourceBySlug("opera-executive-guide")!;

export const metadata: Metadata = buildMetadata({
  title: guide.title,
  description: guide.description,
  path: "/resources/opera-executive-guide",
});

const capabilities = ["AI Governance", "Digital Governance", "Cyber Governance", "Technology Risk", "Third-Party Governance"];

const deliverables = [
  "Governance Charter",
  "Operating Model",
  "RACI Matrix",
  "Risk Register",
  "Evidence Register",
  "Decision Framework",
  "Implementation Roadmap",
  "Board Reporting Pack",
];

const businessOutcomes = Array.from(new Set([...operaStages.map((stage) => stage.outcome), ...governanceWorkflowOutcomes]));

const frameworkAlignment = ["NIST AI RMF", "EU AI Act", "ISO 42001", "ISO 27001", "Technology Risk", "Third-Party Risk"];

const engagementModel = [
  "Starts with a working conversation about a specific problem, not a scoping questionnaire",
  "Run using the OPERA methodology, scaled to what the organisation needs rather than applied wholesale",
  "Sized to fit: a focused advisory engagement, an operating model redesign, or a longer programme",
  "Ends with something the organisation owns and can run without outside help: an operating model, not a report that sits on a shelf",
];

export default function OperaExecutiveGuidePage() {
  return (
    <>
      <Breadcrumbs items={[{ label: "Resources", href: "/resources" }, { label: guide.title, href: "/resources/opera-executive-guide" }]} />

      <PageHero eyebrow="Executive Guide" title="Explore the OPERA Executive Guide" description={guide.description} />

      {/* Coming soon notice */}
      <section className="border-b border-border bg-surface py-section-sm">
        <Container size="narrow">
          <p className="text-eyebrow uppercase tracking-widest text-muted">Executive Guide (PDF)</p>
          <p className="mt-4 text-base leading-relaxed text-ink pretty">
            The downloadable OPERA Executive Guide is currently being finalised and will be available shortly.
          </p>
          <p className="mt-2 text-base leading-relaxed text-muted pretty">
            In the meantime, this page previews what it covers.
          </p>
        </Container>
      </section>

      {/* 1. Why governance programmes fail */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Why AI Governance Programmes Fail</h2>
          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            Governance programmes rarely fail from a missing framework. They fail because ownership was
            assumed rather than assigned, evidence was produced after the fact rather than maintained, and
            controls were tested on paper but not in the environment where they actually operate.
          </p>
        </Container>
      </section>

      <Divider />

      {/* 2. Why OPERA exists */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Why OPERA Exists</h2>
          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            OPERA exists because most governance frameworks describe intent well and operations poorly. It
            sequences five decisions, from the opportunity behind a requirement to the assurance evidence that
            outlasts it, developed from running this kind of programme inside four regulated environments
            before it had a name.
          </p>
        </Container>
      </section>

      <Divider />

      {/* 3. The OPERA methodology */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">The OPERA Methodology</h2>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted pretty">
            Five stages, from the real opportunity behind a decision to the assurance evidence that outlasts
            it.
          </p>
          <div className="mt-10">
            <OperaDiagram showLink={false} />
          </div>
          <Link href="/methodology" className="mt-8 inline-block text-sm text-accent underline underline-offset-4">
            View the full methodology &rarr;
          </Link>
        </Container>
      </section>

      <Divider />

      {/* 4. Governance workflow preview */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">Governance Workflow Preview</h2>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted pretty">
            How a single AI use case actually moves through OPERA, from submission to evidence and assurance.
          </p>
          <div className="mt-10">
            <GovernanceWorkflow />
          </div>
        </Container>
      </section>

      <Divider />

      {/* 5. Implementation map preview */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">Implementation Map Preview</h2>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted pretty">
            How an engagement actually moves from first contact to ongoing assurance.
          </p>
          <div className="mt-10">
            <EngagementLifecycle />
          </div>
        </Container>
      </section>

      <Divider />

      {/* 6. Governance deliverables */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Governance Deliverables</h2>
          <ul className="mt-6 flex flex-wrap gap-x-6 gap-y-2 border-t border-border pt-6">
            {deliverables.map((item) => (
              <li key={item} className="text-sm text-ink">
                {item}
              </li>
            ))}
          </ul>
        </Container>
      </section>

      <Divider />

      {/* 7. Business outcomes */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Business Outcomes</h2>
          <ul className="mt-6 flex flex-wrap gap-x-6 gap-y-2 border-t border-border pt-6">
            {businessOutcomes.map((item) => (
              <li key={item} className="text-sm text-ink">
                {item}
              </li>
            ))}
          </ul>
        </Container>
      </section>

      <Divider />

      {/* 8. Framework alignment */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Framework Alignment</h2>
          <p className="mt-6 text-sm text-muted">{frameworkAlignment.join(", ")}</p>
        </Container>
      </section>

      <Divider />

      {/* 9. Advisory services */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Advisory Services</h2>
          <ul className="mt-6 flex flex-wrap gap-x-6 gap-y-2 border-t border-border pt-6">
            {capabilities.map((item) => (
              <li key={item} className="text-sm text-ink">
                {item}
              </li>
            ))}
          </ul>
        </Container>
      </section>

      <Divider />

      {/* 10. About Ramya Amballa */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">About {site.advisorName}</h2>
          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            {site.advisorName} spent thirteen years inside the governance, risk and audit functions of PwC,
            Wells Fargo, JPMorgan Chase and Viatris, running enterprise technology risk, cyber risk, GRC,
            third-party risk and audit readiness programmes before founding {site.name}.
          </p>
          <Link href="/about" className="mt-4 inline-block text-sm text-accent underline underline-offset-4">
            Read the full profile &rarr;
          </Link>
        </Container>
      </section>

      <Divider />

      {/* 11. How to engage */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">How to Engage</h2>
          <ul className="mt-6 space-y-3">
            {engagementModel.map((item) => (
              <li key={item} className="flex gap-3 text-base leading-relaxed text-ink">
                <span aria-hidden className="mt-2.5 block h-1 w-1 shrink-0 rounded-full bg-accent" />
                {item}
              </li>
            ))}
          </ul>
        </Container>
      </section>

      <CtaBand />
    </>
  );
}
