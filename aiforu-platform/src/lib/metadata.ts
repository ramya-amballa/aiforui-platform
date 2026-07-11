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
      site: site.twitter,
    },
    robots: noIndex
      ? { index: false, follow: false }
      : { index: true, follow: true },
  };
}
