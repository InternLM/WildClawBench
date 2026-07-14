#!/usr/bin/env python3
# Re-execute ONLY the test suite (testexec phase) against an already-completed
# trajectory — no agent re-run, no testgen, no LLM judge. Mirrors exactly what
# eval/run_batch.py does at the `--execute-tests` step by reusing
# src.utils.test_executor.execute_tests, so the reward it produces matches the
# production path.
#
# What it does:
#   1. Resolve a run dir (output/<harness>/<task>/trajectories/<model>/run_N).
#   2. Mount that run's task_output/workspace_full (the agent's deliverables)
#      read-only at /tmp_workspace inside a throwaway docker container.
#   3. Run the task's test_outputs.py + test_weights.json (preferring the
#      cached/copied suite under output/<task>/data/tests/, falling back to
#      input/<task>/) via the same no-pytest runner used in the batch.
#   4. Recompute the weighted reward and (re)write the run's verifier artifacts:
#         task_output/logs/verifier/{reward.txt, ctrf.json,
#                                    test_function_outputs.json, test_output.log}
#      plus a standalone regrade_test_result.json (score.json is left untouched).
#
# Mock-API note: many suites call <SVC>/audit/summary via <SVC>_URL env vars to
# verify which connectors the agent touched. To reproduce those tests faithfully
# you must point at an ALREADY-RUNNING mock stack with --network + --env*.
# Without it, audit-based tests see zero calls (workspace-file tests still run).
#
# Usage:
#   # workspace-only re-grade (audit/* tests will see 0 mock calls):
#   python3 script/rerun_tests.py --run output/openclaw/amanda_hayes_01/trajectories/claude/run_1
#
#   # faithful re-grade against a live mock stack:
#   python3 script/rerun_tests.py --run <run_dir> \
#       --network wildclawbench-mocknet \
#       --env-json /path/to/mock_env.json
#
#   # point at a whole task (re-grades its latest run_N under each model):
#   python3 script/rerun_tests.py --task output/openclaw/amanda_hayes_01

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils.test_executor import execute_tests  # noqa: E402
from src.utils.harbor.ctrf import build_ctrf        # noqa: E402

DEFAULT_IMAGE = "wildclawbench-ubuntu:v1.3"


def _find_tests(run_dir: Path) -> tuple[Path | None, Path | None]:
    """Locate (test_outputs.py, test_weights.json) for this run.

    Search order mirrors how run_batch sources tests:
      1. output/<harness>/<task>/data/tests/      (cached/generated/copied suite)
      2. input/<task>/  and  input/<task>/tests/  (original provided suite)
    """
    # run_dir = .../<task>/trajectories/<model>/run_N  -> task root is parents[2]
    task_root = run_dir.parents[2]
    task_name = task_root.name

    candidates = [
        task_root / "data" / "tests",
        REPO_ROOT / "input" / task_name / "tests",
        REPO_ROOT / "input" / task_name,
    ]
    for base in candidates:
        code = base / "test_outputs.py"
        if not code.is_file():
            code = base / "test_output.py"
        weights = base / "test_weights.json"
        if code.is_file() and weights.is_file():
            return code, weights
    return None, None


def _load_env(args) -> dict[str, str]:
    env: dict[str, str] = {}
    if args.env_json:
        env.update({str(k): str(v) for k, v in json.loads(Path(args.env_json).read_text()).items()})
    for kv in args.env or []:
        if "=" in kv:
            k, v = kv.split("=", 1)
            env[k] = v
    return env


