"""Tests for the opt-in LiteLLM + Headroom judge transport (`judge_litellm.py`)
and its integration with the council dispatcher in `grading._call_one_judge`.

The 10 unit tests guard the contracts the rest of the harness silently relies
on (see `src/utils/AGENTS.md` and `RUNBOOK.md`):

  1. Default OFF: when `KENSEI_JUDGE_USE_LITELLM` is unset, grading uses the
     legacy urllib path. No litellm import, no headroom import.
  2. Headroom ImportError-safe: if `headroom-ai` is not installed, the LiteLLM
     path still works (compression silently no-ops).
  3. Headroom stats land in the per-judge `usage["headroom"]` sub-dict.
  4. `compress_system_messages=False` is the load-bearing config — guards the
     verdict-format regex `_VERDICT_RE`. Test asserts the CompressConfig.
  5. `max_tokens` passed to `litellm.completion` matches
     `_member_max_output_tokens(arn)` (Sonnet 8192, Kimi/GLM 16384).
  6. The judge call must NOT include `thinking`, `reasoning_effort`,
     `output_config`, or `response_format` (bg_f3f8f684 #4 invariant).
  7. The returned `usage` dict has the canonical 7 keys with the same
     semantics as the urllib path (input_tokens excludes cache).
  8. On ANY LiteLLM exception the dispatcher falls back to urllib so grading
     never fails because of transport choice (user m0039 contract).
  9. `register_judges_for_batch(members)` calls `litellm.register_model` once
     per CURRENT (rotation-aware) judge ARN tail, pulling ctx-window / max-output
     / cost rates from the family-keyed source of truth in `grading`.
 10. ARN tokenizer hint: when the model id contains
     `application-inference-profile`, Headroom is called with the Anthropic
     model hint so its tokenizer can do meaningful estimates.

Plus 1 integration smoke (gated by `RUN_INTEGRATION_JUDGE_TESTS=true`) that
verifies Bedrock `cache_control` markers survive Headroom compression and
trigger a real `cache_read_input_tokens > 0` on the second call (5-min TTL).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import grading, judge_litellm  # noqa: E402


# ---------- shared fixtures / helpers ----------


@pytest.fixture(autouse=True)
def _clean_env_and_state(monkeypatch):
    """Every test starts from a known env baseline + a fresh module-level
    registration flag so test ordering doesn't matter."""
    for var in (
        "KENSEI_JUDGE_USE_LITELLM",
        "KENSEI_JUDGE_HEADROOM_ENABLED",
        "KENSEI_JUDGE_HEADROOM_TARGET_RATIO",
        "KENSEI_JUDGE_HEADROOM_PROTECT_RECENT",
        "KENSEI_JUDGE_HEADROOM_MIN_TOKENS",
    ):
        monkeypatch.delenv(var, raising=False)
    # Reset the per-tail idempotency latch — otherwise the first test that
    # registers a tail blocks subsequent tests from observing the register_model
    # call for that same tail. Clearing keeps tests order-independent and also
    # mirrors the monthly-rotation reality where a new tail must re-register.
    judge_litellm._registered_tails.clear()
    yield


def _make_litellm_response(text: str = "1. example [[RATIONALE: x]] [[SATISFIED: Yes]]",
                           prompt_tokens: int = 1000,
                           completion_tokens: int = 50,
                           cache_read: int = 0,
                           cache_write: int = 0) -> SimpleNamespace:
    """Construct a fake LiteLLM `completion()` return value matching the
    OpenAI-normalized shape the production code reads."""
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=text))],
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cache_read_input_tokens": cache_read,
            "cache_creation_input_tokens": cache_write,
        },
    )


SONNET_ARN = "bedrock/arn:aws:bedrock:ap-south-1:426628337772:application-inference-profile/is9bst5tfadh"
GLM_ARN = "bedrock/arn:aws:bedrock:us-east-1:426628337772:application-inference-profile/xx5msvho23iq"
KIMI_ARN = "bedrock/arn:aws:bedrock:ap-south-1:426628337772:application-inference-profile/p532c9fzmeed"


