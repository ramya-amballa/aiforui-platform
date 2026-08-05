export const metadata = { title: "Legal Disclaimer — AI Governance Workbench" };

function P({ children }: { children: React.ReactNode }) {
  return <p className="prose-body mt-3">{children}</p>;
}

function H2({ children }: { children: React.ReactNode }) {
  return <h2 className="mt-8 text-lg font-semibold text-ink-900">{children}</h2>;
}

export default function LegalPage() {
  return (
    <article className="max-w-3xl">
      <div className="mb-8 border-b border-ink-200 pb-6">
        <h1 className="text-2xl font-semibold text-ink-900 sm:text-3xl">Legal Disclaimer</h1>
        <p className="prose-body mt-3">
          The full version of this document is <code className="text-ink-600">LEGAL_DISCLAIMER.md</code> in the
          repository. This page is that document, rendered for practitioners reading the Explorer directly.
        </p>
      </div>

      <H2>Purpose</H2>
      <P>
        The AI Governance Workbench is provided for <strong>educational and informational purposes only</strong>. It
        is not legal advice, regulatory advice, audit advice, or professional advice of any kind, and using it does
        not create an attorney-client, advisory, consulting, or any other professional relationship between you and
        the AI Governance Workbench, AI for U&amp;I, or any contributor.
      </P>
      <P>
        Nothing on this site or in the underlying repository is an official interpretation of any law, regulation,
        framework, or standard. Where a canonical object describes what a court, regulator, or standards body found,
        ordered, or published, that description is the Workbench&rsquo;s own summary — always verify the underlying
        primary source (linked in the object&rsquo;s citations) before relying on it for any actual decision.
      </P>

      <H2>No warranty</H2>
      <P>
        The dataset is provided &ldquo;as is,&rdquo; without warranty of any kind, express or implied, including
        without limitation any warranty of accuracy, completeness, merchantability, or fitness for a particular
        purpose. AI governance is a fast-moving area: laws change, rulings are appealed, and regulatory guidance is
        superseded. Every object&rsquo;s <strong>confidence</strong> and <strong>status</strong> fields exist
        specifically to signal how much independent verification it has actually received — a{" "}
        <code className="text-ink-600">Community</code> or <code className="text-ink-600">Draft</code> confidence
        object has not been independently verified and should be treated accordingly.
      </P>

      <H2>Not professional reliance</H2>
      <P>
        If you are facing an actual governance, compliance, legal, or regulatory decision, consult qualified counsel
        or a licensed professional in the relevant jurisdiction. Do not treat any Governance Decision, Design
        Pattern, Framework Control, Evidence Type, or Board Question in this dataset as a substitute for that
        consultation, and do not represent to a regulator, court, auditor, or board that a position is defensible
        solely because the Workbench documents it.
      </P>

      <H2>How factual claims are written</H2>
      <P>
        Every factual claim about a specific incident is attributed to its source rather than stated as the
        Workbench&rsquo;s own finding — &ldquo;the FTC alleged,&rdquo; &ldquo;the CJEU held,&rdquo; &ldquo;the
        company announced,&rdquo; not a bare assertion. Where an allegation, complaint, or investigation has not
        resulted in a final judgment or determination, the object&rsquo;s description says so and does not present
        the outcome as settled. See <a href="/standards/" className="text-accent-600 hover:underline">Our Standards</a> for
        the full editorial discipline this is drawn from.
      </P>

      <H2>Named organizations</H2>
      <P>
        This dataset names real companies, regulators, courts, and individuals because accurately identifying the
        parties to a documented, sourced incident is necessary for the dataset to be verifiable at all. Naming an
        organization in connection with a documented incident, ruling, or regulatory action is not an assertion that
        the organization is generally untrustworthy, and does not imply any endorsement, affiliation, sponsorship,
        or business relationship between that organization and the AI Governance Workbench or AI for U&amp;I, in
        either direction.
      </P>

      <H2>Copyright</H2>
      <P>
        Canonical objects summarize and characterize their sources in the project&rsquo;s own words. Where a source
        is quoted, the quotation is a short, direct excerpt offered to support a specific claim, not a reproduction
        of the source in whole or in substantial part. Every citation links to the original source.
      </P>

      <H2>Corrections</H2>
      <P>
        Errors are expected in a reference of this size and are corrected in the open. See{" "}
        <a href="/corrections/" className="text-accent-600 hover:underline">
          how to report an error
        </a>{" "}
        for how corrections are handled once reported.
      </P>

      <div className="mt-10 border-t border-ink-200 pt-6 text-sm italic text-ink-500">
        This disclaimer was drafted to reflect the project&rsquo;s actual editorial practice, honestly and in good
        faith. It is not itself a substitute for review by qualified counsel, and the maintainers should obtain that
        review before treating this document as final.
      </div>
    </article>
  );
}
