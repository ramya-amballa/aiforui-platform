import type { AdvisoryEngagement } from "@/types";

/**
 * Selected Advisory Engagements. This is placeholder data shaping the
 * reusable engagement template at /selected-advisory-engagements/[slug].
 * Real engagement summaries (appropriately anonymised) land in Phase 2.
 */
export const advisoryEngagements: AdvisoryEngagement[] = [
  {
    slug: "government-digital-governance-programme",
    title: "[Engagement Title Placeholder — Government Digital Governance]",
    domainSlugs: ["government-digital-governance"],
    sector: "Government / Public Sector",
    engagementType: "[Engagement Type Placeholder]",
    year: "[Year Placeholder]",
    summary: "[Engagement Summary Placeholder]",
    context: "[Engagement Context Placeholder]",
    approach: ["[Approach Step Placeholder 1]", "[Approach Step Placeholder 2]", "[Approach Step Placeholder 3]"],
    outcome: "[Engagement Outcome Placeholder]",
    featured: true,
  },
  {
    slug: "ai-governance-operating-model",
    title: "[Engagement Title Placeholder — AI Governance]",
    domainSlugs: ["ai-governance"],
    sector: "Technology",
    engagementType: "[Engagement Type Placeholder]",
    year: "[Year Placeholder]",
    summary: "[Engagement Summary Placeholder]",
    context: "[Engagement Context Placeholder]",
    approach: ["[Approach Step Placeholder 1]", "[Approach Step Placeholder 2]", "[Approach Step Placeholder 3]"],
    outcome: "[Engagement Outcome Placeholder]",
    featured: true,
  },
  {
    slug: "technology-risk-assurance",
    title: "[Engagement Title Placeholder — Technology Risk]",
    domainSlugs: ["technology-risk"],
    sector: "Financial Services",
    engagementType: "[Engagement Type Placeholder]",
    year: "[Year Placeholder]",
    summary: "[Engagement Summary Placeholder]",
    context: "[Engagement Context Placeholder]",
    approach: ["[Approach Step Placeholder 1]", "[Approach Step Placeholder 2]", "[Approach Step Placeholder 3]"],
    outcome: "[Engagement Outcome Placeholder]",
    featured: true,
  },
  {
    slug: "third-party-governance-framework",
    title: "[Engagement Title Placeholder — Third Party Governance]",
    domainSlugs: ["third-party-governance"],
    sector: "Healthcare",
    engagementType: "[Engagement Type Placeholder]",
    year: "[Year Placeholder]",
    summary: "[Engagement Summary Placeholder]",
    context: "[Engagement Context Placeholder]",
    approach: ["[Approach Step Placeholder 1]", "[Approach Step Placeholder 2]", "[Approach Step Placeholder 3]"],
    outcome: "[Engagement Outcome Placeholder]",
    featured: false,
  },
  {
    slug: "dpdp-governance-readiness-programme",
    title: "[Engagement Title Placeholder — DPDP Governance]",
    domainSlugs: ["dpdp-governance-readiness"],
    sector: "Enterprise Leadership",
    engagementType: "[Engagement Type Placeholder]",
    year: "[Year Placeholder]",
    summary: "[Engagement Summary Placeholder]",
    context: "[Engagement Context Placeholder]",
    approach: ["[Approach Step Placeholder 1]", "[Approach Step Placeholder 2]", "[Approach Step Placeholder 3]"],
    outcome: "[Engagement Outcome Placeholder]",
    featured: false,
  },
  {
    slug: "ens-readiness-assessment",
    title: "[Engagement Title Placeholder — ENS Readiness]",
    domainSlugs: ["cyber-governance"],
    sector: "Government / Public Sector",
    engagementType: "[Engagement Type Placeholder]",
    year: "[Year Placeholder]",
    summary: "[Engagement Summary Placeholder]",
    context: "[Engagement Context Placeholder]",
    approach: ["[Approach Step Placeholder 1]", "[Approach Step Placeholder 2]", "[Approach Step Placeholder 3]"],
    outcome: "[Engagement Outcome Placeholder]",
    featured: false,
  },
  {
    slug: "pci-dss-advisory",
    title: "[Engagement Title Placeholder — PCI DSS]",
    domainSlugs: ["cyber-governance"],
    sector: "Financial Services",
    engagementType: "[Engagement Type Placeholder]",
    year: "[Year Placeholder]",
    summary: "[Engagement Summary Placeholder]",
    context: "[Engagement Context Placeholder]",
    approach: ["[Approach Step Placeholder 1]", "[Approach Step Placeholder 2]", "[Approach Step Placeholder 3]"],
    outcome: "[Engagement Outcome Placeholder]",
    featured: false,
  },
];

export function getAdvisoryEngagementBySlug(slug: string) {
  return advisoryEngagements.find((engagement) => engagement.slug === slug);
}
