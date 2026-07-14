"""Unit coverage for the previously-untested helpers in
src/utils/docker_utils.py.

Companion to tests/test_docker_env_validation.py, which already covers the
S-001 argv-injection validators (_validate_env_arg / _validate_docker_token /
build_env_args) and the start_container integration argv. To avoid duplication,
this file deliberately does NOT re-test those; it targets the remaining major
helpers:

  * require_image_present / remove_container   (image-presence + cleanup argv)
  * _parse_service_toml / discover_services    (service.toml config parsing)
  * setup_mock_apis / warmup_for_mock_apis     (mock-fleet staging + warmup script)
  * _parse_skill_pip_deps / _parse_skill_bin_deps  (SKILL.md frontmatter parsing)
  * run_warmup                                 (line filtering + background detach)
  * _copy_dir_from_container /                 (returncode-driven collection
    _copy_file_from_container                    decision logic)
  * close_proc_log                             (log-handle lifecycle)
  * setup_workspace                            (docker-error propagation)
  * inject_openclaw_models                     (temp-file cleanup + injection)

Every test runs OFFLINE and deterministically: subprocess.run is monkey-patched
so nothing touches the docker daemon or the network, and all filesystem writes
go to pytest's tmp_path. The tests verify the argv list / control flow that
would be handed to subprocess.run and the return/raise behavior around its
returncode — never a real container.

Where a helper exhibits a surprising-but-current behavior (e.g. a non-numeric
`port` silently staying a string, or an empty-string port dropping a service),
the assertion pins the CURRENT behavior rather than an idealized one; those
sites are flagged with the standard note.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import docker_utils as du  # noqa: E402


# ---------------------------------------------------------------------------
# Shared fakes / fixtures (mirrors the capture style in
# tests/test_docker_env_validation.py so nothing spawns a container).
# ---------------------------------------------------------------------------


class _FakeCompleted:
    """Stand-in for subprocess.CompletedProcess."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture
def capture_run(monkeypatch):
    """Capture every subprocess.run argv without executing anything.

    Returns the list of captured argv lists. subprocess.run always returns a
    success _FakeCompleted() unless a per-test override installs its own fake.
    """
    calls: list[list[str]] = []

    def fake_run(cmd, *args, **kwargs):
        calls.append(list(cmd))
        return _FakeCompleted()

    monkeypatch.setattr(du.subprocess, "run", fake_run)
    return calls


def _install_scripted_run(monkeypatch, results):
    """Install a subprocess.run that returns queued _FakeCompleted results in
    order, recording each argv. `results` is a list of _FakeCompleted; the last
    one is reused if more calls arrive than results provided.
    """
    calls: list[list[str]] = []
    queue = list(results)

    def fake_run(cmd, *args, **kwargs):
        calls.append(list(cmd))
        if queue:
            return queue.pop(0) if len(queue) > 1 else queue[0]
        return _FakeCompleted()

    monkeypatch.setattr(du.subprocess, "run", fake_run)
    return calls


# ---------------------------------------------------------------------------
# Section A — require_image_present (fail-fast image-presence precheck)
# ---------------------------------------------------------------------------


class TestRequireImagePresent:
    def test_present_image_issues_inspect_and_returns_none(self, monkeypatch):
        calls = _install_scripted_run(monkeypatch, [_FakeCompleted(returncode=0)])
        assert du.require_image_present("wildclawbench-ubuntu:v1.3") is None
        # Exactly one `docker image inspect <image>` call.
        assert calls == [["docker", "image", "inspect", "wildclawbench-ubuntu:v1.3"]]

    def test_missing_image_raises_runtimeerror_with_stderr(self, monkeypatch):
        _install_scripted_run(
            monkeypatch,
            [_FakeCompleted(returncode=1, stderr="Error: No such image: foo:bar\n")],
        )
        with pytest.raises(RuntimeError) as exc:
            du.require_image_present("foo:bar")
        msg = str(exc.value)
        assert "Required Docker image not present locally: foo:bar" in msg
        # The captured docker stderr is surfaced (stripped) into the message.
        assert "No such image: foo:bar" in msg

    def test_missing_image_with_empty_stderr_still_raises(self, monkeypatch):
        # stderr may be None/empty; the helper coalesces to "" — no crash.
        _install_scripted_run(monkeypatch, [_FakeCompleted(returncode=125, stderr="")])
        with pytest.raises(RuntimeError, match="not present locally: img:x"):
            du.require_image_present("img:x")


