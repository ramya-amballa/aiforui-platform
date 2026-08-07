# Citation Policy

`/docs/citation-model.md` defines the citation *schema* — what fields exist and when they're required. This document defines the editorial judgment layered on top: what sources are acceptable, how different source types are weighted, and how citation quality is actually measured. It governs every `citations` entry in `/data`, using the same seven `source_type` values the schema defines: `regulator`, `legislation`, `court_judgment`, `company_statement`, `academic_paper`, `standards_body`, `news_publication`, `other`.

## Acceptable primary sources

A primary source is the thing itself: the regulator's own order, the statute's own text, the court's own judgment, the standard's own published document, the company's own statement. Primary sources are always preferred over reporting about them, and are required — not merely preferred — for any object claiming `Verified` confidence.

- **`regulator`** — an order, guidance document, enforcement action, or public statement issued directly by a regulatory body (e.g., the FTC, the ICO, a national data protection authority). Preferred over news coverage of the same action whenever the primary document is public.
- **`legislation`** — the text of a statute, regulation, or directive itself (e.g., GDPR Article 22, the EU AI Act). Cite the specific article or provision via `locator`, not the instrument as a whole.
- **`court_judgment`** — a court's or tribunal's own ruling or order. Cite the specific paragraph, page, or docket reference via `locator` wherever the source supports it.
- **`standards_body`** — a published standard or framework document from its issuing body (NIST, ISO/IEC, IEEE, etc.).
- **`company_statement`** — a statement made directly by the organization involved (a press release, an official blog post, an SEC filing, sworn testimony). Preferred over a third party's characterization of what a company said, though a company's self-serving framing should be read critically and, where it conflicts with regulator or court findings, the latter controls the dataset's characterization of what happened.

## Acceptable secondary sources

- **`news_publication`** — reporting from an outlet with an editorial/fact-checking process. Acceptable, and often necessary — many incidents are only publicly known through investigative journalism, and a primary source (an internal company decision, an unreported settlement) may not exist publicly at all. Preferred: outlets with original reporting (interviews, documents obtained directly) over outlets syndicating another outlet's reporting.
- **`academic_paper`** — peer-reviewed research. Strong for establishing a technical or empirical claim (e.g., a documented bias measurement); rarely sufficient alone to establish that a specific organizational governance failure occurred, which usually needs a regulator, court, or reporting source alongside it.
- **`other`** — the deliberate escape hatch in the schema for a legitimate source that doesn't fit the six categories above (e.g., a parliamentary committee report, an NGO investigation, a Freedom of Information disclosure). Using `other` is not a lower-quality choice by itself; it should not be used to avoid the judgment call of picking the right category when one of the six actually fits.

## Sources treated as insufficient on their own

- **Vendor blogs and vendor-commissioned research** — usable as a `company_statement` for what the vendor itself claims, but not as independent corroboration of a governance claim about that same vendor. A vendor's own blog post is not treated as confirming a fact that only the vendor benefits from asserting.
- **Conference papers without peer review** (as distinct from `academic_paper`, which implies peer review) — usable as `other`, but weighted like a preliminary claim, not an established one, until a more authoritative source corroborates it.
- **A single, uncorroborated social-media post or forum claim** — not an acceptable citation under any `source_type`. If a claim's only support is unverified social media, the claim is not ready for the canonical dataset.
- **Anonymous or unattributable sources** — a source needs an identifiable `publisher`. "Multiple sources say" reporting is acceptable to cite (as `news_publication`) for what the outlet reported, but the dataset should not present that reporting's underlying anonymous claims as more certain than the outlet itself asserts them to be.

## Treatment of court judgments

A `court_judgment` citation should reflect the judgment's actual holding, not a party's characterization of it, and should be updated if a ruling is appealed, reversed, or vacated — this is exactly the kind of change that should move an object's `status` toward `retracted` or trigger a correction under `EDITORIAL_POLICY.md`, not be left stale. Where a case is ongoing, the dataset should describe it as such (`status: draft` or `active` with the procedural posture stated in `description`), not presented as a settled outcome before it is one. Where multiple levels of a judgment exist (trial court, appeal), cite the most current, and note the procedural history in `description` when it materially affects what the object claims.

