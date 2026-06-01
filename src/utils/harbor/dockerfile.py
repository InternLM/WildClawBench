"""Harbor environment Dockerfile generator.

Ports `_generate_harbor_dockerfile` from kensei2.py L3001.
"""

from __future__ import annotations

_AGENT_SKILL_DIRS = [
    "/root/.claude/skills",
    "/root/.codex/skills",
    "/root/.opencode/skills",
    "/root/.goose/skills",
    "/root/.factory/skills",
    "/root/.agents/skills",
    "/root/.gemini/skills",
    "/root/.cursor/skills",
]


def generate_harbor_dockerfile() -> str:
    lines = [
        "FROM ubuntu:24.04",
        "",
        "RUN apt-get update && \\",
        "    apt-get install -y --no-install-recommends \\",
        "        curl jq python3 python3-pip ca-certificates && \\",
        "    apt-get clean && rm -rf /var/lib/apt/lists/*",
        "",
        "WORKDIR /app",
        "",
    ]
    for d in _AGENT_SKILL_DIRS:
        lines.append("RUN mkdir -p %s" % d)
        lines.append("COPY skills %s" % d)
    lines.append("")
    return "\n".join(lines)
