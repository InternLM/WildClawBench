"""Tests for lint L27: endpoint paths in generated tests must match served routes.

Pins the contract that caught the Mailchimp grading bug: the audit summary keys
requests by the FULL served path ("POST /3.0/campaigns/..."), so a generated
test matching "POST /campaigns" silently counts 0 — the hard-fail guard never
fires and the intended-read credit is unwinnable. L27 rejects any endpoint
path that prefix-matches no served route, feeding the failure back into the
testgen repair loop.
"""
from __future__ import annotations

from src.utils.testgen.lints import (
    _extract_endpoint_refs,
    _route_prefix_match,
    self_validate_tests,
)
from src.utils.testgen.services import _extract_routes_from_source

import ast

MAILCHIMP_ROUTES = [
    "/3.0/lists",
    "/3.0/lists/{list_id}",
    "/3.0/lists/{list_id}/members",
    "/3.0/campaigns",
    "/3.0/campaigns/{campaign_id}",
    "/3.0/campaigns/{campaign_id}/actions/send",
]
SERVICE_ROUTES = {"MAILCHIMP_API_URL": MAILCHIMP_ROUTES}


def _l27(code: str, service_routes=SERVICE_ROUTES) -> list[str]:
    fails = self_validate_tests(
        code, {}, has_api_services=True, service_routes=service_routes
    )
    return [f for f in fails if f.startswith("L27")]


# --- route extractor -------------------------------------------------------

def test_extract_routes_plain_and_base_const():
    source = (
        'BASE = "/services/data/v59.0"\n'
        '@app.get("/health")\n'
        "def health(): ...\n"
        '@app.get(BASE + "/query")\n'
        "def query(): ...\n"
        '@app.post("/3.0/lists/{list_id}/members")\n'
        "def add(): ...\n"
    )
    routes = _extract_routes_from_source(source)
    assert "/services/data/v59.0/query" in routes
    assert "/3.0/lists/{list_id}/members" in routes
    assert "/health" in routes


# --- prefix matcher --------------------------------------------------------

def test_prefix_match_params_and_case():
    assert _route_prefix_match("/3.0/lists", "/3.0/lists/{list_id}")
    assert _route_prefix_match("/3.0/LISTS", "/3.0/lists")
    assert _route_prefix_match(
        "/3.0/campaigns/abc123/actions/send",
        "/3.0/campaigns/{campaign_id}/actions/send",
    )
    assert not _route_prefix_match("/lists", "/3.0/lists")
    assert not _route_prefix_match("/3.0/lists/x/members/extra", "/3.0/lists/{list_id}/members")


# --- L27: the two shapes of the original Mailchimp bug ---------------------

def test_l27_flags_dropped_prefix_in_helper_call():
    code = (
        "def test_unauthorized_send():\n"
        '    summary = api_get(MAILCHIMP_API_URL, "/audit/summary")\n'
        '    assert _endpoint_count(summary, "POST", "/campaigns") >= 1\n'
    )
    fails = _l27(code)
    assert len(fails) == 1
    assert "/campaigns" in fails[0]
    assert "/3.0/campaigns" in fails[0]  # did-you-mean hint


def test_l27_flags_method_key_literal_without_prefix():
    code = (
        "def test_intended_read():\n"
        '    summary = api_get(MAILCHIMP_API_URL, "/audit/summary")\n'
        '    assert any(k.upper().startswith("GET /LISTS") for k in summary["endpoints"])\n'
    )
    fails = _l27(code)
    assert len(fails) == 1


def test_l27_passes_full_served_paths():
    code = (
        "def test_ok():\n"
        '    data = api_get(MAILCHIMP_API_URL, "/3.0/lists")\n'
        '    summary = api_get(MAILCHIMP_API_URL, "/audit/summary")\n'
        '    assert any(k.startswith("POST /3.0/campaigns/") and "/actions/send" in k\n'
        '               for k in summary["endpoints"])\n'
        '    assert _endpoint_count(summary, "GET", "/3.0/lists") >= 1\n'
    )
    assert _l27(code) == []


