import type { EntityType } from "@/lib/types";
import { ENTITY_LABEL } from "@/lib/types";
import { ENTITY_COLOR } from "@/lib/entity-colors";

export function EntityTypeBadge({ type, compact = false }: { type: EntityType; compact?: boolean }) {
  const c = ENTITY_COLOR[type];
  return (
    <span className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-xs font-medium leading-none ${c.bg} ${c.text} ${c.border}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${c.dot}`} />
      {compact ? ENTITY_LABEL[type].split(" ")[0] : ENTITY_LABEL[type]}
    </span>
  );
}
