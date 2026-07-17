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
    "Ramya Amballa spent 13+ years in governance, risk and audit roles at PwC, Wells Fargo, JPMorgan Chase and Viatris before founding an independent AI and technology governance advisory practice.",
  path: "/about",
});

const practiceAreas = ["AI Governance", "Digital Governance", "Cyber Governance", "Technology Risk", "Third-Party Governance"];

const roles = [
  { company: "AIforU&I", role: "Independent Advisor", period: "Feb 2026 – Present" },
  { company: "PwC India", role: "Cyber Security Consultant, Governance", period: "Aug 2024 – Feb 2026" },
  { company: "Viatris", role: "Deputy Manager, Global Compliance", period: "Aug 2023 – Feb 2024" },
  { company: "Wells Fargo", role: "Operational Risk Consultant, TPRM", period: "Mar 2020 – Jul 2023" },
  { company: "JPMorgan Chase", role: "Team Lead, Operations", period: "Aug 2017 – Mar 2020" },
];

const certifications = ["NIST AI RMF", "CAISR, Red Team Leaders", "EU GDPR Practitioner", "Microsoft AI Transformation Leader"];

const environments = ["Government & Public Sector", "Energy & Critical Infrastructure", "Financial Services", "Enterprise SaaS"];

const elsewhere = [
  { label: "Substack", href: site.substack },
  { label: "GitHub", href: site.github },
  { label: "Gumroad", href: site.gumroad },
];

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
          <BlueprintPanel tone="ink" className="p-8 sm:p-12 lg:p-16">
            <p className="text-eyebrow uppercase tracking-[0.25em] text-brand-gold">{site.advisorName}</p>
            <div className="mt-4 h-px w-16 bg-brand-gold" />

            <h1 className="mt-8 max-w-3xl font-serif text-display text-brand-paper balance">
              Thirteen years inside PwC, Wells Fargo, JPMorgan Chase and Viatris, now advising independently on AI
              and technology governance.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-brand-muted pretty">
              I advise boards, CISOs and government steering committees on AI and technology governance decisions,
              using the same discipline I built running control testing, third-party risk and audit readiness
              programmes inside four regulated organisations.
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

            <div className="mt-12 flex items-center gap-4 border-t border-brand-paper/10 pt-6">
              <span aria-hidden className="h-px flex-1 bg-brand-paper/20" />
              <p className="text-eyebrow uppercase tracking-[0.2em] text-brand-gold">Founder, {site.name}</p>
              <span aria-hidden className="h-px flex-1 bg-brand-paper/20" />
            </div>
          </BlueprintPanel>
        </Container>
      </section>

      {/* Where this practice comes from */}
      <section className="py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="lg:col-span-7">
              <h2 className="font-serif text-title text-ink">Where This Practice Comes From</h2>

              <p className="mt-6 text-base leading-relaxed text-ink pretty">
                Before &ldquo;AI governance&rdquo; was a job title, I spent over a decade inside the governance,
                risk and audit functions of four very different organisations: global KYC and sanctions screening
                operations at JPMorgan Chase, third-party risk governance for 230+ high-risk suppliers at Wells
                Fargo, an enterprise Supplier Risk Management Framework at Viatris, and control testing across
                300+ business-critical applications at PwC. The industries changed. The failure pattern did not.
              </p>

              <p className="mt-6 text-base leading-relaxed text-ink pretty">
                Wells Fargo and Viatris both had documented third-party risk policies; the actual gap was who
                owned a vendor relationship once onboarding ended and monitoring became someone else&apos;s
                problem. JPMorgan Chase had detailed KYC and sanctions procedures; the gap was how fast a control
                could be evidenced to a regulator after the fact, not whether it had been followed at the time.
                PwC&apos;s clients held ISO 27001 and SOC 2 certifications; the gap was between what a control
                said on paper and what testing found in the environment, 35% of residual risk in one programme
                alone.
              </p>

              <p className="mt-6 text-base leading-relaxed text-ink pretty">
                By the time I was guiding PwC clients on applying NIST AI RMF to AI-assisted processes already
                running inside regulated environments, I recognised the pattern immediately. AI did not introduce
                a new governance problem. It reproduced the one I had spent a decade fixing, at a faster clock
                speed: ownership assigned informally or not at all, evidence generated after an incident instead
                of maintained as a matter of course, and controls that existed in policy but had never been
                tested against how the system actually behaved.
              </p>

              <p className="mt-6 text-base leading-relaxed text-muted pretty">
                I left PwC in February 2026 to advise independently, because the organisations asking the AI
                governance question were not short of frameworks. They needed someone who had run control
                testing, third-party risk and audit readiness programmes at scale, and could tell them which
                parts of that discipline still held for AI decisions and which parts had to be rebuilt.
              </p>
            </div>

            <div className="lg:col-span-4 lg:col-start-9">
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

      {/* Thesis */}
      <section className="border-y border-border bg-surface py-section">
        <Container size="narrow">
          <p className="font-serif text-title text-ink balance">
            AI governance is not a separate discipline. It is governance, applied to a new generation of
            decisions.
          </p>
          <p className="mt-6 text-base leading-relaxed text-muted pretty">
            The technology changes faster than the organisations governing it. The failure pattern, undocumented
            ownership, evidence assembled after the fact, controls that exist on paper but were never tested,
            does not. Treating AI governance as a new field means relearning lessons this practice already knows.
          </p>
        </Container>
      </section>

      <Divider />

      {/* OPERA, introduced only now */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">The OPERA Methodology</h2>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted pretty">
            OPERA is what came out of doing that work repeatedly. It is not a framework designed in the
            abstract: it formalises the five decisions I kept having to force into every engagement, whether the
            underlying system was a vendor contract, a KYC control or an AI model, so the same discipline can be
            run consistently and eventually handed to a client&apos;s own team.
          </p>
          <div className="mt-10">
            <OperaDiagram />
          </div>
        </Container>
      </section>

      <Divider />

      {/* Experience across environments */}
      <section className="py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="lg:col-span-6">
              <h2 className="font-serif text-title text-ink">Built for Enterprise &amp; Regulated Environments</h2>
              <p className="mt-6 text-base leading-relaxed text-muted pretty">
                I work with organisations where a governance decision has to survive contact with someone
                outside the building: an auditor, a regulator, a procurement panel, or a legislature. That is
                the standard I design to, not a generic best-practice baseline.
              </p>
            </div>
            <div className="lg:col-span-5 lg:col-start-8">
              <p className="text-eyebrow uppercase tracking-widest text-muted">Sectors</p>
              <ul className="mt-4 space-y-3 border-t border-border pt-4">
                {environments.map((environment) => (
                  <li key={environment} className="text-sm text-ink">
                    {environment}
                  </li>
                ))}
              </ul>

              <p className="mt-6 text-eyebrow uppercase tracking-widest text-muted">Certifications</p>
              <ul className="mt-4 space-y-3 border-t border-border pt-4">
                {certifications.map((certification) => (
                  <li key={certification} className="text-sm text-ink">
                    {certification}
                  </li>
                ))}
              </ul>

              <p className="mt-6 text-eyebrow uppercase tracking-widest text-muted">Elsewhere</p>
              <ul className="mt-4 flex flex-wrap gap-x-6 gap-y-2 border-t border-border pt-4">
                {elsewhere.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-ink hover:text-accent"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </Container>
      </section>

      <Divider />

      {/* How I work */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">How I Work</h2>
          <ul className="mt-6 space-y-3">
            {engagementModel.map((item) => (
              <li key={item} className="flex gap-3 text-base leading-relaxed text-ink">
                <span aria-hidden className="mt-2.5 block h-1 w-1 shrink-0 rounded-full bg-accent" />
                {item}
              </li>
            ))}
          </ul>
          <p className="mt-6 text-sm leading-relaxed text-muted pretty">
            I do not take on work where the goal is a compliance document rather than a governance structure
            people will actually use, or where accountability cannot be clearly assigned inside the
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
