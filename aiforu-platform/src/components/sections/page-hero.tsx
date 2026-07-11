import { Container } from "@/components/ui/container";
import { Eyebrow } from "@/components/ui/eyebrow";
import { cn } from "@/lib/utils";

interface PageHeroProps {
  eyebrow: string;
  title: string;
  description?: string;
  size?: "default" | "compact";
  children?: React.ReactNode;
}

/**
 * Standard hero used at the top of top-level pages (services, domains
 * index, insights index, about, contact). The homepage uses its own
 * larger hero composition.
 */
export function PageHero({ eyebrow, title, description, size = "default", children }: PageHeroProps) {
  return (
    <section className={cn("border-b border-border", size === "default" ? "py-section" : "py-section-sm")}>
      <Container size="wide">
        <Eyebrow>{eyebrow}</Eyebrow>
        <h1 className="mt-6 max-w-3xl font-serif text-display text-ink balance">{title}</h1>
        {description ? (
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-muted pretty">{description}</p>
        ) : null}
        {children}
      </Container>
    </section>
  );
}
