import type { Metadata } from "next";
import { PageHero } from "@/components/sections/page-hero";
import { Container } from "@/components/ui/container";
import { buildMetadata } from "@/lib/metadata";
import { site } from "@/lib/constants";

export const metadata: Metadata = buildMetadata({
  title: "Terms of Use",
  description: "Terms governing use of the AI for U&I website.",
  path: "/terms",
});

export default function TermsPage() {
  return (
    <>
      <PageHero eyebrow="Legal" title="Terms of Use" description="Last updated July 2026." size="compact" />
      <section className="py-section">
        <Container size="narrow" className="space-y-10">
          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">Scope</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              These terms govern use of {site.url}, the website of {site.name}, the advisory practice of{" "}
              {site.advisorName}. They apply to this website only. Any advisory engagement is governed by
              separate terms agreed directly between {site.advisorName} and the client.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">Content is not advice</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              Insights, frameworks, resources and other content published on this site reflect general
              perspective on governance practice. They are provided for informational purposes and do not
              constitute legal, regulatory or professional advice for any specific situation. Organisations
              should seek advice tailored to their own facts before acting on anything published here.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">Intellectual property</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              The content on this site, including the OPERA methodology, frameworks, articles and resources,
              is the intellectual property of {site.advisorName} unless otherwise stated. You may read, cite
              and link to it for non-commercial purposes with attribution. Reproducing or redistributing it
              for commercial purposes requires prior written permission.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">No warranty</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              This site is provided as is. While reasonable care is taken to keep content accurate and
              current, no guarantee is made that it is complete, up to date, or free of error, and it should
              not be relied on as the sole basis for a governance, risk or compliance decision.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">Changes to these terms</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              These terms may be updated as the site changes. The date at the top of this page reflects the
              most recent update. Continued use of the site after a change constitutes acceptance of the
              updated terms.
            </p>
          </div>

          <div className="space-y-4">
            <h2 className="font-serif text-title text-ink">Contact</h2>
            <p className="text-base leading-relaxed text-muted pretty">
              Questions about these terms can be sent through the Contact page.
            </p>
          </div>
        </Container>
      </section>
    </>
  );
}
