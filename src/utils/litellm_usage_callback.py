"""LiteLLM proxy callback that writes real per-request usage to a JSONL log.

Mounted into the LiteLLM sidecar container at /app/litellm_usage_callback.py and
referenced from the proxy YAML as:

    litellm_settings:
      callbacks: ["litellm_usage_callback.proxy_handler_instance"]

Each successful upstream call appends one JSON row with the real provider-side
token counts and cost. The host-side reader (`extract_usage_from_litellm_log` in
`src/utils/grading.py`) filters by timestamp window per task.

This bypasses openclaw's internal LiteLLM provider, whose `chat.jsonl` usage
fields are always zero on this image build — every cost was previously coming
from an `len(text)//4` heuristic flagged as `usage_source: estimated`.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from datetime import datetime, timezone
from typing import Any

try:
    from litellm.integrations.custom_logger import CustomLogger  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - litellm only present inside the sidecar
    class CustomLogger:  # type: ignore[no-redef]
        pass


_PATH = os.environ.get("LITELLM_USAGE_LOG_PATH", "/var/litellm_usage/usage.jsonl")
_LOCK = threading.Lock()

# Rate-limit usage-invariant warnings to once per (model, UTC date) so a
# persistent upstream mis-report cannot flood the sidecar's stderr/gateway.log.
_WARN_SEEN: set[tuple[str, str]] = set()


def _warn_once_per_day(model: Any, fmt: str, *args: Any) -> None:
    key = (str(model or ""), datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    if key in _WARN_SEEN:
        return
    _WARN_SEEN.add(key)
    sys.stderr.write(f"[litellm_usage_callback] WARN model={model!r}: " + (fmt % args) + "\n")


def _usage_to_dict(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {}
    if isinstance(usage, dict):
        return usage
    # ModelResponse.usage is a Pydantic Usage object; .dict()/.model_dump() both work.
    for method_name in ("model_dump", "dict"):
        meth = getattr(usage, method_name, None)
        if callable(meth):
            try:
                result = meth()
                if isinstance(result, dict):
                    return result
            except Exception:
                pass
    fallback = getattr(usage, "__dict__", {}) or {}
    return fallback if isinstance(fallback, dict) else {}


def _int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _is_preflight_ping(kwargs: dict) -> bool:
    # The sidecar startup probe at src/utils/litellm_sidecar.py::
    # verify_litellm_upstream_reachable posts exactly:
    #   {"messages":[{"role":"user","content":"ping"}], "max_tokens":1, "stream":false}
    # to /v1/chat/completions. Tag it so the host-side extractor can put its
    # cost in `sources.preflight` instead of dropping it on the floor (it
    # happens BEFORE any task's run window, so the in-window agent extractor
    # filters it out).
    try:
        op = kwargs.get("optional_params") or {}
        max_tok = kwargs.get("max_tokens", op.get("max_tokens", op.get("maxTokens")))
        if max_tok not in (1, "1"):
            return False
        messages = kwargs.get("messages") or []
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


def _write_row(kwargs: dict, response_obj: Any, start_time: Any, end_time: Any) -> None:
    try:
        usage_dict = _usage_to_dict(getattr(response_obj, "usage", None))
        if not usage_dict and isinstance(response_obj, dict):
            usage_dict = _usage_to_dict(response_obj.get("usage"))

        cache_read = _int((usage_dict.get("prompt_tokens_details") or {}).get("cached_tokens"))
        if not cache_read:
            cache_read = _int(usage_dict.get("cache_read_input_tokens"))
        cache_write = _int(usage_dict.get("cache_creation_input_tokens"))

        # Audio transcription (/v1/audio/transcriptions) responses use a different
        # usage schema than chat completions. LiteLLM emits one of two shapes:
        #   token-billed (gpt-4o-transcribe / gpt-4o-mini-transcribe):
        #       {type: "tokens", input_tokens, output_tokens, total_tokens, input_token_details}
        #   duration-billed (whisper-1):
        #       {type: "duration", seconds}   -- NO token fields at all
        # Chat keys (prompt_tokens/completion_tokens) are absent in both, so fall
        # back to the transcription keys; whisper's seconds is surfaced separately.
        prompt_tokens_raw = _int(usage_dict.get("prompt_tokens"))
        if not prompt_tokens_raw:
            prompt_tokens_raw = _int(usage_dict.get("input_tokens"))
        output_tokens = _int(usage_dict.get("completion_tokens"))
        if not output_tokens:
            output_tokens = _int(usage_dict.get("output_tokens"))

        # input_tokens = NON-cached input only. Across every provider shape
        # this callback sees, prompt_tokens already folds in cache_read AND
        # cache_write whenever those exist, so the universal recovery rule is
        # `non_cached = prompt - cache_read - cache_write` (clamped to 0).
        # Verified provider shapes (litellm v1.87.x):
        #   - Bedrock-Converse — llms/bedrock/chat/converse_transformation.py
        #     _transform_usage lines 1715-1748: adds BOTH cacheReadInputTokens
        #     AND cacheWriteInputTokens to input_tokens before emitting it as
        #     prompt_tokens.
        #   - Anthropic-native /v1/messages — llms/anthropic/chat/
        #     transformation.py lines 2173-2193: adds BOTH cache_read_input_tokens
        #     AND cache_creation_input_tokens to prompt_tokens.
        #   - OpenAI Chat Completions: no cache_creation field exists in the
        #     provider response at all (grep confirms zero hits in llms/openai/),
        #     so cache_write extracted at line 96 is always 0 and the third
        #     term is a no-op.
        #   - Audio: no cache fields; both terms are 0.
        # The prior rule "subtract cache_read only" was wrong on the two
        # Anthropic paths: a 38k-cache-write opus turn over-reported input by
        # ~38,000 tokens. Diagnosed via the rohan-dasgupta trajectory against
        # CloudWatch ModelInvocationLog; do not revert.
        non_cached = prompt_tokens_raw - cache_read - cache_write
        if non_cached < 0:
            _warn_once_per_day(
                kwargs.get("model"),
                "prompt_tokens (%d) < cache_read (%d) + cache_write (%d); clamping non-cached input to 0",
                prompt_tokens_raw, cache_read, cache_write,
            )
            non_cached = 0
        input_tokens = non_cached
        total_tokens = input_tokens + output_tokens + cache_read + cache_write
        # whisper-1 (default json format) returns NO usage object at all; the audio
        # length is exposed only as the top-level TranscriptionResponse.duration
        # attribute (verified live in litellm:main-stable). Prefer usage.seconds
        # when present (verbose_json / future shapes), else fall back to .duration.
        audio_seconds = _float(usage_dict.get("seconds"))
        if not audio_seconds:
            audio_seconds = _float(getattr(response_obj, "duration", None))

        duration = 0.0
        try:
            duration = (end_time - start_time).total_seconds()
        except Exception:
            pass

        # Cost: prefer litellm.completion_cost() over the proxy-supplied
        # kwargs["response_cost"], because the latter is systematically wrong on
        # at least two upstream paths (both verified live against
        # litellm:main-stable v1.87.0):
        #   - Bedrock Anthropic streaming with prompt caching: response_cost
        #     omits cache_write (cache_creation_input_tokens) pricing entirely,
        #     under-counting opus rows ~12-14x (e.g. a 38k-cache-write turn
        #     priced at $0.0028 instead of $0.245).
        #   - OpenAI /responses path (gpt-5.5) with large outputs: response_cost
        #     comes back 0.0 on ~5/78 rows.
        # completion_cost(completion_response=, model=) reads the cache fields and
        # prices them at the correct per-token rates. We fall back to
        # response_cost ONLY when completion_cost yields <= 0, which preserves
        # whisper-1 duration billing (no tokens -> completion_cost is 0 and
        # response_cost is the only valid source). Do NOT revert to plain
        # response_cost.
        cost = 0.0
        try:
            import litellm
            cost = float(
                litellm.completion_cost(
                    completion_response=response_obj,
                    model=kwargs.get("model"),
                )
                or 0.0
            )
        except Exception as exc:
            sys.stderr.write(
                f"[litellm_usage_callback] completion_cost failed for "
                f"model={kwargs.get('model')!r}: {exc}\n"
            )
            cost = 0.0
        if cost <= 0.0:
            cost = _float(kwargs.get("response_cost"))

        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "model": kwargs.get("model") or "",
            "kind": "preflight" if _is_preflight_ping(kwargs) else "agent",
            "input_tokens":       input_tokens,
            "output_tokens":      output_tokens,
            "total_tokens":       total_tokens,
            "cache_read_tokens":  cache_read,
            "cache_write_tokens": cache_write,
            "audio_seconds":      round(audio_seconds, 3),
            "cost_usd":           cost,
            "duration_s":         round(duration, 3),
        }
        os.makedirs(os.path.dirname(_PATH), exist_ok=True)
        with _LOCK:
            with open(_PATH, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")
    except Exception as exc:  # pragma: no cover - never crash the proxy
        try:
            sys.stderr.write(f"[litellm_usage_callback] error: {exc}\n")
        except Exception:
            pass


class UsageWriter(CustomLogger):
    # async-only on purpose: LiteLLM's streaming_handler.run_success_logging_and_
    # cache_storage and its async stream finalizer dispatch BOTH success_handler
    # (sync) AND async_success_handler on every streamed completion. The
    # litellm_logging.has_run_logging dedup early-returns for self.stream=True
    # (litellm v1.87.x line 1631), so the has_logged_sync_success / async_success
    # flags are never set and both branches run. Defining log_success_event here
    # in addition to async_log_success_event therefore writes every Bedrock
    # streaming row twice. Verified live against the rohan-dasgupta trajectory
    # vs CloudWatch ModelInvocationLog: request_count/output/cache_read/
    # cache_write all matched 2x exactly until log_success_event was removed.
    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        _write_row(kwargs, response_obj, start_time, end_time)


# Name expected by LiteLLM YAML config: callbacks: ["litellm_usage_callback.proxy_handler_instance"]
proxy_handler_instance = UsageWriter()
