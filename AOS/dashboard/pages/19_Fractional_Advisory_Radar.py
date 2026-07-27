import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Fractional Advisory Radar", "◎")

st.title("Fractional Advisory Radar")
st.caption(
    "Detects organisations likely to need fractional AI Governance support, by re-reading Demand "
    "Intelligence's own already-collected signals — never a second, independently-scanned feed. "
    "Ranked by expected consulting revenue."
)

if st.button("Refresh Radar", type="primary"):
    with st.spinner("Refreshing the radar..."):
        result = run_script("fractional-advisory-radar/runtime/generate.py", "fractional-advisory-radar/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Fractional Advisory Radar completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Fractional Advisory Radar failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("fractional-advisory-radar/runtime/output/fractional-advisory-radar-feed.json")
orgs = feed.get("organisations", []) if feed_exists and isinstance(feed, dict) else []

st.subheader(f"Organisations, Ranked by Expected Consulting Revenue ({len(orgs)})")

if not orgs:
    st.info(
        "No organisations on the radar yet. Requires at least one organisation already qualified by "
        "Demand Intelligence — click **Refresh Radar** above once one exists."
    )
else:
    stage_filter = st.multiselect("Filter by stage", options=["Urgent", "Enterprise", "Growing", "Emerging"])
    filtered = [o for o in orgs if not stage_filter or o["stage"] in stage_filter]

    rows = [
        {
            "organisation": o["organisation"], "industry": o["industry"], "stage": o["stage"],
            "fractionalAdvisoryPotential": o["fractionalAdvisoryPotential"],
            "recommendedEngagementModel": o["recommendedEngagementModel"],
            "expectedConsultingRevenue": o["expectedConsultingRevenue"]["estimate"],
            "buyingReadinessBand": o["buyingReadinessBand"],
        }
        for o in filtered
    ]
    show_table(
        rows,
        columns=["organisation", "industry", "stage", "fractionalAdvisoryPotential",
                 "recommendedEngagementModel", "expectedConsultingRevenue", "buyingReadinessBand"],
        empty_message="No organisation matches that filter.",
    )

st.divider()
st.subheader("Fractional Advisory Radar Report")
text, exists = load_text_safe(resolve_dated("fractional-advisory-radar/runtime/output/{date}-fractional-advisory-radar-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
