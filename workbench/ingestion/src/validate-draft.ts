import { buildIngestionAjv, readJsonFile } from "./schema.js";

function main(): void {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error("Usage: npm run ingest:validate-draft -- <path-to-draft.json>");
    process.exit(2);
  }

  const { draftValidator } = buildIngestionAjv();
  const draft = readJsonFile<unknown>(filePath);

  if (draftValidator(draft)) {
    console.log(`✔ ${filePath} is a schema-valid draft incident.`);
    process.exit(0);
  }

  console.error(`✘ ${filePath} failed draft-incident schema validation:\n`);
  for (const err of draftValidator.errors ?? []) {
    console.error(`  ${err.instancePath || "(root)"} ${err.message ?? "is invalid"}`);
  }
  process.exit(1);
}

main();
