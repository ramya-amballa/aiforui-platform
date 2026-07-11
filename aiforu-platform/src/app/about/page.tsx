import type { Metadata } from "next";
import { CtaBand } from "@/components/sections/cta-band";
import { JsonLd } from "@/components/seo/json-ld";
import { personSchema } from "@/components/seo/schema";
import { Container } from "@/components/ui/container";
import { Eyebrow } from "@/components/ui/eyebrow";
import { Placeholder } from "@/components/ui/placeholder";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "About Ramya",
  description: "[About Ramya — Meta Description Placeholder]",
  path: "/about",
});

const credentials = ["[Credential Placeholder 1]", "[Credential Placeholder 2]", "[Credential Placeholder 3]"];

export default function AboutPage() {
  return (
    <>
      <JsonLd data={personSchema()} />

      <section className="border-b border-border py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="lg:col-span-7">
              <Eyebrow>About {site.advisorName}</Eyebrow>
              <h1 className="mt-6 font-serif text-display text-ink balance">[About Page Title Placeholder]</h1>
              <p className="mt-6 text-lg leading-relaxed text-muted pretty">[About — Lead Paragraph Placeholder]</p>
            </div>
            <div className="lg:col-span-4 lg:col-start-9">
              <Placeholder label="Executive Portrait Placeholder" aspect="portrait" />
            </div>
          </div>
        </Container>
      </section>

      <section className="py-section">
        <Container size="wide">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-12">
            <div className="space-y-6 lg:col-span-7">
              <p className="text-base leading-relaxed text-ink pretty">[About — Body Paragraph Placeholder 1]</p>
              <p className="text-base leading-relaxed text-ink pretty">[About — Body Paragraph Placeholder 2]</p>
              <p className="text-base leading-relaxed text-ink pretty">[About — Body Paragraph Placeholder 3]</p>
            </div>
            <aside className="border-t border-border pt-8 lg:col-span-4 lg:col-start-9 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
              <p className="text-eyebrow uppercase tracking-widest text-muted">Credentials</p>
              <ul className="mt-4 space-y-3">
                {credentials.map((credential) => (
                  <li key={credential} className="text-sm text-ink">
                    {credential}
                  </li>
                ))}
              </ul>
            </aside>
          </div>
        </Container>
      </section>

      <CtaBand />
    </>
  );
}
