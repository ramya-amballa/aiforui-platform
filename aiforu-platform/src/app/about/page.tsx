import type { Metadata } from "next";
import Link from "next/link";
import { BlueprintPanel } from "@/components/sections/blueprint-panel";
import { CtaBand } from "@/components/sections/cta-band";
import { OperaDiagram } from "@/components/sections/opera-diagram";
import { JsonLd } from "@/components/seo/json-ld";
import { personSchema } from "@/components/seo/schema";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "About",
  description:
    "Ramya Amballa advises boards, CISOs and government steering committees on AI and technology governance, drawing on thirteen-plus years in governance, risk and audit roles and the OPERA methodology.",
  path: "/about",
});

const practiceAreas = ["AI Governance", "Digital Governance", "Cyber Governance", "Technology Risk", "Third-Party Governance"];

const roles = [
  { company: "AI for U&I", role: "Independent Advisor", period: "Feb 2026 – Present" },
  { company: "PwC India", role: "Cyber Security Consultant, Governance", period: "Aug 2024 – Feb 2026" },
  { company: "Viatris", role: "Deputy Manager, Global Compliance", period: "Aug 2023 – Feb 2024" },
  { company: "Wells Fargo", role: "Operational Risk Consultant, TPRM", period: "Mar 2020 – Jul 2023" },
  { company: "JPMorgan Chase", role: "Team Lead, Operations", period: "Aug 2017 – Mar 2020" },
];

const certifications = "NIST AI RMF, CAISR, EU GDPR Practitioner, Microsoft AI Transformation Leader";

const environments = "Government & Public Sector, Energy & Critical Infrastructure, Financial Services, Enterprise SaaS";

const engagementModel = [
  "Starts with a working conversation about a specific problem, not a scoping questionnaire",
  "Run using the OPERA methodology, scaled to what the organisation needs rather than applied wholesale",
  "Sized to fit: a focused advisory engagement, an operating model redesign, or a longer programme",
  "Ends with something the organisation owns and can run without me: an operating model, not a report that sits on a shelf",
];

export default function AboutPage() {
  return (
    <>
      <JsonLd data={personSchema()} />

      {/* Identity */}
      <section className="border-b border-border py-section">
        <Container size="wide">
          <BlueprintPanel tone="ink" className="p-8 sm:p-10 lg:p-12">
            <p className="text-eyebrow uppercase tracking-[0.25em] text-brand-gold">{site.advisorName}</p>
            <div className="mt-4 h-px w-16 bg-brand-gold" />

            <h1 className="mt-8 max-w-3xl font-serif text-display text-brand-paper balance">
              Frameworks describe what governance should look like. OPERA is how it actually gets run.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-brand-muted pretty">
              Advisory work in AI, digital, cyber and third-party governance, for boards, CISOs and government
              steering committees in regulated and high-assurance organisations.
            </p>

            <div className="mt-10 flex flex-wrap items-center gap-x-3 gap-y-2 border-t border-brand-paper/10 pt-8 text-sm text-brand-paper">
              {practiceAreas.map((area, index) => (
                <span key={area} className="flex items-center gap-3">
                  {area}
                  {index < practiceAreas.length - 1 && (
                    <span aria-hidden className="text-brand-gold">
                      &middot;
                    </span>
                  )}
                </span>
              ))}
            </div>
          </BlueprintPanel>
        </Container>
      </section>

      {/* Who this practice serves */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Who This Practice Serves</h2>
          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            Boards, CISOs, CIOs and government steering committees who need a governance decision to hold up
            when someone outside the organisation, an auditor, a regulator, a procurement panel, examines it.
            Work spans {environments}.
          </p>
        </Container>
      </section>

      <Divider />

      {/* Why organisations engage */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Why Organisations Engage This Practice</h2>
          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            Governance programmes rarely fail from a missing framework. They fail because ownership was
            assumed rather than assigned, evidence was produced after the fact rather than maintained, and
            controls were tested on paper but not in the environment where they actually operate. Closing that
            gap, not adding another policy, is the work.
          </p>
        </Container>
      </section>

      {/* Philosophy */}
      <section className="border-y border-border bg-surface py-section">
        <Container size="narrow">
          <p className="font-serif text-title text-ink balance">
            AI governance is not a separate discipline. It is governance, applied to a new generation of
            decisions.
          </p>
          <p className="mt-6 text-base leading-relaxed text-muted pretty">
            The technology changes faster than the organisations governing it. The failure pattern,
            undocumented ownership, evidence assembled after the fact, controls never tested against how the
            system actually behaves, does not.
          </p>
        </Container>
      </section>

      <Divider />

      {/* Why OPERA exists */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">Why OPERA Exists</h2>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted pretty">
            Most governance frameworks describe intent well and operations poorly. OPERA sequences five
            decisions, from the opportunity behind a requirement to the assurance evidence that outlasts it, so
            a governance requirement becomes something an organisation runs, not just a document it produces.
          </p>
          <div className="mt-10">
            <OperaDiagram />
          </div>
        </Container>
      </section>

      <Divider />

      {/* Credibility */}
      <section className="py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="lg:col-span-6">
              <h2 className="font-serif text-title text-ink">Background</h2>
              <p className="mt-6 text-base leading-relaxed text-muted pretty">
                Thirteen-plus years across professional services, banking and life sciences: control testing,
                third-party risk and audit readiness, most recently leading control testing across 300+
                business-critical applications at PwC.
              </p>
              <p className="mt-4 text-sm text-muted">Certifications: {certifications}</p>
            </div>
            <div className="lg:col-span-5 lg:col-start-8">
              <p className="text-eyebrow uppercase tracking-widest text-muted">Experience</p>
              <ul className="mt-4 space-y-4 border-t border-border pt-4">
                {roles.map((item) => (
                  <li key={item.company}>
                    <p className="text-sm text-ink">
                      {item.company} <span className="text-muted">&middot; {item.role}</span>
                    </p>
                    <p className="mt-0.5 text-xs text-muted">{item.period}</p>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Container>
      </section>

      <Divider />

      {/* How engagements work */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">How Engagements Work</h2>
          <ul className="mt-6 space-y-3">
            {engagementModel.map((item) => (
              <li key={item} className="flex gap-3 text-base leading-relaxed text-ink">
                <span aria-hidden className="mt-2.5 block h-1 w-1 shrink-0 rounded-full bg-accent" />
                {item}
              </li>
            ))}
          </ul>
          <p className="mt-6 text-sm leading-relaxed text-muted pretty">
            No work where the goal is a compliance document rather than a governance structure people will
            actually use, or where accountability cannot be clearly assigned inside the organisation.
          </p>
          <p className="mt-6 text-sm leading-relaxed text-muted">
            <Link href="/methodology" className="text-accent underline underline-offset-4">
              Read the full OPERA methodology
            </Link>
            .
          </p>
        </Container>
      </section>

      <CtaBand />
    </>
  );
}
