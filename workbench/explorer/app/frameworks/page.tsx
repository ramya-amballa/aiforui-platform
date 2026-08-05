import Link from "next/link";
import { graph } from "@/lib/data";
import { PageHeader } from "@/components/PageHeader";

export const metadata = { title: "Frameworks — AI Governance Workbench" };

export default function FrameworksPage() {
  return (
    <div>
      <PageHeader
        title="Frameworks"
        description="Real regulatory and standards frameworks, and the controls, decisions, incidents, evidence, and board questions mapped to each — only where genuinely, directly applicable."
        count={graph.frameworks.length}
      />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {graph.frameworks.map((f) => (
          <Link key={f.slug} href={`/frameworks/${f.slug}/`} className="card flex flex-col gap-2 p-4 hover:border-ink-400 transition-colors">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-ink-900">{f.label}</h3>
              <span
                className={`rounded border px-1.5 py-0.5 text-xs font-medium ${
                  f.status === "covered" ? "border-emerald-200 bg-emerald-50 text-emerald-700" : "border-ink-200 bg-ink-50 text-ink-400"
                }`}
              >
                {f.status === "covered" ? `${f.control_ids.length} control${f.control_ids.length === 1 ? "" : "s"}` : "gap"}
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
