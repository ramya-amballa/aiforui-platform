import Link from "next/link";
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
  return nodesByType("control").map((n) => ({ slug: n.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const node = getNode("control", slug);
  if (!node) return {};
  return {
    title: node.title,
    description: node.description,
    alternates: { canonical: `/controls/${node.slug}/` },
    openGraph: { title: node.title, description: node.description },
  };
}

export default async function ControlDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const node = getNode("control", slug);
  if (!node) notFound();

  const requiresEvidence = relatedByVerb(node, "REQUIRES_EVIDENCE", "out");
  const satisfiedBy = relatedByVerb(node, "SATISFIES_CONTROL", "in");
  const mitigatesIncidents = relatedByVerb(node, "MITIGATED_BY", "in").filter((r) => r.other_type === "incident");
  const boardQuestions = relatedByVerb(node, "RAISES_BOARD_QUESTION", "out");

  return (
    <article>
      <DetailHeader node={node} />
      <RelationshipChain node={node} />

      <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
        <h2 className="mb-2 text-base font-semibold text-ink-900">Control text</h2>
        {node.control_text && <p className="prose-body">{node.control_text}</p>}
        <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
          {node.framework_name && (
            <div>
              <dt className="text-xs text-ink-400">Framework</dt>
              <dd>
                <Link href={`/frameworks/${node.framework_slug}/`} className="text-accent-600 hover:underline">
                  {node.framework_name}
                </Link>
              </dd>
            </div>
          )}
          {node.control_reference && (
            <div>
              <dt className="text-xs text-ink-400">Reference</dt>
              <dd className="text-ink-700">{node.control_reference}</dd>
            </div>
          )}
          {node.control_family && (
            <div>
              <dt className="text-xs text-ink-400">Control family</dt>
              <dd className="text-ink-700">{node.control_family}</dd>
            </div>
          )}
        </dl>
      </section>

      <RelSection id={ANCHOR_ID.evidence} title="Requires evidence" items={requiresEvidence} />
      <RelSection id={ANCHOR_ID.decision} title="Satisfied by" items={satisfiedBy} emptyText="No decision or pattern maps to this control yet." />
      <RelSection id={ANCHOR_ID.incident} title="Mitigates incidents" items={mitigatesIncidents} />
      <RelSection id={ANCHOR_ID.board_question} title="Board questions" items={boardQuestions} />
      <RelationshipReasoning node={node} />
      <CitationsSection node={node} />
      <HistorySection node={node} />
      <ConfidenceSection node={node} />
    </article>
  );
}
