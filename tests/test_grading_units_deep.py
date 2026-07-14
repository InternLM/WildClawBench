"""Deep unit coverage for src/utils/grading.py helpers NOT already covered by
tests/test_judge_sonnet_tiebreak.py (which owns the `_grade_council`
aggregation rule). This file targets the untested lower-level machinery:

  * _extract_weight        — full weight/score/missing/non-numeric/NaN matrix
  * _parse_verdict_text    — valid / truncated / garbage / extra / empty vs _VERDICT_RE
  * _judge_user_prompt     — "[points: w]" rubric-block rendering against the REAL
                             system_prompts/judge_user.md format string
  * _split_evidence        — transcript-marker partition
  * _collect_deliverable_files / _gather_evidence — over real tmp_path artifact trees
  * a handful of _grade_council REWARD edge cases the tiebreak file does not
    exercise: all-negative rubric -> 0.0, mixed dict/string numerator inflation,
    NaN weight -> overall 1.0 (all three PIN CURRENT — possibly-defect — behavior)
  * print_summary / print_global_summary rollup math (capsys, tmp_path)

All tests are offline/deterministic: no docker, no network, no AWS/Bedrock, no
LiteLLM. The council-transport helpers are exercised only via monkeypatched
`grading._run_council` returning synthetic per-member result dicts, so no real
judge call is ever made. Temp data goes to pytest tmp_path only.
"""
from __future__ import annotations

import io
import json
import math
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

# sys.path bootstrap: repo root before "from src..." imports (matches
# tests/test_signed_reward.py / test_docker_env_validation.py convention).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import grading  # noqa: E402


# ---------------------------------------------------------------------------
# _extract_weight — full matrix
# ---------------------------------------------------------------------------


def test_extract_weight_missing_both_defaults_to_one():
    # No 'weight' and no 'score' key -> canonical positive default 1.0.
    assert grading._extract_weight({}) == 1.0
    assert grading._extract_weight({"criterion": "x"}) == 1.0


def test_extract_weight_uses_weight_when_present():
    assert grading._extract_weight({"weight": 5}) == 5.0
    assert grading._extract_weight({"weight": -3}) == -3.0


def test_extract_weight_score_fallback_preserves_sign():
    # kensei2-style rubrics store the (signed) weight under 'score'; the SIGN
    # encodes guardrail polarity and must survive the fallback.
    assert grading._extract_weight({"score": -5}) == -5.0
    assert grading._extract_weight({"score": 3}) == 3.0


def test_extract_weight_weight_takes_precedence_over_score():
    # 'weight' wins when both present (score only consulted if weight is None).
    assert grading._extract_weight({"weight": 2, "score": -9}) == 2.0


def test_extract_weight_explicit_none_weight_falls_through_to_score():
    assert grading._extract_weight({"weight": None, "score": -4}) == -4.0


def test_extract_weight_both_none_defaults_to_one():
    assert grading._extract_weight({"weight": None, "score": None}) == 1.0


def test_extract_weight_numeric_string_is_coerced():
    # "3" -> float 3.0 (str.format handles the display; float() the value).
    assert grading._extract_weight({"weight": "3"}) == 3.0
    assert grading._extract_weight({"score": "-2"}) == -2.0


def test_extract_weight_non_numeric_string_defaults_to_one():
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # A non-numeric weight silently collapses to positive 1.0 rather than
    # raising, so a malformed rubric weight is invisibly treated as a normal
    # positive criterion.
    assert grading._extract_weight({"weight": "abc"}) == 1.0
    assert grading._extract_weight({"weight": []}) == 1.0
    assert grading._extract_weight({"weight": {}}) == 1.0


def test_extract_weight_nan_string_returns_nan_not_default():
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # float("nan") SUCCEEDS, so "nan" is NOT caught by the except and flows
    # through as an actual NaN weight (it is NOT flattened to 1.0). Downstream
    # reward math then propagates the NaN (see the grade_council NaN test).
    w = grading._extract_weight({"weight": "nan"})
    assert math.isnan(w)
    w2 = grading._extract_weight({"weight": float("nan")})
    assert math.isnan(w2)


