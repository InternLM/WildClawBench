from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import logging
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

logger = logging.getLogger(__name__)

MOCK_IMAGE = "kensei3-mocks:v1"

_CONTENT_HASH_LABEL = "kensei3.content_hash"

# Bump whenever the image's build recipe (Dockerfile / entrypoint / supervisord
# generation / healthcheck) changes so cached images rebuild even when the
# environment/ contents are byte-identical. _compute_mock_content_hash folds
# this in, so a recipe change shifts the content hash and invalidates the cache.
_BUILDER_VERSION = "rt-filter-1"


def _compute_mock_content_hash(env_dir: Path) -> str:
    # b54 Issue 9: tag-only cache check let stale images keep running after
    # environment/ edits. Manifest is (relpath, size, mtime) over every file
    # under env_dir; mtime included because byte-for-byte content read would
    # take seconds on 101 dirs. mtime is sufficient because docker build is
    # the only writer to the cached image and any environment/ edit bumps it.
    h = hashlib.sha256()
    env_dir = Path(env_dir)
    if not env_dir.is_dir():
        return ""
    manifest: list[tuple[str, int, int]] = []
    for path in sorted(env_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            st = path.stat()
        except OSError:
            continue
        rel = path.relative_to(env_dir).as_posix()
        manifest.append((rel, int(st.st_size), int(st.st_mtime)))
    h.update(json.dumps(manifest, sort_keys=True).encode("utf-8"))
    h.update(_BUILDER_VERSION.encode("utf-8"))
    return h.hexdigest()[:16]


def _image_content_hash(image: str) -> str:
    r = subprocess.run(
        ["docker", "image", "inspect", image, "--format",
         "{{ index .Config.Labels \"" + _CONTENT_HASH_LABEL + "\" }}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return ""
    return (r.stdout or "").strip()


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


def _generate_ports_manifest(api_ports: dict[str, int]) -> str:
    """Full {api_name: port} map baked into the image. The entrypoint reads this
    plus MOCK_ENABLED_APIS at container start to decide which services to run."""
    return json.dumps({k: int(v) for k, v in sorted(api_ports.items())}, indent=2)


# Generates /tmp/supervisord.conf and /tmp/mock_enabled_ports at CONTAINER START
# from the baked manifest, honoring the MOCK_ENABLED_APIS env var. This is what
# makes the same cached image run only a task's required+distractor APIs instead
# of all ~101: pass MOCK_ENABLED_APIS=a-api,b-api to start_mock_stack. Empty /
# unset MOCK_ENABLED_APIS => run everything (back-compat). A filter that selects
# nothing falls back to all, so a typo never yields a dead, empty stack.
_GEN_SUPERVISORD_PY = r'''import json, os

with open("/opt/mock_ports.json") as f:
    ports = json.load(f)

raw = (os.environ.get("MOCK_ENABLED_APIS") or "").strip()
if raw:
    wanted = {n.strip() for n in raw.split(",") if n.strip()}
    selected = {n: p for n, p in ports.items() if n in wanted}
    if not selected:
        selected = ports
else:
    selected = ports

lines = [
    "[supervisord]",
    "nodaemon=true",
    "logfile=/tmp/supervisord.log",
    "logfile_maxbytes=0",
    "",
]
for name, port in sorted(selected.items()):
    lines += [
        "[program:%s]" % name,
        "command=uvicorn server:app --host 0.0.0.0 --port %d" % int(port),
        'environment=PYTHONPATH="/opt/mocks"',
        "directory=/opt/mocks/%s" % name,
        "autorestart=true",
        "startsecs=3",
        "startretries=3",
        "stdout_logfile=/tmp/%s.log" % name,
        "stderr_logfile=/tmp/%s.err" % name,
        "",
    ]
with open("/tmp/supervisord.conf", "w") as f:
    f.write("\n".join(lines))
with open("/tmp/mock_enabled_ports", "w") as f:
    f.write(" ".join(str(int(p)) for p in sorted(selected.values())))
print("mock-stack: running %d/%d APIs" % (len(selected), len(ports)))
'''

_START_SH = """#!/bin/bash
set -e
python3 /opt/gen_supervisord.py
exec supervisord -c /tmp/supervisord.conf -n
"""

# Healthcheck probes ONLY the ports the entrypoint actually started (written to
# /tmp/mock_enabled_ports), not the full baked catalog. Probing all ~101 would
# never go green when a task only runs a handful of services.
_HEALTHCHECK_SH = """#!/bin/bash
set -e
PORTS=$(cat /tmp/mock_enabled_ports 2>/dev/null || true)
[ -z "$PORTS" ] && exit 1
for port in $PORTS; do
  curl -sf --max-time 2 http://localhost:$port/health >/dev/null || exit 1
done
"""


def _generate_dockerfile(api_dirs: list[str]) -> str:
    # BUG-S-001 non-root runtime: create the `app` system user EARLY (idempotent,
    # depends on no later state), do all root-only work (apt install, pip
    # install into /usr/local site-packages, chmod scripts) BEFORE the USER
    # switch, then chown the writable trees (/opt) right before flipping
    # USER app. supervisord here drives the 101 FastAPI services bound to
    # non-privileged ports 8000+ — no CAP_NET_BIND_SERVICE required. The
    # mirror of the per-API Dockerfile S-001 hardening; CVSS 8.4 / CWE-250.
    #
    # BUG-S-002 base image pinned by @sha256: digest (CVSS 8.0 / CWE-829). The
    # digest below is python:3.11-slim resolved 2026-06-10 from docker.io. Do
    # NOT remove the @sha256: suffix — without it the build is vulnerable to
    # tag-mutation supply-chain attacks (a malicious publisher pushing a
    # backdoored layer under the same tag). To refresh the digest after an
    # upstream release: `docker pull python:3.11-slim && docker inspect
    # python:3.11-slim --format '{{index .RepoDigests 0}}'` and replace the
    # suffix here AND in every environment/*-api/Dockerfile. Per-API surface
    # currently uses python:3.12-slim@sha256:090ba77...; the version mismatch
    # is a separate tracking item, but both surfaces MUST stay digest-pinned.
    #
    # BUG-S-003 hash-pinned per-service install (CVSS 7.7 / CWE-1357). The
    # runtime per-service install loop reads requirements-locked.txt (NOT the
    # human-edited requirements.txt) and passes --require-hashes so any wheel
    # whose sha256 does not match the lockfile is rejected. This is the
    # parallel of the per-API Dockerfile S-003 hardening; lockfiles live at
    # environment/<api>/requirements-locked.txt and are regenerated via
    # `pip-compile --generate-hashes` inside the digest-pinned base image
    # (see audit/BUGS.md BUG-S-003 for the full refresh recipe).
    return """\
FROM python:3.11-slim@sha256:a3ab0b966bc4e91546a033e22093cb840908979487a9fc0e6e38295747e49ac0
RUN groupadd -r app && useradd -r -g app -d /opt/mocks -s /usr/sbin/nologin app
RUN apt-get update && apt-get install -y --no-install-recommends curl procps \\
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir supervisor fastapi uvicorn flask pydantic
COPY env_dir/ /opt/mocks/
RUN set -e; for f in /opt/mocks/*/requirements-locked.txt; do \\
        pip install --no-cache-dir --require-hashes -r "$f" 2>&1 | tail -3 || \\
        echo "warn: $f had failures"; \\
    done
COPY mock_ports.json /opt/mock_ports.json
COPY gen_supervisord.py /opt/gen_supervisord.py
COPY start.sh /start.sh
COPY healthcheck.sh /healthcheck.sh
RUN chmod +x /start.sh /healthcheck.sh
RUN chown -R app:app /opt/mocks /opt/mock_ports.json /opt/gen_supervisord.py
ENV PYTHONPATH=/opt/mocks
HEALTHCHECK --interval=15s --timeout=10s --retries=10 --start-period=60s \\
    CMD /healthcheck.sh
USER app
CMD ["/start.sh"]
"""


@contextlib.contextmanager
def _mock_build_lock():
    """Serialize concurrent mock-image builds ACROSS processes (flock).

    Under `xargs -P N`, several run.sh / run_batch processes can find the image
    stale at the same instant and all launch `docker build kensei3-mocks:v1`
    simultaneously — wasting 5-10 min each and racing on the shared tag. An
    exclusive cross-process file lock makes them build one-at-a-time; the
    staleness re-check inside the locked body (docker image inspect + content
    hash) then turns every waiter after the first into a no-op. Best-effort: if
    flock is unavailable (non-POSIX), proceed without locking.
    """
    lock_path = Path(tempfile.gettempdir()) / "kensei3-mocks-build.lock"
    try:
        lf = open(lock_path, "w")  # noqa: SIM115
    except OSError:
        yield
        return
    try:
        fcntl.flock(lf, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(lf, fcntl.LOCK_UN)
        finally:
            lf.close()


def build_mock_image_if_needed(env_dir: Path, image: str = MOCK_IMAGE,
                               force: bool = False) -> bool:
    # Cross-process build serialization: only one builder at a time. The locked
    # body re-checks staleness first, so concurrent runs that arrive after the
    # first builder finishes find the image current and skip the rebuild.
    with _mock_build_lock():
        return _build_mock_image_locked(env_dir, image, force)


def _build_mock_image_locked(env_dir: Path, image: str = MOCK_IMAGE,
                             force: bool = False) -> bool:
    # Opt-in rebuild: the cached image otherwise serves whatever mock server
    # code / baseline CSVs existed when it was first built, so edits under
    # environment/ are silently ignored until the tag is removed. force=True
    # (or KENSEI_MOCK_REBUILD=1) rebuilds; default stays cached (no behavior
    # change). Per-task data does NOT need this — it is bind-mounted at runtime.
    force = force or os.environ.get("KENSEI_MOCK_REBUILD", "").strip().lower() in ("1", "true", "yes")
    current_hash = _compute_mock_content_hash(Path(env_dir))
    if force:
        logger.info("Force-rebuilding mock image %s (removing cached tag)", image)
        subprocess.run(["docker", "rmi", "-f", image], capture_output=True)
    else:
        r = subprocess.run(
            ["docker", "image", "inspect", image],
            capture_output=True,
        )
        if r.returncode == 0:
            cached_hash = _image_content_hash(image)
            if current_hash and cached_hash == current_hash:
                logger.info("Mock image %s already built (content_hash=%s)", image, cached_hash)
                return True
            logger.info(
                "Mock image %s is stale (cached_hash=%r expected=%r); rebuilding",
                image, cached_hash, current_hash,
            )
            subprocess.run(["docker", "rmi", "-f", image], capture_output=True)

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
        (tmp / "mock_ports.json").write_text(
            _generate_ports_manifest(api_ports), encoding="utf-8"
        )
        (tmp / "gen_supervisord.py").write_text(_GEN_SUPERVISORD_PY, encoding="utf-8")
        (tmp / "start.sh").write_text(_START_SH, encoding="utf-8")
        (tmp / "healthcheck.sh").write_text(_HEALTHCHECK_SH, encoding="utf-8")
        build_cmd = ["docker", "build", "-t", image]
        if current_hash:
            build_cmd += ["--label", f"{_CONTENT_HASH_LABEL}={current_hash}"]
        build_cmd += ["."]
        r = subprocess.run(
            build_cmd,
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
                     overlays: dict | None = None,
                     admin_env: dict[str, str] | None = None,
                     publish_ports: list[int] | None = None,
                     enabled_apis: "set[str] | list[str] | None" = None) -> None:
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
    env_args: list[str] = []
    # Inside the live container a seed-load failure must not kill uvicorn (it
    # would take the whole per-task stack down and disable injection); degrade
    # to an empty table instead. Host-side imports/validators stay strict.
    env_args += ["-e", "MOCK_RESILIENT_LOAD=1"]
    # Limit the stack to exactly these API services. Empty/None => run all
    # (back-compat). The image's entrypoint reads MOCK_ENABLED_APIS at start.
    if enabled_apis:
        enabled_csv = ",".join(sorted(enabled_apis))
        env_args += ["-e", f"MOCK_ENABLED_APIS={enabled_csv}"]
        logger.info("[%s] mock-stack limited to %d APIs: %s",
                    container_name, len(set(enabled_apis)), enabled_csv)
    for k, v in (admin_env or {}).items():
        env_args += ["-e", f"{k}={v}"]
    if admin_env:
        # Avoid logging token values; allowlist/enabled are safe.
        safe_keys = sorted(k for k in admin_env if k != "MOCK_ADMIN_TOKEN")
        logger.info("[%s] admin plane enabled (vars: %s)", container_name, safe_keys)
    publish_args: list[str] = []
    for port in publish_ports or []:
        # Bind to 127.0.0.1 only -- the host-side DriftDirector connects via
        # localhost; we must not expose the admin plane on the host's public
        # interfaces.
        publish_args += ["-p", f"127.0.0.1::{int(port)}"]
    cmd = [
        "docker", "run", "-d",
        "--name", container_name,
        "--network", network,
        *mount_args,
        *env_args,
        *publish_args,
        image,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"mock-stack start failed:\n{r.stderr}")
    logger.info("[%s] mock-stack container started", container_name)
    if publish_ports:
        # Published ports (-p) only route from the host when the container is
        # reachable on a host-connected network. The task network is created
        # with --internal, so an internal-only container is isolated and
        # `docker port` reports nothing -- the host-side admin plane then has
        # no URL and injection is disabled ("no host ports resolved").
        # Dual-home onto the default bridge (mirrors the LiteLLM sidecar) so the
        # published admin ports become reachable on 127.0.0.1.
        rb = subprocess.run(
            ["docker", "network", "connect", "bridge", container_name],
            capture_output=True, text=True,
        )
        if rb.returncode != 0:
            logger.warning("[%s] could not dual-home to default bridge "
                           "(published admin ports may be unreachable): %s",
                           container_name, (rb.stderr or "").strip())
        else:
            logger.info("[%s] dual-homed to default bridge for published admin ports",
                        container_name)


def get_published_ports(container_name: str, internal_ports: list[int]) -> dict[int, int]:
    """Resolve internal->host port mapping for a running container.

    Used by the DriftDirector to find each API's localhost port after the
    container is up. Returns {internal_port: host_port}. Ports not yet
    published (or never mapped) are omitted from the result.
    """
    out: dict[int, int] = {}
    for p in internal_ports:
        r = subprocess.run(
            ["docker", "port", container_name, str(p)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            continue
        for line in (r.stdout or "").splitlines():
            line = line.strip()
            if not line:
                continue
            host_part = line.rsplit(":", 1)[-1]
            try:
                out[int(p)] = int(host_part)
                break
            except ValueError:
                continue
    return out


def get_network_gateway(network: str) -> str | None:
    """Return the docker bridge gateway IP for `network`, or None on failure.

    The host appears to containers on `network` under this IP. We pass it as
    MOCK_ADMIN_ALLOWLIST so the admin plane only accepts inbound requests from
    the harness host (which is where the DriftDirector runs).
    """
    r = subprocess.run(
        ["docker", "network", "inspect", network,
         "--format", "{{range .IPAM.Config}}{{.Gateway}} {{end}}"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return None
    gws = (r.stdout or "").strip().split()
    return gws[0] if gws else None


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
