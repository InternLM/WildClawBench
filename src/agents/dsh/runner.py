from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path

from src.agents.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.agents.dsh.config import PROVIDER_ID, patch_entry_yaml, resolve_rung
from src.utils.grading import extract_usage_from_jsonl
from src.utils.docker_utils import (
    run_background,
    run_warmup,
    setup_skills,
    setup_workspace,
    start_container,
)

logger = logging.getLogger(__name__)

COMPAT_TRANSCRIPT_HOST_PATH = Path(__file__).with_name("compat_transcript.py")
OPENCLAW_COMPAT_TRANSCRIPT_PATH = "/root/.openclaw/agents/main/sessions/chat.jsonl"
PATCH_CONTAINER_PATH = "/tmp/wcb-dsh.yml"
LB_FALLBACK_URL = "http://host.docker.internal:4000/v1"


class DshAgent(BaseAgent):
    def __init__(self, lb_base_url: str = "http://100.64.0.1:4000/v1") -> None:
        self.lb_base_url = lb_base_url.rstrip("/")
        self.lb_api_key = os.environ.get("WCB_LB_API_KEY", "")

    @property
    def expects_gateway(self) -> bool:
        return False

    @property
    def transcript_container_path(self) -> str:
        return OPENCLAW_COMPAT_TRANSCRIPT_PATH

    def validate_config(self, spec: AgentTaskSpec) -> str:
        return resolve_rung(spec.thinking)

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        rung = self.validate_config(spec)  # raises before any side effects
        elapsed_time = float(spec.timeout_seconds)
        agent_proc = None
        try:
            exec_path = os.path.join(spec.workspace_path, "exec")
            tmp_path = os.path.join(spec.workspace_path, "tmp")
            os.makedirs(exec_path, exist_ok=True)

            start_container(spec.task_id, exec_path,
                            extra_env=spec.task.get("env", ""), tmp_path=tmp_path)
            setup_workspace(spec.task_id)
            setup_skills(spec.task_id, spec.task.get("skills", ""),
                         spec.task.get("skills_path", ""),
                         container_skills_root="/root/.dsh/skills")
            run_warmup(spec.task_id, spec.task.get("warmup", ""))

            self._probe_lb(spec.task_id)
            self._write_patch(spec.task_id, spec.model, rung)

            safe_prompt = spec.prompt.replace("'", "'\\''")
            start_time = time.perf_counter()
            agent_proc = run_background(
                spec.task_id,
                bash_cmd=(f"export WCB_LB_API_KEY='{self.lb_api_key}' && "
                          f"cd /tmp_workspace && dsh --profile bench "
                          f"--patch {PATCH_CONTAINER_PATH} '{safe_prompt}'"),
                log_path=spec.output_dir / "agent.log",
            )
            try:
                agent_proc.wait(timeout=spec.timeout_seconds)
                elapsed_time = time.perf_counter() - start_time
            except subprocess.TimeoutExpired:
                logger.info("[%s] dsh timed out", spec.task_id)
                elapsed_time = float(spec.timeout_seconds)
                agent_proc.kill()
                agent_proc.wait()
            return AgentExecution(elapsed_time=elapsed_time, error=None,
                                  gateway_proc=None, agent_proc=agent_proc)
        except Exception as exc:
            logger.error("[%s] dsh execution error: %s", spec.task_id, exc)
            return AgentExecution(elapsed_time=float(spec.timeout_seconds),
                                  error=str(exc), gateway_proc=None,
                                  agent_proc=agent_proc)

    def prepare_grading_transcript(self, task_id: str) -> str:
        self._write_compat_transcript(task_id)
        return self.transcript_container_path

    def collect_usage(self, task_id: str, output_dir: Path,
                      elapsed_time: float) -> dict:
        transcript_host = output_dir / "chat.jsonl"
        output_dir.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(
            ["docker", "cp", f"{task_id}:{self.transcript_container_path}",
             str(transcript_host)], capture_output=True, text=True)
        if r.returncode == 0 and transcript_host.exists():
            usage = extract_usage_from_jsonl(transcript_host)
        else:
            usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0,
                     "cache_write_tokens": 0, "total_tokens": 0, "cost_usd": 0.0,
                     "request_count": 0}
        usage["elapsed_time"] = round(elapsed_time, 2)
        usage["self_hosted"] = True
        return usage

    def _probe_lb(self, task_id: str) -> None:
        auth = f"-H 'Authorization: Bearer {self.lb_api_key}' " if self.lb_api_key else ""
        cmd = (f"curl -sf -m 10 {auth}{self.lb_base_url}/models | grep -q qwen3.8-flash-next "
               f"|| curl -sf -m 10 {auth}{LB_FALLBACK_URL}/models | grep -q qwen3.8-flash-next")
        r = subprocess.run(["docker", "exec", task_id, "/bin/bash", "-c", cmd],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(
                f"LiteLLM LB not serving qwen3.8-flash-next from container "
                f"{task_id}: tried {self.lb_base_url}/models then {LB_FALLBACK_URL}/models "
                f"(spec risk R1): {r.stderr.strip()}")

    def _write_patch(self, task_id: str, model: str, rung: str) -> None:
        body = patch_entry_yaml(PROVIDER_ID, model, rung)
        r = subprocess.run(
            ["docker", "exec", "-i", task_id, "/bin/bash", "-c",
             f"cat > {PATCH_CONTAINER_PATH}"],
            input=body, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"patch write failed: {r.stderr}")
        logger.info("[%s] dsh patch written (rung=%s)", task_id, rung)

    def _write_compat_transcript(self, task_id: str) -> None:
        if not COMPAT_TRANSCRIPT_HOST_PATH.exists():
            logger.warning("[%s] compat script missing", task_id)
            return
        cp = subprocess.run(
            ["docker", "cp", str(COMPAT_TRANSCRIPT_HOST_PATH),
             f"{task_id}:/tmp/_dsh_compat_transcript.py"],
            capture_output=True, text=True)
        if cp.returncode != 0:
            logger.warning("[%s] compat cp failed: %s", task_id, cp.stderr)
            return
        ex = subprocess.run(
            ["docker", "exec", task_id, "python3", "/tmp/_dsh_compat_transcript.py"],
            capture_output=True, text=True)
        if ex.returncode != 0:
            logger.warning("[%s] compat run failed: %s", task_id, ex.stderr)
