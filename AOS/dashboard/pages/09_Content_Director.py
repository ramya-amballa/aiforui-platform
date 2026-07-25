import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.theme import apply_page_config
from utils.paths import aos_path
from utils.state import bump_refresh

apply_page_config("Content Director", "✎")

st.title("Content Director")
st.caption("Turns Market Intelligence signals, Opportunity Hunter's content-worthy items, and Product Manager's shipped products into ready drafts: LinkedIn, newsletter, and website.")

if st.button("Generate Content", type="primary"):
    with st.spinner("Generating drafts..."):
        result = run_script("content-director/runtime/generate.py", "content-director/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Content Director completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Content Director failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

drafts_dir = aos_path("content-director", "runtime", "output", "drafts")
drafts = sorted(drafts_dir.glob("*.md")) if drafts_dir.is_dir() else []

by_format = {"linkedin": [], "newsletter": [], "website": [], "product": []}
for path in drafts:
    for fmt in by_format:
        if path.stem.endswith(f"-{fmt}"):
            by_format[fmt].append(path)
            break

tab_linkedin, tab_newsletter, tab_website, tab_product = st.tabs(
    [f"LinkedIn ({len(by_format['linkedin'])})", f"Newsletter ({len(by_format['newsletter'])})",
     f"Website ({len(by_format['website'])})", f"Product Announcements ({len(by_format['product'])})"]
)

def render_drafts(paths, empty_message):
    if not paths:
        st.info(empty_message)
        return
    for path in paths:
        with st.expander(path.stem):
            st.markdown(path.read_text(encoding="utf-8"))

with tab_linkedin:
    render_drafts(by_format["linkedin"], "No LinkedIn drafts yet. Click **Generate Content** above.")
with tab_newsletter:
    render_drafts(by_format["newsletter"], "No newsletter drafts yet.")
with tab_website:
    render_drafts(by_format["website"], "No website drafts yet.")
with tab_product:
    render_drafts(by_format["product"], "No product announcement drafts yet.")

st.divider()
st.subheader("Content Director Report")
text, exists = load_text_safe(resolve_dated("content-director/runtime/output/{date}-content-director-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
