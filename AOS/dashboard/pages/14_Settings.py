import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.data_loader import load_json_safe, load_text_safe
from components.theme import apply_page_config
from utils.paths import dashboard_path, aos_path, REPO_ROOT

apply_page_config("Settings", "⚙")

st.title("Settings")
st.caption("Configuration and connector status. This page never collects or stores real API keys or secrets — those live only in environment variables or GitHub Actions repository secrets, exactly as every runtime already expects.")

# ---------------------------------------------------------------------------
# GitHub Actions schedule
# ---------------------------------------------------------------------------

st.subheader("GitHub Actions Schedule")
workflow_path = REPO_ROOT / ".github" / "workflows" / "aos-daily-operations.yml"
if workflow_path.exists():
    workflow_text = workflow_path.read_text(encoding="utf-8")
    cron_match = re.search(r'cron:\s*"([^"]+)"', workflow_text)
    cron = cron_match.group(1) if cron_match else "not found"
    st.markdown(f"**Schedule:** `{cron}` (06:00 IST daily)")
    st.caption(f"Defined in `.github/workflows/aos-daily-operations.yml`. Edit that file directly (and via a reviewed pull request) to change the schedule — the dashboard does not modify CI configuration.")
    with st.expander("View workflow file"):
        st.code(workflow_text, language="yaml")
else:
    st.info("No GitHub Actions workflow file found.")

st.divider()

# ---------------------------------------------------------------------------
# API keys / connector credentials — presence only, never values
# ---------------------------------------------------------------------------

st.subheader("API Keys & Connector Credentials")
st.caption("Shows whether each environment variable is set — never its value. Set real values as GitHub Actions repository secrets, or a local `.env` (already gitignored), per the credentials template.")

template_path = aos_path("demand-intelligence", "runtime", "config", "credentials.template.env")
if template_path.exists():
    env_var_names = re.findall(r'^([A-Z][A-Z0-9_]*)=', template_path.read_text(encoding="utf-8"), re.MULTILINE)
    rows = []
    for name in env_var_names:
        is_set = bool(os.environ.get(name))
        rows.append({"Environment Variable": name, "Status": "Set" if is_set else "Not set"})
    st.dataframe(rows, use_container_width=True, hide_index=True)
else:
    st.info("No credentials template found.")

st.divider()

# ---------------------------------------------------------------------------
# Connector status (Demand Intelligence's own Integration Status Dashboard)
# ---------------------------------------------------------------------------

st.subheader("Connector Status")
connector_text, connector_exists = load_text_safe("demand-intelligence/runtime/integration-status-dashboard.md")
if connector_exists:
    st.markdown(connector_text)
else:
    st.info("No integration status dashboard yet — it regenerates automatically at the end of every Demand Intelligence run.")

st.divider()

# ---------------------------------------------------------------------------
# Runtime status — one row per employee, from the manifest + status.json
# ---------------------------------------------------------------------------

st.subheader("Runtime Status")
manifest = json.loads(dashboard_path("config", "runtimes.json").read_text(encoding="utf-8"))
status, status_exists = load_json_safe("orchestrator/status.json")
status_by_key = {e["key"]: e for e in status.get("employees", [])} if status_exists else {}

rows = []
for key, employee in manifest.get("employees", {}).items():
    script_exists = aos_path(employee["script"]).exists()
    last = status_by_key.get(key, {})
    rows.append({
        "Employee": employee["name"],
        "Script Found": "Yes" if script_exists else "No",
        "Last Run Status": last.get("status", "Never run"),
        "Last Duration (s)": last.get("durationSeconds", "-"),
    })
st.dataframe(rows, use_container_width=True, hide_index=True)

st.divider()

# ---------------------------------------------------------------------------
# Theme (UI-only preference, not a business setting)
# ---------------------------------------------------------------------------

st.subheader("Theme")
st.caption("Color palette is fixed to the AI for U&I brand (white background, dark blue headings, grey cards) by design. Table density is the only adjustable display preference.")

settings_path = dashboard_path("config", "settings.json")
settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.exists() else {}
density = st.radio("Table density", ["comfortable", "compact"], index=0 if settings.get("tableDensity") != "compact" else 1, horizontal=True)
if st.button("Save Preference"):
    settings["tableDensity"] = density
    settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    st.success("Saved.")
