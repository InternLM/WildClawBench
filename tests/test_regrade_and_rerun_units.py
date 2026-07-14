"""Unit coverage for the three offline re-grade / backfill scripts.

Modules under test (loaded by path because ``script/`` is not an importable
package — same technique as tests/test_repackage_bundle_ground_truth.py):

  * script/regrade.py        — rubric loading (incl. SystemExit on malformed
                               rubric), task-id derivation, results-dir pick,
                               score.json verbatim overwrite, usage.json merge.
  * script/rerun_tests.py    — test-suite discovery + verifier-artifact rewrite
                               (reward.txt / ctrf.json / *_result.json) with
                               execute_tests mocked; run/task iteration.
  * script/backfill_run_data.py — input<->output resolution, store-task build,
                               per-run backfill state machine, root discovery.

All heavy collaborators (grade_with_rubric, execute_tests, write_bundle,
load_task, docker, boto3, LLM judge) are monkeypatched. Nothing here touches
the network, docker, or AWS, and all temp data goes under pytest tmp_path.

Some assertions PIN CURRENT (possibly-defective) behaviour — see
SCORING_AUDIT_REPORT.md. Those are flagged inline.
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
# module loaders (load each script by path, like the repackager test does)
# --------------------------------------------------------------------------- #
def _load_script(basename: str, alias: str):
    path = _REPO_ROOT / "script" / basename
    assert path.exists(), f"script missing: {path}"
    spec = importlib.util.spec_from_file_location(alias, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def regrade_mod():
    return _load_script("regrade.py", "_test_regrade")


@pytest.fixture(scope="module")
def rerun_mod():
    return _load_script("rerun_tests.py", "_test_rerun_tests")


@pytest.fixture(scope="module")
def backfill_mod():
    return _load_script("backfill_run_data.py", "_test_backfill_run_data")


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #
def _mk_run_dir(root: Path, *, backend="openclaw", task="alice-croft",
                model="claude", run="run_1") -> Path:
    """Build output/<backend>/<task>/trajectories/<model>/run_N tree."""
    run_dir = root / backend / task / "trajectories" / model / run
    run_dir.mkdir(parents=True)
    return run_dir


# =========================================================================== #
# script/regrade.py
# =========================================================================== #
class TestRegradeTaskIdAndPaths:
    def test_derive_task_id_from_layout(self, regrade_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path, task="renata-voss")
        assert regrade_mod._derive_task_id(run_dir) == "renata-voss"

    def test_find_rubric_override_exists(self, regrade_mod, tmp_path):
        rb = tmp_path / "custom_rubric.json"
        rb.write_text("[]", encoding="utf-8")
        assert regrade_mod._find_rubric_path("anytask", rb) == rb

    def test_find_rubric_override_missing_raises_systemexit(self, regrade_mod, tmp_path):
        missing = tmp_path / "nope.json"
        with pytest.raises(SystemExit):
            regrade_mod._find_rubric_path("anytask", missing)

    def test_find_rubric_default_missing_raises_systemexit(self, regrade_mod):
        # A task id that does not exist under input/ -> default candidate missing.
        with pytest.raises(SystemExit):
            regrade_mod._find_rubric_path("definitely-not-a-real-task-zzz", None)

    def test_find_prompt_path_returns_none_when_absent(self, regrade_mod):
        assert regrade_mod._find_prompt_path("definitely-not-a-real-task-zzz") is None

    def test_derive_task_id_shallow_path_raises_systemexit(self, regrade_mod):
        # A path with < 3 parents -> parents[2] IndexError -> SystemExit.
        # Path("a/b").parents == [Path("a"), Path(".")]  (len 2).
        shallow = Path("a") / "b"
        with pytest.raises(SystemExit):
            regrade_mod._derive_task_id(shallow)


class TestRegradeLoadRubrics:
    def test_load_list_rubric(self, regrade_mod, tmp_path):
        p = tmp_path / "rubric.json"
        p.write_text(json.dumps([{"criterion": "does x", "weight": 5}]), encoding="utf-8")
        got = regrade_mod._load_rubrics(p)
        assert got == [{"criterion": "does x", "weight": 5}]

    def test_load_dict_wrapper_rubric(self, regrade_mod, tmp_path):
        p = tmp_path / "rubric.json"
        p.write_text(json.dumps({"rubrics": [{"criterion": "y", "weight": 3}]}), encoding="utf-8")
        got = regrade_mod._load_rubrics(p)
        assert got == [{"criterion": "y", "weight": 3}]

    def test_empty_list_raises_no_criteria(self, regrade_mod, tmp_path):
        p = tmp_path / "rubric.json"
        p.write_text("[]", encoding="utf-8")
        with pytest.raises(SystemExit):
            regrade_mod._load_rubrics(p)

    def test_dict_without_rubrics_key_raises_no_criteria(self, regrade_mod, tmp_path):
        # dict path with empty/absent "rubrics" -> [] -> "no rubric criteria".
        p = tmp_path / "rubric.json"
        p.write_text(json.dumps({"something_else": 1}), encoding="utf-8")
        with pytest.raises(SystemExit):
            regrade_mod._load_rubrics(p)

    def test_malformed_type_raises_systemexit(self, regrade_mod, tmp_path):
        # top-level JSON that is neither list nor dict (a bare string).
        p = tmp_path / "rubric.json"
        p.write_text(json.dumps("i am a string"), encoding="utf-8")
        with pytest.raises(SystemExit):
            regrade_mod._load_rubrics(p)


class TestRegradeTrajectoryAndResultsDir:
    def test_load_trajectory_missing_output_json_raises(self, regrade_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)
        with pytest.raises(SystemExit):
            regrade_mod._load_trajectory(run_dir)

    def test_load_trajectory_reads_output_json(self, regrade_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)
        (run_dir / "output.json").write_text(json.dumps({"messages": []}), encoding="utf-8")
        assert regrade_mod._load_trajectory(run_dir) == {"messages": []}

    def test_pick_results_dir_prefers_nonempty_artifacts(self, regrade_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)
        artifacts = run_dir / "task_output" / "artifacts"
        artifacts.mkdir(parents=True)
        (artifacts / "solution.py").write_text("print('hi')", encoding="utf-8")
        assert regrade_mod._pick_results_dir(run_dir) == artifacts

    def test_pick_results_dir_falls_back_when_artifacts_empty(self, regrade_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)
        (run_dir / "task_output" / "artifacts").mkdir(parents=True)  # empty
        assert regrade_mod._pick_results_dir(run_dir) == (
            run_dir / "task_output" / "workspace_full"
        )

    def test_pick_results_dir_falls_back_when_artifacts_absent(self, regrade_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)
        assert regrade_mod._pick_results_dir(run_dir) == (
            run_dir / "task_output" / "workspace_full"
        )


class TestRegradeScoreOverwrite:
    def test_regrade_writes_score_json_verbatim(self, regrade_mod, tmp_path, monkeypatch):
        run_dir = _mk_run_dir(tmp_path)
        (run_dir / "output.json").write_text(json.dumps({"messages": []}), encoding="utf-8")

        rubric = tmp_path / "rubric.json"
        rubric.write_text(json.dumps([{"criterion": "c", "weight": 5}]), encoding="utf-8")

        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # score.json is overwritten VERBATIM with grade_with_rubric()'s return.
        # A pre-existing "combined_reward" key in the old score.json is dropped
        # because the new dict has no such key and no merge is performed.
        (run_dir / "score.json").write_text(
            json.dumps({"combined_reward": 0.9, "stale": "gone"}), encoding="utf-8"
        )

        fake_scores = {
            "overall_score": 0.42,
            "criteria_total": 1,
            "criteria_passed": 1,
            "usage": {"cost_usd": 0.01},
        }
        captured = {}

        def fake_grade(rubrics, task_description, results_dir, **kw):
            captured["rubrics"] = rubrics
            captured["results_dir"] = results_dir
            captured["use_council"] = kw.get("use_council")
            return dict(fake_scores)

        monkeypatch.setattr(regrade_mod, "grade_with_rubric", fake_grade)

        out = regrade_mod.regrade(run_dir, rubric_override=rubric)

        assert out["overall_score"] == 0.42
        assert captured["use_council"] is True  # council-only script
        assert captured["rubrics"] == [{"criterion": "c", "weight": 5}]

        on_disk = json.loads((run_dir / "score.json").read_text(encoding="utf-8"))
        assert on_disk["overall_score"] == 0.42
        # verbatim overwrite: old keys are NOT preserved / merged.
        assert "combined_reward" not in on_disk
        assert "stale" not in on_disk

    def test_regrade_reads_prompt_into_task_description(self, regrade_mod, tmp_path, monkeypatch):
        run_dir = _mk_run_dir(tmp_path)
        (run_dir / "output.json").write_text(json.dumps({"messages": []}), encoding="utf-8")
        rubric = tmp_path / "rubric.json"
        rubric.write_text(json.dumps([{"criterion": "c", "weight": 1}]), encoding="utf-8")

        prompt = tmp_path / "prompt.txt"
        prompt.write_text("  the task question  \n", encoding="utf-8")
        # Force the prompt path so the read-and-strip branch executes.
        monkeypatch.setattr(regrade_mod, "_find_prompt_path", lambda task_id: prompt)

        seen = {}

        def fake_grade(rubrics, task_description, results_dir, **kw):
            seen["desc"] = task_description
            return {"overall_score": 1.0}

        monkeypatch.setattr(regrade_mod, "grade_with_rubric", fake_grade)
        regrade_mod.regrade(run_dir, rubric_override=rubric)
        assert seen["desc"] == "the task question"  # stripped

    def test_regrade_missing_run_dir_raises(self, regrade_mod, tmp_path):
        with pytest.raises(SystemExit):
            regrade_mod.regrade(tmp_path / "does" / "not" / "exist")


class TestRegradeUpdateUsageJson:
    def test_no_usage_json_is_skipped(self, regrade_mod, tmp_path, capsys):
        run_dir = _mk_run_dir(tmp_path)
        # No usage.json present -> early return, no crash.
        regrade_mod._update_usage_json(run_dir, {"usage": {"cost_usd": 1.0}})
        assert not (run_dir / "usage.json").exists()

    def test_malformed_usage_json_is_skipped(self, regrade_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)
        (run_dir / "usage.json").write_text("{not valid json", encoding="utf-8")
        # Should swallow the JSONDecodeError and leave the file as-is.
        regrade_mod._update_usage_json(run_dir, {"usage": {"cost_usd": 1.0}})
        assert (run_dir / "usage.json").read_text(encoding="utf-8") == "{not valid json"

    def test_usage_json_merges_judge_source_and_recomputes(self, regrade_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)
        usage = {
            "cost_usd": 0.5,
            "input_tokens": 10,
            "output_tokens": 5,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 15,
            "request_count": 1,
            "sources": {"agent": {
                "input_tokens": 10, "output_tokens": 5,
                "cache_read_tokens": 0, "cache_write_tokens": 0,
                "total_tokens": 15, "request_count": 1, "cost_usd": 0.5,
            }},
            "extra_preserved": "keepme",
        }
        (run_dir / "usage.json").write_text(json.dumps(usage), encoding="utf-8")

        scores = {"usage": {
            "input_tokens": 2, "output_tokens": 3,
            "cache_read_tokens": 0, "cache_write_tokens": 0,
            "total_tokens": 5, "request_count": 1, "cost_usd": 0.25,
        }}
        regrade_mod._update_usage_json(run_dir, scores)

        out = json.loads((run_dir / "usage.json").read_text(encoding="utf-8"))
        # judge source recorded.
        assert out["sources"]["judge"]["cost_usd"] == 0.25
        assert out["sources"]["agent"]["input_tokens"] == 10
        # combined recomputed across agent + judge.
        assert out["input_tokens"] == 12
        assert out["output_tokens"] == 8
        assert out["total_tokens"] == 20
        assert out["request_count"] == 2
        assert out["cost_usd"] == pytest.approx(0.75)
        # unrelated top-level keys carried through verbatim.
        assert out["extra_preserved"] == "keepme"


class TestRegradePrintSummary:
    def test_print_summary_error_path(self, regrade_mod, capsys):
        regrade_mod._print_summary({"error": "judge blew up"})
        out = capsys.readouterr().out
        assert "FAILED" in out and "judge blew up" in out

    def test_print_summary_council_block(self, regrade_mod, capsys):
        regrade_mod._print_summary({
            "overall_score": 0.8,
            "criteria_total": 2, "criteria_passed": 1, "criteria_failed": 1,
            "judge_model": "sonnet",
            "judge_council": {
                "surviving": [{"model": "sonnet"}, {"model": "glm"}],
                "failed": [{"model": "kimi", "error": "timeout boom"}],
            },
        })
        out = capsys.readouterr().out
        assert "overall_score" in out
        assert "council surviving=2/3" in out
        assert "kimi" in out and "timeout boom" in out

    def test_print_summary_falls_back_to_tests_keys(self, regrade_mod, capsys):
        # When criteria_* absent, summary reads deprecated tests_* aliases.
        regrade_mod._print_summary({
            "overall_score": 1.0,
            "tests_total": 3, "tests_passed": 3, "tests_failed": 0,
        })
        out = capsys.readouterr().out
        assert "total=3" in out and "passed=3" in out


class TestRegradeMain:
    def test_main_returns_zero_on_success(self, regrade_mod, tmp_path, monkeypatch):
        run_dir = _mk_run_dir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["regrade.py", "--run", str(run_dir), "--quiet"])
        monkeypatch.setattr(regrade_mod, "regrade", lambda rd, rubric_override=None: {"overall_score": 1.0})
        assert regrade_mod.main() == 0

    def test_main_returns_one_on_error(self, regrade_mod, tmp_path, monkeypatch):
        run_dir = _mk_run_dir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["regrade.py", "--run", str(run_dir)])
        monkeypatch.setattr(regrade_mod, "regrade", lambda rd, rubric_override=None: {"error": "x"})
        # Not --quiet: also exercises _print_summary's error branch.
        assert regrade_mod.main() == 1


# =========================================================================== #
# script/rerun_tests.py
# =========================================================================== #
class TestRerunFindTests:
    def test_find_tests_in_data_tests(self, rerun_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path, task="mytask")
        data_tests = run_dir.parents[2] / "data" / "tests"
        data_tests.mkdir(parents=True)
        (data_tests / "test_outputs.py").write_text("def test_x(): pass", encoding="utf-8")
        (data_tests / "test_weights.json").write_text("{}", encoding="utf-8")

        code, weights = rerun_mod._find_tests(run_dir)
        assert code == data_tests / "test_outputs.py"
        assert weights == data_tests / "test_weights.json"

    def test_find_tests_accepts_singular_test_output_py(self, rerun_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path, task="mytask")
        data_tests = run_dir.parents[2] / "data" / "tests"
        data_tests.mkdir(parents=True)
        # note singular filename fallback
        (data_tests / "test_output.py").write_text("def test_x(): pass", encoding="utf-8")
        (data_tests / "test_weights.json").write_text("{}", encoding="utf-8")

        code, weights = rerun_mod._find_tests(run_dir)
        assert code == data_tests / "test_output.py"
        assert weights == data_tests / "test_weights.json"

    def test_find_tests_none_when_missing(self, rerun_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path, task="no-such-task-anywhere-zzz")
        code, weights = rerun_mod._find_tests(run_dir)
        assert code is None and weights is None

    def test_find_tests_none_when_weights_missing(self, rerun_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path, task="mytask2")
        data_tests = run_dir.parents[2] / "data" / "tests"
        data_tests.mkdir(parents=True)
        (data_tests / "test_outputs.py").write_text("def test_x(): pass", encoding="utf-8")
        # no test_weights.json -> considered not found
        code, weights = rerun_mod._find_tests(run_dir)
        assert code is None and weights is None


class TestRerunLoadEnv:
    def test_load_env_from_json_and_flags(self, rerun_mod, tmp_path):
        j = tmp_path / "env.json"
        j.write_text(json.dumps({"A_URL": "http://a", "N": 5}), encoding="utf-8")

        class Args:
            env_json = str(j)
            env = ["B_URL=http://b", "malformed_no_equals"]

        env = rerun_mod._load_env(Args())
        assert env["A_URL"] == "http://a"
        assert env["N"] == "5"           # values are stringified
        assert env["B_URL"] == "http://b"
        assert "malformed_no_equals" not in env  # entries without '=' are ignored

    def test_load_env_empty(self, rerun_mod):
        class Args:
            env_json = None
            env = None
        assert rerun_mod._load_env(Args()) == {}


class TestRerunRegradeRun:
    def _args(self, **over):
        class Args:
            env_json = None
            env = None
            network = None
            image = "img:test"
            timeout = 600
        a = Args()
        for k, v in over.items():
            setattr(a, k, v)
        return a

    def test_skip_when_no_workspace_full(self, rerun_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)
        assert rerun_mod._regrade_run(run_dir, self._args()) is None

    def test_skip_when_no_tests(self, rerun_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path, task="no-tests-task-zzz")
        (run_dir / "task_output" / "workspace_full").mkdir(parents=True)
        assert rerun_mod._regrade_run(run_dir, self._args()) is None

    def test_writes_verifier_artifacts(self, rerun_mod, tmp_path, monkeypatch):
        run_dir = _mk_run_dir(tmp_path, task="hastests")
        (run_dir / "task_output" / "workspace_full").mkdir(parents=True)
        data_tests = run_dir.parents[2] / "data" / "tests"
        data_tests.mkdir(parents=True)
        (data_tests / "test_outputs.py").write_text("def test_x(): pass", encoding="utf-8")
        (data_tests / "test_weights.json").write_text(json.dumps({"test_x": 5}), encoding="utf-8")

        te_result = {
            "reward": 0.75,
            "tests_total": 4,
            "tests_passed": 3,
            "tests_failed": 1,
            "tests_errored": 0,
            "tests_skipped": 0,
            "test_scores": json.dumps({"test_x": "passed"}),
            "test_function_outputs": {"test_x": "ok"},
            "test_output": "pytest ran fine",
            "error": None,
        }
        captured = {}

        def fake_execute(**kw):
            captured.update(kw)
            return dict(te_result)

        monkeypatch.setattr(rerun_mod, "execute_tests", fake_execute)

        out = rerun_mod._regrade_run(run_dir, self._args(image="myimg", timeout=42))
        assert out is not None and out["reward"] == 0.75

        # execute_tests got the right wiring.
        assert captured["image"] == "myimg"
        assert captured["timeout"] == 42
        assert captured["network"] is None
        assert captured["workspace_dir"] == run_dir / "task_output" / "workspace_full"

        vdir = run_dir / "task_output" / "logs" / "verifier"
        assert (vdir / "reward.txt").read_text(encoding="utf-8") == "0.750000\n"
        ctrf = json.loads((vdir / "ctrf.json").read_text(encoding="utf-8"))
        assert isinstance(ctrf, dict) and "results" in ctrf
        # function outputs written (dict -> json-serialized).
        fn = json.loads((vdir / "test_function_outputs.json").read_text(encoding="utf-8"))
        assert fn == {"test_x": "ok"}
        assert (vdir / "test_output.log").read_text(encoding="utf-8") == "pytest ran fine"

        # standalone snapshot excludes the big test_output blob and never
        # clobbers score.json (which we never created here).
        snap = json.loads((run_dir / "regrade_test_result.json").read_text(encoding="utf-8"))
        assert "test_output" not in snap
        assert snap["reward"] == 0.75
        assert not (run_dir / "score.json").exists()

    def test_string_function_outputs_written_asis(self, rerun_mod, tmp_path, monkeypatch):
        run_dir = _mk_run_dir(tmp_path, task="hasteststr")
        (run_dir / "task_output" / "workspace_full").mkdir(parents=True)
        data_tests = run_dir.parents[2] / "data" / "tests"
        data_tests.mkdir(parents=True)
        (data_tests / "test_outputs.py").write_text("x", encoding="utf-8")
        (data_tests / "test_weights.json").write_text("{}", encoding="utf-8")

        def fake_execute(**kw):
            return {
                "reward": 0.0, "tests_total": 0, "tests_passed": 0,
                "tests_failed": 0, "tests_errored": 0,
                "test_function_outputs": '{"already":"string"}',
                "error": "boom",  # tests_total==0 + error -> printed
            }

        monkeypatch.setattr(rerun_mod, "execute_tests", fake_execute)
        rerun_mod._regrade_run(run_dir, self._args())
        fn = (run_dir / "task_output" / "logs" / "verifier"
              / "test_function_outputs.json").read_text(encoding="utf-8")
        assert fn == '{"already":"string"}'


class TestRerunIterRuns:
    def test_iter_runs_single(self, rerun_mod, tmp_path):
        run_dir = _mk_run_dir(tmp_path)

        class Args:
            run = str(run_dir)
            task = None
            latest = False
        got = rerun_mod._iter_runs(Args())
        assert got == [run_dir.resolve()]

    def test_iter_runs_task_all(self, rerun_mod, tmp_path):
        task_root = tmp_path / "openclaw" / "sometask"
        for m in ("modelA",):
            for r in ("run_1", "run_2"):
                (task_root / "trajectories" / m / r).mkdir(parents=True)

        class Args:
            run = None
            task = str(task_root)
            latest = False
        got = rerun_mod._iter_runs(Args())
        names = sorted(p.name for p in got)
        assert names == ["run_1", "run_2"]

    def test_iter_runs_task_latest_only(self, rerun_mod, tmp_path):
        task_root = tmp_path / "openclaw" / "sometask2"
        for r in ("run_1", "run_2", "run_3"):
            (task_root / "trajectories" / "modelA" / r).mkdir(parents=True)

        class Args:
            run = None
            task = str(task_root)
            latest = True
        got = rerun_mod._iter_runs(Args())
        assert [p.name for p in got] == ["run_3"]


class TestRerunMain:
    def test_main_no_runs_returns_2(self, rerun_mod, tmp_path, monkeypatch):
        empty_task = tmp_path / "openclaw" / "emptytask"
        (empty_task / "trajectories").mkdir(parents=True)
        monkeypatch.setattr(sys, "argv", ["rerun_tests.py", "--task", str(empty_task)])
        assert rerun_mod.main() == 2

    def test_main_runs_and_reports(self, rerun_mod, tmp_path, monkeypatch, capsys):
        run_dir = _mk_run_dir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["rerun_tests.py", "--run", str(run_dir)])
        monkeypatch.setattr(rerun_mod, "_regrade_run", lambda rd, args: {"reward": 0.5})
        rc = rerun_mod.main()
        assert rc == 0
        out = capsys.readouterr().out
        assert "mean reward=0.5000" in out

    def test_main_all_skipped_no_mean(self, rerun_mod, tmp_path, monkeypatch, capsys):
        run_dir = _mk_run_dir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["rerun_tests.py", "--run", str(run_dir)])
        monkeypatch.setattr(rerun_mod, "_regrade_run", lambda rd, args: None)
        rc = rerun_mod.main()
        assert rc == 0
        assert "mean reward" not in capsys.readouterr().out


# =========================================================================== #
# script/backfill_run_data.py
# =========================================================================== #
class TestBackfillResolveInputDir:
    def test_none_when_input_root_absent(self, backfill_mod, tmp_path):
        assert backfill_mod._resolve_input_dir(tmp_path / "nope", tmp_path / "out") is None

    def test_single_persona_core_match(self, backfill_mod, tmp_path):
        input_root = tmp_path / "input"
        (input_root / "barbara-kidd-1259abcd").mkdir(parents=True)
        out_task = tmp_path / "out" / "barbara-kidd-73c78b73"
        out_task.mkdir(parents=True)
        got = backfill_mod._resolve_input_dir(input_root, out_task)
        assert got == input_root / "barbara-kidd-1259abcd"

    def test_no_match_returns_none(self, backfill_mod, tmp_path):
        input_root = tmp_path / "input"
        (input_root / "totally-different-name").mkdir(parents=True)
        out_task = tmp_path / "out" / "barbara-kidd-73c78b73"
        out_task.mkdir(parents=True)
        assert backfill_mod._resolve_input_dir(input_root, out_task) is None

    def test_disambiguate_by_prompt_text(self, backfill_mod, tmp_path):
        input_root = tmp_path / "input"
        a = input_root / "barbara-kidd-aaaaaaaa"
        b = input_root / "barbara-kidd-bbbbbbbb"
        a.mkdir(parents=True)
        b.mkdir(parents=True)
        (a / "prompt.txt").write_text("WRONG prompt", encoding="utf-8")
        (b / "prompt.txt").write_text("the RIGHT prompt", encoding="utf-8")

        out_task = tmp_path / "out" / "barbara-kidd-73c78b73"
        out_task.mkdir(parents=True)
        (out_task / "prompt.txt").write_text("the RIGHT prompt", encoding="utf-8")

        got = backfill_mod._resolve_input_dir(input_root, out_task)
        assert got == b

    def test_ambiguous_without_prompt_is_deterministic(self, backfill_mod, tmp_path):
        input_root = tmp_path / "input"
        (input_root / "barbara-kidd-bbbbbbbb").mkdir(parents=True)
        (input_root / "barbara-kidd-aaaaaaaa").mkdir(parents=True)
        out_task = tmp_path / "out" / "barbara-kidd-73c78b73"
        out_task.mkdir(parents=True)
        # No prompt.txt anywhere -> sorted deterministically; both share the
        # exact persona core, so the alphabetically-first name wins.
        got = backfill_mod._resolve_input_dir(input_root, out_task)
        assert got == input_root / "barbara-kidd-aaaaaaaa"

    def test_none_when_out_name_has_no_persona_core(self, backfill_mod, tmp_path):
        # An all-numeric / uuid-only dir name reduces to an empty core -> None.
        input_root = tmp_path / "input"
        (input_root / "barbara-kidd").mkdir(parents=True)
        out_task = tmp_path / "out" / "12345678"
        out_task.mkdir(parents=True)
        assert backfill_mod._resolve_input_dir(input_root, out_task) is None

    def test_prompt_match_narrows_to_two_then_sorts(self, backfill_mod, tmp_path):
        # Two candidates share the exact prompt text -> exact has len 2, so the
        # code sets cands = exact and falls through to the deterministic sort.
        input_root = tmp_path / "input"
        b = input_root / "barbara-kidd-bbbbbbbb"
        a = input_root / "barbara-kidd-aaaaaaaa"
        c = input_root / "barbara-kidd-cccccccc"
        for d in (b, a, c):
            d.mkdir(parents=True)
        (a / "prompt.txt").write_text("shared", encoding="utf-8")
        (b / "prompt.txt").write_text("shared", encoding="utf-8")
        (c / "prompt.txt").write_text("DIFFERENT", encoding="utf-8")

        out_task = tmp_path / "out" / "barbara-kidd-73c78b73"
        out_task.mkdir(parents=True)
        (out_task / "prompt.txt").write_text("shared", encoding="utf-8")

        got = backfill_mod._resolve_input_dir(input_root, out_task)
        # a and b matched the prompt; alphabetically-first among them wins.
        assert got == a


class TestBackfillBuildStoreTask:
    def test_build_store_task_maps_fields(self, backfill_mod):
        task = {
            "task_id": "t1",
            "persona": "p",
            "initial_prompt": "go",
            "task_type": "coding",
            "difficulty": "hard",
            "l1": "L1", "l2": "L2",
            "rubrics": [{"criterion": "c"}],
            "required_apis": ["quickbooks-api"],
            "distractor_apis": ["stripe-api"],
        }
        st = backfill_mod._build_store_task(task)
        assert st.id == "t1" and st.task_id == "t1"
        assert st.initial_prompt == "go"
        assert json.loads(st.rubrics_json) == [{"criterion": "c"}]
        assert st.extra["required_apis"] == ["quickbooks-api"]
        assert st.extra["distractor_apis"] == ["stripe-api"]

    def test_build_store_task_prompt_fallback(self, backfill_mod):
        # initial_prompt missing -> falls back to "prompt"; None-y fields -> "".
        task = {"task_id": "t2", "prompt": "fallback prompt"}
        st = backfill_mod._build_store_task(task)
        assert st.initial_prompt == "fallback prompt"
        assert st.persona == ""
        assert st.extra["required_apis"] == []


class TestBackfillIterOutputTaskDirs:
    def test_backend_named_root(self, backfill_mod, tmp_path):
        backend = tmp_path / "openclaw"
        t1 = backend / "task-a"
        (t1 / "trajectories").mkdir(parents=True)
        (backend / "task-b").mkdir(parents=True)  # no trajectories -> skipped
        got = list(backfill_mod._iter_output_task_dirs(backend))
        assert got == [t1]

    def test_parent_output_root_with_backend_subdir(self, backfill_mod, tmp_path):
        out = tmp_path / "output"
        t1 = out / "openclaw" / "task-a"
        (t1 / "trajectories").mkdir(parents=True)
        got = list(backfill_mod._iter_output_task_dirs(out))
        assert got == [t1]

    def test_flat_output_root(self, backfill_mod, tmp_path):
        # No backend subdirs -> treated as a flat dir of task dirs.
        out = tmp_path / "flatout"
        t1 = out / "task-a"
        (t1 / "trajectories").mkdir(parents=True)
        got = list(backfill_mod._iter_output_task_dirs(out))
        assert got == [t1]

    def test_backend_named_root_that_does_not_exist_yields_nothing(self, backfill_mod, tmp_path):
        # Name matches a backend but the dir is absent -> the loop's
        # `not backend_dir.is_dir(): continue` guard skips it.
        missing = tmp_path / "openclaw"  # never created
        assert list(backfill_mod._iter_output_task_dirs(missing)) == []


class TestBackfillDiscoverRoots:
    def test_explicit_roots(self, backfill_mod):
        class Args:
            output_root = "/some/out"
            input_root = "/some/in"
            temp_dirs = []
        pairs = backfill_mod._discover_roots(Args())
        assert pairs == [(Path("/some/out"), Path("/some/in"))]

    def test_temp_dirs_with_output_and_input(self, backfill_mod, tmp_path):
        temp = tmp_path / "temp"
        (temp / "output").mkdir(parents=True)
        (temp / "input").mkdir(parents=True)

        class Args:
            output_root = None
            input_root = None
            temp_dirs = [str(temp)]
        pairs = backfill_mod._discover_roots(Args())
        assert pairs == [(temp / "output", temp / "input")]

    def test_temp_dir_missing_subdirs_skipped(self, backfill_mod, tmp_path, capsys):
        temp = tmp_path / "temp"
        temp.mkdir()  # no output/ or input/

        class Args:
            output_root = None
            input_root = None
            temp_dirs = [str(temp)]
        pairs = backfill_mod._discover_roots(Args())
        assert pairs == []
        assert "missing output/ or input/" in capsys.readouterr().err


class TestBackfillOne:
    def _out_task(self, tmp_path):
        d = tmp_path / "out" / "barbara-kidd-73c78b73"
        (d / "trajectories").mkdir(parents=True)
        return d

    def test_skip_when_env_exists_and_no_force(self, backfill_mod, tmp_path):
        out_task = self._out_task(tmp_path)
        env_dir = out_task / "data" / "environment"
        env_dir.mkdir(parents=True)
        (env_dir / "something-api").mkdir()
        res = backfill_mod.backfill_one(
            out_task, tmp_path / "input", augment=None,
            force=False, dry_run=False, verbose=False)
        assert res == "skip"

    def test_nomatch_when_no_input_dir(self, backfill_mod, tmp_path):
        out_task = self._out_task(tmp_path)
        input_root = tmp_path / "input"
        input_root.mkdir()  # empty -> no match
        res = backfill_mod.backfill_one(
            out_task, input_root, augment=None,
            force=False, dry_run=False, verbose=False)
        assert res == "nomatch"

    def test_dry_run_reports_done_without_writing(self, backfill_mod, tmp_path, capsys):
        out_task = self._out_task(tmp_path)
        input_root = tmp_path / "input"
        (input_root / "barbara-kidd-1259abcd").mkdir(parents=True)
        res = backfill_mod.backfill_one(
            out_task, input_root, augment=None,
            force=False, dry_run=True, verbose=True)
        assert res == "done"
        assert not (out_task / "data").exists()
        assert "WOULD backfill" in capsys.readouterr().out

    def test_done_calls_write_bundle(self, backfill_mod, tmp_path, monkeypatch):
        out_task = self._out_task(tmp_path)
        input_root = tmp_path / "input"
        (input_root / "barbara-kidd-1259abcd").mkdir(parents=True)

        # Stub every heavy collaborator on the loaded module.
        monkeypatch.setattr(backfill_mod.Config, "from_env",
                            classmethod(lambda cls: object()))
        monkeypatch.setattr(backfill_mod, "load_task",
                            lambda d: {"task_id": "bk", "initial_prompt": "go"})

        wb_calls = {}

        def fake_write_bundle(**kw):
            wb_calls.update(kw)

        monkeypatch.setattr(backfill_mod, "write_bundle", fake_write_bundle)
        monkeypatch.setattr(backfill_mod, "Store", lambda path: object())

        aug_calls = []

        def fake_augment(task, config, mock_env):
            aug_calls.append((task, mock_env))
            task["required_apis"] = ["a-api"]
            task["distractor_apis"] = []

        res = backfill_mod.backfill_one(
            out_task, input_root, augment=fake_augment,
            force=False, dry_run=False, verbose=True)
        assert res == "done"
        assert aug_calls  # augmenter was invoked
        assert wb_calls["out_dir"] == out_task
        assert wb_calls["trajectories_by_model"] is None  # leaves trajectories/ alone
        # store-task carried the resolved required api.
        assert wb_calls["task"].extra["required_apis"] == ["a-api"]

    def test_fail_when_collaborator_raises(self, backfill_mod, tmp_path, monkeypatch, capsys):
        out_task = self._out_task(tmp_path)
        input_root = tmp_path / "input"
        (input_root / "barbara-kidd-1259abcd").mkdir(parents=True)

        monkeypatch.setattr(backfill_mod.Config, "from_env",
                            classmethod(lambda cls: object()))

        def boom(_d):
            raise RuntimeError("kaboom")

        monkeypatch.setattr(backfill_mod, "load_task", boom)
        res = backfill_mod.backfill_one(
            out_task, input_root, augment=lambda *a, **k: None,
            force=False, dry_run=False, verbose=True)
        assert res == "fail"
        assert "backfill FAILED: kaboom" in capsys.readouterr().err


class TestBackfillMain:
    def test_main_errors_when_only_one_root_given(self, backfill_mod):
        with pytest.raises(SystemExit):
            backfill_mod.main(["--output-root", "/x"])

    def test_main_errors_when_nothing_to_do(self, backfill_mod):
        with pytest.raises(SystemExit):
            backfill_mod.main([])

    def test_main_dry_run_summary(self, backfill_mod, tmp_path, monkeypatch, capsys):
        temp = tmp_path / "temp"
        out = temp / "output" / "openclaw" / "barbara-kidd-73c78b73"
        (out / "trajectories").mkdir(parents=True)
        inp = temp / "input"
        (inp / "barbara-kidd-1259abcd").mkdir(parents=True)

        rc = backfill_mod.main([str(temp), "--dry-run"])
        assert rc == 0
        report = capsys.readouterr().out
        assert "backfill summary" in report
        assert "backfilled=1" in report

    def test_main_returns_one_on_failure(self, backfill_mod, tmp_path, monkeypatch):
        temp = tmp_path / "temp"
        out = temp / "output" / "openclaw" / "barbara-kidd-73c78b73"
        (out / "trajectories").mkdir(parents=True)
        inp = temp / "input"
        (inp / "barbara-kidd-1259abcd").mkdir(parents=True)

        # dry_run False path needs an augmenter; force fail via load_task.
        monkeypatch.setattr(backfill_mod, "_load_augmenter", lambda: (lambda *a, **k: None))
        monkeypatch.setattr(backfill_mod.Config, "from_env",
                            classmethod(lambda cls: object()))

        def boom(_d):
            raise RuntimeError("nope")

        monkeypatch.setattr(backfill_mod, "load_task", boom)
        rc = backfill_mod.main([str(temp)])
        assert rc == 1
