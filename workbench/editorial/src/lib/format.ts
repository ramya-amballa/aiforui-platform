export function countBy<T>(items: T[], key: (item: T) => string[] | string | undefined): Map<string, number> {
  const counts = new Map<string, number>();
  for (const item of items) {
    const raw = key(item);
    const values = Array.isArray(raw) ? raw : raw !== undefined ? [raw] : [];
    for (const value of values) {
      counts.set(value, (counts.get(value) ?? 0) + 1);
    }
  }
  return counts;
}

export function sortedEntries(counts: Map<string, number>): [string, number][] {
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

/** Renders a GitHub-Flavored-Markdown table that also reads cleanly as plain terminal text. */
export function markdownTable(headers: string[], rows: (string | number)[][]): string {
  const line = (cells: (string | number)[]) => `| ${cells.map(String).join(" | ")} |`;
  const separator = `| ${headers.map(() => "---").join(" | ")} |`;
  return [line(headers), separator, ...rows.map(line)].join("\n");
}
