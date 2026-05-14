"""
Commander Agent — Multi-Agent Orchestration Harness for WildClawBench.

Runs Commander's full multi-agent pipeline on the HOST machine (Node.js),
accessing the task workspace via shared filesystem. Results are written
to the workspace for Docker-based grading.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.agents.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.utils.docker_utils import (
    run_warmup,
    setup_skills,
    TMP_WORKSPACE,
)

load_dotenv()
logger = logging.getLogger(__name__)

# Path to Commander's CLI script
COMMANDER_CLI = os.environ.get(
    "COMMANDER_CLI",
    os.path.expanduser("~/Documents/GitHub/Commander/cli.ts"),
)
COMMANDER_DIR = os.environ.get(
    "COMMANDER_DIR",
    os.path.expanduser("~/Documents/GitHub/Commander"),
)
TRANSCRIPT_PATH = "/tmp/commander_transcript.jsonl"


class CommanderAgent(BaseAgent):
    @property
    def expects_gateway(self) -> bool:
        return False

    @property
    def transcript_container_path(self) -> str:
        return TRANSCRIPT_PATH

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        elapsed_time = float(spec.timeout_seconds)

        try:
            # Start Docker container for workspace isolation
            exec_path = os.path.join(spec.workspace_path, "exec")
            tmp_path = os.path.join(spec.workspace_path, "tmp")
            os.makedirs(exec_path, exist_ok=True)

            self._start_container(
                spec.task_id,
                exec_path,
                extra_env=spec.task.get("env", ""),
                tmp_path=tmp_path,
            )
            setup_skills(
                spec.task_id,
                spec.task.get("skills", ""),
                spec.task.get("skills_path", ""),
            )
            run_warmup(spec.task_id, spec.task.get("warmup", ""))

            # Run Commander on the HOST, pointing at the task workspace
            start_time = time.perf_counter()

            # Build the prompt: task description + output instruction
            prompt = spec.prompt
            if not prompt.endswith("."):
                prompt += "."
            prompt += (
                "\n\nSave all output files to /tmp_workspace/results/ "
                "or the working directory. Make sure any files you create "
                "are saved to disk."
            )

            # Run Commander CLI with the task prompt
            env = os.environ.copy()
            env["COMMANDER_TOOLS"] = "web_search,web_fetch,file_read,file_write,file_edit,file_search,file_list,python_execute,shell_execute,git"

            # Also pass the workspace path so Commander knows where to work
            task_workspace_host = os.path.join(spec.workspace_path, "exec")
            env["COMMANDER_WORKSPACE"] = task_workspace_host

            tsx_path = os.path.expanduser(
                "~/.npm/_npx/fd45a72a545557e9/node_modules/.bin/tsx"
            )
            if not os.path.exists(tsx_path):
                tsx_path = "npx tsx"

            cmd = [
                tsx_path,
                COMMANDER_CLI,
                "run",
                prompt,
            ]

            logger.info(
                "[%s] Running Commander (timeout=%ss)...",
                spec.task_id,
                spec.timeout_seconds,
            )

            result = subprocess.run(
                cmd,
                cwd=COMMANDER_DIR,
                env=env,
                capture_output=True,
                text=True,
                timeout=spec.timeout_seconds,
            )

            elapsed_time = time.perf_counter() - start_time
            logger.info(
                "[%s] Commander finished in %.2fs (rc=%d)",
                spec.task_id,
                elapsed_time,
                result.returncode,
            )

            # Save transcript/agent log
            output_dir = spec.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            agent_log = output_dir / "agent.log"
            agent_log.write_text(
                f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}",
                encoding="utf-8",
            )

            # Save a minimal compat transcript for grading
            transcript = output_dir / "chat.jsonl"
            transcript.write_text(
                json.dumps({
                    "role": "assistant",
                    "content": result.stdout[-2000:] if result.stdout else "",
                    "usage": {
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                    },
                }) + "\n",
                encoding="utf-8",
            )

            return AgentExecution(
                elapsed_time=elapsed_time,
                error=None,
                gateway_proc=None,
                agent_proc=None,
            )

        except subprocess.TimeoutExpired:
            logger.info("[%s] Commander timed out after %ss", spec.task_id, spec.timeout_seconds)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error="timeout",
                gateway_proc=None,
                agent_proc=None,
            )
        except Exception as exc:
            logger.error("[%s] Commander execution error: %s", spec.task_id, exc)
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error=str(exc),
                gateway_proc=None,
                agent_proc=None,
            )

    def collect_usage(self, task_id: str, output_dir: Path, elapsed_time: float) -> dict[str, Any]:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "request_count": 0,
            "elapsed_time": round(elapsed_time, 2),
        }

    def _start_container(
        self,
        task_id: str,
        workspace_path: str,
        extra_env: str = "",
        tmp_path: str = "",
    ) -> None:
        """Start a minimal Docker container for workspace isolation."""
        cmd = [
            "docker", "run", "-d",
            "--name", task_id,
            "-v", f"{workspace_path}:/app:ro",
            "python:3.12-slim",
            "/bin/bash", "-c", "tail -f /dev/null",
        ]
        logger.info("[%s] Starting container", task_id)
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Container startup failed:\n{r.stderr}")
        logger.info("[%s] Container ID: %s", task_id, r.stdout.strip()[:12])

        if tmp_path and os.path.exists(tmp_path):
            subprocess.run(
                ["docker", "exec", task_id, "mkdir", "-p", "/tmp_workspace/tmp"],
                capture_output=True,
            )
            subprocess.run(
                ["docker", "cp", f"{tmp_path}/.", f"{task_id}:/tmp_workspace/tmp/"],
                capture_output=True,
            )

        # Create results dir
        subprocess.run(
            ["docker", "exec", task_id, "mkdir", "-p", f"{TMP_WORKSPACE}/results"],
            capture_output=True,
        )