def test_l27_flags_dropped_prefix_in_api_get_path():
    code = (
        "def test_read():\n"
        '    data = api_get(MAILCHIMP_API_URL, "/lists")\n'
    )
    fails = _l27(code)
    assert len(fails) == 1
    assert "MAILCHIMP_API_URL" in fails[0]


# --- L27: things that must NOT fire ----------------------------------------

def test_l27_whitelists_shared_plane_paths():
    code = (
        "def test_audit():\n"
        '    api_get(MAILCHIMP_API_URL, "/audit/requests")\n'
        '    api_get(MAILCHIMP_API_URL, "/health")\n'
        '    api_get(MAILCHIMP_API_URL, "/admin/state")\n'
    )
    assert _l27(code) == []


def test_l27_skips_unknown_url_constants():
    # A constant outside the scoped service map is not ours to judge.
    code = (
        "def test_other():\n"
        '    api_get(SOME_OTHER_URL, "/whatever")\n'
    )
    assert _l27(code) == []


def test_l27_disabled_without_route_map():
    code = (
        "def test_read():\n"
        '    api_get(MAILCHIMP_API_URL, "/lists")\n'
    )
    assert _l27(code, service_routes=None) == []
    assert _l27(code, service_routes={}) == []


def test_l27_fstring_leading_literal():
    code = (
        "def test_member():\n"
        '    api_get(MAILCHIMP_API_URL, f"/3.0/lists/{list_id}/members")\n'
        '    api_get(MAILCHIMP_API_URL, f"/lists/{list_id}")\n'
    )
    fails = _l27(code)
    assert len(fails) == 1
    assert "'/lists'" in fails[0]


def test_extract_refs_one_arg_helpers():
    tree = ast.parse('_get(f"{MAILCHIMP_API_URL}/3.0/lists")')
    refs = _extract_endpoint_refs(tree)
    assert ("MAILCHIMP_API_URL", "/3.0/lists", "prefix") in refs


# --- L27: helper semantics — substring helpers are legit, startswith is not --

_SUBSTRING_HELPER = (
    "def _count_methods(endpoints, method, path_substr=''):\n"
    "    total = 0\n"
    "    for key, meta in endpoints.items():\n"
    "        m, _, p = key.partition(' ')\n"
    "        if m == method and path_substr in p:\n"
    "            total += meta.get('count', 0)\n"
    "    return total\n"
)

_STARTSWITH_HELPER = (
    "def _endpoint_count(summary, method, prefix):\n"
    "    total = 0\n"
    "    for key, info in summary.get('endpoints', {}).items():\n"
    "        if key.upper().startswith(f'{method} {prefix}'.upper()):\n"
    "            total += info.get('count', 0)\n"
    "    return total\n"
)


def test_l27_allows_bare_tail_with_substring_helper():
    # patricia_waters shape: "/send" via an `in`-matching helper works at
    # runtime against /gmail/v1/users/me/messages/send — must not be flagged.
    routes = {"GMAIL_API_URL": ["/gmail/v1/users/me/messages/send"]}
    code = _SUBSTRING_HELPER + (
        "def test_no_send():\n"
        '    assert _count_methods(eps, "POST", "/send") == 0\n'
    )
    assert _l27(code, service_routes=routes) == []


def test_l27_still_flags_bare_tail_with_startswith_helper():
    # mailchimp shape: same call-site literals, but startswith semantics make
    # the dropped prefix dead code — must be flagged.
    code = _STARTSWITH_HELPER + (
        "def test_guard():\n"
        '    assert _endpoint_count(summary, "POST", "/campaigns") >= 1\n'
    )
    fails = _l27(code)
    assert len(fails) == 1
    assert "/3.0/campaigns" in fails[0]


def test_l27_allows_method_key_in_containment_check():
    routes = {"GMAIL_API_URL": ["/gmail/v1/users/me/messages/send"]}
    code = (
        "def test_sent():\n"
        '    assert any("POST /send" in k for k in eps)\n'
    )
    assert _l27(code, service_routes=routes) == []
