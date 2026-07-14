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
  questions: string[];
  activities: string[];
  artefacts: string[];
  outcome: string;
}

export const operaStages: OperaStage[] = [
  {
    letter: "O",
    name: "Opportunity",
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
    questions: ["Who is accountable for this AI system?", "Who approves governance decisions?"],
    activities: ["Ownership assignment", "Accountability model", "Governance roles"],
    artefacts: ["Ownership matrix", "RACI", "Escalation framework"],
    outcome: "Named ownership",
  },
  {
    letter: "E",
    name: "Evaluation",
    questions: ["What is the risk exposure?", "What is the business impact of getting this wrong?"],
    activities: ["Risk assessment", "Control analysis", "Regulatory mapping"],
    artefacts: ["Risk assessment", "Impact assessment", "Regulatory mapping"],
    outcome: "Risk visibility",
  },
  {
    letter: "R",
    name: "Response",
    questions: ["What controls are required?", "What decisions must be approved, and by whom?"],
    activities: ["Decision process", "Documentation", "Evidence generation"],
    artefacts: ["Decision log", "Approvals", "Evidence register"],
    outcome: "Controlled deployment",
  },
  {
    letter: "A",
    name: "Assurance",
    questions: ["How do we know it is working?", "What does leadership need to see?"],
    activities: ["Monitoring", "Metrics", "Governance review"],
    artefacts: ["KRI dashboard", "Audit pack", "Board briefings"],
    outcome: "Audit-ready assurance",
  },
];

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