# ---------------------------------------------------------------------------
# _parse_verdict_text — against the real _VERDICT_RE
# ---------------------------------------------------------------------------


def test_parse_verdict_valid_two_criteria():
    resp = (
        "<judgment>\n"
        "1. Did the thing. [[RATIONALE: yes it did it]] "
        "[[SATISFIED: Yes]] [[TRUNCATION_AFFECTED: No]]\n"
        "2. Did other thing. [[RATIONALE: no it did not]] [[SATISFIED: No]]\n"
        "</judgment>"
    )
    v = grading._parse_verdict_text(resp, 2)
    assert len(v) == 2
    assert v[0] == {
        "rationale": "yes it did it",
        "satisfied": True,
        "truncation_affected": False,
    }
    # Second verdict omits TRUNCATION_AFFECTED -> defaults False (optional group).
    assert v[1]["satisfied"] is False
    assert v[1]["truncation_affected"] is False


def test_parse_verdict_case_and_multiline_rationale():
    # DOTALL + IGNORECASE: rationale spans newlines; lowercase 'yes' accepted.
    resp = (
        "1. crit. [[rationale: line one\nline two]] [[satisfied: yes]] "
        "[[truncation_affected: yes]]"
    )
    v = grading._parse_verdict_text(resp, 1)
    assert len(v) == 1
    assert "line one" in v[0]["rationale"] and "line two" in v[0]["rationale"]
    assert v[0]["satisfied"] is True
    assert v[0]["truncation_affected"] is True


def test_parse_verdict_truncated_returns_partial_list():
    # Smaller-context judge truncates: only 1 verdict emitted for a 3-item
    # rubric. Partial list is returned (NOT padded, NOT raised) so the council
    # aggregator can vote per-covered-index.
    resp = "1. only one. [[RATIONALE: ok]] [[SATISFIED: Yes]] [[TRUNCATION_AFFECTED: Yes]]"
    v = grading._parse_verdict_text(resp, 3)
    assert len(v) == 1
    assert v[0]["truncation_affected"] is True


def test_parse_verdict_extra_verdicts_capped_at_n_criteria():
    # A judge emits stray numbered items beyond the rubric -> capped at n.
    resp = "\n".join(
        f"{i}. c{i}. [[RATIONALE: r]] [[SATISFIED: Yes]]" for i in range(1, 6)
    )
    v = grading._parse_verdict_text(resp, 2)
    assert len(v) == 2


def test_parse_verdict_garbage_raises_valueerror():
    with pytest.raises(ValueError, match="no verdicts parsed"):
        grading._parse_verdict_text("totally unrelated prose, no verdicts here", 3)


def test_parse_verdict_missing_number_anchor_raises():
    # The leading 'N.' anchor is required; without it _VERDICT_RE misses.
    resp = "crit text [[RATIONALE: r]] [[SATISFIED: Yes]]"
    with pytest.raises(ValueError, match="no verdicts parsed"):
        grading._parse_verdict_text(resp, 1)


def test_parse_verdict_empty_response_raises():
    with pytest.raises(ValueError, match="empty judge response"):
        grading._parse_verdict_text("", 2)
    with pytest.raises(ValueError, match="empty judge response"):
        grading._parse_verdict_text(None, 2)  # falsy -> same guard


def test_parse_verdict_satisfied_no_and_absent_truncation_defaults():
    resp = "1. c. [[RATIONALE: reasoning]] [[SATISFIED: No]]"
    v = grading._parse_verdict_text(resp, 1)
    assert v[0]["satisfied"] is False
    assert v[0]["truncation_affected"] is False


# ---------------------------------------------------------------------------
# _split_evidence — transcript marker partition
# ---------------------------------------------------------------------------


def test_split_evidence_with_marker():
    ev = "FILES BLOB\n----- TRANSCRIPT (condensed) -----\nTHE TRANSCRIPT"
    files_part, transcript = grading._split_evidence(ev)
    assert files_part == "FILES BLOB"
    assert transcript == "THE TRANSCRIPT"


