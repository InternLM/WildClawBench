# WildClawBench Runbook

End-to-end operator guide for running the harness, from a cold machine to a graded run with `score.json` on disk.

---

## 1. What this harness does (one paragraph)

WildClawBench runs an LLM agent (default: `claude-opus-4.7` via Bedrock through a LiteLLM sidecar) against a task that ships a prompt, a rubric, optional persona/data/mock-API overlays, and optional drift scripts. The agent runs inside a sandboxed Docker container with no internet egress, talking only to the LiteLLM sidecar (which has internet) and a 101-API mock stack on a private internal bridge. After the agent finishes, the harness generates tests (or reuses cached ones), executes them as a pytest reward signal, then asks a 3-judge Bedrock council to score the rubric as Yes/No verdicts. All outputs land under `output/<backend>/<task>/trajectories/<model>/run_N/`.

---

## 2. Prerequisites

### Required on the host
- **Docker Engine ≥ 24** (Docker Desktop fine). Must be running. Apple Silicon works (agent image runs amd64 under Rosetta 2).
- **Python 3.10–3.12**. Python 3.14 has known wheel issues.
- **`pip`** or **`uv`** for installing requirements.
- **~50 GB free disk** (agent image alone is 27.9 GB on disk).

### Optional but strongly recommended
- **`pv`** — shows progress when loading the 13 GB agent tar. `script/run.sh` will auto-install it on first use if missing: Homebrew on macOS (only if `brew` is already present), or `apt-get` / `dnf` / `yum` / `apk` on Linux (only if `sudo` works without a password, or the script runs as root). If auto-install can't run, the load still works — it just appears silent for 2-15 minutes. Manual install: `brew install pv` (macOS) or `sudo apt-get install -y pv` (Debian/Ubuntu).
- **`huggingface_hub` CLI** (`pip install huggingface_hub[cli]`) — for downloading the agent image tar from HF.

### Credentials you must have
- **AWS Bedrock bearer token** with access to the inference-profile ARNs in your `.env` (agent + judge council).
- **OpenAI API key** if you want `gpt-5.5` as the agent model or `openai/gpt-5.4` as a judge fallback.

---

## 3. First-time setup

### 3.1 Clone and install Python deps

```bash
git clone <repo-url> wildclawbench
cd wildclawbench
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Create `.env`

Copy `.env.example` to `.env` and fill in. Minimal working set:

```ini
# Agent model (Opus 4.7 via Bedrock through LiteLLM)
KENSEI_BEDROCK_MODEL_ARN=arn:aws:bedrock:ap-south-1:<acct>:application-inference-profile/j6mdizxjngus
KENSEI_BEDROCK_SONNET_ARN=arn:aws:bedrock:ap-south-1:<acct>:application-inference-profile/urg0zifsjiga
KENSEI_AWS_BEARER_TOKEN=ABSK...
KENSEI_AWS_REGION=ap-south-1

# OpenAI (for gpt-5.5 agent or gpt-5.4 judge fallback)
KENSEI_OPENAI_API_KEY=sk-proj-...

# Judge primary (Sonnet via Bedrock direct)
JUDGE_MODEL=bedrock/arn:aws:bedrock:ap-south-1:<acct>:application-inference-profile/urg0zifsjiga
JUDGE_MODEL_FALLBACK=openai/gpt-5.4

# Defaults
DEFAULT_MODEL=claude-opus-4.7
WILDCLAW_DEFAULT_SKILLS=video-frames,pdf-extract,audio-extract
BRAVE_API_KEY=placeholder

# Proxy controls — leave EMPTY. The harness injects these as empty-string overrides
# to neutralize the agent image's baked-in poisoned proxy (Fix 16).
HTTP_PROXY_INNER=
HTTPS_PROXY_INNER=
NO_PROXY_INNER=

# S3 disabled
S3_BUCKET=
UPLOAD_MEDIA_TO_S3=false
```

### 3.3 Get the agent image

The agent image (`wildclawbench-ubuntu:v1.3`, sha `60eec8752cb5`) is not pulled from a registry. It ships as a 13 GB tar on Hugging Face.

```bash
# Download (~13 GB)
hf download internlm/WildClawBench Images/wildclawbench-ubuntu_v1.3.tar \
  --repo-type dataset --local-dir .

