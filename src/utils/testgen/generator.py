"""Main test-generation orchestrator.

Ported from kensei2/models/kensei2_sandbox.py `_generate_task_tests_background`
(lines 933-1345). Odoo coupling (Registry, env.cr, task.write, ir.config_parameter,
bus notifications) removed; this is a synchronous pure function returning
`TestGenResult`. Callers persist via `src/utils/store.upsert_task`.

Flow per task:
  1. Discover services + API docs + mock-data snapshot from env_dir
  2. Infer required + distractor APIs via src/utils/skills_inference
  3. Build wrapper prefix
  4. Loop up to MAX_TESTGEN_ATTEMPTS:
       a. Assemble user message (prompt + services + docs + snapshot + prior lint failures)
       b. call_bedrock_converse() -> raw text
       c. strip fences + extract JSON {code, weights}
       d. sanitize_llm_test_code, auto_repair_truncated_python
       e. self_validate_tests -> lint failure list
       f. Track best draft; break early on zero failures
  5. Final repair pass; fall back to SAFE_FALLBACK_STUB if unparseable
  6. Return wrapper_prefix + best_code, weights JSON, usage, attempts, lint failures
"""

from __future__ import annotations

import ast
import json
import logging
import re
import time
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Optional

from ..config import Config
from ..skills_inference import compute_distractor_skills, infer_required_apis
from .bedrock import call_bedrock_converse
from .constants import (
    ALLOWED_WEIGHTS,
    FALLBACK_WEIGHTS,
    MAX_TESTGEN_ATTEMPTS,
    SAFE_FALLBACK_STUB,
)
from .lints import self_validate_tests
from .repair import auto_repair_truncated_python
from .sanitize import sanitize_llm_test_code
from .services import (
    collect_mock_data_snapshot,
    read_api_docs,
    read_service_routes,
    read_services,
)
from .wrapper import build_wrapper_prefix

_logger = logging.getLogger(__name__)


@dataclass
class TestGenResult:
    test_code: str                       # wrapper_prefix + best_code (or fallback)
    test_weights: dict = field(default_factory=dict)
    attempts: int = 0
    lint_failures: list = field(default_factory=list)
    usage: dict = field(default_factory=lambda: {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "total_tokens": 0,
        "request_count": 0,
    })
    duration_ms: float = 0.0
    used_fallback: bool = False
    error: str = ""

    @property
    def test_weights_json(self) -> str:
        return json.dumps(self.test_weights, indent=2, ensure_ascii=False)


def _load_prompt(name: str) -> str:
    from src.utils.prompt_loader import load_prompt
    return load_prompt(name)


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        try:
            first_nl = cleaned.index("\n")
            cleaned = cleaned[first_nl + 1:]
        except ValueError:
            pass
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return cleaned


def _extract_json_object(text: str) -> Optional[dict]:
    """Find the first {...} block and parse it as JSON. Returns None on failure."""
    cleaned = _strip_code_fences(text)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _clean_weights(raw_weights: object) -> dict:
    """Drop weight entries with non-allowed values or non-string keys."""
    if not isinstance(raw_weights, dict):
        return {}
    out = {}
    for name, w in raw_weights.items():
        if isinstance(name, str) and isinstance(w, int) and w in ALLOWED_WEIGHTS:
            out[name] = w
    return out


def _derive_task_output_format(rubrics: object) -> str:
    if not isinstance(rubrics, list):
        return "unknown"
    counts: dict[str, int] = {}
    for r in rubrics:
        if isinstance(r, dict):
            t = str(r.get("evaluation_target") or "").strip()
            if t:
                counts[t] = counts.get(t, 0) + 1
    if not counts:
        return "unknown"
    dominant = max(counts, key=lambda k: counts[k])
    # Only `workspace_artifact` and `file_output` evaluate against a file on
    # disk. `state_change` and `trajectory` evaluate against the tool-use
    # transcript (e.g. "did agent call this API?", "did agent NOT call this
    # forbidden endpoint?") and are satisfied by `TestBehavioral*`/`TestNegativeWeight*`
    # tests \u2014 not `file_exists()`. Misclassifying them as file targets would
    # silently steer the LLM into emitting useless file-existence assertions
    # for behavioral-audit criteria.
    file_targets = ("workspace_artifact", "file_output")
    has_file = any(k in counts for k in file_targets)
    has_text = "final_answer" in counts or "user_facing_message" in counts
    if dominant == "final_answer" and not has_file:
        return "final_answer"
    if dominant in file_targets and not has_text:
        return "workspace_artifact"
    return "mixed"


