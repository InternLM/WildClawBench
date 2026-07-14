"""Harbor v1.1 `task.toml` builder.

Ports `_build_harbor_task_toml` from kensei2.py L2870. The strict section
order is documented at the top of the bundle spec and must not change.
"""

from __future__ import annotations

from typing import Iterable, List, Mapping, Optional

from src.utils.store import Task


def _q(value: object) -> str:
    """Quote a TOML string value with double quotes, escaping as required."""
    s = "" if value is None else str(value)
    s = s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ")
    return "\"%s\"" % s


def _arr_strs(values: Iterable[str]) -> str:
    return "[" + ", ".join(_q(v) for v in values) + "]"


def _arr_authors(authors: Iterable[Mapping]) -> str:
    if not authors:
        return "[]"
    items = []
    for a in authors:
        name = a.get("name", "") if isinstance(a, Mapping) else str(a)
        items.append("{ name = %s }" % _q(name))
    return "[" + ", ".join(items) + "]"


def _truncate_for_description(text: str, limit: int | None = None) -> str:
    s = (text or "").strip().replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    if limit is not None and len(s) > limit:
        s = s[: limit - 1] + "\u2026"
    return s


_DEFAULTS = {
    "verifier_timeout_sec": 600.0,
    "agent_timeout_sec": 900.0,
    "env_build_timeout_sec": 600.0,
    "env_cpus": 1,
    "env_memory_mb": 4096,
    "env_storage_mb": 10240,
    "env_allow_internet": True,
    "env_skills_dir": "skills",
    "healthcheck_command": "curl -f http://localhost:8000/health",
    "healthcheck_interval_sec": 5.0,
    "healthcheck_timeout_sec": 30.0,
    "healthcheck_retries": 3,
    "pass_at_k": 8,
}

_DEFAULT_DIMENSIONS = {
    "complex": "medium",
    "long_horizon": "false",
    "objective": "true",
    "multimodal": "true",
    "cross_modal_cross_api": "false",
    "asset_complexity": "low",
}


def build_task_toml(
    task: Task,
    required_skills: Iterable[str],
    distractor_skills: Iterable[str],
    env_vars: Optional[Mapping[str, str]] = None,
    dependency_tags: Optional[Iterable[str]] = None,
    dimensions: Optional[Mapping[str, str]] = None,
    authors: Optional[Iterable[Mapping]] = None,
    verifier_env: Optional[Mapping[str, str]] = None,
    solution_env: Optional[Mapping[str, str]] = None,
    safety_critical: str = "",
    trajectory_modifier: str = "",
    pass_at_k: Optional[int] = None,
    healthcheck_command: Optional[str] = None,
) -> str:
    """Emit a Harbor v1.1 task.toml string. Section order is strict."""
    env_vars = env_vars or {}
    verifier_env = verifier_env or {}
    solution_env = solution_env or {}
    dims = {**_DEFAULT_DIMENSIONS, **(dependency_tags and {} or {}), **(dimensions or {})}
    name = task.task_id or task.id or "kensei2-task"
    description = _truncate_for_description(task.initial_prompt or "")
    keywords: List[str] = []
    if task.task_type:
        keywords.append(task.task_type)
    if task.difficulty:
        keywords.append(task.difficulty)

    lines: List[str] = []
    lines.append("schema_version = \"1.1\"")
    lines.append("")
    lines.append("[task]")
    lines.append("name = %s" % _q(name))
    lines.append("task_id = %s" % _q(name))
    lines.append("description = %s" % _q(description))
    lines.append("authors = %s" % _arr_authors(authors or []))
    lines.append("keywords = %s" % _arr_strs(keywords))
    lines.append("")

    lines.append("[metadata]")
    lines.append("category = %s" % _q(task.task_type or ""))
    lines.append("difficulty = %s" % _q(task.difficulty or ""))
    if trajectory_modifier:
        lines.append("trajectory_modifier = %s" % _q(trajectory_modifier))
    if safety_critical and safety_critical != "N/A":
        lines.append("safety_critical = %s" % _q(safety_critical))
    lines.append("required_skills = %s" % _arr_strs(required_skills))
    lines.append("distractor_skills = %s" % _arr_strs(distractor_skills))
    lines.append("")

    lines.append("[verifier]")
    lines.append("timeout_sec = %s" % _DEFAULTS["verifier_timeout_sec"])
    lines.append("")
    lines.append("[verifier.env]")
    for k, v in verifier_env.items():
        lines.append("%s = %s" % (k, _q(v)))
    lines.append("")

    lines.append("[agent]")
    lines.append("timeout_sec = %s" % _DEFAULTS["agent_timeout_sec"])
    lines.append("")

    lines.append("[environment]")
    lines.append("build_timeout_sec = %s" % _DEFAULTS["env_build_timeout_sec"])
    lines.append("cpus = %d" % _DEFAULTS["env_cpus"])
    lines.append("memory_mb = %d" % _DEFAULTS["env_memory_mb"])
    lines.append("storage_mb = %d" % _DEFAULTS["env_storage_mb"])
    lines.append("allow_internet = %s" % ("true" if _DEFAULTS["env_allow_internet"] else "false"))
    lines.append("skills_dir = %s" % _q(_DEFAULTS["env_skills_dir"]))
    lines.append("")

    lines.append("[environment.env]")
    for k, v in env_vars.items():
        lines.append("%s = %s" % (k, _q(v)))
    lines.append("")

    lines.append("[environment.healthcheck]")
    lines.append("command = %s" % _q(healthcheck_command or _DEFAULTS["healthcheck_command"]))
    lines.append("interval_sec = %s" % _DEFAULTS["healthcheck_interval_sec"])
    lines.append("timeout_sec = %s" % _DEFAULTS["healthcheck_timeout_sec"])
    lines.append("retries = %d" % _DEFAULTS["healthcheck_retries"])
    lines.append("")

    lines.append("[solution.env]")
    for k, v in solution_env.items():
        lines.append("%s = %s" % (k, _q(v)))
    lines.append("")

    lines.append("[multimodal]")
    lines.append("dependency_tags = %s" % _arr_strs(dependency_tags or []))
    lines.append("")

    lines.append("[evaluation]")
    lines.append("pass_at_k = %d" % int(pass_at_k or _DEFAULTS["pass_at_k"]))
    lines.append("")

    lines.append("[dimensions]")
    for k in (
        "complex", "long_horizon", "objective",
        "multimodal", "cross_modal_cross_api", "asset_complexity",
    ):
        lines.append("%s = %s" % (k, _q(dims.get(k, _DEFAULT_DIMENSIONS[k]))))
    lines.append("")

    return "\n".join(lines)