# Load (use pv to see progress; takes 2–10 min depending on disk)
pv Images/wildclawbench-ubuntu_v1.3.tar | docker load
```

Verify:

```bash
docker image inspect wildclawbench-ubuntu:v1.3 --format '{{.Id}}'
# Expected: sha256:60eec8752cb597e180780ff08d7569c1892c169521f1f2b069c2efeb006a4078
```

If the tag returns "No such image" but `docker image ls --filter reference=wildclawbench-ubuntu` shows the SHA, the tag table got corrupted (known Docker Desktop quirk after VM restart). Fix:

```bash
docker tag 60eec8752cb5 wildclawbench-ubuntu:v1.3
```

The other two images (`kensei3-mocks:v1` and `ghcr.io/berriai/litellm:main-stable`) are built/pulled automatically on first run.

### 3.4 Smoke test

```bash
pytest tests/test_drift_plane_smoke.py -q
# Expected: 6 passed
```

If this fails, do not proceed — your install is broken.

---

## 4. Anatomy of a task

A task lives in `input/<task_id>/`. Two shipped examples: `input/alden-croft_MB/`, `input/renata-voss/`.

### Required files
| File | Purpose |
|---|---|
| `prompt.txt` | The task prompt the agent reads. |
| `rubric.json` | List of criteria. Bare list OR `{"rubrics": [...]}`. Each item: `{id, criterion, weight, evaluation_target}`. Weights must be in `{5, 3, 1, -1, -3, -5}` (positive = desired behavior, negative = guardrail). |

### Optional
| Path | Purpose |
|---|---|
| `persona/` | 0–7 of `AGENTS.md`, `SOUL.md`, `MEMORY.md`, `IDENTITY.md`, `USER.md`, `TOOLS.md`, `HEARTBEAT.md`. Copied to `/root/` and indexed into `/root/memory/` for openclaw's memory search. |
| `data/` | Workspace inputs. Copied into `/root/workspace/` at agent start. Subdirs preserved. |
| `mock_data/<api>-api/*.csv` | Per-API overlay files. Bind-mounted READ-ONLY at `/opt/mocks/<api>/<filename>:ro` into the mock-stack container. |
| `drift.yaml` | DriftDirector script (mid-run mutations of mock API data). |
| `task_config.yaml` | Optional config; participates in testgen cache key. |
| `taxonomy.json` | Override derived L1/L2 labels. |
| `gt/` | Ground-truth files. Used only by graders, never staged for the agent. |

### Required-API inference
The harness infers which APIs the agent will need from (a) keyword matching against `prompt.txt`, (b) directories present under `mock_data/`. Inferred APIs get their connector skills (`environment/skills/<api>-api-connector/`) copied into `/usr/lib/node_modules/openclaw/skills/` so the agent can read their `SKILL.md`. All 101 API URL env vars (`<API>_API_URL=...`) are injected regardless. Distractor APIs = all 101 minus required.

---

## 5. Running

### 5.1 Easiest: use `script/run.sh`

The wrapper handles preflight (docker daemon, image presence, tag corruption, orphan cleanup), runs the harness, and on docker errors retries once.

```bash
# Default: input/alden-croft_MB, claude-opus-4.7, K=1
bash script/run.sh

# One task, K=1
bash script/run.sh input/renata-voss

# One task, custom model
bash script/run.sh input/renata-voss gpt-5.5

# pass@K — run the same task 4 times sequentially, then auto-aggregate
bash script/run.sh input/alden-croft_MB claude-opus-4.7 4

# Bulk: one task path per line in tasks.txt
bash script/run.sh --bulk tasks.txt claude-opus-4.7 1

# Help
bash script/run.sh --help
```

Per-run logs land in `logs/<task>_<model>_run<N>_<ts>.log`.

### 5.2 Direct invocation (for one-off custom flag combos)

```bash
python3 eval/run_batch.py \
  --task input/alden-croft_MB \
  --agent-backend openclaw \
  --model claude-opus-4.7 \
  --litellm \
  --mock-stack \
  --generate-tests --testgen-max-attempts 3 \
  --execute-tests --testexec-timeout 600 \
  --thinking xhigh \
  --parallel 1 \
  --judge-council \
  2>&1 | tee "logs/manual_$(date +%Y%m%d_%H%M%S).log"
```

### 5.3 Important CLI flags

| Flag | What |
|---|---|
| `--task <path>` | Required (or `--category`). Path to task directory. |
| `--agent-backend openclaw\|claudecode\|codex\|hermesagent` | Default `openclaw`. |
| `--model <name>` | e.g. `claude-opus-4.7`, `gpt-5.5`. |
| `--litellm` | Use the LiteLLM sidecar. Always set this. |
| `--mock-stack` | Start the 101-API mock container. Always set this. |
| `--generate-tests` | Run testgen (skipped if cached). |
| `--testgen-max-attempts 3` | Retry budget for testgen. |
| `--execute-tests` | Run the pytest reward signal. |
| `--testexec-timeout 600` | Per-test-subprocess wall-clock cap (seconds). |
| `--thinking xhigh` | Reasoning effort. |
| `--parallel 1` | Keep this 1 — concurrent runs race on shared mock image + Bedrock throttles. |
| `--judge-council` | Use 3-judge council (Sonnet + Kimi + GLM). Without it, falls back to single judge (Sonnet primary, gpt-5.4 fallback). |
| `--force-testgen` | Bypass the testgen cache and regenerate tests. |

### 5.4 Sequential vs parallel
The wrapper runs sequentially. Concurrent runs are unsupported:
- `kensei3-mocks:v1` image build is not concurrency-safe.
- Two parallel Bedrock streams hit ThrottlingException.

Wall clock is roughly 6–10 min per run (testgen + agent + testexec + judge), so K=4 ≈ 25–40 min total.

---

## 6. Output anatomy

After a run, `output/<backend>/<task>/trajectories/<model>/run_N/` contains:

| Path | What |
|---|---|
| `output.json` | Trajectory (messages, tool calls, usage). |
| `score.json` | Judge verdict per criterion + `overall_score` + `rubric_weights_percentage`. Stub written on judge failure with `error` field. |
| `usage.json` | Token counts per phase (agent / testgen / judge). `agent.usage_source: 'litellm'` confirms real provider counts. |
| `agent.log` + `gateway.log` | openclaw runtime logs (also include `[gateway]`, `[tools]`, `[security]` events). |
| `chat.jsonl` | Host snapshot of agent's chat log (via `docker cp /tmp/chat-snap-<task>.jsonl` — anti-tamper). |
| `task_output/artifacts/` | **Agent-produced files only.** Populated by diff against baseline taken before agent ran. Empty = agent created nothing new. |
| `task_output/workspace_full/` | Full forensic copy of `/root/workspace/` (inputs + outputs + persona + scratch). |
| `task_output/logs/verifier/` | Pytest: `ctrf.json` + `reward.txt` + `test_function_outputs.json` + `test_output.log`. |
| `task_output/data/tests/` | Per-run snapshot of `test_outputs.py` + `test_weights.json`. |
| `drift_timeline.jsonl` | Only present if task ships `drift.yaml`. |

Shared cache (read across runs of same task): `output/<backend>/<task>/data/tests/{test_outputs.py, test_weights.json}`. Reused unless `--force-testgen` is set or the testgen cache key (hash over rubric.json + prompt.txt + task_config.yaml + mock_data manifest) mismatches.

### 6.1 What "good" looks like

- `score.json` exists, no `error` field, `overall_score` between 0.0 and 1.0.
- `task_output/artifacts/` has the deliverables the rubric expects.
- `usage.json` shows `agent.request_count > 0` and `judge.request_count` ≥ 1 (3 if council survived).
- `reward.txt` in verifier dir is non-zero (depends on test pass rate).

### 6.2 What "bad" looks like

- `task_output/artifacts/` empty → agent created no new files. Either it gave up, wrote to the wrong location, or genuinely had nothing to produce. Check `chat.jsonl` last assistant message and `output.json` for `stopReason`.
- `score.json` has `error` field → judge raised. The stub still tells you which `results_dir` was attempted and which exception type fired.
- `score.json` missing entirely → judge phase wasn't entered. Check the `logs/*.log` runlog for `[task] rubric grading failed: <exc>` warnings.
- `usage.json` `agent.usage_source: 'estimated'` (not `'litellm'`) → LiteLLM never streamed a response. Sidecar or upstream broke.

---

## 7. Operational tools

### 7.1 Cross-run aggregation (pass@K)

After K>1 runs, the wrapper auto-invokes:

```bash
python3 script/aggregate_runs.py --backend openclaw
```

Emits `output/openclaw_aggregate_summary.json` with:
- Per `(task, model)`: `runs[]`, `average_rubric_weights_percentage`, `pass_at_k = max(rubric_weights_percentage across K)`, `k`.
- Per `model`: `task_count`, `average_rubric_weights_percentage` (across all runs), `average_pass_at_k` (mean of per-task best).

Manual flags: `--output-root ./output`, `--backend openclaw`, `--write <path>`, `--json-only`.

### 7.2 Re-grade an existing run with an edited rubric

After editing `input/<task>/rubric.json`, re-judge without re-running the agent:

```bash
python3 script/regrade.py --run output/openclaw/<task>/trajectories/<model>/run_N
```

Reuses the existing `chat.jsonl` + `task_output/artifacts/` (or `workspace_full/` fallback) as evidence. Always uses the council. Overwrites `score.json` in place. ~$0.05 vs ~$6 for a full re-run.

Options:
- `--rubric path/to/alt.json` — A/B against a different rubric file.
- `--quiet` — suppress the summary print.

### 7.3 Hot-edit prompts

All 7 LLM prompts live in `system_prompts/*.md`:
- `judge_system.md`, `judge_user.md` — Yes/No verdict spec.
- `testgen_system.md`, `testgen_user.md`, `testgen_weights_system.md`, `testgen_intent.md`, `testgen_rubric_overlap.md` — testgen.

Loader is LRU-cached. To pick up edits without restarting:

```bash
WCB_PROMPT_NOCACHE=1 python3 eval/run_batch.py ...
```

### 7.4 Verbose LiteLLM logging

```bash
LITELLM_LOG=DEBUG bash script/run.sh ...
# Then: docker logs ll-<batch_id>
```

---

## 8. Critical env vars

| Var | Effect |
|---|---|
| `KENSEI_MOCK_REBUILD=1` | Force rebuild of `kensei3-mocks:v1`. |
| `KENSEI_LITELLM_HEALTH_TIMEOUT=180` | Sidecar health probe budget (default 120s). |
| `JUDGE_COUNCIL=1` | Enable council without `--judge-council` flag. |
| `JUDGE_MAX_EVIDENCE=N` | Override per-judge evidence char cap (default 450k, per-member budgets apply). |
| `JUDGE_COUNCIL_DISAGREEMENT_THRESHOLD=0.30` | Stddev threshold for disagreement flags (legacy mean-aggregator artifact). |
| `KENSEI_JUDGE_USE_LITELLM=true` | Route judge calls through LiteLLM library mode (default OFF → urllib direct). On any LiteLLM error the dispatcher falls back to urllib. |
| `KENSEI_JUDGE_HEADROOM_ENABLED=false` | Disable Headroom compression while keeping LiteLLM (A/B testing). Default ON when `KENSEI_JUDGE_USE_LITELLM=true`. |
| `KENSEI_JUDGE_HEADROOM_TARGET_RATIO=0.4` | Headroom target compression ratio. |
| `KENSEI_JUDGE_HEADROOM_PROTECT_RECENT=2` | Headroom protect-recent message count. |
| `KENSEI_JUDGE_HEADROOM_MIN_TOKENS=2000` | Skip Headroom compression below this token count. |
| `KENSEI_AGENT_HEADROOM_ENABLED=true` | Enable Headroom compression on the AGENT-path sidecar (`claude-opus-4.7`, `gpt-5.5`). Default OFF → sidecar uses stock `ghcr.io/berriai/litellm:main-stable`. When ON, sidecar uses `wildclawbench-litellm-headroom:v1` (must be built first; see below). |
| `KENSEI_AGENT_HEADROOM_TARGET_RATIO=0.4` | Agent-path Headroom target compression ratio. |
| `KENSEI_AGENT_HEADROOM_PROTECT_RECENT=4` | Agent-path protect-recent message count (larger than judge's 2 because tool loops have more recent context worth preserving). |
| `KENSEI_AGENT_HEADROOM_MIN_TOKENS=2000` | Skip agent-path compression below this token count. |
| `KENSEI_AGENT_HEADROOM_LOG_PATH=/var/litellm_headroom/headroom.jsonl` | Agent-path compression-telemetry JSONL path INSIDE the sidecar container (separate from `LITELLM_USAGE_LOG_PATH` by mandate — token tracking is owned exclusively by `litellm_usage_callback.py`). |
| `WCB_PROMPT_NOCACHE=1` | Bypass prompt cache, re-read `.md` per call. |
| `LITELLM_LOG=DEBUG` | Verbose sidecar logs. |

**Headroom telemetry (judge):** when `KENSEI_JUDGE_USE_LITELLM=true`, per-call compression stats land in `score.json.judge_council.headroom_per_member` and the cumulative `headroom_tokens_saved_total`. Inspect via `jq '.judge_council.headroom_per_member' output/**/score.json`.

**Headroom telemetry (agent sidecar):** when `KENSEI_AGENT_HEADROOM_ENABLED=true`, the sidecar writes per-request compression rows to a SEPARATE JSONL at the host mount `config.work_dir/litellm-headroom-<batch_id>/headroom.jsonl` (8 keys: `ts, model, call_type, tokens_before, tokens_after, tokens_saved, compression_ratio, transforms_applied`). The 11-key `usage.jsonl` token-tracking schema is untouched.

**Building the agent-path Headroom image (one-time, only needed when `KENSEI_AGENT_HEADROOM_ENABLED=true`):**
```bash
docker build -f docker/litellm-headroom.Dockerfile -t wildclawbench-litellm-headroom:v1 .
```
Inspect compression stats per batch:
```bash
jq -s 'group_by(.model) | map({model: .[0].model, total_saved: (map(.tokens_saved) | add), n: length})' \
  /tmp/wildclawbench/litellm-headroom-<batch_id>/headroom.jsonl
