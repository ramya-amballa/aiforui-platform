import type { Resource } from "@/types";

/**
 * Resources: frameworks, checklists, playbooks, reference
 * architectures and toolkits. Designed as the platform's largest
 * long-term collection: `type` and `accessTier` drive the filters on
 * /resources so this can grow to hundreds of entries without a
 * redesign. `accessTier: "Premium"` is a labelling placeholder only;
 * no gating or paywall is wired up yet.
 */
export const resources: Resource[] = [
  {
    slug: "ai-governance-maturity-framework",
    title: "AI Governance Maturity Framework",
    type: "Framework",
    accessTier: "Free",
    domainSlugs: ["ai-governance"],
    description:
      "A structured way to assess where an organisation's AI governance actually stands, across ownership, risk evaluation and assurance, built on the OPERA methodology.",
    featured: true,
  },
  {
    slug: "ai-governance-decision-playbook",
    title: "AI Governance Decision Playbook",
    type: "Playbook",
    accessTier: "Premium",
    domainSlugs: ["ai-governance", "responsible-ai"],
    description:
      "A working playbook for the specific decisions AI governance requires: use-case risk evaluation, escalation triggers and sign-off criteria.",
    featured: true,
  },
  {
    slug: "third-party-risk-assessment-checklist",
    title: "Third-Party Risk Assessment Checklist",
    type: "Checklist",
    accessTier: "Free",
    domainSlugs: ["third-party-governance"],
    description:
      "A checklist for assessing vendor risk proportional to criticality and data access, covering onboarding through ongoing monitoring.",
    featured: true,
  },
  {
    slug: "dpdp-readiness-briefing",
    title: "DPDP Readiness Briefing",
    type: "Briefing",
    accessTier: "Free",
    domainSlugs: ["dpdp-governance-readiness"],
    description:
      "A concise briefing on India's Digital Personal Data Protection Act, framed around the governance decisions it actually requires organisations to make.",
    featured: true,
  },
  {
    slug: "dpdp-compliance-toolkit",
    title: "DPDP Compliance Toolkit",
    type: "Toolkit",
    accessTier: "Premium",
    domainSlugs: ["dpdp-governance-readiness", "operational-compliance"],
    description:
      "Templates and working documents for DPDP compliance: data processing inventory, consent mapping and accountability structure.",
    featured: false,
  },
  {
    slug: "governance-operating-model-template",
    title: "Governance Operating Model Template",
    type: "Template",
    accessTier: "Premium",
    domainSlugs: ["governance-transformation"],
    description:
      "A working template for documenting decision rights, ownership and escalation paths as part of a governance operating model redesign.",
    featured: false,
  },
  {
    slug: "technology-risk-whitepaper",
    title: "Technology Risk Whitepaper",
    type: "Whitepaper",
    accessTier: "Free",
    domainSlugs: ["technology-risk"],
    description:
      "A whitepaper on building technology risk appetite statements and control ownership models that hold up under audit.",
    featured: false,
  },
  {
    slug: "cyber-governance-reference-architecture",
    title: "Cyber Governance Reference Architecture",
    type: "Reference Architecture",
    accessTier: "Premium",
    domainSlugs: ["cyber-governance"],
    description:
      "A reference architecture for the governance layer behind a cyber security programme: control ownership, gap prioritisation and assessment readiness.",
    featured: false,
  },
  {
    slug: "government-digital-governance-artefact-pack",
    title: "Government Digital Governance Artefact Pack",
    type: "Toolkit",
    accessTier: "Free",
    domainSlugs: ["government-digital-governance"],
    description:
      "A set of governance artefacts adapted for public-sector accountability: ownership maps, oversight reporting templates and statutory alignment checklists.",
    featured: true,
  },
  {
    slug: "audit-readiness-checklist",
    title: "Audit Readiness Checklist",
    type: "Checklist",
    accessTier: "Free",
    domainSlugs: ["audit-readiness"],
    description:
      "A checklist for building continuous audit evidence into day-to-day control operation, so audit becomes validation rather than discovery.",
    featured: false,
  },
];

export function getResourceBySlug(slug: string) {
  return resources.find((resource) => resource.slug === slug);
}
