# Search (reserved, not built in Phase 1)

This directory exists to match the module's target repository structure. Phase 1 is scoped to the data foundation only — no search index, search page, or query API is built here yet. See `/docs/architecture.md` for why.

When search is built (Phase 2+), it should be a *derived* artifact generated from `/data` — e.g. a build step that reads every validated object and produces a search index (full-text and/or graph-traversal) — never a second source of truth. Anything placed here in the future should be regeneratable from `/data` alone.
