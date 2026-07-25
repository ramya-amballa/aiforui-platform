import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Market Intelligence", "◇")

st.title("Market Intelligence")
st.caption("Monitors configured sources for regulatory, competitive, and consulting-demand signals, and routes structured records to Content Director, Product Manager, Demand Intelligence, and CEO Advisor.")

if st.button("Check Market", type="primary"):
    with st.spinner("Checking configured sources..."):
        result = run_script("05-Market-Intelligence/runtime/monitor.py", "05-Market-Intelligence/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Market check completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Market check failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

st.subheader("New Developments")
report_text, exists = load_text_safe(resolve_dated("05-Market-Intelligence/runtime/output/{date}-market-intelligence-report.md"))
if exists:
    st.markdown(report_text)
else:
    st.info("No market intelligence report for today yet. Click **Check Market** above.")
