from __future__ import annotations

import json
import logging
import os
import shlex
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DOCKER_IMAGE  = os.environ.get("DOCKER_IMAGE",   "wildclawbench-ubuntu:v1.3")
TMP_WORKSPACE = os.environ.get("TMP_WORKSPACE",  "/tmp_workspace")
WORKSPACE_BASELINE_PATH = "/tmp/wildclaw_workspace_baseline.json"

BRAVE_API_KEY = os.environ.get("BRAVE_API_KEY", "")


# ---------------------------------------------------------------------------
# S-001 argv-injection guards.
#
# Every docker-run argv in this module + src/agents/*/runner.py +
# src/utils/litellm_sidecar.py + src/utils/test_executor.py builds env-var
# entries as flat ['-e', 'KEY=VALUE', ...] tokens. Because subprocess.run
# is called with a list (not shell=True), the shell-metacharacter class of
# command-injection does not apply, but **argv-flag injection does**: a
# VALUE that begins with '-' becomes a new docker flag (e.g. '--privileged'
# smuggled via the '-e KEY=...' position), and a KEY containing whitespace
# / NUL / newline can split one '-e' pair into two argv tokens. Bare
# tokens like `image`, `network`, and `container_name` have the same
# flag-injection risk at their own argv positions.
#
# These helpers fail closed on the patterns that enable injection. They
# are deliberately strict (POSIX env-var-name regex, no leading '-',
# no embedded control bytes, no embedded whitespace for bare tokens) so
# that a malicious value cannot dress itself up as a docker flag.
# ---------------------------------------------------------------------------

import re as _re

_ENV_KEY_RE = _re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_FORBIDDEN_VALUE_CHARS = ("\n", "\r", "\x00")
_FORBIDDEN_TOKEN_CHARS = ("\n", "\r", "\x00", " ", "\t")


def _validate_env_arg(key: str, value: str) -> tuple[str, str]:
    """Validate an env-var (KEY, VALUE) pair destined for `docker run -e`.

    Returns the validated pair unchanged. Raises ValueError on any pattern
    that could become a new argv flag or split into multiple argv tokens
    after the f'{key}={value}' join. Empty values are allowed (the proxy
    block in start_container relies on '-e KEY=' to *unset* upstream
    proxy env vars), but the caller is responsible for the existing
    `if value:` guards where that semantic differs.
    """
    if not isinstance(key, str) or not _ENV_KEY_RE.match(key):
        raise ValueError(f"invalid env var name: {key!r}")
    if not isinstance(value, str):
        raise ValueError(
            f"env value for {key!r} must be str, got {type(value).__name__}"
        )
    if value.startswith("-"):
        raise ValueError(
            f"env value for {key!r} starts with '-' (argv-flag injection)"
        )
    if any(c in value for c in _FORBIDDEN_VALUE_CHARS):
        raise ValueError(
            f"env value for {key!r} contains a forbidden control char"
        )
    return key, value


def _validate_docker_token(name: str, token: str) -> str:
    """Validate a bare argv token (image, network, container_name, ...).

    These positions never have a '-e' prefix, so a leading '-' would be
    consumed directly as a docker flag. Whitespace would split the token
    into multiple argv elements. NUL would terminate it.
    """
    if not isinstance(token, str):
        raise ValueError(
            f"{name} must be str, got {type(token).__name__}"
        )
    if not token:
        raise ValueError(f"{name} must be a non-empty string")
    if token.startswith("-"):
        raise ValueError(
            f"{name} {token!r} starts with '-' (argv-flag injection)"
        )
    if any(c in token for c in _FORBIDDEN_TOKEN_CHARS):
        raise ValueError(
            f"{name} {token!r} contains a forbidden whitespace / control char"
        )
    return token


def build_env_args(pairs: list[tuple[str, str]] | dict[str, str]) -> list[str]:
    """Build a validated ['-e', 'K=V', '-e', 'K=V', ...] list.

    Accepts an ordered list of (key, value) pairs OR a dict (insertion-
    ordered). Empty values are honored — they emit '-e KEY=' which docker
    treats as 'set KEY to the empty string', the form the proxy-clear
    block in start_container depends on.
    """
    if isinstance(pairs, dict):
        items = list(pairs.items())
    else:
        items = list(pairs)
    out: list[str] = []
    for key, value in items:
        _validate_env_arg(key, value)
        out.append("-e")
        out.append(f"{key}={value}")
    return out


def remove_container(name: str) -> None:
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)


def _container_running(task_id: str) -> bool:
    r = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", task_id],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and r.stdout.strip() == "true"


def _map_workspace_dst(container_dst: str) -> str:
    """Map an inject mutation's container path to the live agent workspace.

    Inject mutations address files as ``/workspace/<rel>`` (occasionally
    ``/app/<rel>``); the agent's writable tree lives at ``TMP_WORKSPACE``, which
    ``/root/workspace`` and ``/root/.openclaw/workspace`` symlink to. A relative
    path is taken as workspace-relative. Other absolute paths are honored as-is.
    """
    p = str(container_dst or "").strip()
    for prefix in ("/workspace/", "/app/"):
        if p.startswith(prefix):
            return str(PurePosixPath(TMP_WORKSPACE) / p[len(prefix):])
    if p in ("/workspace", "/app"):
        return TMP_WORKSPACE
    if p.startswith(TMP_WORKSPACE) or p.startswith("/"):
        return p
    return str(PurePosixPath(TMP_WORKSPACE) / p)


def copy_file_into_workspace(task_id: str, host_src: "Path | None",
                             container_dst: str, mkdir: bool = False) -> bool:
    """InjectDirector filesystem hook: place a host file (or mkdir) inside the
    running agent container's workspace via ``docker cp`` / ``docker exec``.

    Returns False (the caller logs it as a skipped fs op) when the container is
    not running — e.g. the pre-T0 seed stage, which fires before the agent
    container starts and whose drops are redundant with the mounted ``/app``
    baseline. Per-turn drops fire mid-run while the container is up.
    """
    if not _container_running(task_id):
        logger.info("[%s] inject fs: container not up; skip %s", task_id, container_dst)
        return False
    dst = _map_workspace_dst(container_dst)
    try:
        if mkdir:
            r = subprocess.run(["docker", "exec", task_id, "mkdir", "-p", dst],
                               capture_output=True, text=True)
            return r.returncode == 0
        if host_src is None:
            return False
        parent = str(PurePosixPath(dst).parent)
        subprocess.run(["docker", "exec", task_id, "mkdir", "-p", parent],
                       capture_output=True, text=True)
        r = subprocess.run(["docker", "cp", str(host_src), f"{task_id}:{dst}"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            logger.warning("[%s] inject fs: docker cp failed %s -> %s: %s",
                           task_id, host_src, dst, (r.stderr or "").strip())
            return False
        # Keep agent-writable so later turns can edit (mirrors setup_workspace).
        subprocess.run(["docker", "exec", task_id, "chmod", "-R", "u+w", dst],
                       capture_output=True, text=True)
        return True
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("[%s] inject fs: error placing %s: %s", task_id, dst, exc)
        return False


def require_image_present(image: str) -> None:
    # Strict precheck for images that must already exist locally (the agent
    # image is loaded from the HuggingFace tar via `docker load`; we never
    # pull-on-run). Any miss raises so the harness fails fast at startup
    # instead of silently letting `docker run` try and fail mid-task with
    # `manifest unknown`.
    r = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"Required Docker image not present locally: {image}\n"
            f"Load it first (e.g. `docker load -i Images/wildclawbench-ubuntu_v1.3.tar`)\n"
            f"or set DOCKER_IMAGE to a tag that exists. docker inspect said:\n"
            f"{(r.stderr or '').strip()}"
        )
    logger.info("Agent image %s present", image)

def start_container(task_id: str, workspace_path: str, extra_env: str = "",
                    tmp_path: str = "", lobster_env: list[str] | None = None,
                    extra_env_dict: dict[str, str] | None = None,
                    network: str = "") -> None:
    workspace = Path(workspace_path).expanduser()
    if not workspace.is_dir():
        raise RuntimeError(f"Workspace path does not exist or is not a directory: {workspace}")

    _validate_docker_token("task_id", task_id)
    if network:
        _validate_docker_token("network", network)

    proxy_http = os.environ.get('HTTP_PROXY_INNER', '')
    proxy_https = os.environ.get('HTTPS_PROXY_INNER', '')
    # The wildclawbench-ubuntu:v1.3 image bakes in
    #   http_proxy=http://100.104.40.233:7897
    #   https_proxy=http://100.104.40.233:7897
    # (from the image builder's prior corporate VPN; unreachable from Docker).
    # If we don't override them, every outbound HTTP from the agent (curl,
    # requests, the OpenAI SDK that openclaw uses to call our LiteLLM
    # sidecar) routes through that dead proxy and returns "Connection
    # error." instantly. That is the alden-croft 2026-06-02 incident:
    # rawErrorPreview="Connection error." rawErrorHash=sha256:8ec9a0b7fe5c,
    # 4 retries within 20s, surface_error, score 0. Empirically reproduced
    # against bare image (no env injection) — both intra-network sidecar
    # and public internet calls fail identically because curl tries the
    # poisoned proxy before TCP-connect to the real target.
    # Fix: when no external proxy is configured, EXPLICITLY pass `-e
    # var=""` so Docker overrides the image's baked defaults with empty
    # strings (most HTTP libs treat empty as "no proxy"; coherent with the
    # --internal-bridge sandbox from (b14)).
    env_pairs: list[tuple[str, str]] = [("BRAVE_API_KEY", BRAVE_API_KEY)]
    if proxy_http or proxy_https:
        no_proxy_value = os.environ.get("NO_PROXY_INNER", "")
        env_pairs += [
            ("http_proxy", proxy_http),
            ("https_proxy", proxy_https),
            ("HTTP_PROXY", proxy_http),
            ("HTTPS_PROXY", proxy_https),
            ("no_proxy", no_proxy_value),
            ("NO_PROXY", no_proxy_value),
        ]
    else:
        env_pairs += [
            ("http_proxy", ""),
            ("https_proxy", ""),
            ("HTTP_PROXY", ""),
            ("HTTPS_PROXY", ""),
            ("no_proxy", ""),
            ("NO_PROXY", ""),
        ]
    for line in extra_env.splitlines():
        key = line.strip()
        if not key or key.startswith("#"):
            continue
        value = os.environ.get(key, "")
        env_pairs.append((key, value))
        masked = (value[:4] + "***") if value else "(empty)"
        logger.info("[%s] Injecting env var: %s=%s", task_id, key, masked)

    for key in (lobster_env or []):
        value = os.environ.get(key, "")
        if not value:
            logger.warning("[%s] Lobster env key %s not found in environment, skipping", task_id, key)
            continue
        env_pairs.append((key, value))
        masked = value[:4] + "***"
        logger.info("[%s] Injecting lobster env: %s=%s", task_id, key, masked)

    _injected_keys: list[str] = []
    for k, v in (extra_env_dict or {}).items():
        env_pairs.append((k, v))
        _injected_keys.append(k)
    if _injected_keys:
        logger.info("[%s] Injected %d extra env vars: %s",
                    task_id, len(_injected_keys), ",".join(sorted(_injected_keys)))

    env_args = build_env_args(env_pairs)
    image = _validate_docker_token("image", os.environ.get("DOCKER_IMAGE", DOCKER_IMAGE))
    network_args = ["--network", network] if network else []
    cmd = [
        "docker", "run", "-d",
        "--name", task_id,
        *network_args,
        *env_args,
        "-v", f"{workspace}:/app:ro",
        image,
        "/bin/bash", "-c", "tail -f /dev/null",
    ]
    logger.info("[%s] Starting container, mounting %s → /app (ro)", task_id, workspace)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Container startup failed:\n{r.stderr}")
    logger.info("[%s] Container ID: %s", task_id, r.stdout.strip()[:12])

    if tmp_path and os.path.exists(tmp_path):
        mkdir_cmd = ["docker", "exec", task_id, "mkdir", "-p", "/tmp_workspace/tmp"]
        subprocess.run(mkdir_cmd, capture_output=True)

        cp_cmd = ["docker", "cp", f"{tmp_path}/.", f"{task_id}:/tmp_workspace/tmp/"]
        
        logger.info("[%s] Copying temp files: %s → /tmp_workspace/tmp", task_id, tmp_path)
        cp_r = subprocess.run(cp_cmd, capture_output=True, text=True)
        
        if cp_r.returncode != 0:
            logger.error("[%s] File copy failed: %s", task_id, cp_r.stderr)
        else:
            logger.info("[%s] Temp file copy complete", task_id)

def setup_workspace(task_id: str, thinking: str | None = None) -> None:
    logger.info("[%s] Copying /app → %s", task_id, TMP_WORKSPACE)
    r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c",
         f"cp -r /app/. {TMP_WORKSPACE} && chmod -R u+w {TMP_WORKSPACE}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Workspace copy failed:\n{r.stderr}")

    if thinking is not None:
        logger.info("[%s] Setting thinkingDefault to %s", task_id, thinking)
        thinking_result = subprocess.run(
            ["docker", "exec", task_id,
             "openclaw", "config", "set", "agents.defaults.thinkingDefault", thinking],
            capture_output=True, text=True,
        )
        if thinking_result.returncode != 0:
            raise RuntimeError(
                f"Failed to set thinkingDefault to {thinking}:\n{thinking_result.stderr}"
            )

    # Symlink OpenClaw workspace → TMP_WORKSPACE so the image tool's
    # media-local-roots check allows reading files under /tmp_workspace.
    subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c",
         f"rm -rf /root/.openclaw/workspace && ln -s {TMP_WORKSPACE} /root/.openclaw/workspace"],
        capture_output=True, text=True,
    )

    # Expose the workspace at /root/workspace too (kensei-native flow reads
    # deliverables from here). Use a SYMLINK to TMP_WORKSPACE, not a copy: the
    # in-container grader runs against TMP_WORKSPACE, so anything an agent writes
    # to /root/workspace/... must land in TMP_WORKSPACE to be graded/collected.
    # A copy drifts after setup and silently hides those deliverables (the
    # /root/workspace/<subdir> → empty /tmp_workspace/results mismatch). Mirrors
    # the /root/.openclaw/workspace symlink above.
    subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c",
         f"rm -rf /root/workspace && ln -s {TMP_WORKSPACE} /root/workspace"],
        capture_output=True, text=True,
    )