# ---------------------------------------------------------------------------
# Section B — remove_container (orphan-container removal argv)
# ---------------------------------------------------------------------------


class TestRemoveContainer:
    def test_issues_docker_rm_force(self, capture_run):
        du.remove_container("task-123")
        assert capture_run == [["docker", "rm", "-f", "task-123"]]

    def test_return_value_is_none(self, capture_run):
        # remove_container ignores returncode by design (best-effort cleanup).
        assert du.remove_container("already-gone") is None

    def test_does_not_validate_token(self, capture_run):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # remove_container passes `name` straight to argv WITHOUT the
        # _validate_docker_token guard the run-sites use. A leading-dash name is
        # forwarded verbatim (safe here only because it is never attacker-fed).
        du.remove_container("--nope")
        assert capture_run == [["docker", "rm", "-f", "--nope"]]


# ---------------------------------------------------------------------------
# Section C — _parse_service_toml (minimal [service] TOML reader)
# ---------------------------------------------------------------------------


class TestParseServiceToml:
    def _toml(self, tmp_path, body: str) -> Path:
        p = tmp_path / "service.toml"
        p.write_text(body, encoding="utf-8")
        return p

    def test_parses_service_section_and_coerces_port(self, tmp_path):
        p = self._toml(
            tmp_path,
            "[service]\n"
            'name = "figma"\n'
            "port = 8055\n"
            'env_var_name = "FIGMA_API_URL"\n',
        )
        cfg = du._parse_service_toml(p)
        assert cfg["name"] == "figma"
        assert cfg["env_var_name"] == "FIGMA_API_URL"
        # port is coerced to int when the key is 'port' and the value is digits.
        assert cfg["port"] == 8055
        assert isinstance(cfg["port"], int)

    def test_strips_both_quote_styles(self, tmp_path):
        p = self._toml(tmp_path, "[service]\nname = 'single'\nother = \"double\"\n")
        cfg = du._parse_service_toml(p)
        assert cfg["name"] == "single"
        assert cfg["other"] == "double"

    def test_ignores_keys_outside_service_section(self, tmp_path):
        p = self._toml(
            tmp_path,
            "[service]\n"
            "port = 9000\n"
            "[other]\n"
            "port = 1234\n"
            'name = "should-be-ignored"\n',
        )
        cfg = du._parse_service_toml(p)
        # Only the [service] section is captured; the [other] section is skipped.
        assert cfg == {"port": 9000}

    def test_ignores_comments_and_blank_lines(self, tmp_path):
        p = self._toml(
            tmp_path,
            "# a comment\n\n[service]\n# inner comment\nport = 42\n\n",
        )
        assert du._parse_service_toml(p) == {"port": 42}

    def test_non_numeric_port_stays_string(self, tmp_path):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # port coercion is gated on val.isdigit(); a non-numeric port is left as
        # a raw string rather than raising. discover_services()/setup_mock_apis()
        # then treat a truthy string port as valid.
        p = self._toml(tmp_path, '[service]\nport = "abc"\n')
        cfg = du._parse_service_toml(p)
        assert cfg["port"] == "abc"

    def test_lines_before_service_section_are_dropped(self, tmp_path):
        # A key = value pair appearing before the [service] header is not in the
        # service section, so it is dropped.
        p = self._toml(tmp_path, 'stray = "x"\n[service]\nport = 7\n')
        assert du._parse_service_toml(p) == {"port": 7}


# ---------------------------------------------------------------------------
# Section D — discover_services (walk env dir for service.toml files)
# ---------------------------------------------------------------------------


