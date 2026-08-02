# ADR 0001: Artifact Registry as an additive shadow index, not a system of record

**Status:** Accepted

## Context

AOS's output has no lineage, versioning, or queryable metadata layer —
every cross-employee reference is a hardcoded file path, and finding
"what did employee X produce, from what, and how confident is it"
requires reading the file directly and knowing its shape by
convention. `architecture-v2/aos-v2-architecture.md` named this as one
of four structural limits the 22-employee design hits at scale, citing
a real, concrete example: this week's output-path consolidation
touched roughly 40 files precisely because every cross-employee
reference to another employee's output was an independent, hardcoded
string.

A second model's enterprise roadmap (evaluated in
`architecture-v2/gemini-enterprise-roadmap-critique.md`) proposed a
Typed Artifact Registry, and separately proposed backing it with
Postgres and a JSON-LD sidecar. The critique's verdict was mixed: a
registry is genuinely worth building now, in a specific, narrow form;
a networked database and a linked-data sidecar are not — they solve
problems this system does not have, at an operational cost its
one-founder operating model cannot absorb.

## Decision

Build the Artifact Registry as a **read-only shadow index**: a script
(`registry_builder.py`) that scans `AOS/output/` and writes one JSON
index file, rebuilt from scratch on every run. The index stores
metadata *about* artifacts (ID, employee, type, produced date, content
hash, coarse-grained lineage, opportunistic confidence, advisory
validation flags) — never a copy of an artifact's actual content.
Markdown and JSON files under `output/` remain the sole canonical,
human-readable artifacts.

Two employees — Company 360 and CEO Advisor — gained a read-only,
optional integration: they read the registry's own index file exactly
as they read any other employee's `*-feed.json`, never by importing
`registry_query.py` as a Python module. Every existing call site of
every function touched keeps a valid default and continues to behave
exactly as before if the registry has never been built.

## Alternatives Considered

- **A networked database (Postgres) as the registry's backing store.**
  Rejected for the current single-founder, single-tenant deployment:
  it introduces a running service, credentials, backup, and a new "is
  the database up" failure mode, for a query-performance problem that
  does not exist at today's artifact volume. Also breaks the property
  that git *is* the audit trail — a database sitting outside git has
  no equivalent auditability unless it's exported back into git, which
  just reintroduces the file-based approach with an extra moving part.
- **A JSON-LD sidecar with dual-write.** Rejected outright. JSON-LD
  solves cross-organization vocabulary disambiguation on the open
  semantic web — a problem this single-practice tool does not have,
  even under a future multi-firm licensing model. Dual-write would
  also introduce a durable new bug class (the sidecar and the primary
  drifting out of sync) for no identified benefit.
- **Employees importing `registry_query.py` directly.** Considered and
  rejected: no employee today imports another component's Python
  module in-process — every cross-employee reference is a file read.
  Preserving that isolation (an explicit invariant in
  `ARCHITECTURE-CONSTITUTION.md` Section 3) was judged more valuable
  than the small convenience of a typed Python API, so Company 360 and
  CEO Advisor read the registry's index file exactly like a feed.
- **True per-instance data lineage** (which specific upstream artifact
  version fed this exact file). Rejected for this phase: it would
  require every employee to declare what it read at write time,
  violating "existing employees continue to function unchanged."
  Lineage here is intentionally coarser — employee-level, derived from
  the Orchestrator's own `dependsOn` graph — an honest boundary rather
  than a false promise of precision the system can't back up yet.

## Consequences

- The registry can be deleted and rebuilt at any time with zero data
  loss, because nothing in it is a system of record — verified by a
  dedicated test (`test_rebuilding_from_scratch_reproduces_identical_ids`).
- Adding a 23rd, 30th, or 50th employee requires no registry change:
  any file under `output/<employee>/` is picked up automatically by
  the same path-convention rules.
- The registry is not yet wired into the daily Orchestrator run —
  that is an orchestration change, explicitly deferred (see this
  phase's own constraint: "do not redesign orchestration"). Until it
  is, the index reflects whatever state it was last built against, not
  necessarily today's.
- Confidence and validation metadata (Phase 3) surface only what an
  artifact's own content already states or structurally violates —
  they never compute, infer, or estimate a fact the artifact doesn't
  already carry, preserving the "never fabricate" principle at the
  infrastructure layer, not just within each employee's own logic.

## Future Migration Path

If file-scanning ever becomes measurably (not speculatively) too slow,
the natural next step is an embeddable, still-zero-ops local index
(e.g. SQLite) sitting alongside the JSON index, not replacing it —
per `ARCHITECTURE-CONSTITUTION.md`'s distinction between an invariant
(human-readable, git-auditable persistence) and its implementation
detail (a flat JSON file today). A networked database only becomes
worth reconsidering alongside a genuine, separately-decided hosted
multi-tenant business model — never as a default upgrade path from
here.
