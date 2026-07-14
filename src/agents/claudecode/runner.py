from __future__ import annotations

import json
import logging
import os
import shlex
import subprocess
import tempfile
import time
from pathlib import Path, PurePosixPath
from typing import Any

from dotenv import load_dotenv

from src.agents.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.agents.claudecode.transcript import convert_claudecode_chat_to_openclaw_jsonl
from src.utils.docker_utils import run_warmup, setup_skills, snapshot_workspace_state
from src.utils.endpoint_utils import normalize_openrouter_base_url_for_claudecode

load_dotenv()

logger = logging.getLogger(__name__)
CLAUDECODE_SKILLS_DIR = "/root/.claude/skills"
CLAUDECODE_COMPAT_TRANSCRIPT_PATH = "/tmp/claudecode/openclaw_chat.jsonl"
OPENCLAW_COMPAT_TRANSCRIPT_PATH = "/root/.openclaw/agents/main/sessions/chat.jsonl"


class ClaudeCodeAgent(BaseAgent):
    def __init__(
        self,
        image: str | None = None,
        anthropic_api_key: str = "",
        anthropic_base_url: str = "",
        openrouter_base_url: str = "",
    ) -> None:
        self.image = (
            image
            or os.environ.get("DOCKER_IMAGE_CLAUDECODE")
            or os.environ.get("CLAUDECODE_DOCKER_IMAGE")
            or "wildclawbench-claudecode-ubuntu:v0.2"
        )
        explicit_api_key = anthropic_api_key.strip()
        self.api_key = explicit_api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.openrouter_base_url = normalize_openrouter_base_url_for_claudecode(
            openrouter_base_url or os.environ.get("OPENROUTER_BASE_URL", "")
        )
        explicit_base_url = anthropic_base_url.strip()
        self.api_base_url = explicit_base_url.rstrip("/") if explicit_base_url else self.openrouter_base_url

    @property
    def expects_gateway(self) -> bool:
        return False

    @property
    def transcript_container_path(self) -> str:
        return "/claude_code/log/chat.json"

    def prepare_grading_transcript(self, task_id: str) -> str:
        with tempfile.TemporaryDirectory(prefix="claudecode_transcript_") as tmp_dir:
            tmp_root = Path(tmp_dir)
            chat_host = tmp_root / "chat.json"
            compat_host = tmp_root / "chat.jsonl"

            r_cp = subprocess.run(
                ["docker", "cp", f"{task_id}:{self.transcript_container_path}", str(chat_host)],
                capture_output=True,
                text=True,
            )
            if r_cp.returncode != 0:
                logger.warning(
                    "[%s] Failed to copy ClaudeCode transcript for grading: %s",
                    task_id,
                    r_cp.stderr.strip(),
                )
                return self.transcript_container_path

            converted_count = convert_claudecode_chat_to_openclaw_jsonl(chat_host, compat_host)
            container_parent = str(PurePosixPath(CLAUDECODE_COMPAT_TRANSCRIPT_PATH).parent)
            r_mkdir = subprocess.run(
                ["docker", "exec", task_id, "mkdir", "-p", container_parent],
                capture_output=True,
                text=True,
            )
            if r_mkdir.returncode != 0:
                logger.warning(
                    "[%s] Failed to create ClaudeCode compat transcript dir (%s): %s",
                    task_id,
                    container_parent,
                    r_mkdir.stderr.strip(),
                )
                return self.transcript_container_path

            r_push = subprocess.run(
                ["docker", "cp", str(compat_host), f"{task_id}:{CLAUDECODE_COMPAT_TRANSCRIPT_PATH}"],
                capture_output=True,
                text=True,
            )
            if r_push.returncode != 0:
                logger.warning(
                    "[%s] Failed to copy ClaudeCode compat transcript into container: %s",
                    task_id,
                    r_push.stderr.strip(),
                )
                return self.transcript_container_path

            openclaw_parent = str(PurePosixPath(OPENCLAW_COMPAT_TRANSCRIPT_PATH).parent)
            r_openclaw_mkdir = subprocess.run(
                ["docker", "exec", task_id, "mkdir", "-p", openclaw_parent],
                capture_output=True,
                text=True,
            )
            if r_openclaw_mkdir.returncode == 0:
                r_openclaw_push = subprocess.run(
                    ["docker", "cp", str(compat_host), f"{task_id}:{OPENCLAW_COMPAT_TRANSCRIPT_PATH}"],
                    capture_output=True,
                    text=True,
                )
                if r_openclaw_push.returncode != 0:
                    logger.warning(
                        "[%s] Failed to copy ClaudeCode compat transcript to OpenClaw path: %s",
                        task_id,
                        r_openclaw_push.stderr.strip(),
                    )
            else:
                logger.warning(
                    "[%s] Failed to create OpenClaw compat transcript dir (%s): %s",
                    task_id,
                    openclaw_parent,
                    r_openclaw_mkdir.stderr.strip(),
                )

            logger.info(
                "[%s] ClaudeCode transcript normalized for grading (%d messages): %s",
                task_id,
                converted_count,
                CLAUDECODE_COMPAT_TRANSCRIPT_PATH,
            )
            return CLAUDECODE_COMPAT_TRANSCRIPT_PATH

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        elapsed_time = float(spec.timeout_seconds)
        start_time = time.perf_counter()
        task_id = spec.task_id

        try:
            self._start_container(task_id, spec.workspace_path)
            self._prepare_workspace(task_id)
            self._copy_tmp_files(task_id, spec.workspace_path)
            setup_skills(
                task_id,
                spec.task.get("skills", ""),
                spec.task.get("skills_path", ""),
                container_skills_root=CLAUDECODE_SKILLS_DIR,
            )
            run_warmup(task_id, spec.task.get("warmup", ""))
            snapshot_workspace_state(task_id)
            self._run_prompt(
                task_id,
                spec.prompt,
                spec.model,
                spec.timeout_seconds,
                spec.output_dir,
            )
            elapsed_time = time.perf_counter() - start_time
            return AgentExecution(elapsed_time=elapsed_time, error=None, gateway_proc=None, agent_proc=None)
        except subprocess.TimeoutExpired:
            logger.info("[%s] ClaudeCode timed out...", task_id)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error="ClaudeCode run timed out",
                gateway_proc=None,
                agent_proc=None,
            )
        except Exception as exc:
            logger.error("[%s] ClaudeCode execution error: %s", task_id, exc)
            return AgentExecution(
                elapsed_time=elapsed_time,
                error=str(exc),
                gateway_proc=None,
                agent_proc=None,
            )

    def collect_usage(self, task_id: str, output_dir: Path, elapsed_time: float) -> dict[str, Any]:
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

        log_dest = output_dir / "claude_code_log"
        log_dest.mkdir(parents=True, exist_ok=True)
        self._copy_file_from_container(task_id, "/claude_code/log/usage.json", log_dest / "usage.json")
        self._copy_file_from_container(task_id, "/claude_code/log/chat.json", log_dest / "chat.json")
        self._copy_dir_from_container(task_id, "/claude_code/log/.", log_dest)
        self._sync_agent_log_from_claude_logs(task_id, output_dir, log_dest)

        parsed = self._extract_usage_from_chat_json(log_dest / "chat.json")
        if parsed["request_count"] == 0:
            parsed = self._extract_usage_from_usage_json(log_dest / "usage.json")
        if parsed["request_count"] == 0:
            parsed["request_count"] = self._extract_request_count_from_chat_json(log_dest / "chat.json")
        if parsed["request_count"] == 0:
            fallback = self._extract_usage_from_logs(log_dest)
            for key in (
                "input_tokens",
                "output_tokens",
                "cache_read_tokens",
                "cache_write_tokens",
                "total_tokens",
                "cost_usd",
                "request_count",
            ):
                parsed_value = parsed.get(key, 0)
                fallback_value = fallback.get(key, 0)
                if (parsed_value is None or parsed_value <= 0) and fallback_value > 0:
                    parsed[key] = fallback_value

        usage.update(parsed)
        usage["elapsed_time"] = round(elapsed_time, 2)
        return usage

    def _extract_usage_from_chat_json(self, chat_path: Path) -> dict[str, Any]:
        totals = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }
        if not chat_path.exists():
            return totals

        try:
            content = chat_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return totals

        payloads: list[Any] = []
        try:
            parsed = json.loads(content)
            payloads = parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            for line in content.splitlines():
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    payloads.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        for payload in payloads:
            self._accumulate_costed_usage(payload, totals)

        totals["total_tokens"] = (
            totals["input_tokens"]
            + totals["output_tokens"]
            + totals["cache_read_tokens"]
            + totals["cache_write_tokens"]
        )
        if totals["request_count"] > 0 and totals["cost_usd"] == 0.0:
            totals["cost_usd"] = self._estimate_cost(totals)
        totals["cost_usd"] = round(totals["cost_usd"], 6)
        return totals

    def _accumulate_costed_usage(self, payload: Any, totals: dict[str, Any]) -> None:
        if isinstance(payload, list):
            for item in payload:
                self._accumulate_costed_usage(item, totals)
            return
        if not isinstance(payload, dict):
            return

        if (
            "input_tokens" in payload
            and "output_tokens" in payload
            and ("cost_details" in payload or "cost" in payload)
        ):
            input_tokens = int(payload.get("input_tokens") or 0)
            output_tokens = int(payload.get("output_tokens") or 0)
            cache_read_tokens = int(payload.get("cache_read_input_tokens") or 0)
            cache_write_tokens = int(payload.get("cache_creation_input_tokens") or 0)
            cost_details = payload.get("cost_details")
            cost = self._num(
                cost_details.get("upstream_inference_cost") if isinstance(cost_details, dict) else payload.get("cost"),
                default=0.0,
            )

            if (
                input_tokens == 0
                and output_tokens == 0
                and cache_read_tokens == 0
                and cache_write_tokens == 0
                and cost == 0
            ):
                return

            totals["input_tokens"] += input_tokens
            totals["output_tokens"] += output_tokens
            totals["cache_read_tokens"] += cache_read_tokens
            totals["cache_write_tokens"] += cache_write_tokens
            totals["cost_usd"] += cost
            totals["request_count"] += 1
            return

        for value in payload.values():
            self._accumulate_costed_usage(value, totals)

    def _sync_agent_log_from_claude_logs(self, task_id: str, output_dir: Path, log_dest: Path) -> None:
        candidates = (
            log_dest / "agent.log",
            log_dest / "chat.json",
            log_dest / "chat.jsonl",
        )
        for src in candidates:
            if not src.exists() or not src.is_file():
                continue
            try:
                content = src.read_text(encoding="utf-8", errors="ignore")
            except Exception as exc:
                logger.warning("[%s] Failed to read ClaudeCode log source %s: %s", task_id, src, exc)
                continue
            if not content.strip():
                continue
            try:
                (output_dir / "agent.log").write_text(content, encoding="utf-8")
            except Exception as exc:
                logger.warning("[%s] Failed to write agent.log from %s: %s", task_id, src, exc)
                return
            logger.info("[%s] agent.log synced from %s", task_id, src)
            return

    def _copy_file_from_container(self, task_id: str, src: str, dest: Path) -> None:
        r = subprocess.run(
            ["docker", "cp", f"{task_id}:{src}", str(dest)],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            logger.warning("[%s] ClaudeCode file copy failed (%s): %s", task_id, src, r.stderr.strip())

    def _copy_dir_from_container(self, task_id: str, src: str, dest: Path) -> None:
        r = subprocess.run(
            ["docker", "cp", f"{task_id}:{src}", str(dest)],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            logger.warning("[%s] ClaudeCode log dir copy failed: %s", task_id, r.stderr.strip())

    def _start_container(self, task_id: str, workspace_path: str) -> None:
        from src.utils.docker_utils import (
            build_env_args,
            _validate_docker_token,
        )
        _validate_docker_token("task_id", task_id)

        proxy_http = os.environ.get("HTTP_PROXY_INNER", "")
        proxy_https = os.environ.get("HTTPS_PROXY_INNER", "")
        env_map = {
            "ANTHROPIC_API_KEY": self.api_key,
            "ANTHROPIC_BASE_URL": self.api_base_url,
            "OPENROUTER_API_KEY": self.api_key,
            "OPENROUTER_BASE_URL": self.openrouter_base_url,
            "DISABLE_PROMPT_CACHING": os.environ.get("DISABLE_PROMPT_CACHING", "1"),
            "DISABLE_INTERLEAVED_THINKING": os.environ.get("DISABLE_INTERLEAVED_THINKING", "1"),
            "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS": os.environ.get("CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS", "1"),
            "IS_SANDBOX": os.environ.get("IS_SANDBOX", "1"),
            "CLAUDE_CODE_FULL_LOG_PATH": os.environ.get("CLAUDE_CODE_FULL_LOG_PATH", "./log"),
            "http_proxy": proxy_http,
            "https_proxy": proxy_https,
            "HTTP_PROXY": proxy_http,
            "HTTPS_PROXY": proxy_https,
        }
        env_args = build_env_args(
            [(k, v) for k, v in env_map.items() if v]
        )
        image = _validate_docker_token("image", self.image)

        exec_path = os.path.join(workspace_path, "exec")
        os.makedirs(exec_path, exist_ok=True)
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
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"ClaudeCode container startup failed:\n{r.stderr}")
        self._patch_claudecode_runtime(task_id)

    def _patch_claudecode_runtime(self, task_id: str) -> None:
        patch_cmd = r"""python3 - <<'PY'
from pathlib import Path

path = Path("/claude_code/src/tasks/LocalAgentTask/LocalAgentTask.tsx")
text = path.read_text(encoding="utf-8")
old = "  const usage = message.message.usage;\n  // Keep latest input (it's cumulative in the API), sum outputs\n"
new = '''  const usage = message.message.usage ?? {
    input_tokens: 0,
    cache_creation_input_tokens: 0,
    cache_read_input_tokens: 0,
    output_tokens: 0,
  };
  // Keep latest input (it's cumulative in the API), sum outputs
'''
if old in text and new not in text:
    path.write_text(text.replace(old, new), encoding="utf-8")
PY"""
        r = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", patch_cmd],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            logger.warning("[%s] ClaudeCode runtime patch failed: %s", task_id, r.stderr.strip())

    def _prepare_workspace(self, task_id: str) -> None:
        r = subprocess.run(
            [
                "docker",
                "exec",
                task_id,
                "/bin/bash",
                "-c",
                "mkdir -p /tmp_workspace && cp -r /workspace/. /tmp_workspace && chmod -R u+w /tmp_workspace",
            ],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"ClaudeCode workspace copy failed:\n{r.stderr}")

    def _copy_tmp_files(self, task_id: str, workspace_path: str) -> None:
        tmp_path = Path(workspace_path) / "tmp"
        if not tmp_path.exists():
            return
        r_mkdir = subprocess.run(
            ["docker", "exec", task_id, "mkdir", "-p", "/tmp_workspace/tmp"],
            capture_output=True,
            text=True,
        )
        if r_mkdir.returncode != 0:
            raise RuntimeError(f"ClaudeCode tmp directory setup failed:\n{r_mkdir.stderr}")
        r_cp = subprocess.run(
            ["docker", "cp", f"{tmp_path}/.", f"{task_id}:/tmp_workspace/tmp/"],
            capture_output=True,
            text=True,
        )
        if r_cp.returncode != 0:
            raise RuntimeError(f"ClaudeCode tmp copy failed:\n{r_cp.stderr}")

    def _run_prompt(self, task_id: str, prompt: str, model: str, timeout_seconds: int, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        cmd = (
            f"cd /claude_code && "
            f"IS_SANDBOX=1 ./start.sh "
            f"--add-dir /tmp_workspace "
            f"-p {shlex.quote(prompt)} "
            f"--model {shlex.quote(model)}"
        )
        r = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", cmd],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        (output_dir / "agent.log").write_text(
            (r.stdout or "") + ("\n" if r.stdout else "") + (r.stderr or ""),
            encoding="utf-8",
        )
        if r.returncode != 0:
            raise RuntimeError(f"ClaudeCode run failed (rc={r.returncode}):\n{r.stderr}")

    def _extract_usage_from_logs(self, log_dir: Path) -> dict[str, Any]:
        totals = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }
        if not log_dir.exists():
            return totals

        for file_path in log_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in {".json", ".jsonl", ".log", ".txt"}:
                continue
            self._accumulate_from_file(file_path, totals)

        totals["total_tokens"] = (
            totals["input_tokens"]
            + totals["output_tokens"]
            + totals["cache_read_tokens"]
            + totals["cache_write_tokens"]
        )
        totals["cost_usd"] = round(self._estimate_cost(totals), 6)
        return totals

    def _extract_usage_from_usage_json(self, usage_path: Path) -> dict[str, Any]:
        totals = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
        }
        if not usage_path.exists():
            return totals

        try:
            payload = json.loads(usage_path.read_text(encoding="utf-8"))
        except Exception:
            return totals

        if not isinstance(payload, dict):
            return totals

        # Support both known schemas:
        # 1) totalInputTokens / totalOutputTokens / totalCostUSD / modelUsage
        # 2) total_cost_usd + nested usage.{input_tokens,output_tokens,...}
        usage_block = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}

        totals["input_tokens"] = int(
            self._num(
                payload.get("totalInputTokens", usage_block.get("input_tokens")),
            )
        )
        totals["output_tokens"] = int(
            self._num(
                payload.get("totalOutputTokens", usage_block.get("output_tokens")),
            )
        )
        totals["cache_read_tokens"] = int(
            self._num(
                payload.get("totalCacheReadInputTokens", usage_block.get("cache_read_input_tokens")),
            )
        )
        totals["cache_write_tokens"] = int(
            self._num(
                payload.get("totalCacheCreationInputTokens", usage_block.get("cache_creation_input_tokens")),
            )
        )
        totals["cost_usd"] = round(
            self._num(
                payload.get("totalCostUSD", payload.get("total_cost_usd")),
                default=0.0,
            ),
            6,
        )

        totals["total_tokens"] = (
            totals["input_tokens"]
            + totals["output_tokens"]
            + totals["cache_read_tokens"]
            + totals["cache_write_tokens"]
        )

        totals["request_count"] = self._request_count_from_model_usage(payload.get("modelUsage"))
        return totals

    def _request_count_from_model_usage(self, model_usage: Any) -> int:
        if isinstance(model_usage, list):
            total = 0
            for item in model_usage:
                if not isinstance(item, dict):
                    continue
                total += int(
                    self._num(
                        item.get("requestCount", item.get("requests", item.get("count"))),
                        default=0,
                    )
                )
            return total

        if isinstance(model_usage, dict):
            total = 0
            for value in model_usage.values():
                if not isinstance(value, dict):
                    continue
                total += int(
                    self._num(
                        value.get("requestCount", value.get("requests", value.get("count"))),
                        default=0,
                    )
                )
            return total

        return 0

    def _extract_request_count_from_chat_json(self, chat_path: Path) -> int:
        if not chat_path.exists():
            return 0
        try:
            content = chat_path.read_text(encoding="utf-8")
        except Exception:
            return 0

        try:
            payload = json.loads(content)
        except Exception:
            payload = None

        if isinstance(payload, list):
            assistant_messages = [
                m
                for m in payload
                if isinstance(m, dict)
                and str(m.get("role", "")).lower() == "assistant"
            ]
            return len(assistant_messages)

        if isinstance(payload, dict):
            if str(payload.get("event", "")).lower() == "query_start":
                return 1
            return 0

        count = 0
        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if isinstance(row, dict) and str(row.get("event", "")).lower() == "query_start":
                count += 1
        if count > 0:
            return count
        return 0

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

    def _accumulate_from_file(self, file_path: Path, totals: dict[str, Any]) -> None:
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return

        for line in lines:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            usage = self._find_usage(payload)
            if usage is None:
                continue
            totals["request_count"] += 1
            totals["input_tokens"] += int(usage.get("input_tokens", usage.get("input", 0)) or 0)
            totals["output_tokens"] += int(usage.get("output_tokens", usage.get("output", 0)) or 0)
            totals["cache_read_tokens"] += int(
                usage.get("cache_read_input_tokens", usage.get("cacheRead", 0)) or 0
            )
            totals["cache_write_tokens"] += int(
                usage.get("cache_creation_input_tokens", usage.get("cacheWrite", 0)) or 0
            )

    def _find_usage(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if "usage" in payload and isinstance(payload["usage"], dict):
            return payload["usage"]
        message = payload.get("message")
        if isinstance(message, dict) and isinstance(message.get("usage"), dict):
            return message["usage"]
        return None

    def _estimate_cost(self, totals: dict[str, Any]) -> float:
        # Prices input_tokens in full (no cache subtraction): Claude Code's usage
        # already reports input_tokens cache-exclusive, with cache_read/cache_write
        # broken out separately. (Codex's estimator subtracts cache first because its
        # input field is cache-inclusive.) Rates default to 0 -> $0 if unset; see
        # CLAUDECODE_*_PRICE_PER_MTOK in .env.example.
        input_price = float(os.environ.get("CLAUDECODE_INPUT_PRICE_PER_MTOK", "0"))
        output_price = float(os.environ.get("CLAUDECODE_OUTPUT_PRICE_PER_MTOK", "0"))
        cache_read_price = float(os.environ.get("CLAUDECODE_CACHE_READ_PRICE_PER_MTOK", "0"))
        cache_write_price = float(os.environ.get("CLAUDECODE_CACHE_WRITE_PRICE_PER_MTOK", "0"))
        return (
            totals["input_tokens"] / 1_000_000 * input_price
            + totals["output_tokens"] / 1_000_000 * output_price
            + totals["cache_read_tokens"] / 1_000_000 * cache_read_price
            + totals["cache_write_tokens"] / 1_000_000 * cache_write_price
        )
