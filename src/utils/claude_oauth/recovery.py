"""Pause-and-resume helper for the per-module aider loop.

When ``run_pipeline.sh`` is using the Claude Code OAuth bridge and the
upstream returns a `SUBSCRIPTION_CAP` 429 (5-hour or weekly limit hit), the
bridge can't retry inline -- the wait would exceed the inactivity watchdog.
Instead it bubbles a structured ``X-WCB-Bridge-Error: subscription_cap``
response, which litellm raises as ``litellm.exceptions.RateLimitError``.

This module wraps ``agent.run(...)`` so we catch that, query the bridge's
``/quota`` endpoint for the soonest reset time, sleep with periodic
heartbeats (so ``INACTIVITY_TIMEOUT`` doesn't fire), and retry the same call
once. Bedrock / Vertex paths bypass this entirely (the wrapper is a no-op
when ``ANTHROPIC_API_BASE`` is not pointing at the bridge).
"""

from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar
from urllib.parse import urlparse

import httpx

# Best-effort: import real exception classes so isinstance() works against the
# canonical types. Fall back to MRO-walk + string match if litellm/openai aren't
# present (e.g. in pure-unit tests).
_RATE_LIMIT_EXC_CLASSES: tuple[type, ...] = ()
try:
    from litellm.exceptions import RateLimitError as _LitellmRateLimitError  # type: ignore
    _RATE_LIMIT_EXC_CLASSES = _RATE_LIMIT_EXC_CLASSES + (_LitellmRateLimitError,)
except ImportError:
    pass
try:
    from openai import RateLimitError as _OpenAIRateLimitError  # type: ignore
    _RATE_LIMIT_EXC_CLASSES = _RATE_LIMIT_EXC_CLASSES + (_OpenAIRateLimitError,)
except ImportError:
    pass
_LOG = logging.getLogger(__name__)

T = TypeVar("T")

DEFAULT_MAX_PAUSE_SECONDS = 6 * 3600  # 6h: just above the 5h cap, well below weekly
DEFAULT_HEARTBEAT_SECONDS = 60        # < INACTIVITY_TIMEOUT (900s in run_pipeline.sh)
QUOTA_TIMEOUT = 5.0


def _bridge_base_url() -> Optional[str]:
    """Return the bridge base URL only when ``ANTHROPIC_API_BASE`` is set to a
    local-looking value. We don't want to call /quota on api.anthropic.com.
    """
    base = os.environ.get("ANTHROPIC_API_BASE", "").strip()
    if not base:
        return None
    try:
        host = urlparse(base).hostname or ""
    except Exception:  # noqa: BLE001
        return None
    if host in ("localhost", "127.0.0.1", "::1") or host.endswith(".local"):
        return base.rstrip("/")
    return None


def _fetch_quota(base_url: str) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=QUOTA_TIMEOUT) as c:
            r = c.get(f"{base_url}/quota")
            if r.status_code != 200:
                return {}
            return r.json()
    except (httpx.HTTPError, ValueError) as e:
        _LOG.warning("could not query bridge /quota: %s", e)
        return {}


def _next_reset_seconds(base_url: str, fallback_seconds: int) -> int:
    """Seconds until the soonest cap reset, or ``fallback_seconds`` if unknown."""
    quota = _fetch_quota(base_url)
    reset_at = quota.get("next_reset_at_unix")
    if reset_at:
        delta = int(reset_at - time.time())
        if delta > 0:
            return delta
    return fallback_seconds


def _effective_max_retries(base_url: str, user_max_retries: int) -> int:
    """Auto-scale ``max_retries`` to the multi-account pool size.

    Single-account: user's value (default 1) is fine -- one pause cycle covers
    the 5h cap reset for a single subscription.

    Multi-account: we must be able to traverse the entire pool before giving
    up. If accountA hits a cap, recovery pauses, retries, lands on accountB.
    If accountB is ALSO capped, we need ANOTHER retry to reach accountC, etc.
    So effective_max_retries >= pool_size.
    """
    quota = _fetch_quota(base_url)
    accounts = quota.get("accounts") or []
    pool_size = len(accounts) if quota.get("multi_account") else 0
    if pool_size <= 1:
        return user_max_retries
    return max(user_max_retries, pool_size)


def _max_pause_seconds() -> int:
    raw = os.environ.get("WCB_CC_MAX_PAUSE_SEC", "").strip()
    if not raw:
        return DEFAULT_MAX_PAUSE_SECONDS
    try:
        return max(60, int(raw))
    except ValueError:
        return DEFAULT_MAX_PAUSE_SECONDS


