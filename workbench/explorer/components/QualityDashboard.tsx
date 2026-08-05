import Link from "next/link";
import type { CheckResult, QualityReport } from "@/lib/types";

function StatusIcon({ pass }: { pass: boolean | null }) {
  if (pass === null) {
    return (
      <span className="flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full border border-ink-300 text-[10px] font-bold text-ink-400" title="Could not be verified in this build environment">
        ?
      </span>
    );
  }
  if (pass) {
    return (
      <span className="flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700">
        <svg viewBox="0 0 12 12" className="h-2.5 w-2.5" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M2 6.5l2.5 2.5L10 3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
    );
  }
  return (
    <span className="flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full bg-red-100 text-red-700">
      <svg viewBox="0 0 12 12" className="h-2.5 w-2.5" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 3l6 6M9 3l-6 6" strokeLinecap="round" />
      </svg>
    </span>
  );
}

function CheckRow({ label, result, href }: { label: string; result: CheckResult; href: string }) {
  return (
    <Link
      href={href}
      className="group flex items-start justify-between gap-3 border-b border-ink-100 py-2.5 last:border-b-0 hover:bg-ink-50 -mx-1.5 px-1.5 rounded"
    >
      <div className="flex items-center gap-2">
        <StatusIcon pass={result.pass} />
        <span className="text-sm text-ink-800 underline decoration-ink-200 decoration-dotted underline-offset-2 group-hover:text-accent-700 group-hover:decoration-accent-400">
          {label}
        </span>
      </div>
      <span className="max-w-[55%] text-right text-xs text-ink-400 group-hover:text-accent-600">
        {result.pass === null ? "unverified" : result.pass ? "pass" : "fail"} <span aria-hidden>→</span>
      </span>
    </Link>
  );
}

function StatBlock({ label, value }: { label: string; value: number | string }) {
  return (
    <div>
      <div className="field-label mb-1">{label}</div>
      <div className="text-2xl font-semibold tabular-nums text-ink-900">{value}</div>
    </div>
  );
}

export function QualityDashboard({ quality }: { quality: QualityReport }) {
  const pct = Math.min(100, (quality.citation_completeness.average / 100) * 100);
  const targetPct = quality.citation_completeness.target;

  return (
    <div id="quality-dashboard" className="scroll-mt-20 card p-5 sm:p-6">
      <div className="mb-5 flex items-baseline justify-between gap-3">
        <h2 className="text-base font-semibold text-ink-900">Repository status</h2>
        <span className="text-xs text-ink-400">Generated {new Date(quality.generated_at).toISOString().slice(0, 10)}</span>
      </div>

      <div className="mb-6 grid grid-cols-3 gap-4 sm:max-w-md">
        <StatBlock label="Canonical objects" value={quality.canonical_objects} />
        <StatBlock label="Real incidents" value={quality.real_incidents} />
        <StatBlock label="Entity types" value={quality.entity_types} />
      </div>

      <div className="grid grid-cols-1 gap-x-8 md:grid-cols-2">
        <div>
          <CheckRow label="Schema validation" result={quality.checks.schema_validation} href="/standards/#deterministic-validation" />
          <CheckRow label="Zero orphans" result={quality.checks.zero_orphans} href="/standards/#connected-knowledge" />
          <CheckRow label="Relationship integrity" result={quality.checks.relationship_integrity} href="/standards/#connected-knowledge" />
        </div>
        <div>
          <CheckRow label="Type check" result={quality.checks.type_check} href="/standards/#continuous-quality-improvement" />
          <CheckRow label="Editorial audit" result={quality.checks.editorial_audit} href="/standards/#continuous-quality-improvement" />
        </div>
      </div>

      <p className="mt-5 border-t border-ink-200 pt-4 text-xs italic text-ink-500">
        All quality metrics shown on this page are computed directly from the repository&rsquo;s validation and
        editorial tooling during the build process. No values are entered manually.
      </p>

      <div className="mt-5 border-t border-ink-200 pt-5">
        <Link href="/sources/" className="group block rounded -mx-1.5 px-1.5 py-1 hover:bg-ink-50">
          <div className="mb-2 flex items-baseline justify-between">
            <span className="field-label underline decoration-ink-200 decoration-dotted underline-offset-2 group-hover:text-accent-700 group-hover:decoration-accent-400">
              Citation completeness
            </span>
            <span className="text-xs text-ink-400 group-hover:text-accent-600">
              target {targetPct}+ <span aria-hidden>→</span>
            </span>
          </div>
          <div className="mb-1.5 flex items-baseline gap-1.5">
            <span className="text-2xl font-semibold tabular-nums text-ink-900">{quality.citation_completeness.average}</span>
            <span className="text-sm text-ink-400">/ 100</span>
          </div>
          <div className="relative h-2 w-full overflow-hidden rounded-full bg-ink-100">
            <div className="h-full rounded-full bg-amber-500" style={{ width: `${pct}%` }} />
            <div className="absolute inset-y-0 border-l-2 border-ink-900" style={{ left: `${targetPct}%` }} />
          </div>
        </Link>
        <p className="mt-2 text-xs text-ink-500">
          Below target, and reported honestly rather than rounded up — closing this gap requires re-verifying real
          sources, not a script. See{" "}
          <Link href="/sources/" className="text-accent-600 hover:underline">
            Source Transparency
          </Link>{" "}
          for how this score is measured.
        </p>
      </div>
    </div>
  );
}
