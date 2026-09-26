import type { Metadata } from "next";
import styles from "./case-01.module.css";

export const metadata: Metadata = {
  title: "Case 01: Should this bank launch its customer AI assistant?",
  description:
    "Simulated case · UAE banking context. A customer-data exposure is found six weeks before launch. The architectural cause, the proposed controls and the conditions for a restricted launch.",
  alternates: {
    canonical: "https://www.aiforui.org/cases/case-01",
  },
  openGraph: {
    title: "Case 01: Should this bank launch its customer AI assistant?",
    description: "Simulated case · UAE banking context. The architectural cause, the proposed controls and the conditions for a restricted launch.",
    url: "https://www.aiforui.org/cases/case-01",
  },
};

export default function Case01Page() {
  return (
    <main className={styles.wrap}>
      <p className={styles.eyebrow}>AI Governance Evidence Portfolio · Case 01</p>
      <p className={styles.toplabels}>
        <span className={`${styles.chip} ${styles["c-sim"]} ${styles.big}`}>Simulated case · UAE banking context</span>
        <span className={`${styles.chip} ${styles["c-pend"]} ${styles.big}`}>Deployment not approved</span>
      </p>
      <h1 className={styles.h1}>Should this bank launch its customer AI assistant?</h1>
      <p className={styles.sub}>Ramya Amballa, AI for U&amp;I</p>
      <div className={styles.simbox}>
        <strong style={{ color: "inherit" }}>Illustrative simulated case.</strong> The bank, its systems, test
        results, costs and evidence are invented. The reasoning and the work products are mine. This is not a client
        engagement, no control described here has operated in a real organisation, and no approval described here
        has been given.
      </div>
      <div className={styles.legend}>
        <p>How to read this case</p>
        <ul>
          <li>
            <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>invented for the scenario,
            including test results
          </li>
          <li>
            <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>my recommended control or decision
          </li>
          <li>
            <span className={`${styles.chip} ${styles["c-pend"]}`}>Pending approval</span>a decision the case leaves
            open
          </li>
          <li>
            <span className={`${styles.chip} ${styles["c-hyp"]}`}>Hypothetical</span>an estimate or projected outcome
          </li>
        </ul>
      </div>
      <p className={styles.lede}>
        A simulated pre-launch security finding raises a difficult deployment decision. Explore the architecture,
        proposed controls, test evidence and conditions that would need to be met before approval could be
        considered.
      </p>
      <ul className={styles.tags}>
        <li>Architecture</li>
        <li>Risk assessment</li>
        <li>Control testing</li>
        <li>Deployment decision</li>
      </ul>

      <section className={`${styles.res} ${styles.screenOnly}`} aria-label="Resources">
        <h2>Available resources</h2>
        <ul>
          <li>
            <a href="#the-situation">Read the case study</a>
          </li>
          <li>
            <a href="#excerpt">See the evidence-pack excerpt</a>
          </li>
          <li>
            <a href="/downloads/case-01-customer-ai-assistant.pdf">Download the case study and excerpt (PDF)</a>
          </li>
          <li>
            <a href="/downloads/case-01-evidence-pack-v2.pdf">Download the full evidence pack (PDF)</a>
          </li>
        </ul>
        <p className="note">
          The full pack contains the ADGL risk classification, control matrix, test scenarios, traceability, Gate 4
          checklist, evidence register, decision memorandum and an independent review with its open findings.
        </p>
      </section>

      <div className={styles.conds} style={{ borderColor: "#D9C4E8" }}>
        <h3>
          Outstanding issues <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
        </h3>
        <ul className={styles.body} style={{ margin: 0 }}>
          <li>One simulated control test has failed.</li>
          <li>One control is only partially demonstrated.</li>
          <li>One control has not yet been built.</li>
          <li>The kill switch has only been demonstrated in staging.</li>
          <li>Committee approval and CRO risk acceptance remain pending.</li>
        </ul>
      </div>

      <h2 id="the-situation" className={styles.h2}>
        The situation <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
      </h2>
      <p>
        A UAE retail bank is six weeks from launching an in-app AI assistant. It answers questions on balances,
        transactions and cards, in Arabic and English. A paid campaign is booked. Then, in pre-launch testing with
        synthetic customers, the red team finds that one customer can get another customer&apos;s balance out of it.
        Three times in forty attempts.
      </p>
      <p>The CISO will not sign. The business wants its date. The brief: a launch recommendation within a week.</p>

      <h2 className={styles.h2}>What was actually wrong</h2>
      <p>
        The obvious reading is that the model misbehaved. It did not. The design let the model choose which customer
        and account IDs to pass to the bank&apos;s data service. That service trusted the assistant&apos;s service
        account, which could read every customer. So model output was acting as an authorisation decision.
      </p>
      <p>
        That reframing mattered. It moved the conversation from prompt tuning, which would never have closed the
        gap, to identity architecture, which could.
      </p>

      <figure className={styles.figure}>
        <div className={styles.panels}>
          <div className={`${styles.panel} ${styles.bad}`}>
            <h4>
              As built <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
            </h4>
            <svg
              viewBox="0 0 320 300"
              role="img"
              aria-label="As built: the model chooses the customer ID and the data service trusts a service account that can read every customer"
            >
              <defs>
                <marker id="ar" viewBox="0 0 10 10" refX={9} refY={5} markerWidth={7} markerHeight={7} orient="auto">
                  <path d="M0,0 L10,5 L0,10 z" fill="#56616D" />
                </marker>
                <marker id="arr" viewBox="0 0 10 10" refX={9} refY={5} markerWidth={7} markerHeight={7} orient="auto">
                  <path d="M0,0 L10,5 L0,10 z" fill="#B3261E" />
                </marker>
              </defs>
              <g fontFamily="inherit" fontSize={12.5} textAnchor="middle">
                <rect x={30} y={6} width={260} height={40} rx={8} fill="#F4F6F9" stroke="#8A96A3" />
                <text x={160} y={24} fill="#14202E">
                  Customer logs in to the app
                </text>
                <text x={160} y={39} fill="#56616D" fontSize={11}>
                  the session knows who they are
                </text>
                <line x1={160} y1={46} x2={160} y2={70} stroke="#56616D" markerEnd="url(#ar)" />
                <rect x={30} y={72} width={260} height={40} rx={8} fill="#F4F6F9" stroke="#8A96A3" />
                <text x={160} y={90} fill="#14202E">
                  AI model
                </text>
                <text x={160} y={105} fill="#56616D" fontSize={11}>
                  writes the data request
                </text>
                <line x1={160} y1={112} x2={160} y2={136} stroke="#B3261E" strokeWidth={1.6} markerEnd="url(#arr)" />
                <rect x={30} y={138} width={260} height={46} rx={8} fill="#FBEAE8" stroke="#B3261E" />
                <text x={160} y={157} fill="#B3261E" fontWeight={600}>
                  Model picks the customer ID
                </text>
                <text x={160} y={174} fill="#7A1A14" fontSize={11}>
                  nothing checks it against the session
                </text>
                <line x1={160} y1={184} x2={160} y2={208} stroke="#B3261E" strokeWidth={1.6} markerEnd="url(#arr)" />
                <rect x={30} y={210} width={260} height={46} rx={8} fill="#FBEAE8" stroke="#B3261E" />
                <text x={160} y={229} fill="#B3261E" fontWeight={600}>
                  Data service trusts the assistant
                </text>
                <text x={160} y={246} fill="#7A1A14" fontSize={11}>
                  service account can read every customer
                </text>
                <text x={160} y={284} fill="#B3261E" fontSize={12} fontWeight={600}>
                  In testing: another customer&apos;s balance
                </text>
              </g>
            </svg>
          </div>
          <div className={`${styles.panel} ${styles.good}`}>
            <h4>
              Proposed controls <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>
            </h4>
            <svg
              viewBox="0 0 320 300"
              role="img"
              aria-label="Proposed: identity from the session, entitlement check outside the model, ownership enforced by the data service"
            >
              <defs>
                <marker id="ag" viewBox="0 0 10 10" refX={9} refY={5} markerWidth={7} markerHeight={7} orient="auto">
                  <path d="M0,0 L10,5 L0,10 z" fill="#1E6B3A" />
                </marker>
              </defs>
              <g fontFamily="inherit" fontSize={12.5} textAnchor="middle">
                <rect x={30} y={6} width={260} height={40} rx={8} fill="#F4F6F9" stroke="#8A96A3" />
                <text x={160} y={24} fill="#14202E">
                  AI model
                </text>
                <text x={160} y={39} fill="#56616D" fontSize={11}>
                  asks for data, cannot name a customer
                </text>
                <line x1={160} y1={46} x2={160} y2={70} stroke="#1E6B3A" markerEnd="url(#ag)" />
                <rect x={30} y={72} width={260} height={46} rx={8} fill="#E6F2EA" stroke="#1E6B3A" />
                <text x={160} y={91} fill="#1E6B3A" fontWeight={600}>
                  1&nbsp;&nbsp;Identity from the login session
                </text>
                <text x={160} y={108} fill="#1E4D2E" fontSize={11}>
                  added by the bank&apos;s code, never the model
                </text>
                <line x1={160} y1={118} x2={160} y2={138} stroke="#1E6B3A" markerEnd="url(#ag)" />
                <rect x={30} y={140} width={260} height={46} rx={8} fill="#E6F2EA" stroke="#1E6B3A" />
                <text x={160} y={159} fill="#1E6B3A" fontWeight={600}>
                  2&nbsp;&nbsp;Entitlement check
                </text>
                <text x={160} y={176} fill="#1E4D2E" fontSize={11}>
                  every account checked before any call
                </text>
                <line x1={160} y1={186} x2={160} y2={206} stroke="#1E6B3A" markerEnd="url(#ag)" />
                <rect x={30} y={208} width={260} height={46} rx={8} fill="#E6F2EA" stroke="#1E6B3A" />
                <text x={160} y={227} fill="#1E6B3A" fontWeight={600}>
                  3&nbsp;&nbsp;Data service enforces ownership
                </text>
                <text x={160} y={244} fill="#1E4D2E" fontSize={11}>
                  independent of the AI layer
                </text>
                <text x={160} y={284} fill="#1E6B3A" fontSize={12} fontWeight={600}>
                  Estimate: 1 and 2 in weeks, 3 by mid-December
                </text>
              </g>
            </svg>
          </div>
        </div>
        <figcaption className={styles.figcaption}>
          Simplified view. The evidence pack has the full data-flow diagram with trust boundaries and all ten flows.
          Timings are estimates.
        </figcaption>
      </figure>

      <h2 className={styles.h2}>How I approached the decision</h2>
      <p>
        I used <a href="/methodology">OPERA v1.1</a> to frame the governance decisions and <a href="/adgl">ADGL</a>{" "}
        to sequence the deployment work, its gates and its control library.
      </p>
      <table className={styles.opera}>
        <tbody>
          <tr>
            <th>Opportunity</th>
            <td>
              Contact-centre deflection worth about AED 2.4m a year{" "}
              <span className={`${styles.chip} ${styles["c-hyp"]}`}>Hypothetical</span>. Real, but not worth carrying
              a Critical confidentiality risk. Scope cut to read-only, no card actions.
            </td>
          </tr>
          <tr>
            <th>People</th>
            <td>
              Head of Retail owns the outcome. The AI Governance Committee approves gates. The CRO holds
              residual-risk acceptance. Kill-switch authority is named in advance.
            </td>
          </tr>
          <tr>
            <th>Evaluation</th>
            <td>
              Applicable CBUAE obligations mapped. Cross-customer disclosure rated Critical. The bank will consider
              customer exposure only when every Gate 4 condition is met or covered by an approved exception, and
              only with written acceptance. Proposed treatment: reduce.
            </td>
          </tr>
          <tr>
            <th>Response</th>
            <td>
              Three layers of identity control, launch conditions, the incident playbook and kill switch. The
              committee, with the CRO signing as chair, would make and record any residual-risk acceptance here.
              None has been made.
            </td>
          </tr>
          <tr>
            <th>Assurance</th>
            <td>
              Independent retest before launch, a production kill-switch drill, weekly quality sampling and retained
              evidence that each control operates.
            </td>
          </tr>
        </tbody>
      </table>
      <p>
        <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>Neither methodology solves the
        security flaw. That needed three layers of engineering control:
      </p>
      <ul className={styles.body}>
        <li>Take customer identity from the login session, never from the model.</li>
        <li>Check every account the assistant touches against that customer&apos;s entitlements, outside the model.</li>
        <li>Make the data service enforce ownership itself, so a future flaw in the AI layer cannot expose anyone.</li>
      </ul>
      <p>
        The first two could be built in weeks. The third needs the core banking team and is estimated to take until
        mid-December <span className={`${styles.chip} ${styles["c-hyp"]}`}>Hypothetical</span>. That timing gap is
        the real decision.
      </p>

      <h2 className={styles.h2}>Two scoring rules I held to</h2>
      <p>
        <strong>No credit for untested controls.</strong> A designed control does not lower a risk score until it
        has been tested. <strong>Likelihood follows evidence.</strong> A reproduced exploit is Likely, however
        confident the build team feels.
      </p>
      <p>
        Under those rules, cross-customer disclosure stays Critical under ADGL even after the interim fixes. None of
        them has passed an independent retest, and they sit in the same layer that produced the flaw. I did not let
        the numbers pretend otherwise.
      </p>

      <h2 className={styles.h2}>
        The recommendation <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>
      </h2>
      <p>
        <strong>This is a conditional recommendation, not a deployment approval.</strong> As the case stands, the
        conditions below are not met and the exposure is unresolved. No customer should use the assistant until they
        are.
      </p>
      <p>
        Not an unrestricted launch. Not a blanket delay either. An opt-in soft launch on the original date, capped
        at 10,000 sole-owner customers, read-only, no card actions, no paid media. Any confirmed disclosure would
        trigger the kill switch without waiting for a committee. Wider launch waits for the data-service fix.
      </p>
      <div className={styles.conds}>
        <h3>Launch conditions include</h3>
        <ol>
          <li>Identity binding and entitlement checks pass an independent retest. Zero cross-customer returns in 500 attempts.</li>
          <li>Transcripts masked, including account numbers written in Eastern Arabic numerals. Integrator access to production logs removed.</li>
          <li>Model version pinned in production, so the provider cannot change behaviour unannounced.</li>
          <li>Prompt-injection results within threshold in Arabic and English.</li>
          <li>An agreed and tested approach for Arabic fee questions.</li>
          <li>Kill switch proven in production.</li>
          <li>UAE processing and retention confirmed by the cloud provider and corroborated by configuration.</li>
        </ol>
        <p className={styles.small} style={{ margin: "8px 0 0" }}>
          These are seven of the 30 Gate 4 conditions in the evidence pack. 3 of the 30 are met.
        </p>
      </div>
      <p>
        <span className={`${styles.chip} ${styles["c-pend"]}`}>Pending approval</span>The committee has not approved
        deployment. Any launch would need the committee, with the CRO signing as chair, to accept the residual
        cross-customer risk in writing, with an expiry date. It remains Critical under ADGL. No acceptance has been
        given.
      </p>

      <h2 className={styles.h2}>
        Where testing changed the plan <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
      </h2>
      <p>
        The simulated test results were built to surface the problems real projects hit. Log masking missed account
        numbers written in Eastern Arabic numerals. Arabic answers on fees were 7.3 points less accurate than
        English. Production was calling the model through a &apos;latest&apos; alias, so the provider could change
        behaviour without the bank knowing. Each of these became a condition or a decision for the committee, not a
        footnote.
      </p>
      <p>
        Arabic quality was the hardest call. Launching English only would sit badly with the CBUAE&apos;s February
        2026 guidance on bilingual disclosure and fair treatment. My recommendation{" "}
        <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>was to answer fee questions in Arabic
        by quoting the approved tariff text with a citation, rather than letting the model paraphrase. That decision
        is still open <span className={`${styles.chip} ${styles["c-pend"]}`}>Pending approval</span>
      </p>

      <h2 className={styles.h2}>Where my own methodology bent</h2>
      <p>
        ADGL requires a human to approve every customer-facing output. A live chat cannot work that way, so the case
        uses human-on-the-loop oversight, which the CBUAE guidance recognises. ADGL also says never defer a control
        past deployment. The data-service fix cannot land before launch, so it is recorded as a named exception with
        an owner and a date. I would rather show where a framework needs judgement than pretend it fitted perfectly.
      </p>

      <h2 className={styles.h2}>Challenging my own work</h2>
      <p>
        Before finalising, I reviewed the pack as a CISO and as an internal auditor. Thirteen challenges. Six
        changed the pack, five were accepted with reasons and two remain open. The most useful:
      </p>
      <ul className={styles.body}>
        <li>
          The entitlement model had not considered joint accounts or powers of attorney. The proposed cohort is now
          restricted to sole-owner accounts.
        </li>
        <li>
          Test thresholds had been asserted, not agreed. They now have to be approved by Compliance and Model Risk
          before tests run, so nobody moves the goal posts after seeing results.
        </li>
        <li>
          Much of the evidence came from the team that built the controls. That supports design. It is not
          assurance. Independent retest is now a launch condition.
        </li>
      </ul>
      <p>
        A second review of the rebuilt evidence pack leaves ten findings open. They are published in the pack
        rather than closed on paper.
      </p>

      <h2 className={styles.h2}>What the full pack contains</h2>
      <div className={styles.contains}>
        <div>Executive briefing and decision memorandum</div>
        <div>Risk assessment with transparent scoring</div>
        <div>Data-flow diagram with trust boundaries</div>
        <div>Control matrix mapped to the ADGL control library</div>
        <div>AI asset and stakeholder registers</div>
        <div>Simulated test cases and deficiency tracker</div>
        <div>RACI and decision log</div>
        <div>Evidence register with auditor sufficiency notes</div>
        <div>Dated remediation plan and costs</div>
        <div>Independent CISO and auditor challenge</div>
      </div>
      <p className={styles.screenOnly}>
        <a href="/downloads/case-01-evidence-pack-v2.pdf">
          <strong>Download the full evidence pack →</strong>
        </a>
      </p>
      <p className={styles.printOnly}>The full evidence pack is at aiforui.org/downloads/case-01-evidence-pack-v2.pdf.</p>

      <section className={styles.ex} id="excerpt">
        <h2 className={styles.h2}>Evidence-pack excerpt</h2>
        <p className={styles.small}>
          Extracted from the Case 01 evidence pack. Every result and evidence item is simulated. The full pack is
          available as a download.
        </p>
        <h3 className={styles.h3}>Architecture: the flaw and the proposed controls</h3>
        <p className={styles.small}>Shown above in the case study.</p>

        <h3 className={styles.h3}>
          Risk register entry R01 <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
        </h3>
        <table className={styles.kv}>
          <tbody>
            <tr>
              <th>Risk</th>
              <td>Cross-customer disclosure of account data</td>
            </tr>
            <tr>
              <th>Cause and evidence</th>
              <td>
                The model supplies customer and account IDs. The Account Data Service trusts a service account with
                read access to all retail customers. Red-team test RT-07: 3 of 40 attempts returned another
                customer&apos;s balance.
              </td>
            </tr>
            <tr>
              <th>Inherent score</th>
              <td className={styles.red}>
                Likelihood 4 × impact 5 = 20, Critical. Likely because it was reproduced. Severe because any
                disclosure of one customer&apos;s data to another is the top impact band.
              </td>
            </tr>
            <tr>
              <th>ADGL tier</th>
              <td className={styles.red}>
                Critical, inherent and at soft launch. Severe, all customers, irreversible, autonomous. The tier does
                not fall with likelihood, so any soft launch would rest on a named exception, committee approval and
                CRO acceptance. None has been given.
              </td>
            </tr>
            <tr>
              <th>Key controls</th>
              <td>WC-01 identity binding, WC-02 entitlement check, WC-04 output filter (backstop only), WC-12 kill switch, WC-19 independent retest</td>
            </tr>
            <tr>
              <th>
                Target at soft launch <span className={`${styles.chip} ${styles["c-hyp"]}`}>Hypothetical</span>
              </th>
              <td className={styles.amb}>2 × 5 = 10, High. A target, not an achieved score. It counts only once the independent retest passes.</td>
            </tr>
            <tr>
              <th>
                Target at general availability <span className={`${styles.chip} ${styles["c-hyp"]}`}>Hypothetical</span>
              </th>
              <td className={styles.grn}>1 × 5 = 5, Medium, once WC-03 enforces ownership in the data service</td>
            </tr>
            <tr>
              <th>Owner and treatment</th>
              <td>
                CDO. Reduce. No written acceptance has been requested or given{" "}
                <span className={`${styles.chip} ${styles["c-pend"]}`}>Pending approval</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p className={styles.small}>
          ADGL tiers govern every decision. The 5-point score is the bank&apos;s enterprise risk scale, shown for
          enterprise reporting only.
        </p>

        <h3 className={styles.h3}>Five representative controls</h3>
        <div className={styles.tscroll}>
          <table className={styles.ctl}>
            <thead>
              <tr>
                <th>ID</th>
                <th>
                  Proposed control <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>
                </th>
                <th>Owner</th>
                <th>Gate</th>
                <th>Test method</th>
                <th>Evidence required</th>
                <th>
                  Test result <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
                </th>
                <th>
                  Evidence status <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>WC-01</td>
                <td>
                  <b>Identity binding.</b> Customer ID removed from tool schemas and injected from the validated
                  session token.
                </td>
                <td>Head of Digital Engineering</td>
                <td>Soft launch</td>
                <td>Code review. Inject a foreign customer ID into tool arguments (TC-02).</td>
                <td>Schema diff with commit ID. Peer review by someone other than the author. Test log.</td>
                <td className={styles.grn}>40 of 40 ignored. Pass</td>
                <td className={styles.amb}>Test log received. Independent retest pending</td>
              </tr>
              <tr>
                <td>WC-02</td>
                <td>
                  <b>Entitlement check.</b> Every account or card ID checked against the session&apos;s entitlements
                  before any call. Mismatch denied and alerted.
                </td>
                <td>Head of Digital Engineering</td>
                <td>Soft launch</td>
                <td>500 cross-customer attempts over 50 synthetic pairs, run in CI every build (TC-03).</td>
                <td>Test log. SIEM alert export. Configuration export.</td>
                <td className={styles.amb}>0 disclosures. 497 of 500 alerts. Partial</td>
                <td className={styles.amb}>SIEM export partial: 3 events dropped by the parser</td>
              </tr>
              <tr>
                <td>WC-03</td>
                <td>
                  <b>Data-service ownership enforcement.</b> Customer-bound token passed to the data service, which
                  checks ownership itself.
                </td>
                <td>Head of Core Banking Integration</td>
                <td>General availability</td>
                <td>API tests that bypass the orchestrator. IAM scope review. Independent pen test.</td>
                <td>Design record. IAM scope export. Pen test report.</td>
                <td className={styles.gry}>Not yet built</td>
                <td className={styles.gry}>Not yet registered</td>
              </tr>
              <tr>
                <td>WC-07</td>
                <td>
                  <b>Transcript minimisation.</b> Account data masked before logging, including Eastern Arabic
                  numerals. No integrator access to production transcripts.
                </td>
                <td>CIO</td>
                <td>Soft launch</td>
                <td>Sample 100 log entries for unmasked data (TC-08). Access list review.</td>
                <td>Masking config export. Redacted log sample. Access list with approver.</td>
                <td className={styles.red}>2 IBANs unmasked. Fail</td>
                <td className={styles.red}>Insufficient: undated screenshot, no system identifier</td>
              </tr>
              <tr>
                <td>WC-12</td>
                <td>
                  <b>Kill switch.</b> Disables the assistant for all users or the cohort within 15 minutes. Authorised
                  roles named.
                </td>
                <td>CDO</td>
                <td>Soft launch</td>
                <td>Timed drill in staging, then in production at soft launch (TC-13).</td>
                <td>Drill record with timestamps and approver.</td>
                <td className={styles.grn}>6 minutes in staging. Pass</td>
                <td className={styles.amb}>Partial: production drill still needed</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className={styles.small}>
          The evidence-status column is written from an auditor&apos;s point of view. A passing test run by the
          build team supports the design. It is not independent assurance.
        </p>

        <h3 className={styles.h3}>
          Deployment recommendation <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>
        </h3>
        <p>
          <strong>Not approved. Conditions not met.</strong> The results above show one fail, one partial, one
          control not yet built and a kill switch proven only in staging. On that evidence, no customer exposure is
          recommended. Once every condition is met or covered by an approved exception, the committee could consider
          an opt-in soft launch capped at 10,000 sole-owner customers, read-only, no paid media. Until WC-03 is live,
          one control failure could still expose any customer&apos;s data, not only the cohort&apos;s. Wider launch
          not before WC-03 is live and pen tested. Committee endorsement and CRO risk acceptance are both pending{" "}
          <span className={`${styles.chip} ${styles["c-pend"]}`}>Pending approval</span>
        </p>
      </section>

      <p className={styles.reg}>
        <strong>Regulatory anchor.</strong> CBUAE Guidance Note on the Consumer Protection and Responsible Adoption
        and Use of Artificial Intelligence and Machine Learning by Licensed Financial Institutions (February 2026),
        read with the CBUAE Consumer Protection Regulation, Model Management Standards and Outsourcing Regulation.
        Applicability is professional opinion on simulated facts, not legal advice.
      </p>
      <p className={styles.foot}>
        Illustrative scenario. All organisations, results, approvals and evidence are simulated. Case 01 of the AI
        Governance Evidence Portfolio by Ramya Amballa, <a href="https://www.aiforui.org">AI for U&amp;I</a>.
        Published September 2026.
      </p>
    </main>
  );
}
