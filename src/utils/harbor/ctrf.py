"""CTRF (Common Test Report Format) builder + test reward calculator.

Ports `_build_ctrf_from_test_result` and `_compute_test_reward` from
kensei2.py (lines 3202-3280).
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Mapping


def _parse_json(blob: Any) -> Any:
    if blob is None or blob == "":
        return None
    if isinstance(blob, (dict, list)):
        return blob
    if isinstance(blob, str):
        try:
            return json.loads(blob)
        except Exception:
            return None
    return None


def _coerce_weights_map(weights: Any) -> Dict[str, float]:
    out: Dict[str, float] = {}
    if isinstance(weights, dict):
        for k, v in weights.items():
            if isinstance(v, (int, float)):
                out[str(k)] = float(v)
    elif isinstance(weights, list):
        for item in weights:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("test")
            w = item.get("weight")
            if name and isinstance(w, (int, float)):
                out[str(name)] = float(w)
    return out


def _coerce_scores_map(scores: Any) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if isinstance(scores, dict):
        for k, v in scores.items():
            out[str(k)] = str(v).lower() if v is not None else ""
    elif isinstance(scores, list):
        for item in scores:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or item.get("test")
            status = item.get("status") or item.get("result")
            if name:
                out[str(name)] = str(status).lower() if status else ""
    return out


def build_ctrf(
    tests_total: int,
    tests_passed: int,
    tests_failed: int,
    tests_errored: int = 0,
    test_scores_json: str = "",
    tests_skipped: int = 0,
    reward: float | None = None,
) -> Dict[str, Any]:
    """Return a CTRF dict for `/logs/verifier/ctrf.json`.

    Mirrors `_build_ctrf_from_test_result` (kensei2.py:3248).

    `reward` (0..1, from compute_test_reward) is the weighted score and is
    surfaced as summary.overall_score/weighted_percentage. It is NOT
    passed/total: distractor penalties make the raw ratio misleading.
    """
    tests_total = int(tests_total or 0)
    tests_passed = int(tests_passed or 0)
    tests_failed = int(tests_failed or 0)
    tests_errored = int(tests_errored or 0)
    tests_skipped = int(tests_skipped or 0)

    scores = _coerce_scores_map(_parse_json(test_scores_json))

    tests: list = []
    if scores:
        for name, status in scores.items():
            tests.append({
                # Bare test name only — drop any "Class::" / "<module>::" /
                # "<file>.py::" qualifiers from the runner's score key.
                "name": name.split("::")[-1],
                "status": status or "failed",
                "duration": 0,
            })
    else:
        synth_total = tests_total + tests_skipped
        for idx in range(synth_total):
            if idx < tests_passed:
                status = "passed"
            elif idx < tests_passed + tests_failed:
                status = "failed"
            elif idx < tests_passed + tests_failed + tests_errored:
                status = "other"
            else:
                status = "skipped"
            tests.append({
                "name": f"test_unknown_{idx}",
                "status": status,
                "duration": 0,
            })

    summary: Dict[str, Any] = {
        "tests": tests_total,
        "passed": tests_passed,
        "failed": tests_failed,
        "pending": 0,
        "skipped": tests_skipped,
        "other": tests_errored,
    }
    if reward is not None:
        summary["overall_score"] = round(float(reward), 4)
        summary["weighted_percentage"] = round(float(reward) * 100.0, 2)

    return {
        "results": {
            "tool": {"name": "pytest", "version": "8.4.1"},
            "summary": summary,
            "tests": tests,
        }
    }


def compute_test_reward(
    test_weights_json: str,
    test_scores_json: str,
    tests_total: int,
    tests_passed: int,
    test_output: str = "",
    test_code: str = "",
) -> float:
    """Return reward in [0, 1].

    Mirrors `_compute_test_reward` (kensei2.py:3202).

    - No positive weights configured → fall back to passed / total ratio.
    - With weights → reward = max(0, (pos_earned - neg_penalty) / pos_total),
      where pos_earned sums positive weights whose tests passed, and
      neg_penalty sums |w| for negative-weighted tests that passed (triggered).
    """
    tests_total = int(tests_total or 0)
    tests_passed = int(tests_passed or 0)

    weights = _coerce_weights_map(_parse_json(test_weights_json))
    scores = _coerce_scores_map(_parse_json(test_scores_json))

    # A.1+A.2 parity with src/utils/harbor/test_sh.py: build three
    # normalized passed-name shapes (full FQN / class-qualified / bare) so a
    # weight key in any of those forms can resolve. Bare-key lookups use a
    # class-aware multiset (any service class's pass counts as the bare key
    # passing); class-qualified keys require precise match (no bare-multiset
    # fallback) so multi-service tasks don't get false credit.
    passed_full: set[str] = set()
    passed_class_qual: set[str] = set()
    passed_bare: set[str] = set()
    for raw_name, status in scores.items():
        if status != "passed":
            continue
        passed_full.add(raw_name)
        parts = raw_name.split("::")
        if len(parts) >= 2:
            passed_bare.add(parts[-1])
        if len(parts) >= 3:
            passed_class_qual.add("::".join(parts[-2:]))

    if not (passed_full or passed_bare) and test_output and weights:
        for name in weights.keys():
            if re.search(re.escape(name) + r"\s+PASSED", test_output):
                passed_full.add(name)
                passed_bare.add(name.split("::")[-1])

    def _key_passed(key: str) -> bool:
        if key in passed_full:
            return True
        if "::" in key:
            return key in passed_class_qual
        return key in passed_bare

    pos_total = sum(w for w in weights.values() if w > 0)
    pos_earned = sum(w for n, w in weights.items() if w > 0 and _key_passed(n))
    neg_penalty = sum(abs(w) for n, w in weights.items() if w < 0 and _key_passed(n))

    if pos_total > 0:
        return (pos_earned - neg_penalty) / pos_total
    if tests_total > 0:
        return tests_passed / tests_total
    return 0.0
