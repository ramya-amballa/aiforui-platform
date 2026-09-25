/**
 * The OPERA governance methodology: the canonical, single source of
 * truth for this content across the site. Terminology, stage order,
 * governance decision questions, activities, artefacts and business
 * outcomes are transcribed directly from the reference methodology
 * diagrams and must not be reinterpreted, simplified or renamed
 * elsewhere. Every governance page should trace back to this data.
 */

export interface OperaStage {
  letter: "O" | "P" | "E" | "R" | "A";
  name: string;
  /** The single v1.1 core question for this stage — see
   * OPERA_Methodology_v1.1_Clarifications. Used verbatim wherever a
   * stage's defining question is shown. */
  coreQuestion: string;
  questions: string[];
  activities: string[];
  artefacts: string[];
  outcome: string;
}

export const operaStages: OperaStage[] = [
  {
    letter: "O",
    name: "Opportunity",
    coreQuestion: "Why are we using AI, and what outcome are we seeking?",
    questions: [
      "What business problem are we solving?",
      "What AI capability is proposed?",
      "Who owns the business outcome?",
      "What regulatory context applies?",
    ],
    activities: ["Use case intake", "Business objectives", "Stakeholder identification"],
    artefacts: ["Use case record", "Governance track", "Business owner"],
    outcome: "Approved use case",
  },
  {
    letter: "P",
    name: "People",
    coreQuestion: "Who owns the system and the governance decisions?",
    questions: ["Who is accountable for this AI system?", "Who approves governance decisions?"],
    activities: ["Ownership assignment", "Accountability model", "Governance roles"],
    artefacts: ["Ownership matrix", "RACI", "Escalation framework"],
    outcome: "Named ownership",
  },
  {
    letter: "E",
    name: "Evaluation",
    coreQuestion: "What are the risks, and what level of exposure is the organisation prepared to consider?",
    questions: ["What is the risk exposure?", "What is the business impact of getting this wrong?"],
    activities: ["Risk assessment", "Control analysis", "Regulatory mapping"],
    artefacts: ["Risk assessment", "Impact assessment", "Regulatory mapping"],
    outcome: "Risk visibility",
  },
  {
    letter: "R",
    name: "Response",
    coreQuestion: "What controls and actions are required, and who is authorised to accept the residual risk?",
    questions: ["What controls are required?", "What decisions must be approved, and by whom?"],
    activities: ["Decision process", "Documentation", "Evidence generation"],
    artefacts: ["Decision log", "Approvals", "Evidence register"],
    outcome: "Controlled deployment",
  },
  {
    letter: "A",
    name: "Assurance",
    coreQuestion: "How do we demonstrate that the controls are working?",
    questions: ["How do we know it is working?", "What does leadership need to see?"],
    activities: ["Monitoring", "Metrics", "Governance review"],
    artefacts: ["KRI dashboard", "Audit pack", "Board briefings"],
    outcome: "Audit-ready assurance",
  },
];

export interface OperaClarification {
  title: string;
  body: string;
}

/** The three v1.1 clarifications, verbatim from
 * OPERA_Methodology_v1.1_Clarifications. */
export const operaV11Clarifications: OperaClarification[] = [
  {
    title: "Risk exposure and risk acceptance",
    body: "Evaluation and Response handle two different things. Evaluation determines the level of exposure the organisation is prepared to consider and proposes a treatment. It does not accept risk. Response is where the authorised executive makes the formal residual-risk acceptance decision, and where that decision is recorded. In practice: the appetite position and the proposed treatment come out of Evaluation. The signed acceptance, its scope and its expiry come out of Response.",
  },
  {
    title: "Incident management",
    body: "Incident management spans two stages. The incident playbook, escalation arrangements and kill switch are designed under Response, because they are required actions. They are tested under Assurance, and the evidence of their effectiveness is retained there. A kill switch that exists but has never been drilled is a Response output without an Assurance output.",
  },
  {
    title: "Regulatory mapping",
    body: "Evaluation is where applicable regulatory obligations are determined and compliance exposure is assessed. Opportunity and People still identify the business context and the accountable stakeholders, which often point to the regulatory regime in play. The obligations themselves are settled in Evaluation.",
  },
];

/** Verbatim from OPERA_Methodology_v1.1_Clarifications. */
export const operaRetiredTerminologyNote =
  "An earlier version of OPERA used the stage names Ownership, Planning, Evaluation, Review, Assurance. That terminology is retired and is not an alternative definition of OPERA. Historical posts that use it remain as dated historical versions. Current methodology pages, diagrams and case studies use Opportunity, People, Evaluation, Response, Assurance only.";

export const operaWhyItExists =
  "Most organisations do not struggle with AI frameworks. They struggle with operationalising them. OPERA provides a structured pathway from business use case through ownership, risk assessment, governance decisions and ongoing assurance.";

export const operaDesignedFor =
  "Designed for regulated and high-assurance environments, including energy, critical infrastructure, financial services, enterprise SaaS and government.";

export interface GovernanceWorkflowStep {
  step: number;
  name: string;
  detail: string;
}

export const governanceWorkflow: GovernanceWorkflowStep[] = [
  { step: 1, name: "AI Use Case Submission", detail: "Business need identified" },
  { step: 2, name: "Business & Stakeholder Intake", detail: "Objectives, stakeholders, context" },
  { step: 3, name: "Ownership Assignment", detail: "RACI, accountability, governance roles" },
  { step: 4, name: "Risk & Control Assessment", detail: "Impact, risk classification, regulatory mapping" },
  { step: 5, name: "Governance Review Decision", detail: "Approval, conditions, exceptions" },
  { step: 6, name: "Evidence & Assurance", detail: "Evidence register, monitoring, reporting" },
];

export const governanceWorkflowOutcomes = [
  "Approved use case",
  "Named ownership",
  "Risk visibility",
  "Governance decision record",
  "Audit-ready evidence",
];
