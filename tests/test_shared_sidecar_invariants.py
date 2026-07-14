"""AST + regex invariants for the shared LiteLLM sidecar + network bootstrap.

Pins Fix A (shared network) + Fix B (shared LiteLLM sidecar) from
docs/reps-failure-diagnosis.md. See script/AGENTS.md "Shared-infra (Fix A+B)"
and src/utils/AGENTS.md for the underlying contract.

These tests are STATIC (no docker, no network, no subprocess) so they can run
on any host. Same posture as tests/test_run_single_task_isolation.py.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_BATCH = REPO_ROOT / "eval" / "run_batch.py"
BOOTSTRAP = REPO_ROOT / "eval" / "bootstrap_sidecar.py"
RUN_SH = REPO_ROOT / "script" / "run.sh"


# ---------- helpers ----------


def _read(path: Path) -> str:
    assert path.is_file(), f"required file missing: {path}"
    return path.read_text(encoding="utf-8")


def _ast(path: Path) -> ast.Module:
    return ast.parse(_read(path), filename=str(path))


# ---------- eval/bootstrap_sidecar.py: exists, valid CLI, emits 5 keys ----------


def test_bootstrap_sidecar_module_exists_and_parses() -> None:
    """The python-side helper must exist and be importable as AST."""
    tree = _ast(BOOTSTRAP)
    assert any(
        isinstance(n, ast.FunctionDef) and n.name == "main"
        for n in ast.walk(tree)
    ), "eval/bootstrap_sidecar.py must define a main() entry point"


def test_bootstrap_sidecar_declares_name_suffix_arg() -> None:
    """argparse contract: --name-suffix is the only required arg.

    Bash passes `$$-$(date +%Y%m%d_%H%M%S)`. If this changes, the
    bash side in script/run.sh::bootstrap_shared_sidecar must change too.
    """
    src = _read(BOOTSTRAP)
    assert "--name-suffix" in src, "bootstrap_sidecar.py must accept --name-suffix"


def test_bootstrap_sidecar_emits_five_contract_keys() -> None:
    """Stdout contract: 5 key=value lines parsed by bash bootstrap_shared_sidecar.

    Removing or renaming any of these breaks the bash<->python handoff
    (script/run.sh:413-417 case-switch reads exactly these keys).
    """
    src = _read(BOOTSTRAP)
    for key in ("name=", "network=", "usage_log=", "yaml_path=", "master_key="):
        assert key in src, (
            f"bootstrap_sidecar.py must emit {key!r} (consumed by "
            "script/run.sh::bootstrap_shared_sidecar)"
        )


def test_bootstrap_sidecar_naming_prefixes_safe_from_cleanup_orphans() -> None:
    """Naming-prefix safety per script/AGENTS.md.

    cleanup_orphans filters on `name=ll-`, `name=mocks-`, `name=t_`,
    `name=k3net-` (substring match). Shared resources MUST use prefixes
    that do not contain any of those substrings, else a peer
    `bash script/run.sh` invocation would sweep them.
    """
    src = _read(BOOTSTRAP)
    # The two literal prefixes the bootstrap uses for network + sidecar.
    assert "wcbsh-net-" in src, "shared network name must start with wcbsh-net-"
    assert "wcbsh-sidecar-" in src, "shared sidecar name must start with wcbsh-sidecar-"
    # Guardrails: neither prefix may contain the orphan-sweep substrings.
    for prefix in ("wcbsh-net-", "wcbsh-sidecar-"):
        for swept in ("ll-", "mocks-", "t_", "k3net-"):
            assert swept not in prefix, (
                f"shared resource prefix {prefix!r} contains orphan-sweep "
                f"substring {swept!r}; cleanup_orphans would destroy it"
            )


def test_bootstrap_sidecar_has_no_atexit_or_signal_handlers() -> None:
    """Bash owns the lifecycle. Python must not register cleanup handlers
    that would race with bash's trap chain (EXIT/INT/TERM)."""
    src = _read(BOOTSTRAP)
    # Allow `import` for safety only; flag actual registrations.
    forbidden_patterns = [
        r"\batexit\.register\b",
        r"\bsignal\.signal\b",
    ]
    for pat in forbidden_patterns:
        assert not re.search(pat, src), (
            f"bootstrap_sidecar.py must not call {pat!r}; bash owns "
            "the lifecycle via the trap chain in script/run.sh"
        )


