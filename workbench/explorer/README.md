# Explorer

The public, interactive interface for the AI Governance Workbench knowledge graph. Think MDN Web Docs, Refactoring.Guru, or the MITRE ATT&CK Navigator — a practitioner reference, not a documentation portal or marketing site.

This is a **view**, not a second source of truth. Per the Canonical Principle (`/ONTOLOGY.md`): "The Knowledge Graph is the product. Everything else is a view." The Explorer never edits `/workbench/data` — it only reads it, at build time, and renders it.

## Information architecture

```
/                          Homepage: hero, live stats, the 6 entity cards, example queries
/decisions, /incidents,
/patterns, /controls,
/evidence, /board-questions  Browse pages: filter + sort + search over one entity type, no pagination
/decisions/[slug]  etc.     Node detail pages: an executive briefing on one canonical object
/frameworks                 Framework index (NIST AI RMF, EU AI Act, GDPR, ...)
/frameworks/[slug]          What maps to one framework: controls, decisions, incidents, evidence, board questions
/graph                      Supplemental full-graph visualization
```

Every route is statically generated (`next build && next export`, `output: "export"` in `next.config.mjs`). There is no backend, no database, and no runtime API — the entire site is static HTML/JS/CSS that could be served from any CDN or `file://`.

## Data architecture

`scripts/build-data.ts` is the *only* place the Explorer reads `/workbench/data` and `/workbench/relationships/ontology.json`. It runs as a `predev`/`prebuild` npm hook (see `package.json`) and emits `data/generated/graph.json` — nodes with pre-resolved inbound/outbound relationships, derived framework groupings, and flattened search documents. That file is gitignored: it is always regenerated from canonical data, never hand-edited, and never a second source of truth (the same rule `/workbench/search/README.md` states for any future search index). Every page imports typed accessors from `lib/data.ts`, never the raw JSON directly.

If the canonical dataset changes, the Explorer's content changes automatically on the next build — there is nothing to keep in sync by hand.

## Search architecture

Universal search (`⌘K` desktop, search button mobile) is entirely local: `lib/search.ts` builds a [MiniSearch](https://github.com/lucaong/minisearch) index client-side, once, from `graph.search_documents` (title, description, tags, jurisdiction, frameworks, and type-specific text, per object). No network request, no backend, no third-party search service. Results are grouped by entity type, ranked, keyboard-navigable, and every result is a direct link to that node's detail page. This satisfies "no backend, instant, local indexed search" without introducing any new infrastructure.

## Graph visualization architecture

`/graph` (`components/GraphView.tsx`) lays out the full graph once, client-side, using `d3-force` run headlessly for a fixed number of ticks (no animation loop — the layout settles before the first paint, consistent with the "no animations" design direction). Rendering is a single `<canvas>` element with hand-rolled pan (drag), zoom (wheel), hover-to-highlight-neighbors, and click-to-navigate, chosen over a graph-visualization library to keep the bundle small and the interaction model fully under our control. Filters (entity type, confidence, framework) hide/dim nodes and edges without re-running the simulation, so filtering stays instant. The graph is explicitly supplemental — search is the primary way to find something specific; the graph is for seeing how things connect.

## Filtering architecture

Browse pages (`components/BrowseView.tsx`) compute facets (tags, jurisdiction, framework, confidence, status) from whatever entity list is passed in, filter and sort entirely client-side (datasets here are small — at most 35 objects per type — so there is no pagination, per the product brief), and mirror filter state into the URL query string (`lib/filter-url.ts`) via `history.replaceState`, so a filtered view is always a shareable, deep-linkable link (e.g. answering "show every incident involving human oversight failures" as a URL, not just a search).

## Relationship Explorer

Every relationship is clickable everywhere it appears: the compact reference cards in each detail page's "Linked X" sections (`components/RelSection.tsx`), the dense audit-style `Relationship reasoning` table that lists every edge with its `reason` and `confidence` verbatim (`components/RelationshipReasoning.tsx`), and the wayfinding strip at the top of every detail page (`components/RelationshipChain.tsx`) that shows, at a glance, which of the other five entity types the current node connects to and jumps straight to that section.

## Executive Export

Every node page has **Export Markdown** and **Print / PDF** actions (`components/ExportButtons.tsx`). Markdown export (`lib/markdown.ts`) is a pure, deterministic template over the node's already-canonical fields — no AI generation, no network call, byte-for-byte reproducible from the same data. Print uses a dedicated `@media print` stylesheet (`app/globals.css`) that hides navigation/chrome and lays out the remaining content for a clean PDF via the browser's native print-to-PDF.

## Design language

Bloomberg Terminal meets Linear meets Stripe Docs: dense, quiet, high information-per-pixel, restrained color (a neutral gray scale plus one accent, with semantic color reserved for confidence/status/severity badges and per-entity-type identity), no gradients, no decorative animation, no marketing illustration. See `tailwind.config.ts` for the token set.

## Running locally

```
npm install
npm run dev      # regenerates data, starts the dev server
npm run build    # regenerates data, produces a static export in /out
npm run typecheck
npm run lint
```
