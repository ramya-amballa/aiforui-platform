# Release Checklist

Every dataset edition — minor or major, per `VERSION_POLICY.md` — passes this checklist in full before publication. It is deterministic by design: every item is either a command that exits 0 or a document that exists and is up to date. Nothing on this list is a judgment call left for release day; judgment calls (is this incident ready, does this citation actually support its claim) happen earlier, in `REVIEW_PROCESS.md`, on individual objects, before an edition is ever assembled.

Run every command from `/workbench` unless noted otherwise.

## 1. Validation

```sh
npm run validate
```

Must exit 0 with zero errors across every object in `/data`. This is the non-negotiable floor — a release does not proceed past this step under any circumstance, including a deadline. Structural warnings (e.g., approaching the soft outbound-relationship limit) do not block release but should be reviewed.

## 2. Typecheck

```sh
npm run typecheck
cd explorer && npm run typecheck && npm run lint
```

Confirms the validator, ingestion pipeline, editorial tooling, and Explorer all still compile cleanly against the current TypeScript. A release should never ship with a type error anywhere in the toolchain that produced it.

## 3. Repository audit

```sh
npm run editorial:audit
```

Zero `ERROR`-severity findings is required. `WARNING`-severity findings should be resolved before release if they are mechanically fixable (naming, terminology, tag hygiene — see `/docs/quality-audit-2026-08.md` for the precedent); a `WARNING` that isn't mechanically fixable (e.g., citation depth, which requires research) is acceptable to carry forward *only if it is already documented* in the edition's release notes as a known, tracked gap — never silently.

## 4. Zero orphans

```sh
npm run editorial:health
```

Confirms the Zero-Orphan Invariant: every object has at least one relationship. This is a hard gate — `editorial:health` exits non-zero if any orphan exists, independent of `validate`'s own check, and a release cannot ship with either check failing.

## 5. Coverage metrics

```sh
npm run editorial:coverage
```

Review the Coverage Matrix (per-entity-type connectivity) and the harm-type/jurisdiction/framework breakdowns. Nothing here is a hard pass/fail gate, but any newly-introduced sparse area should be a deliberate, acknowledged tradeoff — stated in the edition's release notes under "known gaps" — not an unnoticed side effect of what got added.

## 6. Citation score

```sh
npm run editorial:citations
npm run editorial:audit
```

Record the dataset-wide average citation completeness score in the release notes, and compare it against the previous edition's figure and the standing Edition 1.2 target of 80/100 (`CITATION_POLICY.md`). A release does not need to hit the target to ship, but the number must be reported honestly every time, trending in the stated direction, not omitted when it's unflattering.

## 7. Editorial review

Confirm, for every object newly promoted or added since the last edition:

- It went through the stages in `REVIEW_PROCESS.md` appropriate to its current confidence level.
- Its `confidence`, `reviewed_by`/`approved_by`, and `history` are consistent with the review it actually received.
- Any Incident added answers the six mandatory questions in `METHODOLOGY.md`'s canonical promotion process.

## 8. Release notes

A new file under `/docs/releases/` (or an update to the pending edition's notes) documenting, per `METHODOLOGY.md`'s release methodology: new incidents and objects added (with IDs), coverage improvements, editorial or structural changes, the citation-score figure from step 6, and known gaps — carried forward honestly, not papered over. Once published, a release note is never rewritten to read differently than it did at release time; corrections to content happen in the objects themselves per `EDITORIAL_POLICY.md`.

## 9. Screenshots

For any release that includes an Explorer change (a permitted bug fix or performance improvement under the current architectural freeze — see `VISION.md`, `ONTOLOGY.md`): browser-verified screenshots of the affected pages, confirming the change renders correctly before and doesn't regress unrelated pages. Not required for a data-only edition that doesn't touch `/explorer`.

## 10. Version tags

- Every object added or edited since the last edition has a correctly bumped `version` and a corresponding `history` entry (spot-check, since `validate` does not currently enforce this mechanically — see `VERSION_POLICY.md`'s object-version section).
- `/docs/releases/README.md`'s edition index table is updated with the new edition's status and date.
- The edition itself is named consistently with `VERSION_POLICY.md`'s numbering rules (minor vs. major).

## 11. Documentation completeness

Run (or re-run) the Repository Readiness Audit process described in `/docs/quality-audit-2026-08.md`'s sibling readiness reports: confirm every cross-link between governance documents still resolves, no document contradicts `ONTOLOGY.md`, and no reference to object/incident counts, edition numbers, or phase status anywhere in `/docs`, `README.md`, `ONTOLOGY.md`, or `VISION.md` is stale relative to the edition being published. A release does not ship with documentation that describes a prior edition's numbers as current.

## Sign-off

An edition is ready to publish only when every item above is either passing or has a stated, deliberate exception recorded in that edition's release notes. "Ready" is a checklist being complete, not a feeling — the same standard `METHODOLOGY.md` applies to individual objects applies here to the dataset as a whole.
