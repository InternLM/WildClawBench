# Live LLM Response Streaming — Detailed Implementation Plan

**Status:** approved for implementation · **Author:** research pass 2026-07-10
**Scope:** stream AI responses live during trajectory generation (agent), judge grading, and testgen — terminal now, Odoo frontend later — on **both** branches (`main` / Bedrock, `claude_oauth_pathway` / Claude-subscription OAuth), **without changing how trajectories are generated or what is delivered**.

Verified against: `main` @ `7091e6c`, `claude_oauth_pathway` @ `cfdad62`.
Every claim below was read from the code at those commits; file:line refs are anchors, not guesses.

---

## 0. Locked decisions (from TL + follow-ups)

| # | Decision |
|---|---|
| D1 | Terminal rendering now; Odoo frontend later. The stream contract (JSONL side-channel) must serve both unchanged. |
| D2 | Stream **all 3 judge council members** (Sonnet, Kimi, GLM), answer text only — judges emit no thinking **by design** (judge calls strip all reasoning params; test-enforced invariant, `tests/test_judge_litellm.py` invariant 6). |
| D3 | Agent stream shows **thinking + final text** as deltas. |
| D4 | OAuth-branch Sonnet judge stays `stream: False` (`judge_litellm.py:363`) — **no streaming change for it**. It still gets a status line (started/finished) in the display. |
| D5 | Sub-agent / concurrent-call handling (Q1): tag every event with a request id; render the **main session token-by-token**, sub-agents as prefixed line-buffered summaries; filter non-trajectory traffic (preflight pings, embeddings, whisper, image-tool calls). |
| D6 | Shared-sidecar attribution (Q2): token-level rendering **only in single-run foreground** (K=1, one model, `--parallel-tasks 1`). Under fan-out, degrade to per-run turn-level from `agent.log` (inherently per-run). No per-request run-tagging is attempted — same wall-clock-window philosophy as usage attribution (`grading.py:1590`). |
| D7 | `stream.jsonl` artifact rules (Q3): non-blocking fail-open writes, size-capped, **never** consulted by grading, **never** shipped in deliverables. |
| D8 | **Nothing about trajectory generation or deliverables changes.** All protocol paths stay byte-identical; buffer-and-retry stays ON on the OAuth branch. |

---

## 1. Verified findings (what the code actually does today)

### 1.1 What already streams on the wire

| Path | Branch | Verified behavior |
|---|---|---|
| openclaw agent → LLM | main | openclaw → LiteLLM sidecar `/v1/messages` (anthropic-messages) → Bedrock INVOKE, native Anthropic SSE. Sidecar config sets `stream_options: {include_usage: true}` on every model block (`litellm_sidecar.py:115,150,175,205`) and `stream_timeout: 86400` (`:349`). |
| openclaw agent → LLM | oauth | openclaw → sidecar (`api_base` = bridge) → **cc-bridge** → `api.anthropic.com`. The bridge's **buffer-and-retry is ON by default** (`WCB_CC_BUFFER_AND_RETRY`, `bridge.py:267-271`): it consumes the whole upstream SSE stream (emitting keepalive pings, `bridge.py:282-285`), then replays a complete response. Client-side, tokens arrive as an end-of-turn burst. |
| Judge council | both | Host-side HTTPS POST to Bedrock `/converse-stream`, consumed event-by-event via `iter_eventstream` — `contentBlockDelta` texts are appended one at a time then joined (`grading.py:723-736`). Already a delta loop; nothing surfaces the deltas. |
| Sonnet judge | oauth only | Routed through the bridge via `litellm.completion` with `"stream": False` (`judge_litellm.py:363`, bridge override at `judge_litellm.py` `_judge_oauth_bridge_url`). Stays that way (D4). |
| testgen | both | httpx to `/converse-stream`, same delta-aggregation pattern (`src/utils/testgen/bedrock.py:106-111`). |
| OpenAI judge fallback | both | SSE with `stream: True` (`grading.py:577-583`). Rarely used (council members are Bedrock ARNs). |

### 1.2 What the operator sees today

