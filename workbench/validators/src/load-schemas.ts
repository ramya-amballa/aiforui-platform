import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import type { ValidateFunction } from "ajv";
import { ENTITY_TYPES, SCHEMA_FILE_BY_TYPE, type EntityType } from "./types.js";

type Ajv = InstanceType<typeof Ajv2020>;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const WORKBENCH_ROOT = path.resolve(__dirname, "..", "..");
export const SCHEMAS_DIR = path.join(WORKBENCH_ROOT, "schemas");
export const DATA_DIR = path.join(WORKBENCH_ROOT, "data");
export const RELATIONSHIPS_DIR = path.join(WORKBENCH_ROOT, "relationships");

function readJson(filePath: string): unknown {
  return JSON.parse(readFileSync(filePath, "utf-8"));
}

export function buildAjv(): Ajv {
  const ajv = new Ajv2020({ allErrors: true, strict: true });
  addFormats(ajv);

  const commonDir = path.join(SCHEMAS_DIR, "common");
  for (const file of [
    "citation.schema.json",
    "relationship.schema.json",
    "history-entry.schema.json",
    "base-entity.schema.json",
  ]) {
    ajv.addSchema(readJson(path.join(commonDir, file)) as object);
  }

  return ajv;
}

export function compileEntityValidators(ajv: Ajv): Record<EntityType, ValidateFunction> {
  const validators: Partial<Record<EntityType, ValidateFunction>> = {};
  for (const entityType of ENTITY_TYPES) {
    const schemaPath = path.join(SCHEMAS_DIR, SCHEMA_FILE_BY_TYPE[entityType]);
    const schema = readJson(schemaPath) as object;
    validators[entityType] = ajv.compile(schema);
  }
  return validators as Record<EntityType, ValidateFunction>;
}

export function loadOntology() {
  return readJson(path.join(RELATIONSHIPS_DIR, "ontology.json")) as import("./types.js").Ontology;
}
