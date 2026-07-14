"""Harbor environment Dockerfile generator.

Ports `_generate_harbor_dockerfile` from kensei2.py L3001.

Emits the client-mandated image recipe: base tooling plus the multimodal stack
(ffmpeg / poppler-utils / pymupdf / pillow) so PDF/image/video tasks have what
they need at build time. apt packages are intentionally left unpinned: Ubuntu's
archive keeps only the latest build of each package, so an exact pin
(`jq=1.7.1-3build1`) breaks the build the moment Ubuntu ships a security update
and purges the old version. `skills/`, `persona/` and `artifacts/inputs/files`
are COPYed only when the caller confirms those dirs are present in the build
context (`has_skills` / `has_persona` / `has_artifacts`) -- a `COPY` of a missing
path fails the build, so these stay conditional.
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


def generate_harbor_dockerfile(
    has_skills: bool = False,
    has_persona: bool = False,
    has_artifacts: bool = False,
) -> str:
    lines = [
        "FROM ubuntu:24.04",
        "",
        "RUN apt-get update && apt-get install -y --no-install-recommends \\",
        "    curl \\",
        "    jq \\",
        "    python3 \\",
        "    python3-pip \\",
        "    ffmpeg \\",
        "    poppler-utils \\",
        "    ca-certificates \\",
        "    && rm -rf /var/lib/apt/lists/*",
        "",
        "RUN pip install --no-cache-dir --break-system-packages pymupdf pillow",
        "",
    ]
    if has_skills:
        # COPY the skills tree once, then fan it out to the remaining agent
        # framework paths inside the image. COPYing the build context 8 times
        # would duplicate the whole tree across 8 layers; a single COPY + `cp`
        # keeps one copy in the context layer and lets the rest share inodes.
        first, *rest = _AGENT_SKILL_DIRS
        lines += ["# Copy skills to all agent framework paths", "COPY skills %s" % first]
        if rest:
            mkdirs = " ".join(rest)
            copies = " && ".join("cp -a %s/. %s/" % (first, d) for d in rest)
            lines.append("RUN mkdir -p %s && %s" % (mkdirs, copies))
        lines.append("")
    if has_persona:
        lines += ["# Copy persona", "COPY persona /root/.openclaw/persona", ""]
    if has_artifacts:
        lines += [
            "# Copy multimodal artifacts",
            "COPY artifacts/inputs/files /app/artifacts/inputs/files",
            "",
        ]
    lines += ["WORKDIR /app", ""]
    return "\n".join(lines)
