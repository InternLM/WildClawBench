"""
WildClawBench SubagentDirector: harness-provided sub-agent spawn primitive.

The openclaw harness exposes a ``spawn_subagent`` tool when a task opts-in via
``task_config.yaml`` ``multi_agent.enabled: true``. The parent agent calls the
tool with a role, instructions, and an allowed-tool list; this module runs the
child as a short, bounded LLM session against the same LiteLLM sidecar, then
returns the child's final text to the parent.

Two-layer split so the module is testable without HTTP / Docker / a real model:

    pure layer  -> ``run_with_invoker(spec, invoker, ...) -> SubagentResult``
                   ``invoker`` is any callable matching ``InvokerCallable``.
                   Tests pass a scripted ``FakeInvoker``.

    runtime layer -> ``LiteLLMInvoker`` (HTTP) + ``main()`` (CLI / skill entry
                     point). Reads stdin JSON spec, writes one NDJSON row to
                     ``$SPAWN_TREE_PATH`` (default
                     ``/tmp_workspace/spawn_tree.jsonl``), writes the full
                     child transcript to
                     ``/tmp_workspace/subagents/{spawn_id}.jsonl``, prints the
                     final assistant text to stdout for the parent skill.

Hard rules
----------
* No nested spawning. ``allowed_tools`` MUST NOT contain ``spawn_subagent``;
  the runtime layer enforces this and rejects with ``status='blocked'``.
* One NDJSON row per spawn. The spawn_tree row carries a *preview* of the
  child output (first 240 chars) plus a SHA-256 of the full output; the full
  transcript lives in the per-spawn file so the spawn_tree stays small.
* Bounded. ``max_tool_calls`` and ``timeout_seconds`` are capped by the
  runtime layer. ``max_tokens`` has no harness-side cap — it flows straight
  through to the upstream ``/v1/messages`` endpoint, which enforces its own
  per-model upper bound.
* Turn-correlated. The spawn row carries ``turn_index`` read from
  ``/tmp_workspace/.wildclaw_current_turn`` (written by the openclaw runner
  between turns). Missing / unreadable -> ``turn_index = -1`` (still logged).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

LOG = logging.getLogger(__name__)

# Default container-side paths. Host-side tests override via kwargs.
_DEFAULT_SPAWN_TREE_PATH = Path("/tmp_workspace/spawn_tree.jsonl")
_DEFAULT_TRANSCRIPT_DIR = Path("/tmp_workspace/subagents")
_DEFAULT_TURN_MARKER = Path("/tmp_workspace/.wildclaw_current_turn")

# Hard ceilings on tool calls + wall-clock prevent a rogue parent from
# stalling the sidecar. max_tokens is intentionally NOT capped: per-task
# tool loops may need to produce long structured answers, and the underlying
# /v1/messages endpoint already enforces its own per-model upper bound.
_MAX_TOOL_CALLS_CEILING = 50
_MAX_TIMEOUT_CEILING = 600  # seconds
_PREVIEW_CHARS = 240

_BLOCKED_TOOLS = frozenset({"spawn_subagent"})


@dataclass(frozen=True)
class SubagentSpec:
    """Parent-supplied request to spawn a single sub-agent."""

    role: str
    instructions: str
    allowed_tools: tuple[str, ...] = ()
    context: str = ""
    model: str | None = None
    max_tool_calls: int = 20
    max_tokens: int = 32000
    timeout_seconds: int = 300

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> SubagentSpec:
        tools_raw = raw.get("allowed_tools") or ()
        if not isinstance(tools_raw, (list, tuple)):
            raise ValueError("allowed_tools must be a list of strings")
        allowed_tools = tuple(str(t) for t in tools_raw)

        return cls(
            role=str(raw.get("role", "")).strip(),
            instructions=str(raw.get("instructions", "")),
            allowed_tools=allowed_tools,
            context=str(raw.get("context", "")),
            model=raw.get("model"),
            max_tool_calls=int(raw.get("max_tool_calls", 20)),
            max_tokens=int(raw.get("max_tokens", 32000)),
            timeout_seconds=int(raw.get("timeout_seconds", 300)),
        )


@dataclass
class SubagentResult:
    """Outcome of one sub-agent run.

    Token accounting matches the project-wide 5-key shape used by
    ``litellm_usage_callback`` / ``grading`` / ``judge_litellm``:
    ``input_tokens`` (non-cached), ``output_tokens``, ``cache_read_tokens``,
    ``cache_write_tokens``, and a derived ``total_tokens``. The legacy
    ``tokens_in`` / ``tokens_out`` field names are kept on the dataclass for
    backward compatibility with existing invokers and tests; new consumers
    should read the canonical names off the log row / delivery JSON.
    """

    spawn_id: str
    role: str
    output: str
    tool_calls: int = 0
    tokens_in: int = 0
    tokens_out: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    elapsed_seconds: float = 0.0
    # Effective model the invoker actually ran (spec.model is often unset and
    # falls back to WILDCLAW_MODEL at runtime); captured so cost can be priced.
    model: str | None = None
    # USD cost of this spawn, priced from tokens via litellm. 0.0 when the model
    # is unknown / unpriceable (see _subagent_cost_usd).
    cost_usd: float = 0.0
    # ok | timeout | error | blocked
    status: str = "ok"
    error: str | None = None
    # Per-HTTP-round capture from _drive_tool_loop. Each round is a dict
    # {assistant_content, tool_results, usage, stop_reason} preserving the
    # Anthropic /v1/messages content blocks so a delivery converter can
    # reshape them into the parent's toolCall/toolResult message schema.
    rounds: list[dict] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return (
            int(self.tokens_in)
            + int(self.tokens_out)
            + int(self.cache_read_tokens)
            + int(self.cache_write_tokens)
        )

    def to_log_row(
        self,
        *,
        spec: SubagentSpec,
        turn_index: int,
        parent_session_id: str | None,
    ) -> dict[str, Any]:
        out = self.output or ""
        digest = hashlib.sha256(out.encode("utf-8", "replace")).hexdigest()
        return {
            "ts": time.time(),
            "spawn_id": self.spawn_id,
            "parent_session_id": parent_session_id,
            "turn_index": turn_index,
            "role": self.role,
            "status": self.status,
            "error": self.error,
            "allowed_tools": list(spec.allowed_tools),
            # Effective model the spawn ran (resolved at runtime); falls back to
            # the spec value when the invoker didn't report one (e.g. tests).
            "model": self.model or spec.model,
            "max_tool_calls": spec.max_tool_calls,
            "max_tokens": spec.max_tokens,
            "timeout_seconds": spec.timeout_seconds,
            "tool_calls": self.tool_calls,
            # Legacy aliases kept for backcompat; canonical keys follow.
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            # Canonical 5-key cost shape (matches grading / judge / litellm
            # usage callback). cache_* default to 0 on providers without
            # prompt caching, so the keys are always present.
            "input_tokens": self.tokens_in,
            "output_tokens": self.tokens_out,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(float(self.cost_usd or 0.0), 6),
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "output_preview": out[:_PREVIEW_CHARS],
            "output_sha256": digest,
            "output_chars": len(out),
        }


# An invoker receives a system prompt + a user prompt and returns a dict:
#   {"output": str, "tool_calls": int,
#    "tokens_in": int, "tokens_out": int,
#    "cache_read_tokens": int, "cache_write_tokens": int,
#    "rounds": list[dict]}
# cache_* fields default to 0 when absent, so older invokers stay compatible.
# Tests use a FakeInvoker; production uses LiteLLMInvoker.
InvokerCallable = Callable[[str, str, SubagentSpec], Mapping[str, Any]]


def _extract_round_usage(usage: Any) -> dict[str, int]:
    """Extract the canonical 4-token shape from an Anthropic ``usage`` block.

    Raw Anthropic ``/v1/messages`` responses already split cache traffic from
    non-cached input (unlike the LiteLLM-transformed prompt_tokens path that
    ``litellm_usage_callback`` has to disentangle), so we just read the four
    fields directly and default missing ones to 0.
    """
    if not isinstance(usage, Mapping):
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
        }
    return {
        "input_tokens":       int(usage.get("input_tokens", 0) or 0),
        "output_tokens":      int(usage.get("output_tokens", 0) or 0),
        "cache_read_tokens":  int(usage.get("cache_read_input_tokens", 0) or 0),
        "cache_write_tokens": int(usage.get("cache_creation_input_tokens", 0) or 0),
    }


# Per-token USD rates by model-name substring: (input, output, cache_read,
# cache_write). subagent_director runs INSIDE the agent container, which is a
# bare Python interpreter (no litellm), so we price from a static table — the
# same approach grading._JUDGE_RATES uses for the judge council. Cache
# multipliers follow Anthropic's standard 0.1x (read) / 1.25x (write) of input.
# litellm (when importable, e.g. host-side) refines an unmatched model.
_AGENT_COST_RATES: dict[str, tuple[float, float, float, float]] = {
    "opus":   (15e-6, 75e-6, 1.5e-6, 18.75e-6),
    "sonnet": (3e-6,  15e-6, 0.3e-6, 3.75e-6),
    "haiku":  (0.8e-6, 4e-6, 0.08e-6, 1.0e-6),
}


def _subagent_cost_usd(
    model: str | None,
    in_tok: int,
    out_tok: int,
    cache_read: int = 0,
    cache_write: int = 0,
) -> float:
    """Price a sub-agent's token usage in USD. Never raises (pricing must not
    break a spawn) → returns 0.0 when the model is unknown/unset.

    Primary path is the static ``_AGENT_COST_RATES`` table (works in the bare
    container). If the model matches no table entry, fall back to litellm's
    price map when it happens to be importable (host-side). Otherwise 0.0.
    """
    if not model:
        return 0.0
    in_tok = int(in_tok or 0)
    out_tok = int(out_tok or 0)
    cache_read = int(cache_read or 0)
    cache_write = int(cache_write or 0)
    name = model.lower()
    for key, (r_in, r_out, r_cr, r_cw) in _AGENT_COST_RATES.items():
        if key in name:
            cost = (in_tok * r_in + out_tok * r_out
                    + cache_read * r_cr + cache_write * r_cw)
            return round(cost, 6)
    try:
        import litellm  # lazy: host-only refinement; absent in the agent container
        prompt_cost, completion_cost = litellm.cost_per_token(
            model=model,
            prompt_tokens=in_tok + cache_read + cache_write,
            completion_tokens=out_tok,
        )
        return round(float(prompt_cost) + float(completion_cost), 6)
    except Exception as exc:  # noqa: BLE001 — pricing must never break a spawn
        LOG.warning("[subagent_cost] could not price model=%r: %s", model, exc)
        return 0.0


def _build_system_prompt(spec: SubagentSpec) -> str:
    """Construct the constrained system prompt for the sub-agent.

    The system prompt names the role, restates the allow-list as a hard
    constraint, and forbids nested spawning even if the model has learned
    about the tool elsewhere.
    """
    tools_line = (
        ", ".join(spec.allowed_tools) if spec.allowed_tools else "(none — text-only)"
    )
    return (
        f"You are a sub-agent in role: {spec.role}.\n"
        "You were spawned by a parent agent to perform one bounded task and "
        "return a concise textual answer.\n"
        f"You may only use these tools: {tools_line}.\n"
        "You MUST NOT spawn further sub-agents. The spawn_subagent tool is "
        "unavailable to you even if you have seen it before.\n"
        f"Stop after at most {spec.max_tool_calls} tool calls and return your "
        "final answer as plain text."
    )


def _build_user_prompt(spec: SubagentSpec) -> str:
    parts = [spec.instructions.strip()]
    ctx = spec.context.strip()
    if ctx:
        parts.append("\n\n--- Additional context ---\n" + ctx)
    return "\n".join(p for p in parts if p)


def _validate_spec(spec: SubagentSpec) -> str | None:
    if not spec.role:
        return "role is required"
    if not spec.instructions.strip():
        return "instructions are required"
    blocked = sorted(set(spec.allowed_tools) & _BLOCKED_TOOLS)
    if blocked:
        return (
            "nested spawning is forbidden; allowed_tools contains: "
            + ", ".join(blocked)
        )
    if spec.max_tool_calls < 0 or spec.max_tool_calls > _MAX_TOOL_CALLS_CEILING:
        return f"max_tool_calls must be in [0, {_MAX_TOOL_CALLS_CEILING}]"
    if spec.max_tokens <= 0:
        return "max_tokens must be > 0"
    if spec.timeout_seconds <= 0 or spec.timeout_seconds > _MAX_TIMEOUT_CEILING:
        return f"timeout_seconds must be in (0, {_MAX_TIMEOUT_CEILING}]"
    return None


def run_with_invoker(
    spec: SubagentSpec,
    invoker: InvokerCallable,
    *,
    spawn_id: str | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> SubagentResult:
    """Run one sub-agent using ``invoker`` (pure, no I/O).

    ``invoker`` is responsible for HTTP / model interaction; this function
    only validates, builds prompts, dispatches once, and packages the result.
    A ``TimeoutError`` raised by the invoker becomes ``status='timeout'``;
    any other exception becomes ``status='error'``.
    """
    sid = spawn_id or _new_spawn_id()
    err = _validate_spec(spec)
    if err is not None:
        return SubagentResult(
            spawn_id=sid,
            role=spec.role or "<unspecified>",
            output="",
            status="blocked",
            error=err,
        )

    sys_prompt = _build_system_prompt(spec)
    usr_prompt = _build_user_prompt(spec)

    t0 = clock()
    try:
        raw = invoker(sys_prompt, usr_prompt, spec)
    except TimeoutError as exc:
        return SubagentResult(
            spawn_id=sid,
            role=spec.role,
            output="",
            status="timeout",
            error=str(exc) or "invoker timed out",
            elapsed_seconds=clock() - t0,
        )
    except Exception as exc:  # noqa: BLE001 — surface any invoker failure
        return SubagentResult(
            spawn_id=sid,
            role=spec.role,
            output="",
            status="error",
            error=f"{type(exc).__name__}: {exc}",
            elapsed_seconds=clock() - t0,
        )
    elapsed = clock() - t0

    if not isinstance(raw, Mapping):
        return SubagentResult(
            spawn_id=sid,
            role=spec.role,
            output="",
            status="error",
            error=f"invoker returned non-mapping: {type(raw).__name__}",
            elapsed_seconds=elapsed,
        )

    raw_rounds = raw.get("rounds") or []
    rounds = [dict(r) for r in raw_rounds if isinstance(r, Mapping)]
    # Effective model: invokers report the resolved model; fall back to the spec.
    model = str(raw.get("model") or spec.model or "") or None
    tokens_in = int(raw.get("tokens_in", 0) or 0)
    tokens_out = int(raw.get("tokens_out", 0) or 0)
    cache_read = int(raw.get("cache_read_tokens", 0) or 0)
    cache_write = int(raw.get("cache_write_tokens", 0) or 0)
    return SubagentResult(
        spawn_id=sid,
        role=spec.role,
        output=str(raw.get("output", "")),
        tool_calls=int(raw.get("tool_calls", 0) or 0),
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cache_read_tokens=cache_read,
        cache_write_tokens=cache_write,
        model=model,
        cost_usd=_subagent_cost_usd(
            model, tokens_in, tokens_out, cache_read, cache_write
        ),
        elapsed_seconds=elapsed,
        status="ok",
        rounds=rounds,
    )


def _new_spawn_id() -> str:
    return "spw_" + uuid.uuid4().hex[:12]


def read_current_turn(marker_path: Path = _DEFAULT_TURN_MARKER) -> int:
    """Read the 0-indexed current turn the openclaw runner is on.

    Returns -1 if the marker is missing or unparseable; callers should still
    log the row (the spawn happened; the absent turn just means the runner
    has not started turn tracking yet, e.g. tests).
    """
    try:
        return int(marker_path.read_text().strip())
    except (OSError, ValueError):
        return -1


def append_spawn_row(
    row: Mapping[str, Any],
    *,
    spawn_tree_path: Path = _DEFAULT_SPAWN_TREE_PATH,
) -> None:
    spawn_tree_path.parent.mkdir(parents=True, exist_ok=True)
    with spawn_tree_path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(row, ensure_ascii=False) + "\n")


def summarize_results(
    results: Iterable["SubagentResult"],
    *,
    scope: str = "batch",
) -> dict[str, Any]:
    """Aggregate per-spawn token usage into one summary row.

    Output keys match the per-spawn ``to_log_row`` canonical names so the
    same downstream aggregator code can sum across summary + per-spawn
    rows without branching. ``kind`` is fixed to ``"summary"`` and there is
    NO ``status`` field, so ``spawn_tree_checks._count_spawns_per_turn``
    (which counts rows with ``status == "ok"``) ignores summary rows.
    """
    n = 0
    n_ok = 0
    by_status: dict[str, int] = {}
    in_tok = 0
    out_tok = 0
    cr_tok = 0
    cw_tok = 0
    tool_calls = 0
    elapsed = 0.0
    cost = 0.0
    for r in results:
        n += 1
        if r.status == "ok":
            n_ok += 1
        by_status[r.status] = by_status.get(r.status, 0) + 1
        in_tok += int(r.tokens_in or 0)
        out_tok += int(r.tokens_out or 0)
        cr_tok += int(r.cache_read_tokens or 0)
        cw_tok += int(r.cache_write_tokens or 0)
        tool_calls += int(r.tool_calls or 0)
        elapsed += float(r.elapsed_seconds or 0.0)
        cost += float(r.cost_usd or 0.0)
    return {
        "ts": time.time(),
        "kind": "summary",
        "scope": scope,
        "n_spawns": n,
        "n_ok": n_ok,
        "by_status": by_status,
        "tool_calls": tool_calls,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "cache_read_tokens": cr_tok,
        "cache_write_tokens": cw_tok,
        "total_tokens": in_tok + out_tok + cr_tok + cw_tok,
        "cost_usd": round(cost, 6),
        "elapsed_seconds": round(elapsed, 3),
    }


def summarize_spawn_tree(
    spawn_tree_path: str | Path,
) -> dict[str, Any]:
    """Compute a task-level summary from every per-spawn row in the ledger.

    Skips rows that look like summary rows themselves (``kind == "summary"``)
    so re-running this against a file that already has summaries appended
    does not double-count. Missing/unreadable files yield a zero summary.
    """
    p = Path(spawn_tree_path)
    in_tok = out_tok = cr_tok = cw_tok = tool_calls = 0
    n = n_ok = 0
    by_status: dict[str, int] = {}
    elapsed = 0.0
    cost = 0.0
    if not p.is_file():
        return {
            "ts": time.time(),
            "kind": "summary",
            "scope": "task",
            "n_spawns": 0,
            "n_ok": 0,
            "by_status": {},
            "tool_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "elapsed_seconds": 0.0,
        }
    with p.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            if row.get("kind") == "summary":
                continue
            n += 1
            status = row.get("status")
            if status == "ok":
                n_ok += 1
            by_status[str(status)] = by_status.get(str(status), 0) + 1
            in_tok += int(row.get("input_tokens", row.get("tokens_in", 0)) or 0)
            out_tok += int(row.get("output_tokens", row.get("tokens_out", 0)) or 0)
            cr_tok += int(row.get("cache_read_tokens", 0) or 0)
            cw_tok += int(row.get("cache_write_tokens", 0) or 0)
            tool_calls += int(row.get("tool_calls", 0) or 0)
            elapsed += float(row.get("elapsed_seconds", 0.0) or 0.0)
            cost += float(row.get("cost_usd", 0.0) or 0.0)
    return {
        "ts": time.time(),
        "kind": "summary",
        "scope": "task",
        "n_spawns": n,
        "n_ok": n_ok,
        "by_status": by_status,
        "tool_calls": tool_calls,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "cache_read_tokens": cr_tok,
        "cache_write_tokens": cw_tok,
        "total_tokens": in_tok + out_tok + cr_tok + cw_tok,
        "cost_usd": round(cost, 6),
        "elapsed_seconds": round(elapsed, 3),
    }


_STATUS_TO_COMPLETION = {
    "ok": "completed",
    "blocked": "partial",
    "timeout": "partial",
    "error": "partial",
}


def _anthropic_block_to_delivery(block: Mapping[str, Any]) -> dict[str, Any] | None:
    t = block.get("type")
    if t == "text":
        return {"type": "text", "text": str(block.get("text", ""))}
    if t == "thinking":
        return {
            "type": "thinking",
            "thinking": str(block.get("thinking", "")),
            "thinkingSignature": str(block.get("signature", "")),
        }
    if t == "tool_use":
        inp = block.get("input") or {}
        if not isinstance(inp, Mapping):
            inp = {}
        return {
            "type": "toolCall",
            "id": block.get("id", ""),
            "name": str(block.get("name", "")),
            "arguments": dict(inp),
        }
    return None


def _tool_use_name_map(rounds: list[dict[str, Any]]) -> dict[str, str]:
    names: dict[str, str] = {}
    for rnd in rounds:
        for blk in rnd.get("assistant_content") or []:
            if not isinstance(blk, Mapping) or blk.get("type") != "tool_use":
                continue
            tu_id = blk.get("id")
            if tu_id:
                names[str(tu_id)] = str(blk.get("name", ""))
    return names


def write_subagent_delivery(
    spawn_id: str,
    *,
    spec: SubagentSpec,
    result: SubagentResult,
    sys_prompt: str,
    usr_prompt: str,
    transcript_dir: Path = _DEFAULT_TRANSCRIPT_DIR,
) -> Path:
    """Write the per-spawn delivery file ``{spawn_id}.delivery.json``.

    The on-disk shape mirrors the parent harness ``delivery.json``: a
    top-level ``meta_info`` block plus a ``messages`` list whose entries
    follow the same wrapper shape (``type='message'``, deterministic
    ``id`` / ``parentId`` chain, ``timestamp``, ``message.role`` /
    ``message.content``). Anthropic content blocks captured per round
    (``text`` / ``thinking`` / ``tool_use``) are reshaped into the
    delivery vocabulary (``text`` / ``thinking`` with ``thinkingSignature``
    / ``toolCall`` with ``arguments``). Each tool_result block becomes its
    own ``toolResult`` user message so the parent's ``toolCall`` \u2192
    ``toolResult`` pairing convention holds inside the sub-agent
    trajectory too.
    """
    transcript_dir.mkdir(parents=True, exist_ok=True)
    path = transcript_dir / f"{spawn_id}.delivery.json"

    rounds = list(result.rounds or [])
    tu_names = _tool_use_name_map(rounds)
    now_iso = _now_iso()

    messages: list[dict[str, Any]] = []
    counter = [0]
    prev_id: str | None = None

    def _next_id() -> str:
        mid = f"{spawn_id}:m{counter[0]}"
        counter[0] += 1
        return mid

    def _wrap(role: str, content: list[dict[str, Any]], extra: Mapping[str, Any] | None = None) -> dict[str, Any]:
        nonlocal prev_id
        mid = _next_id()
        body: dict[str, Any] = {"role": role, "content": content}
        if extra:
            body.update(extra)
        msg = {
            "type": "message",
            "id": mid,
            "parentId": prev_id,
            "timestamp": now_iso,
            "message": body,
        }
        prev_id = mid
        return msg

    messages.append(_wrap("system", [{"type": "text", "text": sys_prompt}]))
    messages.append(_wrap("user", [{"type": "text", "text": usr_prompt}]))

    for rnd in rounds:
        asst_blocks: list[dict[str, Any]] = []
        for blk in rnd.get("assistant_content") or []:
            if not isinstance(blk, Mapping):
                continue
            converted = _anthropic_block_to_delivery(blk)
            if converted is not None:
                asst_blocks.append(converted)
        if asst_blocks:
            messages.append(_wrap("assistant", asst_blocks))
        for tr in rnd.get("tool_results") or []:
            if not isinstance(tr, Mapping):
                continue
            tc_id = str(tr.get("tool_use_id", ""))
            tool_name = tu_names.get(tc_id, "")
            messages.append(_wrap(
                "toolResult",
                [{"type": "text", "text": str(tr.get("content", ""))}],
                extra={
                    "toolCallId": tc_id,
                    "toolName": tool_name,
                    "isError": bool(tr.get("is_error", False)),
                },
            ))

    meta_info = {
        "task_type": spec.role,
        "task_description": spec.instructions[:4000],
        "task_completion_status": _STATUS_TO_COMPLETION.get(
            result.status, result.status,
        ),
        "system_prompt": sys_prompt,
        "platform": "linux",
        "usage": {
            "input_tokens":       result.tokens_in,
            "output_tokens":      result.tokens_out,
            "cache_read_tokens":  result.cache_read_tokens,
            "cache_write_tokens": result.cache_write_tokens,
            "total_tokens":       result.total_tokens,
            "cost_usd":           round(float(result.cost_usd or 0.0), 6),
        },
    }

    payload = {"meta_info": meta_info, "messages": messages}
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def _now_iso() -> str:
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _import_subagent_tools():
    # The skill copy of this file lives at
    # /usr/lib/node_modules/openclaw/skills/spawn-subagent-connector/scripts/,
    # with ``subagent_tools.py`` as a sibling. On the host the module is
    # ``src.utils.subagent_tools``. Try host first, then fall back to the
    # sibling on sys.path.
    try:
        from src.utils import subagent_tools as st  # type: ignore
        return st
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import subagent_tools as st  # type: ignore[import-not-found]
        return st


def _drive_tool_loop(
    *,
    http_post: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    tool_dispatch: Callable[[str, Mapping[str, Any]], str],
    sys_prompt: str,
    usr_prompt: str,
    tools_schemas: list[dict],
    model: str,
    max_tokens: int,
    max_tool_calls: int,
) -> dict[str, Any]:
    """Drive an Anthropic ``/v1/messages`` tool-use loop until end_turn.

    Pure I/O is delegated to ``http_post`` (POST one round, return parsed body)
    and ``tool_dispatch`` (run one tool call, return its result as a string).
    Both are injected so this function is unit-testable with no HTTP and no
    real tool execution.

    Token usage is summed across every round. ``max_tool_calls`` is a hard
    budget across the whole spawn; once exhausted, any further ``tool_use``
    blocks in the same assistant message are answered with an ``is_error``
    tool_result telling the model to produce its final answer. ``max_rounds``
    is intentionally ``max_tool_calls + 1`` so the model always has one final
    round to emit text after exhausting its tool budget.
    """
    messages: list[dict[str, Any]] = [{"role": "user", "content": usr_prompt}]
    rounds_log: list[dict[str, Any]] = []
    total_in = 0
    total_out = 0
    total_cache_read = 0
    total_cache_write = 0
    total_tool_calls = 0
    final_text = ""
    max_rounds = max(1, max_tool_calls + 1)

    for _ in range(max_rounds):
        payload: dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "system": sys_prompt,
            "messages": messages,
        }
        if tools_schemas:
            payload["tools"] = tools_schemas
        body = http_post(payload)
        if not isinstance(body, Mapping):
            raise RuntimeError(f"non-mapping body: {type(body).__name__}")
        round_usage = _extract_round_usage(body.get("usage"))
        total_in += round_usage["input_tokens"]
        total_out += round_usage["output_tokens"]
        total_cache_read += round_usage["cache_read_tokens"]
        total_cache_write += round_usage["cache_write_tokens"]

        content = body.get("content") or []
        if not isinstance(content, list):
            content = []
        tool_uses = [
            b for b in content
            if isinstance(b, Mapping) and b.get("type") == "tool_use"
        ]
        text_blocks = [
            str(b.get("text", "")) for b in content
            if isinstance(b, Mapping) and b.get("type") == "text"
        ]
        messages.append({"role": "assistant", "content": list(content)})
        stop_reason = body.get("stop_reason")

        if not tool_uses:
            final_text = "\n".join(t for t in text_blocks if t).strip()
            rounds_log.append({
                "assistant_content": [dict(b) for b in content if isinstance(b, Mapping)],
                "tool_results": [],
                "usage": round_usage,
                "stop_reason": stop_reason,
            })
            break

        tool_results: list[dict[str, Any]] = []
        for tu in tool_uses:
            tu_id = tu.get("id")
            if total_tool_calls >= max_tool_calls:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu_id,
                    "content": "ERROR: tool-call budget exhausted; "
                               "produce your final answer now.",
                    "is_error": True,
                })
                continue
            name = str(tu.get("name", ""))
            tool_input = tu.get("input") or {}
            if not isinstance(tool_input, Mapping):
                tool_input = {}
            try:
                result_str = tool_dispatch(name, tool_input)
            except Exception as exc:  # noqa: BLE001 — surface tool failure to model
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu_id,
                    "content": f"ERROR: {type(exc).__name__}: {exc}",
                    "is_error": True,
                })
            else:
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu_id,
                    "content": str(result_str),
                })
            total_tool_calls += 1
        messages.append({"role": "user", "content": tool_results})
        rounds_log.append({
            "assistant_content": [dict(b) for b in content if isinstance(b, Mapping)],
            "tool_results": [dict(r) for r in tool_results],
            "usage": round_usage,
            "stop_reason": stop_reason,
        })
    else:
        final_text = (
            "(no final answer produced before tool-call budget exhausted)"
        )

    return {
        "output": final_text,
        "tool_calls": total_tool_calls,
        "tokens_in": total_in,
        "tokens_out": total_out,
        "cache_read_tokens": total_cache_read,
        "cache_write_tokens": total_cache_write,
        "rounds": rounds_log,
    }


class LiteLLMInvoker:
    """HTTP invoker that talks to the LiteLLM sidecar's ``/v1/messages``.

    Drives a real Anthropic-format tool-use loop: passes the tool schemas
    from ``subagent_tools.schemas_for(spec.allowed_tools)`` on every round,
    dispatches each ``tool_use`` block through ``subagent_tools.dispatch``,
    and feeds the results back as ``tool_result`` user messages until the
    model emits a final text-only response (``stop_reason == end_turn``).
    """

    def __init__(
        self,
        *,
        base_url: str,
        default_model: str,
        api_key: str | None = None,
    ):
        if not base_url:
            raise ValueError("LiteLLMInvoker requires base_url")
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.api_key = api_key

    def __call__(
        self, sys_prompt: str, usr_prompt: str, spec: SubagentSpec
    ) -> Mapping[str, Any]:
        # Lazy imports: requests is a runtime dep; subagent_tools lives next
        # to this file inside the container skill bundle.
        import requests  # type: ignore[import-not-found]

        st = _import_subagent_tools()
        tools_schemas = st.schemas_for(spec.allowed_tools)
        model = spec.model or self.default_model

        headers: dict[str, str] = {
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
            headers["x-api-key"] = self.api_key

        url = f"{self.base_url}/v1/messages"

        def _http_post(payload: Mapping[str, Any]) -> Mapping[str, Any]:
            try:
                resp = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=spec.timeout_seconds,
                )
            except requests.Timeout as exc:  # type: ignore[attr-defined]
                raise TimeoutError(str(exc)) from exc
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"LiteLLM {resp.status_code}: {resp.text[:200]}"
                )
            return resp.json()

        out = dict(_drive_tool_loop(
            http_post=_http_post,
            tool_dispatch=st.dispatch,
            sys_prompt=sys_prompt,
            usr_prompt=usr_prompt,
            tools_schemas=tools_schemas,
            model=model,
            max_tokens=spec.max_tokens,
            max_tool_calls=spec.max_tool_calls,
        ))
        # Report the resolved model so run_with_invoker can price the spawn.
        out.setdefault("model", model)
        return out


def _make_invoker_from_env() -> LiteLLMInvoker:
    base = os.environ.get("LITELLM_BASE_URL") or os.environ.get("LITELLM_URL")
    if not base:
        raise RuntimeError(
            "LITELLM_BASE_URL is not set in the sub-agent environment"
        )
    model = (
        os.environ.get("WILDCLAW_SUBAGENT_MODEL")
        or os.environ.get("WILDCLAW_MODEL")
        or "claude-opus-4-7"
    )
    return LiteLLMInvoker(
        base_url=base,
        default_model=model,
        api_key=os.environ.get("LITELLM_API_KEY") or os.environ.get("OPENAI_API_KEY"),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Skill entry point. Reads spec JSON from stdin, prints text to stdout."""
    parser = argparse.ArgumentParser(
        description="Run one WildClawBench sub-agent."
    )
    parser.add_argument(
        "--spawn-tree",
        type=Path,
        default=_DEFAULT_SPAWN_TREE_PATH,
        help="Path to the spawn_tree.jsonl ledger (one NDJSON row appended).",
    )
    parser.add_argument(
        "--transcript-dir",
        type=Path,
        default=_DEFAULT_TRANSCRIPT_DIR,
        help="Directory for per-spawn full transcripts.",
    )
    parser.add_argument(
        "--turn-marker",
        type=Path,
        default=_DEFAULT_TURN_MARKER,
        help="File holding the openclaw runner's current 0-indexed turn.",
    )
    args = parser.parse_args(argv)

    try:
        raw = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError as exc:
        print(f"subagent_director: invalid JSON on stdin: {exc}", file=sys.stderr)
        return 2

    # Batch mode: stdin is either a bare list of specs or {"specs": [...]}.
    # Hard concurrency cap of _MAX_PARALLEL_SPAWNS (=5) keeps a single parent
    # turn from saturating the sidecar; results are emitted in completion order
    # as one JSON object per line, so the parent skill can stream them back.
    batch: list | None = None
    if isinstance(raw, list):
        batch = raw
    elif isinstance(raw, dict) and isinstance(raw.get("specs"), list):
        batch = raw["specs"]

    try:
        invoker = _make_invoker_from_env()
    except Exception as exc:  # noqa: BLE001
        print(f"subagent_director: cannot build invoker: {exc}", file=sys.stderr)
        return 2

    if batch is not None:
        return _run_batch_main(
            batch,
            invoker=invoker,
            spawn_tree=args.spawn_tree,
            transcript_dir=args.transcript_dir,
            turn_marker=args.turn_marker,
        )

    try:
        spec = SubagentSpec.from_dict(raw)
    except Exception as exc:  # noqa: BLE001
        print(f"subagent_director: bad spec: {exc}", file=sys.stderr)
        return 2

    sys_prompt = _build_system_prompt(spec)
    usr_prompt = _build_user_prompt(spec)
    result = run_with_invoker(spec, invoker)

    turn_index = read_current_turn(args.turn_marker)
    parent_session = os.environ.get("WILDCLAW_PARENT_SESSION_ID")

    row = result.to_log_row(
        spec=spec, turn_index=turn_index, parent_session_id=parent_session
    )
    try:
        append_spawn_row(row, spawn_tree_path=args.spawn_tree)
        append_spawn_row(
            summarize_results([result], scope="single"),
            spawn_tree_path=args.spawn_tree,
        )
        write_subagent_delivery(
            result.spawn_id,
            spec=spec,
            result=result,
            sys_prompt=sys_prompt,
            usr_prompt=usr_prompt,
            transcript_dir=args.transcript_dir,
        )
    except OSError as exc:
        # Logging failed but the spawn itself ran; surface to parent on stderr
        # and still return the output so the parent isn't stuck.
        print(
            f"subagent_director: spawn_tree write failed: {exc}", file=sys.stderr
        )

    if result.status != "ok":
        # Parent skill sees the error in stderr; stdout still carries whatever
        # text the model produced (often empty for blocked/timeout/error).
        print(
            f"subagent_director: status={result.status} error={result.error}",
            file=sys.stderr,
        )
    sys.stdout.write(result.output)
    return 0 if result.status == "ok" else 1


