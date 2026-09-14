"""Nightly-window driver for the WildClawBench dsh harness.

Runs remaining tasks 05:00-07:30 America/Chicago (host-local), resumable
via a JSON ledger. One run_batch subprocess per task; up to PARALLEL
concurrent; hard stop when the window closes (in-flight runs finish,
then all bench containers are swept).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time as dtime
from pathlib import Path

def resolve_backend(root: Path) -> str:
    """Env wins; else output/backend.conf (written by the M3 audit card when
    the dsh arm is terminal); else dsh."""
    env = os.environ.get("WCB_BACKEND")
    if env:
        return env
    conf = root / "output" / "backend.conf"
    if conf.exists():
        return conf.read_text().strip() or "dsh"
    return "dsh"


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"
BACKEND = resolve_backend(ROOT)
MODEL = os.environ.get("WCB_MODEL", "qwen3.8-flash-next")
OUT_ROOT = ROOT / "output" / BACKEND
LEDGER = OUT_ROOT / (f"ledger_{MODEL}.json" if BACKEND == "dsh"
                     else f"ledger_{BACKEND}_{MODEL}.json")
PARALLEL = 4
WINDOW_START = "05:00"
WINDOW_STOP = "07:30"
DOCKER_IMAGE_TAG = {"dsh": "wildclawbench-dsh:v0.1",
                    "openclaw": "wildclawbench-ubuntu:v1.3"}[BACKEND]

_lock = threading.Lock()


def load_ledger(path: Path) -> dict:
    path = Path(path)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            raise RuntimeError(f"ledger unreadable (refusing to guess): {path}")
    return {}


def save_ledger(path: Path, data: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1, sort_keys=True))
    os.replace(tmp, path)


def record_result(path: Path, task_id: str, score_json_path: Path) -> str:
    try:
        payload = json.loads(Path(score_json_path).read_text())
        status = "failed" if "error" in payload else "completed"
    except Exception:
        status = "failed"
    with _lock:
        led = load_ledger(path)
        led[task_id] = status
        save_ledger(path, led)
    return status


def short_id(task_file: Path) -> str:
    m = re.match(r"(\d+_.*?task_\d+)", Path(task_file).stem)
    return m.group(1) if m else Path(task_file).stem


def pending_tasks(tasks_dir: Path, ledger: dict) -> list[Path]:
    files = sorted(Path(tasks_dir).glob("*/*task_*.md"))
    return [f for f in files
            if short_id(f) not in ledger or ledger[short_id(f)] == "failed"]


def window_active(now: datetime | None = None,
                  start: str = WINDOW_START, stop: str = WINDOW_STOP) -> bool:
    now = now or datetime.now()
    s = dtime(*map(int, start.split(":")))
    e = dtime(*map(int, stop.split(":")))
    return s <= now.time() < e


def _newest_score(category: str, task_stem: str) -> Path:
    base = OUT_ROOT / category / task_stem
    # Runs write <run>/score.json (plus legacy <run>/<name>.score.json).
    hits = sorted(
        (p for pat in ("*/score.json", "*/*.score.json")
         for p in base.glob(pat)),
        key=lambda p: p.stat().st_mtime,
    ) if base.is_dir() else []
    return hits[-1] if hits else OUT_ROOT / "_missing_score.json"


def build_run_cmd(backend: str, model: str, task_file: Path) -> list[str]:
    cmd = [sys.executable, str(ROOT / "eval" / "run_batch.py"),
           "--agent-backend", backend, "--task", str(task_file),
           "--model", model if backend == "dsh" else f"wcb-lb/{model}"]
    if backend == "openclaw":  # matched run: same self-hosted LB endpoint
        cmd += ["--models-config", str(ROOT / "my_api.lb.json")]
    return cmd


def run_one(task_file: Path) -> str:
    if not window_active():  # hard stop: queued futures past WINDOW_STOP defer
        return "deferred"
    cmd = build_run_cmd(BACKEND, MODEL, task_file)
    env = dict(os.environ, DOCKER_IMAGE=DOCKER_IMAGE_TAG)
    if BACKEND == "openclaw":
        env["MY_PROXY_API_KEY"] = os.environ.get("WCB_LB_API_KEY", "")
    subprocess.run(cmd, cwd=ROOT, env=env)
    score = _newest_score(Path(task_file).parent.name, Path(task_file).stem)
    return record_result(LEDGER, short_id(task_file), score)


def sweep_containers() -> None:
    subprocess.run(
        ["bash", "-c",
         f"docker ps -a --filter ancestor={DOCKER_IMAGE_TAG} -q "
         f"| xargs -r docker rm -f"],
        cwd=ROOT)


def main(argv: list[str]) -> int:
    if not window_active() and "force" not in argv:
        print("outside nightly window; pass 'force' to run anyway")
        return 0
    led = load_ledger(LEDGER)
    queue = pending_tasks(TASKS_DIR, led)
    print(f"nightly: {len(queue)} tasks pending; ledger {LEDGER}")
    stopped_early = False
    with ThreadPoolExecutor(max_workers=PARALLEL) as pool:
        futures = []
        for tf in queue:
            if not window_active() and "force" not in argv:
                stopped_early = True
                print("window closed; remaining tasks deferred to next night")
                break
            futures.append(pool.submit(run_one, tf))
        for f in futures:
            f.result()
    sweep_containers()
    led = load_ledger(LEDGER)
    done = sum(1 for v in led.values() if v == "completed")
    print(f"nightly done: {done} completed, {len(led) - done} failed/retry in ledger")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
