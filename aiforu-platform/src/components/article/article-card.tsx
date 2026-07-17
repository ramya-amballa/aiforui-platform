import { Badge } from "@/components/ui/badge";
import { Card, CardDescription, CardEyebrow, CardTitle } from "@/components/ui/card";
import type { Insight } from "@/types";

export function ArticleCard({ insight }: { insight: Insight }) {
  const isPointOfView = insight.format === "Point of View";

  return (
    <Card href={`/insights/${insight.slug}`} className={isPointOfView ? "border-accent/40" : undefined}>
      <div className="flex items-center justify-between gap-3">
        <CardEyebrow>{insight.category}</CardEyebrow>
        <Badge tone={isPointOfView ? "accent" : "neutral"}>{insight.format}</Badge>
      </div>
      <CardTitle>{insight.title}</CardTitle>
      <CardDescription>{insight.excerpt}</CardDescription>
      <p className="mt-auto pt-6 text-xs uppercase tracking-widest text-muted">{insight.readTime}</p>
    </Card>
  );
}
