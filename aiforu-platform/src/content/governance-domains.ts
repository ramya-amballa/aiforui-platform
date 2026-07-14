import type { GovernanceDomain } from "@/types";

/**
 * The full governance domain capability map: thirteen domains across
 * four clusters, all live as full pages from launch. This is a
 * living-platform architecture, so the page and route for each domain
 * already exist; adding depth later never requires a navigation or
 * routing change.
 *
 * To add a fourteenth domain: append an entry with an existing
 * `cluster` id. To introduce a fifth cluster, add it to
 * governance-clusters.ts first.
 */
export const governanceDomains: GovernanceDomain[] = [
  // ---- Emerging Technology Governance ----
  {
    slug: "ai-governance",
    name: "AI Governance",
    shortName: "AI Governance",
    cluster: "emerging-technology-governance",
    eyebrow: "Governance Domain",
    summary: "Turning AI policy into named ownership, risk decisions and evidence, not documentation alone.",
    overview:
      "AI governance work here starts from the OPERA methodology: identifying the actual opportunity behind an AI use case, assigning named owners, applying a consistent risk evaluation model, and building the response and assurance structure that keeps pace as use cases multiply. The goal is an operating model that survives contact with a real audit or a real incident, not a policy document that sits alongside one.",
    focusAreas: [
      "AI use-case inventories and risk registers",
      "Ownership and decision-rights models for AI governance",
      "Risk evaluation criteria and escalation paths",
    ],
    whoItsFor: ["CIO", "CISO", "Board"],
    relatedEngagementSlugs: ["ai-governance-operating-model"],
    relatedInsightSlugs: ["ai-governance-board-oversight", "judgment-over-frameworks"],
    relatedResourceSlugs: ["ai-governance-maturity-framework", "ai-governance-decision-playbook"],
    featured: true,
  },
  {
    slug: "responsible-ai",
    name: "Responsible AI",
    shortName: "Responsible AI",
    cluster: "emerging-technology-governance",
    eyebrow: "Governance Domain",
    summary: "Putting fairness, transparency and human oversight into practice, not just principle.",
    overview:
      "Responsible AI principles are widely published and rarely operationalised. This work focuses on the practical mechanics: how fairness and bias are actually tested, who reviews a model before it goes live, what transparency means for the people affected by an automated decision, and where human oversight is genuinely exercised rather than nominally present.",
    focusAreas: ["Model review and sign-off processes", "Bias testing and monitoring practice"],
    whoItsFor: ["CIO", "Chief Risk Officer"],
    relatedEngagementSlugs: [],
    relatedInsightSlugs: ["judgment-over-frameworks"],
    relatedResourceSlugs: ["ai-governance-decision-playbook"],
    featured: true,
  },
  {
    slug: "digital-governance",
    name: "Digital Governance",
    shortName: "Digital Governance",
    cluster: "emerging-technology-governance",
    eyebrow: "Governance Domain",
    summary: "Governance for digital platforms, products and data as they scale across the enterprise.",
    overview:
      "As digital platforms multiply, governance often lags behind delivery. This domain covers the ownership structures, decision rights and standards needed to keep digital products, platforms and data assets accountable to a single governance model rather than a patchwork of team-level conventions.",
    focusAreas: ["Digital platform ownership models", "Cross-functional governance standards"],
    whoItsFor: ["CIO", "Enterprise Leadership"],
    relatedEngagementSlugs: [],
    relatedInsightSlugs: [],
    relatedResourceSlugs: [],
    featured: false,
  },

  // ---- Risk, Cyber & Assurance ----
  {
    slug: "technology-risk",
    name: "Technology Risk",
    shortName: "Technology Risk",
    cluster: "risk-cyber-assurance",
    eyebrow: "Governance Domain",
    summary: "Risk appetite, control ownership and reporting that hold up under audit and regulatory review.",
    overview:
      "Technology risk functions frequently have a risk taxonomy and a control library that no longer reflect actual exposure. This work resets the taxonomy against real risk, restates appetite in language engineering and business teams can apply, and puts control ownership at the level where the control is actually operated.",
    focusAreas: ["Technology risk taxonomy and control libraries", "Risk appetite statements", "Assurance evidence cycles"],
    whoItsFor: ["Chief Risk Officer", "Board Members"],
    relatedEngagementSlugs: ["technology-risk-assurance"],
    relatedInsightSlugs: ["technology-risk-appetite", "governance-debt"],
    relatedResourceSlugs: ["technology-risk-whitepaper"],
    featured: true,
  },
  {
    slug: "cyber-governance",
    name: "Cyber Governance",
    shortName: "Cyber Governance",
    cluster: "risk-cyber-assurance",
    eyebrow: "Governance Domain",
    summary: "Governance structures behind cyber security programmes, including regulatory assessment readiness.",
    overview:
      "Cyber security controls are only as strong as the governance behind them: who owns which control, how gaps are prioritised, and how the organisation prepares for formal assessment against a specific standard, whether that is PCI DSS, ENS or an internal control framework. This domain covers that governance layer directly.",
    focusAreas: ["Control ownership and gap prioritisation", "Regulatory and standards-based assessment readiness", "Assurance evidence structures"],
    whoItsFor: ["CISO", "Chief Risk Officer"],
    relatedEngagementSlugs: ["ens-readiness-assessment", "pci-dss-advisory"],
    relatedInsightSlugs: [],
    relatedResourceSlugs: ["cyber-governance-reference-architecture"],
    featured: true,
  },
  {
    slug: "enterprise-risk-governance",
    name: "Enterprise Risk Governance",
    shortName: "Enterprise Risk Governance",
    cluster: "risk-cyber-assurance",
    eyebrow: "Governance Domain",
    summary: "Enterprise-wide risk governance that connects technology, operational and strategic risk.",
    overview:
      "Technology risk rarely stays contained to technology. This domain connects technology risk governance to the wider enterprise risk framework, so risk appetite, escalation and board reporting are consistent across risk categories rather than siloed by function.",
    focusAreas: ["Enterprise risk taxonomy alignment", "Cross-functional escalation paths"],
    whoItsFor: ["Chief Risk Officer", "Board Members"],
    relatedEngagementSlugs: [],
    relatedInsightSlugs: ["governance-debt"],
    relatedResourceSlugs: [],
    featured: false,
  },
  {
    slug: "audit-readiness",
    name: "Audit Readiness",
    shortName: "Audit Readiness",
    cluster: "risk-cyber-assurance",
    eyebrow: "Governance Domain",
    summary: "Building the evidence trail ahead of audit, rather than reconstructing it during one.",
    overview:
      "Audit readiness is usually treated as a pre-audit scramble. This domain treats it as an operating discipline: evidence is captured as controls run, ownership is documented as decisions are made, and the audit itself becomes a validation exercise rather than a discovery process.",
    focusAreas: ["Continuous evidence capture", "Control documentation standards"],
    whoItsFor: ["Chief Compliance Officer", "CISO"],
    relatedEngagementSlugs: [],
    relatedInsightSlugs: [],
    relatedResourceSlugs: ["audit-readiness-checklist"],
    featured: false,
  },

  // ---- Regulatory, Privacy & Third-Party ----
  {
    slug: "privacy-data-governance",
    name: "Privacy & Data Governance",
    shortName: "Privacy & Data Governance",
    cluster: "regulatory-privacy-third-party",
    eyebrow: "Governance Domain",
    summary: "Data governance built around actual data flows, not a policy document describing intended ones.",
    overview:
      "Privacy and data governance programmes often describe how data should move without reflecting how it actually does. This domain starts with mapping real data flows and processing activities, then builds ownership, classification and retention practice around what is actually found.",
    focusAreas: ["Data flow and processing inventories", "Data ownership and classification models"],
    whoItsFor: ["Chief Compliance Officer", "Board Members"],
    relatedEngagementSlugs: [],
    relatedInsightSlugs: [],
    relatedResourceSlugs: [],
    featured: false,
  },
  {
    slug: "dpdp-governance-readiness",
    name: "DPDP Governance & Readiness",
    shortName: "DPDP Readiness",
    cluster: "regulatory-privacy-third-party",
    eyebrow: "Governance Domain",
    summary: "Readiness for India's Digital Personal Data Protection Act, built as governance, not a checklist.",
    overview:
      "The DPDP Act sets specific obligations around consent, purpose limitation and data principal rights. This domain translates those obligations into a governance structure: accountable owners for consent management and grievance redressal, and the evidence base a Data Protection Officer or equivalent function needs to demonstrate ongoing compliance, not just initial readiness.",
    focusAreas: ["Data processing and consent inventories", "DPDP gap assessment against current practice", "Accountability structures for ongoing compliance"],
    whoItsFor: ["Chief Compliance Officer", "Enterprise Leadership"],
    relatedEngagementSlugs: ["dpdp-governance-readiness-programme"],
    relatedInsightSlugs: ["dpdp-readiness-priorities"],
    relatedResourceSlugs: ["dpdp-readiness-briefing", "dpdp-compliance-toolkit"],
    featured: true,
  },
  {
    slug: "third-party-governance",
    name: "Third Party Governance",
    shortName: "Third Party Governance",
    cluster: "regulatory-privacy-third-party",
    eyebrow: "Governance Domain",
    summary: "Vendor governance across the full lifecycle, with ownership assigned at every stage.",
    overview:
      "Third-party risk is frequently assessed once, at onboarding, and rarely revisited. This domain covers the full vendor lifecycle: risk segmentation by criticality and data access, proportional assessment criteria, and a monitoring cadence that catches drift between what a vendor contracted to do and what it actually does.",
    focusAreas: ["Vendor risk segmentation", "Lifecycle ownership from onboarding to exit"],
    whoItsFor: ["Chief Compliance Officer", "CISO"],
    relatedEngagementSlugs: ["third-party-governance-framework"],
    relatedInsightSlugs: ["third-party-risk-in-regulated-sectors", "third-party-accountability-gap"],
    relatedResourceSlugs: ["third-party-risk-assessment-checklist"],
    featured: true,
  },
  {
    slug: "operational-compliance",
    name: "Operational Compliance",
    shortName: "Operational Compliance",
    cluster: "regulatory-privacy-third-party",
    eyebrow: "Governance Domain",
    summary: "Compliance obligations translated into operational routines that teams actually follow.",
    overview:
      "A compliance obligation that exists only in a policy document is not being met. This domain focuses on converting regulatory and contractual obligations into operational routines, owned by named teams, with the evidence trail to demonstrate they are being followed.",
    focusAreas: ["Obligation-to-routine translation", "Ownership at the team level"],
    whoItsFor: ["Chief Compliance Officer"],
    relatedEngagementSlugs: [],
    relatedInsightSlugs: [],
    relatedResourceSlugs: ["dpdp-compliance-toolkit"],
    featured: false,
  },

  // ---- Public Sector & Transformation ----
  {
    slug: "government-digital-governance",
    name: "Government Digital Governance",
    shortName: "Government Digital Governance",
    cluster: "public-sector-transformation",
    eyebrow: "Governance Domain",
    summary: "Digital and AI governance structured for public-sector accountability, procurement and oversight.",
    overview:
      "Government and public-sector digital programmes operate under a different accountability model than private enterprise: statutory obligation, procurement rules, legislative and public scrutiny. This domain designs governance models that hold up against that model specifically, not a private-sector framework adapted after the fact.",
    focusAreas: ["Statutory and policy-aligned governance models", "Cross-department and vendor ownership mapping", "Oversight-ready reporting structures"],
    whoItsFor: ["Government", "Public Sector"],
    relatedEngagementSlugs: ["government-digital-governance-programme"],
    relatedInsightSlugs: ["government-digital-governance-maturity"],
    relatedResourceSlugs: ["government-digital-governance-artefact-pack"],
    featured: true,
  },
  {
    slug: "governance-transformation",
    name: "Governance Transformation",
    shortName: "Governance Transformation",
    cluster: "public-sector-transformation",
    eyebrow: "Governance Domain",
    summary: "Redesigning governance operating models once governance debt has outpaced actual risk.",
    overview:
      "Governance debt accumulates quietly: duplicated committees, undocumented decisions, ownership that exists on paper but not in practice. This domain diagnoses where that debt has built up and redesigns the operating model around decision rights first, sequencing change so the highest-risk gaps close early.",
    focusAreas: ["Governance debt diagnostics", "Target operating model design"],
    whoItsFor: ["Enterprise Leadership", "Board Members"],
    relatedEngagementSlugs: ["enterprise-governance-transformation-programme"],
    relatedInsightSlugs: ["governance-transformation-operating-models", "judgment-over-frameworks"],
    relatedResourceSlugs: ["governance-operating-model-template"],
    featured: false,
  },
];

export function getGovernanceDomainBySlug(slug: string) {
  return governanceDomains.find((domain) => domain.slug === slug);
}

export function getGovernanceDomainsByCluster(clusterId: string) {
  return governanceDomains.filter((domain) => domain.cluster === clusterId);
}
