"""Behavioral tests for the two LiteLLM usage-callback modules.

`litellm_usage_callback.py` is the SOLE writer of the 11-key `usage.jsonl`
schema and `litellm_usage_oauth_callback.py` is its OAuth-path sibling that
writes the separate `usage_oauth.jsonl` (9-key) audit trail. These callbacks run
inside the LiteLLM sidecar container; nothing else in the harness may reproduce
their row shape, so these tests pin:

  - the EXACT row key set + ordering-independent contract of each schema,
  - `_is_preflight_ping` classification (the only thing separating the
    startup probe cost from real agent cost),
  - the universal non-cached input recovery rule
    `non_cached = prompt - cache_read - cache_write` (clamped to 0),
  - cost preference (`litellm.completion_cost` over `kwargs['response_cost']`,
    falling back only when completion_cost <= 0),
  - append (never truncate) semantics against a tmp_path file,
  - the small numeric/coercion helpers and their edge cases.

Everything is offline: `litellm` is stubbed via monkeypatch.setitem(sys.modules,
...) and the log path is redirected into tmp_path. No docker / network / AWS.
"""
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import litellm_usage_callback as uc  # noqa: E402
from src.utils import litellm_usage_oauth_callback as oc  # noqa: E402


# ============================================================================
# Fixtures / helpers
# ============================================================================


@pytest.fixture(autouse=True)
def _reset_warn_state():
    """The primary module carries a process-global warn-dedup set; clear it so
    a warn emitted by one test can't suppress the assertion in another."""
    uc._WARN_SEEN.clear()
    yield
    uc._WARN_SEEN.clear()


@pytest.fixture
def usage_path(tmp_path, monkeypatch):
    """Redirect the primary callback's log path into tmp_path (nested dir to
    exercise the os.makedirs branch)."""
    p = tmp_path / "var" / "litellm_usage" / "usage.jsonl"
    monkeypatch.setattr(uc, "_PATH", str(p))
    return p


@pytest.fixture
def oauth_path(tmp_path, monkeypatch):
    p = tmp_path / "var" / "litellm_usage" / "usage_oauth.jsonl"
    monkeypatch.setattr(oc, "_PATH", str(p))
    return p


@pytest.fixture
def stub_completion_cost(monkeypatch):
    """Install a fake `litellm` module whose completion_cost returns a fixed
    value. Returns a mutable holder so a test can change the value / assert
    call args."""
    holder = {"return_value": 0.123, "calls": []}

    def _completion_cost(completion_response=None, model=None):
        holder["calls"].append({"completion_response": completion_response, "model": model})
        rv = holder["return_value"]
        if isinstance(rv, Exception):
            raise rv
        return rv

    fake = SimpleNamespace(completion_cost=_completion_cost)
    monkeypatch.setitem(sys.modules, "litellm", fake)
    return holder


def _chat_usage(prompt_tokens=1000, completion_tokens=50, cache_read=0, cache_write=0):
    """A Bedrock/Anthropic-style usage dict where prompt_tokens already folds
    in cache_read + cache_write (the documented provider shape)."""
    d = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }
    if cache_read:
        d["cache_read_input_tokens"] = cache_read
    if cache_write:
        d["cache_creation_input_tokens"] = cache_write
    return d


def _resp(usage=None, duration=None):
    """Response object exposing `.usage` (and optionally `.duration`)."""
    ns = SimpleNamespace(usage=usage)
    if duration is not None:
        ns.duration = duration
    return ns


def _read_rows(path: Path):
    text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


T0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
T1 = T0 + timedelta(seconds=2, milliseconds=500)  # 2.5s duration


# ============================================================================
# _usage_to_dict (shared logic, tested on both modules)
# ============================================================================


@pytest.mark.parametrize("mod", [uc, oc])
def test_usage_to_dict_none_returns_empty(mod):
    assert mod._usage_to_dict(None) == {}


@pytest.mark.parametrize("mod", [uc, oc])
def test_usage_to_dict_passthrough_dict(mod):
    d = {"prompt_tokens": 5}
    assert mod._usage_to_dict(d) is d