# ---------- eval/run_batch.py: shared-mode short-circuit ----------


def test_setup_function_reads_both_shared_env_vars() -> None:
    """_setup_litellm_and_mocks must read both WCB_SHARED_NETWORK and
    WCB_SHARED_SIDECAR to detect shared mode."""
    src = _read(RUN_BATCH)
    assert "WCB_SHARED_NETWORK" in src, (
        "run_batch.py must read WCB_SHARED_NETWORK to detect shared-mode"
    )
    assert "WCB_SHARED_SIDECAR" in src, (
        "run_batch.py must read WCB_SHARED_SIDECAR to detect shared-mode"
    )


def test_setup_function_skips_start_litellm_in_shared_mode() -> None:
    """In shared mode the python side must NOT call start_litellm /
    wait_for_litellm_healthy / verify_litellm_upstream_reachable — those
    are bash's responsibility. We enforce this structurally: each call
    site must be inside an `if`-block that references shared_mode."""
    tree = _ast(RUN_BATCH)
    targets = {
        "start_litellm",
        "wait_for_litellm_healthy",
        "verify_litellm_upstream_reachable",
        "pull_litellm_image",
        "create_network",
    }
    # Build parent map so we can walk upward.
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        # match either bare Name or attribute call ending in target name
        name: str | None = None
        if isinstance(fn, ast.Name):
            name = fn.id
        elif isinstance(fn, ast.Attribute):
            name = fn.attr
        if name not in targets:
            continue
        # Walk up looking for an `if`-block whose test references "shared_mode"
        cur: ast.AST | None = parents.get(id(node))
        gated = False
        while cur is not None:
            if isinstance(cur, ast.If):
                test_src = ast.unparse(cur.test)
                if "shared_mode" in test_src or "WCB_SHARED" in test_src:
                    gated = True
                    break
            cur = parents.get(id(cur))
        # We only care about calls INSIDE _setup_litellm_and_mocks, but the
        # invariant is strong: every call to these litellm-startup helpers
        # in run_batch.py must be gated by shared_mode (or live in a function
        # that doesn't exist outside that scope).
        # Find the enclosing function name to scope the check.
        cur = parents.get(id(node))
        enclosing_fn: ast.FunctionDef | None = None
        while cur is not None:
            if isinstance(cur, ast.FunctionDef):
                enclosing_fn = cur
                break
            cur = parents.get(id(cur))
        if enclosing_fn is None or enclosing_fn.name != "_setup_litellm_and_mocks":
            continue
        assert gated, (
            f"call to {name}() at line {node.lineno} inside "
            "_setup_litellm_and_mocks is not guarded by `if shared_mode` / "
            "`if not shared_mode` — shared-mode bypass invariant broken"
        )


# ---------- script/run.sh: bootstrap, teardown, trap chain ----------


def test_run_sh_defines_bootstrap_and_teardown() -> None:
    """run.sh must define both functions."""
    src = _read(RUN_SH)
    assert re.search(r"^\s*bootstrap_shared_sidecar\s*\(\)\s*\{", src, re.M), (
        "script/run.sh must define bootstrap_shared_sidecar()"
    )
    assert re.search(r"^\s*teardown_shared_sidecar\s*\(\)\s*\{", src, re.M), (
        "script/run.sh must define teardown_shared_sidecar()"
    )


def test_run_sh_invokes_bootstrap_before_task_loop() -> None:
    """The bootstrap must be CALLED somewhere in run.sh (not just defined)."""
    src = _read(RUN_SH)
    # Match a call site (not the function definition).
    call_matches = re.findall(r"bootstrap_shared_sidecar(?!\s*\(\))", src)
    # The grep is loose; require at least one occurrence outside the
    # `bootstrap_shared_sidecar() {` line itself.
    invocations = [
        ln for ln in src.splitlines()
        if "bootstrap_shared_sidecar" in ln
        and not re.match(r"^\s*bootstrap_shared_sidecar\s*\(\)\s*\{", ln)
        and not ln.lstrip().startswith("#")
    ]
    assert invocations, (
        "script/run.sh must INVOKE bootstrap_shared_sidecar (not only define it)"
    )


