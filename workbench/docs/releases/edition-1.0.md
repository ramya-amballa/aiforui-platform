# Edition 1.0 — The Foundational Twenty

**Released:** 2026-08-04 · **Incidents:** 20 (`INC-001`–`INC-020`) · **Canonical objects:** 91

This is the AI Governance Workbench's first canonical edition: the data foundation (schemas, ontology, validation engine, ingestion pipeline), the editorial tooling that supports it, and the first curated body of real, independently-verified AI governance incidents fully linked through the six-entity ontology. Treat this document as a citable snapshot of the dataset at this point in its history — later editions build on it but do not retroactively change what this edition contained.

## New incidents (20)

Amazon recruiting-tool bias (`INC-001`) · Air Canada chatbot liability (`INC-002`) · iTutorGroup EEOC age discrimination (`INC-003`) · COMPAS/ProPublica (`INC-004`) · healthcare risk-prediction bias (`INC-005`) · Uber Tempe AV fatality (`INC-006`) · Tesla Autopilot recall (`INC-007`) · Dutch SyRI/childcare benefits scandal (`INC-008`) · UK Ofqual grading algorithm (`INC-009`) · Australia Robodebt (`INC-010`) · Samsung ChatGPT leak (`INC-011`) · Italy/ChatGPT ban (`INC-012`) · Italy/Replika ban (`INC-013`) · FTC v. Rite Aid facial recognition (`INC-014`) · Clearview AI (`INC-015`) · NH Biden deepfake robocall (`INC-016`) · Apple Card/Goldman Sachs (`INC-017`) · Microsoft Tay (`INC-018`) · Getty Images v. Stability AI (`INC-019`) · Google Gemini image generation (`INC-020`).

See [`/docs/foundational-twenty.md`](../foundational-twenty.md) for the full selection rationale and the 13 governance-concept clusters these incidents organise into.

## New Governance Decisions (14)

`DEC-001`–`DEC-014`, spanning: pre-deployment bias audits for hiring AI; disaggregated fairness testing for risk-scoring algorithms; verified human-oversight for automated driving; meaningful human review before automated adverse decisions in public services; enterprise generative-AI acceptable-use policy; GDPR legal-basis/age-verification gates for consumer AI; facial-recognition accuracy/human-review and biometric-consent requirements (two decisions, one cluster); synthetic-media disclosure for election integrity; adverse-action explainability for credit decisions; adversarial red-teaming and kill switches for public-facing learning AI; training-data provenance review; staged rollout for generative content features; chatbot output accountability.

## New Design Patterns (13)

`PAT-001`–`PAT-013`, one primary pattern per decision (one pattern, `PAT-007`, shared across two decisions addressing related biometric-safeguard concerns).

## New Framework Controls (18)

`CTR-001`–`CTR-018`, citing real provisions across **NIST AI RMF** (5: GOVERN 1.2, MAP 1.1, MAP 5.1, MEASURE 2.11, MANAGE 4.1), **EU AI Act** (6: Articles 5, 6/Annex III, 10, 13, 14, 15), **GDPR** (3: Articles 5, 22, 35), **BIPA**, **FCRA**, **FTC Act Section 5**, and **EEOC** Title VII AI guidance.

## New Evidence Types (13) and Board Questions (13)

`EVI-001`–`EVI-013`, `BRD-001`–`BRD-013` — one evidence type and one board question per governance-concept cluster.

## Coverage achieved

Harm types: all 8 represented (discrimination, privacy_violation, safety, financial, reputational, misinformation, security, other). Jurisdictions: US, EU/UK, Netherlands, Italy, Australia, South Korea, Canada. Relationship verbs: all 7 used at least once. Structural health: 0 validator errors, 0 orphans, all soft/hard outbound-edge limits respected.

## Known coverage gaps (deliberately left open, not papered over)

No standalone Framework Control yet for **ISO/IEC 42001** or **NYC Local Law 144** (the latter is present only as a citation on `PAT-001`/`EVI-001`, not its own control object). Jurisdiction coverage outside the US/EU/UK is thin (single-incident representation for NL, IT×2, AU, KR, CA). No incidents yet from Africa, South America, or most of Asia beyond South Korea. See `npm run editorial:coverage` for the live, current picture.

## Editorial infrastructure delivered this edition

- **Schemas, ontology, validation engine** (`/schemas`, `/relationships`, `/validators`) — the merge gate.
- **Ingestion pipeline** (`/ingestion`) — draft → human review → canonical promotion, with sequential ID/slug generation.
- **Editorial tooling** (`/editorial`) — Incident Authoring Wizard, Relationship Suggestion Engine, Citation Completeness Checker, Coverage Metrics Dashboard (with per-entity-type Coverage Matrix), Graph Health Report (with the Zero-Orphan Invariant as a hard, CI-enforced gate).
- **`ONTOLOGY.md`** — the project constitution: the Canonical Principle, the AI-authorship rule, and the full glossary.

## Editorial principle for this edition

Incidents were selected to maximise breadth of governance concepts, not media popularity — each of the 13 clusters represents a genuinely distinct governance lesson, not a repeated one. Every relationship carries an explicit `reason`; no edge was added because two concepts merely "seemed related."
