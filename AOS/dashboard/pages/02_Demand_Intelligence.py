import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import list_data_records, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Demand Intelligence", "▲")

st.title("Demand Intelligence")
st.caption(
    "Formerly Opportunity Hunter. Answers \"who is most likely to need AI for U&I's services this week\" — "
    "led by Demand Signals (named organisations reported adopting AI at scale, before they ever advertise a "
    "vacancy), plus targeted job-board channels (Upwork, Greenhouse, Lever, Ashby, RemoteOK)."
)

if st.button("Scan Opportunities", type="primary"):
    with st.spinner("Collecting from all configured sources..."):
        result = run_script("demand-intelligence/runtime/collect.py", "demand-intelligence/runtime", timeout_seconds=600)
    if result.ok:
        st.success(f"Scan completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Scan failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

opportunities = list_data_records("demand-intelligence/opportunity-schema.json", "opportunities")
demand_signal_opps = [o for o in opportunities if o.get("source") == "Demand Signal"]

tab_all, tab_signals = st.tabs([f"All Opportunities ({len(opportunities)})", f"Demand Signals ({len(demand_signal_opps)})"])
columns = ["id", "dateFound", "source", "sourceCategory", "title", "organisation",
           "classification", "relevanceScore", "priorityScore", "band"]

with tab_all:
    show_table(
        opportunities, columns=columns,
        empty_message="No opportunities collected yet. Click **Scan Opportunities** above.",
    )

with tab_signals:
    show_table(
        demand_signal_opps, columns=columns,
        empty_message="No demand signals yet. Requires ANTHROPIC_API_KEY to be configured (see Settings) — "
                       "click **Scan Opportunities** above once it is.",
    )

st.divider()
st.subheader("Today's Collection Report")
report_text, exists = load_text_safe(resolve_dated("demand-intelligence/runtime/output/{date}-daily-report.md"))
if exists:
    st.markdown(report_text)
else:
    st.info("No daily report for today yet.")