class TestDiscoverServices:
    def _mk_service(self, root: Path, name: str, body: str) -> None:
        d = root / name
        d.mkdir(parents=True)
        (d / "service.toml").write_text(body, encoding="utf-8")

    def test_missing_environment_dir_returns_empty(self, tmp_path):
        assert du.discover_services(tmp_path / "does-not-exist") == []

    def test_collects_services_sorted_by_dir_name(self, tmp_path):
        env = tmp_path / "environment"
        env.mkdir()
        self._mk_service(env, "zebra-api", '[service]\nport = 8100\nenv_var_name = "Z"\n')
        self._mk_service(env, "alpha-api", '[service]\nport = 8001\nenv_var_name = "A"\n')
        out = du.discover_services(env)
        # sorted(iterdir()) => alpha before zebra.
        assert [s["name"] for s in out] == ["alpha-api", "zebra-api"]
        assert out[0] == {"name": "alpha-api", "port": 8001, "env_var_name": "A"}

    def test_skips_dirs_without_service_toml(self, tmp_path):
        env = tmp_path / "environment"
        env.mkdir()
        (env / "not-a-service").mkdir()  # no service.toml
        self._mk_service(env, "real-api", "[service]\nport = 8002\n")
        out = du.discover_services(env)
        assert [s["name"] for s in out] == ["real-api"]
        # Missing env_var_name defaults to "".
        assert out[0]["env_var_name"] == ""

    def test_skips_service_with_no_port(self, tmp_path):
        # A service.toml lacking a port (falsy) is dropped entirely.
        env = tmp_path / "environment"
        env.mkdir()
        self._mk_service(env, "portless-api", '[service]\nenv_var_name = "P"\n')
        self._mk_service(env, "good-api", "[service]\nport = 8003\n")
        out = du.discover_services(env)
        assert [s["name"] for s in out] == ["good-api"]

    def test_ignores_regular_files_at_top_level(self, tmp_path):
        env = tmp_path / "environment"
        env.mkdir()
        (env / "README.md").write_text("not a service dir", encoding="utf-8")
        self._mk_service(env, "svc-api", "[service]\nport = 8004\n")
        out = du.discover_services(env)
        assert [s["name"] for s in out] == ["svc-api"]


# ---------------------------------------------------------------------------
# Section E — setup_mock_apis (per-task mock copy + env-var map)
# ---------------------------------------------------------------------------


class TestSetupMockApis:
    def _mk_api(self, env: Path, name: str, body: str) -> None:
        d = env / name
        d.mkdir(parents=True)
        (d / "service.toml").write_text(body, encoding="utf-8")

    def test_builds_localhost_url_map_for_valid_apis(self, tmp_path, capture_run):
        env = tmp_path / "environment"
        env.mkdir()
        self._mk_api(
            env, "figma-api", '[service]\nport = 8055\nenv_var_name = "FIGMA_API_URL"\n'
        )
        # A tracking_middleware.py present => staged after the api copies.
        (env / "tracking_middleware.py").write_text("# mw\n", encoding="utf-8")

        env_vars = du.setup_mock_apis("task-1", env, ["figma-api"])
        assert env_vars == {"FIGMA_API_URL": "http://localhost:8055"}
        # A docker cp for the api dir must have been issued.
        cp_calls = [c for c in capture_run if len(c) >= 2 and c[1] == "cp"]
        assert any("figma-api" in "".join(c) for c in cp_calls)

    def test_missing_api_dir_is_skipped(self, tmp_path, capture_run):
        env = tmp_path / "environment"
        env.mkdir()
        # No dir created for 'ghost-api'.
        env_vars = du.setup_mock_apis("task-1", env, ["ghost-api"])
        assert env_vars == {}

    def test_api_missing_env_var_name_is_skipped(self, tmp_path, capture_run):
        env = tmp_path / "environment"
        env.mkdir()
        # Valid port but no env_var_name => cannot build a URL => skipped.
        self._mk_api(env, "bad-api", "[service]\nport = 8060\n")
        env_vars = du.setup_mock_apis("task-1", env, ["bad-api"])
        assert env_vars == {}

    def test_tracking_middleware_not_staged_when_no_env_vars(self, tmp_path, capture_run):
        env = tmp_path / "environment"
        env.mkdir()
        (env / "tracking_middleware.py").write_text("# mw\n", encoding="utf-8")
        # required_apis empty => env_vars empty => middleware staging is skipped.
        du.setup_mock_apis("task-1", env, [])
        assert not any("tracking_middleware.py" in "".join(c) for c in capture_run)


# ---------------------------------------------------------------------------
# Section F — warmup_for_mock_apis (bash warmup script builder, no subprocess)
# ---------------------------------------------------------------------------


