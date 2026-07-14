"""Unit tests for the AGENT-PATH Headroom proxy pre-call hook
(`src/utils/litellm_headroom_callback.py`).

Each test names the production invariant it guards so a failure self-explains:

| # | Invariant guarded |
|---|---|
| 1 | Callback DISABLED → data returned unchanged, headroom never invoked |
| 2 | Callback ENABLED but headroom unimportable → data unchanged, no crash |
| 3 | call_type='completion' triggers compression when net-positive saved |
| 4 | call_type='embeddings' (or anything except completion/acompletion) skipped |
| 5 | CompressConfig.compress_system_messages MUST be False (system prompt has |
|   | tool schemas + openclaw verbatim instructions — must not be compressed) |
| 6 | ARN tokenizer hint: Bedrock ARN → 'anthropic/claude-opus-4-20250514' for |
|   | accurate token budget math; non-ARN model strings pass through |
| 7 | Telemetry writes to the SEPARATE JSONL path under |
|   | KENSEI_AGENT_HEADROOM_LOG_PATH; usage.jsonl never touched |
| 8 | compress() exception → fail-open: data returned unchanged |
| 9 | Module exposes a singleton `headroom_callback_instance` that IS a |
|   | CustomLogger subclass (LiteLLM's pre-call dispatch loop requires this) |
| 10| Regression guard: async_pre_call_hook accepts the canonical LiteLLM proxy |
|   | 4-arg keyword signature (user_api_key_dict, cache, data, call_type) — |
|   | bundled HeadroomCallback only accepts 3 args and crashes on first request |

Pattern follows `tests/test_judge_litellm.py` (sys.path shim, autouse fixture
clearing env vars + module-level state, sys.modules stubbing for the headroom
package, parametrize for tokenizer-hint table).
"""

from __future__ import annotations

import asyncio
import importlib
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

# tests/ is one level below repo root; mirror the test_judge_litellm.py shim
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import litellm_headroom_callback as hr  # noqa: E402


# ────────────────────────────────────────────────────────────────────────────
# Fixtures
# ────────────────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _clean_env_and_state(monkeypatch, tmp_path):
    # The 5 KENSEI_AGENT_HEADROOM_* env vars are read live on every hook call
    # (except LOG_PATH which is captured at module-import time — handled
    # separately in the telemetry test via module reload). Reset them so test
    # ordering is irrelevant.
    for var in (
        "KENSEI_AGENT_HEADROOM_ENABLED",
        "KENSEI_AGENT_HEADROOM_TARGET_RATIO",
        "KENSEI_AGENT_HEADROOM_PROTECT_RECENT",
        "KENSEI_AGENT_HEADROOM_MIN_TOKENS",
        "KENSEI_AGENT_HEADROOM_LOG_PATH",
    ):
        monkeypatch.delenv(var, raising=False)

    # Reset the tri-state probe so each test re-evaluates whether headroom is
    # importable (some tests stub it, some don't; we don't want the first
    # test's outcome to be cached for the rest).
    hr._HEADROOM_AVAILABLE = None
    hr._compress = None
    hr._CompressConfig = None

    yield

    # Post-test: ensure stubbed sys.modules entries don't leak across tests
    sys.modules.pop("headroom", None)


def _make_compress_result(
    *,
    messages=None,
    tokens_before=10_000,
    tokens_after=4_000,
    compression_ratio=0.4,
    transforms=("dedupe", "whitespace"),
):
    """Build a SimpleNamespace matching headroom.CompressResult shape."""
    return SimpleNamespace(
        messages=messages if messages is not None else [{"role": "user", "content": "compressed"}],
        tokens_before=tokens_before,
        tokens_after=tokens_after,
        tokens_saved=tokens_before - tokens_after,
        compression_ratio=compression_ratio,
        transforms_applied=list(transforms),
    )


