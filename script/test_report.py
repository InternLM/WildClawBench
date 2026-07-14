#!/usr/bin/env python3
"""Generate a weighted pytest report for published trajectories.

For each trajectory: locate test_outputs.py, rebuild agent_state.json from the
captured snapshot (+ assistant text), run the suite, and compute the weighted
reward exactly like the harness (test_sh.py):

    reward = max(0, (earned_positive - violated_redline_penalty) / total_positive)

Scores are a FLOOR: the API audit log is not persisted in trajectories, so
audit-dependent checkers cannot pass.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.state_extractor import build_agent_state  # noqa: E402


def _assistant_text(output_json: Path) -> str:
    if not output_json.is_file():
        return ""
    try:
        msgs = json.loads(output_json.read_text(encoding="utf-8")).get("messages", [])
    except (OSError, json.JSONDecodeError):
        return ""
    out = []
    for row in msgs:
        msg = row.get("message") if isinstance(row, dict) else None
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            c = msg.get("content")
            if isinstance(c, str):
                out.append(c)
            elif isinstance(c, list):
                out += [b["text"] for b in c if isinstance(b, dict) and isinstance(b.get("text"), str)]
    return "\n".join(out)


def _norm(name: str) -> str:
    return name.rsplit("::", 1)[-1].strip()


def _find_suite(traj: Path) -> Path | None:
    cands = list((traj / "input").rglob("test_outputs.py"))
    cands = [c for c in cands if (c.parent / "test_weights.json").is_file()] or cands
    return cands[0] if cands else None


def _snapshot(traj: Path) -> Path | None:
    runs = sorted(traj.glob("output-raw/trajectories/*/run_*"))
    if not runs:
        return None
    snap = runs[-1] / "snapshot" / "workspace_after" / "mock_data"
    return snap if snap.is_dir() else None


def regrade(traj: Path) -> dict:
    suite = _find_suite(traj)
    snap = _snapshot(traj)
    if not suite or not snap:
        return {"task": traj.name, "status": "skip", "reason": "no suite or no snapshot"}

    run = sorted(traj.glob("output-raw/trajectories/*/run_*"))[-1]
    state = build_agent_state(store_snapshot_dir=snap, last_response=_assistant_text(run / "output.json"))
    (suite.parent / "agent_state.json").write_text(json.dumps(state, ensure_ascii=False, default=str))

    # per-test pass/fail via verbose output
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", suite.name, "-v", "--tb=no", "--no-header", "-p", "no:cacheprovider"],
        cwd=suite.parent, capture_output=True, text=True,
    )
    results = {}
    for line in proc.stdout.splitlines():
        m = re.search(r"::(\S+)\s+(PASSED|FAILED|SKIPPED|ERROR)", line)
        if m:
            results[_norm(m.group(1))] = m.group(2)

    weights = {}
    wf = suite.parent / "test_weights.json"
    if wf.is_file():
        try:
            raw = json.loads(wf.read_text())
            if isinstance(raw, dict):
                weights = {_norm(k): float(v) for k, v in raw.items() if isinstance(v, (int, float))}
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    passed = {_norm(k) for k, v in results.items() if v == "PASSED"}
    ran = {_norm(k) for k, v in results.items() if v in ("PASSED", "FAILED")}
    pos_total = sum(w for w in weights.values() if w > 0)
    pos_earned = sum(w for n, w in weights.items() if w > 0 and n in passed)
    neg_penalty = sum(abs(w) for n, w in weights.items() if w < 0 and n in ran and n not in passed)
    reward = max(0.0, (pos_earned - neg_penalty) / pos_total) if pos_total > 0 else 0.0

    counts = {"PASSED": 0, "FAILED": 0, "SKIPPED": 0, "ERROR": 0}
    for v in results.values():
        counts[v] = counts.get(v, 0) + 1

    return {
        "task": traj.name, "status": "ok", "suite": str(suite.relative_to(traj)),
        "total": len(results), **counts,
        "pos_total": pos_total, "pos_earned": pos_earned, "neg_penalty": neg_penalty,
        "weighted_reward": round(reward, 4),
        "failures": sorted(n for n, v in results.items() if v == "FAILED"),
    }


def main(argv):
    targets = [Path(a) for a in argv] or sorted(Path("trajectories").glob("*"))
    targets = [t for t in targets if t.is_dir()]
    reports = [regrade(t) for t in targets]

    print("=" * 92)
    print("  WEIGHTED TEST REPORT — trajectories (FLOOR scores; API audit log not persisted)")
    print("=" * 92)
    hdr = f"{'TASK':<24}{'pass':>6}{'fail':>6}{'skip':>6}{'tot':>6}{'wt_earned':>11}{'wt_total':>10}{'reward':>9}"
    print(hdr); print("-" * 92)
    for r in reports:
        if r["status"] != "ok":
            print(f"{r['task']:<24}  SKIP ({r['reason']})"); continue
        print(f"{r['task']:<24}{r['PASSED']:>6}{r['FAILED']:>6}{r['SKIPPED']:>6}{r['total']:>6}"
              f"{r['pos_earned']:>11.1f}{r['pos_total']:>10.1f}{r['weighted_reward']:>9.2%}")
    print("=" * 92)

    out = Path("trajectories/TEST_REPORT.json")
    out.write_text(json.dumps(reports, indent=2))
    print(f"Full per-test detail (incl. failure lists) → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
