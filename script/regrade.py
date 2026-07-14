#!/usr/bin/env python3
# Re-runs ONLY the judge phase against an existing completed run dir, using
# the rubric currently at `input/<task>/rubric.json`. Overwrites the run's
# score.json in place (per user m1820 design choices). Does NOT re-run the
# agent, testgen, or testexec. Council mode only.
#
# Usage:
#   python3 script/regrade.py --run output/openclaw/<task>/trajectories/<model>/run_N
#
# Inputs read from the run dir:
#   output.json   — for the trajectory and message stream
#   task_output/artifacts/    — judge evidence (b99 canonical)
#   task_output/workspace_full/   — fallback when artifacts/ empty
#
# Input read from elsewhere:
#   input/<task>/rubric.json  — the (possibly edited) rubric file
#   input/<task>/prompt.txt   — task description (the judge needs the question)

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.run_batch import _condense_transcript_for_judge, recompute_combined  # noqa: E402
from src.utils.grading import grade_with_rubric  # noqa: E402

_USAGE_KEYS = (
    "input_tokens", "output_tokens", "cache_read_tokens",
    "cache_write_tokens", "total_tokens", "request_count", "cost_usd",
)


def _update_usage_json(run_dir: Path, scores: dict) -> None:
    usage_path = run_dir / "usage.json"
    if not usage_path.is_file():
        print(f"[regrade] no usage.json at {usage_path}; skipping usage update", file=sys.stderr)
        return
    try:
        usage = json.loads(usage_path.read_text(encoding="utf-8")) or {}
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[regrade] could not read usage.json ({exc}); skipping usage update", file=sys.stderr)
        return

    sources = dict(usage.get("sources") or {})
    old_cost = float(usage.get("cost_usd", 0.0) or 0.0)
    new_judge = dict(scores.get("usage") or {})
    sources["judge"] = new_judge

    combined = recompute_combined(sources, task_id=run_dir.parents[2].name)
    out = {k: combined[k] for k in _USAGE_KEYS}
    out["sources"] = sources
    for k, v in usage.items():
        if k not in out and k != "sources":
            out[k] = v

    usage_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"[regrade] usage.json updated: judge cost ${float(new_judge.get('cost_usd',0.0)):.4f}, "
        f"combined cost ${old_cost:.4f} -> ${float(out.get('cost_usd',0.0)):.4f}",
        file=sys.stderr,
    )


def _derive_task_id(run_dir: Path) -> str:
    # Layout per run_batch.py:_write_pass_summary:
    #   output/<backend>/<task_id>/trajectories/<model>/run_N/
    # So run_dir.parents = [run_N, <model>, trajectories, <task_id>, <backend>, output]
    try:
        return run_dir.parents[2].name
    except IndexError:
        raise SystemExit(f"run_dir does not match expected layout output/<backend>/<task>/trajectories/<model>/run_N: {run_dir}")


def _find_rubric_path(task_id: str, override: Path | None) -> Path:
    if override is not None:
        if not override.is_file():
            raise SystemExit(f"--rubric path does not exist: {override}")
        return override
    candidate = REPO_ROOT / "input" / task_id / "rubric.json"
    if not candidate.is_file():
        raise SystemExit(
            f"could not find rubric at {candidate}\n"
            f"pass --rubric <path> to point at it manually"
        )
    return candidate


def _find_prompt_path(task_id: str) -> Path | None:
    candidate = REPO_ROOT / "input" / task_id / "prompt.txt"
    return candidate if candidate.is_file() else None


def _load_rubrics(path: Path) -> list:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        rubrics = raw.get("rubrics") or []
    elif isinstance(raw, list):
        rubrics = raw
    else:
        raise SystemExit(f"rubric.json must be a list or {{rubrics: [...]}}; got {type(raw).__name__}")
    if not rubrics:
        raise SystemExit(f"no rubric criteria found in {path}")
    return rubrics


def _load_trajectory(run_dir: Path) -> dict:
    output_json = run_dir / "output.json"
    if not output_json.is_file():
        raise SystemExit(f"missing output.json in {run_dir} (cannot regrade without trajectory)")
    return json.loads(output_json.read_text(encoding="utf-8"))


