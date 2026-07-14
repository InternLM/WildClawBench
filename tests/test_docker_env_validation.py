"""S-001 regression tests: docker argv-flag injection hardening.

Covers the three validators in src/utils/docker_utils.py
(_validate_env_arg, _validate_docker_token, build_env_args) plus per-site
integration tests that monkey-patch subprocess.run and assert the assembled
docker-run argv (a) rejects flag-injection attempts and (b) preserves the
exact tokenisation that the six audited call sites relied on
(claudecode/codex/hermesagent runners + docker_utils.start_container +
litellm_sidecar.start_litellm + test_executor.run_tests_in_container).

These tests do NOT spawn containers. They verify the argv list that would be
handed to subprocess.run.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils.docker_utils import (  # noqa: E402
    _validate_docker_token,
    _validate_env_arg,
    build_env_args,
)


# ---------------------------------------------------------------------------
# Section A — _validate_env_arg
# ---------------------------------------------------------------------------


class TestValidateEnvArg:
    def test_accepts_typical_env_var(self):
        assert _validate_env_arg("API_KEY", "sk-abc123") == ("API_KEY", "sk-abc123")

    def test_accepts_underscore_leading_key(self):
        assert _validate_env_arg("_HIDDEN", "v")[0] == "_HIDDEN"

    def test_accepts_empty_value(self):
        # Load-bearing: start_container uses '-e PROXY=' to *clear* a parent-inherited
        # proxy inside the child container. Empty values must remain legal.
        assert _validate_env_arg("PROXY", "") == ("PROXY", "")

    def test_accepts_value_containing_spaces(self):
        # Some legitimate config values (paths, URLs with encoded params) have spaces.
        assert _validate_env_arg("K", "with space")[1] == "with space"

    def test_accepts_value_containing_equals_sign(self):
        # KEY=VALUE join must tolerate '=' in VALUE (think: encoded base64 padding).
        assert _validate_env_arg("K", "a=b=c")[1] == "a=b=c"

    def test_rejects_key_starting_with_digit(self):
        with pytest.raises(ValueError, match="invalid env var name"):
            _validate_env_arg("1BAD", "v")

    def test_rejects_key_with_dash(self):
        with pytest.raises(ValueError, match="invalid env var name"):
            _validate_env_arg("BAD-KEY", "v")

    def test_rejects_empty_key(self):
        with pytest.raises(ValueError, match="invalid env var name"):
            _validate_env_arg("", "v")

    def test_rejects_key_with_space(self):
        with pytest.raises(ValueError, match="invalid env var name"):
            _validate_env_arg("BAD KEY", "v")

    def test_rejects_value_starting_with_dash(self):
        with pytest.raises(ValueError, match="argv-flag injection"):
            _validate_env_arg("K", "--privileged")

    def test_rejects_value_starting_with_single_dash(self):
        with pytest.raises(ValueError, match="argv-flag injection"):
            _validate_env_arg("K", "-rm")

    def test_rejects_value_with_newline(self):
        with pytest.raises(ValueError, match="forbidden control char"):
            _validate_env_arg("K", "line1\nline2")

    def test_rejects_value_with_cr(self):
        with pytest.raises(ValueError, match="forbidden control char"):
            _validate_env_arg("K", "a\rb")

    def test_rejects_value_with_nul(self):
        with pytest.raises(ValueError, match="forbidden control char"):
            _validate_env_arg("K", "a\x00b")

    def test_rejects_non_string_key(self):
        with pytest.raises(ValueError, match="invalid env var name"):
            _validate_env_arg(123, "v")  # type: ignore[arg-type]

    def test_rejects_non_string_value(self):
        with pytest.raises(ValueError, match="must be str"):
            _validate_env_arg("K", 123)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Section B — _validate_docker_token (bare argv tokens: image / network / name)
# ---------------------------------------------------------------------------


class TestValidateDockerToken:
    def test_accepts_typical_image(self):
        assert _validate_docker_token("image", "wildclawbench:v1") == "wildclawbench:v1"

    def test_accepts_registry_qualified_image(self):
        assert (
            _validate_docker_token("image", "ghcr.io/org/repo:sha-abc")
            == "ghcr.io/org/repo:sha-abc"
        )

    def test_accepts_network_name(self):
        assert _validate_docker_token("network", "kensei-net") == "kensei-net"

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="non-empty"):
            _validate_docker_token("image", "")

    def test_rejects_dash_prefix(self):
        with pytest.raises(ValueError, match="argv-flag injection"):
            _validate_docker_token("image", "--privileged")

    def test_rejects_whitespace(self):
        with pytest.raises(ValueError, match="whitespace"):
            _validate_docker_token("image", "img with space")

    def test_rejects_tab(self):
        with pytest.raises(ValueError, match="whitespace"):
            _validate_docker_token("image", "img\timg")

    def test_rejects_newline(self):
        with pytest.raises(ValueError, match="whitespace"):
            _validate_docker_token("image", "img\nimg")

    def test_rejects_nul(self):
        with pytest.raises(ValueError, match="whitespace"):
            _validate_docker_token("image", "img\x00img")

    def test_rejects_non_string(self):
        with pytest.raises(ValueError, match="must be str"):
            _validate_docker_token("image", None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Section C — build_env_args (validated argv constructor)
# ---------------------------------------------------------------------------


class TestBuildEnvArgs:
    def test_emits_alternating_flag_value_pairs(self):
        out = build_env_args([("A", "1"), ("B", "2")])
        assert out == ["-e", "A=1", "-e", "B=2"]

    def test_empty_input_returns_empty_list(self):
        assert build_env_args([]) == []
        assert build_env_args({}) == []

    def test_accepts_dict_input(self):
        # Python dicts preserve insertion order since 3.7.
        out = build_env_args({"A": "1", "B": "2"})
        assert out == ["-e", "A=1", "-e", "B=2"]

    def test_preserves_empty_value_for_proxy_clear_pattern(self):
        # start_container uses this to clear an inherited proxy var inside the
        # container; the '=' MUST remain so docker treats it as 'set to empty'
        # rather than 'pass through host value'.
        out = build_env_args([("PROXY", "")])
        assert out == ["-e", "PROXY="]

    def test_rejects_first_bad_pair_loudly(self):
        with pytest.raises(ValueError):
            build_env_args([("OK", "ok"), ("BAD", "--rm")])


# ---------------------------------------------------------------------------
# Section D — start_container (docker_utils.py site 4) integration
# ---------------------------------------------------------------------------


class _FakeCompleted:
    def __init__(self, returncode=0, stdout="abc123\n", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture
def capture_run(monkeypatch):
    """Capture every subprocess.run argv list without spawning anything."""
    calls: list[list[str]] = []

    def fake_run(cmd, *args, **kwargs):
        calls.append(list(cmd))
        return _FakeCompleted()

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def _import_docker_utils_fresh():
    """Re-import to pick up our monkey-patched subprocess.run."""
    if "src.utils.docker_utils" in sys.modules:
        del sys.modules["src.utils.docker_utils"]
    from src.utils import docker_utils  # noqa: WPS433

    return docker_utils


class TestStartContainerSite:
    def test_clean_task_id_and_image_produces_valid_argv(
        self, tmp_path, monkeypatch, capture_run
    ):
        monkeypatch.setenv("HTTP_PROXY_INNER", "http://proxy:8080")
        monkeypatch.setenv("HTTPS_PROXY_INNER", "http://proxy:8080")
        monkeypatch.setenv("DOCKER_IMAGE", "wildclawbench-ubuntu:v1.3")
        ws = tmp_path / "ws"
        ws.mkdir()

        du = _import_docker_utils_fresh()
        du.start_container("task-123", str(ws))

        # First call is the docker-run.
        cmd = capture_run[0]
        assert cmd[0:3] == ["docker", "run", "-d"]
        assert "--name" in cmd
        assert cmd[cmd.index("--name") + 1] == "task-123"
        # Every -e is followed by a single 'KEY=VALUE' token (validator invariant).
        for i, tok in enumerate(cmd):
            if tok == "-e":
                assert "=" in cmd[i + 1], f"-e token at {i} not KEY=VALUE: {cmd[i + 1]!r}"
                assert not cmd[i + 1].startswith("-")

    def test_flag_injecting_task_id_is_rejected(self, tmp_path, monkeypatch, capture_run):
        ws = tmp_path / "ws"
        ws.mkdir()
        du = _import_docker_utils_fresh()
        with pytest.raises(ValueError, match="argv-flag injection"):
            du.start_container("--privileged", str(ws))
        assert capture_run == []

    def test_flag_injecting_image_env_is_rejected(self, tmp_path, monkeypatch, capture_run):
        monkeypatch.setenv("DOCKER_IMAGE", "--privileged")
        ws = tmp_path / "ws"
        ws.mkdir()
        du = _import_docker_utils_fresh()
        with pytest.raises(ValueError, match="argv-flag injection"):
            du.start_container("task-1", str(ws))
        assert capture_run == []

    def test_flag_injecting_extra_env_value_is_rejected(
        self, tmp_path, monkeypatch, capture_run
    ):
        ws = tmp_path / "ws"
        ws.mkdir()
        monkeypatch.setenv("EVIL_KEY", "--privileged")
        du = _import_docker_utils_fresh()
        with pytest.raises(ValueError, match="argv-flag injection"):
            du.start_container("task-1", str(ws), extra_env="EVIL_KEY\n")
        assert capture_run == []

    def test_flag_injecting_lobster_env_value_is_rejected(
        self, tmp_path, monkeypatch, capture_run
    ):
        ws = tmp_path / "ws"
        ws.mkdir()
        monkeypatch.setenv("EVIL_KEY2", "-rm")
        du = _import_docker_utils_fresh()
        with pytest.raises(ValueError, match="argv-flag injection"):
            du.start_container("task-1", str(ws), lobster_env=["EVIL_KEY2"])
        assert capture_run == []

    def test_flag_injecting_extra_env_dict_value_is_rejected(
        self, tmp_path, monkeypatch, capture_run
    ):
        ws = tmp_path / "ws"
        ws.mkdir()
        du = _import_docker_utils_fresh()
        with pytest.raises(ValueError):
            du.start_container(
                "task-1",
                str(ws),
                extra_env_dict={"SKILL_URL": "--mount=/etc/passwd"},
            )
        assert capture_run == []

    def test_flag_injecting_network_is_rejected(self, tmp_path, monkeypatch, capture_run):
        ws = tmp_path / "ws"
        ws.mkdir()
        du = _import_docker_utils_fresh()
        with pytest.raises(ValueError, match="argv-flag injection"):
            du.start_container("task-1", str(ws), network="--net=host")
        assert capture_run == []


# ---------------------------------------------------------------------------
# Section E — litellm_sidecar.start_litellm (site 5) integration
# ---------------------------------------------------------------------------


class TestStartLitellmSite:
    def test_clean_inputs_produce_valid_argv(self, tmp_path, monkeypatch, capture_run):
        # start_litellm also probes the container with subsequent docker inspect/exec.
        # We capture every subprocess call and return success for all of them, then
        # assert just the first (docker run) is well-formed.
        from src.utils import litellm_sidecar as sidecar

        cfg = tmp_path / "config.yaml"
        cfg.write_text("model_list: []\n")

        # The function loops on a health-check; short-circuit by patching it.
        monkeypatch.setattr(sidecar, "wait_for_litellm_healthy", lambda *a, **kw: True)

        sidecar.start_litellm(
            container_name="litellm-test",
            network="kensei-net",
            host_config_path=str(cfg),
            master_key="mk-123",
        )
        # start_litellm prefaces with 'docker rm -f' cleanup; locate the run call.
        run_cmds = [c for c in capture_run if len(c) >= 2 and c[1] == "run"]
        assert run_cmds, f"no docker run call captured: {capture_run!r}"
        run_cmd = run_cmds[0]
        assert run_cmd[0:3] == ["docker", "run", "-d"]
        assert "--name" in run_cmd
        assert run_cmd[run_cmd.index("--name") + 1] == "litellm-test"
        assert "--network" in run_cmd
        assert run_cmd[run_cmd.index("--network") + 1] == "kensei-net"

    def test_flag_injecting_container_name_is_rejected(
        self, tmp_path, monkeypatch, capture_run
    ):
        from src.utils import litellm_sidecar as sidecar

        cfg = tmp_path / "config.yaml"
        cfg.write_text("model_list: []\n")
        monkeypatch.setattr(sidecar, "wait_for_litellm_healthy", lambda *a, **kw: True)

        with pytest.raises(ValueError, match="argv-flag injection"):
            sidecar.start_litellm(
                container_name="--rm",
                network="kensei-net",
                host_config_path=str(cfg),
                master_key="mk-123",
            )
        assert capture_run == []

    def test_flag_injecting_network_is_rejected(self, tmp_path, monkeypatch, capture_run):
        from src.utils import litellm_sidecar as sidecar

        cfg = tmp_path / "config.yaml"
        cfg.write_text("model_list: []\n")
        monkeypatch.setattr(sidecar, "wait_for_litellm_healthy", lambda *a, **kw: True)

        with pytest.raises(ValueError, match="argv-flag injection"):
            sidecar.start_litellm(
                container_name="litellm-test",
                network="--privileged",
                host_config_path=str(cfg),
                master_key="mk-123",
            )
        assert capture_run == []

    def test_flag_injecting_master_key_is_rejected(self, tmp_path, monkeypatch, capture_run):
        from src.utils import litellm_sidecar as sidecar

        cfg = tmp_path / "config.yaml"
        cfg.write_text("model_list: []\n")
        monkeypatch.setattr(sidecar, "wait_for_litellm_healthy", lambda *a, **kw: True)

        with pytest.raises(ValueError, match="argv-flag injection"):
            sidecar.start_litellm(
                container_name="litellm-test",
                network="kensei-net",
                host_config_path=str(cfg),
                master_key="--rm",
            )
        assert capture_run == []


# ---------------------------------------------------------------------------
# Section F — test_executor.run_tests_in_container (site 6) integration
# ---------------------------------------------------------------------------


class TestExecuteTestsSite:
    _TC = "def test_ok():\n    assert True\n"

    def test_clean_inputs_produce_valid_argv(self, tmp_path, monkeypatch, capture_run):
        from src.utils import test_executor

        ws = tmp_path / "ws"
        ws.mkdir()
        test_executor.execute_tests(
            test_code=self._TC,
            test_weights_json="{}",
            workspace_dir=ws,
            network="kensei-net",
            image="wildclawbench-ubuntu:v1.3",
        )
        run_cmds = [c for c in capture_run if len(c) >= 2 and c[1] == "run"]
        assert run_cmds, f"no docker run call captured: {capture_run!r}"
        run_cmd = run_cmds[0]
        assert run_cmd[0:2] == ["docker", "run"]
        assert "--network" in run_cmd
        assert run_cmd[run_cmd.index("--network") + 1] == "kensei-net"

    def test_flag_injecting_network_is_rejected(self, tmp_path, monkeypatch, capture_run):
        # execute_tests catches all exceptions and surfaces them as a result-dict
        # error so a single bad task can't crash an entire batch. Assert the
        # validator fires (via the result-dict error message) and no docker run
        # was issued.
        from src.utils import test_executor

        ws = tmp_path / "ws"
        ws.mkdir()
        result = test_executor.execute_tests(
            test_code=self._TC,
            test_weights_json="{}",
            workspace_dir=ws,
            network="--privileged",
            image="wildclawbench-ubuntu:v1.3",
        )
        assert "argv-flag injection" in result["error"]
        assert result["reward"] == 0.0
        run_cmds = [c for c in capture_run if len(c) >= 2 and c[1] == "run"]
        assert run_cmds == []

    def test_flag_injecting_image_is_rejected(self, tmp_path, monkeypatch, capture_run):
        from src.utils import test_executor

        ws = tmp_path / "ws"
        ws.mkdir()
        result = test_executor.execute_tests(
            test_code=self._TC,
            test_weights_json="{}",
            workspace_dir=ws,
            network="kensei-net",
            image="--privileged",
        )
        assert "argv-flag injection" in result["error"]
        run_cmds = [c for c in capture_run if len(c) >= 2 and c[1] == "run"]
        assert run_cmds == []

    def test_flag_injecting_mock_env_value_is_rejected(
        self, tmp_path, monkeypatch, capture_run
    ):
        from src.utils import test_executor

        ws = tmp_path / "ws"
        ws.mkdir()
        result = test_executor.execute_tests(
            test_code=self._TC,
            test_weights_json="{}",
            workspace_dir=ws,
            network="kensei-net",
            image="wildclawbench-ubuntu:v1.3",
            mock_env_dict={"FIGMA_URL": "--rm"},
        )
        assert "argv-flag injection" in result["error"]
        run_cmds = [c for c in capture_run if len(c) >= 2 and c[1] == "run"]
        assert run_cmds == []


# ---------------------------------------------------------------------------
# Section G — agent runner sites (1, 2, 3) integration
# ---------------------------------------------------------------------------
#
# We test each runner's _start_container by constructing a minimal instance
# and intercepting subprocess.run. Each runner has its own image override
# chain (DOCKER_IMAGE_<AGENT> -> <AGENT>_DOCKER_IMAGE -> default per
# src/agents/AGENTS.md); we set it in env or directly on self.image.


class TestClaudecodeRunnerSite:
    def _make(self, image="wildclawbench-claudecode-ubuntu:v0.2"):
        from src.agents.claudecode.runner import ClaudeCodeAgent

        agent = ClaudeCodeAgent.__new__(ClaudeCodeAgent)
        agent.api_key = "sk-x"
        agent.api_base_url = "https://api.anthropic.com"
        agent.openrouter_base_url = "https://openrouter.ai"
        agent.image = image
        return agent

    def test_clean_inputs_produce_valid_argv(self, tmp_path, capture_run):
        agent = self._make()
        ws = tmp_path / "ws"
        ws.mkdir()
        try:
            agent._start_container("task-cc-1", str(ws))
        except Exception:
            pass  # patch step after docker run will fail; we only need the argv
        assert capture_run
        cmd = capture_run[0]
        assert cmd[0:3] == ["docker", "run", "-d"]
        assert cmd[cmd.index("--name") + 1] == "task-cc-1"

    def test_flag_injecting_task_id_is_rejected(self, tmp_path, capture_run):
        agent = self._make()
        ws = tmp_path / "ws"
        ws.mkdir()
        with pytest.raises(ValueError, match="argv-flag injection"):
            agent._start_container("--privileged", str(ws))
        assert capture_run == []

    def test_flag_injecting_image_is_rejected(self, tmp_path, capture_run):
        agent = self._make(image="--privileged")
        ws = tmp_path / "ws"
        ws.mkdir()
        with pytest.raises(ValueError, match="argv-flag injection"):
            agent._start_container("task-cc-1", str(ws))
        assert capture_run == []


class TestCodexRunnerSite:
    def _make(self):
        from src.agents.codex.runner import CodexAgent

        agent = CodexAgent.__new__(CodexAgent)
        agent.openrouter_api_key = "sk-x"
        agent.openrouter_base_url = "https://openrouter.ai"
        agent.image = "wildclawbench-codex-ubuntu:v0.1"
        return agent

    def test_clean_inputs_produce_valid_argv(self, tmp_path, capture_run):
        agent = self._make()
        ws = tmp_path / "ws"
        (ws / "exec").mkdir(parents=True)
        agent._start_container("task-cx-1", str(ws), task={}, lobster={})
        assert capture_run
        cmd = capture_run[0]
        assert cmd[0:3] == ["docker", "run", "-d"]

    def test_attacker_keyed_extra_env_with_bad_key_is_rejected(
        self, tmp_path, monkeypatch, capture_run
    ):
        # task["env"] is a newline-list of *variable names*; bad key shape must fail.
        agent = self._make()
        ws = tmp_path / "ws"
        (ws / "exec").mkdir(parents=True)
        with pytest.raises(ValueError, match="invalid env var name"):
            agent._start_container(
                "task-cx-1",
                str(ws),
                task={"env": "BAD-KEY\n"},
                lobster={},
            )
        assert capture_run == []

    def test_attacker_keyed_lobster_env_with_flag_value_is_rejected(
        self, tmp_path, monkeypatch, capture_run
    ):
        agent = self._make()
        ws = tmp_path / "ws"
        (ws / "exec").mkdir(parents=True)
        monkeypatch.setenv("EVIL_LOB", "--rm")
        with pytest.raises(ValueError, match="argv-flag injection"):
            agent._start_container(
                "task-cx-1",
                str(ws),
                task={},
                lobster={"env": ["EVIL_LOB"]},
            )
        assert capture_run == []


class TestHermesRunnerSite:
    def _make(self):
        from src.agents.hermesagent.runner import HermesAgentAgent

        agent = HermesAgentAgent.__new__(HermesAgentAgent)
        agent.brave_api_key = "brv-x"
        agent.image = "wildclawbench-hermes-ubuntu:v0.1"
        return agent

    def test_clean_inputs_produce_valid_argv(self, tmp_path, capture_run):
        agent = self._make()
        ws = tmp_path / "ws"
        ws.mkdir()
        agent._start_container(
            "task-h-1", str(ws), api_key="sk-x", base_url="https://openrouter.ai"
        )
        assert capture_run
        cmd = capture_run[0]
        assert cmd[0:3] == ["docker", "run", "-d"]

    def test_flag_injecting_task_id_is_rejected(self, tmp_path, capture_run):
        agent = self._make()
        ws = tmp_path / "ws"
        ws.mkdir()
        with pytest.raises(ValueError, match="argv-flag injection"):
            agent._start_container(
                "--privileged", str(ws), api_key="sk-x", base_url="https://or"
            )
        assert capture_run == []

    def test_flag_injecting_image_is_rejected(self, tmp_path, capture_run):
        agent = self._make()
        agent.image = "--privileged"
        ws = tmp_path / "ws"
        ws.mkdir()
        with pytest.raises(ValueError, match="argv-flag injection"):
            agent._start_container(
                "task-h-1", str(ws), api_key="sk-x", base_url="https://or"
            )
        assert capture_run == []

    def test_attacker_keyed_extra_env_with_bad_key_is_rejected(
        self, tmp_path, monkeypatch, capture_run
    ):
        agent = self._make()
        ws = tmp_path / "ws"
        ws.mkdir()
        with pytest.raises(ValueError, match="invalid env var name"):
            agent._start_container(
                "task-h-1",
                str(ws),
                api_key="sk-x",
                base_url="https://or",
                extra_env="BAD-KEY\n",
            )
        assert capture_run == []
