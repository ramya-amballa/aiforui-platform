# Ingestion Pipeline

```
News Article -> Draft Incident -> Human Review -> Validated Incident -> Graph Update
```

This is the only sanctioned path by which content sourced from an external event (starting with, in Phase 1, news reporting about AI incidents) enters the canonical dataset. It exists to make the boundary between "someone/something suggested this" and "this is canonical knowledge" a structural fact, not a matter of trust — directly implementing the project principle that no AI-generated content enters the canonical dataset without human review.

## The five stages

1. **News Article.** A contributor (human or AI-assisted) finds a source — a news article, a tribunal ruling, a regulator statement — describing an AI-related incident.

2. **Draft Incident.** The contributor captures it as a JSON file conforming to `/ingestion/schemas/draft-incident.schema.json` and places it in `/ingestion/drafts/`. This schema is deliberately **separate** from `/schemas/incident.schema.json`: it requires a `source` block (what was read and when), a verbatim `raw_excerpt` (the ground truth the draft was built from), an `extraction_method` (`human` or `ai_assisted`, recorded for transparency), an optional `captured_by` (who captured the draft, carried through to the canonical record's `created_by`), a `suggested_incident` block (the candidate content — title, description, dates, harm types, etc.), and a `human_review` block that starts at `human_review.status: "pending"`. A draft's own `id` (`draft-incident-...`) is just a working handle — it is never the canonical `INC-###` id, which is assigned at promotion time.

   A draft in this state is **not canonical**: nothing in `/data` references it, the main validator (`/validators`) never reads `/ingestion/drafts`, and it carries no weight until reviewed.

3. **Human Review.** A qualified human reads the draft against its source, edits `suggested_incident` as needed, and either sets `human_review.status` to `"approved"` (filling in `reviewer` and `confidence_assigned`), `"rejected"`, or `"needs_changes"`. This step cannot be automated away — `npm run ingest:promote` (see below) refuses to run without a completed, approved review.

4. **Validated Incident.** Running `npm run ingest:promote -- <path-to-draft.json>` (from `/workbench`, see `/ingestion/src/promote.ts`):
   - Re-validates the draft against `draft-incident.schema.json`.
   - Hard-stops unless `human_review.status === "approved"`, `human_review.reviewer` is set, and `human_review.confidence_assigned` is set.
   - Assigns the next sequential canonical id (scans `/data/incidents` for the highest existing `INC-###` and increments) and derives a `slug` from the draft's title (kebab-cased, de-duplicated against existing incident slugs by appending `-2`, `-3`, ... if needed).
   - Mechanically builds a canonical `Incident` object: `id`/`slug` as above, `status: "active"`, `confidence` = the reviewer's `confidence_assigned`, `created_by` = `captured_by` (or the reviewer, if no capturer was recorded), `reviewed_by`/`approved_by` = the reviewer, a `history` array with `created` and `approved` entries, one citation built from the draft's `source` + `raw_excerpt`, and `suggested_incident`'s fields mapped across. That object is then validated against `/schemas/incident.schema.json`. If it doesn't pass, nothing is written — an invalid object never reaches `/data`.
   - Writes the result to `/data/incidents/<slug>.json`.
   - Moves (does not delete) the source draft into `/ingestion/drafts/promoted/`, preserving the exact draft and review decision that produced the canonical record, so the new incident stays traceable back to it.

   `relationships` on the newly promoted incident are always left empty. Deciding what a new incident connects to (which decision it should motivate, which board question it raises) is an editorial judgement call, not something a mechanical script should guess at — see `/docs/relationship-model.md`.

5. **Graph Update.** A human adds the appropriate `relationships` to the new incident (and/or to the objects it should connect to) by editing the file directly — each edge needs a `reason` (see `/docs/relationship-model.md`) — then runs `npm run validate` to confirm the dataset — now including the new incident and its relationships — is internally consistent before opening/merging the pull request.

## Why Incidents specifically get a pipeline, and other entity types don't

`Incident` is the entity type most naturally sourced from a single external event a contributor stumbles across (a news article, a ruling). `Decision`, `Pattern`, `Control`, `Evidence`, and `Board Question` are more often authored or curated judgement calls — a contributor proposing a decision, documenting a pattern they've seen work, or mapping a framework control — where a "draft capture -> promote" mechanical step wouldn't add much over just writing the canonical JSON directly and opening a PR (see `/docs/contributing.md`). Nothing prevents extending the same draft/promote pattern to another entity type later if a similar bulk-capture need shows up (e.g. bulk-importing framework controls from a published standard); Phase 1 scopes it to Incidents because that's the concrete pipeline described in the brief.

## Commands

Run from `/workbench` (after `npm install`):

```sh
npm run ingest:validate-draft -- ingestion/drafts/<file>.json
npm run ingest:promote -- ingestion/drafts/<file>.json
npm run validate
```
