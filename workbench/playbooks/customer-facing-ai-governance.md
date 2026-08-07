# Customer-Facing AI Governance

**A Governance Playbook from the AI Governance Workbench**

Source data: Edition 1.1 (139 canonical objects). Snapshot date: 2026-08-05. Every claim in this document traces to a canonical object ID in `/workbench/data` — decisions, patterns, controls, evidence types, and board questions are cited by ID throughout and can be looked up directly in the repository or the Explorer. Nothing in this playbook is generated or inferred beyond what the cited objects state. Where the graph's coverage has a real limit, that limit is stated explicitly in "Coverage and Confidence," not smoothed over.

This is the reference implementation for the AI Governance Workbench's Practitioner Toolkit — the first of what `VISION.md` calls Governance Playbooks. See `FOUNDATION_COMPLETE.md` for the standard every future playbook is held to.

---

## 1. Executive Summary

AI systems that interact directly with an organization's own customers — chatbots, virtual assistants, companion apps, and generative content features — carry a distinct governance profile from AI used internally or embedded in back-office decisioning. The failure mode is not "the model was inaccurate" in the abstract; it is a customer relying on that inaccuracy, in real time, in a channel the organization represented as authoritative.

This playbook synthesizes nine documented incidents involving customer-facing AI systems, connected through the AI Governance Workbench's graph to **five Governance Decisions**, five Design Patterns, five Framework Controls (spanning GDPR, the EU AI Act, the NIST AI Risk Management Framework, and the FTC Act), five Evidence Types, and five Board Questions. The pattern across all nine incidents is consistent: a customer-facing AI system was deployed without a specific, testable safeguard — an accuracy-accountability process, an age-verification gate, an adversarial red-team exercise, a context-aware pre-release test, or a clinical crisis-escalation path — and the absence of that specific safeguard, not a general failure of "AI safety," is what produced the harm.

**Governing question this playbook answers:** for a customer-facing AI system under active development or already in production, what decisions has this organization actually made, what evidence would demonstrate those decisions were followed, and what should the board be asking before the next incident makes the answer public.

## 2. Governance Context

"Customer-facing AI" in this playbook means an AI system a company deploys to interact directly with its own customers or the public — not an AI system used internally by employees, and not an AI system embedded in a back-office decisioning process (hiring, credit, benefits eligibility) the customer never directly converses with. The Workbench's dataset currently categorizes customer-facing systems under `ai_system_category` values including `customer_service_chatbot`, `generative_ai_chatbot`, `ai_companion_app`, `conversational_chatbot`, `companion_chatbot`, `mental_health_chatbot`, and `generative_ai_image` — see "Coverage and Confidence" for why this remains a free-text field rather than a fixed taxonomy.

This is a deliberately narrower scope than "AI governance" generally. A customer-facing system's failure is witnessed directly by the person it harms, in a channel the company controls end-to-end — which is why liability, regulatory, and reputational exposure in this category has moved faster than in most other AI governance domains: two of the nine incidents below produced a binding legal judgment or an active lawsuit, three produced a formal regulatory enforcement action, and one produced a voluntary business-line pause after public reporting alone.

## 3. Historical Incidents

Nine incidents, four governance clusters. Full citations for every incident are in "References."

### Chatbot output as company communication

**`INC-002`** — *Air Canada held liable for its chatbot giving incorrect bereavement-fare information* (Canada, 2024-02-14, medium severity). A customer relied on Air Canada's website chatbot for its bereavement-fare policy and received inaccurate information about retroactive refund eligibility. Air Canada argued it should not be liable for its own chatbot's statements, treating it as a separate legal entity; the Civil Resolution Tribunal of British Columbia rejected that argument and awarded damages. *Root cause: the chatbot provided information conflicting with actual policy, and no process caught the discrepancy before the customer relied on it.*

### Consumer generative AI: legal basis and age verification

**`INC-012`** — *Italy bans ChatGPT over GDPR violations* (Italy/EU, 2023-03-30, high severity). Italy's Garante ordered OpenAI to stop processing Italian users' data, citing no legal basis for training-data collection, no age verification, and an unreported data breach. First Western regulatory ban of a major consumer generative AI product.

**`INC-013`** — *Italy orders AI companion app Replika to stop processing user data* (Italy/EU, 2023-02-02, high severity). Same regulator, same core deficiencies — no effective age verification, no adequate GDPR legal basis — applied to a psychologically higher-stakes companion product.

