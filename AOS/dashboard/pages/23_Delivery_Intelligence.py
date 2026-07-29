import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe, resolve_dated
from components.runtime_runner import run_script
from components.tables import show_table
from components.theme import apply_page_config
from utils.paths import REPO_ROOT
from utils.state import bump_refresh

apply_page_config("Delivery Intelligence", "📦")

st.title("Delivery Intelligence")
st.caption(
    "AOS Sprint 17 — the Consulting Delivery Engine. For every engagement that reaches stage 'won' in "
    "Revenue Hunter's pipeline, generates a full delivery kit (10 ADGL/OPERA-aligned artifacts: kickoff "
    "agenda, discovery questionnaire, readiness workbook, roadmap, RACI, risk register, workshop materials, "
    "status report, steering committee pack, closure report) built from the reusable template library in "
    "templates/delivery/. Kits are generated once and never overwritten — these are living documents the "
    "founder edits by hand during real delivery."
)

if st.button("Refresh Delivery Intelligence", type="primary"):
    with st.spinner("Checking for newly won engagements..."):
        result = run_script("delivery-intelligence/runtime/generate.py", "delivery-intelligence/runtime", timeout_seconds=300)
    if result.ok:
        st.success(f"Delivery Intelligence completed in {result.duration_seconds}s.")
        bump_refresh()
    else:
        st.error(f"Delivery Intelligence failed (exit code {result.returncode}).")
        if result.stderr:
            with st.expander("Error details"):
                st.code(result.stderr)

st.divider()

feed, feed_exists = load_json_safe("delivery-intelligence/runtime/output/delivery-intelligence-feed.json")
engagements = feed.get("engagements", []) if feed_exists and isinstance(feed, dict) else []

st.subheader(f"Won Engagements ({len(engagements)})")

if not engagements:
    st.info(
        "No delivery kits yet. This engine triggers only when an entry in 08-Revenue-Hunter/pipeline.json "
        "reaches stage 'won' — click **Refresh Delivery Intelligence** above once one has."
    )
else:
    rows = [
        {"organisation": e["organisation"], "engagementRef": e["engagementRef"], "primaryService": e["primaryService"],
         "regulatoryFramework": e.get("regulatoryFramework", "Not recorded — regenerate this kit to backfill"),
         "phase": e["phase"], "kitPath": e["kitPath"]}
        for e in engagements
    ]
    show_table(rows, columns=["organisation", "engagementRef", "primaryService", "regulatoryFramework", "phase", "kitPath"],
               empty_message="No engagement matches.")

    names = [e["organisation"] for e in engagements]
    selected_name = st.selectbox("Select an engagement", options=names)
    selected = next(e for e in engagements if e["organisation"] == selected_name)

    st.metric("Delivery Phase", selected["phase"])
    st.caption(
        "Phase is read from delivery-log.json — a founder-maintained record, exactly like "
        "relationship-profiles.json. Update that file by hand as the real engagement progresses."
    )

    st.markdown("### Delivery Kit Artifacts")
    labels = {
        "kickoff-agenda": "📋 Kickoff Agenda", "discovery-questionnaire": "❓ Discovery Questionnaire",
        "readiness-assessment-workbook": "📊 AI Readiness Assessment Workbook", "governance-roadmap": "🗺️ Governance Roadmap",
        "raci": "👥 RACI", "risk-register": "⚠️ Risk Register", "workshop-materials": "🧩 Workshop Materials",
        "executive-status-report": "📈 Executive Status Report", "steering-committee-pack": "🏛️ Steering Committee Pack",
        "project-closure-report": "✅ Project Closure Report",
    }
    for suffix, path in selected.get("artifacts", {}).items():
        artifact_path = REPO_ROOT / path
        label = labels.get(suffix, suffix)
        with st.expander(label):
            if artifact_path.exists():
                content = artifact_path.read_text(encoding="utf-8")
                with st.popover("Preview"):
                    st.code(content, language="markdown")
                st.download_button("Download", data=content, file_name=artifact_path.name,
                                    mime="text/markdown", key=f"dl-{selected_name}-{suffix}")
            else:
                st.warning("Artifact file not found on disk.")

st.divider()
st.subheader("Delivery Intelligence Report")
text, exists = load_text_safe(resolve_dated("delivery-intelligence/runtime/output/{date}-delivery-intelligence-report.md"))
if exists:
    st.markdown(text)
else:
    st.info("No report for today yet.")
