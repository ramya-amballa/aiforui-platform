#!/usr/bin/env python3
"""
AOS Orchestrator v1.0 — the single entry point for daily AOS operations.

Usage:
    python3 orchestrator.py

Runs all nine AI employees in the fixed order documented in
execution-plan.md, honouring the dependency graph in
dependency-map.md. Every employee with a real runtime script is
invoked as its own subprocess — never imported, never called
in-process — so this file contains no employee business logic and
cannot duplicate any. An employee with no runtime yet is recorded
NOT_EXECUTABLE, not simulated.

Writes, every run:
  - logs/{date}-{time}-orchestrator.log   — full run log
  - status.json                           — latest completion status
  - runtime/reports/{date}-daily-execution-report.md — the Daily
    Execution Report (employees executed, duration, failures, retries,
    outputs generated, business impact)

This script is the only thing GitHub Actions (or a human) should ever
invoke to run AOS's daily operations — see
../../.github/workflows/aos-daily-operations.yml. It never invokes an
employee directly except through the registry in
runtime/config/orchestrator-config.json.
"""

import json
import re
import subprocess
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

ORCHESTRATOR_DIR = Path(__file__).resolve().parent
AOS_DIR = ORCHESTRATOR_DIR.parent
REPO_ROOT = AOS_DIR.parent

CONFIG_PATH = ORCHESTRATOR_DIR / "runtime" / "config" / "orchestrator-config.json"
LOGS_DIR = ORCHESTRATOR_DIR / "logs"
REPORTS_DIR = ORCHESTRATOR_DIR / "runtime" / "reports"
STATUS_PATH = ORCHESTRATOR_DIR / "status.json"

TODAY = date.today().isoformat()
RUN_STARTED = datetime.now(timezone.utc)

STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"
STATUS_NOT_EXECUTABLE = "NOT_EXECUTABLE"
STATUS_SKIPPED_DEPENDENCY_FAILED = "SKIPPED_DEPENDENCY_FAILED"

# A dependency in either of these states satisfies a downstream step;
# only an actual failure (its own or inherited) blocks one.
SATISFIES_DEPENDENCY = {STATUS_SUCCESS, STATUS_NOT_EXECUTABLE}


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def open_log():
    LOGS_DIR.mkdir(exist_ok=True)
    log_path = LOGS_DIR / f"{TODAY}-{RUN_STARTED.strftime('%H%M%S')}-orchestrator.log"
    return log_path, open(log_path, "w", encoding="utf-8")


def log(fh, message):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {message}"
    print(line)
    fh.write(line + "\n")
    fh.flush()


def resolve_output_paths(output_paths, date_str):
    return [p.replace("{date}", date_str) for p in (output_paths or [])]


def detect_outputs(employee, aos_dir, date_str):
    detected = []
    for rel_path in resolve_output_paths(employee.get("outputPaths"), date_str):
        full = aos_dir / rel_path
        if full.exists():
            detected.append(rel_path)
    return detected


def run_attempt(script_path, timeout_seconds, fh):
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(script_path.parent),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        if result.stdout:
            fh.write(result.stdout)
        if result.stderr:
            fh.write(result.stderr)
        return result.returncode, (result.stderr or result.stdout or "").strip().splitlines()[-1:] or [""]
    except subprocess.TimeoutExpired:
        fh.write(f"TIMEOUT after {timeout_seconds}s\n")
        return None, [f"timed out after {timeout_seconds}s"]


def run_employee(employee, defaults, aos_dir, fh):
    key, name = employee["key"], employee["name"]
    started = time.monotonic()

    if not employee.get("script"):
        log(fh, f"{name}: NOT_EXECUTABLE — {employee.get('note', 'no runtime implementation yet')}")
        return {"key": key, "name": name, "status": STATUS_NOT_EXECUTABLE, "attempts": 0,
                "durationSeconds": 0, "error": None, "outputs": []}

    script_path = aos_dir / employee["script"]
    max_retries = employee.get("maxRetries", defaults["maxRetries"])
    backoff = employee.get("retryBackoffSeconds", defaults["retryBackoffSeconds"])
    timeout_seconds = employee.get("timeoutSeconds", defaults["timeoutSeconds"])

    attempts = 0
    last_error_lines = []
    for attempt_num in range(1, max_retries + 2):  # 1 initial + maxRetries
        attempts = attempt_num
        log(fh, f"{name}: attempt {attempt_num}/{max_retries + 1} -> {employee['script']}")
        exit_code, last_error_lines = run_attempt(script_path, timeout_seconds, fh)
        if exit_code == 0:
            duration = round(time.monotonic() - started, 2)
            log(fh, f"{name}: SUCCESS after {attempts} attempt(s), {duration}s")
            outputs = detect_outputs(employee, aos_dir, TODAY)
            return {"key": key, "name": name, "status": STATUS_SUCCESS, "attempts": attempts,
                    "durationSeconds": duration, "error": None, "outputs": outputs}

        log(fh, f"{name}: attempt {attempt_num} failed (exit {exit_code}): {' '.join(last_error_lines)}")
        if attempt_num <= max_retries:
            time.sleep(backoff)

    duration = round(time.monotonic() - started, 2)
    error = " ".join(last_error_lines) or "non-zero exit code"
    log(fh, f"{name}: FAILED after {attempts} attempt(s), {duration}s — {error}")
    return {"key": key, "name": name, "status": STATUS_FAILED, "attempts": attempts,
            "durationSeconds": duration, "error": error, "outputs": []}


def extract_business_impact(source_path):
    if not source_path or not source_path.exists():
        return None
    text = source_path.read_text(encoding="utf-8")
    marker = "## Daily Summary"
    if marker not in text:
        return None
    return text.split(marker, 1)[1].strip()


