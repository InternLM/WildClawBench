from __future__ import annotations

import ast
from pathlib import Path

import pytest

RUN_BATCH = Path(__file__).resolve().parent.parent / "eval" / "run_batch.py"


def _module() -> ast.Module:
    return ast.parse(RUN_BATCH.read_text(encoding="utf-8"), filename=str(RUN_BATCH))


def _enclosing_try(node: ast.AST, parents: dict[int, ast.AST]) -> ast.Try | None:
    cur = parents.get(id(node))
    while cur is not None:
        if isinstance(cur, ast.Try):
            return cur
        cur = parents.get(id(cur))
    return None


def _parents(tree: ast.AST) -> dict[int, ast.AST]:
    table: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            table[id(child)] = parent
    return table


def _call_sites_to_run_single_task(tree: ast.Module) -> list[ast.Call]:
    out: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id == "run_single_task":
            out.append(node)
    return out


def _submit_sites(tree: ast.Module) -> list[ast.Call]:
    out: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if (
            isinstance(fn, ast.Attribute)
            and fn.attr == "submit"
            and node.args
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "run_single_task"
        ):
            out.append(node)
    return out


def _handler_builds_soft_error_dict(handler: ast.ExceptHandler) -> bool:
    for sub in ast.walk(handler):
        if not isinstance(sub, ast.Dict):
            continue
        keys = {k.value for k in sub.keys if isinstance(k, ast.Constant)}
        if {"task_id", "scores", "error"}.issubset(keys):
            return True
    return False


def test_every_run_single_task_call_is_wrapped_in_try() -> None:
    tree = _module()
    parents = _parents(tree)
    call_sites = _call_sites_to_run_single_task(tree)
    assert call_sites, "expected at least one run_single_task() call in run_batch.py"

    unwrapped: list[int] = []
    for call in call_sites:
        if _enclosing_try(call, parents) is None:
            unwrapped.append(getattr(call, "lineno", -1))

    assert not unwrapped, (
        "ISOLATION INVARIANT (script/AGENTS.md): every run_single_task() call must "
        "be inside try/except so a per-task RuntimeError (e.g. malformed overlay CSV "
        f"from _start_task_mock_stack) cannot cascade. Unwrapped at lines: {unwrapped}"
    )


def test_every_run_single_task_handler_builds_soft_error_dict() -> None:
    tree = _module()
    parents = _parents(tree)
    call_sites = _call_sites_to_run_single_task(tree)

    bad: list[int] = []
    for call in call_sites:
        try_node = _enclosing_try(call, parents)
        assert try_node is not None, f"call at line {call.lineno} is not in a try"
        if not any(_handler_builds_soft_error_dict(h) for h in try_node.handlers):
            bad.append(getattr(call, "lineno", -1))

    assert not bad, (
        "Each wrapped run_single_task() call's except handler must build the soft "
        "error dict shape {'task_id': ..., 'scores': {}, 'error': str(exc)} so "
        "script/run.sh::run_one_rep and deliver.sh see a structured rc=1 instead "
        f"of a raw traceback. Missing at lines: {bad}"
    )


def test_threadpool_submit_call_is_covered_by_future_result_try() -> None:
    tree = _module()
    parents = _parents(tree)

    submit_calls = _submit_sites(tree)
    assert submit_calls, "expected pool.submit(run_single_task, ...) in run_batch.py"

    for call in submit_calls:
        enclosing_func = parents.get(id(call))
        while enclosing_func is not None and not isinstance(
            enclosing_func, (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            enclosing_func = parents.get(id(enclosing_func))
        assert enclosing_func is not None, "submit call must live inside a function"
        found = False
        for sub in ast.walk(enclosing_func):
            if isinstance(sub, ast.Try) and any(
                isinstance(node, ast.Attribute)
                and node.attr == "result"
                and isinstance(node.value, ast.Name)
                and node.value.id == "future"
                for node in ast.walk(sub)
            ):
                if any(_handler_builds_soft_error_dict(h) for h in sub.handlers):
                    found = True
                    break
        assert found, (
            "threadpool branch must wrap future.result() in try/except with the "
            "soft-error dict (existing pattern, do not regress)"
        )


def test_no_bare_sys_exit_immediately_after_run_single_task() -> None:
    """sys.exit(1) is acceptable AFTER the try/except converts the exception to
    result['error'], but NOT in place of the try block. This test catches the
    regression where someone removes the try and relies on sys.exit alone."""
    tree = _module()
    parents = _parents(tree)
    for call in _call_sites_to_run_single_task(tree):
        try_node = _enclosing_try(call, parents)
        assert try_node is not None
        for handler in try_node.handlers:
            for sub in ast.walk(handler):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "exit"
                    and isinstance(sub.func.value, ast.Name)
                    and sub.func.value.id == "sys"
                ):
                    pytest.fail(
                        f"except handler at line {handler.lineno} calls sys.exit() "
                        "directly — must build soft-error dict and let the "
                        "normal post-call rc=1 path handle exit"
                    )
