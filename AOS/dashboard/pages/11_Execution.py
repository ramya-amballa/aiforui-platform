import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe
from components.runtime_runner import run_script
from components.theme import apply_page_config, status_pill
from utils.formatting import format_timestamp
from utils.state import bump_refresh

apply_page_config("Execution", "▶")

st.title("Execution")
st.caption("Runs AOS/orchestrator/orchestrator.py — the single entry point that runs every AI employee in the fixed, dependency-checked order documented in orchestrator/execution-plan.md. This is exactly the same command GitHub Actions runs automatically every day at 06:00 IST.")

run_clicked = st.button("Run Full AOS", type="primary")

if run_clicked:
    progress = st.progress(0, text="Starting Orchestrator...")
    with st.spinner("Running all 11 AI employees in fixed order — this can take a few minutes..."):
        result = run_script("orchestrator/orchestrator.py", "orchestrator", timeout_seconds=1800)
    progress.progress(100, text="Orchestrator finished.")
    if result.ok:
        st.success(f"Run Full AOS completed in {result.duration_seconds}s.")
    else:
        st.error(f"Orchestrator exited with code {result.returncode} after {result.duration_seconds}s.")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)
    bump_refresh()
    st.info("Every page now reads the latest output files — open any employee's page from the sidebar to see the refreshed results.")

st.divider()

st.subheader("Last Run Summary")
status, exists = load_json_safe("output/orchestrator/status.json")
if not exists:
    st.info("AOS has not been run yet. Click **Run Full AOS** above.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Status", status.get("overallStatus", "-"))
    with col2:
        st.metric("Finished At", format_timestamp(status.get("finishedAt")))
    with col3:
        st.metric("Duration (s)", status.get("durationSeconds", "-"))

    st.markdown("**Per-Employee Results**")
    kind_map = {"SUCCESS": "ok", "NOT_EXECUTABLE": "idle", "FAILED": "fail", "SKIPPED_DEPENDENCY_FAILED": "warn"}
    for e in status.get("employees", []):
        kind = kind_map.get(e.get("status"), "idle")
        st.markdown(
            f"- **{e.get('name')}** {status_pill(e.get('status'), kind)} "
            f"— {e.get('durationSeconds', 0)}s, {e.get('attempts', 0)} attempt(s)"
            + (f" — _{e.get('error')}_" if e.get("error") else ""),
            unsafe_allow_html=True,
        )

    report_path = status.get("reportPath")
    if report_path:
        text, report_exists = load_text_safe(report_path.replace("AOS/", "", 1) if report_path.startswith("AOS/") else report_path)
        if report_exists:
            with st.expander("Full Daily Execution Report"):
                st.markdown(text)
