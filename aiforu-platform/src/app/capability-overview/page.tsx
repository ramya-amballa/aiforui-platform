import type { Metadata } from "next";
import Link from "next/link";
import { CtaBand } from "@/components/sections/cta-band";
import { OperaDiagram } from "@/components/sections/opera-diagram";
import { PageHero } from "@/components/sections/page-hero";
import { JsonLd } from "@/components/seo/json-ld";
import { organizationSchema, personSchema } from "@/components/seo/schema";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { advisoryEngagements } from "@/content/advisory-engagements";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "Executive Capability Overview",
  description:
    "An executive overview of AI for U&I's advisory capabilities, the OPERA methodology, representative engagement areas and the practitioner behind the practice.",
  path: "/capability-overview",
});

const capabilities = ["AI Governance", "Digital Governance", "Cyber Governance", "Technology Risk", "Third-Party Governance"];

const industries = ["Government & Public Sector", "Energy & Critical Infrastructure", "Financial Services", "Enterprise SaaS"];

const differentiators = [
  "Direct access to the practitioner running the engagement, not a staffing pyramid delivering behind one",
  "OPERA is a working method built from thirteen-plus years of implementation, not a licensed or resold framework",
  "Every engagement produces artefacts, an Operating Model, RACI Matrix, Risk Register, Evidence Register, that the organisation keeps and can run without outside help",
];

const representativeEngagements = advisoryEngagements.filter((engagement) => engagement.featured);

export default function CapabilityOverviewPage() {
  return (
    <>
      <JsonLd data={personSchema()} />
      <JsonLd data={organizationSchema()} />

      <PageHero
        eyebrow="Executive Capability Overview"
        title="A summary of the practice, for those evaluating before a conversation."
        description={`${site.name} is an independent advisory practice in AI, digital, cyber and technology risk governance, founded by ${site.advisorName} and built on the OPERA methodology.`}
      />

      {/* PDF notice */}
      <section className="border-b border-border bg-surface py-section-sm">
        <Container size="narrow">
          <p className="text-eyebrow uppercase tracking-widest text-muted">Executive Capability Overview (PDF)</p>
          <p className="mt-4 text-base leading-relaxed text-ink pretty">
            Our downloadable executive capability overview is currently being finalised and will be available
            shortly.
          </p>
          <p className="mt-2 text-base leading-relaxed text-muted pretty">
            In the meantime, this page provides an overview of our advisory capabilities and engagement
            approach.
          </p>
        </Container>
      </section>

      {/* Positioning */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Positioning</h2>
          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            {site.name} is built around a single practitioner and a documented methodology, not a delivery
            team. It exists to make governance decisions that hold up under audit, regulation and board
            scrutiny, for boards, CISOs, CIOs and government steering committees in regulated and high-assurance
            organisations.
          </p>
        </Container>
      </section>

      <Divider />

      {/* Core capabilities */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">Core Advisory Capabilities</h2>
          <ul className="mt-8 grid grid-cols-1 gap-x-8 gap-y-3 border-t border-border pt-6 sm:grid-cols-2 lg:grid-cols-5">
            {capabilities.map((capability) => (
              <li key={capability} className="text-sm text-ink">
                {capability}
              </li>
            ))}
          </ul>
        </Container>
      </section>

      <Divider />

      {/* OPERA */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">The OPERA Methodology</h2>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted pretty">
            OPERA sequences five decisions, from the opportunity behind a governance requirement to the
            assurance evidence that outlasts it, developed from running this kind of programme inside four
            regulated environments before it had a name.
          </p>
          <div className="mt-10">
            <OperaDiagram />
          </div>
        </Container>
      </section>

      <Divider />

      {/* Representative engagement areas */}
      <section className="py-section">
        <Container size="wide">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-end">
            <h2 className="font-serif text-title text-ink">Representative Engagement Areas</h2>
            <Link href="/selected-advisory-engagements" className="text-sm text-accent underline underline-offset-4">
              View all engagement areas &rarr;
            </Link>
          </div>
          <ul className="mt-8 divide-y divide-border border-t border-border">
            {representativeEngagements.map((engagement) => (
              <li key={engagement.slug} className="py-6">
                <Link
                  href={`/selected-advisory-engagements/${engagement.slug}`}
                  className="group grid grid-cols-1 gap-2 lg:grid-cols-12 lg:items-baseline lg:gap-8"
                >
                  <h3 className="font-serif text-base text-ink group-hover:text-accent lg:col-span-4">
                    {engagement.title}
                  </h3>
                  <p className="text-sm leading-relaxed text-muted lg:col-span-8">{engagement.focus}</p>
                </Link>
              </li>
            ))}
          </ul>
        </Container>
      </section>

      <Divider />

      {/* Industries served */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Industries Served</h2>
          <p className="mt-6 text-base leading-relaxed text-ink pretty">{industries.join(", ")}</p>
        </Container>
      </section>

      <Divider />

      {/* Why AI for U&I */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Why {site.name}</h2>
          <ul className="mt-6 space-y-3">
            {differentiators.map((item) => (
              <li key={item} className="flex gap-3 text-base leading-relaxed text-ink">
                <span aria-hidden className="mt-2.5 block h-1 w-1 shrink-0 rounded-full bg-accent" />
                {item}
              </li>
            ))}
          </ul>
        </Container>
      </section>

      <Divider />

      {/* Founder profile */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Founder Profile</h2>
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

      <CtaBand />
    </>
  );
}
