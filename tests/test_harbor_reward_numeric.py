"""NUMERIC execution tests for the signed-weight test-reward formula.

Two mirror implementations must produce identical numbers:
  1. src/utils/harbor/ctrf.py :: compute_test_reward  (imported directly)
  2. the python heredoc embedded in src/utils/harbor/test_sh.py's test.sh
     (extracted, path-rewritten to tmp_path, and exec'd)

Today the suite only greps the formula source text
(tests/test_signed_reward.py:110-121). This file adds the actual numbers:
  - mixed weights giving exactly 0.25
  - unclamped negative passthrough (-7.0)
  - all-negative fallback CURRENT behavior (1.0 when the guardrail triggers)
  - empty weights -> 0.0

Everything runs offline; the heredoc is exec'd in-process against a fake
ctrf.json / test_weights.json written into tmp_path (no pytest/uv/network).

Import bootstrapping mirrors tests/test_docker_env_validation.py.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.utils.harbor.ctrf import (  # noqa: E402
    _coerce_scores_map,
    _coerce_weights_map,
    _parse_json,
    build_ctrf,
    compute_test_reward,
)
from src.utils.harbor.test_sh import generate_harbor_test_sh  # noqa: E402


# --------------------------------------------------------------------------
# Heredoc extraction + hermetic exec harness
# --------------------------------------------------------------------------

_HEREDOC_RE = re.compile(r"python3 - <<'PY'\n(.*?)\nPY", re.DOTALL)


def _extract_scoring_python() -> str:
    sh = generate_harbor_test_sh()
    m = _HEREDOC_RE.search(sh)
    assert m is not None, "could not locate the python scoring heredoc in test.sh"
    return m.group(1)


def _run_test_sh_scoring(
    tmp_path: Path,
    monkeypatch,
    *,
    ctrf: dict,
    weights,
) -> float:
    """Exec the extracted test.sh python heredoc against a fake filesystem and
    return the reward it writes to reward.txt.

    The heredoc hard-codes /logs/verifier/{ctrf.json,reward.txt} and reads
    test_weights.json from $TEST_DIR. We rewrite the /logs/verifier prefix to a
    tmp dir and point TEST_DIR at another tmp dir, then exec the (unmodified in
    every other respect) source so we are exercising the SHIPPED formula.
    """
    verifier_dir = tmp_path / "verifier"
    verifier_dir.mkdir()
    test_dir = tmp_path / "tests"
    test_dir.mkdir()

    (verifier_dir / "ctrf.json").write_text(
        json.dumps(ctrf), encoding="utf-8"
    )
    (test_dir / "test_weights.json").write_text(
        json.dumps(weights), encoding="utf-8"
    )

    monkeypatch.setenv("TEST_DIR", str(test_dir))

    src = _extract_scoring_python()
    # Rewrite only the two hard-coded absolute verifier paths so the heredoc
    # reads/writes inside tmp_path. The scoring logic itself is untouched.
    src = src.replace('"/logs/verifier"', json.dumps(str(verifier_dir)))
    src = src.replace(
        'ctrf_path = "/logs/verifier/ctrf.json"',
        'ctrf_path = %s' % json.dumps(str(verifier_dir / "ctrf.json")),
    )
    src = src.replace(
        'reward_path = "/logs/verifier/reward.txt"',
        'reward_path = %s' % json.dumps(str(verifier_dir / "reward.txt")),
    )
    # Guard: the two path constants must have been rewritten.
    assert "/logs/verifier/ctrf.json" not in src
    assert "/logs/verifier/reward.txt" not in src

    exec(compile(src, "<test_sh_heredoc>", "exec"), {"__name__": "__main__"})

    return float((verifier_dir / "reward.txt").read_text().strip())


def _ctrf_from_scores(scores: dict, *, total: int, passed: int) -> dict:
    """Build a minimal ctrf dict whose tests[] carry the given statuses.

    Names are emitted bare (no '::') so both mirror implementations resolve
    them via the bare-name lookup path.
    """
    tests = [{"name": n, "status": st, "duration": 0} for n, st in scores.items()]
    return {
        "results": {
            "tool": {"name": "pytest", "version": "8.4.1"},
            "summary": {"tests": total, "passed": passed},
            "tests": tests,
        }
    }


# ==========================================================================
# ctrf.py :: compute_test_reward — direct numeric pins
# ==========================================================================

class TestComputeTestRewardNumbers:
    def test_all_positive_passing_is_one(self):
        w = json.dumps({"a": 3, "b": 5})
        s = json.dumps({"a": "passed", "b": "passed"})
        assert compute_test_reward(w, s, 2, 2) == pytest.approx(1.0)

    def test_all_positive_failing_is_zero(self):
        w = json.dumps({"a": 3, "b": 5})
        s = json.dumps({"a": "failed", "b": "failed"})
        assert compute_test_reward(w, s, 2, 0) == pytest.approx(0.0)

    def test_mixed_weights_exact_quarter(self):
        # pos_total = 3 + 1 = 4; a passes -> earned 3; b fails; guard passes
        # -> penalty 2. (3 - 2) / 4 = 0.25 exactly.
        w = json.dumps({"a": 3, "b": 1, "guard": -2})
        s = json.dumps({"a": "passed", "b": "failed", "guard": "passed"})
        assert compute_test_reward(w, s, 3, 1) == pytest.approx(0.25)

    def test_mixed_weights_half(self):
        # (3 + 1 earned) - 0 penalty over pos_total 4 with one positive failing.
        w = json.dumps({"a": 3, "b": 1, "c": 4})
        # earned a+b = 4, c fails; pos_total = 8 -> 0.5
        s = json.dumps({"a": "passed", "b": "passed", "c": "failed"})
        assert compute_test_reward(w, s, 3, 2) == pytest.approx(0.5)

    def test_unclamped_negative_passthrough_minus_seven(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # Despite the docstring claiming `max(0, ...)`, ctrf.py does NOT clamp:
        # a large triggered guardrail drives the raw ratio well below zero.
        # pos_total = 1; earned 1; penalty 8 -> (1 - 8) / 1 = -7.0.
        w = json.dumps({"a": 1, "g": -8})
        s = json.dumps({"a": "passed", "g": "passed"})
        assert compute_test_reward(w, s, 2, 2) == pytest.approx(-7.0)

    def test_negative_only_triggered_is_negative(self):
        # pos_total 5, earned 5, guard -3 triggered -> (5 - 3)/5 = 0.4
        w = json.dumps({"a": 5, "guard": -3})
        s = json.dumps({"a": "passed", "guard": "passed"})
        assert compute_test_reward(w, s, 2, 2) == pytest.approx(0.4)

    def test_all_negative_fallback_returns_one_when_triggered(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # With no positive weights, pos_total == 0 so the formula falls back to
        # passed/total. When the guardrail-only test PASSES (i.e. the bad
        # behavior is present) and all tests pass, reward is a spurious 1.0 —
        # the guardrail penalty is silently lost on the all-negative path.
        w = json.dumps({"guard": -3})
        s = json.dumps({"guard": "passed"})
        assert compute_test_reward(w, s, 1, 1) == pytest.approx(1.0)

    def test_all_negative_fallback_uses_passed_ratio(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # 1 of 2 tests passed on the all-negative path -> 0.5, again ignoring
        # the negative weight entirely.
        w = json.dumps({"guard": -3})
        s = json.dumps({"guard": "passed"})
        assert compute_test_reward(w, s, 2, 1) == pytest.approx(0.5)

    def test_empty_weights_no_tests_is_zero(self):
        assert compute_test_reward(json.dumps({}), json.dumps({}), 0, 0) == pytest.approx(0.0)

    def test_empty_weights_falls_back_to_passed_ratio(self):
        # No weights at all but tests ran -> passed/total.
        assert compute_test_reward("", "", 4, 3) == pytest.approx(0.75)

    def test_list_form_weights_and_scores(self):
        # weights + scores supplied as list-of-dicts rather than maps.
        w = json.dumps([
            {"name": "a", "weight": 3},
            {"test": "b", "weight": 1},
        ])
        s = json.dumps([
            {"name": "a", "status": "passed"},
            {"test": "b", "result": "failed"},
        ])
        # earned 3 over pos_total 4 -> 0.75
        assert compute_test_reward(w, s, 2, 1) == pytest.approx(0.75)

    def test_fqn_weight_key_resolves_against_bare_ctrf_name(self):
        # weight key is a full pytest FQN; scores emit the bare name. The
        # bare-multiset lookup (A.1) must still credit it.
        w = json.dumps({"tests/test_outputs.py::TestFoo::test_bar": 5})
        s = json.dumps({"tests/test_outputs.py::TestFoo::test_bar": "passed"})
        assert compute_test_reward(w, s, 1, 1) == pytest.approx(1.0)

    def test_bare_weight_key_resolves_against_fqn_ctrf_name(self):
        # weight key is bare; score name is a full FQN -> bare lookup matches
        # via parts[-1].
        w = json.dumps({"test_bar": 5})
        s = json.dumps({"tests/test_outputs.py::TestFoo::test_bar": "passed"})
        assert compute_test_reward(w, s, 1, 1) == pytest.approx(1.0)

    def test_class_qualified_key_requires_precise_match(self):
        # A class-qualified weight key must NOT be satisfied by a different
        # class's bare pass (A.2 precision guarantee).
        w = json.dumps({"TestFoo::test_bar": 5})
        s = json.dumps({"tests/test_outputs.py::TestOther::test_bar": "passed"})
        # bare "test_bar" passed but class-qualified key demands TestFoo -> 0
        assert compute_test_reward(w, s, 1, 1) == pytest.approx(0.0)

    def test_test_output_regex_fallback(self):
        # No structured scores, but raw -rA test_output mentions PASSED; the
        # regex fallback credits the weight key.
        w = json.dumps({"test_ok": 5})
        out = "tests/test_outputs.py::test_ok PASSED\n"
        assert compute_test_reward(w, "", 1, 1, test_output=out) == pytest.approx(1.0)


class TestCtrfHelpers:
    def test_parse_json_variants(self):
        assert _parse_json(None) is None
        assert _parse_json("") is None
        assert _parse_json('{"a": 1}') == {"a": 1}
        assert _parse_json([1, 2]) == [1, 2]
        assert _parse_json("not json") is None

    def test_coerce_weights_map_dict_skips_nonnumeric(self):
        m = _coerce_weights_map({"a": 3, "b": "x", "c": -1})
        assert m == {"a": 3.0, "c": -1.0}

    def test_coerce_weights_map_list(self):
        m = _coerce_weights_map([
            {"name": "a", "weight": 2},
            {"test": "b", "weight": -1},
            {"weight": 5},  # no name -> dropped
            "bogus",         # non-dict -> skipped
        ])
        assert m == {"a": 2.0, "b": -1.0}

    def test_coerce_scores_map_normalizes_status(self):
        m = _coerce_scores_map({"a": "PASSED", "b": None})
        assert m == {"a": "passed", "b": ""}

    def test_coerce_scores_map_list(self):
        m = _coerce_scores_map([
            {"name": "a", "status": "Passed"},
            {"test": "b", "result": "Failed"},
        ])
        assert m == {"a": "passed", "b": "failed"}


class TestBuildCtrf:
    def test_summary_counts_and_reward_surfaced(self):
        ctrf = build_ctrf(
            tests_total=3, tests_passed=2, tests_failed=1, reward=0.25,
        )
        summary = ctrf["results"]["summary"]
        assert summary["tests"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1
        assert summary["overall_score"] == pytest.approx(0.25)
        assert summary["weighted_percentage"] == pytest.approx(25.0)

    def test_tests_synthesized_when_no_scores(self):
        ctrf = build_ctrf(
            tests_total=3, tests_passed=1, tests_failed=1, tests_errored=1,
        )
        statuses = [t["status"] for t in ctrf["results"]["tests"]]
        assert statuses == ["passed", "failed", "other"]

    def test_scores_json_drives_test_names_bare(self):
        ctrf = build_ctrf(
            tests_total=1, tests_passed=1, tests_failed=0,
            test_scores_json=json.dumps(
                {"tests/test_outputs.py::TestX::test_bar": "passed"}
            ),
        )
        names = [t["name"] for t in ctrf["results"]["tests"]]
        # qualifiers dropped -> bare test name
        assert names == ["test_bar"]

    def test_reward_omitted_leaves_no_overall_score(self):
        ctrf = build_ctrf(tests_total=1, tests_passed=1, tests_failed=0)
        assert "overall_score" not in ctrf["results"]["summary"]

    def test_skipped_tests_synthesized(self):
        ctrf = build_ctrf(
            tests_total=1, tests_passed=1, tests_failed=0, tests_skipped=1,
        )
        statuses = [t["status"] for t in ctrf["results"]["tests"]]
        assert statuses == ["passed", "skipped"]
        assert ctrf["results"]["summary"]["skipped"] == 1


# ==========================================================================
# test_sh.py heredoc — exec the SHIPPED bash-embedded python numerically
# ==========================================================================

class TestTestShHeredocNumbers:
    def test_mixed_weights_exact_quarter(self, tmp_path, monkeypatch):
        weights = {"a": 3, "b": 1, "guard": -2}
        scores = {"a": "passed", "b": "failed", "guard": "passed"}
        ctrf = _ctrf_from_scores(scores, total=3, passed=1)
        reward = _run_test_sh_scoring(tmp_path, monkeypatch, ctrf=ctrf, weights=weights)
        assert reward == pytest.approx(0.25)

    def test_unclamped_negative_passthrough_minus_seven(self, tmp_path, monkeypatch):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # The shipped heredoc writes reward=-7.000000 (no clamp), matching
        # ctrf.py. reward.txt therefore CAN hold a negative number in prod.
        weights = {"a": 1, "g": -8}
        scores = {"a": "passed", "g": "passed"}
        ctrf = _ctrf_from_scores(scores, total=2, passed=2)
        reward = _run_test_sh_scoring(tmp_path, monkeypatch, ctrf=ctrf, weights=weights)
        assert reward == pytest.approx(-7.0)

    def test_all_negative_fallback_returns_one(self, tmp_path, monkeypatch):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # pos_total == 0 -> passed/total fallback -> 1.0 even though the
        # guardrail fired. Guardrail penalty is lost on the all-negative path.
        weights = {"guard": -3}
        scores = {"guard": "passed"}
        ctrf = _ctrf_from_scores(scores, total=1, passed=1)
        reward = _run_test_sh_scoring(tmp_path, monkeypatch, ctrf=ctrf, weights=weights)
        assert reward == pytest.approx(1.0)

    def test_empty_weights_no_tests_is_zero(self, tmp_path, monkeypatch):
        ctrf = _ctrf_from_scores({}, total=0, passed=0)
        reward = _run_test_sh_scoring(tmp_path, monkeypatch, ctrf=ctrf, weights={})
        assert reward == pytest.approx(0.0)

    def test_all_positive_passing_is_one(self, tmp_path, monkeypatch):
        weights = {"a": 3, "b": 5}
        scores = {"a": "passed", "b": "passed"}
        ctrf = _ctrf_from_scores(scores, total=2, passed=2)
        reward = _run_test_sh_scoring(tmp_path, monkeypatch, ctrf=ctrf, weights=weights)
        assert reward == pytest.approx(1.0)

    def test_heredoc_rewrites_ctrf_summary_in_place(self, tmp_path, monkeypatch):
        # The heredoc also patches overall_score / weighted_percentage back
        # into ctrf.json. Confirm that round-trips.
        weights = {"a": 3, "b": 1, "guard": -2}
        scores = {"a": "passed", "b": "failed", "guard": "passed"}
        ctrf = _ctrf_from_scores(scores, total=3, passed=1)
        verifier_dir = tmp_path / "verifier"
        # run scoring (writes reward + patches ctrf)
        reward = _run_test_sh_scoring(tmp_path, monkeypatch, ctrf=ctrf, weights=weights)
        patched = json.loads((verifier_dir / "ctrf.json").read_text())
        summary = patched["results"]["summary"]
        assert summary["overall_score"] == pytest.approx(round(reward, 4))
        assert summary["weighted_percentage"] == pytest.approx(round(reward * 100.0, 2))


# ==========================================================================
# Cross-check: the two mirror implementations agree on the SAME numbers.
# ==========================================================================

_PARITY_CASES = [
    # (weights, scores, total, passed, expected)
    ({"a": 3, "b": 1, "guard": -2}, {"a": "passed", "b": "failed", "guard": "passed"}, 3, 1, 0.25),
    ({"a": 1, "g": -8}, {"a": "passed", "g": "passed"}, 2, 2, -7.0),
    ({"guard": -3}, {"guard": "passed"}, 1, 1, 1.0),
    ({}, {}, 0, 0, 0.0),
    ({"a": 3, "b": 5}, {"a": "passed", "b": "passed"}, 2, 2, 1.0),
    ({"a": 5, "guard": -3}, {"a": "passed", "guard": "passed"}, 2, 2, 0.4),
]


@pytest.mark.parametrize("weights,scores,total,passed,expected", _PARITY_CASES)
def test_ctrf_and_test_sh_mirrors_agree(tmp_path, monkeypatch, weights, scores, total, passed, expected):
    """The python ported into ctrf.py and the python embedded in test.sh must
    compute byte-identical rewards for the same inputs (the mirror contract
    that tests/test_signed_reward.py only checks by source-grep)."""
    direct = compute_test_reward(json.dumps(weights), json.dumps(scores), total, passed)
    ctrf = _ctrf_from_scores(scores, total=total, passed=passed)
    via_sh = _run_test_sh_scoring(tmp_path, monkeypatch, ctrf=ctrf, weights=weights)
    assert direct == pytest.approx(expected)
    assert via_sh == pytest.approx(expected)
    assert direct == pytest.approx(via_sh)