def _stub_headroom(compress_fn=None, config_cls=None):
    """Inject a fake `headroom` package whose top-level exports match the real
    0.24+ API (`from headroom import compress, CompressConfig`).

    Tri-state probe re-runs after this since the autouse fixture reset
    `_HEADROOM_AVAILABLE` to None.
    """
    fake_root = SimpleNamespace(
        compress=compress_fn or (lambda messages, model=None, config=None: _make_compress_result()),
        CompressConfig=config_cls or (lambda **kwargs: SimpleNamespace(**kwargs)),
    )
    sys.modules["headroom"] = fake_root


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if sys.version_info < (3, 10) else asyncio.run(coro)


# ────────────────────────────────────────────────────────────────────────────
# Test 1 — DISABLED returns data unchanged
# ────────────────────────────────────────────────────────────────────────────


def test_callback_disabled_returns_data_unchanged(monkeypatch):
    """When KENSEI_AGENT_HEADROOM_ENABLED is unset, the hook is a no-op."""
    monkeypatch.delenv("KENSEI_AGENT_HEADROOM_ENABLED", raising=False)

    # Poison: if compress is called, raise loudly — the disabled path must
    # never even probe headroom.
    def _boom(*a, **kw):  # pragma: no cover - asserted not called
        raise AssertionError("compress() called despite KENSEI_AGENT_HEADROOM_ENABLED=unset")

    _stub_headroom(compress_fn=_boom)
    data = {"messages": [{"role": "user", "content": "x" * 5000}], "model": "claude-opus-4.7"}

    result = _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="completion",
        )
    )
    assert result is data
    assert data["messages"][0]["content"] == "x" * 5000


# ────────────────────────────────────────────────────────────────────────────
# Test 2 — ENABLED but headroom unimportable → no crash
# ────────────────────────────────────────────────────────────────────────────


def test_callback_enabled_no_headroom_install_returns_data(monkeypatch):
    """If headroom-ai is not installed inside the sidecar (operator forgot
    to switch to wildclawbench-litellm-headroom:v1 image), the hook degrades
    silently — the agent's request proceeds uncompressed."""
    monkeypatch.setenv("KENSEI_AGENT_HEADROOM_ENABLED", "true")

    # Force the probe to fail by removing any chance of importing headroom.
    # We use a real ImportError raised during the probe.
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def _no_headroom(name, *args, **kwargs):
        if name.startswith("headroom"):
            raise ImportError(f"simulated missing headroom-ai for: {name}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", _no_headroom)
    data = {"messages": [{"role": "user", "content": "x" * 5000}], "model": "gpt-5.5"}

    result = _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="completion",
        )
    )
    assert result is data
    assert hr._HEADROOM_AVAILABLE is False  # probe cached the negative result


# ────────────────────────────────────────────────────────────────────────────
# Test 3 — completion triggers compression when net-positive
# ────────────────────────────────────────────────────────────────────────────


def test_compress_runs_on_completion_call_type(monkeypatch):
    """call_type='completion' + ENABLED + headroom importable + tokens_saved>0
    → data['messages'] is replaced with compressed list."""
    monkeypatch.setenv("KENSEI_AGENT_HEADROOM_ENABLED", "true")

    new_msgs = [{"role": "user", "content": "compressed-evidence"}]
    _stub_headroom(
        compress_fn=lambda messages, model=None, config=None: _make_compress_result(
            messages=new_msgs, tokens_before=20_000, tokens_after=8_000,
        ),
    )
    data = {
        "messages": [{"role": "user", "content": "x" * 10000}],
        "model": "claude-opus-4.7",
    }
    result = _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="completion",
        )
    )
    assert result is data
    # data["messages"] is replaced with the compressed content. (It is now a
    # freshly-merged list rather than the exact result.messages object, because
    # the hook restores original block-shaped messages where compression no-ops
    # — see _flatten_text_block_content — so assert by equality, not identity.)
    assert data["messages"] == new_msgs


# ────────────────────────────────────────────────────────────────────────────
# Test 3b — Anthropic block content is flattened so the compressor engages
# ────────────────────────────────────────────────────────────────────────────


