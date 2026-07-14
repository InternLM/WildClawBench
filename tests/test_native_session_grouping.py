"""Tests for native sessions_spawn child harvesting (jsonl_reader.read_sessions_grouped).

Fixtures mirror the real on-disk OpenClaw session format confirmed from captured
chat.jsonl: each session file starts with a {"type":"session","id":...} header,
followed by message entries. The main headless run is session id "chat"; native
sessions_spawn children are separate files with their own header id.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.jsonl_reader import read_sessions_grouped  # noqa: E402


def _write_session(sessions_dir: Path, filename: str, session_id: str, msgs):
    """Write one OpenClaw-shaped session .jsonl with a header + message entries."""
    path = sessions_dir / filename
    lines = [{"type": "session", "version": 3, "id": session_id, "cwd": "/root"}]
    lines.extend(msgs)
    path.write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    return path


def _sessions_dir(workdir: Path, persona: str) -> Path:
    d = workdir / "data" / persona / "agents" / "main" / "sessions"
    d.mkdir(parents=True)
    return d


def test_groups_main_and_children_by_header_id(tmp_path: Path):
    persona = "jae"
    sdir = _sessions_dir(tmp_path, persona)
    main = _write_session(
        sdir, "chat.jsonl", "chat",
        [{"type": "message", "id": "m1", "message": {"role": "user", "content": "hi"}}],
    )
    c1 = _write_session(
        sdir, "sub1.jsonl", "agent:main:subagent:aaa",
        [{"type": "message", "id": "x1", "message": {"role": "user", "content": "child A"}}],
    )
    c2 = _write_session(
        sdir, "sub2.jsonl", "agent:main:subagent:bbb",
        [{"type": "message", "id": "y1", "message": {"role": "user", "content": "child B"}}],
    )
    # Force a deterministic spawn order via mtime: c1 before c2.
    os.utime(main, (1000, 1000))
    os.utime(c1, (2000, 2000))
    os.utime(c2, (3000, 3000))

    grouped = read_sessions_grouped(tmp_path, persona)

    # main carries only the chat session's entries (header + 1 message).
    assert any(e.get("id") == "m1" for e in grouped["main"])
    assert not any("child" in json.dumps(e) for e in grouped["main"])
    # two children, keyed by their header session id, not concatenated into main.
    assert set(grouped["children"]) == {
        "agent:main:subagent:aaa",
        "agent:main:subagent:bbb",
    }
    assert any(e.get("id") == "x1" for e in grouped["children"]["agent:main:subagent:aaa"])
    # children dict preserves mtime/spawn order.
    assert list(grouped["children"]) == [
        "agent:main:subagent:aaa",
        "agent:main:subagent:bbb",
    ]


def test_no_children_when_only_main(tmp_path: Path):
    persona = "jae"
    sdir = _sessions_dir(tmp_path, persona)
    _write_session(
        sdir, "chat.jsonl", "chat",
        [{"type": "message", "id": "m1", "message": {"role": "user", "content": "hi"}}],
    )
    grouped = read_sessions_grouped(tmp_path, persona)
    assert grouped["children"] == {}
    assert any(e.get("id") == "m1" for e in grouped["main"])


def test_headerless_file_folds_into_main(tmp_path: Path):
    """A file with no session header is treated as main (backward compatible)."""
    persona = "jae"
    sdir = _sessions_dir(tmp_path, persona)
    (sdir / "legacy.jsonl").write_text(
        json.dumps({"type": "message", "id": "z1", "message": {"role": "user", "content": "x"}}) + "\n"
    )
    grouped = read_sessions_grouped(tmp_path, persona)
    assert grouped["children"] == {}
    assert any(e.get("id") == "z1" for e in grouped["main"])


def test_custom_main_session_id(tmp_path: Path):
    """The parent session id is parameterized (runner may not use 'chat')."""
    persona = "jae"
    sdir = _sessions_dir(tmp_path, persona)
    _write_session(
        sdir, "root.jsonl", "main-123",
        [{"type": "message", "id": "m1", "message": {"role": "user", "content": "hi"}}],
    )
    _write_session(
        sdir, "kid.jsonl", "agent:main:subagent:ccc",
        [{"type": "message", "id": "k1", "message": {"role": "user", "content": "kid"}}],
    )
    grouped = read_sessions_grouped(tmp_path, persona, main_session_id="main-123")
    assert any(e.get("id") == "m1" for e in grouped["main"])
    assert set(grouped["children"]) == {"agent:main:subagent:ccc"}


def test_missing_sessions_dir_returns_empty(tmp_path: Path):
    grouped = read_sessions_grouped(tmp_path, "nobody")
    assert grouped == {"main": [], "children": {}}
