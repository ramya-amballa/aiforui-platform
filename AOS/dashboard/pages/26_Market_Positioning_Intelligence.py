import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Market Positioning Intelligence", "🧭")

st.title("Market Positioning Intelligence")
st.caption(
    "AOS Sprint 21. There is no competitor, market-share, or win/loss data source anywhere in AOS — "
    "confirmed before this employee was built, and stated plainly below rather than filled in with an "
    "invented number. This page instead shows where AI for U&I's own service catalogue stands relative to "
    "real demand and regulatory signal AOS already tracks."
)

if st.button("Refresh Market Positioning Intelligence", type="primary"):
    with st.spinner("Aggregating service demand coverage and regulatory tailwinds..."):
        result = run_script("market-positioning-intelligence/runtime/generate.py",
                             "market-positioning-intelligence/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Market Positioning Intelligence completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Market Positioning Intelligence failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("market-positioning-intelligence/runtime/output/market-positioning-feed.json")
feed = feed if feed_exists and isinstance(feed, dict) else {}

st.subheader("Service Demand Coverage")
st.caption("How many real, already-mapped opportunities recommended each catalogue service.")
show_table(feed.get("serviceDemandCoverage", []), columns=["service", "recommendationCount"],
           empty_message="No service catalogue loaded yet.")

st.subheader("Regulatory Tailwinds")
st.metric("Substantive regulatory developments logged", feed.get("substantiveRegulatoryDevelopmentCount", 0))
show_table(feed.get("regulatoryTailwinds", []), columns=["source", "developmentCount"],
           empty_message="No substantive regulatory development logged yet.")

st.subheader("Competitive Signal")
st.warning(feed.get("competitiveSignal", "Not tracked — AOS has no data source for competitor activity, market share or competitive pricing."))
lost = feed.get("lostOpportunities", [])
st.metric("Lost opportunities on record", len(lost))
if lost:
    show_table(lost, columns=["organisation", "title"], empty_message="No lost opportunities on record.")
    st.caption("Organisation and title only — no competitor name or loss reason is tracked anywhere in AOS.")

st.divider()
st.subheader("Market Positioning Report")
text, exists = load_text_safe(resolve_dated("market-positioning-intelligence/runtime/output/{date}-market-positioning-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