def test_split_evidence_without_marker_returns_all_as_files():
    ev = "just files, no transcript marker present"
    files_part, transcript = grading._split_evidence(ev)
    assert files_part == ev
    assert transcript == ""


# ---------------------------------------------------------------------------
# _judge_user_prompt — real prompt file "[points: w]" rendering
# ---------------------------------------------------------------------------


def test_judge_user_prompt_renders_points_and_header():
    rubrics = [
        {"criterion": "crit A", "weight": 3},
        {"criterion": "crit B", "score": -2},   # score fallback, negative
        "a bare string criterion",              # non-dict -> weight 1.0
    ]
    evidence = "SOME FILES\n----- TRANSCRIPT (condensed) -----\nTHE TALK"
    out = grading._judge_user_prompt("accomplish the task", rubrics, evidence)

    # Rubric block: one numbered "[points: w]" line per criterion, in order.
    assert "1. crit A  [points: 3.0]" in out
    assert "2. crit B  [points: -2.0]" in out
    assert "3. a bare string criterion  [points: 1.0]" in out
    # n_criteria threaded into the RUBRIC header and closing instruction.
    assert "RUBRIC (3 criteria" in out
    assert "exactly 3 verdicts" in out
    # task_description + split transcript/files land in their slots.
    assert "accomplish the task" in out
    assert "THE TALK" in out
    assert "SOME FILES" in out


def test_judge_user_prompt_empty_evidence_uses_placeholders():
    out = grading._judge_user_prompt("t", [{"criterion": "c", "weight": 1}], "")
    assert "(no transcript captured)" in out
    assert "(no deliverable files were collected)" in out


# ---------------------------------------------------------------------------
# _collect_deliverable_files / _gather_evidence — real tmp_path trees
# ---------------------------------------------------------------------------


def _make_results_tree(tmp_path: Path) -> Path:
    """Build a workspace where results_path.name == 'results' so the sibling
    sweep (workspace_root = parent.parent) fires. Returns the results/ path.

    Layout:
      <root>/task_output/artifacts/results/report.md           (text, primary)
      <root>/task_output/artifacts/results/notes.pdf           (binary presence)
      <root>/task_output/artifacts/results/pic.png             (unsupported ext)
      <root>/task_output/workspace_full/output/flagged.csv     (named-dir sweep)
      <root>/task_output/workspace_full/top.txt                (root-level glob)
    """
    task_output = tmp_path / "task_output"
    results = task_output / "artifacts" / "results"
    results.mkdir(parents=True)
    (results / "report.md").write_text("the report body", encoding="utf-8")
    (results / "notes.pdf").write_bytes(b"%PDF-1.4 secret binary bytes")
    (results / "pic.png").write_bytes(b"\x89PNG unsupported")
    wf = task_output / "workspace_full"
    (wf / "output").mkdir(parents=True)
    (wf / "output" / "flagged.csv").write_text("a,b,c", encoding="utf-8")
    (wf / "top.txt").write_text("top level deliverable", encoding="utf-8")
    return results


def test_collect_deliverable_files_text_binary_and_sibling_sweep(tmp_path):
    results = _make_results_tree(tmp_path)
    files = grading._collect_deliverable_files(results)
    names = sorted(f.name for f in files)
    # report.md (text) + notes.pdf (binary presence) from results/,
    # flagged.csv from workspace_full/output/, top.txt from workspace_full root.
    assert names == ["flagged.csv", "notes.pdf", "report.md", "top.txt"]
    # Unsupported .png is never collected.
    assert "pic.png" not in names


def test_collect_deliverable_files_empty_dir_returns_empty(tmp_path):
    results = tmp_path / "task_output" / "results"
    results.mkdir(parents=True)
    assert grading._collect_deliverable_files(results) == []


def test_collect_deliverable_files_missing_dir_returns_empty(tmp_path):
    # Non-existent results path: _add_from short-circuits on not is_dir().
    assert grading._collect_deliverable_files(tmp_path / "nope" / "results") == []


