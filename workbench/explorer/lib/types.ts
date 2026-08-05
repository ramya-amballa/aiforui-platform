export type EntityType = "decision" | "incident" | "pattern" | "control" | "evidence" | "board_question";

export const ENTITY_TYPES: EntityType[] = ["decision", "incident", "pattern", "control", "evidence", "board_question"];

export const ENTITY_LABEL: Record<EntityType, string> = {
  decision: "Governance Decision",
  incident: "Incident",
  pattern: "Design Pattern",
  control: "Framework Control",
  evidence: "Evidence Type",
  board_question: "Board Question",
};

export const ENTITY_LABEL_PLURAL: Record<EntityType, string> = {
  decision: "Governance Decisions",
  incident: "Incidents",
  pattern: "Design Patterns",
  control: "Framework Controls",
  evidence: "Evidence Types",
  board_question: "Board Questions",
};

export const ENTITY_ROUTE: Record<EntityType, string> = {
  decision: "decisions",
  incident: "incidents",
  pattern: "patterns",
  control: "controls",
  evidence: "evidence",
  board_question: "board-questions",
};

export const ENTITY_DESCRIPTION: Record<EntityType, string> = {
  decision: "Concrete, testable governance commitments — the hub entity linking incidents to the patterns, controls, evidence, and board questions that surround them.",
  incident: "Real, independently-verified AI governance incidents, selected for the governance lesson each one demonstrates.",
  pattern: "Reusable architectural and process responses that satisfy a control or implement a decision.",
  control: "Directly-applicable provisions from real regulatory and standards frameworks, mapped only where genuinely relevant.",
  evidence: "The observable artifacts an auditor or regulator would actually ask to see.",
  board_question: "One concise, executive-actionable question per governance concept, ready for the boardroom.",
};

export type Status = "draft" | "active" | "deprecated" | "superseded" | "retracted";
export type Confidence = "Verified" | "Reviewed" | "Draft" | "Community" | "Archived";
export type RelationshipVerb =
  | "RESULTED_FROM"
  | "MITIGATED_BY"
  | "IMPLEMENTED_BY"
  | "SATISFIES_CONTROL"
  | "REQUIRES_EVIDENCE"
  | "RAISES_BOARD_QUESTION"
  | "RELATED_TO";

export const CONFIDENCE_ORDER: Confidence[] = ["Verified", "Reviewed", "Draft", "Community", "Archived"];

export interface Citation {
  id: string;
  source_type: "regulator" | "legislation" | "court_judgment" | "company_statement" | "academic_paper" | "standards_body" | "news_publication" | "other";
  title: string;
  publisher: string;
  url?: string;
  publication_date?: string;
  accessed_date: string;
  locator?: string;
  excerpt?: string;
}

export interface HistoryEntry {
  event: "created" | "updated" | "reviewed" | "approved" | "archived" | "retracted";
  date: string;
  by: string;
  version: string;
  note?: string;
}

export interface RawRelationship {
  type: RelationshipVerb;
  target_id: string;
  target_type: EntityType;
  reason: string;
  confidence?: Confidence;
  citation_ids?: string[];
}

export interface RawEntity {
  id: string;
  slug: string;
  title: string;
  description: string;
  version: string;
  status: Status;
  confidence: Confidence;
  created_date: string;
  updated_date: string;
  tags: string[];
  contributors?: string[];
  created_by?: string;
  reviewed_by?: string;
  approved_by?: string;
  history: HistoryEntry[];
  citations: Citation[];
  relationships: RawRelationship[];

  // decision
  decision_statement?: string;
  decision_type?: string;
  decision_context?: string;
  governing_body?: string;
  jurisdiction?: string[];
  frameworks_referenced?: string[];
  alternatives_considered?: string[];
  problem_statement?: string;
  decision_rationale?: string;
  outcome?: string;

  // incident
  occurred_date?: string;
  organizations_involved?: string[];
  harm_types?: string[];
  ai_system_category?: string;
  severity?: "low" | "medium" | "high" | "critical";
  root_cause?: string;

  // pattern
  problem?: string;
  solution?: string;
  applicability?: string;
  consequences?: string;
  maturity?: string;

  // control
  framework_name?: string;
  framework_slug?: string;
  control_reference?: string;
  control_text?: string;
  control_family?: string;

  // evidence
  evidence_description?: string;
  collection_method?: string;
  retention_period?: string;
  artifact_format?: string;

  // board_question
  question_text?: string;
  audience?: string[];
  rationale?: string;
  follow_up_actions?: string[];
}

export interface ResolvedRelationship {
  type: RelationshipVerb;
  direction: "out" | "in";
  reason: string;
  confidence?: Confidence;
  citation_ids?: string[];
  other_id: string;
  other_type: EntityType;
  other_slug: string;
  other_title: string;
}

export interface GraphNode extends RawEntity {
  entity_type: EntityType;
  relationships_out: ResolvedRelationship[];
  relationships_in: ResolvedRelationship[];
  related_frameworks: string[];
}

export interface FrameworkGroup {
  slug: string;
  label: string;
  control_ids: string[];
  status: "covered" | "gap";
}

export interface SearchDocument {
  id: string;
  entity_type: EntityType;
  slug: string;
  title: string;
  description: string;
  tags: string[];
  jurisdiction: string[];
  frameworks: string[];
  status: Status;
  confidence: Confidence;
  extra: string;
}

export interface GraphData {
  generated_at: string;
  counts: Record<EntityType, number>;
  nodes: GraphNode[];
  frameworks: FrameworkGroup[];
  search_documents: SearchDocument[];
  relationship_verbs: { verb: RelationshipVerb; description: string }[];
}