# ---------- Test 1: litellm OFF → uses direct urllib path ----------


def test_litellm_off_uses_direct_path(monkeypatch):
    """When KENSEI_JUDGE_USE_LITELLM is unset/false the dispatcher must take
    the urllib branch. We assert by sentinel-mocking the urllib function and
    poisoning `judge_litellm.call_judge_via_litellm` to raise if accidentally
    invoked."""
    sentinel = ("ok-from-urllib", {"input_tokens": 1, "output_tokens": 2,
                                   "cache_read_tokens": 0, "cache_write_tokens": 0,
                                   "total_tokens": 3, "request_count": 1,
                                   "cost_usd": 0.0})
    monkeypatch.setattr(grading, "_call_judge_bedrock", lambda *a, **k: sentinel)

    def _poison(*a, **k):
        raise AssertionError("LiteLLM path must NOT be called when flag is off")

    monkeypatch.setattr(judge_litellm, "call_judge_via_litellm", _poison)

    text, usage = grading._call_one_judge(SONNET_ARN, "sys", "user")
    assert text == "ok-from-urllib"
    assert usage["input_tokens"] == 1


# ---------- Test 2: Headroom ImportError → silent no-op ----------


def test_litellm_on_no_headroom_install_falls_back_gracefully(monkeypatch):
    """If headroom-ai is not installed, `maybe_compress` returns the original
    messages + {} stats. The LiteLLM call still proceeds with uncompressed
    payload — grading never fails because compression is unavailable."""
    monkeypatch.setenv("KENSEI_JUDGE_USE_LITELLM", "true")

    # Simulate ImportError on `from headroom import compress, CompressConfig`
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "headroom":
            raise ImportError("simulated: headroom-ai not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _fake_import)

    messages = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
    out_messages, stats = judge_litellm.maybe_compress(messages, SONNET_ARN)

    assert out_messages is messages, "must pass-through original list on ImportError"
    assert stats == {}, "no telemetry when headroom unavailable"


# ---------- Test 3: Headroom compression stats recorded ----------


def test_headroom_compression_stats_recorded(monkeypatch):
    """Stub `compress()` to return a non-trivial CompressResult and assert
    the stats land in `usage['headroom']` with the expected key shape."""
    monkeypatch.setenv("KENSEI_JUDGE_USE_LITELLM", "true")

    fake_result = SimpleNamespace(
        messages=[{"role": "system", "content": "s"},
                  {"role": "user", "content": "u-compressed"}],
        tokens_before=10_000,
        tokens_after=4_000,
        tokens_saved=6_000,
        compression_ratio=0.4,
        transforms_applied=["dedupe", "whitespace"],
    )

    class _FakeCompressConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_headroom = SimpleNamespace(
        compress=lambda messages, model, config: fake_result,
        CompressConfig=_FakeCompressConfig,
    )

    fake_litellm = SimpleNamespace(
        completion=mock.MagicMock(return_value=_make_litellm_response()),
        register_model=mock.MagicMock(),
    )

    monkeypatch.setitem(sys.modules, "headroom", fake_headroom)
    monkeypatch.setitem(sys.modules, "litellm", fake_litellm)

    _, usage = judge_litellm.call_judge_via_litellm(
        model=SONNET_ARN, system="s", user="u",
        max_output_tokens=8192, cost_fn=grading._judge_cost_usd, family="sonnet",
    )
    hr = usage["headroom"]
    assert hr["tokens_before"] == 10_000
    assert hr["tokens_after"] == 4_000
    assert hr["tokens_saved"] == 6_000
    assert hr["compression_ratio"] == pytest.approx(0.4)
    assert hr["transforms_applied"] == ["dedupe", "whitespace"]


# ---------- Test 4: compress_system_messages=False is load-bearing ----------


def test_compress_system_messages_is_false(monkeypatch):
    """The system prompt encodes the verdict format that `_VERDICT_RE` parses;
    compressing it risks zeroing the whole council. Asserts CompressConfig
    was constructed with compress_system_messages=False AND
    compress_user_messages=True."""
    monkeypatch.setenv("KENSEI_JUDGE_USE_LITELLM", "true")

    captured_config = {}

    class _RecordingConfig:
        def __init__(self, **kwargs):
            captured_config.update(kwargs)

    fake_result = SimpleNamespace(
        messages=[{"role": "system", "content": "s"}, {"role": "user", "content": "u"}],
        tokens_before=3_000, tokens_after=3_000, tokens_saved=0,
        compression_ratio=1.0, transforms_applied=[],
    )
    fake_headroom = SimpleNamespace(
        compress=lambda messages, model, config: fake_result,
        CompressConfig=_RecordingConfig,
    )
    monkeypatch.setitem(sys.modules, "headroom", fake_headroom)

    judge_litellm.maybe_compress(
        [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}],
        SONNET_ARN,
    )

    assert captured_config.get("compress_user_messages") is True
    assert captured_config.get("compress_system_messages") is False


