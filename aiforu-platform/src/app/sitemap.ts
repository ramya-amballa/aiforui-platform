import type { MetadataRoute } from "next";
import { advisoryEngagements } from "@/content/advisory-engagements";
import { governanceDomains } from "@/content/governance-domains";
import { insights } from "@/content/insights";
import { resources } from "@/content/resources";
import { site } from "@/lib/constants";

const staticRoutes = [
  "",
  "/methodology",
  "/selected-advisory-engagements",
  "/governance-domains",
  "/insights",
  "/resources",
  "/about",
  "/contact",
  "/privacy-policy",
  "/terms",
];

export default function sitemap(): MetadataRoute.Sitemap {
  const staticEntries: MetadataRoute.Sitemap = staticRoutes.map((path) => ({
    url: new URL(path, site.url).toString(),
    lastModified: new Date(),
  }));

  const engagementEntries: MetadataRoute.Sitemap = advisoryEngagements.map((engagement) => ({
    url: new URL(`/selected-advisory-engagements/${engagement.slug}`, site.url).toString(),
    lastModified: new Date(),
  }));

  const domainEntries: MetadataRoute.Sitemap = governanceDomains.map((domain) => ({
    url: new URL(`/governance-domains/${domain.slug}`, site.url).toString(),
    lastModified: new Date(),
  }));

  const insightEntries: MetadataRoute.Sitemap = insights.map((insight) => ({
    url: new URL(`/insights/${insight.slug}`, site.url).toString(),
    lastModified: new Date(insight.date),
  }));

  const resourceEntries: MetadataRoute.Sitemap = resources.map((resource) => ({
    url: new URL(`/resources/${resource.slug}`, site.url).toString(),
    lastModified: new Date(),
  }));

  return [...staticEntries, ...engagementEntries, ...domainEntries, ...insightEntries, ...resourceEntries];
}
