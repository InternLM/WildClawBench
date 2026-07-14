"""Fail-open emitter for the live-stream observability feed (stream.jsonl).

This module is the HOST-side half of the streaming feature described in
docs/STREAMING_PLAN.md. It is used by grading.py (judge deltas), the testgen
generator (status heartbeats), and stream_renderer.py (reader). The sidecar
container has its own standalone writer (litellm_stream_callback.py) that
appends to the same file through a bind mount — both sides emit single-line
O_APPEND writes so records never interleave intra-line.

Event schema (one JSON object per line, append-only):

    {
      "ts": 1783075200.123,          # unix seconds
      "seq": 42,                      # monotonic per request_id
      "source": "agent" | "judge:sonnet" | "judge:kimi" | "judge:glm"
                | "judge:openai" | "testgen",
      "request_id": "<opaque id>",
      "model": "<model or ARN label>",
      "kind": "text" | "thinking" | "status",
      "event": "message_start" | "delta" | "message_stop" | "error" | "status",
      "delta": "<text fragment or status message>"
    }

Invariants (docs/STREAMING_PLAN.md R1/R2/R7):
  * OBSERVABILITY ONLY. Nothing in the grading/scoring/bundling chain may
    read this file or wait on this module. Do not add such a dependency.
  * FAIL-OPEN. emit() never raises. After ``_MAX_ERRORS`` consecutive write
    failures the emitter disables itself for the rest of the process.
  * SINK SEPARATION (user m0130 lineage): this module writes ONLY to
    WCB_STREAM_LOG_PATH — never to usage.jsonl / usage_oauth.jsonl /
    headroom.jsonl, and their schemas never merge.
  * Enabled ONLY when both WCB_STREAM is truthy and WCB_STREAM_LOG_PATH is a
    non-empty path. Otherwise every emit() is a cheap no-op — the default,
    so a batch without --stream behaves byte-identically to today.
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Optional

_TRUTHY = ("1", "true", "yes", "on")
_MAX_ERRORS = 3
_DEFAULT_MAX_BYTES = 64 * 1024 * 1024  # 64 MiB per feed file
_SIZE_CHECK_EVERY = 32  # stat() the file every N writes, not every write

VALID_EVENTS = ("message_start", "delta", "message_stop", "error", "status")
VALID_KINDS = ("text", "thinking", "status")


def _enabled_from_env() -> bool:
    return (
        os.environ.get("WCB_STREAM", "").strip().lower() in _TRUTHY
        and bool(os.environ.get("WCB_STREAM_LOG_PATH", "").strip())
    )


def _max_bytes_from_env() -> int:
    raw = os.environ.get("WCB_STREAM_MAX_BYTES", "").strip()
    try:
        n = int(raw) if raw else _DEFAULT_MAX_BYTES
    except ValueError:
        return _DEFAULT_MAX_BYTES
    return n if n > 0 else _DEFAULT_MAX_BYTES


class StreamEmitter:
    """Append-only JSONL writer. Every public method is exception-proof."""

    def __init__(self, path: str, max_bytes: int = _DEFAULT_MAX_BYTES) -> None:
        self._path = path
        self._max_bytes = max_bytes
        self._lock = threading.Lock()
        self._seq: dict[str, int] = {}
        self._errors = 0
        self._writes = 0
        self._capped = False
        self._disabled = False

    @property
    def disabled(self) -> bool:
        return self._disabled or self._capped

    def emit(
        self,
        source: str,
        event: str,
        request_id: str,
        *,
        kind: str = "text",
        delta: str = "",
        model: str = "",
    ) -> None:
        if self._disabled or self._capped:
            return
        try:
            with self._lock:
                seq = self._seq.get(request_id, -1) + 1
                self._seq[request_id] = seq
                row = {
                    "ts": round(time.time(), 3),
                    "seq": seq,
                    "source": source,
                    "request_id": request_id,
                    "model": model,
                    "kind": kind,
                    "event": event,
                    "delta": delta,
                }
                line = json.dumps(row, ensure_ascii=False, default=str) + "\n"
                self._writes += 1
                if self._writes % _SIZE_CHECK_EVERY == 0:
                    try:
                        if os.path.getsize(self._path) > self._max_bytes:
                            self._capped = True
                            import sys
                            sys.stderr.write(
                                f"[stream_events] WARN feed exceeded "
                                f"{self._max_bytes} bytes; further events dropped "
                                f"({self._path})\n"
                            )
                            return
                    except OSError:
                        pass
                # O_APPEND single-line write: atomic enough for the renderer,
                # which skips any torn/unparseable line rather than erroring.
                with open(self._path, "a", encoding="utf-8") as fh:
                    fh.write(line)
            self._errors = 0
        except Exception:
            self._errors += 1
            if self._errors >= _MAX_ERRORS:
                self._disabled = True
                try:
                    import sys
                    sys.stderr.write(
                        f"[stream_events] WARN emitter disabled after "
                        f"{_MAX_ERRORS} consecutive write failures ({self._path})\n"
                    )
                except Exception:
                    pass


class _NullEmitter:
    """No-op stand-in used whenever streaming is off (the default)."""

    disabled = True

    def emit(self, *args, **kwargs) -> None:  # noqa: D102 - intentionally inert
        return


_singleton: Optional[object] = None
_singleton_lock = threading.Lock()


def get_emitter():
    """Return the process-wide emitter (or a no-op when streaming is off).

    The decision is latched on first call: WCB_STREAM / WCB_STREAM_LOG_PATH
    are batch-scoped (docs/STREAMING_PLAN.md R6) and set by
    eval/run_batch.py::_setup_litellm_and_mocks before any emitter user runs.
    """
    global _singleton
    if _singleton is not None:
        return _singleton
    with _singleton_lock:
        if _singleton is None:
            if _enabled_from_env():
                _singleton = StreamEmitter(
                    os.environ["WCB_STREAM_LOG_PATH"].strip(),
                    max_bytes=_max_bytes_from_env(),
                )
            else:
                _singleton = _NullEmitter()
    return _singleton


def reset_emitter_for_tests() -> None:
    """Drop the latched singleton so tests can re-evaluate the env gate."""
    global _singleton
    with _singleton_lock:
        _singleton = None


def emit(
    source: str,
    event: str,
    request_id: str,
    *,
    kind: str = "text",
    delta: str = "",
    model: str = "",
) -> None:
    """Module-level convenience wrapper. Never raises; no-op when disabled."""
    try:
        get_emitter().emit(
            source, event, request_id, kind=kind, delta=delta, model=model
        )
    except Exception:
        # Belt over braces: even a bug in get_emitter() must not surface
        # into a caller (judge loops, testgen). Observability never breaks
        # the pipeline (R2).
        pass
