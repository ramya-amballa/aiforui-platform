# Discovery Questionnaire — {{CLIENT_NAME}}

**Prepared by:** {{PREPARED_BY}}
**Date:** {{DATE}}
**Reference:** {{ENGAGEMENT_REF}}
**ADGL phase:** Discover

Structured around ADGL's own five phases so answers map directly onto
the rest of the delivery kit (readiness workbook, roadmap, risk
register). Every question below is a template question, not an answer
— nothing here is filled in from public signal except which risk areas
to prioritise asking about.

## Maturity Model

Rate each section below on COBIT's Process Assessment Model (PAM)
0-5 scale — a recognised model, not one invented for this engagement —
so a client's own auditors or a certification body recognise the
scoring convention on sight. This is the same scale the AI Readiness
Assessment Workbook uses per dimension; score it once here, carry it
forward there, never re-score on a second scale:

| Score | Level | What it looks like in practice |
|---|---|---|
| 0 | Incomplete | The process doesn't exist, or fails to achieve its purpose |
| 1 | Initial | Ad hoc, undocumented, dependent on one person's effort |
| 2 | Repeatable | A basic process exists and is applied, but largely undocumented and inconsistent |
| 3 | Defined | Documented, standardised, and communicated across the organisation |
| 4 | Managed | Measured and monitored against defined metrics |
| 5 | Optimised | Continuously improved based on quantitative feedback |

## 1. AI Inventory (Discover)

- What AI systems, models or vendor products are currently in
  production, in pilot, or planned?
- Who owns each one (business owner, technical owner)?
- How was this inventory produced — a formal review, or best
  recollection in the room today?
- {{PRIMARY_SERVICE}} is the primary service in scope — confirm which
  systems that covers.

**Maturity (0-5):** {{MATURITY_SCORE}} — {{MATURITY_EVIDENCE: what was observed, not assumed}}

## 2. Governance Baseline (Discover / Assess)

Priority areas to probe, based on risks already flagged from public
signal — confirm, correct or rule out each:

{{GOVERNANCE_RISKS_LIST}}

- Is there an existing AI governance owner, committee, or policy today?
- What regulatory regimes apply? (On record: {{REGULATORY_ENVIRONMENT}})
- If a policy exists, when was it last reviewed, and against what
  evidence?

### {{REGULATORY_FRAMEWORK_LABEL}} — framework-specific questions

{{REGULATORY_FRAMEWORK_DISCOVERY_QUESTIONS}}

**Maturity (0-5):** {{MATURITY_SCORE}} — {{MATURITY_EVIDENCE}}

## 3. Risk & Impact (Assess)

- Which AI use case, if it failed or produced a biased/incorrect
  output, would cause the most business, legal or reputational harm?
- Is there a documented risk-tiering method today, and has it actually
  been applied to a real use case, or only described?
- Who currently has authority to say no to a use case on risk grounds
  — and has that authority ever actually been exercised?

**Maturity (0-5):** {{MATURITY_SCORE}} — {{MATURITY_EVIDENCE}}

## 4. Operating Model (Govern)

- Who currently approves a new AI use case going live?
- What escalation path exists for an AI-related incident today, and
  has it been tested (a drill, or a real incident) rather than only
  documented?
- Where do AI governance decisions get recorded, and can a decision
  made six months ago be retrieved today?

**Maturity (0-5):** {{MATURITY_SCORE}} — {{MATURITY_EVIDENCE}}

## 5. Deployment & Monitoring (Deploy / Operate)

- What monitoring exists post-deployment (drift, performance, misuse)?
- How often is an AI system's governance status reviewed once live,
  and by whom?
- What would actually happen today if a live AI system started
  producing materially wrong outputs — who would notice first?

**Maturity (0-5):** {{MATURITY_SCORE}} — {{MATURITY_EVIDENCE}}

## 6. Success Criteria

- What does a successful outcome from this engagement look like to
  the client, in their own words?
- What would the client show their own board, or an external
  auditor, to demonstrate this engagement worked?

---

*Template only — every answer, maturity score and piece of evidence
must come from the actual client conversation, never inferred or
filled in automatically.*
