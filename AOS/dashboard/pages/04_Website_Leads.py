import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Website Leads", "✉")

st.title("Website Leads")
st.caption("Every enquiry submitted through the AI for U&I website (Contact form / Start a Conversation, reached from ADGL, OPERA, and Selected Engagement Areas) becomes a Lead ID here, then an opportunity, CRM record, pipeline entry, and Service Mapping recommendation — automatically, with no email sent from this runtime.")

if st.button("Refresh Website Leads", type="primary"):
    with st.spinner("Processing any new website submissions..."):
        result = run_script("website-intake/runtime/generate.py", "website-intake/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Website Intake completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Website Intake failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

leads_data, leads_exist = load_json_safe("website-intake/leads.json")
leads = list(leads_data.get("leads", {}).values()) if leads_exist and isinstance(leads_data, dict) else []

st.subheader(f"Website Enquiries ({len(leads)})")

rows = []
for lead in leads:
    qualification = lead.get("qualification", {}) or {}
    sales_package = lead.get("salesPackage", {}) or {}
    rows.append({
        "leadId": lead.get("leadId"),
        "dateReceived": lead.get("dateReceived"),
        "organisation": lead.get("organisation"),
        "sourcePage": lead.get("sourcePage"),
        "leadClassification": lead.get("leadClassification"),
        "urgency": qualification.get("urgency"),
        "recommendedService": sales_package.get("recommendedService") or "pending",
        "recommendedProposalTemplate": sales_package.get("recommendedProposalTemplate") or "pending",
        "opportunityId": lead.get("opportunityId") or "pending",
    })

show_table(
    rows,
    columns=["leadId", "dateReceived", "organisation", "sourcePage", "leadClassification",
             "urgency", "recommendedService", "recommendedProposalTemplate", "opportunityId"],
    empty_message="No website leads yet. Enquiries land in runtime/inbox/ from the live site; click **Refresh Website Leads** once one has arrived.",
)

st.divider()
st.subheader("Latest Intake Report")
report_text, exists = load_text_safe("website-intake/runtime/output/website-intake-report.md")
if exists:
    st.markdown(report_text)
else:
    st.info("No intake report yet.")
