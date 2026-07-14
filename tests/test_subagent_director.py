from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.subagent_director import (  # noqa: E402
    SubagentResult,
    SubagentSpec,
    _build_system_prompt,
    append_spawn_row,
    read_current_turn,
    run_with_invoker,
    write_subagent_delivery,
)


def _ok_invoker(_sys: str, _usr: str, _spec: SubagentSpec) -> Mapping[str, Any]:
    return {
        "output": "hello world",
        "tool_calls": 2,
        "tokens_in": 11,
        "tokens_out": 22,
    }


def test_from_dict_basic_shape():
    spec = SubagentSpec.from_dict(
        {
            "role": "budget-extractor",
            "instructions": "Pull budget totals.",
            "allowed_tools": ["read_file", "grep"],
            "context": "Files in /work",
            "model": "claude-haiku-4-5",
            "max_tool_calls": 10,
            "max_tokens": 1024,
            "timeout_seconds": 60,
        }
    )
    assert spec.role == "budget-extractor"
    assert spec.allowed_tools == ("read_file", "grep")
    assert spec.model == "claude-haiku-4-5"
    assert spec.max_tool_calls == 10


def test_from_dict_rejects_non_list_tools():
    with pytest.raises(ValueError):
        SubagentSpec.from_dict({"role": "r", "instructions": "i", "allowed_tools": "read_file"})


def test_run_with_invoker_happy_path():
    spec = SubagentSpec(role="extractor", instructions="Do the thing.")
    res = run_with_invoker(spec, _ok_invoker)
    assert res.status == "ok"
    assert res.output == "hello world"
    assert res.tool_calls == 2
    assert res.tokens_in == 11
    assert res.tokens_out == 22
    assert res.spawn_id.startswith("spw_")


def test_run_with_invoker_blocks_nested_spawn():
    spec = SubagentSpec(
        role="r",
        instructions="i",
        allowed_tools=("read_file", "spawn_subagent"),
    )
    res = run_with_invoker(spec, _ok_invoker)
    assert res.status == "blocked"
    assert "nested" in (res.error or "")
    assert res.output == ""


def test_run_with_invoker_blocks_missing_role():
    spec = SubagentSpec(role="", instructions="i")
    res = run_with_invoker(spec, _ok_invoker)
    assert res.status == "blocked"
    assert "role" in (res.error or "")


def test_run_with_invoker_blocks_missing_instructions():
    spec = SubagentSpec(role="r", instructions="   ")
    res = run_with_invoker(spec, _ok_invoker)
    assert res.status == "blocked"


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("max_tool_calls", -1),
        ("max_tool_calls", 9999),
        ("max_tokens", 0),
        ("timeout_seconds", 0),
        ("timeout_seconds", 10**9),
    ],
)
def test_run_with_invoker_clamps_out_of_range(field, bad_value):
    kwargs = dict(role="r", instructions="i")
    kwargs[field] = bad_value
    spec = SubagentSpec(**kwargs)
    res = run_with_invoker(spec, _ok_invoker)
    assert res.status == "blocked"
    assert field in (res.error or "")


def test_run_with_invoker_timeout():
    def slow(_s, _u, _spec):
        raise TimeoutError("model never replied")

    res = run_with_invoker(SubagentSpec(role="r", instructions="i"), slow)
    assert res.status == "timeout"
    assert "never replied" in (res.error or "")


def test_run_with_invoker_generic_error_surfaces():
    def boom(_s, _u, _spec):
        raise RuntimeError("upstream 503")

    res = run_with_invoker(SubagentSpec(role="r", instructions="i"), boom)
    assert res.status == "error"
    assert "RuntimeError" in (res.error or "")


def test_run_with_invoker_rejects_non_mapping_return():
    def junk(_s, _u, _spec):
        return "not a dict"  # type: ignore[return-value]

    res = run_with_invoker(SubagentSpec(role="r", instructions="i"), junk)
    assert res.status == "error"
    assert "non-mapping" in (res.error or "")


def test_build_system_prompt_mentions_constraints():
    spec = SubagentSpec(
        role="reconciler",
        instructions="x",
        allowed_tools=("read_file", "grep"),
        max_tool_calls=7,
    )
    prompt = _build_system_prompt(spec)
    assert "reconciler" in prompt
    assert "read_file" in prompt and "grep" in prompt
    assert "MUST NOT spawn" in prompt
    assert "7" in prompt


