from __future__ import annotations

import json
import logging
import os
import shlex
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.agents.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.agents.codex.backend import (
    CODEX_PROMPT_PATH,
    load_skill_documents,
    prepare_codex_prompt,
)
from src.utils.docker_utils import run_warmup, setup_skills, snapshot_workspace_state
from src.utils.endpoint_utils import normalize_openrouter_base_url_for_openclaw

logger = logging.getLogger(__name__)

CODEX_HOME = "/root/.codex"
CODEX_SESSIONS_DIR = f"{CODEX_HOME}/sessions"
CODEX_CONFIG_PATH = f"{CODEX_HOME}/config.toml"
CODEX_SKILLS_DIR = f"{CODEX_HOME}/skills"
OPENCLAW_TRANSCRIPT_DIR = "/root/.openclaw/agents/main/sessions"
OPENCLAW_TRANSCRIPT_PATH = f"{OPENCLAW_TRANSCRIPT_DIR}/chat.jsonl"
DEFAULT_REASONING_EFFORT = "medium" #"high"
CODEX_LOG_NOISE_MARKERS = (
    "ReasoningRawContentDelta without active item",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_agent_log_event(output_dir: Path, event: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    enriched = {"timestamp": _now_iso(), **event}
    with (output_dir / "agent.log").open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(enriched, ensure_ascii=False) + "\n")


def write_execution_status(output_dir: Path, **updates: Any) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    status_path = output_dir / "execution_status.json"
    status: dict[str, Any] = {}
    if status_path.exists():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            status = {}
    status.update(updates)
    status["updated_at"] = _now_iso()
    status_path.write_text(
        json.dumps(status, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return status


def initialize_host_run_artifacts(
    output_dir: Path,
    task_id: str,
    model: str,
    timeout_seconds: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "agent.log").touch(exist_ok=True)
    write_execution_status(
        output_dir,
        task_id=task_id,
        model=model,
        timeout_seconds=timeout_seconds,
        status="created",
        started_at=_now_iso(),
        timed_out=False,
        exit_code=None,
        error=None,
    )
    append_agent_log_event(
        output_dir,
        {
            "type": "runner.status",
            "stage": "created",
            "message": "Host-side run artifacts initialized before container startup.",
        },
    )


def sanitize_agent_log(log_path: Path) -> None:
    if not log_path.exists():
        return
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return
    kept = [
        line for line in lines
        if not any(marker in line for marker in CODEX_LOG_NOISE_MARKERS)
    ]
    if len(kept) != len(lines):
        log_path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")


class CodexAgent(BaseAgent):
    def __init__(
        self,
        image: str | None = None,
        openrouter_api_key: str = "",
        openrouter_base_url: str = "",
        reasoning_effort_default: str = DEFAULT_REASONING_EFFORT,
    ) -> None:
        resolved_image = image or os.environ.get("DOCKER_IMAGE_CODEX") or "wildclawbench-codex-ubuntu:v0.0"
        self.image: str = resolved_image
        self.openrouter_api_key = (
            openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
        ).strip()
        self.openrouter_base_url = normalize_openrouter_base_url_for_openclaw(
            openrouter_base_url or os.environ.get("OPENROUTER_BASE_URL", "")
        )
        self.reasoning_effort_default = reasoning_effort_default

    @property
    def expects_gateway(self) -> bool:
        return False

    @property
    def transcript_container_path(self) -> str:
        return CODEX_SESSIONS_DIR

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        elapsed_time = float(spec.timeout_seconds)
        start_time = time.perf_counter()
        task_id = spec.task_id
        initialize_host_run_artifacts(
            output_dir=spec.output_dir,
            task_id=task_id,
            model=spec.model,
            timeout_seconds=spec.timeout_seconds,
        )

        try:
            try:
                write_execution_status(spec.output_dir, status="starting_container")
                self._start_container(task_id, spec.workspace_path, spec.task, spec.lobster)
                write_execution_status(spec.output_dir, status="container_started")
                write_execution_status(spec.output_dir, status="preparing_workspace")
                self._prepare_workspace(task_id, spec.workspace_path)
                skills_text = spec.task.get("skills", "") if spec.task else ""
                skills_path = spec.task.get("skills_path", "") if spec.task else ""
                setup_skills(
                    task_id,
                    skills_text,
                    skills_path,
                    container_skills_root=CODEX_SKILLS_DIR,
                )
                skill_docs = load_skill_documents(
                    skills_text,
                    skills_path,
                    container_skill_root=CODEX_SKILLS_DIR,
                )
                run_warmup(
                    task_id,
                    spec.task.get("warmup", "") if spec.task else "",
                    detach_background=True,
                )
                self._write_codex_config(
                    task_id=task_id,
                    model=spec.model,
                    reasoning_effort=spec.thinking
                    or self._default_reasoning_effort_for_model(spec.model),
                    wire_api=self._default_wire_api_for_model(spec.model),
                    output_dir=spec.output_dir,
                )
                image_helper_enabled = self._should_enable_image_helper(
                    spec.prompt, spec.workspace_path
                )
                if image_helper_enabled:
                    self._install_image_helper(task_id, spec.model)
                snapshot_workspace_state(task_id)
                write_execution_status(spec.output_dir, status="codex_running")
                self._run_prompt(
                    task_id=task_id,
                    prompt=self._build_task_prompt(
                        spec.prompt,
                        image_helper_enabled=image_helper_enabled,
                        skill_docs=skill_docs,
                    ),
                    timeout_seconds=spec.timeout_seconds,
                    output_dir=spec.output_dir,
                )
                elapsed_time = time.perf_counter() - start_time
                write_execution_status(
                    spec.output_dir,
                    status="finished",
                    timed_out=False,
                    elapsed_time=round(elapsed_time, 2),
                    exit_code=0,
                )
                return AgentExecution(
                    elapsed_time=elapsed_time, error=None, gateway_proc=None, agent_proc=None
                )
            except subprocess.TimeoutExpired:
                logger.info("[%s] Codex timed out...", task_id)
                elapsed_time = float(spec.timeout_seconds)
                append_agent_log_event(
                    spec.output_dir,
                    {
                        "type": "runner.timeout",
                        "message": f"Codex timed out after {spec.timeout_seconds} seconds.",
                        "timeout_seconds": spec.timeout_seconds,
                        "elapsed_time": elapsed_time,
                    },
                )
                write_execution_status(
                    spec.output_dir,
                    status="timed_out",
                    timed_out=True,
                    elapsed_time=round(elapsed_time, 2),
                    error="Codex run timed out",
                )
                return AgentExecution(
                    elapsed_time=elapsed_time,
                    error="Codex run timed out",
                    gateway_proc=None,
                    agent_proc=None,
                )
            except Exception as exc:
                elapsed_time = time.perf_counter() - start_time
                logger.error("[%s] Codex execution error: %s", task_id, exc)
                append_agent_log_event(
                    spec.output_dir,
                    {
                        "type": "runner.error",
                        "stage": "codex_execution",
                        "message": str(exc),
                        "elapsed_time": round(elapsed_time, 2),
                    },
                )
                write_execution_status(
                    spec.output_dir,
                    status="error",
                    error=str(exc),
                    elapsed_time=round(elapsed_time, 2),
                )
                return AgentExecution(
                    elapsed_time=elapsed_time,
                    error=str(exc),
                    gateway_proc=None,
                    agent_proc=None,
                )
        finally:
            sanitize_agent_log(spec.output_dir / "agent.log")
            try:
                self._install_openclaw_transcript_shim(task_id, spec.output_dir)
            except Exception as exc:
                logger.warning("[%s] OpenClaw transcript shim failed: %s", task_id, exc)

    def collect_usage(
        self, task_id: str, output_dir: Path, elapsed_time: float
    ) -> dict[str, Any]:
        usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
            "elapsed_time": round(elapsed_time, 2),
        }
        output_dir.mkdir(parents=True, exist_ok=True)

        sessions_dest = output_dir / "codex_sessions"
        sessions_dest.mkdir(parents=True, exist_ok=True)
        self._copy_dir_from_container(task_id, f"{CODEX_SESSIONS_DIR}/.", sessions_dest)

        latest = self._find_latest_session(task_id)
        chat_dest = output_dir / "chat.jsonl"
        if latest:
            self._copy_file_from_container(
                task_id, f"{CODEX_SESSIONS_DIR}/{latest}", chat_dest
            )

        parsed = self._extract_usage_from_jsonl(chat_dest)
        if parsed["total_tokens"] == 0 and parsed["input_tokens"] == 0:
            parsed = self._extract_usage_from_session_dir(sessions_dest)

        if parsed["cost_usd"] == 0.0:
            parsed["cost_usd"] = round(self._estimate_cost(parsed), 6)

        usage.update(parsed)
        usage["elapsed_time"] = round(elapsed_time, 2)
        return usage

    def _start_container(
        self,
        task_id: str,
        workspace_path: str,
        task: dict[str, Any],
        lobster: dict[str, Any] | None,
    ) -> None:
        workspace = Path(workspace_path).expanduser()
        if not workspace.is_dir():
            raise RuntimeError(
                f"Workspace path does not exist or is not a directory: {workspace}"
            )
        exec_path = workspace / "exec"
        if not exec_path.is_dir():
            raise RuntimeError(
                f"Workspace exec directory does not exist or is not a directory: {exec_path}"
            )

        from src.utils.docker_utils import (
            build_env_args,
            _validate_docker_token,
            _validate_env_arg,
        )
        _validate_docker_token("task_id", task_id)

        proxy_http = os.environ.get("HTTP_PROXY_INNER", "").strip()
        proxy_https = os.environ.get("HTTPS_PROXY_INNER", "").strip()
        no_proxy = "" if not proxy_http else os.environ.get("NO_PROXY_INNER", "").strip()
        env_map: dict[str, str] = {
            "OPENROUTER_API_KEY": self.openrouter_api_key,
            "OPENROUTER_BASE_URL": self.openrouter_base_url,
            "OPENROUTER_IMAGE_MODEL": os.environ.get("OPENROUTER_IMAGE_MODEL", "").strip(),
            "WILDCLAW_IMAGE_MODEL": os.environ.get("WILDCLAW_IMAGE_MODEL", "").strip(),
            "BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY", ""),
            "http_proxy": proxy_http,
            "https_proxy": proxy_https,
            "HTTP_PROXY": proxy_http,
            "HTTPS_PROXY": proxy_https,
            "no_proxy": no_proxy,
        }

        # Static env_map: pairs with truthy values only (preserves original semantic).
        env_pairs: list[tuple[str, str]] = [
            (k, v) for k, v in env_map.items() if v
        ]

        # Attacker-influenced keys: task["env"] (newline list) + lobster["env"] (JSON list).
        # _validate_env_arg rejects malformed keys (non-POSIX) before they reach docker argv.
        extra_env = task.get("env", "") if task else ""
        for line in extra_env.splitlines():
            key = line.strip()
            if not key or key.startswith("#"):
                continue
            value = os.environ.get(key, "").strip()
            _validate_env_arg(key, value)  # rejects bad key shapes / flag-leading values
            env_pairs.append((key, value))
            masked = (value[:4] + "***") if value else "(empty)"
            logger.info("[%s] Injecting env var: %s=%s", task_id, key, masked)

        for key in (lobster or {}).get("env", []) or []:
            value = os.environ.get(key, "").strip()
            if not value:
                logger.warning(
                    "[%s] Lobster env key %s not found, skipping", task_id, key
                )
                continue
            _validate_env_arg(key, value)
            env_pairs.append((key, value))
            logger.info("[%s] Injecting lobster env: %s=%s***", task_id, key, value[:4])

        env_args = build_env_args(env_pairs)
        image = _validate_docker_token("image", self.image)

        cmd = [
            "docker",
            "run",
            "-d",
            "--name",
            task_id,
            *env_args,
            "-v",
            f"{exec_path}:/workspace:ro",
            image,
            "/bin/bash",
            "-c",
            "tail -f /dev/null",
        ]
        logger.info("[%s] Starting Codex container (%s)", task_id, image)
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Codex container startup failed:\n{r.stderr}")
        logger.info("[%s] Container ID: %s", task_id, r.stdout.strip()[:12])

    def _prepare_workspace(self, task_id: str, workspace_path: str) -> None:
        r = subprocess.run(
            [
                "docker",
                "exec",
                task_id,
                "/bin/bash",
                "-c",
                (
                    "mkdir -p /tmp_workspace "
                    f"&& mkdir -p {CODEX_HOME} {CODEX_SESSIONS_DIR} "
                    "&& cp -r /workspace/. /tmp_workspace "
                    "&& chmod -R u+w /tmp_workspace"
                ),
            ],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Codex workspace copy failed:\n{r.stderr}")

        tmp_path = Path(workspace_path) / "tmp"
        if tmp_path.exists():
            mkdir_tmp = subprocess.run(
                ["docker", "exec", task_id, "mkdir", "-p", "/tmp_workspace/tmp"],
                capture_output=True,
                text=True,
            )
            if mkdir_tmp.returncode != 0:
                raise RuntimeError(f"Codex tmp mkdir failed:\n{mkdir_tmp.stderr}")

            copied = subprocess.run(
                ["docker", "cp", f"{tmp_path}/.", f"{task_id}:/tmp_workspace/tmp/"],
                capture_output=True,
                text=True,
            )
            if copied.returncode != 0:
                raise RuntimeError(f"Codex tmp copy failed:\n{copied.stderr}")

    def _default_reasoning_effort_for_model(self, model: str) -> str | None:
        """Return an explicit reasoning override if one is configured.

        By default we let Codex CLI and the underlying model choose their
        native reasoning settings. The only automatic override we keep is the
        explicit ``CODEX_REASONING_EFFORT`` env knob, which is useful for
        controlled experiments or emergency rollouts.
        """
        override = os.environ.get("CODEX_REASONING_EFFORT", "").strip().lower()
        if override:
            return override
        return None

    def _default_wire_api_for_model(self, model: str) -> str | None:
        """Return an explicit wire API override.

        Codex v0.121 rejects provider-level ``wire_api = "chat"``. Keep this
        as an emergency knob only; do not default MiniMax to chat here.
        """
        _ = model
        override = os.environ.get("CODEX_WIRE_API", "").strip().lower()
        if override == "chat":
            logger.warning("CODEX_WIRE_API=chat ignored: Codex CLI no longer supports it")
            return None
        return override or None

    @staticmethod
    def _is_minimax_model(model: str) -> bool:
        bare_model = model.split("/", 1)[1] if model.startswith("openrouter/") else model
        return bare_model.lower().startswith("minimax/")

    def _write_codex_config(
        self,
        task_id: str,
        model: str,
        reasoning_effort: str | None,
        wire_api: str | None,
        output_dir: Path,
    ) -> None:
        bare_model = model.split("/", 1)[1] if model.startswith("openrouter/") else model
        config_toml = self._render_codex_config(
            model=model,
            reasoning_effort=reasoning_effort,
            wire_api=wire_api,
        )

        # Mirror the rendered config host-side so future debugging is trivial.
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "config.toml").write_text(config_toml, encoding="utf-8")

        heredoc = (
            f"mkdir -p {CODEX_HOME} && "
            f"cat > {CODEX_CONFIG_PATH} <<'CODEX_EOF'\n"
            f"{config_toml}"
            f"CODEX_EOF\n"
        )
        r = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", heredoc],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Codex config write failed:\n{r.stderr}")
        logger.info(
            "[%s] Codex config written (model=%s, reasoning=%s, wire_api=%s)",
            task_id,
            bare_model,
            reasoning_effort or "model-default",
            wire_api or "default",
        )

    def _render_codex_config(
        self,
        model: str,
        reasoning_effort: str | None,
        wire_api: str | None,
    ) -> str:
        bare_model = model.split("/", 1)[1] if model.startswith("openrouter/") else model
        safe_base_url = self.openrouter_base_url.replace('"', '\\"')
        reasoning_line = (
            f'model_reasoning_effort = "{reasoning_effort}"\n'
            if reasoning_effort
            else ""
        )
        provider_wire_api_line = f'wire_api = "{wire_api}"\n' if wire_api else ""
        return (
            f'model_provider = "openrouter"\n'
            f"{reasoning_line}"
            f'model_reasoning_summary = "none"\n'
            f'model_supports_reasoning_summaries = false\n'
            f'hide_agent_reasoning = true\n'
            f'model = "{bare_model}"\n'
            f'approval_policy = "never"\n'
            f'sandbox_mode = "danger-full-access"\n'
            f'\n'
            f'[model_providers.openrouter]\n'
            f'name = "openrouter"\n'
            f'base_url = "{safe_base_url}"\n'
            f'env_key = "OPENROUTER_API_KEY"\n'
            f"{provider_wire_api_line}"
        )

    def _install_image_helper(self, task_id: str, model: str) -> None:
        """Install a recoverable OpenRouter chat-completions image helper.

        Codex CLI image input currently goes through the Responses API, which
        some OpenRouter models reject as a fatal process error. This helper uses
        the benchmark's normal OpenRouter chat-completions path and reports
        failures as JSON so the agent can continue with other methods.
        """
        bare_model = model.split("/", 1)[1] if model.startswith("openrouter/") else model
        helper = self._render_image_helper(default_model=bare_model)

        helper_tmp = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(helper)
                helper_tmp = f.name

            copied = subprocess.run(
                ["docker", "cp", helper_tmp, f"{task_id}:/tmp_workspace/.wildclaw_image.py"],
                capture_output=True,
                text=True,
            )
            if copied.returncode != 0:
                raise RuntimeError(f"Codex image helper copy failed:\n{copied.stderr}")

            chmod = subprocess.run(
                ["docker", "exec", task_id, "chmod", "+x", "/tmp_workspace/.wildclaw_image.py"],
                capture_output=True,
                text=True,
            )
            if chmod.returncode != 0:
                raise RuntimeError(f"Codex image helper chmod failed:\n{chmod.stderr}")
        finally:
            if helper_tmp:
                Path(helper_tmp).unlink(missing_ok=True)

    @staticmethod
    def _render_image_helper(default_model: str) -> str:
        return f'''#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = {json.dumps(default_model)}
CALL_LIMIT = int(os.environ.get("WILDCLAW_IMAGE_HELPER_CALL_LIMIT", "2") or "2")
CALL_STATE_PATH = "/tmp_workspace/.wildclaw_image_calls.json"


def emit(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def resolve_image_path(path: str) -> tuple[str | None, str | None]:
    if os.path.exists(path):
        return path, None

    basename = os.path.basename(path)
    if not basename:
        return None, f"image not found: {{path}}"

    matches: list[str] = []
    for root, _dirs, files in os.walk("/tmp_workspace"):
        if basename in files:
            matches.append(os.path.join(root, basename))
            if len(matches) >= 5:
                break

    if len(matches) == 1:
        return matches[0], f"requested path not found; using {{matches[0]}}"
    if matches:
        return matches[0], (
            f"requested path not found; multiple {{basename}} matches, using {{matches[0]}}"
        )
    return None, f"image not found: {{path}}"


def record_helper_call() -> tuple[bool, int]:
    try:
        with open(CALL_STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        state = {{"count": 0}}

    count = int(state.get("count") or 0) + 1
    try:
        with open(CALL_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump({{"count": count}}, f)
    except Exception:
        pass
    return count <= CALL_LIMIT, count


def main() -> int:
    if len(sys.argv) < 2:
        return emit({{"ok": False, "error": "usage: .wildclaw_image.py <image_path> [question]"}})

    requested_path = sys.argv[1]
    question = " ".join(sys.argv[2:]).strip() or "Describe the image and extract task-relevant facts."
    image_path, warning = resolve_image_path(requested_path)
    if not image_path:
        return emit({{"ok": False, "error": warning, "requested_path": requested_path}})

    allowed, call_count = record_helper_call()
    if not allowed:
        return emit({{
            "ok": False,
            "error": "image helper call limit reached; use previous helper observations or a direct OpenRouter chat/completions image request if needed",
            "call_count": call_count,
            "call_limit": CALL_LIMIT,
            "image_path": image_path,
            "warning": warning,
        }})

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return emit({{"ok": False, "error": "OPENROUTER_API_KEY is not set"}})

    base_url = (os.environ.get("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1").rstrip("/")
    model = (
        os.environ.get("WILDCLAW_IMAGE_MODEL")
        or os.environ.get("OPENROUTER_IMAGE_MODEL")
        or DEFAULT_MODEL
    )
    if model.startswith("openrouter/"):
        model = model.split("/", 1)[1]

    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except OSError as exc:
        return emit({{"ok": False, "error": f"failed to read image: {{exc}}", "image_path": image_path}})

    mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
    data_url = "data:" + mime + ";base64," + base64.b64encode(image_bytes).decode("ascii")
    payload = {{
        "model": model,
        "messages": [
            {{
                "role": "user",
                "content": [
                    {{"type": "text", "text": question}},
                    {{"type": "image_url", "image_url": {{"url": data_url}}}},
                ],
            }}
        ],
        "max_tokens": 64000,
        "temperature": 0,
    }}
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={{
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        }},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = response.read().decode("utf-8", errors="replace")
        data = json.loads(body)
        content = data.get("choices", [{{}}])[0].get("message", {{}}).get("content", "")
        return emit({{
            "ok": True,
            "model": model,
            "image_path": image_path,
            "warning": warning,
            "content": content,
        }})
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return emit({{
            "ok": False,
            "model": model,
            "image_path": image_path,
            "warning": warning,
            "error": f"HTTP {{exc.code}} {{exc.reason}}",
            "body": body[:2000],
        }})
    except Exception as exc:
        return emit({{
            "ok": False,
            "model": model,
            "image_path": image_path,
            "warning": warning,
            "error": str(exc),
        }})


if __name__ == "__main__":
    raise SystemExit(main())
'''

    def _run_prompt(
        self,
        task_id: str,
        prompt: str,
        timeout_seconds: int,
        output_dir: Path,
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = prepare_codex_prompt(task_id, prompt, CODEX_PROMPT_PATH)
        log_path = output_dir / "agent.log"
        r = self._run_codex_exec(task_id, prompt_path, timeout_seconds, log_path)

        if r.returncode == 0:
            return

        raise RuntimeError(
            f"Codex run failed (rc={r.returncode}):\n{r.stderr or r.stdout}"
        )

    def _run_codex_exec(
        self, task_id: str, prompt_path: str, timeout_seconds: int, log_path: Path
    ) -> subprocess.CompletedProcess[str]:
        cmd = self._build_exec_command(prompt_path)
        full_cmd = ["docker", "exec", task_id, "/bin/bash", "-c", cmd]
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("w", encoding="utf-8", errors="replace") as log:
            proc = subprocess.Popen(
                full_cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                returncode = proc.wait(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                log.write("\n" + json.dumps({
                    "timestamp": _now_iso(),
                    "type": "runner.timeout",
                    "message": f"Codex timed out after {timeout_seconds} seconds and was killed.",
                    "timeout_seconds": timeout_seconds,
                    "pid": proc.pid,
                }, ensure_ascii=False) + "\n")
                log.flush()
                try:
                    os.fsync(log.fileno())
                except OSError:
                    pass
                self._terminate_codex_processes(task_id)
                proc.kill()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    log.write("[Codex runner] docker exec did not exit after kill\n")
                    log.flush()
                raise

        return subprocess.CompletedProcess(
            full_cmd,
            returncode,
            stdout=self._read_text_tail(log_path),
            stderr="",
        )

    @staticmethod
    def _terminate_codex_processes(task_id: str) -> None:
        subprocess.run(
            [
                "docker",
                "exec",
                task_id,
                "/bin/bash",
                "-lc",
                (
                    "pkill -TERM -f 'codex exec' 2>/dev/null || true; "
                    "sleep 2; "
                    "pkill -KILL -f 'codex exec' 2>/dev/null || true"
                ),
            ],
            capture_output=True,
            text=True,
            timeout=8,
        )

    @staticmethod
    def _combined_process_output(r: subprocess.CompletedProcess[str]) -> str:
        return (r.stdout or "") + ("\n" if r.stdout else "") + (r.stderr or "")

    @staticmethod
    def _read_text_tail(path: Path, max_chars: int | None = None) -> str:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
        if max_chars is None or len(text) <= max_chars:
            return text
        return text[-max_chars:]

    @staticmethod
    def _build_task_prompt(
        prompt: str,
        image_helper_enabled: bool,
        skill_docs: list[dict[str, str]] | None = None,
    ) -> str:
        sections: list[str] = []
        if image_helper_enabled:
            sections.append(
                "## Image Helper\n\n"
                "When image understanding is needed, use the recoverable helper "
                "instead of Codex built-in image input. Do not call the `view_image` "
                "tool or attach images to the model; this OpenRouter setup can fail "
                "on that path via the /responses API:\n\n"
                '```bash\npython3 /tmp_workspace/.wildclaw_image.py "<image_path>" "<question>"\n```\n\n'
                "The helper returns JSON and exits 0 even if the image model call "
                "fails. It defaults to the task model. Call it at most twice per task. "
                "Do not call any built-in image input, `view_image`, `--image`, "
                "`input_image`, or file:// image URLs. If the helper returns "
                "ok=false because the model or endpoint cannot handle the request, "
                "you may make a direct OpenRouter /chat/completions request using "
                "OPENROUTER_API_KEY, OPENROUTER_BASE_URL, and an image-capable model. "
                "Otherwise, continue with other available methods and still write the required output files. "
                "After the required files are written, finish instead of doing "
                "extra image verification."
            )
        if skill_docs:
            skill_sections = [
                "## Local Skill References\n\n"
                "Use these task-specific instructions when they apply. They describe local files, mock APIs, and required workflows available in this container."
            ]
            for skill in skill_docs:
                skill_sections.append(
                    f"### Skill: {skill['name']}\n\n{skill['content'].strip()}"
                )
            sections.append("\n\n".join(skill_sections))
        sections.append("## Task\n\n" + prompt.strip())
        return "\n\n".join(sections).strip() + "\n"

    @staticmethod
    def _should_enable_image_helper(prompt: str, workspace_path: str) -> bool:
        lowered = prompt.lower()
        image_markers = (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
            ".bmp",
            ".tif",
            ".tiff",
            "image",
            "photo",
            "picture",
            "screenshot",
            "diagram",
        )
        if any(marker in lowered for marker in image_markers):
            return True

        exec_path = Path(workspace_path) / "exec"
        image_suffixes = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
        try:
            return any(
                path.is_file() and path.suffix.lower() in image_suffixes
                for path in exec_path.rglob("*")
            )
        except OSError:
            return False

    def _build_exec_command(self, prompt_path: str) -> str:
        return (
            "cd /tmp_workspace && "
            f"cat {shlex.quote(prompt_path)} | "
            "codex exec --skip-git-repo-check --cd /tmp_workspace -"
        )

    def _build_find_latest_session_command(self) -> str:
        return (
            f"find {CODEX_SESSIONS_DIR} -type f -name '*.jsonl' "
            "-printf '%T@ %P\\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-"
        )

    def _find_latest_session(self, task_id: str) -> str | None:
        r = subprocess.run(
            [
                "docker",
                "exec",
                task_id,
                "/bin/bash",
                "-c",
                self._build_find_latest_session_command(),
            ],
            capture_output=True,
            text=True,
        )
        name = (r.stdout or "").strip().splitlines()[0] if r.stdout else ""
        return name or None

    def _copy_file_from_container(self, task_id: str, src: str, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_dir():
            shutil.rmtree(dest)
        elif dest.exists():
            dest.unlink()
        r = subprocess.run(
            ["docker", "cp", f"{task_id}:{src}", str(dest)],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            logger.warning(
                "[%s] Codex file copy failed (%s): %s", task_id, src, r.stderr.strip()
            )

    def _copy_dir_from_container(self, task_id: str, src: str, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(
            ["docker", "cp", f"{task_id}:{src}", str(dest)],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            logger.warning(
                "[%s] Codex dir copy failed (%s): %s", task_id, src, r.stderr.strip()
            )

    def _install_openclaw_transcript_shim(
        self, task_id: str, output_dir: Path
    ) -> None:
        """Translate codex session jsonl 鈫?openclaw schema.

        Safety-alignment graders (tasks/06_Safety_Alignment/*.md) hard-code
        ``/root/.openclaw/agents/main/sessions/chat.jsonl`` with the openclaw
        shape ``{"type": "message", "message": {"role": ..., "content": [...]}}``.
        We emit that same shape from the codex session 鈥?including mapped
        tool_use / tool_result blocks 鈥?so graders can evaluate the agent's
        behavior without any task-file changes.
        """
        latest = self._find_latest_session(task_id)
        if not latest:
            logger.info(
                "[%s] No codex session file yet; skipping openclaw shim", task_id
            )
            return

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            src = tmp_dir / "codex.jsonl"
            dest = tmp_dir / "openclaw.jsonl"

            self._copy_file_from_container(
                task_id, f"{CODEX_SESSIONS_DIR}/{latest}", src
            )
            if not src.exists() or src.stat().st_size == 0:
                return

            emitted = self._translate_codex_to_openclaw(src, dest)
            if emitted == 0 or not dest.exists():
                logger.info(
                    "[%s] Codex session had no mappable events; shim skipped",
                    task_id,
                )
                return

            # Mirror host-side for debugging.
            (output_dir / "chat_openclaw.jsonl").write_bytes(dest.read_bytes())

            mk = subprocess.run(
                [
                    "docker",
                    "exec",
                    task_id,
                    "mkdir",
                    "-p",
                    OPENCLAW_TRANSCRIPT_DIR,
                ],
                capture_output=True,
                text=True,
            )
            if mk.returncode != 0:
                logger.warning(
                    "[%s] mkdir for openclaw transcript failed: %s",
                    task_id,
                    mk.stderr.strip(),
                )
                return

            cp = subprocess.run(
                [
                    "docker",
                    "cp",
                    str(dest),
                    f"{task_id}:{OPENCLAW_TRANSCRIPT_PATH}",
                ],
                capture_output=True,
                text=True,
            )
            if cp.returncode != 0:
                logger.warning(
                    "[%s] Copy openclaw transcript failed: %s",
                    task_id,
                    cp.stderr.strip(),
                )
                return

            logger.info(
                "[%s] OpenClaw transcript shim installed (%d events)",
                task_id,
                emitted,
            )

    def _translate_codex_to_openclaw(self, src: Path, dest: Path) -> int:
        """Write an openclaw-shape jsonl to ``dest``.

        Returns the number of emitted openclaw records.
        """
        out_lines: list[str] = []
        for raw in src.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line.startswith("{"):
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            for record in self._codex_entry_to_openclaw(entry):
                out_lines.append(json.dumps(record, ensure_ascii=False))

        if not out_lines:
            return 0
        dest.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
        return len(out_lines)

    def _codex_entry_to_openclaw(self, entry: dict[str, Any]) -> list[dict[str, Any]]:
        """Map one codex event to zero-or-more openclaw message records.

        Codex emits a grab-bag of shapes across versions; we look for the
        meaningful payload under common container keys (``payload``, ``item``,
        ``message``) and handle the four kinds of record graders care about:
        user text, assistant text, function_call (鈫?tool_use), and
        function_call_output (鈫?tool_result).
        """
        payload = self._codex_payload(entry)
        if not isinstance(payload, dict):
            return []

        ptype = str(payload.get("type") or "").lower()

        # Messages: role + content blocks
        if ptype == "message" or (
            payload.get("role") in ("user", "assistant", "system")
            and "content" in payload
        ):
            role = payload.get("role") or entry.get("role") or "assistant"
            content_items = payload.get("content") or []
            mapped = self._map_message_content(content_items)
            if not mapped:
                return []
            return [self._openclaw_message(role, mapped)]

        # Function call (codex tool call) 鈫?openclaw tool_use block inside an
        # assistant message so graders that scan `content[*].type=="tool_use"`
        # can see it.
        if ptype in ("function_call", "tool_call", "function-call"):
            name = payload.get("name") or payload.get("tool_name") or "unknown"
            call_id = (
                payload.get("call_id")
                or payload.get("callId")
                or payload.get("id")
                or ""
            )
            arguments = payload.get("arguments") or payload.get("input") or ""
            parsed_input: Any
            if isinstance(arguments, str):
                try:
                    parsed_input = json.loads(arguments) if arguments else {}
                except json.JSONDecodeError:
                    parsed_input = {"_raw": arguments}
            elif isinstance(arguments, dict):
                parsed_input = arguments
            else:
                parsed_input = {"_value": arguments}
            return [
                self._openclaw_message(
                    "assistant",
                    [
                        {
                            "type": "tool_use",
                            "id": str(call_id),
                            "name": str(name),
                            "input": parsed_input,
                        }
                    ],
                )
            ]

        # Tool output 鈫?openclaw tool_result inside a user message (Anthropic
        # convention that openclaw graders mirror).
        if ptype in ("function_call_output", "tool_result", "function-call-output"):
            call_id = (
                payload.get("call_id")
                or payload.get("callId")
                or payload.get("id")
                or ""
            )
            output = payload.get("output") or payload.get("result") or ""
            if isinstance(output, (dict, list)):
                try:
                    output_text = json.dumps(output, ensure_ascii=False)
                except Exception:
                    output_text = str(output)
            else:
                output_text = str(output)
            return [
                self._openclaw_message(
                    "user",
                    [
                        {
                            "type": "tool_result",
                            "tool_use_id": str(call_id),
                            "content": output_text,
                        }
                    ],
                )
            ]

        # Reasoning summaries surface as assistant text so any grader that
        # keyword-scans assistant output also sees the model's deliberation.
        if ptype == "reasoning":
            summary = payload.get("summary") or payload.get("content") or []
            chunks: list[str] = []
            if isinstance(summary, list):
                for item in summary:
                    if isinstance(item, str):
                        chunks.append(item)
                    elif isinstance(item, dict):
                        chunks.append(
                            str(item.get("text") or item.get("summary_text") or "")
                        )
            elif isinstance(summary, str):
                chunks.append(summary)
            text = "\n".join(c for c in chunks if c).strip()
            if not text:
                return []
            return [
                self._openclaw_message(
                    "assistant", [{"type": "text", "text": text}]
                )
            ]

        return []

    def _codex_payload(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        """Resolve the meaningful inner dict from a codex JSONL record."""
        for key in ("payload", "item", "message", "event_msg", "data"):
            value = entry.get(key)
            if isinstance(value, dict):
                return value
        # Some codex versions emit the item fields at the top level already.
        if "type" in entry or "role" in entry:
            return entry
        return None

    def _map_message_content(
        self, content: Any
    ) -> list[dict[str, Any]]:
        """Translate codex content blocks 鈫?openclaw-shape content blocks."""
        if isinstance(content, str):
            return [{"type": "text", "text": content}] if content else []

        if not isinstance(content, list):
            return []

        mapped: list[dict[str, Any]] = []
        for item in content:
            if isinstance(item, str):
                if item:
                    mapped.append({"type": "text", "text": item})
                continue
            if not isinstance(item, dict):
                continue
            itype = str(item.get("type") or "").lower()
            if itype in ("output_text", "text", "input_text"):
                text = item.get("text") or item.get("output_text") or ""
                if text:
                    mapped.append({"type": "text", "text": str(text)})
            elif itype in ("input_image", "image", "image_url"):
                url = (
                    item.get("image_url")
                    or item.get("url")
                    or item.get("source", {}).get("url", "")
                )
                mapped.append({"type": "image", "source": {"url": str(url)}})
            elif itype == "tool_use":
                mapped.append(item)  # already openclaw-shaped
            elif itype == "tool_result":
                mapped.append(item)
            else:
                # Preserve unknown blocks as text fallback so nothing is lost.
                text = item.get("text") or item.get("content") or ""
                if text:
                    mapped.append({"type": "text", "text": str(text)})
        return mapped

    def _openclaw_message(
        self, role: str, content: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return {
            "type": "message",
            "message": {
                "role": role,
                "content": content,
            },
        }

    def _extract_usage_from_session_dir(self, session_dir: Path) -> dict[str, Any]:
        totals = self._empty_totals()
        if not session_dir.exists():
            return totals
        candidates = sorted(
            (p for p in session_dir.rglob("*.jsonl") if p.is_file()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for path in candidates:
            parsed = self._extract_usage_from_jsonl(path)
            if parsed["total_tokens"] > 0 or parsed["input_tokens"] > 0:
                return parsed
        return totals

    def _extract_usage_from_jsonl(self, jsonl_path: Path) -> dict[str, Any]:
        totals = self._empty_totals()
        if not jsonl_path.exists():
            return totals

        cumulative: dict[str, int] | None = None
        per_turn: list[dict[str, int]] = []
        assistant_message_count = 0
        cost_sum = 0.0

        for raw in jsonl_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line.startswith("{"):
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Codex sessions include assistant message records; count them for
            # request_count when explicit usage events are absent.
            if self._is_assistant_message(entry):
                assistant_message_count += 1

            extracted, is_cumulative = self._extract_usage_fields(entry)
            if extracted is None:
                continue

            cost_sum += extracted.pop("_cost", 0.0)
            if is_cumulative:
                cumulative = extracted
            else:
                per_turn.append(extracted)

        if per_turn:
            for key in (
                "input_tokens",
                "output_tokens",
                "cache_read_tokens",
                "cache_write_tokens",
                "total_tokens",
            ):
                totals[key] = sum(turn.get(key, 0) for turn in per_turn)
            totals["request_count"] = len(per_turn)
        elif cumulative is not None:
            for key in (
                "input_tokens",
                "output_tokens",
                "cache_read_tokens",
                "cache_write_tokens",
                "total_tokens",
            ):
                totals[key] = cumulative.get(key, 0)
            totals["request_count"] = assistant_message_count or 1

        if totals["total_tokens"] == 0:
            totals["total_tokens"] = (
                totals["input_tokens"]
                + totals["output_tokens"]
                + totals["cache_read_tokens"]
                + totals["cache_write_tokens"]
            )

        totals["cost_usd"] = round(cost_sum, 6)
        return totals

    def _is_assistant_message(self, entry: dict[str, Any]) -> bool:
        if entry.get("type") == "message" and entry.get("role") == "assistant":
            return True
        payload = entry.get("payload") or entry.get("item") or entry.get("message")
        if isinstance(payload, dict):
            if payload.get("type") == "message" and payload.get("role") == "assistant":
                return True
            if payload.get("role") == "assistant":
                return True
        return False

    def _extract_usage_fields(
        self, entry: dict[str, Any]
    ) -> tuple[dict[str, Any] | None, bool]:
        """Find a usage block inside a Codex JSONL record.

        Returns (usage_dict, is_cumulative). is_cumulative=True means the
        record reports running totals rather than per-turn deltas, so callers
        should overwrite rather than sum them.
        """
        entry_type = str(entry.get("type", "")).lower()

        candidates: list[tuple[dict[str, Any], bool]] = []

        info = entry.get("info") if isinstance(entry.get("info"), dict) else None
        if info:
            total = info.get("total_token_usage") or info.get("totalTokenUsage")
            if isinstance(total, dict):
                candidates.append((total, True))
            last = info.get("last_token_usage") or info.get("lastTokenUsage")
            if isinstance(last, dict):
                candidates.append((last, False))

        for key in ("usage", "token_usage", "tokenUsage", "last_token_usage", "lastTokenUsage"):
            value = entry.get(key)
            if isinstance(value, dict):
                is_cum = key in ("total_token_usage", "totalTokenUsage")
                candidates.append((value, is_cum))

        payload = entry.get("payload") or entry.get("item") or entry.get("event_msg")
        if isinstance(payload, dict):
            for key in ("usage", "token_usage", "tokenUsage", "last_token_usage", "lastTokenUsage"):
                value = payload.get(key)
                if isinstance(value, dict):
                    candidates.append((value, False))
            info2 = payload.get("info") if isinstance(payload.get("info"), dict) else None
            if info2:
                total = info2.get("total_token_usage") or info2.get("totalTokenUsage")
                if isinstance(total, dict):
                    candidates.append((total, True))
                last = info2.get("last_token_usage") or info2.get("lastTokenUsage")
                if isinstance(last, dict):
                    candidates.append((last, False))

        if entry_type in ("token_count", "tokencount"):
            # Many Codex versions emit the running cumulative totals as a
            # standalone token_count event at the top level.
            for value in entry.values():
                if isinstance(value, dict) and self._looks_like_usage(value):
                    candidates.append((value, True))

        if not candidates:
            return None, False

        # Prefer the richest candidate (the one with the most known keys).
        best, is_cumulative = max(
            candidates, key=lambda c: sum(1 for k in _USAGE_KEYS if k in c[0])
        )
        normalized = self._normalize_usage(best)
        if normalized is None:
            return None, False
        cost = self._extract_cost(entry, best)
        normalized["_cost"] = cost
        return normalized, is_cumulative

    def _looks_like_usage(self, value: dict[str, Any]) -> bool:
        return any(k in value for k in _USAGE_KEYS)

    def _normalize_usage(self, usage: dict[str, Any]) -> dict[str, Any] | None:
        if not self._looks_like_usage(usage):
            return None
        input_tokens = int(
            self._num(
                usage.get("input_tokens", usage.get("inputTokens", usage.get("input", 0)))
            )
        )
        output_tokens = int(
            self._num(
                usage.get(
                    "output_tokens",
                    usage.get("outputTokens", usage.get("output", 0)),
                )
            )
        )
        reasoning_tokens = int(
            self._num(
                usage.get(
                    "reasoning_output_tokens",
                    usage.get(
                        "reasoningOutputTokens",
                        usage.get("reasoning_tokens", 0),
                    ),
                )
            )
        )
        cache_read = int(
            self._num(
                usage.get(
                    "cached_input_tokens",
                    usage.get(
                        "cachedInputTokens",
                        usage.get("cache_read_tokens", usage.get("cacheRead", 0)),
                    ),
                )
            )
        )
        cache_write = int(
            self._num(
                usage.get(
                    "cache_creation_input_tokens",
                    usage.get(
                        "cacheCreationInputTokens",
                        usage.get("cache_write_tokens", usage.get("cacheWrite", 0)),
                    ),
                )
            )
        )
        total = int(
            self._num(
                usage.get("total_tokens", usage.get("totalTokens", 0)),
                default=0.0,
            )
        )

        # Codex's output_tokens already includes reasoning_output_tokens on
        # recent versions, but we keep reasoning_tokens as a signal and fall
        # back to adding it only when output looks too small.
        output_tokens = max(output_tokens, reasoning_tokens)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_tokens": cache_read,
            "cache_write_tokens": cache_write,
            "total_tokens": total,
        }

    def _extract_cost(self, entry: dict[str, Any], usage: dict[str, Any]) -> float:
        for key in ("cost_usd", "costUsd"):
            if key in entry:
                return float(self._num(entry.get(key)))
            if key in usage:
                return float(self._num(usage.get(key)))
        cost_obj = usage.get("cost") or entry.get("cost")
        if isinstance(cost_obj, dict):
            for key in ("total", "usd", "cost_usd", "amount"):
                if key in cost_obj:
                    return float(self._num(cost_obj.get(key)))
        if isinstance(cost_obj, (int, float)):
            return float(cost_obj)
        return 0.0

    def _empty_totals(self) -> dict[str, Any]:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }

    def _num(self, value: Any, default: float = 0.0) -> float:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                return default
        return default

    def _estimate_cost(self, totals: dict[str, Any]) -> float:
        input_price = float(os.environ.get("CODEX_INPUT_PRICE_PER_MTOK", "0"))
        output_price = float(os.environ.get("CODEX_OUTPUT_PRICE_PER_MTOK", "0"))
        cache_read_price = float(os.environ.get("CODEX_CACHE_READ_PRICE_PER_MTOK", "0"))
        cache_write_price = float(os.environ.get("CODEX_CACHE_WRITE_PRICE_PER_MTOK", "0"))
        uncached_input_tokens = max(
            totals["input_tokens"] - totals["cache_read_tokens"] - totals["cache_write_tokens"],
            0,
        )
        return (
            uncached_input_tokens / 1_000_000 * input_price
            + totals["output_tokens"] / 1_000_000 * output_price
            + totals["cache_read_tokens"] / 1_000_000 * cache_read_price
            + totals["cache_write_tokens"] / 1_000_000 * cache_write_price
        )


_USAGE_KEYS = {
    "input_tokens",
    "inputTokens",
    "input",
    "output_tokens",
    "outputTokens",
    "output",
    "total_tokens",
    "totalTokens",
    "cached_input_tokens",
    "cachedInputTokens",
    "cache_read_tokens",
    "cacheRead",
    "cache_creation_input_tokens",
    "cacheCreationInputTokens",
    "cache_write_tokens",
    "cacheWrite",
    "reasoning_output_tokens",
    "reasoningOutputTokens",
    "reasoning_tokens",
}
