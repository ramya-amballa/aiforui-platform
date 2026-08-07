# Contributing

The AI Governance Workbench is built for community contribution from day one — that's a core project principle, not an afterthought. This is the contribution model for the data layer: every change is a pull request against `/data`, gated by `npm run validate`. Phase 2A added `/editorial` tooling (a wizard, a relationship-suggestion engine, quality checkers — see `/editorial/README.md`) to make that PR easier to get right the first time, but the model itself — PR in, validator gate, human merge — will extend, not change, once a frontend/API exists.

## Adding or editing a Decision, Pattern, Control, Evidence type, or Board Question

1. Pick the right directory under `/data` (`decisions`, `patterns`, `controls`, `evidence`, `board_questions`) and the matching schema under `/schemas`.
2. Assign the next sequential `id` for that type — e.g. if the highest existing `pattern-*` id is `PAT-004`, yours is `PAT-005`. IDs are deterministic and assigned in order, never a UUID (see `/ONTOLOGY.md`).
3. Choose a `slug` — a permanent, kebab-case, human-readable address unique within your object's entity type (e.g. `my-new-pattern`), and name your file after it (e.g. `data/patterns/my-new-pattern.json`). Once merged, don't change a slug — treat it as a stable public address.
4. Fill in every field required by the schema (see `/docs/schemas.md`), plus at least one citation if your object's `confidence` will be `Verified` or `Reviewed`.
5. Add `relationships` connecting your new object into the graph — an object with none is rejected as an orphan node (see `/docs/relationship-model.md`). Every relationship needs a `reason` (required by the schema): a short sentence explaining *why* this specific edge exists, not just that it does. If you're not sure what it should connect to, `RELATED_TO` a relevant `decision` is a reasonable starting point. Keep an eye on the outbound-relationship soft limit of 5 (hard limit 7) — the validator will warn or error if you exceed it.
6. Set `confidence` honestly — new community submissions should generally start at `Draft` or `Community`, not `Reviewed`/`Verified` (see `/docs/confidence-model.md`); a maintainer promotes it after review.
7. Add `created_by` (your name/handle) and a `history` entry with `event: "created"` — see `/schemas/common/history-entry.schema.json`.
8. Run `npm run validate` from `/workbench` and fix anything it flags before opening a pull request.

## Adding an Incident

Incidents sourced from an external event (a news article, a ruling, a regulator statement) go through the ingestion pipeline instead of being hand-written directly into `/data/incidents` — see `/docs/ingestion-pipeline.md`. Run `npm run editorial:wizard` to build the draft interactively rather than hand-writing the JSON; it validates as you go. If you're instead adding an incident you already have full, well-sourced knowledge of and don't need the draft/review scaffolding for, writing directly into `/data/incidents` following the schema is fine too; the pipeline is a convenience for the common "I read something, someone else should sanity-check it" case, not a mandatory gate.

## AI-assisted contributions

You may use AI tools to help draft content — the ingestion pipeline's `extraction_method: "ai_assisted"` field exists specifically to record this transparently. What's not permitted is AI-generated content reaching `/data` without a named human reviewer's sign-off. For Incidents, that's enforced structurally by `promote.ts` (see `/docs/ingestion-pipeline.md`). For other entity types authored directly, it's enforced by ordinary PR review — a maintainer should not merge a PR whose content nobody has actually checked against its citations.

## Extending the ontology

See "Extending the ontology" in `/docs/relationship-model.md`. In short: `/relationships/ontology.json` and `/docs/relationship-model.md` change together, and a new verb or triple should come with an explanation of the real-world relationship it's meant to capture.

## Review bar before merge

A pull request touching `/workbench/data` should:

- Pass `npm run validate` with zero issues.
- Have citations that actually support the claims they're attached to (a reviewer should spot-check at least one; `npm run editorial:citations` flags obviously weak ones).
- Not silently change the `confidence` of an existing object without explanation — a downgrade or upgrade in trust level is itself a claim that deserves a sentence in the PR description.
- Not introduce a new orphan node — `npm run editorial:health`'s Zero-Orphan Invariant check will catch this, but it's worth confirming before pushing.

## What Phase 1 does not yet support

There is no web UI for contribution yet — everything above happens via editing JSON files and opening a GitHub pull request. See `/docs/architecture.md` for why that's a deliberate Phase 1 scope decision, not an oversight.
