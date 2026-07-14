"""Tests for the golden-layout serializer (native sessions_spawn output).

Verifies parent.json + children/NN_<name>.json + spawn_tree/ are written in the
exact reference golden schema (Larry_Bates / dawn_mitchell).
"""
from __future__ import annotations

import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.trajectory.builder import (  # noqa: E402
    extract_spawn_calls,
    build_child_trajectory,
    write_golden_layout,
)


def _parent_with_spawns():
    """A slim published parent doc with two native sessions_spawn calls."""
    return {
        "meta_info": {
            "task_type": "skill_use_and_orchestration",
            "task_description": "Assemble the packet.",
            "task_completion_status": "success",
            "system_prompt": "You are an assistant.",
            "platform": "linux",
        },
        "messages": [
            {"type": "message", "id": "m0", "message": {"role": "user",
             "content": [{"type": "text", "text": "do it"}]}},
            {"type": "message", "id": "m1", "message": {"role": "assistant", "content": [
                {"type": "toolCall", "id": "t1", "name": "sessions_spawn",
                 "arguments": {"name": "gmail-scanner", "prompt": "Scan Gmail."}},
                {"type": "toolCall", "id": "t2", "name": "sessions_spawn",
                 "arguments": {"name": "calendar-scanner", "prompt": "Scan calendar."}},
            ]}},
        ],
    }


def test_extract_spawn_calls_in_order():
    calls = extract_spawn_calls(_parent_with_spawns()["messages"])
    assert [c["name"] for c in calls] == ["gmail-scanner", "calendar-scanner"]
    assert calls[0]["prompt"] == "Scan Gmail."


def test_build_child_trajectory_schema():
    child = build_child_trajectory(
        session_key="agent:main:subagent:aaa",
        raw_messages=[
            {"type": "message", "id": "c0", "message": {"role": "user",
             "content": [{"type": "text", "text": "Scan Gmail."}]}},
            {"type": "message", "id": "c1", "message": {"role": "assistant",
             "content": [{"type": "text", "text": "done"}]}},
        ],
        name="gmail-scanner",
        description="Scan Gmail.",
        parent_session="agent:main:dashboard:root",
    )
    meta = child["meta_info"]
    # Exact reference key set + order.
    assert list(meta.keys()) == [
        "task_name", "task_description", "task_completion_status",
        "parent_session", "session_key", "platform", "message_count",
    ]
    assert meta["task_name"] == "gmail-scanner"
    assert meta["session_key"] == "agent:main:subagent:aaa"
    assert meta["parent_session"] == "agent:main:dashboard:root"
    assert meta["message_count"] == 2
    # parentId threading reconstructed.
    assert child["messages"][0]["parentId"] == ""
    assert child["messages"][1]["parentId"] == "c0"


def test_write_golden_layout_full(tmp_path: Path):
    parent = _parent_with_spawns()
    children_sessions = [
        {"session_key": "agent:main:subagent:aaa", "completion_status": "success",
         "raw_messages": [{"type": "message", "id": "a0",
                           "message": {"role": "assistant", "content": [{"type": "text", "text": "gmail done"}]}}]},
        {"session_key": "agent:main:subagent:bbb", "completion_status": "success",
         "raw_messages": [{"type": "message", "id": "b0",
                           "message": {"role": "assistant", "content": [{"type": "text", "text": "cal done"}]}}]},
    ]
    out = tmp_path / "run_1"
    parent_doc = write_golden_layout(
        out,
        parent_published=parent,
        children_sessions=children_sessions,
        root_session="agent:main:dashboard:root",
        cluster="create_and_act",
    )

    # parent.json
    pj = json.loads((out / "parent.json").read_text())
    assert list(pj["meta_info"].keys()) == [
        "cluster", "task_type", "task_description", "task_completion_status",
        "system_prompt", "platform", "agents",
    ]
    assert pj["meta_info"]["agents"] == {
        "root": "agent:main:dashboard:root",
        "spawned": ["agent:main:subagent:aaa", "agent:main:subagent:bbb"],
    }
    assert parent_doc["meta_info"]["cluster"] == "create_and_act"

    # children/NN_<name>.json — named from the parent's spawn calls, in order.
    kids = sorted((out / "children").iterdir())
    assert [k.name for k in kids] == ["01_gmail-scanner.json", "02_calendar-scanner.json"]
    c0 = json.loads(kids[0].read_text())
    assert c0["meta_info"]["task_name"] == "gmail-scanner"
    assert c0["meta_info"]["task_description"] == "Scan Gmail."
    assert c0["meta_info"]["session_key"] == "agent:main:subagent:aaa"

    # spawn_tree
    tree = (out / "spawn_tree" / "parent_spawn_tree.txt").read_text()
    assert "Children: 2" in tree
    assert "gmail-scanner" in tree


def test_write_golden_layout_no_children(tmp_path: Path):
    """Zero spawns: parent.json written, no children/ dir, empty spawned list."""
    parent = {
        "meta_info": {"task_type": "t", "task_description": "d",
                      "task_completion_status": "success", "system_prompt": "s", "platform": "linux"},
        "messages": [{"type": "message", "id": "m0",
                      "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}}],
    }
    out = tmp_path / "run_solo"
    write_golden_layout(out, parent_published=parent, children_sessions=[],
                        root_session="agent:main:dashboard:r", cluster="c")
    assert (out / "parent.json").is_file()
    assert not (out / "children").exists()
    pj = json.loads((out / "parent.json").read_text())
    assert pj["meta_info"]["agents"]["spawned"] == []
