/**
 * Shared domain types for the AIforU&I advisory platform.
 * All copy fields are placeholder content pending Phase 2.
 */

export interface NavItem {
  label: string;
  href: string;
  description?: string;
}

export interface GovernanceDomain {
  slug: string;
  name: string;
  shortName: string;
  eyebrow: string;
  summary: string;
  overview: string;
  focusAreas: string[];
  whoItsFor: string[];
  relatedEngagementSlugs: string[];
  relatedInsightSlugs: string[];
  featured: boolean;
}

export interface AdvisoryEngagement {
  slug: string;
  title: string;
  domainSlugs: string[];
  sector: string;
  engagementType: string;
  year: string;
  summary: string;
  context: string;
  approach: string[];
  outcome: string;
  featured: boolean;
}

export interface Insight {
  slug: string;
  title: string;
  category: string;
  domainSlugs: string[];
  date: string;
  readTime: string;
  excerpt: string;
  featured: boolean;
}

export type ResourceType = "Framework" | "Checklist" | "Whitepaper" | "Template" | "Briefing";

export interface Resource {
  slug: string;
  title: string;
  type: ResourceType;
  domainSlugs: string[];
  description: string;
  featured: boolean;
}

export interface AdvisoryService {
  slug: string;
  name: string;
  summary: string;
  deliverables: string[];
}
