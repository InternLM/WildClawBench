"""Classify Anthropic API errors so the bridge and pipeline can react sensibly.

Anthropic returns a small set of HTTP+body shapes; this module turns each
into an ``ErrorKind`` plus a recommended ``retry_after_seconds`` so callers
don't have to re-parse headers.

The hardest call is 429: it covers both a short transient throttle AND the
hard 5-hour / weekly subscription caps. The API does not distinguish, so we
heuristically classify based on the ``Retry-After`` value and the
``anthropic-ratelimit-tokens-remaining`` header.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Optional, Tuple

_LOG = logging.getLogger(__name__)

# Boundary between "wait inline at the bridge" and "this is a subscription cap,
# bubble up so the pipeline can pause-and-resume". 60s is the practical cutoff
# observed on real 429 responses -- transient throttles report Retry-After
# values of single-digit to ~30 seconds; subscription caps report values
# >= 60 seconds (typically thousands).
TRANSIENT_RETRY_AFTER_THRESHOLD = 60


class ErrorKind(str, Enum):
    """Coarse classification of an Anthropic API error."""

    TRANSIENT_THROTTLE = "transient_throttle"
    SUBSCRIPTION_CAP = "subscription_cap"
    OAUTH_TOKEN_INVALID = "oauth_token_invalid"
    ACCOUNT_RESTRICTED = "account_restricted"
    OVERLOADED = "overloaded"
    BILLING_ERROR = "billing_error"
    INVALID_REQUEST = "invalid_request"
    UPSTREAM_5XX = "upstream_5xx"
    UNKNOWN = "unknown"

    @property
    def is_retryable(self) -> bool:
        """Whether the bridge should retry this error class itself."""
        return self in {
            ErrorKind.TRANSIENT_THROTTLE,
            ErrorKind.OVERLOADED,
            ErrorKind.UPSTREAM_5XX,
        }

    @property
    def is_account_problem(self) -> bool:
        """Whether failing over to a different account would help."""
        return self in {
            ErrorKind.SUBSCRIPTION_CAP,
            ErrorKind.OAUTH_TOKEN_INVALID,
            ErrorKind.ACCOUNT_RESTRICTED,
            ErrorKind.BILLING_ERROR,
        }


@dataclass
class ClassifiedError:
    kind: ErrorKind
    status_code: int
    retry_after_seconds: Optional[int]
    reset_at_unix: Optional[float]
    message: str
    raw_error_type: Optional[str] = None
    request_id: Optional[str] = None


def _parse_int_header(headers: Mapping[str, str], name: str) -> Optional[int]:
    val = headers.get(name) or headers.get(name.lower())
    if val is None:
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _parse_iso_header(headers: Mapping[str, str], name: str) -> Optional[float]:
    """Parse an RFC3339 reset timestamp into Unix seconds. None on failure."""
    val = headers.get(name) or headers.get(name.lower())
    if not val:
        return None
    # Anthropic returns either RFC3339 (preferred) or seconds-from-epoch.
    try:
        return float(val)
    except (TypeError, ValueError):
        pass
    try:
        from datetime import datetime

        # Normalize trailing Z -> +00:00 so fromisoformat accepts it.
        norm = val.rstrip()
        if norm.endswith("Z"):
            norm = norm[:-1] + "+00:00"
        dt = datetime.fromisoformat(norm)
        return dt.timestamp()
    except (TypeError, ValueError):
        return None


def extract_retry_after(headers: Mapping[str, str]) -> Optional[int]:
    """Best-effort seconds-to-retry, preferring Retry-After then ratelimit-reset."""
    explicit = _parse_int_header(headers, "Retry-After") or _parse_int_header(
        headers, "retry-after"
    )
    if explicit is not None and explicit >= 0:
        return explicit

    now = time.time()
    for key in (
        "anthropic-ratelimit-unified-tokens-reset",
        "anthropic-ratelimit-unified-requests-reset",
        "anthropic-ratelimit-tokens-reset",
        "anthropic-ratelimit-requests-reset",
    ):
        reset_at = _parse_iso_header(headers, key)
        if reset_at is not None:
            delta = int(reset_at - now)
            if delta > 0:
                return delta
    return None


def _extract_reset_at(headers: Mapping[str, str]) -> Optional[float]:
    """Absolute Unix-time when the most relevant rate-limit bucket resets."""
    for key in (
        "anthropic-ratelimit-unified-tokens-reset",
        "anthropic-ratelimit-unified-requests-reset",
        "anthropic-ratelimit-tokens-reset",
        "anthropic-ratelimit-requests-reset",
    ):
        v = _parse_iso_header(headers, key)
        if v is not None:
            return v
    ra = extract_retry_after(headers)
    if ra is not None:
        return time.time() + ra
    return None


def _decode_body(body: bytes | str | None) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Pull (error_type, message, request_id) out of an Anthropic error body."""
    if body is None:
        return None, None, None
    if isinstance(body, (bytes, bytearray)):
        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            return None, None, None
    else:
        text = body
    try:
        obj = json.loads(text)
    except (TypeError, ValueError):
        return None, text[:200] if text else None, None
    if not isinstance(obj, dict):
        return None, None, None
    err = obj.get("error") or {}
    if isinstance(err, dict):
        return (
            err.get("type"),
            err.get("message"),
            obj.get("request_id"),
        )
    return None, str(err)[:200], obj.get("request_id")


