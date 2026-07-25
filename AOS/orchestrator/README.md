# AOS Orchestrator (v1.0)

The single entry point for daily AOS operations. Before this build, each
live employee (`opportunity-hunter/runtime/collect.py`,
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
