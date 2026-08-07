import type { Confidence, Status } from "@/lib/types";

const CONFIDENCE_STYLE: Record<Confidence, string> = {
  Verified: "bg-emerald-50 text-emerald-700 border-emerald-200",
  Reviewed: "bg-accent-50 text-accent-700 border-accent-200",
  Draft: "bg-amber-50 text-amber-700 border-amber-200",
  Community: "bg-ink-100 text-ink-600 border-ink-200",
  Archived: "bg-ink-50 text-ink-400 border-ink-200",
};

const STATUS_STYLE: Record<Status, string> = {
  active: "bg-emerald-50 text-emerald-700 border-emerald-200",
  draft: "bg-amber-50 text-amber-700 border-amber-200",
  deprecated: "bg-ink-100 text-ink-500 border-ink-200",
  superseded: "bg-ink-100 text-ink-500 border-ink-200",
  retracted: "bg-red-50 text-red-700 border-red-200",
};

const SEVERITY_STYLE: Record<string, string> = {
  critical: "bg-red-50 text-red-700 border-red-200",
  high: "bg-orange-50 text-orange-700 border-orange-200",
  medium: "bg-amber-50 text-amber-700 border-amber-200",
  low: "bg-ink-100 text-ink-500 border-ink-200",
};

function BaseBadge({ label, className }: { label: string; className: string }) {
  return (
    <span className={`inline-flex items-center rounded border px-1.5 py-0.5 text-xs font-medium leading-none ${className}`}>
      {label}
    </span>
  );
}

export function ConfidenceBadge({ value }: { value: Confidence }) {
  return <BaseBadge label={value} className={CONFIDENCE_STYLE[value]} />;
}

export function StatusBadge({ value }: { value: Status }) {
  return <BaseBadge label={value} className={STATUS_STYLE[value]} />;
}

export function SeverityBadge({ value }: { value: string }) {
  return <BaseBadge label={value} className={SEVERITY_STYLE[value] ?? SEVERITY_STYLE.low} />;
}

export function TagBadge({ value }: { value: string }) {
  return <BaseBadge label={value} className="bg-white text-ink-600 border-ink-200" />;
}
