import type { EntityType } from "./types";

export const ANCHOR_ID: Record<EntityType, string> = {
  incident: "linked-incidents",
  decision: "linked-decisions",
  pattern: "linked-patterns",
  evidence: "linked-evidence",
  control: "linked-controls",
  board_question: "linked-board-questions",
};

export const CHAIN_ORDER: EntityType[] = ["incident", "decision", "pattern", "evidence", "control", "board_question"];