def _regrade_run(run_dir: Path, args) -> dict | None:
    ws = run_dir / "task_output" / "workspace_full"
    if not ws.is_dir():
        print(f"  [skip] no workspace_full at {ws}")
        return None

    code_path, weights_path = _find_tests(run_dir)
    if not code_path:
        print(f"  [skip] no test_outputs.py + test_weights.json found for {run_dir}")
        return None

    test_code = code_path.read_text(encoding="utf-8")
    test_weights_json = weights_path.read_text(encoding="utf-8")
    env = _load_env(args)

    print(f"  tests:     {code_path}")
    print(f"  workspace: {ws}")
    print(f"  network:   {args.network or '<host, no mock stack>'}  ({len(env)} *_URL env vars)")

    te = execute_tests(
        test_code=test_code,
        test_weights_json=test_weights_json,
        workspace_dir=ws,
        mock_env_dict=env,
        network=args.network or None,
        image=args.image,
        timeout=args.timeout,
    )

    # (Re)write verifier artifacts exactly like run_batch.py:1254-1274.
    verifier_dir = run_dir / "task_output" / "logs" / "verifier"
    verifier_dir.mkdir(parents=True, exist_ok=True)
    (verifier_dir / "reward.txt").write_text(f"{te['reward']:.6f}\n", encoding="utf-8")
    ctrf = build_ctrf(
        tests_total=te["tests_total"],
        tests_passed=te["tests_passed"],
        tests_failed=te["tests_failed"],
        tests_errored=te["tests_errored"],
        test_scores_json=te.get("test_scores", "{}"),
        tests_skipped=te.get("tests_skipped", 0),
        reward=te.get("reward"),
    )
    (verifier_dir / "ctrf.json").write_text(
        json.dumps(ctrf, indent=2, ensure_ascii=False), encoding="utf-8")
    _fn = te.get("test_function_outputs") or "{}"
    (verifier_dir / "test_function_outputs.json").write_text(
        _fn if isinstance(_fn, str) else json.dumps(_fn, indent=2), encoding="utf-8")
    (verifier_dir / "test_output.log").write_text(te.get("test_output", "") or "", encoding="utf-8")
    # Standalone snapshot — does NOT clobber the judge-owned score.json.
    (run_dir / "regrade_test_result.json").write_text(
        json.dumps({k: v for k, v in te.items() if k != "test_output"}, indent=2),
        encoding="utf-8")

    err = f"  ERROR={te['error']}" if te["tests_total"] == 0 and te.get("error") else ""
    print(f"  RESULT: {te['tests_passed']}/{te['tests_total']} passed "
          f"(failed={te['tests_failed']} errored={te['tests_errored']} "
          f"skipped={te.get('tests_skipped', 0)}) reward={te['reward']:.4f}{err}")
    return te


def _iter_runs(args) -> list[Path]:
    if args.run:
        return [Path(args.run).resolve()]
    task_root = Path(args.task).resolve()
    runs: list[Path] = []
    for model_dir in sorted((task_root / "trajectories").glob("*")):
        run_dirs = sorted(model_dir.glob("run_*"), key=lambda p: p.name)
        if run_dirs:
            runs.append(run_dirs[-1] if args.latest else run_dirs[0])
            if not args.latest:
                runs[-1:] = run_dirs  # all runs
    return runs


def main() -> int:
    ap = argparse.ArgumentParser(description="Re-execute a trajectory's test suite (no agent re-run).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", help="A single run dir: output/<harness>/<task>/trajectories/<model>/run_N")
    g.add_argument("--task", help="A task dir: output/<harness>/<task> (re-grades its runs)")
    ap.add_argument("--latest", action="store_true", help="With --task, only the highest run_N per model")
    ap.add_argument("--network", help="Docker network of a RUNNING mock stack (for audit/* tests)")
    ap.add_argument("--env-json", help="JSON file of {<SVC>_URL: http://host:port} for the mock stack")
    ap.add_argument("--env", action="append", help="Extra SVC_URL=... env var (repeatable)")
    ap.add_argument("--image", default=DEFAULT_IMAGE, help=f"Runner image (default {DEFAULT_IMAGE})")
    ap.add_argument("--timeout", type=int, default=600, help="Outer testexec timeout seconds")
    args = ap.parse_args()

    runs = _iter_runs(args)
    if not runs:
        print("No run dirs found.", file=sys.stderr)
        return 2

    rewards = []
    for rd in runs:
        print(f"\n== {rd} ==")
        te = _regrade_run(rd, args)
        if te is not None:
            rewards.append(te["reward"])

    if rewards:
        print(f"\nDone. {len(rewards)} run(s) re-graded; mean reward={sum(rewards) / len(rewards):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
