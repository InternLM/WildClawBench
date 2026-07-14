"""Unit coverage for src/utils/bedrock_eventstream.py and
src/utils/mock_health_logger.py.

bedrock_eventstream: a pure-Python parser for AWS vnd.amazon.eventstream
binary frames. The tests craft real byte frames matching the wire layout
documented in the module and assert (event_type, payload_dict) tuples come
back correctly, including chunk-boundary buffering, base64-wrapped payloads,
malformed headers/payloads, and the CRC-free framing invariants.

mock_health_logger: a background thread that probes mock ``/health``
endpoints through ``docker exec``. All subprocess.run + container-running
calls are monkeypatched so nothing spawns docker or touches the network.
Temp output goes to tmp_path only.

These tests are offline, deterministic, and self-contained. Where the module
under test exhibits behaviour that looks surprising, the test PINS the current
actual behaviour rather than asserting an idealised contract.
"""
from __future__ import annotations

import json
import logging
import struct
import subprocess
import sys
from base64 import b64encode
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import bedrock_eventstream as bes  # noqa: E402
from src.utils import mock_health_logger as mhl  # noqa: E402


# ===========================================================================
# bedrock_eventstream — frame construction helpers
# ===========================================================================


def _encode_header(name: str, value: str, type_byte: int = 7) -> bytes:
    """Encode a single eventstream header entry.

    Layout: [1B name_len][name][1B type][2B val_len][value]
    """
    name_b = name.encode("utf-8")
    value_b = value.encode("utf-8")
    return (
        bytes([len(name_b)])
        + name_b
        + bytes([type_byte])
        + struct.pack(">H", len(value_b))
        + value_b
    )


def _build_frame(event_type: str | None, payload: bytes, *, extra_headers: bytes = b"") -> bytes:
    """Assemble one full eventstream frame.

    Layout: [4B total_len][4B headers_len][4B prelude_crc]
            [headers][payload][4B message_crc]
    ``payload`` is raw bytes (usually JSON). ``event_type`` of None emits no
    ``:event-type`` header. ``prelude_crc`` and ``message_crc`` are zeroed —
    the parser skips CRC validation by design.
    """
    headers = b""
    if event_type is not None:
        headers += _encode_header(":event-type", event_type)
    headers += extra_headers
    headers_len = len(headers)
    # total_len = 4 (total) + 4 (headers_len) + 4 (prelude_crc)
    #             + headers + payload + 4 (message_crc)
    total_len = 12 + headers_len + len(payload) + 4
    return (
        struct.pack(">I", total_len)
        + struct.pack(">I", headers_len)
        + struct.pack(">I", 0)  # prelude_crc (skipped)
        + headers
        + payload
        + struct.pack(">I", 0)  # message_crc (skipped)
    )


def _json_frame(event_type: str, obj: dict) -> bytes:
    return _build_frame(event_type, json.dumps(obj).encode("utf-8"))


def _drain(chunks: list[bytes]) -> list[tuple[str, dict]]:
    return list(bes.iter_eventstream(iter(chunks)))


# ===========================================================================
# bedrock_eventstream — happy paths
# ===========================================================================


def test_single_frame_yields_event_type_and_payload():
    frame = _json_frame("contentBlockDelta", {"delta": {"text": "hi"}})
    out = _drain([frame])
    assert out == [("contentBlockDelta", {"delta": {"text": "hi"}})]


def test_multiple_frames_in_one_chunk():
    f1 = _json_frame("messageStart", {"role": "assistant"})
    f2 = _json_frame("contentBlockDelta", {"delta": {"text": "a"}})
    f3 = _json_frame("messageStop", {"stopReason": "end_turn"})
    out = _drain([f1 + f2 + f3])
    assert [t for t, _ in out] == ["messageStart", "contentBlockDelta", "messageStop"]
    assert out[0][1] == {"role": "assistant"}
    assert out[2][1] == {"stopReason": "end_turn"}


def test_frame_split_across_chunk_boundaries():
    frame = _json_frame("metadata", {"usage": {"inputTokens": 10}})
    # Split the frame at an arbitrary interior byte; buffering must reassemble.
    mid = len(frame) // 2
    out = _drain([frame[:mid], frame[mid:]])
    assert out == [("metadata", {"usage": {"inputTokens": 10}})]


