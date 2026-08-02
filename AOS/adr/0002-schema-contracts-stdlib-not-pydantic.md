# ADR 0002: Schema Contracts as stdlib enum + hand-written validation, not Pydantic

**Status:** Accepted

## Context

A grep across every employee's own code found seven honest-gap
phrases ("Not specified", "Not tracked", "Not enough signal yet", and
four others) already in use 131 times combined — a real, informal
vocabulary for "this field genuinely has no value," expressed as
implicit string literals rather than a formal, checkable contract.
Formalizing this, plus giving AOS's JSON feed shapes a real, versioned
schema instead of only a hand-written comment block, was proposed
using Pydantic models.

Every AOS employee runtime has been dependency-free stdlib Python
since day one, with exactly one demonstrated exception: spaCy, adopted
for Demand Signals' offline Named Entity Recognition, a capability
pure stdlib genuinely cannot provide (see `demand-intelligence/
runtime/requirements.txt`). No employee runtime has ever adopted a
dependency for convenience alone.

## Decision

Build Schema Contracts as two small, stdlib-only pieces:

- `status_vocabulary.py` — a `GapMarker(str, Enum)` naming the seven
  real phrases already in use. Because it subclasses both `str` and
  `Enum`, `GapMarker.NOT_SPECIFIED == "Not specified"` is `True` — an
  employee that adopts it writes the exact same string to disk as
  before; an employee that never adopts it is unaffected.
- `schema_validator.py` — a minimal structural checker (required
  top-level keys present, each declared field's Python type matches)
  against real, hand-authored `.schema.json` files. Deliberately not
  the `jsonschema` package, and deliberately not the full JSON Schema
  specification (no `$ref`, `pattern`, `enum`, or nested-schema
  support) — this checks exactly the two things that have actually
  gone wrong in this codebase so far (a field silently renamed, a
  feed's shape drifting from its own documented comment), nothing
  speculative beyond that.

Two pilot Schema Contracts ship with this decision:
`account-intelligence-feed.schema.json` (a real, already-documented
employee feed) and `artifact-index.schema.json` (the Artifact
Registry's own output — it validates itself against the same
discipline it applies to everyone else). Both are wired into
`registry_validation.py`'s existing Phase 3 structural checks,
advisory only, exactly like every other flag it already raises.

## Alternatives Considered

- **Pydantic models.** Real runtime validation and serialization with
  materially less hand-written code — a genuine capability gap
  against the stdlib approach. Rejected for now because it would be
  the first dependency adopted for convenience rather than
  demonstrated necessity, across all 22 employee runtimes at once,
  and because AOS's actual schema complexity today (mostly flat
  dictionaries, not deeply nested polymorphic structures) doesn't yet
  show the kind of validation burden that gap would meaningfully
  close. If a future employee's data shape grows complex enough that
  hand-written validation becomes its own maintenance burden, that is
  the trigger to revisit this decision — not a schedule, a demonstrated
  cost.
- **The `jsonschema` package**, to validate against real JSON Schema
  spec files without hand-rolling a validator. Rejected for the same
  reason as Pydantic: a second new dependency for a validation need
  the codebase's actual schema complexity doesn't yet require in full.
- **Migrating every employee's existing string literals to the enum
  immediately.** Rejected as unnecessarily wide for this decision —
  the enum is available for incremental adoption; forcing a 22-employee
  migration in one pass would be scope far beyond what was asked.

## Consequences

- Zero new dependencies added to any employee runtime.
- `GapMarker` and `is_gap_marker()` are available today for any
  employee (or a future enforcing verification layer) to check "is
  this an honest, declared gap" programmatically, without adopting
  Pydantic or rewriting existing string literals.
- The two pilot Schema Contracts prove the mechanism end-to-end
  (loadable, validate a real correct shape with zero violations, and
  correctly flag a real broken one) before any wider rollout is
  attempted.
- Schema Contracts beyond these two pilots are added incrementally, as
  and when a real employee's feed shape is worth formalizing — not
  batched into a single large migration.

## Future Migration Path

If Pydantic (or `jsonschema`) is ever adopted, it should replace
`schema_validator.py`'s internals behind the same
`validate_against_schema()` interface, so every existing pilot schema
and every caller is unaffected — the interface, not the mechanism
behind it, is the stable contract. That adoption is itself a decision
warranting its own ADR, made when a demonstrated validation gap
justifies it, not inferred from this one.