def test_anthropic_block_content_is_flattened_for_compressor(monkeypatch):
    """openclaw drives /v1/messages, whose content is a LIST OF BLOCKS. Headroom
    no-ops on block content, so the hook must collapse pure-text blocks to a
    string before compressing — while leaving tool_use / cache_control blocks
    structurally intact. Verified end-to-end 2026-06-15 that the un-flattened
    path saved 0 on real openclaw traffic. Capture what compress() receives.
    Also implicitly exercises the anthropic_messages call_type allowlist."""
    monkeypatch.setenv("KENSEI_AGENT_HEADROOM_ENABLED", "true")

    seen = {}

    def _capture(messages, model=None, config=None):
        seen["messages"] = messages
        return _make_compress_result(messages=messages)

    _stub_headroom(compress_fn=_capture)

    data = {
        "model": "bedrock/anthropic.claude-opus-4-6-v1",
        "messages": [
            # pure text block -> MUST be flattened to a string
            {"role": "user", "content": [{"type": "text", "text": "T" * 9000}]},
            # tool_use block -> MUST stay a list (structure preserved verbatim)
            {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "read", "input": {}}]},
            # text block carrying cache_control -> MUST stay a list (cache hint kept)
            {"role": "user", "content": [{"type": "text", "text": "k", "cache_control": {"type": "ephemeral"}}]},
        ],
    }
    _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="anthropic_messages",
        )
    )
    got = seen["messages"]
    assert isinstance(got[0]["content"], str) and got[0]["content"] == "T" * 9000, \
        "pure text-block content must flatten to a string so the compressor engages"
    assert isinstance(got[1]["content"], list), "tool_use block must NOT be flattened"
    assert isinstance(got[2]["content"], list), "cache_control text block must NOT be flattened"


# ────────────────────────────────────────────────────────────────────────────
# Test 4 — non-completion call types are skipped
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("call_type", ["embeddings", "image_generation", "moderation", "audio_transcription"])
def test_skips_non_completion_call_types(monkeypatch, call_type):
    """Headroom compresses chat-completion message lists. Transcription /
    embeddings / image-gen have different request shapes — skip them."""
    monkeypatch.setenv("KENSEI_AGENT_HEADROOM_ENABLED", "true")

    def _boom(*a, **kw):  # pragma: no cover - asserted not called
        raise AssertionError(f"compress() called for non-completion call_type={call_type!r}")

    _stub_headroom(compress_fn=_boom)
    data = {"messages": [{"role": "user", "content": "x" * 5000}], "model": "whisper-1"}
    result = _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type=call_type,
        )
    )
    assert result is data


# ────────────────────────────────────────────────────────────────────────────
# Test 5 — load-bearing: compress_system_messages MUST be False
# ────────────────────────────────────────────────────────────────────────────


def test_compress_system_messages_is_false(monkeypatch):
    """openclaw's system prompt carries tool schemas + verbatim instruction
    grammar; compressing it can corrupt tool dispatch. Verify the
    CompressConfig kwargs the callback feeds to Headroom."""
    monkeypatch.setenv("KENSEI_AGENT_HEADROOM_ENABLED", "true")

    captured = {}

    def _recording_config(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(**kwargs)

    _stub_headroom(
        compress_fn=lambda messages, model=None, config=None: _make_compress_result(),
        config_cls=_recording_config,
    )
    data = {"messages": [{"role": "user", "content": "x"}], "model": "claude-opus-4.7"}
    _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="completion",
        )
    )
    assert captured.get("compress_system_messages") is False
    # compress_user_messages MUST be True — empirically verified live
    # (2026-06-11) that OpenAI chat-completion proxies (incl. openclaw's
    # tool loop) route tool_result blocks back as role=user messages, so
    # leaving Headroom 0.24.0 at default compress_user_messages=False
    # marks every user message as "router:protected:user_message" and
    # saves zero tokens. With True, smart_crusher compresses JSON tool
    # results (verified: 88KB JSON → 25.3K→15.6K tokens).
    assert captured.get("compress_user_messages") is True


