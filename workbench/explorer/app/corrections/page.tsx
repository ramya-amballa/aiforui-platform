export const metadata = { title: "Corrections — AI Governance Workbench" };

export default function CorrectionsPage() {
  return (
    <article className="max-w-3xl">
      <div className="mb-8 border-b border-ink-200 pb-6">
        <h1 className="text-2xl font-semibold text-ink-900 sm:text-3xl">Corrections</h1>
        <p className="prose-body mt-3">
          Errors are expected in a reference of this size. What matters is what happens after one is found — this
          page states that plainly, drawn from <code className="text-ink-600">EDITORIAL_POLICY.md</code>&rsquo;s
          correction policy in the repository.
        </p>
      </div>

      <section className="border-t border-ink-200 py-6 first:border-t-0 first:pt-0">
        <h2 className="text-lg font-semibold text-ink-900">What you can report</h2>
        <ul className="mt-3 space-y-2 text-sm text-ink-700">
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-ink-400" />A factual error in an
            incident, decision, pattern, control, evidence type, or board question
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-ink-400" />A broken, stale, or
            link-rotted citation
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-ink-400" />
            Outdated information — a ruling that was appealed, a settlement that was reached, a regulatory matter
            that was resolved
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-ink-400" />A relationship whose stated
            reason no longer holds, or a citation that doesn&rsquo;t actually support the claim it&rsquo;s attached to
          </li>
        </ul>
      </section>

      <section className="border-t border-ink-200 py-6">
        <h2 className="text-lg font-semibold text-ink-900">How to report one</h2>
        <p className="prose-body mt-3">
          The dataset is a public git repository. Open a pull request or an issue against the specific object&rsquo;s
          file under <code className="text-ink-600">/workbench/data</code>, citing the source that supports the
          correction. If you&rsquo;re not comfortable with git, describe the error, the object&rsquo;s ID (e.g.{" "}
          <code className="text-ink-600">INC-012</code>), and a source for the correction, and a maintainer will
          make the edit.
        </p>
      </section>

      <section className="border-t border-ink-200 py-6">
        <h2 className="text-lg font-semibold text-ink-900">How corrections are handled</h2>
        <p className="prose-body mt-3">
          A correction goes through the same review path as any other change to the dataset — it is not a special,
          lower-scrutiny path, and it is not a higher one either. Concretely:
        </p>
        <ul className="mt-3 space-y-2 text-sm text-ink-700">
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-ink-400" />
            The object&rsquo;s <code className="text-ink-600">version</code> is bumped and a{" "}
            <code className="text-ink-600">history</code> entry is added stating what was wrong and what changed —
            the record of the error and its correction is kept, not erased
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-ink-400" />A material factual error is
            corrected as soon as it&rsquo;s confirmed, independent of any release schedule — it is not left live
            until the next numbered edition
          </li>
          <li className="flex items-start gap-2">
            <span className="mt-1.5 h-1 w-1 flex-shrink-0 rounded-full bg-ink-400" />
            If the underlying claim no longer holds at all (a ruling was overturned, a finding was vacated), the
            object moves toward <code className="text-ink-600">status: retracted</code> rather than being quietly
            edited to look as if it always said something else
          </li>
        </ul>
      </section>

      <section className="border-t border-ink-200 py-6">
        <h2 className="text-lg font-semibold text-ink-900">Published transparently</h2>
        <p className="prose-body mt-3">
          Every correction is a public commit, and every object&rsquo;s <strong>History</strong> section (visible on
          its own page) shows every correction it has ever received, who made it, and why. There is no private
          errata list — the correction record <em>is</em> the object&rsquo;s history.
        </p>
      </section>
    </article>
  );
}