**`INC-032`** — *UK ICO issues preliminary enforcement notice against Snap over My AI* (UK, 2023-10-06, medium severity). The ICO found Snap's data protection impact assessment for its My AI chatbot — reaching millions of UK users including 13-to-17-year-olds — inadequately assessed risk to children. Snap revised its DPIA; the ICO closed the matter without a fine in December 2023.

**`INC-035`** — *Meta pauses AI training on EU/UK user data after regulator pressure* (EU/UK/Ireland, 2024-06-14, medium severity). *Adjacent to the direct-interaction incidents above*: this concerns the training-data pipeline feeding customer-facing generative products, not a customer's direct interaction with one. Meta paused its plan to train models on public EU/UK user posts under a "legitimate interests" legal basis after Irish and UK regulators found that basis inadequately justified for the scale and sensitivity involved.

### Public-facing systems that learn from live input

**`INC-018`** — *Microsoft's Tay chatbot manipulated into racist tweets, shut down within hours* (US, 2016-03-23, medium severity). Coordinated trolling exploited Tay's live-learning design within hours of launch; Microsoft had no rehearsed rapid-disable capability and took the system offline roughly 16 hours after launch.

### Generative content features and pre-release testing

**`INC-020`** — *Google pauses Gemini image generator after historically inaccurate depictions* (US, 2024-02-21, medium severity). Diversity tuning applied without context-specific testing produced historically inaccurate images (e.g., racially diverse 1943 Wehrmacht soldiers); Google paused the feature's ability to generate images of people.

### Chatbots serving emotionally vulnerable users

**`INC-027`** — *NEDA suspends 'Tessa' AI chatbot after harmful eating-disorder advice* (US, 2023-05-30, high severity). NEDA replaced its human-staffed crisis helpline with a chatbot that, when told about active eating-disorder symptoms, recommended calorie counting and weight-loss targets — advice contradicting treatment guidance. Disabled indefinitely after public documentation by an activist and a psychologist.

**`INC-028`** — *Wrongful-death lawsuit against Character.AI and Google* (US, 2024-10-22, **critical** severity). A wrongful-death and product-liability suit alleges a 14-year-old died by suicide after months of an emotionally and sexually charged relationship with a Character.AI chatbot persona lacking adequate minor safeguards. A federal judge allowed product-liability claims to proceed in May 2025; the FTC separately issued compulsory study orders to seven AI-companion-chatbot operators in September 2025. The most severe documented case in this playbook's scope.

## 4. Critical Governance Decisions

Five decisions, each `RESULTED_FROM` one of the incidents above and each `MITIGATED_BY`-linked from every incident in its cluster.

| ID | Decision | Originating incident |
|---|---|---|
| `DEC-014` | Treat customer-facing chatbot output as an accountable company communication | `INC-002` |
| `DEC-006` | Require a documented GDPR legal basis and age-verification before launching a consumer AI product to EU users | `INC-012` |
| `DEC-011` | Require adversarial red-teaming and a tested kill switch before deploying a publicly-facing AI system that learns from live input | `INC-018` |
| `DEC-013` | Require context-aware pre-release testing and staged rollout for generative content features | `INC-020` |
| `DEC-019` | Require clinical safety review and crisis-escalation protocols before deploying a chatbot to an emotionally vulnerable user population | `INC-027` |

**`DEC-014`** (full statement): "Any customer-facing AI chatbot's substantive statements (pricing, policy, eligibility) must be treated as binding company communications subject to the same accuracy review, correction, and escalation process as a human agent's statements — not as a disclaimed third party's output."

**`DEC-006`** (full statement): "Before a consumer-facing AI product processes EU users' personal data, the organization must document its GDPR legal basis for that processing (including for any training data drawn from user interactions), publish a clear privacy notice, and implement an effective age-verification mechanism where the product could plausibly be used by minors."

**`DEC-011`** (full statement): "Before deploying a publicly-facing AI system that adapts its behaviour from live user input, the organization must conduct adversarial red-teaming specifically targeting coordinated manipulation attempts, and must have a tested kill-switch/rollback mechanism capable of disabling the system within minutes of detecting harmful output at scale."

**`DEC-013`** (full statement): "Before broadly releasing a generative content feature, the organization must test its output against a diverse, context-specific set of prompts — including prompts where a safety or fairness adjustment could plausibly conflict with factual/historical accuracy — and release to a limited audience first, with a fast feedback and rollback path, before full public availability."

