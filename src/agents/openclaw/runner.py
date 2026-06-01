from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from pathlib import Path

from dotenv import load_dotenv

from src.agents.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.utils.docker_utils import (
    inject_api_connectors,
    inject_lobster_workspace,
    inject_openclaw_models,
    run_background,
    run_warmup,
    setup_skills,
    setup_workspace,
    start_container,
)
from src.utils.grading import extract_usage_from_jsonl

load_dotenv()

logger = logging.getLogger(__name__)

# Logical model names used when routing through the LiteLLM sidecar.
MODEL_NAMES: dict[str, str] = {
    "claude": "claude-opus-4.7",
    "gpt": "gpt-5.5",
}

_GPT_PREFIXES = ("gpt", "o1", "o3", "o4", "llama", "mistral", "kimi", "deepseek", "gemini", "qwen")


def _normalize_openrouter_model(model: str) -> str:
    if model.startswith("openrouter/"):
        return model
    if "/" in model:
        return f"openrouter/{model}"
    if any(model.lower().startswith(p) for p in _GPT_PREFIXES):
        return f"openrouter/openai/{model}"
    return f"openrouter/anthropic/{model}"


class OpenClawAgent(BaseAgent):
    """OpenClaw backend with dual routing:

    - LiteLLM/Bedrock mode (when ``litellm_config_yaml`` is set): writes a
      ``models.providers.litellm`` block into openclaw.json pointing at the
      shared LiteLLM sidecar container, and skips OpenRouter auth.
    - OpenRouter mode (default fallback): injects the OpenRouter key into
      auth-profiles.json and sets the model via the normalized model string.
    """

    def __init__(
        self,
        gateway_port: int,
        openrouter_api_key: str = "",
        openrouter_base_url: str = "https://openrouter.ai/api/v1",
        openai_api_key: str = "",
        litellm_master_key: str = "",
        litellm_port: int = 4000,
        litellm_config_yaml: str = "",
        litellm_container_name: str = "",
        litellm_network: str = "",
        image_model: str | None = None,
    ) -> None:
        self.gateway_port = gateway_port
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_base_url = openrouter_base_url
        self.openai_api_key = openai_api_key
        self.litellm_master_key = litellm_master_key
        self.litellm_port = litellm_port
        self.litellm_config_yaml = litellm_config_yaml
        self.litellm_container_name = litellm_container_name
        self.litellm_network = litellm_network
        self.image_model = (
            image_model
            if image_model is not None
            else os.environ.get("OPENCLAW_IMAGE_MODEL", "").strip()
        )

    @property
    def expects_gateway(self) -> bool:
        return True

    @property
    def transcript_container_path(self) -> str:
        return "/root/.openclaw/agents/main/sessions/chat.jsonl"

    def prepare_grading_transcript(self, task_id: str) -> str:
        return self.transcript_container_path

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        gateway_proc = None
        agent_proc = None
        elapsed_time = float(spec.timeout_seconds)

        try:
            exec_path = os.path.join(spec.workspace_path, "exec")
            tmp_path = os.path.join(spec.workspace_path, "tmp")
            os.makedirs(exec_path, exist_ok=True)

            start_container(
                spec.task_id,
                exec_path,
                extra_env=spec.task.get("env", ""),
                tmp_path=tmp_path,
                lobster_env=spec.lobster.get("env") if spec.lobster else None,
                extra_env_dict=spec.task.get("env_dict") or None,
                network=self.litellm_network,
            )

            if spec.lobster:
                inject_lobster_workspace(spec.task_id, spec.lobster["workspace"])
                self._index_memory(spec.task_id)

            # Native (kensei2-style) task: inject the task-provided persona
            # (SOUL.md / MEMORY.md / AGENT(S).md, sent at runtime) into /root/ and
            # index it so the agent recalls it. Lives at <task_dir>/persona/.
            persona_dir = spec.task.get("persona_dir") if isinstance(spec.task, dict) else ""
            if persona_dir:
                inject_lobster_workspace(spec.task_id, persona_dir)
                self._index_memory(spec.task_id)

            setup_workspace(spec.task_id, thinking=spec.thinking)
            setup_skills(
                spec.task_id,
                spec.task.get("skills", ""),
                spec.task.get("skills_path", ""),
            )
            inject_api_connectors(
                spec.task_id,
                spec.task.get("env_dir", ""),
                spec.task.get("required_apis", []) or [],
            )

            run_warmup(spec.task_id, spec.task.get("warmup", ""))

            if spec.models_config:
                inject_openclaw_models(spec.task_id, spec.models_config)

            self._set_model(spec.task_id, spec.model, thinking=spec.thinking)
            self._inject_auth(spec.task_id)
            image_model = self.image_model or spec.model
            self._set_image_model(spec.task_id, image_model)

            gateway_cmd = f"openclaw gateway --port {self.gateway_port}"
            if self.openrouter_api_key and not self.litellm_config_yaml:
                gateway_cmd = (
                    f"export OPENROUTER_API_KEY='{self.openrouter_api_key}' && "
                    f"export OPENROUTER_BASE_URL='{self.openrouter_base_url}' && "
                    + gateway_cmd
                )
            if self.openai_api_key and not self.litellm_config_yaml:
                gateway_cmd = f"export OPENAI_API_KEY='{self.openai_api_key}' && " + gateway_cmd

            gateway_proc = run_background(
                spec.task_id,
                bash_cmd=gateway_cmd,
                log_path=spec.output_dir / "gateway.log",
            )
            logger.info("[%s] Waiting for gateway (2s)...", spec.task_id)
            time.sleep(2)

            safe_prompt = spec.prompt.replace("'", "'\\''")
            start_time = time.perf_counter()
            agent_proc = run_background(
                spec.task_id,
                bash_cmd=(
                    f"openclaw agent --session-id chat "
                    f"--timeout {spec.timeout_seconds} "
                    f"--message '{safe_prompt}'"
                ),
                log_path=spec.output_dir / "agent.log",
            )

            logger.info("[%s] Waiting for agent to finish...", spec.task_id)
            try:
                agent_proc.wait(timeout=spec.timeout_seconds)
                elapsed_time = time.perf_counter() - start_time
                logger.info("[%s] Agent finished (%.2fs)", spec.task_id, elapsed_time)
            except subprocess.TimeoutExpired:
                logger.warning("[%s] Agent timed out", spec.task_id)
                elapsed_time = float(spec.timeout_seconds)
                agent_proc.kill()
                agent_proc.wait()

            logger.info("[%s] Agent exit code: %s", spec.task_id, agent_proc.returncode)
            return AgentExecution(
                elapsed_time=elapsed_time,
                error=None,
                gateway_proc=gateway_proc,
                agent_proc=agent_proc,
            )

        except Exception as exc:
            logger.error("[%s] Execution error: %s", spec.task_id, exc)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error=str(exc),
                gateway_proc=gateway_proc,
                agent_proc=agent_proc,
            )

    def collect_usage(self, task_id: str, output_dir: Path, elapsed_time: float) -> dict:
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
            usage = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0,
                "request_count": 0,
                "usage_source": "none",
            }
        usage["elapsed_time"] = round(elapsed_time, 2)
        return usage

    def _set_model(self, task_id: str, model: str, thinking: str | None = None) -> None:
        if self.litellm_config_yaml:
            model_id = model[len("litellm/"):] if model.startswith("litellm/") else model
            primary = f"litellm/{model_id}"
            base_url = f"http://{self.litellm_container_name}:{self.litellm_port}/v1"
            litellm_provider = {
                "baseUrl": base_url,
                "apiKey": self.litellm_master_key or "sk-litellm",
                "auth": "api-key",
                "api": "openai-completions",
                "models": [
                    {"id": "claude-opus-4.7", "name": "claude-opus-4.7",
                     "input": ["text", "image"], "reasoning": True,
                     "contextWindow": 200000, "maxTokens": 128000},
                    {"id": "gpt-5.5", "name": "gpt-5.5",
                     "input": ["text", "image"], "reasoning": True,
                     "contextWindow": 1050000, "maxTokens": 128000},
                ],
            }
            thinking_default = (thinking or "").strip()
            set_thinking_line = (
                f'defaults["thinkingDefault"] = {json.dumps(thinking_default)}\n'
                if thinking_default and thinking_default.lower() not in {"off", "none", "disabled"}
                else ""
            )
            script = f"""\
import json, pathlib
p = pathlib.Path("/root/.openclaw/openclaw.json")
d = json.loads(p.read_text()) if p.exists() else {{}}
models = d.setdefault("models", {{}})
providers = models.setdefault("providers", {{}})
providers["litellm"] = json.loads({json.dumps(json.dumps(litellm_provider))})
agents = d.setdefault("agents", {{}})
defaults = agents.setdefault("defaults", {{}})
defaults["model"] = {{"primary": {json.dumps(primary)}}}
defaults["imageModel"] = {{"primary": {json.dumps(primary)}}}
defaults.pop("models", None)
{set_thinking_line}d["browser"] = {{"enabled": False}}
tools = d.setdefault("tools", {{}})
tools["deny"] = ["browser", "duckduckgo"]
web = tools.setdefault("web", {{}})
web["search"] = {{"enabled": False}}
web["fetch"] = {{"enabled": False}}
p.write_text(json.dumps(d, indent=2))
"""
        else:
            normalized = _normalize_openrouter_model(model)
            primary = normalized
            script = f"""\
import json, pathlib
p = pathlib.Path("/root/.openclaw/openclaw.json")
d = json.loads(p.read_text()) if p.exists() else {{}}
agents = d.setdefault("agents", {{}})
defaults = agents.setdefault("defaults", {{}})
defaults["model"] = {{"primary": {json.dumps(normalized)}}}
defaults["imageModel"] = {{"primary": {json.dumps(normalized)}}}
defaults.setdefault("models", {{}})[{json.dumps(normalized)}] = {{}}
d["browser"] = {{"enabled": False}}
tools = d.setdefault("tools", {{}})
tools["deny"] = ["browser", "duckduckgo"]
web = tools.setdefault("web", {{}})
web["search"] = {{"enabled": False}}
web["fetch"] = {{"enabled": False}}
p.write_text(json.dumps(d, indent=2))
"""
        r = subprocess.run(
            ["docker", "exec", "-i", task_id, "python3", "-"],
            input=script,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Model setup failed:\n{r.stderr}")
        logger.info("[%s] Model set in openclaw.json: %s", task_id, primary)

    def _inject_auth(self, task_id: str) -> None:
        # LiteLLM holds Bedrock/OpenAI creds via its own env; no agent-side key.
        if self.litellm_config_yaml:
            return
        if self.openai_api_key and not self.openrouter_api_key:
            key = self.openai_api_key
            profile_id = "openai:default"
            provider = "openai"
        elif self.openrouter_api_key:
            key = self.openrouter_api_key
            profile_id = "openrouter:default"
            provider = "openrouter"
        else:
            return

        auth_profile_path = "/root/.openclaw/agents/main/agent/auth-profiles.json"
        script = f"""\
import json, pathlib
p = pathlib.Path({json.dumps(auth_profile_path)})
d = json.loads(p.read_text()) if p.exists() else {{"version": 1, "profiles": {{}}}}
d.setdefault("profiles", {{}})[{json.dumps(profile_id)}] = {{
    "type": "api_key",
    "provider": {json.dumps(provider)},
    "key": {json.dumps(key)}
}}
p.write_text(json.dumps(d, indent=2))
"""
        subprocess.run(
            ["docker", "exec", "-i", task_id, "python3", "-"],
            input=script,
            capture_output=True,
            text=True,
        )
        logger.info("[%s] Injected %s key into auth-profiles.json", task_id, provider)

    def _set_image_model(self, task_id: str, model: str) -> None:
        if self.litellm_config_yaml:
            if model:
                logger.warning("[%s] image model %r ignored in LiteLLM mode; "
                               "imageModel mirrors the chat model", task_id, model)
            return
        subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c",
             f"openclaw config set agents.defaults.imageModel.primary '{model}'"],
            capture_output=True,
            text=True,
        )
        logger.info("[%s] imageModel set: %s", task_id, model)

    def _index_memory(self, task_id: str) -> None:
        cmd = (
            "mkdir -p /root/memory && "
            "for f in /root/MEMORY.md /root/SOUL.md /root/AGENT.md /root/AGENTS.md; do "
            '  [ -f "$f" ] && cp "$f" /root/memory/ || true; '
            "done && "
            "openclaw memory index --force 2>&1 | tail -3"
        )
        result = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", cmd],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.warning("[%s] memory index failed: %s", task_id, result.stderr[:200])
        else:
            logger.info("[%s] Memory indexed: %s", task_id, result.stdout.strip()[:200])
