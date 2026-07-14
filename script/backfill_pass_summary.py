#!/usr/bin/env python3
"""Backfill / repair pass_summary.json files for already-graded output trees.

Historically `pass_summary.json` aliased its ``tests_*`` keys to the rubric
criteria counts and reported a rubric-only ``average_reward`` — so the real
pytest channel (and the combined reward) were invisible in that file. This
script rebuilds every pass_summary.json under an output root from the canonical
on-disk sources:

  * rubric (Channel B)  -> run_N/score.json
  * pytest (Channel A)  -> run_N/task_output/logs/verifier/ctrf.json
                           (reward.txt as a fallback for the scalar reward)

The emitted schema matches eval/run_batch.py:_pass_summary_entry — real
``tests_*`` counts, explicit ``rubric_reward`` / ``test_reward`` /
``combined_reward``, and ``average_reward`` = combined mean.

Usage:
    python3 script/backfill_pass_summary.py <output_root> [--backend NAME] [--dry-run]

<output_root> may be any directory; every ``trajectories/<model>/`` folder that
contains run_N subdirectories beneath it is rebuilt. Examples:

    python3 script/backfill_pass_summary.py output
    python3 script/backfill_pass_summary.py 25-JUNE-2026-Night/BATCH_7/temp/output --dry-run
    python3 script/backfill_pass_summary.py output/openclaw/some-task
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

RUN_DIR_RE = re.compile(r"^run_(\d+)$")


def _load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _finite_float(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v)):
        return float(v)
    return None


def _mean_or_none(vals):
    nums = [v for v in vals if v is not None]
    return (sum(nums) / len(nums)) if nums else None


def _ctrf_test_result(run_dir: Path) -> dict:
    """Reconstruct a test_result-shaped dict from the verifier ctrf.json.

    Counts are taken from the per-test status list when present (more accurate
    than the CTRF summary, which lumps errored runs into ``other``), and the
    scalar reward from summary.overall_score, with reward.txt as a fallback.
    """
    verifier = run_dir / "task_output" / "logs" / "verifier"
    ctrf = _load_json(verifier / "ctrf.json")
    out = {"tests_total": 0, "tests_passed": 0, "tests_failed": 0,
           "tests_errored": 0, "tests_skipped": 0, "reward": None}
    if isinstance(ctrf, dict):
        results = ctrf.get("results") or {}
        summary = results.get("summary") or {}
        tests = results.get("tests") or []
        if isinstance(tests, list) and tests:
            counts = {"passed": 0, "failed": 0, "errored": 0, "skipped": 0}
            for t in tests:
                st = (t or {}).get("status", "")
                if st in counts:
                    counts[st] += 1
            out["tests_total"] = len(tests)
            out["tests_passed"] = counts["passed"]
            out["tests_failed"] = counts["failed"]
            out["tests_errored"] = counts["errored"]
            out["tests_skipped"] = counts["skipped"]
        else:
            out["tests_total"] = int(summary.get("tests", 0) or 0)
            out["tests_passed"] = int(summary.get("passed", 0) or 0)
            out["tests_failed"] = int(summary.get("failed", 0) or 0)
            out["tests_errored"] = int(summary.get("other", 0) or 0)
            out["tests_skipped"] = int(summary.get("skipped", 0) or 0)
        out["reward"] = _finite_float(summary.get("overall_score"))
    if out["reward"] is None:
        try:
            out["reward"] = _finite_float(float((verifier / "reward.txt").read_text().strip()))
        except (OSError, ValueError):
            pass
    return out


def _entry(run_index: int, scores: dict, test_result: dict) -> dict:
    """Mirror of eval/run_batch.py:_pass_summary_entry (kept in sync by hand)."""
    s = scores or {}
    tr = test_result or {}
    crit_total = int(s.get("criteria_total", s.get("tests_total", 0)) or 0)
    crit_passed = int(s.get("criteria_passed", s.get("tests_passed", 0)) or 0)
    crit_failed = int(s.get("criteria_failed", s.get("tests_failed", 0)) or 0)
    rubric_reward = _finite_float(s.get("rubric_based_reward"))
    if rubric_reward is None:
        rubric_reward = _finite_float(s.get("overall_score"))
    rubric_pct = _finite_float(s.get("rubric_weights_percentage"))
    if rubric_pct is None and rubric_reward is not None:
        rubric_pct = rubric_reward * 100.0
    t_total = int(tr.get("tests_total", 0) or 0)
    test_reward = _finite_float(s.get("test_based_reward"))
    if test_reward is None and t_total > 0:
        test_reward = _finite_float(tr.get("reward"))
    combined = _finite_float(s.get("combined_reward"))
    if combined is None:
        if test_reward is not None and rubric_reward is not None:
            combined = (test_reward + rubric_reward) / 2.0
        elif test_reward is not None:
            combined = test_reward
        else:
            combined = rubric_reward
    authoritative = combined if combined is not None else (rubric_reward or 0.0)
    return {
        "run_index": run_index,
        "criteria_total": crit_total,
        "criteria_passed": crit_passed,
        "criteria_failed": crit_failed,
        "rubric_reward": rubric_reward,
        "rubric_weights_percentage": round(rubric_pct, 2) if rubric_pct is not None else None,
        "tests_total": t_total,
        "tests_passed": int(tr.get("tests_passed", 0) or 0),
        "tests_failed": int(tr.get("tests_failed", 0) or 0),
        "tests_errored": int(tr.get("tests_errored", 0) or 0),
        "tests_skipped": int(tr.get("tests_skipped", 0) or 0),
        "test_reward": test_reward,
        "combined_reward": combined,
        "reward": authoritative,
    }


def _doc(model_type: str, per_run: list) -> dict:
    per_run = sorted(per_run, key=lambda r: r["run_index"])
    avg_reward = _mean_or_none([r.get("reward") for r in per_run]) or 0.0
    avg_pct = _mean_or_none([r.get("rubric_weights_percentage") for r in per_run])
    return {
        "model": model_type,
        "runs": len(per_run),
        "average_reward": avg_reward,
        "average_combined_reward": _mean_or_none([r.get("combined_reward") for r in per_run]),
        "average_rubric_reward": _mean_or_none([r.get("rubric_reward") for r in per_run]),
        "average_test_reward": _mean_or_none([r.get("test_reward") for r in per_run]),
        "average_rubric_weights_percentage": round(avg_pct, 2) if avg_pct is not None else None,
        "per_run": per_run,
    }


def _find_model_dirs(root: Path):
    """Yield every <...>/trajectories/<model>/ dir that has run_N children."""
    seen = set()
    for run_dir in root.rglob("run_*"):
        if not run_dir.is_dir() or not RUN_DIR_RE.match(run_dir.name):
            continue
        model_dir = run_dir.parent
        if model_dir.parent.name != "trajectories":
            continue
        if model_dir not in seen:
            seen.add(model_dir)
            yield model_dir


def rebuild_model_dir(model_dir: Path) -> dict | None:
    runs = []
    for child in model_dir.iterdir():
        m = RUN_DIR_RE.match(child.name)
        if child.is_dir() and m:
            runs.append((int(m.group(1)), child))
    if not runs:
        return None
    per_run = []
    for idx, run_dir in sorted(runs):
        scores = _load_json(run_dir / "score.json") or {}
        test_result = _ctrf_test_result(run_dir)
        per_run.append(_entry(idx, scores, test_result))
    return _doc(model_dir.name, per_run)


def main() -> int:
    ap = argparse.ArgumentParser(description="Rebuild pass_summary.json files with real test data + combined reward.")
    ap.add_argument("output_root", help="Directory to scan for trajectories/<model>/run_N folders")
    ap.add_argument("--backend", default=None,
                    help="Only rebuild dirs whose path contains /<backend>/ (e.g. openclaw)")
    ap.add_argument("--dry-run", action="store_true", help="Print what would change without writing")
    args = ap.parse_args()

    root = Path(args.output_root)
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    written = 0
    scanned = 0
    for model_dir in _find_model_dirs(root):
        if args.backend and f"/{args.backend}/" not in str(model_dir) + "/":
            continue
        doc = rebuild_model_dir(model_dir)
        if doc is None:
            continue
        scanned += 1
        target = model_dir / "pass_summary.json"
        old = _load_json(target)
        old_avg = (old or {}).get("average_reward")
        new_text = json.dumps(doc, indent=2)
        tag = "DRY" if args.dry_run else "WROTE"
        print(f"[{tag}] {target}")
        for r in doc["per_run"]:
            print(f"        run {r['run_index']}: rubric={r['rubric_reward']} "
                  f"({r['criteria_passed']}/{r['criteria_total']} criteria)  "
                  f"tests={r['tests_passed']}/{r['tests_total']} (reward={r['test_reward']})  "
                  f"combined={r['combined_reward']}")
        if old_avg is not None and old_avg != doc["average_reward"]:
            print(f"        average_reward: {old_avg} -> {doc['average_reward']}")
        if not args.dry_run:
            target.write_text(new_text, encoding="utf-8")
            written += 1

    verb = "would rebuild" if args.dry_run else "rebuilt"
    print(f"\n{verb} {scanned if args.dry_run else written} pass_summary.json file(s) under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
