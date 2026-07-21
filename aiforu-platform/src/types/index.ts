/**
 * Shared domain types for the AIforU&I advisory platform.
 *
 * This is a living-platform architecture: every collection below is
 * additive-only by design. New engagements, domains, insights and
 * resources are appended to content/*.ts without touching page or
 * component code; see content/README.md for the extension contract.
 */

export interface NavItem {
  label: string;
  href: string;
  description?: string;
}

export type GovernanceClusterId =
  | "emerging-technology-governance"
  | "risk-cyber-assurance"
  | "regulatory-privacy-third-party"
  | "public-sector-transformation";

export interface GovernanceCluster {
  id: GovernanceClusterId;
  name: string;
  description: string;
}

export interface GovernanceDomain {
  slug: string;
  name: string;
  shortName: string;
  cluster: GovernanceClusterId;
  eyebrow: string;
  summary: string;
  overview: string;
  focusAreas: string[];
  whoItsFor: string[];
  relatedEngagementSlugs: string[];
  relatedInsightSlugs: string[];
  relatedResourceSlugs: string[];
  featured: boolean;
}

/**
 * Government work, enterprise consulting-style engagements and
 * standalone strategic advisory assignments all live in the same
 * collection, distinguished by `track` rather than separate content
 * types, so they share one template and one taxonomy.
 *
 * This describes engagement areas: real methodology, real deliverables,
 * real scope of practice. It does not claim specific client instances.
 * `client`, `sector`, `year` and `outcome` are reserved, optional fields
 * for named, verified engagements once cleared for public reference;
 * the detail template renders them only when present, so adding a real
 * case study later is a data-only change.
 */
export type EngagementTrack = "Government" | "Enterprise Advisory" | "Strategic Programme";

export interface AdvisoryEngagement {
  slug: string;
  title: string;
  track: EngagementTrack;
  domainSlugs: string[];
  focus: string;
  approach: string[];
  deliverables: string[];
  featured: boolean;
  client?: string;
  sector?: string;
  year?: string;
  outcome?: string;
}

/**
 * `format` separates original-thinking pieces ("Point of View") from
 * shorter operational notes and briefings, without splitting Insights
 * into a separate content type. The homepage's signature Point of
 * View section is simply a filtered, featured slice of this same
 * collection.
 */
export type InsightFormat = "Point of View" | "Governance Note" | "Briefing" | "Field Note";

export interface Insight {
  slug: string;
  title: string;
  format: InsightFormat;
  category: string;
  domainSlugs: string[];
  readTime: string;
  excerpt: string;
  body: string[];
  featured: boolean;
}

export type ResourceType =
  | "Executive Guide"
  | "Framework"
  | "Checklist"
  | "Whitepaper"
  | "Template"
  | "Briefing"
  | "Playbook"
  | "Reference Architecture"
  | "Toolkit";

export type ResourceAccessTier = "Free" | "Premium" | "Coming Soon";

export interface Resource {
  slug: string;
  title: string;
  type: ResourceType;
  accessTier: ResourceAccessTier;
  domainSlugs: string[];
  description: string;
  featured: boolean;
}

/**
 * A single dated snapshot of what the practice is actively focused on
 * right now: the homepage "Current Advisory Priorities" section.
 * Update `updatedAt` whenever `items` changes so staleness is visible
 * in the data itself, not just in the rendered page.
 */
export interface CurrentPriority {
  label: string;
  domainSlug?: string;
}

export interface CurrentPrioritiesSnapshot {
  updatedAt: string;
  items: CurrentPriority[];
}
