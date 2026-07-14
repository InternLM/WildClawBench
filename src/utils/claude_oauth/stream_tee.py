"""Real-time SSE tee for the cc-bridge — live token feed on the OAuth path.

WHY THIS EXISTS (docs/STREAMING_PLAN.md §1.5): with buffer-and-retry ON
(default), the bridge replays the response to the client as an end-of-turn
burst, so the LiteLLM sidecar's stream hook cannot see tokens in real time
on this branch. The only place chunks exist live is INSIDE the bridge —
this module observes them there and appends display events to the shared
stream feed (bind-mounted host file, same JSONL schema as
src/utils/stream_events.py).

HARD RULES:
  * OBSERVE-ONLY. The tee never modifies, drops, delays, or reorders the
    bytes the bridge buffers/forwards (R5 — callers pass the chunk in and
    keep using their own reference; nothing is returned).
  * FAIL-OPEN (R2). Every public method swallows every exception and
    self-disables; a broken tee can never affect a client response.
  * INERT unless ``WCB_CC_STREAM_LOG_PATH`` is set (start_bridge sets it
    only when the batch runs with --stream; R6 batch-scoped gate).
  * Sink separation (m0130): writes ONLY to WCB_CC_STREAM_LOG_PATH.

This file ships inside the bridge image automatically (docker/cc-bridge
Dockerfile does ``COPY src/utils/claude_oauth /app/claude_oauth``).
"""
from __future__ import annotations

import json
import os
import threading
import time
import uuid
from typing import Optional

_MAX_BYTES_DEFAULT = 64 * 1024 * 1024
_SIZE_CHECK_EVERY = 32

_LOCK = threading.Lock()
_writes = 0
_capped = False


def _feed_path() -> str:
    return os.environ.get("WCB_CC_STREAM_LOG_PATH", "").strip()


def _max_bytes() -> int:
    raw = os.environ.get("WCB_STREAM_MAX_BYTES", "").strip()
    try:
        n = int(raw) if raw else _MAX_BYTES_DEFAULT
    except ValueError:
        return _MAX_BYTES_DEFAULT
    return n if n > 0 else _MAX_BYTES_DEFAULT


def _write_row(row: dict) -> None:
    """Append one event line; raises to the caller (which fail-opens)."""
    global _writes, _capped
    path = _feed_path()
    if not path or _capped:
        return
    line = json.dumps(row, ensure_ascii=False, default=str) + "\n"
    with _LOCK:
        _writes += 1
        if _writes % _SIZE_CHECK_EVERY == 0:
            try:
                if os.path.getsize(path) > _max_bytes():
                    _capped = True
                    return
            except OSError:
                pass
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line)


class StreamTee:
    """Per-request SSE observer. One instance per inbound bridge request.

    Lifecycle used by bridge.py:
        tee = StreamTee()
        tee.attempt_started()      # per upstream attempt (re-emits after retry)
        tee.feed(chunk)            # every upstream chunk, verbatim bytes
        tee.retrying(attempt_no)   # buffered mode: before a re-issue
        tee.finish()               # terminal: complete response captured
        tee.error(msg)             # terminal: request failed
    """

    def __init__(self, source: str = "agent", model: str = "") -> None:
        self._enabled = bool(_feed_path())
        self._source = source
        self._model = model
        self._req_id = uuid.uuid4().hex[:16]
        self._seq = 0
        self._carry = b""
        self._started = False
        self._stopped = False

    # ------------------------------------------------------------- internals

    def _emit(self, event: str, kind: str = "status", delta: str = "") -> None:
        _write_row({
            "ts": round(time.time(), 3),
            "seq": self._seq,
            "source": self._source,
            "request_id": self._req_id,
            "model": self._model,
            "kind": kind,
            "event": event,
            "delta": delta,
        })
        self._seq += 1

    def _handle_sse_data(self, payload: bytes) -> None:
        obj = json.loads(payload)
        if not isinstance(obj, dict):
            return
        t = obj.get("type")
        if t == "content_block_delta":
            d = obj.get("delta") or {}
            if d.get("type") == "text_delta" and isinstance(d.get("text"), str):
                self._emit("delta", kind="text", delta=d["text"])
            elif d.get("type") == "thinking_delta" and isinstance(d.get("thinking"), str):
                self._emit("delta", kind="thinking", delta=d["thinking"])
        elif t == "message_stop":
            if not self._stopped:
                self._stopped = True
                self._emit("message_stop")
        elif t == "error":
            # An SSE error frame is terminal for the display request: latch
            # _stopped so a later finish() can't append a message_stop after
            # the error (the renderer treats error as request-closing).
            err = obj.get("error") or {}
            if not self._stopped:
                self._stopped = True
                self._emit("error", delta=str(err.get("message") or "stream error")[:200])

    # ------------------------------------------------------------ public API

    def attempt_started(self) -> None:
        """Mark the start of an upstream attempt (idempotent per attempt)."""
        if not self._enabled:
            return
        try:
            if not self._started:
                self._started = True
                self._emit("message_start")
        except Exception:
            self._enabled = False

    def feed(self, chunk: bytes) -> None:
        """Observe one upstream chunk. Incremental SSE frame parsing with a
        carry buffer, so a ``data:`` line split across chunks still parses on
        the frame boundary (same rolling technique the bridge itself uses for
        its message_stop detection)."""
        if not self._enabled:
            return
        try:
            if not isinstance(chunk, (bytes, bytearray)):
                return
            self._carry += bytes(chunk)
            # SSE frames are separated by a blank line. Process every
            # complete frame; keep the trailing partial as the new carry.
            while b"\n\n" in self._carry:
                frame, self._carry = self._carry.split(b"\n\n", 1)
                for raw_line in frame.split(b"\n"):
                    raw_line = raw_line.strip()
                    if raw_line.startswith(b"data:"):
                        payload = raw_line[len(b"data:"):].strip()
                        if payload and payload != b"[DONE]":
                            try:
                                self._handle_sse_data(payload)
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                continue
            # Defensive cap: a pathological no-frame stream must not grow the
            # carry unboundedly. 1 MiB is far above any real SSE frame.
            if len(self._carry) > 1024 * 1024:
                self._carry = self._carry[-65536:]
        except Exception:
            self._enabled = False

    def retrying(self, attempt: int) -> None:
        """Buffered mode re-issue: the partial turn the feed saw is void.
        Emit an error marker (the renderer closes/replaces the partial turn)
        and reset so the next attempt re-emits message_start."""
        if not self._enabled:
            return
        try:
            self._emit("error", delta=f"upstream drop — retrying (attempt {attempt})")
            self._carry = b""
            self._started = False
            self._stopped = False
        except Exception:
            self._enabled = False

    def finish(self) -> None:
        """Terminal success: ensure the request is closed in the feed."""
        if not self._enabled:
            return
        try:
            if self._started and not self._stopped:
                self._stopped = True
                self._emit("message_stop")
        except Exception:
            self._enabled = False

    def error(self, message: str) -> None:
        """Terminal failure: close the request with an error event."""
        if not self._enabled:
            return
        try:
            if not self._stopped:
                self._stopped = True
                self._emit("error", delta=str(message)[:200])
        except Exception:
            self._enabled = False