# ---------- Test 5: max_tokens passed to litellm.completion is per-judge ----------


@pytest.mark.parametrize("arn,family,expected_max", [
    (SONNET_ARN, "sonnet", 8192),
    (GLM_ARN, "glm", 16384),
    (KIMI_ARN, "kimi", 16384),
])
def test_judge_max_tokens_unchanged(monkeypatch, arn, family, expected_max):
    """Each judge keeps its production max-output ceiling. Drift here would
    truncate verdicts mid-rubric — `_parse_verdict_text` would still return a
    list but with fewer entries, silently dropping criteria. The ceiling is
    resolved by stable family, not the rotating ARN tail."""
    monkeypatch.setenv("KENSEI_JUDGE_USE_LITELLM", "true")
    monkeypatch.setenv("KENSEI_JUDGE_HEADROOM_ENABLED", "false")

    completion_mock = mock.MagicMock(return_value=_make_litellm_response())
    fake_litellm = SimpleNamespace(completion=completion_mock, register_model=mock.MagicMock())
    monkeypatch.setitem(sys.modules, "litellm", fake_litellm)

    judge_litellm.call_judge_via_litellm(
        model=arn, system="s", user="u",
        max_output_tokens=grading._member_max_output_tokens(grading._arn_from_model(arn), family),
        cost_fn=grading._judge_cost_usd, family=family,
    )

    completion_mock.assert_called_once()
    _, kwargs = completion_mock.call_args
    assert kwargs["max_tokens"] == expected_max


# ---------- Test 6: no thinking / reasoning_effort / output_config / response_format ----------


def test_no_thinking_field_in_litellm_call(monkeypatch):
    """The Sonnet sidecar entry in litellm_sidecar.py enables `thinking:
    adaptive` for the AGENT path, but judges MUST NOT get extended thinking
    (changes character of output, breaks the verdict-format regex). Same for
    `reasoning_effort`, `output_config`, and `response_format:json_object`
    (the last breaks `_VERDICT_RE` per grading.py:413-420 comment)."""
    monkeypatch.setenv("KENSEI_JUDGE_USE_LITELLM", "true")
    monkeypatch.setenv("KENSEI_JUDGE_HEADROOM_ENABLED", "false")

    completion_mock = mock.MagicMock(return_value=_make_litellm_response())
    fake_litellm = SimpleNamespace(completion=completion_mock, register_model=mock.MagicMock())
    monkeypatch.setitem(sys.modules, "litellm", fake_litellm)

    judge_litellm.call_judge_via_litellm(
        model=SONNET_ARN, system="s", user="u",
        max_output_tokens=8192, cost_fn=grading._judge_cost_usd, family="sonnet",
    )
    _, kwargs = completion_mock.call_args
    for forbidden in ("thinking", "reasoning_effort", "output_config", "response_format"):
        assert forbidden not in kwargs, f"judge call must not include {forbidden!r}"


# ---------- Test 7: usage dict shape matches urllib path ----------


