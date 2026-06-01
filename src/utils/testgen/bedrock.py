"""Direct Bedrock Converse API client for test generation.

Bypasses the LiteLLM sidecar by design — the test-gen LLM is invoked at task
preparation time (outside the agent's container network), so we'd have to spin
the sidecar earlier just to call it. Direct httpx is simpler and matches
kensei2's behavior.

Ported from kensei2/controllers/llm_assisst_qc.py (lines 21-23, 322-391).

Auth: AWS bearer token (Authorization: Bearer <KENSEI_AWS_BEARER_TOKEN> /
AWS_BEARER_TOKEN_BEDROCK). Cross-account inference-profile ARN is URL-encoded
into the path.
"""

from __future__ import annotations

import logging
from typing import Optional, Tuple
from urllib.parse import quote

import httpx

_logger = logging.getLogger(__name__)

BEDROCK_CONVERSE_STREAM_URL = (
    "https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/converse-stream"
)


def call_bedrock_converse(
    *,
    api_key: str,
    inference_arn: str,
    region: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int = 4096,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    timeout: float = 600.0,
) -> Tuple[str, dict]:
    """Single Bedrock ConverseStream round-trip. Returns (response_text, usage).

    Wire protocol: posts to ``/converse-stream`` and consumes the
    vnd.amazon.eventstream binary response, aggregating text from
    ``contentBlockDelta`` events and usage from the final ``metadata`` event.
    Synchronous facade: callers receive the same ``(text, usage)`` tuple as
    the non-streaming `/converse` path, so no consumer code changes.

    usage keys: input_tokens, output_tokens, cache_read_tokens,
    cache_write_tokens, total_tokens, request_count.

    Raises RuntimeError on non-200 status or service-level error in any event.
    """
    if not api_key:
        raise RuntimeError("Bedrock bearer token is empty (set KENSEI_AWS_BEARER_TOKEN or AWS_BEARER_TOKEN_BEDROCK)")
    if not inference_arn:
        raise RuntimeError("Bedrock inference ARN is empty (set KENSEI_BEDROCK_MODEL_ARN or BEDROCK_MODEL_ARN)")

    url = BEDROCK_CONVERSE_STREAM_URL.format(
        region=region,
        model_id=quote(inference_arn, safe=""),
    )
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.amazon.eventstream",
        "Authorization": "Bearer %s" % api_key,
    }

    payload = {
        "messages": [
            {"role": "user", "content": [{"text": user_message}]},
        ],
        "inferenceConfig": {"maxTokens": max_tokens},
    }
    if temperature is not None:
        payload["inferenceConfig"]["temperature"] = temperature
    if top_p is not None:
        payload["inferenceConfig"]["topP"] = top_p
    if system_prompt:
        payload["system"] = [
            {"text": system_prompt},
            {"cachePoint": {"type": "default"}},
        ]

    from src.utils.bedrock_eventstream import iter_eventstream

    response_text = ""
    usage_raw: dict = {}
    with httpx.Client(http2=True, timeout=timeout) as client:
        with client.stream("POST", url, json=payload, headers=headers) as resp:
            if resp.status_code != 200:
                error_detail = resp.read().decode("utf-8", errors="replace")[:500]
                _logger.error("Bedrock API returned status %d: %s", resp.status_code, error_detail)
                raise RuntimeError("Bedrock API error (HTTP %d): %s" % (resp.status_code, error_detail))
            for evt_type, evt_payload in iter_eventstream(resp.iter_bytes()):
                if not isinstance(evt_payload, dict):
                    continue
                if evt_payload.get("Message") or evt_payload.get("message"):
                    err = evt_payload.get("Message") or evt_payload.get("message") or ""
                    if evt_type and evt_type.endswith("Exception"):
                        raise RuntimeError("Bedrock service error (%s): %s" % (evt_type, err))
                if evt_type == "contentBlockDelta":
                    delta = evt_payload.get("delta") or {}
                    text_part = delta.get("text")
                    if isinstance(text_part, str):
                        response_text += text_part
                elif evt_type == "metadata":
                    usage_obj = evt_payload.get("usage")
                    if isinstance(usage_obj, dict):
                        usage_raw = usage_obj

    input_tokens = int(usage_raw.get("inputTokens", 0) or 0)
    output_tokens = int(usage_raw.get("outputTokens", 0) or 0)
    # AWS streaming metadata events have shipped multiple field-name spellings
    # for the cache counters over time (cacheReadInputTokens / cacheReadTokens
    # / cache_read_input_tokens). We probe all known variants so any future
    # rename does not silently zero out cache_read in usage.json (which would
    # masquerade as a caching-regression like the one observed in b35).
    cache_read = int(
        usage_raw.get("cacheReadInputTokens")
        or usage_raw.get("cacheReadTokens")
        or usage_raw.get("cache_read_input_tokens")
        or 0
    )
    cache_write = int(
        usage_raw.get("cacheWriteInputTokens")
        or usage_raw.get("cacheCreationInputTokens")
        or usage_raw.get("cache_creation_input_tokens")
        or 0
    )
    total_tokens = int(
        usage_raw.get("totalTokens", 0)
        or (input_tokens + output_tokens + cache_read + cache_write)
    )
    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug("[bedrock-converse-stream] raw usage event: %s", usage_raw)
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_tokens": cache_read,
        "cache_write_tokens": cache_write,
        "total_tokens": total_tokens,
        "request_count": 1,
    }

    return response_text.strip(), usage
