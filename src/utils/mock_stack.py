from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

logger = logging.getLogger(__name__)

MOCK_IMAGE = "kensei3-mocks:v1"


def read_api_ports(env_dir: Path) -> dict[str, int]:
    ports: dict[str, int] = {}
    if not env_dir.is_dir():
        return ports
    for entry in sorted(env_dir.iterdir()):
        if not entry.is_dir():
            continue
        toml_path = entry / "service.toml"
        if not toml_path.is_file():
            continue
        port = _extract_port(toml_path)
        if port is not None:
            ports[entry.name] = port
    return ports


def _extract_port(path: Path) -> int | None:
    in_service = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_service = line == "[service]"
            continue
        if not in_service or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == "port":
            v = v.strip().strip('"').strip("'")
            try:
                return int(v)
            except ValueError:
                return None
    return None


def _generate_supervisord_conf(api_ports: dict[str, int]) -> str:
    lines = [
        "[supervisord]",
        "nodaemon=true",
        "logfile=/tmp/supervisord.log",
        "logfile_maxbytes=0",
        "",
    ]
    for name, port in sorted(api_ports.items()):
        lines.extend([
            f"[program:{name}]",
            f"command=uvicorn server:app --host 0.0.0.0 --port {port}",
            "environment=PYTHONPATH=\"/opt/mocks\"",
            f"directory=/opt/mocks/{name}",
            "autorestart=true",
            "startsecs=3",
            "startretries=3",
            f"stdout_logfile=/tmp/{name}.log",
            f"stderr_logfile=/tmp/{name}.err",
            "",
        ])
    return "\n".join(lines)


def _generate_healthcheck_sh(api_ports: dict[str, int]) -> str:
    ports = " ".join(str(p) for p in sorted(api_ports.values()))
    return (
        "#!/bin/bash\n"
        "set -e\n"
        f"for port in {ports}; do\n"
        "  curl -sf --max-time 2 http://localhost:$port/health >/dev/null || exit 1\n"
        "done\n"
    )


def _generate_dockerfile(api_dirs: list[str]) -> str:
    return """\
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl procps \\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir supervisor fastapi uvicorn flask pydantic
COPY env_dir/ /opt/mocks/
RUN set -e; for f in /opt/mocks/*/requirements.txt; do \\
        pip install --no-cache-dir -r "$f" 2>&1 | tail -3 || \\
        echo "warn: $f had failures"; \\
    done
COPY supervisord.conf /etc/supervisor.conf
COPY healthcheck.sh /healthcheck.sh
RUN chmod +x /healthcheck.sh
ENV PYTHONPATH=/opt/mocks
HEALTHCHECK --interval=15s --timeout=10s --retries=10 --start-period=60s \\
    CMD /healthcheck.sh
CMD ["supervisord", "-c", "/etc/supervisor.conf", "-n"]
"""


def build_mock_image_if_needed(env_dir: Path, image: str = MOCK_IMAGE,
                               force: bool = False) -> bool:
    # Opt-in rebuild: the cached image otherwise serves whatever mock server
    # code / baseline CSVs existed when it was first built, so edits under
    # environment/ are silently ignored until the tag is removed. force=True
    # (or KENSEI_MOCK_REBUILD=1) rebuilds; default stays cached (no behavior
    # change). Per-task data does NOT need this — it is bind-mounted at runtime.
    force = force or os.environ.get("KENSEI_MOCK_REBUILD", "").strip().lower() in ("1", "true", "yes")
    if force:
        logger.info("Force-rebuilding mock image %s (removing cached tag)", image)
        subprocess.run(["docker", "rmi", "-f", image], capture_output=True)
    else:
        r = subprocess.run(
            ["docker", "image", "inspect", image],
            capture_output=True,
        )
        if r.returncode == 0:
            logger.info("Mock image %s already built", image)
            return True

    env_dir = Path(env_dir)
    if not env_dir.is_dir():
        logger.warning("Cannot build mock image: env_dir %s missing", env_dir)
        return False

    api_ports = read_api_ports(env_dir)
    if not api_ports:
        logger.warning("Cannot build mock image: no mock APIs found in %s", env_dir)
        return False

    api_dirs = sorted(api_ports.keys())
    logger.info("Building mock image %s with %d APIs (~5-10 min)", image, len(api_dirs))

    with tempfile.TemporaryDirectory(prefix="kensei3-mocks-build-") as tmpdir:
        tmp = Path(tmpdir)
        shutil.copytree(env_dir, tmp / "env_dir", symlinks=False, dirs_exist_ok=True)
        (tmp / "Dockerfile").write_text(_generate_dockerfile(api_dirs), encoding="utf-8")
        (tmp / "supervisord.conf").write_text(
            _generate_supervisord_conf(api_ports), encoding="utf-8"
        )
        (tmp / "healthcheck.sh").write_text(
            _generate_healthcheck_sh(api_ports), encoding="utf-8"
        )
        r = subprocess.run(
            ["docker", "build", "-t", image, "."],
            cwd=str(tmp),
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            logger.error("docker build failed:\n%s", r.stderr[-2000:])
            return False
    logger.info("Mock image %s built", image)
    return True


def start_mock_stack(container_name: str, network: str,
                     image: str = MOCK_IMAGE,
                     overlays: dict | None = None) -> None:
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
    mount_args: list[str] = []
    for api_name, files in (overlays or {}).items():
        if not isinstance(files, dict):
            continue
        for filename, host_path in files.items():
            container_path = f"/opt/mocks/{api_name}/{filename}"
            mount_args += ["-v", f"{host_path}:{container_path}:ro"]
            logger.info("[%s] overlay %s/%s -> %s",
                        container_name, api_name, filename, host_path)
    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "--network", network,
        *mount_args,
        image,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"mock-stack start failed:\n{r.stderr}")
    logger.info("[%s] mock-stack container started", container_name)


def wait_for_mock_stack_healthy(container_name: str, timeout: float = 120.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}",
             container_name],
            capture_output=True, text=True,
        )
        status = (r.stdout or "").strip()
        if status == "healthy":
            logger.info("[%s] mock-stack healthy", container_name)
            return True
        if status in ("unhealthy",):
            logger.warning("[%s] mock-stack unhealthy", container_name)
            return False
        time.sleep(3)
    logger.warning("[%s] mock-stack did not reach healthy within %.0fs",
                   container_name, timeout)
    return False


def wait_for_ports_healthy(container_name: str, ports: list[int],
                           timeout: float = 120.0) -> bool:
    """Readiness for ONLY the given ports inside the container (via exec+curl).

    Used by the per-task mock stack: a task that overlays one API
    (e.g. google-classroom-api:8002) must not wait on the image's baked-in
    HEALTHCHECK, which probes ALL ~101 ports and may never go green when 100
    unrelated uvicorn workers are still booting / contending for CPU. We only
    need the task's own API(s) up.
    """
    if not ports:
        return True
    deadline = time.time() + timeout
    port_args = " ".join(str(p) for p in ports)
    check = (
        f"for port in {port_args}; do "
        f"curl -sf --max-time 2 http://localhost:$port/health >/dev/null || exit 1; "
        f"done"
    )
    last_err = ""
    while time.time() < deadline:
        r = subprocess.run(
            ["docker", "exec", container_name, "/bin/bash", "-c", check],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            logger.info("[%s] target ports healthy: %s", container_name, port_args)
            return True
        last_err = (r.stderr or "").strip()
        time.sleep(2)
    logger.warning("[%s] target ports %s not healthy within %.0fs (last: %s)",
                   container_name, port_args, timeout, last_err[:200])
    return False


def stop_mock_stack(container_name: str) -> None:
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
