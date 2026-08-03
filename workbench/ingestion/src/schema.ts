import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const INGESTION_ROOT = path.resolve(__dirname, "..");
export const WORKBENCH_ROOT = path.resolve(INGESTION_ROOT, "..");
export const DRAFTS_DIR = path.join(INGESTION_ROOT, "drafts");
export const PROMOTED_DRAFTS_DIR = path.join(DRAFTS_DIR, "promoted");
export const CANONICAL_INCIDENTS_DIR = path.join(WORKBENCH_ROOT, "data", "incidents");

function readJson(filePath: string): unknown {
  return JSON.parse(readFileSync(filePath, "utf-8"));
}

export function buildIngestionAjv() {
  const ajv = new Ajv2020({ allErrors: true, strict: true });
  addFormats(ajv);

  const commonDir = path.join(WORKBENCH_ROOT, "schemas", "common");
  for (const file of [
    "citation.schema.json",
    "relationship.schema.json",
    "history-entry.schema.json",
    "base-entity.schema.json",
  ]) {
    ajv.addSchema(readJson(path.join(commonDir, file)) as object);
  }

  const draftValidator = ajv.compile(
    readJson(path.join(INGESTION_ROOT, "schemas", "draft-incident.schema.json")) as object,
  );
  const incidentValidator = ajv.compile(
    readJson(path.join(WORKBENCH_ROOT, "schemas", "incident.schema.json")) as object,
  );

  return { ajv, draftValidator, incidentValidator };
}

export function readJsonFile<T>(filePath: string): T {
  return readJson(filePath) as T;
}
