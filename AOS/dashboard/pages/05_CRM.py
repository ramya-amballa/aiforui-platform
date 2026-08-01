import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import list_data_records, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("CRM", "●")

st.title("CRM")
st.caption("Recruiter and client relationship records: temperature, follow-up cadence, and next actions. relationshipTemperature/nextFollowUpDue/outreachHistory are owned exclusively by Sales Director.")

if st.button("Open CRM", type="primary"):
    with st.spinner("Refreshing CRM reports..."):
        result = run_script("crm/runtime/generate.py", "crm/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"CRM refresh completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"CRM refresh failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

companies = list_data_records("06-CRM/company-intelligence.json", "companies")

recruiters = [c for c in companies if c.get("recruiter")]
clients = [c for c in companies if (c.get("existingRelationship") or "").lower() in ("active client", "prior client")]
follow_ups = [c for c in companies if c.get("nextFollowUpDue")]

tab_all, tab_recruiters, tab_clients, tab_followups = st.tabs(
    ["All Companies", f"Recruiters ({len(recruiters)})", f"Clients ({len(clients)})", f"Follow-ups ({len(follow_ups)})"]
)

columns = ["companyName", "industry", "existingRelationship", "recruiter",
           "relationshipTemperature", "nextFollowUpDue"]

with tab_all:
    show_table(companies, columns=columns, empty_message="No CRM records yet. Click **Open CRM** above.")

with tab_recruiters:
    show_table(recruiters, columns=columns, empty_message="No recruiter relationships yet.")

with tab_clients:
    show_table(clients, columns=columns, empty_message="No client relationships yet.")

with tab_followups:
    show_table(
        sorted(follow_ups, key=lambda c: c.get("nextFollowUpDue", "")),
        columns=["companyName", "relationshipTemperature", "nextFollowUpDue", "recruiter"],
        empty_message="No follow-ups due.",
    )

st.divider()
st.subheader("Latest Reports")
r1, r2, r3 = st.tabs(["Daily Follow-Up Queue", "Relationship Health", "Stale Relationship Alerts"])
with r1:
    text, exists = load_text_safe(resolve_dated("output/crm/{date}-daily-follow-up-queue.md"))
    st.markdown(text) if exists else st.info("No follow-up queue for today yet.")
with r2:
    text, exists = load_text_safe(resolve_dated("output/crm/{date}-relationship-health-report.md"))
    st.markdown(text) if exists else st.info("No relationship health report for today yet.")
with r3:
    text, exists = load_text_safe(resolve_dated("output/crm/{date}-stale-relationship-alerts.md"))
    st.markdown(text) if exists else st.info("No stale relationship alerts for today yet.")
