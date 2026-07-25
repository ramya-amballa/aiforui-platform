#!/usr/bin/env python3
"""
Unit tests for the Phase 1 connectors: RemoteOK, Greenhouse, Lever,
Ashby, Upwork, LinkedIn Jobs, Wellfound.

Every test mocks the network boundary (collectors.common.http_get_json,
or urllib.request.urlopen for Upwork's OAuth2/GraphQL calls) with
realistic canned responses shaped like each platform's real, documented
API — no live network call is made, so these run identically in any
environment, including one with no outbound network access at all.

Run with:
    python3 -m unittest tests.test_collectors -v      (from runtime/)
    python3 -m unittest AOS.opportunity-hunter.runtime.tests.test_collectors -v  (from repo root)
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

RUNTIME_DIR = Path(__file__).resolve().parent.parent
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from collectors import ashby, greenhouse, lever, linkedin_jobs, remoteok, upwork, wellfound  # noqa: E402

KEYWORDS = ["AI Governance", "AI Deployment", "RAG"]


class FakeHttpResponse:
    """Minimal stand-in for urllib.request.urlopen's context-manager
    response, so Upwork's real urllib-based code can be tested without
    a live connection."""

    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


class RemoteOKTests(unittest.TestCase):
    def test_matches_and_normalises_real_shape(self):
        # RemoteOK's real response: first element is a legend/metadata
        # object with no "position" key, the rest are real jobs.
        fake_response = [
            {"legend": "this is not a job"},
            {"position": "AI Governance Lead", "company": "Acme AI",
             "description": "Own our AI Governance and RAG rollout",
             "tags": ["ai", "governance"], "url": "https://remoteok.com/1",
             "location": "Worldwide"},
            {"position": "Barista", "company": "Coffee Co",
             "description": "Make coffee", "tags": ["food"],
             "url": "https://remoteok.com/2", "location": "Worldwide"},
        ]
        with patch("collectors.common.http_get_json", return_value=fake_response):
            results = remoteok.collect(KEYWORDS, {})
        self.assertEqual(len(results), 1)
        opp = results[0]
        self.assertEqual(opp["title"], "AI Governance Lead")
        self.assertEqual(opp["organisation"], "Acme AI")
        self.assertEqual(opp["source"], "RemoteOK")
        self.assertTrue(opp["remote"])
        self.assertTrue(opp["autoCollected"])
        self.assertTrue(opp["autoScored"])
        self.assertIn("AI Governance", opp["matchedKeywords"])

    def test_no_data_returns_empty(self):
        with patch("collectors.common.http_get_json", return_value=None):
            self.assertEqual(remoteok.collect(KEYWORDS, {}), [])


class GreenhouseTests(unittest.TestCase):
    def test_no_board_tokens_skips_cleanly(self):
        self.assertEqual(greenhouse.collect(KEYWORDS, {}), [])
        self.assertEqual(greenhouse.collect(KEYWORDS, {"boardTokens": []}), [])

    def test_parses_real_shape(self):
        fake_response = {"jobs": [
            {"title": "AI Governance Consultant",
             "content": "Lead our RAG and AI Deployment programme",
             "location": {"name": "Remote - US"},
             "absolute_url": "https://boards.greenhouse.io/acme/jobs/1"},
            {"title": "Office Manager", "content": "Manage the office",
             "location": {"name": "New York"},
             "absolute_url": "https://boards.greenhouse.io/acme/jobs/2"},
        ]}
        with patch("collectors.common.http_get_json", return_value=fake_response):
            results = greenhouse.collect(KEYWORDS, {"boardTokens": ["acme"]})
        self.assertEqual(len(results), 1)
        opp = results[0]
        self.assertEqual(opp["title"], "AI Governance Consultant")
        self.assertEqual(opp["organisation"], "acme")
        self.assertTrue(opp["remote"])
        self.assertEqual(opp["source"], "Greenhouse")


class LeverTests(unittest.TestCase):
    def test_no_companies_skips_cleanly(self):
        self.assertEqual(lever.collect(KEYWORDS, {}), [])
        self.assertEqual(lever.collect(KEYWORDS, {"companies": []}), [])

    def test_parses_real_shape(self):
        fake_response = [
            {"text": "AI Risk & Governance Lead",
             "descriptionPlain": "Own AI Governance across the org",
             "categories": {"location": "Remote"},
             "hostedUrl": "https://jobs.lever.co/acme/1"},
            {"text": "Warehouse Associate",
             "descriptionPlain": "Pack boxes",
             "categories": {"location": "Chicago"},
             "hostedUrl": "https://jobs.lever.co/acme/2"},
        ]
        with patch("collectors.common.http_get_json", return_value=fake_response):
            results = lever.collect(KEYWORDS, {"companies": ["acme"]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "AI Risk & Governance Lead")
        self.assertEqual(results[0]["organisation"], "acme")
        self.assertTrue(results[0]["remote"])


class AshbyTests(unittest.TestCase):
    def test_no_job_boards_skips_cleanly(self):
        self.assertEqual(ashby.collect(KEYWORDS, {}), [])
        self.assertEqual(ashby.collect(KEYWORDS, {"jobBoardNames": []}), [])

    def test_parses_real_shape(self):
        fake_response = {"jobs": [
            {"title": "AI Deployment Governance Lead",
             "descriptionPlain": "Own our ADGL rollout with RAG governance",
             "location": "Remote", "isRemote": True,
             "jobUrl": "https://jobs.ashbyhq.com/acme/1"},
            {"title": "Sales Development Rep",
             "descriptionPlain": "Book meetings",
             "location": "Austin", "isRemote": False,
             "jobUrl": "https://jobs.ashbyhq.com/acme/2"},
        ]}
        with patch("collectors.common.http_get_json", return_value=fake_response):
            results = ashby.collect(KEYWORDS, {"jobBoardNames": ["acme"]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "AI Deployment Governance Lead")
        self.assertTrue(results[0]["remote"])


class UpworkTests(unittest.TestCase):
    def test_missing_any_credential_skips_cleanly(self):
        self.assertEqual(upwork.collect(KEYWORDS, {}), [])
        self.assertEqual(upwork.collect(KEYWORDS, {"apiKey": "x"}), [])
        self.assertEqual(upwork.collect(KEYWORDS, {"apiKey": "x", "apiSecret": "y"}), [])

    def test_full_oauth_and_graphql_flow(self):
        config = {"apiKey": "client-id", "apiSecret": "client-secret",
                   "refreshToken": "refresh-token-value"}

        token_response = FakeHttpResponse({"access_token": "fake-access-token"})
        graphql_response = FakeHttpResponse({
            "data": {"marketplaceJobPostingsSearch": {"edges": [
                {"node": {
                    "title": "AI Governance Fractional Advisor",
                    "description": "Scoped AI Governance engagement",
                    "client": {"companyName": "Acme Client"},
                    "job": {"publicUrl": "https://www.upwork.com/jobs/1"},
                }},
            ]}}
        })

        def fake_urlopen(request, timeout=15):
            if request.full_url == upwork.TOKEN_URL:
                return token_response
            return graphql_response

        with patch("collectors.upwork.urllib.request.urlopen", side_effect=fake_urlopen):
            results = upwork.collect(["AI Governance"], config)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "AI Governance Fractional Advisor")
        self.assertEqual(results[0]["organisation"], "Acme Client")
        self.assertEqual(results[0]["source"], "Upwork")

    def test_token_refresh_failure_skips_cleanly(self):
        config = {"apiKey": "a", "apiSecret": "b", "refreshToken": "c"}
        with patch("collectors.upwork.urllib.request.urlopen", side_effect=OSError("network down")):
            self.assertEqual(upwork.collect(KEYWORDS, config), [])

    def test_graphql_error_response_returns_no_fabricated_results(self):
        config = {"apiKey": "a", "apiSecret": "b", "refreshToken": "c"}
        token_response = FakeHttpResponse({"access_token": "fake-access-token"})
        error_response = FakeHttpResponse({"errors": [{"message": "field not found"}]})

        def fake_urlopen(request, timeout=15):
            if request.full_url == upwork.TOKEN_URL:
                return token_response
            return error_response

        with patch("collectors.upwork.urllib.request.urlopen", side_effect=fake_urlopen):
            results = upwork.collect(KEYWORDS, config)
        self.assertEqual(results, [])


class LinkedInJobsTests(unittest.TestCase):
    def test_no_credentials_skips_cleanly(self):
        self.assertEqual(linkedin_jobs.collect(KEYWORDS, {}), [])

    def test_credentials_present_but_unimplemented_returns_empty_not_fabricated(self):
        # No documented public API contract exists to implement against
        # yet; the connector must never invent a result even with a key set.
        self.assertEqual(linkedin_jobs.collect(KEYWORDS, {"apiKey": "granted-token"}), [])


class WellfoundTests(unittest.TestCase):
    def test_no_credentials_skips_cleanly(self):
        self.assertEqual(wellfound.collect(KEYWORDS, {}), [])

    def test_credentials_present_but_unimplemented_returns_empty_not_fabricated(self):
        self.assertEqual(wellfound.collect(KEYWORDS, {"apiKey": "some-key"}), [])


if __name__ == "__main__":
    unittest.main()
