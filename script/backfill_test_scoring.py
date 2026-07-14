#!/usr/bin/env python3
"""Backfill correct test-channel scoring into an already-generated bundle.

WHY: repackage_to_bundle._weighted_test_percentage previously inverted the
negative-weight (guardrail) polarity — it penalised guardrail tests the agent
*avoided* (status != passed) instead of guardrails that *fired* (status ==
passed). That collapsed test_weights_percentage (and the derived final_reward /
pass_summary averages) toward 0 for every guardrail-heavy task.

This script recomputes, in place, from each run's report.json:
  * pytest.tests           -> test_weights_percentage   (corrected polarity)
  * final_reward           = mean(test_weights_percentage, rubric_weights_percentage)
and rebuilds every per-model pass_summary.json from the corrected runs.

rubric_weights_percentage is LEFT UNTOUCHED: the rubric grader already uses the
correct polarity (grading.py:_criterion_pass_from_satisfied), so the shipped
value already equals (Sigma passed_positive - Sigma |triggered_negative|) /
Sigma positive. Verified: recomputing it from the report rubric block reproduces
score.json exactly.

Idempotent. Run:  python3 script/backfill_test_scoring.py [BUNDLE_DIR]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def weighted_test_percentage(tests: list[dict]) -> float:
    """Canonical weighted test reward as a 0-100 percentage.

    reward = max(0, (pos_earned - neg_penalty) / pos_total), where a NEGATIVE
    (guardrail) test is penalised only when it PASSED (the forbidden behaviour
    fired). Falls back to a simple pass-ratio when no positive weights exist.
    """
    pos_total = sum(t["weight"] for t in tests if t["weight"] > 0)
    if pos_total > 0:
        pos_earned = sum(t["weight"] for t in tests if t["weight"] > 0 and t["passed"])
        neg_penalty = sum(abs(t["weight"]) for t in tests if t["weight"] < 0 and t["passed"])
        return round(max(0.0, (pos_earned - neg_penalty) / pos_total) * 100.0, 2)
    total = len(tests)
    passed = sum(1 for t in tests if t["passed"])
    return round((passed / total) * 100.0, 2) if total else 0.0


def main() -> int:
    bundle = Path(sys.argv[1] if len(sys.argv) > 1 else "output_bundle")
    if not bundle.is_dir():
        print(f"bundle dir not found: {bundle}", file=sys.stderr)
        return 1

    # task/model dir -> list of per_run summary entries (in run order)
    per_model: dict[Path, list[dict]] = defaultdict(list)
    changed = 0

    for report_path in sorted(bundle.glob("*/trajectories/*/run_*/report.json")):
        report = json.loads(report_path.read_text())
        tests = report.get("pytest", {}).get("tests", [])
        old_test = report.get("test_weights_percentage")
        new_test = weighted_test_percentage(tests)
        rubric_pct = float(report.get("rubric_weights_percentage", 0.0))
        new_final = round((new_test + rubric_pct) / 2.0, 2)

        if (old_test != new_test) or (report.get("final_reward") != new_final):
            report["test_weights_percentage"] = new_test
            report["final_reward"] = new_final
            report_path.write_text(json.dumps(report, indent=2) + "\n")
            changed += 1
            print(f"  fixed {report_path.relative_to(bundle)}: "
                  f"test {old_test} -> {new_test}, final -> {new_final}")

        model_dir = report_path.parent.parent  # .../trajectories/<model>
        per_model[model_dir].append({
            "run_index": report["run_index"],
            "include_multimodal": report.get("include_multimodal"),
            "test_weights_percentage": new_test,
            "rubric_weights_percentage": rubric_pct,
            "combined_score": new_final,
        })

    # Rebuild each pass_summary.json from corrected runs.
    for model_dir, runs in per_model.items():
        runs.sort(key=lambda r: r["run_index"])
        n = len(runs)
        summary = {
            "model": model_dir.name,
            "runs": n,
            "average_combined_score": round(sum(r["combined_score"] for r in runs) / n, 2),
            "average_test_weights_percentage": round(sum(r["test_weights_percentage"] for r in runs) / n, 2),
            "average_rubric_weights_percentage": round(sum(r["rubric_weights_percentage"] for r in runs) / n, 2),
            "per_run": runs,
        }
        (model_dir / "pass_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(f"\nreport.json files changed: {changed}")
    print(f"pass_summary.json files rebuilt: {len(per_model)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
