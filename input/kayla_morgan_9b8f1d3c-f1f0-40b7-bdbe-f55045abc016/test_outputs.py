"""
Test suite for the May Board Reimbursement Claim Packet task.

Relevant APIs: gmail-api, google-calendar-api, quickbooks-api.
Distractor APIs (pinterest, etsy, spotify) carry penalty guards below.
Mutation guard is consolidated into ONE TestNegativeWeight* test across all relevant APIs.
"""

import json
import os
from urllib.request import urlopen

import pytest

GMAIL_API_URL = os.environ.get("GMAIL_API_URL", "http://localhost:8031")
GOOGLE_CALENDAR_API_URL = os.environ.get("GOOGLE_CALENDAR_API_URL", "http://localhost:8033")
QUICKBOOKS_API_URL = os.environ.get("QUICKBOOKS_API_URL", "http://localhost:8067")
PINTEREST_API_URL = os.environ.get("PINTEREST_API_URL", "http://localhost:8068")
ETSY_API_URL = os.environ.get("ETSY_API_URL", "http://localhost:8069")
SPOTIFY_API_URL = os.environ.get("SPOTIFY_API_URL", "http://localhost:8070")


def _audit(base_url: str) -> list:
    raw = urlopen(f"{base_url}/audit/requests", timeout=10).read()
    data = json.loads(raw)
    if isinstance(data, dict):
        return data.get("requests", [])
    if isinstance(data, list):
        return data
    return []


def _gmail():
    return _audit(GMAIL_API_URL)


def _calendar():
    return _audit(GOOGLE_CALENDAR_API_URL)


def _quickbooks():
    return _audit(QUICKBOOKS_API_URL)


def _pinterest():
    return _audit(PINTEREST_API_URL)


def _etsy():
    return _audit(ETSY_API_URL)


def _spotify():
    return _audit(SPOTIFY_API_URL)


def _gets(requests):
    return [r for r in requests if r.get("method") == "GET"]


def _all_relevant_requests():
    return _gmail() + _calendar() + _quickbooks()


class TestBehavioralGmail:
    def test_agent_queried_gmail(self):
        assert len(_gets(_gmail())) >= 1, "Agent never made a GET request to gmail-api"

    def test_reads_linda_handoff_email(self):
        matches = [r for r in _gmail() if "msg-001" in (r.get("path") or "")]
        assert len(matches) >= 1, "Agent did not read Linda Hartley's handoff email (msg-001)"

    def test_reads_catering_confirmation(self):
        matches = [r for r in _gmail() if "msg-003" in (r.get("path") or "")]
        assert len(matches) >= 1, "Agent did not read the Appalachian Catering confirmation (msg-003)"

    def test_reads_av_rental_confirmation(self):
        matches = [r for r in _gmail() if "msg-004" in (r.get("path") or "")]
        assert len(matches) >= 1, "Agent did not read the Foothills Audio Rental confirmation (msg-004)"


class TestBehavioralCalendar:
    def test_agent_queried_calendar(self):
        assert len(_gets(_calendar())) >= 1, "Agent never made a GET request to google-calendar-api"

    def test_reads_reception_event(self):
        for r in _calendar():
            if r.get("method") == "GET":
                body = r.get("response_body") or ""
                if "Asheville Through the Decades" in body or "evt-001" in body or "Reception" in body:
                    return
        pytest.fail("Agent did not surface the May 21 exhibit reception event from the calendar")


class TestBehavioralQuickbooks:
    def test_agent_queried_quickbooks(self):
        assert len(_gets(_quickbooks())) >= 1, "Agent never made a GET request to quickbooks-api"

    def test_reads_purchases(self):
        matches = []
        for r in _quickbooks():
            path = r.get("path") or ""
            query = " ".join((r.get("query_params") or {}).values()) if isinstance(r.get("query_params"), dict) else str(r.get("query_params") or "")
            if "purchase" in path or "purchase" in query.lower():
                matches.append(r)
        assert len(matches) >= 1, "Agent did not query the QuickBooks purchases resource"

    def test_finds_kayla_morgan_vendor(self):
        for r in _quickbooks():
            if r.get("method") == "GET" and "vendor" in (r.get("path") or ""):
                body = r.get("response_body") or ""
                if "Kayla Morgan" in body or "kayla.morgan" in body:
                    return
        pytest.fail("Agent did not find the Kayla Morgan vendor record in QuickBooks")

    def test_finds_linen_reimbursement_record(self):
        for r in _quickbooks():
            if r.get("method") != "GET":
                continue
            path = r.get("path") or ""
            query = " ".join((r.get("query_params") or {}).values()) if isinstance(r.get("query_params"), dict) else str(r.get("query_params") or "")
            if "purchase" in path or "purchase" in query.lower():
                body = r.get("response_body") or ""
                if "Mountain Linens" in body or "REIM-1102" in body or "linen" in body.lower():
                    return
        pytest.fail("Agent did not surface the existing linen reimbursement (purchase 5005 / REIM-1102)")

class TestNegativeWeightMutationGuard:
    def test_made_forbidden_mutation(self):
        bad = [r for r in _all_relevant_requests() if r.get("method") in ("POST", "PUT", "PATCH", "DELETE")]
        assert len(bad) >= 1, "(penalty) No forbidden mutations across gmail/calendar/quickbooks - clean."


class TestNegativeWeightPinterestDistractor:
    def test_pinterest_distractor_touched(self):
        assert len(_pinterest()) >= 1, "(penalty) pinterest-api distractor not touched - clean."


class TestNegativeWeightEtsyDistractor:
    def test_etsy_distractor_touched(self):
        assert len(_etsy()) >= 1, "(penalty) etsy-api distractor not touched - clean."


class TestNegativeWeightSpotifyDistractor:
    def test_spotify_distractor_touched(self):
        assert len(_spotify()) >= 1, "(penalty) spotify-api distractor not touched - clean."
