# AOS Orchestrator — Execution Plan

The single entry point for daily AOS operations:

```
python3 AOS/orchestrator/orchestrator.py
```

Nothing else should be invoked directly — not by a human's daily
routine, not by GitHub Actions. Everything below is what happens
inside that one command.

## Scheduling

`.github/workflows/aos-daily-operations.yml` runs this exact command
automatically every day at **06:00 IST** (`cron: "30 0 * * *"` — 00:30
UTC, since IST is UTC+5:30), plus `workflow_dispatch` for an on-demand
manual run. No other workflow exists, and no workflow invokes an
individual employee's script directly — see that file.

## Execution Sequence

Fixed order, per the founder's instruction — see `dependency-map.md`
for why this order holds. Sprint 3 inserted the Service Mapping Engine
as step 6 (its only hard dependency is Demand Intelligence; it runs
after CRM and before Sales Director so Sales Director can read its
recommendations the same day). Sprint 4 inserted the Website Intake
Runtime as a new step 2 — it is fully self-contained (it invokes
Demand Intelligence's, Revenue Hunter's and the Service Mapping
Engine's own scripts as subprocesses within its own run, rather than
depending on their separately scheduled steps below), so it has no
`dependsOn` and runs early enough that every downstream step already
sees website-sourced opportunities as just another opportunity by the
time it runs. Sprint 5 swapped Daily Brief and CEO Advisor: the
founder's explicit instruction was "CEO Advisor must become the final
step of every AOS execution cycle," with Daily Brief itself listed as
one of CEO Advisor's own inputs — so Daily Brief now runs second-to-
last and CEO Advisor genuinely last, reading Daily Brief's output
rather than feeding it (see `09-CEO-Advisor/operating-manual.md`):

1. Market Intelligence
2. Website Intake Runtime
3. Demand Intelligence
4. Revenue Hunter
5. CRM
6. Service Mapping Engine
7. Sales Director
8. Product Manager
9. Content Director
10. Daily Brief
11. CEO Advisor

## Per-Step Behaviour

For each employee, in order:

1. **Check dependencies.** If any employee in its `dependsOn` list
   (`dependency-map.md`) finished `FAILED` or `SKIPPED_DEPENDENCY_FAILED`,
   this step is recorded `SKIPPED_DEPENDENCY_FAILED` and nothing runs.
2. **Check executability.** If `runtime/config/orchestrator-config.json`
   has no `script` for this employee, it is recorded `NOT_EXECUTABLE`
   and nothing runs. This is not a failure.
3. **Run, with retries.** Otherwise, invoke the employee's script as
   its own subprocess (`python3 <script>`, run from that script's own
   directory, exactly as it would be run by hand) — never imported,
   never called in-process, so a crash in one employee can never take
   down the Orchestrator or any other employee. On a non-zero exit
   code or a timeout, retry up to `maxRetries` additional times (default
   2, configurable per employee in `orchestrator-config.json`), waiting
   `retryBackoffSeconds` between attempts (default 5s). Every attempt's
   stdout and stderr is captured into the run's log.
4. **Record the outcome.** `SUCCESS` (exit 0, no further retries
   needed), or `FAILED` (every attempt exhausted). Duration and attempt
   count are recorded either way.
5. **Detect outputs.** After a `SUCCESS`, the Orchestrator checks each
   employee's own well-known output paths (documented in
   `runtime/config/orchestrator-config.json`'s `outputPaths`) for a
   file dated today, and records which exist. It does not parse or
   interpret their contents beyond that one exception: Daily Brief's
   "## Daily Summary" section is read verbatim to become the Execution
   Report's Business Impact section (see below) — the Orchestrator
   quotes it, it does not recompute it.

## Failure Handling

- **Retry**: configurable count and backoff, per employee, above.
- **Log**: every attempt, every exit code, every stdout/stderr capture,
  and every skip decision goes to `../output/orchestrator/logs/{date}-{time}-orchestrator.log`.
- **Continue where possible**: a failed employee does not stop the
  run. Only employees that actually depend on the failed one are
  skipped (`SKIPPED_DEPENDENCY_FAILED`); everything else still runs.
  For example, if Demand Intelligence fails, Market Intelligence,
  Product Manager and Content Director are unaffected and still run.
- **Notify CEO Advisor**: any `FAILED` employee is written into
  `../output/orchestrator/status.json`'s `failures` list. `09-CEO-Advisor/decision-model.md`
  and `operating-manual.md` were given one additive line each pointing
  at this file, so a pipeline failure surfaces as a candidate action
  the same way an at-risk relationship or a stalled deal does — see
  those files for the exact normalisation. Since Sprint 5,
  `ceo-advisor/runtime/generate.py` reads this list for real, as its
  own run's last step, and always treats any failure as urgent
  regardless of which employee failed. The Orchestrator does not
  modify `09-CEO-Advisor`'s or `executive-dashboard`'s scoring logic to
  do this; it only makes the failure discoverable where CEO Advisor
  already looks.

## Completion Status

`AOS/output/orchestrator/status.json` is
overwritten at the end of every run with: start/finish timestamps,
total duration, one entry per employee (status, attempts, duration,
error if any, detected outputs), the overall run status
(`SUCCESS` — everything either succeeded or was honestly
`NOT_EXECUTABLE`; `PARTIAL_FAILURE` — at least one real failure, but at
least one employee succeeded; `FAILED` — every executable employee
failed), and a pointer to that run's Daily Execution Report.

## Daily Execution Report

Written to `AOS/output/orchestrator/reports/{date}-daily-execution-report.md` on every
run, and includes exactly what was asked for:

- **Employees executed** — all nine, with status
- **Duration** — total and per-employee
- **Failures** — which employees, which error, how many attempts
- **Retries** — how many retries each employee needed
- **Outputs generated** — the detected files from step 5 above,
  including Daily Brief's Markdown and HTML dashboard in both their
  stable location and their immutable dated archive copy under
  `AOS/output/daily-briefs/YYYY/MM/DD/`
- **Business impact** — Daily Brief's own "## Daily Summary" paragraph,
  quoted verbatim (see step 5) — the Orchestrator does not have its own
  business-impact model and does not build one; that would duplicate
  what Daily Brief and CEO Advisor already compute

## What the Orchestrator Deliberately Does Not Do

- Does not reimplement any employee's scoring, classification, routing,
  or aggregation logic.
- Does not simulate a result for an employee with no runtime — it
  reports `NOT_EXECUTABLE` honestly.
- Does not write to any employee's data files
  (`opportunity-schema.json`, `pipeline.json`, `company-intelligence.json`,
  etc.) — only the employees themselves do that, exactly as before.
  The Orchestrator's own writes are limited to `output/orchestrator/logs/`,
  `output/orchestrator/status.json`, and `output/orchestrator/reports/`.
