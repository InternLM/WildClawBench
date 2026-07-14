"""
In-process tool registry for the WildClawBench sub-agent runtime.

Six built-in tools matching the openclaw default palette: ``Read``, ``Write``,
``Edit``, ``Grep``, ``Glob``, ``Bash``. Each runs in-process inside the agent
container, so the sub-agent script (``spawn_subagent.py``) needs nothing more
than a Python interpreter and a writable ``/tmp_workspace``.

Filesystem operations are whitelist-scoped to ``/tmp_workspace``, ``/root``,
and ``/tmp``; any path that resolves outside those roots is rejected with
``ERROR: permission denied``. ``Bash`` runs with ``cwd=/tmp_workspace`` and
a hard timeout cap of 120 seconds.

Two public entry points are used by ``subagent_director.py``:

    schemas_for(allowed_tools) -> list[dict]   # Anthropic ``tools`` array
    dispatch(name, tool_input) -> str          # invoke a single tool

Both are pure-Python; ``subagent_director``'s tool loop drives them.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping

# Filesystem ops are restricted to these prefixes. Resolving outside the
# whitelist raises PermissionError, which the dispatcher converts into a
# tool_result error string the model can read back.
_ALLOWED_PATH_PREFIXES = ("/tmp_workspace", "/root", "/tmp")

_BASH_TIMEOUT_DEFAULT = 30
_BASH_TIMEOUT_MAX = 120
_GREP_MAX_MATCHES = 200
_GLOB_MAX_RESULTS = 500
_BASH_STDOUT_TAIL = 8000
_BASH_STDERR_TAIL = 2000


def _check_path(p: str) -> Path:
    if not p:
        raise PermissionError("path is empty")
    path = Path(p).resolve()
    s = str(path)
    for prefix in _ALLOWED_PATH_PREFIXES:
        if s == prefix or s.startswith(prefix + "/"):
            return path
    raise PermissionError(
        f"path {p!r} resolves to {s!r}, outside allowed roots {_ALLOWED_PATH_PREFIXES}"
    )


def _read_tool(input_: Mapping[str, Any]) -> str:
    path = _check_path(str(input_.get("path", "")))
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except IsADirectoryError:
        return f"ERROR: {path} is a directory"
    except FileNotFoundError:
        return f"ERROR: {path} does not exist"
    except OSError as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"


def _write_tool(input_: Mapping[str, Any]) -> str:
    path = _check_path(str(input_.get("path", "")))
    content = str(input_.get("content", ""))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"wrote {len(content)} chars to {path}"
    except OSError as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"


def _edit_tool(input_: Mapping[str, Any]) -> str:
    path = _check_path(str(input_.get("path", "")))
    old = str(input_.get("old_string", ""))
    new = str(input_.get("new_string", ""))
    if not old:
        return "ERROR: old_string is required"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"ERROR: {path} does not exist"
    except OSError as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
    n = text.count(old)
    if n == 0:
        return "ERROR: old_string not found in file"
    if n > 1:
        return f"ERROR: old_string matches {n} times; provide more surrounding context"
    try:
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    except OSError as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
    return f"edited {path}"


def _grep_tool(input_: Mapping[str, Any]) -> str:
    pattern = str(input_.get("pattern", ""))
    if not pattern:
        return "ERROR: pattern is required"
    raw_path = str(input_.get("path", "/tmp_workspace"))
    root = _check_path(raw_path)
    try:
        rx = re.compile(pattern)
    except re.error as exc:
        return f"ERROR: bad regex: {exc}"

    matches: list[str] = []
    if root.is_file():
        targets: Iterable[Path] = (root,)
    elif root.is_dir():
        targets = (p for p in root.rglob("*") if p.is_file())
    else:
        return f"ERROR: {root} does not exist"
    for p in targets:
        try:
            for i, line in enumerate(
                p.read_text(encoding="utf-8", errors="replace").splitlines(), 1
            ):
                if rx.search(line):
                    matches.append(f"{p}:{i}:{line}")
                    if len(matches) >= _GREP_MAX_MATCHES:
                        return (
                            "\n".join(matches)
                            + f"\n[truncated at {_GREP_MAX_MATCHES} matches]"
                        )
        except OSError:
            continue
    return "\n".join(matches) if matches else "no matches"


def _glob_tool(input_: Mapping[str, Any]) -> str:
    pattern = str(input_.get("pattern", "**/*"))
    raw_path = str(input_.get("path", "/tmp_workspace"))
    root = _check_path(raw_path)
    if not root.exists():
        return f"ERROR: {root} does not exist"
    try:
        results = [str(p) for p in root.glob(pattern)][:_GLOB_MAX_RESULTS]
    except OSError as exc:
        return f"ERROR: {exc}"
    return "\n".join(results) if results else "no matches"


def _bash_tool(input_: Mapping[str, Any]) -> str:
    cmd = str(input_.get("command", ""))
    if not cmd.strip():
        return "ERROR: command is required"
    raw_timeout = input_.get("timeout", _BASH_TIMEOUT_DEFAULT)
    try:
        timeout = int(raw_timeout)
    except (TypeError, ValueError):
        timeout = _BASH_TIMEOUT_DEFAULT
    timeout = max(1, min(timeout, _BASH_TIMEOUT_MAX))
    cwd = "/tmp_workspace" if Path("/tmp_workspace").is_dir() else None
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: bash command timed out after {timeout}s"
    except OSError as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"
    out = (result.stdout or "")[-_BASH_STDOUT_TAIL:]
    err = (result.stderr or "")[-_BASH_STDERR_TAIL:]
    return f"[exit={result.returncode}]\nstdout:\n{out}\nstderr:\n{err}"


_HANDLERS = {
    "Read": _read_tool,
    "Write": _write_tool,
    "Edit": _edit_tool,
    "Grep": _grep_tool,
    "Glob": _glob_tool,
    "Bash": _bash_tool,
}


_SCHEMAS: dict[str, dict[str, Any]] = {
    "Read": {
        "name": "Read",
        "description": (
            "Read a UTF-8 text file from within /tmp_workspace, /root, or /tmp. "
            "Returns the file contents or an 'ERROR: ...' line."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path within the allowed roots.",
                },
            },
            "required": ["path"],
        },
    },
    "Write": {
        "name": "Write",
        "description": (
            "Write content to a file under /tmp_workspace, /root, or /tmp. "
            "Creates parent directories as needed. Overwrites any existing file."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    "Edit": {
        "name": "Edit",
        "description": (
            "Replace exactly one occurrence of old_string with new_string in the "
            "named file. Fails if old_string is missing or matches more than once."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string"},
                "new_string": {"type": "string"},
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
    "Grep": {
        "name": "Grep",
        "description": (
            "Recursive regex search across files under a path. Returns lines as "
            "'path:lineno:content'. Capped at 200 matches."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Python regular expression.",
                },
                "path": {
                    "type": "string",
                    "description": (
                        "Directory or single file to search. Defaults to "
                        "/tmp_workspace."
                    ),
                },
            },
            "required": ["pattern"],
        },
    },
    "Glob": {
        "name": "Glob",
        "description": (
            "Glob-pattern file listing under a path. Returns one path per line, "
            "capped at 500."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob like '**/*.py'.",
                },
                "path": {
                    "type": "string",
                    "description": "Root directory. Defaults to /tmp_workspace.",
                },
            },
            "required": ["pattern"],
        },
    },
    "Bash": {
        "name": "Bash",
        "description": (
            "Run a shell command in /tmp_workspace. Returns combined "
            "[exit=N]/stdout/stderr; stdout is tailed to 8000 chars, stderr to 2000."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "timeout": {
                    "type": "integer",
                    "description": "Seconds (1..120, default 30).",
                },
            },
            "required": ["command"],
        },
    },
}


def schemas_for(allowed_tools: Iterable[str]) -> list[dict[str, Any]]:
    """Return Anthropic tool schemas for the names in ``allowed_tools``.

    Unknown names are silently filtered out — the sub-agent's system prompt
    still mentions them, but they have no executable wiring so we omit the
    schema rather than fail the spawn.
    """
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for name in allowed_tools:
        if name in seen:
            continue
        seen.add(name)
        schema = _SCHEMAS.get(name)
        if schema is not None:
            out.append(schema)
    return out


def dispatch(name: str, tool_input: Mapping[str, Any]) -> str:
    """Invoke a single tool. Always returns a string; never raises."""
    handler = _HANDLERS.get(name)
    if handler is None:
        return f"ERROR: unknown tool {name!r}"
    try:
        result = handler(tool_input or {})
    except PermissionError as exc:
        return f"ERROR: permission denied: {exc}"
    except Exception as exc:  # noqa: BLE001 — never let one bad tool kill the loop
        return f"ERROR: {type(exc).__name__}: {exc}"
    return result if isinstance(result, str) else str(result)


def available_tools() -> tuple[str, ...]:
    return tuple(_HANDLERS.keys())
