"""Intent-based (lighter-weight) test generation variant.

Ported from kensei2/models/kensei2_sandbox.py `_generate_intent_tests_background`
(line 897) + `_load_intent_test_system_prompt` (7079) + `_build_intent_test_user_message`
(7103).

Differences from the main `generator.generate_task_tests`:
  - No weights, no lint loop, single Bedrock call
  - Smaller prompt; uses `intent_test_generation_prompt.md`
  - Output is raw pytest code (not JSON-wrapped); markdown fences stripped
  - Intended to run in parallel with pod deployment so tests are ready by the
    time the agent finishes — for non-API tasks or as a cheap first pass
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Optional

from ..config import Config
from .bedrock import call_bedrock_converse
from .services import read_api_docs, read_services

_logger = logging.getLogger(__name__)

_DEFAULT_INTENT_PROMPT = (
    "You are a test engineer. Given a task instruction describing what an AI agent "
    "should do with mock APIs, generate pytest test cases that verify the expected "
    "state changes by querying the mock API GET endpoints.\n\n"
    "Rules:\n"
    "- Use only the `urllib.request` module (stdlib) for HTTP calls — do NOT use `requests`\n"
    "- Base URLs come from environment variables (e.g., os.environ['AMAZON_SELLER_API_URL'])\n"
    "- Test assertions verify the data state matches what the task instruction requires\n"
    "- Generate one test function per expected operation or logical group\n"
    "- Use descriptive test names: test_<service>_<operation>_<entity>\n"
    "- Include docstrings explaining what operation this verifies\n"
    "- Output ONLY valid Python code (no markdown fences, no explanations)\n"
    "- Import only: os, json, urllib.request, urllib.parse, pytest\n"
)


@dataclass
class IntentResult:
    test_code: str = ""
    usage: dict = field(default_factory=lambda: {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "total_tokens": 0,
        "request_count": 0,
    })
    error: str = ""


def _load_intent_system_prompt() -> str:
    try:
        return resources.files("src.utils.testgen.prompts").joinpath(
            "intent_test_generation_prompt.md"
        ).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return _DEFAULT_INTENT_PROMPT


def _extract_python_code(text: str) -> str:
    """Strip markdown fences if present; else return as-is."""
    pattern = r"```(?:python)?\s*\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def generate_intent_tests(
    task: dict,
    cfg: Config,
    *,
    environment_dir: Optional[Path] = None,
    task_toml: str = "",
    max_tokens: int = 12000,
    temperature: Optional[float] = None,
    timeout: float = 120.0,
) -> IntentResult:
    """One-shot intent-based pytest generator (no weights, no lint loop)."""
    result = IntentResult()
    prompt = (
        task.get("batch_prompt")
        or task.get("initial_prompt")
        or task.get("prompt")
        or ""
    ).strip()
    if not prompt:
        result.error = "no prompt available for intent test generation"
        return result

    env_dir = Path(environment_dir) if environment_dir else cfg.environment_dir
    services = read_services(env_dir)
    api_docs = read_api_docs(env_dir)

    parts = [
        "## Task Instruction (instruction.md)\n",
        "This is the prompt that will be sent to the AI agent. "
        "Generate tests that verify the agent performed these actions correctly.\n\n",
        prompt[:8000] if len(prompt) > 8000 else prompt,
        "\n",
    ]
    if task_toml:
        parts.append("\n## task.toml (distractor_skills and metadata)\n")
        parts.append("```toml\n%s\n```\n" % task_toml)

    parts.append("\n## Environment Variables for API Base URLs\n")
    parts.append("Use `os.environ.get('<ENV_VAR>', '<default>')` to get the full base URL.\n\n")
    for svc_name, info in services.items():
        parts.append(
            "- `%s` → service: %s (port %d, value will be like `http://localhost:%d`)\n"
            % (info["env_var"], svc_name, info["port"], info["port"])
        )

    if api_docs:
        parts.append("\n## Mock API Documentation (endpoints for verification)\n")
        parts.append(api_docs)

    user_message = "\n".join(parts)
    system_prompt = _load_intent_system_prompt()

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
        _logger.warning("[INTENT-TESTGEN] LLM call failed: %s", exc)
        result.error = str(exc)
        return result

    result.usage = usage
    result.test_code = _extract_python_code(response_text)
    return result