def _build_user_message(
    *,
    prompt: str,
    task_toml: str,
    services: dict,
    required_apis: list,
    distractor_apis: list,
    api_docs: str,
    data_snapshot: str,
    lint_failures: list,
    attempt: int,
    task_output_format: str = "unknown",
) -> str:
    parts = [
        "## Task Instruction (instruction.md)\n",
        "Generate tests that verify the agent performed these actions correctly.\n\n",
        prompt,
        "\n",
    ]
    if task_output_format == "final_answer":
        parts.append(
            "\n## TASK OUTPUT FORMAT — TEXT-ONLY (CRITICAL)\n"
            "This task's rubric evaluates the agent's FINAL CHAT MESSAGE, not files. "
            "The agent will NOT produce a deliverable file under /tmp_workspace/results/. "
            "DO NOT generate `TestOutcome*` classes that assert `file_exists(...)`, "
            "`read_file(...)` against `/root/out/*`, `/tmp_workspace/results/*`, or any "
            "report-file path. Every such test WILL fail trivially and waste positive weight. "
            "Instead, generate `TestBehavioral*` API-call audits "
            "(`api_get(.../audit/requests)`) to verify the agent USED the required APIs, "
            "and `TestNegativeWeight*` distractor-not-touched checks. The rubric judge "
            "scores the answer's CONTENT separately — your job is to prove the agent "
            "exercised the right tools.\n"
        )
    elif task_output_format == "workspace_artifact":
        parts.append(
            "\n## TASK OUTPUT FORMAT — FILE DELIVERABLES\n"
            "This task's rubric evaluates files the agent writes under "
            "`/tmp_workspace/results/` (or `/root/out/`). `TestOutcome*` classes "
            "asserting `file_exists(...)` and content checks against those paths "
            "are appropriate.\n"
        )
    elif task_output_format == "mixed":
        parts.append(
            "\n## TASK OUTPUT FORMAT — MIXED (text answer + file artifacts)\n"
            "The rubric evaluates BOTH the agent's final chat answer AND files it writes. "
            "Generate a balanced mix of `TestBehavioral*` API audits and "
            "`TestOutcome*` file-existence/content checks.\n"
        )
    if task_toml:
        parts.append("\n## task.toml (metadata)\n")
        parts.append("```toml\n%s\n```\n" % task_toml)

    parts.append("\n## Available Mock API Services\n")
    if services:
        for svc_name, info in services.items():
            const_name = svc_name.upper().replace("-", "_") + "_URL"
            tag = ""
            if svc_name in required_apis:
                tag = " **(REQUIRED — task uses this API)**"
            elif svc_name in distractor_apis:
                tag = " **(DISTRACTOR — agent should NOT touch this)**"
            parts.append(
                "- `%s` (env: `%s`, port %d) → use constant `%s`%s\n"
                % (svc_name, info["env_var"], info["port"], const_name, tag)
            )
    else:
        parts.append("No API services configured.\n")

    if required_apis:
        parts.append("\n## Required APIs (agent MUST use these)\n")
        for api_name in required_apis:
            parts.append("- `%s`\n" % api_name)

    if distractor_apis:
        parts.append("\n## Distractor APIs (agent must NOT touch — generate TestNegativeWeight* for each)\n")
        for api_name in distractor_apis:
            const_name = api_name.upper().replace("-", "_") + "_URL"
            parts.append("- `%s` → constant `%s`\n" % (api_name, const_name))

    if api_docs:
        parts.append("\n## Mock API Documentation (endpoints for verification)\n")
        parts.append(api_docs)

    if data_snapshot:
        parts.append("\n\n## Mock Data Snapshot (REAL entity IDs and field values)\n")
        parts.append(data_snapshot)

    if lint_failures:
        if attempt >= 2:
            lint_failures = [
                "THIS IS RETRY %d/%d. The previous draft had these issues. "
                "Read each lint message LITERALLY. Do NOT repeat the same mistakes."
                % (attempt, MAX_TESTGEN_ATTEMPTS),
                "",
            ] + lint_failures
        parts.append("\n\n## LINT FAILURES FROM PREVIOUS ATTEMPT (fix ALL of these)\n")
        for fail in lint_failures:
            parts.append("- %s\n" % fail)

    return "\n".join(parts)


