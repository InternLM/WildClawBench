from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.agents.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.utils.docker_utils import (
    run_warmup,
    setup_skills,
    inject_lobster_workspace,
    TMP_WORKSPACE,
)
from src.utils.grading import extract_usage_from_jsonl

load_dotenv()

logger = logging.getLogger(__name__)

HERMES_IMAGE = os.environ.get("HERMES_DOCKER_IMAGE", "wildclawbench-hermes-agent:v0.5")
HERMES_HOME = "/root/.hermes"
HERMES_INSTALL_DIR = "/opt/hermes"
HERMES_VENV_PYTHON = "/opt/hermes/.venv/bin/python3"

OPENCLAW_COMPAT_TRANSCRIPT_PATH = "/root/.openclaw/agents/main/sessions/chat.jsonl"
BENCH_RUNNER_HOST_PATH = Path(__file__).with_name("bench_runner.py")
BENCH_CONFIG_CONTAINER_PATH = "/tmp/hermes_bench_config.json"
COMPAT_TRANSCRIPT_HOST_PATH = Path(__file__).with_name("compat_transcript.py")


class HermesAgentAgent(BaseAgent):
    def __init__(
        self,
        image: str | None = None,
        openrouter_api_key: str = "",
        openrouter_base_url: str = "https://openrouter.ai/api/v1",
        brave_api_key: str = "",
    ) -> None:
        self.image = image or HERMES_IMAGE
        self.openrouter_api_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.openrouter_base_url = openrouter_base_url
        self.brave_api_key = brave_api_key or os.environ.get("BRAVE_API_KEY", "")

    @property
    def expects_gateway(self) -> bool:
        return False

    @property
    def transcript_container_path(self) -> str:
        return OPENCLAW_COMPAT_TRANSCRIPT_PATH

    def prepare_grading_transcript(self, task_id: str) -> str:
        self._write_compat_transcript(task_id)
        return self.transcript_container_path

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        elapsed_time = float(spec.timeout_seconds)
        agent_proc = None

        try:
            api_key, base_url = self._resolve_runtime_provider(spec.model, spec.models_config)

            exec_path = os.path.join(spec.workspace_path, "exec")
            tmp_path = os.path.join(spec.workspace_path, "tmp")
            os.makedirs(exec_path, exist_ok=True)

            self._start_container(
                spec.task_id,
                exec_path,
                api_key=api_key,
                base_url=base_url,
                extra_env=spec.task.get("env", ""),
                tmp_path=tmp_path,
                lobster_env=spec.lobster.get("env") if spec.lobster else None,
            )
            if spec.lobster:
                inject_lobster_workspace(spec.task_id, spec.lobster["workspace"])

            self._prepare_workspace(spec.task_id)
            setup_skills(
                spec.task_id,
                spec.task.get("skills", ""),
                spec.task.get("skills_path", ""),
                container_skills_root=f"{HERMES_HOME}/skills",
            )
            run_warmup(spec.task_id, spec.task.get("warmup", ""))

            self._configure_hermes(spec.task_id, api_key, base_url)

            reasoning_config = self._map_thinking(spec.thinking)
            self._write_bench_runner(
                spec.task_id, spec.prompt, spec.model,
                api_key, base_url, reasoning_config,
            )

            start_time = time.perf_counter()

            agent_proc = self._run_bench_runner_background(
                task_id=spec.task_id,
                log_path=spec.output_dir / "agent.log",
            )

            logger.info("[%s] Waiting for hermes-agent to finish...", spec.task_id)
            try:
                agent_proc.wait(timeout=spec.timeout_seconds)
                elapsed_time = time.perf_counter() - start_time
                logger.info(
                    "[%s] hermes-agent finished, elapsed: %.2f seconds",
                    spec.task_id,
                    elapsed_time,
                )
            except subprocess.TimeoutExpired:
                logger.info("[%s] hermes-agent timed out...", spec.task_id)
                elapsed_time = float(spec.timeout_seconds)
                agent_proc.kill()
                agent_proc.wait()
            self._close_runner_streams(agent_proc)

            logger.info("[%s] hermes-agent exit code: %s", spec.task_id, agent_proc.returncode)
            self._cleanup_bench_config(spec.task_id)

            return AgentExecution(
                elapsed_time=elapsed_time,
                error=None,
                gateway_proc=None,
                agent_proc=agent_proc,
            )
        except Exception as exc:
            if agent_proc is not None:
                self._close_runner_streams(agent_proc)
            self._cleanup_bench_config(spec.task_id)
            logger.error("[%s] hermes-agent execution error: %s", spec.task_id, exc)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error=str(exc),
                gateway_proc=None,
                agent_proc=agent_proc,
            )

    def collect_usage(self, task_id: str, output_dir: Path, elapsed_time: float) -> dict[str, Any]:
        transcript_host = output_dir / "chat.jsonl"
        output_dir.mkdir(parents=True, exist_ok=True)
        r_cp = subprocess.run(
            ["docker", "cp", f"{task_id}:{self.transcript_container_path}", str(transcript_host)],
            capture_output=True,
            text=True,
        )
        if r_cp.returncode == 0 and transcript_host.exists():
            usage = extract_usage_from_jsonl(transcript_host)
        else:
            logger.warning("[%s] Transcript copy failed: %s", task_id, r_cp.stderr.strip())
            usage = self._extract_usage_from_session_logs(task_id)

        if self._usage_has_no_tokens(usage):
            log_usage = self._extract_usage_from_agent_log(output_dir / "agent.log")
            if not self._usage_has_no_tokens(log_usage):
                usage = log_usage

        self._copy_session_log(task_id, output_dir)

        usage["elapsed_time"] = round(elapsed_time, 2)
        return usage

    # ------------------------------------------------------------------
    # Provider / thinking helpers
    # ------------------------------------------------------------------

    def _resolve_runtime_provider(self, model: str, models_config: dict | None) -> tuple[str, str]:
        api_key = self.openrouter_api_key
        base_url = self.openrouter_base_url
        config_key, config_base_url = self._resolve_provider_config(model, models_config)
        if config_key:
            api_key = config_key
        if config_base_url:
            base_url = config_base_url
        return api_key, base_url

    @staticmethod
    def _resolve_provider_config(model: str, models_config: dict | None) -> tuple[str, str]:
        """Extract api_key and base_url from *models_config* for *model*.

        Returns (api_key, base_url) — either or both may be empty strings
        if the config does not contain a matching provider.
        """
        if not models_config:
            return "", ""
        providers = models_config.get("providers", {})
        # Try exact model-id match first.
        for _prov_name, prov in providers.items():
            if not isinstance(prov, dict):
                continue
            for m in prov.get("models", []):
                if isinstance(m, dict) and m.get("id") == model:
                    return prov.get("apiKey", ""), prov.get("baseUrl", "")
        # No exact match — fall back to the first (usually only) provider.
        if providers:
            first = next(iter(providers.values()))
            if isinstance(first, dict):
                return first.get("apiKey", ""), first.get("baseUrl", "")
        return "", ""

    @staticmethod
    def _map_thinking(thinking: str | None) -> dict | None:
        """Map the benchmark ``thinking`` value to a Hermes *reasoning_config* dict."""
        if thinking is None:
            return None
        t = thinking.strip().lower()
        if t in ("off", "none", "disabled", "false"):
            return {"enabled": False}
        if t in ("on", "enabled", "medium", "true"):
            return {"enabled": True, "effort": "medium"}
        if t == "high":
            return {"enabled": True, "effort": "high"}
        if t in ("low", "minimal"):
            return {"enabled": True, "effort": "low"}
        return {"enabled": True, "effort": t}

    # ------------------------------------------------------------------
    # Container setup helpers
    # ------------------------------------------------------------------

    def _start_container(
        self,
        task_id: str,
        workspace_path: str,
        api_key: str,
        base_url: str,
        extra_env: str = "",
        tmp_path: str = "",
        lobster_env: list[str] | None = None,
    ) -> None:
        from src.utils.docker_utils import (
            build_env_args,
            _validate_docker_token,
            _validate_env_arg,
        )
        _validate_docker_token("task_id", task_id)

        proxy_http = os.environ.get("HTTP_PROXY_INNER", "")
        proxy_https = os.environ.get("HTTPS_PROXY_INNER", "")
        no_proxy = "" if not proxy_http else os.environ.get("NO_PROXY_INNER", "")
        env_pairs: list[tuple[str, str]] = [
            ("http_proxy", proxy_http),
            ("https_proxy", proxy_https),
            ("HTTP_PROXY", proxy_http),
            ("HTTPS_PROXY", proxy_https),
            ("BRAVE_API_KEY", self.brave_api_key),
            ("OPENROUTER_API_KEY", api_key),
            ("OPENROUTER_BASE_URL", base_url),
            ("no_proxy", no_proxy),
        ]
        for line in extra_env.splitlines():
            key = line.strip()
            if not key or key.startswith("#"):
                continue
            value = os.environ.get(key, "")
            _validate_env_arg(key, value)
            env_pairs.append((key, value))

        for key in (lobster_env or []):
            value = os.environ.get(key, "")
            if not value:
                continue
            _validate_env_arg(key, value)
            env_pairs.append((key, value))

        env_args = build_env_args(env_pairs)
        image = _validate_docker_token("image", self.image)

        cmd = [
            "docker", "run", "-d",
            "--name", task_id,
            *env_args,
            "-v", f"{workspace_path}:/app:ro",
            image,
            "/bin/bash", "-c", "tail -f /dev/null",
        ]
        logger.info("[%s] Starting hermes-agent container (image=%s)", task_id, image)
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"hermes-agent container startup failed:\n{r.stderr}")
        logger.info("[%s] Container ID: %s", task_id, r.stdout.strip()[:12])

        if tmp_path and os.path.exists(tmp_path):
            subprocess.run(
                ["docker", "exec", task_id, "mkdir", "-p", "/tmp_workspace/tmp"],
                capture_output=True,
            )
            cp_r = subprocess.run(
                ["docker", "cp", f"{tmp_path}/.", f"{task_id}:/tmp_workspace/tmp/"],
                capture_output=True, text=True,
            )
            if cp_r.returncode != 0:
                logger.error("[%s] Temp file copy failed: %s", task_id, cp_r.stderr)

    def _prepare_workspace(self, task_id: str) -> None:
        r = subprocess.run(
            [
                "docker", "exec", task_id, "/bin/bash", "-c",
                f"mkdir -p {TMP_WORKSPACE} && cp -r /app/. {TMP_WORKSPACE} && chmod -R u+w {TMP_WORKSPACE}",
            ],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"hermes-agent workspace copy failed:\n{r.stderr}")

    def _configure_hermes(self, task_id: str, api_key: str = "", base_url: str = "") -> None:
        """Configure hermes-agent inside the container with one consistent provider config."""
        hermes_yaml = (
            "tools:\n"
            "  profile: coding\n"
            "  web:\n"
            "    search:\n"
            "      enabled: true\n"
            "      provider: brave\n"
        )
        hermes_env = (
            f"OPENROUTER_API_KEY={api_key}\n"
            f"OPENROUTER_BASE_URL={base_url}\n"
            f"BRAVE_API_KEY={self.brave_api_key}\n"
        )

        with tempfile.TemporaryDirectory(prefix="hermes_config_") as tmp_dir:
            tmp_root = Path(tmp_dir)
            yaml_host = tmp_root / "hermes.yaml"
            env_host = tmp_root / ".env"
            yaml_host.write_text(hermes_yaml, encoding="utf-8")
            env_host.write_text(hermes_env, encoding="utf-8")

            r_mkdir = subprocess.run(
                [
                    "docker",
                    "exec",
                    task_id,
                    "/bin/bash",
                    "-c",
                    f"mkdir -p {HERMES_HOME} && mkdir -p $(dirname {OPENCLAW_COMPAT_TRANSCRIPT_PATH})",
                ],
                capture_output=True,
                text=True,
            )
            if r_mkdir.returncode != 0:
                raise RuntimeError(f"hermes-agent config mkdir failed:\n{r_mkdir.stderr}")

            for src, dst in (
                (yaml_host, f"{HERMES_HOME}/hermes.yaml"),
                (env_host, f"{HERMES_HOME}/.env"),
            ):
                copied = subprocess.run(
                    ["docker", "cp", str(src), f"{task_id}:{dst}"],
                    capture_output=True,
                    text=True,
                )
                if copied.returncode != 0:
                    raise RuntimeError(f"hermes-agent config copy failed ({dst}):\n{copied.stderr}")

            r_link = subprocess.run(
                ["docker", "exec", task_id, "ln", "-sfn", TMP_WORKSPACE, f"{HERMES_HOME}/workspace"],
                capture_output=True,
                text=True,
            )
            if r_link.returncode != 0:
                raise RuntimeError(f"hermes-agent workspace link failed:\n{r_link.stderr}")

        logger.info("[%s] hermes-agent configured", task_id)

    def _write_bench_runner(
        self,
        task_id: str,
        prompt: str,
        model: str,
        api_key: str,
        base_url: str,
        reasoning_config: dict | None,
    ) -> None:
        """Write the bench runner config into the container."""
        config_payload = {
            "config": {
                "model": model,
                "api_key": api_key,
                "base_url": base_url,
                "max_iterations": 90,
                "reasoning_config": reasoning_config,
            },
            "prompt": prompt,
        }

        config_tmp = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False, encoding="utf-8",
            ) as f:
                json.dump(config_payload, f, ensure_ascii=False)
                config_tmp = f.name

            r = subprocess.run(
                ["docker", "cp", config_tmp, f"{task_id}:{BENCH_CONFIG_CONTAINER_PATH}"],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                raise RuntimeError(f"Failed to copy {BENCH_CONFIG_CONTAINER_PATH} into container:\n{r.stderr}")
        finally:
            for p in (config_tmp,):
                if p:
                    Path(p).unlink(missing_ok=True)

    def _run_bench_runner_background(self, task_id: str, log_path: Path) -> subprocess.Popen[str]:
        if not BENCH_RUNNER_HOST_PATH.exists():
            raise RuntimeError(f"Hermes bench runner script not found: {BENCH_RUNNER_HOST_PATH}")

        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_file = log_path.open("w", encoding="utf-8")
        script_file = BENCH_RUNNER_HOST_PATH.open("r", encoding="utf-8")
        proc = subprocess.Popen(
            [
                "docker",
                "exec",
                "-i",
                task_id,
                "/bin/bash",
                "-c",
                f"cd {HERMES_INSTALL_DIR} && {HERMES_VENV_PYTHON} -",
            ],
            stdin=script_file,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        proc._log_file = log_file  # type: ignore[attr-defined]
        proc._script_file = script_file  # type: ignore[attr-defined]
        logger.info("[%s] Started Hermes bench runner PID=%s -> %s", task_id, proc.pid, log_path)
        return proc

    @staticmethod
    def _close_runner_streams(proc: subprocess.Popen[str] | None) -> None:
        if proc is None:
            return
        stream = getattr(proc, "_script_file", None)
        if stream is not None:
            try:
                stream.close()
            except Exception:
                pass

    @staticmethod
    def _cleanup_bench_config(task_id: str) -> None:
        subprocess.run(
            ["docker", "exec", task_id, "rm", "-f", BENCH_CONFIG_CONTAINER_PATH],
            capture_output=True,
            text=True,
        )

    # ------------------------------------------------------------------
    # Transcript conversion (all sessions merged)
    # ------------------------------------------------------------------

    def _write_compat_transcript(self, task_id: str) -> None:
        """Convert Hermes session logs to OpenClaw-compatible JSONL for grading."""
        if not COMPAT_TRANSCRIPT_HOST_PATH.exists():
            logger.warning(
                "[%s] Compat transcript script not found: %s",
                task_id,
                COMPAT_TRANSCRIPT_HOST_PATH,
            )
            return

        with COMPAT_TRANSCRIPT_HOST_PATH.open("r", encoding="utf-8") as script_file:
            r = subprocess.run(
                [
                    "docker",
                    "exec",
                    "-i",
                    task_id,
                    HERMES_VENV_PYTHON,
                    "-",
                ],
                stdin=script_file,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        if r.returncode != 0:
            logger.warning("[%s] Compat transcript write failed: %s", task_id, r.stderr)
        else:
            logger.info("[%s] Compat transcript written to %s", task_id, OPENCLAW_COMPAT_TRANSCRIPT_PATH)

    # ------------------------------------------------------------------
    # Usage extraction (all sessions merged)
    # ------------------------------------------------------------------

    def _extract_usage_from_session_logs(self, task_id: str) -> dict[str, Any]:
        """Fallback: extract usage from copied Hermes session JSON files."""
        usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }

        with tempfile.TemporaryDirectory(prefix="hermes_usage_") as tmp_dir:
            sessions_host = Path(tmp_dir) / "sessions"
            sessions_host.mkdir(parents=True, exist_ok=True)
            copied = subprocess.run(
                ["docker", "cp", f"{task_id}:{HERMES_HOME}/sessions/.", str(sessions_host)],
                capture_output=True,
                text=True,
            )
            if copied.returncode != 0:
                return usage

            total_requests = 0
            for session_file in sorted(sessions_host.glob("session_*.json"), key=lambda p: p.stat().st_mtime):
                try:
                    payload = json.loads(session_file.read_text(encoding="utf-8"))
                except Exception:
                    continue
                messages = payload.get("messages", [])
                if not isinstance(messages, list):
                    continue
                total_requests += sum(
                    1 for item in messages if isinstance(item, dict) and item.get("role") == "assistant"
                )
            usage["request_count"] = total_requests

        return usage

    def _usage_has_no_tokens(self, usage: dict[str, Any]) -> bool:
        return (
            usage.get("input_tokens", 0) == 0
            and usage.get("output_tokens", 0) == 0
            and usage.get("total_tokens", 0) == 0
        )

    def _extract_usage_from_agent_log(self, log_path: Path) -> dict[str, Any]:
        usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }
        if not log_path.exists():
            return usage

        for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "API Response received" not in line or (
                "CompletionUsage(" not in line and "ResponseUsage(" not in line
            ):
                continue
            usage["request_count"] += 1
            usage["input_tokens"] += (
                self._extract_int_from_log(line, "prompt_tokens")
                or self._extract_int_from_log(line, "input_tokens")
            )
            usage["output_tokens"] += (
                self._extract_int_from_log(line, "completion_tokens")
                or self._extract_int_from_log(line, "output_tokens")
            )
            usage["total_tokens"] += self._extract_int_from_log(line, "total_tokens")
            usage["cache_read_tokens"] += self._extract_int_from_log(line, "cached_tokens")
            usage["cache_write_tokens"] += self._extract_int_from_log(line, "cache_write_tokens")
            usage["cost_usd"] += self._extract_float_from_log(line, "cost")

        usage["cost_usd"] = round(usage["cost_usd"], 6)
        return usage

    def _extract_int_from_log(self, line: str, field: str) -> int:
        match = re.search(rf"\b{re.escape(field)}=(\d+)", line)
        return int(match.group(1)) if match else 0

    def _extract_float_from_log(self, line: str, field: str) -> float:
        match = re.search(rf"\b{re.escape(field)}=([0-9.eE+-]+)", line)
        return float(match.group(1)) if match else 0.0

    def _copy_session_log(self, task_id: str, output_dir: Path) -> None:
        """Copy *all* hermes session logs from the container to the output directory."""
        hermes_log_dest = output_dir / "hermes_session"
        hermes_log_dest.mkdir(parents=True, exist_ok=True)

        r = subprocess.run(
            ["docker", "cp", f"{task_id}:{HERMES_HOME}/sessions/.", str(hermes_log_dest)],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            logger.info("[%s] Hermes session logs copied to %s", task_id, hermes_log_dest)
        else:
            logger.warning("[%s] Hermes session log copy failed: %s", task_id, r.stderr.strip())