class TestWarmupForMockApis:
    def _mk_api(self, env: Path, name: str, body: str) -> None:
        d = env / name
        d.mkdir(parents=True)
        (d / "service.toml").write_text(body, encoding="utf-8")

    def test_emits_pip_install_and_uvicorn_lines(self, tmp_path):
        env = tmp_path / "environment"
        env.mkdir()
        self._mk_api(env, "figma-api", "[service]\nport = 8055\n")
        script = du.warmup_for_mock_apis(["figma-api"], env)
        assert "pip install -q -r /opt/mock_apis/figma-api/requirements.txt" in script
        # uvicorn bound to the declared port with PYTHONPATH for shared middleware.
        assert "uvicorn server:app --host 0.0.0.0 --port 8055" in script
        assert "PYTHONPATH=/opt/mock_apis" in script
        # Launched in the background.
        assert script.rstrip().endswith("&")

    def test_skips_apis_without_service_toml(self, tmp_path):
        env = tmp_path / "environment"
        env.mkdir()
        # 'ghost-api' dir absent entirely => no lines contributed.
        script = du.warmup_for_mock_apis(["ghost-api"], env)
        assert script == ""

    def test_skips_service_with_no_port(self, tmp_path):
        env = tmp_path / "environment"
        env.mkdir()
        self._mk_api(env, "noport-api", '[service]\nenv_var_name = "X"\n')
        script = du.warmup_for_mock_apis(["noport-api"], env)
        assert script == ""

    def test_multiple_apis_join_with_newlines(self, tmp_path):
        env = tmp_path / "environment"
        env.mkdir()
        self._mk_api(env, "a-api", "[service]\nport = 8001\n")
        self._mk_api(env, "b-api", "[service]\nport = 8002\n")
        script = du.warmup_for_mock_apis(["a-api", "b-api"], env)
        assert "--port 8001" in script
        assert "--port 8002" in script
        # 2 pip lines + 2 uvicorn lines = 4 newline-joined lines.
        assert len(script.split("\n")) == 4


# ---------------------------------------------------------------------------
# Section G — SKILL.md frontmatter parsing (pip + bin deps)
# ---------------------------------------------------------------------------


class TestParseSkillDeps:
    def _mk_skill(self, tmp_path, body: str) -> Path:
        p = tmp_path / "SKILL.md"
        p.write_text(body, encoding="utf-8")
        return p

    _FRONTMATTER = (
        "---\n"
        "name: pdf-extract\n"
        "metadata:\n"
        "  clawdbot:\n"
        "    pip: [pymupdf, pillow]\n"
        "    requires:\n"
        "      pip: [pdfplumber]\n"
        "      bins: [pdftotext, tesseract]\n"
        "---\n"
        "# body\n"
    )

    def test_pip_deps_merge_direct_and_requires(self, tmp_path):
        skill = self._mk_skill(tmp_path, self._FRONTMATTER)
        deps = du._parse_skill_pip_deps(skill)
        # clawdbot.pip + clawdbot.requires.pip, in that order.
        assert deps == ["pymupdf", "pillow", "pdfplumber"]

    def test_bin_deps_from_requires_bins(self, tmp_path):
        skill = self._mk_skill(tmp_path, self._FRONTMATTER)
        assert du._parse_skill_bin_deps(skill) == ["pdftotext", "tesseract"]

    def test_missing_file_returns_empty(self, tmp_path):
        missing = tmp_path / "nope" / "SKILL.md"
        assert du._parse_skill_pip_deps(missing) == []
        assert du._parse_skill_bin_deps(missing) == []

    def test_no_frontmatter_returns_empty(self, tmp_path):
        skill = self._mk_skill(tmp_path, "# just a heading, no --- fence\n")
        assert du._parse_skill_pip_deps(skill) == []
        assert du._parse_skill_bin_deps(skill) == []

    def test_frontmatter_without_clawdbot_returns_empty(self, tmp_path):
        skill = self._mk_skill(
            tmp_path, "---\nname: x\nmetadata:\n  other: 1\n---\nbody\n"
        )
        assert du._parse_skill_pip_deps(skill) == []
        assert du._parse_skill_bin_deps(skill) == []

    def test_malformed_yaml_frontmatter_returns_empty(self, tmp_path):
        # A YAML parse error is swallowed => empty list (best-effort parsing).
        skill = self._mk_skill(
            tmp_path, "---\n: : : not valid yaml : :\n\t- broken\n---\nbody\n"
        )
        assert du._parse_skill_pip_deps(skill) == []
        assert du._parse_skill_bin_deps(skill) == []

    def test_deps_are_stringified_and_stripped(self, tmp_path):
        skill = self._mk_skill(
            tmp_path,
            "---\nmetadata:\n  clawdbot:\n    pip: ['  padded  ', '', 42]\n---\nx\n",
        )
        # Empty entries are dropped; non-empty ones are str()'d and stripped.
        assert du._parse_skill_pip_deps(skill) == ["padded", "42"]

    def test_incomplete_frontmatter_fence_returns_empty(self, tmp_path):
        # Starts with --- but has no closing fence (only one delimiter) => the
        # split into 3 parts fails and we bail to [].
        skill = self._mk_skill(tmp_path, "---\nmetadata:\n  clawdbot:\n    pip: [x]\n")
        assert du._parse_skill_pip_deps(skill) == []


