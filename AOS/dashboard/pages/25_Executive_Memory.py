import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.state import bump_refresh

apply_page_config("Executive Memory", "🧠")

st.title("Executive Memory")
st.caption(
    "AOS Sprint 20 — a read-only aggregator, not a new score. Recognises patterns already present in real, "
    "already-computed data: which organisations keep recurring in CEO Advisor's own Top 3, which alert types "
    "keep firing, what founder-written Lessons Learned exist across closed engagements, and which governance "
    "risks recur across multiple companies. Nothing here is invented — an empty section means nothing has "
    "repeated yet, not that the check failed."
)

if st.button("Refresh Executive Memory", type="primary"):
    with st.spinner("Aggregating recurring patterns..."):
        result = run_script("executive-memory/runtime/generate.py", "executive-memory/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Executive Memory completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Executive Memory failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("executive-memory/runtime/output/executive-memory-feed.json")
feed = feed if feed_exists and isinstance(feed, dict) else {}

st.metric("Days of CEO Advisor priority history tracked", feed.get("daysTracked", 0))

st.subheader("Recurring Priorities")
show_table(feed.get("recurringPriorities", []), columns=["organisation", "daysInTop3"],
           empty_message="No organisation has recurred in Top 3 across the tracked history yet.")

st.subheader("Recurring Alert Types")
show_table(feed.get("recurringAlerts", []), columns=["alertType", "daysFired"],
           empty_message="No alert type has recurred across the tracked history yet.")

st.subheader("Lessons Learned Library")
library = feed.get("lessonsLearnedLibrary", [])
if library:
    for entry in library:
        with st.expander(entry["organisation"]):
            st.markdown(entry["lessons"])
else:
    st.info("No engagement has a completed Lessons Learned section yet.")

st.subheader("Recurring Governance Risk Patterns")
risks = feed.get("recurringGovernanceRisks", [])
if risks:
    show_table(
        [{"risk": r["risk"], "occurrenceCount": r["occurrenceCount"], "organisations": ", ".join(r["organisations"])} for r in risks],
        columns=["risk", "occurrenceCount", "organisations"],
        empty_message="No governance risk has recurred across two or more organisations yet.",
    )
else:
    st.info("No governance risk has recurred across two or more organisations yet.")

st.subheader("Founder-Recorded Decisions")
decisions = feed.get("founderDecisions", [])
if decisions:
    show_table(decisions, columns=["date", "decision", "context"], empty_message="No decisions recorded yet.")
    st.caption("Recorded by hand in executive-memory/decision-log.json — this page only reads it.")
else:
    st.info("No decisions recorded yet in decision-log.json.")

st.divider()
st.subheader("Executive Memory Report")
text, exists = load_text_safe(resolve_dated("executive-memory/runtime/output/{date}-executive-memory-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