def generate_task_tests(
    task: dict,
    cfg: Config,
    *,
    environment_dir: Optional[Path] = None,
    task_toml: str = "",
    max_attempts: int = MAX_TESTGEN_ATTEMPTS,
    max_tokens: int = 64000,
    temperature: Optional[float] = None,
    timeout: float = 300.0,
) -> TestGenResult:
    """Generate pytest code + per-test weights for a single task.

    Args:
        task: Normalized task dict (must have `task_id` and one of
            `batch_prompt` / `initial_prompt` / `prompt`).
        cfg: Config providing bedrock_inference_arn, bedrock_region, aws_bearer_token.
        environment_dir: Override for service discovery (defaults to cfg.environment_dir).
        task_toml: Optional harbor task.toml text to include in the prompt context.
        max_attempts: LLM retry budget before falling back to SAFE_FALLBACK_STUB.
        max_tokens / temperature / timeout: Bedrock Converse params.

    Returns:
        TestGenResult with `test_code` ready to write to a file. On total
        failure: `used_fallback=True`, `test_code` = wrapper + SAFE_FALLBACK_STUB.
    """
    gen_start = time.time()
    result = TestGenResult(test_code="")

    prompt = (
        task.get("batch_prompt")
        or task.get("initial_prompt")
        or task.get("prompt")
        or ""
    ).strip()
    if not prompt:
        result.error = "no prompt available for test generation"
        result.test_code = build_wrapper_prefix({}) + SAFE_FALLBACK_STUB
        result.test_weights = dict(FALLBACK_WEIGHTS)
        result.used_fallback = True
        return result

    env_dir = Path(environment_dir) if environment_dir else cfg.environment_dir
    services = read_services(env_dir)
    api_docs = read_api_docs(env_dir)
    has_api_services = bool(services)

    task_identifier = task.get("task_id") or task.get("id") or "wildclaw-task"

    # Required-API discovery priority (most-trusted first):
    #   1. task["required_apis"] — pre-computed by run_batch._augment_task_with_mocks
    #      from prompt keywords + task_dir/mock_data/<api>/ subdirs. This is the
    #      authoritative source for persona-format tasks whose prompt never
    #      mentions API names (e.g. danielle-lee, dana-ellison).
    #   2. infer_required_apis(prompt) — fallback for callers that bypass
    #      run_batch (standalone testgen scripts).
    #   3. mock_data/<api>/ subdir scan — last resort when task_dir is set but
    #      step 1 didn't pre-populate.
    # NEVER fall back to `sorted(services.keys())`: marking all 101 APIs as
    # required leaves compute_distractor_skills with an empty candidate pool
    # (distractors must NOT overlap required), so distractors=[] and the
    # TestNegativeWeight* class for every distractor in lints L7/L26 has
    # nothing to match.
    required_apis: list[str] = []
    pre_required = task.get("required_apis")
    if isinstance(pre_required, list) and pre_required:
        required_apis = sorted({a for a in pre_required if isinstance(a, str)})
    if not required_apis and prompt:
        required_apis = infer_required_apis(prompt, environment_dir=env_dir)
    if not required_apis:
        task_dir_str = task.get("task_dir") or ""
        if task_dir_str:
            mock_root = Path(task_dir_str) / "mock_data"
            if mock_root.is_dir():
                required_apis = sorted(
                    d.name for d in mock_root.iterdir()
                    if d.is_dir() and d.name in services
                )
    distractor_apis = (
        compute_distractor_skills(required_apis, task_identifier, environment_dir=env_dir)
        if required_apis else []
    )

    data_snapshot = collect_mock_data_snapshot(env_dir) if has_api_services else ""

    task_output_format = _derive_task_output_format(task.get("rubrics"))

    _logger.info(
        "[TESTGEN] task=%s required=%s distractors=%s services=%d output_format=%s",
        task_identifier, required_apis, distractor_apis, len(services), task_output_format,
    )

    scoped = sorted(set(required_apis) | set(distractor_apis))
    wrapper_prefix = build_wrapper_prefix(services, scoped_apis=scoped)

    # Served routes for scoped APIs, keyed by the <SVC>_URL wrapper constant —
    # feeds lint L27 (endpoint prefixes in tests must match real served paths).
    all_routes = read_service_routes(env_dir)
    service_routes = {
        name.upper().replace("-", "_") + "_URL": all_routes[name]
        for name in scoped if name in all_routes
    }

    try:
        system_prompt = _load_prompt("testgen_system")
    except (FileNotFoundError, OSError) as exc:
        result.error = "failed to load testgen_system prompt: %s" % exc
        result.test_code = wrapper_prefix + SAFE_FALLBACK_STUB
        result.test_weights = dict(FALLBACK_WEIGHTS)
        result.used_fallback = True
        return result

    best_code = ""
    best_weights: dict = {}
    best_failures: list = []
    lint_failures: list = []
    total_usage = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "total_tokens": 0,
        "request_count": 0,
        "cost_usd": 0.0,
    }
    attempts_done = 0

    # Live-stream heartbeat (docs/STREAMING_PLAN.md §3.4): status events only
    # — testgen output is cached generated code, not worth token streaming.
    # stream_events.emit() is a guaranteed no-raise no-op when WCB_STREAM is
    # off (the default).
    from src.utils import stream_events as _stream
    import uuid as _uuid
    _stream_id = _uuid.uuid4().hex[:12]

    for attempt in range(1, max_attempts + 1):
        attempts_done = attempt
        _stream.emit("testgen", "status", _stream_id, kind="status",
                     delta=f"attempt {attempt}/{max_attempts} started")
        user_message = _build_user_message(
            prompt=prompt,
            task_toml=task_toml,
            services=services,
            required_apis=required_apis,
            distractor_apis=distractor_apis,
            api_docs=api_docs,
            data_snapshot=data_snapshot,
            lint_failures=lint_failures,
            attempt=attempt,
            task_output_format=task_output_format,
        )

        try:
            response_text, usage = call_bedrock_converse(
                api_key=cfg.aws_bearer_token,
                inference_arn=cfg.bedrock_inference_arn,
                region=cfg.bedrock_region,
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )
        except Exception as exc:
            _logger.warning(
                "[TESTGEN] LLM call failed on attempt %d/%d (task=%s): %s",
                attempt, max_attempts, task_identifier, exc,
            )
            if best_code:
                break
            continue

        for _k in ("input_tokens", "output_tokens", "cache_read_tokens",
                   "cache_write_tokens", "total_tokens", "request_count"):
            total_usage[_k] += int(usage.get(_k, 0) or 0)
        total_usage["cost_usd"] += float(usage.get("cost_usd", 0.0) or 0.0)

        parsed = _extract_json_object(response_text)
        if parsed is None:
            _logger.warning(
                "[TESTGEN] No JSON in LLM response on attempt %d (task=%s)",
                attempt, task_identifier,
            )
            lint_failures = ["No JSON object found in LLM response — emit valid {code, weights} JSON"]
            continue

        llm_code = parsed.get("code", "")
        raw_weights = parsed.get("weights", {})

        if not llm_code or not isinstance(llm_code, str) or not llm_code.strip():
            lint_failures = ["LLM returned empty test code"]
            continue

        llm_code = sanitize_llm_test_code(llm_code)

        try:
            ast.parse(llm_code)
        except SyntaxError:
            repaired = auto_repair_truncated_python(llm_code)
            if repaired is not None:
                _logger.info(
                    "[TESTGEN] Auto-repaired truncated code on attempt %d (task=%s)",
                    attempt, task_identifier,
                )
                llm_code = repaired

        weights = _clean_weights(raw_weights)
        # Keep raw weights as a fallback so downstream callers see something
        # even when the LLM emits values outside the allowed set.
        if not weights and isinstance(raw_weights, dict):
            weights = {k: v for k, v in raw_weights.items() if isinstance(v, int)}

        failures = self_validate_tests(
            llm_code,
            weights,
            has_api_services=has_api_services,
            distractor_apis=distractor_apis,
            service_routes=service_routes,
        )

        if not best_code or len(failures) < len(best_failures):
            best_code = llm_code
            best_weights = weights
            best_failures = failures

        if not failures:
            _logger.info(
                "[TESTGEN] Passed all lints on attempt %d (task=%s)",
                attempt, task_identifier,
            )
            _stream.emit("testgen", "status", _stream_id, kind="status",
                         delta=f"attempt {attempt}: all lints passed")
            break

        _logger.info(
            "[TESTGEN] Attempt %d/%d failed %d lints (task=%s): %s",
            attempt, max_attempts, len(failures), task_identifier,
            "; ".join(failures[:3]),
        )
        _stream.emit("testgen", "status", _stream_id, kind="status",
                     delta=f"attempt {attempt}: {len(failures)} lint failure(s)")
        lint_failures = failures

    # Final auto-repair + fallback
    if best_code:
        try:
            ast.parse(best_code)
        except SyntaxError:
            repaired = auto_repair_truncated_python(best_code)
            if repaired is not None:
                _logger.warning("[TESTGEN] Final auto-repair applied (task=%s)", task_identifier)
                best_code = repaired
            else:
                _logger.error(
                    "[TESTGEN] Best draft unparseable after auto-repair (task=%s); using fallback",
                    task_identifier,
                )
                best_code = SAFE_FALLBACK_STUB
                best_weights = dict(FALLBACK_WEIGHTS)
                result.used_fallback = True
    else:
        _logger.error(
            "[TESTGEN] All attempts produced no usable code (task=%s); using fallback",
            task_identifier,
        )
        best_code = SAFE_FALLBACK_STUB
        best_weights = dict(FALLBACK_WEIGHTS)
        result.used_fallback = True

    result.test_code = wrapper_prefix + best_code
    result.test_weights = best_weights
    result.attempts = attempts_done
    result.lint_failures = best_failures
    result.usage = total_usage
    result.duration_ms = (time.time() - gen_start) * 1000
    _stream.emit(
        "testgen", "status", _stream_id, kind="status",
        delta=("done (fallback stub)" if result.used_fallback
               else f"done ({attempts_done} attempt(s))"),
    )

    _logger.info(
        "[TESTGEN] Done task=%s code=%dch weights=%d tokens_in=%d tokens_out=%d "
        "cache_r=%d cache_w=%d total=%d duration=%.0fms attempts=%d "
        "lint_failures=%d fallback=%s",
        task_identifier,
        len(result.test_code),
        len(result.test_weights),
        total_usage["input_tokens"],
        total_usage["output_tokens"],
        total_usage["cache_read_tokens"],
        total_usage["cache_write_tokens"],
        total_usage["total_tokens"],
        result.duration_ms,
        result.attempts,
        len(result.lint_failures),
        result.used_fallback,
    )
    return result