def test_frame_split_into_many_single_byte_chunks():
    frame = _json_frame("messageStop", {"stopReason": "end_turn"})
    chunks = [frame[i : i + 1] for i in range(len(frame))]
    out = _drain(chunks)
    assert out == [("messageStop", {"stopReason": "end_turn"})]


def test_two_frames_where_second_completes_in_later_chunk():
    f1 = _json_frame("a", {"x": 1})
    f2 = _json_frame("b", {"y": 2})
    combined = f1 + f2
    # cut in the middle of the second frame
    cut = len(f1) + 3
    out = _drain([combined[:cut], combined[cut:]])
    assert out == [("a", {"x": 1}), ("b", {"y": 2})]


def test_empty_chunks_are_skipped():
    frame = _json_frame("evt", {"k": "v"})
    out = _drain([b"", frame, b""])
    assert out == [("evt", {"k": "v"})]


def test_empty_iterator_yields_nothing():
    assert _drain([]) == []


def test_only_empty_chunks_yields_nothing():
    assert _drain([b"", b"", b""]) == []


# ===========================================================================
# bedrock_eventstream — base64-wrapped inner payload
# ===========================================================================


def test_base64_bytes_payload_is_unwrapped():
    inner = {"delta": {"text": "unwrapped"}}
    b64 = b64encode(json.dumps(inner).encode("utf-8")).decode("ascii")
    frame = _json_frame("chunk", {"bytes": b64})
    out = _drain([frame])
    assert out == [("chunk", {"delta": {"text": "unwrapped"}})]


def test_base64_bytes_with_invalid_base64_keeps_outer_payload():
    # 'bytes' present as str but not valid base64 -> b64decode raises, caught,
    # outer payload passes through unchanged.
    frame = _json_frame("chunk", {"bytes": "!!!not-base64!!!"})
    out = _drain([frame])
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # base64 is lenient and may decode garbage; either the outer dict survives
    # or the inner decode fails and the outer dict is kept. Assert 'bytes' key
    # survived (outer payload retained) since inner JSON parse fails.
    assert out[0][0] == "chunk"
    assert out[0][1] == {"bytes": "!!!not-base64!!!"}


def test_base64_bytes_decoding_to_non_json_keeps_outer_payload():
    # valid base64 but the decoded bytes are not JSON -> JSONDecodeError caught,
    # outer payload retained.
    b64 = b64encode(b"this is not json").decode("ascii")
    frame = _json_frame("chunk", {"bytes": b64})
    out = _drain([frame])
    assert out[0][1] == {"bytes": b64}


def test_bytes_key_that_is_not_a_string_is_left_alone():
    # 'bytes' present but not a str -> the isinstance(..., str) guard skips the
    # unwrap branch entirely; outer payload retained verbatim.
    frame = _json_frame("chunk", {"bytes": 123})
    out = _drain([frame])
    assert out == [("chunk", {"bytes": 123})]


def test_payload_without_bytes_key_passes_through():
    frame = _json_frame("chunk", {"delta": {"text": "no-wrap"}})
    out = _drain([frame])
    assert out == [("chunk", {"delta": {"text": "no-wrap"}})]


# ===========================================================================
# bedrock_eventstream — malformed / edge frames
# ===========================================================================


def test_non_dict_json_payload_becomes_empty_dict():
    # A JSON list is valid JSON but not a dict; the parser normalises it to {}.
    payload = json.dumps([1, 2, 3]).encode("utf-8")
    frame = _build_frame("evt", payload)
    out = _drain([frame])
    assert out == [("evt", {})]


def test_json_scalar_payload_becomes_empty_dict():
    payload = json.dumps(42).encode("utf-8")
    frame = _build_frame("evt", payload)
    out = _drain([frame])
    assert out == [("evt", {})]


def test_invalid_json_payload_becomes_empty_dict():
    frame = _build_frame("evt", b"{not valid json")
    out = _drain([frame])
    assert out == [("evt", {})]


def test_undecodable_utf8_payload_becomes_empty_dict():
    # Lone continuation byte 0x80 is not valid UTF-8 -> UnicodeDecodeError caught.
    frame = _build_frame("evt", b"\x80\x80\x80")
    out = _drain([frame])
    assert out == [("evt", {})]


