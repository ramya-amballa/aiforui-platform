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

apply_page_config("Account Intelligence", "◆")

st.title("Account Intelligence")
st.caption(
    "Internal strategic briefings for every organisation Demand Intelligence has already qualified — "
    "not a proposal. Answers why this company matters, who to contact, what governance problems they "
    "likely face, which services fit, and what the first conversation should sound like. Additive and "
    "downstream only; never modifies Demand Intelligence's own data."
)

if st.button("Generate Briefs", type="primary"):
    with st.spinner("Generating account intelligence briefs..."):
        result = run_script("account-intelligence/runtime/generate.py", "account-intelligence/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Account Intelligence completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Account Intelligence failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("output/account-intelligence/account-intelligence-feed.json")
briefs = feed.get("briefs", []) if feed_exists and isinstance(feed, dict) else []

st.subheader(f"Qualified Organisations ({len(briefs)})")

if not briefs:
    st.info(
        "No account intelligence briefs yet. Requires at least one organisation already qualified by "
        "Demand Intelligence (organisation-profiles.json) — click **Generate Briefs** above once Demand "
        "Intelligence has found one."
    )
else:
    search = st.text_input("Search by company")
    filtered = [b for b in briefs if search.lower() in b["organisation"].lower()] if search else briefs

    show_table(
        filtered,
        columns=["organisation", "industry", "region", "buyingReadinessBand", "outreachStrategy", "overallPriority", "lastSeen"],
        empty_message="No organisation matches that search.",
    )

    if filtered:
        st.subheader("Brief")
        labels = [f"{b['organisation']} — {b['industry']} ({b['buyingReadinessBand']})" for b in filtered]
        choice = st.selectbox("Select an organisation", options=range(len(filtered)), format_func=lambda i: labels[i])
        selected = filtered[choice]

        # briefPath is written by generate.py relative to the repo root
        # (not AOS/), the same convention sales-director's packagePath
        # uses — resolve via REPO_ROOT, not aos_path().
        brief_path = REPO_ROOT / selected["briefPath"] if selected.get("briefPath") else None
        if brief_path and brief_path.exists():
            content = brief_path.read_text(encoding="utf-8")
            st.markdown(content)
            st.download_button(
                "Download Brief",
                data=content,
                file_name=brief_path.name,
                mime="text/markdown",
            )
        else:
            st.warning("Brief file not found on disk.")

st.divider()
st.subheader("Account Intelligence Report")
text, exists = load_text_safe(resolve_dated("output/account-intelligence/{date}-account-intelligence-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
