# `--reps N>1` Failure Surface — Complete Static Diagnosis

> **Mode**: Analyze-only. NO code changes. This document enumerates every code path that can cause a `--reps N` run to fail rep 2 (or any rep ≥ 2), with file:line evidence, falsification verdicts, and a single diagnostic command for ground-truthing on the live system.

## Honest framing (read first)

1. The diagnosis is **100% static**. Local `logs/` only contains `_run1_` files. THE actual cause of the user's rep-2 failure cannot be pinned without the user's `logs/<task>_*_run2_*.log`. The diagnostic command in §F maps log evidence to specific failure points enumerated below.
2. Each rep is a **fresh `python3 eval/run_batch.py` process** (`script/run.sh:414`). Cross-rep coupling exists ONLY via (a) Docker daemon state, (b) host filesystem, (c) external service quotas. Anything bound to one of those three is a candidate.
3. The earlier framing of "primary cause = Bedrock TPM" was unsupported. It is one structurally-confirmed candidate among many.
4. The b7 isolation invariant (`tests/test_run_single_task_isolation.py`) wraps `run_single_task` at three call sites (line 2138 `--task`, 2213 sequential, 2255 threadpool). **It does NOT wrap `_setup_litellm_and_mocks` (line 2010).** Setup-phase failures exit with traceback.

## A. Cross-rep coupling vectors (the SHORT LIST)

### A1. AWS Bedrock per-account TPM/RPM quotas
- **File:line**: `src/utils/judge_litellm.py:368`, `eval/run_batch.py:1688-1698`, `src/utils/litellm_sidecar.py:612-669`
- **Mechanism**: Agent LiteLLM sidecar AND `judge_council` (Sonnet/Kimi/GLM) share one Bedrock account. Rep 1's grading exhausts per-region per-account TPM; rep 2's `verify_litellm_upstream_reachable` synthetic probe gets `ThrottlingException`.
- **Failure shape**: `RuntimeError("LiteLLM sidecar {sidecar} is up but upstream provider is unreachable via model='claude-opus-4.7': ...")` from `run_batch.py:1692-1698` → traceback exit (NOT caught by b7 wrap; `_setup_litellm_and_mocks` is outside the wrap) → `script/run.sh:425` `is_docker_recoverable_error` regex does NOT match → no retry → rep 2 marked failed.
- **Verdict**: STRUCTURALLY CONFIRMED. Actual incidence requires user's rep-2 log.

### A2. AWS Bedrock bearer token TTL expiry
- **File:line**: `src/utils/config.py:142`, `src/utils/judge_litellm.py:352-354`, `src/utils/grading.py:668`
- **Mechanism**: `KENSEI_AWS_BEARER_TOKEN` read once per `Config.from_env()` (per process). STS-backed tokens (12h typical) expire mid-batch. No refresh, no TTL check. Stale token → 403 → same path as A1.

### A3. Docker bridge IP pool exhaustion
- **File:line**: `src/utils/litellm_sidecar.py:438-458` (`create_network`)
- **Mechanism**: Each rep creates one `k3net-<batch_id>`. Default bridge pool `172.17/16 → 172.31/16` carves into `/24` → ~256 networks. SIGKILL'd reps leak networks (no `atexit`). After enough reps, `docker network create` returns `could not find an available, non-overlapping IPv4 address pool`.
- **Where it bites**: `_setup_litellm_and_mocks` → `create_network(network)` at `run_batch.py:1612` → `RuntimeError("Failed to create network {name}: {r.stderr}")` from `litellm_sidecar.py:457`. Unwrapped path.
- **Verdict**: STANDS.

### A4. Disk / inode fill from unbounded `work/` and `/tmp/` accumulation
- **File:line**:
  - `eval/run_batch.py:1615` `work/litellm-config-<batch_id>.yaml`
  - `eval/run_batch.py:1619-1622` `work/litellm-usage-<batch_id>/`
  - `eval/run_batch.py:1647-1648` `work/litellm-headroom-<batch_id>/`
  - `eval/run_batch.py:351` `work/<task_id>/exec/`
  - `src/agents/openclaw/runner.py:113` `/tmp/chat-snap-<task_id>.jsonl`
