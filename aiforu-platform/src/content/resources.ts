import type { Resource } from "@/types";

/**
 * Downloadable / reference resources. Placeholder set driving
 * /resources and the /resources/[slug] template.
 */
export const resources: Resource[] = [
  {
    slug: "ai-governance-maturity-framework",
    title: "[Resource Title Placeholder — AI Governance Maturity Framework]",
    type: "Framework",
    domainSlugs: ["ai-governance"],
    description: "[Resource Description Placeholder]",
    featured: true,
  },
  {
    slug: "third-party-risk-assessment-checklist",
    title: "[Resource Title Placeholder — Third Party Risk Assessment Checklist]",
    type: "Checklist",
    domainSlugs: ["third-party-governance"],
    description: "[Resource Description Placeholder]",
    featured: true,
  },
  {
    slug: "dpdp-readiness-briefing",
    title: "[Resource Title Placeholder — DPDP Readiness Briefing]",
    type: "Briefing",
    domainSlugs: ["dpdp-governance-readiness"],
    description: "[Resource Description Placeholder]",
    featured: true,
  },
  {
    slug: "governance-operating-model-template",
    title: "[Resource Title Placeholder — Governance Operating Model Template]",
    type: "Template",
    domainSlugs: ["governance-transformation"],
    description: "[Resource Description Placeholder]",
    featured: false,
  },
  {
    slug: "technology-risk-whitepaper",
    title: "[Resource Title Placeholder — Technology Risk Whitepaper]",
    type: "Whitepaper",
    domainSlugs: ["technology-risk"],
    description: "[Resource Description Placeholder]",
    featured: false,
  },
];

export function getResourceBySlug(slug: string) {
  return resources.find((resource) => resource.slug === slug);
}
