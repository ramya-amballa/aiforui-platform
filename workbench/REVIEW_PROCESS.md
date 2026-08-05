# Review Process

This is the procedural companion to `EDITORIAL_POLICY.md` and `METHODOLOGY.md`'s "Editorial review workflow": the concrete stages a canonical object moves through, and what's expected of the people responsible for it at each stage. It applies uniformly — an object drafted by a maintainer is held to the same process as one submitted by a first-time contributor.

## Stages

### 1. Draft

An object is authored — by a contributor writing directly against a schema (`/docs/contributing.md`), or via the ingestion pipeline for Incidents (`/docs/ingestion-pipeline.md`, `npm run editorial:wizard`). At this stage: `confidence` is `Draft` or `Community`, `created_by` is set, and a `history` entry with `event: "created"` exists. A draft may be incomplete — missing citations on non-Incident/Decision types, thin relationships — but must still pass `npm run validate` structurally before it can be reviewed at all; a malformed draft isn't ready for a human reviewer's time.

### 2. Review

A maintainer checks the object against `EDITORIAL_POLICY.md` and `CITATION_POLICY.md`: do the citations actually support the claims they're attached to (not just present), are the relationships meaningfully reasoned rather than templated, is the confidence level honest, and — for Incidents specifically — does it answer the six mandatory questions in `METHODOLOGY.md`'s canonical promotion process. Review is a human judgment step; `/validators` has already confirmed the object is well-formed by this point, which is a different and lower bar than being right.

### 3. Revision

If review finds gaps, the object returns to the contributor (or the reviewing maintainer, if self-authored) for revision — a specific, actionable list of what's missing or wrong, not a rejection. Revision and review can cycle more than once; there's no limit on iterations, only a requirement that each round of feedback be concrete enough to act on.

### 4. Verification

Reaching `Reviewed` confidence requires the review above. Reaching `Verified` requires a **second, independent reviewer** — someone other than whoever performed the initial review — checking the object's sources again from scratch, not rubber-stamping the first reviewer's conclusion. This is intentionally the highest-friction step in the process, because `Verified` is the dataset's strongest claim and is meant to stay rare (see `/docs/quality-audit-2026-08.md`'s confidence-maturity numbers for the current, honest baseline).

### 5. Promotion

The object's `confidence` is updated to reflect the review it actually received, `reviewed_by` and/or `approved_by` are set to the reviewer(s)' names, and a `history` entry records the promotion with its date and reason. Promotion is the point at which an object's stated trust level and its actual review history become the same thing — see `EDITORIAL_POLICY.md`'s confidence-states section.

### 6. Publication

The object ships as part of a dataset edition per `VERSION_POLICY.md` and `RELEASE_CHECKLIST.md`. Publication is not a separate quality gate beyond promotion — an object that has been properly promoted is already fit to publish; the release checklist verifies the *dataset as a whole* (structural health, coverage, citation score) rather than re-litigating individual objects.

### 7. Retirement

An object is retired via `status: deprecated`, `superseded`, or `retracted` (`/docs/confidence-model.md`), never by deletion. Retirement follows the same review discipline as promotion: a maintainer decision, stated in `history`, with a reason (a later ruling overturned the original finding; a newer object supersedes it; the claim no longer holds). A retired object remains in the dataset and remains citable as a historical record of what the project once stated and why that changed — see `EDITORIAL_POLICY.md`'s correction policy.

## Appeal process

A contributor who disagrees with a review decision — a rejection, a confidence downgrade, a retirement — may raise the disagreement for a second maintainer's independent assessment, distinct from whoever made the original call. The appeal is resolved the same way any editorial disagreement is resolved per `GOVERNANCE_CHARTER.md`'s decision-making principles: on the evidence, not on seniority. An appeal that surfaces a source the original reviewer missed, or a citation that was in fact stronger than credited, should change the outcome; an appeal that amounts to disagreement with the neutrality or evidence standards themselves is a discussion about `EDITORIAL_POLICY.md`, not a reason to bypass it for one object. Every appeal and its resolution is recorded in the object's `history` or the relevant PR, for the same traceability reason everything else in this process is recorded.

## Reviewer responsibilities

A maintainer acting as a reviewer is expected to:

- **Actually check the sources**, not just confirm citations are present. A citation that exists but doesn't support its attached claim is a review failure, not a schema failure.
- **Disclose any conflict of interest** before reviewing content it touches, per `CONFLICT_OF_INTEREST.md`, and recuse rather than review when one exists.
- **Apply the same bar regardless of who submitted the content** — a maintainer's own draft gets the same scrutiny as an outside contributor's, including the second-reviewer requirement for `Verified`.
- **Leave a record**, not just a verdict — a `history` note explaining *why* an object was promoted, revised, or retired, so a future reader (including a future maintainer with no memory of this specific review) can reconstruct the reasoning.
- **Decline to promote rather than promote provisionally.** An object that isn't ready stays at its current confidence level; there is no "promote now, verify properly later" shortcut, since that would make the confidence field describe an aspiration rather than a fact.