- **Mechanism**: NONE are registered for cleanup. `cleanups[]` only holds `remove_network`, `stop_litellm`, `stop_mock_stack` (`run_batch.py:1613, 1675, 1716`). Each rep adds 3-5 new files/dirs. Unbounded.
- **Where it bites**: Rep N hits `OSError: [Errno 28] No space left` during chmod (`run_batch.py:1632`), config write (`1616`), or workspace stage. Traceback exit.

### A5. Judge_council shares Bedrock account with agent
- **File:line**: `src/utils/judge_litellm.py:60-99, 287-422`
- **Mechanism**: 4× TPM consumption per task (agent + 3 judges). Reduces headroom for rep N+1. Intensifies A1.

### A6. Orphan `t_*`/`mocks-task-*`/`k3net-*`/agent containers from SIGKILL'd reps
- **File:line**:
  - Backend `except Exception`: `openclaw/runner.py:285-292`, `codex/runner.py:234-263`, `claudecode/runner.py:174-181`, `hermesagent/runner.py:136-146` — NO `remove_container`.
  - Cleanup ONLY in `run_single_task`'s `finally` at `run_batch.py:1532` — SIGKILL bypasses.
- **Verified**: ZERO `atexit.register`, ZERO cleanup-purpose `signal.signal` in repo (sole `signal.signal` is `SIGALRM` at `test_executor.py:45` for per-test in-container timeout — unrelated).
- **Mechanism**: Rep 1 killed by OOM → containers survive → rep 2 hits docker resource pressure (see A3). Under `--parallel-reps` (NOT default), C1 below causes cascade.

## B. Unwrapped setup-phase raise points (the "rep 2 crashed loudly" vector)

The b7 isolation wrap covers ONLY `run_single_task` (test-pinned at `tests/test_run_single_task_isolation.py`). All pre-`_run_dispatch` setup in `main()` (`run_batch.py:1970-2053`) is unwrapped. The localized `try/except: raise` at `run_batch.py:2013-2018` only protects the `_setup_litellm_and_mocks` call itself (running cleanups before re-raising); everything OUTSIDE that try has no cleanup safety net. **THIRTEEN sites raise from this region:**

