import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.paths import REPO_ROOT
from utils.state import bump_refresh

apply_page_config("Reverse Job Hunt", "▶")

st.title("Reverse Job Hunt")
st.caption(
    "Proactive business development, not reactive opportunity finding. For every organisation Demand "
    "Intelligence has already qualified: why to pursue them, entry point, probability of engagement, "
    "timeline and a 90-day action sequence — an internal playbook, not a proposal. Each strategy now also "
    "includes a Client Acquisition Campaign (Sprint 16): a draft LinkedIn connection request, a follow-up "
    "message, the recommended asset to share first, and campaign status tracked in touchpoint-log.json. "
    "Additive and downstream only; does not modify any existing scoring logic."
)

if st.button("Generate Strategies", type="primary"):
    with st.spinner("Generating reverse job hunt strategies..."):
        result = run_script("reverse-job-hunt/runtime/generate.py", "reverse-job-hunt/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Reverse Job Hunt completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Reverse Job Hunt failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("output/reverse-job-hunt/reverse-job-hunt-feed.json")
strategies = feed.get("strategies", []) if feed_exists and isinstance(feed, dict) else []

st.subheader(f"Companies, Sorted by Expected Consulting ROI ({len(strategies)})")

if not strategies:
    st.info(
        "No reverse job hunt strategies yet. Requires at least one organisation already qualified by "
        "Demand Intelligence (organisation-profiles.json) — click **Generate Strategies** above once "
        "Demand Intelligence has found one."
    )
else:
    ranked = sorted(strategies, key=lambda s: s["expectedConsultingRoi"] if s["expectedConsultingRoi"] is not None else -1, reverse=True)

    search = st.text_input("Search by company")
    filtered = [s for s in ranked if search.lower() in s["organisation"].lower()] if search else ranked

    show_table(
        filtered,
        columns=["organisation", "industry", "expectedConsultingRoi", "buyingReadinessBand",
                 "entryPoint", "probabilityOfEngagement", "recommendedTimeline", "lastSeen",
                 "campaignStatus", "touchpointCount", "assetToShareFirst"],
        empty_message="No organisation matches that search.",
    )

    if filtered:
        st.subheader("Strategy")
        labels = [f"{s['organisation']} — ROI {s['expectedConsultingRoi']} ({s['entryPoint']})" for s in filtered]
        choice = st.selectbox("Select an organisation", options=range(len(filtered)), format_func=lambda i: labels[i])
        selected = filtered[choice]

        # strategyPath is written by generate.py relative to the repo
        # root (not AOS/), the same convention sales-director's
        # packagePath and account-intelligence's briefPath both use —
        # resolve via REPO_ROOT, not aos_path().
        strategy_path = REPO_ROOT / selected["strategyPath"] if selected.get("strategyPath") else None
        if strategy_path and strategy_path.exists():
            content = strategy_path.read_text(encoding="utf-8")
            st.markdown(content)
            st.download_button(
                "Download Strategy",
                data=content,
                file_name=strategy_path.name,
                mime="text/markdown",
            )
        else:
            st.warning("Strategy file not found on disk.")

st.divider()
st.subheader("Reverse Job Hunt Report")
text, exists = load_text_safe(resolve_dated("output/reverse-job-hunt/{date}-reverse-job-hunt-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
