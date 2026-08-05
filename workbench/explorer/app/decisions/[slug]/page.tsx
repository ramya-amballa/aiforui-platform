import { notFound } from "next/navigation";
import { nodesByType, getNode, relatedByVerb } from "@/lib/data";
import { DetailHeader } from "@/components/DetailHeader";
import { RelationshipChain } from "@/components/RelationshipChain";
import { RelSection } from "@/components/RelSection";
import { RiskSummary } from "@/components/RiskSummary";
import { RelationshipReasoning } from "@/components/RelationshipReasoning";
import { CitationsSection, HistorySection, ConfidenceSection } from "@/components/CitationsHistory";
import { ANCHOR_ID } from "@/lib/anchors";

export function generateStaticParams() {
  return nodesByType("decision").map((n) => ({ slug: n.slug }));
}

export default async function DecisionDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const node = getNode("decision", slug);
  if (!node) notFound();

  const linkedIncidents = [
    ...relatedByVerb(node, "RESULTED_FROM", "out").filter((r) => r.other_type === "incident"),
    ...relatedByVerb(node, "MITIGATED_BY", "in").filter((r) => r.other_type === "incident"),
  ];
  const linkedPatterns = relatedByVerb(node, "IMPLEMENTED_BY", "out").filter((r) => r.other_type === "pattern");
  const requiredEvidence = relatedByVerb(node, "REQUIRES_EVIDENCE", "out");
  const frameworkControls = relatedByVerb(node, "SATISFIES_CONTROL", "out");
  const boardQuestions = relatedByVerb(node, "RAISES_BOARD_QUESTION", "out");
  const relatedDecisions = [
    ...relatedByVerb(node, "RESULTED_FROM", "out").filter((r) => r.other_type === "decision"),
    ...relatedByVerb(node, "RESULTED_FROM", "in").filter((r) => r.other_type === "decision"),
    ...[...relatedByVerb(node, "RELATED_TO", "out"), ...relatedByVerb(node, "RELATED_TO", "in")].filter((r) => r.other_type === "decision"),
  ];

  const whyItMatters = node.problem_statement || node.decision_rationale || node.description;

  return (
    <article>
      <DetailHeader node={node} />
      <RelationshipChain node={node} />

      {node.decision_statement && (
        <div className="mb-8 rounded-md border border-accent-200 bg-accent-50 p-4">
          <div className="field-label mb-1 text-accent-700">Decision statement</div>
          <p className="text-sm font-medium leading-relaxed text-ink-900">{node.decision_statement}</p>
        </div>
      )}

      <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
        <h2 className="mb-2 text-base font-semibold text-ink-900">Why this decision matters</h2>
        <p className="prose-body">{whyItMatters}</p>
        {node.decision_rationale && node.decision_rationale !== whyItMatters && (
          <p className="prose-body mt-2">{node.decision_rationale}</p>
        )}
        {node.outcome && (
          <div className="mt-3 text-sm">
            <span className="field-label mr-2">Outcome</span>
            <span className="text-ink-700">{node.outcome}</span>
          </div>
        )}
        <dl className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
          {node.decision_type && (
            <div>
              <dt className="text-xs text-ink-400">Type</dt>
              <dd className="text-ink-700 capitalize">{node.decision_type.replace(/_/g, " ")}</dd>
            </div>
          )}
          {node.governing_body && (
            <div>
              <dt className="text-xs text-ink-400">Governing body</dt>
              <dd className="text-ink-700">{node.governing_body}</dd>
            </div>
          )}
          {node.jurisdiction && node.jurisdiction.length > 0 && (
            <div>
              <dt className="text-xs text-ink-400">Jurisdiction</dt>
              <dd className="text-ink-700">{node.jurisdiction.join(", ")}</dd>
            </div>
          )}
        </dl>
      </section>

      <RiskSummary node={node} />
      <RelSection id={ANCHOR_ID.incident} title="Linked incidents" items={linkedIncidents} />
      <RelSection id={ANCHOR_ID.pattern} title="Linked design patterns" items={linkedPatterns} />
      <RelSection id={ANCHOR_ID.evidence} title="Required evidence" items={requiredEvidence} />
      <RelSection id={ANCHOR_ID.control} title="Framework controls" items={frameworkControls} />
      <RelSection id={ANCHOR_ID.board_question} title="Board questions" items={boardQuestions} />
      <RelSection id={ANCHOR_ID.decision} title="Related decisions" items={relatedDecisions} emptyText="No directly related decisions." />
      <RelationshipReasoning node={node} />
      <CitationsSection node={node} />
      <HistorySection node={node} />
      <ConfidenceSection node={node} />
    </article>
  );
}
