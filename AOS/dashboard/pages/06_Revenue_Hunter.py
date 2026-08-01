import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import list_data_records, load_text_safe
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Revenue Hunter", "$")

st.title("Revenue Hunter")
st.caption("Scores and forecasts the revenue pipeline: Priority, Active, and Deferred bands, plus month-by-month forecasting.")

if st.button("Update Forecast", type="primary"):
    with st.spinner("Scoring pipeline and rebuilding forecast..."):
        result = run_script("revenue-hunter/runtime/generate.py", "revenue-hunter/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Forecast updated in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Update failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

pipeline = list_data_records("08-Revenue-Hunter/pipeline.json", "pipeline")
st.subheader(f"Pipeline ({len(pipeline)})")
show_table(
    pipeline,
    columns=["id", "title", "organisation", "type", "expectedRevenue", "score", "band",
             "stage", "nextAction", "nextActionDue", "expectedCloseDate"],
    empty_message="No pipeline entries yet. Click **Update Forecast** above.",
)

st.divider()
tab1, tab2 = st.tabs(["Revenue Dashboard", "Revenue Forecast"])
with tab1:
    text, exists = load_text_safe("output/revenue-hunter/revenue-dashboard.md")
    st.markdown(text) if exists else st.info("No revenue dashboard yet.")
with tab2:
    text, exists = load_text_safe("output/revenue-hunter/revenue-forecast.md")
    st.markdown(text) if exists else st.info("No revenue forecast yet.")