def _pick_results_dir(run_dir: Path) -> Path:
    # Contract mirror: run_batch.py:_build_trajectory picks artifacts/ when
    # present and non-empty, otherwise workspace_full/. Regrade must use the
    # same rule so a regraded score is comparable to the original.
    artifacts = run_dir / "task_output" / "artifacts"
    try:
        if artifacts.exists() and any(artifacts.iterdir()):
            return artifacts
    except OSError:
        pass
    return run_dir / "task_output" / "workspace_full"


def regrade(run_dir: Path, rubric_override: Path | None = None) -> dict:
    if not run_dir.is_dir():
        raise SystemExit(f"run_dir does not exist or is not a directory: {run_dir}")

    task_id = _derive_task_id(run_dir)
    rubric_path = _find_rubric_path(task_id, rubric_override)
    prompt_path = _find_prompt_path(task_id)

    rubrics = _load_rubrics(rubric_path)
    traj = _load_trajectory(run_dir)
    results_dir = _pick_results_dir(run_dir)
    transcript_text = _condense_transcript_for_judge(traj)

    task_description = ""
    if prompt_path is not None:
        task_description = prompt_path.read_text(encoding="utf-8").strip()

    print(f"[regrade] task_id      = {task_id}", file=sys.stderr)
    print(f"[regrade] rubric       = {rubric_path} ({len(rubrics)} criteria)", file=sys.stderr)
    print(f"[regrade] results_dir  = {results_dir}", file=sys.stderr)
    print(f"[regrade] transcript   = {len(transcript_text):,} chars", file=sys.stderr)
    print(f"[regrade] judge        = council", file=sys.stderr)
    print(f"[regrade] grading …", file=sys.stderr)

    scores = grade_with_rubric(
        rubrics,
        task_description,
        results_dir,
        transcript_text=transcript_text,
        use_council=True,
    )

    score_path = run_dir / "score.json"
    score_path.write_text(json.dumps(scores, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[regrade] wrote {score_path}", file=sys.stderr)

    _update_usage_json(run_dir, scores)
    return scores


def _print_summary(scores: dict) -> None:
    overall = scores.get("overall_score")
    pct = scores.get("rubric_weights_percentage")
    total = scores.get("criteria_total", scores.get("tests_total", 0))
    passed = scores.get("criteria_passed", scores.get("tests_passed", 0))
    failed = scores.get("criteria_failed", scores.get("tests_failed", 0))
    abstained = scores.get("criteria_abstained", 0)
    judge_model = scores.get("judge_model", "?")
    if scores.get("error"):
        print(f"\n[regrade] FAILED: {scores.get('error')}")
        return
    print(f"\n[regrade] overall_score              = {overall}")
    print(f"[regrade] rubric_weights_percentage  = {pct}")
    print(f"[regrade] criteria  total={total}  passed={passed}  failed={failed}  abstained={abstained}")
    print(f"[regrade] judge_model = {judge_model}")
    council = scores.get("judge_council")
    if isinstance(council, dict):
        surviving = council.get("surviving") or []
        failed_members = council.get("failed") or []
        print(f"[regrade] council surviving={len(surviving)}/{len(surviving) + len(failed_members)}")
        for f in failed_members:
            if isinstance(f, dict):
                print(f"[regrade]   FAILED member: {f.get('model', '?')} — {str(f.get('error',''))[:160]}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-judge an existing run with the current rubric. Overwrites score.json in place.",
    )
    parser.add_argument("--run", required=True, help="path to run dir (output/<backend>/<task>/trajectories/<model>/run_N)")
    parser.add_argument("--rubric", default=None, help="override rubric path (default: input/<task>/rubric.json)")
    parser.add_argument("--quiet", action="store_true", help="suppress final summary table")
    args = parser.parse_args()

    run_dir = Path(args.run).resolve()
    rubric_override = Path(args.rubric).resolve() if args.rubric else None

    scores = regrade(run_dir, rubric_override=rubric_override)
    if not args.quiet:
        _print_summary(scores)
    return 0 if not scores.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