def test_build_system_prompt_handles_no_tools():
    spec = SubagentSpec(role="r", instructions="x")
    prompt = _build_system_prompt(spec)
    assert "(none" in prompt


def test_to_log_row_truncates_preview_and_hashes_full():
    spec = SubagentSpec(role="r", instructions="i", allowed_tools=("read_file",))
    long_out = "abc" * 500
    result = SubagentResult(
        spawn_id="spw_test1234",
        role="r",
        output=long_out,
        tool_calls=3,
        tokens_in=10,
        tokens_out=20,
        elapsed_seconds=0.123,
        status="ok",
    )
    row = result.to_log_row(spec=spec, turn_index=4, parent_session_id="ses_abc")
    assert row["spawn_id"] == "spw_test1234"
    assert row["turn_index"] == 4
    assert row["parent_session_id"] == "ses_abc"
    assert row["allowed_tools"] == ["read_file"]
    assert len(row["output_preview"]) == 240
    assert row["output_chars"] == len(long_out)
    assert len(row["output_sha256"]) == 64


def test_read_current_turn_missing_returns_minus_one(tmp_path: Path):
    assert read_current_turn(tmp_path / "absent") == -1


def test_read_current_turn_parses_int(tmp_path: Path):
    p = tmp_path / "turn"
    p.write_text("7\n")
    assert read_current_turn(p) == 7


def test_read_current_turn_malformed_returns_minus_one(tmp_path: Path):
    p = tmp_path / "turn"
    p.write_text("not-a-number")
    assert read_current_turn(p) == -1


def test_append_spawn_row_writes_ndjson(tmp_path: Path):
    path = tmp_path / "tree" / "spawn_tree.jsonl"
    append_spawn_row({"a": 1}, spawn_tree_path=path)
    append_spawn_row({"b": 2}, spawn_tree_path=path)
    lines = path.read_text().splitlines()
    assert [json.loads(l) for l in lines] == [{"a": 1}, {"b": 2}]


def test_write_subagent_delivery_basic_shape(tmp_path: Path):
    spec = SubagentSpec(role="reconciler", instructions="Pull totals.")
    result = SubagentResult(
        spawn_id="spw_xyz",
        role="reconciler",
        output="done",
        tool_calls=0,
        tokens_in=1,
        tokens_out=2,
        elapsed_seconds=0.01,
        status="ok",
        rounds=[],
    )
    out_path = write_subagent_delivery(
        "spw_xyz",
        spec=spec,
        result=result,
        sys_prompt="SYS",
        usr_prompt="USR",
        transcript_dir=tmp_path,
    )
    assert out_path.name == "spw_xyz.delivery.json"
    payload = json.loads(out_path.read_text())
    meta = payload["meta_info"]
    assert meta["task_type"] == "reconciler"
    assert meta["task_description"] == "Pull totals."
    assert meta["task_completion_status"] == "completed"
    assert meta["system_prompt"] == "SYS"
    assert meta["platform"] == "linux"
    msgs = payload["messages"]
    assert msgs[0]["message"]["role"] == "system"
    assert msgs[0]["message"]["content"][0]["text"] == "SYS"
    assert msgs[0]["parentId"] is None
    assert msgs[1]["message"]["role"] == "user"
    assert msgs[1]["message"]["content"][0]["text"] == "USR"
    assert msgs[1]["parentId"] == msgs[0]["id"]
    assert msgs[0]["id"] == "spw_xyz:m0"
    assert msgs[1]["id"] == "spw_xyz:m1"


def test_write_subagent_delivery_status_to_completion_partial(tmp_path: Path):
    spec = SubagentSpec(role="r", instructions="i")
    result = SubagentResult(spawn_id="spw_t", role="r", output="", status="timeout")
    out_path = write_subagent_delivery(
        "spw_t", spec=spec, result=result,
        sys_prompt="S", usr_prompt="U", transcript_dir=tmp_path,
    )
    payload = json.loads(out_path.read_text())
    assert payload["meta_info"]["task_completion_status"] == "partial"