@pytest.mark.parametrize("mod", [uc, oc])
def test_usage_to_dict_uses_model_dump(mod):
    obj = SimpleNamespace(model_dump=lambda: {"prompt_tokens": 7})
    assert mod._usage_to_dict(obj) == {"prompt_tokens": 7}


@pytest.mark.parametrize("mod", [uc, oc])
def test_usage_to_dict_uses_dict_method_when_model_dump_missing(mod):
    # object with .dict() but not .model_dump()
    class Only:
        def dict(self):
            return {"completion_tokens": 3}

    assert mod._usage_to_dict(Only()) == {"completion_tokens": 3}


@pytest.mark.parametrize("mod", [uc, oc])
def test_usage_to_dict_model_dump_raises_falls_through_to_dunder_dict(mod):
    class Boom:
        # model_dump raises -> caught -> falls to __dict__ fallback
        def model_dump(self):
            raise RuntimeError("nope")

    obj = Boom()
    obj.prompt_tokens = 11  # populates __dict__
    assert mod._usage_to_dict(obj) == {"prompt_tokens": 11}


@pytest.mark.parametrize("mod", [uc, oc])
def test_usage_to_dict_model_dump_returns_non_dict_ignored(mod):
    # model_dump returns a list (not dict) -> ignored, falls to __dict__
    obj = SimpleNamespace(model_dump=lambda: [1, 2, 3])
    # SimpleNamespace __dict__ includes the model_dump entry; that's the fallback.
    out = mod._usage_to_dict(obj)
    assert isinstance(out, dict)
    assert "model_dump" in out


# ============================================================================
# _int / _float coercion helpers
# ============================================================================


@pytest.mark.parametrize("mod", [uc, oc])
@pytest.mark.parametrize("value,expected", [
    (5, 5),
    ("7", 7),
    (3.9, 3),          # float truncates toward zero
    (None, 0),         # None -> default
    ("abc", 0),        # unparseable -> default
    ([], 0),           # wrong type -> default
])
def test_int_helper(mod, value, expected):
    assert mod._int(value) == expected


def test_int_helper_custom_default():
    assert uc._int(None, default=99) == 99
    assert uc._int("bad", default=-1) == -1


def test_float_helper():
    assert uc._float(1.5) == 1.5
    assert uc._float("2.25") == 2.25
    assert uc._float(None) == 0.0
    assert uc._float("bad") == 0.0
    assert uc._float(None, default=4.0) == 4.0


# ============================================================================
# _is_preflight_ping
# ============================================================================


def test_preflight_ping_str_content():
    kwargs = {
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "ping"}],
    }
    assert uc._is_preflight_ping(kwargs) is True


def test_preflight_ping_case_and_whitespace_insensitive():
    kwargs = {
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "  PiNg  "}],
    }
    assert uc._is_preflight_ping(kwargs) is True


def test_preflight_ping_max_tokens_string_one():
    kwargs = {
        "max_tokens": "1",
        "messages": [{"role": "user", "content": "ping"}],
    }
    assert uc._is_preflight_ping(kwargs) is True


def test_preflight_ping_max_tokens_from_optional_params():
    kwargs = {
        "optional_params": {"max_tokens": 1},
        "messages": [{"role": "user", "content": "ping"}],
    }
    assert uc._is_preflight_ping(kwargs) is True


def test_preflight_ping_max_tokens_from_optional_params_camelcase():
    kwargs = {
        "optional_params": {"maxTokens": 1},
        "messages": [{"role": "user", "content": "ping"}],
    }
    assert uc._is_preflight_ping(kwargs) is True


def test_preflight_ping_content_list_shape():
    kwargs = {
        "max_tokens": 1,
        "messages": [{"role": "user", "content": [{"text": "ping"}]}],
    }
    assert uc._is_preflight_ping(kwargs) is True


def test_preflight_ping_content_list_uses_content_key():
    # inner dict has 'content' rather than 'text'
    kwargs = {
        "max_tokens": 1,
        "messages": [{"role": "user", "content": [{"content": "ping"}]}],
    }
    assert uc._is_preflight_ping(kwargs) is True


def test_not_preflight_wrong_max_tokens():
    kwargs = {
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": "ping"}],
    }
    assert uc._is_preflight_ping(kwargs) is False


