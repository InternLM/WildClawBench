"""LiteLLM + Headroom transport for the judge council (opt-in).

This module is the SECOND transport for the rubric judge council. The original
host-side urllib transport lives in `grading.py` (`_call_judge_bedrock` /
`_call_judge_openai`) and remains the default. When the env flag
`KENSEI_JUDGE_USE_LITELLM` is on, `grading._call_one_judge` routes here first
and falls back to urllib on any exception — grading is the harness's promise
to a task and MUST NEVER fail because of a transport choice.

Why this module exists
----------------------
Headroom (https://github.com/chopratejas/headroom, PyPI `headroom-ai`) is a
prompt-compression tool. Its README suggests
`litellm.callbacks = [HeadroomCallback()]`, but LiteLLM's own docs mark the
mutating `async_pre_call_hook` as **proxy-only** — in library mode (which is
what we use here, no proxy), callbacks are observe-only and CANNOT rewrite
the outgoing messages. So we use the explicit `compress()` call BEFORE
`litellm.completion()` instead. More debuggable too — each call returns a
`CompressResult` with full transform telemetry.

Env vars (read at call time, NOT cached at import)
---------------------------------------------------
  KENSEI_JUDGE_USE_LITELLM            bool  default false  — master toggle
  KENSEI_JUDGE_HEADROOM_ENABLED       bool  default true   — compression switch
  KENSEI_JUDGE_HEADROOM_TARGET_RATIO  float default 0.4    — target compress ratio
  KENSEI_JUDGE_HEADROOM_PROTECT_RECENT int default 2       — protected message count
  KENSEI_JUDGE_HEADROOM_MIN_TOKENS    int   default 2000   — skip below this size

Token tracking invariants (DO NOT BREAK)
----------------------------------------
The per-judge `usage` dict shape returned by `call_judge_via_litellm()` MUST
match the existing shape produced by `_call_judge_bedrock` / `_call_judge_openai`
exactly (8 keys: input_tokens, output_tokens, cache_read_tokens,
cache_write_tokens, total_tokens, request_count, cost_usd, cost_priced_ok). The
`headroom` sub-dict is purely additive and harmless to readers that don't expect it.

The JSONL log at `litellm_usage_callback.py` (10-key schema) is for AGENT
calls through the per-batch sidecar — NOT touched by this module.
"""
from __future__ import annotations

import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)


# ---------- env-flag helpers (read live every call; never cached) ----------

def _truthy(val: str | None) -> bool:
    if val is None:
        return False
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def judge_use_litellm() -> bool:
    """Master toggle. False = use legacy urllib path in grading.py."""
    return _truthy(os.environ.get("KENSEI_JUDGE_USE_LITELLM"))


def _judge_oauth_bridge_url() -> str:
    """Master gate for routing the Sonnet judge through the Claude Max OAuth
    bridge. Empty/unset = judge uses Bedrock/OpenAI as before. When set (e.g.
    http://127.0.0.1:<port>), the sonnet judge's litellm.completion is pointed
    at the host-published cc-bridge instead of Bedrock."""
    return (os.environ.get("KENSEI_JUDGE_OAUTH_BRIDGE_URL") or "").strip()


def _judge_oauth_bridge_model() -> str:
    """Model id sent on the bridge route. The bridge normalizes the exact tail
    upstream, so this only needs to be a valid anthropic/ sonnet id."""
    return (
        os.environ.get("KENSEI_JUDGE_OAUTH_BRIDGE_MODEL")
        or "anthropic/claude-sonnet-4-5-20250929"
    ).strip()


def judge_headroom_enabled() -> bool:
    """Compression switch. Default on when set empty/unset; allows A/B
    testing LiteLLM-without-compression by setting this to false explicitly."""
    raw = os.environ.get("KENSEI_JUDGE_HEADROOM_ENABLED")
    if raw is None or str(raw).strip() == "":
        return True
    return _truthy(raw)


