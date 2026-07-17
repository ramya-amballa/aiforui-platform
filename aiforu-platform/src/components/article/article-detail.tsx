import { Container } from "@/components/ui/container";
import type { Insight } from "@/types";

/**
 * Reusable article template for /insights/[slug]. Body copy comes from
 * insight.body, one paragraph per array entry. These are evergreen
 * advisory perspectives, not dated news posts, so no publication date
 * is shown; format and read time are the only metadata.
 */
export function ArticleDetail({ insight }: { insight: Insight }) {
  return (
    <article>
      <Container size="narrow" className="py-section-sm">
        <p className="text-eyebrow uppercase tracking-widest text-accent">{insight.category}</p>
        <h1 className="mt-6 font-serif text-display text-ink balance">{insight.title}</h1>
        <div className="mt-6 flex items-center gap-3 text-sm text-muted">
          <span>{insight.format}</span>
          <span aria-hidden>&middot;</span>
          <span>{insight.readTime}</span>
        </div>

        <div className="mt-10 space-y-6 text-base leading-relaxed text-ink pretty">
          {insight.body.map((paragraph, index) => (
            <p key={index}>{paragraph}</p>
          ))}
        </div>
      </Container>
    </article>
  );
}
