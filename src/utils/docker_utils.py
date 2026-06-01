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

def remove_container(name: str) -> None:
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)

def start_container(task_id: str, workspace_path: str, extra_env: str = "",
                    tmp_path: str = "", lobster_env: list[str] | None = None,
                    extra_env_dict: dict[str, str] | None = None,
                    network: str = "") -> None:
    workspace = Path(workspace_path).expanduser()
    if not workspace.is_dir():
        raise RuntimeError(f"Workspace path does not exist or is not a directory: {workspace}")

    proxy_http = os.environ.get('HTTP_PROXY_INNER', '')
    proxy_https = os.environ.get('HTTPS_PROXY_INNER', '')
    # When no proxy is configured, bypass any inherited proxy entirely (no_proxy="*").
    no_proxy_value = os.environ.get("NO_PROXY_INNER", "*") if not proxy_http else os.environ.get("NO_PROXY_INNER", "")
    env_args = [
        "-e", f"http_proxy={proxy_http}",
        "-e", f"https_proxy={proxy_https}",
        "-e", f"HTTP_PROXY={proxy_http}",
        "-e", f"HTTPS_PROXY={proxy_https}",
        "-e", f"BRAVE_API_KEY={BRAVE_API_KEY}",
        "-e", f"no_proxy={no_proxy_value}",
        "-e", f"NO_PROXY={no_proxy_value}",
    ]
    for line in extra_env.splitlines():
        key = line.strip()
        if not key or key.startswith("#"):
            continue
        value = os.environ.get(key, "")
        env_args += ["-e", f"{key}={value}"]
        masked = (value[:4] + "***") if value else "(empty)"
        logger.info("[%s] Injecting env var: %s=%s", task_id, key, masked)

    for key in (lobster_env or []):
        value = os.environ.get(key, "")
        if not value:
            logger.warning("[%s] Lobster env key %s not found in environment, skipping", task_id, key)
            continue
        env_args += ["-e", f"{key}={value}"]
        masked = value[:4] + "***"
        logger.info("[%s] Injecting lobster env: %s=%s", task_id, key, masked)

    for k, v in (extra_env_dict or {}).items():
        env_args += ["-e", f"{k}={v}"]
        logger.info("[%s] Injecting extra env: %s=%s", task_id, k, v)

    image = os.environ.get("DOCKER_IMAGE", DOCKER_IMAGE)
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
    injected: list[str] = []
    for api in required_apis:
        connector = env_root / "skills" / f"{api}-connector"
        if not connector.is_dir():
            continue
        dest = f"{container_skills_root}/{api}-connector"
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
        else:
            injected.append(api)
    api_doc = env_root / "API_DOCUMENTATION.md"
    if api_doc.is_file():
        subprocess.run(
            ["docker", "cp", str(api_doc), f"{task_id}:/root/API_DOCUMENTATION.md"],
            capture_output=True, text=True,
        )
    if injected:
        logger.info("[%s] Injected API connectors: %s", task_id, ",".join(injected))


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


def collect_output_from_container(
    task_id: str,
    output_dir: Path,
    *,
    include_workspace_changes: bool = False,
) -> None:
    """Collect task output files from the container to output_dir/task_output/.

    Collection strategy:
      1. All files under /tmp/openclaw/ (agent session logs, etc.)
      2. Task output files under /tmp_workspace/results/
      3. The full /tmp_workspace/ tree (into workspace_full/) so deliverables an
         agent wrote outside results/ are never lost. /root/workspace is a
         symlink to /tmp_workspace (see setup_workspace), so writes to either
         path are captured here.
    """
    task_output_dir = output_dir / "task_output"
    task_output_dir.mkdir(parents=True, exist_ok=True)

    _copy_dir_from_container(task_id, "/tmp/openclaw/.", str(task_output_dir))

    workspace_out = task_output_dir / "workspace"
    workspace_out.mkdir(parents=True, exist_ok=True)

    if include_workspace_changes:
        ok = _copy_dir_from_container(task_id, f"{TMP_WORKSPACE}/.", str(workspace_out))
        if not ok:
            logger.warning("[%s] workspace directory does not exist or is empty", task_id)
        return

    results_out = workspace_out / "results"
    results_out.mkdir(parents=True, exist_ok=True)
    ok = _copy_dir_from_container(
        task_id, f"{TMP_WORKSPACE}/results/.", str(results_out),
    )
    if not ok:
        logger.warning("[%s] results/ directory does not exist or is empty", task_id)

    # Additively sweep the full workspace into a distinct subdir so deliverables
    # written outside results/ (e.g. /root/workspace/<subdir>/, which resolves
    # into TMP_WORKSPACE via the symlink) are still captured. Strictly additive:
    # never overwrites or shadows workspace/results/. Best-effort, not a warning.
    full_out = task_output_dir / "workspace_full"
    full_out.mkdir(parents=True, exist_ok=True)
    if not _copy_dir_from_container(task_id, f"{TMP_WORKSPACE}/.", str(full_out)):
        logger.debug("[%s] full workspace sweep found nothing to collect", task_id)


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
    else:
        logger.info("[%s] Lobster workspace copied: %s → /root/", task_id, workspace_path)


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
