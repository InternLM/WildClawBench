from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional


_SCHEMA = """
CREATE TABLE IF NOT EXISTS task (
    id              TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL,
    persona         TEXT NOT NULL,
    initial_prompt  TEXT NOT NULL,
    seed_prompt     TEXT DEFAULT '',
    task_type       TEXT DEFAULT '',
    difficulty      TEXT DEFAULT '',
    l1              TEXT DEFAULT '',
    l2              TEXT DEFAULT '',
    system_prompt   TEXT DEFAULT '',
    task_description TEXT DEFAULT '',
    rubrics_json    TEXT DEFAULT '',
    test_code       TEXT DEFAULT '',
    test_weights    TEXT DEFAULT '',
    golden_trajectory TEXT DEFAULT '',
    extra_json      TEXT DEFAULT '{}',
    status          TEXT DEFAULT 'pending',
    created_at      REAL NOT NULL,
    updated_at      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sandbox (
    id              TEXT PRIMARY KEY,
    task_pk         TEXT NOT NULL REFERENCES task(id),
    model_type      TEXT NOT NULL,
    run_index       INTEGER NOT NULL DEFAULT 1,
    container_name  TEXT DEFAULT '',
    gateway_port    INTEGER DEFAULT 0,
    workdir         TEXT DEFAULT '',
    status          TEXT DEFAULT 'pending',
    error           TEXT DEFAULT '',
    trajectory_json TEXT DEFAULT '',
    tokens_in       INTEGER DEFAULT 0,
    tokens_out      INTEGER DEFAULT 0,
    score           REAL,
    grading_status  TEXT DEFAULT '',
    automated_checks_passed INTEGER DEFAULT 0,
    automated_checks_total  INTEGER DEFAULT 0,
    started_at      REAL,
    stopped_at      REAL
);

CREATE TABLE IF NOT EXISTS api_request (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sandbox_id      TEXT NOT NULL REFERENCES sandbox(id),
    service_name    TEXT NOT NULL,
    method          TEXT NOT NULL,
    path            TEXT NOT NULL,
    query_params    TEXT DEFAULT '',
    request_body    TEXT DEFAULT '',
    status_code     INTEGER DEFAULT 0,
    response_body   TEXT DEFAULT '',
    request_time    REAL,
    duration_ms     INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS test_result (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sandbox_id      TEXT NOT NULL REFERENCES sandbox(id),
    model_type      TEXT NOT NULL,
    trajectory_index INTEGER NOT NULL,
    status          TEXT DEFAULT 'pending',
    score           REAL DEFAULT 0.0,
    test_code       TEXT DEFAULT '',
    test_output     TEXT DEFAULT '',
    test_scores     TEXT DEFAULT '',
    test_function_outputs TEXT DEFAULT '',
    tests_total     INTEGER DEFAULT 0,
    tests_passed    INTEGER DEFAULT 0,
    tests_failed    INTEGER DEFAULT 0,
    tests_errored   INTEGER DEFAULT 0,
    duration_generation_ms INTEGER DEFAULT 0,
    duration_execution_ms  INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_sandbox_task ON sandbox(task_pk);
CREATE INDEX IF NOT EXISTS idx_api_request_sandbox ON api_request(sandbox_id);
CREATE INDEX IF NOT EXISTS idx_test_result_sandbox ON test_result(sandbox_id);
"""


@dataclass
class Task:
    id: str
    task_id: str
    persona: str
    initial_prompt: str
    seed_prompt: str = ""
    task_type: str = ""
    difficulty: str = ""
    l1: str = ""
    l2: str = ""
    system_prompt: str = ""
    task_description: str = ""
    rubrics_json: str = ""
    test_code: str = ""
    test_weights: str = ""
    golden_trajectory: str = ""
    extra: dict = field(default_factory=dict)
    status: str = "pending"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class Sandbox:
    id: str
    task_pk: str
    model_type: str
    run_index: int = 1
    container_name: str = ""
    gateway_port: int = 0
    workdir: str = ""
    status: str = "pending"
    error: str = ""
    trajectory_json: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    score: Optional[float] = None
    grading_status: str = ""
    automated_checks_passed: int = 0
    automated_checks_total: int = 0
    started_at: Optional[float] = None
    stopped_at: Optional[float] = None