def setup_skills(
    task_id: str,
    skills: str,
    skills_path: str,
    container_skills_root: str = "/root/skills",
) -> None:
    container_skills_root = container_skills_root.rstrip("/")
    subprocess.run(
        ["docker", "exec", task_id, "mkdir", "-p", container_skills_root],
        capture_output=True,
        text=True,
    )
    seen_dest_names: set[str] = set()
    for line in skills.splitlines():
        line = line.strip()
        if not line:
            continue
        src_rel = line.replace("\\", "/").strip("/")
        dest_name = PurePosixPath(src_rel).name
        if not dest_name:
            logger.warning("[%s] Invalid skill path %r, skipping", task_id, line)
            continue
        if dest_name in seen_dest_names:
            logger.warning(
                "[%s] Duplicate flattened skill target %s from %s, skipping",
                task_id,
                dest_name,
                line,
            )
            continue
        seen_dest_names.add(dest_name)
        subprocess.run(
            ["docker", "exec", task_id,
             "mkdir", "-p", f"{container_skills_root}/{dest_name}"],
            capture_output=True, text=True,
        )
        r = subprocess.run(
            ["docker", "cp",
             f"{skills_path}/{src_rel}/.", f"{task_id}:{container_skills_root}/{dest_name}/"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            logger.warning(
                "[%s] Failed to copy skill %s to %s/%s: %s",
                task_id,
                line,
                container_skills_root,
                dest_name,
                r.stderr.strip(),
            )


_BASELINE_SKILL_PIP_DEPS: tuple[str, ...] = (
    "pymupdf",
    "pillow",
    "pytesseract",
    "pdfplumber",
    "pdf2image",
    "opencv-python-headless",
    "openpyxl",
    "python-docx",
    "python-pptx",
    "pandas",
    "pypdf",
)


# Offline wheelhouse + debhouse. Agent containers run on an --internal docker
# network (litellm_sidecar.py:272-307) so PyPI and archive.ubuntu.com are
# unreachable; we docker-cp these in and install offline with
# `pip install --no-index --find-links` / `dpkg -i`.
_REPO_ROOT: Path = Path(__file__).resolve().parent.parent.parent
_WHEELHOUSE_HOST_DIR: Path = _REPO_ROOT / "wheelhouse" / "skill-deps"
# /opt is writable and avoids colliding with /tmp_workspace (ro) and /opt/mocks
# (mock_stack.py:216-256 bind mounts).
_WHEELHOUSE_CONTAINER_DIR: str = "/opt/wb_wheels"
_DEBHOUSE_HOST_DIR: Path = _REPO_ROOT / "debhouse" / "skill-deps"
_DEBHOUSE_CONTAINER_DIR: str = "/opt/wb_debs"


_BIN_TO_APT_PACKAGE: dict[str, str] = {
    "ffmpeg": "ffmpeg",
    "ffprobe": "ffmpeg",
    "tesseract": "tesseract-ocr",
    "pdftotext": "poppler-utils",
    "pdfinfo": "poppler-utils",
    "unzip": "unzip",
}


_BASELINE_SKILL_APT_PACKAGES: tuple[str, ...] = (
    "ffmpeg",
    "tesseract-ocr",
    "poppler-utils",
    "unzip",
)


_SKILL_DEP_PROBE_IMPORTS: tuple[tuple[str, str], ...] = (
    ("fitz", "pymupdf"),
    ("PIL", "pillow"),
    ("pytesseract", "pytesseract"),
    ("pdfplumber", "pdfplumber"),
    ("openpyxl", "openpyxl"),
    ("docx", "python-docx"),
    ("pandas", "pandas"),
    ("pypdf", "pypdf"),
)


_SKILL_DEP_PROBE_BINS: tuple[str, ...] = (
    "ffmpeg",
    "tesseract",
    "pdftotext",
    "unzip",
)


def _parse_skill_pip_deps(skill_md_path: Path) -> list[str]:
    if not skill_md_path.is_file():
        return []
    try:
        text = skill_md_path.read_text(encoding="utf-8")
    except OSError:
        return []
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    try:
        import yaml as _yaml
        frontmatter = _yaml.safe_load(parts[1]) or {}
    except Exception:
        return []
    if not isinstance(frontmatter, dict):
        return []
    metadata = frontmatter.get("metadata") or {}
    if not isinstance(metadata, dict):
        return []
    clawdbot = metadata.get("clawdbot") or {}
    if not isinstance(clawdbot, dict):
        return []
    pip_deps = clawdbot.get("pip") or []
    requires = clawdbot.get("requires") or {}
    requires_pip = requires.get("pip") or [] if isinstance(requires, dict) else []
    deps = list(pip_deps) + list(requires_pip)
    return [str(d).strip() for d in deps if str(d).strip()]


def _parse_skill_bin_deps(skill_md_path: Path) -> list[str]:
    if not skill_md_path.is_file():
        return []
    try:
        text = skill_md_path.read_text(encoding="utf-8")
    except OSError:
        return []
    if not text.startswith("---"):
        return []
    parts = text.split("---", 2)
    if len(parts) < 3:
        return []
    try:
        import yaml as _yaml
        frontmatter = _yaml.safe_load(parts[1]) or {}
    except Exception:
        return []
    if not isinstance(frontmatter, dict):
        return []
    metadata = frontmatter.get("metadata") or {}
    if not isinstance(metadata, dict):
        return []
    clawdbot = metadata.get("clawdbot") or {}
    if not isinstance(clawdbot, dict):
        return []
    requires = clawdbot.get("requires") or {}
    bins = requires.get("bins") or [] if isinstance(requires, dict) else []
    return [str(b).strip() for b in bins if str(b).strip()]


def _install_skill_runtime_deps(task_id: str, env_root: Path) -> dict[str, list[str]]:
    pip_deps: set[str] = set(_BASELINE_SKILL_PIP_DEPS)
    apt_packages: set[str] = set(_BASELINE_SKILL_APT_PACKAGES)
    skills_src = env_root / "skills"
    if skills_src.is_dir():
        for entry in sorted(skills_src.iterdir()):
            if not entry.is_dir() or entry.name.endswith("-connector"):
                continue
            skill_md = entry / "SKILL.md"
            for pkg in _parse_skill_pip_deps(skill_md):
                pip_deps.add(pkg)
            for binary in _parse_skill_bin_deps(skill_md):
                apt_pkg = _BIN_TO_APT_PACKAGE.get(binary)
                if apt_pkg:
                    apt_packages.add(apt_pkg)

    sorted_apt = sorted(apt_packages)
    if sorted_apt:
        _install_apt_deps_from_debhouse(task_id, sorted_apt)

    sorted_pip = sorted(pip_deps)
    if sorted_pip:
        _install_pip_deps_from_wheelhouse(task_id, sorted_pip)

    return {"pip": sorted_pip, "apt": sorted_apt}


def _install_apt_deps_from_debhouse(task_id: str, sorted_apt: list[str]) -> None:
    precheck_cmd = (
        "set -e; "
        "if ! command -v dpkg >/dev/null 2>&1; then echo 'no-dpkg'; exit 0; fi; "
        "missing=''; "
        "for p in " + " ".join(shlex.quote(p) for p in sorted_apt) + "; do "
        "  dpkg -s \"$p\" >/dev/null 2>&1 || missing=\"$missing $p\"; "
        "done; "
        "if [ -z \"$missing\" ]; then echo 'all-present'; else echo \"missing:$missing\"; fi"
    )
    precheck = subprocess.run(
        ["docker", "exec", task_id, "bash", "-lc", precheck_cmd],
        capture_output=True, text=True,
    )
    pre_stdout = (precheck.stdout or "").strip()
    if pre_stdout == "all-present":
        logger.info(
            "[%s] Skill runtime apt packages already present (%d): %s",
            task_id, len(sorted_apt), ",".join(sorted_apt),
        )
        return
    if pre_stdout == "no-dpkg":
        logger.warning(
            "[%s] dpkg not available in image; skipping apt step", task_id,
        )
        return

    if not _DEBHOUSE_HOST_DIR.is_dir():
        logger.error(
            "[%s] Debhouse missing at %s. Skill runtime apt deps will NOT be installed; "
            "pdf/image/audio skills will fail. Rebuild via: "
            "docker run --rm --platform linux/amd64 -v %s:/out ubuntu:22.04 bash -c "
            "'apt-get update && apt-get install -y --no-install-recommends apt-rdepends && "
            "for p in %s; do for d in $(apt-rdepends $p 2>/dev/null | grep -v \"^ \"); do "
            "apt-get download \"$d\" 2>/dev/null || true; done; done && mv *.deb /out/'",
            task_id, _DEBHOUSE_HOST_DIR, _DEBHOUSE_HOST_DIR, " ".join(sorted_apt),
        )
        return

    debs = list(_DEBHOUSE_HOST_DIR.glob("*.deb"))
    if not debs:
        logger.error(
            "[%s] Debhouse %s contains no *.deb files; skill runtime apt deps will NOT be installed",
            task_id, _DEBHOUSE_HOST_DIR,
        )
        return

    mkdir = subprocess.run(
        ["docker", "exec", task_id, "mkdir", "-p", _DEBHOUSE_CONTAINER_DIR],
        capture_output=True, text=True,
    )
    if mkdir.returncode != 0:
        logger.warning(
            "[%s] Failed to create %s in container (continuing). stderr: %s",
            task_id, _DEBHOUSE_CONTAINER_DIR, (mkdir.stderr or "").strip()[:300],
        )
        return

    cp = subprocess.run(
        ["docker", "cp", f"{_DEBHOUSE_HOST_DIR}/.", f"{task_id}:{_DEBHOUSE_CONTAINER_DIR}/"],
        capture_output=True, text=True,
    )
    if cp.returncode != 0:
        logger.warning(
            "[%s] docker cp debhouse -> %s failed (continuing). stderr: %s",
            task_id, _DEBHOUSE_CONTAINER_DIR, (cp.stderr or "").strip()[:300],
        )
        return

    install_cmd = (
        "set -e; "
        "export DEBIAN_FRONTEND=noninteractive; "
        "cd " + shlex.quote(_DEBHOUSE_CONTAINER_DIR) + "; "
        "dpkg -i *.deb >/tmp/wb_dpkg.log 2>&1 || { "
        "  cat /tmp/wb_dpkg.log >&2; exit 1; "
        "}; "
        "echo 'installed-offline'"
    )
    install = subprocess.run(
        ["docker", "exec", task_id, "bash", "-lc", install_cmd],
        capture_output=True, text=True,
    )
    if install.returncode != 0:
        logger.warning(
            "[%s] Offline dpkg install from debhouse returned %d (continuing; "
            "verify probe will report missing bins). stderr: %s",
            task_id, install.returncode, (install.stderr or "").strip()[:500],
        )
    else:
        logger.info(
            "[%s] Installed skill runtime apt deps offline from %s "
            "(%d .debs staged, %d top-level packages): %s",
            task_id, _DEBHOUSE_CONTAINER_DIR, len(debs), len(sorted_apt), ",".join(sorted_apt),
        )


def _install_pip_deps_from_wheelhouse(task_id: str, sorted_pip: list[str]) -> None:
    requirements_file = _WHEELHOUSE_HOST_DIR / "requirements.txt"
    if not _WHEELHOUSE_HOST_DIR.is_dir() or not requirements_file.is_file():
        logger.error(
            "[%s] Wheelhouse missing at %s (expected requirements.txt + *.whl). "
            "Skill runtime pip deps will NOT be installed; pdf/image/audio skills will fail. "
            "Rebuild via: docker run --rm --platform linux/amd64 -v %s:/out python:3.10-slim "
            "bash -c 'pip download --dest /out --platform manylinux2014_x86_64 "
            "--python-version 310 --implementation cp --abi cp310 --only-binary=:all: %s'",
            task_id, _WHEELHOUSE_HOST_DIR, _WHEELHOUSE_HOST_DIR, " ".join(sorted_pip),
        )
        return

    wheels = list(_WHEELHOUSE_HOST_DIR.glob("*.whl"))
    if not wheels:
        logger.error(
            "[%s] Wheelhouse %s contains no *.whl files; skill runtime pip deps will NOT be installed",
            task_id, _WHEELHOUSE_HOST_DIR,
        )
        return

    mkdir = subprocess.run(
        ["docker", "exec", task_id, "mkdir", "-p", _WHEELHOUSE_CONTAINER_DIR],
        capture_output=True, text=True,
    )
    if mkdir.returncode != 0:
        logger.warning(
            "[%s] Failed to create %s in container (continuing). stderr: %s",
            task_id, _WHEELHOUSE_CONTAINER_DIR, (mkdir.stderr or "").strip()[:300],
        )
        return

    cp = subprocess.run(
        ["docker", "cp", f"{_WHEELHOUSE_HOST_DIR}/.", f"{task_id}:{_WHEELHOUSE_CONTAINER_DIR}/"],
        capture_output=True, text=True,
    )
    if cp.returncode != 0:
        logger.warning(
            "[%s] docker cp wheelhouse -> %s failed (continuing). stderr: %s",
            task_id, _WHEELHOUSE_CONTAINER_DIR, (cp.stderr or "").strip()[:300],
        )
        return

    install = subprocess.run(
        ["docker", "exec", task_id, "pip", "install",
         "--quiet", "--disable-pip-version-check", "--no-input",
         "--no-index", "--find-links", _WHEELHOUSE_CONTAINER_DIR,
         "-r", f"{_WHEELHOUSE_CONTAINER_DIR}/requirements.txt",
         *sorted_pip],
        capture_output=True, text=True,
    )
    if install.returncode != 0:
        logger.warning(
            "[%s] Offline pip install from wheelhouse returned %d (continuing; "
            "verify probe will report missing modules). stderr: %s",
            task_id, install.returncode, (install.stderr or "").strip()[:500],
        )
    else:
        logger.info(
            "[%s] Installed skill runtime pip deps offline from %s (%d wheels staged, %d top-level deps): %s",
            task_id, _WHEELHOUSE_CONTAINER_DIR, len(wheels), len(sorted_pip), ",".join(sorted_pip),
        )


def _verify_skill_runtime_deps(task_id: str) -> list[str]:
    probe = (
        "import importlib, json, shutil, sys\n"
        "modules = " + repr([m for m, _ in _SKILL_DEP_PROBE_IMPORTS]) + "\n"
        "bins = " + repr(list(_SKILL_DEP_PROBE_BINS)) + "\n"
        "missing_modules = []\n"
        "for m in modules:\n"
        "    try:\n"
        "        importlib.import_module(m)\n"
        "    except Exception:\n"
        "        missing_modules.append(m)\n"
        "missing_bins = [b for b in bins if shutil.which(b) is None]\n"
        "sys.stdout.write(json.dumps({'modules': missing_modules, 'bins': missing_bins}))\n"
    )
    r = subprocess.run(
        ["docker", "exec", task_id, "python3", "-c", probe],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning(
            "[%s] Skill runtime verification probe failed to run: %s",
            task_id, (r.stderr or "").strip()[:300],
        )
        return []
    try:
        result = json.loads(r.stdout.strip() or "{}")
    except json.JSONDecodeError:
        logger.warning(
            "[%s] Skill runtime verification: could not parse probe stdout: %r",
            task_id, r.stdout[:200],
        )
        return []
    module_to_pkg = dict(_SKILL_DEP_PROBE_IMPORTS)
    missing_pkgs = [module_to_pkg.get(m, m) for m in result.get("modules", [])]
    missing_bins = list(result.get("bins", []))
    all_missing = missing_pkgs + missing_bins
    if all_missing:
        logger.error(
            "[%s] Skill runtime deps STILL MISSING after install "
            "(pdf/image/audio skills will fail): pip=%s bins=%s",
            task_id, ",".join(missing_pkgs) or "-", ",".join(missing_bins) or "-",
        )
    else:
        logger.info(
            "[%s] Skill runtime deps verified present: pip=%s bins=%s",
            task_id,
            ",".join(m for m, _ in _SKILL_DEP_PROBE_IMPORTS),
            ",".join(_SKILL_DEP_PROBE_BINS),
        )
    return all_missing


def inject_api_connectors(
    task_id: str,
    env_dir: str,
    required_apis: list[str],
    container_skills_root: str = "/root/skills",
) -> None:
    """Copy <env_dir>/skills/<api>-connector dirs into the container's skills
    root, plus API_DOCUMENTATION.md into /root/. No-op if env_dir or required
    APIs are empty."""
    if not env_dir or not required_apis:
        return
    env_root = Path(env_dir)
    if not env_root.is_dir():
        return
    container_skills_root = container_skills_root.rstrip("/")
    subprocess.run(
        ["docker", "exec", task_id, "mkdir", "-p", container_skills_root],
        capture_output=True, text=True,
    )
    # openclaw's skill loader calls realpath() on every entry in its
    # bundled root and rejects anything resolving outside that root
    # ('Skipping skill path that resolves outside its configured root').
    # Symlinks from /usr/lib/.../skills -> /root/skills are rejected.
    # Copy connector files directly into the bundled root so realpath
    # returns the same root and the loader accepts them. Observed in
    # 2026-06-02 gpt trajectory (gateway.log lines 7-14, 17 skill-skip
    # warnings for etsy/google-classroom/google-drive/instagram).
    openclaw_skills_root = "/usr/lib/node_modules/openclaw/skills"
    subprocess.run(
        ["docker", "exec", task_id, "mkdir", "-p", openclaw_skills_root],
        capture_output=True, text=True,
    )
    injected: list[str] = []
    missing_sources: list[str] = []
    for api in required_apis:
        connector = env_root / "skills" / f"{api}-connector"
        if not connector.is_dir():
            missing_sources.append(api)
            continue
        dest = f"{openclaw_skills_root}/{api}-connector"
        subprocess.run(
            ["docker", "exec", task_id, "rm", "-rf", dest],
            capture_output=True, text=True,
        )
        subprocess.run(
            ["docker", "exec", task_id, "mkdir", "-p", dest],
            capture_output=True, text=True,
        )
        r = subprocess.run(
            ["docker", "cp", f"{connector}/.", f"{task_id}:{dest}/"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            logger.warning("[%s] Failed to inject connector %s: %s", task_id, api, r.stderr.strip())
            continue
        injected.append(api)
    if missing_sources:
        logger.warning(
            "[%s] Connector source missing for required API(s) (no env_dir/skills/<api>-connector): %s",
            task_id, missing_sources,
        )
    # Non-connector utility skills (pdf-extract, audio-extract, video-frames,
    # self-improving-agent-*) ship in environment/skills/ alongside the 101
    # <api>-connector dirs. They are NOT keyed by required_apis. Without
    # injection, agent attempts to read /usr/lib/.../skills/pdf-extract/SKILL.md
    # and ENOENTs. Observed in alden-croft 2026-06-02T17:05:11 gateway.log line
    # 3: '[tools] read failed: ENOENT ... /skills/pdf-extract/SKILL.md'. The
    # agent image's bundled openclaw package does not ship these built-ins; the
    # harness owns them. Copy every non-connector top-level skill dir.
    skills_src = env_root / "skills"
    utility_injected: list[str] = []
    if skills_src.is_dir():
        for entry in sorted(skills_src.iterdir()):
            if not entry.is_dir() or entry.name.endswith("-connector"):
                continue
            dest = f"{openclaw_skills_root}/{entry.name}"
            subprocess.run(
                ["docker", "exec", task_id, "rm", "-rf", dest],
                capture_output=True, text=True,
            )
            subprocess.run(
                ["docker", "exec", task_id, "mkdir", "-p", dest],
                capture_output=True, text=True,
            )
            r = subprocess.run(
                ["docker", "cp", f"{entry}/.", f"{task_id}:{dest}/"],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                logger.warning("[%s] Failed to inject utility skill %s: %s", task_id, entry.name, r.stderr.strip())
                continue
            utility_injected.append(entry.name)
    # The wildclawbench-ubuntu:v1.3 image does not ship pymupdf/pillow/etc.
    # pdf-extract's SKILL.md declares pip:["pymupdf"] in its frontmatter; without
    # this install pass the agent reads SKILL.md, follows its instructions, then
    # hits `ModuleNotFoundError: No module named 'fitz'`. Observed in trajectory
    # 727a9129-fadc-495b-b29f-0abba34cd594 (2026-06-05). Image-OCR libs are also
    # absent (PIL/pytesseract/cv2). Until the image is rebuilt, install at task
    # startup. Verification probe afterward catches future drift loudly.
    _install_skill_runtime_deps(task_id, env_root)
    _verify_skill_runtime_deps(task_id)
    api_doc = env_root / "API_DOCUMENTATION.md"
    if api_doc.is_file():
        r = subprocess.run(
            ["docker", "cp", str(api_doc), f"{task_id}:/root/API_DOCUMENTATION.md"],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            logger.info("[%s] Injected API_DOCUMENTATION.md → /root/API_DOCUMENTATION.md", task_id)
        else:
            logger.warning("[%s] Failed to inject API_DOCUMENTATION.md: %s", task_id, r.stderr.strip())
    else:
        logger.info("[%s] No API_DOCUMENTATION.md at %s (skipped)", task_id, api_doc)
    if injected:
        logger.info("[%s] Injected API connectors (%d): %s", task_id, len(injected), ",".join(injected))
    if utility_injected:
        logger.info("[%s] Injected utility skills (%d): %s", task_id, len(utility_injected), ",".join(utility_injected))


def _parse_service_toml(path: Path) -> dict:
    result: dict = {}
    in_service = False
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "[service]":
            in_service = True
            continue
        if line.startswith("["):
            in_service = False
            continue
        if in_service and "=" in line:
            k, v = line.split("=", 1)
            key = k.strip()
            val = v.strip().strip('"').strip("'")
            result[key] = int(val) if key == "port" and val.isdigit() else val
    return result


def discover_services(environment_dir: Path) -> list[dict]:
    """Return [{name, port, env_var_name}] for every <env>/<svc>/service.toml."""
    services: list[dict] = []
    environment_dir = Path(environment_dir)
    if not environment_dir.is_dir():
        return services
    for entry in sorted(environment_dir.iterdir()):
        if not entry.is_dir():
            continue
        toml_path = entry / "service.toml"
        if not toml_path.is_file():
            continue
        try:
            cfg = _parse_service_toml(toml_path)
        except Exception:
            continue
        port = cfg.get("port")
        if not port:
            continue
        services.append({
            "name": entry.name,
            "port": port,
            "env_var_name": cfg.get("env_var_name", ""),
        })
    return services


def setup_mock_apis(task_id: str, environment_dir: Path,
                    required_apis: list[str]) -> dict[str, str]:
    """Per-task (non-stack) mode: copy each required mock API into the agent
    container under /opt/mock_apis/<name>, returning a {env_var_name: url} map
    for localhost ports. Use warmup_for_mock_apis() to start them."""
    env_vars: dict[str, str] = {}
    for api_name in required_apis:
        api_dir = Path(environment_dir) / api_name
        if not api_dir.is_dir():
            logger.warning("[%s] Mock API dir not found: %s", task_id, api_dir)
            continue
        service_toml = api_dir / "service.toml"
        if not service_toml.is_file():
            logger.warning("[%s] service.toml missing for %s", task_id, api_name)
            continue
        try:
            cfg = _parse_service_toml(service_toml)
        except Exception as exc:
            logger.warning("[%s] Failed to parse service.toml for %s: %s", task_id, api_name, exc)
            continue
        port = cfg.get("port")
        env_var_name = cfg.get("env_var_name")
        if not port or not env_var_name:
            logger.warning("[%s] Missing port/env_var_name for %s", task_id, api_name)
            continue
        dest = f"/opt/mock_apis/{api_name}"
        subprocess.run(["docker", "exec", task_id, "mkdir", "-p", dest], capture_output=True)
        r = subprocess.run(
            ["docker", "cp", f"{api_dir}/.", f"{task_id}:{dest}/"],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            logger.warning("[%s] Failed to copy mock API %s: %s", task_id, api_name, r.stderr)
            continue
        env_vars[env_var_name] = f"http://localhost:{port}"
        logger.info("[%s] Mock API %s copied → %s (port %s)", task_id, api_name, dest, port)
    # Stage the shared tracking middleware alongside the copied APIs so that
    # `from tracking_middleware import install_tracker` resolves when each server
    # runs with PYTHONPATH=/opt/mock_apis (see warmup_for_mock_apis).
    tracking_mw = Path(environment_dir) / "tracking_middleware.py"
    if env_vars and tracking_mw.is_file():
        subprocess.run(["docker", "exec", task_id, "mkdir", "-p", "/opt/mock_apis"],
                       capture_output=True)
        subprocess.run(["docker", "cp", str(tracking_mw),
                        f"{task_id}:/opt/mock_apis/tracking_middleware.py"],
                       capture_output=True)
    return env_vars


def warmup_for_mock_apis(required_apis: list[str], environment_dir: Path) -> str:
    lines: list[str] = []
    for api_name in required_apis:
        api_dir = Path(environment_dir) / api_name
        toml_path = api_dir / "service.toml"
        if not toml_path.is_file():
            continue
        try:
            port = _parse_service_toml(toml_path).get("port")
        except Exception:
            port = None
        if not port:
            continue
        dest = f"/opt/mock_apis/{api_name}"
        lines.append(f"pip install -q -r {dest}/requirements.txt 2>/dev/null || true")
        # server.py exposes `app` but has no __main__ block, so it must be served
        # via uvicorn (not `python server.py`, which would import and exit without
        # binding). PYTHONPATH=/opt/mock_apis lets the shared tracking_middleware
        # module import (staged by setup_mock_apis).
        lines.append(
            f"cd {dest} && PYTHONPATH=/opt/mock_apis "
            f"uvicorn server:app --host 0.0.0.0 --port {port} "
            f"> /tmp/mock_{api_name}.log 2>&1 &"
        )
    return "\n".join(lines)


def inject_openclaw_models(task_id: str, models_config: dict) -> None:
    """Inject custom models into ~/.openclaw/openclaw.json."""
    container_tmp_path = "/tmp/openclaw_models.json"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tmp_file:
        json.dump(models_config, tmp_file, indent=2)
        tmp_file_path = tmp_file.name

    try:
        cp_r = subprocess.run(
            ["docker", "cp", tmp_file_path, f"{task_id}:{container_tmp_path}"],
            capture_output=True, text=True,
        )
        if cp_r.returncode != 0:
            raise RuntimeError(f"Failed to copy models config into container:\n{cp_r.stderr}")

        inject_cmd = f"""python3 - <<'PY'
import json
import pathlib

config_path = pathlib.Path('/root/.openclaw/openclaw.json')
models_path = pathlib.Path('{container_tmp_path}')

config = json.loads(config_path.read_text()) if config_path.exists() else {{}}
models = json.loads(models_path.read_text())
config['models'] = models

config_path.write_text(json.dumps(config, indent=2))
PY"""
        r = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", inject_cmd],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Failed to inject models config:\n{r.stderr}")
    finally:
        Path(tmp_file_path).unlink(missing_ok=True)

    logger.info("[%s] Injected custom models config", task_id)



# ---- spawn-subagent skill injection (ported from june-7) ----
_SUBAGENT_SKILL_NAME = "spawn-subagent-connector"
_SUBAGENT_CONTAINER_ROOT = f"/usr/lib/node_modules/openclaw/skills/{_SUBAGENT_SKILL_NAME}"
# Native-path fan-out steering is appended to AGENTS.md (the persona bootstrap),
# NOT shipped as a skill: skills do not surface in the openclaw system prompt,
# so a SKILL.md cannot steer the model. See _render_native_spawn_steering and
# the AGENTS.md append in configure_native_subagents.
_SUBAGENT_TURN_MARKER = f"{TMP_WORKSPACE}/.wildclaw_current_turn"
_SUBAGENT_SPAWN_TREE = f"{TMP_WORKSPACE}/spawn_tree.jsonl"


def _render_subagent_skill_md(multi_agent_config: dict | None) -> str:
    cfg = multi_agent_config or {}
    default_tools = cfg.get("default_allowed_tools") or [
        "Read", "Write", "Edit", "Grep", "Glob", "Bash",
    ]
    tools_line = ", ".join(f"`{t}`" for t in default_tools)
    tools_json = ", ".join(f'"{t}"' for t in default_tools)
    return (
        "---\n"
        f"name: {_SUBAGENT_SKILL_NAME}\n"
        "description: \"Spawn one or more bounded sub-agents to fan a single turn out "
        "across independent angles in parallel. Each sub-agent runs a focused task using "
        "its own tools and returns plain text you synthesize. Let the turn's own structure "
        "decide: fan out when (1) the user asks you to handle several independent "
        "workstreams at once or to 'run the whole thing' / 'take care of all of it', (2) "
        "the work spans 2+ named sources or angles (e.g. workbook AND guide AND photo), or "
        "(3) the turn asks for a synthesized multi-section brief or summary that pulls "
        "together several separate areas. Each independent workstream, source, or section "
        "= one sub-agent. Do NOT use for a single tight question or one sequential task. "
        "Sub-agents cannot spawn further sub-agents.\"\n"
        "metadata: {\"clawdbot\":{\"emoji\":\"🪺\"}}\n"
        "---\n"
        "\n"
        "# Spawn Sub-Agent\n"
        "\n"
        "Run one or more short, bounded sub-agents in parallel and synthesize their final "
        "text answers. **Each sub-agent has its own tools and MUST fetch its own data** — "
        "do not paste raw data into `context`; point the sub-agent at a path or query and "
        "let it Read/Grep/Bash to gather what it needs.\n"
        "\n"
        "## When to invoke (trigger checklist)\n"
        "\n"
        "Let the turn's own structure decide. Invoke this skill at the start of any turn "
        "where ANY of these is true:\n"
        "\n"
        "1. **The turn bundles several independent workstreams** — one message that asks "
        "you to *'run the whole thing'*, *'sweep every surface and put it together'*, or to "
        "(say) draft quotes AND stand up a tracker AND reconcile the books AND stage a "
        "launch. Spawn one sub-agent per independent workstream.\n"
        "2. **The prompt asks you to consider 2+ independent sources or angles** — e.g. "
        "*'look at the workbook, the guide, AND the photo'*, *'extract budget then draft "
        "narrative'*, *'reconcile imagery against the log AND build the argument'*. Each "
        "named angle = one sub-agent.\n"
        "3. **The turn asks for a synthesized multi-section deliverable** over several "
        "separate areas — e.g. *'a launch-week brief, at least four sections'* or *'a "
        "verification summary, at least five sections'*. Fan out to gather each area in "
        "parallel, then synthesize.\n"
        "\n"
        "Do NOT invoke when the turn is a single tight question or one sequential task "
        "with no independent parts.\n"
        "\n"
        "## How to invoke\n"
        "\n"
        "Pipe a JSON spec to the script on stdin and read the sub-agent's final text "
        "from stdout. **Always pass `allowed_tools` and a non-zero `max_tool_calls`** so "
        "the sub-agent can fetch its own data; otherwise it can only hallucinate from the "
        "instructions string.\n"
        "\n"
        "```bash\n"
        "echo '{\n"
        "  \"role\": \"budget-extractor\",\n"
        "  \"instructions\": \"Open /tmp_workspace/deep_roots_grant_draft.docx (use Bash + python-docx or pdftotext as needed), extract the five Deep Roots budget line items with amounts in dollars, and report them as a plain-text table plus the total.\",\n"
        f"  \"allowed_tools\": [{tools_json}],\n"
        "  \"max_tool_calls\": 12,\n"
        "  \"max_tokens\": 8000\n"
        "}' | python3 {baseDir}/scripts/spawn_subagent.py\n"
        "```\n"
        "\n"
        "Available tool names (exact strings — case sensitive):\n"
        "\n"
        "* `Read` — read a file. Input: `{\"path\": \"/tmp_workspace/foo.csv\"}`.\n"
        "* `Write` — overwrite a file. Input: `{\"path\": ..., \"content\": ...}`.\n"
        "* `Edit` — single-match string replace. Input: `{\"path\": ..., \"old_string\": ..., \"new_string\": ...}`.\n"
        "* `Grep` — regex search in a file or directory. Input: `{\"pattern\": ..., \"path\": ...}`.\n"
        "* `Glob` — filename pattern search. Input: `{\"pattern\": \"**/*.xlsx\", \"path\": \"/tmp_workspace\"}`.\n"
        "* `Bash` — run a shell command. Input: `{\"command\": ..., \"timeout\": 30}`. Use this for API calls (curl), parsing (python3 -c), pdftotext, etc.\n"
        "\n"
        "Paths must live under `/tmp_workspace`, `/root`, or `/tmp` — anything else is rejected.\n"
        "\n"
        "## Spec fields\n"
        "\n"
        "| Field | Required | Notes |\n"
        "|-------|----------|-------|\n"
        "| `role` | yes | Short name describing the sub-agent's role. |\n"
        "| `instructions` | yes | One concrete task. Name the file paths / API endpoints the child should hit; do NOT paraphrase data already in your context — let the child fetch it fresh. |\n"
        "| `allowed_tools` | **strongly recommended** | List of tool names the child may use. Default: " + tools_line + ". Pass `[]` only for pure-synthesis sub-agents that need no data access. |\n"
        "| `context` | no | Short orienting prose (objective + constraints). Do NOT dump raw file contents here — the child should Read them itself. |\n"
        "| `model` | no | Override model. Default: inherit parent's model. |\n"
        "| `max_tool_calls` | no | Default 20, ceiling 50. Set to 0 only for text-only sub-agents. |\n"
        "| `max_tokens` | no | Default 32000. No upper cap. |\n"
        "| `timeout_seconds` | no | Default 300, ceiling 600. |\n"
        "\n"
        "## Anti-patterns (do NOT do these)\n"
        "\n"
        "* **Pasting raw data into `context` and passing `allowed_tools: []`** — the child "
        "will just rewrite what you handed it, often hallucinating fields. Give it tools "
        "and a path/query instead.\n"
        "* **`max_tool_calls: 0`** — same outcome: child cannot fetch anything, can only "
        "produce prose from `instructions`. Use 8-20 for normal fan-out.\n"
        "* **One sub-agent doing everything** — defeats the purpose. One angle per "
        "sub-agent.\n"
        "* **Sub-agents calling each other** — `spawn_subagent` is blocked inside the "
        "child; do not put it in `allowed_tools`.\n"
        "\n"
        "## Rules\n"
        "\n"
        "* Each spawn is independent — children do NOT see each other.\n"
        "* Children may NOT spawn further sub-agents.\n"
        "* Issue multiple spawns in parallel by calling this skill multiple times; results land in the order they complete.\n"
        "* The sub-agent's full transcript is at "
        f"`{TMP_WORKSPACE}/subagents/{{spawn_id}}.jsonl` if you need to audit it.\n"
    )


def _render_native_spawn_steering(multi_agent_config: dict | None) -> str:
    """Markdown steering block appended to AGENTS.md (the persona bootstrap).

    Skills do NOT surface in the openclaw system prompt, but AGENTS.md content
    does (verified 2026-06-25), so the fan-out directive lives here. References
    only tools this build actually registers — ``sessions_spawn`` to launch and
    ``sessions_list`` / ``sessions_history`` to collect (NO ``sessions_yield``,
    which does not exist in this build). Trigger checklist mirrors the proven
    legacy connector skill that reliably elicited fan-out.
    """
    return (
        "## Working style: fan out independent workstreams (native sub-agents)\n"
        "\n"
        "When a single turn bundles several **independent** workstreams, do NOT "
        "work through them yourself one by one. Decompose the turn and spawn one "
        "sub-agent per independent workstream **in parallel** using the built-in "
        "`sessions_spawn` tool, let each gather its own data and report back, then "
        "synthesize their results into the final deliverables yourself.\n"
        "\n"
        "Fan out (spawn sub-agents) at the START of the turn if ANY of these hold:\n"
        "\n"
        "1. The turn bundles several independent workstreams — one message asking "
        "you to *run the whole thing* / *sweep every surface and put it together*, "
        "or to (e.g.) draft quotes AND stand up a tracker AND reconcile the books "
        "AND stage a launch. One sub-agent per workstream.\n"
        "2. The prompt names 2+ independent sources or angles (e.g. *the workbook, "
        "the guide, AND the photo*). Each named angle = one sub-agent.\n"
        "3. The turn asks for a synthesized multi-section deliverable spanning "
        "several separate areas. Fan out to gather each area in parallel, then "
        "synthesize.\n"
        "\n"
        "How to fan out:\n"
        "\n"
        "1. Identify the independent workstreams (aim for one per deliverable or "
        "named source).\n"
        "2. Call `sessions_spawn` once per workstream, up front, in parallel. Give "
        "each a short `label` and a concrete, self-contained `task` naming the file "
        "paths / API endpoints to hit and exactly what to return. The child fetches "
        "its own data — point it at a path or query, do not paste raw data in.\n"
        "   Pass ONLY these parameters to `sessions_spawn`: `label`, `task`, "
        "`mode: \"run\"`, and `runtime: \"subagent\"`. Do NOT pass an `agentId` "
        "(or any other field): this build rejects `agentId` with "
        "`{\"status\": \"forbidden\", \"error\": \"agentId is not allowed\"}`, so a "
        "spawn that includes it never starts a child and the workstream is silently "
        "lost.\n"
        "3. Track the children with `sessions_list` and read their results with "
        "`sessions_history`; wait until they finish.\n"
        "4. Synthesize the children's results into the requested deliverables "
        "yourself, holding the same red lines you normally would.\n"
        "\n"
        "Do NOT fan out for a single tight question or one purely sequential task. "
        "Do NOT make one sub-agent do everything, and do NOT skip fan-out to do it "
        "all inline when the turn clearly bundles independent workstreams.\n"
    )


def configure_native_subagents(
    task_id: str,
    multi_agent_config: dict | None = None,
) -> None:
    """Enable OpenClaw's NATIVE sessions_spawn multi-agent path for a task.

    Unlike :func:`inject_subagent_tool` (which installs the custom
    spawn_subagent.py skill), this uses the binary's built-in
    ``sessions_spawn`` / ``sessions_yield`` tools.

    Config writes required for native spawning to actually work:

    1. ``agents.defaults.subagents.maxConcurrent`` (default 8) — fan-out width.

    1b. ``agents.defaults.subagents.maxChildrenPerAgent`` (set to 20) — the
       per-session active-children gate. OpenClaw's dist default is 5; left
       unset, wide fan-out is rejected mid-turn with ``forbidden: ... reached
       max active children for this session (N/5)``. 20 is the schema MAXIMUM
       (the validator rejects > 20 and aborts startup), so this raises the cap
       as far as openclaw allows.

    2. ``tools.alsoAllow`` listing the session tools. This is the critical one:
       the agent image ships ``tools.profile = "coding"`` (from
       ``@mariozechner/pi-coding-agent``), whose allowlist contains only
       read/write/edit/exec-style coding tools and does NOT include
       ``sessions_spawn`` / ``sessions_yield`` / ``subagents``. Without an
       additive grant those tools are filtered out of the callable set, so the
       model is never offered them and cannot spawn — verified empirically
       across JAE_002 run_1/run_2 (spawn_tree empty, zero sessions_spawn calls)
       on 2026-06-25. ``tools.alsoAllow`` is the schema-recognized additive path
       (``ToolPolicySchema`` accepts ``allow|alsoAllow|deny``; ``profile`` +
       ``alsoAllow`` is legal, ``allow`` + ``alsoAllow`` in one scope is not).

    ``spawnEnabled`` itself is already ON for the headless ``chat`` channel
    (``normalizeBoolean(undefined)`` is nullish, so the gate falls through to
    ``channel !== "discord"`` = true), so no spawn-flag key is written:
    ``session.threadBindings.spawnSubagentSessions`` is rejected by the config
    validator (verified 2026-06-25).

    The turn-marker file is still initialized so spawn/turn correlation works
    for the harvester. No-op-safe: failures are logged, not raised, so a config
    hiccup never aborts an otherwise-valid run.
    """
    cfg = multi_agent_config or {}
    max_concurrent = int(cfg.get("max_concurrent", 8))
    # Per-session active-children gate. OpenClaw enforces a SEPARATE limit from
    # maxConcurrent: `agents.defaults.subagents.maxChildrenPerAgent` (dist
    # default 5). When a session already has that many live children, further
    # sessions_spawn calls are rejected with `status: "forbidden" ... reached
    # max active children for this session (N/5)` — observed throttling fan-out
    # to 5 and forcing serial retries (Gabriela_Scott_01 run_1, 6/14 spawns
    # forbidden, 2026-06-26). We raise it to the SCHEMA MAXIMUM of 20 (the
    # openclaw config validator rejects anything > 20: "Too big: expected
    # number to be <=20", which aborts gateway/agent startup — Kevin_Harper_01
    # run_2, 2026-06-26). maxConcurrent still governs how many run at once.
    max_children = min(20, int(cfg.get("max_children", 20)))
    # Session tools the `coding` profile allowlist omits; granted additively so
    # the native sessions_spawn path is actually callable by the agent. NOTE:
    # this openclaw build registers sessions_spawn / sessions_list /
    # sessions_history / subagents / agents_list but NOT sessions_yield (verified
    # 2026-06-25: gateway warned `tools.allow allowlist contains unknown entries
    # (sessions_yield)`). Children are collected via sessions_list /
    # sessions_history, so sessions_yield is intentionally omitted.
    session_tools = [
        "sessions_spawn", "subagents", "agents_list",
        "sessions_list", "sessions_history", "sessions_send",
    ]
    script = (
        "import json, pathlib\n"
        "p = pathlib.Path('/root/.openclaw/openclaw.json')\n"
        "d = json.loads(p.read_text()) if p.exists() else {}\n"
        "defaults = d.setdefault('agents', {}).setdefault('defaults', {})\n"
        f"defaults.setdefault('subagents', {{}})['maxConcurrent'] = {max_concurrent}\n"
        # Lift the per-session active-children gate (dist default 5) so wide
        # fan-out is not rejected with `forbidden: max active children`.
        f"defaults.setdefault('subagents', {{}})['maxChildrenPerAgent'] = {max_children}\n"
        # Additively allow the native session tools on top of the `coding`
        # profile (profile + alsoAllow is the supported combination).
        "tools = d.setdefault('tools', {})\n"
        "also = tools.setdefault('alsoAllow', [])\n"
        f"for _t in {session_tools!r}:\n"
        "    if _t not in also:\n"
        "        also.append(_t)\n"
        # Guard the schema rule: alsoAllow cannot coexist with an inline allow
        # in the same scope. The image config uses `profile`, not `allow`, so we
        # only drop a stray `allow` if one was somehow written earlier.
        "if tools.get('allow'):\n"
        "    tools['allow'] = [t for t in tools['allow'] if t not in also]\n"
        "    if not tools['allow']:\n"
        "        tools.pop('allow', None)\n"
        "p.write_text(json.dumps(d, indent=2))\n"
    )
    r = subprocess.run(
        ["docker", "exec", "-i", task_id, "python3", "-"],
        input=script, capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning(
            "[%s] configure_native_subagents: config patch failed: %s",
            task_id, r.stderr.strip(),
        )

    # Initialize the turn marker + spawn ledger dir (harvester correlates native
    # child sessions to the turn that spawned them via this marker).
    init_cmd = (
        f"mkdir -p {TMP_WORKSPACE}/subagents && "
        f"touch {_SUBAGENT_SPAWN_TREE} && "
        f"printf 0 > {_SUBAGENT_TURN_MARKER}"
    )
    r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c", init_cmd],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning(
            "[%s] configure_native_subagents: marker init failed: %s",
            task_id, r.stderr.strip(),
        )

    # Steering: append the fan-out directive to the agent's bootstrap context.
    # Allowing the tool (above) only makes spawning POSSIBLE; the model still
    # needs to be TOLD to do it. Skills do NOT surface in the system prompt
    # (verified JAE_002 run_3: zero skill names in meta_info.system_prompt), but
    # the persona bootstrap MDs (AGENTS.md) DO — its content appears verbatim in
    # the system prompt. So the steering goes into AGENTS.md, the channel the
    # legacy connector skill effectively relied on. Appended to every AGENTS.md
    # openclaw might load (persona home + workspace cwd) for robustness.
    steering = _render_native_spawn_steering(cfg)
    with tempfile.TemporaryDirectory() as staging:
        steer_file = Path(staging) / "steer.md"
        steer_file.write_text("\n\n" + steering + "\n", encoding="utf-8")
        container_tmp = f"{TMP_WORKSPACE}/.wildclaw_spawn_steering.md"
        cp = subprocess.run(
            ["docker", "cp", str(steer_file), f"{task_id}:{container_tmp}"],
            capture_output=True, text=True,
        )
    if cp.returncode != 0:
        logger.warning(
            "[%s] configure_native_subagents: steering stage failed: %s",
            task_id, cp.stderr.strip(),
        )
    else:
        # Append to each AGENTS.md that exists (idempotent: skip if already added).
        append_cmd = (
            "MARK='<!-- wildclaw-native-spawn -->'; "
            f"for f in /root/AGENTS.md {TMP_WORKSPACE}/AGENTS.md; do "
            "  [ -f \"$f\" ] || continue; "
            "  grep -q \"$MARK\" \"$f\" && continue; "
            f"  printf '\\n%s\\n' \"$MARK\" >> \"$f\"; "
            f"  cat {container_tmp} >> \"$f\"; "
            "done"
        )
        r = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", append_cmd],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            logger.warning(
                "[%s] configure_native_subagents: AGENTS.md steering append failed: %s",
                task_id, r.stderr.strip(),
            )
        else:
            logger.info(
                "[%s] Native multi-agent armed: alsoAllow'd session tools + "
                "fan-out steering appended to AGENTS.md",
                task_id,
            )


def deny_native_subagents(task_id: str) -> None:
    """Explicitly deny the native session tools for a single-agent run.

    Belt-and-suspenders for --no-subagents: skipping
    :func:`configure_native_subagents` already withholds the tools (the
    ``coding`` profile allowlist omits them, verified zero spawns without the
    alsoAllow grant), but a deny entry also wins over any grant that might
    arrive from image config drift. Only tools this build registers are
    listed — same set configure_native_subagents grants. deny beats
    profile/allow/alsoAllow in OpenClaw's ToolPolicySchema resolution.
    No-op-safe: failure is logged, never raised.
    """
    session_tools = [
        "sessions_spawn", "subagents", "agents_list",
        "sessions_list", "sessions_history", "sessions_send",
    ]
    script = (
        "import json, pathlib\n"
        "p = pathlib.Path('/root/.openclaw/openclaw.json')\n"
        "d = json.loads(p.read_text()) if p.exists() else {}\n"
        "tools = d.setdefault('tools', {})\n"
        "deny = tools.setdefault('deny', [])\n"
        f"for _t in {session_tools!r}:\n"
        "    if _t not in deny:\n"
        "        deny.append(_t)\n"
        # Drop any stale grant from an earlier config write so allow/deny
        # never disagree about the same tools.
        "also = tools.get('alsoAllow')\n"
        "if also:\n"
        f"    tools['alsoAllow'] = [t for t in also if t not in {session_tools!r}]\n"
        "    if not tools['alsoAllow']:\n"
        "        tools.pop('alsoAllow', None)\n"
        "p.write_text(json.dumps(d, indent=2))\n"
    )
    r = subprocess.run(
        ["docker", "exec", "-i", task_id, "python3", "-"],
        input=script, capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning(
            "[%s] deny_native_subagents: config patch failed: %s",
            task_id, r.stderr.strip(),
        )
    else:
        logger.info("[%s] Session tools denied (sub-agent spawning disabled)", task_id)


def inject_subagent_tool(
    task_id: str,
    multi_agent_config: dict | None = None,
    *,
    subagent_director_src: str | None = None,
) -> None:
    """Install the spawn_subagent skill into the openclaw skill root.

    Mirrors the inject_api_connectors pattern: copies into the bundled root
    (symlinks rejected by openclaw's realpath check). Also initializes the
    empty spawn_tree.jsonl ledger and the turn-marker file used by the
    sub-agent script to correlate spawns to turns. No-op for backends other
    than openclaw; callers gate on AgentTaskSpec.multi_agent_enabled.
    """
    utils_dir = Path(__file__).resolve().parent
    if subagent_director_src is None:
        subagent_director_src = str(utils_dir / "subagent_director.py")
    src_path = Path(subagent_director_src)
    if not src_path.is_file():
        raise RuntimeError(
            f"inject_subagent_tool: subagent_director.py not found at {src_path}"
        )
    tools_src = utils_dir / "subagent_tools.py"
    if not tools_src.is_file():
        raise RuntimeError(
            f"inject_subagent_tool: subagent_tools.py not found at {tools_src}"
        )

    subprocess.run(
        ["docker", "exec", task_id, "rm", "-rf", _SUBAGENT_CONTAINER_ROOT],
        capture_output=True, text=True,
    )
    subprocess.run(
        ["docker", "exec", task_id, "mkdir", "-p", f"{_SUBAGENT_CONTAINER_ROOT}/scripts"],
        capture_output=True, text=True,
    )

    with tempfile.TemporaryDirectory() as staging:
        staging_path = Path(staging)
        skill_md = staging_path / "SKILL.md"
        skill_md.write_text(_render_subagent_skill_md(multi_agent_config), encoding="utf-8")
        scripts_dir = staging_path / "scripts"
        scripts_dir.mkdir()
        entry = scripts_dir / "spawn_subagent.py"
        entry.write_bytes(src_path.read_bytes())
        tools_entry = scripts_dir / "subagent_tools.py"
        tools_entry.write_bytes(tools_src.read_bytes())

        for src_file, container_dst in (
            (skill_md, f"{_SUBAGENT_CONTAINER_ROOT}/SKILL.md"),
            (entry, f"{_SUBAGENT_CONTAINER_ROOT}/scripts/spawn_subagent.py"),
            (tools_entry, f"{_SUBAGENT_CONTAINER_ROOT}/scripts/subagent_tools.py"),
        ):
            r = subprocess.run(
                ["docker", "cp", str(src_file), f"{task_id}:{container_dst}"],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                raise RuntimeError(
                    f"inject_subagent_tool: docker cp failed for {container_dst}: {r.stderr.strip()}"
                )

    subprocess.run(
        ["docker", "exec", task_id, "chmod", "+x",
         f"{_SUBAGENT_CONTAINER_ROOT}/scripts/spawn_subagent.py"],
        capture_output=True, text=True,
    )

    init_cmd = (
        f"mkdir -p {TMP_WORKSPACE}/subagents && "
        f"touch {_SUBAGENT_SPAWN_TREE} && "
        f"printf 0 > {_SUBAGENT_TURN_MARKER}"
    )
    r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c", init_cmd],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning(
            "[%s] subagent ledger init failed: %s", task_id, r.stderr.strip()
        )

    logger.info("[%s] Injected spawn_subagent skill into %s", task_id, _SUBAGENT_CONTAINER_ROOT)


def write_turn_marker(task_id: str, turn_index: int) -> None:
    """Write the current 0-indexed turn into the in-container marker file.

    Called between turns by the openclaw runner so that sub-agent spawns
    landing in the next turn carry the right turn_index in spawn_tree.jsonl.
    """
    r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c",
         f"printf {int(turn_index)} > {_SUBAGENT_TURN_MARKER}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.warning(
            "[%s] turn marker write failed for turn %s: %s",
            task_id, turn_index, r.stderr.strip(),
        )


def run_warmup(
    task_id: str,
    warmup: str,
    *,
    detach_background: bool = False,
) -> None:
    """Execute warmup bash commands line by line inside the container (skip blank lines and comments)."""
    if not warmup.strip():
        return
    commands = [
        line.strip()
        for line in warmup.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not commands:
        return

    logger.info("[%s] Running warmup (%d commands)", task_id, len(commands))
    for idx, cmd in enumerate(commands, start=1):
        logger.info("[%s] warmup: %s", task_id, cmd)
        stripped_cmd = cmd.rstrip()
        if detach_background and stripped_cmd.endswith("&"):
            background_cmd = stripped_cmd[:-1].strip()
            log_path = f"/tmp/wildclaw_warmup_{idx}.log"
            wrapped = (
                f"cd {TMP_WORKSPACE} && "
                f"nohup /bin/bash -lc {shlex.quote(background_cmd)} "
                f"> {shlex.quote(log_path)} 2>&1 < /dev/null &"
            )
            r = subprocess.run(
                ["docker", "exec", task_id, "/bin/bash", "-lc", wrapped],
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                raise RuntimeError(
                    f"Warmup background command failed: {cmd!r}\n{r.stderr}"
                )
            continue

        r = subprocess.run(
            ["docker", "exec", task_id, "/bin/bash", "-c", cmd],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Warmup command failed: {cmd!r}\n{r.stderr}")


def run_background(task_id: str, bash_cmd: str, log_path: Path) -> subprocess.Popen:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        ["docker", "exec", task_id, "/bin/bash", "-c",
         f"cd {TMP_WORKSPACE} && {bash_cmd}"],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
    )
    proc._log_file = log_file
    logger.info("[%s] Started process PID=%s → %s", task_id, proc.pid, log_path)
    return proc


def close_proc_log(proc: subprocess.Popen) -> None:
    """Close the log file handle created by run_background."""
    log_file = getattr(proc, "_log_file", None)
    if log_file and not log_file.closed:
        log_file.close()


_ROOT_DELIVERABLE_EXTENSIONS = (
    ".csv", ".tsv", ".json", ".yaml", ".yml", ".md", ".txt", ".jsonl",
    ".html", ".xml", ".pdf", ".png", ".jpg", ".jpeg", ".svg",
    ".py", ".js", ".ts", ".sql", ".sh",
)


def _sweep_root_deliverables_to_workspace(task_id: str) -> None:
    sweep_cmd = "python3 - <<'PY'\n" + "\n".join([
        "import os, shutil",
        f"exts = {_ROOT_DELIVERABLE_EXTENSIONS!r}",
        f"workspace = {TMP_WORKSPACE!r}",
        "os.makedirs(workspace, exist_ok=True)",
        "moved = []",
        "skipped = {'AGENT.md','AGENTS.md','MEMORY.md','SOUL.md','USER.md',",
        "           'IDENTITY.md','HEARTBEAT.md','TOOLS.md','API_DOCUMENTATION.md'}",
        "for name in os.listdir('/root'):",
        "    src = os.path.join('/root', name)",
        "    if not os.path.isfile(src):",
        "        continue",
        "    if name.startswith('.') or name in skipped:",
        "        continue",
        "    if not name.lower().endswith(exts):",
        "        continue",
        "    dst = os.path.join(workspace, name)",
        "    if os.path.exists(dst):",
        "        continue",
        "    try:",
        "        shutil.copy2(src, dst)",
        "        moved.append(name)",
        "    except OSError:",
        "        pass",
        "if moved: print('swept:', ','.join(moved))",
        "PY",
    ])
    r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c", sweep_cmd],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0 and r.stdout.strip().startswith("swept:"):
        logger.info("[%s] Recovered /root deliverables: %s", task_id, r.stdout.strip())


def collect_output_from_container(
    task_id: str,
    output_dir: Path,
    *,
    include_workspace_changes: bool = False,
) -> None:
    """Collect task output files from the container to output_dir/task_output/.

    Collection strategy:
      0. Sweep deliverable-shaped files an agent left at /root/ (top-level)
         into /tmp_workspace/.
      1. All files under /tmp/openclaw/ (agent session logs, etc.)
      2. The full /tmp_workspace/ tree (into workspace_full/) — forensic copy
         including staged inputs, persona files, agent scratch, and deliverables.
      3. artifacts/ — agent-produced files only, computed by diffing the
         current workspace against the baseline snapshot taken right before
         the agent ran. This is the canonical place to look for what the
         model produced. If no baseline was taken (legacy backends), this
         dir is silently skipped and workspace_full/ remains the source.
    """
    task_output_dir = output_dir / "task_output"
    task_output_dir.mkdir(parents=True, exist_ok=True)

    _copy_dir_from_container(task_id, "/tmp/openclaw/.", str(task_output_dir))

    # Native multi-agent: collect the OpenClaw session store so the parent
    # session AND every native sessions_spawn child session survive teardown.
    # Children live at /root/.openclaw/agents/main/sessions/<session-key>.jsonl;
    # without this they are lost when the container is removed. jsonl_reader.
    # read_sessions_grouped consumes this dir to split parent from children.
    sessions_out = task_output_dir / "sessions"
    sessions_out.mkdir(parents=True, exist_ok=True)
    if not _copy_dir_from_container(
        task_id, "/root/.openclaw/agents/main/sessions/.", str(sessions_out)
    ):
        logger.debug("[%s] no native session store to collect", task_id)

    _sweep_root_deliverables_to_workspace(task_id)

    if include_workspace_changes:
        workspace_out = task_output_dir / "workspace"
        workspace_out.mkdir(parents=True, exist_ok=True)
        ok = _copy_dir_from_container(task_id, f"{TMP_WORKSPACE}/.", str(workspace_out))
        if not ok:
            logger.warning("[%s] workspace directory does not exist or is empty", task_id)
        return

    full_out = task_output_dir / "workspace_full"
    full_out.mkdir(parents=True, exist_ok=True)
    if not _copy_dir_from_container(task_id, f"{TMP_WORKSPACE}/.", str(full_out)):
        logger.debug("[%s] full workspace sweep found nothing to collect", task_id)

    artifacts_out = task_output_dir / "artifacts"
    artifacts_out.mkdir(parents=True, exist_ok=True)
    _copy_changed_workspace_outputs_from_container(task_id, artifacts_out)


def snapshot_workspace_state(task_id: str) -> None:
    snapshot_cmd = "python3 - <<'PY'\n" + "\n".join([
        "import json",
        "from pathlib import Path",
        f"root = Path({TMP_WORKSPACE!r})",
        f"snapshot_path = Path({WORKSPACE_BASELINE_PATH!r})",
        "files = {}",
        "if root.exists():",
        "    for path in root.rglob('*'):",
        "        if not (path.is_file() or path.is_symlink()):",
        "            continue",
        "        try:",
        "            stat = path.lstat()",
        "        except OSError:",
        "            continue",
        "        rel = path.relative_to(root).as_posix()",
        "        files[rel] = {",
        "            'size': stat.st_size,",
        "            'mtime_ns': stat.st_mtime_ns,",
        "            'is_symlink': path.is_symlink(),",
        "        }",
        "snapshot_path.write_text(json.dumps(files, sort_keys=True), encoding='utf-8')",
        "PY",
    ])
    r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c", snapshot_cmd],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Workspace baseline snapshot failed:\n{r.stderr}")
    logger.info("[%s] Workspace baseline saved at %s", task_id, WORKSPACE_BASELINE_PATH)


def _copy_changed_workspace_outputs_from_container(task_id: str, dest: Path) -> None:
    list_cmd = "python3 - <<'PY'\n" + "\n".join([
        "import json",
        "from pathlib import Path",
        f"root = Path({TMP_WORKSPACE!r})",
        f"snapshot_path = Path({WORKSPACE_BASELINE_PATH!r})",
        "if not snapshot_path.exists():",
        "    print(json.dumps([]))",
        "    raise SystemExit(0)",
        "before = json.loads(snapshot_path.read_text(encoding='utf-8'))",
        "excluded_prefixes = (",
        "    'results/', 'gt/', 'tmp/', '.git/',",
        "    'node_modules/', '.venv/', 'venv/', '__pycache__/', '.cache/',",
        ")",
        "excluded_names = {'results', 'gt', 'tmp', '.git', 'node_modules', '.venv', 'venv', '__pycache__', '.cache'}",
        "changed = []",
        "if root.exists():",
        "    for path in root.rglob('*'):",
        "        if not (path.is_file() or path.is_symlink()):",
        "            continue",
        "        rel = path.relative_to(root).as_posix()",
        "        if rel in excluded_names or rel.startswith(excluded_prefixes):",
        "            continue",
        "        try:",
        "            stat = path.lstat()",
        "        except OSError:",
        "            continue",
        "        current = {",
        "            'size': stat.st_size,",
        "            'mtime_ns': stat.st_mtime_ns,",
        "            'is_symlink': path.is_symlink(),",
        "        }",
        "        if before.get(rel) != current:",
        "            changed.append(rel)",
        "print(json.dumps(sorted(changed)))",
        "PY",
    ])
    r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c", list_cmd],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        logger.warning("[%s] Failed to list changed workspace outputs: %s", task_id, r.stderr.strip())
        return

    try:
        changed_paths = json.loads(r.stdout.strip() or "[]")
    except json.JSONDecodeError:
        logger.warning("[%s] Failed to parse changed workspace output list: %s", task_id, r.stdout[:200])
        return

    for rel_path in changed_paths:
        if not isinstance(rel_path, str) or rel_path.startswith("/") or ".." in Path(rel_path).parts:
            continue
        dest_path = dest / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        _copy_file_from_container(task_id, f"{TMP_WORKSPACE}/{rel_path}", dest_path)


def inject_lobster_workspace(task_id: str, workspace_path: str) -> None:
    """Copy the entire lobster workspace into /root/ (the OpenClaw workspace in the image).

    This brings in everything: SOUL.md, USER.md, MEMORY.md, memory/, skills/, etc.
    """
    r = subprocess.run(
        ["docker", "cp", f"{workspace_path}/.", f"{task_id}:/root/"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.error("[%s] Lobster workspace copy failed: %s", task_id, r.stderr)
        return
    logger.info("[%s] Lobster workspace copied: %s → /root/", task_id, workspace_path)

    ls_r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c",
         "ls -1 /root/*.md 2>/dev/null | xargs -n1 basename 2>/dev/null | sort"],
        capture_output=True, text=True,
    )
    if ls_r.returncode == 0 and ls_r.stdout.strip():
        md_files = [name for name in ls_r.stdout.strip().splitlines() if name]
        logger.info("[%s] Persona MDs landed at /root/: %s", task_id, md_files)
    else:
        logger.warning("[%s] Persona MD copy succeeded but /root/ contains no *.md", task_id)


def inject_persona_into_workspace(task_id: str, persona_dir: str) -> None:
    """Copy the task persona into the agent workspace (TMP_WORKSPACE).

    OpenClaw assembles AGENTS/SOUL/MEMORY context from the workspace, not /root
    (where inject_lobster_workspace puts it). MUST run AFTER setup_workspace so
    the persona OVERWRITES the image's stock scaffold that cp -r /app/. lays down.
    """
    r = subprocess.run(
        ["docker", "cp", f"{persona_dir}/.", f"{task_id}:{TMP_WORKSPACE}/"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.error("[%s] Persona→workspace copy failed: %s", task_id, r.stderr)
        return
    logger.info("[%s] Persona copied: %s → %s/", task_id, persona_dir, TMP_WORKSPACE)

    ls_r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c",
         f"ls -1 {TMP_WORKSPACE}/*.md 2>/dev/null | xargs -n1 basename 2>/dev/null | sort"],
        capture_output=True, text=True,
    )
    if ls_r.returncode == 0 and ls_r.stdout.strip():
        md_files = [name for name in ls_r.stdout.strip().splitlines() if name]
        logger.info("[%s] Persona MDs landed in workspace: %s", task_id, md_files)
    else:
        logger.warning(
            "[%s] Persona→workspace copy succeeded but %s contains no *.md",
            task_id, TMP_WORKSPACE,
        )


def inject_data_into_workspace(task_id: str, data_dir: str) -> None:
    """Stage legacy `data/` input artifacts at /root/workspace/home.

    Pre-23b0fc7 tasks ship their input documents in `<task>/data/` rather than
    `persona/home/`. `inject_persona_into_workspace` only surfaces `persona/`,
    so without this the agent never receives those documents (multimodal tasks
    then run against an empty workspace). Mirrors the persona injection but
    targets `TMP_WORKSPACE/home` (== /root/workspace/home, the path the workspace
    hint promises the agent). MUST run AFTER setup_workspace + the persona inject
    so it lands on top of the bootstrapped workspace. Best-effort: a failure is
    logged, never raised. Only invoked when the task loader set `data_dir` (i.e.
    the task ships input documents in <task>/data/)."""
    home = f"{TMP_WORKSPACE}/home"
    mk = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c", f"mkdir -p {home}"],
        capture_output=True, text=True,
    )
    if mk.returncode != 0:
        logger.error("[%s] data→workspace mkdir failed: %s", task_id, mk.stderr)
        return
    r = subprocess.run(
        ["docker", "cp", f"{data_dir}/.", f"{task_id}:{home}/"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        logger.error("[%s] data→workspace copy failed: %s", task_id, r.stderr)
        return
    count_r = subprocess.run(
        ["docker", "exec", task_id, "/bin/bash", "-c",
         f"find {home} -type f 2>/dev/null | wc -l"],
        capture_output=True, text=True,
    )
    n = (count_r.stdout or "").strip() or "?"
    logger.info("[%s] Legacy data/ staged into workspace: %s → %s/ (%s files)",
                task_id, data_dir, home, n)


def _copy_dir_from_container(task_id: str, src: str, dest: str) -> bool:
    r = subprocess.run(
        ["docker", "cp", f"{task_id}:{src}", dest],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        logger.info("[%s] Collected container directory %s → %s", task_id, src, dest)
        return True
    return False


def _copy_file_from_container(task_id: str, src: str, dest: Path) -> bool:
    r = subprocess.run(
        ["docker", "cp", f"{task_id}:{src}", str(dest)],
        capture_output=True,
        text=True,
    )
    if r.returncode == 0:
        logger.info("[%s] Collected container file %s → %s", task_id, src, dest)
        return True
    logger.warning("[%s] Container file copy failed (%s): %s", task_id, src, r.stderr.strip())
    return False


def snapshot_persona_and_data_from_container(
    task_id: str,
    persona_entries: "list[str]",
    data_rel_paths: "list[str]",
    dest_dir: Path,
) -> dict:
    """Copy the FINAL state of the persona/ and data/ folders out of the running
    agent container into ``dest_dir/{persona,data}/``.

    Used to build the post-run ``workspace_after`` snapshot. ``persona_entries``
    are the top-level names the task's persona dir shipped (copied into ``/root/``
    by ``inject_lobster_workspace``); ``data_rel_paths`` are the staged data
    attachment ``storedAs`` rel paths (under ``TMP_WORKSPACE``). Best-effort: a
    missing/edited/deleted file is skipped, not fatal. Must be called BEFORE the
    agent container is removed.
    """
    persona_dest = dest_dir / "persona"
    data_dest = dest_dir / "data"
    persona_dest.mkdir(parents=True, exist_ok=True)
    data_dest.mkdir(parents=True, exist_ok=True)
    n_persona = 0
    for name in persona_entries:
        if not name or name.startswith("/") or ".." in Path(name).parts:
            continue
        # Persona files live at /root/ in the container (some are dirs: memory/, skills/).
        if _copy_dir_from_container(task_id, f"/root/{name}", str(persona_dest)):
            n_persona += 1
    # Capture the FULL final workspace tree — not just the originally-staged
    # attachment manifest. The agent writes its deliverables (draft .eml, logs,
    # agendas, updated sheets) under /root/workspace -> TMP_WORKSPACE; replaying
    # only the input manifest produced an after-snapshot byte-identical to
    # before, losing every agent artifact (IAN report Pointer 4). `docker cp
    # <c>:/tmp_workspace/. dest` copies the whole tree (original + produced).
    n_data = 0
    if _copy_dir_from_container(task_id, f"{TMP_WORKSPACE}/.", str(data_dest)):
        try:
            n_data = sum(1 for p in data_dest.rglob("*") if p.is_file())
        except OSError:
            n_data = -1
    else:
        # Fallback: per-file copy of the declared attachments if the full-tree
        # copy failed (e.g. workspace is a symlink the daemon won't follow).
        for rel in data_rel_paths:
            if not rel or rel.startswith("/") or ".." in Path(rel).parts:
                continue
            dst = data_dest / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if _copy_file_from_container(task_id, f"{TMP_WORKSPACE}/{rel}", dst):
                n_data += 1
    logger.info("[%s] workspace_after: collected %d persona entr(ies), %d data file(s)",
                task_id, n_persona, n_data)
    return {"persona": n_persona, "data": n_data}
