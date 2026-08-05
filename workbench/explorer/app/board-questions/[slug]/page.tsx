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
  return nodesByType("board_question").map((n) => ({ slug: n.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const node = getNode("board_question", slug);
  if (!node) return {};
  return {
    title: node.title,
    description: node.description,
    alternates: { canonical: `/board-questions/${node.slug}/` },
    openGraph: { title: node.title, description: node.description },
  };
}

export default async function BoardQuestionDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const node = getNode("board_question", slug);
  if (!node) notFound();

  const raisedBy = relatedByVerb(node, "RAISES_BOARD_QUESTION", "in");
  const resultedFromIncidents = relatedByVerb(node, "RESULTED_FROM", "out").filter((r) => r.other_type === "incident");

  return (
    <article>
      <DetailHeader node={node} />
      <RelationshipChain node={node} />

      <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
        {node.question_text && (
          <div className="mb-4 rounded-md border border-sky-200 bg-sky-50 p-4">
            <div className="field-label mb-1 text-sky-700">The question</div>
            <p className="text-sm font-medium leading-relaxed text-ink-900">{node.question_text}</p>
          </div>
        )}
        {node.rationale && (
          <div className="mb-3">
            <div className="field-label mb-1">Rationale</div>
            <p className="prose-body">{node.rationale}</p>
          </div>
        )}
        {node.audience && node.audience.length > 0 && (
          <div className="mb-3 text-sm">
            <span className="field-label mr-2">Audience</span>
            <span className="text-ink-700 capitalize">{node.audience.map((a) => a.replace(/_/g, " ")).join(", ")}</span>
          </div>
        )}
        {node.follow_up_actions && node.follow_up_actions.length > 0 && (
          <div>
            <div className="field-label mb-1">Follow-up actions</div>
            <ul className="list-disc space-y-1 pl-5 text-sm text-ink-700">
              {node.follow_up_actions.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <RelSection id={ANCHOR_ID.decision} title="Raised by" items={raisedBy} />
      <RelSection id={ANCHOR_ID.incident} title="Resulted directly from" items={resultedFromIncidents} emptyText="Not tied to one specific triggering incident." />
      <RelationshipReasoning node={node} />
      <CitationsSection node={node} />
      <HistorySection node={node} />
      <ConfidenceSection node={node} />
    </article>
  );
}
