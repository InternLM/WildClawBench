"""Build the fixed Python wrapper prefix prepended to LLM-generated tests.

Supplies the imports, <SERVICE>_URL constants from env vars, and the helper
functions (`api_get`, `api_post`, `_get`, `_post`, `read_file`, `file_exists`)
that the generated test bodies call. Generated code is stripped of any
duplicate imports/helpers by `sanitize.py`, then concatenated after this prefix.

Ported from kensei2/models/kensei2_sandbox.py (lines 1031-1098).
"""

from __future__ import annotations

from typing import Dict, Iterable, Optional


def build_wrapper_prefix(
    services: Dict[str, dict],
    scoped_apis: Optional[Iterable[str]] = None,
) -> str:
    """Return the wrapper boilerplate. services: {name: {env_var, port}}.

    When `scoped_apis` is provided, only emit `<SVC>_URL` constants for those
    names (required + distractors). With 101 discovered services this keeps the
    wrapper at ~5 lines instead of 101. Pass None to emit constants for every
    service in `services` (kensei2 default for small env trees).
    """
    lines = [
        '"""',
        "Auto-generated test suite for verifying API state changes and task completion.",
        '"""',
        "",
        "import json",
        "import os",
        "import subprocess",
        "import sqlite3",
        "from urllib.request import Request, urlopen",
        "",
        "try:",
        "    import pytest",
        "except ImportError:",
        "    pytest = None",
        "",
    ]
    scope = set(scoped_apis) if scoped_apis is not None else None
    for svc_name, info in services.items():
        if scope is not None and svc_name not in scope:
            continue
        const_name = svc_name.upper().replace("-", "_") + "_URL"
        lines.append(
            '%s = os.environ.get("%s", "http://localhost:%d")'
            % (const_name, info["env_var"], info["port"])
        )
    lines.extend(
        [
            "",
            "",
            "def _request(method, url, data=None):",
            "    body = None",
            '    headers = {"Accept": "application/json"}',
            "    if data is not None:",
            '        body = json.dumps(data).encode("utf-8")',
            '        headers["Content-Type"] = "application/json"',
            "    req = Request(url, data=body, method=method, headers=headers)",
            "    with urlopen(req, timeout=8) as resp:",
            '        return json.loads(resp.read().decode("utf-8"))',
            "",
            "",
            "def api_get(base_url, endpoint):",
            '    """Two-arg helper: api_get(BASE_URL, "/path")."""',
            '    return _request("GET", f"{base_url}{endpoint}")',
            "",
            "",
            "def api_post(base_url, endpoint, data=None):",
            '    """Two-arg helper: api_post(BASE_URL, "/path", {...})."""',
            '    return _request("POST", f"{base_url}{endpoint}", data=data)',
            "",
            "",
            "# Compatibility aliases — accept a full URL (one argument)",
            "def _get(url):",
            '    """One-arg helper: _get(f"{BASE_URL}/path")."""',
            '    return _request("GET", url)',
            "",
            "",
            "def _post(url, data=None):",
            '    """One-arg helper: _post(f"{BASE_URL}/path", {...})."""',
            '    return _request("POST", url, data=data)',
            "",
            "",
            "def read_file(path):",
            "    with open(path) as f:",
            "        return f.read()",
            "",
            "",
            "def file_exists(path):",
            "    return os.path.exists(path)",
            "",
            "",
        ]
    )
    return "\n".join(lines)