def test_run_sh_traps_chain_teardown_on_all_three_signals() -> None:
    """After bootstrap_shared_sidecar exports the env vars, the trap chain
    must cover EXIT + INT + TERM and chain teardown_shared_sidecar."""
    src = _read(RUN_SH)
    # Look for at least one trap line referencing teardown_shared_sidecar
    # for each of EXIT, INT, TERM.
    for sig in ("EXIT", "INT", "TERM"):
        pattern = rf"trap\s+['\"][^'\"]*teardown_shared_sidecar[^'\"]*['\"][^\n]*\b{sig}\b"
        matches = re.findall(pattern, src)
        assert matches, (
            f"script/run.sh must install a {sig} trap that chains "
            "teardown_shared_sidecar"
        )


def test_run_sh_teardown_is_idempotent() -> None:
    """teardown_shared_sidecar must early-return when env vars are blank
    (signal cascade safety) — checked by presence of the guard line."""
    src = _read(RUN_SH)
    # The idiomatic guard line we wrote.
    assert re.search(
        r"\[\[\s*-z\s*\"\$\{WCB_SHARED_SIDECAR:-\}\$\{WCB_SHARED_NETWORK:-\}\"\s*\]\]"
        r"\s*&&\s*return\s+0",
        src,
    ), (
        "teardown_shared_sidecar must early-return when both WCB_SHARED_SIDECAR "
        "and WCB_SHARED_NETWORK are blank (idempotency under signal cascade)"
    )


def test_run_sh_respects_skip_shared_sidecar_escape_hatch() -> None:
    """SKIP_SHARED_SIDECAR=1 must disable the bootstrap so a manual
    `python3 eval/run_batch.py` flow can use its own sidecar."""
    src = _read(RUN_SH)
    assert "SKIP_SHARED_SIDECAR" in src, (
        "script/run.sh must honor SKIP_SHARED_SIDECAR=1 as an escape hatch"
    )


def test_run_sh_worker_inherits_shared_sidecar_via_elif() -> None:
    """Under -P >1 worker propagation, a child run.sh with --skip-preflight
    must INHERIT WCB_SHARED_SIDECAR from the parent (the elif branch),
    not bootstrap its own."""
    src = _read(RUN_SH)
    # We require the inheritance log line we wrote.
    assert "Inheriting shared sidecar from parent" in src, (
        "script/run.sh must have an elif branch that inherits the shared "
        "sidecar from the parent invocation under -P >1 worker propagation"
    )


# ---------- regression guard: run_single_task isolation still holds ----------


def test_b7_isolation_still_intact() -> None:
    """Sanity check: the shared-infra work must not regress the b7 wrap.

    This duplicates one assertion from test_run_single_task_isolation.py
    so a refactor that drops both files is impossible to miss.
    """
    tree = _ast(RUN_BATCH)
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent

    calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == "run_single_task"
    ]
    if not calls:  # pragma: no cover — defensive
        pytest.skip("run_single_task not present (refactored?)")
    for c in calls:
        cur = parents.get(id(c))
        while cur is not None:
            if isinstance(cur, ast.Try):
                break
            cur = parents.get(id(cur))
        assert isinstance(cur, ast.Try), (
            f"run_single_task() at line {c.lineno} is not wrapped in try/except "
            "— see tests/test_run_single_task_isolation.py for the full pin"
        )


# ---------- K-loop frag-write must use `if`-form, not `[[ -n ... ]] && printf` ----------