```

---

## 9. Troubleshooting

### `Required Docker image not present locally: wildclawbench-ubuntu:v1.3`
Tag table corruption or image never loaded. Run `script/run.sh` once — preflight will re-tag from SHA or attempt tar load. Manually:
```bash
docker image ls --filter reference=wildclawbench-ubuntu
docker tag <sha-shown> wildclawbench-ubuntu:v1.3
```

### `LLM request timed out` / `Connection error.` in `gateway.log`
The image has a baked-in poisoned proxy (`http://100.104.40.233:7897`). Fix 16 should override it via empty-string env vars. Verify by `docker exec <agent-task-id> env | grep -i proxy` — should show `http_proxy=` and `https_proxy=` as empty. If they're set, the harness isn't overriding correctly.

Note: openclaw's embedded-agent has its own hardcoded ~22s connection timeout, which fires before LiteLLM's `request_timeout: 86400`. This means: connection failures look like timeouts ~22s in. Real LLM slowness past 22s won't trigger this — it's TCP-connect-side only.

### `score.json` missing, agent succeeded
Judge raised an exception. Look in the runlog (`logs/*.log`) for `[task] rubric grading failed: <exc>`. Common causes:
- Council quorum failed (all 3 judges raised). Often a Bedrock context-window violation if rubric × evidence is huge.
- `_VERDICT_RE` parser found 0 matches in judge output. Either judge ignored the format spec, or `_VERDICT_RE` was changed without updating `judge_system.md`.
After Fix 2 atomic shipment, this should always produce a stub `score.json` with the `error` field naming the exception type. If you see no score.json AND no stub, the trajectory write itself failed.

