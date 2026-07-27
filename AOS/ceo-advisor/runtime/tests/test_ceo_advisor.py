#!/usr/bin/env python3
"""
Unit tests for CEO Advisor's decision logic: candidate collection and
normalisation, the effort tie-break (including the specific bug this
suite caught — a chain of narrow ties letting a lower-scored candidate
bubble past a higher-scored one), Revenue Impact, Strategic Alerts,
and the Ignore List. All against fixtures, never real AOS data.

Run with:
    python3 -m unittest tests.test_ceo_advisor -v   (from runtime/)
"""

import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import generate  # noqa: E402

CONFIG = generate.load_json(RUNTIME_DIR / "config" / "ceo-advisor-config.json")


class RankingTests(unittest.TestCase):
    def test_strict_descending_order_when_no_ties(self):
        candidates = [
            {"label": "A", "normalisedValue": 5, "urgencyFactor": 1.0, "effort": 5},
            {"label": "B", "normalisedValue": 9, "urgencyFactor": 1.0, "effort": 5},
            {"label": "C", "normalisedValue": 7, "urgencyFactor": 1.0, "effort": 5},
        ]
        ranked = generate.rank_candidates(candidates, CONFIG)
        self.assertEqual([c["label"] for c in ranked], ["B", "C", "A"])

    def test_effort_tie_break_swaps_only_the_top_two(self):
        # A and B are tied (within 10%); B has lower effort (higher
        # effort-field number, per the 10=lowest-effort convention) so
        # B should win the #1 spot.
        candidates = [
            {"label": "A", "normalisedValue": 9, "urgencyFactor": 1.5, "effort": 3},   # 13.5, high effort
            {"label": "B", "normalisedValue": 9, "urgencyFactor": 1.5, "effort": 9},   # 13.5, low effort
        ]
        ranked = generate.rank_candidates(candidates, CONFIG)
        self.assertEqual(ranked[0]["label"], "B")

    def test_no_cascading_bubble_past_the_top_two(self):
        # The exact scenario that caught a real bug: a chain of narrow
        # adjacent ties must never let a much lower-scored candidate
        # end up ranked above a much higher-scored, unrelated one.
        candidates = [
            {"label": "Top", "normalisedValue": 9, "urgencyFactor": 1.5, "effort": 5},      # 13.5
            {"label": "Mid", "normalisedValue": 8.8, "urgencyFactor": 1.5, "effort": 6},     # 13.2
            {"label": "Chain", "normalisedValue": 8.5, "urgencyFactor": 1.5, "effort": 7},   # 12.75, within 10% of Mid
        ]
        ranked = generate.rank_candidates(candidates, CONFIG)
        # Mid (13.2) must never end up below Chain (12.75) just because
        # Chain has lower effort than Mid — only the top two may swap.
        labels = [c["label"] for c in ranked]
        self.assertLess(labels.index("Mid"), labels.index("Chain"))

    def test_tie_break_does_not_apply_beyond_threshold(self):
        candidates = [
            {"label": "A", "normalisedValue": 9, "urgencyFactor": 1.5, "effort": 3},
            {"label": "B", "normalisedValue": 5, "urgencyFactor": 1.0, "effort": 9},
        ]
        ranked = generate.rank_candidates(candidates, CONFIG)
        self.assertEqual(ranked[0]["label"], "A")