def _headroom_target_ratio() -> float:
    raw = os.environ.get("KENSEI_JUDGE_HEADROOM_TARGET_RATIO")
    if not raw:
        return 0.4
    try:
        return float(raw)
    except ValueError:
        return 0.4


def _headroom_protect_recent() -> int:
    raw = os.environ.get("KENSEI_JUDGE_HEADROOM_PROTECT_RECENT")
    if not raw:
        return 2
    try:
        return int(raw)
    except ValueError:
        return 2


def _headroom_min_tokens() -> int:
    raw = os.environ.get("KENSEI_JUDGE_HEADROOM_MIN_TOKENS")
    if not raw:
        return 2000
    try:
        return int(raw)
    except ValueError:
        return 2000


# ---------- litellm.register_model() for judge ARNs ----------
#
# LiteLLM's Bedrock layer extracts the model id from ARNs via
# `extract_model_name_from_bedrock_arn(model.split('/')[-1])`. The
# application-inference-profile tail is an opaque ID that is NOT in
# `model_prices_and_context_window.json`, so `get_model_info()` returns defaults
# and per-model `max_input_tokens` / cost enforcement is wrong without
# explicit registration.
#
# ROTATION-SAFE: the company rotates council ARNs monthly, so the opaque tail
# is NOT a stable key. The registry is built per batch from the CURRENT council
# members — each member's stable FAMILY supplies the rates (grading._FAMILY_RATES,
# the single source of truth) and ctx/max_output (grading._FAMILY_EVIDENCE); the
# member's current (rotated) ARN tail is what we register. This eliminates the
# stale duplicate rate table that previously drifted from grading.py.

_registered_tails: set[str] = set()


def _arn_tail(model: str) -> str:
    return (model or "").rsplit("/", 1)[-1]


_ARN_REGION_RE = re.compile(r"^arn:aws:bedrock:([a-z0-9-]+):")


def _litellm_model_and_region(model: str) -> tuple[str, str | None]:
    # A bare Bedrock application-inference-profile ARN has provider=None as far
    # as litellm is concerned, so litellm.completion(model=<arn>) raises
    # NotFoundError "Unknown provider=None ... Try calling via converse". Prefix
    # it as bedrock/converse/<arn> so litellm routes to the Converse handler, and
    # return the ARN's own region (GLM council member is us-east-1 while the
    # batch default is ap-south-1) so the call hits the right regional endpoint.
    # Non-Bedrock judges (openai/<model>, gpt-5.x) pass through unchanged.
    m = (model or "").strip()
    if m.startswith("bedrock/"):
        m = m[len("bedrock/"):]
    if m.startswith("arn:aws:bedrock:") or ":application-inference-profile/" in m:
        match = _ARN_REGION_RE.match(m)
        region = match.group(1) if match else None
        return f"bedrock/converse/{m}", region
    return model, None


def register_judges_for_batch(members) -> None:
    """Register each CURRENT council member's ARN tail with LiteLLM, keyed by
    the member's stable family rates. Idempotent per tail (a rotated tail
    re-registers fresh; an unchanged tail is skipped), so repeated calls within
    a batch are cheap and rotations never accumulate dead pricing entries beyond
    what LiteLLM's additive register_model leaves behind. Failure to register is
    logged and never re-raised — LiteLLM falls back to defaults, calls still
    succeed, per-model enforcement is merely loose. Always safe to call."""
    try:
        import litellm  # type: ignore
    except ImportError:
        logger.warning(
            "litellm not importable; judge council cannot use LiteLLM transport "
            "(falling back to urllib path inside grading.py)"
        )
        return

    from . import grading

    for member in members:
        tail = _arn_tail(member.model)
        if not tail or tail in _registered_tails:
            continue
        rates = grading._FAMILY_RATES.get(member.family)
        evidence = grading._FAMILY_EVIDENCE.get(member.family)
        if rates is None or evidence is None:
            logger.warning(
                "no _FAMILY_RATES/_FAMILY_EVIDENCE for family=%r (member %s); "
                "skipping registration, call will use LiteLLM defaults",
                member.family, tail,
            )
            continue
        r_in, r_out, r_cr, r_cw = rates
        ctx, max_out = evidence
        try:
            litellm.register_model({
                tail: {
                    "max_tokens": ctx,
                    "max_input_tokens": ctx,
                    "max_output_tokens": max_out,
                    "input_cost_per_token": r_in,
                    "output_cost_per_token": r_out,
                    "cache_read_input_token_cost": r_cr,
                    "cache_creation_input_token_cost": r_cw,
                    "litellm_provider": "bedrock_converse",
                    "mode": "chat",
                }
            })
            _registered_tails.add(tail)
        except Exception as exc:  # pragma: no cover (LiteLLM schema drift)
            logger.warning(
                "litellm.register_model failed for %s: %s — call will use LiteLLM defaults",
                tail, exc,
            )


