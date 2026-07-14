"""Output-assembly + grading wiring for the sub-agent feature (june-7 port).

Covers the june-10-specific graft points (the runtime director/tools have their
own ported suites):
  * build_published_trajectory attaches `sub_agent_trajectories` only when
    sub-agents exist, in spawn-tree order, leaving the {meta_info, messages}
    schema otherwise byte-identical.
  * build_checker_state turns a spawn_tree.jsonl into the `state["checkers"]`
    shape the grading fixture reads.
  * task_parser synthesizes a multi_agent config from prompts.txt headers.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.trajectory.builder import build_published_trajectory  # noqa: E402
from src.utils.spawn_tree_checks import build_checker_state  # noqa: E402
from src.utils.task_parser import (  # noqa: E402
    _synthesize_multi_agent_config,
    _multi_agent_config_from_complex_turns,
    _attach_drift_script,
)

_TRAJ = {
    "messages": [
        {"type": "message", "id": "m0", "timestamp": "t",
         "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}},
    ],
    "trajectory": {"meta_info": {"platform": "linux"}},
}
_TASK = {"task_type": "research", "task_description": "d", "system_prompt": "sp"}


def test_no_subagents_key_omitted():
    pub = build_published_trajectory(_TRAJ, _TASK, "success")
    assert set(pub.keys()) == {"meta_info", "messages"}
    assert "sub_agent_trajectories" not in pub


def _write_spawns(tmp_path: Path) -> tuple[Path, Path]:
    sub = tmp_path / "subagents"
    sub.mkdir()
    (sub / "spw_B.delivery.json").write_text(
        json.dumps({"meta_info": {"usage": {}}, "messages": []}))
    (sub / "spw_A.delivery.json").write_text(
        json.dumps({"meta_info": {"usage": {}}, "messages": []}))
    st = tmp_path / "spawn_tree.jsonl"
    st.write_text('{"spawn_id":"spw_A"}\n{"spawn_id":"spw_B"}\n')
    return sub, st


def test_subagents_embedded_in_spawn_tree_order(tmp_path):
    sub, st = _write_spawns(tmp_path)
    pub = build_published_trajectory(
        _TRAJ, _TASK, "success", subagents_dir=sub, spawn_tree_path=st)
    assert "sub_agent_trajectories" in pub
    # spawn_tree order wins over filesystem sort.
    assert list(pub["sub_agent_trajectories"].keys()) == ["spw_A", "spw_B"]
    # base schema untouched.
    assert {"meta_info", "messages"} <= set(pub.keys())


def test_subagents_orphan_delivery_files_still_embedded(tmp_path):
    # A spawn with a delivery file but no spawn_tree row is still captured.
    sub = tmp_path / "subagents"
    sub.mkdir()
    (sub / "spw_X.delivery.json").write_text(json.dumps({"messages": []}))
    pub = build_published_trajectory(
        _TRAJ, _TASK, "success", subagents_dir=sub, spawn_tree_path=tmp_path / "missing.jsonl")
    assert list(pub["sub_agent_trajectories"].keys()) == ["spw_X"]


def test_checker_state_pass_and_fail(tmp_path):
    st = tmp_path / "spawn_tree.jsonl"
    st.write_text(
        '{"spawn_id":"a","turn_index":1,"status":"ok"}\n'
        '{"spawn_id":"b","turn_index":1,"status":"ok"}\n'
        '{"spawn_id":"c","turn_index":2,"status":"ok"}\n'  # only 1 in turn 2
    )
    cfg = {
        "expected_per_turn": {
            "1": {"min_subagents": 2, "checker_id": "T1_MA"},
            "2": {"min_subagents": 2, "checker_id": "T2_MA"},
        },
        "aggregate_checker_id": "MA_C1",
    }
    state = build_checker_state(st, cfg)
    checkers = state["checkers"]
    assert checkers["T1_MA"] is True      # 2 ok spawns >= 2
    assert checkers["T2_MA"] is False     # 1 ok spawn < 2
    assert checkers["MA_C1"] is False     # aggregate requires all per-turn


def test_checker_state_missing_file_all_false(tmp_path):
    cfg = {"expected_per_turn": {"1": {"min_subagents": 2, "checker_id": "T1_MA"}}}
    state = build_checker_state(tmp_path / "nope.jsonl", cfg)
    assert state["checkers"]["T1_MA"] is False


def test_task_parser_synthesizes_from_prompts(tmp_path):
    (tmp_path / "prompts.txt").write_text(
        "--- TURN 1 (Day 1, Light) ---\nhi\n"
        "--- TURN 2 (Day 1, Multi-Agent) ---\ngo\n"
    )
    cfg = _synthesize_multi_agent_config(tmp_path)
    assert cfg["enabled"] is True
    # 1-indexed header -> 0-indexed turn key.
    assert "1" in cfg["expected_per_turn"]
    assert cfg["expected_per_turn"]["1"]["checker_id"] == "T1_MA"
    task = _attach_drift_script({}, tmp_path)
    assert task["multi_agent_enabled"] is True


def test_task_parser_no_multi_agent_disabled(tmp_path):
    # Multi-agent is opt-in: a task that declares nothing gets the sub-agent
    # tool disabled. Enable per-task via multi_agent_complex_turns / a
    # task_config.yaml multi_agent block / a prompts.txt Multi-Agent label.
    (tmp_path / "prompts.txt").write_text("--- TURN 1 (Day 1, Light) ---\nhi\n")
    task = _attach_drift_script({}, tmp_path)
    assert task["multi_agent_enabled"] is False
    assert task["multi_agent_config"] == {}


def test_complex_turns_helper_shape():
    # 1-indexed task.yaml turns -> 0-indexed checkers, same shape as the token path.
    cfg = _multi_agent_config_from_complex_turns([1, 4], num_turns=4)
    assert cfg["enabled"] is True
    assert set(cfg["expected_per_turn"]) == {"0", "3"}
    assert cfg["expected_per_turn"]["0"]["checker_id"] == "T0_MA"
    assert cfg["expected_per_turn"]["3"]["checker_id"] == "T3_MA"
    assert cfg["expected_per_turn"]["0"]["min_subagents"] == 2
    assert cfg["aggregate_checker_id"] == "MA_C1"


def test_complex_turns_empty_or_bad_input_disabled():
    assert _multi_agent_config_from_complex_turns(None) == {}
    assert _multi_agent_config_from_complex_turns([]) == {}
    assert _multi_agent_config_from_complex_turns("nope") == {}


def test_complex_turns_out_of_range_kept(caplog):
    # A configured turn beyond the actual turn count is honoured (kept) but warned;
    # it can never spawn, so the author is told to align turns / prompts / config.
    cfg = _multi_agent_config_from_complex_turns([1, 4], num_turns=1)
    assert set(cfg["expected_per_turn"]) == {"0", "3"}


def test_task_parser_enables_from_complex_turns_config(tmp_path):
    # No "Multi-Agent" token anywhere -- enablement comes from the config key.
    (tmp_path / "prompts.txt").write_text(
        "--- TURN T1 (Day 1, 05:30) ---\nrun the whole thing\n"
    )
    task = {"multi_agent_complex_turns": [1], "turn_messages": ["run the whole thing"]}
    out = _attach_drift_script(task, tmp_path)
    assert out["multi_agent_enabled"] is True
    cfg = out["multi_agent_config"]
    assert cfg["expected_per_turn"]["0"]["checker_id"] == "T0_MA"
    assert cfg["aggregate_checker_id"] == "MA_C1"