class Store:
    def __init__(self, path: Path):
        import threading
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.executescript(_SCHEMA)
        self.conn.commit()
        self._lock = threading.RLock()

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            try:
                yield self.conn
                self.conn.commit()
            except Exception:
                self.conn.rollback()
                raise

    def close(self) -> None:
        with self._lock:
            self.conn.close()

    # ---- Task ----------------------------------------------------------

    def upsert_task(self, task: Task) -> None:
        task.updated_at = time.time()
        with self.tx() as c:
            c.execute(
                """
                INSERT INTO task(id, task_id, persona, initial_prompt, seed_prompt,
                                 task_type, difficulty, l1, l2, system_prompt,
                                 task_description, rubrics_json, test_code,
                                 test_weights, golden_trajectory, extra_json,
                                 status, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                    task_id=excluded.task_id,
                    persona=excluded.persona,
                    initial_prompt=excluded.initial_prompt,
                    seed_prompt=excluded.seed_prompt,
                    task_type=excluded.task_type,
                    difficulty=excluded.difficulty,
                    l1=excluded.l1,
                    l2=excluded.l2,
                    system_prompt=excluded.system_prompt,
                    task_description=excluded.task_description,
                    rubrics_json=excluded.rubrics_json,
                    test_code=excluded.test_code,
                    test_weights=excluded.test_weights,
                    golden_trajectory=excluded.golden_trajectory,
                    extra_json=excluded.extra_json,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (
                    task.id, task.task_id, task.persona, task.initial_prompt,
                    task.seed_prompt, task.task_type, task.difficulty, task.l1,
                    task.l2, task.system_prompt, task.task_description,
                    task.rubrics_json, task.test_code, task.test_weights,
                    task.golden_trajectory, json.dumps(task.extra),
                    task.status, task.created_at, task.updated_at,
                ),
            )

    def get_task(self, task_pk: str) -> Optional[Task]:
        row = self.conn.execute("SELECT * FROM task WHERE id=?", (task_pk,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["extra"] = json.loads(d.pop("extra_json") or "{}")
        return Task(**d)

    # ---- Sandbox -------------------------------------------------------

    def upsert_sandbox(self, sandbox: Sandbox) -> None:
        with self.tx() as c:
            c.execute(
                """
                INSERT INTO sandbox(id, task_pk, model_type, run_index,
                                    container_name, gateway_port, workdir,
                                    status, error, trajectory_json,
                                    tokens_in, tokens_out, score, grading_status,
                                    automated_checks_passed, automated_checks_total,
                                    started_at, stopped_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                    status=excluded.status,
                    error=excluded.error,
                    container_name=excluded.container_name,
                    gateway_port=excluded.gateway_port,
                    workdir=excluded.workdir,
                    trajectory_json=excluded.trajectory_json,
                    tokens_in=excluded.tokens_in,
                    tokens_out=excluded.tokens_out,
                    score=excluded.score,
                    grading_status=excluded.grading_status,
                    automated_checks_passed=excluded.automated_checks_passed,
                    automated_checks_total=excluded.automated_checks_total,
                    started_at=excluded.started_at,
                    stopped_at=excluded.stopped_at
                """,
                (
                    sandbox.id, sandbox.task_pk, sandbox.model_type,
                    sandbox.run_index, sandbox.container_name,
                    sandbox.gateway_port, sandbox.workdir,
                    sandbox.status, sandbox.error,
                    sandbox.trajectory_json, sandbox.tokens_in,
                    sandbox.tokens_out, sandbox.score,
                    sandbox.grading_status,
                    sandbox.automated_checks_passed,
                    sandbox.automated_checks_total,
                    sandbox.started_at, sandbox.stopped_at,
                ),
            )

    def get_sandbox(self, sandbox_id: str) -> Optional[Sandbox]:
        row = self.conn.execute("SELECT * FROM sandbox WHERE id=?", (sandbox_id,)).fetchone()
        if not row:
            return None
        return Sandbox(**dict(row))

    # ---- API audit -----------------------------------------------------

    def insert_api_request(self, sandbox_id: str, payload: dict) -> None:
        with self.tx() as c:
            c.execute(
                """
                INSERT INTO api_request(sandbox_id, service_name, method, path,
                                        query_params, request_body, status_code,
                                        response_body, request_time, duration_ms)
                VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    sandbox_id,
                    payload.get("service_name", ""),
                    payload.get("method", "GET"),
                    payload.get("path", ""),
                    json.dumps(payload.get("query_params") or {}),
                    payload.get("request_body", ""),
                    int(payload.get("status_code", 0)),
                    payload.get("response_body", ""),
                    payload.get("request_time"),
                    int(payload.get("duration_ms", 0)),
                ),
            )

    # ---- Test results --------------------------------------------------

    def insert_test_result(self, sandbox_id: str, model_type: str,
                           trajectory_index: int, result: dict) -> int:
        with self.tx() as c:
            cur = c.execute(
                """
                INSERT INTO test_result(sandbox_id, model_type, trajectory_index,
                                        status, score, test_code, test_output,
                                        test_scores, test_function_outputs,
                                        tests_total, tests_passed, tests_failed,
                                        tests_errored, duration_generation_ms,
                                        duration_execution_ms)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    sandbox_id, model_type, trajectory_index,
                    result.get("status", "pending"),
                    float(result.get("score", 0.0)),
                    result.get("test_code", ""),
                    result.get("test_output", ""),
                    json.dumps(result.get("test_scores") or {}),
                    json.dumps(result.get("test_function_outputs") or {}),
                    int(result.get("tests_total", 0)),
                    int(result.get("tests_passed", 0)),
                    int(result.get("tests_failed", 0)),
                    int(result.get("tests_errored", 0)),
                    int(result.get("duration_generation_ms", 0)),
                    int(result.get("duration_execution_ms", 0)),
                ),
            )
            return cur.lastrowid or 0

    def list_test_results(self, task_pk: str) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT tr.* FROM test_result tr
            JOIN sandbox s ON tr.sandbox_id = s.id
            WHERE s.task_pk = ?
            ORDER BY tr.trajectory_index
            """,
            (task_pk,),
        ).fetchall()
        return [dict(r) for r in rows]
