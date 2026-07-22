import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import type { Resource } from "@/types";

export function ResourceDetail({ resource }: { resource: Resource }) {
  const isPremium = resource.accessTier === "Premium";
  const isComingSoon = resource.accessTier === "Coming Soon";

  return (
    <article>
      <Container size="narrow" className="py-section-sm">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="accent">{resource.type}</Badge>
          <Badge tone={resource.accessTier === "Free" ? "neutral" : "accent"}>{resource.accessTier}</Badge>
        </div>
        <h1 className="mt-6 font-serif text-display text-ink balance">{resource.title}</h1>
        <p className="mt-6 max-w-2xl text-lg leading-relaxed text-muted pretty">{resource.description}</p>

        <div className="mt-10">
          {resource.fileUrl ? (
            <Button href={resource.fileUrl} target="_blank" rel="noopener noreferrer" variant="primary" size="lg">
              Download PDF
            </Button>
          ) : (
            <Button variant="primary" size="lg" disabled={isComingSoon}>
              {isComingSoon ? "Coming soon" : isPremium ? "Request access" : "Download resource"}
            </Button>
          )}
        </div>
      </Container>
    </article>
  );
}
