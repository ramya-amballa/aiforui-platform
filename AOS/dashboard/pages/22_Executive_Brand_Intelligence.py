import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Executive Brand Intelligence", "📣")

st.title("Executive Brand Intelligence")
st.caption(
    "A weekly thought-leadership plan built entirely from real data other employees already computed — "
    "qualified companies, Account Intelligence briefs, tracked relationships, and the shared resource "
    "catalogue. Nothing here is a fabricated name, figure or event."
)

if st.button("Refresh Executive Brand Intelligence", type="primary"):
    with st.spinner("Refreshing the weekly brand plan..."):
        result = run_script("executive-brand-intelligence/runtime/generate.py",
                             "executive-brand-intelligence/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Executive Brand Intelligence completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Executive Brand Intelligence failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("output/executive-brand-intelligence/executive-brand-intelligence-feed.json")
plan = feed.get("weeklyPlan") if feed_exists and isinstance(feed, dict) else None
monthly = feed.get("monthlyAuthorityReport") if feed_exists and isinstance(feed, dict) else None

if not plan:
    st.info(
        "No Weekly Brand Plan yet. Requires at least one organisation already qualified by Demand "
        "Intelligence — click **Refresh Executive Brand Intelligence** above once one exists."
    )
else:
    tab_weekly, tab_monthly = st.tabs(["Weekly Brand Plan", "Monthly Authority Report"])

    with tab_weekly:
        st.subheader(f"Week of {plan['weekOf']}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Visibility Impact", plan["visibilityImpact"])
        c2.metric("Lead Generation Potential", plan["leadGenerationPotential"])
        c3.metric("Expected Consulting Influence", plan["expectedConsultingInfluence"])

        st.markdown(f"**Companies this week:** {plan['companiesThisWeek']}  \n"
                    f"**Trending domain:** {plan['trendingDomain'] or 'Not enough signal yet'}  \n"
                    f"**Trending governance risk:** {plan['trendingGovernanceRisk'] or 'Not enough signal yet'}")

        st.markdown("### Companies to Engage")
        show_table(plan["companiesToEngage"],
                   columns=["organisation", "industry", "buyingReadinessBand", "buyingReadinessScore"],
                   empty_message="None this week.")

        st.markdown("### Executives to Follow")
        show_table(plan["executivesToFollow"], columns=["person", "company", "role"],
                   empty_message="No executives tracked yet in relationship-profiles.json.")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### Topics to Write")
            for t in plan["topicsToWrite"] or ["Not enough signal yet."]:
                st.markdown(f"- {t}")
            st.markdown("### Newsletter Themes")
            for t in plan["newsletterThemes"] or ["Not enough signal yet."]:
                st.markdown(f"- {t}")
        with col_b:
            st.markdown("### Products to Update")
            for a in plan["productsToUpdate"] or []:
                st.markdown(f"- **{a['title']}** ({a['type']})")
            st.markdown("### Whitepapers to Publish")
            for a in plan["whitepapersToPublish"] or [{"title": "None in the catalogue yet."}]:
                st.markdown(f"- **{a['title']}**")

        st.markdown("### Conferences to Monitor")
        show_table(plan["conferencesToMonitor"], columns=["name", "date"],
                   empty_message="None tracked yet in relationship-profiles.json.")

        st.markdown("### GitHub Improvements")
        st.info(plan["githubImprovements"])
        st.markdown("### LinkedIn Strategy")
        st.info(plan["linkedinStrategy"])

    with tab_monthly:
        st.subheader("Monthly Authority Report")
        if not monthly or monthly.get("weeksIncluded", 0) == 0:
            st.info("Not enough weekly history yet — this rolls up as more weeks run.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Weeks Included", monthly["weeksIncluded"])
            c2.metric("Most Common Domain", monthly["topDomain"] or "Not enough signal")
            c3.metric("Most Common Risk", monthly["topRisk"] or "Not enough signal")
            c4.metric("Companies Engaged", monthly["totalCompaniesEngaged"])

st.divider()
st.subheader("Executive Brand Intelligence Report")
text, exists = load_text_safe(resolve_dated("output/executive-brand-intelligence/{date}-executive-brand-intelligence-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
