# AGENTS.md — eval

Two files. One is THE orchestrator. The other is the stdlib-only bash↔python bootstrap.

## Files
| File | Size | Role |
|---|---|---|
| `run_batch.py` | ~2078 lines (~105 KB) | The single Python orchestrator. Invoked by `script/run.sh` (preferred) or directly. |
| `bootstrap_sidecar.py` | ~265 lines (~10.6 KB) | Stdlib-only entry that boots the shared LiteLLM sidecar + Docker network ONCE per `run.sh` batch and emits `key=value` lines on stdout for bash to consume. |

No `__init__.py`. `run_batch.py:21` does `sys.path.insert(0, '..')` to import `src.utils.*`. There is no installed package; everything runs path-based.

## `run_batch.py` — what it does
- `argparse`-driven. Selects backend (`--agent-backend openclaw|claudecode|codex|hermesagent`), model, K reps, scoring channels (`--generate-tests`, `--execute-tests`, `--judge-council`), litellm/mock toggles.
- Per task: `task_parser.load_task` → `_augment_task_with_mocks` → `_build_trajectory` (host-side env-overlay snapshot via `src/utils/env_overlay_snapshot.py`) → dispatch to backend's `run()` → Channel A pytest synthesis + execution → Channel B judge council → write `output/<backend>/<task>/trajectories/<model>/run_N/`.
- Three call sites for `run_single_task(...)` (`--task` mode ~L2138, sequential category-mode loop ~L2213, `ThreadPoolExecutor` via `future.result()` ~L2255). **All three MUST be wrapped in `try/except` building the soft-error dict `{"task_id": ..., "scores": {}, "error": str(exc)}`** (cascade-prevention invariant, pinned by `tests/test_run_single_task_isolation.py`).
- Trajectory passed to judge is **NEVER truncated** (`run_batch.py:615` / `:681`). The `limit` kwarg is retained for API compatibility only.

## `bootstrap_sidecar.py` — bash↔python contract
- Imports `src.utils.litellm_sidecar` and runs the LiteLLM portion of `_setup_litellm_and_mocks` ONCE: `pull_litellm_image` → optional `ensure_litellm_headroom_image` (if `KENSEI_AGENT_HEADROOM_ENABLED`) → `create_network` → write yaml at `work/litellm-config-shared-<suffix>.yaml` → create usage dir (`chmod 0o700`/`0o600`) → `start_litellm` → `wait_for_litellm_healthy` → optional `verify_litellm_upstream_reachable`.
- **Stdout emits exactly 5 `key=value` lines** consumed by `script/run.sh::bootstrap_shared_sidecar()`:
  ```
  name=wcbsh-sidecar-<suffix>
  network=wcbsh-net-<suffix>
  usage_log=<path>
  yaml_path=<path>
  master_key=<key>
  ```
  Logs go to stderr. Bash forwards stderr → `log::info`.
- **Exit codes (load-bearing):** `0` = success; `2` = litellm disabled (still emits empty values so bash knows); `3` = `start_litellm` failed; `4` = `wait_for_litellm_healthy` failed; `5` = `verify_litellm_upstream_reachable` failed.
- **NO `atexit` / `signal` handler.** Bash owns the lifecycle (see `script/AGENTS.md` "Shared-infra Fix A+B"). Adding one would race the bash teardown trap.
- **Naming prefixes** MUST start with `wcbsh-net-` / `wcbsh-sidecar-` — these are deliberately chosen NOT to match `cleanup_orphans` filters (`ll-`, `mocks-`, `t_`, `k3net-`) in `run.sh`. Pinned by `tests/test_shared_sidecar_invariants.py`.
- Cleanup prefixes that `bootstrap_sidecar.py:121` uses MUST NOT collide with `run.sh::cleanup_orphans` filters.

## Shared-mode short-circuit in `_setup_litellm_and_mocks`
When BOTH `WCB_SHARED_NETWORK` AND `WCB_SHARED_SIDECAR` are set in the environment, `run_batch.py::_setup_litellm_and_mocks`:
- reuses `network = $WCB_SHARED_NETWORK` and `sidecar = $WCB_SHARED_SIDECAR`
- **skips** `pull_litellm_image`, `ensure_litellm_headroom_image`, `create_network`, yaml write, `start_litellm`, `wait_for_litellm_healthy`, `verify_litellm_upstream_reachable`
- reuses `WCB_SHARED_SIDECAR_YAML` and `WCB_SHARED_SIDECAR_USAGE_LOG` when set
- **does NOT register** `remove_network` / `stop_litellm` in `cleanups[]` (bash owns teardown)
- still creates the **per-task** mock stack inline (Fix C deferred).

This short-circuit is pinned by `tests/test_shared_sidecar_invariants.py`. Breaking it causes the python rep to tear down infra that bash thinks it still owns.

## Invariants (don't break)
1. **Soft-error wrap on every `run_single_task` call site.** Three sites today; all four AST predicates in `tests/test_run_single_task_isolation.py` must pass. Do NOT replace the wrap with `sys.exit(1)` — the post-call `if result.get('error'): sys.exit(1)` block already exits, bypassing the wrap removes the structured log line and breaks `script/run.sh::run_one_rep`'s `RUN_RC=${PIPESTATUS[0]}` capture.
2. **Trajectory never truncated when fed to judge** (`run_batch.py:615` / `:681`).
3. **`bootstrap_sidecar.py` exit code shape** is part of the bash contract — preserve 0/2/3/4/5 semantics.
4. **Stdout = `key=value` lines only.** Anything else on stdout breaks bash parsing. Send progress/info to stderr.
5. **No `atexit`/`signal` in `bootstrap_sidecar.py`** — bash trap is the authoritative cleanup.
6. **`--parallel 1` default for Bedrock throttling** (RUNBOOK §9). `--reps` > 1 is fine with shared sidecar.

## Convergence guarantee
`script/run.sh` and direct `python3 eval/run_batch.py` must produce identical artifacts for equivalent args. If they don't, `run.sh` is wrong (per `script/AGENTS.md` Conventions). The shared-sidecar short-circuit is the one place this is subtle: outside `run.sh` the per-rep fallback runs; under `run.sh` the shared path runs. Both must yield the same `output/...` tree.
