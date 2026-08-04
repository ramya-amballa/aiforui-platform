# Edition 1.1

**Released:** 2026-08-04 · **Incidents:** 35 (`INC-001`–`INC-035`) · **Canonical objects:** 139

This edition expands the Foundational Twenty into a 35-incident dataset under Phase 3's Infrastructure Freeze: no new platform features, only canonical knowledge growth. Every incident promoted this edition was required to answer the six mandatory editorial questions (governance decision, observable evidence, one primary pattern, genuinely-applicable controls, one board question, confidence rationale) before being added. Precision over completeness: several well-researched candidates (India Aadhaar, UK DWP algorithmic welfare fraud detection) were deliberately held back for Edition 1.2 rather than added to hit a round number.

## New incidents (15)

SCHUFA credit-scoring / CJEU automated-decision ruling (`INC-021`) · Civio v. Spain, BOSCO fuel-poverty algorithm disclosure (`INC-022`) · France Parcoursup algorithm transparency (`INC-023`) · Uber Amsterdam "robo-firing" driver deactivation (`INC-024`) · Deliveroo Italy ranking-algorithm discrimination ruling (`INC-025`) · OpenAI/Sama Kenyan data-labeler working conditions (`INC-026`) · NEDA Tessa chatbot crisis-response failure (`INC-027`) · Character.AI / Garcia wrongful-death lawsuit (`INC-028`) · Amazon Rekognition / ACLU congressional accuracy test (`INC-029`) · Zillow Offers algorithmic home-buying shutdown (`INC-030`) · Allegheny Family Screening Tool AP investigation / DOJ scrutiny (`INC-031`) · Snapchat My AI / UK ICO DPIA enforcement (`INC-032`) · Mata v. Avianca ChatGPT-hallucinated legal citations (`INC-033`) · DoNotPay FTC "AI lawyer" settlement (`INC-034`) · Meta EU/UK generative-AI training-data pause (`INC-035`).

Five of these fifteen (Parcoursup, Rekognition/ACLU, Allegheny, Snapchat/ICO, Meta training pause) are deliberate reuses of Edition 1.0 governance clusters rather than new Decisions/Patterns/Controls — each incident file documents in its own `history` note why reuse was chosen over a near-duplicate object, directly serving the "avoid over-linking" and pattern-reuse-frequency editorial goals.

## New Governance Decisions (8)

`DEC-015`–`DEC-022`:
- `DEC-015` — Treat a decisively-relied-upon score as triggering GDPR Article 22, requiring evidence of genuine (not symbolic) human deviation from automated scores.
- `DEC-016` — Proactively disclose the logic of any algorithm used to determine eligibility for a public benefit.
- `DEC-017` — Guarantee genuine human review and disclosure before an algorithm penalises or deactivates a platform worker.
- `DEC-018` — Require documented labour and psychological-safety standards for any data-labelling workforce.
- `DEC-019` — Require clinical safety review and crisis-escalation protocols before deploying a chatbot to an emotionally vulnerable user population.
- `DEC-020` — Require independent public accuracy testing before any law-enforcement procurement of facial recognition (deliberately reuses `PAT-007`/`CTR-007`/`EVI-006`/`BRD-007` rather than creating near-duplicates).
- `DEC-021` — Require a pre-defined, binding model-risk kill criterion before scaling an algorithmic program with direct financial exposure.
- `DEC-022` — Verify AI-generated output against authoritative primary sources before professional reliance.

## New Design Patterns (7)

`PAT-014`–`PAT-020`: Meaningful Human Deviation Pattern · Public Algorithm Transparency Register Pattern · Worker-Facing Algorithmic Decision Transparency & Appeal Pattern · Data Labeling Workforce Welfare Pattern · Crisis Escalation & Clinical Safety Review Pattern · Algorithmic Model-Risk Kill Criterion Pattern · AI Output Primary-Source Verification Pattern.

## New Framework Controls (4)

`CTR-019`–`CTR-022`, all citing real, directly-applicable provisions: **EU Platform Work Directive** ((EU) 2024/2831, Articles 7–11, algorithmic management transparency) · **ILO Declaration on Fundamental Principles and Rights at Work** (data-labeling workforce standards) · **SR 11-7 / OCC 2011-12** (Federal Reserve model-risk-management guidance, recorded at `Community` confidence pending a dedicated verification pass) · **ABA Model Rules of Professional Conduct, Rule 1.1, Comment 8** (technological-competence duty).

## New Evidence Types (7) and Board Questions (7)

`EVI-014`–`EVI-020`, `BRD-014`–`BRD-020` — one evidence type and one board question per new governance-concept cluster, each board question kept to a single, concise, executive-actionable ask per the Phase 3 editorial rule.

## Coverage improvements

- **New governance domains opened**: platform/gig-work algorithmic management, data-labeling workforce welfare, generative-AI mental-health/crisis-safety, financial model-risk kill criteria, and AI-output verification before professional reliance (legal/consumer-service reliance on hallucinated content) — none of which existed in Edition 1.0.
- **New jurisdictions**: Germany (`DE`), Spain (`ES`), France (`FR` — new incident, existing cluster), Ireland (`IE`), Kenya (`KE`) join the dataset for the first time.
- **Cross-framework overlap** newly visible in `editorial:insights`: `EVI-004` (DPIA) is now required by controls from both the EU AI Act and GDPR; `EVI-001` (Bias Audit Report) by both EEOC guidance and NIST AI RMF.
- **Pattern reuse** is now measurable and non-trivial: `PAT-007` (Biometric Collection & Use Safeguards) is reused by 3 objects, the first pattern in the dataset to cross the single-decision threshold.
- Zero-Orphan Invariant: **PASS** — all 139 objects have at least one relationship. Coverage Matrix: all 6 entity types remain above the sparse-connectivity threshold (avg degree 2.63–6.55). See `npm run editorial:health` and `npm run editorial:coverage` for the live reports.

## Known coverage gaps (deliberately left open)

`ISO/IEC 42001` and `NYC Local Law 144` still have no standalone Framework Control (unchanged from Edition 1.0). Twelve jurisdictions now have exactly one incident (`CA`, `CA-BC`, `DE`, `ES`, `FR`, `IE`, `KE`, `KR`, `US-AZ`, `US-NH`, `US-NY`, `US-PA`) — genuine breadth, but each is a single data point, not a validated pattern. Citation completeness averages 61.3/100 dataset-wide (126 of 139 objects below 70): most citations lack a specific locator/excerpt and most relationship edges don't yet cite a specific `citation_id` — a systemic gap carried over from Edition 1.0, not introduced this edition, and the next clear target for editorial (not incident-count) work.

## Editorial infrastructure

No new platform features this edition, per the Infrastructure Freeze. The Editorial Analytics tool (`editorial:insights`, added just before the freeze) was used directly to identify pattern-reuse frequency, cross-framework overlap, and weakly-covered areas cited above — the graph explaining itself, as intended.

## Editorial principle for this edition

Every one of the 15 new incidents was authored against the six mandatory questions before promotion: the actual governance decision (not just "what happened"), observable evidence only, exactly one primary pattern, only genuinely-applicable controls, one concise board question, and an explicit confidence rationale. Five incidents were deliberately mapped onto existing Edition 1.0 clusters instead of generating near-duplicate governance objects — curation over aggregation. Two well-researched candidates were held back for Edition 1.2 rather than included to inflate this edition's count.