def test_collect_skips_oversized_binary(tmp_path):
    # Binary deliverable over _ROOT_SCAN_MAX_FILE_BYTES is dropped (presence
    # scan cap), while an oversized TEXT deliverable is still collected (text
    # path has no size gate in _is_text_deliverable).
    results = tmp_path / "task_output" / "artifacts" / "results"
    results.mkdir(parents=True)
    big = b"x" * (grading._ROOT_SCAN_MAX_FILE_BYTES + 10)
    (results / "huge.pdf").write_bytes(big)
    (results / "small.md").write_text("ok", encoding="utf-8")
    names = sorted(f.name for f in grading._collect_deliverable_files(results))
    assert names == ["small.md"]


def test_gather_evidence_orders_primary_first_and_dumps_binary_body(tmp_path):
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # Ordering: a 'report' stem sorts ahead of a larger, non-primary csv.
    # Binary polarity: although _is_text_deliverable EXCLUDES pdf from the
    # verbatim path, _gather_evidence iterates over the FULL deliverable list
    # (text + binary, from _collect_deliverable_files) and read_text()s each
    # with errors='replace'. So a collected .pdf's bytes ARE dumped verbatim
    # here (as latin-ish text), contradicting the module docstring's
    # "presence-only" intent for binaries. This is the mojibake-poisoning
    # hazard the comments warn about, still live.
    results = tmp_path / "task_output" / "artifacts" / "results"
    results.mkdir(parents=True)
    (results / "zdata.csv").write_text("x,y,z," * 200, encoding="utf-8")
    (results / "report.md").write_text("PRIMARY REPORT", encoding="utf-8")
    (results / "notes.pdf").write_bytes(b"%PDF secret-body-marker")

    ev = grading._gather_evidence(results, "MY TRANSCRIPT", budget=None)
    # Primary 'report' sorts ahead of the larger, non-primary csv.
    assert ev.index("report.md") < ev.index("zdata.csv")
    # PDF IS collected AND its (ASCII-decodable) bytes are dumped verbatim.
    assert "DELIVERABLE: notes.pdf" in ev
    assert "secret-body-marker" in ev
    # Transcript appended under the condensed marker.
    assert "MY TRANSCRIPT" in ev
    assert "TRANSCRIPT (condensed)" in ev


def test_gather_evidence_budget_truncates(tmp_path):
    results = tmp_path / "task_output" / "artifacts" / "results"
    results.mkdir(parents=True)
    (results / "report.md").write_text("A" * 5000, encoding="utf-8")
    ev = grading._gather_evidence(results, "transcript", budget=50)
    assert len(ev) == 50


def test_gather_evidence_no_deliverables_placeholder(tmp_path):
    results = tmp_path / "task_output" / "results"
    results.mkdir(parents=True)
    ev = grading._gather_evidence(results, "", budget=None)
    assert "no deliverable files were collected under any of" in ev
    # Every recognised deliverable-dir name appears in the placeholder.
    for name in grading._DELIVERABLE_DIR_NAMES:
        assert f"{name}/" in ev


def test_gather_evidence_split_roundtrips_through_split_evidence(tmp_path):
    results = tmp_path / "task_output" / "artifacts" / "results"
    results.mkdir(parents=True)
    (results / "report.md").write_text("BODY", encoding="utf-8")
    ev = grading._gather_evidence(results, "THE TRANSCRIPT", budget=None)
    files_part, transcript = grading._split_evidence(ev)
    assert transcript == "THE TRANSCRIPT"
    assert "TRANSCRIPT (condensed)" not in files_part
    assert "BODY" in files_part


# ---------------------------------------------------------------------------
# _grade_council reward EDGE cases (NOT covered by test_judge_sonnet_tiebreak)
# ---------------------------------------------------------------------------

_SONNET = "bedrock/arn:aws:bedrock:us-east-1:1:application-inference-profile/sonnet-x"
_GLM = "bedrock/arn:aws:bedrock:us-east-1:1:application-inference-profile/glm-x"
_KIMI = "bedrock/arn:aws:bedrock:us-east-1:1:application-inference-profile/kimi-x"


