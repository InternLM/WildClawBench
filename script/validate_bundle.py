#!/usr/bin/env python3
"""Validate packaged trajectory bundles for silent damage.

Scans every run under the given roots (bundle layout:
``<task>/trajectories/<model>/run_N``) and flags the failure signatures found
in the 2026-07-06 audit of Midori_Kelley_01 / Gabriela_Vargas_01 /
Gabriela_Scott_01 — all of which shipped labeled "success":

ERRORS (data loss / wrong record)
  * child ending classified aborted/blocked (empty final assistant content,
    thinking-only final turn, trailing toolCall with no toolResult,
    ``/approve`` plea) — lane died mid-run
  * empty assistant ``content: []`` anywhere (stream cut)
  * toolCall not followed by a toolResult mid-file
  * toolResult text of 199,000-200,000 chars — fingerprint of OpenClaw's
    silent exec output cap (OUTPUT_CAP=2e5, tail-kept: the FIRST bytes are
    the ones missing)
  * meta message_count != actual messages
  * spawn_tree children count != subagent files

WARNINGS (suspicious but often benign)
  * child session end timestamp after the parent's last message (orphan —
    usually post-report heartbeat turns, verify the report exists)
  * final thinking text ends mid-word at EOF

USAGE
    python3 script/validate_bundle.py output_bundle
    python3 script/validate_bundle.py --strict output_bundle temp_output_bundle
Exit code is 1 when errors were found and --strict is set (warnings never
fail the run).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.utils.trajectory.builder import classify_child_completion

# OpenClaw exec output cap (dist: OUTPUT_CAP = 2e5, trimWithCap keeps the
# tail). Anything in this band was almost certainly cut — organic outputs
# land on a round 200,000 chars at ~1/200k odds per result.
_EXEC_CAP_BAND = (199_000, 200_000)
_SPAWN_TREE_CHILD_RE = re.compile(
    r"^\s+(\d+)\. (\S+) \[(\w+)\] -> (\S+) \((\d+) msgs\)", re.M
)


def _ts(value: str) -> float | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return None


def _blocks(msg: dict) -> list:
    content = (msg.get("message") or {}).get("content")
    return content if isinstance(content, list) else []


def _texts(msg: dict) -> list[str]:
    return [b.get("text", "") for b in _blocks(msg)
            if isinstance(b, dict) and b.get("type") == "text"]


def check_messages(msgs: list, *, is_child: bool) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for one trajectory's message list."""
    errors: list[str] = []
    warnings: list[str] = []
    for i, m in enumerate(msgs):
        if not isinstance(m, dict):
            continue
        inner = m.get("message") or {}
        role = inner.get("role")
        if role == "assistant" and inner.get("content") == []:
            errors.append(f"msg {i}: assistant turn with empty content (stream cut)")
        for b in _blocks(m):
            if not isinstance(b, dict):
                continue
            if b.get("type") in ("toolCall", "tool_use"):
                nxt = msgs[i + 1].get("message") if i + 1 < len(msgs) else None
                nxt_role = (nxt or {}).get("role") if isinstance(nxt, dict) else None
                if nxt_role != "toolResult":
                    errors.append(
                        f"msg {i}: toolCall {b.get('name')!r} has no following toolResult"
                    )
        if role == "toolResult":
            for t in _texts(m):
                if _EXEC_CAP_BAND[0] <= len(t) <= _EXEC_CAP_BAND[1]:
                    errors.append(
                        f"msg {i}: toolResult of {len(t)} chars — silent exec-cap "
                        f"fingerprint (first bytes of the output are missing)"
                    )
    # Mid-word thinking at EOF: last block of the final message only.
    if msgs and isinstance(msgs[-1], dict):
        for b in _blocks(msgs[-1]):
            if isinstance(b, dict) and b.get("type") == "thinking":
                txt = (b.get("thinking") or "").rstrip()
                if txt and txt[-1].isalnum() and not txt.endswith(
                        (".", "!", "?", ":", ")", '"', "'", "]", "…")):
                    warnings.append(
                        f"final thinking ends mid-word: ...{txt[-50:]!r}"
                    )
    if is_child:
        status, reason = classify_child_completion(msgs)
        if status != "success":
            errors.append(f"ending classified {status}: {reason}")
    return errors, warnings


def check_run(run_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    parent_path = run_dir / "output.json"
    parent_end: float | None = None
    if parent_path.is_file():
        try:
            parent = json.loads(parent_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return [f"output.json unreadable: {exc}"], []
        pmsgs = parent.get("messages") or []
        if pmsgs:
            parent_end = _ts(pmsgs[-1].get("timestamp"))
        errs, warns = check_messages(pmsgs, is_child=False)
        errors += [f"PARENT: {e}" for e in errs]
        warnings += [f"PARENT: {w}" for w in warns]
    else:
        errors.append("missing output.json")

    sub_files = sorted((run_dir / "subagents").glob("*.json")) \
        if (run_dir / "subagents").is_dir() else []
    for f in sub_files:
        try:
            child = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{f.name}: unreadable ({exc})")
            continue
        msgs = child.get("messages") or []
        meta = child.get("meta_info") or {}
        mc = meta.get("message_count")
        if mc is not None and mc != len(msgs):
            errors.append(f"{f.name}: meta message_count={mc}, actual={len(msgs)}")
        errs, warns = check_messages(msgs, is_child=True)
        errors += [f"{f.name}: {e}" for e in errs]
        warnings += [f"{f.name}: {w}" for w in warns]
        if parent_end is not None and msgs:
            child_end = _ts(msgs[-1].get("timestamp"))
            if child_end is not None and child_end > parent_end:
                warnings.append(
                    f"{f.name}: outlived parent by {child_end - parent_end:.0f}s "
                    f"(orphan — check for trailing heartbeat turns)"
                )

    tree_path = run_dir / "spawn_tree" / "parent_spawn_tree.txt"
    if tree_path.is_file():
        tree_children = _SPAWN_TREE_CHILD_RE.findall(
            tree_path.read_text(encoding="utf-8"))
        if len(tree_children) != len(sub_files):
            errors.append(
                f"spawn_tree lists {len(tree_children)} children, "
                f"{len(sub_files)} subagent files on disk"
            )
    elif sub_files:
        warnings.append("subagents/ present but no spawn_tree/parent_spawn_tree.txt")

    return errors, warnings


def _run_dirs(root: Path):
    for out in sorted(root.rglob("output.json")):
        if re.match(r"run_\d+$", out.parent.name):
            yield out.parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="+", help="Bundle roots to walk")
    ap.add_argument("--strict", action="store_true",
                    help="Exit 1 if any errors were found")
    ap.add_argument("--quiet", action="store_true",
                    help="Only print runs with findings")
    args = ap.parse_args(argv)

    total = bad = warned = 0
    any_errors = False
    for root in args.roots:
        rp = Path(root)
        if not rp.exists():
            print(f"!! skip (missing): {root}", file=sys.stderr)
            continue
        for run_dir in _run_dirs(rp):
            total += 1
            errors, warnings = check_run(run_dir)
            if errors:
                bad += 1
                any_errors = True
            if warnings:
                warned += 1
            if errors or warnings or not args.quiet:
                status = "FAIL" if errors else ("WARN" if warnings else "ok")
                print(f"[{status:4s}] {run_dir}")
            for e in errors:
                print(f"    ERROR {e}")
            for w in warnings:
                print(f"    warn  {w}")

    print("-" * 70)
    print(f"{total} run(s) checked: {bad} with errors, {warned} with warnings")
    return 1 if (args.strict and any_errors) else 0


if __name__ == "__main__":
    raise SystemExit(main())