def test_not_preflight_missing_max_tokens_entirely():
    # no max_tokens anywhere -> max_tok is None -> not in (1,"1")
    kwargs = {"messages": [{"role": "user", "content": "ping"}]}
    assert uc._is_preflight_ping(kwargs) is False


def test_not_preflight_multiple_messages():
    kwargs = {
        "max_tokens": 1,
        "messages": [
            {"role": "system", "content": "s"},
            {"role": "user", "content": "ping"},
        ],
    }
    assert uc._is_preflight_ping(kwargs) is False


def test_not_preflight_wrong_role():
    kwargs = {
        "max_tokens": 1,
        "messages": [{"role": "assistant", "content": "ping"}],
    }
    assert uc._is_preflight_ping(kwargs) is False


def test_not_preflight_wrong_content_text():
    kwargs = {
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "hello world"}],
    }
    assert uc._is_preflight_ping(kwargs) is False


def test_not_preflight_content_list_wrong_length():
    kwargs = {
        "max_tokens": 1,
        "messages": [{"role": "user", "content": [{"text": "ping"}, {"text": "extra"}]}],
    }
    assert uc._is_preflight_ping(kwargs) is False


def test_not_preflight_empty_messages():
    kwargs = {"max_tokens": 1, "messages": []}
    assert uc._is_preflight_ping(kwargs) is False


def test_not_preflight_message_not_dict():
    kwargs = {"max_tokens": 1, "messages": ["ping"]}
    assert uc._is_preflight_ping(kwargs) is False


def test_preflight_exception_path_returns_false():
    # messages is a non-iterable-non-list truthy value; len() will raise inside
    # -> the outer try/except returns False.
    class Weird:
        def __len__(self):
            raise RuntimeError("boom")

    kwargs = {"max_tokens": 1, "messages": Weird()}
    assert uc._is_preflight_ping(kwargs) is False


# ============================================================================
# _warn_once_per_day (rate limiting)
# ============================================================================


def test_warn_once_per_day_dedups(monkeypatch):
    writes = []
    monkeypatch.setattr(uc.sys.stderr, "write", lambda s: writes.append(s))
    uc._warn_once_per_day("model-x", "hi %d", 1)
    uc._warn_once_per_day("model-x", "hi %d", 2)  # same model+day -> suppressed
    assert len(writes) == 1
    assert "model-x" in writes[0]


def test_warn_once_per_day_distinct_models(monkeypatch):
    writes = []
    monkeypatch.setattr(uc.sys.stderr, "write", lambda s: writes.append(s))
    uc._warn_once_per_day("model-a", "x")
    uc._warn_once_per_day("model-b", "x")
    assert len(writes) == 2


# ============================================================================
# _write_row (primary callback) — the 11-key schema + math
# ============================================================================

# The canonical 11 keys of usage.jsonl. Pinning this exact set is the whole
# point of this file: nothing else may reproduce or diverge from it.
EXPECTED_KEYS = {
    "ts", "model", "kind",
    "input_tokens", "output_tokens", "total_tokens",
    "cache_read_tokens", "cache_write_tokens",
    "audio_seconds", "cost_usd", "duration_s",
}


def test_write_row_exact_key_schema(usage_path, stub_completion_cost):
    kwargs = {"model": "claude-opus-4.7", "messages": [], "response_cost": 0.0}
    uc._write_row(kwargs, _resp(_chat_usage()), T0, T1)
    rows = _read_rows(usage_path)
    assert len(rows) == 1
    assert set(rows[0].keys()) == EXPECTED_KEYS


