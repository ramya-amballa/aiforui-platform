#!/usr/bin/env python3
"""
Unit tests for the Website Intake Runtime's pure decision logic: Lead
ID generation, Lead Classification, and Qualification. Does not invoke
ingest.py/revenue-hunter/service-mapping (those are exercised for real
in a scratch copy during manual verification, not here — this suite
covers only generate.py's own deterministic functions, against
fixtures, never real AOS data).

Run with:
    python3 -m unittest tests.test_website_intake -v   (from runtime/)
"""

import sys
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

import generate  # noqa: E402

CONFIG = generate.load_json(RUNTIME_DIR / "config" / "website-intake-config.json")


def raw(**kwargs):
    base = {
        "name": "Test Person", "organization": "Test Org", "role": "",
        "email": "test@testorg.com", "message": "General enquiry.",
        "sourcePage": "contact", "submittedAt": "2026-07-25T10:00:00Z",
    }
    base.update(kwargs)
    return base


class LeadIdTests(unittest.TestCase):
    def test_deterministic(self):
        r = raw()
        self.assertEqual(generate.generate_lead_id(r), generate.generate_lead_id(r))

    def test_different_submissions_differ(self):
        self.assertNotEqual(
            generate.generate_lead_id(raw(email="a@x.com")),
            generate.generate_lead_id(raw(email="b@x.com")),
        )

    def test_prefixed(self):
        self.assertTrue(generate.generate_lead_id(raw()).startswith("lead-"))


class LeadClassificationTests(unittest.TestCase):
    def test_adgl_source_page(self):
        classification, _ = generate.classify_lead(raw(sourcePage="adgl"), CONFIG)
        self.assertEqual(classification, "ADGL enquiry")

    def test_opera_source_page(self):
        classification, _ = generate.classify_lead(raw(sourcePage="opera"), CONFIG)
        self.assertEqual(classification, "AI Governance Advisory")

    def test_selected_engagement_areas_source_page(self):
        classification, _ = generate.classify_lead(raw(sourcePage="selected-engagement-areas"), CONFIG)
        self.assertEqual(classification, "AI Governance Advisory")

    def test_fractional_keyword(self):
        classification, _ = generate.classify_lead(
            raw(sourcePage="contact", message="Looking for a fractional advisor."), CONFIG)
        self.assertEqual(classification, "Fractional Consulting")

    def test_speaking_keyword(self):
        classification, _ = generate.classify_lead(
            raw(sourcePage="contact", message="Would you speak at our conference?"), CONFIG)
        self.assertEqual(classification, "Speaking")

    def test_partnership_keyword(self):
        classification, _ = generate.classify_lead(
            raw(sourcePage="contact", message="We'd like to explore a partnership."), CONFIG)
        self.assertEqual(classification, "Partnership")

    def test_unknown_fallback(self):
        classification, _ = generate.classify_lead(
            raw(sourcePage="contact", message="Just saying hello."), CONFIG)
        self.assertEqual(classification, "Unknown")

    def test_source_page_checked_before_keywords(self):
        # message would otherwise match Fractional Consulting, but adgl
        # sourcePage is the stronger signal and is checked first.
        classification, _ = generate.classify_lead(
            raw(sourcePage="adgl", message="Looking for fractional support."), CONFIG)
        self.assertEqual(classification, "ADGL enquiry")


