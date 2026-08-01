import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Recruiter Intelligence", "☎")

st.title("Recruiter Intelligence")
st.caption(
    "A knowledge base of every recruiter and consulting contact, built from real Recruiter/Consulting "
    "Channel opportunities and CRM relationship data — never a separately-fabricated source."
)

if st.button("Refresh Recruiter Intelligence", type="primary"):
    with st.spinner("Refreshing recruiter intelligence..."):
        result = run_script("recruiter-intelligence/runtime/generate.py", "recruiter-intelligence/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Recruiter Intelligence completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Recruiter Intelligence failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("output/recruiter-intelligence/recruiter-intelligence-feed.json")
contacts = feed.get("contacts", []) if feed_exists and isinstance(feed, dict) else []

st.subheader(f"Contacts ({len(contacts)})")

if not contacts:
    st.info(
        "No recruiter or consulting contacts yet. Requires at least one Recruiter Channel/Consulting Channel "
        "opportunity or a CRM company with a recruiter attributed — click **Refresh Recruiter Intelligence** "
        "above once one exists."
    )
else:
    tab_all, tab_weekly, tab_dormant, tab_priority, tab_hiring = st.tabs([
        "All Contacts", "Weekly Follow-up List", "Dormant Relationships", "Priority Recruiters",
        "Hiring AI Governance / GRC / Fractional",
    ])

    columns = ["recruiter", "firm", "contactType", "relationshipBand", "priorityScore",
               "responseRate", "successRate", "nextFollowUp", "lastInteraction"]

    with tab_all:
        show_table(contacts, columns=columns, empty_message="No contacts yet.")

    contacts_by_name = {c["recruiter"]: c for c in contacts}

    with tab_weekly:
        due = [contacts_by_name[n] for n in feed.get("weeklyFollowUpList", []) if n in contacts_by_name]
        show_table(due, columns=columns, empty_message="No follow-ups due this week.")

    with tab_dormant:
        dormant = [contacts_by_name[n] for n in feed.get("dormantRelationships", []) if n in contacts_by_name]
        show_table(dormant, columns=columns, empty_message="No dormant relationships.")

    with tab_priority:
        priority = [contacts_by_name[n] for n in feed.get("priorityRecruiters", []) if n in contacts_by_name]
        show_table(priority, columns=columns, empty_message="No priority recruiters yet.")

    with tab_hiring:
        st.caption("Recruiters Hiring AI Governance")
        show_table([contacts_by_name[n] for n in feed.get("hiringAiGovernance", []) if n in contacts_by_name],
                   columns=columns, empty_message="None yet.")
        st.caption("Recruiters Hiring GRC")
        show_table([contacts_by_name[n] for n in feed.get("hiringGrc", []) if n in contacts_by_name],
                   columns=columns, empty_message="None yet.")
        st.caption("Recruiters Hiring Fractional Consultants")
        show_table([contacts_by_name[n] for n in feed.get("hiringFractionalConsultants", []) if n in contacts_by_name],
                   columns=columns, empty_message="None yet.")

    st.divider()
    st.subheader("Contact Detail — Timeline & Next Action")
    labels = [f"{c['recruiter']} — {c['relationshipBand']} (priority {c['priorityScore']})" for c in contacts]
    choice = st.selectbox("Select a contact", options=range(len(contacts)), format_func=lambda i: labels[i])
    selected = contacts[choice]

    col1, col2, col3 = st.columns(3)
    col1.metric("Relationship Score", f"{selected['relationshipStrength']}/100", selected["relationshipBand"])
    col2.metric("Priority Score", f"{selected['priorityScore']}/100")
    col3.metric("Next Action Due", selected.get("nextFollowUp") or "Not scheduled")

    st.markdown("**Specialisation:** " + (", ".join(selected.get("specialisation", [])) or "Not enough data yet"))
    st.markdown("**Industries:** " + (", ".join(selected.get("industries", [])) or "Not enough data yet"))
    st.markdown("**Countries:** " + (", ".join(selected.get("countries", [])) or "Not specified"))

    st.markdown("#### Timeline")
    profiles, profiles_exist = load_json_safe("recruiter-intelligence/recruiter-profiles.json")
    full_profile = (profiles or {}).get("recruiters", {}).get(selected["recruiter"], {}) if profiles_exist else {}
    history = full_profile.get("responseHistory", [])
    if history:
        show_table(history, columns=["date", "company", "channel", "summary"], empty_message="No interactions recorded yet.")
    else:
        st.info("No interaction history recorded yet for this contact.")

st.divider()
st.subheader("Recruiter Intelligence Report")
text, exists = load_text_safe(resolve_dated("output/recruiter-intelligence/{date}-recruiter-intelligence-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
