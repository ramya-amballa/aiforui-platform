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

apply_page_config("Company 360", "🔎")

st.title("Company 360")
st.caption(
    "AOS Sprint 19 — a read-only rollup, not a new score. Joins what already exists across Demand "
    "Intelligence, Account Intelligence, CRM, Relationship Intelligence, Reverse Job Hunt, Revenue Hunter's "
    "pipeline, Service Mapping and Delivery Intelligence into one view per organisation. Computes nothing new: "
    "where two employees independently estimate the same kind of thing, both are shown, labelled by source, "
    "never averaged."
)

if st.button("Refresh Company 360", type="primary"):
    with st.spinner("Joining every source per organisation..."):
        result = run_script("company-360/runtime/generate.py", "company-360/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Company 360 completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Company 360 failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("company-360/runtime/output/company-360-feed.json")
companies = feed.get("companies", []) if feed_exists and isinstance(feed, dict) else []

st.subheader(f"Organisations ({len(companies)})")

if not companies:
    st.info(
        "No organisations profiled yet. This requires Demand Intelligence to have run at least once — click "
        "**Refresh Company 360** above once it has."
    )
else:
    show_table(
        companies,
        columns=["organisation", "industry", "buyingReadinessBand", "existingRelationship", "deliveryPhase", "pipelineEntryCount"],
        empty_message="No organisation matches.",
    )

    names = [c["organisation"] for c in companies]
    selected_name = st.selectbox("Select an organisation", options=names)
    selected = next(c for c in companies if c["organisation"] == selected_name)

    profile_path = REPO_ROOT / selected["profilePath"]
    if profile_path.exists():
        st.markdown(profile_path.read_text(encoding="utf-8"))
        st.download_button(
            "Download 360 Profile",
            data=profile_path.read_text(encoding="utf-8"),
            file_name=profile_path.name,
            mime="text/markdown",
        )
    else:
        st.warning("Profile file not found on disk.")

st.divider()
st.subheader("Company 360 Report")
text, exists = load_text_safe(resolve_dated("company-360/runtime/output/{date}-company-360-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
