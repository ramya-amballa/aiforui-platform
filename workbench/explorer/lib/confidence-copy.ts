import type { Confidence } from "./types";

export const CONFIDENCE_EXPLANATION: Record<Confidence, string> = {
  Verified: "Independently reviewed by a second party against its citations. The highest trust tier in this dataset.",
  Reviewed: "Reviewed against its citations by a contributor at authoring time, but has not yet had independent second-party review.",
  Draft: "Authored but not yet reviewed against its citations. Treat as provisional.",
  Community: "A plausible, illustrative reference object — often modelling a reasonable response to a real incident rather than a documented decision of a real organisation — or relies on background knowledge rather than a fresh verification pass.",
  Archived: "Superseded or no longer actively maintained, retained for historical record.",
};
