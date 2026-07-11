import { Card, CardDescription, CardEyebrow, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import type { Insight } from "@/types";

export function ArticleCard({ insight }: { insight: Insight }) {
  return (
    <Card href={`/insights/${insight.slug}`}>
      <CardEyebrow>
        {insight.category} &middot; {formatDate(insight.date)}
      </CardEyebrow>
      <CardTitle>{insight.title}</CardTitle>
      <CardDescription>{insight.excerpt}</CardDescription>
      <p className="mt-auto pt-6 text-xs uppercase tracking-widest text-muted">{insight.readTime}</p>
    </Card>
  );
}
