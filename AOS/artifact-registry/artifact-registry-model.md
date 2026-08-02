# Artifact Registry — Model

Built per `ARCHITECTURE-CONSTITUTION.md` and `architecture-v2/aos-v2-
architecture.md`'s Phase 1 proposal, and evaluated against
`architecture-v2/gemini-enterprise-roadmap-critique.md`'s explicit
verdict on this exact component ("NOW, shadow-index form only").

This is not a new employee. It has no consulting responsibility of
its own — it does not score an opportunity, generate a deliverable, or
make a recommendation. It is infrastructure, in the same category as
`orchestrator/`: something every employee's real output can be
indexed by, never something that changes what any employee produces.

## What this is

A metadata index, rebuilt from scratch on every run, over whatever is
already sitting in `AOS/output/`. It never stores a copy of any
artifact's content — every record is a pointer (a path, a content
hash) plus derived metadata (type, produced date, lineage, confidence,
validation flags). Delete the index and rebuild it: the result is
identical, because nothing in it is a system of record. The Markdown
and JSON files under `output/` remain the only canonical, human-
readable artifacts, exactly as the Constitution requires.

## What this is not

- **Not a database.** No engine, no server process, no schema
  migration tooling. `registry_builder.py` reads files and writes one
  JSON file back out.
- **Not a replacement for any employee's own output.** Every employee
  still writes exactly what it wrote before this existed, to exactly
  the same place. Company 360 and CEO Advisor's read-only integration
  (Phase 2) is additive: remove the registry entirely and both
  employees fall back to exactly their pre-registry behavior.
- **Not imported by any employee's Python code.** Company 360 and CEO
  Advisor read the registry's own index file exactly the way they read
  any other employee's `*-feed.json` — never `import registry_query`.
  This preserves the same subprocess-isolation invariant every other
  cross-employee reference in AOS already honors.
- **Not a source of true, per-instance data lineage.** Lineage here is
  coarse-grained and employee-level, derived from the Orchestrator's
  own `dependsOn` graph — see Phase 1, below.
- **Not a verification or fabrication-detection system.** Phase 3's
  validation flags are cheap, structural, advisory-only checks (does
  this parse as JSON, does a feed declare its own schema key) — never
  a claim about whether an artifact's *content* is true. See the
  Gemini critique's explicit rejection of a general claim-extraction
  engine for why that line is deliberate.

## Phase 1 — Schema, index builder, artifact metadata model, lineage model

`registry_model.py` defines what one artifact record looks like:
stable ID (derived from its path, so rebuilding reproduces the same
IDs), employee, artifact type (rule-based, from real path conventions
already in this codebase — feeds, dated reports, delivery kit
components, account briefs, strategy documents, company profiles,
platform artifacts), produced date (parsed from the filename, this
codebase's own convention, never guessed from mtime), a content hash,
and lineage.

Lineage is deliberately coarse: it names which employees a given
artifact's producer is *allowed* to have read from, per the
Orchestrator's own `dependsOn` graph — not which specific upstream
artifact version it actually read. Getting true per-instance lineage
would require every employee to declare what it read at write time,
which would violate "existing employees continue to function
unchanged." This is the honest boundary of what a read-only shadow
index can know without employee cooperation.

`registry_builder.py` scans `output/` and writes one full index,
rebuilt from scratch, every time it runs. As of ADR 0003, it runs as
part of the daily Orchestrator cycle — the last step before CEO
Advisor — and its index lives at `output/artifact-registry/artifact-
index.json`, committed the same way every other employee's daily
output already is.

## Phase 2 — Query API, employee lookup helpers, read-only integration

`registry_query.py` is a pure, read-only API over an already-loaded
index: latest artifact for an employee, lookup by ID, artifacts for a
named organisation (matching the same `slugify()` every employee
already uses in its own file naming), lineage for an artifact, and a
one-line human-readable summary.

Company 360 gained one new field, `artifactRegistry`, populated only
when a registry index is passed in (default `None`) — every existing
call site is unaffected. CEO Advisor gained one new report section,
`## Artifact Registry`, following the exact structural pattern
Capacity Management's own section established — read-only, purely
informational, never changing ranking or Top 3 — but with a real
improvement Capacity Management's own feed can't have: since the
registry depends on nothing CEO Advisor itself produces, ADR 0003
positions it to run immediately before CEO Advisor in the same daily
cycle, so CEO Advisor's read is genuinely same-run-fresh, not one
cycle behind.

## Phase 3 — Registry validation, confidence metadata, structural verification hooks

`registry_validation.py` adds two things, both opportunistic and
advisory only:

- **Confidence** — surfaced only when an artifact's own content
  already states one, via a pattern that already exists in this
  codebase (`**Confidence score:** N/100` in Sales Director's own
  proposal packages; `confidenceScore`/`qualificationScore` JSON
  fields). Never computed, never inferred, `null` for every artifact
  that doesn't already carry one.
- **Validation flags** — cheap, deterministic, structural checks only
  (invalid JSON, an empty file that isn't a `.gitkeep`, a `feed`-typed
  artifact missing its own documented `schema` key). A flagged
  artifact is still fully indexed; flags are a worklist for a human
  (or a future enforcing verification layer, per the Constitution's
  own evolution path), never a filter that excludes anything.

## Phase 4 — Schema Contracts (schema-contracts/, a sibling component)

A separate, sibling infrastructure component — not part of
`artifact-registry/` itself, but wired into its Phase 3 validation.
`status_vocabulary.py` formalizes seven honest-gap phrases already in
real use 131 times across this codebase (`"Not specified"`, `"Not
tracked"`, `"Not enough signal yet"`, and four others) into one
`GapMarker(str, Enum)`, interchangeable with the plain strings already
on disk. `schema_validator.py` is a minimal, hand-written structural
checker — required keys present, declared types match — against real
`.schema.json` files, starting with two pilots:
`account-intelligence-feed.schema.json` and the registry's own
`artifact-index.schema.json` (the registry validates its own output
against the same discipline it applies to everyone else). Deliberately
stdlib only, not Pydantic — see ADR 0002 for the full reasoning.

## What is deliberately still missing

- **No enforcing verification.** Everything here is advisory; nothing
  blocks an artifact from being indexed or an employee from running.
- **No Candidate Artifact lifecycle.** Every record's `lifecycle`
  field is a constant `"published"` — meaningful lifecycle states
  require the enforcing verification gate this phase deliberately does
  not build yet (see the Gemini critique's own sequencing note on this
  exact point).
- **No SQLite/Postgres.** The index is one JSON file. It stays that
  way until file-scanning is *measurably*, not speculatively, too slow
  — per the Constitution's Technology Philosophy.
