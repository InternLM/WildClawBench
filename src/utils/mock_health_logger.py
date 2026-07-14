"""Per-task mock API health logger.

Runs as a background thread for the duration of a single task run.
Polls each mock API's ``/health`` endpoint at a configurable interval and
records the result to a dedicated log set co-located with the task's
trajectory output:

* ``<output_dir>/mock_health.log``  -- human-readable probe summaries.
* ``<output_dir>/mock_health.jsonl`` -- one JSON record per probe for
  programmatic analysis.

Neither stream is propagated to the root logger, so the periodic ticks
stay OUT of the harness/bash stdout that hosts run_batch.py.

Probes are issued via ``docker exec <container> curl ...`` so the same
network path OpenClaw uses to reach the mock stack is actually exercised:

* Primary target: the **agent container** (``task_id``). When it is up,
  the probe uses the docker-network DNS name from ``env_dict`` --
  exactly what OpenClaw does at runtime. A break in the network path or
  container DNS between agent and mock is visible only via this probe.
* Fallback: the **mock container** itself (parsed from each URL). Used
  when the agent container is not yet running (before
  ``backend.run_task`` creates it) or has already torn down. This still
  proves the mock service is responsive even if the agent is gone.

When neither target is reachable, the iteration is recorded as
``status=probe_skipped`` so the timeline never silently goes blank.
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping


_URL_RE = re.compile(r"https?://([^/:]+):(\d+)")


def _parse_url(url: str) -> tuple[str, int] | None:
    """Extract ``(container, port)`` from a ``http://name:port`` URL."""
    m = _URL_RE.match(url or "")
    if not m:
        return None
    return m.group(1), int(m.group(2))


def _container_running(name: str) -> bool:
    if not name:
        return False
    r = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Running}}", name],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and (r.stdout or "").strip() == "true"