**`DEC-019`** (full statement): "Before deploying a chatbot in a mental-health-adjacent context, or to a user base known to include emotionally vulnerable individuals or minors, the organization must complete a clinical safety review of the chatbot's responses to crisis-adjacent input, implement a crisis-escalation protocol that connects the user to a trained human, and never replace a trained human crisis responder with an unsupervised chatbot."

## 5. Design Patterns

Each decision above is `IMPLEMENTED_BY` exactly one primary pattern — this playbook's cluster deliberately follows the Workbench's "one primary pattern per decision" discipline rather than listing every loosely-related pattern.

| ID | Pattern | Implements | Maturity |
|---|---|---|---|
| `PAT-013` | Chatbot Output Accuracy & Accountability Pattern | `DEC-014` | emerging |
| `PAT-006` | Consumer AI Age Verification & Legal Basis Gate Pattern | `DEC-006` | emerging |
| `PAT-010` | Adversarial Red-Team & Kill Switch Pattern | `DEC-011` | established |
| `PAT-012` | Context-Aware Content Safety Review Pattern | `DEC-013` | emerging |
| `PAT-018` | Crisis Escalation & Clinical Safety Review Pattern | `DEC-019` | emerging |

**`PAT-013` — Chatbot Output Accuracy & Accountability.** Ground chatbot responses to policy questions in a maintained, versioned source-of-truth document rather than open-ended generation; log every substantive policy statement; provide a fast escalation/correction path treated with the same urgency as a documented human-agent error. *Consequence to weigh:* grounding reduces but does not eliminate incorrect answers, since source documents can themselves be stale or ambiguous.

**`PAT-006` — Consumer AI Age Verification & Legal Basis Gate.** Before EU launch, document the specific legal basis for each category of processing (including training-data use), publish a plain-language privacy notice, and implement age verification stronger than a self-reported checkbox for any product plausibly reachable by minors. *Consequence to weigh:* effective age verification is a genuinely hard, partially unsolved problem — most methods are either weak or themselves privacy-invasive.

**`PAT-010` — Adversarial Red-Team & Kill Switch.** Before launch, run red-team exercises specifically simulating coordinated manipulation (not just individual bad prompts), and build and *rehearse* — not merely document — a kill-switch or rollback procedure capable of disabling the system within minutes. *Consequence to weigh:* red-teaming can only anticipate known categories of manipulation; an easily-triggered kill switch also creates an availability risk from false alarms.

**`PAT-012` — Context-Aware Content Safety Review.** Enumerate the distinct prompt categories a generative feature will plausibly encounter, including categories where a safety/fairness adjustment could conflict with factual or historical accuracy, and test each explicitly before release; release first to a limited audience with a fast feedback and rollback path. *Consequence to weigh:* enumerating every plausible category is inherently incomplete; staged rollout requires monitoring infrastructure during the limited-release phase.

**`PAT-018` — Crisis Escalation & Clinical Safety Review.** Before deployment, have qualified clinicians review the chatbot's responses to a structured set of crisis-adjacent and vulnerable-population test inputs; build and test an escalation mechanism that reliably routes a crisis-showing user to a trained human; treat any chatbot marketed to or known to reach a vulnerable population as requiring this review regardless of its original intended use case. *Consequence to weigh:* clinical review is not a one-time exercise — it must repeat as the underlying model changes, and an escalation mechanism only helps if it is actually staffed and reachable.

## 6. Framework Mapping

Every mapping below is a direct `SATISFIES_CONTROL` edge from the decision to the control — not a broad, illustrative association. See "Coverage and Confidence" for frameworks this cluster does *not* currently map to, stated explicitly rather than implied by omission.

| Decision | Control | Framework | Reference |
|---|---|---|---|
| `DEC-014` | `CTR-018` | EU Artificial Intelligence Act (Regulation (EU) 2024/1689) | Article 13 — Transparency and provision of information to users |
| `DEC-006` | `CTR-010` | General Data Protection Regulation (Regulation (EU) 2016/679) | Article 5 — Principles relating to processing of personal data |
| `DEC-011` | `CTR-015` | NIST AI Risk Management Framework (AI RMF 1.0) | MANAGE 4.1 — Post-deployment monitoring and incident response |
| `DEC-013` | `CTR-017` | NIST AI Risk Management Framework (AI RMF 1.0) | MAP 1.1 — Intended purpose and context are understood and documented |
| `DEC-019` | `CTR-011` | FTC Act Section 5 (15 U.S.C. § 45) | Section 5(a) — Unfair or deceptive acts or practices, as applied to AI |

