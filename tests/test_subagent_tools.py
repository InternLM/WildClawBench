from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import subagent_tools as st  # noqa: E402


@pytest.fixture
def tmp_root(monkeypatch):
    d = Path(tempfile.mkdtemp(prefix="wcb_tools_")).resolve()
    monkeypatch.setattr(
        st,
        "_ALLOWED_PATH_PREFIXES",
        (str(d), "/tmp_workspace", "/root", "/tmp"),
    )
    yield d


def test_available_tools_lists_all_six():
    assert set(st.available_tools()) == {
        "Read",
        "Write",
        "Edit",
        "Grep",
        "Glob",
        "Bash",
    }


def test_schemas_for_filters_to_known_names():
    schemas = st.schemas_for(["Read", "Write", "DoesNotExist"])
    names = [s["name"] for s in schemas]
    assert names == ["Read", "Write"]


def test_schemas_for_dedupes():
    schemas = st.schemas_for(["Read", "Read", "Read"])
    assert len(schemas) == 1


def test_schemas_for_empty():
    assert st.schemas_for([]) == []


def test_dispatch_unknown_tool_returns_error_string():
    out = st.dispatch("Nope", {})
    assert out.startswith("ERROR: unknown tool")


def test_dispatch_never_raises_on_bad_input():
    out = st.dispatch("Read", {"path": None})
    assert out.startswith("ERROR:")


def test_read_happy_path(tmp_root):
    p = tmp_root / "a.txt"
    p.write_text("hello world", encoding="utf-8")
    assert st.dispatch("Read", {"path": str(p)}) == "hello world"


def test_read_missing_file(tmp_root):
    out = st.dispatch("Read", {"path": str(tmp_root / "nope.txt")})
    assert "does not exist" in out


def test_read_directory_returns_error(tmp_root):
    out = st.dispatch("Read", {"path": str(tmp_root)})
    assert "directory" in out


def test_read_rejects_path_outside_whitelist():
    out = st.dispatch("Read", {"path": "/etc/passwd"})
    assert "permission denied" in out


def test_read_rejects_empty_path():
    out = st.dispatch("Read", {"path": ""})
    assert "permission denied" in out


def test_write_creates_parent_and_file(tmp_root):
    target = tmp_root / "nested" / "deep" / "file.txt"
    out = st.dispatch("Write", {"path": str(target), "content": "abc"})
    assert "wrote 3 chars" in out
    assert target.read_text() == "abc"


def test_write_overwrites(tmp_root):
    p = tmp_root / "x.txt"
    p.write_text("old")
    st.dispatch("Write", {"path": str(p), "content": "new"})
    assert p.read_text() == "new"


def test_write_rejects_outside(tmp_root):
    out = st.dispatch("Write", {"path": "/etc/wcb_test", "content": "x"})
    assert "permission denied" in out


def test_edit_single_match(tmp_root):
    p = tmp_root / "x.txt"
    p.write_text("alpha beta gamma")
    out = st.dispatch(
        "Edit",
        {"path": str(p), "old_string": "beta", "new_string": "BETA"},
    )
    assert out.startswith("edited")
    assert p.read_text() == "alpha BETA gamma"


def test_edit_zero_matches_errors(tmp_root):
    p = tmp_root / "x.txt"
    p.write_text("alpha")
    out = st.dispatch(
        "Edit",
        {"path": str(p), "old_string": "beta", "new_string": "x"},
    )
    assert "not found" in out
    assert p.read_text() == "alpha"


def test_edit_multiple_matches_errors(tmp_root):
    p = tmp_root / "x.txt"
    p.write_text("aa aa aa")
    out = st.dispatch(
        "Edit",
        {"path": str(p), "old_string": "aa", "new_string": "bb"},
    )
    assert "matches 3 times" in out
    assert p.read_text() == "aa aa aa"


