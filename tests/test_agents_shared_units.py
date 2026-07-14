"""Unit coverage for the shared agent-backend helpers.

Modules under test (all offline, no docker / network / boto3):
  - src/agents/base.py                         (AgentTaskSpec / AgentExecution / BaseAgent)
  - src/agents/codex/backend.py                (config/prompt/event->transcript pure fns)
  - src/agents/claudecode/transcript.py        (chat.jsonl -> openclaw jsonl conversion)
  - src/agents/hermesagent/compat_transcript.py (hermes sessions -> openclaw messages)
  - src/agents/hermesagent/bench_runner.py     (thin main() harness)

Style follows tests/test_docker_env_validation.py (sys.path bootstrap + package
imports) and tests/test_repackage_bundle_ground_truth.py (importlib load for the
non-package script-style modules bench_runner / compat_transcript main()).

Where a module's *current* behavior looks surprising it is pinned verbatim with a
"# NOTE: pins current behavior" comment rather than asserting an idealized result.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Package-importable modules ------------------------------------------------
from src.agents import base as base_mod  # noqa: E402
from src.agents.base import (  # noqa: E402
    AgentExecution,
    AgentTaskSpec,
    BaseAgent,
)
from src.agents.claudecode.transcript import (  # noqa: E402
    convert_claudecode_chat_to_openclaw_jsonl,
)
from src.agents.codex import backend as codex_backend  # noqa: E402


# Script-style modules loaded by path (mirrors the repackager test) ---------
def _load_by_path(mod_name: str, rel_path: str):
    path = REPO_ROOT / rel_path
    assert path.exists(), f"missing module: {path}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


compat = _load_by_path(
    "_test_hermes_compat", "src/agents/hermesagent/compat_transcript.py"
)
bench_runner = _load_by_path(
    "_test_hermes_bench_runner", "src/agents/hermesagent/bench_runner.py"
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# ===========================================================================
# src/agents/base.py
# ===========================================================================


class _ConcreteAgent(BaseAgent):
    """Minimal concrete subclass so we can exercise the non-abstract logic."""

    @property
    def expects_gateway(self) -> bool:
        return True

    @property
    def transcript_container_path(self) -> str:
        return "/root/.openclaw/agents/main/sessions/chat.jsonl"

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:  # pragma: no cover
        return AgentExecution(elapsed_time=1.0, error=None)

    def collect_usage(  # pragma: no cover
        self, task_id: str, output_dir: Path, elapsed_time: float
    ) -> dict[str, Any]:
        return {}


def test_agent_task_spec_is_frozen_with_defaults():
    spec = AgentTaskSpec(
        task_id="t1",
        task={"prompt": "hi"},
        workspace_path="/ws",
        prompt="do it",
        timeout_seconds=60,
        output_dir=Path("/out"),
        model="claude-opus-4.7",
    )
    assert spec.thinking is None
    assert spec.models_config is None
    assert spec.lobster is None
    # frozen dataclass: assignment must raise
    with pytest.raises(Exception):
        spec.task_id = "other"  # type: ignore[misc]


def test_agent_execution_defaults():
    execu = AgentExecution(elapsed_time=2.5, error=None)
    assert execu.gateway_proc is None
    assert execu.agent_proc is None
    # AgentExecution is a plain (mutable) dataclass — assignment is allowed
    execu.error = "boom"
    assert execu.error == "boom"


def test_base_agent_cannot_instantiate_directly():
    with pytest.raises(TypeError):
        BaseAgent()  # type: ignore[abstract]


def test_prepare_grading_transcript_returns_container_path():
    agent = _ConcreteAgent()
    # The default impl ignores task_id and returns the container transcript path.
    out = agent.prepare_grading_transcript("any-task-id")
    assert out == "/root/.openclaw/agents/main/sessions/chat.jsonl"
    assert out == agent.transcript_container_path


def test_base_module_exposes_expected_symbols():
    for name in ("AgentTaskSpec", "AgentExecution", "BaseAgent"):
        assert hasattr(base_mod, name)


# ===========================================================================
# src/agents/codex/backend.py  — pure helpers
# ===========================================================================


def test_normalize_codex_model_strips_openrouter_prefix():
    assert codex_backend.normalize_codex_model("openrouter/gpt-5.5") == "gpt-5.5"
    assert codex_backend.normalize_codex_model("gpt-5.5") == "gpt-5.5"
    # Prefix only removed at the very start.
    assert (
        codex_backend.normalize_codex_model("x/openrouter/gpt")
        == "x/openrouter/gpt"
    )


def test_build_codex_config_toml_embeds_normalized_model_and_url():
    toml = codex_backend.build_codex_config_toml(
        base_url="https://example/api", model="openrouter/gpt-5.5"
    )
    assert 'model = "gpt-5.5"' in toml
    assert 'base_url = "https://example/api"' in toml
    assert 'env_key = "OPENROUTER_API_KEY"' in toml
    assert "apply_patch = true" in toml


def test_build_codex_bootstrap_command_with_and_without_version():
    with_ver = codex_backend.build_codex_bootstrap_command("@openai/codex", "1.2.3")
    # shlex.quote leaves @-. specs unquoted (no shell metacharacters).
    assert "npm install -g @openai/codex@1.2.3" in with_ver
    assert "command -v codex" in with_ver

    no_ver = codex_backend.build_codex_bootstrap_command("@openai/codex", None)
    assert "npm install -g @openai/codex" in no_ver
    assert "@1.2.3" not in no_ver

    # A spec containing a space DOES get quoted by shlex.quote.
    spaced = codex_backend.build_codex_bootstrap_command("weird pkg", "1")
    assert "'weird pkg@1'" in spaced


def test_looks_like_transient_bootstrap_failure():
    assert codex_backend.looks_like_transient_bootstrap_failure("ECONNRESET while fetching")
    assert codex_backend.looks_like_transient_bootstrap_failure("Read timed out")
    assert codex_backend.looks_like_transient_bootstrap_failure("Temporary failure in name resolution")
    assert not codex_backend.looks_like_transient_bootstrap_failure("npm ERR! 404 not found")
    assert not codex_backend.looks_like_transient_bootstrap_failure("")


def test_build_codex_exec_command_includes_model_prompt_and_env():
    cmd = codex_backend.build_codex_exec_command(
        model="openrouter/gpt-5.5",
        prompt_path="/tmp/p.txt",
        env_vars={"OPENROUTER_API_KEY": "sk-123"},
    )
    # shlex.quote leaves a plain key value unquoted.
    assert "export OPENROUTER_API_KEY=sk-123 &&" in cmd
    assert "--model gpt-5.5" in cmd
    assert "cat /tmp/p.txt |" in cmd
    assert "codex exec --json" in cmd
    assert codex_backend.CODEX_LAST_MESSAGE_PATH in cmd


def test_build_codex_exec_command_empty_model_omits_model_flag():
    cmd = codex_backend.build_codex_exec_command(model="", env_vars=None)
    assert "--model" not in cmd
    # env prefix absent when env_vars is None
    assert "export " not in cmd


def test_get_codex_provider_env_filters_empty(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-abc")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "")
    env = codex_backend.get_codex_provider_env()
    assert env == {"OPENROUTER_API_KEY": "sk-abc"}
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)
    assert codex_backend.get_codex_provider_env() == {}


def test_build_codex_prompt_no_skills_returns_base():
    assert codex_backend.build_codex_prompt("just the task", []) == "just the task"


def test_build_codex_prompt_with_skills_sections():
    skills = [{"name": "alpha", "content": "  Do alpha  "}]
    out = codex_backend.build_codex_prompt("solve x", skills)
    assert "## Skill: alpha" in out
    assert "Do alpha" in out
    assert "## Task" in out
    assert out.endswith("\n")
    assert "solve x" in out


def test_load_skill_documents_reads_and_substitutes(tmp_path):
    skill_dir = tmp_path / "myskill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "Use dir {baseDir} for artifacts", encoding="utf-8"
    )
    docs = codex_backend.load_skill_documents(
        skills="myskill\n", skills_path=str(tmp_path)
    )
    assert len(docs) == 1
    assert docs[0]["name"] == "myskill"
    assert "/root/skills/myskill for artifacts" in docs[0]["content"]


def test_load_skill_documents_skips_blank_and_missing(tmp_path):
    # blank lines, and a skill whose SKILL.md is absent, are both dropped.
    docs = codex_backend.load_skill_documents(
        skills="\n   \nghost\n", skills_path=str(tmp_path)
    )
    assert docs == []


def test_load_skill_documents_custom_container_root(tmp_path):
    skill_dir = tmp_path / "nested" / "leaf"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("root={baseDir}", encoding="utf-8")
    docs = codex_backend.load_skill_documents(
        skills="nested/leaf",
        skills_path=str(tmp_path),
        container_skill_root="/custom",
    )
    assert len(docs) == 1
    # leaf name (not full rel path) is used for the container path.
    assert docs[0]["content"] == "root=/custom/leaf"


def test_discover_and_setup_codex_auth_are_noops(monkeypatch):
    assert codex_backend.discover_codex_auth_sources() == []
    assert codex_backend.discover_codex_auth_sources("/some/home") == []
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-x")
    assert codex_backend.setup_codex_auth("task1") == []
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert codex_backend.setup_codex_auth("task1") == []


# ---- codex event -> openclaw transcript ----------------------------------


def test_parse_codex_json_events_missing_file(tmp_path):
    assert codex_backend.parse_codex_json_events(tmp_path / "nope.log") == []


def test_parse_codex_json_events_filters_noise(tmp_path):
    log = tmp_path / "agent.log"
    log.write_text(
        "\n".join(
            [
                "plain log line not json",
                '{"type": "item.completed", "item": {"type": "agent_message", "text": "hi"}}',
                "{ not valid json",
                '{"no_type": true}',  # dict but no 'type' -> dropped
                '   ',
            ]
        ),
        encoding="utf-8",
    )
    events = codex_backend.parse_codex_json_events(log)
    assert len(events) == 1
    assert events[0]["type"] == "item.completed"


def test_codex_events_agent_message_and_usage_attachment():
    events = [
        {"type": "item.completed", "item": {"type": "agent_message", "text": "done"}},
        {
            "type": "turn.completed",
            "usage": {"input_tokens": 10, "output_tokens": 4, "cached_input_tokens": 2},
        },
    ]
    msgs = codex_backend.codex_events_to_openclaw_messages(events)
    assert len(msgs) == 1
    m = msgs[0]["message"]
    assert m["role"] == "assistant"
    assert m["content"] == [{"type": "text", "text": "done"}]
    usage = m["usage"]
    assert usage["input"] == 10
    assert usage["output"] == 4
    assert usage["cacheRead"] == 2
    assert usage["totalTokens"] == 16  # input+output+cache
    assert usage["cost"] == {"total": 0.0}


def test_codex_events_assistant_message_content_list():
    events = [
        {
            "type": "item.completed",
            "item": {
                "type": "assistant_message",
                "content": [
                    {"type": "text", "text": "part1"},
                    {"type": "text", "text": "part2"},
                    {"type": "other", "text": "ignored"},
                ],
            },
        }
    ]
    msgs = codex_backend.codex_events_to_openclaw_messages(events)
    assert msgs[0]["message"]["content"] == [{"type": "text", "text": "part1\npart2"}]


def test_codex_events_command_execution_tool_call():
    events = [
        {
            "type": "item.completed",
            "item": {
                "type": "command_execution",
                "command": "ls -la",
                "status": "completed",
                "exit_code": 0,
                "aggregated_output": "file.txt",
            },
        }
    ]
    msgs = codex_backend.codex_events_to_openclaw_messages(events)
    block = msgs[0]["message"]["content"][0]
    assert block["type"] == "toolCall"
    assert block["name"] == "exec_command"
    assert block["arguments"]["cmd"] == "ls -la"
    assert block["arguments"]["output"] == "file.txt"


def test_codex_events_web_search_and_file_change_and_mcp():
    events = [
        {
            "type": "item.completed",
            "item": {"type": "web_search", "query": "python", "result_count": 3},
        },
        {
            "type": "item.completed",
            "item": {"type": "file_change", "path": "/a", "change_type": "add"},
        },
        {
            "type": "item.completed",
            "item": {"type": "mcp_tool_call", "tool_name": "grep", "arguments": {"q": 1}},
        },
    ]
    msgs = codex_backend.codex_events_to_openclaw_messages(events)
    names = [m["message"]["content"][0]["name"] for m in msgs]
    assert names == ["web_search", "write_file", "grep"]


def test_codex_events_reasoning_only_when_nonempty():
    events = [
        {"type": "item.completed", "item": {"type": "reasoning", "summary": "  "}},
        {"type": "item.completed", "item": {"type": "reasoning", "summary": "why"}},
    ]
    msgs = codex_backend.codex_events_to_openclaw_messages(events)
    assert len(msgs) == 1
    assert msgs[0]["message"]["content"] == [{"type": "text", "text": "why"}]


def test_codex_events_error_item_and_error_event():
    events = [
        {"type": "item.completed", "item": {"type": "error", "message": "bad thing"}},
        {"type": "error", "message": "top level fail"},
    ]
    msgs = codex_backend.codex_events_to_openclaw_messages(events)
    texts = [m["message"]["content"][0]["text"] for m in msgs]
    assert texts == ["bad thing", "top level fail"]


def test_codex_events_usage_with_no_text_message_appends_synthetic():
    # A tool-call-only run still records usage on a synthetic empty message.
    events = [
        {
            "type": "item.completed",
            "item": {"type": "command_execution", "command": "true"},
        },
        {"type": "task_complete", "usage": {"input_tokens": 5, "output_tokens": 1}},
    ]
    msgs = codex_backend.codex_events_to_openclaw_messages(events)
    # last message is synthetic empty-text carrying usage.
    # NOTE: pins current behavior — _message_entry("") yields a single empty text
    # block (empty string != None), so content is not [] but [{"text": ""}].
    last = msgs[-1]["message"]
    assert last["content"] == [{"type": "text", "text": ""}]
    assert last["usage"]["input"] == 5
    assert last["usage"]["totalTokens"] == 6


def test_codex_events_empty_returns_empty():
    assert codex_backend.codex_events_to_openclaw_messages([]) == []


def test_build_usage_none_and_variants():
    assert codex_backend._build_usage(None) is None
    assert codex_backend._build_usage("not a dict") is None  # type: ignore[arg-type]
    # camelCase keys are accepted as aliases; total defaults to in+out+cacheRead.
    u = codex_backend._build_usage(
        {"inputTokens": 7, "outputTokens": 3, "cacheReadTokens": 1}
    )
    assert u == {
        "input": 7,
        "output": 3,
        "cacheRead": 1,
        "cacheWrite": 0,
        "totalTokens": 11,
        "cost": {"total": 0.0},
    }


def test_message_contains_text_helper():
    assert codex_backend._message_contains_text(
        {"message": {"content": [{"type": "text", "text": "x"}]}}
    )
    assert not codex_backend._message_contains_text(
        {"message": {"content": [{"type": "toolCall", "name": "y"}]}}
    )
    assert not codex_backend._message_contains_text({"message": {"content": "nope"}})


# ---- codex container-touching helpers (subprocess monkeypatched) ----------


def test_read_text_from_container_success_and_failure(monkeypatch):
    calls: list[list[str]] = []

    def fake_run(argv, capture_output, text):
        calls.append(argv)

        class R:
            returncode = 0
            stdout = "file contents"
            stderr = ""

        return R()

    monkeypatch.setattr(codex_backend.subprocess, "run", fake_run)
    assert codex_backend.read_text_from_container("task1", "/tmp/x") == "file contents"
    assert calls[0][:3] == ["docker", "exec", "-u"]

    def fake_run_fail(argv, capture_output, text):
        class R:
            returncode = 1
            stdout = ""
            stderr = "no such file"

        return R()

    monkeypatch.setattr(codex_backend.subprocess, "run", fake_run_fail)
    assert codex_backend.read_text_from_container("task1", "/tmp/x") == ""


def test_ensure_codex_cli_success_no_retry(monkeypatch):
    calls: list[Any] = []

    def fake_run(argv, capture_output, text):
        calls.append(argv)

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    monkeypatch.setattr(codex_backend.subprocess, "run", fake_run)
    slept: list[float] = []
    monkeypatch.setattr(codex_backend.time, "sleep", lambda s: slept.append(s))
    codex_backend.ensure_codex_cli("task1")
    assert len(calls) == 1
    assert slept == []


def test_ensure_codex_cli_permanent_failure_raises(monkeypatch):
    def fake_run(argv, capture_output, text):
        class R:
            returncode = 1
            stdout = ""
            stderr = "npm ERR! 404"  # non-transient -> raises immediately

        return R()

    monkeypatch.setattr(codex_backend.subprocess, "run", fake_run)
    monkeypatch.setattr(codex_backend.time, "sleep", lambda s: None)
    with pytest.raises(RuntimeError, match="Failed to bootstrap"):
        codex_backend.ensure_codex_cli("task1")


def test_ensure_codex_cli_transient_then_success(monkeypatch):
    results = iter(
        [
            (1, "connection reset by peer"),  # transient -> retry
            (0, ""),  # success
        ]
    )

    def fake_run(argv, capture_output, text):
        rc, err = next(results)

        class R:
            returncode = rc
            stdout = ""
            stderr = err

        return R()

    monkeypatch.setattr(codex_backend.subprocess, "run", fake_run)
    slept: list[float] = []
    monkeypatch.setattr(codex_backend.time, "sleep", lambda s: slept.append(s))
    codex_backend.ensure_codex_cli("task1")
    assert len(slept) == 1  # one backoff sleep between the two attempts


def test_copy_text_to_container_success(monkeypatch):
    argvs: list[list[str]] = []

    def fake_run(argv, capture_output, text):
        argvs.append(argv)

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    monkeypatch.setattr(codex_backend.subprocess, "run", fake_run)
    codex_backend._copy_text_to_container("task1", "/root/.codex/config.toml", "data")
    # first call mkdir -p, second docker cp
    assert argvs[0] == ["docker", "exec", "-u", "0", "task1", "mkdir", "-p", "/root/.codex"]
    assert argvs[1][0:2] == ["docker", "cp"]
    assert argvs[1][-1] == "task1:/root/.codex/config.toml"


def test_copy_text_to_container_mkdir_failure_raises(monkeypatch):
    def fake_run(argv, capture_output, text):
        class R:
            returncode = 1
            stdout = ""
            stderr = "permission denied"

        return R()

    monkeypatch.setattr(codex_backend.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="Failed to create container directory"):
        codex_backend._copy_text_to_container("task1", "/x/y.txt", "data")


def test_setup_codex_config_writes_toml(monkeypatch):
    captured: dict[str, str] = {}

    def fake_copy(task_id, container_path, text):
        captured["path"] = container_path
        captured["text"] = text

    monkeypatch.setattr(codex_backend, "_copy_text_to_container", fake_copy)
    monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)
    codex_backend.setup_codex_config("task1", "openrouter/gpt-5.5")
    assert captured["path"].endswith("/config.toml")
    assert 'model = "gpt-5.5"' in captured["text"]
    # default base url used when env unset
    assert codex_backend.DEFAULT_OPENROUTER_BASE_URL in captured["text"]


def test_prepare_codex_prompt_returns_path(monkeypatch):
    seen: dict[str, Any] = {}
    monkeypatch.setattr(
        codex_backend,
        "_copy_text_to_container",
        lambda t, p, x: seen.update(path=p, text=x),
    )
    out = codex_backend.prepare_codex_prompt("task1", "the prompt")
    assert out == codex_backend.CODEX_PROMPT_PATH
    assert seen["text"] == "the prompt"


def test_write_openclaw_compat_transcript(monkeypatch):
    seen: dict[str, Any] = {}
    monkeypatch.setattr(
        codex_backend,
        "_copy_text_to_container",
        lambda t, p, x: seen.update(path=p, text=x),
    )
    events = [
        {"type": "item.completed", "item": {"type": "agent_message", "text": "hi"}}
    ]
    n = codex_backend.write_openclaw_compat_transcript("task1", events)
    assert n == 1
    # transcript text is newline-terminated JSONL
    lines = [l for l in seen["text"].splitlines() if l]
    assert len(lines) == 1
    assert json.loads(lines[0])["message"]["content"][0]["text"] == "hi"


def test_write_openclaw_compat_transcript_empty(monkeypatch):
    seen: dict[str, Any] = {}
    monkeypatch.setattr(
        codex_backend,
        "_copy_text_to_container",
        lambda t, p, x: seen.update(text=x),
    )
    n = codex_backend.write_openclaw_compat_transcript("task1", [])
    assert n == 0
    assert seen["text"] == ""


def test_run_codex_process_success(monkeypatch):
    monkeypatch.setattr(codex_backend, "prepare_codex_prompt", lambda *a, **k: None)
    monkeypatch.setattr(codex_backend, "get_codex_provider_env", lambda: {})

    class FakeProc:
        returncode = 0

        def wait(self, timeout=None):
            return 0

        def kill(self):  # pragma: no cover
            pass

    proc = FakeProc()
    captured: dict[str, Any] = {}

    def fake_bg(task_id, bash_cmd, log_path):
        captured["cmd"] = bash_cmd
        captured["log"] = log_path
        return proc

    gw, ag, elapsed = codex_backend.run_codex_process(
        task_id="task1",
        model="gpt-5.5",
        prompt="p",
        timeout_seconds=30,
        output_dir=Path("/out"),
        run_background_fn=fake_bg,
    )
    assert gw is None
    assert ag is proc
    assert isinstance(elapsed, float)
    assert "codex exec --json" in captured["cmd"]
    assert str(captured["log"]).endswith("agent.log")


def test_run_codex_process_timeout_kills(monkeypatch):
    monkeypatch.setattr(codex_backend, "prepare_codex_prompt", lambda *a, **k: None)
    monkeypatch.setattr(codex_backend, "get_codex_provider_env", lambda: {})

    killed = {"called": False}

    class FakeProc:
        returncode = -9

        def wait(self, timeout=None):
            if timeout is not None:
                raise subprocess.TimeoutExpired(cmd="codex", timeout=timeout)
            return -9

        def kill(self):
            killed["called"] = True

    proc = FakeProc()
    gw, ag, elapsed = codex_backend.run_codex_process(
        task_id="task1",
        model="gpt-5.5",
        prompt="p",
        timeout_seconds=7,
        output_dir=Path("/out"),
        run_background_fn=lambda task_id, **k: proc,
    )
    assert killed["called"] is True
    assert elapsed == 7  # falls back to the timeout value


# ===========================================================================
# src/agents/claudecode/transcript.py
# ===========================================================================


def test_transcript_missing_file_writes_empty(tmp_path):
    out = tmp_path / "sub" / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(tmp_path / "nope.jsonl", out)
    assert n == 0
    assert out.read_text(encoding="utf-8") == ""


def test_transcript_passthrough_openclaw_messages(tmp_path):
    chat = tmp_path / "chat.jsonl"
    rows = [
        {"type": "message", "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}},
        {"type": "message", "message": {"role": "assistant", "content": []}},
    ]
    chat.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    assert n == 2
    written = _read_jsonl(out)
    assert written == rows  # already-openclaw rows pass through unchanged


def test_transcript_role_content_fallback(tmp_path):
    # No openclaw rows and no stream events -> role/content normalization path.
    chat = tmp_path / "chat.jsonl"
    rows = [
        {"role": "user", "content": "hello"},
        {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "sure"},
                {"type": "tool_use", "name": "bash", "input": {"cmd": "ls"}},
            ],
        },
    ]
    chat.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    assert n == 2
    written = _read_jsonl(out)
    assert written[0]["message"]["role"] == "user"
    assert written[0]["message"]["content"] == [{"type": "text", "text": "hello"}]
    assist_blocks = written[1]["message"]["content"]
    assert {"type": "text", "text": "sure"} in assist_blocks
    tool_block = [b for b in assist_blocks if b["type"] == "tool_use"][0]
    assert tool_block["name"] == "bash"
    assert tool_block["input"] == {"cmd": "ls"}


def test_transcript_role_content_json_string_tool_input(tmp_path):
    chat = tmp_path / "chat.jsonl"
    rows = [
        {
            "role": "assistant",
            "content": [
                {"type": "toolCall", "tool_name": "write", "arguments": '{"path": "/a"}'},
            ],
        },
    ]
    chat.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    written = _read_jsonl(out)
    tb = written[0]["message"]["content"][0]
    assert tb["type"] == "tool_use"
    assert tb["name"] == "write"
    assert tb["input"] == {"path": "/a"}  # JSON-string arguments get parsed


def test_transcript_single_json_object_wrapped(tmp_path):
    # A whole-file single JSON object (not JSONL) is treated as one row.
    chat = tmp_path / "chat.jsonl"
    chat.write_text(
        json.dumps({"role": "user", "content": "solo"}), encoding="utf-8"
    )
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    assert n == 1
    assert _read_jsonl(out)[0]["message"]["content"] == [{"type": "text", "text": "solo"}]


def test_transcript_empty_string_content_produces_no_blocks(tmp_path):
    chat = tmp_path / "chat.jsonl"
    chat.write_text(json.dumps({"role": "assistant", "content": ""}), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    # message still emitted, with an empty content list.
    assert n == 1
    assert _read_jsonl(out)[0]["message"]["content"] == []


def test_transcript_claude_stream_events(tmp_path):
    # Full stream-event path: message_start -> block start/delta/stop -> query_end.
    chat = tmp_path / "chat.jsonl"

    def yield_row(event):
        return {
            "event": "query_yield",
            "payload": {"message": {"type": "stream_event", "event": event}},
        }

    rows = [
        yield_row({"type": "message_start", "message": {"role": "assistant"}}),
        yield_row(
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {"type": "text", "text": ""},
            }
        ),
        yield_row(
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": "Hello "},
            }
        ),
        yield_row(
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": "world"},
            }
        ),
        yield_row({"type": "content_block_stop", "index": 0}),
        yield_row(
            {
                "type": "content_block_start",
                "index": 1,
                "content_block": {"type": "tool_use", "name": "bash", "input": {}},
            }
        ),
        yield_row(
            {
                "type": "content_block_delta",
                "index": 1,
                "delta": {"type": "input_json_delta", "partial_json": '{"cmd":'},
            }
        ),
        yield_row(
            {
                "type": "content_block_delta",
                "index": 1,
                "delta": {"type": "input_json_delta", "partial_json": ' "ls"}'},
            }
        ),
        yield_row({"type": "content_block_stop", "index": 1}),
        yield_row({"type": "message_stop"}),
        {"event": "query_end", "payload": {"usage": {"input_tokens": 12, "output_tokens": 5}}},
    ]
    chat.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    assert n == 1
    msg = _read_jsonl(out)[0]["message"]
    assert msg["role"] == "assistant"
    text_blocks = [b for b in msg["content"] if b["type"] == "text"]
    tool_blocks = [b for b in msg["content"] if b["type"] == "tool_use"]
    assert text_blocks[0]["text"] == "Hello world"
    assert tool_blocks[0]["name"] == "bash"
    assert tool_blocks[0]["input"] == {"cmd": "ls"}
    # usage attached from the query_end event
    assert msg["usage"]["input"] == 12
    assert msg["usage"]["output"] == 5
    assert msg["usage"]["totalTokens"] == 17


def test_transcript_stream_tool_use_unparseable_json_wrapped_as_raw(tmp_path):
    chat = tmp_path / "chat.jsonl"

    def yield_row(event):
        return {
            "event": "query_yield",
            "payload": {"message": {"type": "stream_event", "event": event}},
        }

    rows = [
        yield_row({"type": "message_start", "message": {"role": "assistant"}}),
        yield_row(
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {"type": "tool_use", "name": "x", "input": {}},
            }
        ),
        yield_row(
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "input_json_delta", "partial_json": "not-json"},
            }
        ),
        yield_row({"type": "content_block_stop", "index": 0}),
        yield_row({"type": "message_stop"}),
    ]
    chat.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    tb = _read_jsonl(out)[0]["message"]["content"][0]
    # NOTE: pins current behavior — unparseable tool input is wrapped as {"raw": ...}
    assert tb["input"] == {"raw": "not-json"}


def test_transcript_blank_and_garbage_lines_ignored(tmp_path):
    chat = tmp_path / "chat.jsonl"
    chat.write_text(
        "\n".join(
            [
                "",
                "   ",
                "not json at all",
                json.dumps({"role": "user", "content": "ok"}),
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    assert n == 1


def test_transcript_all_empty_rows_writes_empty(tmp_path):
    # Rows exist but normalize to nothing -> empty output, count 0.
    chat = tmp_path / "chat.jsonl"
    chat.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    assert n == 0
    assert out.read_text(encoding="utf-8") == ""


def test_transcript_stream_tool_result_block(tmp_path):
    # tool_result content block flows through content_block_start -> flush.
    chat = tmp_path / "chat.jsonl"

    def yield_row(event):
        return {
            "event": "query_yield",
            "payload": {"message": {"type": "stream_event", "event": event}},
        }

    rows = [
        yield_row({"type": "message_start", "message": {"role": "user"}}),
        yield_row(
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {
                    "type": "tool_result",
                    "tool_use_id": "tu_1",
                    "content": "output text",
                },
            }
        ),
        yield_row({"type": "message_stop"}),
    ]
    chat.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    assert n == 1
    block = _read_jsonl(out)[0]["message"]["content"][0]
    assert block["type"] == "tool_result"
    assert block["tool_use_id"] == "tu_1"
    assert block["content"] == "output text"


def test_transcript_role_fallback_skips_bad_rows(tmp_path):
    # rows that are not dicts, or lack a string role, are dropped by the
    # role/content fallback (no stream events, no openclaw messages present).
    chat = tmp_path / "chat.jsonl"
    rows = [
        [1, 2, 3],  # not a dict
        {"role": 123, "content": "x"},  # role not a string
        {"content": "no role key"},  # missing role
        {"role": "assistant", "content": "kept"},
    ]
    chat.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    n = convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    assert n == 1
    assert _read_jsonl(out)[0]["message"]["content"] == [{"type": "text", "text": "kept"}]


def test_transcript_stream_input_present_on_block_start(tmp_path):
    # tool_use with a fully-populated input at content_block_start (no deltas):
    # the input survives to the flushed message.
    chat = tmp_path / "chat.jsonl"

    def yield_row(event):
        return {
            "event": "query_yield",
            "payload": {"message": {"type": "stream_event", "event": event}},
        }

    rows = [
        yield_row({"type": "message_start", "message": {"role": "assistant"}}),
        yield_row(
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {
                    "type": "tool_use",
                    "name": "read",
                    "input": {"path": "/etc/hosts"},
                },
            }
        ),
        yield_row({"type": "content_block_stop", "index": 0}),
        yield_row({"type": "message_stop"}),
    ]
    chat.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    out = tmp_path / "out.jsonl"
    convert_claudecode_chat_to_openclaw_jsonl(chat, out)
    tb = _read_jsonl(out)[0]["message"]["content"][0]
    assert tb["input"] == {"path": "/etc/hosts"}


def test_transcript_to_openclaw_usage_defaults():
    from src.agents.claudecode.transcript import _to_openclaw_usage

    # Missing/None values coerce to zero without raising.
    u = _to_openclaw_usage({"input_tokens": None, "output_tokens": 2})
    assert u["input"] == 0
    assert u["output"] == 2
    assert u["totalTokens"] == 2
    assert u["cost"] == {"total": 0.0}
    # total_cost_usd fallback for cost.
    u2 = _to_openclaw_usage({"total_cost_usd": 1.5})
    assert u2["cost"] == {"total": 1.5}


# ===========================================================================
# src/agents/hermesagent/compat_transcript.py
# ===========================================================================


def test_hermes_assistant_entry_plain_text():
    entry = compat._assistant_entry({"role": "assistant", "content": "hi", "usage": {"x": 1}})
    assert entry["type"] == "message"
    assert entry["message"]["role"] == "assistant"
    assert entry["message"]["content"] == "hi"
    assert entry["message"]["usage"] == {"x": 1}


def test_hermes_assistant_entry_non_str_content_json_encoded():
    entry = compat._assistant_entry({"role": "assistant", "content": {"a": 1}})
    # Non-string content with no tool calls is JSON-serialized to a string.
    assert entry["message"]["content"] == json.dumps({"a": 1}, ensure_ascii=False)
    assert entry["message"]["usage"] == {}  # missing usage -> {}


def test_hermes_assistant_entry_with_tool_calls():
    entry = compat._assistant_entry(
        {
            "role": "assistant",
            "content": "thinking",
            "tool_calls": [
                {
                    "id": "call_1",
                    "function": {"name": "bash", "arguments": '{"cmd": "ls"}'},
                },
                "not-a-dict",  # skipped
                {"id": "call_2", "function": {"name": "noargs", "arguments": {}}},
            ],
        }
    )
    blocks = entry["message"]["content"]
    assert blocks[0] == {"type": "text", "text": "thinking"}
    tool_blocks = [b for b in blocks if b["type"] == "tool_use"]
    assert tool_blocks[0]["name"] == "bash"
    assert tool_blocks[0]["input"] == {"cmd": "ls"}  # JSON-string args parsed
    assert tool_blocks[0]["id"] == "call_1"
    assert tool_blocks[1]["name"] == "noargs"


def test_hermes_assistant_entry_unparseable_tool_args_kept_raw():
    entry = compat._assistant_entry(
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"id": "c", "function": {"name": "x", "arguments": "oops"}}],
        }
    )
    blocks = entry["message"]["content"]
    # empty content -> no text block, only the tool_use block
    assert all(b["type"] == "tool_use" for b in blocks)
    assert blocks[0]["input"] == "oops"  # unparseable arg string kept verbatim


def test_hermes_user_and_tool_entries():
    u = compat._user_entry({"role": "user", "content": "hey"})
    assert u["type"] == "message"
    assert u["message"] == {"role": "user", "content": "hey"}

    u2 = compat._user_entry({"role": "user", "content": {"k": "v"}})
    assert u2["message"]["content"] == json.dumps({"k": "v"}, ensure_ascii=False)

    t = compat._tool_entry({"content": "result data", "tool_call_id": "tid"})
    assert t["type"] == "toolResult"
    assert t["toolResult"]["content"] == "result data"
    assert t["toolResult"]["tool_call_id"] == "tid"


def test_hermes_to_openclaw_messages_roles():
    msgs = [
        {"role": "assistant", "content": "a"},
        {"role": "user", "content": "b"},
        {"role": "tool", "content": "c", "tool_call_id": "1"},
        {"role": "system", "content": "ignored"},  # dropped
    ]
    out = compat._to_openclaw_messages(msgs)
    assert [o["type"] for o in out] == ["message", "message", "toolResult"]


def test_hermes_load_messages_from_session_files(tmp_path):
    sess = tmp_path / "sessions"
    sess.mkdir()
    (sess / "session_1.json").write_text(
        json.dumps({"messages": [{"role": "user", "content": "hi"}, "bad"]}),
        encoding="utf-8",
    )
    (sess / "session_2.json").write_text(
        json.dumps({"messages": [{"role": "assistant", "content": "yo"}]}),
        encoding="utf-8",
    )
    (sess / "session_bad.json").write_text("not json", encoding="utf-8")
    msgs = compat._load_messages(str(sess), str(tmp_path / "traj.jsonl"))
    # only dict items are kept; corrupt session file skipped
    contents = [m["content"] for m in msgs]
    assert "hi" in contents
    assert "yo" in contents
    assert "bad" not in contents


def test_hermes_load_messages_trajectory_fallback(tmp_path):
    # No session files -> fall back to last line of trajectory jsonl.
    sess = tmp_path / "sessions"  # does not exist / empty
    traj = tmp_path / "traj.jsonl"
    traj.write_text(
        "\n".join(
            [
                json.dumps({"conversations": [{"role": "user", "content": "old"}]}),
                json.dumps({"conversations": [{"role": "user", "content": "last"}, 42]}),
            ]
        ),
        encoding="utf-8",
    )
    msgs = compat._load_messages(str(sess), str(traj))
    assert [m["content"] for m in msgs] == ["last"]  # only last line, dicts only


def test_hermes_load_messages_missing_everything(tmp_path):
    assert compat._load_messages(str(tmp_path / "no"), str(tmp_path / "no.jsonl")) == []


def test_hermes_load_messages_trajectory_bad_last_line(tmp_path):
    traj = tmp_path / "traj.jsonl"
    traj.write_text("{ not valid json", encoding="utf-8")
    assert compat._load_messages(str(tmp_path / "no"), str(traj)) == []


def test_hermes_main_writes_transcript(tmp_path, monkeypatch):
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    (sessions / "session_1.json").write_text(
        json.dumps(
            {
                "messages": [
                    {"role": "user", "content": "do x"},
                    {"role": "assistant", "content": "done"},
                ]
            }
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "out" / "chat.jsonl"

    monkeypatch.setattr(compat, "HERMES_HOME", str(tmp_path))
    monkeypatch.setattr(compat, "HERMES_INSTALL_DIR", str(tmp_path / "install"))
    monkeypatch.setattr(compat, "OUTPUT_TRANSCRIPT_PATH", str(out_path))

    rc = compat.main()
    assert rc == 0
    assert out_path.exists()
    written = _read_jsonl(out_path)
    assert len(written) == 2
    assert written[0]["message"]["role"] == "user"
    assert written[1]["message"]["role"] == "assistant"


def test_hermes_main_no_messages_writes_empty(tmp_path, monkeypatch):
    out_path = tmp_path / "chat.jsonl"
    monkeypatch.setattr(compat, "HERMES_HOME", str(tmp_path / "empty_home"))
    monkeypatch.setattr(compat, "HERMES_INSTALL_DIR", str(tmp_path / "empty_install"))
    monkeypatch.setattr(compat, "OUTPUT_TRANSCRIPT_PATH", str(out_path))
    rc = compat.main()
    assert rc == 0
    assert out_path.read_text(encoding="utf-8") == ""


# ===========================================================================
# src/agents/hermesagent/bench_runner.py
# ===========================================================================


def test_bench_runner_main_invokes_agent(tmp_path, monkeypatch):
    # Stand up a fake run_agent module with an AIAgent, and a config file, then
    # drive bench_runner.main() end to end without touching the real hermes CLI.
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(
        json.dumps(
            {
                "config": {
                    "model": "gpt-5.5",
                    "api_key": "sk-1",
                    "base_url": "http://x",
                    "max_iterations": 3,
                    "reasoning_config": {"effort": "high"},
                },
                "prompt": "hello",
            }
        ),
        encoding="utf-8",
    )

    captured: dict[str, Any] = {}

    class FakeAgent:
        def __init__(self, **kwargs):
            captured["init"] = kwargs

        def run_conversation(self, prompt):
            captured["prompt"] = prompt
            return {"completed": True, "api_calls": 4}

    fake_module = type(sys)("run_agent")
    fake_module.AIAgent = FakeAgent
    monkeypatch.setitem(sys.modules, "run_agent", fake_module)

    monkeypatch.setattr(bench_runner, "BENCH_CONFIG_PATH", str(cfg_path))
    monkeypatch.setattr(bench_runner, "HERMES_INSTALL_DIR", str(tmp_path))
    # os.chdir into tmp_path is harmless; restore afterwards via monkeypatch chdir
    monkeypatch.chdir(tmp_path)

    rc = bench_runner.main()
    assert rc == 0
    assert captured["prompt"] == "hello"
    assert captured["init"]["model"] == "gpt-5.5"
    assert captured["init"]["max_iterations"] == 3
    assert captured["init"]["save_trajectories"] is True
    assert captured["init"]["reasoning_config"] == {"effort": "high"}


def test_bench_runner_main_defaults_when_optional_missing(tmp_path, monkeypatch):
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(
        json.dumps({"config": {"model": "m"}, "prompt": "p"}), encoding="utf-8"
    )

    captured: dict[str, Any] = {}

    class FakeAgent:
        def __init__(self, **kwargs):
            captured["init"] = kwargs

        def run_conversation(self, prompt):
            return {"completed": False}

    fake_module = type(sys)("run_agent")
    fake_module.AIAgent = FakeAgent
    monkeypatch.setitem(sys.modules, "run_agent", fake_module)

    monkeypatch.setattr(bench_runner, "BENCH_CONFIG_PATH", str(cfg_path))
    monkeypatch.setattr(bench_runner, "HERMES_INSTALL_DIR", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    rc = bench_runner.main()
    assert rc == 0
    # defaults applied for the optional keys
    assert captured["init"]["max_iterations"] == 90
    assert captured["init"]["base_url"] == ""
    assert captured["init"]["api_key"] is None  # empty/absent -> None
    assert captured["init"]["reasoning_config"] is None
