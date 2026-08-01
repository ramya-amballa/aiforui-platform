import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.charts import network_chart
from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Relationship Intelligence", "🤝")

st.title("Relationship Intelligence")
st.caption(
    "A founder-maintained, person-level relationship record — meetings, calls, messages, conference "
    "interactions, shared interests, resources shared — exactly like CRM's company-level record, but "
    "for people. Nothing here is auto-collected; every interaction is entered in relationship-profiles.json. "
    "This engine only turns that record into daily intelligence: reconnect recommendations, birthday/work "
    "anniversary/conference reminders, and a relationship health score."
)

if st.button("Refresh Relationship Intelligence", type="primary"):
    with st.spinner("Refreshing relationship intelligence..."):
        result = run_script("relationship-intelligence/runtime/generate.py", "relationship-intelligence/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Relationship Intelligence completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Relationship Intelligence failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("output/relationship-intelligence/relationship-intelligence-feed.json")
people = feed.get("people", []) if feed_exists and isinstance(feed, dict) else []

if not people:
    st.info(
        "No relationships tracked yet. Add people to relationship-intelligence/relationship-profiles.json "
        "(the same founder-maintained pattern as 06-CRM/company-intelligence.json), then click "
        "**Refresh Relationship Intelligence** above."
    )
else:
    tab_all, tab_calendar, tab_network = st.tabs(["All Relationships", "Follow-up Calendar", "Network"])

    with tab_all:
        search = st.text_input("Search by person or company")
        filtered = [
            p for p in people
            if not search or search.lower() in (p["person"] or "").lower() or search.lower() in (p["company"] or "").lower()
        ]
        st.subheader(f"People ({len(filtered)})")
        rows = [
            {
                "person": p["person"], "company": p["company"], "role": p["role"],
                "healthScore": p["healthScore"], "healthBand": p["healthBand"], "risk": p["risk"],
                "lastInteraction": p["lastInteraction"] or "Never", "reconnectRecommended": p["reconnectRecommended"],
            }
            for p in filtered
        ]
        show_table(
            rows,
            columns=["person", "company", "role", "healthScore", "healthBand", "risk", "lastInteraction", "reconnectRecommended"],
            empty_message="No person matches that search.",
        )

        names = [p["person"] for p in filtered]
        if names:
            selected_name = st.selectbox("Select a person for detail", options=names)
            selected = next(p for p in filtered if p["person"] == selected_name)

            c1, c2, c3 = st.columns(3)
            c1.metric("Relationship Health", f"{selected['healthScore']}/100", selected["healthBand"])
            c2.metric("Risk", selected["risk"])
            c3.metric("Last Interaction", selected["lastInteraction"] or "Never")

            st.markdown(f"**LinkedIn:** {selected['linkedIn'] or 'Not specified'}  \n**Email:** {selected['email'] or 'Not specified'}")
            st.markdown(f"**Relationship Opportunity:** {selected['opportunity']}")
            if selected["reconnectRecommended"]:
                st.warning(selected["reconnectReason"])

            if selected["sharedInterests"]:
                st.markdown("**Shared Interests:** " + ", ".join(selected["sharedInterests"]))
            if selected["productsDiscussed"]:
                st.markdown("**Products Discussed:** " + ", ".join(selected["productsDiscussed"]))

            st.markdown("**Timeline**")
            timeline = []
            for m in selected["meetings"]:
                timeline.append({"date": m.get("date"), "type": "Meeting", "summary": m.get("summary")})
            for c in selected["calls"]:
                timeline.append({"date": c.get("date"), "type": "Call", "summary": c.get("summary")})
            for msg in selected["messages"]:
                responded = "responded" if msg.get("responded") else "no response yet"
                timeline.append({"date": msg.get("date"), "type": f"Message ({msg.get('channel')})", "summary": f"{msg.get('summary')} — {responded}"})
            for ci in selected["conferenceInteractions"]:
                timeline.append({"date": ci.get("date"), "type": f"Conference ({ci.get('conference')})", "summary": ci.get("summary")})
            timeline.sort(key=lambda e: e["date"] or "", reverse=True)
            show_table(timeline, columns=["date", "type", "summary"], empty_message="No interactions logged yet.")

    with tab_calendar:
        st.subheader("Follow-up Calendar")
        calendar_rows = []
        by_name = {p["person"]: p for p in people}
        for name in feed.get("reconnectRecommendations", []):
            p = by_name[name]
            calendar_rows.append({"person": name, "company": p["company"], "action": "Reconnect", "detail": p["reconnectReason"]})
        for name in feed.get("birthdayReminders", []):
            p = by_name[name]
            calendar_rows.append({"person": name, "company": p["company"], "action": "Birthday", "detail": p["birthdayDate"]})
        for name in feed.get("workAnniversaryReminders", []):
            p = by_name[name]
            calendar_rows.append({"person": name, "company": p["company"], "action": "Work Anniversary", "detail": p["workAnniversaryDate"]})
        for name in feed.get("conferenceReminders", []):
            p = by_name[name]
            calendar_rows.append({"person": name, "company": p["company"], "action": "Conference", "detail": f"{p['conferenceName']} — {p['conferenceDate']}"})
        show_table(calendar_rows, columns=["person", "company", "action", "detail"], empty_message="Nothing due right now.")

    with tab_network:
        st.subheader("Network")
        st.caption("A simple company-to-person map — not a full relationship-graph tool, just an honest, readable view.")
        edges = [{"person": p["person"], "company": p["company"]} for p in people]
        st.plotly_chart(network_chart(edges, "Relationship Network"), use_container_width=True)

st.divider()
st.subheader("Relationship Intelligence Report")
text, exists = load_text_safe(resolve_dated("output/relationship-intelligence/{date}-relationship-intelligence-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