def test_write_subagent_delivery_converts_rounds_into_messages(tmp_path: Path):
    spec = SubagentSpec(role="r", instructions="i", allowed_tools=("Read",))
    rounds = [
        {
            "assistant_content": [
                {"type": "thinking", "thinking": "first I plan", "signature": "sig-abc"},
                {"type": "tool_use", "id": "tu_1", "name": "Read", "input": {"path": "/x"}},
            ],
            "tool_results": [
                {"tool_use_id": "tu_1", "content": "file contents", "is_error": False},
            ],
            "usage": {"input_tokens": 5, "output_tokens": 7},
        },
        {
            "assistant_content": [{"type": "text", "text": "final answer"}],
            "tool_results": [],
            "usage": {"input_tokens": 3, "output_tokens": 4},
        },
    ]
    result = SubagentResult(
        spawn_id="spw_abc",
        role="r",
        output="final answer",
        tool_calls=1,
        status="ok",
        rounds=rounds,
    )
    out_path = write_subagent_delivery(
        "spw_abc", spec=spec, result=result,
        sys_prompt="S", usr_prompt="U", transcript_dir=tmp_path,
    )
    msgs = json.loads(out_path.read_text())["messages"]
    roles = [m["message"]["role"] for m in msgs]
    assert roles == ["system", "user", "assistant", "toolResult", "assistant"]
    asst1 = msgs[2]["message"]["content"]
    assert asst1[0] == {
        "type": "thinking",
        "thinking": "first I plan",
        "thinkingSignature": "sig-abc",
    }
    assert asst1[1] == {
        "type": "toolCall",
        "id": "tu_1",
        "name": "Read",
        "arguments": {"path": "/x"},
    }
    tr = msgs[3]["message"]
    assert tr["toolCallId"] == "tu_1"
    assert tr["toolName"] == "Read"
    assert tr["isError"] is False
    assert tr["content"][0]["text"] == "file contents"
    assert msgs[4]["message"]["content"][0] == {"type": "text", "text": "final answer"}
    parent_chain = [m["parentId"] for m in msgs]
    assert parent_chain[0] is None
    for i in range(1, len(msgs)):
        assert parent_chain[i] == msgs[i - 1]["id"]


def test_run_batch_parallel_runs_all_and_caps_at_five():
    from src.utils.subagent_director import run_batch_parallel

    specs = [
        SubagentSpec(role=f"r{i}", instructions=f"do {i}")
        for i in range(7)
    ]

    def _inv(_s, _u, spec):
        return {"output": f"hi-{spec.role}", "tokens_in": 1, "tokens_out": 2}

    results = run_batch_parallel(specs, _inv)
    assert len(results) == 7
    assert {r.status for r in results} == {"ok"}
    assert {r.role for r in results} == {f"r{i}" for i in range(7)}
    assert {r.output for r in results} == {f"hi-r{i}" for i in range(7)}


def test_run_batch_parallel_empty():
    from src.utils.subagent_director import run_batch_parallel
    assert run_batch_parallel([], _ok_invoker) == []


def _scripted_http_post(rounds):
    queue = list(rounds)

    def _post(_payload):
        if not queue:
            raise AssertionError("scripted http_post: no more rounds")
        return queue.pop(0)

    return _post


def test_drive_tool_loop_returns_text_when_no_tool_use():
    from src.utils.subagent_director import _drive_tool_loop

    body = {
        "content": [{"type": "text", "text": "final answer"}],
        "usage": {"input_tokens": 5, "output_tokens": 7},
    }
    result = _drive_tool_loop(
        http_post=_scripted_http_post([body]),
        tool_dispatch=lambda _n, _i: "should not be called",
        sys_prompt="S",
        usr_prompt="U",
        tools_schemas=[],
        model="m",
        max_tokens=100,
        max_tool_calls=5,
    )
    assert result["output"] == "final answer"
    assert result["tool_calls"] == 0
    assert result["tokens_in"] == 5
    assert result["tokens_out"] == 7