class MockHealthLogger(threading.Thread):
    """Background thread that periodically probes mock ``/health`` endpoints.

    Lifecycle mirrors ``DriftDirector``: ``start()`` to launch, ``stop()``
    to signal shutdown, then ``join(timeout=...)`` to await thread exit.
    The thread is a daemon, so a forgotten instance will not block process
    exit, but callers should still stop+join for clean log shutdown.
    """

    def __init__(
        self,
        task_id: str,
        api_url_map: Mapping[str, str],
        output_dir: Path,
        agent_container: str = "",
        interval: float = 30.0,
        probe_timeout: float = 3.0,
    ) -> None:
        super().__init__(name=f"mock-health-{task_id}", daemon=True)
        self.task_id = task_id
        self.api_url_map = {k: v for k, v in (api_url_map or {}).items() if v}
        self.output_dir = Path(output_dir)
        self.agent_container = agent_container or task_id
        self.interval = max(float(interval), 1.0)
        self.probe_timeout = max(float(probe_timeout), 1.0)
        self._stop_event = threading.Event()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.output_dir / "mock_health.jsonl"
        self.log_path = self.output_dir / "mock_health.log"
        self._log = self._build_file_logger()

    def _build_file_logger(self) -> logging.Logger:
        # Unique logger name (task_id + instance id) so concurrent tasks under
        # the ThreadPoolExecutor cannot share handlers. propagate=False keeps
        # the ticks out of the harness/root logger.
        name = f"mock_health.{self.task_id}.{id(self):x}"
        lg = logging.getLogger(name)
        lg.setLevel(logging.INFO)
        lg.propagate = False
        # Defensive: clear any handlers a prior incarnation under the same
        # name might have left behind (shouldn't happen given the id() suffix,
        # but a logger name collision would otherwise duplicate every line).
        for h in list(lg.handlers):
            lg.removeHandler(h)
            try:
                h.close()
            except Exception:
                pass
        fh = logging.FileHandler(self.log_path, encoding="utf-8")
        fh.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        ))
        lg.addHandler(fh)
        self._file_handler = fh
        return lg

    def _close_file_logger(self) -> None:
        try:
            self._file_handler.flush()
        except Exception:
            pass
        try:
            self._log.removeHandler(self._file_handler)
        except Exception:
            pass
        try:
            self._file_handler.close()
        except Exception:
            pass

    def run(self) -> None:
        try:
            if not self.api_url_map:
                self._log.info("no APIs to probe; thread exiting")
                return
            self._log.info(
                "starting: %d APIs, interval=%.1fs, agent_container=%s",
                len(self.api_url_map), self.interval, self.agent_container,
            )
            # First tick runs immediately so the initial state is captured at
            # task start rather than <interval>s in.
            self._tick()
            while not self._stop_event.wait(self.interval):
                self._tick()
            # Final tick on shutdown captures the closing state.
            self._tick()
            self._log.info("stopped")
        finally:
            self._close_file_logger()

    def stop(self) -> None:
        self._stop_event.set()

    def _tick(self) -> None:
        agent_up = _container_running(self.agent_container)
        ts = datetime.now(timezone.utc).isoformat()
        records: list[dict] = []
        healthy = 0
        failures: list[str] = []
        for name, url in self.api_url_map.items():
            # Skip non-URL config entries (admin tokens, etc.) so the
            # "<healthy>/<total>" count reflects only real API probe targets —
            # i.e. the APIs actually in use by this task.
            if _parse_url(url) is None:
                continue
            rec = self._probe(name, url, agent_up=agent_up, ts=ts)
            records.append(rec)
            if rec["status"] == "ok":
                healthy += 1
            else:
                failures.append(name)
        self._append_jsonl(records)
        total = healthy + len(failures)
        via = "agent" if agent_up else "mock"
        if failures:
            self._log.warning(
                "%d/%d healthy via=%s (failed: %s)",
                healthy, total, via, ",".join(failures[:6]),
            )
        else:
            self._log.info(
                "%d/%d healthy via=%s",
                healthy, total, via,
            )

    def _probe(self, name: str, url: str, agent_up: bool, ts: str) -> dict:
        parsed = _parse_url(url)
        if parsed is None:
            return {
                "ts": ts, "api": name, "url": url, "via": "none",
                "status": "bad_url", "http_code": 0,
                "latency_ms": 0, "error": "could not parse url",
            }
        mock_host, port = parsed

        # Prefer probing from the agent container -- same docker-network
        # DNS resolution + bridge path the agent uses for real calls.
        # Fall back to the mock container (localhost from inside) when
        # the agent container is not (yet) running.
        if agent_up:
            via = "agent"
            probe_url = url.rstrip("/") + "/health"
            probe_target = self.agent_container
        else:
            via = "mock"
            probe_url = f"http://localhost:{port}/health"
            probe_target = mock_host

        if not _container_running(probe_target):
            return {
                "ts": ts, "api": name, "url": url, "via": via,
                "status": "probe_skipped", "http_code": 0,
                "latency_ms": 0,
                "error": f"probe target {probe_target!r} not running",
            }

        start = time.monotonic()
        cmd = [
            "docker", "exec", probe_target,
            "curl", "-s", "-o", "/dev/null",
            "-w", "%{http_code}",
            "--max-time", str(int(self.probe_timeout)),
            probe_url,
        ]
        try:
            r = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=self.probe_timeout + 2,
            )
        except subprocess.TimeoutExpired:
            return {
                "ts": ts, "api": name, "url": url, "via": via,
                "status": "timeout", "http_code": 0,
                "latency_ms": int((time.monotonic() - start) * 1000),
                "error": "docker exec timed out",
            }
        latency_ms = int((time.monotonic() - start) * 1000)
        if r.returncode != 0:
            return {
                "ts": ts, "api": name, "url": url, "via": via,
                "status": "exec_failed", "http_code": 0,
                "latency_ms": latency_ms,
                "error": (r.stderr or "").strip()[:200],
            }
        code_str = (r.stdout or "").strip()
        try:
            http_code = int(code_str) if code_str else 0
        except ValueError:
            http_code = 0
        status = "ok" if 200 <= http_code < 400 else "http_error"
        return {
            "ts": ts, "api": name, "url": url, "via": via,
            "status": status, "http_code": http_code,
            "latency_ms": latency_ms, "error": "",
        }

    def _append_jsonl(self, records: list[dict]) -> None:
        try:
            with self.jsonl_path.open("a", encoding="utf-8") as fh:
                for rec in records:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError as exc:
            self._log.warning("jsonl write failed: %s", exc)
