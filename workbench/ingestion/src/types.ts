export interface DraftSource {
  source_type: string;
  title: string;
  publisher: string;
  url?: string;
  published_date?: string;
  retrieved_date: string;
}

export interface SuggestedIncident {
  title: string;
  description: string;
  occurred_date: string;
  organizations_involved?: string[];
  harm_types?: string[];
  ai_system_category?: string;
  jurisdiction?: string[];
  severity?: "low" | "medium" | "high" | "critical";
  root_cause?: string;
  tags?: string[];
}

export interface HumanReview {
  status: "pending" | "approved" | "rejected" | "needs_changes";
  reviewer?: string;
  reviewed_date?: string;
  notes?: string;
  confidence_assigned?: "Verified" | "Reviewed" | "Draft" | "Community" | "Archived";
}

export interface DraftIncident {
  id: string;
  created_date: string;
  source: DraftSource;
  raw_excerpt: string;
  extraction_method: "human" | "ai_assisted";
  captured_by?: string;
  suggested_incident: SuggestedIncident;
  human_review: HumanReview;
}