class QualificationTests(unittest.TestCase):
    def test_urgency_high(self):
        urgency = generate.estimate_urgency("We need this urgently, ideally this week.", CONFIG)
        self.assertEqual(urgency, "High")

    def test_urgency_medium(self):
        urgency = generate.estimate_urgency("Hoping to move on this in the coming weeks.", CONFIG)
        self.assertEqual(urgency, "Medium")

    def test_urgency_low_default(self):
        urgency = generate.estimate_urgency("No particular timeline in mind.", CONFIG)
        self.assertEqual(urgency, "Low")

    def test_industry_inferred(self):
        industry, basis = generate.estimate_industry("We are a regional bank.", "", CONFIG)
        self.assertEqual(industry, "Financial Services")
        self.assertEqual(basis, "keyword-inferred")

    def test_industry_not_specified(self):
        industry, basis = generate.estimate_industry("General enquiry.", "", CONFIG)
        self.assertEqual(industry, "Not specified")
        self.assertEqual(basis, "not specified")

    def test_geography_inferred(self):
        geography, _ = generate.estimate_geography("We are based in Dubai.", CONFIG)
        self.assertEqual(geography, "UAE")

    def test_geography_not_specified(self):
        geography, _ = generate.estimate_geography("General enquiry.", CONFIG)
        self.assertEqual(geography, "Not specified")

    def test_organisation_size_always_unknown(self):
        qualification = generate.estimate_qualification(raw(), "Unknown", CONFIG)
        self.assertEqual(qualification["organisationSize"], "Unknown")

    def test_revenue_potential_by_classification(self):
        q_fractional = generate.estimate_qualification(raw(), "Fractional Consulting", CONFIG)
        q_speaking = generate.estimate_qualification(raw(), "Speaking", CONFIG)
        self.assertEqual(q_fractional["revenuePotential"], 8)
        self.assertEqual(q_speaking["revenuePotential"], 3)

    def test_strategic_value_boosted_for_adgl_page(self):
        q = generate.estimate_qualification(raw(sourcePage="adgl"), "ADGL enquiry", CONFIG)
        self.assertEqual(q["strategicValue"], 8)


class OrganisationFromTests(unittest.TestCase):
    def test_uses_organization_field_when_present(self):
        self.assertEqual(generate.organisation_from(raw(organization="Acme Corp")), "Acme Corp")

    def test_falls_back_to_email_domain(self):
        self.assertEqual(
            generate.organisation_from(raw(organization="", email="jane@acme.com")), "acme.com")

    def test_falls_back_to_individual_enquiry_when_nothing_available(self):
        self.assertEqual(
            generate.organisation_from({"organization": "", "email": ""}), "Individual Enquiry")


class OpportunityInputRecordTests(unittest.TestCase):
    def test_source_is_website(self):
        record = generate.build_opportunity_input_record(
            raw(), "lead-abc123", "ADGL enquiry",
            generate.estimate_qualification(raw(), "ADGL enquiry", CONFIG), CONFIG)
        self.assertEqual(record["source"], "Website")

    def test_lead_id_marker_in_notes(self):
        record = generate.build_opportunity_input_record(
            raw(), "lead-abc123", "ADGL enquiry",
            generate.estimate_qualification(raw(), "ADGL enquiry", CONFIG), CONFIG)
        self.assertEqual(record["notes"], f"{generate.LEAD_ID_MARKER}lead-abc123")

    def test_domain_tags_match_classification(self):
        record = generate.build_opportunity_input_record(
            raw(), "lead-abc123", "ADGL enquiry",
            generate.estimate_qualification(raw(), "ADGL enquiry", CONFIG), CONFIG)
        self.assertIn("ADGL", record["domainTags"])

    def test_partnership_gets_consulting_channel_source_category(self):
        record = generate.build_opportunity_input_record(
            raw(), "lead-abc123", "Partnership",
            generate.estimate_qualification(raw(), "Partnership", CONFIG), CONFIG)
        self.assertEqual(record["sourceCategory"], "Consulting Channel")

    def test_scoped_engagement_requires_substantive_message_and_qualifying_classification(self):
        short = generate.build_opportunity_input_record(
            raw(message="ADGL help please"), "lead-1", "ADGL enquiry",
            generate.estimate_qualification(raw(message="ADGL help please"), "ADGL enquiry", CONFIG), CONFIG)
        self.assertFalse(short["scopedEngagement"])

        long_message = " ".join(["We need help with our AI deployment governance programme"] * 4)
        substantial = generate.build_opportunity_input_record(
            raw(message=long_message), "lead-2", "ADGL enquiry",
            generate.estimate_qualification(raw(message=long_message), "ADGL enquiry", CONFIG), CONFIG)
        self.assertTrue(substantial["scopedEngagement"])


if __name__ == "__main__":
    unittest.main()