def test_run_one_rep_uses_if_form_for_frag_failure_printf() -> None:
    """The frag-write brace group inside run_one_rep MUST use `if [[ -n ... ]]`
    instead of `[[ -n ... ]] && printf ...`.

    Why: the && short-circuits on the success path (when $rep_failure is empty),
    making the brace group's exit code 1 (the failed `[[ ]]` test). Since
    run_one() leaks `set -e` into the caller and run_one_rep is invoked from a
    backgrounded subshell (run_k_for_model_bg is `&`-launched from main), bash
    errexit terminates the for-loop after rep 1 — so reps 2..K silently never
    fire. The `if`-form keeps the brace group's last command a successful
    printf (or no-op), so the function returns 0 on success.

    Repro confirmed via /tmp/wcb_fix_verify.sh and the real test on
    2026-06-26: with the buggy `&&` form, `bash script/run.sh --reps 3`
    executed exactly 1 rep per task. With the `if`-form, all 3 reps fire.
    """
    text = _read(RUN_SH)
    # Locate run_one_rep() body
    fn_re = re.compile(r"^run_one_rep\s*\(\)\s*\{", re.MULTILINE)
    m = fn_re.search(text)
    assert m, "run_one_rep() function not found in script/run.sh"
    # Crude but sufficient: walk brace depth from the opening { until matching close
    i = m.end() - 1
    depth = 0
    end = None
    while i < len(text):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
        i += 1
    assert end is not None, "could not find end of run_one_rep() body"
    body = text[m.start():end + 1]

    # The bug-form: [[ -n "$rep_failure" ]] && printf 'failure=...
    bad = re.compile(
        r"\[\[\s*-n\s*\"?\$rep_failure\"?\s*\]\]\s*&&\s*printf\s+['\"]failure="
    )
    assert not bad.search(body), (
        "run_one_rep() uses `[[ -n \"$rep_failure\" ]] && printf 'failure=...'`. "
        "This short-circuits with exit 1 on the success path and kills the "
        "K-loop under set -e inside a backgrounded subshell — reps 2..K never "
        "fire. Use `if [[ -n \"$rep_failure\" ]]; then printf ...; fi` instead. "
        "See script/AGENTS.md (Shared-infra section) and the comment block at "
        "script/run.sh:619-627."
    )

    # The good-form: if [[ -n "$rep_failure" ]]; then printf 'failure=...
    good = re.compile(
        r"if\s+\[\[\s*-n\s*\"?\$rep_failure\"?\s*\]\];\s*then\s+printf\s+['\"]failure="
    )
    assert good.search(body), (
        "run_one_rep() must guard the `failure=...` printf with an `if`-form "
        "test (not `&&`). Current body lacks the expected `if [[ -n "
        "\"$rep_failure\" ]]; then printf 'failure=...'; fi` shape."
    )


# ---------- WCB_SHARED_* globals must preserve inherited values under -P >1 ----------


def test_wcb_shared_globals_use_parameter_default_init():
    """Under -P >1 the parent `bash script/run.sh` exports WCB_SHARED_* and
    fans out workers via `bash $SELF --task ... --skip-preflight`. Each worker
    re-loads run.sh top-to-bottom, hitting the WCB_SHARED_* module-level inits.
    Using bare `WCB_SHARED_NETWORK=""` there CLOBBERS the inherited env var to
    empty BEFORE the bootstrap-gate at line ~1011 can read it, defeating the
    entire shared-sidecar fix (each rep then takes the fallback per-process
    sidecar path, spawning its own `ll-*` container + `k3net-*` network).
    The fix is to use parameter-default expansion `: "${VAR:=}"` so the
    assignment is a no-op when the var is already non-empty. This regression
    test pins the if-form against an "obvious cleanup" back to bare assignment.
    Discovered + fixed 2026-06-27 during `--reps 3 -P 3` testing where each of
    the 9 reps spawned its own per-rep ll-* sidecar instead of reusing the
    shared wcbsh-sidecar-* the parent had bootstrapped.
    """
    text = _read(RUN_SH)
    for var in (
        "WCB_SHARED_NETWORK",
        "WCB_SHARED_SIDECAR",
        "WCB_SHARED_SIDECAR_USAGE_LOG",
        "WCB_SHARED_SIDECAR_YAML",
        "WCB_SHARED_LITELLM_MASTER_KEY",
    ):
        bare = re.compile(rf"^{re.escape(var)}=\"\"\s*$", re.MULTILINE)
        assert not bare.search(text), (
            f"{var} is initialized with bare `{var}=\"\"`. This clobbers the "
            f"inherited export when a -P >1 worker re-loads run.sh, breaking "
            f"the shared-sidecar fix. Use `: \"${{{var}:=}}\"` (parameter-"
            f"default expansion) instead. See script/AGENTS.md Shared-infra."
        )
        default = re.compile(rf':\s*"\$\{{{re.escape(var)}:=\}}"')
        assert default.search(text), (
            f"{var} must be initialized via `: \"${{{var}:=}}\"` so an "
            f"inherited export from the parent -P launcher is preserved. "
            f"See script/AGENTS.md Shared-infra section and the comment block "
            f"at the module-level WCB_SHARED_* init."
        )


