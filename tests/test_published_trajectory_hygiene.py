"""Published-trajectory hygiene: output.json must not carry per-turn usage/cost
or raw infra-failure noise from tool results (see builder._scrub_published_message).

The rich in-memory trajectory must be left untouched so grading still sees what
the agent actually saw.
"""

from src.utils.trajectory.builder import (
    _neutralize_infra_text,
    build_published_trajectory,
)

# Canonical inner-message keys per Golden_Trajectory.json.
_CANON_COMMON = {"role", "content"}
_CANON_TOOLRESULT = {"role", "content", "toolCallId", "toolName", "isError"}


class _Task:
    task_type = "research_and_analysis"
    task_description = "desc"
    system_prompt = "sys"


def _rich(*inner_messages):
    return {"messages": [
        {"type": "message", "id": f"id{i}", "parentId": "",
         "timestamp": "2026-06-16T00:00:00Z", "message": m, "turn_index": i}
        for i, m in enumerate(inner_messages)
    ]}


def _tool_result(text):
    return {"role": "toolResult", "toolName": "exec",
            "content": [{"type": "text", "text": text}]}


def test_per_turn_usage_is_dropped():
    rich = _rich(
        {"role": "assistant",
         "content": [{"type": "text", "text": "ok"}],
         "usage": {"input": 10, "output": 5, "cost": {"total": 0.01}}},
    )
    out = build_published_trajectory(rich, _Task(), "success")
    assert "usage" not in out["messages"][0]["message"]
    # rich source untouched -> grading/usage aggregation still works
    assert rich["messages"][0]["message"]["usage"]["cost"]["total"] == 0.01


def test_infra_noise_in_tool_result_is_neutralized():
    noisy = (
        "*   Trying 172.18.0.4:8035...\n"
        "* connect to 172.18.0.4 port 8035 failed: Connection refused\n"
        "* Closing connection 0"
    )
    rich = _rich(_tool_result(noisy))
    out = build_published_trajectory(rich, _Task(), "success")
    txt = out["messages"][0]["message"]["content"][0]["text"]
    assert "Connection refused" not in txt
    assert txt.startswith("[tool output omitted")
    # original tool output preserved in the rich trajectory
    assert "Connection refused" in rich["messages"][0]["message"]["content"][0]["text"]


def test_each_infra_signature_fires():
    cases = [
        "* connect to 172.18.0.4 port 8000 failed: Connection refused",
        "ModuleNotFoundError: No module named 'fitz'\n(Command exited with code 1)",
        "ERROR: Could not find a version that satisfies the requirement openpyxl",
        "Failed to establish a new connection: [Errno -3] Temporary failure in name resolution",
        "sh: 1: pdftotext: not found",
        "< HTTP/1.1 500 Internal Server Error",
        "Internal Server Error",  # bare 500 body, no numeric prefix
        '{"detail":"Not Found"}---{"detail":"Not Found"}---{"detail":"Not Found"}',
        # mixed probe wall with a multi-line ZERO_RESULTS json fragment
        '{"detail":"Not Found"}---\n{\n    "status": "ZERO_RESULTS",\n    "results": []\n}',
    ]
    for text in cases:
        assert _neutralize_infra_text(text) is not None, text


def test_assistant_text_is_never_rewritten():
    # The model's own narration is genuine run content, not infra noise.
    narration = "Honest: Gmail is down right now — 500 Internal Server Error on the inbox."
    rich = _rich({"role": "assistant",
                  "content": [{"type": "text", "text": narration}]})
    out = build_published_trajectory(rich, _Task(), "success")
    assert out["messages"][0]["message"]["content"][0]["text"] == narration


def test_legitimate_tool_output_is_untouched():
    real = "AGENTS.md\nfile_1.pdf\nimg_1.jpg\ntext_1.txt\n"
    assert _neutralize_infra_text(real) is None
    # a real geocoding hit that merely mentions a status must survive
    assert _neutralize_infra_text('{"status":"OK","results":[{"name":"Rockland"}]}') is None


def test_reply_token_stripped_from_assistant_only():
    rich = _rich(
        {"role": "assistant",
         "content": [{"type": "text", "text": "[[reply_to_current]] Here's the picture."}]},
        {"role": "user",
         "content": [{"type": "text", "text": "[[reply_to_current]] verbatim user text"}]},
    )
    out = build_published_trajectory(rich, _Task(), "success")
    assert out["messages"][0]["message"]["content"][0]["text"] == "Here's the picture."
    # user text is never rewritten
    assert "[[reply_to_current]]" in out["messages"][1]["message"]["content"][0]["text"]


def test_only_canonical_inner_keys_remain():
    rich = _rich(
        {"role": "assistant", "content": [{"type": "text", "text": "ok"}],
         "api": "anthropic-messages", "provider": "anthropic", "model": "claude-opus-4.7",
         "stopReason": "stop", "timestamp": "t", "usage": {"cost": {"total": 1}}},
        {"role": "toolResult", "toolCallId": "tc1", "toolName": "exec", "isError": False,
         "details": {"x": 1}, "timestamp": "t", "content": [{"type": "text", "text": "ls"}]},
    )
    out = build_published_trajectory(rich, _Task(), "success")
    assert set(out["messages"][0]["message"]) == _CANON_COMMON
    assert set(out["messages"][1]["message"]) == _CANON_TOOLRESULT


def test_parent_id_threaded():
    rich = _rich(
        {"role": "user", "content": [{"type": "text", "text": "hi"}]},
        {"role": "assistant", "content": [{"type": "text", "text": "yo"}]},
        {"role": "user", "content": [{"type": "text", "text": "more"}]},
    )
    msgs = build_published_trajectory(rich, _Task(), "success")["messages"]
    assert msgs[0]["parentId"] == ""               # root has no parent
    assert msgs[1]["parentId"] == msgs[0]["id"]     # threaded to previous id
    assert msgs[2]["parentId"] == msgs[1]["id"]
    assert list(msgs[0].keys()) == ["type", "id", "parentId", "timestamp", "message"]


def test_mock_hostname_redacted_in_tool_result():
    text = ("*   Trying 172.18.0.4:8017...\n"
            "* Connected to mocks-task-alden_002_haul_out_week-744148 (172.18.0.4) port 8017\n"
            "> Host: mocks-task-alden_002_haul_out_week-744148:8017\n"
            "{\"ok\": true}")
    rich = _rich({"role": "toolResult", "toolCallId": "t", "toolName": "exec",
                  "isError": False, "content": [{"type": "text", "text": text}]})
    out = build_published_trajectory(rich, _Task(), "success")["messages"][0]
    cleaned = out["message"]["content"][0]["text"]
    assert "mocks-task-alden_002_haul_out_week-744148" not in cleaned
    assert "mock-services" in cleaned
    assert '{"ok": true}' in cleaned  # real payload preserved