# ---------------------------------------------------------------------------
# Section H — run_warmup (line filtering + background-detach wrapping)
# ---------------------------------------------------------------------------


class TestRunWarmup:
    def test_empty_or_blank_warmup_is_noop(self, capture_run):
        du.run_warmup("task-1", "")
        du.run_warmup("task-1", "   \n  \n")
        assert capture_run == []

    def test_comment_and_blank_lines_are_filtered(self, capture_run):
        du.run_warmup("task-1", "# comment\n\n  \necho hi\n# trailing\n")
        # Only the single real command is executed.
        assert len(capture_run) == 1
        cmd = capture_run[0]
        assert cmd[:3] == ["docker", "exec", "task-1"]
        assert cmd[-1] == "echo hi"

    def test_each_command_runs_via_bash_dash_c(self, capture_run):
        du.run_warmup("task-1", "cmd one\ncmd two")
        assert len(capture_run) == 2
        for cmd in capture_run:
            assert cmd[:5] == ["docker", "exec", "task-1", "/bin/bash", "-c"]

    def test_failing_command_raises_runtimeerror(self, monkeypatch):
        _install_scripted_run(
            monkeypatch, [_FakeCompleted(returncode=1, stderr="boom")]
        )
        with pytest.raises(RuntimeError, match="Warmup command failed"):
            du.run_warmup("task-1", "will-fail")

    def test_detach_background_wraps_trailing_ampersand_command(self, capture_run):
        du.run_warmup(
            "task-1", "serve --port 9 &", detach_background=True
        )
        assert len(capture_run) == 1
        cmd = capture_run[0]
        # background path uses '/bin/bash -lc' with a nohup wrapper, cd into
        # TMP_WORKSPACE, and a per-index log file.
        assert cmd[:5] == ["docker", "exec", "task-1", "/bin/bash", "-lc"]
        wrapped = cmd[-1]
        assert "nohup" in wrapped
        assert du.TMP_WORKSPACE in wrapped
        assert "/tmp/wildclaw_warmup_1.log" in wrapped
        # The trailing '&' of the original command is stripped before quoting.
        assert "serve --port 9 &" not in wrapped

    def test_detach_background_leaves_non_ampersand_command_foreground(self, capture_run):
        # detach_background only reroutes commands that END in '&'.
        du.run_warmup("task-1", "echo foreground", detach_background=True)
        cmd = capture_run[0]
        assert cmd[:5] == ["docker", "exec", "task-1", "/bin/bash", "-c"]
        assert cmd[-1] == "echo foreground"

    def test_detach_background_command_failure_raises(self, monkeypatch):
        _install_scripted_run(
            monkeypatch, [_FakeCompleted(returncode=2, stderr="nope")]
        )
        with pytest.raises(RuntimeError, match="Warmup background command failed"):
            du.run_warmup("task-1", "serve &", detach_background=True)


# ---------------------------------------------------------------------------
# Section I — container copy helpers (returncode-driven decision logic)
# ---------------------------------------------------------------------------


class TestCopyHelpers:
    def test_copy_dir_success_returns_true_and_builds_src_ref(self, monkeypatch):
        calls = _install_scripted_run(monkeypatch, [_FakeCompleted(returncode=0)])
        ok = du._copy_dir_from_container("task-1", "/tmp/openclaw/.", "/dest")
        assert ok is True
        assert calls == [["docker", "cp", "task-1:/tmp/openclaw/.", "/dest"]]

    def test_copy_dir_failure_returns_false(self, monkeypatch):
        _install_scripted_run(
            monkeypatch, [_FakeCompleted(returncode=1, stderr="No such container")]
        )
        assert du._copy_dir_from_container("task-1", "/x/.", "/dest") is False

    def test_copy_file_success_returns_true(self, monkeypatch, tmp_path):
        calls = _install_scripted_run(monkeypatch, [_FakeCompleted(returncode=0)])
        dest = tmp_path / "out.txt"
        ok = du._copy_file_from_container("task-1", "/tmp/out.txt", dest)
        assert ok is True
        assert calls == [["docker", "cp", "task-1:/tmp/out.txt", str(dest)]]

    def test_copy_file_failure_returns_false(self, monkeypatch, tmp_path):
        _install_scripted_run(
            monkeypatch, [_FakeCompleted(returncode=1, stderr="missing")]
        )
        dest = tmp_path / "out.txt"
        assert du._copy_file_from_container("task-1", "/tmp/out.txt", dest) is False


