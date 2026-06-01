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
  reward (float, 0..1; sum(weight × pass) / sum(|weight|)).
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
    import importlib.util, inspect, json, signal, sys, traceback

    PER_TEST_TIMEOUT = int(__import__("os").environ.get("WCB_PER_TEST_TIMEOUT", "30"))

    class _TestTimeout(Exception):
        pass

    def _alarm_handler(signum, frame):
        raise _TestTimeout(f"per-test timeout ({PER_TEST_TIMEOUT}s)")

    signal.signal(signal.SIGALRM, _alarm_handler)

    spec = importlib.util.spec_from_file_location("t", "/tests/test_outputs.py")
    mod = importlib.util.module_from_spec(spec)
    out = {"import_error": None, "results": {}}
    try:
        spec.loader.exec_module(mod)
    except Exception as e:
        out["import_error"] = f"{type(e).__name__}: {e}\\n{traceback.format_exc()}"
        print(json.dumps(out)); sys.exit(0)

    for cls_name in sorted(dir(mod)):
        cls = getattr(mod, cls_name)
        if not (inspect.isclass(cls) and cls_name.startswith("Test")):
            continue
        try:
            inst = cls()
        except Exception as e:
            tb = traceback.format_exc()
            for m in dir(cls):
                if m.startswith("test_"):
                    out["results"][f"{cls_name}::{m}"] = {
                        "status": "errored",
                        "error": f"ctor: {type(e).__name__}: {e}",
                        "traceback": tb,
                    }
            continue
        for m in sorted(dir(cls)):
            if not m.startswith("test_"):
                continue
            full = f"{cls_name}::{m}"
            print(f"[runner] running {full}", file=sys.stderr, flush=True)
            signal.alarm(PER_TEST_TIMEOUT)
            try:
                getattr(inst, m)()
                out["results"][full] = {"status": "passed"}
            except _TestTimeout as e:
                out["results"][full] = {
                    "status": "errored",
                    "error": f"timeout: {e}",
                    "traceback": "",
                }
            except AssertionError as e:
                out["results"][full] = {
                    "status": "failed",
                    "error": f"AssertionError: {e}",
                    "traceback": traceback.format_exc(),
                }
            except Exception as e:
                out["results"][full] = {
                    "status": "errored",
                    "error": f"{type(e).__name__}: {e}",
                    "traceback": traceback.format_exc(),
                }
            finally:
                signal.alarm(0)
    print(json.dumps(out))
''').strip()


def _compute_reward(results: Mapping[str, dict], weights: Mapping[str, float]) -> float:
    """Kensei2 canonical: max(0, (pos_earned - neg_penalty) / pos_total).

    Mirrors `Kensei2._compute_test_reward` (kensei2.py:3202).
    - pos_total: sum of positive weights (desired behaviours)
    - pos_earned: sum of positive weights whose test passed
    - neg_penalty: sum of |w| for negative-weight tests that passed (triggered)
    - falls back to tests_passed/tests_total when pos_total <= 0
    Returns 0..1.
    """
    if not weights:
        return 0.0
    passed_names: set[str] = set()
    for full_name, res in results.items():
        if res.get("status") != "passed":
            continue
        passed_names.add(full_name)
        if "::" in full_name:
            passed_names.add(full_name.split("::", 1)[-1])

    pos_total = sum(float(w) for w in weights.values() if w > 0)
    pos_earned = sum(float(w) for n, w in weights.items() if w > 0 and n in passed_names)
    neg_penalty = sum(abs(float(w)) for n, w in weights.items() if w < 0 and n in passed_names)

    if pos_total <= 0:
        total = len(results)
        passed = sum(1 for r in results.values() if r.get("status") == "passed")
        return round(passed / total, 4) if total else 0.0
    return round(max(0.0, (pos_earned - neg_penalty) / pos_total), 4)


def execute_tests(
    *,
    test_code: str,
    test_weights_json: str,
    workspace_dir: Path,
    mock_env_dict: Optional[Mapping[str, str]] = None,
    network: Optional[str] = None,
    image: str = "wildclawbench-ubuntu:v1.3",
    timeout: int = 300,
) -> Dict[str, Any]:
    """Run `test_code` against the live mock stack. Returns a test_result dict.

    `workspace_dir` is mounted read-only at /workspace inside the runner so
    `file_exists("path/file")` and `read_file("path/file")` resolve relative to
    the agent's produced artifacts. `mock_env_dict` carries <SVC>_URL env vars
    pointing at the running mock-stack container hostnames; `network` is the
    docker network those containers live on.
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

        ws_mount = workspace_dir if workspace_dir and workspace_dir.is_dir() else tmp
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{tmp}:/tests:ro",
            "-v", f"{ws_mount}:/tmp_workspace:ro",
            "-w", "/tmp_workspace",
        ]
        if network:
            cmd += ["--network", network]

        # Must mirror docker_utils.py:32-43. amd64-emulated images inherit a
        # phantom proxy on arm64 hosts; no_proxy="*" is required or every
        # docker-bridge HTTP call hangs to timeout.
        proxy_http = os.environ.get("HTTP_PROXY_INNER", "")
        proxy_https = os.environ.get("HTTPS_PROXY_INNER", "")
        no_proxy_value = (
            os.environ.get("NO_PROXY_INNER", "*")
            if not proxy_http
            else os.environ.get("NO_PROXY_INNER", "")
        )
        proxy_env = {
            "http_proxy": proxy_http,
            "https_proxy": proxy_https,
            "HTTP_PROXY": proxy_http,
            "HTTPS_PROXY": proxy_https,
            "no_proxy": no_proxy_value,
            "NO_PROXY": no_proxy_value,
        }
        for k, v in proxy_env.items():
            cmd += ["-e", f"{k}={v}"]

        for k, v in (mock_env_dict or {}).items():
            cmd += ["-e", f"{k}={v}"]
        cmd += [image, "python3", "/tests/runner.py"]

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
        tests_total = len(scores)
        tests_passed = sum(1 for v in scores.values() if v == "passed")
        tests_failed = sum(1 for v in scores.values() if v == "failed")
        tests_errored = sum(1 for v in scores.values() if v == "errored")
        reward = _compute_reward(results, weights)

        logger.info(
            "[testexec] %d/%d passed (%d failed, %d errored) — reward=%.3f",
            tests_passed, tests_total, tests_failed, tests_errored, reward,
        )
        return {
            "tests_total": tests_total,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_errored": tests_errored,
            "test_scores": json.dumps(scores),
            "test_function_outputs": json.dumps({
                k: v.get("error", "") for k, v in results.items()
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