class CandidateCollectionTests(unittest.TestCase):
    def test_revenue_hunter_only_priority_band(self):
        pipeline = {"pipeline": [
            {"id": "rev-1", "title": "X", "organisation": "Y", "band": "Priority", "score": 90,
             "effortRequired": 5, "nextActionDue": None, "sourceRef": None},
            {"id": "rev-2", "title": "Z", "organisation": "W", "band": "Deferred", "score": 40,
             "effortRequired": 5, "nextActionDue": None, "sourceRef": None},
        ]}
        candidates = generate.candidates_from_revenue_hunter(pipeline, CONFIG)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["source"], "Revenue Hunter")

    def test_market_intelligence_consulting_opportunity_outranks_content_only(self):
        feed = {"feed": [
            {"id": "mi-1", "source": "X", "title": "A",
             "checks": {"consultingOpportunity": True, "linkedinContent": False, "websiteUpdate": False, "newProduct": False}},
            {"id": "mi-2", "source": "X", "title": "B",
             "checks": {"consultingOpportunity": False, "linkedinContent": True, "websiteUpdate": False, "newProduct": False}},
        ]}
        candidates = generate.candidates_from_market_intelligence(feed, CONFIG)
        self.assertEqual(candidates[0]["normalisedValue"], CONFIG["marketIntelligenceValue"]["consultingOpportunity"])
        self.assertEqual(candidates[1]["normalisedValue"], CONFIG["marketIntelligenceValue"]["contentOnly"])

    def test_website_intake_high_urgency_value(self):
        feed = {"feed": [{"leadId": "lead-1", "organisation": "Co", "leadClassification": "ADGL enquiry",
                           "urgency": "High", "opportunityId": None}]}
        candidates = generate.candidates_from_website_intake(feed, {}, CONFIG)
        self.assertEqual(candidates[0]["normalisedValue"], CONFIG["websiteIntakeUrgencyValue"]["High"])

    def test_orchestrator_failure_is_always_urgent(self):
        status = {"failures": [{"key": "revenue-hunter", "name": "Revenue Hunter", "error": "boom", "attempts": 3}]}
        candidates = generate.candidates_from_orchestrator_failures(status, CONFIG)
        self.assertEqual(candidates[0]["urgencyFactor"], CONFIG["urgencyFactors"]["within48Hours"])

    def test_demand_intelligence_organisations_very_high_band_most_urgent(self):
        feed = {"organisations": [
            {"organisation": "Acme", "demandSignal": "Failure Trigger", "buyingReadinessScore": 90,
             "buyingReadinessBand": "Very High", "opportunityNarrative": "n", "recommendedServices": ["AI Risk Assessment"],
             "recommendedAction": "Prepare Proposal", "recommendedActionReason": "r", "overallDemandScore": 100},
            {"organisation": "Beta Co", "demandSignal": "Funding Trigger", "buyingReadinessScore": 40,
             "buyingReadinessBand": "Low", "opportunityNarrative": "n", "recommendedServices": ["AI Readiness Assessment"],
             "recommendedAction": "Monitor", "recommendedActionReason": "r", "overallDemandScore": 50},
        ]}
        candidates = generate.candidates_from_demand_intelligence_organisations(feed, CONFIG)
        self.assertEqual(candidates[0]["urgencyFactor"], CONFIG["urgencyFactors"]["within48Hours"])
        self.assertEqual(candidates[1]["urgencyFactor"], CONFIG["urgencyFactors"]["noDeadline"])

    def test_top_organisations_this_week_ranks_and_explains(self):
        feed = {"organisations": [
            {"organisation": "Acme", "demandSignal": "Failure Trigger", "buyingReadinessScore": 90,
             "buyingReadinessBand": "Very High", "opportunityNarrative": "n", "recommendedServices": ["AI Risk Assessment"],
             "recommendedAction": "Prepare Proposal", "recommendedActionReason": "r", "overallDemandScore": 100},
            {"organisation": "Beta Co", "demandSignal": "Funding Trigger", "buyingReadinessScore": 40,
             "buyingReadinessBand": "Low", "opportunityNarrative": "n", "recommendedServices": ["AI Readiness Assessment"],
             "recommendedAction": "Monitor", "recommendedActionReason": "r", "overallDemandScore": 50},
        ]}
        top = generate.top_organisations_this_week(feed, CONFIG, count=10)
        self.assertEqual(top[0]["organisation"], "Acme")
        self.assertIn("whyItOutranksTheNext", top[0])

    def test_render_top_organisations_section_handles_empty_feed(self):
        lines = generate.render_top_organisations_section([])
        self.assertTrue(any("No demand-signal organisations" in line for line in lines))

    def test_recruiter_followups_this_week_splits_due_and_dormant(self):
        recruiter_feed = {
            "contacts": [
                {"recruiter": "Acme Recruiters", "contactType": "Recruiter", "relationshipBand": "Warm",
                 "priorityScore": 70, "nextFollowUp": "2026-08-01", "lastInteraction": "2026-07-20"},
                {"recruiter": "Stale Co", "contactType": "Consulting Firm", "relationshipBand": "Cold",
                 "priorityScore": 10, "nextFollowUp": None, "lastInteraction": "2020-01-01"},
            ],
            "weeklyFollowUpList": ["Acme Recruiters"],
            "dormantRelationships": ["Stale Co"],
        }
        due, dormant = generate.recruiter_followups_this_week(recruiter_feed)
        self.assertEqual([c["recruiter"] for c in due], ["Acme Recruiters"])
        self.assertEqual([c["recruiter"] for c in dormant], ["Stale Co"])

    def test_render_recruiter_followups_section_handles_empty_feed(self):
        lines = generate.render_recruiter_followups_section([], [])
        self.assertTrue(any("No recruiter or consulting-contact follow-ups" in line for line in lines))


