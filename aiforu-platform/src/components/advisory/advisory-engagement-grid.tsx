import { AdvisoryEngagementCard } from "@/components/advisory/advisory-engagement-card";
import type { AdvisoryEngagement } from "@/types";

export function AdvisoryEngagementGrid({ engagements }: { engagements: AdvisoryEngagement[] }) {
  if (engagements.length === 0) {
    return <p className="text-sm text-muted">No engagement areas match this filter yet.</p>;
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {engagements.map((engagement) => (
        <AdvisoryEngagementCard key={engagement.slug} engagement={engagement} />
      ))}
    </div>
  );
}
