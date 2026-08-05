# Search (superseded by /explorer)

This directory was reserved in Phase 1 for a future search index build step. Phase 3 built that capability inside `/workbench/explorer` instead of here: `explorer/lib/search.ts` builds a local, in-browser [MiniSearch](https://github.com/lucaong/minisearch) index from `explorer/data/generated/graph.json`, itself a *derived* artifact regenerated from `/data` on every build (`explorer/scripts/build-data.ts`) — the principle this directory originally described, just realized as part of the Explorer rather than as a standalone module.

This directory is kept only so the historical placeholder isn't silently deleted. See `/workbench/explorer/README.md` for the actual search architecture.
