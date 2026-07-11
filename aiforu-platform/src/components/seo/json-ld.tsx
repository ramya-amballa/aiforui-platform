interface JsonLdProps {
  data: Record<string, unknown>;
}

/**
 * Renders a structured data block. Pass a schema.org object literal
 * (Person, Organization, Article, BreadcrumbList, etc.).
 */
export function JsonLd({ data }: JsonLdProps) {
  return (
    <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }} />
  );
}
