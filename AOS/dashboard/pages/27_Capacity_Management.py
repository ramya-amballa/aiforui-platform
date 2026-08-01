import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Capacity Management", "⏳")

st.title("Capacity Management")
st.caption(
    "AOS Sprint 22 — the sixth and final capability. AI for U&I is one person. Every effort estimate below is "
    "Sales Director's own rate-card typicalDays range, reused verbatim — never a second, independently-invented "
    "number. Advisory only: never blocks a proposal from being prepared or changes a priority ranking."
)

if st.button("Refresh Capacity Management", type="primary"):
    with st.spinner("Aggregating active and incoming workload..."):
        result = run_script("capacity-management/runtime/generate.py", "capacity-management/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Capacity Management completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Capacity Management failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("output/capacity-management/capacity-feed.json")
feed = feed if feed_exists and isinstance(feed, dict) else {}

status = feed.get("capacityStatus", "Not enough signal yet")
status_colors = {"Available Capacity": "green", "Near Capacity": "orange", "Over Capacity": "red"}
color = status_colors.get(status)
if color:
    st.markdown(f"## Capacity Status: :{color}[{status}]")
else:
    st.markdown(f"## Capacity Status: {status}")

min_weeks, max_weeks = feed.get("weeksOfCommittedWorkMin"), feed.get("weeksOfCommittedWorkMax")
if min_weeks is not None:
    st.metric("Weeks of committed work at your available pace",
              f"{min_weeks}-{max_weeks}",
              help=f"At {feed.get('foundersAvailableDaysPerWeek')} available days/week (capacity-management/runtime/config/capacity-config.json)")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Active Engagements ({len(feed.get('activeEngagements', []))})")
    st.caption(f"Estimated days: {feed.get('activeEstimatedDaysMin', 0)}-{feed.get('activeEstimatedDaysMax', 0)}")
    show_table(feed.get("activeEngagements", []), columns=["organisation", "title", "type", "phase", "estimatedDaysMin", "estimatedDaysMax"],
               empty_message="No active engagements on record.")

with col2:
    st.subheader(f"Incoming Pipeline ({len(feed.get('pendingProposals', []))})")
    st.caption(f"Estimated days: {feed.get('pendingEstimatedDaysMin', 0)}-{feed.get('pendingEstimatedDaysMax', 0)}")
    show_table(feed.get("pendingProposals", []), columns=["organisation", "title", "status", "engagementType", "estimatedDaysMin", "estimatedDaysMax"],
               empty_message="No pending proposals on record.")

st.divider()
st.subheader("Capacity Report")
text, exists = load_text_safe(resolve_dated("output/capacity-management/{date}-capacity-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
