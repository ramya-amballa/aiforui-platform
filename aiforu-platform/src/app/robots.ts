import type { MetadataRoute } from "next";
import { site } from "@/lib/constants";

/**
 * True only on a Vercel Production deployment; mirrors the checks in
 * next.config.ts and lib/metadata.ts. Every other environment
 * (Preview deployments, local dev) disallows all crawling.
 */
const isProductionDeployment = process.env.VERCEL_ENV === "production";

export default function robots(): MetadataRoute.Robots {
  if (!isProductionDeployment) {
    return {
      rules: {
        userAgent: "*",
        disallow: "/",
      },
    };
  }

  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: new URL("/sitemap.xml", site.url).toString(),
  };
}
