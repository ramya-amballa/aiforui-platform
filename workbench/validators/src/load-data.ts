import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";
import { DATA_DIR } from "./load-schemas.js";
import { DATA_DIR_BY_TYPE, ENTITY_TYPES, type CanonicalEntity, type LoadedEntity } from "./types.js";

export interface RawLoadResult {
  entities: LoadedEntity[];
  parseErrors: { filePath: string; message: string }[];
}

export function loadAllData(): RawLoadResult {
  const entities: LoadedEntity[] = [];
  const parseErrors: RawLoadResult["parseErrors"] = [];

  for (const entityType of ENTITY_TYPES) {
    const dir = path.join(DATA_DIR, DATA_DIR_BY_TYPE[entityType]);
    let files: string[];
    try {
      files = readdirSync(dir).filter((f) => f.endsWith(".json"));
    } catch {
      continue;
    }

    for (const file of files) {
      const filePath = path.join(dir, file);
      const raw = readFileSync(filePath, "utf-8");
      try {
        const data = JSON.parse(raw) as CanonicalEntity;
        entities.push({ entityType, filePath, data });
      } catch (err) {
        parseErrors.push({
          filePath,
          message: err instanceof Error ? err.message : String(err),
        });
      }
    }
  }

  return { entities, parseErrors };
}
