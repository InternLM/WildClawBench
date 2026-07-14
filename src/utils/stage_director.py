"""
WildClawBench StageDirector: ClawMark-style multi-turn, inject-while-idle.

Unlike ``drift_director`` (which mutates mock state *during* a single
continuous agent run, racing the agent), the staged model invokes the agent
in discrete turns on the same session and applies each stage's mock-data
mutation **between turns, while the agent is idle**. The mutation therefore
always lands before the agent's next turn -- no race -- and is *silent*: the
follow-up message never reveals what changed, so catching it is a genuine test
of whether the agent re-verifies state.

stages.yaml schema (v1)
-----------------------

    description: "Free-form what-and-why."
    default_message: >-
      Before you finalize, double-check that every detail in your draft is
      still current and correct, then give me your final answer.

    stages:
      - id: physical_rescheduled
        # Applied AFTER the previous agent turn, BEFORE the next one (silent).
        inject:
          - api: google-calendar-api
            op: data.patch
            table: events
            pk: evt-201
            fields: { start: "2026-10-22T15:30:00-04:00", end: "2026-10-22T16:15:00-04:00" }
        # Optional per-stage override of default_message (the next turn's nudge).
        message: "Take another look at the appointment details before finalizing."

Turn model
----------

Turn 0 runs the task prompt. Then for each stage i: apply stage[i].inject
(silently, via the admin plane), then run turn i+1 with stage[i].message
(or default_message). The number of agent turns == 1 + len(stages).

The op vocabulary inside ``inject`` is identical to the drift admin plane
(``data.upsert`` / ``data.patch`` / ``data.delete`` / ``data.update_where`` /
``data.delete_where`` / ``doc.set`` / ``doc.merge``); each op additionally
carries an ``api`` naming the mock service to mutate. See docs/DRIFT.md.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError as _exc:  # pragma: no cover
    yaml = None
    _yaml_import_error = _exc
else:
    _yaml_import_error = None

import requests

LOG = logging.getLogger("wildclaw.stages")

_DEFAULT_MESSAGE = (
    "Before you finalize, double-check that every detail in your response is "
    "still current and correct, then give me your final answer."
)


class StageConfigError(Exception):
    """Raised for malformed stages.yaml."""


@dataclass
class Stage:
    id: str
    message: str
    injects: List[Dict[str, Any]]  # each op carries an 'api' key


@dataclass
class StageScript:
    description: str
    default_message: str
    stages: List[Stage] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path | str) -> "StageScript":
        if yaml is None:
            raise StageConfigError(f"pyyaml not installed ({_yaml_import_error})")
        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        if not isinstance(raw, dict):
            raise StageConfigError(f"{path} must be a mapping at top level")
        return cls.from_dict(raw, source=str(path))

    @classmethod
    def from_dict(cls, raw: Dict[str, Any], source: str = "<dict>") -> "StageScript":
        default_message = str(raw.get("default_message") or _DEFAULT_MESSAGE).strip()
        stages: List[Stage] = []
        items = raw.get("stages") or []
        if not isinstance(items, list) or not items:
            raise StageConfigError(f"{source}: 'stages' must be a non-empty list")
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise StageConfigError(f"{source} stages[{i}] must be a mapping")
            injects = item.get("inject") or []
            if not isinstance(injects, list):
                raise StageConfigError(f"{source} stages[{i}] 'inject' must be a list")
            # An empty inject list is allowed: a "message-only" stage advances the
            # agent across one turn boundary (a follow-up nudge) WITHOUT mutating
            # state. This lets a scenario have more turns than injections (e.g. a
            # 7-turn arc with silent injections on only 2 of the boundaries).
            # apply() no-ops cleanly when injects is empty. Stages that DO inject
            # must still name an `api` + `op` per op.
            for j, op in enumerate(injects):
                if not isinstance(op, dict) or "api" not in op or "op" not in op:
                    raise StageConfigError(
                        f"{source} stages[{i}].inject[{j}] needs 'api' and 'op'")
            stages.append(Stage(
                id=str(item.get("id") or f"stage_{i}"),
                message=str(item.get("message") or default_message).strip(),
                injects=injects,
            ))
        return cls(
            description=str(raw.get("description", "")),
            default_message=default_message,
            stages=stages,
        )

    def turn_messages(self, initial_prompt: str) -> tuple[str, ...]:
        """Full per-turn message list: turn 0 = task prompt, then one nudge per stage."""
        return tuple([initial_prompt] + [s.message for s in self.stages])


class StageApplier:
    """Applies a stage's silent injection via each API's ``/admin/inject/raw``.

    ``host_api_to_url`` maps api-name -> ``http://127.0.0.1:<published-port>``
    (the same map the DriftDirector uses). Every applied stage is appended to
    ``stage_timeline.jsonl`` for verification/grading.
    """

    def __init__(
        self,
        host_api_to_url: Dict[str, str],
        admin_token: Optional[str],
        timeline_path: Path,
    ):
        self._urls = dict(host_api_to_url)
        self._token = admin_token
        self._timeline_path = Path(timeline_path)
        self._timeline_path.parent.mkdir(parents=True, exist_ok=True)
        self._session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        return {"X-Admin-Token": self._token} if self._token else {}

    def apply(self, stage: Stage, turn_index: int) -> List[Dict[str, Any]]:
        # Group this stage's ops by target api, then POST each group once.
        by_api: Dict[str, List[Dict[str, Any]]] = {}
        for op in stage.injects:
            api = op.get("api")
            payload = {k: v for k, v in op.items() if k != "api"}
            by_api.setdefault(api, []).append(payload)

        outcomes: List[Dict[str, Any]] = []
        for api, ops in by_api.items():
            base = self._urls.get(api)
            if not base:
                outcomes.append({"api": api, "ok": False, "error": "no admin URL for api"})
                continue
            try:
                r = self._session.post(
                    base.rstrip("/") + "/admin/inject/raw",
                    json={"operations": ops},
                    headers=self._headers(),
                    timeout=5.0,
                )
                ctype = r.headers.get("content-type", "")
                outcomes.append({
                    "api": api, "status": r.status_code,
                    "body": r.json() if ctype.startswith("application/json") else r.text[:200],
                })
            except requests.RequestException as exc:
                outcomes.append({"api": api, "ok": False, "error": str(exc)})

        self._append({
            "type": "stage.applied",
            "ts": time.time(),
            "stage_id": stage.id,
            "applied_before_turn": turn_index,
            "ops": len(stage.injects),
            "outcomes": outcomes,
        })
        LOG.info("stage '%s' injected before turn %d: %s", stage.id, turn_index, outcomes)
        return outcomes

    def record_turn(self, turn_index: int, kind: str) -> None:
        self._append({"type": "turn", "ts": time.time(),
                      "turn_index": turn_index, "kind": kind})

    def close(self) -> None:
        self._session.close()

    def _append(self, entry: Dict[str, Any]) -> None:
        entry.setdefault("ts_iso", time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(entry.get("ts", time.time()))))
        with open(self._timeline_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
