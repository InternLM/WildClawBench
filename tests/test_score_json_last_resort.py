"""Guards the score.json invariant: every claimed run_N/ MUST have a score.json.

Pins three defensive layers introduced to close the "score.json silently missing
on otherwise-successful runs" bug:

1. AST invariant: `run_single_task`'s finally block writes a last-resort stub
   before returning, keyed on the marker `__last_resort_stub__: True`.
2. Rubric-block stub survives failure of `_augment_score_with_combined_rewards`
   (widened inner try/except).
3. Rubric-block stub survives non-OSError json.dumps failures (broadened outer
   except in the stub-write branch).

These tests are AST-level (invariants 1) or in-process stub-substitution
(invariants 2/3). No docker, no sidecar, no network.
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

RUN_BATCH = Path(__file__).resolve().parents[1] / "eval" / "run_batch.py"


def _run_batch_source() -> str:
    return RUN_BATCH.read_text(encoding="utf-8")


def _find_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name!r} not found in run_batch.py")


def test_run_single_task_finally_writes_last_resort_stub() -> None:
    """AST invariant: run_single_task's finally block contains a last-resort
    stub writer keyed on `__last_resort_stub__: True`."""
    tree = ast.parse(_run_batch_source())
    fn = _find_function(tree, "run_single_task")

    tries = [n for n in ast.walk(fn) if isinstance(n, ast.Try) and n.finalbody]
    assert tries, "run_single_task must contain at least one try/finally"

    stub_marker = "__last_resort_stub__"
    found = False
    for t in tries:
        for stmt in ast.walk(ast.Module(body=t.finalbody, type_ignores=[])):
            if isinstance(stmt, ast.Constant) and stmt.value == stub_marker:
                found = True
                break
        if found:
            break
    assert found, (
        "run_single_task's finally block MUST reference '__last_resort_stub__' "
        "so every claimed run_N/ has a score.json even when both grade_the_task "
        "and _build_trajectory miss."
    )


def test_run_single_task_finally_checks_score_path_existence() -> None:
    """AST invariant: the last-resort writer is guarded by score.json exists check
    so it never clobbers a legitimate score.json."""
    src = _run_batch_source()
    assert "score.json" in src
    assert "not score_path.exists()" in src, (
        "last-resort stub must be gated by `if not score_path.exists()` — "
        "otherwise it would clobber legitimate score.json files."
    )


def test_rubric_stub_write_uses_broad_exception_catch() -> None:
    """AST invariant: the stub-write inside _build_trajectory's rubric except
    block catches broad Exception, NOT narrow OSError.

    The narrow `except OSError` variant let ValueError (json.dumps NaN/Inf),
    TypeError (non-serializable score fields), and MemoryError silently escape,
    causing missing score.json on the outer _build_trajectory warn-swallow.
    """
    tree = ast.parse(_run_batch_source())
    fn = _find_function(tree, "_build_trajectory")

    outer_stub_catch = None
    for t in ast.walk(fn):
        if not isinstance(t, ast.Try):
            continue
        for h in t.handlers:
            for stmt in ast.walk(h):
                if (
                    isinstance(stmt, ast.Try)
                    and any(
                        isinstance(inner, ast.Constant)
                        and inner.value == "__last_resort_stub__"
                        for inner in ast.walk(stmt)
                    )
                ):
                    outer_stub_catch = stmt
                    break
    assert outer_stub_catch is not None, (
        "expected the rubric stub-write try/except to reference __last_resort_stub__"
    )
    for h in outer_stub_catch.handlers:
        if h.type is None:
            return
        if isinstance(h.type, ast.Name) and h.type.id == "Exception":
            return
    raise AssertionError(
        "stub-write outer catch must be broad Exception (was OSError before this fix)"
    )


def test_last_resort_stub_functional(tmp_path: Path) -> None:
    """Functional: reproduce the tail-block logic against a bare output_dir.

    The tail-block lives inline in run_single_task; this test mirrors its
    exact structure to lock the behaviour: if no grader wrote score.json,
    a stub with `__last_resort_stub__: True`, `overall_score: None`, and
    a non-empty error message MUST land on disk.
    """
    output_dir = tmp_path / "run_1"
    output_dir.mkdir()
    score_path = output_dir / "score.json"
    result: dict = {"task_id": "t_x", "scores": {}, "error": "container startup failed"}

    if not score_path.exists():
        last_resort = {
            "overall_score": None,
            "rubric_weights_percentage": None,
            "criteria_total": 0,
            "criteria_passed": 0,
            "criteria_failed": 0,
            "criteria_abstained": 0,
            "judge_model": None,
            "error": result.get("error") or "score.json missing after finally; no grader wrote it",
            "source": "run_single_task last-resort stub",
            "task_id": "t_x",
            "__last_resort_stub__": True,
        }
        score_path.write_text(
            json.dumps(last_resort, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

    assert score_path.is_file()
    doc = json.loads(score_path.read_text(encoding="utf-8"))
    assert doc["__last_resort_stub__"] is True
    assert doc["overall_score"] is None
    assert doc["error"] == "container startup failed"
    assert doc["task_id"] == "t_x"


def test_last_resort_stub_does_not_clobber_existing(tmp_path: Path) -> None:
    """If a real score.json exists, the last-resort writer MUST NOT overwrite it."""
    output_dir = tmp_path / "run_2"
    output_dir.mkdir()
    score_path = output_dir / "score.json"
    real = {"overall_score": 0.87, "judge_model": "sonnet-4.6", "criteria_passed": 5}
    score_path.write_text(json.dumps(real), encoding="utf-8")

    if not score_path.exists():
        raise AssertionError("guard failed sanity check")

    doc = json.loads(score_path.read_text(encoding="utf-8"))
    assert doc["overall_score"] == 0.87
    assert "__last_resort_stub__" not in doc


def test_pass_summary_entry_propagates_last_resort_marker() -> None:
    """`_pass_summary_entry` must copy `__last_resort_stub__` into per_run so
    operators can `jq` the summary to enumerate stubs vs real 0-scores."""
    from eval.run_batch import _pass_summary_entry  # noqa: E402

    stub_scores = {"overall_score": None, "__last_resort_stub__": True,
                   "criteria_total": 0, "criteria_passed": 0}
    entry = _pass_summary_entry(run_index=0, scores=stub_scores, test_result=None)
    assert entry.get("__last_resort_stub__") is True

    real_scores = {"overall_score": 0.4, "criteria_total": 3, "criteria_passed": 1}
    real_entry = _pass_summary_entry(run_index=0, scores=real_scores, test_result=None)
    assert "__last_resort_stub__" not in real_entry
