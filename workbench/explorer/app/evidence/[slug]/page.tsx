import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { nodesByType, getNode, relatedByVerb } from "@/lib/data";
import { DetailHeader } from "@/components/DetailHeader";
import { RelationshipChain } from "@/components/RelationshipChain";
import { RelSection } from "@/components/RelSection";
import { RelationshipReasoning } from "@/components/RelationshipReasoning";
import { CitationsSection, HistorySection, ConfidenceSection } from "@/components/CitationsHistory";
import { ANCHOR_ID } from "@/lib/anchors";

export function generateStaticParams() {
  return nodesByType("evidence").map((n) => ({ slug: n.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const node = getNode("evidence", slug);
  if (!node) return {};
  return {
    title: node.title,
    description: node.description,
    alternates: { canonical: `/evidence/${node.slug}/` },
    openGraph: { title: node.title, description: node.description },
  };
}

export default async function EvidenceDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const node = getNode("evidence", slug);
  if (!node) notFound();

  const requiredBy = relatedByVerb(node, "REQUIRES_EVIDENCE", "in");

  return (
    <article>
      <DetailHeader node={node} />
      <RelationshipChain node={node} />

      <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
        <h2 className="mb-2 text-base font-semibold text-ink-900">What auditors would ask to see</h2>
        {node.evidence_description && <p className="prose-body">{node.evidence_description}</p>}
        <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
          {node.collection_method && (
            <div>
              <dt className="text-xs text-ink-400">Collection method</dt>
              <dd className="text-ink-700">{node.collection_method}</dd>
            </div>
          )}
          {node.retention_period && (
            <div>
              <dt className="text-xs text-ink-400">Retention period</dt>
              <dd className="text-ink-700">{node.retention_period}</dd>
            </div>
          )}
          {node.artifact_format && (
            <div>
              <dt className="text-xs text-ink-400">Artifact format</dt>
              <dd className="text-ink-700">{node.artifact_format}</dd>
            </div>
          )}
        </dl>
      </section>

      <RelSection id={ANCHOR_ID.decision} title="Required by" items={requiredBy} emptyText="Not yet required by any decision, pattern, or control." />
      <RelationshipReasoning node={node} />
      <CitationsSection node={node} />
      <HistorySection node={node} />
      <ConfidenceSection node={node} />
    </article>
  );
}
