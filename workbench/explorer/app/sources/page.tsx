export const metadata = { title: "Source Transparency — AI Governance Workbench" };

const SOURCE_TYPES: { label: string; note: string }[] = [
  { label: "Regulator", note: "An order, guidance document, or enforcement action issued directly by a regulatory body — preferred over reporting about it whenever the primary document is public." },
  { label: "Legislation", note: "The text of a statute, regulation, or directive itself, cited to the specific article or provision." },
  { label: "Court judgment", note: "A court's or tribunal's own ruling, read for its actual holding — updated if a ruling is appealed, reversed, or vacated." },
  { label: "Standards body", note: "A published standard or framework document from its issuing body (NIST, ISO/IEC, IEEE, and similar)." },
  { label: "Company statement", note: "A statement made directly by the organization involved — read critically, and superseded by regulator or court findings where the two conflict." },
  { label: "News publication", note: "Reporting from an outlet with an editorial process — often the only public record an incident has, used accordingly." },
  { label: "Academic paper", note: "Peer-reviewed research — strong for a technical or empirical claim, rarely sufficient alone for a governance-failure claim." },
  { label: "Other", note: "A legitimate source that doesn't fit the categories above (a parliamentary report, an FOIA disclosure) — not a lower-quality default." },
];

const CONFIDENCE_STATES: { label: string; note: string; color: string }[] = [
  { label: "Verified", note: "Independently corroborated against primary sources by more than one reviewer. The highest bar in the dataset.", color: "text-emerald-700" },
  { label: "Reviewed", note: "Checked by at least one qualified human reviewer against its cited sources, but not yet independently re-verified by a second party.", color: "text-accent-700" },
  { label: "Draft", note: "Authored — by a human or AI-assisted — but not yet reviewed by anyone besides its author.", color: "text-amber-700" },
  { label: "Community", note: "Submitted by a community contributor; may be well-sourced, but hasn't been through the project's own review process yet.", color: "text-ink-600" },
  { label: "Archived", note: "Was previously Verified or Reviewed, but is retained for historical/traceability reasons rather than current best knowledge.", color: "text-ink-400" },
];

export default function SourcesPage() {
  return (
    <article className="max-w-3xl">
      <div className="mb-8 border-b border-ink-200 pb-6">
        <h1 className="text-2xl font-semibold text-ink-900 sm:text-3xl">Source Transparency</h1>
        <p className="prose-body mt-3">
          Where information in this dataset comes from, and how much it should be trusted, are two different
          questions — this page answers both. The full policies are <code className="text-ink-600">CITATION_POLICY.md</code>{" "}
          and <code className="text-ink-600">docs/confidence-model.md</code> in the repository; this is the
          practitioner-readable version.
        </p>
      </div>

      <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
        <h2 className="text-lg font-semibold text-ink-900">Where claims come from</h2>
        <p className="prose-body mt-2 mb-4">
          Every citation on every object declares one of eight source types, so a reader can weigh it appropriately
          rather than treat every citation as equally authoritative.
        </p>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {SOURCE_TYPES.map((s) => (
            <div key={s.label} className="card p-3">
              <dt className="text-sm font-semibold text-ink-900">{s.label}</dt>
              <dd className="mt-1 text-xs leading-relaxed text-ink-500">{s.note}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="border-t border-ink-200 py-6">
        <h2 className="text-lg font-semibold text-ink-900">How confidence is assigned</h2>
        <p className="prose-body mt-2 mb-4">
          Confidence is a statement about <strong>how a claim was checked</strong>, never about how important or
          well-known it is. A famous incident with one unverified source stays low-confidence; an obscure ruling
          confirmed by two independent reviewers against the primary document reaches the top tier.
        </p>
        <div className="flex flex-col gap-2">
          {CONFIDENCE_STATES.map((c) => (
            <div key={c.label} className="flex items-start gap-3 border-b border-ink-100 py-2 last:border-b-0">
              <span className={`w-20 flex-shrink-0 text-sm font-semibold ${c.color}`}>{c.label}</span>
              <span className="text-sm text-ink-600">{c.note}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="border-t border-ink-200 py-6">
        <h2 className="text-lg font-semibold text-ink-900">What we distinguish</h2>
        <p className="prose-body mt-2">
          Not every source carries the same evidentiary weight, and the dataset is written to reflect that: a
          regulator&rsquo;s own order outweighs its press release about that order; a court&rsquo;s holding outweighs
          a party&rsquo;s characterization of it; a single news article can establish that an incident occurred but
          is treated as provisional until corroborated; a vendor&rsquo;s own blog post is usable for what the vendor
          claims about itself, never as independent confirmation of a claim about itself. See{" "}
          <a href="/standards/#evidence-standards" className="text-accent-600 hover:underline">
            Evidence Standards
          </a>{" "}
          on the Our Standards page for the full hierarchy.
        </p>
      </section>

      <section className="border-t border-ink-200 py-6">
        <h2 className="text-lg font-semibold text-ink-900">Facts vs. editorial analysis</h2>
        <p className="prose-body mt-2">
          A node detail page distinguishes what a source established from what the Workbench&rsquo;s editorial
          process concluded from it. A Governance Decision is an editorial synthesis — the mapping from a documented
          incident to a specific, testable governance commitment is the project&rsquo;s own analysis, stated as
          such, and its <code className="text-ink-600">confidence</code> field and relationship{" "}
          <code className="text-ink-600">reason</code> text exist specifically so that analysis is never presented
          as an official determination. Where a page states what a court or regulator found, that is a fact,
          attributed; where it states which pattern most directly mitigates that finding, that is the Workbench&rsquo;s
          editorial conclusion, not a fact about the world.
        </p>
      </section>
    </article>
  );
}
