import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardEyebrow, CardFooter, CardTitle } from "@/components/ui/card";
import type { AdvisoryEngagement } from "@/types";

export function AdvisoryEngagementCard({ engagement }: { engagement: AdvisoryEngagement }) {
  return (
    <Card href={`/selected-advisory-engagements/${engagement.slug}`}>
      <div className="flex items-center justify-between gap-3">
        {engagement.sector ? <CardEyebrow>{engagement.sector}</CardEyebrow> : <span aria-hidden />}
        <Badge>{engagement.track}</Badge>
      </div>
      <CardTitle>{engagement.title}</CardTitle>
      <CardDescription>{engagement.focus}</CardDescription>
      <CardFooter>
        <span className="text-sm text-accent">View engagement area &rarr;</span>
      </CardFooter>
    </Card>
  );
}
