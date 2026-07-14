"""Unit tests for src/utils/stream_events.py (host-side stream emitter).

Invariants under test (docs/STREAMING_PLAN.md):
  R2  fail-open — emit() never raises, self-disables after repeated failures
  R6  batch-scoped default-off gate — unset env ⇒ no-op emitter, zero writes
  m0130 sink separation — the emitter only ever writes WCB_STREAM_LOG_PATH
  schema — rows carry the documented keys; seq is monotonic per request_id
  size cap — feed stops growing past WCB_STREAM_MAX_BYTES
  R1 (static) — the graded pipeline has no dependency on the stream feed
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import stream_events  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("WCB_STREAM", raising=False)
    monkeypatch.delenv("WCB_STREAM_LOG_PATH", raising=False)
    monkeypatch.delenv("WCB_STREAM_MAX_BYTES", raising=False)
    stream_events.reset_emitter_for_tests()
    yield
    stream_events.reset_emitter_for_tests()


def _enable(monkeypatch, tmp_path: Path) -> Path:
    feed = tmp_path / "stream.jsonl"
    monkeypatch.setenv("WCB_STREAM", "1")
    monkeypatch.setenv("WCB_STREAM_LOG_PATH", str(feed))
    stream_events.reset_emitter_for_tests()
    return feed


def _rows(feed: Path) -> list[dict]:
    if not feed.exists():
        return []
    return [json.loads(ln) for ln in feed.read_text().splitlines() if ln.strip()]


# ---------------------------------------------------------------- default off

def test_disabled_by_default_no_writes(tmp_path):
    feed = tmp_path / "stream.jsonl"
    stream_events.emit("agent", "delta", "r1", delta="hello")
    assert not feed.exists()
    assert isinstance(stream_events.get_emitter(), stream_events._NullEmitter)


def test_gate_requires_both_env_vars(monkeypatch, tmp_path):
    monkeypatch.setenv("WCB_STREAM", "1")  # path missing
    stream_events.reset_emitter_for_tests()
    assert isinstance(stream_events.get_emitter(), stream_events._NullEmitter)
    monkeypatch.delenv("WCB_STREAM")
    monkeypatch.setenv("WCB_STREAM_LOG_PATH", str(tmp_path / "s.jsonl"))  # gate missing
    stream_events.reset_emitter_for_tests()
    assert isinstance(stream_events.get_emitter(), stream_events._NullEmitter)


# -------------------------------------------------------------------- schema

def test_rows_carry_schema_and_monotonic_seq(monkeypatch, tmp_path):
    feed = _enable(monkeypatch, tmp_path)
    stream_events.emit("judge:sonnet", "message_start", "req-a", kind="status", model="arn:x")
    stream_events.emit("judge:sonnet", "delta", "req-a", kind="text", delta="Yes")
    stream_events.emit("agent", "delta", "req-b", kind="thinking", delta="hmm")
    stream_events.emit("judge:sonnet", "message_stop", "req-a", kind="status")
    rows = _rows(feed)
    assert len(rows) == 4
    for row in rows:
        assert set(row) == {"ts", "seq", "source", "request_id", "model", "kind", "event", "delta"}
    a_rows = [r for r in rows if r["request_id"] == "req-a"]
    assert [r["seq"] for r in a_rows] == [0, 1, 2]
    b_rows = [r for r in rows if r["request_id"] == "req-b"]
    assert [r["seq"] for r in b_rows] == [0]
    assert a_rows[1]["delta"] == "Yes" and a_rows[1]["kind"] == "text"
    assert b_rows[0]["kind"] == "thinking"


# ----------------------------------------------------------------- fail-open

def test_unwritable_path_never_raises_and_self_disables(monkeypatch, tmp_path):
    bad_dir = tmp_path / "nope"  # parent does not exist -> open() fails
    monkeypatch.setenv("WCB_STREAM", "1")
    monkeypatch.setenv("WCB_STREAM_LOG_PATH", str(bad_dir / "stream.jsonl"))
    stream_events.reset_emitter_for_tests()
    for _ in range(5):
        stream_events.emit("agent", "delta", "r1", delta="x")  # must not raise
    assert stream_events.get_emitter().disabled


def test_emit_never_raises_even_if_get_emitter_breaks(monkeypatch):
    monkeypatch.setattr(stream_events, "get_emitter", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    stream_events.emit("agent", "delta", "r1", delta="x")  # must not raise


# ------------------------------------------------------------------ size cap

def test_size_cap_stops_writes(monkeypatch, tmp_path):
    feed = _enable(monkeypatch, tmp_path)
    monkeypatch.setenv("WCB_STREAM_MAX_BYTES", "512")
    stream_events.reset_emitter_for_tests()
    for i in range(400):
        stream_events.emit("agent", "delta", "r1", delta="tok" * 10)
    assert stream_events.get_emitter().disabled  # capped counts as disabled
    size = feed.stat().st_size
    # The cap is checked every _SIZE_CHECK_EVERY writes, so allow one window
    # of overshoot but no unbounded growth.
    per_row = 150  # generous upper bound per row in bytes
    assert size < 512 + stream_events._SIZE_CHECK_EVERY * per_row


# ------------------------------------------------- R1 static invariant checks

def test_graded_pipeline_never_reads_the_stream_feed():
    """R1: grading + bundling must have zero dependency on the stream feed.
    Source-level assertion so a future edit that wires them together fails CI.
    """
    grading_src = (REPO_ROOT / "src" / "utils" / "grading.py").read_text(encoding="utf-8")
    assert "stream_renderer" not in grading_src
    # grading may EMIT (write-only, fail-open) but must never read the feed.
    assert "WCB_STREAM_LOG_PATH" not in grading_src
    bundler_src = (REPO_ROOT / "script" / "repackage_to_bundle.py").read_text(encoding="utf-8")
    assert "stream.jsonl" not in bundler_src
    assert "stream_events" not in bundler_src
    executor_src = (REPO_ROOT / "src" / "utils" / "test_executor.py").read_text(encoding="utf-8")
    assert "stream_events" not in executor_src and "stream_renderer" not in executor_src


def test_judge_emits_do_not_change_verdict_parsing(monkeypatch, tmp_path):
    """R4 sanity: _parse_verdict_text output is independent of the emitter
    being live (accumulate-then-parse untouched)."""
    from src.utils import grading
    sample = (
        "<judgment>\n"
        "1. Criterion one text [[RATIONALE: fine]] [[SATISFIED: Yes]]\n"
        "2. Criterion two text [[RATIONALE: nope]] [[SATISFIED: No]]\n"
        "</judgment>"
    )
    baseline = grading._parse_verdict_text(sample, 2)
    _enable(monkeypatch, tmp_path)
    with_stream = grading._parse_verdict_text(sample, 2)
    assert baseline == with_stream
    assert [v["satisfied"] for v in with_stream] == [True, False]
