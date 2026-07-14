"""
WildClawBench DriftDirector: host-side orchestrator for mid-run drift events.

The director reads a per-task ``drift.yaml`` script, watches the mock stack's
``/audit/requests`` feed (plus optional filesystem signals), and dispatches
mutation operations to each API's ``/admin/*`` plane at the right moment.
Every fired event is appended to ``drift_timeline.jsonl`` in the run output
directory so the grader can later check causality and visibility.

This module runs **on the harness host**, never inside the agent container,
and uses only stdlib + ``requests`` + ``pyyaml`` (no extra deps beyond what
``eval/run_batch.py`` already imports).

drift.yaml schema (v1)
----------------------

    description: "Free-form what-and-why."
    schedule:                             # time-based, optional
      - id: "ev1"
        at: "30s"                         # also: "1m30s", "500ms", float seconds
        action:
          api: airbnb-api
          inject:
            - op: data.patch
              table: listings
              pk: L_42
              fields: { price_per_night: 999 }

    triggers:                             # reactive, optional
      - id: "ev2"
        when:
          audit.first_call_on: { api: google-classroom-api }
        action:
          api: google-classroom-api
          inject:
            - op: data.delete
              table: students
              pk: S_stephanie_walker

    one_shot:                             # response-interceptors, optional
      - id: "ev3"
        when:
          audit.after:
            api: stripe-api
            method: GET
            path_regex: "^/v1/customers/.+$"
        action:
          api: stripe-api
          one_shot:
            path_regex: "^/v1/customers/cus_anchor$"
            method: GET
            transform:
              ops:
                - { op: set, path: "balance", value: -50000 }

Triggers (the ``when`` clause)
------------------------------

The director supports 5 primitive trigger kinds plus the ``all_of`` /
``any_of`` composites:

* ``audit.first_call_on: { api: <name> }``
    Fires the first time the agent calls ANY endpoint on the named API.

* ``audit.after: { api, method, path_regex, min_delay: "250ms" }``
    Fires after the agent has made a request matching method+path_regex
    against ``api``. ``min_delay`` (optional) introduces a delay before
    the action runs --- useful when you want the agent to read the
    "real" answer first and only see drift on the *next* call.

* ``audit.count_at_least: { api, n }``
    Fires once the agent has made at least N requests to ``api``.

* ``file.created: { path, min_size_bytes }``
    Fires when ``<workspace>/path`` exists and has at least
    ``min_size_bytes`` bytes (default 1). Path is relative to the agent's
    workspace dir.

* ``time.elapsed: { seconds }``
    Fires once N seconds have elapsed since director start. Discouraged
    because it doesn't track agent progress, but supported.

Composition:

* ``all_of: [t1, t2, ...]`` --- fires when every child has fired.
* ``any_of: [t1, t2, ...]`` --- fires when at least one child has fired.

Every event accepts an optional ``once: true`` (default) or ``fires: N``.

Why polling instead of websockets / pubsub?
-------------------------------------------

The tracking middleware already exposes ``/audit/requests``, the mock stack
already has health-checked HTTP ports, and run_batch.py is already
synchronous code with a ``requests`` dependency. Adding a websocket bridge
would mean modifying the mock container image and the harness. 500ms
polling on ``/audit/requests?since=<cursor>`` is simpler, has no extra
runtime dependencies, and is bounded in cost.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    import yaml
except ImportError as _yaml_exc:
    yaml = None
    _yaml_import_error = _yaml_exc
else:
    _yaml_import_error = None

import requests


LOG = logging.getLogger("wildclaw.drift")


class DriftConfigError(Exception):
    """Raised for malformed drift.yaml."""


_DURATION_RE = re.compile(
    r"^\s*(?:(?P<min>\d+)m)?(?:(?P<sec>\d+(?:\.\d+)?)s)?(?:(?P<ms>\d+)ms)?\s*$"
)


def _parse_duration(value: Any) -> float:
    """Parse '30s', '1m30s', '500ms', or a bare number into seconds.

    Accepts ints / floats directly (interpreted as seconds). Returns 0.0 for
    None / empty. Raises DriftConfigError on garbage.
    """
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        raise DriftConfigError(f"duration must be string or number, got {type(value).__name__}")
    s = value.strip()
    if not s:
        return 0.0
    try:
        return float(s)
    except ValueError:
        pass
    m = _DURATION_RE.match(s)
    if not m:
        raise DriftConfigError(f"unparseable duration: {value!r}")
    parts = m.groupdict()
    minutes = float(parts["min"] or 0)
    seconds = float(parts["sec"] or 0)
    millis = float(parts["ms"] or 0)
    total = minutes * 60 + seconds + millis / 1000
    if total == 0 and parts == {"min": None, "sec": None, "ms": None}:
        raise DriftConfigError(f"unparseable duration: {value!r}")
    return total


@dataclass
class _AuditEntry:
    timestamp: float
    method: str
    path: str
    status_code: int
    api_name: str
    raw: Dict[str, Any]


@dataclass
class _Trigger:
    kind: str
    spec: Dict[str, Any]
    fired: bool = False

    def evaluate(self, ctx: "_DispatchContext") -> bool:
        if self.fired:
            return True
        result = _TRIGGER_EVALUATORS[self.kind](self.spec, ctx)
        if result:
            self.fired = True
        return result


@dataclass
class _Event:
    id: str
    kind: str
    spec: Dict[str, Any]
    action: Dict[str, Any]
    fires_remaining: int
    delay_after: float = 0.0
    fired_count: int = 0


@dataclass
class _DispatchContext:
    audit_by_api: Dict[str, List[_AuditEntry]]
    workspace_dir: Optional[Path]
    director_start_ts: float
    current_ts: float
    # Optional path to the litellm sidecar log. Required only for the
    # ``agent.prompt_sent`` trigger; other evaluators ignore it.
    gateway_log_path: Optional[Path] = None

    def audit_for(self, api: str) -> List[_AuditEntry]:
        return self.audit_by_api.get(api, [])


def _eval_first_call_on(spec: Dict[str, Any], ctx: _DispatchContext) -> bool:
    api = spec.get("api")
    if not api:
        raise DriftConfigError("audit.first_call_on requires 'api'")
    return len(ctx.audit_for(api)) > 0


def _eval_after(spec: Dict[str, Any], ctx: _DispatchContext) -> bool:
    api = spec.get("api")
    method = spec.get("method", "GET").upper()
    path_regex = spec.get("path_regex", ".*")
    if not api:
        raise DriftConfigError("audit.after requires 'api'")
    rx = re.compile(path_regex)
    for entry in ctx.audit_for(api):
        if entry.method.upper() == method and rx.search(entry.path):
            return True
    return False


def _eval_count_at_least(spec: Dict[str, Any], ctx: _DispatchContext) -> bool:
    api = spec.get("api")
    n = int(spec.get("n", 1))
    if not api:
        raise DriftConfigError("audit.count_at_least requires 'api'")
    return len(ctx.audit_for(api)) >= n


def _eval_file_created(spec: Dict[str, Any], ctx: _DispatchContext) -> bool:
    path = spec.get("path")
    if not path:
        raise DriftConfigError("file.created requires 'path'")
    if ctx.workspace_dir is None:
        return False
    target = ctx.workspace_dir / path
    if not target.exists() or not target.is_file():
        return False
    min_size = int(spec.get("min_size_bytes", 1))
    try:
        return target.stat().st_size >= min_size
    except OSError:
        return False


def _eval_time_elapsed(spec: Dict[str, Any], ctx: _DispatchContext) -> bool:
    seconds = _parse_duration(spec.get("seconds", spec.get("at", 0)))
    return (ctx.current_ts - ctx.director_start_ts) >= seconds


def _eval_agent_prompt_sent(spec: Dict[str, Any], ctx: _DispatchContext) -> bool:
    min_count = int(spec.get("min_count", 1))
    log_path = ctx.gateway_log_path
    if log_path is None or not log_path.exists():
        return False
    try:
        with log_path.open("r", encoding="utf-8", errors="ignore") as fh:
            count = sum(
                1 for line in fh
                if ("POST /v1/messages" in line) or ("POST /chat/completions" in line)
            )
    except OSError:
        return False
    return count >= min_count


def _eval_all_of(spec: List[Dict[str, Any]], ctx: _DispatchContext) -> bool:
    return all(_eval_composite(child, ctx) for child in spec)


def _eval_any_of(spec: List[Dict[str, Any]], ctx: _DispatchContext) -> bool:
    return any(_eval_composite(child, ctx) for child in spec)


def _eval_composite(node: Dict[str, Any], ctx: _DispatchContext) -> bool:
    if not isinstance(node, dict) or len(node) != 1:
        raise DriftConfigError(f"trigger node must be a single-key dict, got: {node!r}")
    (kind, spec), = node.items()
    if kind not in _TRIGGER_EVALUATORS:
        raise DriftConfigError(f"unknown trigger kind: {kind}")
    return _TRIGGER_EVALUATORS[kind](spec, ctx)


_TRIGGER_EVALUATORS: Dict[str, Callable[[Any, _DispatchContext], bool]] = {
    "audit.first_call_on": _eval_first_call_on,
    "audit.after": _eval_after,
    "audit.count_at_least": _eval_count_at_least,
    "file.created": _eval_file_created,
    "time.elapsed": _eval_time_elapsed,
    "agent.prompt_sent": _eval_agent_prompt_sent,
    "all_of": _eval_all_of,
    "any_of": _eval_any_of,
}


@dataclass
class DriftScript:
    """Parsed drift.yaml. Built by ``DriftScript.load`` or ``.from_dict``.

    Exposes ``schedule`` (time-based), ``triggers`` (reactive), and
    ``one_shot`` (response interceptors) as flattened ``_Event`` lists.
    """

    description: str
    schedule: List[_Event] = field(default_factory=list)
    triggers: List[_Event] = field(default_factory=list)
    one_shot: List[_Event] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "DriftScript":
        if yaml is None:
            raise DriftConfigError(
                f"pyyaml not installed; cannot read {path} ({_yaml_import_error})"
            )
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        if not isinstance(raw, dict):
            raise DriftConfigError(f"drift script {path} must be a mapping at top level")
        return cls.from_dict(raw, source=str(path))

    @classmethod
    def from_dict(cls, raw: Dict[str, Any], source: str = "<dict>") -> "DriftScript":
        description = str(raw.get("description", ""))
        schedule_events: List[_Event] = []
        for i, item in enumerate(raw.get("schedule") or []):
            schedule_events.append(_compile_schedule_event(item, i, source))
        trigger_events: List[_Event] = []
        for i, item in enumerate(raw.get("triggers") or []):
            trigger_events.append(_compile_trigger_event(item, i, source))
        one_shot_events: List[_Event] = []
        for i, item in enumerate(raw.get("one_shot") or []):
            one_shot_events.append(_compile_trigger_event(item, i, source, kind_hint="one_shot"))
        return cls(
            description=description,
            schedule=schedule_events,
            triggers=trigger_events,
            one_shot=one_shot_events,
        )


def _compile_schedule_event(item: Dict[str, Any], idx: int, source: str) -> _Event:
    if "at" not in item:
        raise DriftConfigError(f"{source} schedule[{idx}] missing 'at'")
    if "action" not in item:
        raise DriftConfigError(f"{source} schedule[{idx}] missing 'action'")
    delay = _parse_duration(item["at"])
    return _Event(
        id=item.get("id") or f"sched_{idx}",
        kind="schedule",
        spec={"at": delay},
        action=item["action"],
        fires_remaining=int(item.get("fires", 1)),
        delay_after=0.0,
    )


def _compile_trigger_event(
    item: Dict[str, Any],
    idx: int,
    source: str,
    kind_hint: str = "trigger",
) -> _Event:
    if "when" not in item:
        raise DriftConfigError(f"{source} {kind_hint}[{idx}] missing 'when'")
    if "action" not in item:
        raise DriftConfigError(f"{source} {kind_hint}[{idx}] missing 'action'")
    when = item["when"]
    if not isinstance(when, dict) or len(when) != 1:
        raise DriftConfigError(
            f"{source} {kind_hint}[{idx}] 'when' must be a single-key mapping"
        )
    (trig_kind, trig_spec), = when.items()
    if trig_kind not in _TRIGGER_EVALUATORS:
        raise DriftConfigError(
            f"{source} {kind_hint}[{idx}] unknown trigger kind: {trig_kind}"
        )
    delay = _parse_duration(item.get("min_delay", item.get("delay_after", 0)))
    return _Event(
        id=item.get("id") or f"{kind_hint}_{idx}",
        kind=kind_hint,
        spec={"when": when, "min_delay": delay},
        action=item["action"],
        fires_remaining=int(item.get("fires", 1)),
        delay_after=delay,
    )


@dataclass
class _ApiTarget:
    name: str
    base_url: str
    admin_token: Optional[str] = None


class DriftDirector(threading.Thread):
    """Background thread that watches the audit feed and fires drift events.

    Usage from ``eval/run_batch.py``::

        director = DriftDirector(
            script=DriftScript.load(task["drift_script_path"]),
            targets={
                "airbnb-api": _ApiTarget("airbnb-api", "http://localhost:8011"),
                ...
            },
            workspace_dir=Path(task["workspace_dir"]),
            timeline_path=run_output_dir / "drift_timeline.jsonl",
            poll_interval=0.5,
        )
        director.start()
        try:
            run_agent(...)
        finally:
            director.stop()
            director.join(timeout=5)

    Thread-safety: the director owns one ``requests.Session`` and one
    timeline file handle. The ``stop()`` method is the only public mutator
    callable from another thread.
    """

    def __init__(
        self,
        script: DriftScript,
        targets: Dict[str, _ApiTarget],
        workspace_dir: Optional[Path],
        timeline_path: Path,
        poll_interval: float = 0.5,
        admin_token: Optional[str] = None,
        gateway_log_path: Optional[Path] = None,
    ):
        super().__init__(name="DriftDirector", daemon=True)
        self._script = script
        self._targets = dict(targets)
        self._workspace_dir = workspace_dir
        self._timeline_path = timeline_path
        self._poll_interval = float(poll_interval)
        self._admin_token = admin_token
        self._gateway_log_path = gateway_log_path
        self._stop_evt = threading.Event()
        self._session = requests.Session()
        self._cursors: Dict[str, float] = {name: 0.0 for name in targets}
        self._audit_by_api: Dict[str, List[_AuditEntry]] = {n: [] for n in targets}
        self._start_ts = 0.0
        self._timeline_lock = threading.Lock()
        self._timeline_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._timeline_path.exists():
            self._timeline_path.touch()

    def stop(self) -> None:
        self._stop_evt.set()

    def run(self) -> None:
        self._start_ts = time.time()
        self._append_timeline({
            "type": "director.start",
            "ts": self._start_ts,
            "description": self._script.description,
            "targets": sorted(self._targets.keys()),
            "schedule_events": len(self._script.schedule),
            "trigger_events": len(self._script.triggers),
            "one_shot_events": len(self._script.one_shot),
        })
        try:
            while not self._stop_evt.is_set():
                tick_start = time.time()
                try:
                    self._poll_audits()
                    self._dispatch()
                except Exception as exc:
                    LOG.exception("DriftDirector tick failed: %s", exc)
                    self._append_timeline({
                        "type": "director.error",
                        "ts": time.time(),
                        "error": str(exc),
                    })
                elapsed = time.time() - tick_start
                self._stop_evt.wait(max(0.0, self._poll_interval - elapsed))
        finally:
            self._append_timeline({
                "type": "director.stop",
                "ts": time.time(),
                "uptime_s": time.time() - self._start_ts,
            })
            self._session.close()

    def _poll_audits(self) -> None:
        for api_name, target in self._targets.items():
            since = self._cursors.get(api_name, 0.0)
            try:
                r = self._session.get(
                    target.base_url.rstrip("/") + "/audit/requests",
                    params={"since": since} if since else None,
                    timeout=2.0,
                )
                if r.status_code != 200:
                    continue
                payload = r.json()
            except (requests.RequestException, ValueError):
                continue
            if isinstance(payload, list):
                entries = payload
            elif isinstance(payload, dict):
                entries = payload.get("requests", [])
            else:
                continue
            if not isinstance(entries, list):
                continue
            for raw in entries:
                ts = float(raw.get("timestamp", 0) or 0)
                if ts <= since:
                    continue
                self._audit_by_api[api_name].append(_AuditEntry(
                    timestamp=ts,
                    method=str(raw.get("method", "")),
                    path=str(raw.get("path", "")),
                    status_code=int(raw.get("status_code", 0) or 0),
                    api_name=api_name,
                    raw=raw,
                ))
                if ts > self._cursors[api_name]:
                    self._cursors[api_name] = ts

    def _dispatch(self) -> None:
        ctx = _DispatchContext(
            audit_by_api=self._audit_by_api,
            workspace_dir=self._workspace_dir,
            director_start_ts=self._start_ts,
            current_ts=time.time(),
            gateway_log_path=self._gateway_log_path,
        )

        for event in self._script.schedule:
            if event.fires_remaining <= 0:
                continue
            delay = event.spec.get("at", 0.0)
            if (ctx.current_ts - self._start_ts) >= delay:
                self._fire(event, ctx, trigger_kind="schedule")

        for event in self._script.triggers:
            if event.fires_remaining <= 0:
                continue
            if not _eval_composite(event.spec["when"], ctx):
                continue
            if event.delay_after > 0:
                first_match_ts = ctx.current_ts
                if (ctx.current_ts - first_match_ts) < event.delay_after:
                    continue
            self._fire(event, ctx, trigger_kind="trigger")

        for event in self._script.one_shot:
            if event.fires_remaining <= 0:
                continue
            if not _eval_composite(event.spec["when"], ctx):
                continue
            self._fire(event, ctx, trigger_kind="one_shot")

    def _fire(self, event: _Event, ctx: _DispatchContext, trigger_kind: str) -> None:
        action = event.action or {}
        api = action.get("api")
        if not api:
            self._append_timeline({
                "type": "event.error",
                "ts": time.time(),
                "event_id": event.id,
                "error": "action missing 'api'",
            })
            event.fires_remaining = 0
            return
        target = self._targets.get(api)
        if target is None:
            self._append_timeline({
                "type": "event.error",
                "ts": time.time(),
                "event_id": event.id,
                "error": f"unknown api target '{api}'",
            })
            event.fires_remaining = 0
            return

        outcomes: List[Dict[str, Any]] = []
        if "inject" in action:
            ops = action["inject"] if isinstance(action["inject"], list) else [action["inject"]]
            outcomes.append(self._call_inject_raw(target, ops))
        if "one_shot" in action:
            outcomes.append(self._call_one_shot(target, action["one_shot"]))
        if "scenario" in action:
            outcomes.append(self._call_scenario(target, action["scenario"]))
        if "snapshot" in action:
            outcomes.append(self._call_snapshot(target, action["snapshot"]))
        if not outcomes:
            outcomes.append({"ok": False, "error": "action declared no operations"})

        event.fires_remaining -= 1
        event.fired_count += 1
        self._append_timeline({
            "type": "event.fired",
            "ts": time.time(),
            "event_id": event.id,
            "trigger_kind": trigger_kind,
            "api": api,
            "action_keys": [k for k in action if k != "api"],
            "outcomes": outcomes,
            "audit_cursor_at_fire": {
                api_name: self._cursors.get(api_name, 0.0)
                for api_name in self._targets
            },
        })

    def _admin_headers(self, target: _ApiTarget) -> Dict[str, str]:
        token = target.admin_token or self._admin_token
        return {"X-Admin-Token": token} if token else {}

    def _call_inject_raw(self, target: _ApiTarget, ops: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            r = self._session.post(
                target.base_url.rstrip("/") + "/admin/inject/raw",
                json={"operations": ops},
                headers=self._admin_headers(target),
                timeout=5.0,
            )
            return {"call": "inject.raw", "status": r.status_code,
                    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text}
        except requests.RequestException as exc:
            return {"call": "inject.raw", "ok": False, "error": str(exc)}

    def _call_one_shot(self, target: _ApiTarget, spec: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self._session.post(
                target.base_url.rstrip("/") + "/admin/inject/one_shot",
                json=spec,
                headers=self._admin_headers(target),
                timeout=5.0,
            )
            return {"call": "inject.one_shot", "status": r.status_code,
                    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text}
        except requests.RequestException as exc:
            return {"call": "inject.one_shot", "ok": False, "error": str(exc)}

    def _call_scenario(self, target: _ApiTarget, spec: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self._session.post(
                target.base_url.rstrip("/") + "/admin/scenario/apply",
                json=spec,
                headers=self._admin_headers(target),
                timeout=5.0,
            )
            return {"call": "scenario.apply", "status": r.status_code,
                    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text}
        except requests.RequestException as exc:
            return {"call": "scenario.apply", "ok": False, "error": str(exc)}

    def _call_snapshot(self, target: _ApiTarget, spec: Dict[str, Any]) -> Dict[str, Any]:
        op = spec.get("op", "take")
        try:
            if op == "take":
                label = spec.get("label")
                params = {"label": label} if label else None
                r = self._session.get(
                    target.base_url.rstrip("/") + "/admin/snapshot",
                    params=params, headers=self._admin_headers(target), timeout=5.0,
                )
            elif op == "restore":
                r = self._session.post(
                    target.base_url.rstrip("/") + "/admin/snapshot/restore",
                    json={"snapshot_id": spec["snapshot_id"]},
                    headers=self._admin_headers(target), timeout=5.0,
                )
            else:
                return {"call": "snapshot", "ok": False, "error": f"unknown op '{op}'"}
            return {"call": f"snapshot.{op}", "status": r.status_code,
                    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text}
        except requests.RequestException as exc:
            return {"call": f"snapshot.{op}", "ok": False, "error": str(exc)}

    def _append_timeline(self, entry: Dict[str, Any]) -> None:
        entry.setdefault("ts_iso", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(entry.get("ts", time.time()))))
        line = json.dumps(entry, default=str) + "\n"
        with self._timeline_lock:
            with open(self._timeline_path, "a", encoding="utf-8") as f:
                f.write(line)


def build_targets_from_env(
    api_to_url: Dict[str, str],
    admin_token: Optional[str] = None,
) -> Dict[str, _ApiTarget]:
    """Helper for run_batch.py: converts ``{api_name: base_url}`` to targets.

    ``api_to_url`` is the mapping run_batch.py already constructs for the
    task's ``env_dict`` -- the same dict that becomes environment variables
    inside the agent container. We reuse it so there's exactly one source
    of truth for "where is API X reachable from the host."
    """
    return {
        name: _ApiTarget(name=name, base_url=url, admin_token=admin_token)
        for name, url in api_to_url.items()
    }