Four distinct frameworks/regimes represented: GDPR, the EU AI Act, NIST AI RMF, and the FTC Act. No framework is mapped more than once to the same decision, consistent with the Workbench's quality-over-quantity mapping discipline (`EDITORIAL_POLICY.md`).

## 7. Required Evidence

Each control above is `REQUIRES_EVIDENCE`-linked to exactly one evidence type — what an auditor or regulator would actually ask to see, not a general assertion that "testing was done."

| ID | Evidence type | What it contains | Required for |
|---|---|---|---|
| `EVI-012` | Chatbot Response Accuracy Audit Log | Structured log sampling policy-sensitive chatbot responses, each reviewed against current source-of-truth policy, with discrepancies and corrections recorded. | `DEC-014` |
| `EVI-004` | Data Protection Impact Assessment (DPIA) | Documents necessity/proportionality of processing, risk to individuals, high-risk classification, and safeguards including pre-decision human review. | `DEC-006` |
| `EVI-010` | Red-Team Test Report | Scenarios tested during adversarial red-teaming, findings, remediations, and a logged kill-switch/rollback drill with measured response time. | `DEC-011` |
| `EVI-013` | Content Safety Review Report | Prompt categories tested pre-release, per-category findings, remediations, and results from the limited-audience staged-rollout phase. | `DEC-013` |
| `EVI-018` | Crisis Escalation Protocol Test Report | Clinical reviewer's findings against structured crisis-adjacent test inputs, remediations, and a timed escalation-path drill confirming actual reachability. | `DEC-019` |

## 8. Board Questions

Each is `RAISES_BOARD_QUESTION`-linked from its decision, written as a single, concise, executive-actionable question — per the Workbench's editorial rule, one board question per governance concept, not a checklist disguised as a question.

- **`BRD-013`** (from `DEC-014`): *"If our customer-facing AI chatbot gives a customer incorrect information about pricing, eligibility, or policy, have we assessed our legal liability exposure the same way we would for a human agent's documented error — and would that liability hold up if challenged, as Air Canada's disclaimer argument did not?"*
- **`BRD-006`** (from `DEC-006`): *"For any consumer AI product we operate that could plausibly be used by minors, is our age-verification mechanism actually effective — not just a self-reported checkbox — and can we point to a documented GDPR legal basis for every category of EU user data we process, including data used for model training?"*
- **`BRD-010`** (from `DEC-011`): *"If our public-facing AI system began producing harmful or offensive output — through adversarial manipulation or otherwise — how quickly could we detect and disable it, and has that response actually been drilled?"*
- **`BRD-012`** (from `DEC-013`): *"Before enabling a new generative AI content feature to the public, was it tested against context-specific prompt categories — including cases where a safety or fairness adjustment could conflict with factual or historical accuracy — and did we use a staged rollout with a fast rollback path?"*
- **`BRD-018`** (from `DEC-019`): *"If a user showing signs of crisis interacts with our chatbot, does it reliably escalate to a trained human, or does it handle the interaction alone?"*

## 9. Architecture Review Checklist

For an architecture or design review of a customer-facing AI system before launch or before a material change. Each item is derived directly from the decision/pattern pair cited — nothing here is a general best practice not already stated in the canonical data above.

- [ ] **Accuracy accountability** (`DEC-014` / `PAT-013`): Are the system's substantive policy statements (pricing, eligibility, refunds) grounded in a maintained, versioned source-of-truth document rather than open-ended generation?
- [ ] **Correction path** (`PAT-013`): Does a discrepancy between the system's output and actual policy trigger the same urgency of correction as a documented human-agent error?
- [ ] **Legal basis documentation** (`DEC-006` / `PAT-006`): Is there a documented GDPR (or equivalent) legal basis for every category of user data processed, including any data used for model training?
- [ ] **Age verification** (`PAT-006`): If the product could plausibly reach minors, does age verification go beyond a self-reported checkbox?
- [ ] **Adversarial testing** (`DEC-011` / `PAT-010`): If the system adapts its behavior from live input, has it been red-teamed specifically for coordinated manipulation, not just individual adversarial prompts?
- [ ] **Kill-switch rehearsal** (`PAT-010`): Has the kill-switch/rollback mechanism been *drilled*, with a measured response time — not just documented as existing?
- [ ] **Context-specific pre-release testing** (`DEC-013` / `PAT-012`): For a generative content feature, have distinct prompt categories been enumerated and tested individually, including categories where safety/fairness tuning could conflict with factual accuracy?
- [ ] **Staged rollout** (`PAT-012`): Is there a limited-audience release phase with a fast feedback and rollback path before full public availability?
- [ ] **Vulnerable-population screening** (`DEC-019` / `PAT-018`): Is this product, or could it plausibly become, used by an emotionally vulnerable population or minors — and if so, has it had a clinical safety review specifically for crisis-adjacent inputs?
- [ ] **Escalation reachability** (`PAT-018`): Has the crisis-escalation path been tested end-to-end to confirm a trained human is actually, currently reachable through it?

