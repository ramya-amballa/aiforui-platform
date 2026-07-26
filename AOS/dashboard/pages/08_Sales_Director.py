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

apply_page_config("Sales Director", "▣")

st.title("Sales Director")
st.caption("Prepares one proposal package per qualified opportunity, reading Demand Intelligence, Revenue Hunter, CRM, and Service Mapping's recommendations.")

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
    empty_message="No proposal packages yet. Click **Generate Proposal** above (requires Demand Intelligence, Revenue Hunter, and CRM to have run first).",
)

# One standalone file per artifact (prepare.py's write_package_files()),
# so each can be previewed/copied/downloaded independently rather than
# only as one combined package.
SECTIONS = [
    ("📄", "Proposal", "proposalPath"),
    ("📧", "Cover Letter", "coverLetterPath"),
    ("💬", "Recruiter Message", "recruiterMessagePath"),
    ("📧", "Client Outreach", "clientOutreachPath"),
]


def resolve(selected, path_key):
    # Every path prepare.py writes (packagePath and the four section
    # paths below) is relative to the repo root, not AOS/ — resolve via
    # REPO_ROOT, not aos_path() (which is AOS/-relative and would
    # double the "AOS/" prefix).
    value = selected.get(path_key)
    return REPO_ROOT / value if value else None


if items:
    st.subheader("Proposal Package")
    labels = [f"{i['organisation']} — {i['title']} ({i['status']})" for i in items]
    choice = st.selectbox("Select a package", options=range(len(items)), format_func=lambda i: labels[i])
    selected = items[choice]

    for emoji, label, path_key in SECTIONS:
        st.markdown(f"#### {emoji} {label}")
        section_path = resolve(selected, path_key)
        if not section_path or not section_path.exists():
            st.warning(f"{label} file not found on disk.")
            st.divider()
            continue

        content = section_path.read_text(encoding="utf-8")
        with st.expander("Preview", expanded=True):
            st.markdown(content)

        col_download, col_copy = st.columns(2)
        with col_download:
            st.download_button(
                "Download",
                data=content,
                file_name=section_path.name,
                mime="text/markdown",
                key=f"download-{path_key}-{choice}",
            )
        with col_copy:
            with st.popover("Copy"):
                st.caption("Click the copy icon in the top-right corner of the box below.")
                st.code(content, language=None)
        st.divider()

    package_path = resolve(selected, "packagePath")
    if package_path and package_path.exists():
        with st.expander("Full combined package (all sections in one file)"):
            st.download_button(
                "Download Full Package",
                data=package_path.read_text(encoding="utf-8"),
                file_name=package_path.name,
                mime="text/markdown",
                key=f"download-full-{choice}",
            )

st.divider()
st.subheader("Sales Director Report")
text, exists = load_text_safe(resolve_dated("sales-director/runtime/output/{date}-sales-director-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