Nothing live. `run_background()` (`src/utils/docker_utils.py:1045-1057`) redirects `openclaw agent` stdout+stderr into `run_N/agent.log` via a live host-side file descriptor — inspection of an on-disk run confirms **turn-level narration is written in real time** — but nothing tails it. `script/run.sh::run_one` (`run.sh:521-558`) pipes all of `eval/run_batch.py`'s output through `tee "$RUN_LOG"`; the operator sees only harness log lines.

### 1.3 The LiteLLM streaming hook — VERIFIED WORKING for our route

Checked **inside the locally cached digest-pinned sidecar image** (litellm `1.82.3`):

- `CustomLogger.async_post_call_streaming_iterator_hook` exists, signature
  `(user_api_key_dict, response, request_data) -> AsyncGenerator[ModelResponseStream]`.
- **The `/v1/messages` route fires it.** Read from the image's own proxy source:
  `litellm/proxy/anthropic_endpoints/endpoints.py:51-53` routes through
  `ProxyBaseLLMRequestProcessing.base_process_llm_request`, whose streaming return
  path is `async_sse_data_generator` → `async_streaming_data_generator`
  (`litellm/proxy/common_request_processing.py:1046,1375`), which wraps the response in
  `proxy_logging_obj.async_post_call_streaming_iterator_hook(...)` and then the
  per-chunk `async_post_call_streaming_hook`.
- Callback dispatch: `litellm/proxy/utils.py:2167-2188` iterates registered callbacks
  and applies each one's iterator hook.

Residual risk: the **production** pin is a different (newer, ~1.88) digest
(`litellm_sidecar.py:21`, identical constant on both branches). Hooks only accumulate
across versions, so this is a formality — but Phase 0 still re-runs the same two
checks against the exact pinned digest (5 minutes, commands in §7 Phase 0).

The pin itself is load-bearing (Bedrock thinking passthrough regression history,
`litellm_sidecar.py:11-21`). **We adapt to the image; we never bump the pin for this feature.**

### 1.4 Chunk shape caveat on the anthropic route

`async_streaming_data_generator` handles chunks that are `ModelResponse`/`ModelResponseStream`, pydantic objects, **or plain dicts** (`common_request_processing.py:1390-1400`). On the `/v1/messages` route, chunks are anthropic-format events (`message_start`, `content_block_delta` with `delta.type` ∈ `text_delta|thinking_delta|input_json_delta`, `message_stop`). The emitter MUST handle both shapes defensively (anthropic dict events and OpenAI-style `choices[0].delta`).

### 1.5 Why the OAuth branch needs its own tap (not redundant)

On oauth, the sidecar sits **in front of** the buffering bridge. The sidecar's iterator hook still fires, but only when the bridge finishes buffering and replays — i.e. an **end-of-turn burst**, not real-time. Real-time tokens on oauth are only visible **inside the bridge**, which already holds every chunk as it buffers (`_stream_buffered_with_retry`, `bridge.py:956+`; passthrough `event_stream()`, `bridge.py:852-905`). Hence two emitters:

- main → sidecar callback (real-time)
- oauth → bridge tee (real-time); the sidecar stream callback is **not registered** on the oauth path to avoid duplicate burst events (the yaml builder already knows `use_claude_oauth`).

### 1.6 Existing patterns we reuse (verbatim precedents)

| Need | Precedent |
|---|---|
| Proxy callback file mounted into sidecar + registered in yaml | `litellm_usage_callback.py` mounted at `/app/litellm_usage_callback.py:ro` with writable `/var/litellm_usage` dir + `LITELLM_USAGE_LOG_PATH` env (`litellm_sidecar.py:517-522`); registered via `litellm_settings.callbacks: [...]` list built at `litellm_sidecar.py:320-330` |
| Fail-open callback that must never break the proxy | headroom callback: any exception returns data unchanged (`litellm_headroom_callback.py:59-64`); separate telemetry sink invariant "must never collide with usage log" (user m0130) |
| Non-trajectory traffic detection | `_is_preflight_ping` (`litellm_usage_callback.py:87-116`) |
| Host-side background thread scoped to a run | `_start_mock_health_logger` (`eval/run_batch.py:2063+`, started at `:1455` right before `backend.run_task`) |
| Terminal rendering contract (tty vs pipe vs file) | `script/lib/log.sh` — ANSI only when tty && !NO_COLOR; progress degrades to periodic lines on non-tty |
| Batch-level shared paths handed to child python | `WCB_SHARED_SIDECAR*` env vars from `eval/bootstrap_sidecar.py` / `script/run.sh::bootstrap_shared_sidecar` (`run.sh:438+`) |
| Bridge container start (oauth) | `start_bridge()` (`litellm_sidecar.py:776+` on branch): env via `build_env_args`, mounts `pool_host_dir → /oauth_pool` — we add one more mount + env pair here |