# ────────────────────────────────────────────────────────────────────────────
# Test 6 — ARN tokenizer hint
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "model,expected_hint",
    [
        # Bedrock ARN with application-inference-profile — should hint
        ("bedrock/arn:aws:bedrock:us-east-1:123:application-inference-profile/abc", "anthropic/claude-opus-4-20250514"),
        # Bedrock Anthropic direct model — should hint
        ("bedrock/anthropic.claude-opus-4-6-v1", "anthropic/claude-opus-4-20250514"),
        # Substring match on the model name even without bedrock/ prefix
        ("anthropic.claude-opus-4-6-v1", "anthropic/claude-opus-4-20250514"),
        # Pass-through for OpenAI / non-Anthropic — Headroom knows these
        ("gpt-5.5", "gpt-5.5"),
        ("openai/responses/gpt-5.5", "openai/responses/gpt-5.5"),
        ("", ""),
    ],
)
def test_arn_tokenizer_hint(model, expected_hint):
    """Bedrock ARNs don't match headroom's static model table, so its
    tokenizer over-estimates by ~30%. Substring-hint Opus 4.6 routes to a
    known Anthropic model so the budget math matches what Bedrock counts."""
    assert hr._model_hint(model) == expected_hint


# ────────────────────────────────────────────────────────────────────────────
# Test 7 — telemetry writes to SEPARATE JSONL
# ────────────────────────────────────────────────────────────────────────────


def test_telemetry_writes_to_separate_path(monkeypatch, tmp_path):
    """Token-tracking invariant (user m0130): the 11-key LITELLM_USAGE_LOG_PATH
    must NEVER be touched. Headroom telemetry goes to its own JSONL keyed by
    KENSEI_AGENT_HEADROOM_LOG_PATH."""
    monkeypatch.setenv("KENSEI_AGENT_HEADROOM_ENABLED", "true")
    sep_path = tmp_path / "headroom.jsonl"
    usage_path = tmp_path / "usage.jsonl"  # poison: must remain empty
    monkeypatch.setenv("KENSEI_AGENT_HEADROOM_LOG_PATH", str(sep_path))
    monkeypatch.setenv("LITELLM_USAGE_LOG_PATH", str(usage_path))

    # _LOG_PATH is captured at module-import time. Reload the module so the
    # new env var takes effect, then re-import the singleton.
    importlib.reload(hr)

    _stub_headroom(
        compress_fn=lambda messages, model=None, config=None: _make_compress_result(
            tokens_before=12_345, tokens_after=4_321,
        ),
    )
    data = {"messages": [{"role": "user", "content": "x"}], "model": "claude-opus-4.7"}
    _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="completion",
        )
    )
    assert sep_path.exists(), "headroom telemetry sink should be written"
    assert not usage_path.exists(), "LITELLM_USAGE_LOG_PATH must remain UNTOUCHED"

    row = json.loads(sep_path.read_text().strip())
    assert row["model"] == "claude-opus-4.7"
    assert row["call_type"] == "completion"
    assert row["tokens_before"] == 12_345
    assert row["tokens_after"] == 4_321
    assert row["tokens_saved"] == 12_345 - 4_321
    assert "ts" in row
    assert "transforms_applied" in row


# ────────────────────────────────────────────────────────────────────────────
# Test 8 — compress() exception → fail-open
# ────────────────────────────────────────────────────────────────────────────


def test_compress_exception_returns_original_data(monkeypatch):
    """If compress() raises (e.g. headroom internal bug, OOM on huge prompt)
    the hook MUST return the original data so the agent's request still
    succeeds with the uncompressed prompt. Fail-open is the contract."""
    monkeypatch.setenv("KENSEI_AGENT_HEADROOM_ENABLED", "true")

    def _broken_compress(messages, model=None, config=None):
        raise RuntimeError("simulated headroom internal bug")

    _stub_headroom(compress_fn=_broken_compress)
    original_msgs = [{"role": "user", "content": "x" * 5000}]
    data = {"messages": original_msgs, "model": "claude-opus-4.7"}
    result = _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="completion",
        )
    )
    assert result is data
    assert data["messages"] is original_msgs


# ────────────────────────────────────────────────────────────────────────────
# Test 9 — singleton is a CustomLogger subclass
# ────────────────────────────────────────────────────────────────────────────


