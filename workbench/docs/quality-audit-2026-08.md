# Repository Quality Audit — August 2026

**Run:** 2026-08-05 · **Scope:** all 139 canonical objects in `/data` · **Tool:** `npm run editorial:audit` (new, permanent, read-only — see `/editorial/README.md`)

This is the audit requested ahead of Edition 1.2: a comprehensive, deterministic pass over every canonical object checking naming consistency, terminology, citation depth, and relationship rationale against the ontology — not a new-content pass. No incidents were added. No object's substantive claims were rewritten. Every change described below is mechanical: a rule was defined, applied consistently, and is re-checkable by running the audit tool again.

## Method

`editorial/src/audit.ts` is the seventh `/editorial` tool, built the same way the other six are: it reuses `/validators`' own loaders so "the graph" means the same thing everywhere, it is read-only (it never writes to `/data` — see "Why `/editorial` doesn't get a write path into `/data`" in `/docs/architecture.md`), and its findings are graded by severity:

- **ERROR** — should block a release.
- **WARNING** — fixed as part of this same pass, because the fix is mechanical.
- **INFO** — logged for future editorial judgment, deliberately not auto-fixed, because closing it requires research or a content rewrite, not a rule.

The fixes themselves were applied as an ordinary direct edit to `/data` (the same path any contributor uses for Decisions/Patterns/Controls/Evidence/Board Questions per `/docs/contributing.md`) — the audit tool measured the gap, a one-off script closed it, then the audit tool re-ran to confirm zero remaining warnings in its own categories.

## Results

| Severity | Before fixes | After fixes |
|---|---|---|
| ERROR | 0 | 0 |
| WARNING | 9 | 1 (citation depth — see below, not mechanically closeable) |
| INFO | 4 | 3 |

`npm run validate` (139/139 objects), `npm run typecheck`, and `npm run editorial:health` (composite score 82.2/100, structural validity 100/100) all pass after the fixes below. **53 of 139 objects (38%) were touched**, each with a version bump and a `history` entry recording exactly what changed and why — the same discipline the project already requires of every substantive edit.

## 1. Naming conventions — fixed

Checked whether each entity type's titles follow the convention the dataset had already, overwhelmingly, established for itself:

- **Design Patterns**: 18/20 titles ended in "Pattern." Two didn't — `PAT-001` ("Pre-Deployment Bias Audit Gate") and `PAT-006` ("Age Verification & Legal Basis Gate for Consumer AI"). Fixed:
  - `PAT-001` → "Pre-Deployment Bias Audit Gate **Pattern**"
  - `PAT-006` → "**Consumer AI** Age Verification & Legal Basis Gate Pattern" (reordered, not just appended, so the sentence still reads naturally)
- **Board Questions**: all 20 titles and `question_text` fields already end in "?" — no fix needed.
- **Evidence Types**: all 20 titles already end in an established artifact noun (Report / Record / Log / Attestation / a recognized acronym like DPIA) — no fix needed.
- **Governance Decisions**: all 22 titles already open with an imperative verb (Require, Treat, Prohibit, Guarantee, Verify, Proactively disclose) — no fix needed.
- **Framework Controls**: all 22 titles already follow "Framework Reference — Description" — no fix needed.

Net: the dataset's naming discipline was already strong. Two outliers, both fixed.

## 2. Terminology consistency (US/UK spelling) — fixed

