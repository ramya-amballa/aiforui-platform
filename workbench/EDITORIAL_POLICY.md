# Editorial Policy

This document governs editorial conduct on the AI Governance Workbench: what standard content must meet before it becomes canonical, and how the project handles being wrong. It applies to every canonical object in `/data`, regardless of who drafted it or how.

## Editorial principles

1. **Evidence before inclusion.** A claim enters the dataset because a source supports it, not because it is plausible, widely believed, or would be a useful data point to have. See "Evidence standards" below.
2. **Precision over completeness.** A smaller, accurate graph is preferable to a larger one padded with plausible-sounding connections. An incident that cannot yet answer what governance decision it involved, what evidence demonstrates that decision, and what confidence should be assigned is not ready for canonical status, regardless of how well-known the incident is.
3. **Every claim is attributable.** A reader should always be able to determine what evidence supports a given fact and how confident the project is in it, without having to trust the project's authority alone.
4. **Structure does not substitute for judgment.** Passing schema validation means an object is well-formed, not that it is correct. Structural validity is necessary; it is never sufficient.
5. **The dataset is corrigible.** Being wrong and correcting it openly is treated as normal editorial function, not failure — see "Correction policy" below.

## Evidence standards

A canonical claim must be traceable to a source a reader can independently check (see `CITATION_POLICY.md` for what counts as an acceptable source). "Evidence" in this dataset means something specific: an *observable* fact — an event that occurred, a document that was published, a ruling that was issued — not an inference, prediction, or opinion about what an organization was probably thinking. A `root_cause` on an Incident or a `decision_rationale` on a Decision should be traceable to what the sources actually establish, with any inferential step the contributor made stated as such, not blended silently into the factual claim.

## Verification requirements

- **Every Incident and Decision requires at least one citation, regardless of confidence.** Enforced structurally by `/validators` — see `CITATION_POLICY.md` and `/docs/citation-model.md`.
- **Objects claiming `Verified` or `Reviewed` confidence require at least one citation, and that citation must actually support the specific claim it's attached to.** A citation that is topically related but doesn't establish the claim it's attached to does not satisfy this requirement, even though the schema cannot detect that automatically — this is what human review exists to catch.
- **A reviewer verifies a citation by checking it, not by trusting its presence.** "Has a citation" and "the citation supports the claim" are different questions; only a human reviewer answers the second. See `REVIEW_PROCESS.md`.
- **A relationship's `reason` is itself subject to verification.** A generic or templated reason (see the Repository Quality Audit's "relationship rationale" findings, `/docs/quality-audit-2026-08.md`) is not a fabrication, but it is a lower editorial standard than an incident-specific one, and reviewers should treat closing that gap as legitimate editorial work, not cosmetic polish.

## Confidence states

The dataset uses five confidence states — `Verified`, `Reviewed`, `Draft`, `Community`, `Archived` — defined precisely in `/docs/confidence-model.md`. Editorially, the governing rule is simple: **confidence is asserted honestly, not aspirationally.** An object is `Community` or `Draft` until it has actually been reviewed against its sources by a maintainer, and `Verified` only after independent, second-party corroboration — not because the content seems solid, but because someone besides its author checked it and can be named as having done so (`reviewed_by`, `approved_by`, `history`).

## Citation expectations

See `CITATION_POLICY.md` for the full policy. In brief: citations should point to primary sources wherever one exists (the regulator's own order, the court's own judgment, the statute's own text), should include a `locator` and `excerpt` wherever the source permits it rather than citing a document as a whole, and should not be duplicated or restated as if independent corroboration when they in fact trace back to the same original reporting.

## Correction policy

Errors are expected in a dataset of this size and are corrected in the open, not quietly.

- **Anyone may flag a suspected error** — a factual mistake, a broken citation, a mischaracterized ruling — via the same pull-request path used for any other contribution, or by raising it for a maintainer to action.
- **A correction is itself a canonical edit**: it goes through the same review path as new content, bumps the object's `version`, and adds a `history` entry stating what was wrong and what changed. The dataset's history is append-only — a correction is recorded, not retroactively erased, so the record of "we said X, then corrected it to Y, on this date, because Z" survives.
- **A material factual error discovered after publication is corrected as soon as it is confirmed**, independent of any release schedule. Editions are snapshots of the dataset's *content* (see `VERSION_POLICY.md`); they are not a reason to leave a known error live until the next one ships.
- **A correction that changes a claim's substance is distinct from a `status: retracted`.** A correction fixes a specific inaccuracy in an otherwise sound record. Retraction is for when the object's core claim no longer holds at all — e.g., a ruling was overturned on appeal, and the incident's original framing is no longer defensible even with edits.

## Update policy

An object's content can change after it is published; its `id` and `slug` never do (`ONTOLOGY.md`). Substantive edits — anything beyond fixing a typo — bump `version` and add a `history` entry naming the actor, date, and reason. Non-substantive edits (spelling, formatting) are held to the same discipline: see the Repository Quality Audit (`/docs/quality-audit-2026-08.md`) for an example of a dataset-wide mechanical update handled this way. An object's `confidence` can move in either direction — a `Verified` record can be downgraded if a source is later found to be weaker than believed — and a downgrade is never treated as embarrassing; it is the confidence model doing its job.

## Neutrality policy

The Workbench takes a position on what happened and what the evidence supports. It does not take a position on contested policy questions where reasonable governance practitioners genuinely disagree, and it does not rank, endorse, or criticize vendors, products, or organizations beyond what the cited evidence establishes about a specific, dated incident.

Concretely:

- Incident descriptions state what is documented to have happened, sourced, without editorializing about whether the organization involved is generally trustworthy or well-run.
- A Decision, Pattern, or Control is included because it is a defensible governance response *to a specific documented incident or requirement*, not because the project judges it to be the single best practice among competing approaches. Where alternatives exist, `alternatives_considered` (on Decisions) exists precisely to show the reasoning was not one-sided.
- Framework Controls are mapped only where genuinely and directly applicable (see `EDITORIAL_POLICY.md`'s sibling, `CITATION_POLICY.md`, and the Phase 3 editorial discipline in `VISION.md`) — never inflated to make the dataset appear more comprehensive than the evidence supports.
- Tags, categorizations, and severity ratings reflect what sources report, not the project's own risk appetite.

## Independence statement

The AI Governance Workbench is not sponsored by, and does not accept payment, data-access preference, or editorial influence from, any vendor, regulator, law firm, or organization named in its dataset. It is maintained as a public reference, free to use, with no commercial product built on top of it. See `CONFLICT_OF_INTEREST.md` for how a maintainer's own affiliations are disclosed and managed when they intersect with content under review.
