import { notFound } from "next/navigation";
import { nodesByType, getNode, relatedByVerb } from "@/lib/data";
import { DetailHeader } from "@/components/DetailHeader";
import { RelationshipChain } from "@/components/RelationshipChain";
import { RelSection } from "@/components/RelSection";
import { RelationshipReasoning } from "@/components/RelationshipReasoning";
import { CitationsSection, HistorySection, ConfidenceSection } from "@/components/CitationsHistory";
import { ANCHOR_ID } from "@/lib/anchors";

export function generateStaticParams() {
  return nodesByType("pattern").map((n) => ({ slug: n.slug }));
}

export default async function PatternDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const node = getNode("pattern", slug);
  if (!node) notFound();

  const satisfiesControls = relatedByVerb(node, "SATISFIES_CONTROL", "out");
  const requiresEvidence = relatedByVerb(node, "REQUIRES_EVIDENCE", "out");
  const implementedFor = relatedByVerb(node, "IMPLEMENTED_BY", "in");
  const mitigatesIncidents = relatedByVerb(node, "MITIGATED_BY", "in").filter((r) => r.other_type === "incident");

  return (
    <article>
      <DetailHeader node={node} />
      <RelationshipChain node={node} />

      <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
        <h2 className="mb-2 text-base font-semibold text-ink-900">Problem &amp; solution</h2>
        {node.problem && (
          <div className="mb-3">
            <div className="field-label mb-1">Problem</div>
            <p className="prose-body">{node.problem}</p>
          </div>
        )}
        {node.solution && (
          <div className="mb-3">
            <div className="field-label mb-1">Solution</div>
            <p className="prose-body">{node.solution}</p>
          </div>
        )}
        <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
          {node.maturity && (
            <div>
              <dt className="text-xs text-ink-400">Maturity</dt>
              <dd className="text-ink-700 capitalize">{node.maturity}</dd>
            </div>
          )}
          {node.applicability && (
            <div className="sm:col-span-1">
              <dt className="text-xs text-ink-400">Applicability</dt>
              <dd className="text-ink-700">{node.applicability}</dd>
            </div>
          )}
          {node.consequences && (
            <div className="sm:col-span-1">
              <dt className="text-xs text-ink-400">Consequences / trade-offs</dt>
              <dd className="text-ink-700">{node.consequences}</dd>
            </div>
          )}
        </dl>
      </section>

      <RelSection id={ANCHOR_ID.control} title="Satisfies framework controls" items={satisfiesControls} />
      <RelSection id={ANCHOR_ID.evidence} title="Requires evidence" items={requiresEvidence} />
      <RelSection id={ANCHOR_ID.decision} title="Implemented for" items={implementedFor} emptyText="Not yet implemented by a decision or control." />
      <RelSection id={ANCHOR_ID.incident} title="Mitigates incidents" items={mitigatesIncidents} />
      <RelationshipReasoning node={node} />
      <CitationsSection node={node} />
      <HistorySection node={node} />
      <ConfidenceSection node={node} />
    </article>
  );
}
