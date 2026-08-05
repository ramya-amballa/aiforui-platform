import { notFound } from "next/navigation";
import { graph, frameworkDetail } from "@/lib/data";
import { NodeListItem } from "@/components/NodeListItem";
import type { GraphNode } from "@/lib/types";

export function generateStaticParams() {
  return graph.frameworks.map((f) => ({ slug: f.slug }));
}

function Group({ title, nodes }: { title: string; nodes: GraphNode[] }) {
  return (
    <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
      <h2 className="mb-3 text-base font-semibold text-ink-900">
        {title} <span className="text-sm font-normal text-ink-400">({nodes.length})</span>
      </h2>
      {nodes.length === 0 ? (
        <p className="text-sm text-ink-400">None mapped yet.</p>
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {nodes.map((n) => (
            <NodeListItem key={n.id} node={n} />
          ))}
        </div>
      )}
    </section>
  );
}

export default async function FrameworkDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const detail = frameworkDetail(slug);
  if (!detail) notFound();
  const { framework, controls, decisions, patterns, incidents, evidence, boardQuestions } = detail;

  return (
    <article>
      <div className="mb-8 border-b border-ink-200 pb-6">
        <h1 className="text-2xl font-semibold text-ink-900">{framework.label}</h1>
        <p className="prose-body mt-2 max-w-2xl">
          {framework.status === "covered"
            ? `${controls.length} control${controls.length === 1 ? "" : "s"} mapped in this dataset, and every decision, pattern, incident, evidence type, and board question that connects to them.`
            : "No control in this dataset yet cites this framework. Listed as a known coverage gap, not silently omitted."}
        </p>
      </div>

      <Group title="Controls" nodes={controls} />
      <Group title="Mapped decisions" nodes={decisions} />
      <Group title="Mapped patterns" nodes={patterns} />
      <Group title="Incidents" nodes={incidents} />
      <Group title="Evidence" nodes={evidence} />
      <Group title="Board questions" nodes={boardQuestions} />
    </article>
  );
}
