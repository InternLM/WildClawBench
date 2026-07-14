from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable, Mapping


logger = logging.getLogger(__name__)


def load_spawn_rows(spawn_tree_path: str | Path) -> list[dict]:
    p = Path(spawn_tree_path)
    if not p.is_file():
        return []
    rows: list[dict] = []
    with p.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def _count_spawns_per_turn(rows: Iterable[Mapping[str, Any]]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for row in rows:
        if row.get("status") != "ok":
            continue
        ti = row.get("turn_index")
        if not isinstance(ti, int):
            try:
                ti = int(ti)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                continue
        counts[ti] = counts.get(ti, 0) + 1
    return counts


def build_checker_state(
    spawn_tree_path: str | Path,
    multi_agent_config: Mapping[str, Any] | None,
) -> dict[str, dict[str, bool]]:
    """Translate a spawn_tree.jsonl file into the ``state["checkers"]`` dict
    GLORIA-style ``test_outputs.py`` reads via ``state.get("checkers", {}).get(ID)``.

    ``multi_agent_config`` shape (per ``input/<task>/task_config.yaml``):
        expected_per_turn:
            "<turn_index>": {min_subagents: int, checker_id: str}
        aggregate_checker_id: str   # optional; True iff all per-turn pass

    Counting rule: only rows with ``status == "ok"`` and a parseable
    ``turn_index`` are counted. Missing/malformed file -> all expected
    checkers False (so the agent is held accountable for the spawn budget
    even when its skill calls silently errored).
    """
    checkers: dict[str, bool] = {}
    if not isinstance(multi_agent_config, Mapping):
        return {"checkers": checkers}

    expected = multi_agent_config.get("expected_per_turn") or {}
    if not isinstance(expected, Mapping):
        expected = {}

    rows = load_spawn_rows(spawn_tree_path)
    counts = _count_spawns_per_turn(rows)

    per_turn_results: list[bool] = []
    for raw_turn_key, raw_spec in expected.items():
        if not isinstance(raw_spec, Mapping):
            continue
        try:
            turn_index = int(raw_turn_key)
        except (TypeError, ValueError):
            continue
        try:
            min_subagents = int(raw_spec.get("min_subagents", 0) or 0)
        except (TypeError, ValueError):
            min_subagents = 0
        checker_id = raw_spec.get("checker_id")
        if not isinstance(checker_id, str) or not checker_id:
            continue
        actual = counts.get(turn_index, 0)
        passed = actual >= min_subagents
        checkers[checker_id] = passed
        per_turn_results.append(passed)

    aggregate_id = multi_agent_config.get("aggregate_checker_id")
    if isinstance(aggregate_id, str) and aggregate_id:
        checkers[aggregate_id] = bool(per_turn_results) and all(per_turn_results)

    return {"checkers": checkers}


def build_state_file(
    spawn_tree_path: str | Path,
    multi_agent_config: Mapping[str, Any] | None,
    out_path: str | Path,
) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    state = build_checker_state(spawn_tree_path, multi_agent_config)
    out.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return out