_MAX_PARALLEL_SPAWNS = 5


def run_batch_parallel(
    specs: Sequence[SubagentSpec],
    invoker: "InvokerCallable",
    *,
    max_concurrency: int = _MAX_PARALLEL_SPAWNS,
) -> list[SubagentResult]:
    """Run multiple SubagentSpec in parallel via a thread pool.

    Returns results in *completion* order (not input order) so a slow spawn
    cannot block the parent from acting on faster siblings. Each result still
    carries its own ``spawn_id`` for downstream correlation. Concurrency is
    capped at ``min(len(specs), max_concurrency, _MAX_PARALLEL_SPAWNS)``.
    """
    import concurrent.futures
    cap = max(1, min(len(specs) or 1, int(max_concurrency), _MAX_PARALLEL_SPAWNS))
    if not specs:
        return []
    results: list[SubagentResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=cap) as pool:
        futures = [pool.submit(run_with_invoker, s, invoker) for s in specs]
        for fut in concurrent.futures.as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as exc:  # noqa: BLE001 - surface as error row
                results.append(SubagentResult(
                    spawn_id=_new_spawn_id(),
                    role="<unknown>",
                    output="",
                    tool_calls=0,
                    tokens_in=0,
                    tokens_out=0,
                    cache_read_tokens=0,
                    cache_write_tokens=0,
                    elapsed_seconds=0.0,
                    status="error",
                    error=f"{type(exc).__name__}: {exc}",
                ))
    return results


