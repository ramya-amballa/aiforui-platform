import MiniSearch from "minisearch";
import { graph } from "./data";
import type { SearchDocument } from "./types";

let index: MiniSearch<SearchDocument> | null = null;

export function getSearchIndex(): MiniSearch<SearchDocument> {
  if (index) return index;
  index = new MiniSearch<SearchDocument>({
    fields: ["title", "description", "tags", "jurisdiction", "frameworks", "extra", "id"],
    storeFields: ["id", "entity_type", "slug", "title", "description", "tags", "jurisdiction", "frameworks", "status", "confidence"],
    searchOptions: {
      boost: { title: 3, tags: 2, id: 4 },
      prefix: true,
      fuzzy: 0.15,
    },
  });
  index.addAll(graph.search_documents);
  return index;
}
