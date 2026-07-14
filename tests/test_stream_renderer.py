"""Unit tests for src/utils/stream_renderer.py (display-only consumer).

Focus: lifecycle safety (R3 bounded stop; gate default-off) and the
line-buffered judge rendering / torn-line tolerance. Full visual behavior is
covered by the manual E2E matrix in docs/STREAMING_PLAN.md §8.2.
"""
from __future__ import annotations

import io
import json
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.stream_renderer import StreamRenderer, start_renderer  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("WCB_STREAM", raising=False)
    monkeypatch.delenv("WCB_STREAM_THINKING", raising=False)
    yield


def test_start_renderer_gate_default_off(tmp_path):
    assert start_renderer(tmp_path / "s.jsonl", tmp_path / "a.log") is None


def test_start_renderer_never_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("WCB_STREAM", "1")
    r = start_renderer(tmp_path / "missing" / "s.jsonl", None, run_label="t/run_1")
    try:
        assert r is not None
    finally:
        if r is not None:
            r.stop(timeout=1.0)


def test_stop_is_bounded_and_idempotent(monkeypatch, tmp_path):
    monkeypatch.setenv("WCB_STREAM", "1")
    feed = tmp_path / "stream.jsonl"
    feed.touch()
    r = start_renderer(feed, tmp_path / "agent.log")
    assert r is not None
    t0 = time.time()
    r.stop(timeout=2.0)
    assert time.time() - t0 < 3.0  # bounded join (R3)
    assert not r.is_alive()
    r.stop(timeout=1.0)  # second stop: no raise


def _fake_out_renderer() -> tuple[StreamRenderer, io.StringIO]:
    r = StreamRenderer(None, None)
    out = io.StringIO()
    r._out = out
    r._interactive = True
    r._color = False
    return r, out


def test_judge_rendering_is_line_buffered():
    r, out = _fake_out_renderer()
    r._render_event({"source": "judge:kimi", "event": "delta", "kind": "text",
                     "delta": "1. Criterion", "request_id": "j1"})
    assert "Criterion" not in out.getvalue()  # incomplete line held back
    r._render_event({"source": "judge:kimi", "event": "delta", "kind": "text",
                     "delta": " [[SATISFIED: Yes]]\n2. Next", "request_id": "j1"})
    assert "[judge:kimi] 1. Criterion [[SATISFIED: Yes]]" in out.getvalue()
    assert "2. Next" not in out.getvalue()
    r._render_event({"source": "judge:kimi", "event": "message_stop", "kind": "status",
                     "delta": "", "request_id": "j1"})
    assert "2. Next" in out.getvalue()  # flushed on stop


def test_agent_main_session_and_subagent_split():
    r, out = _fake_out_renderer()
    r._render_event({"source": "agent", "event": "message_start", "kind": "status",
                     "delta": "", "request_id": "main-1"})
    r._render_event({"source": "agent", "event": "message_start", "kind": "status",
                     "delta": "", "request_id": "sub-2"})
    r._render_event({"source": "agent", "event": "delta", "kind": "text",
                     "delta": "main tokens", "request_id": "main-1"})
    r._render_event({"source": "agent", "event": "delta", "kind": "text",
                     "delta": "SUB TOKENS", "request_id": "sub-2"})
    v = out.getvalue()
    assert "main tokens" in v
    assert "SUB TOKENS" not in v          # sub-agent deltas: status lines only (D5)
    assert "[sub-agent sub-2" in v


def test_thinking_hidden_when_disabled(monkeypatch):
    monkeypatch.setenv("WCB_STREAM_THINKING", "0")
    r, out = _fake_out_renderer()
    r._render_event({"source": "agent", "event": "message_start", "kind": "status",
                     "delta": "", "request_id": "m"})
    r._render_event({"source": "agent", "event": "delta", "kind": "thinking",
                     "delta": "secret reasoning", "request_id": "m"})
    assert "secret reasoning" not in out.getvalue()


def test_token_mode_skips_torn_lines(monkeypatch, tmp_path):
    """A torn/partial JSONL line must be skipped, never crash the thread."""
    monkeypatch.setenv("WCB_STREAM", "1")
    feed = tmp_path / "stream.jsonl"
    feed.write_text("")  # exists, renderer starts at EOF
    r = start_renderer(feed, None)
    assert r is not None
    try:
        with open(feed, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({
                "source": "judge:glm", "event": "delta", "kind": "text",
                "delta": "ok\n", "request_id": "j",
            }) + "\n")
            fh.write('{"source": "agent", "event": "de')  # torn line, no newline
        time.sleep(0.6)  # a couple of poll cycles
        assert r.is_alive()  # torn line did not kill the thread
    finally:
        r.stop(timeout=2.0)
        assert not r.is_alive()


def test_renderer_bus_mode_under_textual_dashboard(monkeypatch, tmp_path):
    """--tui + --stream single-terminal contract: under the dashboard the
    renderer runs in BUS mode (publishes EV_TOKEN for the Live Stream pane,
    never opens a tty handle); without the dashboard it renders to the tty.
    The stream FEED is unaffected either way — taps write it regardless."""
    monkeypatch.setenv("WCB_STREAM", "1")
    from src.utils.ui import lifecycle

    lifecycle.set_dashboard_active(True)
    try:
        r = start_renderer(tmp_path / "s.jsonl", tmp_path / "a.log")
        assert r is not None and r._mode == "bus"  # single-terminal contract
        assert r._out is None  # bus mode never opens a terminal handle
        r.stop(timeout=2.0)
        assert not r.is_alive()
    finally:
        lifecycle.set_dashboard_active(False)

    r = start_renderer(tmp_path / "s.jsonl", tmp_path / "a.log")
    try:
        assert r is not None and r._mode == "tty"  # dashboard off -> tty render
    finally:
        if r is not None:
            r.stop(timeout=1.0)


