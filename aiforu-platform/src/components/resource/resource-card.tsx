import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import type { Resource } from "@/types";

export function ResourceCard({ resource }: { resource: Resource }) {
  return (
    <Card href={`/resources/${resource.slug}`}>
      <div className="flex items-center justify-between gap-3">
        <Badge>{resource.type}</Badge>
        <Badge tone={resource.accessTier === "Free" ? "neutral" : "accent"}>{resource.accessTier}</Badge>
      </div>
      <CardTitle>{resource.title}</CardTitle>
      <CardDescription>{resource.description}</CardDescription>
    </Card>
  );
}
