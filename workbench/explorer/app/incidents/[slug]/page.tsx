import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { nodesByType, getNode, relatedByVerb } from "@/lib/data";
import { DetailHeader } from "@/components/DetailHeader";
import { RelationshipChain } from "@/components/RelationshipChain";
import { RelSection } from "@/components/RelSection";
import { RelationshipReasoning } from "@/components/RelationshipReasoning";
import { CitationsSection, HistorySection, ConfidenceSection } from "@/components/CitationsHistory";
import { SeverityBadge } from "@/components/Badge";
import { ANCHOR_ID } from "@/lib/anchors";

export function generateStaticParams() {
  return nodesByType("incident").map((n) => ({ slug: n.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const node = getNode("incident", slug);
  if (!node) return {};
  return {
    title: node.title,
    description: node.description,
    alternates: { canonical: `/incidents/${node.slug}/` },
    openGraph: { title: node.title, description: node.description },
  };
}

export default async function IncidentDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const node = getNode("incident", slug);
  if (!node) notFound();

  const decisions = relatedByVerb(node, "MITIGATED_BY", "out").filter((r) => r.other_type === "decision");
  const patterns = relatedByVerb(node, "MITIGATED_BY", "out").filter((r) => r.other_type === "pattern");
  const controls = relatedByVerb(node, "MITIGATED_BY", "out").filter((r) => r.other_type === "control");
  const boardQuestions = [
    ...relatedByVerb(node, "RAISES_BOARD_QUESTION", "out"),
    ...relatedByVerb(node, "RESULTED_FROM", "in").filter((r) => r.other_type === "board_question"),
  ];
  const resultingDecisions = relatedByVerb(node, "RESULTED_FROM", "in").filter((r) => r.other_type === "decision");

  return (
    <article>
      <DetailHeader node={node} />
      <RelationshipChain node={node} />

      <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
        <h2 className="mb-2 text-base font-semibold text-ink-900">What happened</h2>
        {node.root_cause && <p className="prose-body">{node.root_cause}</p>}
        <dl className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          {node.occurred_date && (
            <div>
              <dt className="text-xs text-ink-400">Occurred</dt>
              <dd className="text-ink-700">{node.occurred_date}</dd>
            </div>
          )}
          {node.severity && (
            <div>
              <dt className="text-xs text-ink-400">Severity</dt>
              <dd>
                <SeverityBadge value={node.severity} />
              </dd>
            </div>
          )}
          {node.ai_system_category && (
            <div>
              <dt className="text-xs text-ink-400">AI system category</dt>
              <dd className="text-ink-700 capitalize">{node.ai_system_category.replace(/_/g, " ")}</dd>
            </div>
          )}
          {node.jurisdiction && node.jurisdiction.length > 0 && (
            <div>
              <dt className="text-xs text-ink-400">Jurisdiction</dt>
              <dd className="text-ink-700">{node.jurisdiction.join(", ")}</dd>
            </div>
          )}
          {node.harm_types && node.harm_types.length > 0 && (
            <div className="col-span-2">
              <dt className="text-xs text-ink-400">Harm types</dt>
              <dd className="text-ink-700 capitalize">{node.harm_types.map((h) => h.replace(/_/g, " ")).join(", ")}</dd>
            </div>
          )}
          {node.organizations_involved && node.organizations_involved.length > 0 && (
            <div className="col-span-2">
              <dt className="text-xs text-ink-400">Organizations involved</dt>
              <dd className="text-ink-700">{node.organizations_involved.join(", ")}</dd>
            </div>
          )}
        </dl>
      </section>

      <RelSection id={ANCHOR_ID.decision} title="Governance decision(s) triggered" items={[...decisions, ...resultingDecisions]} />
      <RelSection id={ANCHOR_ID.pattern} title="Patterns that would mitigate this" items={patterns} />
      <RelSection id={ANCHOR_ID.control} title="Framework controls implicated" items={controls} />
      <RelSection id={ANCHOR_ID.board_question} title="Board questions raised" items={boardQuestions} />
      <RelationshipReasoning node={node} />
      <CitationsSection node={node} />
      <HistorySection node={node} />
      <ConfidenceSection node={node} />
    </article>
  );
}
