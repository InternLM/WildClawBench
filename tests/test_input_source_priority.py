"""Input-artifact source priority for native tasks.

The task loader sources input artifacts from <task>/persona/home/ when present
(and non-empty), otherwise falls back to <task>/data/. Whichever wins becomes the
task's `data_dir` (staged into the agent workspace at /root/workspace/home by
inject_data_into_workspace) and the source of the `attachments` list. These tests
pin that priority/fallback chain end to end via _load_native_task.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.task_parser import _load_native_task  # noqa: E402


def _mk_task(root: Path) -> Path:
    td = root / "task"
    td.mkdir(parents=True)
    (td / "prompt.txt").write_text("do the thing", encoding="utf-8")
    (td / "rubric.json").write_text("[]", encoding="utf-8")
    return td


def test_persona_home_takes_priority_over_data(tmp_path):
    td = _mk_task(tmp_path)
    (td / "data").mkdir()
    (td / "data" / "from_data.txt").write_text("D", encoding="utf-8")
    (td / "persona" / "home").mkdir(parents=True)
    (td / "persona" / "home" / "from_persona.txt").write_text("P", encoding="utf-8")

    t = _load_native_task(td)

    assert t["data_dir"] == str(td / "persona" / "home")
    names = sorted(a["name"] for a in t["attachments"])
    assert names == ["from_persona.txt"]
    # in-container destination metadata is unchanged (still under home/)
    assert t["attachments"][0]["storedAs"] == "home/from_persona.txt"


def test_falls_back_to_data_when_no_persona_home(tmp_path):
    td = _mk_task(tmp_path)
    (td / "data").mkdir()
    (td / "data" / "only_data.txt").write_text("D", encoding="utf-8")

    t = _load_native_task(td)

    assert t["data_dir"] == str(td / "data")
    assert [a["name"] for a in t["attachments"]] == ["only_data.txt"]


def test_empty_persona_home_falls_through_to_data(tmp_path):
    td = _mk_task(tmp_path)
    (td / "data").mkdir()
    (td / "data" / "only_data.txt").write_text("D", encoding="utf-8")
    (td / "persona" / "home").mkdir(parents=True)  # present but empty -> not masking

    t = _load_native_task(td)

    assert t["data_dir"] == str(td / "data")
    assert [a["name"] for a in t["attachments"]] == ["only_data.txt"]


def test_persona_home_nested_files_preserve_relative_path(tmp_path):
    td = _mk_task(tmp_path)
    (td / "persona" / "home" / "sub").mkdir(parents=True)
    (td / "persona" / "home" / "sub" / "doc.txt").write_text("X", encoding="utf-8")

    t = _load_native_task(td)

    assert t["data_dir"] == str(td / "persona" / "home")
    assert t["attachments"][0]["storedAs"] == "home/sub/doc.txt"


def test_neither_source_yields_empty(tmp_path):
    td = _mk_task(tmp_path)

    t = _load_native_task(td)

    assert t["data_dir"] == ""
    assert t["attachments"] == []
