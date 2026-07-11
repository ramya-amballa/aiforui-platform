import { Container } from "@/components/ui/container";
import { Placeholder } from "@/components/ui/placeholder";
import { formatDate } from "@/lib/utils";
import type { Insight } from "@/types";

/**
 * Reusable article template for /insights/[slug]. Body copy is
 * represented by placeholder paragraphs pending Phase 2 authoring.
 */
export function ArticleDetail({ insight }: { insight: Insight }) {
  return (
    <article>
      <Container size="narrow" className="py-section-sm">
        <p className="text-eyebrow uppercase tracking-widest text-accent">{insight.category}</p>
        <h1 className="mt-6 font-serif text-display text-ink balance">{insight.title}</h1>
        <div className="mt-6 flex items-center gap-3 text-sm text-muted">
          <span>{formatDate(insight.date)}</span>
          <span aria-hidden>&middot;</span>
          <span>{insight.readTime}</span>
        </div>

        <Placeholder label="Article Cover Image Placeholder" aspect="video" className="mt-10" />

        <div className="mt-10 space-y-6 text-base leading-relaxed text-ink pretty">
          <p>[Article Body Paragraph Placeholder 1]</p>
          <p>[Article Body Paragraph Placeholder 2]</p>
          <p>[Article Body Paragraph Placeholder 3]</p>
        </div>
      </Container>
    </article>
  );
}
