"""LiteLLM proxy streaming tap — live token feed for the operator terminal.

Mounted read-only into the sidecar at /app/litellm_stream_callback.py and
registered via the LiteLLM YAML:

    litellm_settings:
      callbacks: [..., "litellm_stream_callback.stream_handler_instance"]

It implements ONLY ``async_post_call_streaming_iterator_hook``, which the
proxy applies to every streamed response — including the /v1/messages
(anthropic-messages) route openclaw uses (verified: proxy
anthropic_endpoints/endpoints.py -> base_process_llm_request ->
async_sse_data_generator -> async_streaming_data_generator wraps the response
in this hook; see docs/STREAMING_PLAN.md §1.3).

HARD RULES (docs/STREAMING_PLAN.md R2/R5 + user m0130 lineage):
  * R5 pass-the-original-object: this hook yields the EXACT chunk object it
    received, unconditionally, on every code path. Delta extraction only
    READS the chunk. Never construct/modify/skip a forwarded chunk — a
    silent-mutation bug here would degrade agent turns invisibly.
  * R2 fail-open: any exception in extraction/writing disables the tap for
    the remainder of that request and the chunk still flows. The ``yield``
    itself is never inside our try/except.
  * Sink separation: writes ONLY to WCB_STREAM_LOG_PATH (default
    /var/litellm_stream/stream.jsonl). NEVER to LITELLM_USAGE_LOG_PATH /
    usage_oauth.jsonl / the headroom JSONL. Schemas never merge.

Event schema matches src/utils/stream_events.py (this file is standalone —
the sidecar container only has this module, so the schema is duplicated by
design, same as the usage/headroom callbacks are standalone).
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
import uuid
from typing import Any, AsyncGenerator, Optional

try:
    from litellm.integrations.custom_logger import CustomLogger  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - litellm only present inside the sidecar
    class CustomLogger:  # type: ignore[no-redef]
        pass


_PATH = os.environ.get("WCB_STREAM_LOG_PATH", "/var/litellm_stream/stream.jsonl")
_LOCK = threading.Lock()
_MAX_BYTES_DEFAULT = 64 * 1024 * 1024
_SIZE_CHECK_EVERY = 32

_writes = 0
_capped = False


def _max_bytes() -> int:
    raw = os.environ.get("WCB_STREAM_MAX_BYTES", "").strip()
    try:
        n = int(raw) if raw else _MAX_BYTES_DEFAULT
    except ValueError:
        return _MAX_BYTES_DEFAULT
    return n if n > 0 else _MAX_BYTES_DEFAULT


def _write_row(row: dict) -> None:
    """Append one event line. Raises to the caller (which fail-opens)."""
    global _writes, _capped
    if _capped:
        return
    line = json.dumps(row, ensure_ascii=False, default=str) + "\n"
    with _LOCK:
        _writes += 1
        if _writes % _SIZE_CHECK_EVERY == 0:
            try:
                if os.path.getsize(_PATH) > _max_bytes():
                    _capped = True
                    sys.stderr.write(
                        "[litellm_stream_callback] WARN feed size cap reached; "
                        "further events dropped\n"
                    )
                    return
            except OSError:
                pass
        with open(_PATH, "a", encoding="utf-8") as fh:
            fh.write(line)


def _is_preflight_ping(request_data: dict) -> bool:
    """Mirror of litellm_usage_callback._is_preflight_ping, keyed on the
    request_data dict this hook receives (same messages/max_tokens shape).
    The startup probe posts {"messages":[{"role":"user","content":"ping"}],
    "max_tokens":1} — it must not appear in the live feed."""
    try:
        if request_data.get("max_tokens") not in (1, "1"):
            return False
        messages = request_data.get("messages") or []
        if not isinstance(messages, list) or len(messages) != 1:
            return False
        msg = messages[0]
        if not isinstance(msg, dict) or msg.get("role") != "user":
            return False
        content = msg.get("content")
        if isinstance(content, str):
            return content.strip().lower() == "ping"
        if isinstance(content, list) and len(content) == 1:
            inner = content[0]
            if isinstance(inner, dict):
                text = inner.get("text") or inner.get("content")
                return isinstance(text, str) and text.strip().lower() == "ping"
        return False
    except Exception:
        return False


def _should_emit(request_data: Any) -> bool:
    if not isinstance(request_data, dict):
        return False
    # Chat-shaped traffic only: transcription/embedding calls carry no
    # `messages` (and embeddings are mock_response no-ops anyway).
    if not request_data.get("messages"):
        return False
    if _is_preflight_ping(request_data):
        return False
    return True


def _as_event_dict(chunk: Any) -> Optional[dict]:
    """Best-effort read-only view of a chunk as a dict. None = opaque."""
    if isinstance(chunk, dict):
        return chunk
    for meth in ("model_dump", "dict"):
        fn = getattr(chunk, meth, None)
        if callable(fn):
            try:
                d = fn()
                if isinstance(d, dict):
                    return d
            except Exception:
                return None
    if isinstance(chunk, (bytes, str)):
        # Raw SSE frame(s): parse the LAST data: line we can see. Purely
        # best-effort — a torn frame just yields no event.
        try:
            text = chunk.decode("utf-8", "replace") if isinstance(chunk, bytes) else chunk
            for ln in reversed(text.strip().splitlines()):
                ln = ln.strip()
                if ln.startswith("data:"):
                    return json.loads(ln[len("data:"):].strip())
        except Exception:
            return None
    return None


def _extract(chunk: Any) -> Optional[tuple[str, str, str]]:
    """Map one chunk to (event, kind, delta) or None when it carries nothing
    displayable. Handles both wire shapes seen on this proxy:

    * anthropic /v1/messages events: {"type": "message_start" |
      "content_block_delta" (delta.type text_delta/thinking_delta) |
      "message_stop" | ...}
    * OpenAI-style ModelResponseStream: choices[0].delta.content /
      .reasoning_content
    """
    d = _as_event_dict(chunk)
    if d is None:
        return None
    t = d.get("type")
    if t == "content_block_delta":
        delta = d.get("delta") or {}
        if delta.get("type") == "text_delta" and isinstance(delta.get("text"), str):
            return ("delta", "text", delta["text"])
        if delta.get("type") == "thinking_delta" and isinstance(delta.get("thinking"), str):
            return ("delta", "thinking", delta["thinking"])
        return None
    if t == "message_start":
        return ("message_start", "status", "")
    if t == "message_stop":
        return ("message_stop", "status", "")
    if t == "error":
        err = d.get("error") or {}
        return ("error", "status", str(err.get("message") or "stream error"))
    # OpenAI-style delta chunk.
    choices = d.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0] or {}
        delta_obj = first.get("delta") or {}
        content = delta_obj.get("content")
        if isinstance(content, str) and content:
            return ("delta", "text", content)
        reasoning = delta_obj.get("reasoning_content")
        if isinstance(reasoning, str) and reasoning:
            return ("delta", "thinking", reasoning)
    return None


class StreamTap(CustomLogger):
    """Pass-through observer for streamed proxy responses."""

    async def async_post_call_streaming_iterator_hook(
        self,
        user_api_key_dict: Any,
        response: Any,
        request_data: dict,
    ) -> AsyncGenerator[Any, None]:
        # Per-request emit decision + state. Any failure here downgrades to
        # pure passthrough for the whole request — never blocks the stream.
        try:
            live = _should_emit(request_data)
            req_id = str(
                (request_data or {}).get("litellm_call_id") or uuid.uuid4().hex
            )
            model = str((request_data or {}).get("model") or "")
            saw_stop = False
            seq = 0
        except Exception:
            live = False
            req_id, model, saw_stop, seq = "", "", True, 0

        if live:
            try:
                _write_row({
                    "ts": round(time.time(), 3), "seq": seq, "source": "agent",
                    "request_id": req_id, "model": model, "kind": "status",
                    "event": "message_start", "delta": "",
                })
                seq += 1
            except Exception:
                live = False

        async for chunk in response:
            if live:
                # R2: extraction/write failures self-disable; the chunk below
                # still flows. The yield is OUTSIDE this try by design.
                try:
                    got = _extract(chunk)
                    # The hook already emitted message_start for this request;
                    # the chunk-derived one is a duplicate the renderer would
                    # misread as a second (sub-agent) request opening.
                    if got is not None and got[0] == "message_start":
                        got = None
                    if got is not None:
                        event, kind, delta = got
                        if event == "message_stop":
                            saw_stop = True
                        _write_row({
                            "ts": round(time.time(), 3), "seq": seq,
                            "source": "agent", "request_id": req_id,
                            "model": model, "kind": kind, "event": event,
                            "delta": delta,
                        })
                        seq += 1
                except Exception:
                    live = False
            # R5: forward the ORIGINAL object, unconditionally.
            yield chunk

        if live and not saw_stop:
            # Upstream ended without a terminal frame (or we never saw one
            # through this shape) — close the request in the feed so the
            # renderer doesn't hold it open forever.
            try:
                _write_row({
                    "ts": round(time.time(), 3), "seq": seq, "source": "agent",
                    "request_id": req_id, "model": model, "kind": "status",
                    "event": "message_stop", "delta": "",
                })
            except Exception:
                pass


# Name referenced from the LiteLLM YAML:
#   callbacks: ["litellm_stream_callback.stream_handler_instance"]
stream_handler_instance = StreamTap()
