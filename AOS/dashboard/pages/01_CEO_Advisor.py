import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_text_safe
from components.runtime_runner import run_script
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("CEO Advisor", "◆")

st.title("CEO Advisor")
st.caption("Synthesizes every other AI employee's output into ranked priorities and recommendations. Never rewrites their outputs — only reads, prioritizes, and cites its sources.")

if st.button("Run CEO Advisor", type="primary"):
    with st.spinner("Running CEO Advisor — reading all 8 upstream sources..."):
        result = run_script("ceo-advisor/runtime/generate.py", "ceo-advisor/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"CEO Advisor completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"CEO Advisor failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

tab1, tab2, tab3 = st.tabs(["Daily Report", "Weekly Report", "Monthly Business Review"])

with tab1:
    text, exists = load_text_safe("ceo-advisor/runtime/output/ceo-daily-report.md")
    if exists:
        st.markdown(text)
    else:
        st.info("No CEO Daily Report yet. Click **Run CEO Advisor** above.")

with tab2:
    text, exists = load_text_safe("ceo-advisor/runtime/output/ceo-weekly-report.md")
    if exists:
        st.markdown(text)
    else:
        st.info("No CEO Weekly Report yet.")

with tab3:
    text, exists = load_text_safe("ceo-advisor/runtime/output/ceo-monthly-business-review.md")
    if exists:
        st.markdown(text)
    else:
        st.info("No CEO Monthly Business Review yet.")