def test_usage_dict_shape_matches_urllib_path(monkeypatch):
    """The 7-key shape is the contract `_grade_council`'s council_usage
    aggregator depends on. The `headroom` sub-dict is purely additive."""
    monkeypatch.setenv("KENSEI_JUDGE_USE_LITELLM", "true")
    monkeypatch.setenv("KENSEI_JUDGE_HEADROOM_ENABLED", "false")

    fake_litellm = SimpleNamespace(
        completion=lambda **kw: _make_litellm_response(
            prompt_tokens=1500, completion_tokens=120,
            cache_read=300, cache_write=50,
        ),
        register_model=mock.MagicMock(),
    )
    monkeypatch.setitem(sys.modules, "litellm", fake_litellm)

    _, usage = judge_litellm.call_judge_via_litellm(
        model=SONNET_ARN, system="s", user="u",
        max_output_tokens=8192, cost_fn=grading._judge_cost_usd, family="sonnet",
    )
    expected_keys = set(grading._ZERO_USAGE.keys())
    assert expected_keys.issubset(set(usage.keys())), \
        f"missing keys: {expected_keys - set(usage.keys())}"
    # input_tokens MUST be non-cached
    assert usage["input_tokens"] == 1500 - 300 - 50
    assert usage["cache_read_tokens"] == 300
    assert usage["cache_write_tokens"] == 50
    assert usage["output_tokens"] == 120
    assert usage["total_tokens"] == (1500 - 300 - 50) + 120 + 300 + 50
    assert usage["request_count"] == 1
    # Additive field is present but doesn't displace any canonical key
    assert "headroom" in usage


# ---------- Test 8: LiteLLM failure falls back to urllib ----------


def test_litellm_failure_falls_back_to_urllib(monkeypatch):
    """Any exception inside the LiteLLM path must NOT propagate — the
    dispatcher logs + falls through to urllib. This is the m0039 'follow the
    code at all times' contract: grading cannot fail because LiteLLM had a
    bad day."""
    monkeypatch.setenv("KENSEI_JUDGE_USE_LITELLM", "true")

    def _explode(*a, **k):
        raise RuntimeError("simulated LiteLLM blowup")

    monkeypatch.setattr(judge_litellm, "call_judge_via_litellm", _explode)

    sentinel = ("urllib-fallback-worked", dict(grading._ZERO_USAGE, request_count=1))
    monkeypatch.setattr(grading, "_call_judge_bedrock", lambda *a, **k: sentinel)

    text, usage = grading._call_one_judge(SONNET_ARN, "sys", "user")
    assert text == "urllib-fallback-worked"
    assert usage["request_count"] == 1


# ---------- Test 9: register_judges_for_batch registers all three judges ----------


