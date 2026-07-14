import type { Metadata } from "next";
import { site } from "@/lib/constants";

interface BuildMetadataInput {
  title: string;
  description?: string;
  path?: string;
  type?: "website" | "article";
  noIndex?: boolean;
}

/**
 * True only on a Vercel Production deployment; mirrors the check in
 * next.config.ts. Preview deployments and local dev must never be
 * indexable, regardless of what an individual page passes as `noIndex`.
 */
const isProductionDeployment = process.env.VERCEL_ENV === "production";

/**
 * Central metadata builder so every page produces consistent title
 * templates, canonical URLs and Open Graph / Twitter tags.
 */
export function buildMetadata({
  title,
  description = site.description,
  path = "/",
  type = "website",
  noIndex = false,
}: BuildMetadataInput): Metadata {
  const url = new URL(path, site.url).toString();
  const shouldIndex = isProductionDeployment && !noIndex;

  return {
    title,
    description,
    alternates: {
      canonical: url,
    },
    openGraph: {
      title,
      description,
      url,
      siteName: site.name,
      locale: site.locale,
      type,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      ...(site.twitter ? { site: site.twitter } : {}),
    },
    robots: shouldIndex
      ? { index: true, follow: true }
      : { index: false, follow: false },
  };
}
