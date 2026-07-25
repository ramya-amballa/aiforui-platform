import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import list_data_records, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Product Manager", "◫")

st.title("Product Manager")
st.caption("Evaluates product candidates from Market Intelligence, Demand Intelligence, Sales Director's recurring domains, and Content Director's signals.")

if st.button("Review Product Ideas", type="primary"):
    with st.spinner("Evaluating backlog candidates..."):
        result = run_script("product-manager/runtime/generate.py", "product-manager/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Product Manager completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Product Manager failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

backlog = list_data_records("03-Product-Manager/product-backlog.json", "backlog")
st.subheader(f"Product Backlog ({len(backlog)})")

tab_all, tab_candidate, tab_dev, tab_shipped = st.tabs(["All", "Candidate", "In Development", "Shipped"])
columns = ["id", "dateAdded", "signalSource", "proposedFormat", "score", "status", "revenueOrLeadPotential", "owner"]

with tab_all:
    show_table(backlog, columns=columns, empty_message="No backlog items yet. Click **Review Product Ideas** above.")
with tab_candidate:
    show_table([b for b in backlog if b.get("status") == "candidate"], columns=columns, empty_message="No candidates.")
with tab_dev:
    show_table([b for b in backlog if b.get("status") == "in-development"], columns=columns, empty_message="Nothing in development.")
with tab_shipped:
    show_table([b for b in backlog if b.get("status") == "shipped"], columns=columns, empty_message="Nothing shipped yet.")

st.divider()
st.subheader("Product Manager Report")
text, exists = load_text_safe(resolve_dated("product-manager/runtime/output/{date}-product-manager-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
