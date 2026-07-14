import { Badge } from "@/components/ui/badge";
import { Container } from "@/components/ui/container";
import { Divider } from "@/components/ui/divider";
import type { AdvisoryEngagement, GovernanceDomain } from "@/types";

interface AdvisoryEngagementDetailProps {
  engagement: AdvisoryEngagement;
  relatedDomains: GovernanceDomain[];
}

/**
 * Reusable detail template for every Selected Engagement Area page.
 * New engagement areas are added purely through content/advisory-engagements.ts,
 * no new template code required. `client`, `sector`, `year` and `outcome`
 * render only when present, so a verified case study can be added to any
 * entry later without a template change.
 */
export function AdvisoryEngagementDetail({ engagement, relatedDomains }: AdvisoryEngagementDetailProps) {
  const hasCaseDetail = engagement.client || engagement.sector || engagement.year;

  return (
    <article>
      <Container size="narrow" className="py-section-sm">
        <div className="flex flex-wrap gap-2">
          {relatedDomains.map((domain) => (
            <Badge key={domain.slug} tone="accent">
              {domain.shortName}
            </Badge>
          ))}
        </div>

        <h1 className="mt-6 font-serif text-display text-ink balance">{engagement.title}</h1>

        <dl className="mt-8 grid grid-cols-2 gap-6 border-y border-border py-6 sm:grid-cols-4">
          <div>
            <dt className="text-eyebrow uppercase tracking-widest text-muted">Track</dt>
            <dd className="mt-2 text-sm text-ink">{engagement.track}</dd>
          </div>
          {engagement.client && (
            <div>
              <dt className="text-eyebrow uppercase tracking-widest text-muted">Client</dt>
              <dd className="mt-2 text-sm text-ink">{engagement.client}</dd>
            </div>
          )}
          {engagement.sector && (
            <div>
              <dt className="text-eyebrow uppercase tracking-widest text-muted">Sector</dt>
              <dd className="mt-2 text-sm text-ink">{engagement.sector}</dd>
            </div>
          )}
          {engagement.year && (
            <div>
              <dt className="text-eyebrow uppercase tracking-widest text-muted">Year</dt>
              <dd className="mt-2 text-sm text-ink">{engagement.year}</dd>
            </div>
          )}
        </dl>

        <div className="mt-12 space-y-12">
          <section>
            <h2 className="font-serif text-title text-ink">Focus</h2>
            <p className="mt-4 text-base leading-relaxed text-muted pretty">{engagement.focus}</p>
          </section>

          <Divider />

          <section>
            <h2 className="font-serif text-title text-ink">Approach</h2>
            <ol className="mt-4 space-y-4">
              {engagement.approach.map((step, index) => (
                <li key={index} className="flex gap-4">
                  <span className="font-serif text-sm text-accent">{String(index + 1).padStart(2, "0")}</span>
                  <p className="text-base leading-relaxed text-muted">{step}</p>
                </li>
              ))}
            </ol>
          </section>

          <Divider />

          <section>
            <h2 className="font-serif text-title text-ink">Deliverables</h2>
            <ul className="mt-4 space-y-3">
              {engagement.deliverables.map((item, index) => (
                <li key={index} className="flex gap-3 text-base leading-relaxed text-muted">
                  <span aria-hidden className="text-accent">
                    &middot;
                  </span>
                  {item}
                </li>
              ))}
            </ul>
          </section>

          {engagement.outcome && (
            <>
              <Divider />
              <section>
                <h2 className="font-serif text-title text-ink">Outcome</h2>
                <p className="mt-4 text-base leading-relaxed text-muted pretty">{engagement.outcome}</p>
              </section>
            </>
          )}

          {!hasCaseDetail && (
            <p className="text-sm text-muted">
              Named case studies for this engagement area will be added here once cleared for public reference.
            </p>
          )}
        </div>
      </Container>
    </article>
  );
}
