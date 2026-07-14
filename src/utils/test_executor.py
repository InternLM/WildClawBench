"""Execute generated tests against the agent's deliverables + live mock stack.

Runs the LLM-generated `test_outputs.py` inside a transient container joined to
the mock-stack docker network, parses pass/fail per test, and computes the
weighted reward — the missing half of the kensei2 testgen → execute → reward
pipeline.

Returns a dict shaped for `bundle.write_bundle`'s `__test_result__` consumer:
  tests_total, tests_passed, tests_failed, tests_errored,
  test_scores (JSON str: {qualified_name: "passed"|"failed"|"errored"}),
  test_output (raw stdout/stderr text),
  test_code (verbatim copy of the executed code, for the harbor bundle),
  reward (float, unclamped; (Σ passed_positive_w − Σ |triggered_negative_w|) / Σ positive_w).
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

logger = logging.getLogger(__name__)


_RUNNER_SCRIPT = textwrap.dedent('''
    import asyncio, importlib.util, inspect, json, signal, sys, traceback, unittest

    PER_TEST_TIMEOUT = int(__import__("os").environ.get("WCB_PER_TEST_TIMEOUT", "30"))

    class _TestTimeout(Exception):
        pass

    class _Skipped(Exception):
        pass

    def _alarm_handler(signum, frame):
        raise _TestTimeout(f"per-test timeout ({PER_TEST_TIMEOUT}s)")

    signal.signal(signal.SIGALRM, _alarm_handler)

    # Hand-authored suites commonly `import pytest` at module top level but never
    # use fixtures (this runner instantiates Test* classes and calls test_*
    # methods directly — no pytest involved). The sandbox image may not ship
    # pytest globally, so a bare import would import_error the whole suite. When
    # the real pytest is absent, install a permissive stub so the import (and any
    # incidental pytest.* references) succeed; a real pytest takes precedence.
    # The stub also makes pytest.skip / pytest.mark.skip / skipif raise a
    # recognizable _Skipped so those tests are recorded skipped (not run/errored).
    try:
        import pytest  # noqa: F401
        _REAL_PYTEST = True
    except Exception:
        _REAL_PYTEST = False
        def _skip(*a, **k):
            raise _Skipped(a[0] if a else "")
        class _PytestStub:
            # pytest.skip(...) and pytest.fail(...) have call-time semantics.
            def skip(self, *a, **k):
                raise _Skipped(a[0] if a else "")
            def fail(self, *a, **k):
                raise AssertionError(a[0] if a else "pytest.fail")
            def __getattr__(self, _n):
                return _PytestStub()
            def __call__(self, *a, **k):
                # Decorator forms: @pytest.fixture, @pytest.mark.parametrize(...),
                # used as @deco or @deco(...). Return the function unchanged when
                # used as a bare decorator; otherwise return a passthrough deco.
                if len(a) == 1 and callable(a[0]) and not k:
                    return a[0]
                def _passthrough(fn=None):
                    return fn if fn is not None else (lambda g: g)
                return _passthrough
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
        sys.modules["pytest"] = _PytestStub()

    # ------------------------------------------------------------------ #
    # Built-in fixtures. Persona/inject suites authored against the Talos
    # CHECKERS contract take two pytest fixtures the no-fixture runner used to
    # reject outright (every test -> errored, IAN report H5):
    #   state         -> the live agent state dict (audit, per-service store,
    #                    last_response), shipped as /tests/agent_state.json
    #   task_checkers -> {checker_id: checker} from the sibling task.py CHECKERS
    #                    list, shipped as /tests/task/task.py
    # We synthesize both here so the suite runs as authored. Anything the
    # runner cannot supply still errors (below), preserving the old behavior
    # for genuinely unsatisfiable fixtures.
    import os as _os
    _FIXTURES = {}
    try:
        _sp = "/tests/agent_state.json"
        if _os.path.exists(_sp):
            with open(_sp) as _f:
                _FIXTURES["state"] = json.load(_f)
        else:
            _FIXTURES["state"] = {}
    except Exception as _e:
        print(f"[runner] state fixture load failed: {_e}", file=sys.stderr)
        _FIXTURES["state"] = {}
    try:
        if _os.path.isdir("/tests/task"):
            sys.path.insert(0, "/tests/task")
            import task as _taskmod  # /tests/task/task.py
            _FIXTURES["task_checkers"] = {c["id"]: c for c in _taskmod.CHECKERS}
    except Exception as _e:
        print(f"[runner] task_checkers fixture load failed: {_e}", file=sys.stderr)

    def _kwargs_for(req):
        # Return (kwargs, missing). kwargs supplies every required param the
        # runner knows how to build; missing lists the rest.
        kwargs, missing = {}, []
        for p in req:
            if p in _FIXTURES:
                kwargs[p] = _FIXTURES[p]
            else:
                missing.append(p)
        return kwargs, missing

    def _is_skip_exc(e):
        # Recognize our stub skip, real pytest/unittest skips by class name.
        if isinstance(e, _Skipped):
            return True
        n = type(e).__name__
        return n in ("Skipped", "SkipTest")

    spec = importlib.util.spec_from_file_location("t", "/tests/test_outputs.py")
    mod = importlib.util.module_from_spec(spec)
    out = {"import_error": None, "results": {}, "collected": 0}
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        out["import_error"] = f"{type(e).__name__}: {e}\\n{traceback.format_exc()}"
        # Targeted hint for the two most common authoring mistakes: importing a
        # local/sibling module (e.g. `import task`) or a 3rd-party dependency
        # that is not shipped into the hermetic /tests sandbox.
        if isinstance(e, ModuleNotFoundError):
            missing = getattr(e, "name", "") or ""
            out["import_hint"] = (
                f"suite imports module '{missing}' which is not shipped to the "
                f"sandbox; the runner ships only test_outputs.py (stdlib only, "
                f"no local task.py / conftest.py / 3rd-party deps)"
            )
        print(json.dumps(out)); sys.exit(0)

    def _required_param_names(fn):
        # Positional/keyword params with no default, excluding self/cls.
        try:
            sig = inspect.signature(fn)
        except (TypeError, ValueError):
            return []
        req = []
        for p in sig.parameters.values():
            if p.name in ("self", "cls"):
                continue
            if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
                continue
            if p.default is p.empty:
                req.append(p.name)
        return req

    def _record(results, full, callable_fn, is_async=False, kwargs=None):
        print(f"[runner] running {full}", file=sys.stderr, flush=True)
        signal.alarm(PER_TEST_TIMEOUT)
        try:
            res = callable_fn(**(kwargs or {}))
            if inspect.iscoroutine(res):  # (F) async test or sync fn returning a coroutine
                asyncio.run(res)
            results[full] = {"status": "passed"}
        except _TestTimeout as e:
            results[full] = {"status": "errored", "error": f"timeout: {e}", "traceback": ""}
        except AssertionError as e:
            results[full] = {"status": "failed",
                             "error": f"AssertionError: {e}",
                             "traceback": traceback.format_exc()}
        except BaseException as e:  # noqa: BLE001 - catch unittest SkipTest too
            if _is_skip_exc(e):
                results[full] = {"status": "skipped", "error": f"skipped: {e}"}
            else:
                results[full] = {"status": "errored",
                                 "error": f"{type(e).__name__}: {e}",
                                 "traceback": traceback.format_exc()}
        finally:
            signal.alarm(0)

    def _run_method(results, owner, inst, cls_name, m):
        # Resolve WITHOUT triggering descriptors/properties (C): a `test_*`
        # property must never auto-execute during collection, and non-callable
        # `test_*` data attributes (e.g. test_cases=[...]) are skipped, not
        # errored. static/classmethods bind correctly via getattr(inst, m).
        full = f"{cls_name}::{m}"
        try:
            raw = inspect.getattr_static(owner, m)
        except AttributeError:
            return False
        if isinstance(raw, property):
            return False
        if not (inspect.isfunction(raw) or inspect.ismethod(raw)
                or isinstance(raw, (staticmethod, classmethod))):
            return False  # data attribute named test_* — not a test
        fn = getattr(inst, m)
        if not callable(fn):
            return False
        # (D) fixture-style signature: supply known fixtures (state,
        # task_checkers); error only on params the runner can't build.
        req = _required_param_names(fn)
        kwargs, missing = _kwargs_for(req)
        if missing:
            results[full] = {
                "status": "errored",
                "error": ("requires fixtures/params " + ", ".join(missing)
                          + "; the runner cannot supply them "
                          + "(remove pytest fixtures or make the test self-contained)"),
                "traceback": "",
            }
            return True
        is_async = inspect.iscoroutinefunction(fn)
        _record(results, full, fn, is_async=is_async, kwargs=kwargs)
        return True

    # ---- Collect & run Test* classes (incl. unittest.TestCase) ----
    for cls_name in sorted(dir(mod)):
        cls = getattr(mod, cls_name)
        if not (inspect.isclass(cls) and cls_name.startswith("Test")):
            continue
        is_unittest = issubclass(cls, unittest.TestCase)
        # Instantiate. unittest.TestCase needs a method name; use a dummy that
        # exists on all TestCase subclasses so __init__ succeeds, then we drive
        # setUp/tearDown manually around each test.
        try:
            inst = cls("run") if is_unittest else cls()
        except Exception:
            # Retry unittest with a guaranteed-present method name.
            try:
                inst = cls(methodName="__init__") if is_unittest else None
            except Exception:
                inst = None
        if inst is None:
            tb = traceback.format_exc()
            for m in dir(cls):
                if m.startswith("test_"):
                    out["collected"] += 1
                    out["results"][f"{cls_name}::{m}"] = {
                        "status": "errored",
                        "error": "ctor: could not instantiate test class",
                        "traceback": tb,
                    }
            continue
        for m in sorted(dir(cls)):
            if not m.startswith("test_"):
                continue
            # (B) unittest lifecycle: setUp before, tearDown after, each test.
            if is_unittest:
                full = f"{cls_name}::{m}"
                raw = None
                try:
                    raw = inspect.getattr_static(cls, m)
                except AttributeError:
                    pass
                if isinstance(raw, property) or not (
                    inspect.isfunction(raw) or inspect.ismethod(raw)
                    or isinstance(raw, (staticmethod, classmethod))
                ):
                    continue
                fn = getattr(inst, m)
                if not callable(fn):
                    continue
                req = _required_param_names(fn)
                _kw, _missing = _kwargs_for(req)
                if _missing:
                    out["collected"] += 1
                    out["results"][full] = {
                        "status": "errored",
                        "error": "requires fixtures/params " + ", ".join(_missing),
                        "traceback": "",
                    }
                    continue
                out["collected"] += 1
                def _drive(_fn=fn, _inst=inst, **_kwargs):
                    _inst.setUp()
                    try:
                        r = _fn(**_kwargs)
                        if inspect.iscoroutine(r):
                            asyncio.run(r)
                    finally:
                        _inst.tearDown()
                _record(out["results"], full, _drive, kwargs=_kw)
            else:
                if _run_method(out["results"], cls, inst, cls_name, m):
                    out["collected"] += 1

    # ---- (A) Collect & run top-level test_* functions (no class) ----
    for fn_name in sorted(dir(mod)):
        if not fn_name.startswith("test_"):
            continue
        try:
            raw = inspect.getattr_static(mod, fn_name)
        except AttributeError:
            continue
        if not (inspect.isfunction(raw) or isinstance(raw, staticmethod)):
            continue  # skip module-level data named test_*
        fn = getattr(mod, fn_name)
        if not callable(fn):
            continue
        full = f"<module>::{fn_name}"
        req = _required_param_names(fn)
        kwargs, missing = _kwargs_for(req)
        if missing:
            out["collected"] += 1
            out["results"][full] = {
                "status": "errored",
                "error": ("requires fixtures/params " + ", ".join(missing)
                          + "; the runner cannot supply them"),
                "traceback": "",
            }
            continue
        out["collected"] += 1
        _record(out["results"], full, fn, is_async=inspect.iscoroutinefunction(fn), kwargs=kwargs)

    print(json.dumps(out))
''').strip()


def _compute_reward(results: Mapping[str, dict], weights: Mapping[str, float]) -> float:
    """Kensei2 canonical: (pos_earned - neg_penalty) / pos_total.

    - pos_total: sum of positive weights (desired behaviours)
    - pos_earned: sum of positive weights whose test passed
    - neg_penalty: sum of |w| for negative-weight tests that PASSED (triggered).
      The negative tests in this corpus are VIOLATION-DETECTORS: written so
      PASS == the forbidden behaviour occurred (e.g. `assert distractor_touched
      > 0`, `assert stale_value_present`). So a negative test that PASSES means
      the agent did the bad thing → penalise |w|; a negative test that FAILS
      means the agent avoided it → no penalty. This matches the june-7 canonical
      (Kensei2) reward and the rubric grader, which likewise penalises a
      negative criterion only when it is *satisfied* (fired). Penalising failed
      negatives instead — as a prior cut did — inverts the polarity and punishes
      good behaviour (every avoided distractor scored as a failure). The
      `max(0, …)` floor means a violation spree zeroes the run rather than going
      negative.
    - falls back to tests_passed/tests_total when pos_total <= 0
    Returns the raw signed ratio; negative when penalties outweigh earned
    points. No clamp — downstream consumers see the true polarity of the run.
    Mirror copies of this formula live in src/utils/harbor/test_sh.py and
    src/utils/harbor/ctrf.py; they MUST stay byte-aligned so exported task
    bundles compute the same reward as the harness.
    """
    if not weights:
        return 0.0
    # A.1+A.2 parity with src/utils/harbor/test_sh.py + src/utils/harbor/ctrf.py:
    # three normalized shapes (full FQN / class-qualified / bare) so a weight
    # key in any form resolves; class-qualified keys must NOT fall through to
    # bare-multiset (would leak A.2 loose semantics into precise lookups).
    passed_full: set[str] = set()
    passed_class_qual: set[str] = set()
    passed_bare: set[str] = set()
    for full_name, res in results.items():
        if res.get("status") != "passed":
            continue
        passed_full.add(full_name)
        parts = full_name.split("::")
        if len(parts) >= 2:
            passed_bare.add(parts[-1])
        if len(parts) >= 3:
            passed_class_qual.add("::".join(parts[-2:]))

    def _key_passed(key: str) -> bool:
        if key in passed_full:
            return True
        if "::" in key:
            return key in passed_class_qual
        return key in passed_bare

    pos_total = sum(float(w) for w in weights.values() if w > 0)
    pos_earned = sum(float(w) for n, w in weights.items() if w > 0 and _key_passed(n))
    neg_penalty = sum(abs(float(w)) for n, w in weights.items() if w < 0 and _key_passed(n))

    if pos_total <= 0:
        scored = [r for r in results.values() if r.get("status") != "skipped"]
        total = len(scored)
        passed = sum(1 for r in scored if r.get("status") == "passed")
        return round(passed / total, 4) if total else 0.0
    # User formula (verbatim, no clamp): a violation spree may drive the reward
    # below 0 to reflect the true magnitude of guardrail breaches.
    #   final_reward = (Σ passed_positive_w − Σ |triggered_negative_w|) / Σ positive_w
    return round((pos_earned - neg_penalty) / pos_total, 4)


def execute_tests(
    *,
    test_code: str,
    test_weights_json: str,
    workspace_dir: Path,
    mock_env_dict: Optional[Mapping[str, str]] = None,
    network: Optional[str] = None,
    image: str = "wildclawbench-ubuntu:v1.3",
    timeout: int = 300,
    checkers_code: Optional[str] = None,
    agent_state_json: Optional[str] = None,
) -> Dict[str, Any]:
    """Run `test_code` against the live mock stack. Returns a test_result dict.

    `workspace_dir` is mounted read-only at BOTH /tmp_workspace (the cwd) and
    /workspace, with WORKSPACE=/tmp_workspace exported, so the generated
    `test_outputs.py` (which reads `WORKSPACE`, default "/workspace") and any
    relative-path / hardcoded-/workspace readers all resolve against the agent's
    produced artifacts. `mock_env_dict` carries <SVC>_URL env vars
    pointing at the running mock-stack container hostnames; `network` is the
    docker network those containers live on.

    `checkers_code` (a task.py defining a CHECKERS list) and `agent_state_json`
    (the live agent state dict) are shipped into the sandbox so fixture-based
    suites authored against the Talos CHECKERS contract — `def test_x(state,
    task_checkers)` — run as authored instead of erroring on missing fixtures.
    """
    if not test_code.strip():
        return {
            "tests_total": 0, "tests_passed": 0, "tests_failed": 0, "tests_errored": 0,
            "test_scores": "{}", "test_output": "", "test_code": "",
            "reward": 0.0, "duration_execution_ms": 0, "error": "empty test_code",
        }

    try:
        weights = json.loads(test_weights_json) if test_weights_json else {}
        if not isinstance(weights, dict):
            weights = {}
    except Exception:
        weights = {}

    tmp = Path(tempfile.mkdtemp(prefix="wcb-testexec-"))
    started = time.time()
    output = ""
    try:
        (tmp / "test_outputs.py").write_text(test_code, encoding="utf-8")
        (tmp / "test_weights.json").write_text(test_weights_json or "{}", encoding="utf-8")
        (tmp / "runner.py").write_text(_RUNNER_SCRIPT, encoding="utf-8")
        # Ship the CHECKERS module + live agent state so fixture-based suites
        # (state, task_checkers) run as authored (see _RUNNER_SCRIPT fixtures).
        if checkers_code and checkers_code.strip():
            (tmp / "task").mkdir(parents=True, exist_ok=True)
            (tmp / "task" / "task.py").write_text(checkers_code, encoding="utf-8")
        if agent_state_json and agent_state_json.strip():
            (tmp / "agent_state.json").write_text(agent_state_json, encoding="utf-8")

        from src.utils.docker_utils import (
            build_env_args,
            _validate_docker_token,
        )

        ws_mount = workspace_dir if workspace_dir and workspace_dir.is_dir() else tmp
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{tmp}:/tests:ro",
            "-v", f"{ws_mount}:/tmp_workspace:ro",
            # Generated test_outputs.py resolves deliverables via
            # WORKSPACE = os.environ.get("WORKSPACE", "/workspace") + _file_content().
            # The agent's workspace is mounted at /tmp_workspace, so without these
            # two lines every absolute-path read landed on the empty default
            # /workspace and ALL content assertions failed "<file> not found"
            # even when the file existed (ROSE_002 glassy_lagoon: 0/42, files
            # present in workspace_full/). Expose the SAME workspace at /workspace
            # too (honors the default + the docstring) and pin WORKSPACE to the
            # real mount so both relative- and absolute-path readers resolve.
            "-v", f"{ws_mount}:/workspace:ro",
            "-w", "/tmp_workspace",
            "-e", "WORKSPACE=/tmp_workspace",
        ]
        if network:
            _validate_docker_token("network", network)
            cmd += ["--network", network]

        proxy_http = os.environ.get("HTTP_PROXY_INNER", "")
        proxy_https = os.environ.get("HTTPS_PROXY_INNER", "")
        no_proxy_value = (
            os.environ.get("NO_PROXY_INNER", "*")
            if not proxy_http
            else os.environ.get("NO_PROXY_INNER", "")
        )
        env_pairs: list[tuple[str, str]] = [
            ("http_proxy", proxy_http),
            ("https_proxy", proxy_https),
            ("HTTP_PROXY", proxy_http),
            ("HTTPS_PROXY", proxy_https),
            ("no_proxy", no_proxy_value),
            ("NO_PROXY", no_proxy_value),
        ]
        for k, v in (mock_env_dict or {}).items():
            env_pairs.append((k, v))
        cmd += build_env_args(env_pairs)
        cmd += [_validate_docker_token("image", image), "python3", "/tests/runner.py"]

        logger.info("[testexec] docker run image=%s network=%s tests=%s",
                    image, network or "<host>", tmp / "test_outputs.py")
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False,
        )
        output = (proc.stdout or "") + ("\n[stderr]\n" + proc.stderr if proc.stderr else "")
        last_line = (proc.stdout or "").strip().splitlines()
        payload: Dict[str, Any] = {}
        for line in reversed(last_line):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    payload = json.loads(line)
                    # The raw payload (qualified <module>::/Class:: keys) is
                    # parsed into test_scores; keep the persisted log human-
                    # facing only.
                    output = output.replace(line, "[runner JSON payload omitted — parsed into test_scores]", 1)
                    break
                except Exception:
                    continue

        if not payload:
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]
            logger.warning(
                "[testexec] no JSON payload parsed; rc=%s tail=%s",
                proc.returncode, " | ".join(tail),
            )
            return {
                "tests_total": 0, "tests_passed": 0, "tests_failed": 0,
                "tests_errored": 0, "test_scores": "{}", "test_output": output,
                "test_code": test_code, "reward": 0.0,
                "duration_execution_ms": int((time.time() - started) * 1000),
                "error": f"runner produced no parseable output (rc={proc.returncode})",
            }

        if payload.get("import_error"):
            first_line = payload["import_error"].splitlines()[0]
            logger.warning(
                "[testexec] import failed for test_outputs.py: %s", first_line,
            )
            return {
                "tests_total": 0, "tests_passed": 0, "tests_failed": 0,
                "tests_errored": 0, "test_scores": "{}", "test_output": output,
                "test_code": test_code, "reward": 0.0,
                "duration_execution_ms": int((time.time() - started) * 1000),
                "error": "import: " + first_line,
            }

        results: Dict[str, dict] = payload.get("results", {}) or {}
        scores: Dict[str, str] = {k: v.get("status", "errored") for k, v in results.items()}
        tests_passed = sum(1 for v in scores.values() if v == "passed")
        tests_failed = sum(1 for v in scores.values() if v == "failed")
        tests_errored = sum(1 for v in scores.values() if v == "errored")
        tests_skipped = sum(1 for v in scores.values() if v == "skipped")
        tests_total = tests_passed + tests_failed + tests_errored
        reward = _compute_reward(results, weights)

        if not results:
            err = "no tests collected (no Test* classes or test_* functions found)"
            logger.warning("[testexec] %s", err)
            return {
                "tests_total": 0, "tests_passed": 0, "tests_failed": 0,
                "tests_errored": 0, "tests_skipped": 0, "test_scores": "{}",
                "test_output": output, "test_code": test_code, "reward": 0.0,
                "duration_execution_ms": int((time.time() - started) * 1000),
                "error": err,
            }

        logger.info(
            "[testexec] %d/%d passed (%d failed, %d errored, %d skipped) — reward=%.3f",
            tests_passed, tests_total, tests_failed, tests_errored, tests_skipped, reward,
        )
        return {
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_errored": tests_errored,
            "tests_skipped": tests_skipped,
            "test_scores": json.dumps(scores),
            # Artifact-facing map: bare test names (qualified keys stay only in
            # test_scores, where weight matching needs them).
            "test_function_outputs": json.dumps({
                k.split("::")[-1]: v.get("error", "") for k, v in results.items()
            }),
            "test_output": output,
            "test_code": test_code,
            "reward": reward,
            "duration_execution_ms": int((time.time() - started) * 1000),
            "error": "",
        }
    except subprocess.TimeoutExpired:
        return {
            "tests_total": 0, "tests_passed": 0, "tests_failed": 0, "tests_errored": 0,
            "test_scores": "{}", "test_output": output, "test_code": test_code,
            "reward": 0.0, "duration_execution_ms": int((time.time() - started) * 1000),
            "error": f"timeout after {timeout}s",
        }
    except Exception as exc:
        logger.exception("[testexec] failed: %s", exc)
        return {
            "tests_total": 0, "tests_passed": 0, "tests_failed": 0, "tests_errored": 0,
            "test_scores": "{}", "test_output": output, "test_code": test_code,
            "reward": 0.0, "duration_execution_ms": int((time.time() - started) * 1000),
            "error": str(exc),
        }
    finally:
        try:
            shutil.rmtree(tmp, ignore_errors=True)
        except Exception:
            pass