### 1.7 Deliverables are safe by construction (verified)

`script/repackage_to_bundle.py` copies **only named items** per run: `output.json`, generated `report.json`, `output_media/` (from `task_output/artifacts`), `logs/verifier/` (`copy_verifier_logs:846`, `copy_output_media:874`, `build_report:766`). It never copies the whole `run_N/` dir. A `stream.jsonl` placed in `run_N/` is therefore excluded from bundles — and `deliver.sh` ships only bundler output. No ignore-list change is strictly required; we add an explicit exclusion comment + test anyway (belt-and-braces, §8).

### 1.8 Race-condition analysis (the TL's prior failure, mapped to this code)

Downstream (`run_single_task` `finally`: transcript snapshot → `grade_the_task` → `collect_usage` → `collect_task_output` → `execute_tests` → `_build_trajectory` incl. judge council → teardown → last-resort score stub) triggers on **agent process exit** (`runner.py:280-296`), not on any stream signal. The hazards a naive streaming layer introduces:

1. **Transcript flush lag** — mitigated on main by the RC-2 early snapshot (`runner.py:300-310`, atomic `.tmp`+rename `runner.py:112-131`). Our design must not delay or reorder that snapshot. It doesn't: the tap is downstream-invisible.
   ⚠️ **Branch-state note (verified @ oauth `0d6624a`, 2026-07-10):** `claude_oauth_pathway` does NOT contain main's `706db77`/`7091e6c` (RC-1/RC-2) — no early snapshot, no `__snapshot_recovered__` recovery, no agent-exit-code diagnostics in its runner; it carries an independently-applied older variant of the score.json stub fix in `run_batch.py` (commit `41be357`, branch-side). The streaming design doesn't depend on RC-2, but this is live evidence of the branch-divergence risk: **merge `main` → `claude_oauth_pathway` before (or as step one of) the streaming work**, so streaming is implemented once against a converged base.
2. **Usage-row lag** — `UsageWriter.async_log_success_event` fires after stream completion inside the proxy; `collect_usage` reads by wall-clock window ±2s (`grading.py:1590-1592`). Unchanged by us — we add no consumer between stream end and process exit.
3. **Teardown vs. drain** — `remove_container` + sidecar/network teardown run in the same `finally`. The renderer must be joined with a bounded timeout **before** teardown, but grading never waits on it.
4. **OAuth truncation guards** — buffer-and-retry + `message_stop` truncation detection (`bridge.py` B2 comments) exist because Anthropic drops streams mid-response. We keep them ON; the tee observes, never alters.

**Design rules (non-negotiable):**
- R1. Grading/scoring/tests/bundling gate exactly as today. No code in the authoritative chain reads `stream.jsonl` or waits on the renderer.
- R2. Every emitter is fail-open: any exception in the tap yields the chunk through unchanged and disables itself for the rest of the request.
- R3. Explicit `message_stop` / `error` sentinel per request; renderer join timeout ≤ 5s at run end.
- R4. Delta loops that feed parsers (judge, testgen) keep accumulate-then-parse in the same loop; streaming is emission during accumulation, never a restructure.
- R5. **Pass-the-original-object rule.** Inline taps (sidecar iterator hook, bridge tee) must `yield`/forward the exact chunk object/bytes they received — never parse-then-reconstruct the thing they forward. Delta extraction works on a read of the chunk, the forwarded value is the original reference. Rationale: fail-open (R2) only guards against *raising* bugs; the worst realistic failure is a tap that silently mutates or drops chunks without raising, degrading agent turns invisibly. R5 makes that class impossible by construction; §8 identity tests enforce it and PR review checks it.
- R6. **The gate is batch-scoped.** `WCB_STREAM` is evaluated once at batch setup (it decides callback registration and container mounts at sidecar/bridge start). It cannot be toggled mid-batch, especially in shared-sidecar mode where one sidecar serves every rep. Flag OFF ⇒ the callback is absent from `litellm_settings.callbacks`, the stream mounts/env are not added, the bridge emitter env is unset — the containers and config yaml are **byte-identical to today's**.

