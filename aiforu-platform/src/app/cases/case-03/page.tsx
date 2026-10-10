import type { Metadata } from "next";
import styles from "./case-03.module.css";

export const metadata: Metadata = {
  title: "Case 03: The certificate predates the feature.",
  description:
    "Simulated case · Qatar financial services context. A provider holds a current SOC 2 report and ISO certificate, then adds an AI assistant. What does the assurance actually cover?",
  alternates: {
    canonical: "https://www.aiforui.org/cases/case-03",
  },
  openGraph: {
    title: "Case 03: The certificate predates the feature.",
    description: "Simulated case. A timeline is not a coverage conclusion. Separating when assurance was issued, what it covers, and whether it establishes anything about a new AI feature.",
    url: "https://www.aiforui.org/cases/case-03",
  },
};

export default function Case03Page() {
  return (
    <main className={styles.wrap}>
      <p className={styles.eyebrow}>AI Governance Evidence Portfolio · Case Study 03</p>
      <p className={styles.toplabels}>
        <span className={`${styles.chip} ${styles["c-sim"]} ${styles.big}`}>Simulated case · Qatar financial services context</span>
        <span className={`${styles.chip} ${styles["c-pend"]} ${styles.big}`}>Recommended: restrict pending verification</span>
      </p>
      <h1 className={styles.h1}>The certificate predates the feature.</h1>
      <p className={styles.sub}>Ramya Amballa, AI for U&amp;I</p>
      <div className={styles.meta}>
        <div>
          <span>Industry</span>Financial services
        </div>
        <div>
          <span>Setting</span>Qatar
        </div>
        <div>
          <span>Use case</span>Business-critical SaaS with an AI assistant
        </div>
        <div>
          <span>Environment</span>SaaS and a third-party model provider
        </div>
        <div>
          <span>Tension</span>Assurance versus actual coverage
        </div>
      </div>
      <div className={styles.simbox}>
        <strong style={{ color: "inherit" }}>Simulated case.</strong> Dunmore Gulf Bank (DGB), Brindlecast and Halvane
        AI are fictional. The bank, the provider and the evidence are fictional. No real bank, provider, incident or
        assessment is represented. No verification test has been performed. The governance reasoning and the work
        products are mine. This is not a client engagement.
      </div>
      <div className={styles.legend}>
        <p>How to read this case</p>
        <ul>
          <li>
            <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>invented for the scenario
          </li>
          <li>
            <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>my recommended control or decision
          </li>
          <li>
            <span className={`${styles.chip} ${styles["c-pend"]}`}>Open decision</span>a decision for a named
            specialist or owner
          </li>
          <li>
            <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>a question the evidence does
            not answer
          </li>
        </ul>
      </div>
      <p className={styles.lede}>
        A cloud provider holds a current SOC 2 report and a current ISO 27001 certificate. Then it adds an AI
        assistant to the platform you run a core business process on. Both documents now predate the feature. That
        is a timeline fact. It does not tell you the feature is covered, and it does not tell you it is not. This
        case shows how a bank&apos;s third-party risk team keeps three questions apart: when the assurance was
        issued, what it says it covers, and whether it establishes anything about this feature.
      </p>
      <ul className={styles.tags}>
        <li>Third-party risk</li>
        <li>Vendor assurance</li>
        <li>SaaS and AI</li>
        <li>Evidence reasoning</li>
      </ul>

      <section className={`${styles.res} ${styles.screenOnly}`} aria-label="Resources">
        <h2>Available resources</h2>
        <ul>
          <li>
            <a href="#the-situation">Read the case study</a>
          </li>
          <li>
            <a href="#decision">See the decision</a>
          </li>
          <li>
            <a href="/downloads/case-03-case-study.pdf">Download the two-page case summary (PDF)</a>
          </li>
          <li>
            <a href="/downloads/case-03-saas-ai-assurance-scope-check-template.xlsx">
              Free download: SaaS AI Assurance-Scope Check (Excel)
            </a>
          </li>
        </ul>
      </section>

      <div className={styles.conds} style={{ borderColor: "#D9C4E8" }}>
        <h3>
          Where the case stands <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
        </h3>
        <ul className={styles.body} style={{ margin: 0 }}>
          <li>Five findings are open. None states a breach, non-compliance or loss of data.</li>
          <li>12 verification tests have not yet been performed. Findings rest on a simulated document review.</li>
          <li>
            Whether the assistant is active in the bank&apos;s tenant, and whether any data reached the model
            provider, is not established.
          </li>
          <li>The renewal is 60 days away. The recommended decision is to restrict the feature pending verification.</li>
        </ul>
      </div>

      <h2 id="the-situation" className={styles.h2}>
        The situation <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
      </h2>
      <p>
        A Qatar bank runs customer case management on a SaaS platform. The platform is business-critical. The
        bank&apos;s renewal is 60 days away.
      </p>
      <p>
        The provider adds an AI assistant. It summarises cases and drafts replies, using a third-party model
        provider. Case notes can hold customer identifiers and account details.
      </p>
      <p>
        The bank&apos;s third-party risk team asks for the usual package: the SOC 2 report, the ISO 27001
        certificate, the sub-processor list and the AI and data-use terms. At first glance it looks reassuring. Then
        the dates stop lining up.
      </p>

      <h2 className={styles.h2}>The question that actually mattered</h2>
      <p>
        Not &quot;does the provider have SOC 2?&quot; It does. The question is this: what does the provider&apos;s
        assurance actually cover, and what must be established before the bank can rely on it for this feature?
      </p>
      <p>Three questions are easy to blur. I kept them apart.</p>
      <table className={styles.kv}>
        <tbody>
          <tr>
            <th>1. When was the assurance issued?</th>
            <td>Answered by the report period or certificate dates. A timeline fact. Here, both predate the launch.</td>
          </tr>
          <tr>
            <th>2. What does it say it covers?</th>
            <td>Answered by the system description or scope statement. Not yet examined.</td>
          </tr>
          <tr>
            <th>3. Does that coverage establish anything about this feature?</th>
            <td>Answered only by feature-specific verification. Not yet performed.</td>
          </tr>
        </tbody>
      </table>

      <h2 className={styles.h2}>
        What the review found <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
      </h2>
      <p>
        <strong>The assurance predates the feature.</strong> The SOC 2 reporting period ends before the assistant
        launched. The ISO certificate was issued, and last audited, before it too. Both are established.{" "}
        <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>Whether either scope reaches the
        feature is not yet known. That the assurance predates the feature does not by itself establish that the
        feature is outside the assurance scope. &quot;Predates&quot; is a timeline observation, not a coverage
        conclusion. So I recorded the SOC 2 position as outside report period and the ISO position as scope unclear.
        Two instruments, two different evidence problems.
      </p>
      <p>
        <strong>The model provider is named but not listed.</strong> The provider&apos;s AI documentation names the
        model provider. It is absent from the sub-processor list.{" "}
        <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>Why, and what the contract says
        about it, is not established. That is a discrepancy to resolve, not a breach to allege.
      </p>
      <p>
        <strong>The data-flow position is unclear.</strong> The only basis for any flow to the model provider is the
        provider&apos;s own documentation. <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>
        Whether the bank&apos;s data reaches it, or is retained or used for training, is not established. Nothing
        was tested.
      </p>
      <p>
        <strong>The feature is on by default.</strong>{" "}
        <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>Whether it is active in the
        bank&apos;s tenant, or anyone has used it, is not established. A feature that exists is not a feature that
        is switched on.
      </p>
      <p>
        <strong>Disabling may not mean what it sounds like.</strong> The provider says the assistant can be
        disabled. The opt-out wording does not explain what happens to data.{" "}
        <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>Whether the switch stops the
        underlying data flow, or only hides the assistant from users, is not established.
      </p>
      <p>The renewal date puts pressure on the decision. It is not evidence against the provider.</p>

      <figure className={styles.figure}>
        <div className={styles.panel} style={{ padding: "10px" }}>
          <svg
            viewBox="0 0 640 330"
            role="img"
            aria-label="Illustrative timeline. The SOC 2 reporting period and the ISO certificate dates all fall before the AI assistant launch. Whether either scope reaches the feature has not been examined."
          >
            <defs>
              <marker id="b" viewBox="0 0 10 10" refX={9} refY={5} markerWidth={7} markerHeight={7} orient="auto">
                <path d="M0,0 L10,5 L0,10 z" fill="#8A5A00" />
              </marker>
            </defs>
            <g fontFamily="inherit" fontSize={12}>
              <rect x={460} y={40} width={176} height={196} rx={6} fill="#FFF4D6" opacity={0.7} />
              <text x={548} y={58} textAnchor="middle" fill="#8A5A00" fontSize={11} fontWeight={600}>
                AFTER LAUNCH
              </text>
              <text x={548} y={74} textAnchor="middle" fill="#8A5A00" fontSize={10.5}>
                No assurance evidence
              </text>
              <text x={548} y={88} textAnchor="middle" fill="#8A5A00" fontSize={10.5}>
                examined for the feature
              </text>
              <text x={10} y={64} fill="#56616D" fontSize={11} fontWeight={600}>
                SOC 2 REPORTING PERIOD
              </text>
              <rect x={83} y={72} width={258} height={26} rx={4} fill="#0B2E59" />
              <text x={212} y={90} textAnchor="middle" fill="#fff" fontSize={11.5}>
                Period tested
              </text>
              <text x={10} y={132} fill="#56616D" fontSize={11} fontWeight={600}>
                ISO 27001 CERTIFICATE
              </text>
              <path d="M44 150 l7 7 l-7 7 l-7 -7 z" fill="#0B2E59" />
              <text x={44} y={182} textAnchor="middle" fontSize={10.5} fill="#14202E">
                Issued
              </text>
              <path d="M309 150 l7 7 l-7 7 l-7 -7 z" fill="#0B2E59" />
              <text x={309} y={182} textAnchor="middle" fontSize={10.5} fill="#14202E">
                Last audit
              </text>
              <line x1={44} y1={157} x2={309} y2={157} stroke="#0B2E59" strokeWidth={1.5} strokeDasharray="3 3" />
              <line x1={459} y1={40} x2={459} y2={236} stroke="#8A5A00" strokeWidth={2} />
              <text x={451} y={228} textAnchor="end" fill="#8A5A00" fontSize={11.5} fontWeight={600}>
                AI assistant launch
              </text>
              <line x1={543} y1={236} x2={543} y2={214} stroke="#56616D" strokeWidth={1.5} />
              <text x={543} y={208} textAnchor="middle" fontSize={10.5} fill="#56616D">
                Review
              </text>
              <line x1={585} y1={236} x2={585} y2={214} stroke="#B3261E" strokeWidth={1.5} />
              <text x={585} y={208} textAnchor="middle" fontSize={10.5} fill="#B3261E">
                Renewal
              </text>
              <line x1={30} y1={236} x2={620} y2={236} stroke="#8A96A3" strokeWidth={1.5} />
              <line x1={83} y1={232} x2={83} y2={241} stroke="#8A96A3" />
              <text x={83} y={254} textAnchor="middle" fontSize={10.5} fill="#56616D">
                Jan 2025
              </text>
              <line x1={341} y1={232} x2={341} y2={241} stroke="#8A96A3" />
              <text x={341} y={254} textAnchor="middle" fontSize={10.5} fill="#56616D">
                Jan 2026
              </text>
              <rect x={10} y={272} width={620} height={48} rx={6} fill="#F4F6F9" stroke="#D9DEE4" />
              <text x={22} y={291} fontSize={11.5} fill="#14202E">
                <tspan fontWeight={600}>Timeline fact:</tspan> both instruments end before the feature launched.
              </text>
              <text x={22} y={309} fontSize={11.5} fill="#14202E">
                <tspan fontWeight={600}>Not yet known:</tspan> whether either scope reaches the feature, and what
                evidence supports it.
              </text>
            </g>
          </svg>
        </div>
        <figcaption className={styles.figcaption}>
          Illustrative dates, to scale. The SOC 2 period and the ISO dates sit before the launch. That is a timeline
          fact. It says nothing yet about scope.
        </figcaption>
      </figure>

      <h2 className={styles.h2}>Rules I held to</h2>
      <ul className={styles.body}>
        <li>
          <strong>A timeline is not a coverage conclusion.</strong> A report that predates a feature has not been
          shown to exclude it.
        </li>
        <li>
          <strong>A provider&apos;s statement is not verification.</strong> It is recorded as documented by the
          provider until someone else has checked.
        </li>
        <li>
          <strong>A current certificate is not automatic coverage of a later feature.</strong> Neither document is
          treated as invalid. The question is whether it is evidence for this feature.
        </li>
        <li>
          <strong>A feature that exists is not a feature that is active.</strong>
        </li>
        <li>
          <strong>Disabling is not containment.</strong> It counts only when evidence shows the data flow stops.
        </li>
      </ul>

      <h2 id="decision" className={styles.h2}>
        The decision <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>
      </h2>
      <p>
        <strong>Restrict pending verification.</strong>
      </p>
      <p>
        Confirm the assistant&apos;s state in the bank&apos;s tenant and disable it now. Treat the feature as
        contained only when evidence establishes that disabling it stops the relevant data flow.
      </p>
      <p>
        The decision gate is 26 November, before the 11 December renewal. If that evidence is not in by then,
        negotiate a short renewal with the assistant excluded. Exit planning starts only if the provider cannot or
        will not provide the evidence.
      </p>
      <p>
        <strong>Can the bank rely on the existing assurance?</strong> Not yet, for this feature. The assurance is
        treated as valid. The open question is whether it provides evidence for this one.
      </p>
      <p>
        Continuing means renewing on assurance nobody has examined for this feature. Exiting is the highest-cost
        option: migrating case history, rebuilding integrations, running two systems in parallel and retraining
        staff. It is unlikely to finish in 60 days.
      </p>
      <div className={styles.conds}>
        <h3>What would move the decision</h3>
        <ol>
          <li>
            <strong>Towards continuing:</strong> the scope documents name the assistant, evidence dated after launch
            supports it, the contract position on the model provider is documented, and disabling is shown to stop
            the flow.
          </li>
          <li>
            <strong>Towards exit planning:</strong> the provider declines to give the evidence, or data still flows
            after disabling and the provider cannot correct it.
          </li>
        </ol>
      </div>

      <h2 className={styles.h2}>
        What I did not decide <span className={`${styles.chip} ${styles["c-pend"]}`}>Open decision</span>
      </h2>
      <p>
        Applicable Qatar regulatory requirements are not asserted here. Legal and Compliance would confirm them.
        Whether the contract permits the model provider is for Legal. Data classification, and whether the
        bank&apos;s data may be processed by the model provider, are for Data Governance and Legal. Whether a bridge
        letter can stand in for later-period evidence is for the accountable risk owner. Acceptance of any residual
        risk belongs to a named owner.
      </p>

      <h2 className={styles.h2}>How verification stays safe</h2>
      <p>
        No test uses production customer data. The bank cannot see a provider&apos;s server-to-server traffic from
        its own network. So the key test, whether disabling stops the data flow, needs evidence from the provider: a
        provider-run test with synthetic data and outbound request logs, or independent attestation. A pass shows
        behaviour at test time, not future behaviour.
      </p>

      <h2 className={styles.h2}>Challenging my own work</h2>
      <p>The package went through QA before it was frozen. The useful catches:</p>
      <ul className={styles.body}>
        <li>The 60-day renewal first sat in the findings. It is a decision constraint, not a control deficiency, so it moved.</li>
        <li>A single combined assurance verdict hid the fact that SOC 2 and ISO have different evidence problems. They now have a verdict each.</li>
        <li>&quot;Restrict&quot; first looked like the automatic answer. It is only an answer if the restriction can be shown to work.</li>
        <li>A test count that read &quot;4 of 4 performed&quot; could look like verification. It now also shows how many tests support reliance.</li>
      </ul>

      <h2 className={styles.h2}>What the package contains</h2>
      <div className={styles.contains}>
        <div>Findings and verification workbook</div>
        <div>Five findings, six established facts, seven open questions</div>
        <div>12 verification tests, none yet performed</div>
        <div>Coverage matrix tracing every gap to a test</div>
        <div>Two-page executive decision memo</div>
        <div>Reusable SaaS AI Assurance-Scope Check (free download)</div>
      </div>
      <p className={styles.small}>Published here: this page, the two-page summary and the free template.</p>
      <p className={styles.reg}>
        <strong>Reference.</strong> This case does not rely on any regulatory requirement. Any Qatar-specific
        requirement is for Legal and Compliance to confirm. The reasoning is professional opinion on simulated
        facts.
      </p>
      <p className={styles.foot}>
        Illustrative scenario. All organisations, findings, dates, approvals and evidence are simulated. Case 03 of
        the AI Governance Evidence Portfolio by Ramya Amballa, <a href="https://www.aiforui.org">AI for U&amp;I</a>.
        Published October 2026.
      </p>
    </main>
  );
}
