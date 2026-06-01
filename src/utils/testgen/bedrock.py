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

BEDROCK_CONVERSE_URL = (
    "https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/converse"
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
    """Single Bedrock Converse round-trip. Returns (response_text, usage).

    usage keys: input_tokens, output_tokens, cache_read_tokens,
    cache_write_tokens, total_tokens, request_count.

    Raises RuntimeError on non-200 status or service-level error in the body.
    """
    if not api_key:
        raise RuntimeError("Bedrock bearer token is empty (set KENSEI_AWS_BEARER_TOKEN or AWS_BEARER_TOKEN_BEDROCK)")
    if not inference_arn:
        raise RuntimeError("Bedrock inference ARN is empty (set KENSEI_BEDROCK_MODEL_ARN or BEDROCK_MODEL_ARN)")

    url = BEDROCK_CONVERSE_URL.format(
        region=region,
        model_id=quote(inference_arn, safe=""),
    )
    headers = {
        "Content-Type": "application/json",
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

    with httpx.Client(http2=True, timeout=timeout) as client:
        resp = client.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        error_detail = resp.text[:500]
        _logger.error("Bedrock API returned status %d: %s", resp.status_code, error_detail)
        raise RuntimeError("Bedrock API error (HTTP %d): %s" % (resp.status_code, error_detail))

    result = resp.json()

    output_key = "output" if "output" in result else "Output"
    if output_key in result and isinstance(result[output_key], dict):
        err_type = result[output_key].get("__type", "")
        if err_type:
            raise RuntimeError("Bedrock service error: %s" % err_type)

    content_blocks = result.get("output", {}).get("message", {}).get("content", [])
    response_text = ""
    for block in content_blocks:
        if isinstance(block, dict) and "text" in block:
            response_text += block["text"]

    usage_raw = result.get("usage", {}) or {}
    input_tokens = int(usage_raw.get("inputTokens", 0) or 0)
    output_tokens = int(usage_raw.get("outputTokens", 0) or 0)
    cache_read = int(usage_raw.get("cacheReadInputTokens", 0) or 0)
    cache_write = int(usage_raw.get("cacheWriteInputTokens", 0) or 0)
    total_tokens = int(
        usage_raw.get("totalTokens", 0)
        or (input_tokens + output_tokens + cache_read + cache_write)
    )
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_tokens": cache_read,
        "cache_write_tokens": cache_write,
        "total_tokens": total_tokens,
        "request_count": 1,
    }

    return response_text.strip(), usage
