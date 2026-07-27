import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Tender Intelligence", "📋")

st.title("Tender Intelligence")
st.caption(
    "Monitors real, founder-configured procurement RSS/Atom feeds (Government, Banking, Healthcare, UN, "
    "World Bank, ADB, EU, UAE, Public AI Governance) for tenders matching AI Governance, Responsible AI, "
    "Technology Risk, GRC, Cyber Risk, Vendor Risk, or Compliance. The Fit Score is an explicit relevance "
    "heuristic, not a claim of true win probability — AOS has no historical tender outcome data yet."
)

if st.button("Refresh Tender Intelligence", type="primary"):
    with st.spinner("Refreshing tender intelligence..."):
        result = run_script("tender-intelligence/runtime/generate.py", "tender-intelligence/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Tender Intelligence completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Tender Intelligence failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("tender-intelligence/runtime/output/tender-intelligence-feed.json")
tenders = feed.get("tenders", []) if feed_exists and isinstance(feed, dict) else []

st.subheader(f"Tenders, Sorted by Estimated Value ({len(tenders)})")

if not tenders:
    st.info(
        "No tenders tracked yet. This connector does nothing until real procurement feed URLs are added to "
        "tender-intelligence/runtime/config/tender-intelligence-config.json's feedUrls — then click "
        "**Refresh Tender Intelligence** above."
    )
else:
    col1, col2 = st.columns(2)
    with col1:
        source_types = sorted({t["sourceType"] for t in tenders})
        source_filter = st.multiselect("Filter by source type", options=source_types)
    with col2:
        band_filter = st.multiselect("Filter by fit band", options=["High", "Medium", "Low"])

    filtered = [
        t for t in tenders
        if (not source_filter or t["sourceType"] in source_filter)
        and (not band_filter or t["fitBand"] in band_filter)
    ]

    rows = [
        {
            "title": t["title"], "sourceType": t["sourceType"], "matchedDomains": ", ".join(t["matchedDomains"]),
            "estimatedValue": t["estimatedValue"], "fitScore": t["fitScore"], "fitBand": t["fitBand"],
            "deadline": t["deadline"],
        }
        for t in filtered
    ]
    show_table(
        rows,
        columns=["title", "sourceType", "matchedDomains", "estimatedValue", "fitScore", "fitBand", "deadline"],
        empty_message="No tender matches those filters.",
    )

    titles = [t["title"] for t in filtered]
    if titles:
        selected_title = st.selectbox("Select a tender for detail", options=titles)
        selected = next(t for t in filtered if t["title"] == selected_title)

        c1, c2, c3 = st.columns(3)
        c1.metric("Fit Score", f"{selected['fitScore']}/100", selected["fitBand"])
        c2.metric("Estimated Value", selected["estimatedValue"])
        c3.metric("Deadline", selected["deadline"])

        st.markdown(f"**Source:** [{selected['sourceUrl']}]({selected['sourceUrl']})" if selected.get("sourceUrl") else "**Source:** Not specified")
        st.markdown(f"**Summary:** {selected['tenderSummary']}")
        st.markdown(f"**Eligibility:** {selected['eligibility']}")
        st.markdown(f"**Required Partners:** {selected['requiredPartners']}")
        st.markdown(f"**Recommended Response:** {selected['recommendedResponse']}")

st.divider()
st.subheader("Tender Intelligence Report")
text, exists = load_text_safe(resolve_dated("tender-intelligence/runtime/output/{date}-tender-intelligence-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
