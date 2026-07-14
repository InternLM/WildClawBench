#!/usr/bin/env python3
"""Re-grade a finished run OFFLINE against its saved audit diary.

Runs a trajectory's `test_outputs.py` against the `agent_state.json` captured at
run time — no Docker, no live mock stack, no agent re-run. Edit the tests and
re-grade as many times as you like.

Reward uses the canonical weighted formula (test_executor._compute_reward):

    final_reward = (Σ passed_positive_w − Σ |triggered_negative_w|) / Σ positive_w
    rubric_weights_percentage = final_reward × 100

NOTE (floor score): runs created BEFORE the full-diary change saved only audit
counts, so body-inspecting tests (e.g. "did the agent write Room 112?") cannot
pass offline — they ERROR for lack of saved bodies. Runs created after the
change carry the full diary and grade completely. Either way the number is a
FLOOR, never a false pass.

Usage:
    python scripts/retest_run.py <run_folder>
    python scripts/retest_run.py <run_folder> --tests T.py --weights W.json
    python scripts/retest_run.py <run_folder> --keep    # keep temp dir to inspect
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.utils.test_executor import _compute_reward  # noqa: E402

CONFTEST_SRC = Path(__file__).with_name("offline_audit_conftest.py")
_STATUS = {"PASSED": "passed", "FAILED": "failed", "SKIPPED": "skipped", "ERROR": "errored"}


def _locate(run: Path, args) -> tuple[Path | None, Path | None, Path | None]:
    """Find agent_state.json, test_outputs.py, test_weights.json for a run."""
    state = run / "agent_state.json"
    if not state.is_file():
        alt = run / "data" / "tests" / "agent_state.json"
        state = alt if alt.is_file() else state

    tests = Path(args.tests).resolve() if args.tests else None
    weights = Path(args.weights).resolve() if args.weights else None
    if tests is None:
        for up in [run, *run.parents]:
            cand = up / "input" / "test_outputs.py"
            if cand.is_file():
                tests = cand
                if weights is None and (up / "input" / "test_weights.json").is_file():
                    weights = up / "input" / "test_weights.json"
                break
    return (state if state.is_file() else None), tests, weights


def retest(run: Path, args) -> int:
    state, tests, weights = _locate(run, args)
    if state is None:
        print(f"ERROR: no agent_state.json under {run}", file=sys.stderr)
        return 2
    if tests is None or not tests.is_file():
        print("ERROR: no test_outputs.py found (pass --tests)", file=sys.stderr)
        return 2

    work = Path(tempfile.mkdtemp(prefix="retest-"))
    shutil.copy2(tests, work / "test_outputs.py")
    shutil.copy2(state, work / "agent_state.json")
    if weights and weights.is_file():
        shutil.copy2(weights, work / "test_weights.json")
    shutil.copy2(CONFTEST_SRC, work / "conftest.py")

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "test_outputs.py", "-v", "--tb=no",
         "--no-header", "-p", "no:cacheprovider"],
        cwd=work, capture_output=True, text=True,
    )

    results: dict[str, dict] = {}
    for line in proc.stdout.splitlines():
        m = re.search(r"::(\S+)\s+(PASSED|FAILED|SKIPPED|ERROR)\b", line)
        if m:
            results[m.group(1)] = {"status": _STATUS[m.group(2)]}

    weights_map: dict[str, float] = {}
    wp = work / "test_weights.json"
    if wp.is_file():
        try:
            raw = json.loads(wp.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                weights_map = {k: float(v) for k, v in raw.items() if isinstance(v, (int, float))}
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    reward = _compute_reward(results, weights_map)
    pct = round(reward * 100.0, 2)
    n_pass = sum(1 for r in results.values() if r["status"] == "passed")
    n_err = sum(1 for r in results.values() if r["status"] == "errored")

    print("=" * 64)
    print(f"OFFLINE RETEST  {run}")
    print(f"  tests passed                 : {n_pass}/{len(results)}"
          + (f"  ({n_err} errored — no saved diary)" if n_err else ""))
    print(f"  final_reward                 : {reward}")
    print(f"  rubric_weights_percentage    : {pct}%")
    print("=" * 64)

    out = {
        "run": str(run),
        "final_reward": reward,
        "rubric_weights_percentage": pct,
        "tests_total": len(results),
        "tests_passed": n_pass,
        "tests_errored": n_err,
        "results": {k: v["status"] for k, v in results.items()},
    }
    (run / "score_offline.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {run / 'score_offline.json'}")

    if args.keep:
        print(f"kept temp test dir: {work}")
    else:
        shutil.rmtree(work, ignore_errors=True)
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run", help="run folder containing agent_state.json")
    ap.add_argument("--tests", help="path to test_outputs.py (auto-found if omitted)")
    ap.add_argument("--weights", help="path to test_weights.json (auto-found if omitted)")
    ap.add_argument("--keep", action="store_true", help="keep the temp test dir")
    args = ap.parse_args(argv)
    return retest(Path(args.run).resolve(), args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
