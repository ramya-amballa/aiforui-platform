import type { GovernanceCluster } from "@/types";

/**
 * The four groupings of the governance domain capability map. Clusters
 * are a fixed, coarse taxonomy; domains are the unit that grows over
 * time. Adding a new domain means adding one entry to
 * governance-domains.ts with an existing cluster id; it does not
 * require a new cluster or a navigation change.
 */
export const governanceClusters: GovernanceCluster[] = [
  {
    id: "emerging-technology-governance",
    name: "Emerging Technology Governance",
    description: "AI governance, responsible AI and digital governance as adoption accelerates ahead of policy.",
  },
  {
    id: "risk-cyber-assurance",
    name: "Risk, Cyber & Assurance",
    description: "Technology risk, cyber governance, enterprise risk and audit readiness, held to one consistent standard.",
  },
  {
    id: "regulatory-privacy-third-party",
    name: "Regulatory, Privacy & Third-Party",
    description: "Privacy, DPDP readiness, third-party governance and operational compliance, from obligation to evidence.",
  },
  {
    id: "public-sector-transformation",
    name: "Public Sector & Transformation",
    description: "Government digital governance and enterprise governance transformation, built for public accountability.",
  },
];

export function getGovernanceCluster(id: string) {
  return governanceClusters.find((cluster) => cluster.id === id);
}
