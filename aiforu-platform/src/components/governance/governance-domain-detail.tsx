import { AdvisoryEngagementGrid } from "@/components/advisory/advisory-engagement-grid";
import { ArticleGrid } from "@/components/article/article-grid";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import { Eyebrow } from "@/components/ui/eyebrow";
import type { AdvisoryEngagement, GovernanceDomain, Insight } from "@/types";

interface GovernanceDomainDetailProps {
  domain: GovernanceDomain;
  relatedEngagements: AdvisoryEngagement[];
  relatedInsights: Insight[];
}

/**
 * Reusable template for each of the nine governance domain pages.
 * Domain content lives entirely in content/governance-domains.ts.
 */
export function GovernanceDomainDetail({ domain, relatedEngagements, relatedInsights }: GovernanceDomainDetailProps) {
  return (
    <article>
      <section className="border-b border-border py-section">
        <Container size="wide">
          <Eyebrow>{domain.eyebrow}</Eyebrow>
          <h1 className="mt-6 max-w-3xl font-serif text-display text-ink balance">{domain.name}</h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-muted pretty">{domain.summary}</p>
        </Container>
      </section>

      <section className="py-section-sm">
        <Container size="wide" className="grid grid-cols-1 gap-12 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <h2 className="font-serif text-title text-ink">Overview</h2>
            <p className="mt-4 text-base leading-relaxed text-muted pretty">{domain.overview}</p>

            <h2 className="mt-12 font-serif text-title text-ink">Focus Areas</h2>
            <ul className="mt-4 space-y-3">
              {domain.focusAreas.map((area) => (
                <li key={area} className="flex gap-3 text-base leading-relaxed text-muted">
                  <span aria-hidden className="mt-2.5 block h-1 w-1 shrink-0 rounded-full bg-accent" />
                  {area}
                </li>
              ))}
            </ul>
          </div>

          <aside className="border-t border-border pt-8 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
            <h2 className="text-eyebrow uppercase tracking-widest text-muted">Who This Is For</h2>
            <ul className="mt-4 space-y-3">
              {domain.whoItsFor.map((audience) => (
                <li key={audience} className="text-sm text-ink">
                  {audience}
                </li>
              ))}
            </ul>
          </aside>
        </Container>
      </section>

      {relatedEngagements.length > 0 ? (
        <>
          <Divider />
          <section className="py-section-sm">
            <Container size="wide">
              <h2 className="font-serif text-title text-ink">Related Advisory Engagements</h2>
              <div className="mt-8">
                <AdvisoryEngagementGrid engagements={relatedEngagements} />
              </div>
            </Container>
          </section>
        </>
      ) : null}

      {relatedInsights.length > 0 ? (
        <>
          <Divider />
          <section className="py-section-sm">
            <Container size="wide">
              <h2 className="font-serif text-title text-ink">Related Insights</h2>
              <div className="mt-8">
                <ArticleGrid insights={relatedInsights} />
              </div>
            </Container>
          </section>
        </>
      ) : null}
    </article>
  );
}