# ---------- Headroom compression wrapper ----------

def maybe_compress(messages: list[dict], model: str) -> tuple[list[dict], dict]:
    """Best-effort Headroom compression. NEVER raises.

    Returns (messages, stats) where messages is the (possibly compressed)
    list and stats is `{}` on skip/failure OR a dict containing the keys
    {tokens_before, tokens_after, tokens_saved, compression_ratio,
     transforms_applied}.

    Critical config decisions:
      - compress_user_messages=True   — judges' evidence lives in user turn
      - compress_system_messages=False — system prompt encodes the verdict
        format that `_VERDICT_RE` regexes against; compressing it risks
        breaking the regex and silently zeroing all council votes.
      - ARN tokenizer hint: when model contains `application-inference-profile`,
        Headroom can't infer a tokenizer from the opaque ID, so we pass
        `anthropic/claude-sonnet-4-5-20250929` as the model= hint. The judges
        are all Anthropic-protocol-compatible on Bedrock; this is a safe hint
        for counting alone (does NOT change the model LiteLLM actually calls)."""
    if not judge_headroom_enabled():
        return messages, {}

    try:
        from headroom import compress, CompressConfig  # type: ignore
    except ImportError:
        # Headroom not installed; silent no-op so KENSEI_JUDGE_USE_LITELLM=true
        # alone still works without headroom-ai installed.
        return messages, {}
    except Exception as exc:  # pragma: no cover (defensive)
        logger.warning("headroom import raised %s — skipping compression", exc)
        return messages, {}

    # Tokenizer hint for opaque Bedrock ARNs.
    if "application-inference-profile" in (model or ""):
        model_hint = "anthropic/claude-sonnet-4-5-20250929"
    else:
        model_hint = model

    try:
        cfg = CompressConfig(
            compress_user_messages=True,
            compress_system_messages=False,
            protect_recent=_headroom_protect_recent(),
            min_tokens_to_compress=_headroom_min_tokens(),
            target_ratio=_headroom_target_ratio(),
        )
    except Exception as exc:  # pragma: no cover (CompressConfig schema drift)
        logger.warning("CompressConfig construction failed: %s — skipping compression", exc)
        return messages, {}

    try:
        result = compress(messages, model=model_hint, config=cfg)
    except Exception as exc:
        logger.warning("headroom.compress raised %s — sending uncompressed", exc)
        return messages, {}

    tokens_before = int(getattr(result, "tokens_before", 0) or 0)
    tokens_after = int(getattr(result, "tokens_after", 0) or 0)
    tokens_saved = int(getattr(result, "tokens_saved", 0) or 0)
    compression_ratio = float(getattr(result, "compression_ratio", 0.0) or 0.0)
    transforms = list(getattr(result, "transforms_applied", []) or [])
    new_messages = getattr(result, "messages", None) or messages

    if tokens_saved <= 0:
        # Record the no-op too — useful for telemetry to confirm we tried.
        return messages, {
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "tokens_saved": 0,
            "compression_ratio": compression_ratio,
            "transforms_applied": [],
        }

    return new_messages, {
        "tokens_before": tokens_before,
        "tokens_after": tokens_after,
        "tokens_saved": tokens_saved,
        "compression_ratio": compression_ratio,
        "transforms_applied": transforms,
    }


