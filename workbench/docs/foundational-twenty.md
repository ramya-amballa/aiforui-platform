# The Foundational Twenty

Phase 2A's seed content: 20 real, independently verified AI governance incidents, each fully linked through at least one Governance Decision, Design Pattern, Framework Control, Evidence Type, and Board Question. `INC-001` through `INC-020`.

## Selection principle

Per the Phase 2A brief: **select incidents that maximise governance-decision coverage, not media popularity.** Concretely, that meant grouping candidate incidents into distinct governance-concept clusters *first*, then picking the best-documented real incident(s) for each cluster — rather than picking 20 famous AI news stories and forcing them into a handful of repeated "require a bias audit"-style decisions. Two incidents that are both about hiring discrimination (Amazon, iTutorGroup) share a decision; two incidents that look superficially similar but raise genuinely different governance questions (Rite Aid's biased *use* of facial recognition vs. Clearview's non-consensual *collection* of biometric data) get two separate decisions, patterns, and controls, because collapsing them would have hidden a real distinction a practitioner needs.

Coverage was checked, not assumed: `npm run editorial:coverage`'s Coverage Matrix and harm-type/framework breakdowns were run throughout authoring — see "Coverage snapshot" below — specifically to catch a cluster repeating a governance concept the dataset already had well covered.

## The 13 governance-concept clusters

| Cluster | Incidents | Decision | Core governance concept |
|---|---|---|---|
| 1. Hiring/employment screening bias | Amazon (`INC-001`), iTutorGroup (`INC-003`) | `DEC-001` | Pre-deployment bias audits for hiring AI |
| 2. Risk-scoring fairness & proxy bias | COMPAS (`INC-004`), healthcare algorithm (`INC-005`) | `DEC-002` | Disaggregated error-rate testing; proxy-variable scrutiny |
| 3. Autonomous vehicle / driver-assist safety | Uber Tempe fatality (`INC-006`), Tesla Autopilot recall (`INC-007`) | `DEC-003` | Monitored, verified human-oversight fallback |
| 4. Automated adverse decisions in public services | Dutch SyRI (`INC-008`), UK Ofqual (`INC-009`), Australia Robodebt (`INC-010`) | `DEC-004` | Pre-decision human review, legal basis, DPIA |
| 5. Enterprise generative-AI data governance | Samsung ChatGPT leak (`INC-011`) | `DEC-005` | Technically-enforced acceptable-use policy |
| 6. Consumer generative-AI data protection (EU) | Italy/ChatGPT (`INC-012`), Italy/Replika (`INC-013`) | `DEC-006` | GDPR legal basis + effective age verification |
| 7. Facial recognition / biometric surveillance | FTC v. Rite Aid (`INC-014`), Clearview AI (`INC-015`) | `DEC-007`, `DEC-008` | Accuracy + human review (use); informed consent (collection) |
| 8. Election integrity / synthetic media | NH Biden robocall (`INC-016`) | `DEC-009` | Synthetic media detection and disclosure |
| 9. Credit/lending algorithmic explainability | Apple Card / Goldman Sachs (`INC-017`) | `DEC-010` | Specific, individualised adverse-action reasons |
| 10. Public-facing learning AI safety | Microsoft Tay (`INC-018`) | `DEC-011` | Adversarial red-teaming + tested kill switch |
| 11. Generative AI training-data provenance / IP | Getty Images v. Stability AI (`INC-019`) | `DEC-012` | Training-data provenance and licensing review |
| 12. Generative AI output safety review | Google Gemini image generation (`INC-020`) | `DEC-013` | Context-specific pre-release testing, staged rollout |
| 13. Chatbot output accountability | Air Canada / Moffatt (`INC-002`) | `DEC-014` | Chatbot statements as binding company communications |

`INC-002` (Air Canada) was promoted through the actual ingestion pipeline (`npm run ingest:promote`) rather than authored directly, as a live demonstration of that pipeline on real content — see `/docs/ingestion-pipeline.md`.

## Framework coverage achieved

Across 18 Framework Controls: **NIST AI RMF** (5 subcategories: GOVERN 1.2, MAP 1.1, MAP 5.1, MEASURE 2.11, MANAGE 4.1), **EU AI Act** (6 articles: 5, 6/Annex III, 10, 13, 14, 15), **GDPR** (3 articles: 5, 22, 35), **BIPA**, **FCRA**, **FTC Act Section 5**, and **EEOC Title VII AI guidance**. Run `npm run editorial:coverage` for the exact current counts.

**Known gaps**, left deliberately rather than papered over: no control yet cites **ISO/IEC 42001** or **NYC Local Law 144** as its own Framework Control object (NYC LL144 is currently only present as a *citation* on `PAT-001`/`EVI-001`, not as a standalone control). Jurisdiction coverage is concentrated in the US and EU/UK, with single-country representation for Korea (Samsung), the Netherlands (SyRI), Canada (Air Canada), and Australia (Robodebt) — Africa, South America, and most of Asia beyond Korea have no incidents yet. These are exactly the kind of gaps `npm run editorial:coverage`'s Coverage Matrix and gap callouts are meant to surface for the *next* round of additions.

## Confidence honesty

Every incident is `Reviewed` (cross-checked against multiple independent sources by dedicated research passes, with specific uncertain facts — exact dates, disputed figures, unresolved legal statuses — flagged in each object's `description`, `root_cause`, or `history` note rather than stated as settled). Every Decision, Pattern, and most Controls are `Community` confidence: they are illustrative reference objects modelling a plausible governance response, explicitly not documented decisions of any real organisation, and not yet independently human-reviewed. See `/docs/confidence-model.md`.

## Extending this set

Use the editorial tools in `/editorial` (see `/editorial/README.md`) before adding new incidents:

1. `npm run editorial:coverage` — check the Coverage Matrix and gap callouts first, to pick an incident that fills a real gap rather than duplicating an already-covered concept.
2. `npm run editorial:wizard` (for a news-sourced incident) or write directly into `/data` (for other entity types) — see `/docs/contributing.md`.
3. `npm run editorial:suggest -- --id=<new-id>` — get rule-based candidate relationships instead of guessing.
4. `npm run editorial:citations` and `npm run editorial:health` — check citation completeness and confirm the Zero-Orphan Invariant still holds before opening a PR.
5. `npm run validate` — the actual merge gate.