The dataset had never settled on one English dialect, and it showed: `organisation`/`organization`, `labour`/`labor`, `labelling`/`labeling`, `labelled`/`labeled`, `labeller(s)`/`labeler(s)`, `licence`/`license`, `programme`/`program`, and `judgement`/`judgment` all appeared in **both** spellings somewhere in the corpus — in a few cases within the same governance cluster (`DEC-018`'s title said "documented labour ... standards" while its own linked Pattern was titled "Data Labeling Workforce Welfare Pattern").

**Decision: American English is the house style**, on the same reasoning `/docs/architecture.md` already applies elsewhere — schema field names are American (`organizations_involved`), the dataset's dominant jurisdiction is the US (31 of ~90 jurisdiction tags), and the majority of cited frameworks are American sources (NIST, FTC, EEOC, FCRA, BIPA). This is the one genuine judgment call in this audit; applying it consistently afterward was mechanical.

**What was excluded, deliberately:** citation `title`/`publisher`/`excerpt` fields were never touched. A citation excerpt is a verbatim quotation from an external source; "correcting" its spelling would misrepresent what the source actually says. The one instance of "programme" inside a citation excerpt (a Spanish Supreme Court ruling, in translation) stays exactly as quoted. "International Labour Organization" — the ILO's actual, correctly-spelled legal name — was never at risk, for the same reason: it lives only inside a citation `publisher` field. Permanent slugs (e.g. `ilo-core-labour-standards`) were also left untouched, per the project's own rule that a published slug never changes.

Normalized across 44 objects' prose fields (`title`, `description`, `problem`, `solution`, `decision_statement`, `root_cause`, relationship `reason` text, and similar editorially-authored fields — never citations): `organisation(s)/organisational` → `organization(s)/organizational`, `labour` → `labor`, `labelling/labelled/labeller(s)` → `labeling/labeled/labeler(s)`, `licence(s)` → `license(s)`, `programme(s)` → `program(s)`, `judgement` → `judgment`.

**Left as-is, and flagged for a future style decision rather than mass-edited:** a handful of British spellings appear *consistently* (not mixed) throughout the corpus — `modelled` (43 occurrences, 0 `modeled`), `practice` used consistently as both noun and verb (0 `practise`, correct either way), `centre`, `colour`, `behaviour`, `defence`. These aren't inconsistencies — they're a uniform choice — so fixing them isn't what this audit's WARNING-vs-INFO distinction calls for. If a future edition adopts American English as an explicit, permanent style guide, these are the next candidates; noted here so that decision doesn't get re-litigated from scratch.

## 3. Relationship-reason wording — fixed (one case)

The single most common relationship in the dataset — a Decision `IMPLEMENTED_BY` its one primary Pattern — had two different boilerplate phrasings doing the same job: "The decision is put into practice via this design pattern." (14 uses) and "...via this single, primary design pattern." (5 uses). Normalized all 19 to the second, more informative phrasing, since it reinforces the Phase 3 "one primary pattern, avoid over-linking" principle the rest of the dataset already follows.

## 4. Tag hygiene — checked, clean

Compared all 90 unique tags pairwise (ignoring hyphens/underscores/case) for near-duplicates from inconsistent spelling (e.g. `facial-recognition` vs `facial_recognition`). None found.

## 5. Relationship rationale vs. the ontology — checked, clean

Re-validated all 248 relationships' `(verb, source_type, target_type)` triples against `/relationships/ontology.json` — `/validators` already guarantees this structurally, this is a redundant confirmation, and it came back clean, as expected. Every reason string is at least 30 characters (no placeholder-length reasons).

## 6. What's still open (not mechanically fixable — carried into Edition 1.2)

**Citation depth is the real gap**, and closing it honestly requires re-reading sources, not a script:

- Dataset-wide average citation completeness: **61.3/100**. Edition 1.2 target, per the brief: **80/100**.
- 137 of 139 objects are below that target. Roughly evenly spread across all six entity types (19–35 each) — this is not concentrated in one weak corner of the dataset, it's systemic: most citations have a `url` but lack a `locator` (the specific paragraph/section/page) and an `excerpt` (a short supporting quotation), and most relationship edges don't yet cite a specific `citation_id`.
- This cannot be fabricated. A locator has to be read off the actual document; an excerpt has to be a real quotation. The honest path is a dedicated research pass — re-fetch each of the ~58 unique cited sources, record a real locator and excerpt, and link relationship edges to the specific citation that supports them — sized as its own piece of Edition 1.2 work, not folded into this audit.

**Generic relationship reasons** (2 phrasings still reused 3+ times verbatim — the normalized "single, primary design pattern" one at 19 uses, and "modelled as a direct governance response to this incident" at 5): not wrong, every one of them is a true statement, but they're templated rather than incident-specific. Writing a bespoke reason for each requires reading the specific incident again, which is editorial depth work, not a consistency fix.

**`ai_system_category` taxonomy sprawl**: 27 distinct free-text values across 35 incidents, 22 of them used only once (e.g. `mental_health_chatbot`, `robocall_voice_cloning`, `automated_grading`). This field was deliberately left as free text rather than an enum in Phase 1, and at 35 incidents it's genuinely unclear where the category boundaries should sit — collapsing `customer_service_chatbot` and `conversational_chatbot`, for instance, is a real modeling decision, not a spelling fix. Worth a controlled vocabulary once Edition 1.2 or 2.0 gives it enough data points to define boundaries without guessing.

## Reproducing this audit

```sh
cd workbench
npm run editorial:audit                          # console report
npm run editorial:audit -- --out=report.md        # write to a file
```

Re-run after every future edition. The naming/spelling/tag-hygiene checks should stay clean by construction now that the house style is decided; the citation-depth number is the one to watch trend toward 80.