# ---------- LiteLLM-backed judge call ----------

def call_judge_via_litellm(
    model: str,
    system: str,
    user: str,
    max_output_tokens: int,
    cost_fn: Any,
    family: str | None = None,
) -> tuple[str, dict]:
    """LiteLLM-backed judge call with optional Headroom compression.

    Returns the same `(raw_text, usage_dict)` tuple shape as
    `grading._call_judge_bedrock` / `grading._call_judge_openai`, so
    `grading._run_council`'s `_one()` is transport-agnostic.

    `cost_fn` is `grading._judge_cost_usd` injected to avoid a circular
    import. `max_output_tokens` is `grading._member_max_output_tokens(arn)`.
    `family` is the stable council family ('sonnet'/'glm'/'kimi') threaded so
    cost resolution survives monthly ARN rotation; None for non-council judges.

    Raises on any LiteLLM error so `grading._call_one_judge` can fall back
    to the urllib transport. This is intentional: grading must NEVER fail
    because LiteLLM had a bad day."""
    import litellm  # type: ignore  (deliberate: ImportError surfaces as a fall-back trigger)

    if family is not None:
        from typing import cast as _cast

        from .grading import CouncilMember, JudgeFamily
        register_judges_for_batch(
            [CouncilMember(family=_cast(JudgeFamily, family), model=model)]
        )

    call_model, region = _litellm_model_and_region(model)

    # System-prompt caching: the council system prompt is large and IDENTICAL
    # across all members, so marking it with cache_control lets the first member
    # write it to Bedrock's prompt cache (~5 min TTL) and the rest read it back
    # at the cache-read rate instead of re-paying full input. This is the litellm
    # equivalent of the urllib path's `cachePoint` block. Gated on family caching
    # support (Kimi/GLM 403 on cachePoint) so only Anthropic Sonnet caches; the
    # content-list shape is required for cache_control to attach per-block.
    from . import grading
    if family is not None and grading._supports_prompt_caching(model, family):
        system_content: Any = [
            {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
        ]
    else:
        system_content = system

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user},
    ]

    # Headroom (best-effort, never raises)
    messages, compression_stats = maybe_compress(messages, model)

    # Sanity: judges MUST NOT receive `thinking`, `reasoning_effort`,
    # `output_config`, or `response_format` — those silently change the
    # output character and break `_VERDICT_RE` parsing. Pass nothing extra.
    # `drop_params=True` lets LiteLLM silently strip params a provider
    # doesn't accept (verified live: Bedrock application-inference-profile
    # ARNs for Sonnet/Kimi/GLM reject `temperature` → UnsupportedParamsError).
    # The urllib fallback path retries-without-temperature on the same
    # error; this is the LiteLLM-side equivalent.
    _bearer = os.environ.get("KENSEI_AWS_BEARER_TOKEN") or os.environ.get(
        "AWS_BEARER_TOKEN_BEDROCK"
    )
    if _bearer:
        os.environ["AWS_BEARER_TOKEN_BEDROCK"] = _bearer
    
    completion_kwargs: dict[str, Any] = {
        "model": call_model,
        "messages": messages,
        "max_tokens": max_output_tokens,
        "temperature": 0,
        "stream": False,
        "drop_params": True,
    }
    if region:
        completion_kwargs["aws_region_name"] = region

    # OAuth-bridge route: send the sonnet judge to the cc-bridge (Claude Max
    # subscription) instead of Bedrock. Transparent Anthropic-Messages proxy,
    # host-published at KENSEI_JUDGE_OAUTH_BRIDGE_URL; auth = stub key +
    # x-wcb-bridge-secret co-tenant guard. Overrides any Bedrock region.
    bridge_url = _judge_oauth_bridge_url()
    if bridge_url and family == "sonnet":
        completion_kwargs["model"] = _judge_oauth_bridge_model()
        completion_kwargs["api_base"] = bridge_url
        completion_kwargs["api_key"] = os.environ.get(
            "WCB_CC_STUB_KEY", "sk-wcb-oauth-stub"
        )
        completion_kwargs["extra_headers"] = {
            "x-wcb-bridge-secret": os.environ.get("WCB_CC_BRIDGE_SECRET", ""),
        }
        completion_kwargs.pop("aws_region_name", None)

    # Live-stream liveness (docs/STREAMING_PLAN.md D4): this judge call stays
    # NON-streaming by decision (`"stream": False` above is untouched), so the
    # display feed gets exactly two status events — started/finished — instead
    # of token deltas. stream_events.emit() is a guaranteed no-raise no-op
    # unless WCB_STREAM is on.
    from src.utils import stream_events as _stream
    import uuid as _uuid
    _sid = _uuid.uuid4().hex[:12]
    _stream.emit(f"judge:{family}", "status", _sid, kind="status",
                 delta="verdict request started (non-streaming)",
                 model=str(completion_kwargs.get("model") or ""))
    try:
        response = litellm.completion(**completion_kwargs)
    except Exception:
        _stream.emit(f"judge:{family}", "error", _sid, kind="status",
                     delta="verdict request failed",
                     model=str(completion_kwargs.get("model") or ""))
        raise
    _stream.emit(f"judge:{family}", "status", _sid, kind="status",
                 delta="verdict received",
                 model=str(completion_kwargs.get("model") or ""))

    # Extract text. LiteLLM normalizes to OpenAI shape across providers.
    try:
        raw = response.choices[0].message.content or ""
    except (AttributeError, IndexError) as exc:
        raise RuntimeError(f"litellm response shape unexpected: {exc}") from exc

    # Extract usage. LiteLLM normalizes to OpenAI shape but Bedrock under
    # the hood may fold cache_read/cache_write back INTO prompt_tokens. The
    # invariant: returned `input_tokens` must be non-cached only (matches
    # both _call_judge_bedrock and _call_judge_openai semantics).
    u = getattr(response, "usage", None) or {}
    def _gi(obj: Any, name: str) -> int:
        if isinstance(obj, dict):
            v = obj.get(name)
        else:
            v = getattr(obj, name, None)
        try:
            return int(v or 0)
        except (TypeError, ValueError):
            return 0

    prompt_tok = _gi(u, "prompt_tokens")
    comp_tok = _gi(u, "completion_tokens")
    cache_read = _gi(u, "cache_read_input_tokens")
    if not cache_read:
        # OpenAI shape (prompt_tokens_details.cached_tokens)
        details = u.get("prompt_tokens_details") if isinstance(u, dict) else getattr(u, "prompt_tokens_details", None)
        if details:
            cache_read = _gi(details, "cached_tokens")
    cache_write = _gi(u, "cache_creation_input_tokens")

    # Bedrock's `inputTokens` excludes cache by convention; OpenAI's
    # `prompt_tokens` includes cached_tokens. LiteLLM's normalization
    # rolls cache back into prompt_tokens on Bedrock — subtract to maintain
    # the "input_tokens = non-cached" invariant shared with the urllib path.
    input_excl = max(0, prompt_tok - cache_read - cache_write)

    cost_usd, priced_ok = cost_fn(model, input_excl, comp_tok, cache_read, cache_write, family)

    usage = {
        "input_tokens": input_excl,
        "output_tokens": comp_tok,
        "cache_read_tokens": cache_read,
        "cache_write_tokens": cache_write,
        "total_tokens": input_excl + comp_tok + cache_read + cache_write,
        "request_count": 1,
        "cost_usd": float(cost_usd),
        "cost_priced_ok": priced_ok,
        # Additive: never read by existing code paths. New aggregator in
        # `_grade_council` collects these for `score.json.judge_council`.
        "headroom": compression_stats,
    }
    return raw, usage