def test_drive_tool_loop_dispatches_tool_and_feeds_result_back():
    from src.utils.subagent_director import _drive_tool_loop

    round1 = {
        "content": [
            {"type": "tool_use", "id": "tu_1", "name": "Read", "input": {"path": "/x"}},
        ],
        "usage": {"input_tokens": 3, "output_tokens": 4},
    }
    round2 = {
        "content": [{"type": "text", "text": "file says hi"}],
        "usage": {"input_tokens": 6, "output_tokens": 8},
    }
    dispatched: list[tuple[str, dict]] = []

    def _dispatch(name, tool_input):
        dispatched.append((name, dict(tool_input)))
        return "hi"

    result = _drive_tool_loop(
        http_post=_scripted_http_post([round1, round2]),
        tool_dispatch=_dispatch,
        sys_prompt="S",
        usr_prompt="U",
        tools_schemas=[{"name": "Read"}],
        model="m",
        max_tokens=100,
        max_tool_calls=5,
    )
    assert result["output"] == "file says hi"
    assert result["tool_calls"] == 1
    assert dispatched == [("Read", {"path": "/x"})]
    assert result["tokens_in"] == 9
    assert result["tokens_out"] == 12


def test_drive_tool_loop_budget_exhaustion_marks_error_and_continues():
    from src.utils.subagent_director import _drive_tool_loop

    round1 = {
        "content": [
            {"type": "tool_use", "id": "tu_1", "name": "Read", "input": {}},
            {"type": "tool_use", "id": "tu_2", "name": "Read", "input": {}},
        ],
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }
    round2 = {
        "content": [{"type": "text", "text": "stopped"}],
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }

    result = _drive_tool_loop(
        http_post=_scripted_http_post([round1, round2]),
        tool_dispatch=lambda _n, _i: "ok",
        sys_prompt="S",
        usr_prompt="U",
        tools_schemas=[],
        model="m",
        max_tokens=100,
        max_tool_calls=1,
    )
    assert result["output"] == "stopped"
    assert result["tool_calls"] == 1


def test_drive_tool_loop_tool_exception_becomes_error_tool_result():
    from src.utils.subagent_director import _drive_tool_loop

    round1 = {
        "content": [
            {"type": "tool_use", "id": "tu_1", "name": "Bash", "input": {"cmd": "x"}},
        ],
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }
    round2 = {
        "content": [{"type": "text", "text": "recovered"}],
        "usage": {"input_tokens": 0, "output_tokens": 0},
    }

    def _dispatch(_n, _i):
        raise RuntimeError("boom")

    result = _drive_tool_loop(
        http_post=_scripted_http_post([round1, round2]),
        tool_dispatch=_dispatch,
        sys_prompt="S",
        usr_prompt="U",
        tools_schemas=[],
        model="m",
        max_tokens=100,
        max_tool_calls=5,
    )
    assert result["output"] == "recovered"
    assert result["tool_calls"] == 1


def test_extract_round_usage_pulls_anthropic_cache_fields():
    from src.utils.subagent_director import _extract_round_usage

    out = _extract_round_usage({
        "input_tokens": 100,
        "output_tokens": 50,
        "cache_read_input_tokens": 1200,
        "cache_creation_input_tokens": 800,
    })
    assert out == {
        "input_tokens": 100,
        "output_tokens": 50,
        "cache_read_tokens": 1200,
        "cache_write_tokens": 800,
    }


def test_extract_round_usage_defaults_missing_to_zero():
    from src.utils.subagent_director import _extract_round_usage

    assert _extract_round_usage(None) == {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    }
    assert _extract_round_usage({"input_tokens": 5}) == {
        "input_tokens": 5,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    }


def test_drive_tool_loop_accumulates_cache_tokens_across_rounds():
    from src.utils.subagent_director import _drive_tool_loop

    round1 = {
        "content": [
            {"type": "tool_use", "id": "tu_1", "name": "Read", "input": {"path": "/x"}},
        ],
        "usage": {
            "input_tokens": 3,
            "output_tokens": 4,
            "cache_read_input_tokens": 100,
            "cache_creation_input_tokens": 200,
        },
    }
    round2 = {
        "content": [{"type": "text", "text": "done"}],
        "usage": {
            "input_tokens": 6,
            "output_tokens": 8,
            "cache_read_input_tokens": 50,
            "cache_creation_input_tokens": 0,
        },
    }
    result = _drive_tool_loop(
        http_post=_scripted_http_post([round1, round2]),
        tool_dispatch=lambda _n, _i: "ok",
        sys_prompt="S",
        usr_prompt="U",
        tools_schemas=[{"name": "Read"}],
        model="m",
        max_tokens=100,
        max_tool_calls=5,
    )
    assert result["tokens_in"] == 9
    assert result["tokens_out"] == 12
    assert result["cache_read_tokens"] == 150
    assert result["cache_write_tokens"] == 200
    assert [r["usage"] for r in result["rounds"]] == [
        {"input_tokens": 3, "output_tokens": 4,
         "cache_read_tokens": 100, "cache_write_tokens": 200},
        {"input_tokens": 6, "output_tokens": 8,
         "cache_read_tokens": 50, "cache_write_tokens": 0},
    ]


