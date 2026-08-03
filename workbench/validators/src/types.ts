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
  description?: string;
  citation_ids?: string[];
}

export interface CanonicalEntity {
  id: string;
  title: string;
  description: string;
  version: string;
  status: "draft" | "active" | "deprecated" | "superseded" | "retracted";
  confidence: "Verified" | "Reviewed" | "Draft" | "Community" | "Archived";
  created_date: string;
  updated_date: string;
  tags: string[];
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

export interface Ontology {
  version: string;
  entity_types: EntityType[];
  relationship_types: OntologyRelationshipType[];
  acyclic_verbs: string[];
  cycle_detection_scope: string;
}

export type IssueSeverity = "error";

export interface ValidationIssue {
  rule: string;
  severity: IssueSeverity;
  filePath?: string;
  entityId?: string;
  message: string;
}