| # | Line | Source | Match `run.sh:425` regex? | Retry-eligible? |
|---|---|---|---|---|
| B0 | 1976 | `Config.from_env()` raises on missing/malformed env (e.g. `KENSEI_AWS_BEARER_TOKEN` parse failure, `KENSEI_LITELLM_PORT` not an int) | NO | NO |
| B1 | 1604-1607 | `LiteLLM requested but no Bedrock/OpenAI creds resolved` | NO | NO |
| B2 | 1609 | `pull_litellm_image` registry/daemon fail (`litellm_sidecar.py:377-379`) | NO (msg = "Failed to pull LiteLLM image") | NO |
| B3 | 1611 | `ensure_litellm_headroom_image` build fail (gated `KENSEI_AGENT_HEADROOM_ENABLED`) | NO | NO |
| B4 | 1612 | `create_network` fail (A3 surfaces here) | NO (msg = "Failed to create network") | NO |
| B5 | 1659 | `start_litellm` docker run fail (`litellm_sidecar.py:569-572`) | NO | NO |
| B6 | 1677 | `wait_for_litellm_healthy` timeout (`KENSEI_LITELLM_HEALTH_TIMEOUT` default 120s) | NO | NO |
| B7 | 1692 | `verify_litellm_upstream_reachable` fail (A1/A2/A5 surface here) | NO | NO |
| B8 | 1710 | `build_mock_image_if_needed` fail (msg = "Mock image build failed") | NO | NO |
| B9 | 1718 | `wait_for_mock_stack_healthy` timeout (180s budget; msg = "Mock stack ... did not become healthy") | NO | NO |
| B10 | 1982 | `require_image_present(DOCKER_IMAGE)` raises `RuntimeError("Required Docker image not present locally: {image}\n...")` if `wildclawbench-ubuntu:v1.3` was force-removed by `cleanup_orphans` (`run.sh:357`) or by `docker system prune` between reps. Exception message **verified** at `src/utils/docker_utils.py:135-140`. | **YES** — regex `Required Docker image not present` matches | **YES** — retry path fires `cleanup_orphans` → recursive cascade under C1 (`--parallel-reps` only) |
| B11 | 1990-2002 | Backend constructors for `claudecode | codex | hermesagent`. Raises on lazy import failure (line 1998 `from src.agents.hermesagent import HermesAgentAgent`), missing required kwargs (e.g. `OPENROUTER_API_KEY=""`), or constructor-side validation | NO | NO |
| B12 | 2019-2037 | `OpenClawAgent(...)` constructor (litellm or openrouter variant). **LEAK PATH**: this runs AFTER `_setup_litellm_and_mocks` registered cleanups for sidecar+mock_stack+network (lines 1613, 1675, 1716), but BEFORE the `try/finally` at lines 2049-2053 that actually executes them. If `OpenClawAgent.__init__` raises here, the registered `cleanups[]` are **NEVER RUN**. Sidecar `ll-<batch_id>`, mock container `mocks-<batch_id>`, and network `k3net-<batch_id>` all leak. Directly intensifies A3/A4/A6 for rep N+1. | NO | NO |

**Reframed (per Oracle Gap 1)**: This is NOT a cascade failure across reps. Each rep is a separate process; rep 2's setup failure doesn't poison rep 3. The actual problem is **rep 2's first transient flake is unrecoverable** and exits with a confusing traceback the user perceives as "everything stopped." Fix would be converting B0-B12 to soft-error dicts matching the b7 pattern AND wrapping lines 1982-2037 in a try/finally that runs `_run_cleanups(cleanups)` so backend constructor failures don't orphan the sidecar/mock/network.

**B12 cross-reference**: D1 below documents the same "register-after-success" fragility for lines 1659-1675 INSIDE `_setup_litellm_and_mocks`. B12 is the externalized form: cleanups registered inside `_setup_litellm_and_mocks` are protected against setup-internal raises (line 2013-2018), but unprotected against raises in the backend constructor region (line 1982-2037).

## C. Additional failure points

### C1. `other_runs_active()` PID-key broken under `--parallel-reps`
- **File:line**: `script/run.sh:322-337` (`other_runs_active`), `:339-374` (`cleanup_orphans`), `:352` filter `--filter name=ll- --filter name=mocks- --filter name=t_`
- **Mechanism**: Line 329 skips own `$$`. Under `--parallel-reps`, all reps are background bash jobs of the SAME run.sh PID → guard returns FALSE → `cleanup_orphans` force-removes `ll-*`/`mocks-*`/`k3net-*` from sibling reps.
- **Scope**: Affects ONLY `--parallel-reps` (PARALLEL_REPS=1). Default sequential (PARALLEL_REPS=0) is safe.

### C2. Testgen cache write gap (cache NEVER warms)
- **File:line**: `eval/run_batch.py:1295-1297`
- **Direct read confirmed**: Only `cached_key_path.write_text(current_key, encoding='utf-8')` is written. `cached_code_path.write_text(tg.test_code)` and `cached_weights_path.write_text(tg.test_weights_json)` are ABSENT.
- **Mechanism**: Cache lookup at line 1255 requires BOTH `test_outputs.py` AND `test_weights.json` to exist. They never get written. **Cache is permanently cold.**
- **Net effect**: Every rep regenerates tests via LLM (K reps → K×testgen cost). Each fail at line 1305 silently zeroes `task["test_code"]` → score 0.
- **Local log evidence**: `logs/alden-croft_claude-opus-4.7_run1_20260603_175933.log` contains `[ERROR] [TESTGEN] All attempts produced no usable code (task=alden-croft); using fallback` — confirms surface bites in practice.