# ---------- teardown_shared_sidecar MUST guard against worker-PID early-exit ----------


def test_teardown_shared_sidecar_has_owner_pid_guard():
    """Under -P >1, run_parallel_tasks fans out workers via `bash $SELF --task ...`
    The tmpdir-trap installed at run.sh:~1029 fires `teardown_shared_sidecar`
    on EVERY process exit (parent AND workers). Without an owner-PID guard,
    the first finishing worker `docker rm -f`s the shared sidecar while slower
    siblings are still mid-flight (load-dependent race).

    Fix: `bootstrap_shared_sidecar` exports `WCB_SHARED_OWNER_PID=$$`, and
    `teardown_shared_sidecar` early-returns when `$$ != $WCB_SHARED_OWNER_PID`.
    Workers thus never tear down infra they don't own — only the parent does.

    Discovered + fixed 2026-06-27 during real `--reps 3 -P 3` testing where the
    parent log showed 4 "Tearing down" lines: 3 from finishing workers and 1
    from the parent (the parent's was a no-op because workers had already
    docker-rm'd the sidecar). The reps "passed" only because Docker's lazy
    container kill let in-flight TCP complete on a fast laptop.
    """
    text = _read(RUN_SH)

    # bootstrap must set + export WCB_SHARED_OWNER_PID=$$
    assert re.search(r"WCB_SHARED_OWNER_PID\s*=\s*\$\$", text), (
        "bootstrap_shared_sidecar must set `WCB_SHARED_OWNER_PID=$$` before "
        "exporting WCB_SHARED_*. Without this, teardown cannot distinguish "
        "the parent from workers under -P >1."
    )
    assert re.search(r"export\s+[A-Za-z_ \\\n]*WCB_SHARED_OWNER_PID", text), (
        "WCB_SHARED_OWNER_PID must be exported so workers inherit it. "
        "Without the export, workers see `$WCB_SHARED_OWNER_PID` empty and "
        "the guard accidentally allows worker teardown."
    )

    # teardown must early-return when $$ != $WCB_SHARED_OWNER_PID
    guard = re.compile(
        r'\[\[\s*-n\s*"\$\{WCB_SHARED_OWNER_PID:-\}"\s*&&\s*'
        r'"\$\$"\s*!=\s*"\$WCB_SHARED_OWNER_PID"\s*\]\]'
    )
    assert guard.search(text), (
        "teardown_shared_sidecar must contain an owner-PID guard at the top "
        'of the function: `if [[ -n "${WCB_SHARED_OWNER_PID:-}" && "$$" != '
        '"$WCB_SHARED_OWNER_PID" ]]; then return 0; fi`. Without it, a worker '
        "process exiting via the tmpdir-trap will tear down the parent's "
        "shared sidecar, causing load-dependent race failures for slower "
        "sibling workers."
    )

    # module-level init must include WCB_SHARED_OWNER_PID via parameter-default
    init = re.compile(r':\s*"\$\{WCB_SHARED_OWNER_PID:=\}"')
    assert init.search(text), (
        "WCB_SHARED_OWNER_PID must be initialized at module-level via "
        '`: "${WCB_SHARED_OWNER_PID:=}"` so workers preserve the inherited '
        "value from the parent's export. Same parameter-default-expansion "
        "rule as the other WCB_SHARED_* globals."
    )
