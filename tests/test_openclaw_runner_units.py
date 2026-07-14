"""Unit tests for the OpenClaw agent backend (src/agents/openclaw/runner.py).

This is THE default agent backend (--agent-backend openclaw) and previously
had zero direct coverage. These tests exercise, with ALL subprocess / docker /
grading calls mocked (no docker daemon, no network, no AWS):

- _normalize_openrouter_model (pure model-id normalization)
- OpenClawAgent constructor + image_model env fallback
- expects_gateway / transcript_container_path properties
- prepare_grading_transcript (docker cp snapshot, success + failure)
- _wait_for_llm_route_ready (probe loop, warm / cold / no-config paths)
- collect_usage (litellm-log path, jsonl fallback, copy-failure path)
- _set_model (litellm anthropic branch, litellm gpt branch, openrouter branch)
- _inject_auth (litellm no-op, openai, openrouter, none)
- _set_image_model (litellm no-op vs openrouter config-set)
- _set_bootstrap_limits (verified, timeout, OSError, non-zero rc)
- _index_memory (MD token parsing: verified/missing/copy_failed)
- run_task (full happy path + litellm env wiring + agent-timeout + error path),
  with every docker_utils helper monkeypatched on the runner namespace.

Behavioral assertions inspect the exact argv / generated python script handed
to subprocess.run, matching the style of tests/test_docker_env_validation.py.
Some tests pin CURRENT behavior even where it looks surprising; those carry a
NOTE comment. Where the SCORING_AUDIT_REPORT.md file is referenced it documents
known defects — those tests intentionally lock in observed behavior.
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

from src.agents.base import AgentTaskSpec  # noqa: E402
from src.agents.openclaw import runner as ocr  # noqa: E402
from src.agents.openclaw.runner import (  # noqa: E402
    OpenClawAgent,
    _normalize_openrouter_model,
)


# ---------------------------------------------------------------------------
# Shared fakes / fixtures
# ---------------------------------------------------------------------------
class _FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class _RecordingRun:
    """Callable replacement for subprocess.run that records every invocation
    and returns a scripted result. ``result`` may be a single _FakeCompleted,
    a list consumed one-per-call, or a callable(cmd, kwargs)->_FakeCompleted."""

    def __init__(self, result=None):
        self.calls: list[dict] = []
        self._result = result if result is not None else _FakeCompleted()

    def __call__(self, cmd, *args, **kwargs):
        rec = {"cmd": list(cmd), "kwargs": kwargs, "input": kwargs.get("input")}
        self.calls.append(rec)
        r = self._result
        if callable(r) and not isinstance(r, _FakeCompleted):
            return r(cmd, kwargs)
        if isinstance(r, list):
            idx = min(len(self.calls) - 1, len(r) - 1)
            return r[idx]
        return r


@pytest.fixture
def rec_run(monkeypatch):
    r = _RecordingRun()
    monkeypatch.setattr(ocr.subprocess, "run", r)
    return r


def _bare_agent(**overrides):
    """Construct an OpenClawAgent without touching os.environ side effects
    beyond what __init__ needs. Callers override litellm_* to select branch."""
    kwargs = dict(
        gateway_port=8080,
        image_model="",  # explicit -> avoids OPENCLAW_IMAGE_MODEL env lookup
    )
    kwargs.update(overrides)
    return OpenClawAgent(**kwargs)


# ---------------------------------------------------------------------------
# _normalize_openrouter_model (pure)
# ---------------------------------------------------------------------------
class TestNormalizeOpenrouterModel:
    def test_already_openrouter_prefixed_passes_through(self):
        assert _normalize_openrouter_model("openrouter/anthropic/x") == "openrouter/anthropic/x"

    def test_slash_without_prefix_gets_openrouter_prefix(self):
        assert _normalize_openrouter_model("meta/llama-3") == "openrouter/meta/llama-3"

    def test_gpt_family_routes_to_openai_namespace(self):
        assert _normalize_openrouter_model("gpt-5.5") == "openrouter/openai/gpt-5.5"

    @pytest.mark.parametrize("m", ["o1-mini", "o3", "llama-70b", "mistral-large", "kimi-k2", "deepseek", "gemini-2", "qwen-2"])
    def test_all_gpt_prefix_families_go_openai(self, m):
        assert _normalize_openrouter_model(m) == f"openrouter/openai/{m}"

    def test_prefix_match_is_case_insensitive(self):
        assert _normalize_openrouter_model("GPT-4o") == "openrouter/openai/GPT-4o"

    def test_bare_anthropic_style_defaults_to_anthropic_namespace(self):
        assert _normalize_openrouter_model("claude-opus-4.7") == "openrouter/anthropic/claude-opus-4.7"

    def test_empty_string_defaults_to_anthropic(self):
        # NOTE: pins current behavior — an empty model string still gets the
        # anthropic namespace prefix rather than raising.
        assert _normalize_openrouter_model("") == "openrouter/anthropic/"


# ---------------------------------------------------------------------------
# Constructor + properties
# ---------------------------------------------------------------------------
class TestConstructorAndProperties:
    def test_defaults_populated(self):
        a = _bare_agent()
        assert a.gateway_port == 8080
        assert a.openrouter_base_url == "https://openrouter.ai/api/v1"
        assert a.litellm_port == 4000
        assert a._task_windows == {}

    def test_image_model_explicit_empty_stays_empty(self, monkeypatch):
        monkeypatch.setenv("OPENCLAW_IMAGE_MODEL", "should-not-be-read")
        # image_model passed explicitly as "" (not None) -> env NOT consulted.
        a = OpenClawAgent(gateway_port=1, image_model="")
        assert a.image_model == ""

    def test_image_model_none_falls_back_to_env_stripped(self, monkeypatch):
        monkeypatch.setenv("OPENCLAW_IMAGE_MODEL", "  gpt-image-1  ")
        a = OpenClawAgent(gateway_port=1, image_model=None)
        assert a.image_model == "gpt-image-1"

    def test_image_model_none_without_env_is_empty(self, monkeypatch):
        monkeypatch.delenv("OPENCLAW_IMAGE_MODEL", raising=False)
        a = OpenClawAgent(gateway_port=1, image_model=None)
        assert a.image_model == ""

    def test_expects_gateway_true(self):
        assert _bare_agent().expects_gateway is True

    def test_transcript_container_path(self):
        assert (
            _bare_agent().transcript_container_path
            == "/root/.openclaw/agents/main/sessions/chat.jsonl"
        )


# ---------------------------------------------------------------------------
# prepare_grading_transcript
# ---------------------------------------------------------------------------
class TestPrepareGradingTranscript:
    def test_returns_host_snapshot_when_cp_succeeds(self, monkeypatch, tmp_path):
        a = _bare_agent()
        # Point gettempdir at tmp_path and make the snapshot file "exist" nonempty.
        monkeypatch.setattr(ocr.tempfile, "gettempdir", lambda: str(tmp_path))
        snap = tmp_path / "chat-snap-task42.jsonl"

        def fake_run(cmd, *a2, **k2):
            # simulate docker cp writing bytes
            snap.write_text('{"x":1}\n')
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(ocr.subprocess, "run", fake_run)
        out = a.prepare_grading_transcript("task42")
        assert out == str(snap)

    def test_falls_back_to_container_path_when_cp_fails(self, monkeypatch, tmp_path):
        a = _bare_agent()
        monkeypatch.setattr(ocr.tempfile, "gettempdir", lambda: str(tmp_path))
        monkeypatch.setattr(
            ocr.subprocess, "run",
            lambda *a2, **k2: _FakeCompleted(returncode=1, stderr="boom"),
        )
        out = a.prepare_grading_transcript("taskX")
        assert out == a.transcript_container_path

    def test_falls_back_when_snapshot_empty(self, monkeypatch, tmp_path):
        a = _bare_agent()
        monkeypatch.setattr(ocr.tempfile, "gettempdir", lambda: str(tmp_path))
        snap = tmp_path / "chat-snap-empty.jsonl"

        def fake_run(cmd, *a2, **k2):
            snap.write_text("")  # zero bytes
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(ocr.subprocess, "run", fake_run)
        assert a.prepare_grading_transcript("empty") == a.transcript_container_path

    def test_subprocess_error_is_swallowed(self, monkeypatch, tmp_path):
        a = _bare_agent()
        monkeypatch.setattr(ocr.tempfile, "gettempdir", lambda: str(tmp_path))

        def boom(*a2, **k2):
            raise subprocess.SubprocessError("nope")

        monkeypatch.setattr(ocr.subprocess, "run", boom)
        assert a.prepare_grading_transcript("t") == a.transcript_container_path


# ---------------------------------------------------------------------------
# _wait_for_llm_route_ready
# ---------------------------------------------------------------------------
class TestWaitForLlmRouteReady:
    def test_returns_true_immediately_without_litellm_config(self, rec_run):
        a = _bare_agent()  # no litellm_config_yaml/container_name
        assert a._wait_for_llm_route_ready("t") is True
        assert rec_run.calls == []  # never probes

    def test_warm_on_first_probe(self, monkeypatch):
        a = _bare_agent(litellm_config_yaml="x.yaml", litellm_container_name="ll")
        rec = _RecordingRun(_FakeCompleted(returncode=0))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        slept: list[float] = []
        monkeypatch.setattr(ocr.time, "sleep", lambda s: slept.append(s))
        assert a._wait_for_llm_route_ready("t", attempts=5, interval=0.01) is True
        assert len(rec.calls) == 1
        assert slept == []  # no sleep once warm
        # probe exercises the container base url via docker exec python3 -c
        cmd = rec.calls[0]["cmd"]
        assert cmd[:4] == ["docker", "exec", "t", "python3"]
        assert "http://ll:4000/health/liveliness" in cmd[-1]

    def test_cold_then_warm_sleeps_between(self, monkeypatch):
        a = _bare_agent(litellm_config_yaml="x.yaml", litellm_container_name="ll")
        results = [_FakeCompleted(returncode=1), _FakeCompleted(returncode=0)]
        rec = _RecordingRun(results)
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        slept: list[float] = []
        monkeypatch.setattr(ocr.time, "sleep", lambda s: slept.append(s))
        assert a._wait_for_llm_route_ready("t", attempts=5, interval=0.25) is True
        assert len(rec.calls) == 2
        assert slept == [0.25]  # slept once after the cold probe

    def test_never_warm_returns_false_after_all_attempts(self, monkeypatch):
        a = _bare_agent(litellm_config_yaml="x.yaml", litellm_container_name="ll")
        rec = _RecordingRun(_FakeCompleted(returncode=1))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        monkeypatch.setattr(ocr.time, "sleep", lambda s: None)
        assert a._wait_for_llm_route_ready("t", attempts=3, interval=0.0) is False
        assert len(rec.calls) == 3

    def test_probe_timeout_is_treated_as_cold(self, monkeypatch):
        a = _bare_agent(litellm_config_yaml="x.yaml", litellm_container_name="ll")

        def timeout_run(*a2, **k2):
            raise subprocess.TimeoutExpired(cmd="docker", timeout=1)

        monkeypatch.setattr(ocr.subprocess, "run", timeout_run)
        monkeypatch.setattr(ocr.time, "sleep", lambda s: None)
        assert a._wait_for_llm_route_ready("t", attempts=2, interval=0.0) is False

    def test_oserror_on_exec_returns_false_immediately(self, monkeypatch):
        a = _bare_agent(litellm_config_yaml="x.yaml", litellm_container_name="ll")

        def oserr(*a2, **k2):
            raise OSError("docker missing")

        monkeypatch.setattr(ocr.subprocess, "run", oserr)
        assert a._wait_for_llm_route_ready("t", attempts=5, interval=0.0) is False


# ---------------------------------------------------------------------------
# collect_usage
# ---------------------------------------------------------------------------
class TestCollectUsage:
    def test_litellm_log_path_used_when_window_present(self, monkeypatch, tmp_path):
        a = _bare_agent(litellm_usage_log=str(tmp_path / "usage.jsonl"))
        a._task_windows["task"] = (100.0, 200.0)

        monkeypatch.setattr(ocr.subprocess, "run", lambda *a2, **k2: _FakeCompleted(0))
        monkeypatch.setattr(
            ocr, "extract_usage_from_litellm_log",
            lambda p, s, e: {"request_count": 3, "total_tokens": 42},
        )
        monkeypatch.setattr(
            ocr, "extract_preflight_usage_from_litellm_log",
            lambda p: {"request_count": 0},
        )
        monkeypatch.setattr(ocr, "extract_usage_from_jsonl", lambda p: {"request_count": 99})

        out = a.collect_usage("task", tmp_path / "od", 12.345)
        assert out["request_count"] == 3
        assert out["total_tokens"] == 42
        assert out["elapsed_time"] == 12.35  # rounded to 2dp
        # preflight had 0 requests -> not attached
        assert "__preflight__" not in out
        # window consumed / popped
        assert "task" not in a._task_windows

    def test_preflight_attached_when_nonzero(self, monkeypatch, tmp_path):
        a = _bare_agent(litellm_usage_log=str(tmp_path / "u.jsonl"))
        a._task_windows["t"] = (1.0, 2.0)
        monkeypatch.setattr(ocr.subprocess, "run", lambda *a2, **k2: _FakeCompleted(0))
        monkeypatch.setattr(ocr, "extract_usage_from_litellm_log", lambda p, s, e: {"request_count": 1})
        monkeypatch.setattr(ocr, "extract_preflight_usage_from_litellm_log", lambda p: {"request_count": 2, "cost_usd": 0.1})
        out = a.collect_usage("t", tmp_path / "od", 1.0)
        assert out["__preflight__"] == {"request_count": 2, "cost_usd": 0.1}

    def test_synthesizes_window_when_missing(self, monkeypatch, tmp_path):
        a = _bare_agent(litellm_usage_log=str(tmp_path / "u.jsonl"))
        captured = {}

        def fake_extract(p, s, e):
            captured["s"], captured["e"] = s, e
            return {"request_count": 1}

        monkeypatch.setattr(ocr.subprocess, "run", lambda *a2, **k2: _FakeCompleted(0))
        monkeypatch.setattr(ocr, "extract_usage_from_litellm_log", fake_extract)
        monkeypatch.setattr(ocr, "extract_preflight_usage_from_litellm_log", lambda p: {"request_count": 0})
        a.collect_usage("no-window", tmp_path / "od", 5.0)
        # window synthesized: end-start ~= max(elapsed,1)
        assert captured["e"] - captured["s"] == pytest.approx(5.0, abs=0.5)

    def test_falls_back_to_jsonl_when_no_usage_log_and_cp_ok(self, monkeypatch, tmp_path):
        a = _bare_agent(litellm_usage_log="")  # no litellm log -> request_count 0
        od = tmp_path / "od"
        transcript = od / "chat.jsonl"

        def fake_run(cmd, *a2, **k2):
            od.mkdir(parents=True, exist_ok=True)
            transcript.write_text("{}\n")
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(ocr.subprocess, "run", fake_run)
        monkeypatch.setattr(ocr, "extract_usage_from_jsonl", lambda p: {"request_count": 7, "usage_source": "jsonl"})
        out = a.collect_usage("t", od, 3.0)
        assert out["request_count"] == 7
        assert out["usage_source"] == "jsonl"
        assert out["elapsed_time"] == 3.0

    def test_zero_usage_and_cp_fail_returns_zero_block(self, monkeypatch, tmp_path):
        a = _bare_agent(litellm_usage_log="")
        od = tmp_path / "od"
        # cp fails -> transcript never created
        monkeypatch.setattr(ocr.subprocess, "run", lambda *a2, **k2: _FakeCompleted(returncode=1, stderr="no such container"))
        out = a.collect_usage("t", od, 0.0)
        assert out["usage_source"] == "none"
        assert out["request_count"] == 0
        assert out["total_tokens"] == 0
        assert out["cost_usd"] == 0.0
        assert out["elapsed_time"] == 0.0


# ---------------------------------------------------------------------------
# _set_model — litellm anthropic branch
# ---------------------------------------------------------------------------
def _extract_script(rec: _RecordingRun) -> str:
    """Return the python script passed via input= to the last recorded call."""
    return rec.calls[-1]["input"]


class TestSetModelLitellmAnthropic:
    def _run(self, monkeypatch, model="claude-opus-4.7", thinking=None):
        a = _bare_agent(
            litellm_config_yaml="/x.yaml",
            litellm_container_name="ll-sidecar",
            litellm_port=4000,
            litellm_master_key="mk-secret",
        )
        rec = _RecordingRun(_FakeCompleted(returncode=0))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._set_model("task", model, thinking=thinking)
        return rec

    def test_argv_is_docker_exec_python_stdin(self, monkeypatch):
        rec = self._run(monkeypatch)
        cmd = rec.calls[0]["cmd"]
        assert cmd == ["docker", "exec", "-i", "task", "python3", "-"]

    def test_registers_anthropic_provider_with_recognized_model_id(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch))
        # provider key "anthropic" and recognized allowlist id claude-opus-4-6.
        # The provider dict is embedded as a json.dumps(json.dumps(...)) string
        # literal, so inner quotes are backslash-escaped in the emitted script.
        assert '"anthropic"' in script
        assert "claude-opus-4-6" in script
        assert "anthropic-messages" in script

    def test_base_url_points_at_sidecar_root_no_v1_for_anthropic(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch))
        # anthropic branch uses base_url_root (no /v1 suffix in the provider baseUrl)
        assert "http://ll-sidecar:4000" in script
        # master key threaded in
        assert "mk-secret" in script

    def test_thinking_default_written_when_set(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch, thinking="xhigh"))
        assert 'defaults["thinkingDefault"] = "xhigh"' in script

    @pytest.mark.parametrize("off", ["off", "none", "disabled", "  OFF  ", ""])
    def test_thinking_default_omitted_when_off_or_blank(self, monkeypatch, off):
        script = _extract_script(self._run(monkeypatch, thinking=off))
        assert "thinkingDefault" not in script

    def test_strips_litellm_prefix_from_model_id(self, monkeypatch):
        # "litellm/claude-opus-4.7" -> id claude-opus-4.7 -> still anthropic
        script = _extract_script(self._run(monkeypatch, model="litellm/claude-opus-4.7"))
        assert "claude-opus-4-6" in script  # recognized id substituted

    def test_browser_and_web_tools_disabled(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch))
        assert '"browser"' in script
        assert 'web["search"] = {{"enabled": False}}'.replace("{{", "{").replace("}}", "}") in script
        assert '"deny"' in script
        assert '"security"' in script  # exec security=full

    def test_nonzero_rc_raises_runtime_error(self, monkeypatch):
        a = _bare_agent(litellm_config_yaml="/x", litellm_container_name="ll")
        monkeypatch.setattr(ocr.subprocess, "run", lambda *a2, **k2: _FakeCompleted(returncode=2, stderr="bad json"))
        with pytest.raises(RuntimeError, match="Model setup failed"):
            a._set_model("t", "claude-opus-4.7")


class TestSetModelLitellmGpt:
    def _run(self, monkeypatch, model="gpt-5.5"):
        a = _bare_agent(
            litellm_config_yaml="/x.yaml",
            litellm_container_name="ll-sidecar",
            litellm_master_key="mk",
        )
        rec = _RecordingRun(_FakeCompleted(returncode=0))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._set_model("task", model)
        return rec

    def test_gpt_uses_litellm_provider_key_and_openai_completions(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch))
        assert '"litellm"' in script  # provider key literal for non-anthropic
        # provider dict is an escaped json-string literal -> match value only.
        assert "openai-completions" in script
        # base_url ends with /v1 for the openai-completions branch
        assert "http://ll-sidecar:4000/v1" in script
        assert "gpt-5.5" in script

    def test_gpt_registers_openai_vision_sidecar_provider(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch))
        assert "gpt-4o" in script
        assert "gpt-4o-mini" in script


class TestSetModelOpenrouter:
    def _run(self, monkeypatch, model="claude-opus-4.7"):
        a = _bare_agent()  # no litellm config -> openrouter branch
        rec = _RecordingRun(_FakeCompleted(returncode=0))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._set_model("task", model)
        return rec

    def test_writes_normalized_primary_model(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch, "claude-opus-4.7"))
        assert "openrouter/anthropic/claude-opus-4.7" in script
        # openrouter branch seeds defaults["models"][normalized] = {}
        assert 'defaults.setdefault("models"' in script

    def test_gpt_model_normalized_in_openrouter_branch(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch, "gpt-5.5"))
        assert "openrouter/openai/gpt-5.5" in script

    def test_openrouter_branch_disables_browser_and_web(self, monkeypatch):
        script = _extract_script(self._run(monkeypatch))
        assert '"deny"' in script
        assert '"security"' in script


# ---------------------------------------------------------------------------
# _inject_auth
# ---------------------------------------------------------------------------
class TestInjectAuth:
    def test_litellm_mode_is_noop(self, rec_run):
        a = _bare_agent(litellm_config_yaml="/x.yaml")
        a._inject_auth("t")
        assert rec_run.calls == []  # no docker exec at all

    def test_openai_only_injects_openai_profile(self, monkeypatch):
        a = _bare_agent(openai_api_key="sk-openai")
        rec = _RecordingRun(_FakeCompleted(0))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._inject_auth("t")
        script = _extract_script(rec)
        assert "openai:default" in script
        assert "sk-openai" in script
        assert '"provider": "openai"' in script

    def test_openrouter_key_injects_openrouter_profile(self, monkeypatch):
        a = _bare_agent(openrouter_api_key="sk-or")
        rec = _RecordingRun(_FakeCompleted(0))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._inject_auth("t")
        script = _extract_script(rec)
        assert "openrouter:default" in script
        assert "sk-or" in script

    def test_openrouter_takes_precedence_over_openai(self, monkeypatch):
        # both keys set -> openai branch requires openrouter absent, so openrouter wins
        a = _bare_agent(openai_api_key="sk-openai", openrouter_api_key="sk-or")
        rec = _RecordingRun(_FakeCompleted(0))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._inject_auth("t")
        script = _extract_script(rec)
        assert "openrouter:default" in script
        assert "openai:default" not in script

    def test_no_keys_is_noop(self, rec_run):
        a = _bare_agent()  # no keys, no litellm
        a._inject_auth("t")
        assert rec_run.calls == []


# ---------------------------------------------------------------------------
# _set_image_model
# ---------------------------------------------------------------------------
class TestSetImageModel:
    def test_litellm_mode_is_noop(self, rec_run):
        a = _bare_agent(litellm_config_yaml="/x.yaml")
        a._set_image_model("t", "gpt-image-1")
        assert rec_run.calls == []

    def test_openrouter_mode_runs_config_set(self, monkeypatch):
        a = _bare_agent()
        rec = _RecordingRun(_FakeCompleted(0))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._set_image_model("t", "some-image-model")
        cmd = rec.calls[0]["cmd"]
        assert cmd[:4] == ["docker", "exec", "t", "/bin/bash"]
        joined = cmd[-1]
        assert "openclaw config set agents.defaults.imageModel.primary 'some-image-model'" in joined


# ---------------------------------------------------------------------------
# _set_bootstrap_limits
# ---------------------------------------------------------------------------
class TestSetBootstrapLimits:
    def test_verified_success_path(self, monkeypatch):
        a = _bare_agent()
        stdout = "per=1000000000\ntotal=1000000000\n"
        rec = _RecordingRun(_FakeCompleted(returncode=0, stdout=stdout))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        # should not raise; docker exec with a timeout kwarg
        a._set_bootstrap_limits("t")
        assert rec.calls[0]["kwargs"].get("timeout") == 90
        assert rec.calls[0]["cmd"][:2] == ["docker", "exec"]

    def test_timeout_is_swallowed(self, monkeypatch):
        a = _bare_agent()

        def timeout_run(*a2, **k2):
            raise subprocess.TimeoutExpired(cmd="docker", timeout=90)

        monkeypatch.setattr(ocr.subprocess, "run", timeout_run)
        # must not raise
        a._set_bootstrap_limits("t")

    def test_oserror_is_swallowed(self, monkeypatch):
        a = _bare_agent()
        monkeypatch.setattr(ocr.subprocess, "run", lambda *a2, **k2: (_ for _ in ()).throw(OSError("x")))
        a._set_bootstrap_limits("t")

    def test_nonzero_rc_does_not_raise(self, monkeypatch):
        a = _bare_agent()
        rec = _RecordingRun(_FakeCompleted(returncode=1, stdout="", stderr="err"))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._set_bootstrap_limits("t")  # logs warning, no raise

    def test_custom_limits_appear_in_command(self, monkeypatch):
        a = _bare_agent()
        rec = _RecordingRun(_FakeCompleted(returncode=0, stdout="per=5\ntotal=9\n"))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._set_bootstrap_limits("t", per_file_chars=5, total_chars=9)
        joined = rec.calls[0]["cmd"][-1]
        assert "bootstrapMaxChars 5" in joined
        assert "bootstrapTotalMaxChars 9" in joined


# ---------------------------------------------------------------------------
# _index_memory (MD token parsing)
# ---------------------------------------------------------------------------
class TestIndexMemory:
    def test_parses_verified_missing_and_failed_tokens(self, monkeypatch):
        a = _bare_agent()
        stdout = (
            "MD:MEMORY.md:verified\n"
            "MD:SOUL.md:missing\n"
            "MD:AGENT.md:copy_failed\n"
            "MD:2026-07-09.md:verified\n"
            "---INDEX---\n"
            "indexed 4 files ok\n"
        )
        rec = _RecordingRun(_FakeCompleted(returncode=0, stdout=stdout))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        # Should complete without raising, exercising all three token branches.
        a._index_memory("t")
        cmd = rec.calls[0]["cmd"]
        assert cmd[:2] == ["docker", "exec"]
        # command seeds /root/memory and runs openclaw memory index
        assert "openclaw memory index --force" in cmd[-1]

    def test_nonzero_rc_is_handled(self, monkeypatch):
        a = _bare_agent()
        rec = _RecordingRun(_FakeCompleted(returncode=3, stdout="", stderr="index blew up"))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._index_memory("t")  # warning path, no raise

    def test_empty_stdout_is_handled(self, monkeypatch):
        a = _bare_agent()
        rec = _RecordingRun(_FakeCompleted(returncode=0, stdout=""))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._index_memory("t")

    def test_ignores_non_md_lines(self, monkeypatch):
        a = _bare_agent()
        stdout = "random noise\nMD:MEMORY.md:verified\nmore noise\n---INDEX---\nok\n"
        rec = _RecordingRun(_FakeCompleted(returncode=0, stdout=stdout))
        monkeypatch.setattr(ocr.subprocess, "run", rec)
        a._index_memory("t")


# ---------------------------------------------------------------------------
# run_task — full orchestration with docker_utils helpers monkeypatched
# ---------------------------------------------------------------------------
class _FakeProc:
    def __init__(self, returncode=0):
        self.returncode = returncode
        self.waited = False
        self.killed = False

    def poll(self):
        # Gateway-readiness polling treats a live process as None (still
        # running); the fakes never "exit" during the readiness window.
        return None

    def wait(self, timeout=None):
        self.waited = True
        return self.returncode

    def kill(self):
        self.killed = True


def _neutralize_docker_helpers(monkeypatch, run_background_procs):
    """Stub every docker_utils helper imported into the runner namespace so
    run_task performs no real docker/network work. run_background returns
    procs from the provided iterator (gateway first, then agent)."""
    for name in (
        "start_container",
        "inject_lobster_workspace",
        "inject_data_into_workspace",
        "inject_persona_into_workspace",
        "inject_openclaw_models",
        "inject_api_connectors",
        "run_warmup",
        "setup_skills",
        "setup_workspace",
        "snapshot_workspace_state",
    ):
        monkeypatch.setattr(ocr, name, lambda *a, **k: None)
    procs = iter(run_background_procs)
    monkeypatch.setattr(ocr, "run_background", lambda *a, **k: next(procs))
    monkeypatch.setattr(ocr.time, "sleep", lambda *a, **k: None)
    monkeypatch.setattr(ocr.time, "perf_counter", lambda: 1000.0)
    monkeypatch.setattr(ocr.time, "time", lambda: 5000.0)


def _make_spec(tmp_path, **overrides):
    ws = tmp_path / "ws"
    ws.mkdir(exist_ok=True)
    out = tmp_path / "out"
    out.mkdir(exist_ok=True)
    task = overrides.pop("task", {})
    base = dict(
        task_id="task-run-1",
        task=task,
        workspace_path=str(ws),
        prompt="do the thing",
        timeout_seconds=30,
        output_dir=out,
        model="claude-opus-4.7",
        thinking=None,
        models_config=None,
        lobster=None,
    )
    base.update(overrides)
    return AgentTaskSpec(**base)


class TestRunTaskHappyPath:
    def _stub_agent_methods(self, monkeypatch, agent):
        # Stub the agent's own docker-touching helper methods.
        monkeypatch.setattr(agent, "_set_bootstrap_limits", lambda *a, **k: None)
        monkeypatch.setattr(agent, "_index_memory", lambda *a, **k: None)
        monkeypatch.setattr(agent, "_set_model", lambda *a, **k: None)
        monkeypatch.setattr(agent, "_inject_auth", lambda *a, **k: None)
        monkeypatch.setattr(agent, "_set_image_model", lambda *a, **k: None)
        monkeypatch.setattr(agent, "_wait_for_llm_route_ready", lambda *a, **k: True)

    def test_returns_execution_with_procs_and_timing(self, monkeypatch, tmp_path):
        a = _bare_agent()
        gw, ag = _FakeProc(returncode=0), _FakeProc(returncode=0)
        _neutralize_docker_helpers(monkeypatch, [gw, ag])
        self._stub_agent_methods(monkeypatch, a)
        spec = _make_spec(tmp_path)

        result = a.run_task(spec)
        assert result.error is None
        assert result.gateway_proc is gw
        assert result.agent_proc is ag
        # perf_counter frozen at 1000 -> elapsed 0.0
        assert result.elapsed_time == 0.0
        # task window recorded (time frozen at 5000)
        assert a._task_windows[spec.task_id] == (5000.0, 5000.0)

    def test_exec_path_created(self, monkeypatch, tmp_path):
        a = _bare_agent()
        _neutralize_docker_helpers(monkeypatch, [_FakeProc(), _FakeProc()])
        self._stub_agent_methods(monkeypatch, a)
        spec = _make_spec(tmp_path)
        a.run_task(spec)
        assert (Path(spec.workspace_path) / "exec").is_dir()

    def test_litellm_mode_wires_anthropic_base_url_env(self, monkeypatch, tmp_path):
        a = _bare_agent(
            litellm_config_yaml="/x.yaml",
            litellm_container_name="ll",
            litellm_port=4000,
            litellm_master_key="mk",
        )
        captured = {}

        def capture_start(task_id, exec_path, **kwargs):
            captured.update(kwargs)

        monkeypatch.setattr(ocr, "start_container", capture_start)
        for name in (
            "inject_lobster_workspace", "inject_data_into_workspace",
            "inject_persona_into_workspace", "inject_openclaw_models",
            "inject_api_connectors", "run_warmup", "setup_skills",
            "setup_workspace", "snapshot_workspace_state",
        ):
            monkeypatch.setattr(ocr, name, lambda *a2, **k2: None)
        procs = iter([_FakeProc(), _FakeProc()])
        monkeypatch.setattr(ocr, "run_background", lambda *a2, **k2: next(procs))
        monkeypatch.setattr(ocr.time, "sleep", lambda *a2, **k2: None)
        monkeypatch.setattr(ocr.time, "perf_counter", lambda: 0.0)
        monkeypatch.setattr(ocr.time, "time", lambda: 1.0)
        self._stub_agent_methods(monkeypatch, a)

        spec = _make_spec(tmp_path, model="claude-opus-4.7")
        a.run_task(spec)
        env = captured["extra_env_dict"]
        assert env["WCB_AUDIO_TRANSCRIBE_URL"] == "http://ll:4000/v1/audio/transcriptions"
        assert env["WCB_AUDIO_TRANSCRIBE_AUTH"] == "mk"
        # claude model -> ANTHROPIC_* overrides pointing at sidecar
        assert env["ANTHROPIC_BASE_URL"] == "http://ll:4000"
        assert env["ANTHROPIC_AUTH_TOKEN"] == "mk"
        assert env["ANTHROPIC_API_KEY"] == "mk"
        # network threaded through
        assert captured["network"] == a.litellm_network

    def test_non_claude_model_skips_anthropic_env_overrides(self, monkeypatch, tmp_path):
        a = _bare_agent(
            litellm_config_yaml="/x.yaml",
            litellm_container_name="ll",
            litellm_master_key="mk",
        )
        captured = {}
        monkeypatch.setattr(ocr, "start_container", lambda tid, ep, **kw: captured.update(kw))
        for name in (
            "inject_lobster_workspace", "inject_data_into_workspace",
            "inject_persona_into_workspace", "inject_openclaw_models",
            "inject_api_connectors", "run_warmup", "setup_skills",
            "setup_workspace", "snapshot_workspace_state",
        ):
            monkeypatch.setattr(ocr, name, lambda *a2, **k2: None)
        procs = iter([_FakeProc(), _FakeProc()])
        monkeypatch.setattr(ocr, "run_background", lambda *a2, **k2: next(procs))
        monkeypatch.setattr(ocr.time, "sleep", lambda *a2, **k2: None)
        monkeypatch.setattr(ocr.time, "perf_counter", lambda: 0.0)
        monkeypatch.setattr(ocr.time, "time", lambda: 1.0)
        self._stub_agent_methods(monkeypatch, a)

        spec = _make_spec(tmp_path, model="gpt-5.5")
        a.run_task(spec)
        env = captured["extra_env_dict"]
        # audio env still set (litellm mode) but NO anthropic overrides for gpt
        assert "WCB_AUDIO_TRANSCRIBE_URL" in env
        assert "ANTHROPIC_BASE_URL" not in env

    def test_agent_timeout_kills_process(self, monkeypatch, tmp_path):
        a = _bare_agent()

        class _TimeoutProc(_FakeProc):
            def __init__(self):
                super().__init__()
                self._first = True

            def wait(self, timeout=None):
                if self._first and timeout is not None:
                    self._first = False
                    raise subprocess.TimeoutExpired(cmd="agent", timeout=timeout)
                self.waited = True
                return 0

        gw = _FakeProc()
        agent_proc = _TimeoutProc()
        _neutralize_docker_helpers(monkeypatch, [gw, agent_proc])
        self._stub_agent_methods(monkeypatch, a)
        spec = _make_spec(tmp_path, timeout_seconds=15)
        result = a.run_task(spec)
        assert agent_proc.killed is True
        # timeout path sets elapsed to the timeout value
        assert result.elapsed_time == float(15)
        assert result.error is None

    def test_exception_path_returns_error_execution(self, monkeypatch, tmp_path):
        a = _bare_agent()

        def boom(*a2, **k2):
            raise RuntimeError("start_container exploded")

        monkeypatch.setattr(ocr, "start_container", boom)
        monkeypatch.setattr(ocr.time, "sleep", lambda *a2, **k2: None)
        spec = _make_spec(tmp_path)
        result = a.run_task(spec)
        assert result.error == "start_container exploded"
        assert result.elapsed_time == float(spec.timeout_seconds)

    def test_openrouter_gateway_cmd_exports_keys(self, monkeypatch, tmp_path):
        a = _bare_agent(openrouter_api_key="sk-or", openai_api_key="sk-oai")
        captured_cmds = []

        def capture_bg(task_id, bash_cmd=None, log_path=None, **k):
            captured_cmds.append(bash_cmd)
            return _FakeProc()

        for name in (
            "start_container", "inject_lobster_workspace", "inject_data_into_workspace",
            "inject_persona_into_workspace", "inject_openclaw_models",
            "inject_api_connectors", "run_warmup", "setup_skills",
            "setup_workspace", "snapshot_workspace_state",
        ):
            monkeypatch.setattr(ocr, name, lambda *a2, **k2: None)
        monkeypatch.setattr(ocr, "run_background", capture_bg)
        monkeypatch.setattr(ocr.time, "sleep", lambda *a2, **k2: None)
        monkeypatch.setattr(ocr.time, "perf_counter", lambda: 0.0)
        monkeypatch.setattr(ocr.time, "time", lambda: 1.0)
        self._stub_agent_methods(monkeypatch, a)

        spec = _make_spec(tmp_path)
        a.run_task(spec)
        gateway_cmd = captured_cmds[0]
        assert "export OPENROUTER_API_KEY='sk-or'" in gateway_cmd
        assert "export OPENAI_API_KEY='sk-oai'" in gateway_cmd
        assert f"openclaw gateway --port {a.gateway_port}" in gateway_cmd

    def test_all_optional_injection_branches_fire(self, monkeypatch, tmp_path):
        # Exercise the conditional injection paths in run_task: lobster,
        # persona_dir, data_dir and models_config. Record which helpers ran.
        a = _bare_agent()
        called: dict[str, int] = {}

        def mk(name):
            def _f(*a2, **k2):
                called[name] = called.get(name, 0) + 1
            return _f

        for name in (
            "start_container", "inject_lobster_workspace", "inject_data_into_workspace",
            "inject_persona_into_workspace", "inject_openclaw_models",
            "inject_api_connectors", "run_warmup", "setup_skills",
            "setup_workspace", "snapshot_workspace_state",
        ):
            monkeypatch.setattr(ocr, name, mk(name))
        procs = iter([_FakeProc(), _FakeProc()])
        monkeypatch.setattr(ocr, "run_background", lambda *a2, **k2: next(procs))
        monkeypatch.setattr(ocr.time, "sleep", lambda *a2, **k2: None)
        monkeypatch.setattr(ocr.time, "perf_counter", lambda: 0.0)
        monkeypatch.setattr(ocr.time, "time", lambda: 1.0)
        index_calls: list[str] = []
        monkeypatch.setattr(a, "_index_memory", lambda tid: index_calls.append(tid))
        monkeypatch.setattr(a, "_set_bootstrap_limits", lambda *a2, **k2: None)
        monkeypatch.setattr(a, "_set_model", lambda *a2, **k2: None)
        monkeypatch.setattr(a, "_inject_auth", lambda *a2, **k2: None)
        monkeypatch.setattr(a, "_set_image_model", lambda *a2, **k2: None)
        monkeypatch.setattr(a, "_wait_for_llm_route_ready", lambda *a2, **k2: True)

        pdir = tmp_path / "persona"
        pdir.mkdir()
        ddir = tmp_path / "data"
        ddir.mkdir()
        spec = _make_spec(
            tmp_path,
            task={
                "persona_dir": str(pdir),
                "data_dir": str(ddir),
                "required_apis": ["figma"],
                "distractor_apis": ["figma", "slack"],  # dedup with required
            },
            lobster={"workspace": str(tmp_path / "lob")},
            models_config={"providers": {}},
        )
        result = a.run_task(spec)
        assert result.error is None
        assert called.get("inject_data_into_workspace") == 1
        assert called.get("inject_persona_into_workspace") == 1
        assert called.get("inject_openclaw_models") == 1
        assert called.get("inject_api_connectors") == 1
        # inject_lobster_workspace called for BOTH lobster and persona_dir
        assert called.get("inject_lobster_workspace") == 2
        # _index_memory called once for lobster + once for persona_dir
        assert index_calls.count(spec.task_id) == 2

    def test_prompt_single_quotes_are_escaped(self, monkeypatch, tmp_path):
        a = _bare_agent()
        captured_cmds = []

        def capture_bg(task_id, bash_cmd=None, log_path=None, **k):
            captured_cmds.append(bash_cmd)
            return _FakeProc()

        for name in (
            "start_container", "inject_lobster_workspace", "inject_data_into_workspace",
            "inject_persona_into_workspace", "inject_openclaw_models",
            "inject_api_connectors", "run_warmup", "setup_skills",
            "setup_workspace", "snapshot_workspace_state",
        ):
            monkeypatch.setattr(ocr, name, lambda *a2, **k2: None)
        monkeypatch.setattr(ocr, "run_background", capture_bg)
        monkeypatch.setattr(ocr.time, "sleep", lambda *a2, **k2: None)
        monkeypatch.setattr(ocr.time, "perf_counter", lambda: 0.0)
        monkeypatch.setattr(ocr.time, "time", lambda: 1.0)
        self._stub_agent_methods(monkeypatch, a)

        spec = _make_spec(tmp_path, prompt="it's a test")
        a.run_task(spec)
        # agent command is the second run_background invocation
        agent_cmd = captured_cmds[1]
        assert "it'\\''s a test" in agent_cmd
