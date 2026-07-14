import Link from "next/link";
import { Container } from "@/components/ui/container";
import { Eyebrow } from "@/components/ui/eyebrow";
import type { Insight } from "@/types";

/**
 * The signature section of the site. Deliberately not built from the
 * standard Card/ArticleCard primitives. Point of View pieces (original
 * frameworks, decision models, governance perspectives) are meant to
 * read as authored thinking, not as feed items, so the treatment is
 * large serif type over hairline rules rather than bordered cards.
 */
export function PointOfViewSection({ pieces }: { pieces: Insight[] }) {
  if (pieces.length === 0) return null;

  return (
    <section className="border-t border-border py-section">
      <Container size="wide">
        <div className="max-w-2xl">
          <Eyebrow>Point of View</Eyebrow>
          <h2 className="mt-6 font-serif text-headline text-ink balance">
            Original thinking, not commentary on the news cycle
          </h2>
          <p className="mt-4 text-base leading-relaxed text-muted pretty">
            Frameworks, decision models and governance perspectives developed from live advisory work.
          </p>
        </div>

        <div className="mt-12 divide-y divide-border border-t border-border">
          {pieces.map((piece, index) => (
            <Link
              key={piece.slug}
              href={`/insights/${piece.slug}`}
              className="group grid grid-cols-1 gap-4 py-10 lg:grid-cols-12 lg:items-baseline lg:gap-8"
            >
              <span className="font-mono text-xs text-signal lg:col-span-1">
                {String(index + 1).padStart(2, "0")}
              </span>
              <h3 className="font-serif text-title text-ink group-hover:text-accent lg:col-span-6">
                {piece.title}
              </h3>
              <p className="text-sm leading-relaxed text-muted lg:col-span-5">{piece.excerpt}</p>
            </Link>
          ))}
        </div>

        <Link href="/insights?format=Point+of+View" className="mt-10 inline-block text-sm text-accent underline underline-offset-4">
          Read the full body of thinking &rarr;
        </Link>
      </Container>
    </section>
  );
}