### C3. Recovery retry doubles `run_N/` and inflates `pass@K` denominator
- **File:line**: `script/run.sh:518` (retry re-calls `run_one`) + `eval/run_batch.py:1372` (`_claim_run_dir`)
- **Mechanism**: Failed rep writes `pass_summary.json` with score=0; retry claims fresh `run_N+1`, succeeds, writes ANOTHER entry. Both coexist (dedup key is `run_index`, not retry-aware).

### C5. SIGTERM mid-`pass_summary.json` write corrupts file
- **File:line**: `eval/run_batch.py:666-671` — `_write_pass_summary` catches `json.JSONDecodeError` and resets `existing = {}`.
- **Mechanism**: SIGTERM mid-write produces partial JSON inside `_locked` (non-atomic `write_text`). Next rep reads partial → silent reset of `per_run = []` → ALL prior pass@K data lost.

### C6. Orphan agent containers escape `cleanup_orphans` filter
- **File:line**: `script/run.sh:352` filter `name=t_` vs `run_batch.py:1359` task_id format `{short_task_id}_{lobster_prefix}{short_model}_{timestamp}_{run_id}` (e.g. `01_task_2_claude_opus_4_7_20260612_1530_a3f9c2`).
- **Mechanism**: Sanitized agent names don't start with `t_`. Only the fallback at line 1366 (when sanitization fully fails) uses `t_`. Real agent orphans are never swept.

### C7. `test_executor.py` random-named containers escape `cleanup_orphans`
- **File:line**: `src/utils/test_executor.py:383-417` — `docker run --rm` with NO `--name`.
- **Mechanism**: `--rm` self-cleans only on clean container exit. SIGKILL of host Python mid-`subprocess.run` orphans the container. Doesn't match `t_|ll-|mocks-` filter.

### C8. `/tmp/chat-snap-<task_id>.jsonl` unbounded
- **File:line**: `src/agents/openclaw/runner.py:113`
- **Mechanism**: Per-rep `task_id` unique → fresh file per rep, never deleted. MB-sized.

### C9. `is_docker_recoverable_error` regex false-negative matrix
- **File:line**: `script/run.sh:425` regex `Required Docker image not present|Container startup failed|No such image|manifest unknown`
- **Tested matches**:
  - `RuntimeError: LiteLLM sidecar … did not become healthy` → **NO match** (B6 path, no retry)
  - `RuntimeError: … upstream provider is unreachable` → **NO match** (A1/B7 path, no retry)
  - `Connection refused` → **NO match**
  - `OSError: No space left on device` → **NO match** (A4 path, no retry)
  - `RuntimeError: Container startup failed` → **MATCHES** (good for image corruption, bad for OOM since `cleanup_orphans` worsens pressure)
  - `docker: No such image: kensei3-mocks:v1` → **MATCHES** → fires `cleanup_orphans` → recursive cascade under C1

### C10. Cold-path testgen race under `--parallel-reps`
- **File:line**: `eval/run_batch.py:1247-1303` — no flock around cache lookup/write. Parallel reps both miss → 2× LLM cost. (Moot in practice because cache never warms — see C2.)

### C12. Agent container missing `remove_container` in backend `except Exception`
- **File:line**: All 4 backends (`openclaw:285, codex:234, claudecode:174, hermesagent:136`). Cleanup ONLY in `run_single_task`'s `finally` — bypassed on SIGKILL.

### C13. `KENSEI_LITELLM_HEALTH_TIMEOUT` default 120s may be insufficient under daemon load
- **File:line**: `src/utils/litellm_sidecar.py:586`
- **Mechanism**: Under load from orphan containers, sidecar `/health` takes >120s to respond → B6 raise.