def _members():
    return [
        grading.CouncilMember(family="sonnet", model=_SONNET),
        grading.CouncilMember(family="glm", model=_GLM),
        grading.CouncilMember(family="kimi", model=_KIMI),
    ]


def _verdicts(*sats):
    return [
        {"satisfied": s, "rationale": "r", "truncation_affected": False}
        for s in sats
    ]


def _ok(model, family, verds):
    return {
        "model": model,
        "effective_model": model,
        "family": family,
        "ok": True,
        "verdicts": verds,
        "usage": dict(grading._ZERO_USAGE),
        "user_chars": 10,
    }


def _grade(monkeypatch, rubrics, member_results):
    monkeypatch.setattr(
        grading, "_run_council",
        lambda members, system, user, n: list(member_results),
    )
    return grading._grade_council(rubrics, "sys", "user", _members())


def test_all_negative_rubric_guardrails_held_scores_zero(monkeypatch):
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # Rubric of ONLY guardrail (negative-weight) criteria. Denominator is the
    # sum of POSITIVE weights = 0 -> falls back to 1.0. When all guardrails
    # held (satisfied=No -> passed), the numerator stays 0, so overall is 0.0
    # even though the agent did everything right. criteria_passed is still 1.
    rubrics = [{"criterion": "forbidden thing", "weight": -3}]
    out = _grade(monkeypatch, rubrics, [
        _ok(_SONNET, "sonnet", _verdicts(False)),
        _ok(_GLM, "glm", _verdicts(False)),
        _ok(_KIMI, "kimi", _verdicts(False)),
    ])
    assert out["overall_score"] == 0.0
    assert out["criteria_passed"] == 1
    assert out["criteria_failed"] == 0
    assert out["criteria"][0]["passed"] is True
    assert out["criteria"][0]["is_positive"] is False


def test_all_negative_rubric_guardrail_breached_scores_zero(monkeypatch):
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # Same all-negative rubric but forbidden behavior OCCURRED (satisfied=Yes
    # unanimously). Numerator subtracts |weight| -> -3; the formula is
    # deliberately UNCLAMPED (negative-weight violation checkers must pull the
    # reward below zero), so overall is -3/1.0 = -3.0.
    rubrics = [{"criterion": "forbidden thing", "weight": -3}]
    out = _grade(monkeypatch, rubrics, [
        _ok(_SONNET, "sonnet", _verdicts(True)),
        _ok(_GLM, "glm", _verdicts(True)),
        _ok(_KIMI, "kimi", _verdicts(True)),
    ])
    assert out["overall_score"] == -3.0
    assert out["criteria"][0]["passed"] is False


def test_mixed_dict_and_string_rubric_inflates_numerator(monkeypatch):
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # A bare-string rubric entry is treated as a positive weight-1.0 criterion
    # in the NUMERATOR (its satisfied verdict adds +1.0 to `weighted`) but a
    # string is NOT a dict, so it is EXCLUDED from `total_w` (denominator only
    # sums dict positive weights). Numerator 2+1=3 over denominator 2 = 1.5
    # (no clamp). The string entry silently inflates the score.
    rubrics = [{"criterion": "c0", "weight": 2}, "just a string criterion"]
    out = _grade(monkeypatch, rubrics, [
        _ok(_SONNET, "sonnet", _verdicts(True, True)),
        _ok(_GLM, "glm", _verdicts(True, True)),
        _ok(_KIMI, "kimi", _verdicts(True, True)),
    ])
    # Denominator 2; numerator 3 -> unclamped 1.5.
    assert out["overall_score"] == 1.5
    # String criterion rendered as positive weight 1.0.
    assert out["criteria"][1]["weight"] == 1.0
    assert out["criteria"][1]["is_positive"] is True
    assert out["criteria_passed"] == 2