### `artifacts/` empty, agent ran 10 minutes
Agent never wrote to `/root/workspace/`. Either:
- It wrote to `/tmp/` or `/root/<elsewhere>/`. Check `workspace_full/` — if files are there, the sweep didn't pick them up (extension not in `_ROOT_DELIVERABLE_EXTENSIONS`).
- It strategically flailed (e.g. burned turns on parsing). Read `chat.jsonl` last 5 messages.
- Backend doesn't snapshot (only openclaw/codex/claudecode do; hermesagent will always show empty artifacts/).

### `agent.usage_source: 'estimated'`
LiteLLM's success callback never fired. Possible:
- Sidecar died after preflight passed. `docker logs ll-<batch>` while next run is live.
- Upstream provider rejected the request after streaming started. Common with org-verification 400s on gpt-5.5 with `summary: detailed`.
- All requests timed out at openclaw's 22s ceiling before LiteLLM could parse a response.

### Mock APIs not reachable from agent
Container name regex was fixed in Fix at run_batch.py:776 (sanitization + `t_` prefix). If you still see container-name errors, your task id has very unusual characters. Check `gateway.log` for `mocks-task-<id>:8002` URLs and confirm DNS via `docker exec <agent> getent hosts mocks-task-<id>`.

### `kensei3-mocks` running stale code
The image has a content-hash label (`kensei3.content_hash`) computed over `environment/*`. If you edited `environment/_mutable_store.py` or any `<api>_data.py` and didn't see a rebuild, force it:
```bash
KENSEI_MOCK_REBUILD=1 bash script/run.sh ...
```

