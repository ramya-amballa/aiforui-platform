import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardTitle } from "@/components/ui/card";
import type { Resource } from "@/types";

export function ResourceCard({ resource }: { resource: Resource }) {
  return (
    <Card href={`/resources/${resource.slug}`}>
      <Badge>{resource.type}</Badge>
      <CardTitle>{resource.title}</CardTitle>
      <CardDescription>{resource.description}</CardDescription>
    </Card>
  );
}
