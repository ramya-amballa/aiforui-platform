import Link from "next/link";
import type { EntityType } from "@/lib/types";
import { ENTITY_LABEL_PLURAL, ENTITY_DESCRIPTION, ENTITY_ROUTE } from "@/lib/types";
import { ENTITY_COLOR } from "@/lib/entity-colors";

export function EntityCard({ type, count }: { type: EntityType; count: number }) {
  const c = ENTITY_COLOR[type];
  return (
    <Link
      href={`/${ENTITY_ROUTE[type]}/`}
      className="card group flex flex-col justify-between p-5 hover:border-ink-400 transition-colors"
    >
      <div>
        <div className="flex items-center justify-between">
          <span className={`h-2 w-2 rounded-full ${c.dot}`} />
          <span className="text-2xl font-semibold tabular-nums text-ink-900">{count}</span>
        </div>
        <h3 className="mt-3 text-base font-semibold text-ink-900">{ENTITY_LABEL_PLURAL[type]}</h3>
        <p className="mt-1.5 text-sm leading-relaxed text-ink-500">{ENTITY_DESCRIPTION[type]}</p>
      </div>
      <div className={`mt-4 inline-flex items-center gap-1 text-sm font-medium ${c.text}`}>
        Browse {ENTITY_LABEL_PLURAL[type].toLowerCase()}
        <span aria-hidden className="transition-transform group-hover:translate-x-0.5">
          →
        </span>
      </div>
    </Link>
  );
}
