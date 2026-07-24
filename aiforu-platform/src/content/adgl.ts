/**
 * ADGL: AI Deployment Governance Lifecycle. AI for U&I's specialised
 * methodology for governing a specific AI system through deployment,
 * distinct from OPERA (the firm's overall advisory operating method).
 * Transcribed from the reference methodology document
 * ("AI Deployment Governance Lifecycle (ADGL) v1.0") and must not be
 * reinterpreted, simplified or renamed elsewhere; the full sixteen-
 * page control library, RACI, risk model and monitoring framework
 * stay in the PDF itself, not duplicated here — this is the concise,
 * accurate summary that makes the download worth having.
 */

export interface AdglDeliverableGroup {
  label: string;
  items: string[];
}

export interface AdglPhase {
  step: number;
  name: string;
  weeks: string;
  purpose: string;
  question: string;
  activities: string[];
  /** One sentence: why this phase's deliverables matter, not what they're named. */
  deliverablesSummary: string;
  deliverableGroups: AdglDeliverableGroup[];
  gate: string;
  exitSummary: string;
}

export const adglPhases: AdglPhase[] = [
  {
    step: 1,
    name: "Discover",
    weeks: "Weeks 1–3",
    purpose: "Understand the AI system before governance begins.",
    question: "What business problem is this AI solving, and who owns that outcome?",
    activities: [
      "Stakeholder interviews across engineering, security, privacy, operations, legal, product and data platform",
      "Identify and register every AI asset in build or production",
      "Map AI data flow end to end, numbered step by step",
      "Review AI application architecture against the codebase",
    ],
    deliverablesSummary: "Creates the foundational documentation required before risk assessment begins.",
    deliverableGroups: [
      { label: "AI Discovery", items: ["AI Asset Inventory", "Architecture Review"] },
      { label: "Data Understanding", items: ["AI Data Flow Mapping", "Data Classification"] },
      { label: "Documentation", items: ["Prompt Flow Map", "Findings Log"] },
    ],
    gate: "Gate 1 — Proceed to Assess",
    exitSummary: "Asset inventory completed with named owners; data flow mapped and validated against the codebase.",
  },
  {
    step: 2,
    name: "Assess",
    weeks: "Weeks 3–6",
    purpose: "Quantify exposure before any control is designed.",
    question: "What is the worst credible outcome for a customer, and can it be undone?",
    activities: [
      "Score every risk across likelihood, severity, reach, reversibility and decision autonomy",
      "Conduct the Data Protection Impact Assessment",
      "Perform threat modelling with security engineering",
      "Assess the model provider: training use, residency, retention, versioning, exit",
    ],
    deliverablesSummary: "Produces the evidence needed to understand AI risk before governance decisions are made.",
    deliverableGroups: [
      { label: "Risk Analysis", items: ["AI Risk Assessment", "Risk Heat Map"] },
      { label: "Privacy & Security", items: ["DPIA", "Threat Model"] },
      { label: "Vendor & Regulatory", items: ["Third-Party AI Assessment", "Regulatory Assessment"] },
    ],
    gate: "Gate 2 — Proceed to Govern",
    exitSummary: "Regulatory classification documented; residual risk accepted in writing by a named owner.",
  },
  {
    step: 3,
    name: "Govern",
    weeks: "Weeks 6–9",
    purpose: "Design the structure, controls and oversight that reduce risk to the accepted level.",
    question: "Who has authority to stop a deployment, and has that been exercised?",
    activities: [
      "Design the governance operating model and committee decision rights",
      "Build the RACI to individual role level",
      "Design human oversight tiers and measurement thresholds",
      "Build the control library mapped to existing frameworks",
    ],
    deliverablesSummary: "Establishes ownership, controls and decision rights for production deployment.",
    deliverableGroups: [
      { label: "Governance Structure", items: ["Governance Operating Model", "RACI", "Approval Workflow"] },
      { label: "Operational Controls", items: ["AI Control Library", "Logging Specification"] },
      { label: "Oversight", items: ["Human Oversight Design", "Governance KPIs", "AI Policies & Standards"] },
    ],
    gate: "Gate 3 — Proceed to Deploy",
    exitSummary: "Control library approved and mapped; logging schema accepted by engineering.",
  },
  {
    step: 4,
    name: "Deploy",
    weeks: "Weeks 9–12",
    purpose: "Prove every control works, then decide.",
    question: "Can we show this control operated, or only that it exists?",
    activities: [
      "Configure monitoring signals, thresholds and alert routing to named responders",
      "Run adversarial and cross-tenant tests, embedded in CI",
      "Build the evidence repository and populate pre-deployment artefacts",
      "Deliver role-based training with scenario assessment",
    ],
    deliverablesSummary: "Demonstrates that governance controls actually operate before go-live.",
    deliverableGroups: [
      { label: "Monitoring", items: ["Monitoring Framework", "AI Incident Management"] },
      { label: "Evidence", items: ["Evidence Repository", "Test Results Pack"] },
      { label: "Production Readiness", items: ["Training Record", "Production Readiness Governance"] },
    ],
    gate: "Gate 4 — Authorise production deployment",
    exitSummary: "Readiness checklist approved; deployment approved by committee and recorded.",
  },
  {
    step: 5,
    name: "Operate",
    weeks: "Ongoing, quarterly cycle",
    purpose: "Keep governance working after deployment.",
    question: "Has the override rate fallen below the floor?",
    activities: [
      "Tune monitoring thresholds against real production volume",
      "Run independent QA sampling cycles",
      "Produce the quarterly executive and board reporting pack",
      "Route the next AI use case through the approval workflow",
    ],
    deliverablesSummary: "Ensures governance continues after deployment through monitoring and continual improvement.",
    deliverableGroups: [
      { label: "Monitoring", items: ["Threshold Tuning Report", "QA Sampling Results"] },
      { label: "Reporting", items: ["Executive Reporting", "Governance Review"] },
      { label: "Governance Improvement", items: ["Maturity Roadmap"] },
    ],
    gate: "Gate 5 — Governance operates without external support",
    exitSummary: "Next use case governed through the same workflow, without bespoke governance work.",
  },
];

export const adglWhyItExists =
  "Most organisations deploying AI already hold ISO 27001, SOC 2 and a GDPR programme. Yet they still lack an operational process for deploying AI into production: who owns the decision to accept an AI risk, whether retrieval is scoped so one customer cannot reach another's data, whether human review is real or has become a formality. ADGL fills that gap: a practical, implementation-first lifecycle that turns AI governance from policy into operational controls.";

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
  "The lifecycle is deployment-agnostic: the activities, controls and gates hold regardless of model, vendor or industry.";