def classify_anthropic_error(
    status_code: int,
    body: bytes | str | None,
    headers: Mapping[str, str] | None = None,
) -> ClassifiedError:
    """Map an Anthropic upstream response into a ``ClassifiedError``.

    Heuristics:
      - 429 with retry-after < 60s and tokens-remaining > 0  -> TRANSIENT_THROTTLE
      - 429 with retry-after >= 60s OR tokens-remaining == 0 -> SUBSCRIPTION_CAP
      - 401                                                  -> OAUTH_TOKEN_INVALID
      - 403                                                  -> ACCOUNT_RESTRICTED
      - 402                                                  -> BILLING_ERROR
      - 529                                                  -> OVERLOADED
      - 5xx                                                  -> UPSTREAM_5XX
      - 400                                                  -> INVALID_REQUEST
    """
    headers = headers or {}
    err_type, message, request_id = _decode_body(body)
    retry_after = extract_retry_after(headers)
    reset_at = _extract_reset_at(headers)
    message = message or err_type or f"HTTP {status_code}"

    if status_code == 429:
        tokens_remaining = _parse_int_header(
            headers, "anthropic-ratelimit-unified-tokens-remaining"
        )
        if tokens_remaining is None:
            tokens_remaining = _parse_int_header(
                headers, "anthropic-ratelimit-tokens-remaining"
            )
        is_cap = False
        if retry_after is not None and retry_after >= TRANSIENT_RETRY_AFTER_THRESHOLD:
            is_cap = True
        if tokens_remaining == 0:
            is_cap = True
        kind = ErrorKind.SUBSCRIPTION_CAP if is_cap else ErrorKind.TRANSIENT_THROTTLE
        return ClassifiedError(
            kind=kind,
            status_code=429,
            retry_after_seconds=retry_after,
            reset_at_unix=reset_at,
            message=message,
            raw_error_type=err_type,
            request_id=request_id,
        )

    if status_code == 401:
        return ClassifiedError(
            kind=ErrorKind.OAUTH_TOKEN_INVALID,
            status_code=401,
            retry_after_seconds=None,
            reset_at_unix=None,
            message=message,
            raw_error_type=err_type,
            request_id=request_id,
        )

    if status_code == 403:
        return ClassifiedError(
            kind=ErrorKind.ACCOUNT_RESTRICTED,
            status_code=403,
            retry_after_seconds=None,
            reset_at_unix=None,
            message=message,
            raw_error_type=err_type,
            request_id=request_id,
        )

    if status_code == 402:
        return ClassifiedError(
            kind=ErrorKind.BILLING_ERROR,
            status_code=402,
            retry_after_seconds=None,
            reset_at_unix=None,
            message=message,
            raw_error_type=err_type,
            request_id=request_id,
        )

    if status_code == 529:
        return ClassifiedError(
            kind=ErrorKind.OVERLOADED,
            status_code=529,
            retry_after_seconds=retry_after,
            reset_at_unix=reset_at,
            message=message,
            raw_error_type=err_type,
            request_id=request_id,
        )

    if status_code == 400:
        return ClassifiedError(
            kind=ErrorKind.INVALID_REQUEST,
            status_code=400,
            retry_after_seconds=None,
            reset_at_unix=None,
            message=message,
            raw_error_type=err_type,
            request_id=request_id,
        )

    if 500 <= status_code < 600:
        return ClassifiedError(
            kind=ErrorKind.UPSTREAM_5XX,
            status_code=status_code,
            retry_after_seconds=retry_after,
            reset_at_unix=reset_at,
            message=message,
            raw_error_type=err_type,
            request_id=request_id,
        )

    return ClassifiedError(
        kind=ErrorKind.UNKNOWN,
        status_code=status_code,
        retry_after_seconds=None,
        reset_at_unix=None,
        message=message,
        raw_error_type=err_type,
        request_id=request_id,
    )