### Cleanup orphans after a crashed run
```bash
docker rm -f $(docker ps -aq --filter 'name=ll-' --filter 'name=mocks-' --filter 'name=t_') 2>/dev/null
docker network ls --filter 'name=k3net-' -q | xargs -r docker network rm 2>/dev/null
```
The `script/run.sh` preflight does this automatically.

---

## 10. Operational invariants worth knowing

These are non-obvious facts that protect you from cargo-culting bad behavior:

1. **No internet egress from the agent.** Agent container is on `--internal` bridge. Only the LiteLLM sidecar is dual-homed to reach Bedrock/OpenAI. Empirical test: `docker run --rm --network k3net-* wildclawbench-ubuntu:v1.3 curl https://api.ipify.org` returns exit 7.
2. **`/root/workspace/` is the only deliverable location.** Files written to `/tmp/` or other `/root/<dir>/` paths are NOT collected (Fix 9 prompt hint covers this, but the agent might disobey). The artifacts/ baseline-diff is your evidence of what the agent actually produced — empty `artifacts/` is a true signal, not a bug.
3. **Reward formula is binary, not fractional.** Council resolves each criterion by unanimous-or-Sonnet-tiebreak: unanimous verdict if all members voted and agree, else Sonnet's verdict (source of truth for both genuine splits and partial coverage), else Human Evaluation (abstain). Abstained (human-eval-required) criteria are excluded. Reward = `sum(weight where resolved satisfied) / sum(weight where weight > 0)`. No fractional credit possible (the b78 rewrite eliminated the b51 leak structurally).
4. **Testgen cache is hash-keyed.** Editing `rubric.json`, `prompt.txt`, `task_config.yaml`, or anything under `mock_data/` invalidates the cache automatically. The cache key lives at `output/<backend>/<task>/data/tests/cache_key.txt`. `--force-testgen` bypasses.
5. **score.json `criteria_*` is canonical; `tests_*` is a deprecated alias.** Both shipped for back-compat. `aggregate_runs.py` falls back to `tests_*` and `overall_score * 100` for legacy files.
6. **Persona files in `/root/` are NOT swept as deliverables** even though their extensions (`.md`) are in the whitelist. The sweep skip-set explicitly excludes `AGENTS.md SOUL.md MEMORY.md USER.md IDENTITY.md HEARTBEAT.md TOOLS.md API_DOCUMENTATION.md`.
7. **Bedrock prompt caching only works for Anthropic models.** Council Sonnet emits `cachePoint`; Kimi K2.5 and GLM 5 do not (they'd 403). Single-run K=1 won't show any cache hits — 5-min TTL needs at least 2 calls within the window.

---

## 11. File reference

| Path | Role |
|---|---|
| `script/run.sh` | Preflight + sequential runner + auto-aggregate wrapper. |
| `eval/run_batch.py` | Orchestrator entry point. |
| `src/agents/openclaw/runner.py` | openclaw backend dispatcher. |
| `src/utils/docker_utils.py` | Container lifecycle: start, workspace setup, skill/connector injection, deliverable collection. |
| `src/utils/litellm_sidecar.py` | LiteLLM sidecar config + startup + upstream preflight. |
| `src/utils/mock_stack.py` | `kensei3-mocks:v1` build + start. Content-hash label. |
| `src/utils/grading.py` | Judge council + single-judge + verdict parser + reward formula. |
| `src/utils/task_parser.py` | Task input loader (native dir / yaml / md). Workspace hint appender. |
| `src/utils/prompt_loader.py` | LRU-cached loader for `system_prompts/*.md`. |
| `system_prompts/` | All 7 LLM-facing prompts (judge × 2 + testgen × 5). |
| `environment/` | 101 mock API server.py + data modules + skills. Drift plane (`_mutable_store.py`, `admin_plane.py`). |
| `script/aggregate_runs.py` | Cross-run pass@K rollup. |
| `script/regrade.py` | Re-judge an existing run with an edited rubric. |
| `tests/test_drift_plane_smoke.py` | 6-test smoke suite. Must pass before any change ships. |
| `NOMENCLATURE.md` | Field/key glossary for output files. |
| `Images/wildclawbench-ubuntu_v1.3.tar` | Agent image tar (13 GB, gitignored, download from HF). |

---

## 12. Recipes

### Run one task, look at the score
```bash
bash script/run.sh input/alden-croft_MB
cat output/openclaw/alden-croft_MB/trajectories/claude-opus-4.7/run_1/score.json | python3 -m json.tool | head -40
ls output/openclaw/alden-croft_MB/trajectories/claude-opus-4.7/run_1/task_output/artifacts/
```

### pass@K=4 and aggregate
```bash
bash script/run.sh input/alden-croft_MB claude-opus-4.7 4
cat output/openclaw_aggregate_summary.json | python3 -m json.tool
```

### A/B the same trajectory against an edited rubric
```bash
# Run once
bash script/run.sh input/alden-croft_MB
# Edit input/alden-croft_MB/rubric.json
python3 script/regrade.py --run output/openclaw/alden-croft_MB/trajectories/claude-opus-4.7/run_1
# Or against an alt file without overwriting the input
python3 script/regrade.py \
  --run output/openclaw/alden-croft_MB/trajectories/claude-opus-4.7/run_1 \
  --rubric input/alden-croft_MB/rubric.alt.json
```

### Compare two models on the same task
```bash
bash script/run.sh input/alden-croft_MB claude-opus-4.7 1
bash script/run.sh input/alden-croft_MB gpt-5.5 1
python3 script/aggregate_runs.py --backend openclaw
```

### Bulk run a task list
```bash
cat > tasks.txt <<EOF
input/alden-croft_MB
input/renata-voss
EOF
bash script/run.sh --bulk tasks.txt claude-opus-4.7 1
```

### Hot-edit a prompt without restarting Docker state
```bash
# Edit system_prompts/judge_system.md
WCB_PROMPT_NOCACHE=1 python3 script/regrade.py \
  --run output/openclaw/<task>/trajectories/<model>/run_N
```

---

## 13. When something genuinely doesn't work

In order:
1. `pytest tests/test_drift_plane_smoke.py` — if this is red, fix it first.
2. `docker ps -a` — any leaked `ll-`, `mocks-`, `t_` containers? `script/run.sh` preflight will clean them, or do it manually (§9).
3. `cat logs/<latest>.log | grep -E 'ERROR|WARNING'` — surface the real failure.
4. `cat output/.../score.json` — if it has an `error` field, that's the proximate cause.
5. `docker logs ll-<batch_id>` — if the run is still alive or only recently dead, sidecar logs reveal upstream failures.
6. Read the `chat.jsonl` last 5 messages — confirms what the agent actually saw and did.

Most failures are one of: docker tag corruption, baked-in proxy not overridden, openclaw 22s connect ceiling, mock APIs unreachable, judge context overflow. All have signatures in the logs.
