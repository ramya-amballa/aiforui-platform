import { Card, CardDescription, CardEyebrow, CardFooter, CardTitle } from "@/components/ui/card";
import type { AdvisoryEngagement } from "@/types";

export function AdvisoryEngagementCard({ engagement }: { engagement: AdvisoryEngagement }) {
  return (
    <Card href={`/selected-advisory-engagements/${engagement.slug}`}>
      <CardEyebrow>
        {engagement.sector} &middot; {engagement.year}
      </CardEyebrow>
      <CardTitle>{engagement.title}</CardTitle>
      <CardDescription>{engagement.summary}</CardDescription>
      <CardFooter>
        <span className="text-sm text-accent">View engagement &rarr;</span>
      </CardFooter>
    </Card>
  );
}
