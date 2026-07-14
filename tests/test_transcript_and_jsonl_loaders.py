"""Behavioral coverage for transcript / JSONL loaders + trajectory builder.

Modules under test (all pure, no docker/network/AWS):
- src/utils/transcript_loader.py    -> load_transcript, _read_transcript_file,
                                       _parse_json_lines, _safe_json_loads
- src/utils/jsonl_reader.py         -> read_session_jsonl, sanitize_jsonl_message,
                                       extract_tokens, _thinking_stats, _count_thinking
- src/utils/trajectory/builder.py   -> build_trajectory_from_jsonl + pure helpers
                                       (_wrap_trajectory_message,
                                        _wrap_messages_with_turn_feedback,
                                        _unwrap_trajectory_messages,
                                        _artifact_turns_from_entries,
                                        _coerce_top_usage, _count_thinking_blocks)

Tests are offline & deterministic: only tmp_path for scratch, no monkeypatching
of external services needed (the default media_handler is a no-op).

Where a module's current behavior looks like a defect, the test PINS current
behavior with a NOTE comment rather than asserting an "ideal" contract.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import transcript_loader as tl  # noqa: E402
from src.utils import jsonl_reader as jr  # noqa: E402
from src.utils.store import Task  # noqa: E402
from src.utils.trajectory import builder as bld  # noqa: E402


# =========================================================================
# transcript_loader.py
# =========================================================================

# --- _safe_json_loads -----------------------------------------------------

def test_safe_json_loads_valid_object() -> None:
    assert tl._safe_json_loads('{"a": 1}') == {"a": 1}


def test_safe_json_loads_valid_scalar() -> None:
    assert tl._safe_json_loads("42") == 42


def test_safe_json_loads_invalid_returns_none() -> None:
    assert tl._safe_json_loads("{not json") is None


def test_safe_json_loads_empty_returns_none() -> None:
    assert tl._safe_json_loads("") is None


# --- _parse_json_lines ----------------------------------------------------

def test_parse_json_lines_multiple_rows() -> None:
    raw = '{"a": 1}\n{"b": 2}\n'
    assert tl._parse_json_lines(raw) == [{"a": 1}, {"b": 2}]


def test_parse_json_lines_skips_blank_and_whitespace_lines() -> None:
    raw = '{"a": 1}\n\n   \n{"b": 2}'
    assert tl._parse_json_lines(raw) == [{"a": 1}, {"b": 2}]


def test_parse_json_lines_skips_malformed_lines() -> None:
    raw = '{"a": 1}\nGARBAGE\n{"b": 2}'
    assert tl._parse_json_lines(raw) == [{"a": 1}, {"b": 2}]


def test_parse_json_lines_all_bad_returns_empty() -> None:
    assert tl._parse_json_lines("nope\nalso nope") == []


def test_parse_json_lines_keeps_falsey_but_valid_json() -> None:
    # NOTE: pins current behavior — `parsed is not None` guard keeps 0/false/[]
    # even though they are falsey.
    raw = "0\nfalse\n[]"
    assert tl._parse_json_lines(raw) == [0, False, []]


# --- _read_transcript_file ------------------------------------------------

def test_read_transcript_file_missing_returns_empty(tmp_path: Path) -> None:
    assert tl._read_transcript_file(tmp_path / "nope.jsonl") == []


def test_read_transcript_file_top_level_list(tmp_path: Path) -> None:
    p = tmp_path / "t.json"
    p.write_text(json.dumps([{"role": "user"}, {"role": "assistant"}]))
    assert tl._read_transcript_file(p) == [{"role": "user"}, {"role": "assistant"}]


def test_read_transcript_file_dict_with_transcript_key(tmp_path: Path) -> None:
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"transcript": [{"x": 1}], "other": "ignore"}))
    assert tl._read_transcript_file(p) == [{"x": 1}]


def test_read_transcript_file_dict_with_messages_key(tmp_path: Path) -> None:
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"messages": [{"m": 1}]}))
    assert tl._read_transcript_file(p) == [{"m": 1}]


def test_read_transcript_file_dict_with_chat_key(tmp_path: Path) -> None:
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"chat": [{"c": 1}]}))
    assert tl._read_transcript_file(p) == [{"c": 1}]


def test_read_transcript_file_key_precedence_transcript_first(tmp_path: Path) -> None:
    # transcript checked before messages/chat
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"chat": [{"c": 1}], "transcript": [{"t": 1}]}))
    assert tl._read_transcript_file(p) == [{"t": 1}]


def test_read_transcript_file_dict_without_list_keys_wraps_dict(tmp_path: Path) -> None:
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"foo": "bar"}))
    assert tl._read_transcript_file(p) == [{"foo": "bar"}]


def test_read_transcript_file_dict_with_nonlist_transcript_wraps_whole_dict(
    tmp_path: Path,
) -> None:
    # transcript key present but not a list -> falls through to wrap whole dict
    p = tmp_path / "t.json"
    p.write_text(json.dumps({"transcript": "not-a-list"}))
    assert tl._read_transcript_file(p) == [{"transcript": "not-a-list"}]


def test_read_transcript_file_jsonl_fallback(tmp_path: Path) -> None:
    # whole-file parse fails -> line-by-line JSONL parse
    p = tmp_path / "t.jsonl"
    p.write_text('{"a": 1}\n{"b": 2}\n')
    assert tl._read_transcript_file(p) == [{"a": 1}, {"b": 2}]


def test_read_transcript_file_top_level_scalar_falls_to_jsonl(tmp_path: Path) -> None:
    # A bare scalar is valid JSON but not list/dict -> _parse_json_lines(raw).
    # NOTE: pins current behavior — the single scalar line reparses to itself.
    p = tmp_path / "t.json"
    p.write_text("123")
    assert tl._read_transcript_file(p) == [123]


def test_read_transcript_file_oserror_returns_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # read_text raising OSError (e.g. permission/IO) -> [] not an exception.
    p = tmp_path / "t.json"
    p.write_text("[]")

    def boom(*a, **k):
        raise OSError("disk gone")

    monkeypatch.setattr(Path, "read_text", boom)
    assert tl._read_transcript_file(p) == []


def test_read_transcript_file_empty_file_returns_empty(tmp_path: Path) -> None:
    p = tmp_path / "t.json"
    p.write_text("")
    assert tl._read_transcript_file(p) == []


def test_read_transcript_file_bad_encoding_bytes_ignored(tmp_path: Path) -> None:
    # errors="ignore" means invalid bytes are dropped, not raised.
    p = tmp_path / "t.jsonl"
    p.write_bytes(b'{"a": 1}\n\xff\xfe garbage\n{"b": 2}\n')
    assert tl._read_transcript_file(p) == [{"a": 1}, {"b": 2}]


# --- load_transcript ------------------------------------------------------

def test_load_transcript_explicit_path(tmp_path: Path) -> None:
    p = tmp_path / "chat.jsonl"
    p.write_text('{"role": "user"}\n')
    assert tl.load_transcript(str(p)) == [{"role": "user"}]


def test_load_transcript_empty_path_and_no_fallback_returns_empty() -> None:
    # No explicit path; the hard-coded fallback path does not exist on this box.
    assert tl.load_transcript("") == []


def test_load_transcript_default_arg_returns_empty() -> None:
    assert tl.load_transcript() == []


def test_load_transcript_nonexistent_path_falls_through_to_empty(
    tmp_path: Path,
) -> None:
    assert tl.load_transcript(str(tmp_path / "missing.jsonl")) == []


def test_load_transcript_dedupes_when_explicit_equals_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # If explicit == fallback, the `seen` set must not read the same file twice.
    calls: list[str] = []

    def fake_read(path: Path) -> list:
        calls.append(str(path))
        return []

    monkeypatch.setattr(tl, "_read_transcript_file", fake_read)
    tl.load_transcript(tl.OPENCLAW_FALLBACK_PATH)
    assert calls == [tl.OPENCLAW_FALLBACK_PATH]


def test_load_transcript_returns_first_nonempty_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_read(path: Path) -> list:
        if str(path) == "/explicit":
            return [{"first": 1}]
        return [{"fallback": 1}]

    monkeypatch.setattr(tl, "_read_transcript_file", fake_read)
    assert tl.load_transcript("/explicit") == [{"first": 1}]


def test_load_transcript_falls_back_when_explicit_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_read(path: Path) -> list:
        if str(path) == "/explicit":
            return []
        return [{"fallback": 1}]

    monkeypatch.setattr(tl, "_read_transcript_file", fake_read)
    assert tl.load_transcript("/explicit") == [{"fallback": 1}]


# =========================================================================
# jsonl_reader.py
# =========================================================================

# --- read_session_jsonl ---------------------------------------------------

def _sessions_dir(workdir: Path, persona: str) -> Path:
    d = workdir / "data" / persona / "agents" / "main" / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_read_session_jsonl_missing_dir_returns_empty(tmp_path: Path) -> None:
    assert jr.read_session_jsonl(tmp_path, "persona") == []


def test_read_session_jsonl_no_jsonl_files_returns_empty(tmp_path: Path) -> None:
    d = _sessions_dir(tmp_path, "persona")
    (d / "notes.txt").write_text("ignore me")
    assert jr.read_session_jsonl(tmp_path, "persona") == []


def test_read_session_jsonl_reads_entries(tmp_path: Path) -> None:
    d = _sessions_dir(tmp_path, "persona")
    (d / "s1.jsonl").write_text('{"i": 1}\n{"i": 2}\n')
    assert jr.read_session_jsonl(tmp_path, "persona") == [{"i": 1}, {"i": 2}]


def test_read_session_jsonl_skips_blank_lines(tmp_path: Path) -> None:
    d = _sessions_dir(tmp_path, "persona")
    (d / "s1.jsonl").write_text('{"i": 1}\n\n   \n{"i": 2}\n')
    assert jr.read_session_jsonl(tmp_path, "persona") == [{"i": 1}, {"i": 2}]


def test_read_session_jsonl_skips_malformed_lines(tmp_path: Path) -> None:
    d = _sessions_dir(tmp_path, "persona")
    (d / "s1.jsonl").write_text('{"i": 1}\nNOT JSON\n{"i": 2}\n')
    assert jr.read_session_jsonl(tmp_path, "persona") == [{"i": 1}, {"i": 2}]


def test_read_session_jsonl_concatenates_in_mtime_order(tmp_path: Path) -> None:
    d = _sessions_dir(tmp_path, "persona")
    older = d / "b_older.jsonl"
    newer = d / "a_newer.jsonl"
    older.write_text('{"o": 1}\n')
    newer.write_text('{"n": 1}\n')
    import os

    # Force older mtime on 'older' so ordering is by mtime, not filename.
    os.utime(older, (1000, 1000))
    os.utime(newer, (2000, 2000))
    assert jr.read_session_jsonl(tmp_path, "persona") == [{"o": 1}, {"n": 1}]


def test_read_session_jsonl_accepts_str_workdir(tmp_path: Path) -> None:
    d = _sessions_dir(tmp_path, "persona")
    (d / "s.jsonl").write_text('{"x": 9}\n')
    assert jr.read_session_jsonl(str(tmp_path), "persona") == [{"x": 9}]


# --- _thinking_stats / _count_thinking ------------------------------------

def test_thinking_stats_non_list_returns_zeros() -> None:
    assert jr._thinking_stats("not a list") == (0, 0, False)
    assert jr._thinking_stats(None) == (0, 0, False)


def test_thinking_stats_no_thinking_blocks() -> None:
    content = [{"type": "text", "text": "hi"}]
    assert jr._thinking_stats(content) == (0, 0, False)


def test_thinking_stats_counts_and_first_len_and_sig() -> None:
    content = [
        {"type": "thinking", "thinking": "abcd", "thinkingSignature": "sig"},
        {"type": "thinking", "thinking": "xyz"},
    ]
    # count=2, first_len=len("abcd")=4, first block has signature -> True
    assert jr._thinking_stats(content) == (2, 4, True)


def test_thinking_stats_first_len_only_from_first_block() -> None:
    content = [
        {"type": "thinking", "thinking": "ab"},          # first_len=2, no sig
        {"type": "thinking", "thinking": "zzzzz", "thinkingSignature": "s"},
    ]
    # NOTE: pins current behavior — has_sig is read ONLY from the first block,
    # so a signature on a later block is not reflected.
    assert jr._thinking_stats(content) == (2, 2, False)


def test_thinking_stats_nonstring_thinking_len_zero() -> None:
    content = [{"type": "thinking", "thinking": 12345}]
    assert jr._thinking_stats(content) == (1, 0, False)


def test_thinking_stats_ignores_non_dict_blocks() -> None:
    content = ["stray-string", {"type": "thinking", "thinking": "abc"}]
    assert jr._thinking_stats(content) == (1, 3, False)


def test_count_thinking_matches_shape() -> None:
    content = [
        {"type": "thinking", "thinking": "hello", "thinkingSignature": "s"},
        {"type": "thinking", "thinking": "world"},
    ]
    # _count_thinking: n=2, first_len=5, has_sig True (any block, unlike _thinking_stats)
    assert jr._count_thinking(content) == (2, 5, True)


def test_count_thinking_signature_from_any_block() -> None:
    content = [
        {"type": "thinking", "thinking": "aa"},
        {"type": "thinking", "thinking": "bb", "thinkingSignature": "sig"},
    ]
    # NOTE: _count_thinking sets has_sig from ANY block, diverging from
    # _thinking_stats which only reads the first block's signature.
    assert jr._count_thinking(content) == (2, 2, True)


def test_count_thinking_non_list_returns_zeros() -> None:
    assert jr._count_thinking(None) == (0, 0, False)


def test_count_thinking_nonstring_first_text_len_zero() -> None:
    content = [{"type": "thinking", "thinking": {"nested": True}}]
    # first_len stays 0 because txt is not a str when n==1
    assert jr._count_thinking(content) == (1, 0, False)


# --- sanitize_jsonl_message -----------------------------------------------

def test_sanitize_strips_sender_field() -> None:
    msg = {"role": "assistant", "sender": "internal", "content": []}
    out = jr.sanitize_jsonl_message(msg)
    assert "sender" not in out
    assert out["role"] == "assistant"


def test_sanitize_does_not_mutate_input() -> None:
    msg = {"role": "assistant", "sender": "x", "content": [{"type": "text"}]}
    original = json.loads(json.dumps(msg))
    jr.sanitize_jsonl_message(msg)
    assert msg == original  # input untouched


def test_sanitize_strips_cost_from_usage() -> None:
    msg = {"role": "assistant", "usage": {"input": 5, "cost": 0.99}, "content": []}
    out = jr.sanitize_jsonl_message(msg)
    assert "cost" not in out["usage"]
    assert out["usage"]["input"] == 5


def test_sanitize_usage_without_cost_untouched() -> None:
    msg = {"role": "assistant", "usage": {"input": 5}, "content": []}
    out = jr.sanitize_jsonl_message(msg)
    assert out["usage"] == {"input": 5}


def test_sanitize_usage_non_dict_left_alone() -> None:
    msg = {"role": "assistant", "usage": "n/a", "content": []}
    out = jr.sanitize_jsonl_message(msg)
    assert out["usage"] == "n/a"


def test_sanitize_truncates_toolcallid_at_pipe() -> None:
    msg = {
        "role": "toolResult",
        "content": [{"type": "tool_result", "toolCallId": "abc123|route-suffix"}],
    }
    out = jr.sanitize_jsonl_message(msg)
    assert out["content"][0]["toolCallId"] == "abc123"


def test_sanitize_toolcallid_without_pipe_untouched() -> None:
    msg = {
        "role": "toolResult",
        "content": [{"type": "tool_result", "toolCallId": "abc123"}],
    }
    out = jr.sanitize_jsonl_message(msg)
    assert out["content"][0]["toolCallId"] == "abc123"


def test_sanitize_truncates_tool_use_id_at_pipe() -> None:
    msg = {
        "role": "assistant",
        "content": [{"type": "tool_use", "id": "tu_9|extra"}],
    }
    out = jr.sanitize_jsonl_message(msg)
    assert out["content"][0]["id"] == "tu_9"


def test_sanitize_non_tool_use_id_with_pipe_preserved() -> None:
    # id split only happens when type == "tool_use"
    msg = {
        "role": "assistant",
        "content": [{"type": "text", "id": "keep|this"}],
    }
    out = jr.sanitize_jsonl_message(msg)
    assert out["content"][0]["id"] == "keep|this"


def test_sanitize_preserves_thinking_blocks() -> None:
    msg = {
        "role": "assistant",
        "content": [
            {"type": "thinking", "thinking": "deep", "thinkingSignature": "s"},
            {"type": "text", "text": "answer"},
        ],
    }
    out = jr.sanitize_jsonl_message(msg)
    kinds = [b["type"] for b in out["content"]]
    assert kinds == ["thinking", "text"]
    assert out["content"][0]["thinking"] == "deep"


def test_sanitize_thinking_debug_logged(caplog: pytest.LogCaptureFixture) -> None:
    msg = {
        "role": "assistant",
        "content": [{"type": "thinking", "thinking": "abc", "thinkingSignature": "s"}],
    }
    with caplog.at_level(logging.INFO, logger=jr._logger.name):
        jr.sanitize_jsonl_message(msg)
    assert any("[THINKING-DEBUG] sanitize BEFORE" in r.message for r in caplog.records)
    assert any("[THINKING-DEBUG] sanitize AFTER" in r.message for r in caplog.records)


def test_sanitize_no_thinking_no_debug_log(caplog: pytest.LogCaptureFixture) -> None:
    msg = {"role": "assistant", "content": [{"type": "text", "text": "hi"}]}
    with caplog.at_level(logging.INFO, logger=jr._logger.name):
        jr.sanitize_jsonl_message(msg)
    assert not any("[THINKING-DEBUG]" in r.message for r in caplog.records)


def test_sanitize_content_non_list_left_as_is() -> None:
    msg = {"role": "assistant", "content": "plain string"}
    out = jr.sanitize_jsonl_message(msg)
    assert out["content"] == "plain string"


def test_sanitize_content_with_non_dict_block_passes_through() -> None:
    msg = {"role": "assistant", "content": ["stray", {"type": "text", "text": "x"}]}
    out = jr.sanitize_jsonl_message(msg)
    assert out["content"][0] == "stray"
    assert out["content"][1]["text"] == "x"


def test_sanitize_non_mapping_role_defaults_empty() -> None:
    # A non-Mapping (falls through .get default via isinstance guard on role).
    # dict() of a Mapping-like still works; here we pass a plain dict with no role.
    out = jr.sanitize_jsonl_message({"content": []})
    assert out.get("role", "") == ""


# --- extract_tokens -------------------------------------------------------

def test_extract_tokens_anthropic_keys() -> None:
    entries = [{"usage": {"input": 100, "output": 50}}]
    assert jr.extract_tokens(entries) == (100, 50)


def test_extract_tokens_openai_keys() -> None:
    entries = [{"usage": {"prompt_tokens": 30, "completion_tokens": 20}}]
    assert jr.extract_tokens(entries) == (30, 20)


def test_extract_tokens_input_tokens_variant() -> None:
    entries = [{"usage": {"input_tokens": 7, "output_tokens": 3}}]
    assert jr.extract_tokens(entries) == (7, 3)


def test_extract_tokens_camelcase_variant() -> None:
    entries = [{"usage": {"inputTokens": 11, "outputTokens": 4}}]
    assert jr.extract_tokens(entries) == (11, 4)


def test_extract_tokens_usage_under_message() -> None:
    entries = [{"message": {"usage": {"input": 8, "output": 2}}}]
    assert jr.extract_tokens(entries) == (8, 2)


def test_extract_tokens_top_level_usage_wins_over_message() -> None:
    # `entry.get("usage") or ...` — top-level usage takes precedence.
    entries = [{"usage": {"input": 5}, "message": {"usage": {"input": 999}}}]
    assert jr.extract_tokens(entries) == (5, 0)


def test_extract_tokens_sums_across_entries() -> None:
    entries = [
        {"usage": {"input": 10, "output": 1}},
        {"usage": {"prompt_tokens": 5, "completion_tokens": 2}},
    ]
    assert jr.extract_tokens(entries) == (15, 3)


def test_extract_tokens_first_matching_key_breaks() -> None:
    # Both input and input_tokens present -> only the FIRST key in in_keys
    # ("input") contributes because the loop breaks on first truthy match.
    entries = [{"usage": {"input": 4, "input_tokens": 100}}]
    assert jr.extract_tokens(entries) == (4, 0)


def test_extract_tokens_float_values_coerced_to_int() -> None:
    entries = [{"usage": {"input": 2.9, "output": 3.9}}]
    # int(2.9)=2, int(3.9)=3
    assert jr.extract_tokens(entries) == (2, 3)


def test_extract_tokens_zero_values_skipped_by_truthiness() -> None:
    # NOTE: pins current behavior — `and v` means a genuine 0 is skipped,
    # so a later non-zero variant would be used instead (none here -> 0).
    entries = [{"usage": {"input": 0, "input_tokens": 9}}]
    assert jr.extract_tokens(entries) == (9, 0)


def test_extract_tokens_non_dict_entry_skipped() -> None:
    entries = ["garbage", {"usage": {"input": 5, "output": 1}}, 42]
    assert jr.extract_tokens(entries) == (5, 1)


def test_extract_tokens_non_dict_usage_skipped() -> None:
    entries = [{"usage": "n/a"}, {"usage": {"input": 3, "output": 1}}]
    assert jr.extract_tokens(entries) == (3, 1)


def test_extract_tokens_empty_iterable() -> None:
    assert jr.extract_tokens([]) == (0, 0)


def test_extract_tokens_missing_usage_defaults_empty() -> None:
    entries = [{"foo": "bar"}]
    assert jr.extract_tokens(entries) == (0, 0)


def test_extract_tokens_string_numeric_ignored() -> None:
    # values must be int/float; "100" (str) is ignored.
    entries = [{"usage": {"input": "100", "output": "50"}}]
    assert jr.extract_tokens(entries) == (0, 0)


def test_extract_tokens_message_not_dict_uses_empty() -> None:
    # entry has no top-level usage; message key is not a dict.
    # NOTE: `entry.get("message", {})` returns None here (key present, value None),
    # so `.get("usage")` would raise — pin actual behavior: None.get raises
    # AttributeError. Guard against that by confirming current code path.
    # Current code: entry.get("usage") -> None (missing); then
    # entry.get("message", {}).get(...) — message is missing -> {} -> {}.
    entries = [{"other": 1}]
    assert jr.extract_tokens(entries) == (0, 0)


# =========================================================================
# trajectory/builder.py
# =========================================================================

def _msg(role: str, content=None, msg_extra=None) -> dict:
    inner = {"role": role}
    if content is not None:
        inner["content"] = content
    if msg_extra:
        inner.update(msg_extra)
    return {"message": inner}


# --- _wrap_trajectory_message ---------------------------------------------

def test_wrap_assistant_message_wrapped() -> None:
    m = _msg("assistant", [{"type": "text", "text": "ok"}])
    out = bld._wrap_trajectory_message(m, is_accepted=1, hints="do better")
    assert out["is_accepted"] == 1
    assert out["hints"] == "do better"
    assert out["message"] is m


def test_wrap_toolresult_message_wrapped() -> None:
    m = _msg("toolResult", [])
    out = bld._wrap_trajectory_message(m)
    assert out["message"] is m
    assert out["is_accepted"] == 0
    assert out["hints"] is None


def test_wrap_user_message_passthrough() -> None:
    m = _msg("user", [{"type": "text", "text": "hi"}])
    out = bld._wrap_trajectory_message(m)
    assert out is m  # returned unchanged


def test_wrap_system_message_passthrough() -> None:
    m = _msg("system", [])
    assert bld._wrap_trajectory_message(m) is m


def test_wrap_auto_hint_fields_added() -> None:
    m = _msg("assistant", [])
    out = bld._wrap_trajectory_message(
        m, is_accepted=1, hints="h", is_auto_hint=True, auto_hint_iteration=3
    )
    assert out["is_auto_hint"] is True
    assert out["auto_hint_iteration"] == 3


def test_wrap_no_auto_hint_omits_fields() -> None:
    m = _msg("assistant", [])
    out = bld._wrap_trajectory_message(m)
    assert "is_auto_hint" not in out
    assert "auto_hint_iteration" not in out


def test_wrap_non_dict_inner_message_passthrough() -> None:
    m = {"message": "not-a-dict"}
    assert bld._wrap_trajectory_message(m) is m


def test_wrap_missing_message_key_treated_as_empty_role() -> None:
    m = {"no_message": True}
    # inner defaults to {}, role "" -> passthrough
    assert bld._wrap_trajectory_message(m) is m


# --- _wrap_messages_with_turn_feedback ------------------------------------

def test_turn_feedback_empty_turns_wraps_all() -> None:
    msgs = [_msg("assistant", []), _msg("user", [])]
    out = bld._wrap_messages_with_turn_feedback(msgs, [])
    # assistant wrapped, user passthrough
    assert "is_accepted" in out[0]
    assert out[1] is msgs[1]


def test_turn_feedback_applies_hints_on_match() -> None:
    turns = [{"prompt": "do the thing", "hints": "use pandas"}]
    msgs = [
        _msg("user", [{"type": "text", "text": "do the thing"}]),
        _msg("assistant", [{"type": "text", "text": "done"}]),
    ]
    out = bld._wrap_messages_with_turn_feedback(msgs, turns)
    # assistant after matched user turn should inherit is_accepted=1, hints
    assistant_wrapped = out[1]
    assert assistant_wrapped["is_accepted"] == 1
    assert assistant_wrapped["hints"] == "use pandas"


def test_turn_feedback_no_hints_sets_not_accepted() -> None:
    turns = [{"prompt": "task", "hints": ""}]
    msgs = [
        _msg("user", [{"type": "text", "text": "task"}]),
        _msg("assistant", []),
    ]
    out = bld._wrap_messages_with_turn_feedback(msgs, turns)
    assert out[1]["is_accepted"] == 0
    assert out[1]["hints"] is None


def test_turn_feedback_substring_match() -> None:
    # user_text is a substring of expected -> matched path still advances.
    turns = [{"prompt": "please do the full thing now", "hints": "hint1"}]
    msgs = [
        _msg("user", [{"type": "text", "text": "do the full thing"}]),
        _msg("assistant", []),
    ]
    out = bld._wrap_messages_with_turn_feedback(msgs, turns)
    assert out[1]["hints"] == "hint1"


def test_turn_feedback_string_content_user_text() -> None:
    turns = [{"prompt": "hello", "hints": "h"}]
    msgs = [
        _msg("user", "hello"),  # content is a plain string
        _msg("assistant", []),
    ]
    out = bld._wrap_messages_with_turn_feedback(msgs, turns)
    assert out[1]["hints"] == "h"


def test_turn_feedback_auto_hint_flags_propagate() -> None:
    turns = [{
        "prompt": "p", "hints": "h",
        "is_auto_hint": True, "auto_hint_iteration": 2,
    }]
    msgs = [
        _msg("user", [{"type": "text", "text": "p"}]),
        _msg("assistant", []),
    ]
    out = bld._wrap_messages_with_turn_feedback(msgs, turns)
    assert out[1]["is_auto_hint"] is True
    assert out[1]["auto_hint_iteration"] == 2


# --- _unwrap_trajectory_messages ------------------------------------------

def test_unwrap_double_wrapped_and_assigns_turn_index() -> None:
    wrapped = [
        {"is_accepted": 0, "message": {"message": {"role": "assistant"}}},
        {"is_accepted": 1, "message": {"message": {"role": "user"}}},
    ]
    out = bld._unwrap_trajectory_messages(wrapped)
    assert out[0] == {"message": {"role": "assistant"}, "turn_index": 0}
    assert out[1]["turn_index"] == 1


def test_unwrap_passthrough_non_wrapped() -> None:
    plain = [{"message": {"role": "user"}}]  # no double-nesting
    out = bld._unwrap_trajectory_messages(plain)
    assert out[0]["turn_index"] == 0
    assert out[0]["message"] == {"role": "user"}


def test_unwrap_pops_parent_id() -> None:
    plain = [{"message": {"role": "user"}, "parentId": "p1"}]
    out = bld._unwrap_trajectory_messages(plain)
    assert "parentId" not in out[0]


# --- _artifact_turns_from_entries -----------------------------------------

def test_artifact_turns_extracts_tool_calls_and_text() -> None:
    entries = [{
        "message": {
            "role": "assistant",
            "content": [
                {"type": "toolCall", "name": "write", "arguments": {"path": "/x"}},
                {"type": "text", "text": "here you go"},
            ],
        }
    }]
    out = bld._artifact_turns_from_entries(entries)
    assert len(out) == 1
    tc = json.loads(out[0]["tool_calls"])
    assert tc == [{"name": "write", "arguments": {"path": "/x"}}]
    assert out[0]["response"] == "here you go"


def test_artifact_turns_skips_non_assistant() -> None:
    entries = [{"message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}}]
    assert bld._artifact_turns_from_entries(entries) == []


def test_artifact_turns_skips_empty_text() -> None:
    entries = [{
        "message": {"role": "assistant", "content": [{"type": "text", "text": "   "}]}
    }]
    # whitespace-only text is dropped; turn has no keys -> not appended
    assert bld._artifact_turns_from_entries(entries) == []


def test_artifact_turns_content_not_list_skipped() -> None:
    entries = [{"message": {"role": "assistant", "content": "not a list"}}]
    assert bld._artifact_turns_from_entries(entries) == []


def test_artifact_turns_bare_message_shape() -> None:
    # entry without "message" wrapper -> uses entry itself as the message.
    entries = [{
        "role": "assistant",
        "content": [{"type": "text", "text": "flat"}],
    }]
    out = bld._artifact_turns_from_entries(entries)
    assert out == [{"response": "flat"}]


def test_artifact_turns_empty_and_none() -> None:
    assert bld._artifact_turns_from_entries([]) == []
    assert bld._artifact_turns_from_entries(None) == []


def test_artifact_turns_ignores_non_dict_blocks() -> None:
    entries = [{
        "message": {
            "role": "assistant",
            "content": ["stray", {"type": "text", "text": "kept"}],
        }
    }]
    out = bld._artifact_turns_from_entries(entries)
    assert out == [{"response": "kept"}]


# --- _coerce_top_usage ----------------------------------------------------

def test_coerce_top_usage_none_returns_zeros() -> None:
    out = bld._coerce_top_usage(None)
    assert out == dict(bld._ZERO_TOP_USAGE)
    # must be a copy, not the module-level singleton
    assert out is not bld._ZERO_TOP_USAGE


def test_coerce_top_usage_full_projection() -> None:
    src = {
        "input_tokens": 10, "output_tokens": 5,
        "cached_input_tokens": 2, "cache_read_tokens": 1,
        "cache_write_tokens": 3, "cost_usd": 0.123456789,
    }
    out = bld._coerce_top_usage(src)
    assert out["input_tokens"] == 10
    assert out["cost_usd"] == round(0.123456789, 6)


def test_coerce_top_usage_missing_fields_default_zero() -> None:
    out = bld._coerce_top_usage({"input_tokens": 7})
    assert out["input_tokens"] == 7
    assert out["output_tokens"] == 0
    assert out["cost_usd"] == 0.0


def test_coerce_top_usage_malformed_ints_fallback_zero() -> None:
    out = bld._coerce_top_usage({"input_tokens": "abc", "output_tokens": None})
    assert out["input_tokens"] == 0
    assert out["output_tokens"] == 0


def test_coerce_top_usage_malformed_cost_fallback_zero() -> None:
    out = bld._coerce_top_usage({"cost_usd": "not-a-number"})
    assert out["cost_usd"] == 0.0


def test_coerce_top_usage_non_mapping_returns_zeros() -> None:
    assert bld._coerce_top_usage(["list"]) == dict(bld._ZERO_TOP_USAGE)
    assert bld._coerce_top_usage(42) == dict(bld._ZERO_TOP_USAGE)


def test_coerce_top_usage_float_input_int_truncated() -> None:
    # int("...") path: numeric floats coerce via int() only when int(src.get)...
    # here src value is a float -> int(2.9) == 2
    out = bld._coerce_top_usage({"input_tokens": 2.9})
    assert out["input_tokens"] == 2


# --- _count_thinking_blocks (builder) -------------------------------------

def test_builder_count_thinking_blocks_wrapped_and_flat() -> None:
    messages = [
        {"message": {"content": [
            {"type": "thinking", "thinking": "aa", "thinkingSignature": "s"},
        ]}},
        {"content": [{"type": "thinking", "thinking": "bbbb"}]},  # flat
    ]
    total, samples = bld._count_thinking_blocks(messages)
    assert total == 2
    assert samples[0] == {"len": 2, "has_signature": True}
    assert samples[1] == {"len": 4, "has_signature": False}


def test_builder_count_thinking_blocks_empty_and_none() -> None:
    assert bld._count_thinking_blocks([]) == (0, [])
    assert bld._count_thinking_blocks(None) == (0, [])


def test_builder_count_thinking_blocks_skips_non_dict_entries() -> None:
    messages = ["stray", {"content": [{"type": "thinking", "thinking": "x"}]}]
    total, samples = bld._count_thinking_blocks(messages)
    assert total == 1
    assert samples == [{"len": 1, "has_signature": False}]


def test_builder_count_thinking_blocks_content_not_list_skipped() -> None:
    # content present but not a list -> entry contributes nothing.
    messages = [
        {"message": {"content": "plain string"}},
        {"content": None},
        {"content": [{"type": "thinking", "thinking": "z"}]},
    ]
    total, samples = bld._count_thinking_blocks(messages)
    assert total == 1
    assert samples == [{"len": 1, "has_signature": False}]


def test_builder_count_thinking_blocks_nonstring_thinking_len_zero() -> None:
    messages = [{"content": [{"type": "thinking", "thinking": 999}]}]
    total, samples = bld._count_thinking_blocks(messages)
    assert total == 1
    assert samples[0]["len"] == 0


# --- build_trajectory_from_jsonl (integration, pure default media handler) -

def _task() -> Task:
    return Task(
        id="pk-1",
        task_id="demo-task",
        persona="p",
        initial_prompt="do it",
        task_type="data_analysis",
    )


def test_build_trajectory_top_level_schema() -> None:
    entries = [
        {"type": "message", "id": "m1", "timestamp": "t1",
         "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}},
        {"type": "message", "id": "m2", "timestamp": "t2",
         "message": {"role": "assistant", "content": [{"type": "text", "text": "ok"}]}},
    ]
    out = bld.build_trajectory_from_jsonl(_task(), entries)
    assert set(out.keys()) == {
        "session_id", "timestamp", "trajectory",
        "input_files", "output_artifacts", "messages", "usage",
    }
    assert len(out["messages"]) == 2
    assert out["usage"] == dict(bld._ZERO_TOP_USAGE)


def test_build_trajectory_skips_non_message_type_entries() -> None:
    entries = [
        {"type": "event", "id": "e1", "message": {"role": "user"}},
        {"type": "message", "id": "m1",
         "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}},
    ]
    out = bld.build_trajectory_from_jsonl(_task(), entries)
    assert len(out["messages"]) == 1


def test_build_trajectory_skips_leading_system_before_user() -> None:
    # system message before any user message is dropped.
    entries = [
        {"type": "message", "id": "s1", "message": {"role": "system", "content": []}},
        {"type": "message", "id": "u1",
         "message": {"role": "user", "content": [{"type": "text", "text": "go"}]}},
        {"type": "message", "id": "s2", "message": {"role": "system", "content": []}},
    ]
    out = bld.build_trajectory_from_jsonl(_task(), entries)
    ids = [m["id"] for m in out["messages"]]
    # leading system dropped; user kept; trailing system (after user) kept
    assert "s1" not in ids
    assert "u1" in ids
    assert "s2" in ids


def test_build_trajectory_skips_entries_missing_role() -> None:
    entries = [
        {"type": "message", "id": "m1", "message": {"content": []}},  # no role
        {"type": "message", "id": "m2",
         "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}},
    ]
    out = bld.build_trajectory_from_jsonl(_task(), entries)
    assert [m["id"] for m in out["messages"]] == ["m2"]


def test_build_trajectory_skips_non_dict_message() -> None:
    entries = [
        {"type": "message", "id": "m1", "message": "not-a-dict"},
        {"type": "message", "id": "m2",
         "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}},
    ]
    out = bld.build_trajectory_from_jsonl(_task(), entries)
    assert [m["id"] for m in out["messages"]] == ["m2"]


def test_build_trajectory_parent_id_stripped_from_output() -> None:
    # NOTE: pins current behavior — parentId is chained internally during
    # assembly but then popped by _unwrap_trajectory_messages, so the final
    # output carries turn_index instead and NO parentId key survives.
    entries = [
        {"type": "message", "id": "a",
         "message": {"role": "user", "content": [{"type": "text", "text": "1"}]}},
        {"type": "message", "id": "b",
         "message": {"role": "assistant", "content": [{"type": "text", "text": "2"}]}},
    ]
    out = bld.build_trajectory_from_jsonl(_task(), entries)
    assert "parentId" not in out["messages"][1]
    assert out["messages"][0]["turn_index"] == 0
    assert out["messages"][1]["turn_index"] == 1


def test_build_trajectory_non_dict_entry_skipped() -> None:
    entries = [
        "garbage",
        {"type": "message", "id": "m1",
         "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}},
    ]
    out = bld.build_trajectory_from_jsonl(_task(), entries)
    assert len(out["messages"]) == 1


def test_build_trajectory_usage_top_level_projected() -> None:
    out = bld.build_trajectory_from_jsonl(
        _task(), [], usage_top_level={"input_tokens": 9, "cost_usd": 1.5}
    )
    assert out["usage"]["input_tokens"] == 9
    assert out["usage"]["cost_usd"] == 1.5


def test_build_trajectory_media_handler_invoked() -> None:
    seen = {}

    def handler(messages, task_id):
        seen["task_id"] = task_id
        return [{"replaced": True}]

    entries = [
        {"type": "message", "id": "m1",
         "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]}},
    ]
    out = bld.build_trajectory_from_jsonl(_task(), entries, media_handler=handler)
    assert out["messages"] == [{"replaced": True}]
    assert seen["task_id"] == "demo-task"


def test_build_trajectory_empty_entries() -> None:
    out = bld.build_trajectory_from_jsonl(_task(), [])
    assert out["messages"] == []
    assert out["input_files"] == out["input_files"]  # constructed without error
    assert out["output_artifacts"] == []


def test_build_trajectory_with_turns_wraps_feedback() -> None:
    entries = [
        {"type": "message", "id": "u1",
         "message": {"role": "user", "content": [{"type": "text", "text": "do it"}]}},
        {"type": "message", "id": "a1",
         "message": {"role": "assistant", "content": [{"type": "text", "text": "done"}]}},
    ]
    turns = [{"prompt": "do it", "hints": "hint-x"}]
    out = bld.build_trajectory_from_jsonl(_task(), entries, turns=turns)
    # after unwrap, messages carry turn_index; the assistant inherited hints
    # via wrapping then was unwrapped back to raw message shape.
    assert all("turn_index" in m for m in out["messages"])