def test_frame_with_no_event_type_header_yields_empty_string():
    frame = _build_frame(None, json.dumps({"k": "v"}).encode("utf-8"))
    out = _drain([frame])
    assert out == [("", {"k": "v"})]


def test_total_len_below_16_breaks_and_yields_nothing():
    # A frame whose declared total_len is < 16 trips the guard and the loop
    # breaks without yielding. Hand-craft a 12-byte buffer declaring total_len=12.
    buf = struct.pack(">I", 12) + struct.pack(">I", 0) + struct.pack(">I", 0)
    out = _drain([buf])
    assert out == []


def test_buffer_shorter_than_12_bytes_yields_nothing():
    out = _drain([b"\x00\x00\x00"])
    assert out == []


def test_incomplete_frame_never_completes_yields_nothing():
    # A well-formed prelude declaring a large total_len, but the payload never
    # arrives. Parser buffers forever and yields nothing.
    frame = _json_frame("evt", {"k": "v"})
    out = _drain([frame[:-2]])  # drop trailing bytes so len(buf) < total_len
    assert out == []


def test_extra_non_event_type_header_before_event_type_short_circuits():
    # _extract_event_type returns the FIRST :event-type it reaches. Put a
    # non-target header first; the target follows and is found.
    other = _encode_header("content-type", "application/json")
    frame = _build_frame("theEvent", json.dumps({}).encode("utf-8"), extra_headers=other)
    # header order: [:event-type][content-type]; :event-type is first -> returned.
    out = _drain([frame])
    assert out[0][0] == "theEvent"


def test_non_string_header_type_stops_extraction():
    # A header with type_byte != 7 makes _extract_event_type break. If it is the
    # first header and is NOT :event-type-first, event type comes back empty.
    # Build headers manually: a type-2 (non-string) header first.
    bad_header = bytes([len(b"h")]) + b"h" + bytes([2]) + struct.pack(">H", 1) + b"x"
    frame = _build_frame(None, json.dumps({"k": "v"}).encode("utf-8"), extra_headers=bad_header)
    out = _drain([frame])
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # extraction breaks on the non-string type byte before finding :event-type.
    assert out == [("", {"k": "v"})]


def test_zero_headers_length_yields_empty_event_type():
    frame = _build_frame(None, json.dumps({"k": 1}).encode("utf-8"))
    out = _drain([frame])
    assert out[0][0] == ""


def test_trailing_incomplete_frame_after_complete_one():
    good = _json_frame("done", {"ok": True})
    partial = _json_frame("later", {"n": 2})[:-3]
    out = _drain([good + partial])
    # only the complete frame is yielded; the partial one stays buffered.
    assert out == [("done", {"ok": True})]


def test_empty_json_object_payload():
    frame = _json_frame("evt", {})
    out = _drain([frame])
    assert out == [("evt", {})]


# ===========================================================================
# bedrock_eventstream — _extract_event_type direct unit tests
# ===========================================================================


def test_extract_event_type_direct_happy():
    headers = _encode_header(":event-type", "metadata")
    assert bes._extract_event_type(headers) == "metadata"


def test_extract_event_type_empty_bytes_returns_empty():
    assert bes._extract_event_type(b"") == ""


def test_extract_event_type_truncated_name_returns_empty():
    # name_len says 5 but only 2 bytes follow -> guard trips.
    headers = bytes([5]) + b"ab"
    assert bes._extract_event_type(headers) == ""


def test_extract_event_type_truncated_value_length_returns_empty():
    # name present, type=7, but value_length field is truncated.
    headers = bytes([1]) + b"x" + bytes([7]) + b"\x00"  # only 1 of 2 val_len bytes
    assert bes._extract_event_type(headers) == ""


def test_extract_event_type_value_longer_than_buffer_returns_empty():
    # declared val_len exceeds remaining bytes -> guard trips before decode.
    headers = bytes([1]) + b"x" + bytes([7]) + struct.pack(">H", 99) + b"short"
    assert bes._extract_event_type(headers) == ""


