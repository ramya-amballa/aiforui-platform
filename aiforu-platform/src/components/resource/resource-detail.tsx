import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Container } from "@/components/ui/container";
import type { Resource } from "@/types";

export function ResourceDetail({ resource }: { resource: Resource }) {
  return (
    <article>
      <Container size="narrow" className="py-section-sm">
        <Badge tone="accent">{resource.type}</Badge>
        <h1 className="mt-6 font-serif text-display text-ink balance">{resource.title}</h1>
        <p className="mt-6 max-w-2xl text-lg leading-relaxed text-muted pretty">{resource.description}</p>

        <div className="mt-10">
          <Button variant="primary" size="lg">
            [Download Resource Placeholder]
          </Button>
        </div>
      </Container>
    </article>
  );
}
