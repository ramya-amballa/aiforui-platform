import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.paths import aos_path
from utils.state import bump_refresh

apply_page_config("Sales Director", "▣")

st.title("Sales Director")
st.caption("Prepares one proposal package per qualified opportunity, reading Opportunity Hunter, Revenue Hunter, CRM, and Service Mapping's recommendations.")

if st.button("Generate Proposal", type="primary"):
    with st.spinner("Preparing proposal packages..."):
        result = run_script("sales-director/runtime/prepare.py", "sales-director/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Sales Director completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Sales Director failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("sales-director/runtime/output/ceo-advisor-feed.json")
items = feed.get("feed", []) if feed_exists and isinstance(feed, dict) else []

st.subheader(f"Proposal Packages ({len(items)})")
show_table(
    items,
    columns=["opportunityId", "title", "organisation", "status"],
    empty_message="No proposal packages yet. Click **Generate Proposal** above (requires Opportunity Hunter, Revenue Hunter, and CRM to have run first).",
)

if items:
    st.subheader("Download a Proposal")
    labels = [f"{i['organisation']} — {i['title']} ({i['status']})" for i in items]
    choice = st.selectbox("Select a package", options=range(len(items)), format_func=lambda i: labels[i])
    selected = items[choice]
    package_path = aos_path(selected["packagePath"]) if "packagePath" in selected else None
    if package_path and package_path.exists():
        content = package_path.read_text(encoding="utf-8")
        with st.expander("Preview", expanded=True):
            st.markdown(content)
        st.download_button(
            "Download Proposal",
            data=content,
            file_name=package_path.name,
            mime="text/markdown",
        )
    else:
        st.warning("Package file not found on disk.")

st.divider()
st.subheader("Sales Director Report")
text, exists = load_text_safe(resolve_dated("sales-director/runtime/output/{date}-sales-director-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