### C14. `remove_network` silently no-ops if attached
- **File:line**: `src/utils/litellm_sidecar.py:476-477` — `docker network rm` is fire-and-forget, `capture_output=True`, no rc check.
- **Mechanism**: If a sidecar still attached at network teardown, removal fails silently → network leaks → contributes to A3.

### C15. `KENSEI_MOCK_REBUILD=1` rebuilds image every rep
- **File:line**: `src/utils/mock_stack.py:270`
- **Mechanism**: Forces rebuild from scratch per rep. Slow + can fail under disk pressure.

### C16. `ensure_litellm_headroom_image` is content-hash-blind
- **File:line**: `src/utils/litellm_sidecar.py:405-407`
- **Mechanism**: Unlike `mock_stack.py:281` (content-hashes), this uses tag presence. Dockerfile edits don't invalidate → rep N+1 silently uses stale image. (Correctness drift, not failure path.)

## D. NEW findings from supplementary audit

### D1. `start_litellm`/`start_mock_stack` succeed but `cleanups.append` happens AFTER call returns
- **File:line**: `eval/run_batch.py:1659` (sidecar start) ... `:1675` (cleanups.append for sidecar). `:1715` (mock stack start) ... `:1716` (cleanups.append).
- **Mechanism**: Narrow leak window. If `wait_for_litellm_healthy` (line 1677) raises before `cleanups.append(stop_litellm)` at 1675, the started sidecar container is never cleaned. Architectural fragility; would benefit from try/except register-immediately pattern.

### D2. `mock_health_logger._container_running` has NO subprocess timeout
- **File:line**: `src/utils/mock_health_logger.py:58-62`
- **Mechanism**: If Docker daemon hangs, the health thread freezes silently. Daemon=True so doesn't block process exit, but logger emits no further records.

### D3. `mock_stack.build_mock_image_if_needed` mtime-based content hash
- **File:line**: `src/utils/mock_stack.py:282-284` via `_compute_mock_content_hash` (sha256 of relpath + size + MTIME)
- **Mechanism**: If `environment/` files have mtime touches between reps (e.g. by env-overlay snapshot writes — but those write to `output/`, not `environment/`), unnecessary rebuild triggers. Confirmed by reading: snapshot writes to `output/<backend>/<task>/data/environment/` (a different path), so this is theoretical only.

### D4. `aggregate_runs.py` is post-fan-out, not in rep loop
- **File:line**: `script/aggregate_runs.py:80-139`
- **Verified**: Filters via `if not score_path.is_file(): continue`; tolerates missing reps. Uses `statistics.fmean(pcts), pass_at_k = max(pcts)`. NOT a per-rep failure source. (Falsifies any concern that aggregation crashes rep N.)

## E. Falsified (cannot cause sequential rep failure)

| # | Hypothesis | Verdict reason |
|---|---|---|
| F1 | Docker name collision (network/container) | All uuid-stamped per process |
| F2 | `run_N/` directory collision | Atomic `mkdir(exist_ok=False)` loop at `run_batch.py:541-548` |
| F3 | `pass_summary.json` clobber on happy path | flock + read-merge-write keyed on `run_index` at `:661-675` |
| F4 | Env-overlay wipe race with live mock | Wipe target `output/<task>/data/environment/`; mock mounts from `input/<task>/mock_data/`. Different paths |
| F5 | bash `run_one_rep` hard-stopping the loop | No `set -e` propagation, no `return $RUN_RC`, no `exit`. Soft tally into frag file |
| F6 | bash bulk subshells (run.sh:805-811) | `if/else` consumes inner rc; subshell always exits 0 (AGENTS.md invariant) |
| F7 | `_stage_native_workspace` race | Empty dir, RO mount |
| F8 | `mock_health_logger` / `drift_director` thread leaks across reps | daemon=True, joined with timeout, daemon kills on process exit |
| F9 | `judge_litellm.py` cache leak | Module-level `_registered_tails` resets per fresh process |
| F10 | test_executor network reuse | Caller passes per-rep `k3net-{batch_id}` (verified `run_batch.py:1466`) |
| F11 | mock_health_logger shared-path appends | Caller passes per-rep `output_dir = model_dir/run_N` (verified `run_batch.py:1923`) |
| F12 | drift_director shared-path appends | Caller passes per-rep `timeline_path = output_dir / 'drift_timeline.jsonl'` (verified `run_batch.py:1953`) |
| F13 | `RUN_LOG` timestamp collision on retry | `ts=$(date +%Y%m%d_%H%M%S)` is fresh local var per `run_one()` call (verified `run.sh:388-391`) |