---

## 2. Architecture

```
                     ┌────────────────────────────── observability plane (new) ─┐
                     │                                                          │
 main:   openclaw ──▶ LiteLLM sidecar ──▶ Bedrock INVOKE (SSE)                  │
                     │   └─ stream callback (iterator hook) ──▶ stream.jsonl ───┤
 oauth:  openclaw ──▶ LiteLLM sidecar ──▶ cc-bridge ──▶ api.anthropic.com       │
                     │                      └─ tee in buffer loop ─▶ stream.jsonl┤
 judges: grading.py ── urllib /converse-stream ── delta loop ──▶ stream.jsonl ──┤
 testgen: generator.py ── attempt loop ── status events ──────▶ stream.jsonl ───┤
                     │                                                          │
                     └───▶ renderer thread (terminal, log.sh rules)             │
                     └───▶ [Phase 3] Odoo bus consumer                          │
                                                                                │
 authoritative plane (UNCHANGED): chat.jsonl → grading → tests → output.json → bundle
```

One write-only feed, N consumers, zero coupling to the graded pipeline.

### 2.1 Stream event contract (`stream.jsonl`)

One JSON object per line, append-only:

```json
{
  "ts": 1783075200.123,
  "seq": 42,
  "source": "agent" | "judge:sonnet" | "judge:kimi" | "judge:glm" | "testgen",
  "request_id": "<litellm call id | bridge request id | judge call uuid>",
  "model": "claude-opus-4-6",
  "kind": "text" | "thinking" | "status",
  "event": "message_start" | "delta" | "message_stop" | "error" | "status",
  "delta": "<text fragment or status message>"
}
```

- `seq` is monotonic **per request_id** (lets Odoo reorder; the terminal renderer relies on file order).
- `kind:"thinking"` only ever appears with `source:"agent"` (D2/D3).
- Non-trajectory sidecar traffic is **not emitted**: preflight pings (reuse `_is_preflight_ping` logic), embedding mocks, whisper/transcription, and the `gpt-4o*` image-alias rewrites are filtered by model/route in the callback.
- Size cap: emitter stops writing (single WARN line to stderr) past `WCB_STREAM_MAX_BYTES` (default 64 MiB per batch file). Cap applies to the file, not the run.

### 2.2 File locations & knobs

