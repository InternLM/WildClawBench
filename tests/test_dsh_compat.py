import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agents.dsh.compat_transcript import convert_events, main

FIXTURE = Path(__file__).parent / "fixtures" / "dsh_session_sample.txt"


def _entries():
    return convert_events(FIXTURE.read_text().splitlines())


def test_converts_all_roles():
    entries = _entries()
    assert [e["type"] for e in entries] == ["message", "message", "toolResult", "message"]
    assert [e["message"]["role"] for e in entries if e["type"] == "message"] == \
        ["user", "assistant", "assistant"]


def test_assistant_usage_maps_openai_keys():
    u = _entries()[1]["message"]["usage"]
    assert u["input"] == 45096 and u["output"] == 161 and u["totalTokens"] == 45257
    assert u["cacheRead"] == 0 and u["cacheWrite"] == 0


def test_reasoning_dropped_toolcalls_kept():
    blocks = _entries()[1]["message"]["content"]
    assert [b.get("type") for b in blocks] == ["text", "tool_use"]
    assert blocks[1]["name"] == "bash" and blocks[1]["id"] == "call-1"
    assert blocks[1]["input"] == {"command": "ls"}


def test_tool_result_text_extracted():
    tr = _entries()[2]["toolResult"]
    assert tr["tool_call_id"] == "call-1" and tr["content"] == "a.txt"


def test_main_writes_jsonl(tmp_path):
    out = tmp_path / "chat.jsonl"
    assert main(["--uncompressed-file", str(FIXTURE), "--out", str(out)]) == 0
    rows = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
    assert len(rows) == 4


def test_missing_input_writes_empty(tmp_path):
    out = tmp_path / "chat.jsonl"
    assert main(["--uncompressed-file", "/nonexistent", "--out", str(out)]) == 0
    assert out.read_text() == ""