## F. ONE diagnostic command for the user

```bash
TASK=<your-task-id>; LOG_DIR=logs
RUN2_LOG=$(ls -t $LOG_DIR/${TASK}_*_run2_*.log 2>/dev/null | head -1)
echo "=== RUN 2 LOG: $RUN2_LOG ==="
grep -nE 'LiteLLM sidecar .* (did not become healthy|upstream provider is unreachable|Failed to pull)|Mock stack .* did not become healthy|per-task mock stack .* (failed to start|not healthy)|Failed to create network|No space left on device|ThrottlingException|TooManyRequestsException|ExpiredToken|UnrecognizedClient|Bedrock|Connection refused|Traceback \(most recent call last\)' "$RUN2_LOG" 2>/dev/null | head -30
echo "=== DOCKER STATE ==="
docker network ls --filter name=k3net- -q | wc -l
docker ps -a --filter name=ll- --format '{{.Names}} {{.Status}}'
docker ps -a --filter name=mocks- --format '{{.Names}} {{.Status}}'
echo "=== DISK STATE ==="
du -sh work/ /tmp/chat-snap-*.jsonl 2>/dev/null | head -10
df -h work/ /tmp 2>/dev/null
```

### Decision tree (log evidence → failure point)

| Output contains | Likely cause | Failure point |
|---|---|---|
| `upstream provider is unreachable` + `ThrottlingException` | Bedrock TPM/RPM saturation | A1 / A5 / B7 |
| `upstream provider is unreachable` + `ExpiredToken` | STS bearer token expired | A2 / B7 |
| `LiteLLM sidecar … did not become healthy` | sidecar startup slow / daemon load | B6 / C13 |
| `Failed to create network` + many `k3net-` networks remain | Docker bridge pool exhaustion | A3 / B4 |
| `No space left on device` + large `work/` | Disk fill from unregistered cleanups | A4 |
| `per-task mock stack … not healthy` / `overlay CSV likely malformed` | mock CSV malformed OR readiness race (already inside b7 wrap → clean rc=1) | (b6-era) |
| `Container startup failed: network k3net- not found` | Peer's network wiped by `cleanup_orphans` | C1 (`--parallel-reps` only) |
| `Required Docker image not present locally: wildclawbench-ubuntu:v1.3` | Agent image pruned/removed between reps; ONLY B-site with retry path | B10 |
| Traceback first frame is `Config.from_env` / config.py | Env file modified mid-batch OR malformed env var | B0 |
| Traceback first frame is `OpenClawAgent.__init__` or `ClaudeCodeAgent.__init__` etc. | Backend constructor raise — **also orphans sidecar+mock+network** (no cleanup) | B11 / B12 |
| Traceback contains `OpenClawAgent` AND prior log shows successful "LiteLLM sidecar healthy" + "mock stack healthy" | B12 leak path: setup succeeded, backend ctor failed, cleanups never ran. Check `docker network ls --filter name=k3net- -q | wc -l` — expect orphan from this rep | B12 |
| Pure traceback, no recognizable phrase | First line of traceback → match against B0-B12 | various |
| Disk fine, network count fine, no setup phrases | Per-task mock issue inside b7 wrap; check `output/<backend>/<task>/trajectories/<model>/run_2/score.json` for `error` field | C12 |
| `[TESTGEN] All attempts produced no usable code` | Testgen cache cold + LLM flake (cache write gap) | C2 |

