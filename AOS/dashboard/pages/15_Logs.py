import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, today_str
from components.theme import apply_page_config
from utils.paths import aos_path

apply_page_config("Logs", "▤")

st.title("Logs")
st.caption("Today's Orchestrator execution log, plus every employee's own runtime log directory.")

status, status_exists = load_json_safe("orchestrator/status.json")

st.subheader("Today's Execution Log")
logs_dir = aos_path("orchestrator", "logs")
today_logs = sorted(logs_dir.glob(f"{today_str()}-*-orchestrator.log")) if logs_dir.is_dir() else []

if today_logs:
    latest_log = today_logs[-1]
    st.caption(f"`{latest_log.relative_to(aos_path())}`")
    st.code(latest_log.read_text(encoding="utf-8"), language="text")
else:
    st.info("No Orchestrator log for today yet. Run **Run Full AOS** from the Execution page.")

st.divider()

st.subheader("Errors")
if status_exists:
    failures = status.get("failures", [])
    if failures:
        for f in failures:
            st.error(f"**{f.get('name')}**: {f.get('error')} (after {f.get('attempts')} attempts)")
    else:
        st.success("No failures in the last run.")
else:
    st.info("No run recorded yet.")

st.subheader("Warnings")
if status_exists:
    skipped = [e for e in status.get("employees", []) if e.get("status") == "SKIPPED_DEPENDENCY_FAILED"]
    if skipped:
        for e in skipped:
            st.warning(f"**{e.get('name')}** was skipped — a dependency failed.")
    else:
        st.success("No warnings in the last run.")
else:
    st.info("No run recorded yet.")

st.subheader("Completed Tasks")
if status_exists:
    completed = [e for e in status.get("employees", []) if e.get("status") in ("SUCCESS", "NOT_EXECUTABLE")]
    for e in completed:
        note = "not yet implemented" if e.get("status") == "NOT_EXECUTABLE" else f"{e.get('durationSeconds')}s, {e.get('attempts')} attempt(s)"
        st.markdown(f"- **{e.get('name')}** — {e.get('status')} ({note})")
    if not completed:
        st.info("Nothing completed yet.")
else:
    st.info("No run recorded yet.")

st.divider()

st.subheader("Per-Employee Log Directories")
employee_log_dirs = {
    "Market Intelligence": "05-Market-Intelligence/runtime/logs",
    "Website Intake": "website-intake/runtime/logs",
    "Demand Intelligence": "demand-intelligence/runtime",
    "Revenue Hunter": "revenue-hunter/runtime/logs",
    "CRM": "crm/runtime/logs",
    "Service Mapping": "service-mapping/runtime/logs",
    "Sales Director": "sales-director/runtime",
    "Product Manager": "product-manager/runtime/logs",
    "Content Director": "content-director/runtime/logs",
    "Orchestrator": "orchestrator/logs",
}
choice = st.selectbox("View a log directory", options=list(employee_log_dirs.keys()))
log_dir = aos_path(employee_log_dirs[choice])
if log_dir.is_dir():
    files = sorted([p for p in log_dir.iterdir() if p.is_file() and not p.name.startswith(".")],
                    key=lambda p: p.stat().st_mtime, reverse=True)
    if files:
        selected_file = st.selectbox("File", options=files, format_func=lambda p: p.name)
        st.code(selected_file.read_text(encoding="utf-8"), language="text")
    else:
        st.info("No log files yet.")
else:
    st.info("No log directory found.")
