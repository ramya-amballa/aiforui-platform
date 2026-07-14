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
      "Built on the OPERA methodology: named owners, a consistent risk evaluation model, and an assurance structure that keeps pace as use cases multiply. The goal is an operating model that survives a real audit, not a policy document that sits beside one.",
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
      "Responsible AI principles are widely published and rarely operationalised. This covers the mechanics: how bias is actually tested, who signs off a model before launch, and where human oversight is genuinely exercised, not nominally present.",
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
      "Digital platforms usually multiply faster than governance can track them. This covers the ownership structures and decision rights that keep products, platforms and data assets accountable to one governance model, not a patchwork of team conventions.",
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
      "Most risk taxonomies and control libraries drift from actual exposure over time. This resets the taxonomy against real risk, restates appetite in language engineering teams can apply, and puts control ownership where the control is actually operated.",
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
      "Cyber controls are only as strong as the governance behind them: control ownership, gap prioritisation, and readiness for formal assessment against a standard such as PCI DSS or ENS. This covers that governance layer directly.",
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
      "Technology risk rarely stays contained to technology. This connects it to the wider enterprise risk framework, so appetite, escalation and board reporting stay consistent across categories rather than siloed by function.",
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
      "Audit readiness is usually a pre-audit scramble. Treated as an operating discipline instead, evidence is captured as controls run, so the audit becomes validation, not discovery.",
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
      "Privacy programmes often describe how data should move, not how it actually does. This starts by mapping real data flows, then builds ownership, classification and retention practice around what is actually found.",
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
      "The DPDP Act sets specific obligations on consent, purpose limitation and data principal rights. This translates them into governance: accountable owners for consent and grievance redressal, and the evidence base a DPO needs to demonstrate ongoing compliance, not just initial readiness.",
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
      "Third-party risk is usually assessed once, at onboarding, and rarely revisited. This covers the full lifecycle: risk segmentation by criticality, proportional assessment criteria, and monitoring that catches drift between contracted and actual practice.",
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
      "A compliance obligation that exists only in a policy document is not being met. This converts regulatory and contractual obligations into operational routines, owned by named teams, with evidence they are followed.",
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
      "Government digital programmes answer to a different accountability model than private enterprise: statutory obligation, procurement rules, legislative and public scrutiny. Governance is designed against that model directly, not adapted from a private-sector template.",
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
      "Governance debt accumulates quietly: duplicated committees, undocumented decisions, ownership that exists on paper but not in practice. This diagnoses where it has built up and redesigns around decision rights first, closing the highest-risk gaps early.",
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
