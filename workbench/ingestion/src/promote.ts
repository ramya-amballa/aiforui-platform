import { existsSync, mkdirSync, renameSync, writeFileSync } from "node:fs";
import path from "node:path";
import { buildIngestionAjv, readJsonFile, PROMOTED_DRAFTS_DIR, CANONICAL_INCIDENTS_DIR } from "./schema.js";
import type { DraftIncident } from "./types.js";
import type { CanonicalEntity } from "../../validators/src/types.js";

function fail(message: string): never {
  console.error(`✘ ${message}`);
  process.exit(1);
}

function main(): void {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error("Usage: npm run ingest:promote -- <path-to-draft.json>");
    process.exit(2);
  }

  const { draftValidator, incidentValidator } = buildIngestionAjv();
  const draft = readJsonFile<DraftIncident>(filePath);

  if (!draftValidator(draft)) {
    console.error(`✘ ${filePath} failed draft-incident schema validation:\n`);
    for (const err of draftValidator.errors ?? []) {
      console.error(`  ${err.instancePath || "(root)"} ${err.message ?? "is invalid"}`);
    }
    process.exit(1);
  }

  const { human_review, suggested_incident, source, raw_excerpt } = draft;

  if (human_review.status !== "approved") {
    fail(
      `Draft '${draft.id}' has human_review.status = '${human_review.status}', not 'approved'. ` +
        `Only a human reviewer can move a draft to 'approved' — this script will not do it for you.`,
    );
  }
  if (!human_review.reviewer) {
    fail(`Draft '${draft.id}' is approved but has no human_review.reviewer recorded. Refusing to promote.`);
  }
  if (!human_review.confidence_assigned) {
    fail(`Draft '${draft.id}' is approved but has no human_review.confidence_assigned. Refusing to promote.`);
  }

  const canonicalId = `incident-${draft.id.replace(/^draft-incident-/, "")}`;
  const outPath = path.join(CANONICAL_INCIDENTS_DIR, `${canonicalId}.json`);
  if (existsSync(outPath)) {
    fail(`Canonical incident '${canonicalId}' already exists at ${outPath}. Refusing to overwrite.`);
  }

  const today = new Date().toISOString().slice(0, 10);

  const canonical: CanonicalEntity = {
    id: canonicalId,
    title: suggested_incident.title,
    description: suggested_incident.description,
    version: "1.0.0",
    status: "active",
    confidence: human_review.confidence_assigned,
    created_date: today,
    updated_date: today,
    tags: suggested_incident.tags ?? [],
    citations: [
      {
        id: "cite-source",
        source_type: source.source_type,
        title: source.title,
        publisher: source.publisher,
        ...(source.url ? { url: source.url } : {}),
        ...(source.published_date ? { publication_date: source.published_date } : {}),
        accessed_date: source.retrieved_date,
        excerpt: raw_excerpt,
      },
    ],
    // Relationships are deliberately left empty: connecting a newly promoted
    // incident into the graph is an editorial judgement call, not something
    // this mechanical script should infer. Add them in a follow-up edit,
    // then re-run `npm run validate`.
    relationships: [],
    occurred_date: suggested_incident.occurred_date,
    ...(suggested_incident.organizations_involved ? { organizations_involved: suggested_incident.organizations_involved } : {}),
    ...(suggested_incident.harm_types ? { harm_types: suggested_incident.harm_types } : {}),
    ...(suggested_incident.ai_system_category ? { ai_system_category: suggested_incident.ai_system_category } : {}),
    ...(suggested_incident.jurisdiction ? { jurisdiction: suggested_incident.jurisdiction } : {}),
    ...(suggested_incident.severity ? { severity: suggested_incident.severity } : {}),
    ...(suggested_incident.root_cause ? { root_cause: suggested_incident.root_cause } : {}),
  };

  if (!incidentValidator(canonical)) {
    console.error(`✘ Generated canonical incident failed incident.schema.json validation — not written:\n`);
    for (const err of incidentValidator.errors ?? []) {
      console.error(`  ${err.instancePath || "(root)"} ${err.message ?? "is invalid"}`);
    }
    process.exit(1);
  }

  mkdirSync(CANONICAL_INCIDENTS_DIR, { recursive: true });
  writeFileSync(outPath, JSON.stringify(canonical, null, 2) + "\n", "utf-8");

  mkdirSync(PROMOTED_DRAFTS_DIR, { recursive: true });
  const promotedDraftPath = path.join(PROMOTED_DRAFTS_DIR, path.basename(filePath));
  renameSync(path.resolve(filePath), promotedDraftPath);

  console.log(`✔ Promoted '${draft.id}' -> ${path.relative(process.cwd(), outPath)}`);
  console.log(`  Draft archived to ${path.relative(process.cwd(), promotedDraftPath)} for traceability.`);
  console.log(`  Reminder: relationships were left empty. Add them by hand, then run 'npm run validate'.`);
}

main();