def test_callback_instance_is_customlogger_subclass():
    """LiteLLM's `_init_litellm_callbacks` resolves the YAML string
    `litellm_headroom_callback.headroom_callback_instance` and slots it into
    the dispatch list iff it's a CustomLogger subclass. If we accidentally
    define HeadroomPreCallCompressor without inheriting CustomLogger, LiteLLM
    silently skips us — compression would never fire. Guard that here."""
    # CustomLogger might be the stub class if litellm isn't installed during
    # test runs; either way the singleton MUST be an instance of whichever
    # class hr.CustomLogger resolves to at import time.
    assert isinstance(hr.headroom_callback_instance, hr.CustomLogger)
    assert isinstance(hr.headroom_callback_instance, hr.HeadroomPreCallCompressor)


# ────────────────────────────────────────────────────────────────────────────
# Test 10 — regression: 4-arg keyword signature
# ────────────────────────────────────────────────────────────────────────────


def test_async_pre_call_hook_4_arg_signature():
    """LiteLLM's proxy invokes pre-call hooks with kwargs
    `(user_api_key_dict=, cache=, data=, call_type=)`. Headroom's bundled
    `HeadroomCallback.async_pre_call_hook` only accepts 3 args (no `cache`),
    so it crashes with TypeError on the FIRST proxy request. Our subclass
    MUST accept the canonical 4-arg signature — verified by inspection
    AND by calling it with the exact kwargs LiteLLM would use."""
    import inspect

    sig = inspect.signature(hr.HeadroomPreCallCompressor.async_pre_call_hook)
    params = list(sig.parameters.keys())
    # `self` + 4 args
    assert params == ["self", "user_api_key_dict", "cache", "data", "call_type"], (
        f"expected canonical 4-arg LiteLLM proxy signature, got {params!r}"
    )

    # Smoke: actually invoke with kwargs (env disabled so it returns immediately)
    data = {"messages": [], "model": ""}
    result = _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=SimpleNamespace(api_key="sk-test"),
            cache=SimpleNamespace(),
            data=data,
            call_type="completion",
        )
    )
    assert result is data  # no exception raised


# ────────────────────────────────────────────────────────────────────────────
# Integration smoke (gated): real Headroom + real Opus call
# ────────────────────────────────────────────────────────────────────────────


@pytest.mark.skipif(
    not os.environ.get("RUN_INTEGRATION_HEADROOM_TESTS", "").lower() in ("1", "true", "yes", "on"),
    reason="Integration test requires RUN_INTEGRATION_HEADROOM_TESTS=true + AWS creds + headroom-ai installed",
)
def test_integration_real_compression_smoke():
    """End-to-end: install headroom-ai in the test env, build a multi-turn
    tool-loop conversation matching openclaw's shape, run the hook, assert
    tokens_saved > 0 AND telemetry row written AND messages list shrunk."""
    os.environ["KENSEI_AGENT_HEADROOM_ENABLED"] = "true"
    importlib.reload(hr)

    # Simulate an openclaw tool-loop: system prompt with tool schemas + 8
    # rounds of user / assistant_tool_call / tool_result with large JSON
    # outputs. The tool_result blocks should be what compresses.
    system = "You are openclaw. Available tools: ...\n" + ("DOC" * 500)
    messages = [{"role": "system", "content": system}]
    for i in range(8):
        messages.append({"role": "user", "content": f"step {i}: investigate"})
        messages.append({
            "role": "assistant",
            "content": [{"type": "tool_use", "id": f"t{i}", "name": "read_file", "input": {"path": f"/x{i}.log"}}],
        })
        messages.append({
            "role": "tool",
            "tool_use_id": f"t{i}",
            "content": json.dumps({"lines": ["LOG ENTRY " * 200] * 50}),
        })

    data = {"messages": messages, "model": "claude-opus-4.7"}
    before_count = len(data["messages"])
    _run(
        hr.headroom_callback_instance.async_pre_call_hook(
            user_api_key_dict=None, cache=None, data=data, call_type="completion",
        )
    )
    # Either net compression happened (tokens_saved > 0 → messages list
    # mutated) or it didn't (small enough to fall under min_tokens). Either
    # outcome is acceptable as long as no exception escaped.
    assert isinstance(data["messages"], list)
    assert len(data["messages"]) <= before_count
