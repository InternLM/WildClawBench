#!/usr/bin/env python3
"""Backfill output.json meta_info with the native sub-agent roster.

Why this exists: output.json is written twice per run. The first writer
(eval/run_batch.py:_build_trajectory) attaches meta_info.agents / subagents via
attach_native_subagents(). The second writer (src/utils/harbor/bundle.py
write_bundle) used to rewrite output.json WITHOUT that attach, clobbering the
roster. bundle.py is now fixed for future runs; this script repairs runs that
were already emitted with the roster stripped.

It re-runs attach_native_subagents() over each run dir, reading the already-on-
disk task_output/sessions/{sessions.json,*.jsonl}. No-op for runs with no
sessions.json or no sub-agents (single-agent runs stay byte-identical).

USAGE
    python3 script/backfill_subagent_meta.py output/openclaw
    python3 script/backfill_subagent_meta.py --dry-run output/openclaw
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.utils.trajectory.builder import attach_native_subagents


def _run_dirs(root: Path):
    # <root>/<task>/trajectories/<model>/run_N
    for out in sorted(root.rglob("output.json")):
        d = out.parent
        if re.match(r"run_\d+$", d.name):
            yield d


def backfill_run(run_dir: Path, dry_run: bool) -> tuple[bool, str]:
    out_path = run_dir / "output.json"
    try:
        published = json.loads(out_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return (False, "unreadable output.json")
    if not isinstance(published, dict):
        return (False, "output.json not an object")

    sessions_dir = run_dir / "task_output" / "sessions"
    if not (sessions_dir / "sessions.json").is_file():
        return (False, "no sessions.json (single-agent or not collected)")

    before = "subagents" in (published.get("meta_info") or {})
    # attach mutates `published` in place AND returns it; it also (re)writes the
    # subagents/NN and spawn_tree files (idempotent — same content).
    result = attach_native_subagents(published, sessions_dir, run_dir)
    mi = result.get("meta_info", {})
    count = mi.get("subagent_count")
    if "subagents" not in mi:
        return (False, "harvester found no sub-agents")

    if not dry_run:
        out_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    state = "already present, refreshed" if before else "ADDED"
    return (True, f"{state} ({count} sub-agents)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="+", help="Roots to walk (e.g. output/openclaw)")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = ap.parse_args(argv)

    seen = changed = 0
    for root in args.roots:
        rp = Path(root)
        if not rp.exists():
            print(f"!! skip (missing): {root}", file=sys.stderr)
            continue
        for run_dir in _run_dirs(rp):
            seen += 1
            ok, note = backfill_run(run_dir, args.dry_run)
            if ok:
                changed += 1
                print(f"[ok ] {run_dir}  -> {note}")
            else:
                print(f"[ -- ] {run_dir}  ({note})")

    verb = "would update" if args.dry_run else "updated"
    print("-" * 70)
    print(f"{verb} {changed}/{seen} run(s)")
    if args.dry_run:
        print("(dry-run — no files written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
