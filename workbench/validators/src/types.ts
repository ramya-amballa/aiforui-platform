export type EntityType =
  | "decision"
  | "incident"
  | "pattern"
  | "control"
  | "evidence"
  | "board_question";

export const ENTITY_TYPES: EntityType[] = [
  "decision",
  "incident",
  "pattern",
  "control",
  "evidence",
  "board_question",
];

export const DATA_DIR_BY_TYPE: Record<EntityType, string> = {
  decision: "decisions",
  incident: "incidents",
  pattern: "patterns",
  control: "controls",
  evidence: "evidence",
  board_question: "board_questions",
};

export const SCHEMA_FILE_BY_TYPE: Record<EntityType, string> = {
  decision: "decision.schema.json",
  incident: "incident.schema.json",
  pattern: "pattern.schema.json",
  control: "control.schema.json",
  evidence: "evidence.schema.json",
  board_question: "board_question.schema.json",
};

export interface Citation {
  id: string;
  source_type: string;
  title: string;
  publisher: string;
  url?: string;
  publication_date?: string;
  accessed_date: string;
  locator?: string;
  excerpt?: string;
}

export interface Relationship {
  type: string;
  target_id: string;
  target_type: EntityType;
  reason: string;
  confidence?: "Verified" | "Reviewed" | "Draft" | "Community" | "Archived";
  citation_ids?: string[];
}

export interface HistoryEntry {
  event: "created" | "updated" | "reviewed" | "approved" | "archived" | "retracted";
  date: string;
  by: string;
  version: string;
  note?: string;
}

export interface CanonicalEntity {
  id: string;
  slug: string;
  title: string;
  description: string;
  version: string;
  status: "draft" | "active" | "deprecated" | "superseded" | "retracted";
  confidence: "Verified" | "Reviewed" | "Draft" | "Community" | "Archived";
  created_date: string;
  updated_date: string;
  tags: string[];
  created_by?: string;
  reviewed_by?: string;
  approved_by?: string;
  history?: HistoryEntry[];
  citations: Citation[];
  relationships: Relationship[];
  [key: string]: unknown;
}

export interface LoadedEntity {
  entityType: EntityType;
  filePath: string;
  data: CanonicalEntity;
}

export interface OntologyTriple {
  source_type: string;
  target_type: string;
}

export interface OntologyRelationshipType {
  verb: string;
  description: string;
  allowed: OntologyTriple[];
}

export interface OutboundRelationshipLimits {
  soft_limit: number;
  hard_limit: number;
  note?: string;
}

export interface Ontology {
  version: string;
  entity_types: EntityType[];
  id_prefixes: Record<EntityType, string>;
  reserved_prefixes: Record<string, string>;
  outbound_relationship_limits: OutboundRelationshipLimits;
  relationship_types: OntologyRelationshipType[];
  acyclic_verbs: string[];
  cycle_detection_scope: string;
}

export type IssueSeverity = "error" | "warning";

export interface ValidationIssue {
  rule: string;
  severity: IssueSeverity;
  filePath?: string;
  entityId?: string;
  message: string;
}
