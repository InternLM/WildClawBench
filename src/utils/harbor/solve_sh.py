"""Harbor `data/solution/solve.sh` generator.

Port of `_generate_harbor_solve_sh` from kensei2.py (line 3283).

Emits a bash script that reads each mock-service env var (defaulting to
`http://<svc>:<port>`) and prints a placeholder reminder. Real solution code
is intended to be filled in by humans referencing the golden trajectory.
"""
from __future__ import annotations

from typing import Mapping, Optional


def generate_harbor_solve_sh(env_vars: Optional[Mapping[str, str]] = None) -> str:
    env_vars = dict(env_vars or {})

    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "python3 - <<'PY'",
        "import os",
        "",
    ]

    if env_vars:
        for key in sorted(env_vars.keys()):
            default = env_vars[key]
            lvar = key.lower()
            lines.append(
                f"{lvar} = os.environ.get({key!r}, {default!r}).rstrip('/')"
            )
        lines.append("")

    lines.append(
        "print('Solution not yet implemented -- populate with API calls from "
        "golden trajectory.')"
    )
    lines.append("PY")

    return "\n".join(lines) + "\n"
