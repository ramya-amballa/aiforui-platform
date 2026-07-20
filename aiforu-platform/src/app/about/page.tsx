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
    "Ramya Amballa spent thirteen years in enterprise technology risk, cyber risk, GRC, third-party risk and audit readiness at PwC, Wells Fargo, JPMorgan Chase and Viatris before founding an independent AI and technology governance advisory practice built on the OPERA methodology.",
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
  "Ends with something the organisation owns and can run without outside help: an operating model, not a report that sits on a shelf",
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
              Thirteen years across PwC, Wells Fargo, JPMorgan Chase and Viatris, now advising boards and
              regulators on AI and technology governance.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-brand-muted pretty">
              Ramya Amballa built her governance judgment inside enterprise technology risk, cyber risk, GRC,
              third-party risk and audit readiness functions, the disciplines she now applies to AI governance
              for boards, CISOs and government steering committees.
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

      {/* Where this judgment comes from */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Where This Judgment Comes From</h2>

          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            Ramya Amballa spent thirteen years inside the governance, risk and audit functions of PwC, Wells
            Fargo, JPMorgan Chase and Viatris, running enterprise technology risk, cyber risk, GRC, third-party
            risk and audit readiness programmes across banking, professional services and life sciences. At
            JPMorgan Chase, that meant global KYC and sanctions operations across multiple jurisdictions. At
            Wells Fargo and Viatris, it meant third-party risk governance for hundreds of vendor relationships,
            through the part of the relationship most programmes stop watching once onboarding is signed off.
            At PwC, it meant testing controls across 300+ business-critical applications and cutting residual
            risk exposure by 35% in a single programme.
          </p>

          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            AI governance turned out to be the same discipline wearing a faster clock. The organisations asking
            for it were rarely short of frameworks. What they lacked was what those thirteen years had actually
            been about: a named owner for every decision, evidence maintained as a matter of course rather than
            assembled after an incident, and controls tested against what a system does in production, not what
            a policy says it should do.
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
            It fails for the same reasons governance has always failed: assumed ownership, retrospective
            evidence, and controls nobody tested against how the system actually behaves.
          </p>
        </Container>
      </section>

      <Divider />

      {/* Why OPERA exists, introduced only now */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">Why OPERA Exists</h2>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted pretty">
            OPERA is what came out of applying that judgment consistently. It sequences five decisions, from
            the opportunity behind a governance requirement to the assurance evidence that outlasts it,
            developed from running this kind of programme inside four different regulated environments before
            it had a name.
          </p>
          <div className="mt-10">
            <OperaDiagram />
          </div>
        </Container>
      </section>

      <Divider />

      {/* Background */}
      <section className="py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="lg:col-span-6">
              <h2 className="font-serif text-title text-ink">Background</h2>
              <p className="mt-6 text-sm text-muted">Certifications: {certifications}</p>
              <p className="mt-2 text-sm text-muted">Sectors: {environments}</p>
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
            She does not take on work where the goal is a compliance document rather than a governance
            structure people will actually use, or where accountability cannot be clearly assigned inside the
            organisation.
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
