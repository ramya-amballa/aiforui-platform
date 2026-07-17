import { site } from "@/lib/constants";

/**
 * schema.org Person entity for Ramya Amballa, used on the About and
 * homepage routes to establish independent-advisor E-E-A-T signals.
 */
export function personSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "Person",
    name: site.advisorName,
    url: site.url,
    jobTitle: "Founder and Independent Advisor, AIforU&I",
    worksFor: {
      "@type": "Organization",
      name: site.name,
    },
    alumniOf: ["PwC India", "Viatris", "Wells Fargo", "JPMorgan Chase"].map((name) => ({
      "@type": "Organization",
      name,
    })),
    description: site.description,
    sameAs: [site.linkedin],
  };
}

/**
 * schema.org ProfessionalService entity for the advisory practice.
 */
export function organizationSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    name: site.name,
    url: site.url,
    founder: {
      "@type": "Person",
      name: site.advisorName,
    },
    description: site.description,
  };
}

interface BreadcrumbItem {
  name: string;
  path: string;
}

export function breadcrumbSchema(items: BreadcrumbItem[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: new URL(item.path, site.url).toString(),
    })),
  };
}

interface ArticleSchemaInput {
  title: string;
  description: string;
  path: string;
  datePublished?: string;
}

/**
 * datePublished is omitted for evergreen advisory perspectives that
 * carry no real publication date, rather than filling it with a
 * placeholder; schema.org treats it as recommended, not required, for
 * Article.
 */
export function articleSchema({ title, description, path, datePublished }: ArticleSchemaInput) {
  return {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: title,
    description,
    url: new URL(path, site.url).toString(),
    ...(datePublished ? { datePublished } : {}),
    author: {
      "@type": "Person",
      name: site.advisorName,
    },
  };
}