## G. What this diagnosis CANNOT do

- It cannot identify THE actual cause of the user's specific rep-2 failure without the rep-2 log.
- It cannot rank A1-A6 by likelihood for this specific repro without telemetry.
- It cannot exclude environment-specific causes (host OS limits, daemon version, network policy).

The deliverable IS the enumeration of every code path that can fail. The user supplies the log; this document maps log → point.

## H. Summary table

| Category | Count | Most actionable items |
|---|---|---|
| Cross-rep coupling (A) | 6 | A1, A3, A4, A6 |
| Unwrapped setup raises (B) | 13 (B0-B12, +4 vs Round 2: B0/B10/B11/B12) | B6, B7, B9, B10 (only retry-eligible), B12 (leak path) |
| Additional failure points (C) | 14 (C1, C2, C3, C5, C6, C7, C8, C9, C10, C12, C13, C14, C15, C16; C4/C11 retracted as falsified) | C2 (cache write gap — verified bites), C9, C12 |
| New from supplementary audits (D) | 4 | D1 (cleanup register-after-success — same shape as B12), D2 |
| Falsified (E/F) | 13 | — |
| **Total enumerated failure surface** | **37 active + 13 falsified = 50 paths audited** | — |

## I. Verification trail

- **Direct file reads** by build agent on /Users/apple/Documents/WildClawBench: `eval/run_batch.py:1247-1305, 1295-1297, 1604-1721, 532-548, 1970-2059`; `script/run.sh:322-374, 388-391, 419-426, 498-543, 545-589`; `src/utils/litellm_sidecar.py:21, 23, 377-379, 405-457, 476-477, 569-572, 585-669`; `src/utils/mock_stack.py:228-481`; `src/utils/judge_litellm.py:60-99, 287-422, 352-368`; `src/utils/test_executor.py:45, 369, 383-417`; `src/utils/mock_health_logger.py:58-93`; `src/utils/drift_director.py:449-697`; `script/aggregate_runs.py:80-139`; `src/utils/docker_utils.py:124-141` (`require_image_present` exact exception message verified for B10 retry-eligibility); all 4 agent backends `except Exception` blocks.
- **Parallel explore audits**: `bg_77b03b1d` (per-rep paths/collisions), `bg_2f4df16e` (bash-to-python --reps flow), `bg_bc120e28` (mock/docker cleanup), `bg_b8078f6f` (backends + testgen + bash recovery), `bg_05790783` (work_dir + headroom + bearer), `bg_bb73b91e` (test_executor + judge + health logger + drift), `bg_64c87c52` (aggregate + sidecar + mock_stack).
- **Oracle audits**: 2 rounds (the second returned VERDICT=FAIL with 8 specific gap categories; this diagnosis addresses all 8 — see §A reframing per Gap 1, §A1 demoted per Gap 2, §A1-A6 enumerated per Gap 3, §F-G honesty per Gap 4, no setup-phase fix promised per Gap 9, etc.).
- **Local log inspection**: `logs/` contains only `_run1_` files (3 files). No `_run2_` exists locally. Diagnosis remains static.
- **AGENTS.md invariants honored**: `run.sh:776` always exit 0; `run_single_task` wrap pinned by `test_run_single_task_isolation.py`; `GROUND_TRUTH_SECTION_ALIASES` never widen; `extract_ground_truth_sections` pure; `_normalize_heading_text` broad collapse load-bearing; `_overlay_manifest.json` stripped from bundle; env source = `output/<backend>/<task>/data/environment`; aggregate_runs reads `score.json` with `criteria_*/overall_score`.

---

**END OF DIAGNOSIS**

This document is the deliverable for user request m0229 ("Diagnose all the possible error points across this codebase on why multiple runs are not working tasks"). It is analyze-only per ULTRAWORK mode; no code was modified.
