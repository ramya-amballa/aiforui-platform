import type { Metadata } from "next";
import styles from "./case-02.module.css";

export const metadata: Metadata = {
  title: "Case 02: The vendor's AI was approved to predict failures",
  description:
    "Simulated case · Saudi gas processing context. A vendor removes a write-capable credential from its AI gateway. Reconciling contract, capability, evidence and approval before deployment.",
  alternates: {
    canonical: "https://www.aiforui.org/cases/case-02",
  },
  openGraph: {
    title: "Case 02: The vendor's AI was approved to predict failures. Its access told a different story.",
    description: "Simulated case. Reconciling contractual authority, technical capability, evidence and operator approval for an industrial vendor AI.",
    url: "https://www.aiforui.org/cases/case-02",
  },
};

export default function Case02Page() {
  return (
    <main className={styles.wrap}>
      <p className={styles.eyebrow}>AI Governance Evidence Portfolio · Case 02</p>
      <p className={styles.toplabels}>
        <span className={`${styles.chip} ${styles["c-sim"]} ${styles.big}`}>Simulated case · Saudi gas processing context</span>
        <span className={`${styles.chip} ${styles["c-pend"]} ${styles.big}`}>Phase 1 deployment not approved</span>
      </p>
      <h1 className={styles.h1}>The vendor&apos;s AI was approved to predict failures. Its access told a different story.</h1>
      <p className={styles.sub}>Ramya Amballa, AI for U&amp;I</p>
      <div className={styles.simbox}>
        <strong style={{ color: "inherit" }}>Illustrative simulated case.</strong> Sandline Gas Processing Company
        (SGPC) and Meridian Asset Analytics are fictional. No real operator, vendor or facility is represented. No
        incident occurred. No production write, control action, Phase 2 activation or production update was
        performed. The evidence is illustrative. The reasoning and the work products are mine. This is not a client
        engagement.
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
        A vendor removes a write-capable credential, provisioned for a future phase, from its AI gateway. That should
        settle it. It does not. The network path behind it stays open, although nobody has shown the AI could write
        through it. This case shows how to reconcile what a contract permits, what the technology can do, what the
        evidence shows and who actually approved it, before an industrial AI deployment goes ahead.
      </p>
      <ul className={styles.tags}>
        <li>Vendor AI assurance</li>
        <li>OT trust boundaries</li>
        <li>Third-party risk</li>
        <li>Deployment decision</li>
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
            <a href="/downloads/case-02-case-study.pdf">Download the two-page case summary (PDF)</a>
          </li>
          <li>
            <a href="/downloads/case-02-vendor-ai-authority-register-template.xlsx">
              Free download: pre-meeting checklist and blank Vendor AI Authority Register (Excel)
            </a>
          </li>
        </ul>
      </section>

      <div className={styles.conds} style={{ borderColor: "#D9C4E8" }}>
        <h3>
          Where the case stands <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
        </h3>
        <ul className={styles.body} style={{ margin: 0 }}>
          <li>11 vendor capabilities reviewed. One is authorised and verified.</li>
          <li>Five exposures are not yet contained.</li>
          <li>Six findings are open. None is closed.</li>
          <li>19 formal verification tests not yet performed. The findings rest on a simulated review and first retest.</li>
          <li>Phase 1 deployment approval has not been granted.</li>
        </ul>
      </div>

      <h2 id="the-situation" className={styles.h2}>
        The situation <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
      </h2>
      <p>
        A gas processor is deploying a vendor&apos;s predictive-maintenance AI on a critical compressor train. Phase
        1 is advisory only. The AI predicts failures. A reliability engineer decides what to do and raises any work
        request. The AI cannot.
      </p>
      <p>
        During the pre-deployment review, a write-capable integration credential turned up on the vendor&apos;s edge
        gateway. It had been provisioned for a future phase. The vendor removed it. The vendor has also proposed
        Phase 2: autonomous optimisation.
      </p>
      <p>The question put to me was simple. Can Phase 1 go ahead?</p>

      <h2 className={styles.h2}>The question that actually mattered</h2>
      <p>
        Not whether the AI predicts well. Whether four things line up for every vendor capability: what the contract
        permits, what the technology can do, what the evidence shows, and who in the operator approved it.
      </p>
      <p>
        So I built a register to reconcile those four positions, interface by interface, identity by identity, data
        flow by data flow. It classifies each capability. It does not score it. A capability is either authorised
        and verified, authorised but unverified, beyond its authority, undefined because the contract is silent, or
        short of evidence.
      </p>

      <h2 className={styles.h2}>
        What the review found <span className={`${styles.chip} ${styles["c-sim"]}`}>Simulated finding</span>
      </h2>
      <p>
        <strong>The credential went. The path stayed.</strong> The firewall rule that let the gateway reach the OPC
        server was still in place, and its removal had not gone through OT change control. Could the AI write
        through it? <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>Nobody had shown
        that it could, and nobody had shown that it could not. So it is recorded as unresolved reachability, not as
        write access.
      </p>
      <p>
        <strong>The first retest did not pass, for a different reason.</strong> A vendor support route, authorised
        under the support agreement, gave six named support engineers standing access to privileged engineering
        workstation functions. No time limit, no per-session approval, and never approved by the operator. That is
        human vendor access. <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>Nothing in
        the evidence shows the AI can use that route, and I did not assume it either way. A separate test is
        specified to check.
      </p>
      <p>
        <strong>Diagnostics were leaving for the vendor&apos;s cloud with no defined authority.</strong> The contract
        said nothing about content, destination, hosting, retention or use, and there was no classification
        decision. That is a governance gap. <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>
        Whether the transfer meets or breaches any law is not established, and it is not mine to decide.
      </p>
      <p>
        <strong>The Phase 2 module was already on the gateway.</strong> Or so the vendor says. Installed and
        disabled, by its own statement. <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>
        Neither point has been independently verified.
      </p>
      <p>
        <strong>Two more questions stayed open.</strong> Whether software and model updates install automatically is
        unknown. And the contract had no subcontractor terms, though{" "}
        <span className={`${styles.chip} ${styles["c-hyp"]}`}>Not established</span>nobody has shown a subcontractor
        holds access.
      </p>

      <figure className={styles.figure}>
        <div className={styles.panel} style={{ padding: "10px" }}>
          <svg
            viewBox="0 0 640 400"
            role="img"
            aria-label="Illustrative architecture: the AI data path and the human vendor support path are separate. Four paths are shown with their status."
          >
            <defs>
              <marker id="g" viewBox="0 0 10 10" refX={9} refY={5} markerWidth={7} markerHeight={7} orient="auto">
                <path d="M0,0 L10,5 L0,10 z" fill="#1E6B3A" />
              </marker>
              <marker id="a" viewBox="0 0 10 10" refX={9} refY={5} markerWidth={7} markerHeight={7} orient="auto">
                <path d="M0,0 L10,5 L0,10 z" fill="#8A5A00" />
              </marker>
              <marker id="r" viewBox="0 0 10 10" refX={9} refY={5} markerWidth={7} markerHeight={7} orient="auto">
                <path d="M0,0 L10,5 L0,10 z" fill="#B3261E" />
              </marker>
            </defs>
            <g fontFamily="inherit" fontSize={12} textAnchor="middle">
              <rect x={4} y={4} width={632} height={62} rx={8} fill="#F4F6F9" stroke="#D9DEE4" />
              <text x={20} y={22} textAnchor="start" fill="#56616D" fontSize={11} fontWeight={600}>
                VENDOR
              </text>
              <rect x={110} y={18} width={170} height={38} rx={6} fill="#fff" stroke="#8A96A3" />
              <text x={195} y={42}>
                Vendor cloud platform
              </text>
              <rect x={380} y={18} width={170} height={38} rx={6} fill="#fff" stroke="#8A96A3" />
              <text x={465} y={42}>
                Vendor support staff
              </text>
              <rect x={4} y={96} width={632} height={76} rx={8} fill="#F4F6F9" stroke="#D9DEE4" />
              <text x={20} y={114} textAnchor="start" fill="#56616D" fontSize={11} fontWeight={600}>
                INDUSTRIAL DMZ
              </text>
              <rect x={110} y={118} width={170} height={40} rx={6} fill="#fff" stroke="#0B2E59" />
              <text x={195} y={136} fill="#0B2E59" fontWeight={600}>
                Edge gateway
              </text>
              <text x={195} y={151} fill="#56616D" fontSize={10.5}>
                runs the vendor AI
              </text>
              <rect x={380} y={118} width={170} height={40} rx={6} fill="#fff" stroke="#8A96A3" />
              <text x={465} y={143}>
                Jump host
              </text>
              <rect x={4} y={202} width={632} height={76} rx={8} fill="#F4F6F9" stroke="#D9DEE4" />
              <text x={20} y={220} textAnchor="start" fill="#56616D" fontSize={11} fontWeight={600}>
                PLANT SYSTEMS
              </text>
              <rect x={40} y={224} width={140} height={40} rx={6} fill="#fff" stroke="#8A96A3" />
              <text x={110} y={249}>
                Historian replica
              </text>
              <rect x={210} y={224} width={140} height={40} rx={6} fill="#fff" stroke="#8A96A3" />
              <text x={280} y={249}>
                OPC server
              </text>
              <rect x={400} y={224} width={200} height={40} rx={6} fill="#fff" stroke="#8A96A3" />
              <text x={500} y={241}>
                Engineering workstation
              </text>
              <text x={500} y={256} fill="#56616D" fontSize={10.5}>
                privileged functions
              </text>
              <line x1={150} y1={222} x2={168} y2={160} stroke="#1E6B3A" strokeWidth={1.8} markerEnd="url(#g)" />
              <line
                x1={230}
                y1={160}
                x2={262}
                y2={222}
                stroke="#8A5A00"
                strokeWidth={1.8}
                strokeDasharray="5 4"
                markerEnd="url(#a)"
              />
              <line
                x1={195}
                y1={118}
                x2={195}
                y2={58}
                stroke="#8A5A00"
                strokeWidth={1.8}
                strokeDasharray="5 4"
                markerEnd="url(#a)"
              />
              <line x1={465} y1={58} x2={465} y2={116} stroke="#B3261E" strokeWidth={1.8} markerEnd="url(#r)" />
              <line x1={480} y1={160} x2={495} y2={222} stroke="#B3261E" strokeWidth={1.8} markerEnd="url(#r)" />
              <line x1={320} y1={98} x2={320} y2={278} stroke="#B0B7C3" strokeDasharray="2 4" />
              <g fontSize={11} textAnchor="start">
                <rect x={10} y={300} width={12} height={3} fill="#1E6B3A" />
                <text x={30} y={305}>
                  1&nbsp;&nbsp;Read from historian replica. Approved; tag scope not yet verified
                </text>
                <rect x={10} y={322} width={12} height={3} fill="#8A5A00" />
                <text x={30} y={327}>
                  2&nbsp;&nbsp;Conduit to OPC server still permitted. Write capability not established
                </text>
                <rect x={10} y={344} width={12} height={3} fill="#8A5A00" />
                <text x={30} y={349}>
                  3&nbsp;&nbsp;Diagnostics to vendor cloud. Authority undefined; legality not established
                </text>
                <rect x={10} y={366} width={12} height={3} fill="#B3261E" />
                <text x={30} y={371}>
                  4&nbsp;&nbsp;Human support route. Standing privileged access never approved. Not an AI path
                </text>
                <text x={10} y={393} fill="#56616D" fontSize={10.5}>
                  Levels and placement are illustrative. Not a real facility. The dotted line marks the two separate
                  paths.
                </text>
              </g>
            </g>
          </svg>
        </div>
        <figcaption className={styles.figcaption}>
          Simplified view of the fictional architecture. The AI&apos;s data path (left) and the human vendor support
          path (right) are kept separate in the analysis. Nothing in the case shows the AI using the support route.
        </figcaption>
      </figure>

      <h2 className={styles.h2}>Rules I held to</h2>
      <ul className={styles.body}>
        <li>
          <strong>Only a demonstrated capability is a violation.</strong> An open path is a question, not a finding
          of capability.
        </li>
        <li>
          <strong>A vendor statement is not evidence.</strong> It is recorded as attestation until verified.
        </li>
        <li>
          <strong>Containment is not closure.</strong> A restriction counts only when someone other than the person
          who applied it has verified it. Even then the finding stays open.
        </li>
        <li>
          <strong>A review date is not permission.</strong> Anything not contained shows &quot;act now&quot;, not a
          date.
        </li>
        <li>
          <strong>Legitimate support is preserved.</strong> The vendor still supports the gateway. Through named
          accounts, enabled per session, time-limited, with an operator present.
        </li>
      </ul>

      <h2 id="decision" className={styles.h2}>
        The decision <span className={`${styles.chip} ${styles["c-prop"]}`}>Proposed</span>
      </h2>
      <p>
        <strong>Phase 1 deployment approval is not granted.</strong>
      </p>
      <p>
        A temporary, restricted advisory exception may be permitted for the one verified function, the
        engineer-reviewed recommendations, and the authorised capabilities it depends on. Only after the containment
        restrictions are independently verified and the operator&apos;s risk owner formally accepts the restricted
        condition. Anything that cannot be contained is suspended now, not at a later date.
      </p>
      <p>
        <strong>Phase 2 is not considered for approval.</strong> It inherits nothing from Phase 1. It goes through
        the operator&apos;s Management of Change process.
      </p>
      <div className={styles.conds}>
        <h3>Phase 1 can be reconsidered when</h3>
        <ol>
          <li>The conduit is closed under change control, and that is independently verified.</li>
          <li>Support access is scoped, time-limited and reviewed, and the AI and human paths are shown to be separate.</li>
          <li>Diagnostics are limited to agreed fields, with a documented classification and processing position.</li>
          <li>The Phase 2 module is verified disabled, with only the operator able to enable it.</li>
          <li>The update mode is confirmed and gated by change control.</li>
          <li>Subcontractors are named, with contract terms flowed down.</li>
          <li>A contract addendum is executed after legal review.</li>
          <li>Changes that require re-reconciliation are wired to change and vendor notifications.</li>
          <li>Every remaining open register row is verified or formally accepted by its owner.</li>
        </ol>
        <p className={styles.small} style={{ margin: "8px 0 0" }}>
          A clean register without this evidence does not meet the conditions.
        </p>
      </div>

      <h2 className={styles.h2}>
        What I did not decide <span className={`${styles.chip} ${styles["c-pend"]}`}>Open decision</span>
      </h2>
      <p>
        Whether Phase 2 needs hazard review or HAZOP revalidation is for the process-safety engineers. Data
        classification and transfer requirements are for legal and data governance. Whether any active network test
        is acceptable is for OT security and operations. The package names where each decision is needed. It does
        not make them.
      </p>

      <h2 className={styles.h2}>How verification stays safe</h2>
      <p>
        No test is designed to change the live plant. The conduit check starts with firewall deny logs, which
        generate no traffic. Any active connection attempt needs written approval from OT security and operations.
        The Phase 2 module and the update path are examined only in an isolated environment. No test writes, enables
        or updates anything in production.
      </p>

      <h2 className={styles.h2}>Challenging my own work</h2>
      <p>Each layer went through QA before it was frozen. The useful catches were my own overstatements:</p>
      <ul className={styles.body}>
        <li>An early version described the Phase 2 module as installed and disabled, as fact. It was only the vendor&apos;s word.</li>
        <li>The first conduit test made an active probe of a production OPC server the default method. Deny logs are now the default.</li>
        <li>The first decision memo gave uncontained exposures a grace period. That contradicted my own rule that uncontained means act now.</li>
        <li>It also said no test had been performed, which ignored the retest that one finding rests on.</li>
      </ul>

      <h2 className={styles.h2}>What the package contains</h2>
      <div className={styles.contains}>
        <div>Vendor AI Authority Register with a two-page checklist</div>
        <div>11 reconciled vendor capabilities</div>
        <div>Six findings and five observations</div>
        <div>12 control objectives and 19 verification tests</div>
        <div>15 evidence requests and a coverage matrix</div>
        <div>Draft contract addendum for legal review</div>
        <div>Executive decision memo</div>
        <div>Remote-support profile and specialist questions</div>
      </div>
      <p className={styles.reg}>
        <strong>Reference.</strong> The package cites controls from the NCA Operational Technology Cybersecurity
        Controls (OTCC-1:2022). Cloud, data and classification requirements are marked for legal verification and
        are not asserted here. Applicability is professional opinion on simulated facts.
      </p>
      <p className={styles.foot}>
        Illustrative scenario. All organisations, findings, approvals and evidence are simulated. Case 02 of the AI
        Governance Evidence Portfolio by Ramya Amballa, <a href="https://www.aiforui.org">AI for U&amp;I</a>.
        Published October 2026.
      </p>
    </main>
  );
}
