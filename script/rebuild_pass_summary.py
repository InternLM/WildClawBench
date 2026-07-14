#!/usr/bin/env python3
"""Rebuild pass_summary.json from run_N/ artifacts under a trajectories/<model>/ dir.

This is a byte-for-byte faithful reimplementation of the harness's
`_pass_summary_doc()` + `_pass_summary_entry()` pipeline in `eval/run_batch.py`.
Point it at a trajectories/<model>/ folder that already contains 1..N run_N/
sub-dirs, and it emits pass_summary_new.json with the exact same shape the
harness would have written if all N reps had run in a single batch.

Same keys, same order, same rounding, same `_finite_float` semantics, same
None-tolerant means. No extra keys. No merged_from audit trail. No pass@K.

USAGE

    python3 script/rebuild_pass_summary.py TRAJECTORIES_DIR [-o OUTPUT]
    python3 script/rebuild_pass_summary.py TRAJECTORIES_DIR --in-place

Where TRAJECTORIES_DIR is something like:
    output/openclaw/<task>/trajectories/<model>/
or:
    /path/to/trajectories/claude/

The script auto-discovers run_1, run_2, ..., run_N and rebuilds the summary
from the per-rep score.json + ctrf.json + reward.txt artifacts. It does NOT
touch existing pass_summary.json unless you pass --in-place.

WHY

Manual merging of two pass_summary.json files (1-rep verification + N-rep
bulk) proved unreliable across schema versions -- fields end up as null when
a rich-schema field is renamed or a decimal reward hasn't been converted to
a percent. Recomputing from the per-run artifacts sidesteps every
schema-crossover problem: the artifacts are the source of truth the harness
itself reads.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


def _finite_float(v: Any) -> float | None:
    if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v)):
        return float(v)
    return None


def _mean_or_none(vals: list[Any]) -> float | None:
    nums = [v for v in vals if v is not None]
    return (sum(nums) / len(nums)) if nums else None


def _load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _read_ctrf_summary(run_dir: Path) -> dict:
    """Return the pytest counts + reward that _pass_summary_entry expects.

    The harness passes a `test_result` dict with keys
    tests_total/tests_passed/tests_failed/tests_errored/tests_skipped and
    reward (a decimal 0-1 from test_executor). We reconstruct that dict from
    the on-disk ctrf.json + reward.txt so the recompute is byte-equivalent.
    """
    ctrf = _load_json(run_dir / "task_output" / "logs" / "verifier" / "ctrf.json") or {}
    summary = (ctrf.get("results") or {}).get("summary") or ctrf.get("summary") or {}
    reward_path = run_dir / "task_output" / "logs" / "verifier" / "reward.txt"
    reward: float | None = None
    if reward_path.is_file():
        try:
            reward = float(reward_path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            reward = None
    if reward is None:
        reward = _finite_float(summary.get("overall_score"))
    return {
        "tests_total": int(summary.get("tests", 0) or 0),
        "tests_passed": int(summary.get("passed", 0) or 0),
        "tests_failed": int(summary.get("failed", 0) or 0),
        "tests_errored": int(summary.get("other", 0) or 0),
        "tests_skipped": int(summary.get("skipped", 0) or 0),
        "reward": reward,
    }


def _pass_summary_entry(run_index: int, scores: dict | None, test_result: dict | None) -> dict:
    """Verbatim port of eval/run_batch.py::_pass_summary_entry."""
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
    t_passed = int(tr.get("tests_passed", 0) or 0)
    t_failed = int(tr.get("tests_failed", 0) or 0)
    t_err = int(tr.get("tests_errored", 0) or 0)
    t_skip = int(tr.get("tests_skipped", 0) or 0)
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
        "tests_passed": t_passed,
        "tests_failed": t_failed,
        "tests_errored": t_err,
        "tests_skipped": t_skip,
        "test_reward": test_reward,
        "combined_reward": combined,
        "reward": authoritative,
    }


def _pass_summary_doc(model_type: str, per_run: list) -> dict:
    """Verbatim port of eval/run_batch.py::_pass_summary_doc."""
    per_run = sorted(per_run, key=lambda r: r["run_index"])
    avg_reward = _mean_or_none([r.get("reward") for r in per_run]) or 0.0
    avg_combined = _mean_or_none([r.get("combined_reward") for r in per_run])
    avg_rubric = _mean_or_none([r.get("rubric_reward") for r in per_run])
    avg_test = _mean_or_none([r.get("test_reward") for r in per_run])
    avg_pct = _mean_or_none([r.get("rubric_weights_percentage") for r in per_run])
    return {
        "model": model_type,
        "runs": len(per_run),
        "average_reward": avg_reward,
        "average_combined_reward": avg_combined,
        "average_rubric_reward": avg_rubric,
        "average_test_reward": avg_test,
        "average_rubric_weights_percentage": round(avg_pct, 2) if avg_pct is not None else None,
        "per_run": per_run,
    }


_RUN_DIR_RE = re.compile(r"^run_(\d+)$")


def discover_run_dirs(model_dir: Path) -> list[tuple[int, Path]]:
    """Return sorted [(run_index, run_dir), ...] under model_dir."""
    out: list[tuple[int, Path]] = []
    if not model_dir.is_dir():
        return out
    for child in model_dir.iterdir():
        if not child.is_dir():
            continue
        m = _RUN_DIR_RE.match(child.name)
        if not m:
            continue
        out.append((int(m.group(1)), child))
    out.sort(key=lambda x: x[0])
    return out


def rebuild(model_dir: Path, model_type: str | None = None) -> dict:
    """Compute pass_summary contents from run_N/ artifacts under model_dir."""
    runs = discover_run_dirs(model_dir)
    if not runs:
        sys.stderr.write(f"error: no run_N/ dirs under {model_dir}\n")
        sys.exit(2)
    if model_type is None:
        model_type = model_dir.name
    per_run: list[dict] = []
    for run_index, run_dir in runs:
        scores = _load_json(run_dir / "score.json")
        test_result = _read_ctrf_summary(run_dir)
        per_run.append(_pass_summary_entry(run_index, scores, test_result))
    return _pass_summary_doc(model_type, per_run)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Rebuild pass_summary.json from run_N/ artifacts under a "
            "trajectories/<model>/ dir. Byte-equivalent to what the harness "
            "would have written."
        )
    )
    ap.add_argument(
        "model_dir",
        type=Path,
        help="Path to trajectories/<model>/ containing run_1, run_2, ..., run_N/",
    )
    ap.add_argument(
        "--model",
        default=None,
        help="Override the 'model' field. Defaults to the model_dir basename.",
    )
    out = ap.add_mutually_exclusive_group()
    out.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help=(
            "Output path. Use '-' for stdout. Default: write "
            "'pass_summary_new.json' next to the existing pass_summary.json."
        ),
    )
    out.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite <model_dir>/pass_summary.json with the recomputed doc.",
    )
    ap.add_argument("--indent", type=int, default=2, help="JSON indent (default: 2)")
    args = ap.parse_args()

    if not args.model_dir.is_dir():
        ap.error(f"model_dir is not a directory: {args.model_dir}")

    doc = rebuild(args.model_dir, model_type=args.model)
    text = json.dumps(doc, indent=args.indent)

    if args.in_place:
        dst = args.model_dir / "pass_summary.json"
        dst.write_text(text, encoding="utf-8")
        sys.stderr.write(f"wrote {doc['runs']} rep(s) → {dst}\n")
        return 0
    if args.output == "-":
        sys.stdout.write(text)
        return 0
    dst = Path(args.output) if args.output else (args.model_dir / "pass_summary_new.json")
    dst.write_text(text, encoding="utf-8")
    sys.stderr.write(f"wrote {doc['runs']} rep(s) → {dst}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
