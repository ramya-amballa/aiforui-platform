export const DEFAULT_PAGE_SIZE = 9;

export interface PaginationResult<T> {
  items: T[];
  currentPage: number;
  totalPages: number;
  totalItems: number;
}

/**
 * Pure slice-based pagination over an in-memory array. The listing
 * pages that call this only know about `items`/`currentPage`/`totalPages`;
 * when content/*.ts is eventually backed by a CMS or database query
 * with LIMIT/OFFSET, only this function's internals change.
 */
export function paginate<T>(allItems: T[], page: number, pageSize: number = DEFAULT_PAGE_SIZE): PaginationResult<T> {
  const totalItems = allItems.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const currentPage = Math.min(Math.max(1, page), totalPages);
  const start = (currentPage - 1) * pageSize;

  return {
    items: allItems.slice(start, start + pageSize),
    currentPage,
    totalPages,
    totalItems,
  };
}

/** Reads a 1-indexed `page` value out of a Next.js searchParams object. */
export function parsePage(searchParams: Record<string, string | string[] | undefined>): number {
  const raw = searchParams.page;
  const value = Array.isArray(raw) ? raw[0] : raw;
  const parsed = Number.parseInt(value ?? "1", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1;
}

/** Reads a single-value filter param, treating "all" / undefined as "no filter". */
export function parseFilter(searchParams: Record<string, string | string[] | undefined>, key: string): string | undefined {
  const raw = searchParams[key];
  const value = Array.isArray(raw) ? raw[0] : raw;
  return value && value !== "all" ? value : undefined;
}