def test_nan_weight_propagates_to_overall_one(monkeypatch):
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # A NaN weight (e.g. rubric weight literally "nan") is excluded from total_w
    # because `nan > 0` is False, so total_w falls back to 1.0. `weighted`
    # becomes NaN (0 + nan) and the unclamped nan/1.0 stays NaN — the poison
    # value now PROPAGATES (previously the clamp silently converted it to a
    # perfect 1.0).
    rubrics = [{"criterion": "c", "weight": "nan"}]
    out = _grade(monkeypatch, rubrics, [
        _ok(_SONNET, "sonnet", _verdicts(True)),
        _ok(_GLM, "glm", _verdicts(True)),
        _ok(_KIMI, "kimi", _verdicts(True)),
    ])
    assert math.isnan(out["overall_score"])
    assert math.isnan(out["criteria"][0]["weight"])


def test_grade_council_empty_rubrics_via_grade_with_rubric():
    # grade_with_rubric short-circuits on empty rubrics without touching the
    # council (no members, no pricing) — the fast structured-error path.
    out = grading.grade_with_rubric([], "task", Path("/nonexistent"))
    assert out == {"overall_score": 0.0, "error": "no rubric criteria"}


def test_grade_council_zero_survivors_all_abstain(monkeypatch):
    # Every member failed the call -> zero survivors, no Sonnet verdict, every
    # criterion abstains, overall 0.0. Confirms the total-council-failure path.
    failed = {
        "model": _SONNET, "effective_model": _SONNET, "family": "sonnet",
        "ok": False, "error": "call: boom",
        "usage": dict(grading._ZERO_USAGE), "user_chars": 10,
    }
    rubrics = [{"criterion": "c", "weight": 5}]
    monkeypatch.setattr(
        grading, "_run_council", lambda *a, **k: [dict(failed)],
    )
    out = grading._grade_council(
        rubrics, "sys", "user",
        [grading.CouncilMember(family="sonnet", model=_SONNET)],
    )
    assert out["overall_score"] == 0.0
    assert out["criteria_abstained"] == 1
    assert out["abstention_flags"] == [0]
    assert out["criteria"][0]["resolved_by"] == "human_eval"


# ---------------------------------------------------------------------------
# deliverable predicates (direct)
# ---------------------------------------------------------------------------


def test_deliverable_predicates_direct():
    assert grading._is_text_deliverable(Path("report.md")) is True
    assert grading._is_text_deliverable(Path("data.CSV")) is True   # case-insensitive
    assert grading._is_text_deliverable(Path("report.pdf")) is False
    assert grading._is_binary_deliverable(Path("report.pdf")) is True
    assert grading._is_binary_deliverable(Path("report.md")) is False


def test_looks_like_deliverable_wrong_ext_and_oversize(tmp_path):
    good = tmp_path / "a.md"
    good.write_text("hi", encoding="utf-8")
    assert grading._looks_like_deliverable(good, tmp_path) is True
    # Unsupported extension -> False regardless of size.
    bad = tmp_path / "a.png"
    bad.write_bytes(b"\x89PNG")
    assert grading._looks_like_deliverable(bad, tmp_path) is False
    # Supported extension but oversized -> False (size gate).
    big = tmp_path / "b.csv"
    big.write_bytes(b"z" * (grading._ROOT_SCAN_MAX_FILE_BYTES + 1))
    assert grading._looks_like_deliverable(big, tmp_path) is False


def test_gather_evidence_skips_unreadable_file(tmp_path, monkeypatch):
    # A deliverable whose read_text raises is silently skipped (the surrounding
    # try/except in _gather_evidence), not fatal — the readable one survives.
    results = tmp_path / "task_output" / "artifacts" / "results"
    results.mkdir(parents=True)
    (results / "report.md").write_text("GOOD BODY", encoding="utf-8")
    (results / "broken.md").write_text("bad", encoding="utf-8")

    real_read_text = Path.read_text

    def _boom(self, *a, **k):
        if self.name == "broken.md":
            raise OSError("simulated read failure")
        return real_read_text(self, *a, **k)

    monkeypatch.setattr(Path, "read_text", _boom)
    ev = grading._gather_evidence(results, "", budget=None)
    assert "GOOD BODY" in ev
    assert "broken.md" not in ev


