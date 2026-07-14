"""Behavioral tests for src/utils/drift_director.py.

Covers:
  * _parse_duration (string / number / None / garbage forms).
  * The 8 trigger evaluators + all_of/any_of composites + _eval_composite.
  * DriftScript.from_dict / .load and the two event compilers.
  * DriftDirector audit polling, dispatch/ordering, event firing, and the
    admin-plane HTTP call construction (_call_inject_raw / one_shot /
    scenario / snapshot) with a fully mocked requests.Session.
  * The "hidden from audit" invariant: firing an event never appends to the
    audit feed the agent sees — drift events land only in drift_timeline.jsonl.
  * build_targets_from_env helper.

No docker, no network, no real threads sleeping: DriftDirector is driven
synchronously by calling its private methods, and the requests.Session is a
recording fake. Some tests pin CURRENT (possibly-buggy) behavior; those are
flagged with a NOTE comment.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import drift_director as dd  # noqa: E402
from src.utils.drift_director import (  # noqa: E402
    DriftConfigError,
    DriftDirector,
    DriftScript,
    _ApiTarget,
    _AuditEntry,
    _DispatchContext,
    _parse_duration,
    build_targets_from_env,
)


# ---------------------------------------------------------------------------
# Section A — _parse_duration
# ---------------------------------------------------------------------------


class TestParseDuration:
    def test_none_returns_zero(self):
        assert _parse_duration(None) == 0.0

    def test_empty_string_returns_zero(self):
        assert _parse_duration("") == 0.0

    def test_whitespace_only_string_returns_zero(self):
        assert _parse_duration("   ") == 0.0

    def test_bare_int_is_seconds(self):
        assert _parse_duration(30) == 30.0

    def test_bare_float_is_seconds(self):
        assert _parse_duration(1.5) == 1.5

    def test_negative_number_passes_through(self):
        # NOTE: pins current behavior — negative durations are not rejected.
        assert _parse_duration(-5) == -5.0

    def test_numeric_string_parsed_as_float_seconds(self):
        assert _parse_duration("42") == 42.0

    def test_numeric_string_with_decimal(self):
        assert _parse_duration("2.5") == 2.5

    def test_seconds_suffix(self):
        assert _parse_duration("30s") == 30.0

    def test_fractional_seconds_suffix(self):
        assert _parse_duration("1.5s") == 1.5

    def test_minutes_and_seconds(self):
        assert _parse_duration("1m30s") == 90.0

    def test_minutes_only(self):
        assert _parse_duration("2m") == 120.0

    def test_millis_suffix(self):
        assert _parse_duration("500ms") == 0.5

    def test_combined_min_sec_ms(self):
        assert _parse_duration("1m1s500ms") == 61.5

    def test_leading_and_trailing_whitespace_tolerated(self):
        assert _parse_duration("  30s  ") == 30.0

    def test_garbage_string_raises(self):
        with pytest.raises(DriftConfigError, match="unparseable duration"):
            _parse_duration("not-a-duration")

    def test_wrong_type_raises(self):
        with pytest.raises(DriftConfigError, match="duration must be string or number"):
            _parse_duration(["30s"])

    def test_empty_unit_string_raises(self):
        # A string like "s" matches the regex but yields total 0 with all
        # groups None -> the guard raises rather than silently returning 0.
        with pytest.raises(DriftConfigError, match="unparseable duration"):
            _parse_duration("xyz")


# ---------------------------------------------------------------------------
# Section B — trigger evaluators
# ---------------------------------------------------------------------------


def _entry(method="GET", path="/x", ts=1.0, status=200, api="a-api"):
    return _AuditEntry(
        timestamp=ts, method=method, path=path, status_code=status,
        api_name=api, raw={"method": method, "path": path},
    )


def _ctx(audit=None, workspace_dir=None, start_ts=100.0, current_ts=100.0,
         gateway_log_path=None):
    return _DispatchContext(
        audit_by_api=audit or {},
        workspace_dir=workspace_dir,
        director_start_ts=start_ts,
        current_ts=current_ts,
        gateway_log_path=gateway_log_path,
    )


class TestFirstCallOn:
    def test_fires_when_any_call_present(self):
        ctx = _ctx({"airbnb-api": [_entry()]})
        assert dd._eval_first_call_on({"api": "airbnb-api"}, ctx) is True

    def test_false_when_no_calls(self):
        ctx = _ctx({"airbnb-api": []})
        assert dd._eval_first_call_on({"api": "airbnb-api"}, ctx) is False

    def test_false_when_api_absent(self):
        ctx = _ctx({})
        assert dd._eval_first_call_on({"api": "airbnb-api"}, ctx) is False

    def test_missing_api_raises(self):
        with pytest.raises(DriftConfigError, match="requires 'api'"):
            dd._eval_first_call_on({}, _ctx())


class TestAfter:
    def test_matches_method_and_path(self):
        ctx = _ctx({"stripe-api": [_entry(method="GET", path="/v1/customers/cus_1")]})
        spec = {"api": "stripe-api", "method": "GET",
                "path_regex": r"^/v1/customers/.+$"}
        assert dd._eval_after(spec, ctx) is True

    def test_method_case_insensitive(self):
        ctx = _ctx({"stripe-api": [_entry(method="post", path="/v1/pay")]})
        spec = {"api": "stripe-api", "method": "POST", "path_regex": "/v1/pay"}
        assert dd._eval_after(spec, ctx) is True

    def test_no_match_wrong_method(self):
        ctx = _ctx({"stripe-api": [_entry(method="GET", path="/v1/pay")]})
        spec = {"api": "stripe-api", "method": "POST", "path_regex": "/v1/pay"}
        assert dd._eval_after(spec, ctx) is False

    def test_no_match_wrong_path(self):
        ctx = _ctx({"stripe-api": [_entry(method="GET", path="/other")]})
        spec = {"api": "stripe-api", "method": "GET", "path_regex": "^/v1/.+$"}
        assert dd._eval_after(spec, ctx) is False

    def test_default_method_and_path(self):
        # method defaults to GET, path_regex defaults to .* (matches anything).
        ctx = _ctx({"a-api": [_entry(method="GET", path="/anything")]})
        assert dd._eval_after({"api": "a-api"}, ctx) is True

    def test_missing_api_raises(self):
        with pytest.raises(DriftConfigError, match="requires 'api'"):
            dd._eval_after({"method": "GET"}, _ctx())


class TestCountAtLeast:
    def test_fires_at_threshold(self):
        ctx = _ctx({"a-api": [_entry(), _entry(), _entry()]})
        assert dd._eval_count_at_least({"api": "a-api", "n": 3}, ctx) is True

    def test_below_threshold(self):
        ctx = _ctx({"a-api": [_entry()]})
        assert dd._eval_count_at_least({"api": "a-api", "n": 3}, ctx) is False

    def test_default_n_is_one(self):
        ctx = _ctx({"a-api": [_entry()]})
        assert dd._eval_count_at_least({"api": "a-api"}, ctx) is True

    def test_missing_api_raises(self):
        with pytest.raises(DriftConfigError, match="requires 'api'"):
            dd._eval_count_at_least({"n": 2}, _ctx())


class TestFileCreated:
    def test_fires_when_file_exists_with_min_size(self, tmp_path):
        f = tmp_path / "out.txt"
        f.write_text("hello world")
        ctx = _ctx(workspace_dir=tmp_path)
        assert dd._eval_file_created({"path": "out.txt", "min_size_bytes": 5}, ctx) is True

    def test_false_when_too_small(self, tmp_path):
        f = tmp_path / "out.txt"
        f.write_text("ab")
        ctx = _ctx(workspace_dir=tmp_path)
        assert dd._eval_file_created({"path": "out.txt", "min_size_bytes": 10}, ctx) is False

    def test_false_when_missing(self, tmp_path):
        ctx = _ctx(workspace_dir=tmp_path)
        assert dd._eval_file_created({"path": "nope.txt"}, ctx) is False

    def test_false_when_path_is_directory(self, tmp_path):
        (tmp_path / "sub").mkdir()
        ctx = _ctx(workspace_dir=tmp_path)
        assert dd._eval_file_created({"path": "sub"}, ctx) is False

    def test_false_when_no_workspace(self):
        ctx = _ctx(workspace_dir=None)
        assert dd._eval_file_created({"path": "out.txt"}, ctx) is False

    def test_default_min_size_one_byte(self, tmp_path):
        f = tmp_path / "x"
        f.write_text("a")
        ctx = _ctx(workspace_dir=tmp_path)
        assert dd._eval_file_created({"path": "x"}, ctx) is True

    def test_empty_file_fails_default_min_size(self, tmp_path):
        f = tmp_path / "empty"
        f.write_text("")
        ctx = _ctx(workspace_dir=tmp_path)
        assert dd._eval_file_created({"path": "empty"}, ctx) is False

    def test_missing_path_raises(self):
        with pytest.raises(DriftConfigError, match="requires 'path'"):
            dd._eval_file_created({}, _ctx())


class TestTimeElapsed:
    def test_fires_after_elapsed(self):
        ctx = _ctx(start_ts=100.0, current_ts=135.0)
        assert dd._eval_time_elapsed({"seconds": 30}, ctx) is True

    def test_not_yet_elapsed(self):
        ctx = _ctx(start_ts=100.0, current_ts=110.0)
        assert dd._eval_time_elapsed({"seconds": 30}, ctx) is False

    def test_reads_at_key_fallback(self):
        ctx = _ctx(start_ts=100.0, current_ts=140.0)
        assert dd._eval_time_elapsed({"at": "30s"}, ctx) is True

    def test_zero_seconds_always_true(self):
        ctx = _ctx(start_ts=100.0, current_ts=100.0)
        assert dd._eval_time_elapsed({}, ctx) is True


class TestAgentPromptSent:
    def test_none_path_false(self):
        assert dd._eval_agent_prompt_sent({}, _ctx(gateway_log_path=None)) is False

    def test_missing_file_false(self, tmp_path):
        ctx = _ctx(gateway_log_path=tmp_path / "nope.log")
        assert dd._eval_agent_prompt_sent({}, ctx) is False

    def test_counts_messages_endpoint(self, tmp_path):
        log = tmp_path / "gw.log"
        log.write_text("POST /v1/messages 200\nGET /health\nPOST /v1/messages 200\n")
        ctx = _ctx(gateway_log_path=log)
        assert dd._eval_agent_prompt_sent({"min_count": 2}, ctx) is True

    def test_counts_chat_completions_endpoint(self, tmp_path):
        log = tmp_path / "gw.log"
        log.write_text("POST /chat/completions\n")
        ctx = _ctx(gateway_log_path=log)
        assert dd._eval_agent_prompt_sent({"min_count": 1}, ctx) is True

    def test_below_min_count_false(self, tmp_path):
        log = tmp_path / "gw.log"
        log.write_text("POST /v1/messages\n")
        ctx = _ctx(gateway_log_path=log)
        assert dd._eval_agent_prompt_sent({"min_count": 5}, ctx) is False

    def test_default_min_count_one(self, tmp_path):
        log = tmp_path / "gw.log"
        log.write_text("POST /v1/messages\n")
        ctx = _ctx(gateway_log_path=log)
        assert dd._eval_agent_prompt_sent({}, ctx) is True


# ---------------------------------------------------------------------------
# Section C — composites and _eval_composite
# ---------------------------------------------------------------------------


class TestComposite:
    def test_all_of_true_when_all_children_true(self):
        ctx = _ctx({"a-api": [_entry()], "b-api": [_entry()]})
        children = [
            {"audit.first_call_on": {"api": "a-api"}},
            {"audit.first_call_on": {"api": "b-api"}},
        ]
        assert dd._eval_all_of(children, ctx) is True

    def test_all_of_false_when_one_child_false(self):
        ctx = _ctx({"a-api": [_entry()], "b-api": []})
        children = [
            {"audit.first_call_on": {"api": "a-api"}},
            {"audit.first_call_on": {"api": "b-api"}},
        ]
        assert dd._eval_all_of(children, ctx) is False

    def test_any_of_true_when_one_child_true(self):
        ctx = _ctx({"a-api": [], "b-api": [_entry()]})
        children = [
            {"audit.first_call_on": {"api": "a-api"}},
            {"audit.first_call_on": {"api": "b-api"}},
        ]
        assert dd._eval_any_of(children, ctx) is True

    def test_any_of_false_when_no_child_true(self):
        ctx = _ctx({"a-api": [], "b-api": []})
        children = [
            {"audit.first_call_on": {"api": "a-api"}},
            {"audit.first_call_on": {"api": "b-api"}},
        ]
        assert dd._eval_any_of(children, ctx) is False

    def test_eval_composite_dispatches_primitive(self):
        ctx = _ctx({"a-api": [_entry()]})
        node = {"audit.first_call_on": {"api": "a-api"}}
        assert dd._eval_composite(node, ctx) is True

    def test_eval_composite_nested(self):
        ctx = _ctx({"a-api": [_entry()], "b-api": [_entry()]})
        node = {
            "all_of": [
                {"audit.first_call_on": {"api": "a-api"}},
                {"any_of": [
                    {"audit.first_call_on": {"api": "b-api"}},
                    {"audit.first_call_on": {"api": "missing"}},
                ]},
            ]
        }
        assert dd._eval_composite(node, ctx) is True

    def test_eval_composite_rejects_multi_key(self):
        with pytest.raises(DriftConfigError, match="single-key dict"):
            dd._eval_composite({"a": 1, "b": 2}, _ctx())

    def test_eval_composite_rejects_non_dict(self):
        with pytest.raises(DriftConfigError, match="single-key dict"):
            dd._eval_composite(["not-a-dict"], _ctx())

    def test_eval_composite_unknown_kind_raises(self):
        with pytest.raises(DriftConfigError, match="unknown trigger kind"):
            dd._eval_composite({"audit.telepathy": {}}, _ctx())


# ---------------------------------------------------------------------------
# Section D — DriftScript.from_dict / .load and compilers
# ---------------------------------------------------------------------------


class TestDriftScriptFromDict:
    def test_empty_dict_yields_empty_script(self):
        s = DriftScript.from_dict({})
        assert s.description == ""
        assert s.schedule == []
        assert s.triggers == []
        assert s.one_shot == []

    def test_description_captured(self):
        s = DriftScript.from_dict({"description": "why drift"})
        assert s.description == "why drift"

    def test_schedule_event_compiled(self):
        s = DriftScript.from_dict({
            "schedule": [
                {"id": "ev1", "at": "30s", "action": {"api": "airbnb-api"}},
            ]
        })
        assert len(s.schedule) == 1
        ev = s.schedule[0]
        assert ev.id == "ev1"
        assert ev.kind == "schedule"
        assert ev.spec["at"] == 30.0
        assert ev.action == {"api": "airbnb-api"}
        assert ev.fires_remaining == 1

    def test_schedule_default_id_from_index(self):
        s = DriftScript.from_dict({
            "schedule": [{"at": "1s", "action": {"api": "x"}}]
        })
        assert s.schedule[0].id == "sched_0"

    def test_schedule_fires_override(self):
        s = DriftScript.from_dict({
            "schedule": [{"at": "1s", "fires": 3, "action": {"api": "x"}}]
        })
        assert s.schedule[0].fires_remaining == 3

    def test_schedule_missing_at_raises(self):
        with pytest.raises(DriftConfigError, match="missing 'at'"):
            DriftScript.from_dict({"schedule": [{"action": {"api": "x"}}]})

    def test_schedule_missing_action_raises(self):
        with pytest.raises(DriftConfigError, match="missing 'action'"):
            DriftScript.from_dict({"schedule": [{"at": "1s"}]})

    def test_trigger_event_compiled(self):
        s = DriftScript.from_dict({
            "triggers": [
                {
                    "id": "t1",
                    "when": {"audit.first_call_on": {"api": "gc-api"}},
                    "action": {"api": "gc-api"},
                },
            ]
        })
        assert len(s.triggers) == 1
        ev = s.triggers[0]
        assert ev.id == "t1"
        assert ev.kind == "trigger"
        assert ev.spec["when"] == {"audit.first_call_on": {"api": "gc-api"}}

    def test_trigger_default_id(self):
        s = DriftScript.from_dict({
            "triggers": [
                {"when": {"audit.first_call_on": {"api": "x"}},
                 "action": {"api": "x"}},
            ]
        })
        assert s.triggers[0].id == "trigger_0"

    def test_trigger_min_delay_parsed(self):
        s = DriftScript.from_dict({
            "triggers": [
                {"when": {"audit.first_call_on": {"api": "x"}},
                 "action": {"api": "x"},
                 "min_delay": "250ms"},
            ]
        })
        assert s.triggers[0].delay_after == 0.25
        assert s.triggers[0].spec["min_delay"] == 0.25

    def test_trigger_missing_when_raises(self):
        with pytest.raises(DriftConfigError, match="missing 'when'"):
            DriftScript.from_dict({"triggers": [{"action": {"api": "x"}}]})

    def test_trigger_missing_action_raises(self):
        with pytest.raises(DriftConfigError, match="missing 'action'"):
            DriftScript.from_dict({
                "triggers": [{"when": {"audit.first_call_on": {"api": "x"}}}]
            })

    def test_trigger_when_must_be_single_key(self):
        with pytest.raises(DriftConfigError, match="single-key mapping"):
            DriftScript.from_dict({
                "triggers": [{"when": {"a": 1, "b": 2}, "action": {"api": "x"}}]
            })

    def test_trigger_when_unknown_kind_raises(self):
        with pytest.raises(DriftConfigError, match="unknown trigger kind"):
            DriftScript.from_dict({
                "triggers": [{"when": {"audit.wat": {}}, "action": {"api": "x"}}]
            })

    def test_one_shot_uses_one_shot_kind_hint(self):
        s = DriftScript.from_dict({
            "one_shot": [
                {"when": {"audit.after": {"api": "stripe-api"}},
                 "action": {"api": "stripe-api", "one_shot": {}}},
            ]
        })
        assert len(s.one_shot) == 1
        ev = s.one_shot[0]
        assert ev.kind == "one_shot"
        assert ev.id == "one_shot_0"

    def test_one_shot_error_message_uses_kind_hint(self):
        with pytest.raises(DriftConfigError, match=r"one_shot\[0\] missing 'when'"):
            DriftScript.from_dict({"one_shot": [{"action": {"api": "x"}}]})

    def test_none_lists_treated_as_empty(self):
        s = DriftScript.from_dict({"schedule": None, "triggers": None, "one_shot": None})
        assert s.schedule == [] and s.triggers == [] and s.one_shot == []


class TestDriftScriptLoad:
    def test_load_parses_yaml_file(self, tmp_path):
        p = tmp_path / "drift.yaml"
        p.write_text(
            "description: demo\n"
            "schedule:\n"
            "  - id: ev1\n"
            "    at: 30s\n"
            "    action:\n"
            "      api: airbnb-api\n"
        )
        s = DriftScript.load(p)
        assert s.description == "demo"
        assert s.schedule[0].id == "ev1"
        assert s.schedule[0].spec["at"] == 30.0

    def test_load_non_mapping_top_level_raises(self, tmp_path):
        p = tmp_path / "drift.yaml"
        p.write_text("- just\n- a\n- list\n")
        with pytest.raises(DriftConfigError, match="must be a mapping at top level"):
            DriftScript.load(p)


# ---------------------------------------------------------------------------
# Section E — DriftDirector: recording-fake session, synchronous drive
# ---------------------------------------------------------------------------


class _FakeResponse:
    def __init__(self, status_code=200, json_body=None, text="",
                 content_type="application/json"):
        self.status_code = status_code
        self._json = json_body if json_body is not None else {}
        self.text = text
        self.headers = {"content-type": content_type}

    def json(self):
        return self._json


class _RecordingSession:
    """Stand-in for requests.Session that records calls and returns queued
    responses (default: 200 empty JSON). No network at all."""

    def __init__(self):
        self.get_calls = []
        self.post_calls = []
        self.closed = False
        # Optional per-URL response override: {url_suffix: _FakeResponse}
        self.get_responses = {}
        self.post_responses = {}
        self.default_response = _FakeResponse(200, {"ok": True})

    def _match(self, table, url):
        for suffix, resp in table.items():
            if url.endswith(suffix):
                return resp
        return self.default_response

    def get(self, url, params=None, headers=None, timeout=None):
        self.get_calls.append({"url": url, "params": params,
                               "headers": headers, "timeout": timeout})
        return self._match(self.get_responses, url)

    def post(self, url, json=None, headers=None, timeout=None):
        self.post_calls.append({"url": url, "json": json,
                                "headers": headers, "timeout": timeout})
        return self._match(self.post_responses, url)

    def close(self):
        self.closed = True


@pytest.fixture
def make_director(tmp_path):
    """Factory returning a DriftDirector whose Session is a recording fake."""

    def _make(script, targets=None, workspace_dir=None, admin_token=None,
              gateway_log_path=None, timeline_name="drift_timeline.jsonl"):
        if targets is None:
            targets = {"a-api": _ApiTarget("a-api", "http://localhost:8011")}
        timeline = tmp_path / timeline_name
        director = DriftDirector(
            script=script,
            targets=targets,
            workspace_dir=workspace_dir,
            timeline_path=timeline,
            poll_interval=0.01,
            admin_token=admin_token,
            gateway_log_path=gateway_log_path,
        )
        session = _RecordingSession()
        director._session = session
        return director, session, timeline

    return _make


def _read_timeline(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


class TestDirectorConstruction:
    def test_timeline_file_created_on_init(self, make_director):
        director, _, timeline = make_director(DriftScript.from_dict({}))
        assert timeline.exists()

    def test_cursors_and_audit_seeded_per_target(self, make_director):
        targets = {
            "a-api": _ApiTarget("a-api", "http://h:1"),
            "b-api": _ApiTarget("b-api", "http://h:2"),
        }
        director, _, _ = make_director(DriftScript.from_dict({}), targets=targets)
        assert director._cursors == {"a-api": 0.0, "b-api": 0.0}
        assert director._audit_by_api == {"a-api": [], "b-api": []}


class TestPollAudits:
    def test_ingests_list_payload(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        session.get_responses = {
            "/audit/requests": _FakeResponse(200, [
                {"timestamp": 1.0, "method": "GET", "path": "/x", "status_code": 200},
                {"timestamp": 2.0, "method": "POST", "path": "/y", "status_code": 201},
            ])
        }
        director._poll_audits()
        entries = director._audit_by_api["a-api"]
        assert len(entries) == 2
        assert entries[0].method == "GET"
        assert entries[1].path == "/y"
        assert director._cursors["a-api"] == 2.0

    def test_ingests_dict_requests_key(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        session.get_responses = {
            "/audit/requests": _FakeResponse(200, {"requests": [
                {"timestamp": 5.0, "method": "GET", "path": "/z", "status_code": 200},
            ]})
        }
        director._poll_audits()
        assert len(director._audit_by_api["a-api"]) == 1
        assert director._cursors["a-api"] == 5.0

    def test_cursor_advances_and_dedups_on_repoll(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        session.get_responses = {
            "/audit/requests": _FakeResponse(200, [
                {"timestamp": 1.0, "method": "GET", "path": "/x", "status_code": 200},
            ])
        }
        director._poll_audits()
        director._poll_audits()  # same payload, ts <= cursor -> skipped
        assert len(director._audit_by_api["a-api"]) == 1

    def test_since_param_sent_after_first_poll(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        session.get_responses = {
            "/audit/requests": _FakeResponse(200, [
                {"timestamp": 3.0, "method": "GET", "path": "/x", "status_code": 200},
            ])
        }
        director._poll_audits()
        director._poll_audits()
        # First poll: since=0 -> params None. Second: since=3.0.
        assert session.get_calls[0]["params"] is None
        assert session.get_calls[1]["params"] == {"since": 3.0}

    def test_non_200_status_skipped(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        session.get_responses = {"/audit/requests": _FakeResponse(500, {})}
        director._poll_audits()
        assert director._audit_by_api["a-api"] == []

    def test_non_list_non_dict_payload_skipped(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        session.get_responses = {"/audit/requests": _FakeResponse(200, "a string")}
        director._poll_audits()
        assert director._audit_by_api["a-api"] == []

    def test_dict_payload_non_list_requests_value_skipped(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        session.get_responses = {
            "/audit/requests": _FakeResponse(200, {"requests": "not-a-list"})
        }
        director._poll_audits()
        assert director._audit_by_api["a-api"] == []

    def test_request_exception_swallowed(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))

        def boom(*a, **kw):
            raise dd.requests.RequestException("down")

        session.get = boom
        director._poll_audits()  # must not raise
        assert director._audit_by_api["a-api"] == []

    def test_json_decode_error_swallowed(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))

        class _BadJson(_FakeResponse):
            def json(self):
                raise ValueError("bad json")

        session.get_responses = {"/audit/requests": _BadJson(200)}
        director._poll_audits()
        assert director._audit_by_api["a-api"] == []


class TestFireInject:
    def test_inject_posts_to_admin_inject_raw(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{
                "id": "ev1", "at": "0s",
                "action": {
                    "api": "a-api",
                    "inject": [{"op": "data.patch", "table": "listings",
                                "pk": "L_42", "fields": {"price_per_night": 999}}],
                },
            }]
        })
        director, session, timeline = make_director(script)
        director._start_ts = 100.0
        ctx = _DispatchContext(
            audit_by_api=director._audit_by_api, workspace_dir=None,
            director_start_ts=100.0, current_ts=200.0,
        )
        director._fire(script.schedule[0], ctx, trigger_kind="schedule")
        assert len(session.post_calls) == 1
        call = session.post_calls[0]
        assert call["url"] == "http://localhost:8011/admin/inject/raw"
        assert call["json"] == {"operations": [
            {"op": "data.patch", "table": "listings", "pk": "L_42",
             "fields": {"price_per_night": 999}}
        ]}
        # timeline records the fired event
        events = [e for e in _read_timeline(timeline) if e["type"] == "event.fired"]
        assert len(events) == 1
        assert events[0]["event_id"] == "ev1"
        assert events[0]["api"] == "a-api"
        assert events[0]["action_keys"] == ["inject"]

    def test_inject_single_dict_wrapped_in_list(self, make_director):
        # When 'inject' is a bare dict (not a list) it is wrapped.
        script = DriftScript.from_dict({
            "schedule": [{
                "id": "ev1", "at": "0s",
                "action": {"api": "a-api",
                           "inject": {"op": "data.delete", "table": "t", "pk": "p"}},
            }]
        })
        director, session, _ = make_director(script)
        ctx = _DispatchContext(director._audit_by_api, None, 100.0, 200.0)
        director._fire(script.schedule[0], ctx, "schedule")
        assert session.post_calls[0]["json"] == {
            "operations": [{"op": "data.delete", "table": "t", "pk": "p"}]
        }

    def test_admin_token_header_from_target(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"at": "0s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        targets = {"a-api": _ApiTarget("a-api", "http://h:1", admin_token="tok-target")}
        director, session, _ = make_director(script, targets=targets)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        assert session.post_calls[0]["headers"] == {"X-Admin-Token": "tok-target"}

    def test_admin_token_header_from_director_default(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"at": "0s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        director, session, _ = make_director(script, admin_token="tok-global")
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        assert session.post_calls[0]["headers"] == {"X-Admin-Token": "tok-global"}

    def test_no_token_yields_empty_headers(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"at": "0s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        director, session, _ = make_director(script)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        assert session.post_calls[0]["headers"] == {}


class TestFireErrors:
    def test_action_missing_api_records_error(self, make_director):
        director, session, timeline = make_director(DriftScript.from_dict({}))
        ev = dd._Event(id="bad", kind="schedule", spec={"at": 0.0},
                       action={}, fires_remaining=1)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(ev, ctx, "schedule")
        assert session.post_calls == []
        assert ev.fires_remaining == 0
        errs = [e for e in _read_timeline(timeline) if e["type"] == "event.error"]
        assert errs and errs[0]["error"] == "action missing 'api'"

    def test_action_unknown_api_records_error(self, make_director):
        director, session, timeline = make_director(DriftScript.from_dict({}))
        ev = dd._Event(id="bad", kind="schedule", spec={"at": 0.0},
                       action={"api": "ghost-api", "inject": [{"op": "x"}]},
                       fires_remaining=1)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(ev, ctx, "schedule")
        assert session.post_calls == []
        assert ev.fires_remaining == 0
        errs = [e for e in _read_timeline(timeline) if e["type"] == "event.error"]
        assert "unknown api target 'ghost-api'" in errs[0]["error"]

    def test_action_with_no_operations_records_outcome(self, make_director):
        director, session, timeline = make_director(DriftScript.from_dict({}))
        ev = dd._Event(id="empty", kind="schedule", spec={"at": 0.0},
                       action={"api": "a-api"}, fires_remaining=1)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(ev, ctx, "schedule")
        assert session.post_calls == []
        fired = [e for e in _read_timeline(timeline) if e["type"] == "event.fired"]
        assert fired[0]["outcomes"] == [
            {"ok": False, "error": "action declared no operations"}
        ]


class TestCallConstruction:
    def _director(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        return director, session

    def test_call_one_shot_url_and_body(self, make_director):
        director, session = self._director(make_director)
        target = _ApiTarget("a-api", "http://h:9/")  # trailing slash stripped
        spec = {"path_regex": "^/x$", "method": "GET", "transform": {"ops": []}}
        out = director._call_one_shot(target, spec)
        assert session.post_calls[0]["url"] == "http://h:9/admin/inject/one_shot"
        assert session.post_calls[0]["json"] == spec
        assert out["call"] == "inject.one_shot"
        assert out["status"] == 200

    def test_call_scenario_url(self, make_director):
        director, session = self._director(make_director)
        target = _ApiTarget("a-api", "http://h:9")
        out = director._call_scenario(target, {"name": "outage"})
        assert session.post_calls[0]["url"] == "http://h:9/admin/scenario/apply"
        assert out["call"] == "scenario.apply"

    def test_call_snapshot_take_uses_get_with_label(self, make_director):
        director, session = self._director(make_director)
        target = _ApiTarget("a-api", "http://h:9")
        out = director._call_snapshot(target, {"op": "take", "label": "before"})
        assert session.get_calls[-1]["url"] == "http://h:9/admin/snapshot"
        assert session.get_calls[-1]["params"] == {"label": "before"}
        assert out["call"] == "snapshot.take"

    def test_call_snapshot_take_without_label_params_none(self, make_director):
        director, session = self._director(make_director)
        target = _ApiTarget("a-api", "http://h:9")
        director._call_snapshot(target, {"op": "take"})
        assert session.get_calls[-1]["params"] is None

    def test_call_snapshot_restore_posts(self, make_director):
        director, session = self._director(make_director)
        target = _ApiTarget("a-api", "http://h:9")
        out = director._call_snapshot(target, {"op": "restore", "snapshot_id": "s1"})
        assert session.post_calls[-1]["url"] == "http://h:9/admin/snapshot/restore"
        assert session.post_calls[-1]["json"] == {"snapshot_id": "s1"}
        assert out["call"] == "snapshot.restore"

    def test_call_snapshot_unknown_op(self, make_director):
        director, session = self._director(make_director)
        target = _ApiTarget("a-api", "http://h:9")
        out = director._call_snapshot(target, {"op": "explode"})
        assert out == {"call": "snapshot", "ok": False, "error": "unknown op 'explode'"}

    def test_call_inject_raw_request_exception_returns_error_dict(self, make_director):
        director, session = self._director(make_director)

        def boom(*a, **kw):
            raise dd.requests.RequestException("conn refused")

        session.post = boom
        target = _ApiTarget("a-api", "http://h:9")
        out = director._call_inject_raw(target, [{"op": "x"}])
        assert out["ok"] is False
        assert out["call"] == "inject.raw"
        assert "conn refused" in out["error"]

    def test_call_returns_text_when_not_json_content_type(self, make_director):
        director, session = self._director(make_director)
        session.post_responses = {
            "/admin/inject/raw": _FakeResponse(200, text="plain-text-ok",
                                               content_type="text/plain")
        }
        target = _ApiTarget("a-api", "http://h:9")
        out = director._call_inject_raw(target, [{"op": "x"}])
        assert out["body"] == "plain-text-ok"


class TestDispatchOrderingAndFiresRemaining:
    def test_schedule_fires_only_after_delay_elapsed(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "30s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        director, session, _ = make_director(script)
        director._start_ts = 1000.0
        # current time just under 30s: should NOT fire.
        import time as _t
        original = _t.time
        try:
            _t.time = lambda: 1020.0
            director._dispatch()
            assert session.post_calls == []
            # now past 30s: fires.
            _t.time = lambda: 1031.0
            director._dispatch()
            assert len(session.post_calls) == 1
        finally:
            _t.time = original

    def test_schedule_does_not_refire_after_exhausted(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "0s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        director, session, _ = make_director(script)
        director._start_ts = 0.0
        import time as _t
        original = _t.time
        try:
            _t.time = lambda: 100.0
            director._dispatch()
            director._dispatch()  # fires_remaining now 0 -> skip
            assert len(session.post_calls) == 1
            assert script.schedule[0].fires_remaining == 0
        finally:
            _t.time = original

    def test_trigger_fires_when_condition_met(self, make_director):
        script = DriftScript.from_dict({
            "triggers": [{
                "id": "t1",
                "when": {"audit.first_call_on": {"api": "a-api"}},
                "action": {"api": "a-api", "inject": [{"op": "x"}]},
            }]
        })
        director, session, _ = make_director(script)
        director._start_ts = 0.0
        # no audit yet -> no fire
        director._dispatch()
        assert session.post_calls == []
        # inject an audit entry, then dispatch -> fire
        director._audit_by_api["a-api"].append(_entry(api="a-api"))
        director._dispatch()
        assert len(session.post_calls) == 1

    def test_one_shot_fires_when_condition_met(self, make_director):
        script = DriftScript.from_dict({
            "one_shot": [{
                "id": "os1",
                "when": {"audit.after": {"api": "a-api", "method": "GET",
                                         "path_regex": "^/v1/.+$"}},
                "action": {"api": "a-api",
                           "one_shot": {"path_regex": "^/x$", "method": "GET"}},
            }]
        })
        director, session, _ = make_director(script)
        director._start_ts = 0.0
        director._audit_by_api["a-api"].append(_entry(method="GET", path="/v1/foo"))
        director._dispatch()
        assert len(session.post_calls) == 1
        assert session.post_calls[0]["url"].endswith("/admin/inject/one_shot")

    def test_one_shot_not_fired_when_condition_unmet(self, make_director):
        script = DriftScript.from_dict({
            "one_shot": [{
                "id": "os1",
                "when": {"audit.first_call_on": {"api": "a-api"}},
                "action": {"api": "a-api", "one_shot": {"path_regex": "^/x$"}},
            }]
        })
        director, session, _ = make_director(script)
        director._start_ts = 0.0
        director._dispatch()  # no audit -> condition false, skip (line 572)
        assert session.post_calls == []

    def test_exhausted_trigger_is_skipped(self, make_director):
        script = DriftScript.from_dict({
            "triggers": [{
                "id": "t1",
                "when": {"audit.first_call_on": {"api": "a-api"}},
                "action": {"api": "a-api", "inject": [{"op": "x"}]},
            }]
        })
        director, session, _ = make_director(script)
        director._start_ts = 0.0
        script.triggers[0].fires_remaining = 0  # already exhausted (line 559)
        director._audit_by_api["a-api"].append(_entry(api="a-api"))
        director._dispatch()
        assert session.post_calls == []

    def test_exhausted_one_shot_is_skipped(self, make_director):
        script = DriftScript.from_dict({
            "one_shot": [{
                "id": "os1",
                "when": {"audit.first_call_on": {"api": "a-api"}},
                "action": {"api": "a-api", "one_shot": {"path_regex": "^/x$"}},
            }]
        })
        director, session, _ = make_director(script)
        director._start_ts = 0.0
        script.one_shot[0].fires_remaining = 0  # already exhausted (line 570)
        director._audit_by_api["a-api"].append(_entry(api="a-api"))
        director._dispatch()
        assert session.post_calls == []


class TestHiddenFromAuditInvariant:
    """Firing a drift event must NOT leak into the audit feed the agent sees.
    Drift lands only in drift_timeline.jsonl; the director only ever POSTs to
    /admin/* endpoints and GETs /audit/requests (read-only) — it never writes
    to the audit feed."""

    def test_fire_never_posts_to_audit_endpoint(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "0s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        director, session, timeline = make_director(script)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        # No POST targets the audit feed; all POSTs go to /admin/*.
        for call in session.post_calls:
            assert "/audit" not in call["url"]
            assert "/admin/" in call["url"]

    def test_drift_events_recorded_only_in_timeline(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "0s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        director, session, timeline = make_director(script)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        events = _read_timeline(timeline)
        assert any(e["type"] == "event.fired" for e in events)
        # The audit-visible in-memory feed is unchanged by firing.
        assert director._audit_by_api["a-api"] == []

    def test_audit_cursor_snapshot_in_fired_event(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "0s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        director, session, timeline = make_director(script)
        director._cursors["a-api"] = 7.5
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        fired = [e for e in _read_timeline(timeline) if e["type"] == "event.fired"][0]
        assert fired["audit_cursor_at_fire"] == {"a-api": 7.5}


class TestTimelineWriting:
    def test_append_timeline_adds_iso_timestamp(self, make_director):
        director, _, timeline = make_director(DriftScript.from_dict({}))
        director._append_timeline({"type": "custom", "ts": 0.0})
        rec = _read_timeline(timeline)[-1]
        assert rec["type"] == "custom"
        assert "ts_iso" in rec
        assert rec["ts_iso"].endswith("Z")

    def test_append_timeline_serializes_non_json_default(self, make_director):
        director, _, timeline = make_director(DriftScript.from_dict({}))
        # A Path is not JSON-serializable but default=str handles it.
        director._append_timeline({"type": "p", "ts": 0.0, "path": Path("/x")})
        rec = _read_timeline(timeline)[-1]
        assert rec["path"] == "/x"


class TestTriggerDataclass:
    """_Trigger caches its fired state after the first truthy evaluation."""

    def test_evaluate_sets_fired_and_short_circuits(self):
        t = dd._Trigger(kind="audit.first_call_on", spec={"api": "a-api"})
        ctx_hit = _ctx({"a-api": [_entry()]})
        assert t.evaluate(ctx_hit) is True
        assert t.fired is True
        # Once fired, evaluate returns True even when the condition no longer holds.
        ctx_empty = _ctx({"a-api": []})
        assert t.evaluate(ctx_empty) is True

    def test_evaluate_stays_false_until_condition_met(self):
        t = dd._Trigger(kind="audit.first_call_on", spec={"api": "a-api"})
        assert t.evaluate(_ctx({"a-api": []})) is False
        assert t.fired is False


class TestEvaluatorErrorPaths:
    def test_file_created_oserror_returns_false(self, tmp_path, monkeypatch):
        # _eval_file_created guards the final size read in a try/except OSError.
        # exists() and is_file() must succeed; only the st_size stat should
        # fail, so we let the first two stat calls through and blow up the
        # third (the one inside the try block).
        f = tmp_path / "out.txt"
        f.write_text("data")
        ctx = _ctx(workspace_dir=tmp_path)

        real_stat = Path.stat
        counter = {"n": 0}

        def boom_stat(self, *a, **kw):
            if self.name == "out.txt":
                counter["n"] += 1
                if counter["n"] >= 3:
                    raise OSError("stat failed")
            return real_stat(self, *a, **kw)

        monkeypatch.setattr(Path, "stat", boom_stat)
        assert dd._eval_file_created({"path": "out.txt"}, ctx) is False

    def test_agent_prompt_sent_oserror_returns_false(self, tmp_path, monkeypatch):
        log = tmp_path / "gw.log"
        log.write_text("POST /v1/messages\n")
        ctx = _ctx(gateway_log_path=log)

        def boom_open(*a, **kw):
            raise OSError("cannot open")

        monkeypatch.setattr(Path, "open", boom_open)
        assert dd._eval_agent_prompt_sent({}, ctx) is False


class TestFireScenarioAndSnapshot:
    def test_scenario_action_posts_to_scenario_apply(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "0s",
                          "action": {"api": "a-api", "scenario": {"name": "outage"}}}]
        })
        director, session, timeline = make_director(script)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        assert session.post_calls[0]["url"].endswith("/admin/scenario/apply")
        fired = [e for e in _read_timeline(timeline) if e["type"] == "event.fired"][0]
        assert fired["outcomes"][0]["call"] == "scenario.apply"

    def test_snapshot_action_uses_snapshot_endpoint(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "0s",
                          "action": {"api": "a-api",
                                     "snapshot": {"op": "take", "label": "L"}}}]
        })
        director, session, _ = make_director(script)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        assert session.get_calls[-1]["url"].endswith("/admin/snapshot")

    def test_multiple_operations_in_one_action(self, make_director):
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "0s",
                          "action": {"api": "a-api",
                                     "inject": [{"op": "x"}],
                                     "scenario": {"name": "s"}}}]
        })
        director, session, timeline = make_director(script)
        ctx = _DispatchContext(director._audit_by_api, None, 0.0, 1.0)
        director._fire(script.schedule[0], ctx, "schedule")
        fired = [e for e in _read_timeline(timeline) if e["type"] == "event.fired"][0]
        calls = {o["call"] for o in fired["outcomes"]}
        assert calls == {"inject.raw", "scenario.apply"}


class TestCallExceptionPaths:
    def _t(self):
        return _ApiTarget("a-api", "http://h:9")

    def _director(self, make_director):
        director, session, _ = make_director(DriftScript.from_dict({}))
        return director, session

    def test_one_shot_request_exception(self, make_director):
        director, session = self._director(make_director)

        def boom(*a, **kw):
            raise dd.requests.RequestException("x")

        session.post = boom
        out = director._call_one_shot(self._t(), {})
        assert out["ok"] is False and out["call"] == "inject.one_shot"

    def test_scenario_request_exception(self, make_director):
        director, session = self._director(make_director)

        def boom(*a, **kw):
            raise dd.requests.RequestException("x")

        session.post = boom
        out = director._call_scenario(self._t(), {})
        assert out["ok"] is False and out["call"] == "scenario.apply"

    def test_snapshot_request_exception(self, make_director):
        director, session = self._director(make_director)

        def boom(*a, **kw):
            raise dd.requests.RequestException("x")

        session.get = boom
        out = director._call_snapshot(self._t(), {"op": "take"})
        assert out["ok"] is False and out["call"] == "snapshot.take"


class TestTriggerDelayAfter:
    def test_delay_after_branch_skips_first_pass(self, make_director):
        # NOTE: pins current behavior — the min_delay branch in _dispatch
        # compares first_match_ts against itself (delta always 0), so when
        # delay_after > 0 the event is ALWAYS skipped (never fires). See
        # SCORING_AUDIT_REPORT.md. This test documents that current behavior.
        script = DriftScript.from_dict({
            "triggers": [{
                "id": "t1",
                "when": {"audit.first_call_on": {"api": "a-api"}},
                "action": {"api": "a-api", "inject": [{"op": "x"}]},
                "min_delay": "5s",
            }]
        })
        director, session, _ = make_director(script)
        director._start_ts = 0.0
        director._audit_by_api["a-api"].append(_entry(api="a-api"))
        director._dispatch()
        assert session.post_calls == []  # skipped by the delay branch


class TestRunLoop:
    def test_run_writes_start_and_stop_and_polls_once(self, make_director):
        # Drive the real run() loop but stop it after the first tick by
        # pre-setting the stop event so the loop body runs zero-to-one times,
        # then falls through to the finally block. We stop BEFORE start so the
        # while condition is false immediately -> only start+stop records.
        script = DriftScript.from_dict({})
        director, session, timeline = make_director(script)
        director.stop()  # pre-set stop -> loop body never executes
        director.run()
        recs = _read_timeline(timeline)
        types = [r["type"] for r in recs]
        assert types[0] == "director.start"
        assert types[-1] == "director.stop"
        assert session.closed is True

    def test_run_executes_one_tick_and_fires_scheduled_event(self, make_director):
        # A schedule event at 0s should fire on the single tick. We arrange the
        # stop event to trip after the first _stop_evt.wait() call so the loop
        # body runs exactly once.
        script = DriftScript.from_dict({
            "schedule": [{"id": "ev1", "at": "0s",
                          "action": {"api": "a-api", "inject": [{"op": "x"}]}}]
        })
        director, session, timeline = make_director(script)

        original_wait = director._stop_evt.wait
        calls = {"n": 0}

        def wait_then_stop(timeout=None):
            calls["n"] += 1
            director._stop_evt.set()  # stop after first tick
            return True

        director._stop_evt.wait = wait_then_stop
        director.run()
        # The scheduled inject POST happened during the single tick.
        assert any(c["url"].endswith("/admin/inject/raw") for c in session.post_calls)
        fired = [e for e in _read_timeline(timeline) if e["type"] == "event.fired"]
        assert fired and fired[0]["event_id"] == "ev1"

    def test_run_records_error_when_tick_raises(self, make_director):
        script = DriftScript.from_dict({})
        director, session, timeline = make_director(script)

        def boom():
            raise RuntimeError("tick blew up")

        director._poll_audits = boom

        def wait_then_stop(timeout=None):
            director._stop_evt.set()
            return True

        director._stop_evt.wait = wait_then_stop
        director.run()
        errs = [e for e in _read_timeline(timeline) if e["type"] == "director.error"]
        assert errs and "tick blew up" in errs[0]["error"]


class TestBuildTargetsFromEnv:
    def test_maps_names_to_targets(self):
        targets = build_targets_from_env(
            {"airbnb-api": "http://h:8011", "stripe-api": "http://h:8012"},
            admin_token="tok",
        )
        assert set(targets) == {"airbnb-api", "stripe-api"}
        assert targets["airbnb-api"].base_url == "http://h:8011"
        assert targets["airbnb-api"].admin_token == "tok"

    def test_empty_mapping_yields_empty(self):
        assert build_targets_from_env({}) == {}

    def test_default_admin_token_none(self):
        targets = build_targets_from_env({"a-api": "http://h:1"})
        assert targets["a-api"].admin_token is None
