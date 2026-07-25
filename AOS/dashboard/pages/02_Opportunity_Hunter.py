import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import list_data_records, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Opportunity Hunter", "▲")

st.title("Opportunity Hunter")
st.caption("Collects, filters, scores, and routes opportunities from Upwork, LinkedIn Jobs, Wellfound, RemoteOK, Greenhouse, Lever, Ashby and more.")

if st.button("Scan Opportunities", type="primary"):
    with st.spinner("Collecting from all configured sources..."):
        result = run_script("opportunity-hunter/runtime/collect.py", "opportunity-hunter/runtime", timeout_seconds=600)
    if result.ok:
        st.success(f"Scan completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Scan failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

opportunities = list_data_records("opportunity-hunter/opportunity-schema.json", "opportunities")
st.subheader(f"Opportunities ({len(opportunities)})")
show_table(
    opportunities,
    columns=["id", "dateFound", "source", "sourceCategory", "title", "organisation",
             "classification", "relevanceScore", "priorityScore", "band"],
    empty_message="No opportunities collected yet. Click **Scan Opportunities** above.",
)

st.divider()
st.subheader("Today's Collection Report")
report_text, exists = load_text_safe(resolve_dated("opportunity-hunter/runtime/output/{date}-daily-report.md"))
if exists:
    st.markdown(report_text)
else:
    st.info("No daily report for today yet.")
