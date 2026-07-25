# AOS Orchestrator (v1.0)

The single entry point for daily AOS operations. Before this build, each
live employee (`demand-intelligence/runtime/collect.py`,
`sales-director/runtime/prepare.py`, `executive-dashboard/runtime/generate.py`)
was invoked separately, by hand or by its own GitHub Actions workflow.
This is the coordination layer that turns those independent scripts
into one operating system: it decides execution order, enforces the
dependency graph, retries failures, logs everything, and produces one
Daily Execution Report — without changing a single line of any
employee's own logic.

## Files

- `orchestrator.py` — the engine: run order, dependency checks, retry
  loop, logging, `status.json`, the Daily Execution Report
- `execution-plan.md` — the fixed nine-step sequence and exactly what
  happens at each step
- `dependency-map.md` — the real dependency graph, and an honest
  accounting of which employees have a runtime to invoke today and
  which don't yet
- `runtime/config/orchestrator-config.json` — the employee registry:
  script path (or `null`), dependencies, retry/timeout settings, output
  paths — the only file that needs editing to add a new employee's
  runtime later
- `runtime/reports/` — one Daily Execution Report per run
- `logs/` — one full run log per run
- `status.json` — the latest run's completion status, overwritten each
  run

## Production Hardening (v1.0.1)

Everything above was already true from the original build. This pass
made it safe to run unattended, every day, with nobody watching:

- **Schedule** — `.github/workflows/aos-daily-operations.yml` runs on
  `cron: "30 0 * * *"` — 00:30 UTC, i.e. 06:00 IST — plus
  `workflow_dispatch` for a manual run. GitHub Actions still invokes
  only this one script, nothing else.
- **Config-load failures are now logged, not bare tracebacks** — if
  `runtime/config/orchestrator-config.json` itself fails to parse,
  `orchestrator.py` still opens a log, records the failure, and writes
  a `FAILED` `status.json`, rather than crashing before there's
  anywhere to record why.
- **Per-employee bookkeeping is now exception-safe** — an unexpected
  error in the Orchestrator's own per-employee handling (not the
  employee's own subprocess, which was already isolated) is caught,
  logged, and recorded as that one employee's `FAILED`, so every
  independent employee still downstream gets its own chance to run —
  see `../../AOS/deployment-checklist.md` for the failure-injection
  tests this was verified against.
- **The Daily Executive Brief is now archived immutably** — every run,
  Daily Brief's generator writes the same report into
  `AOS/daily-briefs/YYYY/MM/DD/` (both `.md` and a new self-contained
  `.html` rendering), in addition to the stable and dated locations it
  already wrote. `orchestrator-config.json`'s `daily-brief` entry lists
  the new paths so the Daily Execution Report's "Outputs Generated"
  section detects them too.

## Usage

```
python3 AOS/orchestrator/orchestrator.py
```

This is the only command a human or a scheduler should ever run.
GitHub Actions invokes exactly this and nothing else — see
`.github/workflows/aos-daily-operations.yml`. Individual employees
(`collect.py`, `prepare.py`, `generate.py`) are still runnable directly
by hand for testing, but no automation should call them directly
anymore.

## What This Is Not

Not a rewrite of any employee. Every employee keeps its own scoring,
classification, routing and generation logic exactly as built. The
Orchestrator only decides *when* each one runs, *whether* its
dependencies are satisfied, *how many times* to retry it, and *what*
to report afterward. See `execution-plan.md`'s closing section for the
explicit list of what it deliberately does not do.

Start with `execution-plan.md`, then `dependency-map.md`.
