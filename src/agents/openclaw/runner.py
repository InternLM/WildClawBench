from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

from dotenv import load_dotenv

from src.agents.base import AgentExecution, AgentTaskSpec, BaseAgent
from src.utils.docker_utils import (
    configure_native_subagents,
    deny_native_subagents,
    inject_api_connectors,
    inject_data_into_workspace,
    inject_lobster_workspace,
    inject_openclaw_models,
    inject_persona_into_workspace,
    inject_subagent_tool,
    run_background,
    run_warmup,
    setup_skills,
    setup_workspace,
    snapshot_workspace_state,
    start_container,
    write_turn_marker,
)
from src.utils.grading import (
    extract_preflight_usage_from_litellm_log,
    extract_usage_from_jsonl,
    extract_usage_from_litellm_log,
)

try:
    # UI lifecycle rendering. Optional and side-effect free: emit_stage is a
    # no-op when no renderer is attached, so this never affects non-UI runs.
    from src.utils.ui import lifecycle as _ui_lifecycle
except Exception:  # pragma: no cover - defensive; keeps the backend importable
    class _NoLifecycle:
        STAGE_CREATE = STAGE_START = STAGE_EXEC = "STAGE"
        STAGE_STATUS = STAGE_DONE = STAGE_FAIL = "STAGE"

        @staticmethod
        def emit_stage(*a, **k):
            return None

    _ui_lifecycle = _NoLifecycle()  # type: ignore

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
        litellm_usage_log: str = "",
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
        self.litellm_usage_log = litellm_usage_log
        self._task_windows: dict[str, tuple[float, float]] = {}

    @property
    def expects_gateway(self) -> bool:
        return True

    @property
    def transcript_container_path(self) -> str:
        return "/root/.openclaw/agents/main/sessions/chat.jsonl"

    def prepare_grading_transcript(self, task_id: str) -> str:
        # Snapshot chat.jsonl from the agent container to host BEFORE grading so
        # the grader reads a frozen byte-stream the agent can no longer mutate.
        # Without this the agent (which runs as root in its container with rw
        # access to /root/.openclaw/agents/main/sessions/chat.jsonl) could
        # append fabricated assistant messages claiming the task is done
        # between agent_proc.wait() and grade_the_task. See b54 Issue 6.
        try:
            host_snap = Path(tempfile.gettempdir()) / f"chat-snap-{task_id}.jsonl"
            r = subprocess.run(
                ["docker", "cp", f"{task_id}:{self.transcript_container_path}", str(host_snap)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0 and host_snap.exists() and host_snap.stat().st_size > 0:
                return str(host_snap)
        except (subprocess.SubprocessError, OSError) as exc:
            logger.warning("[%s] chat.jsonl host snapshot failed: %s", task_id, exc)
        return self.transcript_container_path

    def _wait_for_llm_route_ready(
        self,
        task_id: str,
        *,
        attempts: int = 20,
        interval: float = 1.5,
        connect_timeout: float = 4.0,
    ) -> bool:
        # ROOT-CAUSE FIX for the intermittent "LLM request timed out." fast-fail
        # that killed trajectories on the FIRST request (and therefore dropped
        # all thinking/thinkingSignature blocks). openclaw's first LLM call goes
        # agent-container -> litellm sidecar -> cc-bridge -> api.anthropic.com. A
        # blind 2s gateway wait did NOT guarantee that in-network route was warm:
        # under concurrent reps the cold first connect got refused and openclaw
        # buckets ANY connect failure (ECONNREFUSED/ECONNRESET/ETIMEDOUT) as
        # reason=timeout, surfacing "LLM request timed out." with no retry that
        # helps. We must probe the route FROM THE AGENT'S OWN NETNS (not the
        # host, not the sidecar) so we exercise the exact path the first real
        # request uses, and only launch the agent once it answers.
        if not (self.litellm_config_yaml and self.litellm_container_name):
            return True
        base = f"http://{self.litellm_container_name}:{self.litellm_port}"
        # Any HTTP response (even 401/404) proves the TCP route to the sidecar is
        # up and forwarding; we only care that the connection is no longer cold.
        probe = (
            "import sys,urllib.request,urllib.error\n"
            f"u='{base}/health/liveliness'\n"
            f"try:\n"
            f"    urllib.request.urlopen(u, timeout={connect_timeout}); sys.exit(0)\n"
            "except urllib.error.HTTPError:\n"
            "    sys.exit(0)\n"
            "except Exception as e:\n"
            "    sys.stderr.write(str(e)); sys.exit(1)\n"
        )
        for i in range(1, attempts + 1):
            try:
                result = subprocess.run(
                    ["docker", "exec", task_id, "python3", "-c", probe],
                    capture_output=True,
                    text=True,
                    timeout=connect_timeout + 6.0,
                )
            except subprocess.TimeoutExpired:
                result = None
            except OSError as exc:
                logger.warning("[%s] LLM route probe exec failed (%s); "
                               "continuing", task_id, exc)
                return False
            if result is not None and result.returncode == 0:
                logger.info(
                    "[%s] LLM route warm after %d probe(s) (%s)",
                    task_id, i, base,
                )
                return True
            time.sleep(interval)
        logger.warning(
            "[%s] LLM route NOT confirmed warm after %d probes (%s); launching "
            "agent anyway (first request may fast-fail as 'timeout')",
            task_id, attempts, base,
        )
        return False

    def run_task(self, spec: AgentTaskSpec) -> AgentExecution:
        gateway_proc = None
        agent_proc = None
        elapsed_time = float(spec.timeout_seconds)

        try:
            exec_path = os.path.join(spec.workspace_path, "exec")
            tmp_path = os.path.join(spec.workspace_path, "tmp")
            os.makedirs(exec_path, exist_ok=True)

            # WCB_AUDIO_TRANSCRIBE_URL points the audio-extract skill at the
            # in-cluster LiteLLM sidecar's /v1/audio/transcriptions endpoint
            # (litellm_sidecar.py:142-170 registers whisper-1 there). The
            # agent container has no internet egress under the --internal
            # bridge, so this URL is the only working transcription path;
            # without it the agent silently drops audio inputs (see
            # ruth_flynn trajectory 925303a7-0a9d-40be-86b4-51da4d6e6544
            # turns 41-57 where every fallback - whisper CLI, pip install,
            # OPENAI_API_KEY env probe - failed in turn).
            extra_env_dict = dict(spec.task.get("env_dict") or {})
            if self.litellm_config_yaml and self.litellm_container_name:
                extra_env_dict.setdefault(
                    "WCB_AUDIO_TRANSCRIBE_URL",
                    f"http://{self.litellm_container_name}:{self.litellm_port}"
                    f"/v1/audio/transcriptions",
                )
                extra_env_dict.setdefault(
                    "WCB_AUDIO_TRANSCRIBE_AUTH",
                    self.litellm_master_key or "sk-litellm",
                )
                # openclaw's Anthropic-messages SDK client ignores the per-provider
                # baseUrl in openclaw.json for provider_key 'anthropic' and dials
                # api.anthropic.com directly, bypassing the litellm sidecar +
                # cc-bridge (the OAuth billing-attribution transform never runs and
                # the raw system[] trips the "extra usage" 400). ANTHROPIC_BASE_URL
                # is the SDK-honored override (same pattern as claudecode/runner.py
                # :370). No /v1 suffix: the client appends /v1/messages itself.
                if "claude" in (spec.model or "").lower():
                    base_url_root = (
                        f"http://{self.litellm_container_name}:{self.litellm_port}"
                    )
                    stub = self.litellm_master_key or "sk-litellm"
                    extra_env_dict.setdefault("ANTHROPIC_BASE_URL", base_url_root)
                    extra_env_dict.setdefault("ANTHROPIC_API_BASE", base_url_root)
                    extra_env_dict.setdefault("ANTHROPIC_AUTH_TOKEN", stub)
                    extra_env_dict.setdefault("ANTHROPIC_API_KEY", stub)

            # Sub-agent spawn runtime (src/utils/subagent_director.py) discovers
            # the LiteLLM sidecar from these container env vars. Only set on the
            # litellm path; OpenRouter runs don't expose a /v1/messages sidecar
            # to the child. Single-agent tasks leave the env untouched.
            if (spec.multi_agent_enabled and self.litellm_config_yaml
                    and self.litellm_container_name):
                base_url = f"http://{self.litellm_container_name}:{self.litellm_port}"
                extra_env_dict.setdefault("LITELLM_BASE_URL", base_url)
                extra_env_dict.setdefault(
                    "LITELLM_API_KEY", self.litellm_master_key or "sk-litellm")
                extra_env_dict.setdefault("WILDCLAW_MODEL", spec.model)

            _ui_lifecycle.emit_stage(spec.task_id, _ui_lifecycle.STAGE_CREATE,
                                     "openclaw agent container")
            start_container(
                spec.task_id,
                exec_path,
                extra_env=spec.task.get("env", ""),
                tmp_path=tmp_path,
                lobster_env=spec.lobster.get("env") if spec.lobster else None,
                extra_env_dict=extra_env_dict or None,
                network=self.litellm_network,
            )
            _ui_lifecycle.emit_stage(spec.task_id, _ui_lifecycle.STAGE_START,
                                     "container up, staging workspace")

            # Raise openclaw binary's bootstrap-file caps before the gateway
            # starts. Default is 20k chars/file + 150k total, which truncates
            # MEMORY.md and persona files for any non-trivial task.
            self._set_bootstrap_limits(spec.task_id)

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

            if persona_dir:
                inject_persona_into_workspace(spec.task_id, persona_dir)

            # Stage <task>/data/ input artifacts into the workspace at
            # /root/workspace/home (the task loader sets data_dir whenever the task
            # has a data/ dir). Without this the agent never sees the input
            # documents for multimodal/reconciliation tasks.
            data_dir = spec.task.get("data_dir") if isinstance(spec.task, dict) else ""
            if data_dir:
                inject_data_into_workspace(spec.task_id, data_dir)

            setup_skills(
                spec.task_id,
                spec.task.get("skills", ""),
                spec.task.get("skills_path", ""),
            )
            # Inject both required AND distractor connector skills so the
            # agent sees plausible-but-unneeded API surfaces alongside the
            # ones it actually needs. Without this, distractors only existed
            # in task.toml + testgen negative-weight tests, so the agent could
            # not realistically be tempted by them at runtime. The two lists
            # are deduplicated; if a distractor was already required (catalog
            # overlap edge case) the connector is only copied once.
            _required = spec.task.get("required_apis", []) or []
            _distractors = spec.task.get("distractor_apis", []) or []
            inject_api_connectors(
                spec.task_id,
                spec.task.get("env_dir", ""),
                list(dict.fromkeys(list(_required) + list(_distractors))),
            )

            run_warmup(spec.task_id, spec.task.get("warmup", ""))

            # Capture workspace state RIGHT BEFORE the agent runs so the
            # post-run diff (see collect_output_from_container) can isolate
            # agent-produced artifacts from the staged input set (data/,
            # persona/, openclaw scratch). Everything written or modified
            # under /tmp_workspace/ between this call and collect time is
            # by definition agent-generated. Codex+claudecode runners already
            # do this; without it openclaw runs land an empty artifacts/ dir.
            snapshot_workspace_state(spec.task_id)

            if spec.models_config:
                inject_openclaw_models(spec.task_id, spec.models_config)

            if spec.multi_agent_enabled:
                # Native mode (default): use OpenClaw's built-in sessions_spawn /
                # sessions_yield tools (children land as separate sessions in the
                # session store and are harvested into the golden parent/children
                # layout). spawnEnabled defaults true for the non-discord headless
                # `chat` channel, so no spawn-flag write is needed (and the config
                # validator rejects a direct session.threadBindings.spawnSubagentSessions
                # key anyway). Legacy mode injects the spawn_subagent.py skill.
                _ma_cfg = spec.multi_agent_config or {}
                if _ma_cfg.get("native", True):
                    configure_native_subagents(spec.task_id, _ma_cfg)
                else:
                    inject_subagent_tool(spec.task_id, _ma_cfg)

            self._set_model(spec.task_id, spec.model, thinking=spec.thinking)
            if not spec.multi_agent_enabled:
                # Explicit deny on top of the withheld alsoAllow grant, so a
                # --no-subagents run (or any single-agent task) can never spawn
                # even if image config drift ever grants the session tools.
                # MUST run after _set_model: its config script ASSIGNS
                # tools["deny"] and would clobber an earlier deny append.
                deny_native_subagents(spec.task_id)
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
            # Poll gateway.log until the gateway reports it is listening, rather
            # than sleeping a fixed 2s. The gateway can take up to ~30s to become
            # ready (memory index, bootstrap-limit tuning, config-triggered
            # restarts). A fixed 2s wait raced the agent's websocket connect: on
            # a slow start the agent connected before the gateway was up, the
            # socket dropped with a "1006 abnormal closure", and the agent fell
            # back to EMBEDDED mode — where it makes no real tool/API calls, so
            # the audit is empty and every rubric/test scores 0. Waiting for the
            # readiness marker removes the race regardless of gateway start time.
            gateway_log = spec.output_dir / "gateway.log"
            ready_timeout = float(os.environ.get("OPENCLAW_GATEWAY_READY_TIMEOUT", "60"))
            logger.info("[%s] Waiting for gateway to listen (up to %ds)...",
                        spec.task_id, int(ready_timeout))
            deadline = time.time() + ready_timeout
            gateway_ready = False
            # Iteration bound alongside the wall-clock deadline: terminates
            # even under a frozen/stubbed clock (unit tests no-op time.sleep).
            for _ in range(max(1, int(ready_timeout / 0.5))):
                if time.time() >= deadline:
                    break
                if gateway_proc.poll() is not None:
                    logger.error("[%s] Gateway process exited before listening "
                                 "(rc=%s) — see gateway.log", spec.task_id,
                                 gateway_proc.returncode)
                    break
                try:
                    if gateway_log.exists() and "listening on ws" in \
                            gateway_log.read_text(errors="ignore"):
                        gateway_ready = True
                        break
                except OSError:
                    pass
                time.sleep(0.5)
            if gateway_ready:
                # Small settle margin so the ws server is fully accepting conns.
                time.sleep(1)
                logger.info("[%s] Gateway is listening; launching agent",
                            spec.task_id)
            else:
                logger.warning("[%s] Gateway readiness marker not seen within "
                               "%ds; proceeding anyway (agent may fall back to "
                               "embedded mode)", spec.task_id, int(ready_timeout))
            # LLM route probe (OAuth/sidecar path): confirm the gateway can
            # actually complete a model round-trip before the first turn.
            self._wait_for_llm_route_ready(spec.task_id)

            # Multi-turn / staged injection: invoke the agent once per turn on
            # the SAME session ("chat") so context carries across turns. Turn 0
            # is the task prompt; each later turn is a follow-up message, and
            # before each later turn the agent is idle while before_turn(i)
            # applies that stage's silent mock-data injection. Single-turn runs
            # (spec.turns is None) execute exactly one iteration with spec.prompt,
            # behaviour-identical to the prior single-shot path.
            turn_messages: tuple[str, ...] = spec.turns or (spec.prompt,)
            start_time = time.perf_counter()
            wall_start = time.time()
            _ui_lifecycle.emit_stage(spec.task_id, _ui_lifecycle.STAGE_EXEC,
                                     f"agent running (timeout {spec.timeout_seconds}s)")
            agent_proc = None
            timed_out = False
            for turn_index, message in enumerate(turn_messages):
                if turn_index > 0 and spec.before_turn is not None:
                    # Agent is idle here -> apply this stage's injection.
                    try:
                        spec.before_turn(turn_index)
                    except Exception as exc:
                        logger.error("[%s] before_turn(%d) hook failed: %s",
                                     spec.task_id, turn_index, exc)
                if spec.multi_agent_enabled:
                    # Correlate sub-agent spawns landing in this turn to its index.
                    write_turn_marker(spec.task_id, turn_index)
                safe_msg = message.replace("'", "'\\''")
                if len(turn_messages) > 1:
                    logger.info("[%s] Agent turn %d/%d starting",
                                spec.task_id, turn_index + 1, len(turn_messages))
                    _ui_lifecycle.emit_stage(
                        spec.task_id, _ui_lifecycle.STAGE_STATUS,
                        f"agent turn {turn_index + 1}/{len(turn_messages)}")
                agent_proc = run_background(
                    spec.task_id,
                    bash_cmd=(
                        f"openclaw agent --session-id chat "
                        f"--timeout {spec.timeout_seconds} "
                        f"--message '{safe_msg}'"
                    ),
                    log_path=spec.output_dir / "agent.log",
                )
                logger.info("[%s] Waiting for agent to finish...", spec.task_id)
                try:
                    agent_proc.wait(timeout=spec.timeout_seconds)
                    logger.info("[%s] Agent turn %d finished", spec.task_id, turn_index + 1)
                except subprocess.TimeoutExpired:
                    logger.warning("[%s] Agent turn %d timed out", spec.task_id, turn_index + 1)
                    agent_proc.kill()
                    agent_proc.wait()
                    timed_out = True
                    break
            elapsed_time = time.perf_counter() - start_time
            if timed_out:
                # Timeout contract: elapsed reports the budget that was spent,
                # not the (possibly frozen/short) wall-clock measurement.
                elapsed_time = float(spec.timeout_seconds)
                _ui_lifecycle.emit_stage(spec.task_id, _ui_lifecycle.STAGE_STATUS,
                                         f"agent timed out after {spec.timeout_seconds}s",
                                         status="timed out")
            else:
                _ui_lifecycle.emit_stage(spec.task_id, _ui_lifecycle.STAGE_STATUS,
                                         f"agent finished in {elapsed_time:.1f}s")
            self._task_windows[spec.task_id] = (wall_start, time.time())
            logger.info("[%s] Agent finished (%.2fs, %d turn(s))",
                        spec.task_id, elapsed_time, len(turn_messages))

            # Native multi-agent: the parent turn returns as soon as it issues
            # its async sessions_spawn calls (mode=run), but the spawned child
            # sessions keep running in the still-alive gateway. Hold the
            # container open until those children quiesce, otherwise teardown
            # kills them mid-run and their trajectories are never written.
            if spec.multi_agent_enabled:
                self._wait_for_subagents(spec.task_id)
                # Repair the fan-out-then-stop failure: the parent occasionally
                # ends its turn right after spawning, believing it will be
                # "resumed on completion" (belief seen verbatim in GERALD
                # run_8's thinking). This single-turn harness has no such
                # resume, so the deliverables never get written and every
                # rubric/test collapses. Detect that exact stop and drive one
                # synthesis turn on the SAME session so the parent collects its
                # children and assembles the outputs. Already-synthesized runs
                # are left untouched. Disable via
                # OPENCLAW_SUBAGENT_SYNTH_RECOVERY=0.
                recovered = self._recover_synthesis_if_stalled(
                    spec, len(turn_messages))
                if recovered is not None:
                    agent_proc = recovered
                    # Extend the usage window + elapsed so the recovery turn's
                    # tokens and time are counted (window end was stamped
                    # above, before the recovery turn ran).
                    self._task_windows[spec.task_id] = (wall_start, time.time())
                    elapsed_time = time.perf_counter() - start_time

            logger.info("[%s] Agent exit code: %s", spec.task_id,
                        agent_proc.returncode if agent_proc else "n/a")
            return AgentExecution(
                elapsed_time=elapsed_time,
                error=None,
                gateway_proc=gateway_proc,
                agent_proc=agent_proc,
            )

        except Exception as exc:
            logger.error("[%s] Execution error: %s", spec.task_id, exc)
            _ui_lifecycle.emit_stage(spec.task_id, _ui_lifecycle.STAGE_FAIL, str(exc))
            return AgentExecution(
                elapsed_time=float(spec.timeout_seconds),
                error=str(exc),
                gateway_proc=gateway_proc,
                agent_proc=agent_proc,
            )

    def _wait_for_subagents(
        self,
        task_id: str,
        *,
        max_wait: float = 600.0,
        quiesce: float = 60.0,
        poll: float = 5.0,
    ) -> None:
        """Block until native sub-agent child sessions finish (or max_wait).

        Native ``sessions_spawn`` children run asynchronously in the gateway and
        write to ``/root/.openclaw/agents/main/sessions/<key>.jsonl``. The parent
        ``chat`` session is in the same dir, so >1 ``.jsonl`` means at least one
        child spawned. We poll the (size, mtime) signature of those files and
        return once it stops changing for ``quiesce`` seconds (children done) or
        ``max_wait`` elapses. No-op when only the parent session exists.

        quiesce=12s truncated live children: sessions append only at message
        boundaries, so a single long LLM turn or slow exec looks identical to
        "done". Measured over 25,226 inter-message gaps in bundled child
        trajectories (2026-07-06): p95=15.9s, p99=56s — 12s misread ~5% of
        gaps and killed lanes mid-turn (Midori run_3 H5, Gabriela_Scott run_5).
        60s covers ~99%; override via OPENCLAW_SUBAGENT_QUIESCE_SECONDS. The
        tail is fat (legit gaps up to 18min), so any timer is a heuristic —
        the authoritative check is the gateway's run registry, which this
        host cannot exercise (image is amd64-only) and is left as the known
        follow-up.
        """
        quiesce = float(os.environ.get("OPENCLAW_SUBAGENT_QUIESCE_SECONDS", quiesce))
        max_wait = float(os.environ.get("OPENCLAW_SUBAGENT_MAX_WAIT_SECONDS", max_wait))
        sessions_dir = "/root/.openclaw/agents/main/sessions"
        count_cmd = f"ls {sessions_dir}/*.jsonl 2>/dev/null | wc -l"
        try:
            n = int(subprocess.run(
                ["docker", "exec", task_id, "/bin/bash", "-c", count_cmd],
                capture_output=True, text=True,
            ).stdout.strip() or "0")
        except (ValueError, subprocess.SubprocessError):
            n = 0
        if n <= 1:
            return  # parent-only: nothing spawned
        logger.info(
            "[%s] %d session files present — waiting for sub-agents to finish "
            "(max %.0fs)", task_id, n, max_wait,
        )
        sig_cmd = (
            f"ls -la --time-style=+%s {sessions_dir}/*.jsonl 2>/dev/null "
            "| awk '{print $5, $6, $NF}'"
        )
        deadline = time.time() + max_wait
        last_sig: str | None = None
        stable_since: float | None = None
        while time.time() < deadline:
            sig = subprocess.run(
                ["docker", "exec", task_id, "/bin/bash", "-c", sig_cmd],
                capture_output=True, text=True,
            ).stdout.strip()
            if sig and sig == last_sig:
                if stable_since is None:
                    stable_since = time.time()
                elif time.time() - stable_since >= quiesce:
                    logger.info("[%s] sub-agent sessions quiesced", task_id)
                    return
            else:
                last_sig = sig
                stable_since = None
            time.sleep(poll)
        logger.warning(
            "[%s] sub-agent wait hit max_wait=%.0fs; collecting as-is",
            task_id, max_wait,
        )

    # Tool calls whose presence AFTER the last sessions_spawn prove the parent
    # went on to build deliverables (vs. ending its turn to "wait" for
    # children). These tools always write files.
    _WRITE_TOOL_NAMES = frozenset(
        {"write", "edit", "str_replace", "apply_patch"}
    )

    # ``exec`` is ambiguous — it is used both to INSPECT (cat/grep/pdftotext/
    # python-read) and to WRITE deliverables. Counting every post-spawn exec as
    # synthesis false-cleared a real stall (GERALD run_9: two inspection execs
    # after fan-out, zero deliverables, rubric 5.8%). So an exec only proves
    # synthesis when its command shows file-writing intent: a pandas/CSV/JSON
    # dump, a Python ``open(..., "w")``, a ``tee``, or a redirect into a
    # real deliverable file (``> report.md``) — excluding /dev, /tmp and fd
    # redirects, which are scratch, not output.
    _EXEC_WRITE_INTENT = re.compile(
        r"""(?xi)
        \.to_csv\( | \.to_json\( | \.to_excel\( | \.write_text\(
        | \.writelines\( | \.savefig\( | json\.dump\( | csv\.writer
        | open\([^)]*,\s*['"][wax] | writeFileSync | fs\.writeFile | \btee\b
        | >>?\s*['"]?(?!/dev/|/tmp/|/proc/|&)[\w./~ -]*\.(?:csv|tsv|json|jsonl
          |md|markdown|txt|eml|html|xml|ya?ml|pdf|png|jpe?g|svg|docx?|xlsx?)
        """
    )

    def _recover_synthesis_if_stalled(
        self, spec: AgentTaskSpec, turns_done: int,
    ) -> subprocess.Popen | None:
        """Drive one synthesis turn iff the parent fanned out but never
        synthesized.

        Returns the recovery agent process (so the caller can report its exit
        code / fold its usage), or ``None`` when no recovery was needed, the
        feature is disabled, or stall-detection failed. Enabled by default;
        disable with ``OPENCLAW_SUBAGENT_SYNTH_RECOVERY=0``.
        """
        flag = os.environ.get(
            "OPENCLAW_SUBAGENT_SYNTH_RECOVERY", "1"
        ).strip().lower()
        if flag in ("0", "false", "no", "off", ""):
            return None
        try:
            stalled = self._parent_stopped_after_spawn(spec.task_id)
        except (subprocess.SubprocessError, OSError, ValueError) as exc:
            logger.warning(
                "[%s] synthesis-stall detection failed (%s); skipping recovery "
                "turn", spec.task_id, exc,
            )
            return None
        if not stalled:
            return None
        logger.warning(
            "[%s] parent ended its turn after fan-out WITHOUT synthesizing "
            "(no deliverable write after the last sessions_spawn) — driving a recovery "
            "synthesis turn on the same session", spec.task_id,
        )
        message = (
            "Your sub-agents have finished and their results are now available. "
            "There is no automatic resume — you must finish the task in THIS "
            "turn. Enumerate the children with `sessions_list` and read each "
            "one's output with `sessions_history`, then produce ALL of the "
            "final deliverables the task asked for and write every deliverable "
            "file to the workspace. Do NOT spawn any more sub-agents and do NOT "
            "reply with only a status update. Hold the same red lines and "
            "two-source verification rules you were given."
        )
        # Tag any (unexpected) spawns from this turn to the next index so spawn
        # correlation stays consistent with the primary turns.
        write_turn_marker(spec.task_id, turns_done)
        safe_msg = message.replace("'", "'\\''")
        proc = run_background(
            spec.task_id,
            bash_cmd=(
                f"openclaw agent --session-id chat "
                f"--timeout {spec.timeout_seconds} "
                f"--message '{safe_msg}'"
            ),
            log_path=spec.output_dir / "agent_recovery.log",
        )
        logger.info("[%s] Waiting for recovery synthesis turn...", spec.task_id)
        try:
            proc.wait(timeout=spec.timeout_seconds)
            logger.info("[%s] Recovery synthesis turn finished", spec.task_id)
        except subprocess.TimeoutExpired:
            logger.warning("[%s] Recovery synthesis turn timed out", spec.task_id)
            proc.kill()
            proc.wait()
        # The recovery turn shouldn't fan out, but settle any stragglers.
        self._wait_for_subagents(spec.task_id)
        return proc

    def _parent_stopped_after_spawn(self, task_id: str) -> bool:
        """True iff a parent session fanned out (>=1 ``sessions_spawn``) yet
        issued no deliverable-producing tool call after its LAST spawn — the
        exact fingerprint of the "ended turn expecting a resume" failure.

        Reads the live session transcripts from the gateway container. The
        parent is the only session that calls ``sessions_spawn`` (children do
        not fan out further in these tasks), so the first session containing a
        spawn is the parent. Returns False when no fan-out is found or the
        parent clearly synthesized.
        """
        sessions_dir = "/root/.openclaw/agents/main/sessions"
        listing = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c",
             f"ls {sessions_dir}/*.jsonl 2>/dev/null"],
            capture_output=True, text=True,
        ).stdout.split()
        for path in listing:
            raw = subprocess.run(
                ["docker", "exec", task_id, "/bin/bash", "-c", f"cat '{path}'"],
                capture_output=True, text=True,
            ).stdout
            # (message_index, tool_name, exec_command_or_empty)
            tool_calls: list[tuple[int, str, str]] = []
            msg_index = 0
            for line in raw.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not (isinstance(entry, dict) and entry.get("type") == "message"):
                    continue
                inner = entry.get("message")
                content = inner.get("content") if isinstance(inner, dict) else None
                if isinstance(content, list):
                    for part in content:
                        if not (isinstance(part, dict)
                                and part.get("type") in ("toolCall", "tool_use")):
                            continue
                        name = str(part.get("name") or "")
                        cmd = ""
                        if name == "exec":
                            args = part.get("arguments") or part.get("input") or {}
                            if isinstance(args, dict):
                                cmd = str(args.get("command") or "")
                        tool_calls.append((msg_index, name, cmd))
                msg_index += 1
            spawn_positions = [i for i, n, _ in tool_calls if n == "sessions_spawn"]
            if not spawn_positions:
                continue  # not the parent (this session never fanned out)
            last_spawn = max(spawn_positions)
            synthesized = any(
                n in self._WRITE_TOOL_NAMES
                or (n == "exec" and self._EXEC_WRITE_INTENT.search(cmd))
                for i, n, cmd in tool_calls if i > last_spawn
            )
            return not synthesized
        return False

    def collect_usage(self, task_id: str, output_dir: Path, elapsed_time: float) -> dict:
        transcript_host = output_dir / "chat.jsonl"
        output_dir.mkdir(parents=True, exist_ok=True)
        r_cp = subprocess.run(
            ["docker", "cp", f"{task_id}:{self.transcript_container_path}", str(transcript_host)],
            capture_output=True,
            text=True,
        )

        usage: dict
        preflight_usage: dict | None = None
        if self.litellm_usage_log:
            window = self._task_windows.get(task_id)
            if window is None:
                window = (time.time() - max(elapsed_time, 1.0), time.time())
            usage = extract_usage_from_litellm_log(Path(self.litellm_usage_log), window[0], window[1])
            preflight_usage = extract_preflight_usage_from_litellm_log(Path(self.litellm_usage_log))
            if preflight_usage.get("request_count", 0) == 0:
                preflight_usage = None
        else:
            usage = {"request_count": 0}

        if usage.get("request_count", 0) == 0:
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

        # Fold sub-agent token totals from spawn_tree.jsonl into parent usage so
        # leaderboard cost math reflects the full call graph (not just the
        # parent's LiteLLM hits). Missing/malformed file is silently treated as
        # zero spawns — single-agent tasks remain byte-identical.
        spawn_tree = output_dir / "task_output" / "workspace_full" / "spawn_tree.jsonl"
        sub_in = sub_out = sub_count = 0
        sub_cost = 0.0
        if spawn_tree.is_file():
            for line in spawn_tree.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(row, dict):
                    continue
                sub_count += 1
                try:
                    sub_in += int(row.get("tokens_in") or 0)
                except (TypeError, ValueError):
                    pass
                try:
                    sub_out += int(row.get("tokens_out") or 0)
                except (TypeError, ValueError):
                    pass
                # Cost lives on BOTH per-spawn and "summary" rows; only sum the
                # per-spawn rows to avoid double-counting.
                if row.get("kind") != "summary":
                    try:
                        sub_cost += float(row.get("cost_usd") or 0.0)
                    except (TypeError, ValueError):
                        pass
        if sub_count:
            usage["subagent_count"] = sub_count
            usage["subagent_tokens_in"] = sub_in
            usage["subagent_tokens_out"] = sub_out
            usage["subagent_cost_usd"] = round(sub_cost, 6)
            usage["input_tokens"] = int(usage.get("input_tokens") or 0) + sub_in
            usage["output_tokens"] = int(usage.get("output_tokens") or 0) + sub_out
            usage["total_tokens"] = int(usage.get("total_tokens") or 0) + sub_in + sub_out
            usage["cost_usd"] = round(float(usage.get("cost_usd") or 0.0) + sub_cost, 6)

        self._task_windows.pop(task_id, None)
        usage["elapsed_time"] = round(elapsed_time, 2)
        if preflight_usage is not None:
            usage["__preflight__"] = preflight_usage
        return usage

    def _set_model(self, task_id: str, model: str, thinking: str | None = None) -> None:
        if self.litellm_config_yaml:
            model_id = model[len("litellm/"):] if model.startswith("litellm/") else model
            # Anthropic models use api="anthropic-messages" so openclaw posts via
            # the bundled Anthropic SDK to {baseUrl}/v1/messages and round-trips
            # thinking_blocks[].signature on every turn. The OpenAI Chat
            # Completions wire format has no field for signed thinking blocks
            # and silently drops them, so a single api="openai-completions"
            # provider for all models lost reasoning visibility after turn 0
            # (empirical: alden-croft claude/run_2 had 1/30 thinking_blocks
            # across all assistant turns despite --thinking xhigh). LiteLLM's
            # /v1/messages handler bridges Anthropic <-> Bedrock Converse and
            # preserves thinking_blocks bidirectionally
            # (litellm/litellm_core_utils/prompt_templates/factory.py:4798-4815).
            # gpt-5.5 stays on openai-completions because it has no native
            # thinking blocks to preserve (OpenAI reasoning is internal). The
            # baseUrl suffix differs by SDK: Anthropic SDK appends /v1/messages
            # to model.baseUrl; OpenAI SDK appends /chat/completions and
            # requires baseUrl to already end with /v1.
            is_anthropic_model = "claude" in model_id.lower()
            # openclaw 2026.3.11 gates extended thinking on a HARDCODED model
            # allowlist (config-mlcrIFGX.js): the registry tops out at
            # claude-opus-4-6 / claude-sonnet-4-6 (dash form). supportsXHighThinking
            # does an exact Set.has on `${provider}/${model}` and mapThinkingLevel
            # only emits a thinkingBudget for a recognized id. Our harness model id
            # "claude-opus-4.7" (dot, version 4.7) is NOT in that allowlist, so
            # openclaw never requests reasoning and the trajectory persists 0
            # thinking blocks (empirical: amanda_hayes_01 claude/run_2 had 0/23
            # despite --thinking xhigh). We present a RECOGNIZED id to openclaw so
            # thinking activates; the actual inference still hits the real opus ARN
            # via LiteLLM (litellm_sidecar.py routes both names to the same
            # bedrock/converse ARN). self.model_id stays "claude-opus-4.7" so the
            # output dir + usage threading are unaffected.
            openclaw_model_id = "claude-opus-4-6" if is_anthropic_model else model_id
            # openclaw 2026.3.11 gates thinking-capability on the PROVIDER KEY too,
            # not only the model id. supportsXHighThinking does an exact Set.has on
            # `${provider}/${model}` and XHIGH_MODEL_SET contains only `anthropic/...`
            # refs, and mapThinkingLevel only emits a thinkingBudget for recognized
            # provider+model pairs. Under the custom provider key "litellm" the agent
            # still produced 0 thinking blocks even with the recognized id
            # claude-opus-4-6 (empirical: amanda_hayes_01 claude/run_3 0/29). We
            # therefore register the sidecar provider under the key "anthropic" so
            # `anthropic/claude-opus-4-6` matches the allowlist and thinking
            # activates. Our providers["anthropic"] override carries baseUrl pointing
            # at the LiteLLM sidecar and api="anthropic-messages", so it shadows
            # openclaw's built-in anthropic provider (api.anthropic.com) and all
            # traffic still goes to the sidecar /v1/messages (verified via
            # ll_stream.log POST /v1/messages, never api.anthropic.com).
            provider_key = "anthropic" if is_anthropic_model else "litellm"
            primary = f"{provider_key}/{openclaw_model_id}"
            base_url_root = f"http://{self.litellm_container_name}:{self.litellm_port}"
            base_url_v1 = f"{base_url_root}/v1"
            if is_anthropic_model:
                litellm_provider = {
                    "baseUrl": base_url_root,
                    "apiKey": self.litellm_master_key or "sk-litellm",
                    "api": "anthropic-messages",
                    "models": [
                        {"id": openclaw_model_id, "name": openclaw_model_id,
                         "input": ["text", "image"], "reasoning": True,
                         "contextWindow": 200000, "maxTokens": 128000},
                    ],
                }
            else:
                # The provider's `models[].id` MUST equal openclaw_model_id (the
                # primary is litellm/<openclaw_model_id>); a hardcoded id only
                # worked while gpt-5.5 was the sole non-anthropic route. For any
                # other OpenAI-compatible sidecar model (e.g. the Meta vendor
                # model) a mismatched id would leave openclaw unable to resolve
                # the selected model.
                litellm_provider = {
                    "baseUrl": base_url_v1,
                    "apiKey": self.litellm_master_key or "sk-litellm",
                    "auth": "api-key",
                    "api": "openai-completions",
                    "models": [
                        {"id": openclaw_model_id, "name": openclaw_model_id,
                         "input": ["text", "image"], "reasoning": True,
                         "contextWindow": 1050000, "maxTokens": 128000},
                    ],
                }
            # Also register an `openai` provider that points at the SAME sidecar.
            # The built-in `image` (vision) tool resolves to provider "openai"
            # whenever the agent doesn't pin model=anthropic/... (or its internal
            # fallback chain kicks in). In litellm mode the agent container has no
            # openai key in auth-profiles.json AND cannot reach api.openai.com
            # (internal bridge), so openclaw fails locally with
            #   "image failed: No API key found for provider openai"
            # (kayla-morgan 2026-06-07 11:55:50) even though the sidecar already
            # aliases gpt-4o / gpt-4o-mini -> the Opus/gpt-5.5 route. Overriding
            # providers["openai"] -> sidecar makes those calls route through
            # LiteLLM (vision-capable) instead of dying on missing auth. The
            # agent never reaches real OpenAI; this is a pure sidecar rewrite.
            openai_sidecar_provider = {
                "baseUrl": base_url_v1,
                "apiKey": self.litellm_master_key or "sk-litellm",
                "auth": "api-key",
                "api": "openai-completions",
                "models": [
                    {"id": "gpt-4o", "name": "gpt-4o",
                     "input": ["text", "image"], "reasoning": False,
                     "contextWindow": 128000, "maxTokens": 16384},
                    {"id": "gpt-4o-mini", "name": "gpt-4o-mini",
                     "input": ["text", "image"], "reasoning": False,
                     "contextWindow": 128000, "maxTokens": 16384},
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
providers[{json.dumps(provider_key)}] = json.loads({json.dumps(json.dumps(litellm_provider))})
providers["openai"] = json.loads({json.dumps(json.dumps(openai_sidecar_provider))})
agents = d.setdefault("agents", {{}})
defaults = agents.setdefault("defaults", {{}})
defaults["model"] = {{"primary": {json.dumps(primary)}}}
defaults["imageModel"] = {{"primary": {json.dumps(primary)}}}
defaults.pop("models", None)
{set_thinking_line}d["browser"] = {{"enabled": False}}
# Defense-in-depth against headless-browser tools is handled via the
# schema-validated tools.deny list below. Earlier Fix 10 also wrote root
# keys d["chrome"], d["chromium"], d["playwright"], d["puppeteer"],
# d["selenium"], d["webdriver"] = {{"enabled": False}}; the openclaw config
# validator rejected all six on 2026-06-02 ('Unrecognized keys: "chrome",
# "chromium", "playwright", "puppeteer", "selenium", "webdriver"') and
# refused to load the config. tools.deny is the only legal layer for
# extra tool blocks. Image lacks every browser binary (verified
# 2026-06-02) and --internal network blocks egress, so the two remaining
# defense layers are sufficient.
tools = d.setdefault("tools", {{}})
tools["deny"] = [
    "browser", "duckduckgo",
    "chrome", "chromium", "playwright", "puppeteer",
    "selenium", "webdriver", "headless_browser",
    "browser_navigate", "browser_screenshot", "browser_eval",
]
# Exec runs in the openclaw gateway process inside this agent container
# (host='gateway'). The container itself is the sandbox (network-isolated
# via --internal bridge). Two other host values are wrong here:
#   * 'sandbox' spawns a nested Docker container per exec, requires the
#     docker CLI inside this container (wildclawbench-ubuntu:v1.3 has
#     none); seen 2026-06-02 06:43 'Sandbox mode requires Docker'.
#   * 'node' routes exec to a paired companion app over WebSocket, which
#     does not exist in headless benchmark runs; seen 2026-06-02 07:17
#     'exec host=node requires a paired node (none available)'.
exec_cfg = tools.setdefault("exec", {{}})
exec_cfg["host"] = "gateway"
# Bypass exec denial in headless benchmark runs. openclaw's config
# validator (seen 2026-06-02 megan-davis run) accepts exactly three
# values for tools.exec.security: "deny"|"allowlist"|"full". "full"
# disables the per-command human-approval check entirely; without it,
# every exec call waits 120s for an approval channel that does not
# exist in the harness, then fails with
#   'exec denied: host=gateway security=deny'
#   'Channel is required (no configured channels detected)'
# (~25x in 2026-06-02 07:43 gateway.log). tools.exec.approval is NOT
# a recognized key per the same validator; do not add it.
exec_cfg["security"] = "full"
# Silence the inline-eval approval prefilter -- but ONLY on openclaw
# versions that recognize the key. The prefilter fires in 2026.4.x as
# "obfuscation detected (gateway): Python/Perl/Ruby with base64 or
# encoded execution" -> exec.approval.waitDecision 119989ms ->
# INVALID_REQUEST: Channel is required, despite security=full above
# (openclaw issues #60054 / #59625). Two earlier attempts BROKE config
# load by writing keys the validator did not recognize, which disables
# the WHOLE config:
#   * obfuscationCheck (PR #60709) -- never merged upstream.
#   * strictInlineEval -- a REAL key, but only since 2026.3.31; the EC2
#     benchmark image ships 2026.3.11, whose validator rejected it as an
#     "Unrecognized key" (gateway.log 2026-06-13 darren_weston) -- same
#     failure class as the 2026-06-02 megan-davis Unrecognized-keys run.
# So we version-gate: read the installed openclaw version and only set
# strictInlineEval=false when >=2026.3.31 (e.g. local 2026.4.x). On older
# builds (2026.3.11) the prefilter does not exist and security="full"
# above already suffices, so skipping the key is both correct and safe.
# Unreadable/unparseable version -> skip (fail safe, keep config valid).
try:
    _ocv = json.loads(pathlib.Path("/usr/lib/node_modules/openclaw/package.json").read_text())["version"]
    if tuple(int(x) for x in _ocv.split(".")[:3]) >= (2026, 3, 31):
        exec_cfg["strictInlineEval"] = False
except Exception:
    pass
sandbox_cfg = defaults.setdefault("sandbox", {{}})
sandbox_cfg["mode"] = "off"
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
tools["deny"] = [
    "browser", "duckduckgo",
    "chrome", "chromium", "playwright", "puppeteer",
    "selenium", "webdriver", "headless_browser",
    "browser_navigate", "browser_screenshot", "browser_eval",
]
# Mirror the LiteLLM branch: see comments there for the full rationale,
# including why the chrome/chromium/etc. root-key writes were removed and
# why strictInlineEval is version-gated (it is unrecognized on the EC2
# image's openclaw 2026.3.11 and disables the whole config if written;
# only >=2026.3.31 accepts it). openclaw issues #60054/#59625.
exec_cfg = tools.setdefault("exec", {{}})
exec_cfg["host"] = "gateway"
exec_cfg["security"] = "full"
try:
    _ocv = json.loads(pathlib.Path("/usr/lib/node_modules/openclaw/package.json").read_text())["version"]
    if tuple(int(x) for x in _ocv.split(".")[:3]) >= (2026, 3, 31):
        exec_cfg["strictInlineEval"] = False
except Exception:
    pass
sandbox_cfg = defaults.setdefault("sandbox", {{}})
sandbox_cfg["mode"] = "off"
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
            logger.info("[%s] imageModel already set via _set_model (litellm mode)", task_id)
            return
        subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c",
             f"openclaw config set agents.defaults.imageModel.primary '{model}'"],
            capture_output=True,
            text=True,
        )
        logger.info("[%s] imageModel set: %s", task_id, model)

    def _set_bootstrap_limits(
        self,
        task_id: str,
        *,
        per_file_chars: int = 1_000_000_000,
        total_chars: int = 1_000_000_000,
    ) -> None:
        # Round-trip the set with a get-back-and-compare. Silent failure here
        # silently truncates MEMORY.md to 20k chars (binary default) and the
        # agent has no in-context signal it lost its tail. We MUST NOT let a
        # timeout/error propagate — gateway-start downstream is critical and
        # must run regardless of whether this verification succeeded.
        cmd = (
            f"openclaw config set agents.defaults.bootstrapMaxChars {per_file_chars} >/dev/null 2>&1 && "
            f"openclaw config set agents.defaults.bootstrapTotalMaxChars {total_chars} >/dev/null 2>&1 && "
            f"echo -n 'per='; openclaw config get agents.defaults.bootstrapMaxChars; "
            f"echo -n 'total='; openclaw config get agents.defaults.bootstrapTotalMaxChars"
        )
        # Best-effort: raising the bootstrap caps is an optimization (it prevents
        # MEMORY.md truncation), NOT a precondition for the run. A slow/hung
        # `openclaw config` call must never abort the task — under qemu x86
        # emulation the CLI can take far longer than a native invocation, so the
        # timeout is generous and any failure (timeout, non-zero rc) is swallowed.
        try:
            result = subprocess.run(
                ["docker", "exec", task_id, "/bin/bash", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=90,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                "[%s] Bootstrap-limit tuning timed out; continuing with binary "
                "defaults (MEMORY.md may be truncated at 20k chars)", task_id,
            )
            return
        except OSError as exc:
            logger.warning("[%s] Bootstrap-limit tuning failed to exec (%s); "
                           "continuing", task_id, exc)
            return

        applied_per = f"per={per_file_chars}" in result.stdout
        applied_total = f"total={total_chars}" in result.stdout
        if result.returncode == 0 and applied_per and applied_total:
            logger.info(
                "[%s] Bootstrap limits raised: per_file=%d total=%d (verified)",
                task_id,
                per_file_chars,
                total_chars,
            )
        else:
            logger.warning(
                "[%s] Failed to raise bootstrap limits (rc=%d): %s",
                task_id,
                result.returncode,
                (result.stderr or result.stdout)[:200],
            )

    def _index_memory(self, task_id: str) -> None:
        # openclaw's memory tool searches /root/memory/<YYYY-MM-DD>.md for
        # today's and yesterday's notes on every session bootstrap. Without
        # these files the agent surfaces ENOENT errors (see gateway.log:
        # 'read failed: ENOENT ... /root/memory/<date>.md') and the persona
        # bootstrap silently falls back to a generic LLM with the prompt
        # only. Seed both with MEMORY.md so the daily-memory layer resolves.
        # Bootstrap-file allowlist widened 2026-06-03 to all 7 files openclaw
        # reads on every turn (docs.openclaw.ai/concepts/agent-workspace):
        # AGENTS/AGENT (instructions), SOUL (personality), MEMORY (long-term),
        # IDENTITY (name/vibe), USER (user profile), TOOLS (tool notes),
        # HEARTBEAT (scheduled tasks). Files absent from the task's persona
        # dir are silently skipped — alden-croft ships all 7, renata-voss
        # ships only AGENTS/MEMORY/SOUL. See `inject_lobster_workspace`
        # (docker_utils.py:762) which already does the /root/ surface copy.
        # Bash emits MD:<name>:<state> tokens parsed by the harness. Token grammar
        # is load-bearing (Option A per user m1721 'option a'): each token represents
        # one verified post-copy state. States: present|missing|copy_failed|verified.
        # 'verified' is emitted only after `test -f /root/memory/<name>` succeeds,
        # closing the b89 'is it really there' gap that opaque success logs left open.
        cmd = (
            "mkdir -p /root/memory && "
            "for f in MEMORY.md SOUL.md AGENT.md AGENTS.md "
            "IDENTITY.md USER.md TOOLS.md HEARTBEAT.md; do "
            '  if [ -f "/root/$f" ]; then '
            '    if cp "/root/$f" /root/memory/ 2>/dev/null && [ -f "/root/memory/$f" ]; then '
            '      echo "MD:$f:verified"; '
            "    else "
            '      echo "MD:$f:copy_failed"; '
            "    fi; "
            "  else "
            '    echo "MD:$f:missing"; '
            "  fi; "
            "done; "
            "if [ -f /root/MEMORY.md ]; then "
            '  today=$(date -u +%Y-%m-%d); '
            '  yesterday=$(date -u -d "yesterday" +%Y-%m-%d 2>/dev/null || date -u -v-1d +%Y-%m-%d); '
            '  cp /root/MEMORY.md "/root/memory/${today}.md" && echo "MD:${today}.md:verified" || echo "MD:${today}.md:copy_failed"; '
            '  cp /root/MEMORY.md "/root/memory/${yesterday}.md" && echo "MD:${yesterday}.md:verified" || echo "MD:${yesterday}.md:copy_failed"; '
            "fi; "
            "echo '---INDEX---'; "
            "openclaw memory index --force 2>&1 | tail -3"
        )
        result = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", cmd],
            capture_output=True,
            text=True,
        )

        stdout = result.stdout or ""
        index_marker = "---INDEX---"
        md_section, _, index_section = stdout.partition(index_marker)

        verified: list[str] = []
        missing: list[str] = []
        failed: list[str] = []
        for line in md_section.splitlines():
            if not line.startswith("MD:"):
                continue
            _, _, rest = line.partition("MD:")
            name, _, state = rest.partition(":")
            if state == "verified":
                verified.append(name)
            elif state == "missing":
                missing.append(name)
            elif state == "copy_failed":
                failed.append(name)

        logger.info(
            "[%s] Bootstrap MDs indexed: verified=%s missing=%s",
            task_id,
            verified or "[]",
            missing or "[]",
        )
        if failed:
            logger.warning("[%s] Bootstrap MD copy failures: %s", task_id, failed)

        if result.returncode != 0:
            logger.warning("[%s] memory index failed (rc=%d): %s", task_id, result.returncode, (result.stderr or "")[:200])
        elif index_section.strip():
            logger.info("[%s] openclaw memory index: %s", task_id, index_section.strip()[:200])