## 10. Audit Checklist

Assembled directly from every `follow_up_actions` entry recorded on this cluster's five Board Questions (`docs/schemas.md` / `/schemas/board_question.schema.json`) — these are the concrete requests an auditor or board committee should make, verbatim from canonical data, not paraphrased.

**From `BRD-013` (chatbot accountability):**
- Confirm chatbot responses to policy-sensitive questions are grounded in current source-of-truth policy documents.
- Confirm there is a review/correction process for chatbot errors comparable to the process for human agent errors.
- Ask legal/compliance whether the organization's terms of service attempt to disclaim chatbot statements, and whether that disclaimer has been tested.

**From `BRD-006` (consumer AI legal basis / age verification):**
- Request the current data protection impact assessment covering EU user data processing.
- Ask what age-verification mechanism is in place and how its effectiveness was tested.
- Confirm the privacy notice discloses whether user interactions are used for model training, and whether users can opt out.

**From `BRD-010` (public-facing system incident response):**
- Request the most recent red-team test report and confirm it includes a timed kill-switch drill.
- Confirm red-teaming specifically includes coordinated-manipulation scenarios, not just individual bad prompts.
- Ask who has authority to trigger the kill switch and how quickly they can be reached.

**From `BRD-012` (generative content pre-release testing):**
- Request the content safety review report for the most recently released generative feature.
- Confirm testing explicitly covered categories where safety/fairness tuning could conflict with accuracy.
- Ask whether a staged rollout with monitoring preceded full public availability.

**From `BRD-018` (crisis escalation):**
- Request the most recent crisis escalation protocol test report.
- Confirm clinical review specifically included eating-disorder, self-harm, and suicide-adjacent test inputs where relevant to the product's user base.
- Ask who is reachable through the escalation path and whether that reachability has been tested, not assumed.

## 11. Common Failure Modes

Each generalized from the specific `root_cause` recorded on the incident(s) that demonstrate it.

