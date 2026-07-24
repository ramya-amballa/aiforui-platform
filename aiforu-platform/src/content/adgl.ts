/**
 * ADGL: AI Deployment Governance Lifecycle. AI for U&I's specialised
 * methodology for governing a specific AI system through deployment,
 * distinct from OPERA (the firm's overall advisory operating method).
 * Canonical source for all ADGL content across the site; see
 * content/README.md for the extension contract other collections follow.
 */

export interface AdglPhase {
  step: number;
  name: string;
  question: string;
  activities: string[];
  deliverables: string[];
  outcome: string;
}

export const adglPhases: AdglPhase[] = [
  {
    step: 1,
    name: "Discover",
    question: "What is actually being deployed, and why?",
    activities: [
      "Business use case intake",
      "AI system and deployment type identification",
      "Stakeholder and business owner identification",
      "Initial regulatory context scan",
    ],
    deliverables: ["Use case record", "Deployment profile", "Business owner sign-off"],
    outcome: "A named, owned deployment, not an assumption",
  },
  {
    step: 2,
    name: "Assess",
    question: "What is the risk and regulatory exposure of this specific deployment?",
    activities: [
      "Risk classification against deployment type",
      "Data sensitivity and access mapping",
      "Regulatory and policy applicability assessment",
      "Control gap analysis",
    ],
    deliverables: ["Risk assessment", "Data flow map", "Regulatory applicability matrix"],
    outcome: "Risk exposure made visible before deployment, not after",
  },
  {
    step: 3,
    name: "Govern",
    question: "What controls, approvals and ownership does this deployment require?",
    activities: [
      "Control requirements definition",
      "Approval and escalation path design",
      "Ownership and accountability assignment",
      "Governance decision documentation",
    ],
    deliverables: ["Control requirements register", "Approval record", "Ownership matrix"],
    outcome: "A governance decision on record, not a verbal go-ahead",
  },
  {
    step: 4,
    name: "Deploy",
    question: "Is this deployment actually ready for production?",
    activities: [
      "Production readiness review",
      "Control implementation verification",
      "Deployment gate sign-off",
      "Rollback and incident-response planning",
    ],
    deliverables: ["Production readiness checklist", "Deployment gate approval", "Incident-response plan"],
    outcome: "A controlled go-live, with a documented gate behind it",
  },
  {
    step: 5,
    name: "Operate",
    question: "How do we know this deployment is still behaving as governed?",
    activities: [
      "Ongoing monitoring and drift detection",
      "Periodic control re-assessment",
      "Incident and exception tracking",
      "Governance reporting to leadership",
    ],
    deliverables: ["Monitoring dashboard", "Control re-assessment log", "Governance reporting pack"],
    outcome: "Audit-ready assurance that holds up after go-live, not just at it",
  },
];

export const adglWhyItExists =
  "Most organisations already know they need AI governance. Far fewer know how to operationalise it during an actual deployment, at the point a specific system, a specific vendor and a specific business owner need a specific decision. ADGL exists to close that gap: a practical, five-phase lifecycle that turns AI governance from a policy statement into a repeatable set of decisions and evidence, applied before a deployment reaches production and maintained after it.";

export const adglOperaRelationship =
  "AI for U&I delivers advisory engagements using the OPERA consulting methodology. ADGL is one specialised methodology within AI for U&I, focused specifically on governing AI deployments through production; OPERA remains the operating method behind how an engagement itself is run, including ADGL engagements.";

export interface AdglDeploymentType {
  name: string;
}

export const adglDeploymentTypes: AdglDeploymentType[] = [
  { name: "Microsoft Copilot Enterprise" },
  { name: "ChatGPT Enterprise" },
  { name: "Customer Support AI" },
  { name: "Internal Knowledge Assistants" },
  { name: "RAG Applications" },
  { name: "Agentic AI" },
  { name: "AI-Enabled SaaS Platforms" },
  { name: "Industry-Specific AI Systems" },
];

export const adglDeploymentAgnosticNote =
  "ADGL governs the deployment decision, not a specific vendor or architecture. The same five phases apply whether the system in question is a licensed enterprise copilot, a custom-built agent, or an AI capability embedded inside a third-party SaaS platform.";