# ---------------------------------------------------------------------------
# _grade_council — truncation flags + short-verdict partial abstain
# ---------------------------------------------------------------------------


def test_grade_council_truncation_flag_recorded(monkeypatch):
    # A member reporting truncation_affected=True on a criterion registers that
    # index in truncation_flags (independent of the verdict resolution).
    rubrics = [{"criterion": "c0", "weight": 1}]
    trunc_verd = [{"satisfied": True, "rationale": "r", "truncation_affected": True}]
    out = _grade(monkeypatch, rubrics, [
        _ok(_SONNET, "sonnet", trunc_verd),
        _ok(_GLM, "glm", _verdicts(True)),
        _ok(_KIMI, "kimi", _verdicts(True)),
    ])
    assert out["truncation_flags"] == [0]
    # Verdict still resolves unanimous (truncation flag is orthogonal).
    assert out["criteria"][0]["resolved_by"] == "unanimous"


def test_grade_council_short_verdict_list_abstains_that_index(monkeypatch):
    # Kimi returns only 1 verdict for a 2-criterion rubric: index 1 is beyond
    # its list -> that member shows "Abstain" with the truncated-before-index
    # rationale, and the criterion resolves via Sonnet (not unanimous).
    rubrics = [{"criterion": "c0", "weight": 1}, {"criterion": "c1", "weight": 1}]
    short = [{"satisfied": True, "rationale": "r", "truncation_affected": False}]
    out = _grade(monkeypatch, rubrics, [
        _ok(_SONNET, "sonnet", _verdicts(True, True)),
        _ok(_GLM, "glm", _verdicts(True, True)),
        _ok(_KIMI, "kimi", short),
    ])
    c1 = out["criteria"][1]
    assert c1["votes"] == "Yes/Yes/Abstain"
    assert c1["resolved_by"] == "sonnet"
    assert c1["voted_by_judge"] == [True, True, False]
    assert "truncated before this criterion" in c1["rationales_by_judge"][2]


# ---------------------------------------------------------------------------
# format_scores
# ---------------------------------------------------------------------------


def test_format_scores_pure_error_returns_error_line():
    s = grading.format_scores("t1", {"error": "no rubric criteria"})
    assert s == "[t1] Grading error: no rubric criteria"


def test_format_scores_numeric_renders_bars():
    s = grading.format_scores("t1", {"overall_score": 0.5, "criteria_passed": 3})
    assert "t1" in s
    assert "0.50" in s
    assert "overall_score" in s
    assert "█" in s  # progress bar rendered for numeric values


# ---------------------------------------------------------------------------
# print_summary — rollup math + JSON side file (capsys / tmp_path)
# ---------------------------------------------------------------------------


def test_print_summary_rollup_and_json(tmp_path):
    results = [
        {
            "task_id": "t1",
            "scores": {"overall_score": 0.8, "criteria_passed": 4, "criteria_total": 5},
            "usage": {"output_tokens": 100, "cost_usd": 0.5},
        },
        {  # empty scores + outer agent error -> "No valid numeric scores" branch
            "task_id": "t2",
            "scores": {},
            "error": "agent boom",
            "usage": {"output_tokens": 0, "cost_usd": 0.0},
        },
        {  # scores dict has only an 'error' key -> "Grading error" branch
            "task_id": "t3",
            "scores": {"error": "grading boom"},
            "usage": {},
        },
    ]
    buf = io.StringIO()
    with redirect_stdout(buf):
        grading.print_summary(results, "catX", tmp_path, "modelZ")
    out = buf.getvalue()

    assert "Summary Report — catX" in out
    assert "t1: avg" in out           # numeric task summarized
    assert "Grading error grading boom" in out   # t3 error branch
    assert "0.80" in out              # t1 overall_score bar line
    # Token/cost table totals: only t1 contributes 100 tokens / $0.5.
    assert "100" in out
    # Side-car summary JSON written under <output_dir>/<category>/.
    summary_path = tmp_path / "catX" / "summary_modelZ.json"
    assert summary_path.exists()
    data = json.loads(summary_path.read_text())
    assert len(data) == 3