def test_edit_empty_old_string_errors(tmp_root):
    p = tmp_root / "x.txt"
    p.write_text("alpha")
    out = st.dispatch(
        "Edit",
        {"path": str(p), "old_string": "", "new_string": "x"},
    )
    assert "old_string is required" in out


def test_edit_missing_file_errors(tmp_root):
    out = st.dispatch(
        "Edit",
        {
            "path": str(tmp_root / "nope.txt"),
            "old_string": "a",
            "new_string": "b",
        },
    )
    assert "does not exist" in out


def test_grep_finds_matches_in_directory(tmp_root):
    (tmp_root / "a.txt").write_text("foo\nbar\nfoo bar\n")
    (tmp_root / "b.txt").write_text("nothing here\n")
    out = st.dispatch("Grep", {"pattern": "foo", "path": str(tmp_root)})
    assert "foo" in out
    assert "a.txt" in out
    assert "b.txt" not in out


def test_grep_no_matches(tmp_root):
    (tmp_root / "a.txt").write_text("hello\n")
    out = st.dispatch("Grep", {"pattern": "zzz", "path": str(tmp_root)})
    assert out == "no matches"


def test_grep_single_file(tmp_root):
    p = tmp_root / "a.txt"
    p.write_text("line1\nline2\n")
    out = st.dispatch("Grep", {"pattern": "line2", "path": str(p)})
    assert "line2" in out


def test_grep_bad_regex_errors(tmp_root):
    out = st.dispatch("Grep", {"pattern": "[", "path": str(tmp_root)})
    assert "bad regex" in out


def test_grep_missing_pattern_errors(tmp_root):
    out = st.dispatch("Grep", {"path": str(tmp_root)})
    assert "pattern is required" in out


def test_grep_caps_at_max(tmp_root, monkeypatch):
    monkeypatch.setattr(st, "_GREP_MAX_MATCHES", 3)
    (tmp_root / "a.txt").write_text("x\n" * 50)
    out = st.dispatch("Grep", {"pattern": "x", "path": str(tmp_root)})
    assert "truncated at 3 matches" in out


def test_glob_lists_matches(tmp_root):
    (tmp_root / "a.py").write_text("")
    (tmp_root / "b.py").write_text("")
    (tmp_root / "c.txt").write_text("")
    out = st.dispatch("Glob", {"pattern": "*.py", "path": str(tmp_root)})
    assert "a.py" in out
    assert "b.py" in out
    assert "c.txt" not in out


def test_glob_no_matches(tmp_root):
    out = st.dispatch("Glob", {"pattern": "*.nothing", "path": str(tmp_root)})
    assert out == "no matches"


def test_glob_missing_root_errors(tmp_root):
    out = st.dispatch(
        "Glob", {"pattern": "*", "path": str(tmp_root / "no_such_dir")}
    )
    assert "does not exist" in out


def test_bash_echo(tmp_root, monkeypatch):
    monkeypatch.chdir(tmp_root)
    out = st.dispatch("Bash", {"command": "echo hello"})
    assert "[exit=0]" in out
    assert "hello" in out


def test_bash_nonzero_exit(tmp_root, monkeypatch):
    monkeypatch.chdir(tmp_root)
    out = st.dispatch("Bash", {"command": "false"})
    assert "[exit=1]" in out


def test_bash_empty_command_errors():
    out = st.dispatch("Bash", {"command": "   "})
    assert "command is required" in out


def test_bash_timeout_clamps(tmp_root, monkeypatch):
    monkeypatch.chdir(tmp_root)
    out = st.dispatch("Bash", {"command": "sleep 5", "timeout": 1})
    assert "timed out after 1s" in out


def test_bash_stdout_tailed(tmp_root, monkeypatch):
    monkeypatch.chdir(tmp_root)
    monkeypatch.setattr(st, "_BASH_STDOUT_TAIL", 10)
    out = st.dispatch("Bash", {"command": "printf 'abcdefghijklmnopqrstuvwxyz'"})
    assert "qrstuvwxyz" in out
    assert "abc" not in out.split("stdout:")[1].split("stderr:")[0]
