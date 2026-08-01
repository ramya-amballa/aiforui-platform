import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import list_data_records, load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Demand Intelligence", "▲")

st.title("Demand Intelligence")
st.caption(
    "Formerly Opportunity Hunter. Answers \"who is most likely to need AI for U&I's services this week\" — "
    "led by Demand Signals (named organisations reported adopting AI at scale, before they ever advertise a "
    "vacancy), plus targeted job-board channels (Upwork, Greenhouse, Lever, Ashby, RemoteOK)."
)

if st.button("Scan Opportunities", type="primary"):
    with st.spinner("Collecting from all configured sources..."):
        result = run_script("demand-intelligence/runtime/collect.py", "demand-intelligence/runtime", timeout_seconds=600)
    if result.ok:
        st.success(f"Scan completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Scan failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

opportunities = list_data_records("demand-intelligence/opportunity-schema.json", "opportunities")
demand_signal_opps = [o for o in opportunities if o.get("source") == "Demand Signal"]

tab_all, tab_signals, tab_engine = st.tabs([
    f"All Opportunities ({len(opportunities)})",
    f"Demand Signals ({len(demand_signal_opps)})",
    "Consulting Demand Engine",
])
columns = ["id", "dateFound", "source", "sourceCategory", "title", "organisation",
           "classification", "relevanceScore", "priorityScore", "band"]

with tab_all:
    show_table(
        opportunities, columns=columns,
        empty_message="No opportunities collected yet. Click **Scan Opportunities** above.",
    )

with tab_signals:
    show_table(
        demand_signal_opps, columns=columns,
        empty_message="No demand signals yet. Runs fully offline by default (spaCy — see Settings for status) "
                       "with no API key required; click **Scan Opportunities** above.",
    )

with tab_engine:
    st.caption(
        "AOS Sprint 6 — every organisation Demand Signals has ever identified, with its accumulated "
        "demand-signal history, Buying Readiness Score, and recommended services/action. Not just this "
        "week's top 10 (that list is CEO Advisor's own Top 10 Organizations This Week section) — the "
        "full, persistent record every signal folds into."
    )

    profiles_data, profiles_exist = load_json_safe("demand-intelligence/organisation-profiles.json")
    organisations = list(profiles_data.get("organisations", {}).values()) if profiles_exist and isinstance(profiles_data, dict) else []

    if not organisations:
        st.info(
            "No organisations identified yet. Runs fully offline by default (spaCy — see Settings for "
            "status) — needs at least one matching article in a configured Demand Signals feed; click "
            "**Scan Opportunities** above."
        )
    else:
        st.subheader("Filters")
        f1, f2, f3, f4, f5 = st.columns(5)

        industries = sorted({o.get("industry") or "Not specified" for o in organisations})
        regions = sorted({o.get("region") or "Not specified" for o in organisations})
        all_categories = sorted({cat for o in organisations for cat in o.get("matchedCategories", [])})
        all_services = sorted({s for o in organisations for s in o.get("recommendedServices", [])})
        bands_present = ["Very High", "High", "Medium", "Low"]

        with f1:
            industry_filter = st.multiselect("Industry", industries)
        with f2:
            region_filter = st.multiselect("Region", regions)
        with f3:
            signal_filter = st.multiselect("Signal Type", all_categories)
        with f4:
            band_filter = st.multiselect("Buying Score band", bands_present)
        with f5:
            service_filter = st.multiselect("Service", all_services)

        def matches_filters(org):
            if industry_filter and (org.get("industry") or "Not specified") not in industry_filter:
                return False
            if region_filter and (org.get("region") or "Not specified") not in region_filter:
                return False
            if signal_filter and not any(c in org.get("matchedCategories", []) for c in signal_filter):
                return False
            if band_filter and org.get("buyingReadinessBand") not in band_filter:
                return False
            if service_filter and not any(s in org.get("recommendedServices", []) for s in service_filter):
                return False
            return True

        filtered = [o for o in organisations if matches_filters(o)]
        filtered.sort(key=lambda o: o.get("buyingReadinessScore", 0), reverse=True)

        st.divider()
        st.subheader(f"Top Organizations ({len(filtered)} of {len(organisations)})")

        rows = []
        for org in filtered:
            rows.append({
                "organisation": org.get("organisation"),
                "industry": org.get("industry") or "Not specified",
                "region": org.get("region") or "Not specified",
                "demandSignals": ", ".join(sorted({
                    s.get("categoryLabel", "") for s in org.get("signals", [])
                })),
                "overallDemandScore": org.get("overallDemandScore", 0),
                "buyingReadinessScore": org.get("buyingReadinessScore", 0),
                "buyingReadinessBand": org.get("buyingReadinessBand", "Low"),
                "recommendedServices": ", ".join(org.get("recommendedServices", [])[:3]),
                "recommendedAction": org.get("recommendedAction", "Monitor"),
                "lastSeen": org.get("lastSeen"),
            })

        show_table(
            rows,
            columns=["organisation", "industry", "region", "demandSignals", "overallDemandScore",
                     "buyingReadinessScore", "buyingReadinessBand", "recommendedServices",
                     "recommendedAction", "lastSeen"],
            empty_message="No organisations match the selected filters.",
        )

        if filtered:
            st.divider()
            st.subheader("Opportunity Narrative")
            labels = [o["organisation"] for o in filtered]
            choice = st.selectbox("Select an organisation", options=range(len(filtered)), format_func=lambda i: labels[i])
            selected = filtered[choice]
            st.markdown(selected.get("opportunityNarrative", "_No narrative available._"))
            st.caption(f"Recommended action: **{selected.get('recommendedAction')}** — {selected.get('recommendedActionReason', '')}")

st.divider()
st.subheader("Today's Collection Report")
report_text, exists = load_text_safe(resolve_dated("output/demand-intelligence/{date}-daily-report.md"))
if exists:
    st.markdown(report_text)
else:
    st.info("No daily report for today yet.")
