import { ArticleCard } from "@/components/article/article-card";
import type { Insight } from "@/types";

export function ArticleGrid({ insights }: { insights: Insight[] }) {
  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {insights.map((insight) => (
        <ArticleCard key={insight.slug} insight={insight} />
      ))}
    </div>
  );
}