def test_run_with_invoker_propagates_cache_fields():
    spec = SubagentSpec(role="r", instructions="i")

    def _inv(_s, _u, _spec):
        return {
            "output": "ok",
            "tokens_in": 1,
            "tokens_out": 2,
            "cache_read_tokens": 3,
            "cache_write_tokens": 4,
        }

    res = run_with_invoker(spec, _inv)
    assert res.cache_read_tokens == 3
    assert res.cache_write_tokens == 4
    assert res.total_tokens == 10


def test_subagent_result_total_tokens_property():
    r = SubagentResult(
        spawn_id="spw_x", role="r", output="",
        tokens_in=10, tokens_out=20,
        cache_read_tokens=300, cache_write_tokens=400,
    )
    assert r.total_tokens == 730


def test_to_log_row_includes_canonical_token_shape():
    spec = SubagentSpec(role="r", instructions="i")
    result = SubagentResult(
        spawn_id="spw_y", role="r", output="x",
        tokens_in=11, tokens_out=22,
        cache_read_tokens=33, cache_write_tokens=44,
    )
    row = result.to_log_row(spec=spec, turn_index=0, parent_session_id=None)
    assert row["input_tokens"] == 11
    assert row["output_tokens"] == 22
    assert row["cache_read_tokens"] == 33
    assert row["cache_write_tokens"] == 44
    assert row["total_tokens"] == 110
    assert row["tokens_in"] == 11
    assert row["tokens_out"] == 22


def test_write_subagent_delivery_includes_usage_in_meta(tmp_path: Path):
    spec = SubagentSpec(role="r", instructions="i")
    result = SubagentResult(
        spawn_id="spw_u", role="r", output="done",
        tokens_in=10, tokens_out=20,
        cache_read_tokens=5, cache_write_tokens=7,
        model="claude-opus-4-6", cost_usd=0.00075,
        status="ok",
    )
    out_path = write_subagent_delivery(
        "spw_u", spec=spec, result=result,
        sys_prompt="S", usr_prompt="U", transcript_dir=tmp_path,
    )
    meta = json.loads(out_path.read_text())["meta_info"]
    assert meta["usage"] == {
        "input_tokens": 10,
        "output_tokens": 20,
        "cache_read_tokens": 5,
        "cache_write_tokens": 7,
        "total_tokens": 42,
        "cost_usd": 0.00075,
    }


def test_summarize_results_aggregates_and_classifies():
    from src.utils.subagent_director import summarize_results

    rs = [
        SubagentResult(spawn_id="a", role="r", output="o",
                       tokens_in=10, tokens_out=20,
                       cache_read_tokens=5, cache_write_tokens=0,
                       tool_calls=1, elapsed_seconds=0.5, status="ok"),
        SubagentResult(spawn_id="b", role="r", output="",
                       tokens_in=0, tokens_out=0, status="timeout",
                       error="x"),
        SubagentResult(spawn_id="c", role="r", output="o2",
                       tokens_in=3, tokens_out=4,
                       cache_write_tokens=11, tool_calls=2,
                       elapsed_seconds=0.25, status="ok"),
    ]
    s = summarize_results(rs, scope="batch")
    assert s["kind"] == "summary"
    assert s["scope"] == "batch"
    assert s["n_spawns"] == 3
    assert s["n_ok"] == 2
    assert s["by_status"] == {"ok": 2, "timeout": 1}
    assert s["tool_calls"] == 3
    assert s["input_tokens"] == 13
    assert s["output_tokens"] == 24
    assert s["cache_read_tokens"] == 5
    assert s["cache_write_tokens"] == 11
    assert s["total_tokens"] == 53
    assert s["elapsed_seconds"] == 0.75
    assert "status" not in s  # so spawn_tree_checks does not count it