| Thing | Value |
|---|---|
| Per-batch sidecar sink | `<work_dir>/litellm-stream-<batch>/stream.jsonl`, mounted at `/var/litellm_stream` (mirrors usage dir handling, `run_batch.py:1786-1800`) |
| Shared-sidecar mode | `bootstrap_sidecar.py` creates it once; bash exports `WCB_SHARED_SIDECAR_STREAM_LOG`; `_setup_litellm_and_mocks` short-circuit reuses it (mirrors `WCB_SHARED_SIDECAR_USAGE_LOG`) |
| OAuth bridge sink | same host dir mounted into the bridge at `/var/wcb_stream`; env `WCB_CC_STREAM_LOG_PATH=/var/wcb_stream/stream.jsonl` (added in `start_bridge`) |
| Judge/testgen (host process) | append directly to the same host file (`O_APPEND` line writes; host+container concurrent appends of single lines are safe) |
| Per-run archival copy (optional, observability only) | at run end, `run_single_task` copies the window-sliced events to `run_N/stream.jsonl` — same wall-clock-window slicing as usage attribution. Never read by anything downstream. |
| Master gate | `WCB_STREAM=1` env / `--stream` on `script/run.sh` (default **off** for the first release; flip default after a soak week) |
| Thinking toggle | `WCB_STREAM_THINKING` default `1` (dim-rendered); `0` hides thinking deltas in the terminal (they're still in the file) |

---

## 3. Emitters (per surface, per branch)

### 3.1 Agent — main branch: sidecar stream callback  *(new file `src/utils/litellm_stream_callback.py`)*

- `CustomLogger` subclass implementing **only** `async_post_call_streaming_iterator_hook`: async-iterate the wrapped response, `yield` every chunk **unchanged** (protocol untouched), extract deltas on the side.
- Chunk parsing handles both shapes (§1.4): anthropic event dicts (`content_block_delta` → `delta.type` `text_delta`/`thinking_delta`; `message_start`/`message_stop`) and `ModelResponseStream` (`choices[0].delta.content`).
- Filtering: skip requests matching the preflight-ping shape; skip `whisper`/`transcription` call types; skip models registered as embedding mocks.
- `request_id` from `request_data` (litellm call id); `source:"agent"` for everything that survives filtering — sub-agent calls are separate request_ids under the same source, which is exactly what D5's renderer needs.
- Fail-open: the extraction body is wrapped so any exception logs once and degrades to pure passthrough for the rest of the stream. The `yield` path must not be able to raise from our code.
- Registration: third entry in the `_cbs` list (`litellm_sidecar.py:320-330`), gated by a new `enable_stream_callback` param → `"litellm_stream_callback.stream_handler_instance"`. Mount pattern copied from the usage callback (`:517-522`): `-v <file>:/app/litellm_stream_callback.py:ro`, `-v <dir>:/var/litellm_stream`, `-e WCB_STREAM_LOG_PATH=/var/litellm_stream/stream.jsonl`.
- **Sink separation invariant (m0130):** never write to `LITELLM_USAGE_LOG_PATH` **nor** to the OAuth branch's second usage sink `usage_oauth.jsonl` (`litellm_usage_oauth_callback.py`, mounted in the same `/var/litellm_usage` dir — its docstring declares itself "NEVER merged back into usage.jsonl"; ours is a third, equally isolated sink). Schemas never merge. Enforced by test (§8).
- **Not registered when `use_claude_oauth`** (§1.5 — avoids end-of-turn burst duplicates). Hook point exists: `build_litellm_config_yaml` already receives `use_claude_oauth` on the branch, and the callbacks list is built per-flag (`_cbs`, both branches).

### 3.2 Agent — oauth branch: bridge tee  *(edits in `src/utils/claude_oauth/bridge.py`)*

- New tiny module-level emitter (same event schema, `source:"agent"`, `request_id` = bridge-generated uuid per inbound request) writing to `WCB_CC_STREAM_LOG_PATH`; silently inert when the env var is unset (dev runs of the bridge outside docker).
- Tap points, observation-only (both read in full, branch @ `cfdad62`):
  - `_stream_buffered_with_retry._capture()` (default path, `bridge.py:956-1071`): the real-time loop is `async for chunk in upstream.aiter_bytes(): buf += chunk` (`:1043-1049`), which already maintains a rolling 256-byte `tail` for `message_stop`/`error` frame detection — the tee emits beside that bookkeeping using the same carry-buffer technique. `buf` (and `tail`) are re-initialized at the top of each retry attempt (`:996-998`), so **on a mid-stream drop + re-issue the tee emits `{"event":"error","delta":"retrying (attempt N)"}` then a fresh `message_start`** — the renderer replaces the partial turn; the client-facing contract (complete responses only, replayed at end by `event_stream()` `:1072+`) is untouched.
  - `event_stream()` passthrough path (used when `WCB_CC_BUFFER_AND_RETRY=0`): same emitter calls beside the existing `tail` bookkeeping.
- `start_bridge()` gains the mount/env pair. The bridge is started in TWO places on the branch — shared mode in `eval/bootstrap_sidecar.py` (exports `WCB_SHARED_CC_BRIDGE`/`_URL`) and per-rep in `run_batch._setup_litellm_and_mocks` (when `use_oauth and not (shared_mode and shared_cc_bridge)`) — **both** call sites must pass the stream dir mount.
- Buffer-and-retry semantics, timeouts, truncation guards: **zero changes** (D8).

### 3.3 Judges — all council members (D2), both branches

- `grading._call_judge_bedrock._consume` (`grading.py:723-736`): in the existing `contentBlockDelta` branch, add one emitter call per delta (`source: f"judge:{family}"`, `kind:"text"`); emit `message_start` before the loop, `message_stop` after, `error` on the raise paths. This covers **all three members on main** and **Kimi+GLM on oauth**.
- `grading._call_judge_openai` (`grading.py:577+`): same three lines in its SSE loop (completeness; rarely exercised).
- OAuth Sonnet judge (`judge_litellm`): stays `stream: False` (D4). Emit exactly two `status` events around the call ("sonnet judge started/finished") so the terminal shows liveness.
- Verdict parsing (`_parse_verdict_text`) still receives the joined string from the same accumulation loop — R4 holds, no ordering change.
- The 3 members run in a `ThreadPoolExecutor` (`grading.py:914`): emitter appends are single-line `O_APPEND` writes behind one `threading.Lock` (same pattern as `litellm_usage_callback._LOCK`), so interleaving is per-event, never intra-line.

### 3.4 Testgen — status heartbeat only

- `src/utils/testgen/generator.py` attempt loop: `status` events — "testgen attempt N/3 started", "lint pass/fail", "done/fallback-stub". No token streaming (decided earlier; output is code, cached per task).

### 3.5 What is deliberately NOT tapped

- Embedding mocks (zero-vector `mock_response`, no tokens exist).
- Whisper/transcription routes.
- Preflight upstream probe.
- Headroom compression (has its own telemetry sink; unrelated).

---

## 4. Renderer (terminal, Phase 2)

New `src/utils/stream_renderer.py`, host-side daemon thread following the `_start_mock_health_logger` lifecycle pattern:

- **Start:** top of `run_single_task` (before testgen cache prep, so heartbeats show), reading the batch `stream.jsonl` from its current EOF (only this run's events are ahead of it — single-run foreground is the only token mode, D6).
- **Stop:** after `_build_trajectory` (judge events included), **before** container/sidecar teardown and the last-resort stub — `stop()` sets a flag and `join(timeout=5.0)` (R3). Grading never waits on it; the join only delays *teardown*, bounded.
- **Rendering rules** (consistent with `script/lib/log.sh`'s tty contract):
  - tty: agent main-session `text` deltas printed raw as they arrive; `thinking` deltas dim (`\033[2m`), prefixed once per block with `[thinking]`, suppressed entirely when `WCB_STREAM_THINKING=0`; judge events prefixed `[judge:kimi]` etc. and **line-buffered** (token-interleaving three parallel judges is unreadable); `status` events as single dim lines.
  - non-tty (run.sh pipes python output through `tee "$RUN_LOG"`, `run.sh:556` — raw token spew would bloat `logs/`): degrade to one summary line per ~5s ("agent streaming: turn 3, +2.1k tokens"). Full fidelity lives in `stream.jsonl`; `tail -f` it for raw view.
- **Main-session vs sub-agents (D5):** the renderer keys on `request_id`. Heuristic: the longest-lived / first non-filtered agent request in a window is the main session; concurrent additional agent request_ids render as `[sub-agent N]` line-buffered summaries (first line + "…"). This is display-only best-effort — misclassification cannot affect anything graded.
- **Degrade switch (D6):** `run.sh` passes `--stream` → `WCB_STREAM=1` only when `K==1 && #models==1 && PARALLEL_TASKS==1`; otherwise it forces turn-level mode, where the renderer tails `run_N/agent.log` (per-run by construction) instead of the shared token feed.
- **Fallback everywhere:** if `stream.jsonl` is absent/stale >30s while the agent runs, the renderer auto-falls back to `agent.log` tailing. This is also the permanent main-branch fallback if Phase 0 fails on the exact pinned digest.

`script/run.sh` additions: `--stream` / `--no-stream` flags; single-run detection; help text; everything through `log::*`.

---

## 5. Phase 3 (future, out of scope now): Odoo

- A consumer service reads the same `stream.jsonl` (or receives it over a socket if the harness later runs remote) and pushes events over Odoo's bus/longpolling to a widget.
- The event contract in §2.1 (with `seq` + `request_id`) is the API; **no emitter changes will be needed.** Only note kept here so nobody "simplifies" `seq`/`request_id` away.

---

## 6. What explicitly does NOT change (review checklist for the PR)

- `chat.jsonl` writing, the RC-2 early snapshot, atomic snap rename — untouched.
- Grading trigger points, judge aggregation (unanimous-or-Sonnet-tiebreak), reward formulas — untouched.
- `usage.jsonl` schema (11-key), usage attribution windows, preflight handling — untouched.
- Bridge buffer-and-retry, timeouts, truncation-detection, account failover — untouched.
- LiteLLM image digest pin — untouched (both branches).
- Bundle contents, `output_bundle/` layout, `deliver.sh` payload — untouched (verified §1.7; test added anyway).
- `--parallel 1`, shared-sidecar lifecycle, teardown ordering — untouched (renderer join inserts before teardown, bounded 5s).

---

## 7. Phasing & task breakdown

### Phase 0 — pin confirmation (½ day, gate for 1a only)
1. `pull_litellm_image()` the production digest, then run the two checks already validated on 1.82.3:
   - `hasattr(CustomLogger, 'async_post_call_streaming_iterator_hook')`
   - grep the image's `proxy/anthropic_endpoints/endpoints.py` + `common_request_processing.py` for the `async_sse_data_generator → async_post_call_streaming_iterator_hook` chain.
2. Live smoke: start a sidecar with a stub stream callback, send one streamed `/v1/messages` request, assert delta rows appear **before** `message_stop` wall-time. (Reuses `verify_litellm_upstream_reachable`'s probe shape with `stream:true`.)
3. **Fail path:** if the hook doesn't fire on the pinned digest, main ships turn-level only (renderer `agent.log` mode) and we file a follow-up to evaluate a bridge-style tee proxy on main. Nothing else in the plan changes.

### Phase 1a — emitter: sidecar callback (main) (~2 days)
- `src/utils/litellm_stream_callback.py` + registration/mount/env plumbing in `litellm_sidecar.py` (`build_litellm_config_yaml`, `start_litellm`), `_setup_litellm_and_mocks` (per-rep dir + return-tuple extension), `eval/bootstrap_sidecar.py` + `script/run.sh::bootstrap_shared_sidecar` (shared mode: create dir, export `WCB_SHARED_SIDECAR_STREAM_LOG`).
- Unit tests (§8 group A).

### Phase 1b — emitter: bridge tee (oauth branch) (~2 days)
- SSE-frame incremental parser + emitter in `bridge.py` (both buffered + passthrough paths), `start_bridge` mount/env, bootstrap wiring.
- Do **not** register the sidecar stream callback when `use_claude_oauth`.
- Unit tests (§8 group B) — the bridge already has a test harness (`tests/test_claude_oauth_bridge.py`) to extend.

### Phase 1c — emitters: judges + testgen (both branches) (~1 day)
- 3-line emit additions in `grading._call_judge_bedrock._consume` and `_call_judge_openai`; status events around the OAuth Sonnet judge call; testgen heartbeats.
- Unit tests (§8 group C).

### Phase 2 — renderer + run.sh UX (~3 days)
- `src/utils/stream_renderer.py`, lifecycle hooks in `run_single_task`, `--stream` flag + single-run gating in `script/run.sh`, `agent.log` fallback mode, optional per-run `stream.jsonl` archival copy.
- Unit tests (§8 group D) + manual E2E matrix (§8.2).

### Rollout order
**Step 0: merge `main` → `claude_oauth_pathway`** (the branch verifiably lags main's RC-1/RC-2 runner fixes and carries a divergent copy of the score.json stub — see §1.8 branch-state note; converge before adding streaming so it's built once). Then: branch-agnostic pieces (schema, emitter helper, judge emits, renderer, run.sh flag) land on `main` → merge into the oauth branch → bridge tee added as the only branch-specific piece → main agent streaming (post-Phase-0) → judges → renderer polish → flip `--stream` default on after one soak week. Each step ships independently; the system merely streams less at every intermediate point.

---

## 8. Test plan

### 8.1 Automated

**A. `tests/test_litellm_stream_callback.py`** (mirror `test_litellm_headroom_callback.py` structure):
- yields all chunks unchanged (byte/object identity) with emitter healthy, broken, and disabled;
- anthropic-dict and ModelResponseStream chunk shapes both produce correct `delta` rows;
- thinking vs text kinds mapped correctly;
- preflight/whisper/embedding requests emit nothing;
- **writes ONLY to `WCB_STREAM_LOG_PATH`; `LITELLM_USAGE_LOG_PATH` never touched** (m0130-style, capture-path-at-import trick from the headroom test);
- exception inside extraction → passthrough continues, emitter self-disables, no raise;
- size cap honored.

**B. bridge tee tests** (extend `tests/test_claude_oauth_bridge.py`):
- buffered path: client receives byte-identical complete response with tee on/off; delta rows appear during buffering (fake slow upstream);
- mid-stream drop + re-issue: `error` + fresh `message_start` emitted; final client bytes still complete;
- env var unset → zero writes, zero behavior change;
- frame-boundary parsing: marker split across two chunks still parsed (reuse the rolling-tail technique's test vectors).

**C. judge emit tests** (extend `tests/test_judge_litellm.py` / grading tests):
- verdict parse result identical with emitter on/off (R4);
- per-family `source` tags; `stream: False` preserved for OAuth Sonnet (assert on `completion_kwargs`);
- concurrent 3-member emission → no interleaved partial lines in the JSONL (lock test).

**D. renderer + invariants:**
- renderer `stop()` joins ≤5s with a wedged feed (never blocks teardown unboundedly);
- grading path has zero imports/reads of `stream_renderer`/`stream.jsonl` (static assertion test);
- bundler run on a run-dir containing `stream.jsonl` → file absent from bundle output;
- non-tty mode emits summary lines, not raw deltas.

**Gate:** `pytest tests/test_drift_plane_smoke.py -q` stays green (ship gate), full `pytest tests/ -q` green on both branches.

### 8.2 Manual E2E matrix (one row per cell before merge)

| Scenario | Branch | Expect |
|---|---|---|
| Single run, tty, `--stream` | main | live thinking(dim)+text; judges prefixed; all run artifacts present & schema-valid (score.json, usage.json, output.json, chat.jsonl, bundle) |
| Grading-parity control (nondeterminism-proof) | both | take ONE completed `--stream` run dir, run `script/regrade.py` with flag on and off → identical verdicts; agent runs themselves are nondeterministic so score-equality across separate runs is NOT the test |
| Single run, tty, `--stream` | oauth | live tokens **during** the turn (not end-burst); buffer-and-retry retry visibly replaces partial turn |
| Piped through `tee` | both | summary lines only; `logs/*.log` size sane |
| K=3 / multi-model | both | auto turn-level mode, prefixed per run |
| Emitter dir made read-only mid-run | both | run completes, scores identical, single WARN |
| Agent timeout kill | both | renderer stops clean; last-resort/score flow unchanged |

---

## 9. Risks & mitigations (residual)

| Risk | Sev | Mitigation |
|---|---|---|
| Pinned-digest hook divergence (~1.88 vs verified 1.82.3) | Low | Phase 0 gate; `agent.log` fallback already built (renderer mode, §4) |
| Anthropic-route chunk shape differs on newer litellm | Low | dual-shape parser + fail-open; Phase 0 live smoke sends a real streamed request |
| Token spew bloats `logs/` via `tee` | Med | non-tty degrade rule (§4); verified `run_one` pipe layout (`run.sh:556`) |
| stream.jsonl grows unbounded on long batches | Low | `WCB_STREAM_MAX_BYTES` cap + it lives in gitignored `work/`; per-run copy is window-sliced |
| Sub-agent misclassification in renderer | Nil (display-only) | heuristic documented; nothing graded reads it |
| Concurrent host+container appends interleave | Low | single-line `O_APPEND` writes < PIPE_BUF equivalent; lock within each process; renderer tolerates rare torn line (skip unparseable) |
| Someone later wires grading to the stream | — | R1 stated here + static assertion test (§8.1-D) |
| **Silent chunk mutation/drop by an inline tap** (worst case: run completes, agent quietly degraded, nothing raises) | Med | R5 pass-the-original-object rule (by construction) + §8.1-A/B byte/object identity tests + PR review item; fail-open R2 covers the raising class, R5 covers the non-raising class |

---

## 10. Effort summary

| Phase | Effort |
|---|---|
| 0 — pin confirmation | 0.5 d |
| 1a — sidecar callback (main) | 2 d |
| 1b — bridge tee (oauth) | 2 d |
| 1c — judges + testgen | 1 d |
| 2 — renderer + run.sh | 3 d |
| **Total** | **~8.5 dev-days** + soak week before default-on |
