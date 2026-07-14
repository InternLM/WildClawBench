"""Behavioral tests for src/utils/store.py (SQLite Store).

Covers:
- Schema creation in tmp_path (incl. nested parent dirs) and idempotent reopen.
- Task upsert (insert + conflict-update), JSON round-trip of the `extra` dict,
  and the fields the ON CONFLICT clause deliberately does NOT touch.
- Sandbox upsert and status transitions (pending -> running -> graded).
- api_request / test_result inserts with default / coerced / malformed payloads.
- list_test_results join + ordering.
- tx() commit-on-success / rollback-on-exception semantics.
- Persistence across close() + reopen with a fresh Store instance.

Everything runs against a database file inside pytest tmp_path — no docker,
no network, no repo writes.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils.store import Sandbox, Store, Task  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path: Path) -> Store:
    s = Store(tmp_path / "store.db")
    yield s
    try:
        s.close()
    except sqlite3.ProgrammingError:
        pass  # already closed by the test


def _make_task(pk: str = "pk-1", **overrides) -> Task:
    fields = dict(
        id=pk,
        task_id="alden-croft_MB",
        persona="alden",
        initial_prompt="do the thing",
    )
    fields.update(overrides)
    return Task(**fields)


def _make_sandbox(sid: str = "sb-1", task_pk: str = "pk-1", **overrides) -> Sandbox:
    fields = dict(id=sid, task_pk=task_pk, model_type="claude-opus-4.7")
    fields.update(overrides)
    return Sandbox(**fields)


# ---------------------------------------------------------------------------
# Section A — construction / schema
# ---------------------------------------------------------------------------


def test_init_creates_db_file_and_tables(tmp_path: Path) -> None:
    s = Store(tmp_path / "store.db")
    try:
        assert (tmp_path / "store.db").exists()
        names = {
            r["name"]
            for r in s.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert {"task", "sandbox", "api_request", "test_result"} <= names
    finally:
        s.close()


def test_init_creates_missing_parent_directories(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "c" / "store.db"
    s = Store(nested)
    try:
        assert nested.exists()
        assert nested.parent.is_dir()
    finally:
        s.close()


def test_init_enables_wal_journal_mode(tmp_path: Path) -> None:
    s = Store(tmp_path / "store.db")
    try:
        mode = s.conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode.lower() == "wal"
    finally:
        s.close()


def test_schema_creation_is_idempotent_on_reopen(tmp_path: Path) -> None:
    path = tmp_path / "store.db"
    s1 = Store(path)
    s1.upsert_task(_make_task())
    s1.close()
    # Second Store on the same file must not error or wipe existing rows.
    s2 = Store(path)
    try:
        assert s2.get_task("pk-1") is not None
    finally:
        s2.close()


def test_close_prevents_further_use(store: Store) -> None:
    store.close()
    with pytest.raises(sqlite3.ProgrammingError):
        store.conn.execute("SELECT 1")


# ---------------------------------------------------------------------------
# Section B — tx() transaction semantics
# ---------------------------------------------------------------------------


def test_tx_commits_on_success(tmp_path: Path) -> None:
    path = tmp_path / "store.db"
    s = Store(path)
    with s.tx() as c:
        c.execute(
            "INSERT INTO task(id, task_id, persona, initial_prompt, created_at, updated_at)"
            " VALUES('t1','tid','p','ip',0.0,0.0)"
        )
    s.close()
    # Visible from a completely fresh connection => genuinely committed.
    s2 = Store(path)
    try:
        assert s2.get_task("t1") is not None
    finally:
        s2.close()


def test_tx_rolls_back_and_reraises_on_exception(store: Store) -> None:
    with pytest.raises(ValueError, match="boom"):
        with store.tx() as c:
            c.execute(
                "INSERT INTO task(id, task_id, persona, initial_prompt, created_at, updated_at)"
                " VALUES('t-rollback','tid','p','ip',0.0,0.0)"
            )
            raise ValueError("boom")
    assert store.get_task("t-rollback") is None


# ---------------------------------------------------------------------------
# Section C — Task upsert / get
# ---------------------------------------------------------------------------


def test_get_task_missing_returns_none(store: Store) -> None:
    assert store.get_task("nope") is None


def test_upsert_task_insert_and_read_back_all_fields(store: Store) -> None:
    task = _make_task(
        "pk-full",
        seed_prompt="seed",
        task_type="agentic",
        difficulty="hard",
        l1="finance",
        l2="reconciliation",
        system_prompt="be helpful",
        task_description="desc",
        rubrics_json=json.dumps([{"criterion": "c1", "weight": 5}]),
        test_code="def test_x(): pass",
        test_weights=json.dumps({"test_x": 3}),
        golden_trajectory="[]",
        extra={"tags": ["drift", "mock"], "k": 4},
        status="pending",
    )
    store.upsert_task(task)
    got = store.get_task("pk-full")
    assert got is not None
    assert got.task_id == "alden-croft_MB"
    assert got.persona == "alden"
    assert got.initial_prompt == "do the thing"
    assert got.seed_prompt == "seed"
    assert got.task_type == "agentic"
    assert got.difficulty == "hard"
    assert got.l1 == "finance"
    assert got.l2 == "reconciliation"
    assert got.system_prompt == "be helpful"
    assert got.task_description == "desc"
    assert json.loads(got.rubrics_json) == [{"criterion": "c1", "weight": 5}]
    assert got.test_code == "def test_x(): pass"
    assert json.loads(got.test_weights) == {"test_x": 3}
    assert got.golden_trajectory == "[]"
    assert got.status == "pending"


def test_task_extra_dict_json_round_trip(store: Store) -> None:
    extra = {"nested": {"a": [1, 2, 3]}, "unicode": "naïve — ✓", "n": None}
    store.upsert_task(_make_task("pk-extra", extra=extra))
    got = store.get_task("pk-extra")
    assert got.extra == extra
    assert isinstance(got.extra, dict)


def test_task_empty_extra_defaults_to_empty_dict(store: Store) -> None:
    store.upsert_task(_make_task("pk-noextra"))
    assert store.get_task("pk-noextra").extra == {}


def test_get_task_tolerates_empty_extra_json_column(store: Store) -> None:
    # A row written outside upsert_task may carry extra_json='' — the reader
    # must fall back to {} instead of crashing in json.loads.
    with store.tx() as c:
        c.execute(
            "INSERT INTO task(id, task_id, persona, initial_prompt, extra_json,"
            " created_at, updated_at) VALUES('pk-raw','tid','p','ip','',0.0,0.0)"
        )
    assert store.get_task("pk-raw").extra == {}


def test_upsert_task_conflict_updates_mutable_fields(store: Store) -> None:
    store.upsert_task(_make_task("pk-up", status="pending"))
    store.upsert_task(
        _make_task(
            "pk-up",
            task_id="renata-voss",
            persona="renata",
            initial_prompt="new prompt",
            rubrics_json='[{"criterion":"c2"}]',
            extra={"v": 2},
            status="completed",
        )
    )
    got = store.get_task("pk-up")
    assert got.task_id == "renata-voss"
    assert got.persona == "renata"
    assert got.initial_prompt == "new prompt"
    assert got.rubrics_json == '[{"criterion":"c2"}]'
    assert got.extra == {"v": 2}
    assert got.status == "completed"
    # Exactly one row — upsert, not duplicate insert.
    n = store.conn.execute("SELECT COUNT(*) FROM task WHERE id='pk-up'").fetchone()[0]
    assert n == 1


def test_upsert_task_conflict_preserves_created_at(store: Store) -> None:
    first = _make_task("pk-ts", created_at=100.0)
    store.upsert_task(first)
    second = _make_task("pk-ts", created_at=999.0)
    store.upsert_task(second)
    got = store.get_task("pk-ts")
    # ON CONFLICT clause intentionally omits created_at: original wins.
    assert got.created_at == 100.0
    # updated_at is refreshed on every upsert (upsert_task stamps time.time()).
    assert got.updated_at > 100.0


def test_upsert_task_mutates_updated_at_on_passed_object(store: Store) -> None:
    task = _make_task("pk-mut", updated_at=0.0)
    store.upsert_task(task)
    assert task.updated_at > 0.0
    assert store.get_task("pk-mut").updated_at == task.updated_at


def test_task_status_transition_persists(store: Store) -> None:
    task = _make_task("pk-status")
    store.upsert_task(task)
    for status in ("running", "graded", "failed"):
        task.status = status
        store.upsert_task(task)
        assert store.get_task("pk-status").status == status


# ---------------------------------------------------------------------------
# Section D — Sandbox upsert / get
# ---------------------------------------------------------------------------


def test_get_sandbox_missing_returns_none(store: Store) -> None:
    assert store.get_sandbox("nope") is None


def test_upsert_sandbox_insert_defaults(store: Store) -> None:
    store.upsert_sandbox(_make_sandbox("sb-def"))
    got = store.get_sandbox("sb-def")
    assert got is not None
    assert got.task_pk == "pk-1"
    assert got.model_type == "claude-opus-4.7"
    assert got.run_index == 1
    assert got.status == "pending"
    assert got.score is None
    assert got.started_at is None
    assert got.stopped_at is None
    assert got.tokens_in == 0 and got.tokens_out == 0


def test_upsert_sandbox_full_lifecycle_status_transitions(store: Store) -> None:
    sb = _make_sandbox("sb-life", run_index=2)
    store.upsert_sandbox(sb)

    sb.status = "running"
    sb.container_name = "kensei-sb-life"
    sb.gateway_port = 4141
    sb.workdir = "/root/workspace"
    sb.started_at = 1000.0
    store.upsert_sandbox(sb)
    got = store.get_sandbox("sb-life")
    assert got.status == "running"
    assert got.container_name == "kensei-sb-life"
    assert got.gateway_port == 4141
    assert got.workdir == "/root/workspace"
    assert got.started_at == 1000.0

    sb.status = "graded"
    sb.score = 0.75
    sb.grading_status = "judge_council"
    sb.tokens_in = 1234
    sb.tokens_out = 567
    sb.automated_checks_passed = 3
    sb.automated_checks_total = 5
    sb.trajectory_json = json.dumps([{"role": "user", "content": "hi"}])
    sb.stopped_at = 2000.0
    store.upsert_sandbox(sb)
    got = store.get_sandbox("sb-life")
    assert got.status == "graded"
    assert got.score == 0.75
    assert got.grading_status == "judge_council"
    assert got.tokens_in == 1234 and got.tokens_out == 567
    assert got.automated_checks_passed == 3
    assert got.automated_checks_total == 5
    assert json.loads(got.trajectory_json) == [{"role": "user", "content": "hi"}]
    assert got.stopped_at == 2000.0

    n = store.conn.execute("SELECT COUNT(*) FROM sandbox").fetchone()[0]
    assert n == 1


def test_upsert_sandbox_error_state_round_trip(store: Store) -> None:
    sb = _make_sandbox("sb-err", status="failed", error="docker daemon unreachable")
    store.upsert_sandbox(sb)
    got = store.get_sandbox("sb-err")
    assert got.status == "failed"
    assert got.error == "docker daemon unreachable"
    assert got.score is None


def test_upsert_sandbox_conflict_preserves_identity_columns(store: Store) -> None:
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # The sandbox ON CONFLICT clause omits task_pk, model_type and run_index,
    # so a re-upsert with different identity values silently keeps the originals.
    store.upsert_sandbox(_make_sandbox("sb-id", task_pk="pk-A", model_type="m1", run_index=1))
    store.upsert_sandbox(_make_sandbox("sb-id", task_pk="pk-B", model_type="m2", run_index=9))
    got = store.get_sandbox("sb-id")
    assert got.task_pk == "pk-A"
    assert got.model_type == "m1"
    assert got.run_index == 1


def test_sandbox_score_can_be_reset_to_none(store: Store) -> None:
    sb = _make_sandbox("sb-score", score=0.9)
    store.upsert_sandbox(sb)
    assert store.get_sandbox("sb-score").score == 0.9
    sb.score = None
    store.upsert_sandbox(sb)
    assert store.get_sandbox("sb-score").score is None


# ---------------------------------------------------------------------------
# Section E — api_request inserts
# ---------------------------------------------------------------------------


def _api_rows(store: Store) -> list[dict]:
    return [dict(r) for r in store.conn.execute("SELECT * FROM api_request").fetchall()]


def test_insert_api_request_full_payload(store: Store) -> None:
    store.insert_api_request(
        "sb-1",
        {
            "service_name": "gmail-api",
            "method": "POST",
            "path": "/v1/messages",
            "query_params": {"labelIds": ["INBOX"]},
            "request_body": '{"to":"x@y.z"}',
            "status_code": 201,
            "response_body": '{"id":"m1"}',
            "request_time": 1720000000.5,
            "duration_ms": 42,
        },
    )
    rows = _api_rows(store)
    assert len(rows) == 1
    r = rows[0]
    assert r["sandbox_id"] == "sb-1"
    assert r["service_name"] == "gmail-api"
    assert r["method"] == "POST"
    assert r["path"] == "/v1/messages"
    assert json.loads(r["query_params"]) == {"labelIds": ["INBOX"]}
    assert r["request_body"] == '{"to":"x@y.z"}'
    assert r["status_code"] == 201
    assert r["response_body"] == '{"id":"m1"}'
    assert r["request_time"] == 1720000000.5
    assert r["duration_ms"] == 42
    assert r["id"] == 1  # autoincrement pk


def test_insert_api_request_empty_payload_uses_defaults(store: Store) -> None:
    store.insert_api_request("sb-1", {})
    r = _api_rows(store)[0]
    assert r["service_name"] == ""
    assert r["method"] == "GET"
    assert r["path"] == ""
    assert json.loads(r["query_params"]) == {}
    assert r["status_code"] == 0
    assert r["request_time"] is None
    assert r["duration_ms"] == 0


def test_insert_api_request_none_query_params_becomes_empty_object(store: Store) -> None:
    store.insert_api_request("sb-1", {"query_params": None})
    assert json.loads(_api_rows(store)[0]["query_params"]) == {}


def test_insert_api_request_coerces_numeric_strings(store: Store) -> None:
    store.insert_api_request("sb-1", {"status_code": "404", "duration_ms": "17"})
    r = _api_rows(store)[0]
    assert r["status_code"] == 404
    assert r["duration_ms"] == 17


def test_insert_api_request_explicit_none_status_code_raises(store: Store) -> None:
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # payload.get("status_code", 0) returns None when the key is present with
    # value None, and int(None) raises TypeError instead of falling back to 0.
    with pytest.raises(TypeError):
        store.insert_api_request("sb-1", {"status_code": None})
    assert _api_rows(store) == []  # tx rolled back, nothing persisted


# ---------------------------------------------------------------------------
# Section F — test_result inserts + list_test_results
# ---------------------------------------------------------------------------


def test_insert_test_result_returns_autoincrement_rowids(store: Store) -> None:
    rid1 = store.insert_test_result("sb-1", "claude-opus-4.7", 0, {})
    rid2 = store.insert_test_result("sb-1", "claude-opus-4.7", 1, {})
    assert rid1 == 1
    assert rid2 == 2


def test_insert_test_result_defaults_for_empty_result(store: Store) -> None:
    store.insert_test_result("sb-1", "m", 0, {})
    r = dict(store.conn.execute("SELECT * FROM test_result").fetchone())
    assert r["status"] == "pending"
    assert r["score"] == 0.0
    assert r["test_code"] == ""
    assert r["test_output"] == ""
    assert json.loads(r["test_scores"]) == {}
    assert json.loads(r["test_function_outputs"]) == {}
    assert r["tests_total"] == 0
    assert r["tests_passed"] == 0
    assert r["tests_failed"] == 0
    assert r["tests_errored"] == 0
    assert r["duration_generation_ms"] == 0
    assert r["duration_execution_ms"] == 0


def test_insert_test_result_full_payload_round_trip(store: Store) -> None:
    result = {
        "status": "passed",
        "score": "0.5",  # numeric string is coerced by float()
        "test_code": "def test_a(): assert True",
        "test_output": "1 passed",
        "test_scores": {"test_a": 1.0, "guardrail": -3},
        "test_function_outputs": {"test_a": "ok"},
        "tests_total": 4,
        "tests_passed": 3,
        "tests_failed": 1,
        "tests_errored": 0,
        "duration_generation_ms": 1200,
        "duration_execution_ms": 350,
    }
    store.insert_test_result("sb-1", "gpt-5.5", 2, result)
    r = dict(store.conn.execute("SELECT * FROM test_result").fetchone())
    assert r["sandbox_id"] == "sb-1"
    assert r["model_type"] == "gpt-5.5"
    assert r["trajectory_index"] == 2
    assert r["status"] == "passed"
    assert r["score"] == 0.5
    assert json.loads(r["test_scores"]) == {"test_a": 1.0, "guardrail": -3}
    assert json.loads(r["test_function_outputs"]) == {"test_a": "ok"}
    assert r["tests_total"] == 4
    assert r["tests_passed"] == 3
    assert r["tests_failed"] == 1
    assert r["duration_generation_ms"] == 1200
    assert r["duration_execution_ms"] == 350


def test_insert_test_result_accepts_negative_counts_unvalidated(store: Store) -> None:
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
    # No range validation: negative counts and out-of-range scores are stored as-is.
    store.insert_test_result("sb-1", "m", 0, {"tests_passed": -1, "score": -8.0})
    r = dict(store.conn.execute("SELECT * FROM test_result").fetchone())
    assert r["tests_passed"] == -1
    assert r["score"] == -8.0


def test_list_test_results_empty_for_unknown_task(store: Store) -> None:
    assert store.list_test_results("no-such-task") == []


def test_list_test_results_joins_on_task_and_orders_by_trajectory_index(store: Store) -> None:
    store.upsert_task(_make_task("pk-A"))
    store.upsert_task(_make_task("pk-B"))
    store.upsert_sandbox(_make_sandbox("sb-A1", task_pk="pk-A"))
    store.upsert_sandbox(_make_sandbox("sb-A2", task_pk="pk-A", run_index=2))
    store.upsert_sandbox(_make_sandbox("sb-B1", task_pk="pk-B"))

    # Insert out of trajectory order, across both sandboxes of task A,
    # plus one row for task B that must NOT leak into A's listing.
    store.insert_test_result("sb-A2", "m", 3, {"status": "failed"})
    store.insert_test_result("sb-A1", "m", 1, {"status": "passed"})
    store.insert_test_result("sb-B1", "m", 0, {"status": "passed"})
    store.insert_test_result("sb-A1", "m", 2, {"status": "errored"})

    rows = store.list_test_results("pk-A")
    assert [r["trajectory_index"] for r in rows] == [1, 2, 3]
    assert [r["status"] for r in rows] == ["passed", "errored", "failed"]
    assert all(r["sandbox_id"] in {"sb-A1", "sb-A2"} for r in rows)
    assert all(isinstance(r, dict) for r in rows)

    rows_b = store.list_test_results("pk-B")
    assert len(rows_b) == 1
    assert rows_b[0]["sandbox_id"] == "sb-B1"


# ---------------------------------------------------------------------------
# Section G — reopen persistence (end-to-end)
# ---------------------------------------------------------------------------


def test_full_state_survives_close_and_reopen(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "store.db"
    s1 = Store(path)
    s1.upsert_task(_make_task("pk-P", extra={"seed": 42}, status="running"))
    s1.upsert_sandbox(_make_sandbox("sb-P", task_pk="pk-P", status="graded", score=1.0))
    s1.insert_api_request("sb-P", {"service_name": "slack-api", "status_code": 200})
    s1.insert_test_result("sb-P", "m", 0, {"status": "passed", "score": 1.0})
    s1.close()

    s2 = Store(path)
    try:
        task = s2.get_task("pk-P")
        assert task.extra == {"seed": 42}
        assert task.status == "running"

        sb = s2.get_sandbox("sb-P")
        assert sb.status == "graded"
        assert sb.score == 1.0

        api = s2.conn.execute("SELECT service_name, status_code FROM api_request").fetchone()
        assert (api["service_name"], api["status_code"]) == ("slack-api", 200)

        results = s2.list_test_results("pk-P")
        assert len(results) == 1
        assert results[0]["status"] == "passed"
        assert results[0]["score"] == 1.0
    finally:
        s2.close()
