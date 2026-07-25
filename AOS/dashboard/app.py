"""
AOS Command Center — Home.

Presentation-only landing page. Reads existing AOS output files and
orchestrator/status.json; never writes to any business data file and
never re-implements any employee's logic. See config/runtimes.json for
the full button-to-runtime mapping and README.md for the architecture.
"""

from datetime import date

import streamlit as st

from components.cards import metric_card, metric_row
from components.data_loader import (
    extract_markdown_section, file_last_modified, list_data_records,
    load_json_safe, load_text_safe, resolve_dated, today_str,
)
from components.theme import apply_page_config, status_pill
from utils.formatting import format_timestamp

apply_page_config("Home", "■")

st.title("AOS Command Center")
st.caption("The internal operating system of AI for U&I")

status, status_exists = load_json_safe("orchestrator/status.json")

# ---------------------------------------------------------------------------
# Top row: date, last execution, system status, employees running
# ---------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card("Current Date", date.today().strftime("%d %b %Y"))

with col2:
    last_run = format_timestamp(status.get("finishedAt")) if status_exists else "Never run yet"
    metric_card("Last Execution", last_run)

with col3:
    overall = status.get("overallStatus") if status_exists else None
    kind = {"SUCCESS": "ok", "PARTIAL_FAILURE": "warn", "FAILED": "fail"}.get(overall, "idle")
    label = overall or "Not yet run"
    st.markdown(
        f'<div class="aos-card"><h4>System Status</h4>'
        f'<div class="aos-card-value">{status_pill(label, kind)}</div></div>',
        unsafe_allow_html=True,
    )

with col4:
    if status_exists:
        employees = status.get("employees", [])
        running_ok = sum(1 for e in employees if e.get("status") in ("SUCCESS",))
        total = len(employees)
        metric_card("AI Employees Running", f"{running_ok} / {total}", "Succeeded this run")
    else:
        metric_card("AI Employees Running", "0 / 11", "No run yet — click Run Full AOS")

st.divider()

# ---------------------------------------------------------------------------
# Today's Executive Summary + CEO Advisor Top 3 Priorities
# ---------------------------------------------------------------------------

left, right = st.columns([3, 2])

ceo_report_text, ceo_report_exists = load_text_safe("ceo-advisor/runtime/output/ceo-daily-report.md")

with left:
    st.subheader("Today's Executive Summary")
    if ceo_report_exists:
        summary = extract_markdown_section(ceo_report_text, "Executive Summary")
        st.markdown(summary or "_No Executive Summary section found in today's report._")
    else:
        st.info("No CEO Advisor report yet. Run **CEO Advisor** (or **Run Full AOS**) to generate one.")

with right:
    st.subheader("Top 3 Priorities")
    if ceo_report_exists:
        priorities = extract_markdown_section(ceo_report_text, "Top 3 Priorities")
        st.markdown(priorities or "_No priorities section found in today's report._")
    else:
        st.info("No priorities yet.")

st.divider()

# ---------------------------------------------------------------------------
# Home dashboard cards
# ---------------------------------------------------------------------------

st.subheader("Business at a Glance")

opportunities = list_data_records("demand-intelligence/opportunity-schema.json", "opportunities")
pipeline = list_data_records("08-Revenue-Hunter/pipeline.json", "pipeline")
companies = list_data_records("06-CRM/company-intelligence.json", "companies")

website_leads_data, website_leads_exists = load_json_safe("website-intake/leads.json")
website_leads_dict = website_leads_data.get("leads", {}) if website_leads_exists and isinstance(website_leads_data, dict) else {}
website_leads = list(website_leads_dict.values())

sales_feed, sales_feed_exists = load_json_safe("sales-director/runtime/output/ceo-advisor-feed.json")
sales_items = sales_feed.get("feed", []) if sales_feed_exists and isinstance(sales_feed, dict) else []
open_proposals = [i for i in sales_items if i.get("status") in ("Ready To Send", "Proposal Ready", "Needs Review")]

pipeline_value_amounts = []
for item in pipeline:
    from utils.formatting import parse_currency
    amount, _ = parse_currency(item.get("expectedRevenue"))
    if amount:
        pipeline_value_amounts.append(amount)
pipeline_value_total = sum(pipeline_value_amounts) if pipeline_value_amounts else 0

forecast_text, forecast_exists = load_text_safe("revenue-hunter/runtime/output/revenue-forecast.md")

recruiters_awaiting = [c for c in companies if c.get("recruiter") and c.get("nextFollowUpDue")]

content_queue, content_queue_exists = load_json_safe("content-director/runtime/queue/content-queue.json")
content_ready = [c for c in (content_queue.get("queue", []) if content_queue_exists and isinstance(content_queue, dict) else [])
                 if c.get("status") == "Ready to Publish"]

backlog, backlog_exists = load_json_safe("03-Product-Manager/product-backlog.json")
products_ready = [p for p in (backlog.get("backlog", []) if backlog_exists and isinstance(backlog, dict) else [])
                  if p.get("status") == "in-development"]

top_priority_text = "No priorities yet"
if ceo_report_exists:
    section = extract_markdown_section(ceo_report_text, "Top 3 Priorities")
    if section:
        first_line = next((l for l in section.splitlines() if l.strip()), "")
        top_priority_text = first_line.strip("- ").strip() or "See CEO Advisor"

adgl_opps = [o for o in opportunities if "ADGL" in (o.get("domainTags") or [])]
latest_adgl = sorted(adgl_opps, key=lambda o: o.get("dateFound", ""), reverse=True)
latest_adgl_label = latest_adgl[0].get("title", "Untitled") if latest_adgl else "None yet"

cards = [
    ("New Opportunities", str(len(opportunities)), "in opportunity-schema.json"),
    ("Website Leads", str(len(website_leads)), "from website-intake"),
    ("Open Proposals", str(len(open_proposals)), "Ready/Needs Review"),
    ("Pipeline Value", f"{pipeline_value_total:,.0f}" if pipeline_value_total else "0", "sum of expectedRevenue"),
    ("Forecast Revenue", "See Revenue Hunter" if forecast_exists else "No forecast yet", ""),
    ("Recruiters Awaiting Follow-up", str(len(recruiters_awaiting)), "from CRM"),
    ("Content Ready", str(len(content_ready)), "queued drafts"),
    ("Products Ready", str(len(products_ready)), "in backlog"),
    ("Top Priority", top_priority_text, "from CEO Advisor"),
    ("Latest ADGL Opportunity", latest_adgl_label, ""),
]

metric_row(cards, columns=5)

st.divider()
st.caption(
    "Use the sidebar to open any AI employee's page and run their action button. "
    "Use **Execution** in the sidebar for the one-click **Run Full AOS** button."
)
