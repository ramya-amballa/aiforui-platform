import { ResourceCard } from "@/components/resource/resource-card";
import type { Resource } from "@/types";

export function ResourceGrid({ resources }: { resources: Resource[] }) {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {resources.map((resource) => (
        <ResourceCard key={resource.slug} resource={resource} />
      ))}
    </div>
  );
}
