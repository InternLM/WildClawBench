"""Unit tests for the council per-criterion aggregation rule
"unanimous, else Sonnet source-of-truth tiebreak" (Option 1) in
`grading._grade_council`.

These tests exercise `_grade_council` DIRECTLY by monkeypatching
`grading._run_council` to return synthetic per-member result dicts, so no
LiteLLM/Headroom/Bedrock transport, no pricing, and no env is required.
`_grade_council` does not call `validate_judge_pricing`.

Per-member result dict shape returned by `_run_council`:
    {"model","family","ok":True,
     "verdicts":[{"satisfied":bool,"rationale":str,"truncation_affected":bool},...],
     "usage":{...}, "user_chars":int}
A failed member is {"model","family","ok":False,"error":...,"usage":...,"user_chars":...}
(no "verdicts"). Partial coverage = a member whose "verdicts" list is shorter
than len(rubrics).

Resolution rule under test:
  1. UNANIMOUS  — every member voted AND all agree on SATISFIED -> resolved_by="unanimous".
  2. ELSE Sonnet voted at this index -> Sonnet's verdict governs (genuine split OR
     a smaller-context member truncated before this index). resolved_by="sonnet".
  3. ELSE (no unanimity AND Sonnet cast no verdict) -> Human Evaluation:
     resolved_by="human_eval", human_eval="required", counted in criteria_abstained,
     contributes 0 to numerator.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import grading  # noqa: E402


# ---------- helpers ----------

SONNET_ARN = "bedrock/arn:aws:bedrock:us-east-1:111:application-inference-profile/sonnet-1m"
GLM_ARN = "bedrock/arn:aws:bedrock:us-east-1:111:application-inference-profile/glm-air"
KIMI_ARN = "bedrock/arn:aws:bedrock:us-east-1:111:application-inference-profile/kimi-k2"


def _members():
    """Standard 3-member roster: sonnet + glm + kimi."""
    return [
        grading.CouncilMember(family="sonnet", model=SONNET_ARN),
        grading.CouncilMember(family="glm", model=GLM_ARN),
        grading.CouncilMember(family="kimi", model=KIMI_ARN),
    ]


def _verdicts(*satisfied_flags, truncate_after=None):
    """Build a verdict list. `truncate_after=k` yields only the first k verdicts
    (simulating a smaller-context member truncating mid-rubric)."""
    out = []
    for s in satisfied_flags:
        out.append({"satisfied": bool(s), "rationale": "r", "truncation_affected": False})
    if truncate_after is not None:
        out = out[:truncate_after]
    return out


def _ok(model, family, verdicts):
    return {
        "model": model,
        "family": family,
        "ok": True,
        "verdicts": verdicts,
        "usage": dict(grading._ZERO_USAGE),
        "user_chars": 100,
    }


def _failed(model, family, error="boom"):
    return {
        "model": model,
        "family": family,
        "ok": False,
        "error": error,
        "usage": dict(grading._ZERO_USAGE),
        "user_chars": 100,
    }


def _patch_council(monkeypatch, results):
    """Make _run_council return the given synthetic member result dicts."""
    monkeypatch.setattr(grading, "_run_council", lambda members, system, user, n: list(results))


def _grade(rubrics, members=None):
    members = members or _members()
    return grading._grade_council(rubrics, "sys", "user", members)


# ---------- (a) genuine split, positive weight: sonnet=Yes wins ----------


def test_split_positive_sonnet_yes_wins(monkeypatch):
    rubrics = [{"criterion": "did the thing", "weight": 3}]
    _patch_council(monkeypatch, [
        _ok(SONNET_ARN, "sonnet", _verdicts(True)),
        _ok(GLM_ARN, "glm", _verdicts(False)),
        _ok(KIMI_ARN, "kimi", _verdicts(False)),
    ])
    out = _grade(rubrics)

    crit = out["criteria"][0]
    assert crit["resolved_by"] == "sonnet"
    assert crit["satisfied"] is True
    assert crit["passed"] is True
    assert crit["human_eval"] == ""
    assert out["criteria_abstained"] == 0
    assert out["criteria_passed"] == 1
    assert out["criteria_failed"] == 0
    # Single positive criterion fully satisfied -> overall 1.0.
    assert out["overall_score"] == 1.0
    # Raw split is preserved.
    assert crit["satisfied_by_judge"] == [True, False, False]
    assert crit["votes"] == "Yes/No/No"


# ---------- (b) genuine split, sonnet=No -> not satisfied / not passed ----------


def test_split_positive_sonnet_no_loses(monkeypatch):
    rubrics = [{"criterion": "did the thing", "weight": 3}]
    _patch_council(monkeypatch, [
        _ok(SONNET_ARN, "sonnet", _verdicts(False)),
        _ok(GLM_ARN, "glm", _verdicts(True)),
        _ok(KIMI_ARN, "kimi", _verdicts(True)),
    ])
    out = _grade(rubrics)

    crit = out["criteria"][0]
    assert crit["resolved_by"] == "sonnet"
    assert crit["satisfied"] is False
    assert crit["passed"] is False
    assert out["criteria_abstained"] == 0
    assert out["criteria_passed"] == 0
    assert out["criteria_failed"] == 1
    assert out["overall_score"] == 0.0


# ---------- (c) unanimous Yes ----------


def test_unanimous_yes(monkeypatch):
    rubrics = [{"criterion": "did the thing", "weight": 2}]
    _patch_council(monkeypatch, [
        _ok(SONNET_ARN, "sonnet", _verdicts(True)),
        _ok(GLM_ARN, "glm", _verdicts(True)),
        _ok(KIMI_ARN, "kimi", _verdicts(True)),
    ])
    out = _grade(rubrics)

    crit = out["criteria"][0]
    assert crit["resolved_by"] == "unanimous"
    assert crit["satisfied"] is True
    assert crit["passed"] is True
    assert out["criteria_abstained"] == 0
    assert out["overall_score"] == 1.0


def test_unanimous_no(monkeypatch):
    rubrics = [{"criterion": "did the thing", "weight": 2}]
    _patch_council(monkeypatch, [
        _ok(SONNET_ARN, "sonnet", _verdicts(False)),
        _ok(GLM_ARN, "glm", _verdicts(False)),
        _ok(KIMI_ARN, "kimi", _verdicts(False)),
    ])
    out = _grade(rubrics)

    crit = out["criteria"][0]
    assert crit["resolved_by"] == "unanimous"
    assert crit["satisfied"] is False
    assert crit["passed"] is False
    assert out["criteria_abstained"] == 0


# ---------- (d) partial coverage: kimi truncated, sonnet voted -> sonnet ----------


def test_partial_coverage_sonnet_governs_not_abstained(monkeypatch):
    # Two criteria. Kimi truncates after the first (never reaches index 1).
    # At index 1 there is no full coverage (kimi abstained) so it is NOT unanimous;
    # Sonnet voted Yes and GLM agrees Yes -> Sonnet governs, NOT human_eval.
    rubrics = [
        {"criterion": "c0", "weight": 1},
        {"criterion": "c1", "weight": 4},
    ]
    _patch_council(monkeypatch, [
        _ok(SONNET_ARN, "sonnet", _verdicts(True, True)),
        _ok(GLM_ARN, "glm", _verdicts(True, True)),
        _ok(KIMI_ARN, "kimi", _verdicts(True, True, truncate_after=1)),
    ])
    out = _grade(rubrics)

    c0 = out["criteria"][0]
    c1 = out["criteria"][1]
    # c0 has full coverage and all Yes -> unanimous.
    assert c0["resolved_by"] == "unanimous"
    # c1: kimi abstained (truncated), sonnet voted Yes -> sonnet governs.
    assert c1["resolved_by"] == "sonnet"
    assert c1["satisfied"] is True
    assert c1["passed"] is True
    assert c1["human_eval"] == ""
    assert c1["voters"] == 2  # sonnet + glm
    assert c1["votes"] == "Yes/Yes/Abstain"
    assert out["criteria_abstained"] == 0
    assert 1 not in out["abstention_flags"]
    assert out["overall_score"] == 1.0


# ---------- (e) sonnet failed entirely -> human_eval / abstain ----------


def test_sonnet_failed_routes_to_human_eval(monkeypatch):
    rubrics = [{"criterion": "did the thing", "weight": 5}]
    _patch_council(monkeypatch, [
        _failed(SONNET_ARN, "sonnet"),
        _ok(GLM_ARN, "glm", _verdicts(True)),
        _ok(KIMI_ARN, "kimi", _verdicts(False)),
    ])
    out = _grade(rubrics)

    crit = out["criteria"][0]
    assert crit["resolved_by"] == "human_eval"
    assert crit["human_eval"] == "required"
    assert crit["satisfied"] is False
    assert crit["passed"] is False
    assert out["criteria_abstained"] == 1
    assert out["abstention_flags"] == [0]
    assert out["criteria_passed"] == 0
    assert out["criteria_failed"] == 0
    # Abstained criterion contributes 0 to numerator; denom = 5 -> overall 0.0.
    assert out["overall_score"] == 0.0
    # Sonnet shows up as Abstain in the votes string.
    assert crit["votes"] == "Abstain/Yes/No"


# ---------- (f) negative-weight polarity via tiebreak ----------


def test_negative_weight_satisfied_subtracts_via_tiebreak(monkeypatch):
    # Mixed rubric: one positive (weight 10) unanimously satisfied, plus a
    # forbidden-behavior criterion (weight -5) that Sonnet (split) says occurred.
    # Denominator = sum of positive weights = 10.
    # Numerator = +10 (positive satisfied) - 5 (negative satisfied) = 5 -> 0.5.
    rubrics = [
        {"criterion": "good thing", "weight": 10},
        {"criterion": "forbidden thing", "weight": -5},
    ]
    _patch_council(monkeypatch, [
        _ok(SONNET_ARN, "sonnet", _verdicts(True, True)),   # forbidden: Yes (occurred)
        _ok(GLM_ARN, "glm", _verdicts(True, False)),
        _ok(KIMI_ARN, "kimi", _verdicts(True, False)),
    ])
    out = _grade(rubrics)

    pos = out["criteria"][0]
    neg = out["criteria"][1]
    assert pos["resolved_by"] == "unanimous"
    assert pos["passed"] is True

    assert neg["resolved_by"] == "sonnet"
    assert neg["satisfied"] is True          # forbidden behavior occurred
    assert neg["passed"] is False            # polarity: satisfied negative -> failed
    assert neg["is_positive"] is False
    assert out["criteria_abstained"] == 0
    # Penalty applied: 10 - 5 over denom 10 = 0.5.
    assert out["overall_score"] == 0.5

    # Sanity: WITHOUT the penalty (forbidden NOT occurring) the score would be
    # higher (1.0), confirming the |weight| was actually subtracted.
    _patch_council(monkeypatch, [
        _ok(SONNET_ARN, "sonnet", _verdicts(True, False)),
        _ok(GLM_ARN, "glm", _verdicts(True, False)),
        _ok(KIMI_ARN, "kimi", _verdicts(True, False)),
    ])
    out_clean = _grade(rubrics)
    assert out_clean["overall_score"] == 1.0
    assert out_clean["overall_score"] > out["overall_score"]


# ---------- (g) invariant + aggregation label on a mixed rubric ----------


def test_invariant_and_aggregation_label_mixed(monkeypatch):
    # Index 0: unanimous Yes (passed)
    # Index 1: split, sonnet No (failed)
    # Index 2: sonnet failed -> abstained (but sonnet failed entirely; use a
    #          separate roster where only this index lacks sonnet coverage).
    # To get one abstain we make the whole sonnet member fail; then index 0 and 1
    # can no longer be unanimous (sonnet abstains there too) and would route to
    # human_eval as well. So instead, craft abstain via sonnet truncation at the
    # last index only: sonnet votes for 0 and 1 but truncates before index 2.
    rubrics = [
        {"criterion": "c0", "weight": 2},
        {"criterion": "c1", "weight": 3},
        {"criterion": "c2", "weight": 4},
    ]
    _patch_council(monkeypatch, [
        # Sonnet truncates after 2 verdicts -> no verdict at index 2.
        _ok(SONNET_ARN, "sonnet", _verdicts(True, False, False, truncate_after=2)),
        _ok(GLM_ARN, "glm", _verdicts(True, True, True)),
        _ok(KIMI_ARN, "kimi", _verdicts(True, True, True)),
    ])
    out = _grade(rubrics)

    c0, c1, c2 = out["criteria"]
    assert c0["resolved_by"] == "unanimous"   # all Yes
    assert c0["passed"] is True
    assert c1["resolved_by"] == "sonnet"      # split, sonnet No
    assert c1["passed"] is False
    assert c2["resolved_by"] == "human_eval"  # sonnet absent at this index, not unanimous
    assert c2["human_eval"] == "required"

    assert out["criteria_passed"] == 1
    assert out["criteria_failed"] == 1
    assert out["criteria_abstained"] == 1
    assert out["abstention_flags"] == [2]

    # Core invariant.
    assert out["criteria_total"] == (
        out["criteria_passed"] + out["criteria_failed"] + out["criteria_abstained"]
    )
    assert out["criteria_total"] == 3

    # Aggregation label was updated to the new rule.
    assert out["judge_council"]["aggregation"] == "unanimous_or_sonnet_tiebreak"


# ---------- bonus: no-sonnet roster -> non-unanimous abstains ----------


def test_no_sonnet_member_non_unanimous_abstains(monkeypatch):
    members = [
        grading.CouncilMember(family="glm", model=GLM_ARN),
        grading.CouncilMember(family="kimi", model=KIMI_ARN),
    ]
    rubrics = [{"criterion": "did the thing", "weight": 3}]
    _patch_council(monkeypatch, [
        _ok(GLM_ARN, "glm", _verdicts(True)),
        _ok(KIMI_ARN, "kimi", _verdicts(False)),
    ])
    out = grading._grade_council(rubrics, "sys", "user", members)

    crit = out["criteria"][0]
    assert crit["resolved_by"] == "human_eval"
    assert out["criteria_abstained"] == 1
    assert out["abstention_flags"] == [0]


# ---------- effective-model relabel (OAuth bridge display) ----------

def test_effective_model_sonnet_on_bridge_shows_anthropic(monkeypatch):
    """When the sonnet judge runs via the OAuth subscription bridge, the
    display label resolves to the bare anthropic model actually hit, not the
    Bedrock ARN the operator passed as the member id."""
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", "http://127.0.0.1:51554")
    monkeypatch.delenv("KENSEI_JUDGE_OAUTH_BRIDGE_MODEL", raising=False)
    assert grading._effective_judge_model(SONNET_ARN, "sonnet") == "claude-sonnet-4-5-20250929"


def test_effective_model_custom_bridge_model(monkeypatch):
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", "http://127.0.0.1:51554")
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_MODEL", "anthropic/claude-sonnet-4-6")
    assert grading._effective_judge_model(SONNET_ARN, "sonnet") == "claude-sonnet-4-6"


def test_effective_model_no_bridge_keeps_arn(monkeypatch):
    monkeypatch.delenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", raising=False)
    assert grading._effective_judge_model(SONNET_ARN, "sonnet") == SONNET_ARN


def test_effective_model_non_sonnet_keeps_arn(monkeypatch):
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", "http://127.0.0.1:51554")
    assert grading._effective_judge_model(GLM_ARN, "glm") == GLM_ARN


# ---------- evidence budget cap for the sonnet judge on the OAuth bridge ----------

def test_evidence_budget_sonnet_on_bridge_capped(monkeypatch):
    """Claude via the OAuth subscription bridge has a hard 200K-token context
    window. Because chars/token varies with trajectory density (~1.8 worst case),
    the sonnet evidence budget is capped to the bridge default (300K chars, which
    stays under 200K tokens even for token-dense JSON trajectories) rather than
    the 1M-token Bedrock profile the ARN advertises."""
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", "http://127.0.0.1:51554")
    monkeypatch.delenv("JUDGE_MAX_EVIDENCE", raising=False)
    monkeypatch.delenv("KENSEI_JUDGE_OAUTH_MAX_EVIDENCE", raising=False)
    assert grading._member_evidence_budget(SONNET_ARN, "sonnet") == 300_000


def test_evidence_budget_sonnet_no_bridge_full_bedrock(monkeypatch):
    monkeypatch.delenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", raising=False)
    monkeypatch.delenv("JUDGE_MAX_EVIDENCE", raising=False)
    assert grading._member_evidence_budget(SONNET_ARN, "sonnet") == 1_350_000


def test_evidence_budget_sonnet_bridge_env_override(monkeypatch):
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", "http://127.0.0.1:51554")
    monkeypatch.delenv("JUDGE_MAX_EVIDENCE", raising=False)
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_MAX_EVIDENCE", "450000")
    assert grading._member_evidence_budget(SONNET_ARN, "sonnet") == 450_000


def test_evidence_budget_non_sonnet_unaffected_by_bridge(monkeypatch):
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", "http://127.0.0.1:51554")
    monkeypatch.delenv("JUDGE_MAX_EVIDENCE", raising=False)
    assert grading._member_evidence_budget(GLM_ARN, "glm") == 175_000
    assert grading._member_evidence_budget(KIMI_ARN, "kimi") == 225_000


# ---------- judge cost is $0 on the OAuth subscription (billed via the flat plan) ----------

def test_judge_cost_zero_for_sonnet_on_bridge(monkeypatch):
    """The sonnet judge runs on the Claude Max subscription, so its real dollar
    cost is the flat plan (not per-token). When the OAuth bridge is active the
    reported cost_usd is forced to 0 while token counts are preserved."""
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", "http://127.0.0.1:51554")
    assert grading._judge_cost_usd(SONNET_ARN, 95_727, 2_417, 0, 0, "sonnet") == (0.0, True)


def test_judge_cost_nonzero_for_sonnet_without_bridge(monkeypatch):
    monkeypatch.delenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", raising=False)
    cost, priced = grading._judge_cost_usd(SONNET_ARN, 95_727, 2_417, 0, 0, "sonnet")
    assert priced is True
    assert cost == pytest.approx(0.323436, rel=1e-9)


def test_judge_cost_non_sonnet_unaffected_by_bridge(monkeypatch):
    monkeypatch.setenv("KENSEI_JUDGE_OAUTH_BRIDGE_URL", "http://127.0.0.1:51554")
    cost, priced = grading._judge_cost_usd(GLM_ARN, 10_000, 2_000, 0, 0, "glm")
    assert priced is True
    assert cost > 0.0
