"""Behavioral coverage for the four cross-run rollup scripts under script/.

Covered modules (loaded via importlib because script/ is not an importable pkg):
  * script/aggregate_runs.py        — pass@K = max(pcts), _pct_from_score,
                                       _criteria_counts alias fallback, error-stub
                                       0.0 inclusion (pins current behavior).
  * script/merge_pass_summaries.py  — _f/_mean/_pmax/_round_or_none/_comparable_per_run,
                                       concat vs --dedup, run renumber, model-conflict
                                       exit, legacy vs extended schema.
  * script/rebuild_pass_summary.py  — reward.txt-first precedence, _pass_summary_entry/
                                       _doc verbatim ports, discover_run_dirs, rebuild.
  * script/backfill_pass_summary.py — overall_score-first precedence, per-test-list vs
                                       summary counting, _find_model_dirs, rebuild_model_dir.

Import bootstrapping and spec_from_file_location loading mirror
tests/test_repackage_bundle_ground_truth.py. All fixtures are self-contained.
No docker / network / AWS: these scripts are stdlib-only file walkers.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


# --------------------------------------------------------------------------- #
# Module loaders (script/ is not a package)
# --------------------------------------------------------------------------- #
def _load_script(basename: str, mod_alias: str):
    path = _REPO_ROOT / "script" / basename
    assert path.exists(), f"script missing: {path}"
    spec = importlib.util.spec_from_file_location(mod_alias, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_alias] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def agg():
    return _load_script("aggregate_runs.py", "_test_aggregate_runs")


@pytest.fixture(scope="module")
def merge():
    return _load_script("merge_pass_summaries.py", "_test_merge_pass_summaries")


@pytest.fixture(scope="module")
def rebuild():
    return _load_script("rebuild_pass_summary.py", "_test_rebuild_pass_summary")


@pytest.fixture(scope="module")
def backfill():
    return _load_script("backfill_pass_summary.py", "_test_backfill_pass_summary")


# --------------------------------------------------------------------------- #
# Shared tree builders
# --------------------------------------------------------------------------- #
def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def _mk_run_dir(
    output_root: Path,
    backend: str,
    task: str,
    model: str,
    run_n: int,
    *,
    score: dict | None = None,
    ctrf: dict | None = None,
    reward_txt: str | None = None,
) -> Path:
    """Build output/<backend>/<task>/trajectories/<model>/run_<N>/ with artifacts."""
    run_dir = output_root / backend / task / "trajectories" / model / f"run_{run_n}"
    run_dir.mkdir(parents=True, exist_ok=True)
    if score is not None:
        _write_json(run_dir / "score.json", score)
    verifier = run_dir / "task_output" / "logs" / "verifier"
    if ctrf is not None:
        _write_json(verifier / "ctrf.json", ctrf)
    if reward_txt is not None:
        verifier.mkdir(parents=True, exist_ok=True)
        (verifier / "reward.txt").write_text(reward_txt, encoding="utf-8")
    return run_dir


# =========================================================================== #
# aggregate_runs.py
# =========================================================================== #
class TestAggregatePctFromScore:
    def test_canonical_rubric_weights_percentage_wins(self, agg):
        assert agg._pct_from_score({"rubric_weights_percentage": 73.5}) == 73.5

    def test_overall_score_fallback_scales_by_100(self, agg):
        # overall_score in [0,1] -> *100.
        assert agg._pct_from_score({"overall_score": 0.42}) == 42.0

    def test_canonical_preferred_over_overall_score(self, agg):
        out = agg._pct_from_score({"rubric_weights_percentage": 90.0, "overall_score": 0.1})
        assert out == 90.0

    def test_zero_overall_score_is_zero_not_none(self, agg):
        # 0.0 * 100 == 0.0 and isinstance(0.0, float) -> returned, not None.
        assert agg._pct_from_score({"overall_score": 0.0}) == 0.0

    def test_missing_both_returns_none(self, agg):
        assert agg._pct_from_score({}) is None

    def test_non_numeric_pct_falls_through_to_overall(self, agg):
        assert agg._pct_from_score({"rubric_weights_percentage": "nope", "overall_score": 0.5}) == 50.0

    def test_bool_is_numeric_subtype(self, agg):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # bool is a subtype of int, so True passes isinstance(..., (int,float)).
        assert agg._pct_from_score({"rubric_weights_percentage": True}) == 1.0


class TestAggregateCriteriaCounts:
    def test_canonical_criteria_keys(self, agg):
        s = {"criteria_total": 10, "criteria_passed": 7, "criteria_failed": 3}
        assert agg._criteria_counts(s) == (10, 7, 3)

    def test_deprecated_tests_alias_fallback(self, agg):
        s = {"tests_total": 5, "tests_passed": 2, "tests_failed": 3}
        assert agg._criteria_counts(s) == (5, 2, 3)

    def test_canonical_wins_over_alias(self, agg):
        s = {"criteria_total": 8, "tests_total": 99}
        total, _, _ = agg._criteria_counts(s)
        assert total == 8

    def test_empty_score_yields_zeros(self, agg):
        assert agg._criteria_counts({}) == (0, 0, 0)

    def test_none_values_coerce_to_zero(self, agg):
        # `score.get(k, 0) or 0` collapses None -> 0.
        s = {"criteria_total": None, "criteria_passed": None, "criteria_failed": None}
        assert agg._criteria_counts(s) == (0, 0, 0)


class TestAggregateWalk:
    def test_walk_yields_valid_runs(self, agg, tmp_path):
        _mk_run_dir(tmp_path, "openclaw", "task-a", "opus", 1, score={"overall_score": 0.5})
        _mk_run_dir(tmp_path, "openclaw", "task-a", "opus", 2, score={"overall_score": 0.9})
        rows = list(agg._walk_score_files(tmp_path, None))
        assert {(b, t, m, i) for (b, t, m, i, _p) in rows} == {
            ("openclaw", "task-a", "opus", 1),
            ("openclaw", "task-a", "opus", 2),
        }

    def test_walk_missing_root_returns_empty(self, agg, tmp_path):
        assert list(agg._walk_score_files(tmp_path / "nope", None)) == []

    def test_walk_backend_filter(self, agg, tmp_path):
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 1, score={"overall_score": 0.5})
        _mk_run_dir(tmp_path, "codex", "t", "m", 1, score={"overall_score": 0.5})
        rows = list(agg._walk_score_files(tmp_path, "openclaw"))
        assert {b for (b, *_rest) in rows} == {"openclaw"}

    def test_walk_skips_non_run_prefixed_and_missing_score(self, agg, tmp_path):
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 1, score={"overall_score": 0.5})
        # run dir with no score.json
        (tmp_path / "openclaw" / "t" / "trajectories" / "m" / "run_2").mkdir(parents=True)
        # non-run-prefixed dir
        (tmp_path / "openclaw" / "t" / "trajectories" / "m" / "junk").mkdir(parents=True)
        rows = list(agg._walk_score_files(tmp_path, None))
        assert len(rows) == 1 and rows[0][3] == 1

    def test_walk_skips_non_integer_run_suffix(self, agg, tmp_path):
        bad = tmp_path / "openclaw" / "t" / "trajectories" / "m" / "run_x"
        bad.mkdir(parents=True)
        (bad / "score.json").write_text("{}", encoding="utf-8")
        assert list(agg._walk_score_files(tmp_path, None)) == []

    def test_walk_skips_task_without_trajectories(self, agg, tmp_path):
        (tmp_path / "openclaw" / "orphan").mkdir(parents=True)
        assert list(agg._walk_score_files(tmp_path, None)) == []


class TestAggregateAggregate:
    def test_pass_at_k_is_max_of_run_pcts(self, agg, tmp_path):
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 1, score={"rubric_weights_percentage": 40.0})
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 2, score={"rubric_weights_percentage": 88.0})
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 3, score={"rubric_weights_percentage": 12.0})
        summary = agg.aggregate(tmp_path)
        tm = summary["by_task_model"][0]
        assert tm["pass_at_k"] == 88.0
        assert tm["k"] == 3
        assert tm["run_count"] == 3
        # mean of 40,88,12 = 46.67
        assert tm["average_rubric_weights_percentage"] == pytest.approx(46.67, abs=0.01)

    def test_error_stub_zero_included_in_pass_at_k(self, agg, tmp_path):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # An error stub run writes overall_score 0.0; it is a valid pct (0.0),
        # so it lands in the pool. pass@K still equals the best good run, but a
        # solitary error stub would make pass@K 0.0 rather than being skipped.
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 1, score={"overall_score": 0.0})
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 2, score={"rubric_weights_percentage": 55.0})
        summary = agg.aggregate(tmp_path)
        tm = summary["by_task_model"][0]
        assert tm["run_count"] == 2
        assert tm["pass_at_k"] == 55.0

    def test_solitary_error_stub_drags_pass_at_k_to_zero(self, agg, tmp_path):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 1, score={"overall_score": 0.0})
        summary = agg.aggregate(tmp_path)
        assert summary["by_task_model"][0]["pass_at_k"] == 0.0

    def test_score_with_no_pct_is_skipped(self, agg, tmp_path):
        # score.json exists but has neither pct nor overall_score -> dropped.
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 1, score={"foo": "bar"})
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 2, score={"overall_score": 0.7})
        summary = agg.aggregate(tmp_path)
        assert summary["by_task_model"][0]["run_count"] == 1

    def test_invalid_json_score_is_skipped(self, agg, tmp_path):
        run_dir = tmp_path / "openclaw" / "t" / "trajectories" / "m" / "run_1"
        run_dir.mkdir(parents=True)
        (run_dir / "score.json").write_text("{not json", encoding="utf-8")
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 2, score={"overall_score": 0.7})
        summary = agg.aggregate(tmp_path)
        assert summary["by_task_model"][0]["run_count"] == 1

    def test_single_run_stddev_is_zero(self, agg, tmp_path):
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 1, score={"rubric_weights_percentage": 50.0})
        summary = agg.aggregate(tmp_path)
        assert summary["by_task_model"][0]["stddev_rubric_weights_percentage"] == 0.0

    def test_by_model_average_pass_at_k_across_tasks(self, agg, tmp_path):
        # two tasks, each best run: task-a best=80, task-b best=20 -> mean pass@K = 50.
        _mk_run_dir(tmp_path, "openclaw", "task-a", "m", 1, score={"rubric_weights_percentage": 80.0})
        _mk_run_dir(tmp_path, "openclaw", "task-a", "m", 2, score={"rubric_weights_percentage": 10.0})
        _mk_run_dir(tmp_path, "openclaw", "task-b", "m", 1, score={"rubric_weights_percentage": 20.0})
        summary = agg.aggregate(tmp_path)
        bm = summary["by_model"][0]
        assert bm["task_count"] == 2
        assert bm["run_count"] == 3
        assert bm["average_pass_at_k"] == pytest.approx(50.0, abs=0.01)
        # mean over ALL runs: (80+10+20)/3 = 36.67
        assert bm["average_rubric_weights_percentage"] == pytest.approx(36.67, abs=0.01)

    def test_empty_output_root_yields_empty_summary(self, agg, tmp_path):
        summary = agg.aggregate(tmp_path)
        assert summary == {"by_task_model": [], "by_model": []}

    def test_print_table_smoke(self, agg, tmp_path, capsys):
        _mk_run_dir(tmp_path, "openclaw", "t", "m", 1, score={"rubric_weights_percentage": 50.0})
        summary = agg.aggregate(tmp_path)
        agg._print_table(summary)
        out = capsys.readouterr().out
        assert "by (backend, task, model)" in out
        assert "by (backend, model)" in out


class TestAggregateMain:
    def test_main_writes_summary_json(self, agg, tmp_path, monkeypatch, capsys):
        out_root = tmp_path / "output"
        _mk_run_dir(out_root, "openclaw", "t", "m", 1, score={"rubric_weights_percentage": 50.0})
        write_target = tmp_path / "summary.json"
        monkeypatch.setattr(sys, "argv", [
            "aggregate_runs.py",
            "--output-root", str(out_root),
            "--backend", "openclaw",
            "--write", str(write_target),
            "--json-only",
        ])
        rc = agg.main()
        assert rc == 0
        data = json.loads(write_target.read_text(encoding="utf-8"))
        assert data["by_task_model"][0]["pass_at_k"] == 50.0

    def test_main_default_write_path_uses_backend_tag(self, agg, tmp_path, monkeypatch):
        out_root = tmp_path / "output"
        _mk_run_dir(out_root, "openclaw", "t", "m", 1, score={"rubric_weights_percentage": 50.0})
        monkeypatch.setattr(sys, "argv", [
            "aggregate_runs.py", "--output-root", str(out_root),
            "--backend", "openclaw", "--json-only",
        ])
        rc = agg.main()
        assert rc == 0
        assert (out_root / "openclaw_aggregate_summary.json").is_file()

    def test_main_default_write_path_all_tag(self, agg, tmp_path, monkeypatch):
        out_root = tmp_path / "output"
        _mk_run_dir(out_root, "openclaw", "t", "m", 1, score={"rubric_weights_percentage": 50.0})
        monkeypatch.setattr(sys, "argv", [
            "aggregate_runs.py", "--output-root", str(out_root), "--json-only",
        ])
        rc = agg.main()
        assert rc == 0
        assert (out_root / "all_aggregate_summary.json").is_file()

    def test_main_prints_table_and_wrote_line(self, agg, tmp_path, monkeypatch, capsys):
        out_root = tmp_path / "output"
        _mk_run_dir(out_root, "openclaw", "t", "m", 1, score={"rubric_weights_percentage": 50.0})
        monkeypatch.setattr(sys, "argv", [
            "aggregate_runs.py", "--output-root", str(out_root),
        ])
        rc = agg.main()
        assert rc == 0
        out = capsys.readouterr().out
        assert "Wrote" in out
        assert "by (backend, task, model)" in out


# =========================================================================== #
# merge_pass_summaries.py
# =========================================================================== #
class TestMergeHelpers:
    def test_f_valid(self, merge):
        assert merge._f("3.5") == 3.5
        assert merge._f(2) == 2.0

    def test_f_none_and_bad(self, merge):
        assert merge._f(None) is None
        assert merge._f("abc") is None
        assert merge._f([1, 2]) is None

    def test_f_rejects_nan_and_inf(self, merge):
        assert merge._f(float("nan")) is None
        assert merge._f(float("inf")) is None
        assert merge._f(float("-inf")) is None

    def test_mean(self, merge):
        assert merge._mean([1.0, 2.0, None, 3.0]) == 2.0

    def test_mean_all_none_is_none(self, merge):
        assert merge._mean([None, None]) is None
        assert merge._mean([]) is None

    def test_pmax(self, merge):
        assert merge._pmax([1.0, None, 9.0, 3.0]) == 9.0

    def test_pmax_all_none_is_none(self, merge):
        assert merge._pmax([None]) is None

    def test_round_or_none(self, merge):
        assert merge._round_or_none(1.23456) == 1.23
        assert merge._round_or_none(None) is None

    def test_comparable_per_run_ignores_run_index(self, merge):
        a = {"run_index": 1, "rubric_weights_percentage": 50.0}
        b = {"run_index": 9, "rubric_weights_percentage": 50.0}
        assert merge._comparable_per_run(a) == merge._comparable_per_run(b)

    def test_comparable_per_run_distinguishes_content(self, merge):
        a = {"run_index": 1, "rubric_weights_percentage": 50.0}
        b = {"run_index": 1, "rubric_weights_percentage": 51.0}
        assert merge._comparable_per_run(a) != merge._comparable_per_run(b)


def _pass_summary_file(tmp_path: Path, name: str, model: str, per_run: list[dict]) -> Path:
    p = tmp_path / name
    _write_json(p, {"model": model, "per_run": per_run})
    return p


class TestMergeCore:
    def test_concat_semantics_1_plus_7_equals_8(self, merge, tmp_path):
        a = _pass_summary_file(tmp_path, "a.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 50.0}])
        b_runs = [{"run_index": i, "rubric_weights_percentage": 10.0 * i} for i in range(1, 8)]
        b = _pass_summary_file(tmp_path, "b.json", "opus", b_runs)
        merged = merge.merge_pass_summaries([a, b])
        assert merged["runs"] == 8
        # run_index renumbered 1..8 sequentially
        assert [r["run_index"] for r in merged["per_run"]] == list(range(1, 9))

    def test_dedup_drops_identical_reps(self, merge, tmp_path):
        rec = {"run_index": 1, "rubric_weights_percentage": 50.0, "include_multimodal": True}
        a = _pass_summary_file(tmp_path, "a.json", "opus", [dict(rec)])
        b = _pass_summary_file(tmp_path, "b.json", "opus", [dict(rec)])
        merged = merge.merge_pass_summaries([a, b], dedup=True)
        assert merged["runs"] == 1

    def test_no_dedup_keeps_coincidental_duplicates(self, merge, tmp_path):
        rec = {"run_index": 1, "rubric_weights_percentage": 50.0}
        a = _pass_summary_file(tmp_path, "a.json", "opus", [dict(rec)])
        b = _pass_summary_file(tmp_path, "b.json", "opus", [dict(rec)])
        merged = merge.merge_pass_summaries([a, b], dedup=False)
        assert merged["runs"] == 2

    def test_legacy_schema_shape(self, merge, tmp_path):
        a = _pass_summary_file(tmp_path, "a.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 60.0,
                                 "test_weights_percentage": 40.0}])
        b = _pass_summary_file(tmp_path, "b.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 80.0,
                                 "test_weights_percentage": 20.0}])
        merged = merge.merge_pass_summaries([a, b])
        assert set(merged.keys()) == {
            "model", "runs", "average_test_weights_percentage",
            "average_rubric_weights_percentage", "per_run",
        }
        assert merged["average_rubric_weights_percentage"] == 70.0
        assert merged["average_test_weights_percentage"] == 30.0
        # per-run keys are the 4 legacy keys
        assert set(merged["per_run"][0].keys()) == {
            "run_index", "include_multimodal",
            "test_weights_percentage", "rubric_weights_percentage",
        }

    def test_legacy_include_multimodal_defaults_true(self, merge, tmp_path):
        a = _pass_summary_file(tmp_path, "a.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 60.0}])
        b = _pass_summary_file(tmp_path, "b.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 80.0,
                                 "include_multimodal": False}])
        merged = merge.merge_pass_summaries([a, b])
        assert merged["per_run"][0]["include_multimodal"] is True
        assert merged["per_run"][1]["include_multimodal"] is False

    def test_extended_schema_emits_pass_at_k(self, merge, tmp_path):
        a = _pass_summary_file(tmp_path, "a.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 60.0,
                                 "reward": 0.6, "combined_reward": 0.6,
                                 "rubric_reward": 0.6, "test_reward": 0.5,
                                 "test_weights_percentage": 50.0}])
        b = _pass_summary_file(tmp_path, "b.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 90.0,
                                 "reward": 0.9, "combined_reward": 0.9,
                                 "rubric_reward": 0.9, "test_reward": 0.8,
                                 "test_weights_percentage": 80.0}])
        merged = merge.merge_pass_summaries([a, b], extended=True)
        assert merged["pass_at_k_rubric_weights_percentage"] == 90.0
        assert merged["pass_at_k_reward"] == 0.9
        assert merged["pass_at_k_combined_reward"] == 0.9
        assert merged["merged_from"] == [str(a), str(b)]
        assert merged["average_reward"] == pytest.approx(0.75)
        # per_run in extended keeps full records
        assert merged["per_run"][0]["run_index"] == 1
        assert merged["per_run"][1]["run_index"] == 2

    def test_extended_average_reward_zero_when_all_none(self, merge, tmp_path):
        a = _pass_summary_file(tmp_path, "a.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 60.0}])
        b = _pass_summary_file(tmp_path, "b.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 80.0}])
        merged = merge.merge_pass_summaries([a, b], extended=True)
        # `_mean(...) or 0.0` -> 0.0 when no reward values present
        assert merged["average_reward"] == 0.0
        assert merged["average_combined_reward"] is None

    def test_model_conflict_exits_2(self, merge, tmp_path):
        a = _pass_summary_file(tmp_path, "a.json", "opus", [{"run_index": 1}])
        b = _pass_summary_file(tmp_path, "b.json", "sonnet", [{"run_index": 1}])
        with pytest.raises(SystemExit) as exc:
            merge.merge_pass_summaries([a, b])
        assert exc.value.code == 2

    def test_missing_model_defaults_to_unknown(self, merge, tmp_path):
        a = tmp_path / "a.json"
        b = tmp_path / "b.json"
        _write_json(a, {"per_run": [{"run_index": 1, "rubric_weights_percentage": 50.0}]})
        _write_json(b, {"per_run": [{"run_index": 1, "rubric_weights_percentage": 60.0}]})
        merged = merge.merge_pass_summaries([a, b])
        assert merged["model"] == "unknown"

    def test_fewer_than_two_inputs_exits_2(self, merge, tmp_path):
        a = _pass_summary_file(tmp_path, "a.json", "opus", [{"run_index": 1}])
        with pytest.raises(SystemExit) as exc:
            merge.merge_pass_summaries([a])
        assert exc.value.code == 2

    def test_non_object_per_run_entry_skipped(self, merge, tmp_path, capsys):
        a = tmp_path / "a.json"
        _write_json(a, {"model": "opus", "per_run": ["not-a-dict",
                                                     {"run_index": 1, "rubric_weights_percentage": 50.0}]})
        b = _pass_summary_file(tmp_path, "b.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 70.0}])
        merged = merge.merge_pass_summaries([a, b])
        # the string entry is dropped; 1 valid from a + 1 from b = 2
        assert merged["runs"] == 2
        assert "non-object per_run entry" in capsys.readouterr().err


class TestMergeLoad:
    def test_load_rejects_bad_json(self, merge, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("{not json", encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            merge._load(p)
        assert exc.value.code == 2

    def test_load_rejects_non_object_top_level(self, merge, tmp_path):
        p = tmp_path / "arr.json"
        p.write_text("[1, 2, 3]", encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            merge._load(p)
        assert exc.value.code == 2

    def test_load_rejects_missing_per_run(self, merge, tmp_path):
        p = tmp_path / "no_pr.json"
        _write_json(p, {"model": "opus"})
        with pytest.raises(SystemExit) as exc:
            merge._load(p)
        assert exc.value.code == 2

    def test_load_missing_file_exits_2(self, merge, tmp_path):
        with pytest.raises(SystemExit) as exc:
            merge._load(tmp_path / "nope.json")
        assert exc.value.code == 2


class TestMergeMain:
    def test_main_stdout(self, merge, tmp_path, monkeypatch, capsys):
        a = _pass_summary_file(tmp_path, "a.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 50.0}])
        b = _pass_summary_file(tmp_path, "b.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 70.0}])
        monkeypatch.setattr(sys, "argv", ["merge.py", str(a), str(b)])
        rc = merge.main()
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["runs"] == 2

    def test_main_in_place_rewrites_first(self, merge, tmp_path, monkeypatch):
        a = _pass_summary_file(tmp_path, "a.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 50.0}])
        b = _pass_summary_file(tmp_path, "b.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 70.0}])
        monkeypatch.setattr(sys, "argv", ["merge.py", str(a), str(b), "--in-place"])
        rc = merge.main()
        assert rc == 0
        rewritten = json.loads(a.read_text(encoding="utf-8"))
        assert rewritten["runs"] == 2

    def test_main_output_file(self, merge, tmp_path, monkeypatch):
        a = _pass_summary_file(tmp_path, "a.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 50.0}])
        b = _pass_summary_file(tmp_path, "b.json", "opus",
                               [{"run_index": 1, "rubric_weights_percentage": 70.0}])
        target = tmp_path / "out.json"
        monkeypatch.setattr(sys, "argv", ["merge.py", str(a), str(b), "-o", str(target)])
        rc = merge.main()
        assert rc == 0
        assert json.loads(target.read_text(encoding="utf-8"))["runs"] == 2


# =========================================================================== #
# rebuild_pass_summary.py
# =========================================================================== #
class TestRebuildHelpers:
    def test_finite_float(self, rebuild):
        assert rebuild._finite_float(3) == 3.0
        assert rebuild._finite_float(2.5) == 2.5

    def test_finite_float_rejects_bool(self, rebuild):
        # bool explicitly excluded.
        assert rebuild._finite_float(True) is None

    def test_finite_float_rejects_nonfinite_and_nonnumeric(self, rebuild):
        assert rebuild._finite_float(float("nan")) is None
        assert rebuild._finite_float(float("inf")) is None
        assert rebuild._finite_float("5") is None
        assert rebuild._finite_float(None) is None

    def test_mean_or_none(self, rebuild):
        assert rebuild._mean_or_none([1.0, None, 3.0]) == 2.0
        assert rebuild._mean_or_none([None]) is None
        assert rebuild._mean_or_none([]) is None

    def test_load_json_missing_and_bad(self, rebuild, tmp_path):
        assert rebuild._load_json(tmp_path / "nope.json") is None
        bad = tmp_path / "bad.json"
        bad.write_text("{oops", encoding="utf-8")
        assert rebuild._load_json(bad) is None


class TestRebuildCtrfSummary:
    def test_reward_txt_takes_precedence_over_overall_score(self, rebuild, tmp_path):
        # reward.txt-first precedence: reward.txt=0.75 wins over summary overall_score=0.1.
        run_dir = tmp_path / "run_1"
        verifier = run_dir / "task_output" / "logs" / "verifier"
        _write_json(verifier / "ctrf.json",
                    {"results": {"summary": {"tests": 4, "passed": 3, "failed": 1,
                                             "overall_score": 0.1}}})
        (verifier / "reward.txt").write_text("0.75\n", encoding="utf-8")
        out = rebuild._read_ctrf_summary(run_dir)
        assert out["reward"] == 0.75
        assert out["tests_total"] == 4
        assert out["tests_passed"] == 3
        assert out["tests_failed"] == 1

    def test_falls_back_to_overall_score_when_no_reward_txt(self, rebuild, tmp_path):
        run_dir = tmp_path / "run_1"
        verifier = run_dir / "task_output" / "logs" / "verifier"
        _write_json(verifier / "ctrf.json",
                    {"results": {"summary": {"tests": 2, "passed": 2, "overall_score": 0.33}}})
        out = rebuild._read_ctrf_summary(run_dir)
        assert out["reward"] == 0.33

    def test_bad_reward_txt_falls_back(self, rebuild, tmp_path):
        run_dir = tmp_path / "run_1"
        verifier = run_dir / "task_output" / "logs" / "verifier"
        _write_json(verifier / "ctrf.json",
                    {"results": {"summary": {"tests": 1, "overall_score": 0.5}}})
        (verifier / "reward.txt").write_text("garbage", encoding="utf-8")
        out = rebuild._read_ctrf_summary(run_dir)
        assert out["reward"] == 0.5

    def test_missing_ctrf_yields_zero_counts(self, rebuild, tmp_path):
        run_dir = tmp_path / "run_1"
        run_dir.mkdir()
        out = rebuild._read_ctrf_summary(run_dir)
        assert out == {
            "tests_total": 0, "tests_passed": 0, "tests_failed": 0,
            "tests_errored": 0, "tests_skipped": 0, "reward": None,
        }

    def test_top_level_summary_shape_accepted(self, rebuild, tmp_path):
        # ctrf.get("summary") fallback when there is no results.summary.
        run_dir = tmp_path / "run_1"
        verifier = run_dir / "task_output" / "logs" / "verifier"
        _write_json(verifier / "ctrf.json",
                    {"summary": {"tests": 3, "passed": 1, "other": 2, "overall_score": 0.2}})
        out = rebuild._read_ctrf_summary(run_dir)
        assert out["tests_total"] == 3
        assert out["tests_errored"] == 2  # `other` -> errored
        assert out["reward"] == 0.2


class TestRebuildEntry:
    def test_rubric_reward_from_rubric_based_reward(self, rebuild):
        entry = rebuild._pass_summary_entry(
            1, {"rubric_based_reward": 0.8, "criteria_total": 5, "criteria_passed": 4}, None)
        assert entry["rubric_reward"] == 0.8
        assert entry["rubric_weights_percentage"] == 80.0
        assert entry["criteria_total"] == 5
        assert entry["criteria_passed"] == 4

    def test_rubric_reward_falls_back_to_overall_score(self, rebuild):
        entry = rebuild._pass_summary_entry(1, {"overall_score": 0.5}, None)
        assert entry["rubric_reward"] == 0.5
        assert entry["rubric_weights_percentage"] == 50.0

    def test_criteria_alias_from_tests_keys(self, rebuild):
        entry = rebuild._pass_summary_entry(
            2, {"tests_total": 7, "tests_passed": 3, "tests_failed": 4}, None)
        assert entry["criteria_total"] == 7
        assert entry["criteria_passed"] == 3
        assert entry["criteria_failed"] == 4

    def test_combined_averages_test_and_rubric(self, rebuild):
        scores = {"rubric_based_reward": 0.6}
        tr = {"tests_total": 3, "reward": 0.4}
        entry = rebuild._pass_summary_entry(1, scores, tr)
        # test_reward from tr.reward since test_based_reward absent and t_total>0.
        assert entry["test_reward"] == 0.4
        assert entry["combined_reward"] == pytest.approx(0.5)
        assert entry["reward"] == pytest.approx(0.5)  # authoritative = combined

    def test_test_reward_ignored_when_no_tests(self, rebuild):
        scores = {"rubric_based_reward": 0.6}
        tr = {"tests_total": 0, "reward": 0.4}
        entry = rebuild._pass_summary_entry(1, scores, tr)
        # t_total == 0 -> test_reward stays None -> combined == rubric_reward.
        assert entry["test_reward"] is None
        assert entry["combined_reward"] == 0.6
        assert entry["reward"] == 0.6

    def test_explicit_combined_reward_wins(self, rebuild):
        scores = {"rubric_based_reward": 0.6, "combined_reward": 0.99}
        tr = {"tests_total": 3, "reward": 0.1}
        entry = rebuild._pass_summary_entry(1, scores, tr)
        assert entry["combined_reward"] == 0.99

    def test_empty_scores_authoritative_zero(self, rebuild):
        entry = rebuild._pass_summary_entry(1, None, None)
        # rubric_reward None, no test -> combined None -> authoritative (rubric_reward or 0.0).
        assert entry["combined_reward"] is None
        assert entry["reward"] == 0.0
        assert entry["rubric_weights_percentage"] is None


class TestRebuildDoc:
    def test_doc_sorts_and_averages(self, rebuild):
        runs = [
            {"run_index": 2, "reward": 0.8, "combined_reward": 0.8,
             "rubric_reward": 0.8, "test_reward": None, "rubric_weights_percentage": 80.0},
            {"run_index": 1, "reward": 0.4, "combined_reward": 0.4,
             "rubric_reward": 0.4, "test_reward": None, "rubric_weights_percentage": 40.0},
        ]
        doc = rebuild._pass_summary_doc("opus", runs)
        assert doc["model"] == "opus"
        assert doc["runs"] == 2
        assert [r["run_index"] for r in doc["per_run"]] == [1, 2]
        assert doc["average_reward"] == pytest.approx(0.6)
        assert doc["average_rubric_weights_percentage"] == 60.0
        assert doc["average_test_reward"] is None

    def test_doc_average_reward_zero_when_all_none(self, rebuild):
        runs = [{"run_index": 1, "reward": None, "combined_reward": None,
                 "rubric_reward": None, "test_reward": None,
                 "rubric_weights_percentage": None}]
        doc = rebuild._pass_summary_doc("opus", runs)
        assert doc["average_reward"] == 0.0
        assert doc["average_rubric_weights_percentage"] is None


class TestRebuildDiscoverAndRebuild:
    def test_discover_run_dirs_sorted(self, rebuild, tmp_path):
        model_dir = tmp_path / "opus"
        for n in (3, 1, 2):
            (model_dir / f"run_{n}").mkdir(parents=True)
        (model_dir / "run_x").mkdir()  # non-integer, ignored
        (model_dir / "notrun").mkdir()  # no prefix, ignored
        found = rebuild.discover_run_dirs(model_dir)
        assert [i for i, _p in found] == [1, 2, 3]

    def test_discover_missing_dir_empty(self, rebuild, tmp_path):
        assert rebuild.discover_run_dirs(tmp_path / "nope") == []

    def test_rebuild_end_to_end(self, rebuild, tmp_path):
        model_dir = tmp_path / "openclaw" / "task" / "trajectories" / "opus"
        for n, ov in ((1, 0.4), (2, 0.8)):
            run_dir = model_dir / f"run_{n}"
            run_dir.mkdir(parents=True)
            _write_json(run_dir / "score.json", {"overall_score": ov})
        doc = rebuild.rebuild(model_dir)
        assert doc["model"] == "opus"
        assert doc["runs"] == 2
        assert doc["average_rubric_reward"] == pytest.approx(0.6)

    def test_rebuild_model_override(self, rebuild, tmp_path):
        model_dir = tmp_path / "opus"
        run_dir = model_dir / "run_1"
        run_dir.mkdir(parents=True)
        _write_json(run_dir / "score.json", {"overall_score": 0.5})
        doc = rebuild.rebuild(model_dir, model_type="custom-name")
        assert doc["model"] == "custom-name"

    def test_rebuild_no_runs_exits_2(self, rebuild, tmp_path):
        model_dir = tmp_path / "empty"
        model_dir.mkdir()
        with pytest.raises(SystemExit) as exc:
            rebuild.rebuild(model_dir)
        assert exc.value.code == 2


class TestRebuildMain:
    def _model_dir(self, tmp_path: Path) -> Path:
        model_dir = tmp_path / "openclaw" / "t" / "trajectories" / "opus"
        for n, ov in ((1, 0.4), (2, 0.8)):
            run_dir = model_dir / f"run_{n}"
            run_dir.mkdir(parents=True)
            _write_json(run_dir / "score.json", {"overall_score": ov})
        return model_dir

    def test_main_default_writes_new_json(self, rebuild, tmp_path, monkeypatch):
        model_dir = self._model_dir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["rebuild.py", str(model_dir)])
        rc = rebuild.main()
        assert rc == 0
        target = model_dir / "pass_summary_new.json"
        assert target.is_file()
        assert json.loads(target.read_text(encoding="utf-8"))["runs"] == 2
        # default must NOT clobber existing pass_summary.json
        assert not (model_dir / "pass_summary.json").exists()

    def test_main_in_place(self, rebuild, tmp_path, monkeypatch):
        model_dir = self._model_dir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["rebuild.py", str(model_dir), "--in-place"])
        rc = rebuild.main()
        assert rc == 0
        target = model_dir / "pass_summary.json"
        assert json.loads(target.read_text(encoding="utf-8"))["runs"] == 2

    def test_main_output_stdout(self, rebuild, tmp_path, monkeypatch, capsys):
        model_dir = self._model_dir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["rebuild.py", str(model_dir), "-o", "-"])
        rc = rebuild.main()
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["runs"] == 2

    def test_main_output_explicit_path(self, rebuild, tmp_path, monkeypatch):
        model_dir = self._model_dir(tmp_path)
        target = tmp_path / "custom.json"
        monkeypatch.setattr(sys, "argv", ["rebuild.py", str(model_dir), "-o", str(target)])
        rc = rebuild.main()
        assert rc == 0
        assert json.loads(target.read_text(encoding="utf-8"))["runs"] == 2

    def test_main_non_directory_errors_via_argparse(self, rebuild, tmp_path, monkeypatch):
        # ap.error() raises SystemExit(2).
        monkeypatch.setattr(sys, "argv", ["rebuild.py", str(tmp_path / "nope")])
        with pytest.raises(SystemExit) as exc:
            rebuild.main()
        assert exc.value.code == 2


# =========================================================================== #
# backfill_pass_summary.py
# =========================================================================== #
class TestBackfillHelpers:
    def test_finite_float(self, backfill):
        assert backfill._finite_float(1.5) == 1.5
        assert backfill._finite_float(True) is None
        assert backfill._finite_float(float("inf")) is None
        assert backfill._finite_float("x") is None

    def test_mean_or_none(self, backfill):
        assert backfill._mean_or_none([2.0, 4.0, None]) == 3.0
        assert backfill._mean_or_none([]) is None

    def test_load_json(self, backfill, tmp_path):
        assert backfill._load_json(tmp_path / "nope.json") is None
        p = tmp_path / "ok.json"
        _write_json(p, {"a": 1})
        assert backfill._load_json(p) == {"a": 1}


class TestBackfillCtrfTestResult:
    def test_per_test_list_preferred_over_summary(self, backfill, tmp_path):
        # per-test list is used when present (more accurate than summary).
        run_dir = tmp_path / "run_1"
        verifier = run_dir / "task_output" / "logs" / "verifier"
        _write_json(verifier / "ctrf.json", {
            "results": {
                "summary": {"tests": 999, "passed": 999, "overall_score": 0.5},
                "tests": [
                    {"status": "passed"}, {"status": "passed"},
                    {"status": "failed"}, {"status": "errored"},
                    {"status": "skipped"},
                ],
            }
        })
        out = backfill._ctrf_test_result(run_dir)
        assert out["tests_total"] == 5
        assert out["tests_passed"] == 2
        assert out["tests_failed"] == 1
        assert out["tests_errored"] == 1
        assert out["tests_skipped"] == 1
        assert out["reward"] == 0.5

    def test_overall_score_first_then_reward_txt_fallback(self, backfill, tmp_path):
        # overall_score-first precedence: summary.overall_score wins over reward.txt.
        run_dir = tmp_path / "run_1"
        verifier = run_dir / "task_output" / "logs" / "verifier"
        _write_json(verifier / "ctrf.json",
                    {"results": {"summary": {"tests": 1, "passed": 1, "overall_score": 0.9}}})
        (verifier / "reward.txt").write_text("0.1", encoding="utf-8")
        out = backfill._ctrf_test_result(run_dir)
        assert out["reward"] == 0.9

    def test_reward_txt_used_when_overall_score_absent(self, backfill, tmp_path):
        run_dir = tmp_path / "run_1"
        verifier = run_dir / "task_output" / "logs" / "verifier"
        _write_json(verifier / "ctrf.json",
                    {"results": {"summary": {"tests": 1, "passed": 1}}})
        (verifier / "reward.txt").write_text("0.7", encoding="utf-8")
        out = backfill._ctrf_test_result(run_dir)
        assert out["reward"] == 0.7

    def test_empty_test_list_falls_back_to_summary_counts(self, backfill, tmp_path):
        run_dir = tmp_path / "run_1"
        verifier = run_dir / "task_output" / "logs" / "verifier"
        _write_json(verifier / "ctrf.json", {
            "results": {
                "summary": {"tests": 4, "passed": 3, "failed": 1, "other": 0,
                            "skipped": 0, "overall_score": 0.75},
                "tests": [],
            }
        })
        out = backfill._ctrf_test_result(run_dir)
        assert out["tests_total"] == 4
        assert out["tests_passed"] == 3
        assert out["tests_failed"] == 1

    def test_missing_ctrf_all_zero(self, backfill, tmp_path):
        run_dir = tmp_path / "run_1"
        run_dir.mkdir()
        out = backfill._ctrf_test_result(run_dir)
        assert out["tests_total"] == 0
        assert out["reward"] is None


class TestBackfillEntry:
    def test_overall_score_first_for_rubric(self, backfill):
        # backfill uses rubric_based_reward first, then overall_score.
        entry = backfill._entry(1, {"overall_score": 0.5}, {})
        assert entry["rubric_reward"] == 0.5
        assert entry["rubric_weights_percentage"] == 50.0

    def test_rubric_based_reward_preferred(self, backfill):
        entry = backfill._entry(1, {"rubric_based_reward": 0.9, "overall_score": 0.1}, {})
        assert entry["rubric_reward"] == 0.9

    def test_combined_from_test_and_rubric(self, backfill):
        entry = backfill._entry(1, {"overall_score": 0.6},
                                {"tests_total": 2, "reward": 0.4})
        assert entry["test_reward"] == 0.4
        assert entry["combined_reward"] == pytest.approx(0.5)

    def test_empty_scores_authoritative_zero(self, backfill):
        entry = backfill._entry(1, {}, {})
        assert entry["combined_reward"] is None
        assert entry["reward"] == 0.0


class TestBackfillDoc:
    def test_doc_shape(self, backfill):
        runs = [
            backfill._entry(1, {"overall_score": 0.4}, {}),
            backfill._entry(2, {"overall_score": 0.8}, {}),
        ]
        doc = backfill._doc("opus", runs)
        assert doc["model"] == "opus"
        assert doc["runs"] == 2
        assert doc["average_reward"] == pytest.approx(0.6)
        assert doc["average_rubric_reward"] == pytest.approx(0.6)
        assert doc["average_rubric_weights_percentage"] == 60.0


class TestBackfillFindAndRebuild:
    def test_find_model_dirs_requires_trajectories_parent(self, backfill, tmp_path):
        # valid: .../trajectories/<model>/run_N
        good = tmp_path / "output" / "openclaw" / "t" / "trajectories" / "opus" / "run_1"
        good.mkdir(parents=True)
        # invalid: run_N whose parent's parent is not "trajectories"
        bad = tmp_path / "output" / "stray" / "run_1"
        bad.mkdir(parents=True)
        found = list(backfill._find_model_dirs(tmp_path))
        assert found == [good.parent]

    def test_find_model_dirs_dedups(self, backfill, tmp_path):
        base = tmp_path / "output" / "b" / "t" / "trajectories" / "opus"
        (base / "run_1").mkdir(parents=True)
        (base / "run_2").mkdir(parents=True)
        found = list(backfill._find_model_dirs(tmp_path))
        assert found == [base]

    def test_rebuild_model_dir_end_to_end(self, backfill, tmp_path):
        model_dir = tmp_path / "output" / "b" / "t" / "trajectories" / "opus"
        for n, ov in ((2, 0.8), (1, 0.4)):
            run_dir = model_dir / f"run_{n}"
            run_dir.mkdir(parents=True)
            _write_json(run_dir / "score.json", {"overall_score": ov})
        doc = backfill.rebuild_model_dir(model_dir)
        assert doc["runs"] == 2
        assert [r["run_index"] for r in doc["per_run"]] == [1, 2]
        assert doc["average_rubric_reward"] == pytest.approx(0.6)

    def test_rebuild_model_dir_no_runs_returns_none(self, backfill, tmp_path):
        model_dir = tmp_path / "empty"
        model_dir.mkdir()
        assert backfill.rebuild_model_dir(model_dir) is None


class TestBackfillMain:
    def _tree(self, tmp_path: Path) -> Path:
        root = tmp_path / "output"
        model_dir = root / "openclaw" / "t" / "trajectories" / "opus"
        run_dir = model_dir / "run_1"
        run_dir.mkdir(parents=True)
        _write_json(run_dir / "score.json", {"overall_score": 0.5})
        return root

    def test_main_writes_pass_summary(self, backfill, tmp_path, monkeypatch, capsys):
        root = self._tree(tmp_path)
        monkeypatch.setattr(sys, "argv", ["backfill.py", str(root)])
        rc = backfill.main()
        assert rc == 0
        target = root / "openclaw" / "t" / "trajectories" / "opus" / "pass_summary.json"
        assert target.is_file()
        assert json.loads(target.read_text(encoding="utf-8"))["runs"] == 1
        assert "WROTE" in capsys.readouterr().out

    def test_main_dry_run_does_not_write(self, backfill, tmp_path, monkeypatch, capsys):
        root = self._tree(tmp_path)
        monkeypatch.setattr(sys, "argv", ["backfill.py", str(root), "--dry-run"])
        rc = backfill.main()
        assert rc == 0
        target = root / "openclaw" / "t" / "trajectories" / "opus" / "pass_summary.json"
        assert not target.exists()
        assert "DRY" in capsys.readouterr().out

    def test_main_backend_filter_excludes(self, backfill, tmp_path, monkeypatch, capsys):
        root = self._tree(tmp_path)
        monkeypatch.setattr(sys, "argv", ["backfill.py", str(root), "--backend", "codex"])
        rc = backfill.main()
        assert rc == 0
        target = root / "openclaw" / "t" / "trajectories" / "opus" / "pass_summary.json"
        assert not target.exists()  # openclaw dir filtered out by /codex/ requirement

    def test_main_non_directory_root_returns_2(self, backfill, tmp_path, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["backfill.py", str(tmp_path / "nope")])
        rc = backfill.main()
        assert rc == 2
