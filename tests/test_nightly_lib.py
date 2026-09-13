import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "script"))
from nightly_lib import (BACKEND, LEDGER, OUT_ROOT, build_run_cmd, load_ledger,
                        pending_tasks, record_result, resolve_backend,
                        save_ledger, short_id, window_active)


def test_resolve_backend_precedence(tmp_path, monkeypatch):
    monkeypatch.delenv("WCB_BACKEND", raising=False)
    assert resolve_backend(tmp_path) == "dsh"
    (tmp_path / "output").mkdir()
    (tmp_path / "output" / "backend.conf").write_text("openclaw\n")
    assert resolve_backend(tmp_path) == "openclaw"
    monkeypatch.setenv("WCB_BACKEND", "dsh")
    assert resolve_backend(tmp_path) == "dsh"


def test_backend_defaults_to_dsh_paths():
    assert BACKEND == "dsh"
    assert OUT_ROOT.name == "dsh"
    assert LEDGER.name == "ledger_qwen3.8-flash-next.json"


def test_build_run_cmd_dsh():
    cmd = build_run_cmd("dsh", "m1", Path("/t/x_task_1_a.md"))
    assert "--agent-backend" in cmd and "dsh" in cmd
    assert str(Path("/t/x_task_1_a.md")) in cmd


def test_build_run_cmd_openclaw_matched():
    cmd = build_run_cmd("openclaw", "qwen3.8-flash-next",
                        Path("/t/01_x_task_2_b.md"))
    assert "openclaw" in cmd and "--models-config" in cmd
    assert any("my_api.lb.json" in c for c in cmd)
    assert "wcb-lb/qwen3.8-flash-next" in cmd


def _mk_tasks(tmp):
    cat = tmp / "tasks" / "01_A"
    cat.mkdir(parents=True)
    (cat / "01_A_task_1_x.md").write_text("---\ntask_id: t1\n---\n## Prompt\np")
    (cat / "01_A_task_2_y.md").write_text("---\ntask_id: t2\n---\n## Prompt\np")


def test_pending_skips_completed(tmp_path):
    _mk_tasks(tmp_path)
    led = tmp_path / "l.json"
    save_ledger(led, {short_id(tmp_path / "tasks/01_A/01_A_task_1_x.md"): "completed"})
    pend = pending_tasks(tmp_path / "tasks", load_ledger(led))
    assert [p.name for p in pend] == ["01_A_task_2_y.md"]


def test_record_result_completed_failed(tmp_path):
    led = tmp_path / "l.json"
    save_ledger(led, {})
    ok = tmp_path / "s1.json"
    ok.write_text('{"score": 0.9}')
    bad = tmp_path / "s2.json"
    bad.write_text('{"error": "boom"}')
    record_result(led, "taskA", ok)
    record_result(led, "taskB", bad)
    assert load_ledger(led) == {"taskA": "completed", "taskB": "failed"}


def test_record_result_retries_failed_next_night(tmp_path):
    led = tmp_path / "l.json"
    _mk_tasks(tmp_path)
    save_ledger(led, {short_id(tmp_path / "tasks/01_A/01_A_task_1_x.md"): "failed"})
    pend = pending_tasks(tmp_path / "tasks", load_ledger(led))
    assert len(pend) == 2  # failed task is back in the queue


def test_window_bounds():
    assert window_active(datetime(2026, 9, 14, 5, 1))
    assert not window_active(datetime(2026, 9, 14, 4, 59))
    assert not window_active(datetime(2026, 9, 14, 7, 31))


def test_ledger_atomic_roundtrip(tmp_path):
    led = tmp_path / "sub" / "l.json"
    save_ledger(led, {"a": "completed"})
    assert load_ledger(led) == {"a": "completed"}
    assert not list(led.parent.glob("*.tmp"))
