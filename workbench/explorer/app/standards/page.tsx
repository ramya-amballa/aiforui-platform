import { graph } from "@/lib/data";
import { QualityDashboard } from "@/components/QualityDashboard";

export const metadata = { title: "Our Standards — AI Governance Workbench" };

function Section({ id, title, lede, items }: { id: string; title: string; lede: string; items: string[] }) {
  return (
    <section id={id} className="scroll-mt-20 border-t border-ink-200 py-8 first:border-t-0 first:pt-0">
      <h2 className="text-lg font-semibold text-ink-900">{title}</h2>
      <p className="prose-body mt-2 max-w-2xl">{lede}</p>
      <ul className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
        {items.map((item) => (
          <li key={item} className="flex items-start gap-2 text-sm text-ink-700">
            <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-ink-400" />
            {item}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default function StandardsPage() {
  return (
    <article>
      <div className="mb-10 max-w-3xl border-b border-ink-200 pb-8">
        <h1 className="text-2xl font-semibold text-ink-900 sm:text-3xl">Our Standards</h1>
        <p className="prose-body mt-3">
          The AI Governance Workbench is built as a curated practitioner reference, not a news aggregator or a
          general-purpose wiki. Every canonical object — every Governance Decision, Incident, Design Pattern,
          Framework Control, Evidence Type, and Board Question — is expected to meet explicit standards for
          accuracy, traceability, editorial review, and governance before it enters the dataset. This page states
          those standards in plain language; the full policies they&rsquo;re drawn from are versioned documents in the
          repository (<code className="text-ink-600">EDITORIAL_POLICY.md</code>, <code className="text-ink-600">CITATION_POLICY.md</code>,{" "}
          <code className="text-ink-600">REVIEW_PROCESS.md</code>, and related documents), and the numbers below are
          computed live from the current dataset, not asserted.
        </p>
      </div>

      <Section
        id="deterministic-validation"
        title="Deterministic Validation"
        lede="Nothing about whether an object is well-formed is a matter of opinion. A fixed set of rules, run the same way every time, decides that — not a model's judgment call."
        items={[
          "No AI-generated facts enter the canonical dataset unreviewed",
          "No opaque scoring — every score's inputs and weights are published",
          "No hidden reasoning — every relationship states, in plain language, why it exists",
          "No probabilistic data model — an object either satisfies the schema or it doesn't",
          "Everything is version-controlled and reproducible from the repository alone",
        ]}
      />

      <Section
        id="human-review"
        title="Human Review"
        lede="AI may assist with drafting a candidate entry. It does not decide what becomes canonical knowledge — a named human reviewer does."
        items={[
          "Only human-reviewed content is promoted to canonical status",
          "Every object records its version history, append-only and auditable",
          "Every object records its review status against the project's confidence vocabulary",
          "Every object records a stated confidence level, never left implicit",
          "Every object's editorial lifecycle — created, reviewed, approved, retired — is on the record",
        ]}
      />

      <Section
        id="evidence-standards"
        title="Evidence Standards"
        lede="Every governance claim in this dataset is expected to be supported by a source a reader can independently check — and not every source carries the same weight."
        items={[
          "Court judgments, read for their actual holding, not a party's characterization of it",
          "Regulations and legislation, cited to the specific article or provision",
          "Government and regulatory publications, preferred over secondhand reporting when public",
          "Standards-body publications (NIST, ISO/IEC, and similar)",
          "Technical and academic documentation, weighed for what it can and can't establish alone",
          "Reputable secondary sources — news reporting is often the only public record an incident has, and is used accordingly, with independent corroboration expected before the highest confidence levels",
        ]}
      />

      <Section
        id="connected-knowledge"
        title="Connected Knowledge"
        lede="An isolated fact is invisible in a knowledge graph. Every canonical object is required to connect to the rest of the dataset, with the connection's meaning stated, not implied."
        items={[
          "Zero orphan nodes — enforced as a hard gate, not a guideline",
          "Every relationship validated against a fixed, published ontology of allowed connections",
          "Every relationship carries a stated rationale for why it exists",
          "Graph integrity — no dangling references, no invalid relationship types, no unexplained cycles",
        ]}
      />

      <Section
        id="editorial-governance"
        title="Editorial Governance"
        lede="Every incident is analyzed the same way, regardless of how it was sourced or how prominently it was covered. The Workbench is not collecting news stories — it is extracting governance structure from them."
        items={[
          "What Governance Decision was actually involved, not merely what happened",
          "What Design Pattern would most directly have mitigated the outcome",
          "Which Framework Controls are genuinely and directly applicable — mapped for relevance, not volume",
          "What Evidence an auditor would actually ask to see",
          "What Board Question follows, stated once, concisely, and made actionable",
        ]}
      />

      <Section
        id="continuous-quality-improvement"
        title="Continuous Quality Improvement"
        lede="Every release is evaluated against the same deterministic gates before it ships — see RELEASE_CHECKLIST.md for the full procedure this dashboard reflects."
        items={[
          "Schema validation across every canonical object",
          "Type safety across the validator, editorial tooling, and this site",
          "A repository-wide editorial audit for naming, terminology, and relationship-rationale consistency",
          "A citation-completeness score, tracked and published even when it isn't where it needs to be yet",
          "A documented release checklist every edition passes through before publication",
        ]}
      />

      <section id="quality-dashboard-section" className="border-t border-ink-200 pt-8">
        <h2 className="mb-2 text-lg font-semibold text-ink-900">Quality Dashboard</h2>
        <p className="prose-body mb-4 max-w-2xl">
          These numbers are computed at build time, directly from the canonical dataset and the project&rsquo;s own
          validation and editorial tooling — the same checks, run the same way, that gate every commit. Nothing on
          this page is asserted without a corresponding, reproducible check.
        </p>
        <QualityDashboard quality={graph.quality} />
      </section>
    </article>
  );
}