def _bus_renderer(monkeypatch):
    """Renderer in bus mode with a collector replacing the real bus publish."""
    import src.utils.stream_renderer as sr
    events = []
    monkeypatch.setattr(sr, "_publish_token",
                        lambda style, text: events.append((style, text)))
    r = StreamRenderer(None, None, mode="bus")
    r._interactive = True  # what run() sets in bus mode
    return r, events


def test_bus_mode_agent_chunks_flush_on_newline_and_size(monkeypatch):
    r, events = _bus_renderer(monkeypatch)
    r._render_event({"source": "agent", "event": "message_start", "kind": "status",
                     "delta": "", "request_id": "m"})
    r._render_event({"source": "agent", "event": "delta", "kind": "text",
                     "delta": "first line\nsecond", "request_id": "m"})
    assert ("text", "first line") in events           # newline flush
    assert all(t != "second" for _, t in events)      # partial held back
    r._render_event({"source": "agent", "event": "delta", "kind": "text",
                     "delta": " word" * 30, "request_id": "m"})
    assert any(s == "text" and len(t) >= 20 for s, t in events)  # size flush
    assert all(len(t) <= 80 for _, t in events)       # never exceeds chunk cap
    r._render_event({"source": "agent", "event": "message_stop", "kind": "status",
                     "delta": "", "request_id": "m"})
    joined = "first line second" + " word" * 30
    reassembled = " ".join(t for s, t in events if s == "text")
    assert reassembled.split() == joined.split()      # nothing lost, order kept


def test_bus_mode_thinking_style_and_gate(monkeypatch):
    r, events = _bus_renderer(monkeypatch)
    r._render_event({"source": "agent", "event": "message_start", "kind": "status",
                     "delta": "", "request_id": "m"})
    r._render_event({"source": "agent", "event": "delta", "kind": "thinking",
                     "delta": "pondering...\n", "request_id": "m"})
    assert ("thinking", "pondering...") in events
    monkeypatch.setenv("WCB_STREAM_THINKING", "0")
    r._render_event({"source": "agent", "event": "delta", "kind": "thinking",
                     "delta": "hidden\n", "request_id": "m"})
    assert all("hidden" not in t for _, t in events)  # gate respected in bus mode


def test_bus_mode_judge_lines_and_subagent_status(monkeypatch):
    r, events = _bus_renderer(monkeypatch)
    r._render_event({"source": "judge:kimi", "event": "delta", "kind": "text",
                     "delta": "1. Yes\n", "request_id": "j"})
    assert ("judge", "[judge:kimi] 1. Yes") in events
    r._render_event({"source": "agent", "event": "message_start", "kind": "status",
                     "delta": "", "request_id": "main"})
    r._render_event({"source": "agent", "event": "message_start", "kind": "status",
                     "delta": "", "request_id": "sub42"})
    assert any(s == "status" and "sub-agent" in t for s, t in events)


def test_bus_mode_fail_open_on_publish_error(monkeypatch):
    import src.utils.stream_renderer as sr

    def _boom(style, text):
        raise RuntimeError("bus gone")
    monkeypatch.setattr(sr, "_publish_token", _boom)
    r = StreamRenderer(None, None, mode="bus")
    r._interactive = True
    r._render_event({"source": "judge:glm", "event": "delta", "kind": "text",
                     "delta": "verdict\n", "request_id": "j"})  # must not raise
    assert r._bus_dead  # latched; subsequent sends are no-ops


def test_waiting_state_narration_until_first_agent_token(monkeypatch, tmp_path):
    """The 2026-07-13 matt_garcia bug, encoded: agent.log narration renders
    while the token feed is silent; the FIRST agent feed row switches the
    pane to token rendering permanently and later narration is dropped.
    Non-agent feed rows must not end the narration phase."""
    import json
    import time as _time
    import src.utils.stream_renderer as sr

    events = []
    monkeypatch.setattr(sr, "_publish_token",
                        lambda style, text: events.append((style, text)))
    feed = tmp_path / "stream.jsonl"
    feed.touch()
    agent_log = tmp_path / "agent.log"
    r = StreamRenderer(feed, agent_log, mode="bus")
    r.start()
    try:
        # Phase 1: feed silent -> narration renders
        agent_log.write_text("setting up workspace\n")
        _time.sleep(0.6)
        assert ("text", "[agent] setting up workspace") in events

        # Phase 2: a NON-agent feed row does not end narration
        with open(feed, "a") as fh:
            fh.write(json.dumps({"source": "testgen", "event": "status",
                                 "kind": "status", "delta": "attempt 1/3",
                                 "request_id": "tg"}) + "\n")
        _time.sleep(0.6)
        with open(agent_log, "a") as fh:
            fh.write("still narrating\n")
        _time.sleep(0.6)
        assert ("text", "[agent] still narrating") in events

        # Phase 3: first AGENT feed row -> tokens live, narration stops
        with open(feed, "a") as fh:
            fh.write(json.dumps({"source": "agent", "event": "message_start",
                                 "kind": "status", "delta": "",
                                 "request_id": "m1"}) + "\n")
            fh.write(json.dumps({"source": "agent", "event": "delta",
                                 "kind": "text", "delta": "streamed tokens\n",
                                 "request_id": "m1"}) + "\n")
        _time.sleep(0.6)
        assert any(s == "text" and t == "streamed tokens" for s, t in events)
        before = len(events)
        with open(agent_log, "a") as fh:
            fh.write("late narration must be dropped\n")
        _time.sleep(0.6)
        assert all("late narration" not in t for _, t in events[before:])
    finally:
        r.stop(timeout=2.0)
        assert not r.is_alive()