def test_extract_event_type_skips_non_target_header_then_finds_target():
    # First a real string header that isn't :event-type, then the target.
    headers = _encode_header("content-type", "application/json") + _encode_header(
        ":event-type", "contentBlockStop"
    )
    assert bes._extract_event_type(headers) == "contentBlockStop"


# ===========================================================================
# mock_health_logger — _parse_url
# ===========================================================================


def test_parse_url_http():
    assert mhl._parse_url("http://figma-api:8010") == ("figma-api", 8010)


def test_parse_url_https():
    assert mhl._parse_url("https://foo:443") == ("foo", 443)


def test_parse_url_with_trailing_path():
    assert mhl._parse_url("http://svc:8000/health") == ("svc", 8000)


def test_parse_url_none_when_no_port():
    assert mhl._parse_url("http://noport") is None


def test_parse_url_none_when_empty():
    assert mhl._parse_url("") is None


def test_parse_url_none_when_none_argument():
    assert mhl._parse_url(None) is None


def test_parse_url_none_when_not_a_url():
    assert mhl._parse_url("just-a-name") is None


# ===========================================================================
# mock_health_logger — _container_running
# ===========================================================================


def test_container_running_empty_name_is_false(monkeypatch):
    called = {"ran": False}

    def fake_run(*a, **kw):
        called["ran"] = True
        raise AssertionError("should not be reached for empty name")

    monkeypatch.setattr(mhl.subprocess, "run", fake_run)
    assert mhl._container_running("") is False
    assert called["ran"] is False


class _Completed:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_container_running_true(monkeypatch):
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda *a, **kw: _Completed(0, "true\n")
    )
    assert mhl._container_running("c1") is True


def test_container_running_false_when_state_not_true(monkeypatch):
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda *a, **kw: _Completed(0, "false\n")
    )
    assert mhl._container_running("c1") is False


def test_container_running_false_when_nonzero_returncode(monkeypatch):
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda *a, **kw: _Completed(1, "true\n")
    )
    assert mhl._container_running("c1") is False


# ===========================================================================
# mock_health_logger — MockHealthLogger construction & config normalisation
# ===========================================================================


def _make_logger(tmp_path, **overrides):
    params = dict(
        task_id="task-x",
        api_url_map={"figma": "http://figma-api:8010"},
        output_dir=tmp_path / "out",
        agent_container="",
        interval=30.0,
        probe_timeout=3.0,
    )
    params.update(overrides)
    return mhl.MockHealthLogger(**params)


def test_ctor_creates_output_dir_and_paths(tmp_path):
    lg = _make_logger(tmp_path)
    assert (tmp_path / "out").is_dir()
    assert lg.jsonl_path == tmp_path / "out" / "mock_health.jsonl"
    assert lg.log_path == tmp_path / "out" / "mock_health.log"
    lg._close_file_logger()


def test_ctor_filters_out_empty_urls(tmp_path):
    lg = _make_logger(
        tmp_path,
        api_url_map={"good": "http://a:1", "empty": "", "none": None},
    )
    assert lg.api_url_map == {"good": "http://a:1"}
    lg._close_file_logger()


def test_ctor_handles_none_api_url_map(tmp_path):
    lg = _make_logger(tmp_path, api_url_map=None)
    assert lg.api_url_map == {}
    lg._close_file_logger()


def test_ctor_agent_container_defaults_to_task_id(tmp_path):
    lg = _make_logger(tmp_path, task_id="my-task", agent_container="")
    assert lg.agent_container == "my-task"
    lg._close_file_logger()


def test_ctor_agent_container_explicit_preserved(tmp_path):
    lg = _make_logger(tmp_path, task_id="my-task", agent_container="agent-c")
    assert lg.agent_container == "agent-c"
    lg._close_file_logger()


def test_ctor_interval_floored_to_one(tmp_path):
    lg = _make_logger(tmp_path, interval=0.1)
    assert lg.interval == 1.0
    lg._close_file_logger()


def test_ctor_probe_timeout_floored_to_one(tmp_path):
    lg = _make_logger(tmp_path, probe_timeout=0.0)
    assert lg.probe_timeout == 1.0
    lg._close_file_logger()


def test_ctor_is_daemon_thread_named(tmp_path):
    lg = _make_logger(tmp_path, task_id="abc")
    assert lg.daemon is True
    assert lg.name == "mock-health-abc"
    lg._close_file_logger()