def test_print_summary_agent_error_note_when_numeric_present(tmp_path):
    # A task WITH numeric scores AND an outer agent error prints the "!" status
    # plus an ` agent_error=` note (distinct from the empty-scores path).
    results = [{
        "task_id": "ta",
        "scores": {"overall_score": 0.5},
        "error": "partial fail",
        "usage": {"output_tokens": 10, "cost_usd": 0.1},
    }]
    buf = io.StringIO()
    with redirect_stdout(buf):
        grading.print_summary(results, "c", tmp_path, "m")
    assert "agent_error=partial fail" in buf.getvalue()


def test_print_summary_grading_error_note_when_numeric_present(tmp_path):
    # numeric score present AND scores.error present -> ` grading_error=` note.
    results = [{
        "task_id": "tb",
        "scores": {"overall_score": 0.5, "error": "grade partial"},
        "usage": {},
    }]
    buf = io.StringIO()
    with redirect_stdout(buf):
        grading.print_summary(results, "c", tmp_path, "m")
    assert "grading_error=grade partial" in buf.getvalue()


def test_print_summary_no_scores_note(tmp_path):
    # scores falsy AND no outer error -> "No scores" line, no crash.
    results = [{"task_id": "tc", "scores": None, "usage": {}}]
    buf = io.StringIO()
    with redirect_stdout(buf):
        grading.print_summary(results, "c", tmp_path, "m")
    assert "No scores" in buf.getvalue()


# ---------------------------------------------------------------------------
# print_global_summary — global average math + JSON side file
# ---------------------------------------------------------------------------


def test_print_global_summary_average_divides_by_total_tasks(tmp_path):
    # global_avg = sum(overall_score of scored) / TOTAL tasks (missing count in
    # the denominator). One scored task at 0.8 over 3 total -> 0.266667.
    results = [
        {"task_id": "t1", "scores": {"overall_score": 0.8}, "usage": {"output_tokens": 100, "cost_usd": 0.5}},
        {"task_id": "t2", "scores": {}, "usage": {"output_tokens": 0, "cost_usd": 0.0}},
        {"task_id": "t3", "scores": {"error": "boom"}, "usage": {}},
    ]
    buf = io.StringIO()
    with redirect_stdout(buf):
        grading.print_global_summary(results, tmp_path, "modelZ")
    out = buf.getvalue()
    assert "Global Summary Report" in out
    assert "Completed tasks: 1 / 3" in out
    assert "Tasks without a valid score.json: 2" in out

    gp = tmp_path / "summary_all_modelZ.json"
    gd = json.loads(gp.read_text())
    assert gd["scored_task_count"] == 1
    assert gd["missing_score_task_count"] == 2
    assert gd["task_count"] == 3
    assert gd["global_avg"] == pytest.approx(0.8 / 3)


def test_print_global_summary_avg_of_numeric_when_no_overall_score(tmp_path):
    # When a task's scores have no 'overall_score', the fallback is the mean of
    # its numeric values. {a:0.4,b:0.6} -> 0.5, single task -> global 0.5.
    results = [
        {"task_id": "t1", "scores": {"a": 0.4, "b": 0.6}, "usage": {}},
    ]
    buf = io.StringIO()
    with redirect_stdout(buf):
        grading.print_global_summary(results, tmp_path, "m")
    gd = json.loads((tmp_path / "summary_all_m.json").read_text())
    assert gd["global_avg"] == pytest.approx(0.5)


def test_print_global_summary_empty_results_no_tasks(tmp_path):
    buf = io.StringIO()
    with redirect_stdout(buf):
        grading.print_global_summary([], tmp_path, "m")
    out = buf.getvalue()
    assert "No tasks found" in out
    gd = json.loads((tmp_path / "summary_all_m.json").read_text())
    assert gd["global_avg"] is None
    assert gd["task_count"] == 0
