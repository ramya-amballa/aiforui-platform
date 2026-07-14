import type { AdvisoryEngagement } from "@/types";

/**
 * Selected Engagement Areas. This spans government initiatives,
 * enterprise advisory work and standalone strategic programmes; `track`
 * distinguishes them within one collection and one template at
 * /selected-advisory-engagements/[slug].
 *
 * Each entry describes a real area of practice: how the work is
 * approached and what it typically produces. It does not attribute
 * outcomes to a named or implied client. Named, verified engagements
 * (client, sector, year, outcome) are added as optional fields on the
 * relevant entry once cleared for public reference, without any change
 * to the page template.
 */
export const advisoryEngagements: AdvisoryEngagement[] = [
  {
    slug: "government-digital-governance-programme",
    title: "Government Digital Governance Programme Design",
    track: "Government",
    domainSlugs: ["government-digital-governance"],
    focus:
      "Structuring digital and AI governance for government bodies, where accountability, procurement rules and public trust carry different weight than in the private sector.",
    approach: [
      "Map the mandate against existing statutory and policy obligations before proposing a governance model.",
      "Identify ownership across departments, vendors and oversight bodies; formalise decision rights in writing.",
      "Evaluate risk against public-sector thresholds, including reputational and constitutional exposure.",
      "Design an assurance cadence that produces evidence suitable for legislative and public scrutiny.",
    ],
    deliverables: [
      "Governance operating model for public-sector accountability lines",
      "Ownership and decision-rights map across departments and vendors",
      "Assurance and reporting cadence aligned to oversight requirements",
    ],
    featured: true,
  },
  {
    slug: "ai-governance-operating-model",
    title: "AI Governance Operating Model Design",
    track: "Enterprise Advisory",
    domainSlugs: ["ai-governance"],
    focus: "Turning an AI governance policy into day-to-day ownership, risk decisions and evidence, using OPERA.",
    approach: [
      "Opportunity: catalogue current and planned AI use cases against business intent, not just capability.",
      "People: assign a named owner for each use case and each governance decision.",
      "Evaluation: apply a consistent risk model across use cases, calibrated to impact and reversibility.",
      "Response and Assurance: define escalation paths, approval gates and the ongoing evidence trail.",
    ],
    deliverables: [
      "AI use-case inventory and risk register",
      "RACI-based ownership model for AI governance decisions",
      "Risk evaluation criteria and approval workflow",
      "Board- and executive-level reporting template",
    ],
    featured: true,
  },
  {
    slug: "technology-risk-assurance",
    title: "Technology Risk Assurance Programme",
    track: "Enterprise Advisory",
    domainSlugs: ["technology-risk"],
    focus: "Building a technology risk assurance function where appetite, control ownership and reporting hold up under audit.",
    approach: [
      "Assess the current risk taxonomy and control library against actual exposure.",
      "Restate risk appetite in language engineering and business teams can apply, not just risk committees.",
      "Establish control ownership at the level where the control is actually operated.",
      "Build an assurance cycle that produces evidence ahead of audit, not reconstructed after it.",
    ],
    deliverables: [
      "Technology risk taxonomy and control library review",
      "Risk appetite statement in operational language",
      "Control ownership and testing schedule",
    ],
    featured: true,
  },
  {
    slug: "third-party-governance-framework",
    title: "Third-Party Governance Framework Design",
    track: "Enterprise Advisory",
    domainSlugs: ["third-party-governance"],
    focus: "Covering the full vendor lifecycle, from onboarding risk assessment to exit, with clear internal ownership at each stage.",
    approach: [
      "Segment vendors by criticality and data access, rather than one assessment for every vendor.",
      "Define assessment criteria proportional to that segmentation: security, resilience, data handling, concentration risk.",
      "Assign internal ownership for each lifecycle stage, including contract, monitoring and exit.",
      "Build a monitoring cadence that catches drift between contracted and actual vendor practice.",
    ],
    deliverables: [
      "Vendor risk segmentation model",
      "Third-party risk assessment framework and questionnaire set",
      "Ongoing monitoring and re-assessment schedule",
      "Exit and offboarding governance checklist",
    ],
    featured: false,
  },
  {
    slug: "dpdp-governance-readiness-programme",
    title: "DPDP Governance Readiness Programme",
    track: "Strategic Programme",
    domainSlugs: ["dpdp-governance-readiness"],
    focus: "Translating DPDP statutory obligations into a governance structure, not just a compliance checklist.",
    approach: [
      "Map personal data flows against DPDP obligations: consent, purpose limitation, data principal rights.",
      "Identify gaps between current practice and the Act's requirements, ranked by exposure.",
      "Assign accountable owners for consent management, grievance redressal and breach response.",
      "Build the evidence structure a DPO or equivalent function needs to demonstrate ongoing compliance.",
    ],
    deliverables: [
      "DPDP readiness gap assessment",
      "Data processing and consent inventory",
      "Governance and accountability structure for ongoing compliance",
    ],
    featured: false,
  },
  {
    slug: "ens-readiness-assessment",
    title: "ENS Readiness Assessment",
    track: "Government",
    domainSlugs: ["cyber-governance"],
    focus: "Assessing readiness against Esquema Nacional de Seguridad (ENS) for organisations operating in Spanish public-sector systems.",
    approach: [
      "Determine the applicable ENS security category and control baseline.",
      "Assess current controls against that baseline, separating documented policy from operating practice.",
      "Prioritise remediation by the categories with the greatest gap to the required level.",
      "Prepare the evidence structure required for formal ENS conformity assessment.",
    ],
    deliverables: [
      "ENS applicability and category determination",
      "Control gap assessment against the ENS baseline",
      "Remediation roadmap prioritised by security category",
    ],
    featured: false,
  },
  {
    slug: "pci-dss-advisory",
    title: "PCI DSS Advisory",
    track: "Enterprise Advisory",
    domainSlugs: ["cyber-governance"],
    focus: "Advising organisations that handle payment card data through PCI DSS scoping and assessment preparation.",
    approach: [
      "Define and validate the cardholder data environment scope before assessing controls.",
      "Assess existing controls against PCI DSS requirements; identify compensating controls where relevant.",
      "Sequence remediation to the highest-risk gaps ahead of a Qualified Security Assessor engagement.",
      "Build the evidence and documentation structure the assessment will require.",
    ],
    deliverables: [
      "Cardholder data environment scoping document",
      "Control gap assessment against PCI DSS requirements",
      "Remediation roadmap and assessment-readiness evidence pack",
    ],
    featured: false,
  },
  {
    slug: "enterprise-governance-transformation-programme",
    title: "Enterprise Governance Transformation Programme",
    track: "Strategic Programme",
    domainSlugs: ["governance-transformation"],
    focus: "Redesigning governance operating models once debt, unclear ownership or fragmented reporting has outpaced actual risk.",
    approach: [
      "Diagnose where governance debt has accumulated: duplicated committees, undocumented decisions, paper-only ownership.",
      "Redesign around decision rights first, then reporting lines, not the reverse.",
      "Sequence the transformation so the highest-risk gaps close early.",
      "Establish metrics and a reporting cadence showing whether the new model is actually being used.",
    ],
    deliverables: [
      "Governance debt diagnostic",
      "Target operating model and decision-rights map",
      "Phased transformation roadmap",
      "Governance effectiveness reporting framework",
    ],
    featured: true,
  },
];

export function getAdvisoryEngagementBySlug(slug: string) {
  return advisoryEngagements.find((engagement) => engagement.slug === slug);
}
