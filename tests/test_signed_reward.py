"""Tests for signed reward range [-1, 1] in _compute_reward.

Pins the contract:
- Range is [-1, 1] (was [0, 1] before clamp removal).
- Raw signed ratio (pos_earned - neg_penalty) / pos_total passes through.
- Mirror copies in harbor/test_sh.py and harbor/ctrf.py stay byte-aligned.

The previous behaviour clamped to 0.0 via max(0.0, ...) which collapsed
three distinct outcomes (did nothing / hit guardrails / hit guardrails hard)
into the same value. These tests fail under the old clamp and pass under
the new unclamped formula.
"""
from __future__ import annotations

from pathlib import Path

from src.utils.test_executor import _compute_reward


def _results(passed_names: list[str], skipped_names: list[str] | None = None) -> dict:
    out: dict = {n: {"status": "passed"} for n in passed_names}
    for n in skipped_names or []:
        out[n] = {"status": "skipped"}
    return out


def test_all_positive_passing_returns_one() -> None:
    results = _results(["test_a", "test_b"])
    weights = {"test_a": 3, "test_b": 5}
    assert _compute_reward(results, weights) == 1.0


def test_all_positive_failing_returns_zero() -> None:
    results: dict = {"test_a": {"status": "failed"}, "test_b": {"status": "failed"}}
    weights = {"test_a": 3, "test_b": 5}
    assert _compute_reward(results, weights) == 0.0


def test_negative_only_triggered_returns_negative() -> None:
    results = _results(["test_a", "guardrail"])
    weights = {"test_a": 5, "guardrail": -3}
    assert _compute_reward(results, weights) == 0.4


def test_negative_exceeds_positive_returns_below_zero() -> None:
    results = _results(["test_a", "guardrail"])
    weights = {"test_a": 1, "guardrail": -5}
    assert _compute_reward(results, weights) == -4.0


def test_full_penalty_no_positive_returns_floor() -> None:
    results: dict = {
        "test_a": {"status": "failed"},
        "guardrail_1": {"status": "passed"},
        "guardrail_2": {"status": "passed"},
    }
    weights = {"test_a": 1, "guardrail_1": -3, "guardrail_2": -5}
    assert _compute_reward(results, weights) == -8.0


def test_neutral_outcome_returns_zero() -> None:
    results: dict = {"test_a": {"status": "failed"}, "guardrail": {"status": "failed"}}
    weights = {"test_a": 5, "guardrail": -3}
    assert _compute_reward(results, weights) == 0.0


def test_old_behaviour_would_have_clamped_to_zero() -> None:
    results = _results(["guardrail"])
    weights = {"test_a": 5, "guardrail": -5}
    raw = _compute_reward(results, weights)
    assert raw == -1.0
    assert raw != 0.0


def test_distinguishes_did_nothing_from_actively_bad() -> None:
    did_nothing: dict = {"test_a": {"status": "failed"}, "guardrail": {"status": "failed"}}
    actively_bad = _results(["guardrail"])
    weights = {"test_a": 5, "guardrail": -3}
    assert _compute_reward(did_nothing, weights) == 0.0
    assert _compute_reward(actively_bad, weights) == -0.6


def test_skipped_negative_test_does_not_penalize() -> None:
    results = _results(["test_a"], skipped_names=["guardrail"])
    weights = {"test_a": 5, "guardrail": -3}
    assert _compute_reward(results, weights) == 1.0


def test_empty_weights_returns_zero() -> None:
    assert _compute_reward({}, {}) == 0.0


def test_fallback_branch_unchanged_when_no_positive_weights() -> None:
    results: dict = {
        "guardrail_1": {"status": "passed"},
        "guardrail_2": {"status": "failed"},
    }
    weights = {"guardrail_1": -3, "guardrail_2": -1}
    assert _compute_reward(results, weights) == 0.5


def test_rounding_preserved_at_four_places() -> None:
    results = _results(["a", "b", "c"])
    weights = {"a": 1, "b": 1, "c": 1, "d": -1}
    assert _compute_reward(results, weights) == 1.0
    results2 = _results(["a", "b", "d"])
    assert _compute_reward(results2, weights) == round((2 - 1) / 3, 4)


def test_harbor_test_sh_mirrors_formula() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    text = (repo_root / "src/utils/harbor/test_sh.py").read_text(encoding="utf-8")
    assert "reward = (pos_earned - neg_penalty) / pos_total" in text
    assert "max(0.0, (pos_earned - neg_penalty)" not in text


def test_harbor_ctrf_mirrors_formula() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    text = (repo_root / "src/utils/harbor/ctrf.py").read_text(encoding="utf-8")
    assert "return (pos_earned - neg_penalty) / pos_total" in text
    assert "max(0.0, (pos_earned - neg_penalty)" not in text


def test_docstring_advertises_signed_range() -> None:
    assert "signed ratio" in (_compute_reward.__doc__ or "")
    assert "0..1" not in (_compute_reward.__doc__ or "")
