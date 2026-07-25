import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Service Mapping", "◈")

st.title("Service Mapping Engine")
st.caption("For every opportunity: Primary Service, Secondary Services, Recommended Engagement Type, Estimated Project Size, Recommended Proposal Template, and Cross-Sell Opportunities — deterministic, never re-scored.")

if st.button("Run Service Mapping", type="primary"):
    with st.spinner("Mapping opportunities to services..."):
        result = run_script("service-mapping/runtime/generate.py", "service-mapping/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Service Mapping completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Service Mapping failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

data, exists = load_json_safe("service-mapping/service-recommendations.json")
recommendations = list(data.get("recommendations", {}).values()) if exists and isinstance(data, dict) else []

st.subheader(f"Service Recommendations ({len(recommendations)})")

rows = []
for r in recommendations:
    if r.get("notApplicable"):
        continue
    rows.append({
        "title": r.get("title"),
        "organisation": r.get("organisation"),
        "primaryService": r.get("primaryService"),
        "secondaryServices": ", ".join(r.get("secondaryServices") or []),
        "recommendedEngagementType": r.get("recommendedEngagementType"),
        "estimatedProjectSize": r.get("estimatedProjectSize"),
        "recommendedProposalTemplate": r.get("recommendedProposalTemplate"),
        "crossSellOpportunities": ", ".join(r.get("crossSellOpportunities") or []),
    })

show_table(
    rows,
    columns=["title", "organisation", "primaryService", "secondaryServices", "recommendedEngagementType",
             "estimatedProjectSize", "recommendedProposalTemplate", "crossSellOpportunities"],
    empty_message="No service recommendations yet. Click **Run Service Mapping** above (requires Demand Intelligence to have run first).",
)

st.divider()
st.subheader("Service Recommendation Report")
text, text_exists = load_text_safe("service-mapping/runtime/output/service-recommendation-report.md")
if text_exists:
    st.markdown(text)
else:
    st.info("No report yet.")
