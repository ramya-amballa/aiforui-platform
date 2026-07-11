import type { Insight } from "@/types";

/**
 * Insights (editorial/thought-leadership articles). Placeholder set
 * driving /insights and the /insights/[slug] template.
 */
export const insights: Insight[] = [
  {
    slug: "ai-governance-board-oversight",
    title: "[Insight Title Placeholder — AI Governance & Board Oversight]",
    category: "AI Governance",
    domainSlugs: ["ai-governance"],
    date: "2026-01-01",
    readTime: "[Read Time Placeholder]",
    excerpt: "[Insight Excerpt Placeholder]",
    featured: true,
  },
  {
    slug: "third-party-risk-in-regulated-sectors",
    title: "[Insight Title Placeholder — Third Party Risk]",
    category: "Third Party Governance",
    domainSlugs: ["third-party-governance"],
    date: "2026-01-01",
    readTime: "[Read Time Placeholder]",
    excerpt: "[Insight Excerpt Placeholder]",
    featured: true,
  },
  {
    slug: "dpdp-readiness-priorities",
    title: "[Insight Title Placeholder — DPDP Readiness Priorities]",
    category: "DPDP Governance & Readiness",
    domainSlugs: ["dpdp-governance-readiness"],
    date: "2026-01-01",
    readTime: "[Read Time Placeholder]",
    excerpt: "[Insight Excerpt Placeholder]",
    featured: true,
  },
  {
    slug: "technology-risk-appetite",
    title: "[Insight Title Placeholder — Technology Risk Appetite]",
    category: "Technology Risk",
    domainSlugs: ["technology-risk"],
    date: "2026-01-01",
    readTime: "[Read Time Placeholder]",
    excerpt: "[Insight Excerpt Placeholder]",
    featured: false,
  },
  {
    slug: "government-digital-governance-maturity",
    title: "[Insight Title Placeholder — Government Digital Governance Maturity]",
    category: "Government Digital Governance",
    domainSlugs: ["government-digital-governance"],
    date: "2026-01-01",
    readTime: "[Read Time Placeholder]",
    excerpt: "[Insight Excerpt Placeholder]",
    featured: false,
  },
  {
    slug: "governance-transformation-operating-models",
    title: "[Insight Title Placeholder — Governance Transformation]",
    category: "Governance Transformation",
    domainSlugs: ["governance-transformation"],
    date: "2026-01-01",
    readTime: "[Read Time Placeholder]",
    excerpt: "[Insight Excerpt Placeholder]",
    featured: false,
  },
];

export function getInsightBySlug(slug: string) {
  return insights.find((insight) => insight.slug === slug);
}