class RevenueImpactTests(unittest.TestCase):
    def test_highest_value_opportunity_uses_roi_not_raw_amount(self):
        pipeline = {"pipeline": [
            {"title": "Big but unlikely", "organisation": "A", "expectedRevenue": "USD 100000",
             "probabilityOfSuccess": 1, "effortRequired": 1, "stage": "identified"},
            {"title": "Smaller but likely", "organisation": "B", "expectedRevenue": "USD 20000",
             "probabilityOfSuccess": 9, "effortRequired": 9, "stage": "identified"},
        ]}
        impact = generate.compute_revenue_impact(pipeline, set())
        self.assertIn("Smaller but likely", impact["highestValueOpportunity"])

    def test_revenue_at_risk_only_counts_cold_risk_organisations(self):
        pipeline = {"pipeline": [
            {"title": "X", "organisation": "AtRisk Co", "expectedRevenue": "USD 10000",
             "probabilityOfSuccess": 5, "effortRequired": 5, "stage": "identified"},
            {"title": "Y", "organisation": "Safe Co", "expectedRevenue": "USD 50000",
             "probabilityOfSuccess": 5, "effortRequired": 5, "stage": "identified"},
        ]}
        impact = generate.compute_revenue_impact(pipeline, {"AtRisk Co"})
        self.assertIn("10,000", impact["revenueAtRisk"])

    def test_no_open_pipeline_reports_honestly(self):
        impact = generate.compute_revenue_impact({"pipeline": []}, set())
        self.assertEqual(impact["highestValueOpportunity"], "None open in pipeline yet")


class StrategicAlertTests(unittest.TestCase):
    def test_adgl_alert_does_not_double_count_dual_tagged_opportunity(self):
        # A real bug this suite caught: one opportunity tagged with
        # BOTH "ADGL" and "AI Deployment Governance" must count once,
        # not twice, toward the demand-increase threshold. Two single-
        # opportunity fixtures (one dual-tagged, one single-tagged)
        # must report a count of 2, never 3.
        from datetime import date, timedelta
        recent = (date.today() - timedelta(days=1)).isoformat()
        schema_data = {"opportunities": [
            {"domainTags": ["ADGL", "AI Deployment Governance"], "dateFound": recent,
             "classification": "Apply", "sourceCategory": "Marketplace"},
            {"domainTags": ["ADGL"], "dateFound": recent,
             "classification": "Apply", "sourceCategory": "Marketplace"},
        ]}
        alerts = generate.detect_strategic_alerts(schema_data, {}, CONFIG)
        adgl_alert = next(a for a in alerts if a["type"] == "ADGL demand increasing")
        self.assertIn("2 ADGL", adgl_alert["evidence"])

    def test_no_website_leads_triggers_silence_alert(self):
        alerts = generate.detect_strategic_alerts({"opportunities": []}, {}, CONFIG)
        self.assertTrue(any(a["type"] == "No website enquiries received" for a in alerts))

    def test_recent_website_lead_suppresses_silence_alert(self):
        from datetime import date
        leads = {"lead-1": {"dateReceived": date.today().isoformat()}}
        alerts = generate.detect_strategic_alerts({"opportunities": []}, leads, CONFIG)
        self.assertFalse(any(a["type"] == "No website enquiries received" for a in alerts))


class IgnoreListTests(unittest.TestCase):
    def test_archived_opportunity_is_ignored(self):
        schema_data = {"opportunities": [{"title": "X", "organisation": "Y", "band": "Archived", "priorityScore": 10}]}
        ignore_list = generate.build_ignore_list(schema_data, [], {"feed": []}, CONFIG)
        self.assertEqual(len(ignore_list), 1)

    def test_needs_review_sales_director_item_is_ignored(self):
        feed = {"feed": [{"title": "X", "organisation": "Y", "status": "Needs Review"}]}
        ignore_list = generate.build_ignore_list({"opportunities": []}, [], feed, CONFIG)
        self.assertEqual(len(ignore_list), 1)

    def test_ready_to_send_is_not_ignored(self):
        feed = {"feed": [{"title": "X", "organisation": "Y", "status": "Ready To Send"}]}
        ignore_list = generate.build_ignore_list({"opportunities": []}, [], feed, CONFIG)
        self.assertEqual(len(ignore_list), 0)


class ExecutiveSummaryTests(unittest.TestCase):
    def test_capped_at_max_words(self):
        top3 = [{"label": "A" * 5, "source": "Revenue Hunter"}]
        revenue_impact = {"revenueWinnableToday": "USD 1", "revenueAtRisk": "USD 1",
                           "highestValueOpportunity": "X"}
        long_alerts = [{"type": f"alert{i}"} for i in range(500)]
        small_config = {**CONFIG, "executiveSummaryMaxWords": 20}
        summary = generate.build_executive_summary(top3, revenue_impact, long_alerts, None, small_config)
        self.assertLessEqual(len(summary.split()), 20)


if __name__ == "__main__":
    unittest.main()