def _is_rate_limit_error(exc: BaseException) -> bool:
    """Detect litellm/openai-flavored rate-limit errors."""
    if _RATE_LIMIT_EXC_CLASSES and isinstance(exc, _RATE_LIMIT_EXC_CLASSES):
        return True
    for cls in type(exc).__mro__:
        if cls.__name__ in ("RateLimitError", "APIError") and "litellm" in cls.__module__:
            return True
        if cls.__name__ == "RateLimitError" and cls.__module__.startswith("openai"):
            return True
    msg = str(exc).lower()
    return ("rate_limit_error" in msg
            or "subscription_cap" in msg
            or "ratelimiterror" in msg)


def _extract_retry_after_from_error(exc: BaseException) -> Optional[int]:
    """Best-effort: pull a Retry-After hint from a litellm RateLimitError."""
    resp = getattr(exc, "response", None) or getattr(exc, "_response", None)
    if resp is not None:
        headers = getattr(resp, "headers", None)
        if headers is not None:
            try:
                val = headers.get("Retry-After") or headers.get("retry-after")
                if val is not None:
                    return int(val)
            except (TypeError, ValueError):
                pass
    msg = str(exc)
    m = re.search(r"retry[-_ ]after[:\s]+(\d+)", msg, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return None


def _heartbeat(log_dir: Optional[Path]) -> None:
    """Touch files the harness watchdog actually polls.

    The watchdog at ``run_pipeline.sh:660+`` checks two file kinds for activity:
      - ``find <stage_log_dir> -name aider.log`` (newest mtime)
      - ``<stage_log_dir>/agent_run.log``

    Touching ``_kaiju_log_dir/.rate_limit_paused`` is invisible to it. So we
    walk UP the directory tree from ``log_dir`` until we find either
    ``agent_run.log`` or any ``aider.log``, and touch them. We ALSO drop a
    marker file at ``_kaiju_log_dir/.rate_limit_paused`` for human debugging.
    """
    if log_dir is None:
        return
    try:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / ".rate_limit_paused").touch()
    except OSError:
        pass
    # Walk up to find agent_run.log (lives in the stage_log_dir) and aider.log
    # files anywhere in subtree of the discovered stage_log_dir. Cap walk depth.
    try:
        cur = Path(log_dir).resolve()
        for _ in range(8):
            cand = cur / "agent_run.log"
            if cand.is_file():
                cand.touch()
                # Also touch the newest aider.log in this subtree, if any.
                aider_logs = list(cur.rglob("aider.log"))
                if aider_logs:
                    newest = max(aider_logs, key=lambda p: p.stat().st_mtime)
                    newest.touch()
                return
            if cur.parent == cur:
                return
            cur = cur.parent
    except OSError:
        pass


def _sleep_with_heartbeat(
    total_seconds: int,
    log_dir: Optional[Path],
    heartbeat_seconds: int = DEFAULT_HEARTBEAT_SECONDS,
) -> None:
    """Sleep up to ``total_seconds``, touching ``log_dir/.rate_limit_paused`` periodically."""
    end = time.time() + max(0, total_seconds)
    while time.time() < end:
        slice_s = min(heartbeat_seconds, end - time.time())
        if slice_s <= 0:
            break
        time.sleep(slice_s)
        _heartbeat(log_dir)


def run_with_recovery(
    fn: Callable[..., T],
    *args: Any,
    _kaiju_log_dir: Optional[Path] = None,
    max_retries: int = 1,
    **kwargs: Any,
) -> T:
    """Call ``fn(*args, **kwargs)``, pause-and-resume on rate-limit errors.

    Only active when the harness is talking to the local Claude Code bridge
    (i.e. ``ANTHROPIC_API_BASE`` points at localhost). Bedrock/Vertex/direct-API
    callers get the unwrapped exception, preserving existing behavior.
    """
    base_url = _bridge_base_url()
    if base_url is None:
        return fn(*args, **kwargs)

    effective_max_retries = _effective_max_retries(base_url, max_retries)
    max_pause = _max_pause_seconds()
    attempt = 0
    while True:
        try:
            return fn(*args, **kwargs)
        except BaseException as exc:
            if not _is_rate_limit_error(exc):
                raise
            if attempt >= effective_max_retries:
                _LOG.error(
                    "rate-limit recovery exhausted after %d retries: %s", attempt, exc
                )
                raise

            retry_after_hint = _extract_retry_after_from_error(exc) or 300
            wait_seconds = _next_reset_seconds(base_url, retry_after_hint)
            if wait_seconds > max_pause:
                _LOG.warning(
                    "rate-limit reset in %ds exceeds WCB_CC_MAX_PAUSE_SEC=%ds; giving up",
                    wait_seconds, max_pause,
                )
                raise

            _LOG.warning(
                "rate-limit hit (%s); pausing %ds (attempt %d/%d). "
                "Heartbeating dir=%s every %ds to keep the inactivity watchdog quiet.",
                type(exc).__name__, wait_seconds, attempt + 1, effective_max_retries + 1,
                _kaiju_log_dir, DEFAULT_HEARTBEAT_SECONDS,
            )
            _sleep_with_heartbeat(wait_seconds, _kaiju_log_dir)
            attempt += 1
