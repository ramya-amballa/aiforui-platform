# ADR 0003: Wire the Artifact Registry into the daily Orchestrator run

**Status:** Accepted

## Context

ADR 0001 built the Artifact Registry as a shadow index, explicitly not
yet wired into the daily Orchestrator run — invoked by hand, its index
living outside `output/` because a manually-triggered build isn't real
daily production data. Once the registry (Phases 1-3) was proven out
by its own test suite and a live run against real data, the next
question was whether adding it to the daily run counts as
"redesigning orchestration" (explicitly out of scope for prior phases)
or as using the existing orchestration mechanism exactly as it already
works for all 22 employees.

Separately, this work surfaced a real, pre-existing bug while
verifying the dependency graph: `reverse-job-hunt`'s own `dependsOn`
names `relationship-intelligence`, which sat *after* it in the fixed
execution array — meaning it had been silently `SKIPPED_DEPENDENCY_
FAILED` in every real run since Sprint 13, without anyone noticing,
because that status looks enough like a legitimate state that it
never got investigated. This was the concrete example cited when
`architecture-v2/aos-v2-architecture.md` first argued the fixed array
doesn't scale — it seemed right to fix directly rather than wait for
a hypothetical future DAG Scheduler v2.

## Decision

Add `artifact-registry` as a new entry in `orchestrator-config.json`,
positioned after every real employee and before CEO Advisor, with
`dependsOn` listing every employee it isn't itself (mirroring exactly
how `ceo-advisor`'s own `dependsOn` is constructed). This is judged to
be *using* the orchestration mechanism, not redesigning it: the same
config format, the same subprocess-per-step model, the same retry and
dependency-check logic every existing employee already runs under —
one more entry in an existing list, not a new execution model.

`ceo-advisor`'s own `dependsOn` gains `artifact-registry`. This gives
CEO Advisor something no other cross-referenced feed in this codebase
has: a **genuinely same-run-fresh** read. Every other optional feed
CEO Advisor reads (Capacity Management's, for instance) is one cycle
behind, because those employees' own dependency chains could create a
cycle back into CEO Advisor if ordered any other way. The Artifact
Registry has no such constraint — it depends on nothing CEO Advisor
itself produces, only that everyone else has already run — so it can
sit immediately before CEO Advisor with no lag at all. Verified
directly: a live run's CEO Daily Report and the registry's own index
carry the identical build timestamp.

The registry's index file moves from a local-only path outside
`output/` to `output/artifact-registry/artifact-index.json`, and the
now-unneeded `.gitignore` entry from ADR 0001 is removed — once it's
produced by the real daily run, it is real daily production data,
committed the same way every other employee's output already is.

Separately, `relationship-intelligence` moves earlier in the
employees array, ahead of `reverse-job-hunt` — the minimal fix for
the ordering bug described above. `relationship-intelligence`'s own
dependencies (`demand-intelligence`, `crm`) both already sit well
before its new position, so this reorder introduces no new ordering
violation. Verified with the same dependency-order check used
throughout this review: zero violations post-fix, versus one
pre-existing violation before it.

## Alternatives Considered

- **Leave the registry un-wired, invoked by hand indefinitely.**
  Rejected — an index that's only ever as fresh as the last manual run
  provides materially less value than one that's current every day,
  and the mechanism for adding it (one config entry) is exactly as
  small and low-risk as adding any other employee has ever been.
- **Give the Artifact Registry the same one-cycle-behind treatment as
  Capacity Management.** Rejected once the actual dependency structure
  was checked: unlike Capacity Management, nothing about the registry
  creates a real cycle risk, so accepting a lag here would be an
  unforced, unnecessary downgrade in freshness.
- **Defer the ordering bug fix to a future DAG Scheduler v2.** Rejected
  — `architecture-v2/aos-v2-architecture.md`'s own roadmap already
  named this fix as "should not wait for this architecture to ship";
  a one-line array reorder, already fully diagnosed, is not worth
  leaving broken until a much larger scheduler rewrite is undertaken.

## Consequences

- Every daily run now produces a same-day artifact index and a
  same-day, non-lagged CEO Advisor summary of it.
- `reverse-job-hunt` runs successfully in every future daily run
  instead of being permanently skipped — verified live: `SUCCESS`
  where it had always previously read `SKIPPED_DEPENDENCY_FAILED`.
- The Orchestrator's own employee count is now 24 (23 real employees
  and Daily Brief/Artifact Registry, both infrastructure entries using
  the same mechanism) — `dependency-map.md` updated accordingly.

## Future Migration Path

If a future DAG Scheduler v2 (per `architecture-v2/aos-v2-
architecture.md`'s Phase 3) replaces the fixed array with a computed
topological sort, this fix and this wiring both migrate for free —
they are already expressed as ordinary `dependsOn` edges, exactly the
data a real scheduler would consume. Nothing here is tied to the
array's current fixed-order implementation detail.
