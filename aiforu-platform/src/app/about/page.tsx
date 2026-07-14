import type { Metadata } from "next";
import { CtaBand } from "@/components/sections/cta-band";
import { JsonLd } from "@/components/seo/json-ld";
import { personSchema } from "@/components/seo/schema";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { Eyebrow } from "@/components/ui/eyebrow";
import { Placeholder } from "@/components/ui/placeholder";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "About",
  description:
    "Ramya Amballa is an independent advisor in AI governance, technology risk and third-party governance, and creator of the OPERA governance methodology.",
  path: "/about",
});

const environments = ["Financial Services", "Government & Public Sector", "Healthcare", "Technology"];

export default function AboutPage() {
  return (
    <>
      <JsonLd data={personSchema()} />

      {/* Identity */}
      <section className="border-b border-border py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="lg:col-span-7">
              <Eyebrow>About {site.advisorName}</Eyebrow>
              <h1 className="mt-6 font-serif text-display text-ink balance">
                Independent advisory in AI, digital and technology risk governance.
              </h1>
              <p className="mt-6 text-lg leading-relaxed text-muted pretty">
                I work with boards, executives and public-sector leaders who need governance decisions made,
                not just documented. That means building the ownership, evidence and assurance structure
                behind a policy, using the OPERA methodology I developed for turning governance intent into
                everyday practice.
              </p>
            </div>
            <div className="lg:col-span-4 lg:col-start-9">
              <Placeholder label="Executive Portrait Placeholder" aspect="portrait" />
            </div>
          </div>
        </Container>
      </section>

      {/* Why I do this work */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">Why I Do This Work</h2>
          <div className="mt-6 space-y-6">
            <p className="text-base leading-relaxed text-ink pretty">
              Most organisations do not lack governance frameworks. They lack clarity about who owns a given
              decision, and evidence that the decision was actually made with the right information in front
              of the right person. That gap is where audits get uncomfortable, where AI initiatives stall
              under board scrutiny, and where regulators lose confidence in an otherwise capable organisation.
            </p>
            <p className="text-base leading-relaxed text-ink pretty">
              I focus on closing that gap directly: building operating models, ownership structures and
              assurance evidence that hold up when someone outside the organisation, an auditor, a regulator,
              a board, asks a hard question about how a decision was made.
            </p>
          </div>
        </Container>
      </section>

      <Divider />

      {/* How I think */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">How I Think About Governance</h2>
          <blockquote className="mt-6 border-l-2 border-accent pl-6 font-serif text-xl italic leading-relaxed text-ink">
            A framework tells you what questions to ask. It does not make the decision for you.
          </blockquote>
          <div className="mt-6 space-y-6">
            <p className="text-base leading-relaxed text-ink pretty">
              I built the OPERA methodology (Opportunity, People, Evaluation, Response, Assurance) because I
              kept seeing the same failure pattern: a well-designed risk framework, applied correctly, that
              still failed to prevent a bad outcome, because no one had been assigned to own the decision it
              was meant to inform.
            </p>
            <p className="text-base leading-relaxed text-ink pretty">
              Governance work, in my view, is judgment work supported by structure, not structure that
              replaces judgment. My job is to build the operating model, ownership map and evidence trail
              that let the people accountable for a decision actually make it well, and demonstrate that they
              did.
            </p>
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
                The methodology, frameworks and advisory approach here are built specifically for organisations
                where governance decisions face external scrutiny: audit, regulation, procurement rules or
                public accountability. That shapes how ownership, risk evaluation and evidence are structured,
                regardless of sector.
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
              <p className="mt-6 text-sm text-muted">Creator of the OPERA governance methodology.</p>
            </div>
          </div>
        </Container>
      </section>

      <Divider />

      {/* How I work */}
      <section className="py-section">
        <Container size="narrow">
          <h2 className="font-serif text-title text-ink">How I Work</h2>
          <div className="mt-6 space-y-6">
            <p className="text-base leading-relaxed text-ink pretty">
              Engagements typically start with a working conversation about a specific governance, risk or AI
              oversight problem, not a standard scoping questionnaire. From there, the work is structured
              around the OPERA methodology and scaled to what the organisation actually needs: a focused
              advisory engagement, a governance operating model redesign, or a longer strategic programme.
            </p>
            <p className="text-base leading-relaxed text-muted pretty">
              I do not take on work where the goal is a compliance document rather than a governance
              structure people will actually use, or where accountability for the resulting decisions cannot
              be clearly assigned to someone inside the organisation.
            </p>
          </div>
        </Container>
      </section>

      <CtaBand />
    </>
  );
}
