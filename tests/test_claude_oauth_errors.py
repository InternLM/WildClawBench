"""Tests for src/utils/claude_oauth/errors.py — Anthropic error classifier."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.claude_oauth.errors import (
    ClassifiedError,
    ErrorKind,
    TRANSIENT_RETRY_AFTER_THRESHOLD,
    classify_anthropic_error,
    extract_retry_after,
)


def test_error_kind_retryable_set():
    assert ErrorKind.TRANSIENT_THROTTLE.is_retryable
    assert ErrorKind.OVERLOADED.is_retryable
    assert ErrorKind.UPSTREAM_5XX.is_retryable
    assert not ErrorKind.SUBSCRIPTION_CAP.is_retryable
    assert not ErrorKind.OAUTH_TOKEN_INVALID.is_retryable
    assert not ErrorKind.INVALID_REQUEST.is_retryable


def test_error_kind_account_problem_set():
    assert ErrorKind.SUBSCRIPTION_CAP.is_account_problem
    assert ErrorKind.OAUTH_TOKEN_INVALID.is_account_problem
    assert ErrorKind.ACCOUNT_RESTRICTED.is_account_problem
    assert ErrorKind.BILLING_ERROR.is_account_problem
    assert not ErrorKind.TRANSIENT_THROTTLE.is_account_problem
    assert not ErrorKind.OVERLOADED.is_account_problem


def test_429_short_retry_after_is_transient():
    headers = {"retry-after": "5"}
    result = classify_anthropic_error(429, b"", headers)
    assert result.kind == ErrorKind.TRANSIENT_THROTTLE
    assert result.retry_after_seconds == 5


def test_429_long_retry_after_is_subscription_cap():
    headers = {"retry-after": "3600"}
    assert TRANSIENT_RETRY_AFTER_THRESHOLD == 60
    result = classify_anthropic_error(429, b"", headers)
    assert result.kind == ErrorKind.SUBSCRIPTION_CAP
    assert result.retry_after_seconds == 3600


def test_429_zero_tokens_remaining_is_subscription_cap():
    headers = {
        "retry-after": "10",
        "anthropic-ratelimit-unified-tokens-remaining": "0",
    }
    result = classify_anthropic_error(429, b"", headers)
    assert result.kind == ErrorKind.SUBSCRIPTION_CAP


def test_401_is_oauth_invalid():
    result = classify_anthropic_error(401, b'{"error":{"type":"authentication_error"}}', {})
    assert result.kind == ErrorKind.OAUTH_TOKEN_INVALID
    assert result.status_code == 401


def test_402_is_billing():
    result = classify_anthropic_error(402, b"", {})
    assert result.kind == ErrorKind.BILLING_ERROR


def test_403_is_restricted():
    result = classify_anthropic_error(403, b"", {})
    assert result.kind == ErrorKind.ACCOUNT_RESTRICTED


def test_400_is_invalid_request():
    result = classify_anthropic_error(400, b'{"error":{"type":"invalid_request_error","message":"bad"}}', {})
    assert result.kind == ErrorKind.INVALID_REQUEST


def test_529_is_overloaded():
    result = classify_anthropic_error(529, b"", {})
    assert result.kind == ErrorKind.OVERLOADED


def test_500_series_is_upstream_5xx():
    result = classify_anthropic_error(503, b"", {})
    assert result.kind == ErrorKind.UPSTREAM_5XX
    assert result.status_code == 503


def test_extract_retry_after_prefers_retry_after_header():
    headers = {
        "retry-after": "45",
        "anthropic-ratelimit-unified-tokens-reset": "9999999999",
    }
    assert extract_retry_after(headers) == 45


def test_extract_retry_after_falls_back_to_reset_headers():
    import time as _t
    future = int(_t.time() + 120)
    headers = {"anthropic-ratelimit-unified-tokens-reset": str(future)}
    result = extract_retry_after(headers)
    assert result is not None
    assert 60 <= result <= 180


def test_classified_error_has_request_id():
    body = b'{"error":{"type":"rate_limit_error","message":"slow down"},"request_id":"req_abc123"}'
    result = classify_anthropic_error(429, body, {"retry-after": "5"})
    assert result.request_id == "req_abc123"
    assert result.message == "slow down"
