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
      "Structuring digital and AI governance for government and public-sector bodies, where accountability, procurement rules and public trust carry different weight than in the private sector.",
    approach: [
      "Map the programme's opportunity and mandate against existing statutory and policy obligations before proposing a governance model.",
      "Identify ownership across departments, vendors and oversight bodies, and formalise decision rights in writing.",
      "Evaluate risk against public-sector thresholds, not private-sector risk appetite, including reputational and constitutional exposure.",
      "Design an assurance cadence that produces evidence suitable for legislative, audit or public scrutiny.",
    ],
    deliverables: [
      "Governance operating model tailored to public-sector accountability lines",
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
    focus:
      "Building the operating model that turns an organisation's AI governance policy into day-to-day ownership, risk decisions and evidence, using the OPERA methodology.",
    approach: [
      "Opportunity: catalogue current and planned AI use cases against business intent, not just technical capability.",
      "People: assign named owners for each use case and each governance decision, so accountability does not default to a committee.",
      "Evaluation: apply a consistent risk evaluation model across use cases, calibrated to impact and reversibility.",
      "Response and Assurance: define escalation paths, approval gates and the evidence trail that supports ongoing assurance.",
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
    focus:
      "Establishing or strengthening a technology risk assurance function so that risk appetite, control ownership and reporting hold up under audit and regulatory review.",
    approach: [
      "Assess the current technology risk taxonomy and control library against the organisation's actual risk exposure.",
      "Clarify risk appetite statements in language that engineering and business teams can apply, not just risk committees.",
      "Establish control ownership at the level where the control is actually operated.",
      "Build an assurance cycle that produces defensible evidence ahead of audit, rather than reconstructing it afterward.",
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
    focus:
      "Designing a third-party governance framework that covers the full vendor lifecycle, from onboarding risk assessment through ongoing monitoring to exit, with clear internal ownership at each stage.",
    approach: [
      "Segment the vendor population by criticality and data access, rather than applying one assessment to every vendor.",
      "Define risk assessment criteria proportional to that segmentation, covering security, resilience, data handling and concentration risk.",
      "Assign internal ownership for each stage of the vendor lifecycle, including contract, monitoring and exit.",
      "Build a monitoring cadence that catches drift between contracted controls and actual vendor practice.",
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
    focus:
      "Preparing organisations for India's Digital Personal Data Protection Act by translating statutory obligations into a governance structure, not just a compliance checklist.",
    approach: [
      "Map personal data flows and processing activities against DPDP obligations, including consent, purpose limitation and data principal rights.",
      "Identify gaps between current data governance practice and what the Act requires, ranked by exposure.",
      "Assign accountable owners for consent management, grievance redressal and breach response.",
      "Build the evidence and reporting structure a Data Protection Officer or equivalent function needs to demonstrate ongoing compliance.",
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
    focus:
      "Assessing readiness against Esquema Nacional de Seguridad (ENS) requirements for organisations operating in or with Spanish public-sector systems.",
    approach: [
      "Determine the applicable ENS security category and the corresponding control baseline.",
      "Assess current controls against that baseline, distinguishing documented policy from operating practice.",
      "Prioritise remediation by the categories with the greatest gap to the required security level.",
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
    focus:
      "Advising organisations that handle payment card data through PCI DSS scoping, control implementation and assessment preparation.",
    approach: [
      "Define and validate the cardholder data environment scope before assessing controls against it.",
      "Assess existing controls against the applicable PCI DSS requirements and identify compensating controls where relevant.",
      "Sequence remediation to address the highest-risk gaps ahead of a Qualified Security Assessor engagement.",
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
    focus:
      "Redesigning enterprise governance operating models where accumulated governance debt, unclear ownership or fragmented reporting has outpaced the organisation's actual risk profile.",
    approach: [
      "Diagnose where governance debt has accumulated: duplicated committees, undocumented decisions, or ownership that exists on paper but not in practice.",
      "Redesign the operating model around decision rights first, then reporting lines, rather than the reverse.",
      "Sequence the transformation so critical risk decisions are covered early, with lower-priority structural change following.",
      "Establish the metrics and reporting cadence that let leadership see whether the new model is actually being used.",
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
