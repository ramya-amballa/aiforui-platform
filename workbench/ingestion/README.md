# Ingestion

Mechanical tooling for the pipeline documented in [`/docs/ingestion-pipeline.md`](../docs/ingestion-pipeline.md):

```
News Article -> Draft Incident -> Human Review -> Validated Incident -> Graph Update
```

- `schemas/draft-incident.schema.json` — the (looser, non-canonical) schema a draft must satisfy.
- `drafts/` — where captured drafts live until they're promoted. Never treated as canonical; never referenced by relationships in `/data`.
- `src/validate-draft.ts` — validates a single draft file against the draft schema.
- `src/promote.ts` — the only path from a draft into `/data/incidents`. It refuses to run unless `human_review.status` is `"approved"`, a `reviewer` and `confidence_assigned` are recorded, and the resulting object passes `incident.schema.json`. It assigns the next sequential `INC-###` id and a de-duplicated slug automatically. It never invents relationships — those are added by hand afterwards, each with a `reason`.

## Commands

Run from `/workbench`:

```sh
npm run ingest:validate-draft -- ingestion/drafts/draft-incident-my-example.json
npm run ingest:promote -- ingestion/drafts/draft-incident-my-example.json
npm run validate
```

`ingest:promote` only ever writes a new file into `/data/incidents` — it does not modify existing canonical records, and it archives the source draft into `drafts/promoted/` rather than deleting it, so every canonical incident stays traceable back to the draft and review decision that produced it.
