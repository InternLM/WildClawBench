"""Unit tests for pure helpers in eval/run_batch.py.

Focus (per SCORING_AUDIT_REPORT.md task brief):
  * _augment_score_with_combined_rewards — the (test+rubric)/2 blend, including
    negative-passthrough, single-channel fallbacks, None-when-neither, and the
    math.isfinite / isinstance-bool guards.
  * _pass_summary_entry / _pass_summary_doc — per_run rollup math.
  * assorted small pure helpers (_finite_float, _mean_or_none, _model_type,
    _merge_usage_source, recompute_combined, _augment_task_with_mocks,
    _project_agent_usage_top_level, _project_artifact_record,
    _condense_transcript_for_judge, _normalize_display_model,
    _compute_testgen_cache_key).

All tests are OFFLINE and deterministic: no docker, no network, no boto3, no
sleeps. Temp files only under pytest tmp_path.

Import-bootstrap style matches tests/test_score_json_last_resort.py (sys.path
insert of repo root before `from eval...` / `from ...` imports).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.run_batch import (  # noqa: E402
    _augment_score_with_combined_rewards,
    _augment_task_with_mocks,
    _compute_testgen_cache_key,
    _condense_transcript_for_judge,
    _finite_float,
    _mean_or_none,
    _merge_usage_source,
    _model_type,
    _normalize_display_model,
    _pass_summary_doc,
    _pass_summary_entry,
    _project_agent_usage_top_level,
    _project_artifact_record,
    _resolve_task_apis,
    _write_pass_summary,
    recompute_combined,
)


# ---------------------------------------------------------------------------
# _augment_score_with_combined_rewards — the (test_reward + rubric_reward) / 2
# blend. This is the core scoring surface flagged in the task brief.
#
# Signature: _augment_score_with_combined_rewards(scores: dict, result: dict)
#   test_reward  ← result["test_result"]["reward"], gated on tests_total truthy
#   rubric_reward ← scores["overall_score"]
#   writes scores["test_based_reward"], ["rubric_based_reward"], ["combined_reward"]
# ---------------------------------------------------------------------------


def _augment(overall_score, test_reward=None, tests_total=None):
    """Helper: build (scores, result) and run the augmenter, return scores."""
    scores: dict = {}
    if overall_score is not None:
        scores["overall_score"] = overall_score
    te: dict = {}
    if test_reward is not None:
        te["reward"] = test_reward
    if tests_total is not None:
        te["tests_total"] = tests_total
    result = {"test_result": te}
    _augment_score_with_combined_rewards(scores, result)
    return scores


class TestAugmentCombinedRewards:
    def test_both_channels_present_averages(self):
        # test=0.8, rubric=0.6 -> combined = 0.7
        s = _augment(overall_score=0.6, test_reward=0.8, tests_total=4)
        assert s["test_based_reward"] == 0.8
        assert s["rubric_based_reward"] == 0.6
        assert s["combined_reward"] == pytest.approx(0.7)

    def test_negative_test_reward_passthrough_into_blend(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # A negative test reward (guardrail-triggered) flows straight into the
        # blend un-clamped: (-7.0 + 0.2) / 2 = -3.4.
        s = _augment(overall_score=0.2, test_reward=-7.0, tests_total=3)
        assert s["test_based_reward"] == -7.0
        assert s["rubric_based_reward"] == 0.2
        assert s["combined_reward"] == pytest.approx(-3.4)

    def test_only_test_channel(self):
        s = _augment(overall_score=None, test_reward=0.5, tests_total=2)
        assert s["test_based_reward"] == 0.5
        assert s["rubric_based_reward"] is None
        assert s["combined_reward"] == 0.5

    def test_only_rubric_channel(self):
        s = _augment(overall_score=0.9, test_reward=None, tests_total=None)
        assert s["test_based_reward"] is None
        assert s["rubric_based_reward"] == 0.9
        assert s["combined_reward"] == 0.9

    def test_neither_channel_yields_none_combined(self):
        s = _augment(overall_score=None, test_reward=None, tests_total=None)
        assert s["test_based_reward"] is None
        assert s["rubric_based_reward"] is None
        assert s["combined_reward"] is None

    def test_tests_total_zero_disables_test_channel(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # test reward is ONLY honored when tests_total is truthy; a reward with
        # tests_total=0 is ignored (falsy guard), so only rubric survives.
        s = _augment(overall_score=0.4, test_reward=0.99, tests_total=0)
        assert s["test_based_reward"] is None
        assert s["rubric_based_reward"] == 0.4
        assert s["combined_reward"] == 0.4

    def test_tests_total_missing_disables_test_channel(self):
        # tests_total absent entirely -> te.get returns None (falsy) -> ignored.
        s = _augment(overall_score=0.4, test_reward=0.99, tests_total=None)
        assert s["test_based_reward"] is None
        assert s["combined_reward"] == 0.4

    def test_nan_test_reward_rejected(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # math.isfinite guard rejects NaN in the test channel.
        s = _augment(overall_score=0.5, test_reward=float("nan"), tests_total=3)
        assert s["test_based_reward"] is None
        assert s["combined_reward"] == 0.5

    def test_inf_test_reward_rejected(self):
        s = _augment(overall_score=0.5, test_reward=float("inf"), tests_total=3)
        assert s["test_based_reward"] is None
        assert s["combined_reward"] == 0.5

    def test_nan_rubric_rejected(self):
        s = _augment(overall_score=float("nan"), test_reward=0.5, tests_total=3)
        assert s["rubric_based_reward"] is None
        assert s["combined_reward"] == 0.5

    def test_inf_rubric_rejected(self):
        s = _augment(overall_score=float("-inf"), test_reward=0.5, tests_total=3)
        assert s["rubric_based_reward"] is None
        assert s["combined_reward"] == 0.5

    def test_bool_test_reward_rejected(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # isinstance(x, bool) check: True is an int subclass but must NOT be
        # treated as a numeric reward.
        s = _augment(overall_score=0.5, test_reward=True, tests_total=3)
        assert s["test_based_reward"] is None
        assert s["combined_reward"] == 0.5

    def test_bool_rubric_reward_rejected(self):
        s = _augment(overall_score=True, test_reward=0.5, tests_total=3)
        assert s["rubric_based_reward"] is None
        assert s["combined_reward"] == 0.5

    def test_int_rewards_are_accepted_as_float(self):
        # int rewards are valid numerics and get floated.
        s = _augment(overall_score=1, test_reward=0, tests_total=2)
        assert s["test_based_reward"] == 0.0
        assert isinstance(s["test_based_reward"], float)
        assert s["rubric_based_reward"] == 1.0
        assert s["combined_reward"] == pytest.approx(0.5)

    def test_non_dict_scores_is_noop(self):
        # Guard clause: non-dict scores returns immediately without raising.
        obj = ["not", "a", "dict"]
        _augment_score_with_combined_rewards(obj, {"test_result": {}})  # no raise
        assert obj == ["not", "a", "dict"]

    def test_none_result_treated_as_empty(self):
        # (result or {}) guard: None result must not raise.
        scores = {"overall_score": 0.3}
        _augment_score_with_combined_rewards(scores, None)
        assert scores["rubric_based_reward"] == 0.3
        assert scores["test_based_reward"] is None
        assert scores["combined_reward"] == 0.3

    def test_test_result_not_a_dict_is_ignored(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # te is coerced to {} when result["test_result"] is falsy, and when it
        # is a non-dict truthy value the isinstance(te, dict) guard skips it.
        scores = {"overall_score": 0.3}
        _augment_score_with_combined_rewards(scores, {"test_result": ["x"]})
        assert scores["test_based_reward"] is None
        assert scores["combined_reward"] == 0.3

    def test_negative_both_channels_average(self):
        # Two negatives average to a negative (fully un-clamped).
        s = _augment(overall_score=-0.4, test_reward=-0.6, tests_total=2)
        assert s["combined_reward"] == pytest.approx(-0.5)


# ---------------------------------------------------------------------------
# _finite_float
# ---------------------------------------------------------------------------


class TestFiniteFloat:
    def test_accepts_int(self):
        assert _finite_float(3) == 3.0

    def test_accepts_float(self):
        assert _finite_float(2.5) == 2.5

    def test_accepts_negative(self):
        assert _finite_float(-1.25) == -1.25

    def test_rejects_bool_true(self):
        assert _finite_float(True) is None

    def test_rejects_bool_false(self):
        assert _finite_float(False) is None

    def test_rejects_nan(self):
        assert _finite_float(float("nan")) is None

    def test_rejects_inf(self):
        assert _finite_float(float("inf")) is None

    def test_rejects_string(self):
        assert _finite_float("1.0") is None

    def test_rejects_none(self):
        assert _finite_float(None) is None


# ---------------------------------------------------------------------------
# _mean_or_none
# ---------------------------------------------------------------------------


class TestMeanOrNone:
    def test_simple_mean(self):
        assert _mean_or_none([1.0, 2.0, 3.0]) == 2.0

    def test_drops_none(self):
        assert _mean_or_none([2.0, None, 4.0]) == 3.0

    def test_all_none_returns_none(self):
        assert _mean_or_none([None, None]) is None

    def test_empty_returns_none(self):
        assert _mean_or_none([]) is None

    def test_single_value(self):
        assert _mean_or_none([0.7]) == 0.7

    def test_negatives_included(self):
        assert _mean_or_none([-1.0, 1.0]) == 0.0


# ---------------------------------------------------------------------------
# _model_type — model id -> kensei pod folder name
# ---------------------------------------------------------------------------


class TestModelType:
    def test_claude_family(self):
        assert _model_type("anthropic/claude-opus-4.7") == "claude"

    def test_claude_bare(self):
        assert _model_type("claude-sonnet-4.6") == "claude"

    def test_gpt_family(self):
        assert _model_type("openai/gpt-5.5") == "gpt"

    def test_o1_family(self):
        assert _model_type("o1-preview") == "gpt"

    def test_o3_family(self):
        assert _model_type("o3") == "gpt"

    def test_o4_family(self):
        assert _model_type("o4-mini") == "gpt"

    def test_other_model_sanitized(self):
        # Non-claude/gpt models get lowercased + non-[a-z0-9.\-_] replaced by _.
        assert _model_type("Kimi/K2 Thinking!") == "k2_thinking_"

    def test_sanitize_preserves_allowed_chars(self):
        assert _model_type("some/glm-4.6_v2") == "glm-4.6_v2"

    def test_uppercase_gpt_normalized(self):
        assert _model_type("OpenAI/GPT-4o") == "gpt"


# ---------------------------------------------------------------------------
# _pass_summary_entry — per_run record with BOTH scoring channels
# ---------------------------------------------------------------------------


class TestPassSummaryEntry:
    def test_rubric_only_run(self):
        scores = {
            "overall_score": 0.4,
            "criteria_total": 5,
            "criteria_passed": 2,
            "criteria_failed": 3,
        }
        entry = _pass_summary_entry(run_index=0, scores=scores, test_result=None)
        assert entry["run_index"] == 0
        assert entry["criteria_total"] == 5
        assert entry["criteria_passed"] == 2
        assert entry["criteria_failed"] == 3
        assert entry["rubric_reward"] == 0.4
        # rubric_pct derived from reward * 100 when absent
        assert entry["rubric_weights_percentage"] == 40.0
        # no tests -> combined falls back to rubric; reward = combined
        assert entry["tests_total"] == 0
        assert entry["test_reward"] is None
        assert entry["combined_reward"] == 0.4
        assert entry["reward"] == 0.4
        assert "__last_resort_stub__" not in entry

    def test_legacy_tests_keys_fall_back_for_criteria(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # criteria_* falls back to legacy tests_* keys inside `scores`.
        scores = {"overall_score": 0.5, "tests_total": 7, "tests_passed": 4, "tests_failed": 3}
        entry = _pass_summary_entry(run_index=1, scores=scores, test_result=None)
        assert entry["criteria_total"] == 7
        assert entry["criteria_passed"] == 4
        assert entry["criteria_failed"] == 3

    def test_both_channels_combined_averaged(self):
        scores = {
            "overall_score": 0.6,
            "criteria_total": 3,
            "test_based_reward": 0.8,
            "rubric_based_reward": 0.6,
        }
        test_result = {"tests_total": 4, "tests_passed": 3, "tests_failed": 1, "reward": 0.8}
        entry = _pass_summary_entry(run_index=2, scores=scores, test_result=test_result)
        assert entry["tests_total"] == 4
        assert entry["tests_passed"] == 3
        assert entry["tests_failed"] == 1
        assert entry["test_reward"] == 0.8
        assert entry["rubric_reward"] == 0.6
        # combined_reward absent from scores -> recomputed here as (0.8+0.6)/2
        assert entry["combined_reward"] == pytest.approx(0.7)
        assert entry["reward"] == pytest.approx(0.7)

    def test_uses_precomputed_combined_when_present(self):
        scores = {
            "overall_score": 0.6,
            "test_based_reward": 0.8,
            "rubric_based_reward": 0.6,
            "combined_reward": 0.123,  # deliberately inconsistent to prove passthrough
        }
        test_result = {"tests_total": 2, "reward": 0.8}
        entry = _pass_summary_entry(run_index=0, scores=scores, test_result=test_result)
        assert entry["combined_reward"] == 0.123
        assert entry["reward"] == 0.123

    def test_test_reward_from_ctrf_when_scores_lack_it(self):
        # test_based_reward absent from scores but tests ran -> pulled from ctrf.
        scores = {"overall_score": 0.2}
        test_result = {"tests_total": 3, "reward": 0.9}
        entry = _pass_summary_entry(run_index=0, scores=scores, test_result=test_result)
        assert entry["test_reward"] == 0.9
        assert entry["combined_reward"] == pytest.approx((0.9 + 0.2) / 2)

    def test_no_scores_no_tests_zero_reward(self):
        entry = _pass_summary_entry(run_index=0, scores=None, test_result=None)
        assert entry["criteria_total"] == 0
        assert entry["rubric_reward"] is None
        assert entry["combined_reward"] is None
        # authoritative reward: combined None, rubric None -> `rubric_reward or 0.0`
        assert entry["reward"] == 0.0

    def test_last_resort_stub_marker_propagates(self):
        scores = {"overall_score": None, "__last_resort_stub__": True}
        entry = _pass_summary_entry(run_index=0, scores=scores, test_result=None)
        assert entry["__last_resort_stub__"] is True

    def test_explicit_rubric_pct_preferred_over_derived(self):
        scores = {"overall_score": 0.5, "rubric_weights_percentage": 55.0}
        entry = _pass_summary_entry(run_index=0, scores=scores, test_result=None)
        assert entry["rubric_weights_percentage"] == 55.0

    def test_tests_errored_and_skipped_carried(self):
        scores = {"overall_score": 0.1}
        test_result = {
            "tests_total": 5, "tests_passed": 2, "tests_failed": 1,
            "tests_errored": 1, "tests_skipped": 1, "reward": 0.4,
        }
        entry = _pass_summary_entry(run_index=0, scores=scores, test_result=test_result)
        assert entry["tests_errored"] == 1
        assert entry["tests_skipped"] == 1


# ---------------------------------------------------------------------------
# _pass_summary_doc — cross-run rollup
# ---------------------------------------------------------------------------


class TestPassSummaryDoc:
    def _entry(self, idx, reward, combined, rubric, test, pct):
        return {
            "run_index": idx,
            "reward": reward,
            "combined_reward": combined,
            "rubric_reward": rubric,
            "test_reward": test,
            "rubric_weights_percentage": pct,
        }

    def test_averages_and_sorts(self):
        per_run = [
            self._entry(1, 0.6, 0.6, 0.6, None, 60.0),
            self._entry(0, 0.4, 0.4, 0.4, None, 40.0),
        ]
        doc = _pass_summary_doc("claude", per_run)
        assert doc["model"] == "claude"
        assert doc["runs"] == 2
        assert doc["average_reward"] == pytest.approx(0.5)
        assert doc["average_rubric_reward"] == pytest.approx(0.5)
        assert doc["average_rubric_weights_percentage"] == 50.0
        # sorted ascending by run_index
        assert [r["run_index"] for r in doc["per_run"]] == [0, 1]

    def test_none_test_rewards_excluded_from_test_mean(self):
        per_run = [
            self._entry(0, 0.4, 0.4, 0.4, None, 40.0),
            self._entry(1, 0.8, 0.8, 0.8, 0.8, 80.0),
        ]
        doc = _pass_summary_doc("gpt", per_run)
        # only run 1 has a test_reward -> mean over the single non-None value
        assert doc["average_test_reward"] == 0.8

    def test_empty_per_run_zeroes(self):
        doc = _pass_summary_doc("claude", [])
        assert doc["runs"] == 0
        assert doc["average_reward"] == 0.0
        assert doc["average_combined_reward"] is None
        assert doc["average_rubric_weights_percentage"] is None


# ---------------------------------------------------------------------------
# _merge_usage_source / recompute_combined
# ---------------------------------------------------------------------------


class TestUsageMerge:
    def test_merge_adds_numeric_keys(self):
        dst: dict = {}
        _merge_usage_source(dst, {"input_tokens": 10, "output_tokens": 5, "cost_usd": 0.01})
        assert dst["input_tokens"] == 10
        assert dst["output_tokens"] == 5
        assert dst["cost_usd"] == 0.01

    def test_merge_accumulates(self):
        dst = {"input_tokens": 3, "cost_usd": 0.5}
        _merge_usage_source(dst, {"input_tokens": 7, "cost_usd": 0.25})
        assert dst["input_tokens"] == 10
        assert dst["cost_usd"] == 0.75

    def test_merge_empty_src_noop(self):
        dst = {"input_tokens": 4}
        _merge_usage_source(dst, {})
        assert dst == {"input_tokens": 4}

    def test_merge_none_values_treated_as_zero(self):
        dst: dict = {}
        _merge_usage_source(dst, {"input_tokens": None, "output_tokens": 2})
        assert dst["input_tokens"] == 0
        assert dst["output_tokens"] == 2

    def test_recompute_combined_enforces_total_invariant(self):
        # total_tokens is overwritten to input+output+cache_read+cache_write,
        # even if a source lied about it.
        sources = {
            "agent": {
                "input_tokens": 100, "output_tokens": 50,
                "cache_read_tokens": 10, "cache_write_tokens": 5,
                "total_tokens": 999999,  # bogus
                "request_count": 3, "cost_usd": 0.02,
            }
        }
        combined = recompute_combined(sources, task_id="t")
        assert combined["total_tokens"] == 100 + 50 + 10 + 5
        assert combined["input_tokens"] == 100
        assert combined["request_count"] == 3
        assert combined["cost_usd"] == pytest.approx(0.02)

    def test_recompute_combined_sums_multiple_sources(self):
        sources = {
            "agent": {"input_tokens": 10, "output_tokens": 4, "total_tokens": 14,
                      "cache_read_tokens": 0, "cache_write_tokens": 0,
                      "request_count": 1, "cost_usd": 0.01},
            "judge": {"input_tokens": 20, "output_tokens": 6, "total_tokens": 26,
                      "cache_read_tokens": 0, "cache_write_tokens": 0,
                      "request_count": 2, "cost_usd": 0.03},
        }
        combined = recompute_combined(sources, task_id="t")
        assert combined["input_tokens"] == 30
        assert combined["output_tokens"] == 10
        assert combined["request_count"] == 3
        assert combined["total_tokens"] == 40
        assert combined["cost_usd"] == pytest.approx(0.04)

    def test_recompute_combined_empty_sources(self):
        combined = recompute_combined({}, task_id="t")
        assert combined["total_tokens"] == 0
        assert combined["cost_usd"] == 0.0


# ---------------------------------------------------------------------------
# _project_agent_usage_top_level
# ---------------------------------------------------------------------------


class TestProjectAgentUsage:
    def test_none_usage_returns_zeroed_shape(self):
        out = _project_agent_usage_top_level(None)
        assert out == {
            "input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0,
            "cache_read_tokens": 0, "cache_write_tokens": 0, "cost_usd": 0.0,
        }

    def test_empty_dict_returns_zeroed_shape(self):
        out = _project_agent_usage_top_level({})
        assert out["input_tokens"] == 0
        assert out["cost_usd"] == 0.0

    def test_maps_cache_read_to_cached_input(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # cached_input_tokens is aliased from cache_read_tokens.
        out = _project_agent_usage_top_level(
            {"input_tokens": 5, "output_tokens": 2, "cache_read_tokens": 9,
             "cache_write_tokens": 1, "cost_usd": 0.1234567}
        )
        assert out["input_tokens"] == 5
        assert out["output_tokens"] == 2
        assert out["cached_input_tokens"] == 9
        assert out["cache_read_tokens"] == 9
        assert out["cache_write_tokens"] == 1
        # cost rounded to 6 places
        assert out["cost_usd"] == 0.123457

    def test_non_numeric_fields_coerced_to_zero(self):
        out = _project_agent_usage_top_level(
            {"input_tokens": "oops", "cost_usd": "nan-ish"}
        )
        assert out["input_tokens"] == 0
        assert out["cost_usd"] == 0.0

    def test_none_field_values_coerced_to_zero(self):
        out = _project_agent_usage_top_level({"input_tokens": None, "cost_usd": None})
        assert out["input_tokens"] == 0
        assert out["cost_usd"] == 0.0


# ---------------------------------------------------------------------------
# _project_artifact_record
# ---------------------------------------------------------------------------


class TestProjectArtifactRecord:
    def test_relativizes_absolute_path_under_run_dir(self, tmp_path):
        run_dir = tmp_path / "run_1"
        run_dir.mkdir()
        rich = {
            "container_path": str(run_dir / "task_output" / "out.txt"),
            "filename": "out.txt", "mime_type": "text/plain", "size_bytes": 12,
        }
        rec = _project_artifact_record(rich, ref_id="artifact_0", run_dir=run_dir)
        assert rec["ref_id"] == "artifact_0"
        assert rec["path"] == "task_output/out.txt"
        assert rec["filename"] == "out.txt"
        assert rec["mime_type"] == "text/plain"
        assert rec["size_bytes"] == 12
        assert rec["source"] == "agent_workspace"

    def test_absolute_path_outside_run_dir_kept_verbatim(self, tmp_path):
        run_dir = tmp_path / "run_1"
        run_dir.mkdir()
        rich = {"container_path": "/root/workspace/thing.bin", "filename": "thing.bin"}
        rec = _project_artifact_record(rich, ref_id="artifact_3", run_dir=run_dir)
        # not under run_dir -> ValueError on relative_to -> path kept as-is
        assert rec["path"] == "/root/workspace/thing.bin"

    def test_bad_size_coerced_to_zero(self, tmp_path):
        rec = _project_artifact_record(
            {"container_path": "", "size_bytes": "big"},
            ref_id="a", run_dir=tmp_path,
        )
        assert rec["size_bytes"] == 0

    def test_missing_fields_default_empty(self, tmp_path):
        rec = _project_artifact_record({}, ref_id="a", run_dir=tmp_path)
        assert rec["path"] == ""
        assert rec["filename"] == ""
        assert rec["mime_type"] == ""
        assert rec["size_bytes"] == 0


# ---------------------------------------------------------------------------
# _condense_transcript_for_judge
# ---------------------------------------------------------------------------


class TestCondenseTranscript:
    def test_empty_trajectory(self):
        assert _condense_transcript_for_judge({}) == ""
        assert _condense_transcript_for_judge({"messages": []}) == ""

    def test_plain_string_content(self):
        traj = {"messages": [{"message": {"role": "user", "content": "hello"}}]}
        assert _condense_transcript_for_judge(traj) == "[user] hello"

    def test_text_block_content(self):
        traj = {
            "messages": [
                {"message": {"role": "assistant",
                             "content": [{"type": "text", "text": "answer"}]}}
            ]
        }
        assert _condense_transcript_for_judge(traj) == "[assistant] answer"

    def test_tool_call_block(self):
        traj = {
            "messages": [
                {"message": {"role": "assistant",
                             "content": [{"type": "toolCall", "name": "ls",
                                          "arguments": {"path": "/"}}]}}
            ]
        }
        out = _condense_transcript_for_judge(traj)
        assert out == '[assistant:tool] ls {"path": "/"}'

    def test_tool_result_block(self):
        traj = {
            "messages": [
                {"message": {"role": "user",
                             "content": [{"type": "toolResult", "text": "file listing"}]}}
            ]
        }
        assert _condense_transcript_for_judge(traj) == "[toolResult] file listing"

    def test_whitespace_only_string_skipped(self):
        traj = {"messages": [{"message": {"role": "user", "content": "   "}}]}
        assert _condense_transcript_for_judge(traj) == ""

    def test_limit_kwarg_ignored(self):
        # By policy the limit is never applied; full text is always emitted.
        long = "x" * 5000
        traj = {"messages": [{"message": {"role": "user", "content": long}}]}
        out = _condense_transcript_for_judge(traj, limit=10)
        assert out == f"[user] {long}"

    def test_message_without_wrapper(self):
        # entries where role/content live at top level (no `message` wrapper).
        traj = {"messages": [{"role": "user", "content": "top-level"}]}
        assert _condense_transcript_for_judge(traj) == "[user] top-level"


# ---------------------------------------------------------------------------
# _normalize_display_model — recursive model-id relabel
# ---------------------------------------------------------------------------


class TestNormalizeDisplayModel:
    def test_rewrites_dash_opus_id_in_dict(self):
        obj = {"model": "claude-opus-4-6"}
        _normalize_display_model(obj)
        assert obj["model"] == "claude-opus-4.7"

    def test_rewrites_provider_qualified_id(self):
        obj = {"model": "anthropic/claude-opus-4-6"}
        _normalize_display_model(obj)
        assert obj["model"] == "anthropic/claude-opus-4.7"

    def test_leaves_unknown_model_untouched(self):
        obj = {"model": "gpt-5.5"}
        _normalize_display_model(obj)
        assert obj["model"] == "gpt-5.5"

    def test_recurses_into_nested_structures(self):
        obj = {"messages": [{"message": {"model": "claude-opus-4-6"}}]}
        _normalize_display_model(obj)
        assert obj["messages"][0]["message"]["model"] == "claude-opus-4.7"

    def test_non_model_string_keys_left_alone(self):
        obj = {"name": "claude-opus-4-6"}
        _normalize_display_model(obj)
        assert obj["name"] == "claude-opus-4-6"


# ---------------------------------------------------------------------------
# _compute_testgen_cache_key — content hash over rubric/prompt/config/mock_data
# ---------------------------------------------------------------------------


class TestComputeTestgenCacheKey:
    def test_no_task_dir_returns_empty(self):
        assert _compute_testgen_cache_key({}) == ""

    def test_missing_dir_returns_empty(self, tmp_path):
        assert _compute_testgen_cache_key({"task_dir": str(tmp_path / "nope")}) == ""

    def test_stable_for_same_content(self, tmp_path):
        d = tmp_path / "task"
        d.mkdir()
        (d / "rubric.json").write_text('{"a": 1}')
        (d / "prompt.txt").write_text("do the thing")
        k1 = _compute_testgen_cache_key({"task_dir": str(d)})
        k2 = _compute_testgen_cache_key({"task_dir": str(d)})
        assert k1 == k2
        assert len(k1) == 32

    def test_changes_when_prompt_changes(self, tmp_path):
        d = tmp_path / "task"
        d.mkdir()
        (d / "rubric.json").write_text('{"a": 1}')
        (d / "prompt.txt").write_text("v1")
        k1 = _compute_testgen_cache_key({"task_dir": str(d)})
        (d / "prompt.txt").write_text("v2")
        k2 = _compute_testgen_cache_key({"task_dir": str(d)})
        assert k1 != k2

    def test_changes_when_mock_data_content_changes(self, tmp_path):
        d = tmp_path / "task"
        (d / "mock_data" / "figma-api").mkdir(parents=True)
        (d / "rubric.json").write_text("{}")
        fixture = d / "mock_data" / "figma-api" / "data.json"
        fixture.write_text('{"x": 1}')
        k1 = _compute_testgen_cache_key({"task_dir": str(d)})
        # same byte length, different content -> must change the key
        fixture.write_text('{"x": 2}')
        k2 = _compute_testgen_cache_key({"task_dir": str(d)})
        assert k1 != k2


# ---------------------------------------------------------------------------
# _augment_task_with_mocks — task-dict population (no docker)
#
# Delegates required/distractor resolution to _resolve_task_apis; here we drive
# it with a task that has no task_dir / no declared APIs so inference is a no-op,
# using a minimal fake config to avoid touching the real environment catalog.
# ---------------------------------------------------------------------------


class _FakeConfig:
    def __init__(self, tmp_path):
        self.environment_dir = tmp_path / "environment"  # nonexistent -> empty catalog
        self.work_dir = tmp_path / "work"
        self.wildclaw_skills_dir = tmp_path / "skills"
        self.default_skills = []


class TestAugmentTaskWithMocks:
    def test_populates_core_fields(self, tmp_path):
        cfg = _FakeConfig(tmp_path)
        task = {"task_id": "t1", "prompt": "hi", "distractor_apis_declared": "__ABSENT__"}
        _augment_task_with_mocks(task, cfg, mock_env_dict={"FIGMA_API_URL": "http://x"})
        assert task["required_apis"] == []
        assert task["distractor_apis"] == []
        assert task["mock_overlays"] == {}
        assert task["env_dict"] == {"FIGMA_API_URL": "http://x"}
        assert task["env_dir"] == str(cfg.environment_dir)
        assert task["skills_path"] == str(cfg.wildclaw_skills_dir)

    def test_env_dict_defaults_empty_when_no_mock_env(self, tmp_path):
        cfg = _FakeConfig(tmp_path)
        task = {"task_id": "t2", "prompt": "hi", "distractor_apis_declared": "__ABSENT__"}
        _augment_task_with_mocks(task, cfg, mock_env_dict=None)
        assert task["env_dict"] == {}

    def test_default_skills_merged_and_deduped(self, tmp_path):
        cfg = _FakeConfig(tmp_path)
        cfg.default_skills = ["pdf-extract", "video-frames"]
        task = {
            "task_id": "t3", "prompt": "hi",
            "distractor_apis_declared": "__ABSENT__",
            "skills": "pdf-extract\ncustom-skill",
        }
        _augment_task_with_mocks(task, cfg, mock_env_dict=None)
        # existing first, new appended, dupes removed, order preserved
        assert task["skills"].splitlines() == ["pdf-extract", "custom-skill", "video-frames"]

    def test_explicit_required_apis_declared(self, tmp_path):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # skills_inference._build_catalog returns a small hardcoded fallback
        # catalog when the environment dir is missing. A declared API IN that
        # fallback (etsy-api) survives; one NOT in it would be dropped as
        # "not present in catalog". etsy-api is a stable member of the fallback.
        cfg = _FakeConfig(tmp_path)
        task = {
            "task_id": "t4", "prompt": "hi",
            "required_apis_declared": ["etsy-api"],
            "distractor_apis_declared": "__ABSENT__",
        }
        _augment_task_with_mocks(task, cfg, mock_env_dict=None)
        assert task["required_apis"] == ["etsy-api"]

    def test_declared_api_absent_from_catalog_is_dropped(self, tmp_path):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # A declared required API that is NOT in the resolved catalog is
        # silently dropped (with a warning), leaving required_apis empty.
        cfg = _FakeConfig(tmp_path)
        task = {
            "task_id": "t5", "prompt": "hi",
            "required_apis_declared": ["totally-made-up-api"],
            "distractor_apis_declared": "__ABSENT__",
        }
        _augment_task_with_mocks(task, cfg, mock_env_dict=None)
        assert task["required_apis"] == []


# ---------------------------------------------------------------------------
# _resolve_task_apis — mock_data overlays + distractor policy
# ---------------------------------------------------------------------------


class TestResolveTaskApis:
    def test_mock_data_unions_into_required_when_undeclared(self, tmp_path):
        cfg = _FakeConfig(tmp_path)
        task_dir = tmp_path / "task"
        # etsy-api is in the fallback catalog so it survives the catalog filter.
        api_dir = task_dir / "mock_data" / "etsy-api"
        api_dir.mkdir(parents=True)
        (api_dir / "listings.json").write_text('{"x": 1}')
        task = {
            "task_id": "tm", "prompt": "hi", "task_dir": str(task_dir),
            "distractor_apis_declared": "__ABSENT__",
        }
        required, distractor, overlays = _resolve_task_apis(task, cfg)
        assert "etsy-api" in required
        assert distractor == []
        # overlay maps filename -> resolved absolute path
        assert "etsy-api" in overlays
        assert overlays["etsy-api"]["listings.json"] == str((api_dir / "listings.json").resolve())

    def test_declared_required_suppresses_mock_data_union(self, tmp_path):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # When required is explicitly declared, mock_data dirs still produce
        # overlays but do NOT union into required (author contract wins).
        cfg = _FakeConfig(tmp_path)
        task_dir = tmp_path / "task"
        api_dir = task_dir / "mock_data" / "linear-api"
        api_dir.mkdir(parents=True)
        (api_dir / "issues.json").write_text("{}")
        task = {
            "task_id": "td", "prompt": "hi", "task_dir": str(task_dir),
            "required_apis_declared": ["etsy-api"],
            "distractor_apis_declared": "__ABSENT__",
        }
        required, distractor, overlays = _resolve_task_apis(task, cfg)
        assert required == {"etsy-api"}  # linear-api NOT unioned in
        assert "linear-api" in overlays  # but overlay still produced

    def test_distractor_list_minus_required(self, tmp_path):
        cfg = _FakeConfig(tmp_path)
        task = {
            "task_id": "tl", "prompt": "hi",
            "required_apis_declared": ["etsy-api"],
            # both in fallback catalog; etsy-api overlaps required -> removed
            "distractor_apis_declared": ["etsy-api", "linear-api"],
        }
        required, distractor, overlays = _resolve_task_apis(task, cfg)
        assert required == {"etsy-api"}
        assert distractor == ["linear-api"]

    def test_distractor_absent_yields_empty(self, tmp_path):
        cfg = _FakeConfig(tmp_path)
        task = {"task_id": "ta", "prompt": "hi",
                "required_apis_declared": ["etsy-api"]}
        # key absent entirely -> distractor_is_absent -> []
        required, distractor, overlays = _resolve_task_apis(task, cfg)
        assert distractor == []


# ---------------------------------------------------------------------------
# _write_pass_summary — locked read-modify-write of pass_summary.json (offline)
# ---------------------------------------------------------------------------


class TestWritePassSummary:
    def test_creates_summary_file(self, tmp_path):
        model_dir = tmp_path / "claude"
        _write_pass_summary(
            model_dir, "claude", run_index=0,
            scores={"overall_score": 0.5, "criteria_total": 2}, test_result=None,
        )
        doc = json.loads((model_dir / "pass_summary.json").read_text())
        assert doc["model"] == "claude"
        assert doc["runs"] == 1
        assert doc["per_run"][0]["run_index"] == 0
        assert doc["average_reward"] == 0.5

    def test_second_run_appends(self, tmp_path):
        model_dir = tmp_path / "claude"
        _write_pass_summary(model_dir, "claude", 0, {"overall_score": 0.4}, None)
        _write_pass_summary(model_dir, "claude", 1, {"overall_score": 0.6}, None)
        doc = json.loads((model_dir / "pass_summary.json").read_text())
        assert doc["runs"] == 2
        assert doc["average_reward"] == pytest.approx(0.5)
        assert [r["run_index"] for r in doc["per_run"]] == [0, 1]

    def test_rerun_same_index_replaces(self, tmp_path):
        model_dir = tmp_path / "claude"
        _write_pass_summary(model_dir, "claude", 0, {"overall_score": 0.2}, None)
        # re-run index 0 with a better score -> old entry replaced, not duplicated
        _write_pass_summary(model_dir, "claude", 0, {"overall_score": 0.9}, None)
        doc = json.loads((model_dir / "pass_summary.json").read_text())
        assert doc["runs"] == 1
        assert doc["per_run"][0]["rubric_reward"] == 0.9

    def test_corrupt_existing_summary_recovers(self, tmp_path):
        model_dir = tmp_path / "claude"
        model_dir.mkdir()
        (model_dir / "pass_summary.json").write_text("{ this is not valid json")
        # malformed existing file -> treated as empty, does not raise
        _write_pass_summary(model_dir, "claude", 0, {"overall_score": 0.3}, None)
        doc = json.loads((model_dir / "pass_summary.json").read_text())
        assert doc["runs"] == 1
