"""Unit tests for src/utils/litellm_stream_callback.py (sidecar stream tap).

Invariants under test (docs/STREAMING_PLAN.md):
  R5  pass-the-original-object — every chunk yielded IS the received object
      (identity, not equality), on healthy, filtered, AND broken-writer paths
  R2  fail-open — a broken writer never stops or breaks the stream
  m0130 sink separation — writes ONLY to WCB_STREAM_LOG_PATH; a configured
      LITELLM_USAGE_LOG_PATH file is never touched
  filtering — preflight pings and message-less requests emit nothing
  shapes — anthropic /v1/messages event dicts AND OpenAI-style
      ModelResponseStream-like objects both map to correct rows
  closure — a request whose stream ends without message_stop gets one
      synthesized so the renderer can close it
"""
from __future__ import annotations

import asyncio
import importlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture()
def cb(monkeypatch, tmp_path):
    """Reload the callback module with WCB_STREAM_LOG_PATH pointed at tmp.
    The module captures _PATH at import time (it runs standalone inside the
    sidecar), so a reload per test is the honest way to re-point it —
    same technique as tests/test_litellm_headroom_callback.py."""
    feed = tmp_path / "stream.jsonl"
    usage = tmp_path / "usage.jsonl"
    monkeypatch.setenv("WCB_STREAM_LOG_PATH", str(feed))
    monkeypatch.setenv("LITELLM_USAGE_LOG_PATH", str(usage))
    import src.utils.litellm_stream_callback as mod
    mod = importlib.reload(mod)
    mod._TEST_FEED = feed        # convenience handles for the tests
    mod._TEST_USAGE = usage
    return mod


def _rows(feed: Path) -> list[dict]:
    if not feed.exists():
        return []
    return [json.loads(ln) for ln in feed.read_text().splitlines() if ln.strip()]


async def _drain(hook_gen):
    out = []
    async for c in hook_gen:
        out.append(c)
    return out


def _run_hook(mod, chunks, request_data):
    async def _source():
        for c in chunks:
            yield c

    tap = mod.StreamTap()
    return asyncio.run(
        _drain(
            tap.async_post_call_streaming_iterator_hook(
                user_api_key_dict=None,
                response=_source(),
                request_data=request_data,
            )
        )
    )


_AGENT_REQUEST = {
    "messages": [{"role": "user", "content": "do the task"}],
    "model": "claude-opus-4-6",
    "litellm_call_id": "call-123",
}


# ------------------------------------------------------------------------- R5

def test_yields_exact_original_objects_healthy_path(cb):
    chunks = [
        {"type": "message_start"},
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hel"}},
        {"type": "content_block_delta", "delta": {"type": "thinking_delta", "thinking": "hm"}},
        {"type": "message_stop"},
    ]
    out = _run_hook(cb, chunks, dict(_AGENT_REQUEST))
    assert len(out) == len(chunks)
    for got, sent in zip(out, chunks):
        assert got is sent  # identity, not equality (R5)


def test_yields_exact_original_objects_when_writer_broken(cb, monkeypatch):
    def _boom(row):
        raise OSError("disk gone")
    monkeypatch.setattr(cb, "_write_row", _boom)
    chunks = [
        {"type": "message_start"},
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "x"}},
        {"type": "message_stop"},
    ]
    out = _run_hook(cb, chunks, dict(_AGENT_REQUEST))  # must not raise
    assert [id(c) for c in out] == [id(c) for c in chunks]


def test_opaque_chunks_flow_untouched(cb):
    class Opaque:
        pass
    chunks = [Opaque(), b"garbage-bytes", "plain string", 42]
    out = _run_hook(cb, chunks, dict(_AGENT_REQUEST))
    assert [id(c) for c in out] == [id(c) for c in chunks]


# ---------------------------------------------------------------- row content

def test_anthropic_events_map_to_rows(cb):
    chunks = [
        {"type": "message_start"},
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hello"}},
        {"type": "content_block_delta", "delta": {"type": "thinking_delta", "thinking": "let me"}},
        {"type": "message_stop"},
    ]
    _run_hook(cb, chunks, dict(_AGENT_REQUEST))
    rows = _rows(cb._TEST_FEED)
    events = [(r["event"], r["kind"], r["delta"]) for r in rows]
    assert events == [
        ("message_start", "status", ""),  # exactly ONE — chunk-derived duplicate suppressed
        ("delta", "text", "Hello"),
        ("delta", "thinking", "let me"),
        ("message_stop", "status", ""),
    ]
    assert all(r["source"] == "agent" for r in rows)
    assert all(r["request_id"] == "call-123" for r in rows)
    assert [r["seq"] for r in rows] == list(range(len(rows)))


def test_openai_style_chunks_map_to_rows(cb):
    class Chunk:
        def __init__(self, content=None, reasoning=None):
            self._d = {"choices": [{"delta": {"content": content,
                                              "reasoning_content": reasoning}}]}

        def model_dump(self):
            return self._d

    chunks = [Chunk(content="Hi"), Chunk(reasoning="think"), Chunk()]
    _run_hook(cb, chunks, dict(_AGENT_REQUEST))
    rows = _rows(cb._TEST_FEED)
    deltas = [(r["kind"], r["delta"]) for r in rows if r["event"] == "delta"]
    assert deltas == [("text", "Hi"), ("thinking", "think")]


def test_message_stop_synthesized_when_stream_ends_without_one(cb):
    chunks = [
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "partial"}},
    ]
    _run_hook(cb, chunks, dict(_AGENT_REQUEST))
    rows = _rows(cb._TEST_FEED)
    assert rows[-1]["event"] == "message_stop"


# ------------------------------------------------------------------ filtering

def test_preflight_ping_emits_nothing(cb):
    ping = {
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "model": "claude-opus-4.7",
    }
    chunks = [{"type": "content_block_delta", "delta": {"type": "text_delta", "text": "pong"}}]
    out = _run_hook(cb, chunks, ping)
    assert len(out) == 1  # chunk still flows
    assert _rows(cb._TEST_FEED) == []


def test_messageless_request_emits_nothing(cb):
    chunks = [{"type": "content_block_delta", "delta": {"type": "text_delta", "text": "x"}}]
    _run_hook(cb, chunks, {"model": "whisper-1"})
    _run_hook(cb, chunks, None)
    assert _rows(cb._TEST_FEED) == []


# ------------------------------------------------------------ sink separation

def test_never_touches_usage_log(cb):
    chunks = [
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hi"}},
        {"type": "message_stop"},
    ]
    _run_hook(cb, chunks, dict(_AGENT_REQUEST))
    assert _rows(cb._TEST_FEED)  # stream feed written
    assert not cb._TEST_USAGE.exists()  # usage sink NEVER touched (m0130)
