from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any, Callable


@dataclass(frozen=True)
class AgentTaskSpec:
    task_id: str
    task: dict[str, Any]
    workspace_path: str
    prompt: str
    timeout_seconds: int
    output_dir: Path
    model: str
    thinking: str | None = None
    models_config: dict[str, Any] | None = None
    lobster: dict[str, Any] | None = None
    # Multi-turn / staged-injection support (ClawMark-style). When ``turns`` is
    # set, the agent is invoked once per turn on the SAME session (context is
    # retained). ``turns[0]`` is the initial task prompt; each later entry is a
    # follow-up message (a neutral "re-verify" nudge for silent injection).
    # Before running turn ``i`` (for i >= 1), the runner calls ``before_turn(i)``
    # while the agent is idle, which applies that stage's silent mock-data
    # injection. Only the openclaw backend honours these fields; other backends
    # run a single turn from ``prompt`` and ignore them.
    turns: tuple[str, ...] | None = None
    before_turn: Callable[[int], None] | None = None
    # Multi-agent (sub-agent spawning) support. When ``multi_agent_enabled`` is
    # set, the openclaw runner injects the spawn-subagent skill into the agent
    # container before the turn loop, so the agent can spawn bounded sub-agent
    # sessions. ``multi_agent_config`` carries the per-turn expectations and
    # allowed-tools config (see ``src/utils/spawn_tree_checks.py``). Only the
    # openclaw backend honours these fields; other backends ignore them.
    multi_agent_enabled: bool = False
    multi_agent_config: dict[str, Any] | None = None


@dataclass
class AgentExecution:
    elapsed_time: float
    error: str | None = None
    gateway_proc: subprocess.Popen[str] | None = None
    agent_proc: subprocess.Popen[str] | None = None


class BaseAgent(ABC):
    @property
    @abstractmethod
    def expects_gateway(self) -> bool:
        """Whether this backend starts a long-running gateway process."""

    @property
    @abstractmethod
    def transcript_container_path(self) -> str:
        """Path to chat transcript inside the runtime container."""

    def prepare_grading_transcript(self, task_id: str) -> str:
        """Prepare and return the transcript path used for grading."""
        _ = task_id
        return self.transcript_container_path

    @abstractmethod
    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        """Execute a task and return process handles, timing and error state."""

    @abstractmethod
    def collect_usage(self, task_id: str, output_dir: Path, elapsed_time: float) -> dict[str, Any]:
        """Collect token usage and cost for one task."""