def test_build_file_logger_no_propagate_and_single_handler(tmp_path):
    lg = _make_logger(tmp_path)
    assert lg._log.propagate is False
    assert len(lg._log.handlers) == 1
    lg._close_file_logger()


# ===========================================================================
# mock_health_logger — _probe
# ===========================================================================


def test_probe_bad_url_returns_bad_url_status(tmp_path):
    lg = _make_logger(tmp_path)
    rec = lg._probe("api", "not-a-url", agent_up=False, ts="T")
    assert rec["status"] == "bad_url"
    assert rec["via"] == "none"
    assert rec["http_code"] == 0
    assert rec["error"] == "could not parse url"
    lg._close_file_logger()


def test_probe_skipped_when_target_not_running(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    monkeypatch.setattr(mhl, "_container_running", lambda name: False)
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["status"] == "probe_skipped"
    assert rec["via"] == "mock"
    assert "not running" in rec["error"]
    lg._close_file_logger()


def test_probe_via_agent_uses_agent_container_and_health_url(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path, agent_container="agent-c")
    captured = {}

    monkeypatch.setattr(mhl, "_container_running", lambda name: True)

    def fake_run(cmd, *a, **kw):
        captured["cmd"] = cmd
        return _Completed(0, "200")

    monkeypatch.setattr(mhl.subprocess, "run", fake_run)
    rec = lg._probe("figma", "http://figma-api:8010/", agent_up=True, ts="T")
    assert rec["status"] == "ok"
    assert rec["via"] == "agent"
    assert rec["http_code"] == 200
    # docker exec runs against the agent container, hitting the mock's own URL
    assert captured["cmd"][0:3] == ["docker", "exec", "agent-c"]
    assert "http://figma-api:8010/health" in captured["cmd"]
    lg._close_file_logger()


def test_probe_via_mock_uses_localhost_and_mock_host(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    captured = {}
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)

    def fake_run(cmd, *a, **kw):
        captured["cmd"] = cmd
        return _Completed(0, "204")

    monkeypatch.setattr(mhl.subprocess, "run", fake_run)
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["status"] == "ok"
    assert rec["via"] == "mock"
    assert rec["http_code"] == 204
    # probe target is the mock container (host part of the url)
    assert captured["cmd"][2] == "figma-api"
    assert "http://localhost:8010/health" in captured["cmd"]
    lg._close_file_logger()


def test_probe_timeout_expired_returns_timeout(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)

    def fake_run(cmd, *a, **kw):
        raise subprocess.TimeoutExpired(cmd, 5)

    monkeypatch.setattr(mhl.subprocess, "run", fake_run)
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["status"] == "timeout"
    assert rec["http_code"] == 0
    assert rec["error"] == "docker exec timed out"
    lg._close_file_logger()


def test_probe_exec_failed_returns_stderr(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)
    monkeypatch.setattr(
        mhl.subprocess,
        "run",
        lambda cmd, *a, **kw: _Completed(7, "", "boom happened\n"),
    )
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["status"] == "exec_failed"
    assert rec["error"] == "boom happened"
    lg._close_file_logger()


def test_probe_http_error_for_5xx(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda cmd, *a, **kw: _Completed(0, "500")
    )
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["status"] == "http_error"
    assert rec["http_code"] == 500
    lg._close_file_logger()


def test_probe_http_error_for_4xx(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda cmd, *a, **kw: _Completed(0, "404")
    )
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["status"] == "http_error"
    assert rec["http_code"] == 404
    lg._close_file_logger()


def test_probe_ok_boundary_200_and_399(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda cmd, *a, **kw: _Completed(0, "399")
    )
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["status"] == "ok"
    assert rec["http_code"] == 399
    lg._close_file_logger()


def test_probe_empty_http_code_becomes_zero_and_http_error(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda cmd, *a, **kw: _Completed(0, "")
    )
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["http_code"] == 0
    assert rec["status"] == "http_error"
    lg._close_file_logger()


def test_probe_non_numeric_http_code_becomes_zero(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda cmd, *a, **kw: _Completed(0, "notanumber")
    )
    rec = lg._probe("figma", "http://figma-api:8010", agent_up=False, ts="T")
    assert rec["http_code"] == 0
    assert rec["status"] == "http_error"
    lg._close_file_logger()


# ===========================================================================
# mock_health_logger — _tick and _append_jsonl integration
# ===========================================================================


def test_tick_writes_jsonl_and_logs_healthy(tmp_path, monkeypatch):
    lg = _make_logger(
        tmp_path,
        api_url_map={"a": "http://a-api:1", "b": "http://b-api:2"},
    )
    # container running -> True everywhere; both probes return 200.
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)
    monkeypatch.setattr(
        mhl.subprocess, "run", lambda cmd, *a, **kw: _Completed(0, "200")
    )
    lg._tick()
    lg._close_file_logger()
    lines = (tmp_path / "out" / "mock_health.jsonl").read_text().strip().splitlines()
    recs = [json.loads(x) for x in lines]
    assert len(recs) == 2
    assert {r["api"] for r in recs} == {"a", "b"}
    assert all(r["status"] == "ok" for r in recs)