def _run_batch_main(
    raw_specs: list,
    *,
    invoker: "InvokerCallable",
    spawn_tree: Path,
    transcript_dir: Path,
    turn_marker: Path,
) -> int:
    specs: list[SubagentSpec] = []
    for i, raw in enumerate(raw_specs):
        try:
            specs.append(SubagentSpec.from_dict(raw))
        except Exception as exc:  # noqa: BLE001
            print(
                f"subagent_director: batch[{i}] bad spec: {exc}", file=sys.stderr
            )
            return 2

    results = run_batch_parallel(specs, invoker)
    turn_index = read_current_turn(turn_marker)
    parent_session = os.environ.get("WILDCLAW_PARENT_SESSION_ID")

    by_spawn_id = {r.spawn_id: r for r in results}
    spec_by_role = {s.role: s for s in specs}

    any_error = False
    for result in results:
        spec = spec_by_role.get(result.role)
        if spec is None:
            spec = specs[0]
        row = result.to_log_row(
            spec=spec, turn_index=turn_index, parent_session_id=parent_session
        )
        try:
            append_spawn_row(row, spawn_tree_path=spawn_tree)
            write_subagent_delivery(
                result.spawn_id,
                spec=spec,
                result=result,
                sys_prompt=_build_system_prompt(spec),
                usr_prompt=_build_user_prompt(spec),
                transcript_dir=transcript_dir,
            )
        except OSError as exc:
            print(
                f"subagent_director: batch spawn_tree write failed: {exc}",
                file=sys.stderr,
            )
        if result.status != "ok":
            any_error = True
        # stdout stays intentionally light — parent's output.json should only
        # see the agent response. Full token/cost telemetry lives on disk in
        # spawn_tree.jsonl (per-spawn row + appended summary row below) and
        # in each {spawn_id}.delivery.json meta_info.usage block.
        sys.stdout.write(json.dumps({
            "spawn_id": result.spawn_id,
            "role": result.role,
            "status": result.status,
            "output": result.output,
            "error": result.error,
            "tokens_in": result.tokens_in,
            "tokens_out": result.tokens_out,
            "tool_calls": result.tool_calls,
        }) + "\n")

    try:
        append_spawn_row(
            summarize_results(results, scope="batch"),
            spawn_tree_path=spawn_tree,
        )
    except OSError as exc:
        print(
            f"subagent_director: batch summary write failed: {exc}",
            file=sys.stderr,
        )
    return 1 if any_error else 0


if __name__ == "__main__":  # pragma: no cover - CLI dispatch
    raise SystemExit(main())
