# AOS v1.0 — Production Deployment Checklist

This is a hardening pass, not a new build: nothing below changed what
any AI employee decides, scores, or writes. It confirms the existing
system — architecture and runtimes as completed through Runtime Sprint
2 — is safe to run daily, unattended, with nobody watching. Each item
is either verified as already true, or was a small, additive fix
listed with what changed.

## 1. Automatic Daily Execution — 06:00 IST

- [x] `.github/workflows/aos-daily-operations.yml` schedules
  `cron: "30 0 * * *"` — 00:30 UTC, which is 06:00 IST (UTC+5:30).
  **Fixed this pass** — it previously ran at 02:00 UTC (06:00 UAE
  time, UTC+4), not IST.
- [x] `workflow_dispatch` is present for an on-demand manual run
  (testing, catching up after an outage).
- [x] The workflow's only executable step is
  `python3 AOS/orchestrator/orchestrator.py` — no individual employee
  script is invoked directly by GitHub Actions.
- [x] The workflow commits and pushes any `AOS/` changes after the run
  (`git add AOS/`, commit if non-empty, push), so every day's outputs
  land in the repo automatically.

## 2. Correct Execution Order, Every Run

- [x] `runtime/config/orchestrator-config.json`'s employee list order
  matches the founder-specified fixed sequence exactly: Market
  Intelligence, Opportunity Hunter, Revenue Hunter, CRM, Sales
  Director, Product Manager, Content Director, CEO Advisor, Daily
  Brief.
- [x] `dependsOn` edges match real data flow (`dependency-map.md`) and
  never point forward in the sequence (verified: no employee depends
  on one that runs after it — this was caught and fixed for CRM's
  entry during Sprint 2, which must depend only on Opportunity Hunter
  and Revenue Hunter, not Sales Director, since Sales Director runs
  after it).
- [x] Verified via a full 9-step run against a fresh scratch copy of
  the real repo: all eight executable employees returned `SUCCESS` in
  the documented order; CEO Advisor correctly reported
  `NOT_EXECUTABLE`.

## 3. One Daily Executive Brief

- [x] Exactly one canonical Daily Executive Brief is produced per run,
  by Daily Brief's own generator (`executive-dashboard/runtime/generate.py`)
  — the Orchestrator does not compute a second one or duplicate its
  logic.
- [x] Verified against the real (currently near-empty) repo: the run
  dated 2026-07-25 produced one real brief end-to-end.

## 4. Dated Archive — `AOS/daily-briefs/YYYY/MM/DD/`

- [x] **Added this pass.** Every run, after writing its existing
  stable (`executive-dashboard/executive-dashboard.md`) and dated
  (`output/executive-dashboard/{date}-executive-dashboard.md`)
  copies exactly as before, the generator now additionally writes an
  immutable dated copy to `AOS/daily-briefs/{YYYY}/{MM}/{DD}/`. Nothing
  existing was removed or restructured — this is additive.
- [x] Placed under `AOS/` (not the repo root) to keep it alongside
  every other AOS working file and out of the unrelated
  `aiforu-platform/` Next.js site.
- [x] `orchestrator-config.json`'s `daily-brief` entry lists the new
  paths (using a new `{date_path}` placeholder that expands
  `YYYY-MM-DD` to `YYYY/MM/DD`) so the Daily Execution Report's
  "Outputs Generated" section detects and lists them.
- [x] Verified: a real run today produced
  `AOS/daily-briefs/2026/07/25/executive-dashboard.md` and `.html`.

## 5. Human-Readable HTML Dashboard

- [x] **Added this pass.** `markdown_to_html()` in
  `executive-dashboard/runtime/generate.py` renders the exact same
  computed report as a self-contained HTML page (inline CSS, no
  external requests, light/dark aware via
  `prefers-color-scheme`) — it does not recompute or reinterpret any
  figure, it renders the same lines the Markdown report already
  contains.