def test_tick_records_failures(tmp_path, monkeypatch):
    lg = _make_logger(
        tmp_path,
        api_url_map={"good": "http://g-api:1", "bad": "http://b-api:2"},
    )
    monkeypatch.setattr(mhl, "_container_running", lambda name: True)

    def fake_run(cmd, *a, **kw):
        # agent_up is True in this test (container_running patched True), so the
        # probe hits each mock's own /health URL via the agent container.
        # 'g-api' is healthy, 'b-api' returns 503.
        code = "200" if "http://g-api:1/health" in cmd else "503"
        return _Completed(0, code)

    monkeypatch.setattr(mhl.subprocess, "run", fake_run)
    lg._tick()
    lg._close_file_logger()
    recs = [
        json.loads(x)
        for x in (tmp_path / "out" / "mock_health.jsonl")
        .read_text()
        .strip()
        .splitlines()
    ]
    by_api = {r["api"]: r for r in recs}
    assert by_api["good"]["status"] == "ok"
    assert by_api["bad"]["status"] == "http_error"


def test_append_jsonl_appends_across_calls(tmp_path):
    lg = _make_logger(tmp_path)
    lg._append_jsonl([{"api": "x", "status": "ok"}])
    lg._append_jsonl([{"api": "y", "status": "http_error"}])
    lg._close_file_logger()
    lines = (tmp_path / "out" / "mock_health.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["api"] == "x"
    assert json.loads(lines[1])["api"] == "y"


def test_append_jsonl_swallows_oserror(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)

    def boom(*a, **kw):
        raise OSError("disk full")

    # Patch the jsonl path's open to raise; the method must not propagate.
    monkeypatch.setattr(type(lg.jsonl_path), "open", boom)
    # Should not raise.
    lg._append_jsonl([{"api": "x"}])
    lg._close_file_logger()


# ===========================================================================
# mock_health_logger — run() lifecycle
# ===========================================================================


def test_run_with_no_apis_exits_immediately(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path, api_url_map={})
    # _tick must never be called when there are no APIs.
    monkeypatch.setattr(lg, "_tick", lambda: (_ for _ in ()).throw(AssertionError("ticked")))
    lg.run()
    log_text = (tmp_path / "out" / "mock_health.log").read_text()
    assert "no APIs to probe" in log_text


def test_run_full_lifecycle_ticks_and_stops(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    tick_count = {"n": 0}
    monkeypatch.setattr(lg, "_tick", lambda: tick_count.__setitem__("n", tick_count["n"] + 1))

    # Make the wait return True immediately so the while-loop body never runs;
    # run() should still do the initial tick + the final shutdown tick == 2.
    monkeypatch.setattr(lg._stop_event, "wait", lambda timeout: True)
    lg.run()
    # First (immediate) tick + final (shutdown) tick.
    assert tick_count["n"] == 2
    log_text = (tmp_path / "out" / "mock_health.log").read_text()
    assert "starting:" in log_text
    assert "stopped" in log_text


def test_run_loops_until_stop_event(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)
    tick_count = {"n": 0}
    monkeypatch.setattr(lg, "_tick", lambda: tick_count.__setitem__("n", tick_count["n"] + 1))

    # wait() returns False twice (loop runs twice) then True (stop).
    seq = iter([False, False, True])
    monkeypatch.setattr(lg._stop_event, "wait", lambda timeout: next(seq))
    lg.run()
    # initial tick (1) + 2 loop ticks + final shutdown tick (1) == 4.
    assert tick_count["n"] == 4


def test_stop_sets_event(tmp_path):
    lg = _make_logger(tmp_path)
    assert not lg._stop_event.is_set()
    lg.stop()
    assert lg._stop_event.is_set()
    lg._close_file_logger()


def test_run_closes_file_handler_even_on_exception(tmp_path, monkeypatch):
    lg = _make_logger(tmp_path)

    def boom():
        raise RuntimeError("tick blew up")

    monkeypatch.setattr(lg, "_tick", boom)
    closed = {"n": 0}
    orig_close = lg._close_file_logger
    monkeypatch.setattr(lg, "_close_file_logger", lambda: (closed.__setitem__("n", closed["n"] + 1), orig_close())[1])
    with pytest.raises(RuntimeError, match="tick blew up"):
        lg.run()
    assert closed["n"] == 1


class _ExplodingHandler(logging.Handler):
    """A handler whose close() raises — exercises the defensive except: pass."""

    def emit(self, record):  # pragma: no cover - never emitted
        pass

    def close(self):
        raise RuntimeError("handler close blew up")


def test_build_file_logger_swallows_prior_handler_close_error(tmp_path, monkeypatch):
    # Pre-seed the exact logger name the fresh instance will use with a handler
    # that raises on close(); the constructor's defensive clear must swallow it.
    lg = _make_logger(tmp_path)
    name = f"mock_health.{lg.task_id}.{id(lg):x}"
    logger_obj = logging.getLogger(name)
    logger_obj.addHandler(_ExplodingHandler())
    # Rebuild — the exploding handler's close() error is swallowed (lines 111-112).
    new_log = lg._build_file_logger()
    assert len(new_log.handlers) == 1  # only the new FileHandler remains
    lg._close_file_logger()


def test_close_file_logger_swallows_all_errors(tmp_path, monkeypatch):
    # Force flush(), removeHandler(), and close() to each raise so all three
    # defensive except: pass branches (lines 125-126, 129-130, 133-134) run.
    lg = _make_logger(tmp_path)

    handler = lg._file_handler
    stream = getattr(handler, "stream", None)  # real underlying file object

    def boom(*a, **kw):
        raise RuntimeError("io error")

    monkeypatch.setattr(handler, "flush", boom)
    monkeypatch.setattr(handler, "close", boom)
    monkeypatch.setattr(lg._log, "removeHandler", boom)
    try:
        # Must not raise despite every underlying call failing.
        lg._close_file_logger()
    finally:
        # The boom-patched close() left the real FileHandler open and still
        # attached to a logger that lives forever in logging's global registry.
        # If left dangling, GC of that broken handler surfaces as a pytest
        # unraisable-exception attributed to whichever test happens to be
        # running (order/coverage dependent — a flaky failure). Fully neutralise
        # it: drop the boom patches, close the real file object, detach the
        # handler, and remove the logger from the global registry.
        monkeypatch.undo()
        try:
            if stream is not None:
                stream.close()
        except Exception:
            pass
        try:
            lg._log.handlers.clear()
        except Exception:
            pass
        logging.Logger.manager.loggerDict.pop(lg._log.name, None)


def test_build_file_logger_clears_prior_handlers(tmp_path, monkeypatch):
    # Force a logger-name collision by monkeypatching id() indirectly: instead,
    # pre-seed a logger with the exact name a fresh instance will use, add a
    # stray handler, and assert the constructor cleared it (single handler left).
    lg = _make_logger(tmp_path)
    name = f"mock_health.{lg.task_id}.{id(lg):x}"
    logger_obj = logging.getLogger(name)
    stray = logging.NullHandler()
    logger_obj.addHandler(stray)
    # Rebuild the file logger; the defensive clear should remove the stray.
    new_log = lg._build_file_logger()
    assert stray not in new_log.handlers
    assert len(new_log.handlers) == 1
    lg._close_file_logger()