def test_summarize_results_empty():
    from src.utils.subagent_director import summarize_results
    s = summarize_results([], scope="batch")
    assert s["n_spawns"] == 0
    assert s["total_tokens"] == 0
    assert s["by_status"] == {}


def test_summarize_spawn_tree_reads_file_and_skips_summary_rows(tmp_path: Path):
    from src.utils.subagent_director import summarize_spawn_tree

    p = tmp_path / "spawn_tree.jsonl"
    p.write_text(
        json.dumps({"status": "ok", "input_tokens": 10, "output_tokens": 20,
                    "cache_read_tokens": 3, "cache_write_tokens": 4,
                    "tool_calls": 1, "elapsed_seconds": 0.1}) + "\n"
        + json.dumps({"status": "error", "input_tokens": 1, "output_tokens": 2,
                      "tool_calls": 0, "elapsed_seconds": 0.05}) + "\n"
        + json.dumps({"kind": "summary", "input_tokens": 9999,
                      "output_tokens": 9999}) + "\n"
        + json.dumps({"status": "ok", "tokens_in": 5, "tokens_out": 6,
                      "tool_calls": 1, "elapsed_seconds": 0.2}) + "\n"
    )
    s = summarize_spawn_tree(p)
    assert s["n_spawns"] == 3
    assert s["n_ok"] == 2
    assert s["by_status"] == {"ok": 2, "error": 1}
    assert s["input_tokens"] == 16
    assert s["output_tokens"] == 28
    assert s["cache_read_tokens"] == 3
    assert s["cache_write_tokens"] == 4
    assert s["total_tokens"] == 51
    assert s["tool_calls"] == 2


def test_summarize_spawn_tree_missing_file_returns_zero(tmp_path: Path):
    from src.utils.subagent_director import summarize_spawn_tree
    s = summarize_spawn_tree(tmp_path / "absent.jsonl")
    assert s["n_spawns"] == 0
    assert s["total_tokens"] == 0


def test_run_batch_main_appends_summary_row_and_keeps_stdout_light(
    tmp_path: Path, capsys
):
    from src.utils.subagent_director import _run_batch_main

    def _inv(_s, _u, spec):
        return {
            "output": f"reply-{spec.role}",
            "tokens_in": 10,
            "tokens_out": 20,
            "cache_read_tokens": 3,
            "cache_write_tokens": 4,
        }

    spawn_tree = tmp_path / "spawn_tree.jsonl"
    transcript_dir = tmp_path / "subagents"
    turn_marker = tmp_path / "turn"

    rc = _run_batch_main(
        [
            {"role": "a", "instructions": "x"},
            {"role": "b", "instructions": "y"},
        ],
        invoker=_inv,
        spawn_tree=spawn_tree,
        transcript_dir=transcript_dir,
        turn_marker=turn_marker,
    )
    assert rc == 0

    stdout_lines = [
        json.loads(l) for l in capsys.readouterr().out.strip().splitlines()
    ]
    assert len(stdout_lines) == 2
    for row in stdout_lines:
        assert set(row) == {
            "spawn_id", "role", "status", "output", "error",
            "tokens_in", "tokens_out", "tool_calls",
        }
        assert "cache_read_tokens" not in row
        assert "cache_write_tokens" not in row
        assert "total_tokens" not in row

    file_rows = [
        json.loads(l) for l in spawn_tree.read_text().splitlines() if l.strip()
    ]
    per_spawn = [r for r in file_rows if r.get("kind") != "summary"]
    summaries = [r for r in file_rows if r.get("kind") == "summary"]
    assert len(per_spawn) == 2
    assert len(summaries) == 1
    s = summaries[0]
    assert s["scope"] == "batch"
    assert s["n_spawns"] == 2
    assert s["n_ok"] == 2
    assert s["input_tokens"] == 20
    assert s["output_tokens"] == 40
    assert s["cache_read_tokens"] == 6
    assert s["cache_write_tokens"] == 8
    assert s["total_tokens"] == 74