def test_register_model_called_for_all_judges(monkeypatch):
    """`register_judges_for_batch(members)` issues one `register_model` call
    per CURRENT (rotation-aware) council ARN tail, and the registered
    ctx-window / max-output / cost rates come straight from the family-keyed
    source of truth in grading (`_FAMILY_EVIDENCE`, `_FAMILY_RATES`). That
    single source is what keeps the LiteLLM transport's pricing from drifting
    away from the urllib transport's — the bug class `test_judge_budget_invariant.py`
    (a different invariant) can't catch. Re-keying on stable family rather than
    the opaque, monthly-rotating profile id is the whole point of the decoupling."""
    # Seed the three council members from env (family derived from var name).
    monkeypatch.setenv("JUDGE_COUNCIL_SONNET_ARN", SONNET_ARN)
    monkeypatch.setenv("JUDGE_COUNCIL_GLM_ARN", GLM_ARN)
    monkeypatch.setenv("JUDGE_COUNCIL_KIMI_ARN", KIMI_ARN)
    monkeypatch.delenv("JUDGE_COUNCIL_MEMBERS", raising=False)

    members = grading.council_members()
    assert {m.family for m in members} == {"sonnet", "glm", "kimi"}

    register_mock = mock.MagicMock()
    fake_litellm = SimpleNamespace(register_model=register_mock)
    monkeypatch.setitem(sys.modules, "litellm", fake_litellm)

    judge_litellm.register_judges_for_batch(members)

    # One register_model call per family.
    assert register_mock.call_count == 3

    # The registered tails are the *current* ARN tails (rotation-aware), and
    # each payload's numbers match grading's family-keyed source of truth.
    tail_to_family = {judge_litellm._arn_tail(m.model): m.family for m in members}
    registered_tails = set()
    for call in register_mock.call_args_list:
        ((payload,), _) = call
        assert isinstance(payload, dict) and len(payload) == 1
        tail = next(iter(payload.keys()))
        info = payload[tail]
        registered_tails.add(tail)

        family = tail_to_family[tail]
        r_in, r_out, r_cr, r_cw = grading._FAMILY_RATES[family]
        ctx, max_out = grading._FAMILY_EVIDENCE[family]
        assert info["max_input_tokens"] == ctx
        assert info["max_tokens"] == ctx
        assert info["max_output_tokens"] == max_out
        assert info["input_cost_per_token"] == r_in
        assert info["output_cost_per_token"] == r_out
        assert info["cache_read_input_token_cost"] == r_cr
        assert info["cache_creation_input_token_cost"] == r_cw
        assert info["litellm_provider"] == "bedrock_converse"
        assert info["mode"] == "chat"

    assert registered_tails == {"is9bst5tfadh", "xx5msvho23iq", "p532c9fzmeed"}

    # Idempotency: second call is a no-op (per-tail latch, no extra calls).
    judge_litellm.register_judges_for_batch(members)
    assert register_mock.call_count == 3


# ---------- Test 10: ARN tokenizer hint ----------


def test_arn_tokenizer_hint(monkeypatch):
    """When the model id contains `application-inference-profile`, Headroom
    must be called with `anthropic/claude-sonnet-4-5-20250929` as the model
    hint (Headroom can't tokenize an opaque ARN). The actual LiteLLM call
    still uses the original ARN; only the tokenizer hint is swapped."""
    captured = {}

    class _RecordingConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    def _recording_compress(messages, model, config):
        captured["model_passed_to_compress"] = model
        return SimpleNamespace(
            messages=messages, tokens_before=5_000, tokens_after=4_500,
            tokens_saved=500, compression_ratio=0.9,
            transforms_applied=["x"],
        )

    fake_headroom = SimpleNamespace(compress=_recording_compress, CompressConfig=_RecordingConfig)
    monkeypatch.setitem(sys.modules, "headroom", fake_headroom)

    judge_litellm.maybe_compress(
        [{"role": "system", "content": "s"}, {"role": "user", "content": "u" * 20_000}],
        SONNET_ARN,
    )
    assert captured["model_passed_to_compress"] == "anthropic/claude-sonnet-4-5-20250929"

    # Sanity: a non-ARN model is passed through unchanged
    captured.clear()
    judge_litellm.maybe_compress(
        [{"role": "system", "content": "s"}, {"role": "user", "content": "u" * 20_000}],
        "openai/gpt-5.5",
    )
    assert captured["model_passed_to_compress"] == "openai/gpt-5.5"


# ---------- Integration smoke: cache_control survives compression ----------


@pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_JUDGE_TESTS", "").lower() not in ("1", "true", "yes", "on"),
    reason="integration smoke — set RUN_INTEGRATION_JUDGE_TESTS=true to run; needs Bedrock creds",
)
def test_cache_control_survival_smoke():
    """End-to-end: make two real Sonnet judge calls within the 5-min cache
    TTL with LiteLLM+Headroom on. The second must report
    `cache_read_tokens > 0`, proving `cache_control` markers survived
    Headroom's compression and translated to Bedrock's `cachePoint` block.

    Gated by env var because it costs ~$0.03/run and needs
    `AWS_BEARER_TOKEN_BEDROCK`."""
    os.environ["KENSEI_JUDGE_USE_LITELLM"] = "true"
    os.environ["KENSEI_JUDGE_HEADROOM_ENABLED"] = "true"

    system = (
        "You are a strict rubric judge. For each numbered criterion respond in this "
        "exact format: 'N. <criterion> [[RATIONALE: ...]] [[SATISFIED: Yes|No]]'."
    )
    # Long enough to trigger Bedrock prompt-caching (>1024 tokens worth of system)
    user = "1. The answer mentions Python.\n\nAnswer: The user mentioned Python."

    _, usage1 = judge_litellm.call_judge_via_litellm(
        model=SONNET_ARN, system=system, user=user,
        max_output_tokens=8192, cost_fn=grading._judge_cost_usd, family="sonnet",
    )
    _, usage2 = judge_litellm.call_judge_via_litellm(
        model=SONNET_ARN, system=system, user=user,
        max_output_tokens=8192, cost_fn=grading._judge_cost_usd, family="sonnet",
    )

    # First call: cache_write should be non-zero (we just primed it)
    # Second call: cache_read should be non-zero (we just read it back)
    assert usage2["cache_read_tokens"] > 0, (
        "cache_control did not survive Headroom compression — second call "
        "should have produced cache_read_tokens > 0"
    )


# ---------- Test 7: Sonnet judge routed through the OAuth subscription bridge ----------


def _bridge_env(monkeypatch, url="http://127.0.0.1:18765", model=None):
    monkeypatch.setenv("KENSEI_JUDGE_USE_LITELLM", "true")
    monkeypatch.setenv("KENSEI_JUDGE_HEADROOM_ENABLED", "false")
    if url is not None:
        monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", url)
    else:
        monkeypatch.delenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", raising=False)
    if model is not None:
        monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_MODEL", model)
    else:
        monkeypatch.delenv("KENSEI_JUDGE_OAUTH_BRIDGE_MODEL", raising=False)
    monkeypatch.setenv("WCB_CC_STUB_KEY", "sk-wcb-oauth-stub")
    monkeypatch.setenv("WCB_CC_BRIDGE_SECRET", "testsecret")


def _capture_completion_kwargs(monkeypatch, arn, family):
    completion_mock = mock.MagicMock(return_value=_make_litellm_response())
    fake_litellm = SimpleNamespace(completion=completion_mock, register_model=mock.MagicMock())
    monkeypatch.setitem(sys.modules, "litellm", fake_litellm)
    judge_litellm.call_judge_via_litellm(
        model=arn, system="s", user="u",
        max_output_tokens=8192, cost_fn=grading._judge_cost_usd, family=family,
    )
    _, kwargs = completion_mock.call_args
    return kwargs


def test_oauth_bridge_route_injected_for_sonnet(monkeypatch):
    _bridge_env(monkeypatch)
    kwargs = _capture_completion_kwargs(monkeypatch, SONNET_ARN, "sonnet")
    assert kwargs["api_base"] == "http://127.0.0.1:18765"
    assert kwargs["api_key"] == "sk-wcb-oauth-stub"
    assert kwargs["extra_headers"] == {"x-wcb-bridge-secret": "testsecret"}
    assert kwargs["model"] == "anthropic/claude-sonnet-4-5-20250929"
    assert "aws_region_name" not in kwargs


def test_oauth_bridge_route_custom_model(monkeypatch):
    _bridge_env(monkeypatch, model="anthropic/claude-sonnet-4-6")
    kwargs = _capture_completion_kwargs(monkeypatch, SONNET_ARN, "sonnet")
    assert kwargs["model"] == "anthropic/claude-sonnet-4-6"
    assert kwargs["api_base"] == "http://127.0.0.1:18765"


def test_oauth_bridge_not_injected_when_url_unset(monkeypatch):
    _bridge_env(monkeypatch, url=None)
    kwargs = _capture_completion_kwargs(monkeypatch, SONNET_ARN, "sonnet")
    assert "api_base" not in kwargs
    assert kwargs.get("aws_region_name") == "ap-south-1"


def test_oauth_bridge_not_injected_for_non_sonnet(monkeypatch):
    _bridge_env(monkeypatch)
    kwargs = _capture_completion_kwargs(monkeypatch, GLM_ARN, "glm")
    assert "api_base" not in kwargs