- [x] Written alongside the Markdown at every location: stable
  (`executive-dashboard.html`), dated (`runtime/output/{date}-...html`),
  and the new dated archive (`daily-briefs/YYYY/MM/DD/...html`).
- [x] All inline content is HTML-escaped before any markdown-style
  emphasis is applied, so a real company or opportunity name
  containing `&`, `<`, or `>` (tested with "AT&T Corp",
  "R&D Labs", "AI Governance <Advisory>") can never be misrendered or
  break the page.
- [x] Whole-line empty-state italics (e.g. `_No open pipeline items
  yet._`) render correctly as `<em>`, while a real identifier
  containing an underscore (tested with "ACME_Corp_Test") is left
  untouched — the italics conversion is anchored to the full line, not
  applied as a general inline substitution, specifically to avoid that
  class of false positive.

## 6. Every Failure Logged, Independent Employees Never Blocked

- [x] Already true by the original Orchestrator design: each employee
  runs as its own subprocess, so a crash in one can never reach
  another; retries are per-employee and configurable; a genuine
  failure only cascades to real dependents
  (`SKIPPED_DEPENDENCY_FAILED`), never to unrelated employees.
- [x] **Hardened this pass** — two gaps closed where an unexpected
  error *inside the Orchestrator's own bookkeeping* (not an employee's
  subprocess) could previously have gone unlogged or aborted the whole
  run:
  - A broken `orchestrator-config.json` (unparseable JSON) previously
    crashed before any log file existed. Now it opens a log, records
    the failure, and writes a `FAILED` `status.json` before exiting.
  - An unexpected exception while processing one employee's turn (not
    its subprocess exit code, which was already handled) is now caught
    per-employee, logged, and recorded as that employee's own `FAILED`
    — the loop continues to every remaining employee exactly as
    before.
- [x] Verified with failure injection against scratch copies (not the
  real repo): (a) a syntactically invalid config file produced a
  logged, diagnosable `FAILED` status rather than a bare traceback;
  (b) a pointed-at-a-missing-file employee script failed all retries,
  correctly cascaded `SKIPPED_DEPENDENCY_FAILED` only to its real
  dependents (CRM, Sales Director, CEO Advisor, Daily Brief), while
  Market Intelligence, Opportunity Hunter, Product Manager and Content
  Director — all independent of it — still ran to `SUCCESS`.
- [x] Every `FAILED` employee is written to `status.json`'s `failures`
  list, which `09-CEO-Advisor/decision-model.md` already reads as a
  candidate action (unchanged from the original Orchestrator build).

## 7. This Checklist

- [x] Produced as the final Sprint task, confirming AOS v1.0 is
  production-ready for unattended daily execution.

## What This Pass Deliberately Did Not Touch

Per instruction, no new AI employee, no redesign, no new business
logic:

- No scoring, classification, routing, or forecasting logic in any
  employee changed.
- No new employee was added; the same eight executable employees plus
  CEO Advisor's documented `NOT_EXECUTABLE` status are unchanged.
- The Orchestrator's dependency graph, retry semantics, and Daily
  Execution Report format are unchanged in substance — only extended
  to detect two new output paths and survive two new failure modes.

## Known, Accepted Limitations (Unchanged From Sprint 2)

- CEO Advisor remains `NOT_EXECUTABLE` by design — its decision model
  already runs as a section of Daily Brief's own generator.
- Three runtimes read a same-day file written by an employee that
  executes later in the fixed sequence (Revenue Hunter and CRM both
  read Sales Director's `processed-index.json`; Product Manager reads
  Content Director's queue state) — one cycle behind, self-corrects
  the following run, documented in each runtime's own notes.
- All real business data files are close to empty on this repo today
  (collection has only just begun) — every report and dashboard
  reflects that honestly rather than fabricating activity.

## Sign-Off

AOS v1.0 is production-ready for autonomous daily execution at 06:00
IST via GitHub Actions, with every runtime failure logged and isolated
to its real dependents, one Daily Executive Brief produced and
archived per day in both Markdown and HTML, and a Daily Execution
Report generated every run.
