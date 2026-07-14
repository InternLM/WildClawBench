"""Read & sanitize OpenClaw session JSONL files.

Ports `_read_jsonl_local` and `_sanitize_jsonl_message` from
`custom_addons/kensei2/models/kensei2_sandbox.py` with the Odoo
machinery removed.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Iterable, List, Mapping, MutableMapping

_logger = logging.getLogger(__name__)

# Keep per-turn metadata in the exported trajectory so output.json shows
# "everything" (model, provider, usage, stopReason, api, thinking/reasoning
# blocks). Only the truly-internal routing field `sender` is stripped.
_INTERNAL_MSG_FIELDS = {"sender"}
_INTERNAL_BLOCK_FIELDS: set = set()


def read_session_jsonl(workdir: str | os.PathLike, persona_name: str) -> List[dict]:
    """Return flat list of JSONL entries from the openclaw sessions dir.

    Files are concatenated in mtime order.
    """
    workdir = Path(workdir)
    sessions_dir = workdir / "data" / persona_name / "agents" / "main" / "sessions"
    if not sessions_dir.is_dir():
        _logger.warning("Sessions dir not found: %s", sessions_dir)
        return []

    files = sorted(
        (p for p in sessions_dir.iterdir() if p.suffix == ".jsonl"),
        key=lambda p: p.stat().st_mtime,
    )
    if not files:
        _logger.warning("No JSONL files in %s", sessions_dir)
        return []

    entries: List[dict] = []
    for path in files:
        with path.open("r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def _read_jsonl_file(path: Path) -> List[dict]:
    """Parse one ``.jsonl`` file into a list of entry dicts (skipping bad lines)."""
    out: List[dict] = []
    with path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _session_id_of(entries: List[dict]) -> str | None:
    """Return the session id from a session file's header entry, if present.

    OpenClaw writes each session file with a leading
    ``{"type": "session", "id": "<session-id>", ...}`` header (verified against
    captured ``chat.jsonl``). The main headless run uses ``--session-id chat``;
    native ``sessions_spawn`` children get their own files whose header id is the
    subagent session id (e.g. ``agent:main:subagent:<uuid>``), which is how we
    tell parent from child without concatenating them.
    """
    for e in entries:
        if isinstance(e, dict) and e.get("type") == "session":
            sid = e.get("id")
            return str(sid) if sid is not None else None
    return None


def read_sessions_grouped(
    workdir: str | os.PathLike,
    persona_name: str,
    *,
    main_session_id: str = "chat",
) -> dict:
    """Group the OpenClaw sessions dir into the main session and its children.

    Returns ``{"main": [entries], "children": {session_id: [entries], ...}}``.

    Unlike :func:`read_session_jsonl` (which concatenates every ``.jsonl`` in
    mtime order — fine when there is only one session, but it would silently
    merge native ``sessions_spawn`` child sessions into the parent), this keys
    off each file's ``session`` header id. The file whose header id equals
    ``main_session_id`` is the parent; all others are children, ordered by file
    mtime (spawn order). A file without a recognizable header is treated as part
    of ``main`` for backward compatibility.

    NOTE (validate-later): the exact on-disk filename / header-id string OpenClaw
    uses for a *headless* subagent session is confirmed in shape but not yet from
    a live native run; ``main_session_id`` is parameterized so the runner can
    pass whatever ``--session-id`` it launched with.
    """
    workdir = Path(workdir)
    sessions_dir = workdir / "data" / persona_name / "agents" / "main" / "sessions"
    result: dict = {"main": [], "children": {}}
    if not sessions_dir.is_dir():
        _logger.warning("Sessions dir not found: %s", sessions_dir)
        return result

    files = sorted(
        (p for p in sessions_dir.iterdir() if p.suffix == ".jsonl"),
        key=lambda p: p.stat().st_mtime,
    )
    for path in files:
        entries = _read_jsonl_file(path)
        if not entries:
            continue
        sid = _session_id_of(entries)
        if sid is None or sid == main_session_id:
            result["main"].extend(entries)
        else:
            result["children"][sid] = entries
    return result


def _count_thinking(content) -> tuple[int, int, bool]:
    """Return (n_thinking_blocks, first_thinking_len, has_signature)."""
    if not isinstance(content, list):
        return 0, 0, False
    n, first_len, has_sig = 0, 0, False
    for block in content:
        if isinstance(block, dict) and block.get("type") == "thinking":
            n += 1
            txt = block.get("thinking", "")
            if n == 1 and isinstance(txt, str):
                first_len = len(txt)
            if block.get("thinkingSignature"):
                has_sig = True
    return n, first_len, has_sig


def _thinking_stats(content) -> tuple[int, int, bool]:
    """Return (block_count, first_thinking_len, has_signature) for a content list.

    Mirrors kensei2/models/kensei2_sandbox.py `_count_thinking_blocks`.
    """
    if not isinstance(content, list):
        return 0, 0, False
    count = 0
    first_len = 0
    has_sig = False
    for block in content:
        if isinstance(block, dict) and block.get("type") == "thinking":
            count += 1
            if count == 1:
                text = block.get("thinking", "")
                first_len = len(text) if isinstance(text, str) else 0
                has_sig = bool(block.get("thinkingSignature"))
    return count, first_len, has_sig


def sanitize_jsonl_message(msg: Mapping) -> dict:
    """Strip internal OpenClaw metadata from a JSONL message before export.

    Logs `[THINKING-DEBUG]` BEFORE/AFTER counters so an operator can audit
    whether any thinking block was accidentally lost during sanitisation
    (mirrors `_sanitize_jsonl_message` in kensei2/models/kensei2_sandbox.py).
    """
    role = msg.get("role", "") if isinstance(msg, Mapping) else ""
    before_count, before_len, before_sig = _thinking_stats(msg.get("content"))
    if before_count:
        _logger.info(
            "[THINKING-DEBUG] sanitize BEFORE: role=%s thinking_blocks=%d "
            "first_thinking_len=%d has_signature=%s",
            role, before_count, before_len, before_sig,
        )

    out: MutableMapping = dict(msg)
    for key in _INTERNAL_MSG_FIELDS:
        out.pop(key, None)

    usage = out.get("usage")
    if isinstance(usage, dict) and "cost" in usage:
        usage = dict(usage)
        usage.pop("cost", None)
        out["usage"] = usage

    content = out.get("content")
    if isinstance(content, list):
        cleaned = []
        for block in content:
            if isinstance(block, dict):
                block = dict(block)
                for key in _INTERNAL_BLOCK_FIELDS:
                    block.pop(key, None)
                tcid = block.get("toolCallId", "")
                if isinstance(tcid, str) and "|" in tcid:
                    block["toolCallId"] = tcid.split("|", 1)[0]
                tc_id = block.get("id", "")
                if (
                    block.get("type") == "tool_use"
                    and isinstance(tc_id, str)
                    and "|" in tc_id
                ):
                    block["id"] = tc_id.split("|", 1)[0]
            cleaned.append(block)
        out["content"] = cleaned

    if before_count:
        after_count, after_len, after_sig = _thinking_stats(out.get("content"))
        if after_count < before_count:
            _logger.error(
                "[THINKING-DEBUG] sanitize LOST thinking blocks! "
                "role=%s before=%d after=%d", role, before_count, after_count,
            )
        else:
            _logger.info(
                "[THINKING-DEBUG] sanitize AFTER: role=%s thinking_blocks=%d "
                "first_thinking_len=%d has_signature=%s",
                role, after_count, after_len, after_sig,
            )

    return dict(out)


def extract_tokens(entries: Iterable[dict]) -> tuple[int, int]:
    """Sum input/output token counts across all JSONL entries.

    Tolerates Anthropic / OpenAI / LiteLLM / OpenClaw key variants.
    """
    in_keys = ("input", "input_tokens", "inputTokens", "prompt_tokens")
    out_keys = ("output", "output_tokens", "outputTokens", "completion_tokens")
    total_in = 0
    total_out = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        usage = entry.get("usage") or entry.get("message", {}).get("usage") or {}
        if not isinstance(usage, dict):
            continue
        for k in in_keys:
            v = usage.get(k)
            if isinstance(v, (int, float)) and v:
                total_in += int(v)
                break
        for k in out_keys:
            v = usage.get(k)
            if isinstance(v, (int, float)) and v:
                total_out += int(v)
                break
    return total_in, total_out