## Treatment of regulatory publications

A regulator's press release and the regulator's underlying order are different documents with different evidentiary weight — the order is the primary source; the press release is the regulator's own secondary summary of it. Prefer citing the order or formal decision directly when it's public; a press release is acceptable when the underlying order isn't publicly available, but should be identified as such.

## Treatment of government reports (non-regulatory)

Reports from a legislative body, an inspector general, an ombudsman, or a government audit office are cited as `other` (unless the schema's categories are later extended — see `/docs/relationship-model.md`'s "Extending the ontology" pattern, which applies equally to citation `source_type`) and are treated with the same weight as a regulator's own publication when the body has direct investigative authority over the matter it's reporting on.

## Treatment of news articles

News reporting is often the *only* public record of an incident, and is fully acceptable — the dataset would be far thinner without it. The policy distinction is about upgrading, not excluding: a claim resting solely on a single news article is a reasonable candidate for `Reviewed` confidence but should not reach `Verified` without either a primary source corroborating it or a second, independent outlet's original (not syndicated) reporting.

## Treatment of conference papers

Cited as `other` unless formally peer-reviewed and published (in which case `academic_paper` applies). Useful for surfacing emerging technical concerns before they reach peer review, but a conference paper's claims should be treated as preliminary in the object's `confidence` until more established sourcing exists.

## Duplicate sources

Multiple citations that trace back to the same original reporting or the same press release do not count as independent corroboration, even if they appear on different outlets' domains — this is a wire-service or syndication artifact, not two sources agreeing. A reviewer checking whether an object has "more than one source type" (part of how citation completeness is scored — see below) should verify the sources are actually independent, not merely differently labeled. Citing the same source twice under two different `id`s within one object's `citations` array is a data-quality defect the Repository Quality Audit checks for (`/docs/quality-audit-2026-08.md`), not an accepted way to pad citation count.

## Archived sources

A citation's `accessed_date` exists specifically so a stale or link-rotted source can be identified — the citation scorer (`scoreCitations`, `/editorial/src/lib/citation-score.ts`) flags any citation accessed more than three years ago for re-verification. If a source URL later disappears (link rot, a page taken down, a regulator restructuring its site), the citation is not deleted: `title`, `publisher`, and `accessed_date` remain as the record of what was originally cited, `url` may be removed or replaced with an archival link (e.g., a web archive snapshot) if one exists, and the object's `history` should note the change. A citation is never quietly deleted because its source became inconvenient to find — that would break the traceability this entire model exists to provide.

## How citation quality is measured

`editorial:citations` (per-object detail) and `editorial:health`/`editorial:audit` (dataset-wide aggregate) compute a deterministic 0–100 completeness score per object (`scoreCitations`), not a measure of source *credibility* — credibility is a human editorial judgment this policy governs; completeness is a mechanically checkable proxy for how easy a claim is for a reader to independently verify. The score rewards, in order: having at least one citation at all (base), the citation having a `url`, having a `locator` (a specific page/section/paragraph, not just the document), having an `excerpt` (a supporting quotation), citing more than one independent `source_type`, and linking specific relationship edges to the specific citation that supports them via `citation_ids`.

The Edition 1.2 target is a dataset-wide average of 80/100, up from a documented baseline of 61.3/100 (`/docs/quality-audit-2026-08.md`). This number cannot be improved by adding citations that merely exist — it requires re-reading actual sources to add real locators and excerpts, which is why closing this gap is treated as dedicated editorial work, not a mechanical pass. See `EDITORIAL_POLICY.md`'s verification requirements for the human-judgment layer this score does not and cannot replace: a citation can score well structurally while still not actually supporting the claim it's attached to, which only a reviewer checking the source itself can catch.
