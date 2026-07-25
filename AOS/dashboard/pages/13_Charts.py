import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from components.charts import bar_chart, empty_chart, line_chart, pie_chart
from components.data_loader import list_data_records, load_json_safe
from components.theme import apply_page_config
from utils.formatting import parse_currency

apply_page_config("Charts", "▦")

st.title("Executive Charts")
st.caption("Read directly from existing AOS output files. An empty chart means the underlying runtime hasn't produced data yet — never a fabricated placeholder.")

opportunities = list_data_records("opportunity-hunter/opportunity-schema.json", "opportunities")
pipeline = list_data_records("08-Revenue-Hunter/pipeline.json", "pipeline")
service_recs_data, service_recs_exist = load_json_safe("service-mapping/service-recommendations.json")
service_recs = service_recs_data.get("recommendations", {}) if service_recs_exist and isinstance(service_recs_data, dict) else {}
leads_data, leads_exist = load_json_safe("website-intake/leads.json")
leads = list(leads_data.get("leads", {}).values()) if leads_exist and isinstance(leads_data, dict) else []
sales_feed, sales_feed_exists = load_json_safe("sales-director/runtime/output/ceo-advisor-feed.json")
sales_items = sales_feed.get("feed", []) if sales_feed_exists and isinstance(sales_feed, dict) else []

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Pipeline by Service")
    counts = Counter()
    for item in pipeline:
        rec = service_recs.get(item.get("sourceRef"))
        service = rec.get("primaryService") if rec else None
        counts[service or "Unmapped"] += 1
    if counts:
        st.plotly_chart(bar_chart(list(counts.keys()), list(counts.values()), "Pipeline by Service", "Count"), use_container_width=True)
    else:
        st.plotly_chart(empty_chart("No pipeline entries yet", "Pipeline by Service"), use_container_width=True)

with row1_col2:
    st.subheader("Revenue Forecast (by Month)")
    monthly = Counter()
    for item in pipeline:
        close_date = item.get("expectedCloseDate")
        amount, _ = parse_currency(item.get("expectedRevenue"))
        if close_date and amount:
            month = str(close_date)[:7]
            monthly[month] += amount
    if monthly:
        months = sorted(monthly.keys())
        st.plotly_chart(line_chart(months, [monthly[m] for m in months], "Revenue Forecast by Month", "Expected Revenue"), use_container_width=True)
    else:
        st.plotly_chart(empty_chart("No forecast data yet", "Revenue Forecast"), use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Opportunity Sources")
    counts = Counter(o.get("source", "Unknown") for o in opportunities)
    if counts:
        st.plotly_chart(pie_chart(list(counts.keys()), list(counts.values()), "Opportunity Sources"), use_container_width=True)
    else:
        st.plotly_chart(empty_chart("No opportunities yet", "Opportunity Sources"), use_container_width=True)

with row2_col2:
    st.subheader("Website Leads by Classification")
    counts = Counter(l.get("leadClassification", "Unknown") for l in leads)
    if counts:
        st.plotly_chart(bar_chart(list(counts.keys()), list(counts.values()), "Website Leads by Classification", "Count"), use_container_width=True)
    else:
        st.plotly_chart(empty_chart("No website leads yet", "Website Leads"), use_container_width=True)

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("Proposal Status")
    counts = Counter(i.get("status", "Unknown") for i in sales_items)
    if counts:
        st.plotly_chart(pie_chart(list(counts.keys()), list(counts.values()), "Proposal Status"), use_container_width=True)
    else:
        st.plotly_chart(empty_chart("No proposals yet", "Proposal Status"), use_container_width=True)

with row3_col2:
    st.subheader("Consulting Pipeline (by Stage)")
    consulting = [p for p in pipeline if p.get("type") == "Consulting Project"]
    counts = Counter(p.get("stage", "Unknown") for p in consulting)
    if counts:
        st.plotly_chart(bar_chart(list(counts.keys()), list(counts.values()), "Consulting Pipeline by Stage", "Count"), use_container_width=True)
    else:
        st.plotly_chart(empty_chart("No consulting pipeline entries yet", "Consulting Pipeline"), use_container_width=True)

st.subheader("Monthly Trend — New Opportunities")
monthly_opps = Counter()
for o in opportunities:
    date_found = o.get("dateFound")
    if date_found:
        monthly_opps[str(date_found)[:7]] += 1
if monthly_opps:
    months = sorted(monthly_opps.keys())
    st.plotly_chart(line_chart(months, [monthly_opps[m] for m in months], "New Opportunities by Month", "Count"), use_container_width=True)
else:
    st.plotly_chart(empty_chart("No opportunities yet", "Monthly Trend"), use_container_width=True)