# ---------------------------------------------------------------------------
# Section J — close_proc_log (log-handle lifecycle)
# ---------------------------------------------------------------------------


class _FakeLogFile:
    def __init__(self, closed: bool = False):
        self.closed = closed
        self.close_called = False

    def close(self):
        self.close_called = True
        self.closed = True


class _FakeProc:
    def __init__(self, log_file=None):
        if log_file is not None:
            self._log_file = log_file


class TestCloseProcLog:
    def test_closes_open_log_handle(self):
        lf = _FakeLogFile(closed=False)
        du.close_proc_log(_FakeProc(log_file=lf))
        assert lf.close_called is True

    def test_already_closed_handle_is_not_reclosed(self):
        lf = _FakeLogFile(closed=True)
        du.close_proc_log(_FakeProc(log_file=lf))
        assert lf.close_called is False

    def test_missing_log_attribute_is_noop(self):
        # A Popen produced outside run_background has no _log_file => no crash.
        du.close_proc_log(_FakeProc(log_file=None))


# ---------------------------------------------------------------------------
# Section K — setup_workspace (docker-error propagation)
# ---------------------------------------------------------------------------


class TestSetupWorkspace:
    def test_copy_failure_raises_runtimeerror(self, monkeypatch):
        # First subprocess.run (the /app -> TMP_WORKSPACE copy) fails.
        _install_scripted_run(
            monkeypatch, [_FakeCompleted(returncode=1, stderr="cp failed")]
        )
        with pytest.raises(RuntimeError, match="Workspace copy failed"):
            du.setup_workspace("task-1")

    def test_thinking_failure_raises_runtimeerror(self, monkeypatch):
        # copy succeeds, then the openclaw config-set for thinking fails.
        _install_scripted_run(
            monkeypatch,
            [
                _FakeCompleted(returncode=0),  # cp -r /app/. TMP_WORKSPACE
                _FakeCompleted(returncode=1, stderr="bad thinking"),  # config set
            ],
        )
        with pytest.raises(RuntimeError, match="Failed to set thinkingDefault"):
            du.setup_workspace("task-1", thinking="high")

    def test_happy_path_issues_expected_docker_execs(self, monkeypatch):
        calls = _install_scripted_run(monkeypatch, [_FakeCompleted(returncode=0)])
        # No thinking => copy + two symlink docker-exec calls (openclaw + root).
        du.setup_workspace("task-1")
        exec_calls = [c for c in calls if len(c) >= 2 and c[1] == "exec"]
        assert len(exec_calls) >= 3
        # The first exec is the workspace copy referencing TMP_WORKSPACE.
        assert du.TMP_WORKSPACE in " ".join(exec_calls[0])


# ---------------------------------------------------------------------------
# Section L — inject_openclaw_models (temp-file staging + cleanup)
# ---------------------------------------------------------------------------


class TestInjectOpenclawModels:
    def test_success_stages_cp_then_exec_and_cleans_temp(self, monkeypatch):
        captured_paths: list[str] = []

        def fake_run(cmd, *args, **kwargs):
            # Record any host temp path referenced by the docker cp source.
            if len(cmd) >= 3 and cmd[1] == "cp":
                captured_paths.append(cmd[2])
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(du.subprocess, "run", fake_run)
        du.inject_openclaw_models("task-1", {"custom": {"provider": "bedrock"}})

        # The temp json handed to docker cp must be removed afterward (finally:).
        assert captured_paths, "expected a docker cp of the temp models json"
        assert not Path(captured_paths[0]).exists()

    def test_cp_failure_raises_and_cleans_temp(self, monkeypatch):
        captured_paths: list[str] = []

        def fake_run(cmd, *args, **kwargs):
            if len(cmd) >= 3 and cmd[1] == "cp":
                captured_paths.append(cmd[2])
                return _FakeCompleted(returncode=1, stderr="cp boom")
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(du.subprocess, "run", fake_run)
        with pytest.raises(RuntimeError, match="Failed to copy models config"):
            du.inject_openclaw_models("task-1", {"m": 1})
        # Even on the raise path, the finally-block unlinks the temp file.
        assert captured_paths
        assert not Path(captured_paths[0]).exists()