def test_write_row_basic_values(usage_path, stub_completion_cost):
    stub_completion_cost["return_value"] = 0.5
    kwargs = {"model": "claude-opus-4.7", "messages": []}
    uc._write_row(kwargs, _resp(_chat_usage(prompt_tokens=1000, completion_tokens=50)), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["model"] == "claude-opus-4.7"
    assert row["kind"] == "agent"
    assert row["input_tokens"] == 1000          # no cache -> non-cached == prompt
    assert row["output_tokens"] == 50
    assert row["total_tokens"] == 1050
    assert row["cache_read_tokens"] == 0
    assert row["cache_write_tokens"] == 0
    assert row["audio_seconds"] == 0.0
    assert row["cost_usd"] == 0.5
    assert row["duration_s"] == 2.5


def test_write_row_non_cached_input_subtracts_read_and_write(usage_path, stub_completion_cost):
    # prompt folds in BOTH cache_read and cache_write -> non-cached = 1500-300-50
    usage = _chat_usage(prompt_tokens=1500, completion_tokens=120, cache_read=300, cache_write=50)
    uc._write_row({"model": "m", "messages": []}, _resp(usage), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["input_tokens"] == 1500 - 300 - 50
    assert row["cache_read_tokens"] == 300
    assert row["cache_write_tokens"] == 50
    # total = non_cached + output + cache_read + cache_write
    assert row["total_tokens"] == (1500 - 300 - 50) + 120 + 300 + 50


def test_write_row_cache_read_from_prompt_tokens_details(usage_path, stub_completion_cost):
    # OpenAI shape: cached tokens live under prompt_tokens_details.cached_tokens
    usage = {
        "prompt_tokens": 800,
        "completion_tokens": 40,
        "prompt_tokens_details": {"cached_tokens": 200},
    }
    uc._write_row({"model": "gpt-5.5", "messages": []}, _resp(usage), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["cache_read_tokens"] == 200
    assert row["input_tokens"] == 800 - 200  # cache_write is 0 here


def test_write_row_negative_non_cached_clamped_and_warned(usage_path, stub_completion_cost, monkeypatch):
    writes = []
    monkeypatch.setattr(uc.sys.stderr, "write", lambda s: writes.append(s))
    # prompt < cache_read + cache_write -> clamp to 0 + warn
    usage = _chat_usage(prompt_tokens=100, completion_tokens=10, cache_read=200, cache_write=50)
    uc._write_row({"model": "m", "messages": []}, _resp(usage), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["input_tokens"] == 0
    assert row["total_tokens"] == 0 + 10 + 200 + 50
    # a warn was emitted
    assert any("clamping non-cached input to 0" in w for w in writes)


def test_write_row_preflight_kind(usage_path, stub_completion_cost):
    kwargs = {
        "model": "claude-sonnet",
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "ping"}],
    }
    uc._write_row(kwargs, _resp(_chat_usage(prompt_tokens=5, completion_tokens=1)), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["kind"] == "preflight"


def test_write_row_model_missing_becomes_empty_string(usage_path, stub_completion_cost):
    uc._write_row({"messages": []}, _resp(_chat_usage()), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["model"] == ""


def test_write_row_transcription_token_shape(usage_path, stub_completion_cost):
    # gpt-4o-transcribe token-billed shape: input_tokens/output_tokens, no
    # prompt_tokens/completion_tokens.
    usage = {
        "type": "tokens",
        "input_tokens": 300,
        "output_tokens": 25,
        "total_tokens": 325,
    }
    uc._write_row({"model": "gpt-4o-transcribe", "messages": []}, _resp(usage), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["input_tokens"] == 300
    assert row["output_tokens"] == 25


def test_write_row_audio_seconds_from_usage_seconds(usage_path, stub_completion_cost):
    usage = {"type": "duration", "seconds": 12.3456}
    uc._write_row({"model": "whisper-1", "messages": []}, _resp(usage), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["audio_seconds"] == 12.346  # rounded to 3 places
    assert row["input_tokens"] == 0
    assert row["output_tokens"] == 0


def test_write_row_audio_seconds_falls_back_to_response_duration(usage_path, stub_completion_cost):
    # whisper-1 default json: no usage object, duration on the response object.
    resp = _resp(usage=None, duration=7.5)
    uc._write_row({"model": "whisper-1", "messages": []}, resp, T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["audio_seconds"] == 7.5


def test_write_row_cost_prefers_completion_cost(usage_path, stub_completion_cost):
    stub_completion_cost["return_value"] = 0.245
    uc._write_row({"model": "m", "messages": [], "response_cost": 0.0028},
                  _resp(_chat_usage()), T0, T1)
    row = _read_rows(usage_path)[0]
    # completion_cost (0.245) wins over the wrong proxy response_cost (0.0028)
    assert row["cost_usd"] == 0.245


def test_write_row_cost_falls_back_to_response_cost_when_completion_cost_zero(usage_path, stub_completion_cost):
    stub_completion_cost["return_value"] = 0.0  # e.g. whisper duration billing
    uc._write_row({"model": "whisper-1", "messages": [], "response_cost": 0.0006},
                  _resp({"type": "duration", "seconds": 3.0}), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["cost_usd"] == 0.0006


def test_write_row_cost_completion_cost_raises_uses_response_cost(usage_path, stub_completion_cost, monkeypatch):
    monkeypatch.setattr(uc.sys.stderr, "write", lambda s: None)
    stub_completion_cost["return_value"] = RuntimeError("pricing blew up")
    uc._write_row({"model": "m", "messages": [], "response_cost": 0.09},
                  _resp(_chat_usage()), T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["cost_usd"] == 0.09


def test_write_row_response_obj_dict_usage(usage_path, stub_completion_cost):
    # response_obj is a plain dict (no .usage attr) -> reads dict["usage"]
    resp = {"usage": _chat_usage(prompt_tokens=600, completion_tokens=30)}
    uc._write_row({"model": "m", "messages": []}, resp, T0, T1)
    row = _read_rows(usage_path)[0]
    assert row["input_tokens"] == 600
    assert row["output_tokens"] == 30


def test_write_row_appends_never_truncates(usage_path, stub_completion_cost):
    for i in range(3):
        uc._write_row({"model": f"m{i}", "messages": []},
                      _resp(_chat_usage(prompt_tokens=100 * (i + 1))), T0, T1)
    rows = _read_rows(usage_path)
    assert len(rows) == 3
    assert [r["model"] for r in rows] == ["m0", "m1", "m2"]
    assert [r["input_tokens"] for r in rows] == [100, 200, 300]


def test_write_row_creates_nested_dir(tmp_path, monkeypatch, stub_completion_cost):
    target = tmp_path / "deep" / "nested" / "dir" / "usage.jsonl"
    assert not target.parent.exists()
    monkeypatch.setattr(uc, "_PATH", str(target))
    uc._write_row({"model": "m", "messages": []}, _resp(_chat_usage()), T0, T1)
    assert target.exists()
    assert len(_read_rows(target)) == 1


def test_write_row_bad_start_end_time_duration_zero(usage_path, stub_completion_cost):
    # start/end not datetime -> subtraction raises -> duration stays 0.0
    uc._write_row({"model": "m", "messages": []}, _resp(_chat_usage()), "notatime", "alsobad")
    row = _read_rows(usage_path)[0]
    assert row["duration_s"] == 0.0


def test_write_row_ts_is_iso8601_utc(usage_path, stub_completion_cost):
    uc._write_row({"model": "m", "messages": []}, _resp(_chat_usage()), T0, T1)
    row = _read_rows(usage_path)[0]
    parsed = datetime.fromisoformat(row["ts"])
    assert parsed.tzinfo is not None  # timezone-aware


def test_write_row_swallows_all_errors(usage_path, monkeypatch):
    # No litellm module in sys.modules AND makedirs blows up -> the outer
    # try/except must swallow it and never raise.
    monkeypatch.setitem(sys.modules, "litellm", None)  # `import litellm` -> ImportError
    monkeypatch.setattr(uc.os, "makedirs", lambda *a, **k: (_ for _ in ()).throw(OSError("nope")))
    # Silence the error stderr write.
    monkeypatch.setattr(uc.sys.stderr, "write", lambda s: None)
    # Must not raise.
    uc._write_row({"model": "m", "messages": []}, _resp(_chat_usage()), T0, T1)


# ============================================================================
# UsageWriter.async_log_success_event (primary)
# ============================================================================


def test_async_log_success_event_writes_row(usage_path, stub_completion_cost):
    import asyncio
    writer = uc.UsageWriter()
    asyncio.run(writer.async_log_success_event(
        {"model": "m", "messages": []}, _resp(_chat_usage()), T0, T1
    ))
    assert len(_read_rows(usage_path)) == 1


def test_proxy_handler_instance_is_usage_writer():
    assert isinstance(uc.proxy_handler_instance, uc.UsageWriter)


# ============================================================================
# OAuth callback: _is_oauth_route
# ============================================================================


@pytest.mark.parametrize("model,expected", [
    ("anthropic/claude-opus-4-5", True),
    ("bedrock/claude-OPUS-4-6", True),  # case-insensitive
    ("claude-sonnet-4-5", False),
    ("gpt-5.5", False),
    ("", False),
    (None, False),
])
def test_is_oauth_route(model, expected):
    assert oc._is_oauth_route(model) is expected


# ============================================================================
# OAuth callback: _bedrock_equivalent_cost
# ============================================================================


def test_bedrock_equivalent_cost_all_terms():
    # 1e6 input @ 5e-6, 1e6 output @ 25e-6, 1e6 read @ 5e-7, 1e6 write @ 6.25e-6
    cost = oc._bedrock_equivalent_cost(1_000_000, 1_000_000, 1_000_000, 1_000_000)
    assert cost == pytest.approx(5.0 + 25.0 + 0.5 + 6.25)


def test_bedrock_equivalent_cost_zero():
    assert oc._bedrock_equivalent_cost(0, 0, 0, 0) == 0.0


def test_bedrock_equivalent_cost_input_only():
    assert oc._bedrock_equivalent_cost(2000, 0, 0, 0) == pytest.approx(2000 * 5e-6)


# ============================================================================
# OAuth callback: _write_row — 9-key schema, oauth gating, cost math
# ============================================================================

EXPECTED_OAUTH_KEYS = {
    "ts", "model", "route",
    "input_tokens", "output_tokens",
    "cache_read_tokens", "cache_write_tokens",
    "cost_actual", "cost_bedrock_equivalent", "duration_s",
}


def test_oauth_write_row_skips_non_opus(oauth_path):
    oc._write_row({"model": "claude-sonnet-4-5"}, _resp(_chat_usage()), T0, T1)
    assert not oauth_path.exists()  # nothing written for non-oauth route


def test_oauth_write_row_skips_empty_model(oauth_path):
    oc._write_row({}, _resp(_chat_usage()), T0, T1)
    assert not oauth_path.exists()


def test_oauth_write_row_exact_key_schema(oauth_path):
    oc._write_row({"model": "anthropic/claude-opus-4-5"}, _resp(_chat_usage()), T0, T1)
    rows = _read_rows(oauth_path)
    assert len(rows) == 1
    assert set(rows[0].keys()) == EXPECTED_OAUTH_KEYS


def test_oauth_write_row_values_and_route(oauth_path):
    usage = _chat_usage(prompt_tokens=1500, completion_tokens=100, cache_read=300, cache_write=50)
    oc._write_row({"model": "anthropic/claude-opus-4-5"}, _resp(usage), T0, T1)
    row = _read_rows(oauth_path)[0]
    assert row["model"] == "anthropic/claude-opus-4-5"
    assert row["route"] == "claude_oauth_bridge"
    assert row["input_tokens"] == 1500 - 300 - 50
    assert row["output_tokens"] == 100
    assert row["cache_read_tokens"] == 300
    assert row["cache_write_tokens"] == 50
    assert row["cost_actual"] == 0.0  # prepaid subscription -> $0 marginal
    assert row["duration_s"] == 2.5


def test_oauth_write_row_cost_bedrock_equivalent(oauth_path):
    usage = _chat_usage(prompt_tokens=1500, completion_tokens=100, cache_read=300, cache_write=50)
    oc._write_row({"model": "opus"}, _resp(usage), T0, T1)
    row = _read_rows(oauth_path)[0]
    input_tokens = 1500 - 300 - 50
    expected = round(
        input_tokens * 5e-6 + 100 * 25e-6 + 300 * 5e-7 + 50 * 6.25e-6, 6
    )
    assert row["cost_bedrock_equivalent"] == expected


def test_oauth_write_row_negative_non_cached_clamped(oauth_path):
    # prompt < cache_read + cache_write -> clamp to 0 (no warn helper here)
    usage = _chat_usage(prompt_tokens=100, completion_tokens=5, cache_read=200, cache_write=30)
    oc._write_row({"model": "opus"}, _resp(usage), T0, T1)
    row = _read_rows(oauth_path)[0]
    assert row["input_tokens"] == 0


def test_oauth_write_row_prompt_tokens_details_cached(oauth_path):
    usage = {
        "prompt_tokens": 900,
        "completion_tokens": 40,
        "prompt_tokens_details": {"cached_tokens": 250},
    }
    oc._write_row({"model": "opus"}, _resp(usage), T0, T1)
    row = _read_rows(oauth_path)[0]
    assert row["cache_read_tokens"] == 250
    assert row["input_tokens"] == 900 - 250


def test_oauth_write_row_input_tokens_key_fallback(oauth_path):
    # transcription-style usage with input_tokens/output_tokens keys
    usage = {"input_tokens": 400, "output_tokens": 20}
    oc._write_row({"model": "opus"}, _resp(usage), T0, T1)
    row = _read_rows(oauth_path)[0]
    assert row["input_tokens"] == 400
    assert row["output_tokens"] == 20


def test_oauth_write_row_dict_response_obj(oauth_path):
    resp = {"usage": _chat_usage(prompt_tokens=700, completion_tokens=35)}
    oc._write_row({"model": "opus"}, resp, T0, T1)
    row = _read_rows(oauth_path)[0]
    assert row["input_tokens"] == 700
    assert row["output_tokens"] == 35


def test_oauth_write_row_appends(oauth_path):
    for i in range(3):
        oc._write_row({"model": "opus"}, _resp(_chat_usage(prompt_tokens=100 * (i + 1))), T0, T1)
    rows = _read_rows(oauth_path)
    assert len(rows) == 3
    assert [r["input_tokens"] for r in rows] == [100, 200, 300]


def test_oauth_write_row_creates_nested_dir(tmp_path, monkeypatch):
    target = tmp_path / "a" / "b" / "usage_oauth.jsonl"
    monkeypatch.setattr(oc, "_PATH", str(target))
    oc._write_row({"model": "opus"}, _resp(_chat_usage()), T0, T1)
    assert target.exists()


def test_oauth_write_row_bad_times_duration_zero(oauth_path):
    oc._write_row({"model": "opus"}, _resp(_chat_usage()), "bad", "bad")
    row = _read_rows(oauth_path)[0]
    assert row["duration_s"] == 0.0


def test_oauth_write_row_swallows_errors(oauth_path, monkeypatch):
    monkeypatch.setattr(oc.os, "makedirs", lambda *a, **k: (_ for _ in ()).throw(OSError("x")))
    monkeypatch.setattr(oc.sys.stderr, "write", lambda s: None)
    # opus route so it gets past the gate, then makedirs blows up -> swallowed.
    oc._write_row({"model": "opus"}, _resp(_chat_usage()), T0, T1)


def test_oauth_async_log_success_event(oauth_path):
    import asyncio
    writer = oc.OAuthUsageWriter()
    asyncio.run(writer.async_log_success_event(
        {"model": "opus"}, _resp(_chat_usage()), T0, T1
    ))
    assert len(_read_rows(oauth_path)) == 1


def test_oauth_callback_instance_type():
    assert isinstance(oc.oauth_usage_callback_instance, oc.OAuthUsageWriter)


# ============================================================================
# Module-level _PATH env override (both modules read env at import)
# ============================================================================


def test_primary_path_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("LITELLM_USAGE_LOG_PATH", str(tmp_path / "custom.jsonl"))
    reloaded = importlib.reload(uc)
    try:
        assert reloaded._PATH == str(tmp_path / "custom.jsonl")
    finally:
        monkeypatch.delenv("LITELLM_USAGE_LOG_PATH", raising=False)
        importlib.reload(uc)


def test_oauth_path_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("WCB_OAUTH_USAGE_LOG_PATH", str(tmp_path / "oauth_custom.jsonl"))
    reloaded = importlib.reload(oc)
    try:
        assert reloaded._PATH == str(tmp_path / "oauth_custom.jsonl")
    finally:
        monkeypatch.delenv("WCB_OAUTH_USAGE_LOG_PATH", raising=False)
        importlib.reload(oc)
