import type { EntityType } from "./types";

export const ENTITY_COLOR: Record<EntityType, { bg: string; text: string; border: string; dot: string; hex: string }> = {
  decision: { bg: "bg-accent-50", text: "text-accent-700", border: "border-accent-200", dot: "bg-accent-500", hex: "#3a63d8" },
  incident: { bg: "bg-rose-50", text: "text-rose-700", border: "border-rose-200", dot: "bg-rose-500", hex: "#e11d48" },
  pattern: { bg: "bg-teal-50", text: "text-teal-700", border: "border-teal-200", dot: "bg-teal-500", hex: "#0d9488" },
  control: { bg: "bg-violet-50", text: "text-violet-700", border: "border-violet-200", dot: "bg-violet-500", hex: "#7c3aed" },
  evidence: { bg: "bg-amber-50", text: "text-amber-700", border: "border-amber-200", dot: "bg-amber-500", hex: "#d97706" },
  board_question: { bg: "bg-sky-50", text: "text-sky-700", border: "border-sky-200", dot: "bg-sky-500", hex: "#0284c7" },
};
