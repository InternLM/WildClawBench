"""Unit coverage for src/utils/test_executor.py BEYOND _compute_reward's
signed-range contract (that is already covered by tests/test_signed_reward.py —
this file deliberately does not duplicate it).

Focus areas (per the audit brief):
  * execute_tests() container-output parsing: subprocess.run is mocked to emit a
    realistic runner stdout carrying the JSON results block the in-container
    runner prints; we assert the results/test_scores/reward/return-dict assembly.
  * test_weights.json loading edge cases: corrupt JSON and string-typed weights.
  * pos_total<=0 fallback via _compute_reward: all-negative weights.
  * skipped-test exclusion from the pass/total denominator.
  * the returned "CTRF-consumer" dict key shape.
  * _RUNNER_SCRIPT static sanity (compiles + carries SIGALRM/discovery markers).

Several assertions PIN CURRENT (arguably buggy) BEHAVIOR rather than the
intended behavior; those are called out inline with the
"# NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md" marker per the
brief. If a pinned test breaks, the underlying behavior changed on purpose and
the test — not the source — should be revisited.

These tests run fully OFFLINE and deterministically: subprocess.run is
monkeypatched, no docker/network is touched, and all temp data goes to tmp_path.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import test_executor  # noqa: E402
from src.utils.test_executor import (  # noqa: E402
    _RUNNER_SCRIPT,
    _compute_reward,
    execute_tests,
)


# ---------------------------------------------------------------------------
# Fake subprocess plumbing (offline; no container ever spawned)
# ---------------------------------------------------------------------------


class _FakeCompleted:
    """Stand-in for subprocess.CompletedProcess."""

    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _runner_stdout(payload: dict, *, prelude: str = "", stderr_noise: str = "") -> str:
    """Compose a realistic runner stdout: some human prelude lines, then the
    single-line JSON payload the in-container runner prints via
    print(json.dumps(out)). The parser scans lines in reverse for the first
    line that both startswith('{') and endswith('}') and json-loads."""
    body = json.dumps(payload)  # single line — matches print(json.dumps(out))
    lines = []
    if prelude:
        lines.append(prelude)
    lines.append(body)
    if stderr_noise:
        lines.append(stderr_noise)
    return "\n".join(lines) + "\n"


@pytest.fixture
def fake_run(monkeypatch):
    """Monkeypatch subprocess.run to return a caller-supplied CompletedProcess
    and record the argv it was handed. Set fake_run.completed before invoking
    execute_tests; inspect fake_run.calls afterwards."""

    state = {"completed": _FakeCompleted(), "calls": []}

    def _run(cmd, *args, **kwargs):
        state["calls"].append(list(cmd))
        return state["completed"]

    monkeypatch.setattr(subprocess, "run", _run)
    return state


def _mk_ws(tmp_path: Path) -> Path:
    ws = tmp_path / "ws"
    ws.mkdir()
    return ws


_TC = "def test_ok():\n    assert True\n"


# ---------------------------------------------------------------------------
# Section A — execute_tests() happy-path container-output parsing
# ---------------------------------------------------------------------------


class TestExecuteTestsParsing:
    def test_parses_runner_json_and_assembles_counts(self, tmp_path, fake_run):
        payload = {
            "import_error": None,
            "collected": 3,
            "results": {
                "t::TestA::test_pass": {"status": "passed"},
                "t::TestA::test_fail": {"status": "failed", "error": "AssertionError: x"},
                "t::test_err": {"status": "errored", "error": "RuntimeError: boom"},
            },
        }
        fake_run["completed"] = _FakeCompleted(
            stdout=_runner_stdout(payload, prelude="running test_pass...")
        )
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["tests_passed"] == 1
        assert res["tests_failed"] == 1
        assert res["tests_errored"] == 1
        # tests_total = passed+failed+errored (skipped intentionally excluded).
        assert res["tests_total"] == 3
        assert res["error"] == ""
        scores = json.loads(res["test_scores"])
        assert scores["t::TestA::test_pass"] == "passed"
        assert scores["t::test_err"] == "errored"

    def test_reward_uses_weights_and_qualified_key_matching(self, tmp_path, fake_run):
        # Weight given as a bare name resolves against the bare tail of the
        # fully-qualified result key ("t::TestA::test_pass" -> "test_pass").
        payload = {
            "results": {
                "t::TestA::test_pass": {"status": "passed"},
                "t::TestA::test_other": {"status": "failed"},
            }
        }
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        weights = {"test_pass": 5, "test_other": 5}
        res = execute_tests(
            test_code=_TC,
            test_weights_json=json.dumps(weights),
            workspace_dir=_mk_ws(tmp_path),
        )
        # one of two equally-weighted positive tests passed -> 5/10 = 0.5.
        assert res["reward"] == 0.5

    def test_json_payload_line_redacted_from_test_output(self, tmp_path, fake_run):
        payload = {"results": {"t::test_a": {"status": "passed"}}}
        stdout = _runner_stdout(payload, prelude="human log line")
        fake_run["completed"] = _FakeCompleted(stdout=stdout)
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        out = res["test_output"]
        # The raw JSON payload line is scrubbed from the persisted, human-facing
        # log and replaced with a placeholder; the prelude survives.
        assert "human log line" in out
        assert "[runner JSON payload omitted" in out
        assert json.dumps(payload) not in out

    def test_stderr_appended_to_test_output(self, tmp_path, fake_run):
        payload = {"results": {"t::test_a": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(
            stdout=_runner_stdout(payload), stderr="a warning on stderr"
        )
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert "[stderr]" in res["test_output"]
        assert "a warning on stderr" in res["test_output"]

    def test_test_function_outputs_uses_bare_names_and_errors(self, tmp_path, fake_run):
        payload = {
            "results": {
                "t::TestA::test_pass": {"status": "passed"},
                "t::TestA::test_fail": {"status": "failed", "error": "AssertionError: nope"},
            }
        }
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        tfo = json.loads(res["test_function_outputs"])
        # Keys are the bare tails; values are the per-test "error" text ("" when none).
        assert tfo["test_pass"] == ""
        assert tfo["test_fail"] == "AssertionError: nope"

    def test_skips_malformed_brace_line_and_uses_valid_payload(self, tmp_path, fake_run):
        # A line that looks like JSON ({...}) but fails json.loads is skipped by
        # the reverse-scan's inner try/except; the parser keeps looking upward
        # for a valid payload line.
        garbage = "{not: valid, json}"  # startswith { and endswith } but not JSON
        real = {"results": {"t::test_good": {"status": "passed"}}}
        # garbage comes AFTER the real payload so the reverse scan hits it first.
        stdout = json.dumps(real) + "\n" + garbage + "\n"
        fake_run["completed"] = _FakeCompleted(stdout=stdout)
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        scores = json.loads(res["test_scores"])
        assert scores == {"t::test_good": "passed"}

    def test_picks_last_json_line_when_multiple_present(self, tmp_path, fake_run):
        # Parser scans in reverse; a stray earlier brace-line must be ignored in
        # favor of the final real payload.
        decoy = '{"not": "the payload"}'
        real = {"results": {"t::test_final": {"status": "passed"}}}
        stdout = decoy + "\n" + json.dumps(real) + "\n"
        fake_run["completed"] = _FakeCompleted(stdout=stdout)
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        scores = json.loads(res["test_scores"])
        assert scores == {"t::test_final": "passed"}


# ---------------------------------------------------------------------------
# Section B — return-dict ("CTRF consumer") key shape
# ---------------------------------------------------------------------------


class TestReturnDictShape:
    _EXPECTED_SUCCESS_KEYS = {
        "tests_total",
        "tests_passed",
        "tests_failed",
        "tests_errored",
        "tests_skipped",
        "test_scores",
        "test_function_outputs",
        "test_output",
        "test_code",
        "reward",
        "duration_execution_ms",
        "error",
    }

    def test_success_dict_has_full_key_set(self, tmp_path, fake_run):
        payload = {"results": {"t::test_a": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert set(res.keys()) == self._EXPECTED_SUCCESS_KEYS
        # test_scores / test_function_outputs are JSON strings, not dicts.
        assert isinstance(res["test_scores"], str)
        assert isinstance(res["test_function_outputs"], str)
        assert isinstance(res["reward"], float)
        assert isinstance(res["duration_execution_ms"], int)
        assert res["test_code"] == _TC

    def test_empty_test_code_short_circuits_without_running_docker(
        self, tmp_path, fake_run
    ):
        res = execute_tests(
            test_code="   \n  ",
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["error"] == "empty test_code"
        assert res["tests_total"] == 0
        assert res["reward"] == 0.0
        # No subprocess.run should have been issued for empty code.
        assert fake_run["calls"] == []


# ---------------------------------------------------------------------------
# Section C — no-results / no-payload / import-error early returns
# ---------------------------------------------------------------------------


class TestExecuteTestsEarlyReturns:
    def test_empty_results_returns_no_tests_collected(self, tmp_path, fake_run):
        payload = {"import_error": None, "collected": 0, "results": {}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["tests_total"] == 0
        assert res["reward"] == 0.0
        assert "no tests collected" in res["error"]
        assert res["tests_skipped"] == 0

    def test_no_parseable_payload_returns_error(self, tmp_path, fake_run):
        # stdout carries no line that both starts with { and ends with }.
        fake_run["completed"] = _FakeCompleted(
            stdout="just some noise\nno json here\n", stderr="stderr tail line", returncode=7
        )
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["tests_total"] == 0
        assert res["reward"] == 0.0
        assert "runner produced no parseable output" in res["error"]
        assert "rc=7" in res["error"]

    def test_import_error_payload_surfaces_first_line(self, tmp_path, fake_run):
        payload = {
            "import_error": "ModuleNotFoundError: No module named 'task'\nfull traceback...",
            "results": {},
        }
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["tests_total"] == 0
        assert res["reward"] == 0.0
        assert res["error"].startswith("import: ")
        assert "ModuleNotFoundError" in res["error"]
        # Only the first line of the import_error is surfaced.
        assert "full traceback" not in res["error"]


# ---------------------------------------------------------------------------
# Section D — subprocess failure surfaces (timeout / generic exception)
# ---------------------------------------------------------------------------


class TestExecuteTestsSubprocessFailures:
    def test_timeout_expired_returns_timeout_error(self, tmp_path, monkeypatch):
        def _boom(cmd, *a, **k):
            raise subprocess.TimeoutExpired(cmd=cmd, timeout=300)

        monkeypatch.setattr(subprocess, "run", _boom)
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
            timeout=300,
        )
        assert res["tests_total"] == 0
        assert res["reward"] == 0.0
        assert res["error"] == "timeout after 300s"

    def test_generic_exception_returns_error_dict(self, tmp_path, monkeypatch):
        def _boom(cmd, *a, **k):
            raise RuntimeError("docker daemon exploded")

        monkeypatch.setattr(subprocess, "run", _boom)
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["tests_total"] == 0
        assert res["reward"] == 0.0
        assert "docker daemon exploded" in res["error"]


# ---------------------------------------------------------------------------
# Section E — test_weights.json loading edge cases
# ---------------------------------------------------------------------------


class TestWeightsLoading:
    def test_corrupt_weights_json_is_swallowed_to_empty(self, tmp_path, fake_run):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # Corrupt weights JSON is caught by a broad `except Exception` and
        # silently coerced to {} (rather than raising). Tests still run; the
        # reward then falls back to 0.0 because _compute_reward returns 0.0 on
        # empty weights — the operator gets NO signal that weights were dropped.
        payload = {"results": {"t::TestA::test_pass": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json="{ this is not valid json ",
            workspace_dir=_mk_ws(tmp_path),
        )
        # Tests were parsed fine...
        assert res["tests_passed"] == 1
        assert res["tests_total"] == 1
        assert res["error"] == ""
        # ...but the reward is silently 0.0 because weights were discarded.
        assert res["reward"] == 0.0

    def test_non_dict_weights_json_coerced_to_empty(self, tmp_path, fake_run):
        # A syntactically-valid JSON that isn't an object (a list) is coerced to
        # {} via the isinstance guard, so reward again falls back to 0.0.
        payload = {"results": {"t::TestA::test_pass": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json="[1, 2, 3]",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["tests_passed"] == 1
        assert res["reward"] == 0.0

    def test_string_typed_weight_raises_and_discards_real_results(
        self, tmp_path, fake_run
    ):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # A weight value typed as a string (e.g. "5") passes the isinstance-dict
        # guard, but inside _compute_reward the comparison `"5" > 0` raises a
        # TypeError. That TypeError is NOT handled locally; it propagates to the
        # broad `except Exception as exc` in execute_tests, which discards the
        # already-parsed passing results and returns tests_total=0, reward=0.0.
        # Real, correctly-executed tests are silently thrown away.
        payload = {"results": {"t::TestA::test_pass": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json=json.dumps({"test_pass": "5"}),
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["tests_total"] == 0
        assert res["reward"] == 0.0
        # The surfaced error is the raw TypeError string (str(exc)), not a graded
        # result — concrete evidence that a real run's results were discarded.
        assert "'>' not supported between instances of 'str' and 'int'" in res["error"]

    def test_empty_weights_string_treated_as_empty_dict(self, tmp_path, fake_run):
        payload = {"results": {"t::TestA::test_pass": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json="",
            workspace_dir=_mk_ws(tmp_path),
        )
        assert res["tests_passed"] == 1
        assert res["reward"] == 0.0


# ---------------------------------------------------------------------------
# Section F — _compute_reward pos_total<=0 fallback + skipped exclusion
# (distinct from tests/test_signed_reward.py, which pins the signed range;
#  here we pin the all-negative-weights fallback path end-to-end and its
#  denominator handling of skipped tests.)
# ---------------------------------------------------------------------------


class TestNegativeWeightFallback:
    def test_all_negative_weights_triggered_guardrail_scores_high(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # When every weight is negative (a rubric made entirely of guardrails),
        # pos_total<=0 so _compute_reward abandons the signed formula and falls
        # back to passed/total. A *triggered* guardrail has status "passed", so
        # it counts toward the numerator — the run that hit a guardrail scores
        # HIGH (0.5 here) instead of being penalized.
        results = {
            "g1::test_x": {"status": "passed"},   # guardrail triggered
            "g2::test_y": {"status": "failed"},   # guardrail not triggered
        }
        weights = {"g1::test_x": -3, "g2::test_y": -1}
        assert _compute_reward(results, weights) == 0.5

    def test_all_negative_weights_all_triggered_scores_full(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # Every guardrail triggered -> passed/total == 1.0, i.e. the maximally
        # bad run scores a perfect 1.0 under the fallback.
        results = {
            "g1::test_x": {"status": "passed"},
            "g2::test_y": {"status": "passed"},
        }
        weights = {"g1::test_x": -3, "g2::test_y": -1}
        assert _compute_reward(results, weights) == 1.0

    def test_skipped_excluded_from_fallback_denominator(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # In the fallback branch, skipped tests are dropped from BOTH numerator
        # and denominator. One passing guardrail + one skipped test => 1/1 = 1.0.
        results = {
            "a::test_pass": {"status": "passed"},
            "b::test_skip": {"status": "skipped"},
        }
        weights = {"a::test_pass": -1}
        assert _compute_reward(results, weights) == 1.0

    def test_all_skipped_fallback_returns_zero_no_div_by_zero(self):
        # When every scored test is skipped, total==0 and the fallback returns
        # 0.0 rather than dividing by zero.
        results = {
            "a::t1": {"status": "skipped"},
            "b::t2": {"status": "skipped"},
        }
        weights = {"a::t1": -1}
        assert _compute_reward(results, weights) == 0.0

    def test_negative_weight_fallback_end_to_end_via_execute_tests(
        self, tmp_path, fake_run
    ):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # Same guardrail-scores-high bug, exercised through the full
        # execute_tests() path (parsing -> reward assembly).
        payload = {
            "results": {
                "t::TestG::test_guard": {"status": "passed"},
            }
        }
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json=json.dumps({"test_guard": -5}),
            workspace_dir=_mk_ws(tmp_path),
        )
        # A single triggered guardrail: pos_total<=0 -> fallback -> 1/1 == 1.0.
        assert res["reward"] == 1.0
        assert res["tests_passed"] == 1


# ---------------------------------------------------------------------------
# Section G — skipped-test handling in the counts path (non-fallback)
# ---------------------------------------------------------------------------


class TestSkippedCounting:
    def test_skipped_excluded_from_tests_total_but_reported(self, tmp_path, fake_run):
        payload = {
            "results": {
                "t::test_pass": {"status": "passed"},
                "t::test_skip": {"status": "skipped"},
            }
        }
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        res = execute_tests(
            test_code=_TC,
            test_weights_json=json.dumps({"test_pass": 5}),
            workspace_dir=_mk_ws(tmp_path),
        )
        # tests_total = passed+failed+errored; skipped is reported separately.
        assert res["tests_total"] == 1
        assert res["tests_passed"] == 1
        assert res["tests_skipped"] == 1
        # Skipped test carries no negative weight and doesn't dilute the reward.
        assert res["reward"] == 1.0


# ---------------------------------------------------------------------------
# Section H — argv assembly details (offline; extends the reference site tests
# without duplicating their flag-injection cases)
# ---------------------------------------------------------------------------


class TestArgvAssembly:
    def test_argv_carries_readonly_mounts_and_runner_entrypoint(self, tmp_path, fake_run):
        payload = {"results": {"t::test_a": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        ws = _mk_ws(tmp_path)
        execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=ws,
            image="wildclawbench-ubuntu:v1.3",
        )
        assert fake_run["calls"], "expected a docker run argv to be captured"
        cmd = fake_run["calls"][0]
        assert cmd[0:3] == ["docker", "run", "--rm"]
        # Read-only mounts for both the /tests overlay and the workspace.
        joined = " ".join(cmd)
        assert ":/tests:ro" in joined
        assert ":/tmp_workspace:ro" in joined
        assert "-w" in cmd and cmd[cmd.index("-w") + 1] == "/tmp_workspace"
        # Entrypoint is the embedded runner script.
        assert cmd[-3:] == ["wildclawbench-ubuntu:v1.3", "python3", "/tests/runner.py"]

    def test_no_network_flag_when_network_none(self, tmp_path, fake_run):
        payload = {"results": {"t::test_a": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
            network=None,
        )
        cmd = fake_run["calls"][0]
        assert "--network" not in cmd

    def test_mock_env_dict_flows_into_argv_as_e_pairs(self, tmp_path, fake_run):
        payload = {"results": {"t::test_a": {"status": "passed"}}}
        fake_run["completed"] = _FakeCompleted(stdout=_runner_stdout(payload))
        execute_tests(
            test_code=_TC,
            test_weights_json="{}",
            workspace_dir=_mk_ws(tmp_path),
            mock_env_dict={"FIGMA_URL": "http://figma-api:9000"},
        )
        cmd = fake_run["calls"][0]
        assert "FIGMA_URL=http://figma-api:9000" in cmd
        # Every -e is immediately followed by a KEY=VALUE token (never a bare flag).
        for i, tok in enumerate(cmd):
            if tok == "-e":
                assert "=" in cmd[i + 1]
                assert not cmd[i + 1].startswith("-")


# ---------------------------------------------------------------------------
# Section I — _RUNNER_SCRIPT static sanity
# ---------------------------------------------------------------------------


class TestRunnerScriptStatic:
    def test_runner_script_compiles(self):
        # The embedded in-container runner must be syntactically valid Python so
        # it can be exec'd inside the sandbox.
        code = compile(_RUNNER_SCRIPT, "<runner>", "exec")
        assert code is not None

    def test_runner_script_has_sigalrm_per_test_timeout(self):
        # Per-test timeout is enforced via a SIGALRM handler + signal.alarm().
        assert "signal.SIGALRM" in _RUNNER_SCRIPT
        assert "signal.signal" in _RUNNER_SCRIPT
        assert "signal.alarm" in _RUNNER_SCRIPT
        assert "WCB_PER_TEST_TIMEOUT" in _RUNNER_SCRIPT

    def test_runner_script_has_discovery_and_output_markers(self):
        # Discovery keys / entrypoint the host parser and _record path depend on.
        assert "test_outputs.py" in _RUNNER_SCRIPT
        assert "import_error" in _RUNNER_SCRIPT
        assert '"results"' in _RUNNER_SCRIPT
        assert "collected" in _RUNNER_SCRIPT
        # The runner emits its payload as a single json.dumps(...) line that the
        # host reverse-scans for; both the discovery prefix and the print exist.
        assert "test_" in _RUNNER_SCRIPT
        assert "json.dumps(out)" in _RUNNER_SCRIPT

    def test_runner_script_recognizes_skips(self):
        # Skip recognition (stub pytest.skip + unittest SkipTest) must be present
        # so skipped tests are classified rather than errored.
        assert "SkipTest" in _RUNNER_SCRIPT or "Skipped" in _RUNNER_SCRIPT
        assert '"skipped"' in _RUNNER_SCRIPT
