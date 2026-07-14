import type { Metadata } from "next";
import { CtaBand } from "@/components/sections/cta-band";
import { OperaDiagram } from "@/components/sections/opera-diagram";
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

const gaps = [
  "Ownership no one clearly holds",
  "Risk decisions no one is accountable for",
  "Evidence assembled after the fact, not maintained as a matter of course",
];

const engagementModel = [
  "Starts with a working conversation about a specific problem, not a scoping questionnaire",
  "Structured around the OPERA methodology, scaled to what the organisation needs",
  "Sized to fit: a focused advisory engagement, an operating model redesign, or a longer programme",
];

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
                not just documented, using the OPERA methodology I developed for turning governance intent
                into everyday practice.
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
          <p className="mt-6 text-base leading-relaxed text-ink pretty">
            Most organisations do not lack governance frameworks. They lack:
          </p>
          <ul className="mt-4 space-y-3">
            {gaps.map((gap) => (
              <li key={gap} className="flex gap-3 text-base leading-relaxed text-ink">
                <span aria-hidden className="mt-2.5 block h-1 w-1 shrink-0 rounded-full bg-accent" />
                {gap}
              </li>
            ))}
          </ul>
          <p className="mt-6 text-base leading-relaxed text-muted pretty">
            That gap is where audits get uncomfortable, AI initiatives stall under board scrutiny, and
            regulators lose confidence in an otherwise capable organisation. I close it directly: operating
            models, ownership structures and assurance evidence that hold up when someone outside the
            organisation asks a hard question.
          </p>
        </Container>
      </section>

      <Divider />

      {/* How I think */}
      <section className="py-section">
        <Container size="wide">
          <h2 className="font-serif text-title text-ink">How I Think About Governance</h2>
          <blockquote className="mt-6 max-w-2xl border-l-2 border-accent pl-6 font-serif text-xl italic leading-relaxed text-ink">
            A framework tells you what questions to ask. It does not make the decision for you.
          </blockquote>
          <p className="mt-6 max-w-2xl text-base leading-relaxed text-muted pretty">
            Governance is judgment work, supported by structure, not replaced by it. OPERA is the structure I
            built to make that judgment accountable at every stage.
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
                Built for organisations where governance decisions face external scrutiny: audit, regulation,
                procurement rules or public accountability.
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
        </Container>
      </section>

      <CtaBand />
    </>
  );
}