1. **Disclaiming the system's own output.** Treating a chatbot as a legally separate entity whose statements the company isn't accountable for. Demonstrated in `INC-002`; rejected by the Civil Resolution Tribunal of British Columbia.
2. **Age verification as a formality.** A self-reported checkbox standing in for an actual verification mechanism, on a product plausibly reachable by minors. Demonstrated in `INC-012`, `INC-013`, `INC-032`.
3. **Legal basis assumed rather than documented and justified.** Relying on "legitimate interests" or similar without a documented, scale-appropriate justification for the specific processing involved. Demonstrated in `INC-012`, `INC-035`.
4. **No rehearsed disable capability.** A documented incident-response plan that has never been tested as an actual timed drill, discovered only once real-time manipulation is already underway. Demonstrated in `INC-018`.
5. **Testing the average case, not the specific case.** A safety or fairness adjustment validated against broad, generic prompts but never tested against the specific historical or contextual categories where it conflicts with accuracy. Demonstrated in `INC-020`.
6. **Repurposing a narrow-use-case system for a higher-stakes population without re-review.** A chatbot built and tested for one context (general wellness, casual companionship) deployed into a higher-stakes one (crisis response, a minor's primary emotional relationship) without a review scoped to the new context. Demonstrated in `INC-027`, `INC-028`.
7. **No tested path to a human.** An escalation mechanism that exists on paper but has not been confirmed, end-to-end, to actually reach a trained person. Demonstrated in `INC-027`, `INC-028`.

## 12. Coverage and Confidence

Stated explicitly, per `EDITORIAL_POLICY.md`'s standard, rather than left implicit:

- **Confidence level.** All five Decisions in this cluster are currently `Community` confidence and `draft` status — authored and internally consistent, but not yet independently re-verified by a second reviewer per `REVIEW_PROCESS.md`. Treat this playbook as a strong starting structure for a governance review, not as pre-verified compliance guidance.
- **Framework gaps.** No control in this cluster maps to ISO/IEC 42001 or NYC Local Law 144 — a known, dataset-wide gap, not specific to customer-facing AI (see `docs/quality-audit-2026-08.md`). No decision in this cluster maps to EU AI Act Article 5 (prohibited practices) or Article 6/Annex III (high-risk classification), even though manipulation-adjacent practices and vulnerable-population targeting are plausibly relevant to the companion/crisis-adjacent incidents (`INC-013`, `INC-027`, `INC-028`) — this mapping does not exist in the current dataset and is not asserted here; it is flagged as a candidate for a future edition rather than filled in speculatively.
- **Jurisdictional coverage.** All nine incidents are US, EU, UK, or Canadian. No incident in this cluster documents customer-facing AI governance failures in Asia-Pacific, Latin America, Africa, or the Middle East — a gap worth naming for any organization operating customer-facing AI in those markets.
- **Citation depth.** Per `CITATION_POLICY.md`, this cluster's objects carry the dataset-wide average citation completeness (61.3/100 as of Edition 1.1) — most citations have a `url` and a `title`/`publisher`, fewer have a specific `locator` or `excerpt`. Verify a citation against its primary source before relying on it for a specific factual claim in a live governance decision.

## References

Primary sources for every incident and control cited above, in citation order:

1. *Moffatt v. Air Canada*, 2024 BCCRT 149 — Civil Resolution Tribunal of British Columbia, 2024-02-14. `INC-002`.
2. "Intelligenza artificiale: il Garante blocca ChatGPT..." — Garante per la protezione dei dati personali, 2023-03-31. `INC-012`.
3. "Intelligenza artificiale, dal Garante privacy stop al chatbot 'Replika'..." — Garante per la protezione dei dati personali, 2023-02-03. `INC-013`.
4. "ICO orders Snap to address risks posed by 'My AI' chatbot" — Information Commissioner's Office, 2023-10-06. `INC-032`.
5. "ICO statement in response to Snap's updated risk assessment for My AI chatbot" — Information Commissioner's Office, 2023-12-14. `INC-032`.
6. "Data Protection Commission welcomes Meta's decision to pause plans to train its Large Language Model..." — Data Protection Commission (Ireland), 2024-06-14. `INC-035`.
7. "ICO statement in response to Meta pausing generative AI training using UK users' data" — Information Commissioner's Office, 2024-06-14. `INC-035`.
8. "Learning from Tay's introduction" — The Official Microsoft Blog, 2016-03-25. `INC-018`.
9. "Gemini image generation got it wrong. We'll do better." — Google (The Keyword), 2024-02-23. `INC-020`.
10. "Chatbot that offered bad advice for eating disorders taken down" — NPR, 2023-06-08. `INC-027`.
11. *Garcia v. Character Technologies, Inc. et al.*, 6:2024cv01903 — U.S. District Court, Middle District of Florida, 2024-10-22. `INC-028`.
12. "FTC Launches Inquiry into AI Chatbots Acting as Companions" — Federal Trade Commission, 2025-09-11. `INC-028`.
13. Regulation (EU) 2016/679 (General Data Protection Regulation) — EUR-Lex, 2016-05-04. `CTR-010`.
14. Artificial Intelligence Risk Management Framework (AI RMF 1.0) — NIST, 2023-01-26. `CTR-015`, `CTR-017`.
15. Regulation (EU) 2024/1689 (Artificial Intelligence Act) — EUR-Lex, 2024-07-12. `CTR-018`.
16. "Aiming for truth, fairness, and equity in your company's use of AI" — FTC Business Guidance Blog, 2021-04-19. `CTR-011`.
17. "Rite Aid Banned from Using AI Facial Recognition..." — Federal Trade Commission, 2023-12-19. `CTR-011`.

Full citation records, including `locator` and `excerpt` fields where present, are in the source JSON files under `/workbench/data` and on each object's page in the Explorer.

---

*This playbook is a derived view of the AI Governance Workbench's canonical dataset. It is not a substitute for independent legal or compliance review, and per `EDITORIAL_POLICY.md`'s independence statement, is not sponsored by or written on behalf of any organization named above. Corrections follow the same process as any other canonical content — see `EDITORIAL_POLICY.md`'s correction policy.*
