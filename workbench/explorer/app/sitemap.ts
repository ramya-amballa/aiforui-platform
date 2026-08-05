import type { MetadataRoute } from "next";
import { graph } from "@/lib/data";
import type { EntityType } from "@/lib/types";

export const dynamic = "force-static";

const SITE_URL = "https://workbench.aiforui.com";

const ROUTE_PREFIX: Record<EntityType, string> = {
  decision: "decisions",
  incident: "incidents",
  pattern: "patterns",
  control: "controls",
  evidence: "evidence",
  board_question: "board-questions",
};

const STATIC_ROUTES = [
  "",
  "decisions",
  "incidents",
  "patterns",
  "controls",
  "evidence",
  "board-questions",
  "frameworks",
  "graph",
  "standards",
  "sources",
  "corrections",
  "legal",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const generatedAt = new Date(graph.quality.generated_at);

  const staticEntries: MetadataRoute.Sitemap = STATIC_ROUTES.map((route) => ({
    url: `${SITE_URL}/${route ? `${route}/` : ""}`,
    lastModified: generatedAt,
    changeFrequency: route === "" ? "weekly" : "monthly",
    priority: route === "" ? 1 : 0.7,
  }));

  const nodeEntries: MetadataRoute.Sitemap = graph.nodes.map((node) => ({
    url: `${SITE_URL}/${ROUTE_PREFIX[node.entity_type]}/${node.slug}/`,
    lastModified: new Date(node.updated_date ?? graph.quality.generated_at),
    changeFrequency: "monthly",
    priority: 0.5,
  }));

  const frameworkEntries: MetadataRoute.Sitemap = graph.frameworks.map((f) => ({
    url: `${SITE_URL}/frameworks/${f.slug}/`,
    lastModified: generatedAt,
    changeFrequency: "monthly",
    priority: 0.5,
  }));

  return [...staticEntries, ...nodeEntries, ...frameworkEntries];
}