def render_report(results, total_duration, business_impact, business_impact_employee):
    lines = [
        "# Daily Execution Report",
        "",
        f"**Date:** {TODAY}",
        f"**Run started:** {RUN_STARTED.isoformat()}",
        f"**Total duration:** {total_duration}s",
        "",
        "## Employees Executed",
        "",
        "| # | Employee | Status | Attempts | Duration |",
        "|---|---|---|---|---|",
    ]
    for i, r in enumerate(results, start=1):
        lines.append(f"| {i} | {r['name']} | {r['status']} | {r['attempts']} | {r['durationSeconds']}s |")

    failures = [r for r in results if r["status"] == STATUS_FAILED]
    retried = [r for r in results if r["attempts"] > 1]
    outputs = [(r["name"], o) for r in results for o in r["outputs"]]

    lines += ["", "## Failures", ""]
    if failures:
        for r in failures:
            lines.append(f"- **{r['name']}**: {r['error']} (after {r['attempts']} attempts)")
    else:
        lines.append("_None._")

    lines += ["", "## Retries", ""]
    if retried:
        for r in retried:
            lines.append(f"- **{r['name']}**: {r['attempts']} attempts before {r['status'].lower()}")
    else:
        lines.append("_None needed._")

    lines += ["", "## Outputs Generated", ""]
    if outputs:
        for name, path in outputs:
            lines.append(f"- **{name}**: `{path}`")
    else:
        lines.append("_None detected for today's date._")

    lines += ["", "## Business Impact", ""]
    if business_impact:
        lines.append(f"_Quoted verbatim from {business_impact_employee}'s Daily Summary — the Orchestrator "
                      f"does not compute its own business-impact figures._")
        lines.append("")
        lines.append(business_impact)
    else:
        lines.append("_Not available this run — Daily Brief did not produce a summary "
                      "(see its status above)._")

    return "\n".join(lines) + "\n"


def overall_status(results):
    executable = [r for r in results if r["status"] in (STATUS_SUCCESS, STATUS_FAILED)]
    if not executable:
        return STATUS_SUCCESS
    if all(r["status"] == STATUS_FAILED for r in executable):
        return STATUS_FAILED
    if any(r["status"] == STATUS_FAILED for r in executable):
        return "PARTIAL_FAILURE"
    return STATUS_SUCCESS


def main():
    config = load_config()
    defaults = config["defaults"]
    employees = config["employees"]
    by_key = {e["key"]: e for e in employees}

    log_path, fh = open_log()
    log(fh, f"AOS Orchestrator v1.0 — run started {RUN_STARTED.isoformat()}")

    results = []
    status_by_key = {}
    run_started_monotonic = time.monotonic()

    for employee in employees:
        deps = employee.get("dependsOn", [])
        unmet = [d for d in deps if status_by_key.get(d) not in SATISFIES_DEPENDENCY]
        if unmet:
            unmet_names = [by_key[d]["name"] for d in unmet]
            log(fh, f"{employee['name']}: SKIPPED_DEPENDENCY_FAILED — waiting on {', '.join(unmet_names)}")
            result = {"key": employee["key"], "name": employee["name"],
                      "status": STATUS_SKIPPED_DEPENDENCY_FAILED, "attempts": 0,
                      "durationSeconds": 0, "error": f"upstream failure: {', '.join(unmet_names)}",
                      "outputs": []}
        else:
            result = run_employee(employee, defaults, AOS_DIR, fh)

        results.append(result)
        status_by_key[employee["key"]] = result["status"]

    total_duration = round(time.monotonic() - run_started_monotonic, 2)

    daily_brief_config = by_key.get("daily-brief", {})
    business_impact_path = None
    if daily_brief_config.get("businessImpactSource"):
        business_impact_path = AOS_DIR / daily_brief_config["businessImpactSource"]
    business_impact = extract_business_impact(business_impact_path)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"{TODAY}-daily-execution-report.md"
    report_path.write_text(
        render_report(results, total_duration, business_impact, daily_brief_config.get("name", "Daily Brief")),
        encoding="utf-8",
    )

    status = {
        "schema": {
            "startedAt": "string — ISO 8601 timestamp, UTC",
            "finishedAt": "string — ISO 8601 timestamp, UTC",
            "durationSeconds": "number",
            "employees": "array — one entry per employee, in execution order: key, name, status "
                         "(SUCCESS, FAILED, NOT_EXECUTABLE, SKIPPED_DEPENDENCY_FAILED), attempts, "
                         "durationSeconds, error, outputs",
            "overallStatus": "string — SUCCESS, PARTIAL_FAILURE, or FAILED",
            "failures": "array — employees with status FAILED this run, for 09-CEO-Advisor to read "
                        "as candidate actions (see decision-model.md)",
            "reportPath": "string — this run's Daily Execution Report, relative to the repo root",
            "logPath": "string — this run's full log, relative to the repo root",
        },
        "startedAt": RUN_STARTED.isoformat(),
        "finishedAt": datetime.now(timezone.utc).isoformat(),
        "durationSeconds": total_duration,
        "employees": results,
        "overallStatus": overall_status(results),
        "failures": [r for r in results if r["status"] == STATUS_FAILED],
        "reportPath": str(report_path.relative_to(REPO_ROOT)),
        "logPath": str(log_path.relative_to(REPO_ROOT)),
    }
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
        f.write("\n")

    log(fh, f"Run finished: {status['overallStatus']}. Report: {status['reportPath']}")
    fh.close()

    return 0 if status["overallStatus"] != STATUS_FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
