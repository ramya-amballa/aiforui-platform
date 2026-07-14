import type { CurrentPrioritiesSnapshot } from "@/types";

/**
 * A "now page" style snapshot of active focus, not a news feed and not
 * a project list. Update `updatedAt` every time `items` changes so
 * staleness is visible in the data itself; a homepage warning can
 * later be added if this drifts too far out of date.
 */
export const currentPriorities: CurrentPrioritiesSnapshot = {
  updatedAt: "2026-07",
  items: [
    { label: "AI governance operating models", domainSlug: "ai-governance" },
    { label: "DPDP readiness for enterprise clients", domainSlug: "dpdp-governance-readiness" },
    { label: "Government digital governance advisory", domainSlug: "government-digital-governance" },
    { label: "Technology risk assurance programmes", domainSlug: "technology-risk" },
    { label: "Governance transformation and operating model redesign", domainSlug: "governance-transformation" },
  ],
};
