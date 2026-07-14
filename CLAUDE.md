# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo actually is

The public `README.md` describes the upstream **WildClawBench** leaderboard (OpenClaw harness, OpenRouter, a `tasks/` suite). The working code in *this* repo is the **kensei delivery pipeline** fork: it runs an LLM agent against tasks under `input/`, scores them through two independent channels, and (optionally) repackages graded runs into "harbor bundles" for delivery. The operational sources of truth are `RUNBOOK.md`, `NOMENCLATURE.md`, and `EC2_PIPELINE.md` — read those before changing grading, output formats, or the delivery flow. When README and RUNBOOK disagree (e.g. `tasks/` vs `input/`, OpenRouter vs Bedrock), RUNBOOK reflects the real harness.

## Commands

```bash
# Install
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Smoke test — MUST be green before shipping any change (gate enforced by convention)
pytest tests/test_drift_plane_smoke.py -q          # expect 6 passed

# Full unit suite / single test / single case
pytest tests/ -q
pytest tests/test_judge_litellm.py -q
pytest tests/test_judge_litellm.py::test_name -q

# Mock-fleet integrity tests (separate suite under tests/mocks/, FastAPI TestClient)
pytest tests/mocks -q

# Run one task (wrapper: preflight + sequential runner + auto-aggregate)
bash script/run.sh                                  # defaults: input/alden-croft_MB, claude-opus-4.7, K=1
bash script/run.sh input/renata-voss gpt-5.5 4      # task, model, K (pass@K)
bash script/run.sh --bulk tasks.txt claude-opus-4.7 1

# Direct orchestrator invocation (custom flag combos — see RUNBOOK §5.3)
python3 eval/run_batch.py --task input/alden-croft_MB --agent-backend openclaw \
  --model claude-opus-4.7 --litellm --mock-stack \
  --generate-tests --execute-tests --judge-council --parallel 1

# Cross-run rollup (pass@K) and cheap re-grade without re-running the agent
python3 script/aggregate_runs.py --backend openclaw
python3 script/regrade.py --run output/openclaw/<task>/trajectories/<model>/run_N

# Delivery pipeline: run → convert to harbor bundle → push to delivery repo
./deliver.sh --run --task input/<task>              # full; --dry-run skips the push
```

Hot-edit any prompt in `system_prompts/*.md` without restarting Python: prefix the command with `WCB_PROMPT_NOCACHE=1` (the loader is LRU-cached otherwise).

## Architecture

**Orchestrator.** `eval/run_batch.py` is the single entry point. It loads a task (`src/utils/task_parser.py`), augments it with required/distractor mock APIs (`_augment_task_with_mocks`), dispatches to an agent backend, runs the two scoring channels, and writes outputs. `script/run.sh` is a thin sequential wrapper around it (preflight: docker daemon, image presence, tag-corruption repair, orphan-container cleanup, single retry on docker errors).

**Agent backends** (`src/agents/<backend>/runner.py`, selected by `--agent-backend`): `openclaw` (default), `claudecode`, `codex`, `hermesagent`. Each runs the agent inside a sandboxed Docker container on an `--internal` bridge with **no internet egress** — the agent talks only to a LiteLLM sidecar (the only dual-homed container) and the mock-API stack. Backends snapshot the workspace before/after the agent runs to produce a baseline-diff of agent-created files.

**Two scoring channels** (this is the core mental model — see `NOMENCLATURE.md`):
- **Channel A — pytest reward.** `--generate-tests` synthesizes tests (`src/utils/testgen/`, cached by a hash over rubric+prompt+config+mock_data) and `--execute-tests` runs them (`src/utils/test_executor.py`). Emits a scalar `reward.txt` in `[0,1]` plus `ctrf.json`. Real pytest counts use `tests_*` keys.
- **Channel B — rubric judge.** `src/utils/grading.py` grades `rubric.json` criteria as Yes/No verdicts. `--judge-council` uses a 3-judge Bedrock council (Sonnet + Kimi + GLM) with **unanimous-or-Sonnet-tiebreak per criterion**: a unanimous verdict wins when all members voted and agree; otherwise Sonnet's verdict is the source of truth (covering both genuine Yes/No splits and partial coverage when a smaller-context judge truncates). True abstention (Human Evaluation required) only when Sonnet itself cast no verdict. Falls back to a single judge. Canonical output keys are `criteria_*` / `overall_score`; `tests_*` are deprecated aliases of the criteria counts — do not conflate with Channel A.

Reward in both channels is the same signed-weight formula: `max(0, (Σ passed_positive_weights − Σ |triggered_negative_weights|) / Σ all_positive_weights)`. Weights live in `{±5, ±3, ±1}` (negative = guardrail). It is strictly binary — no fractional credit by construction.

**LiteLLM sidecar** (`src/utils/litellm_sidecar.py`). Routes agent + judge calls to Bedrock/OpenAI, does upstream health preflight, and tracks usage. Token tracking is owned exclusively by `litellm_usage_callback.py` (11-key `usage.jsonl`); optional Headroom context-compression telemetry (`litellm_headroom_callback.py`) writes to a *separate* JSONL — never merge the two schemas. The agent-path Headroom image is built from `docker/litellm-headroom.Dockerfile` and is opt-in.

**Mock-API fleet** (`environment/`). 101 self-contained FastAPI services (`<name>-api/`) plus a shared admin/drift/audit plane (`tracking_middleware.py`, `admin_plane.py`, `_mutable_store.py`). `src/utils/mock_stack.py` builds the `kensei3-mocks:v1` image with a content-hash label over `environment/*` — edit any `*_data.py` and rebuild with `KENSEI_MOCK_REBUILD=1`. Each service owns a unique port + `<API>_API_URL` env var (declared in its `service.toml`); port 8069 is permanently unassigned. "Drift" = the admin plane mutating a store mid-run so API responses diverge from what persona `MEMORY.md` claims; `src/utils/drift_director.py` drives it from a task's `drift.yaml`, and drift events are hidden from the agent's `/audit` view by design.

**Harbor bundle / delivery** (`src/utils/harbor/`, `script/repackage_to_bundle.py`, `deliver.sh`). Converts a graded run into the harbour-CLI "bundle" format (task.toml, compose, Dockerfile, solve.sh, test.sh, CTRF) and pushes binaries via Git LFS to the `kensei-delievery` repo. See `EC2_PIPELINE.md` for the headless EC2 flow.

## Task & output layout

A task is a directory `input/<task_id>/` with required `prompt.txt` + `rubric.json`, and optional `persona/` (7 OpenClaw bootstrap `.md` files), `data/` (workspace inputs), `mock_data/<api>-api/*` (read-only overlays bind-mounted into mocks), `drift.yaml`, `task_config.yaml`, `taxonomy.json`, `gt/` (grader-only). Full field reference in `NOMENCLATURE.md §"Task input layout"`.

Per-run output lands under `output/<backend>/<task>/trajectories/<model>/run_N/`: `score.json` (judge verdict), `usage.json`, `*.log`, `chat.jsonl`, and `task_output/{artifacts,workspace_full,logs/verifier,data/tests}/`. **`task_output/artifacts/` contains only agent-created/modified files** (baseline diff) — an empty `artifacts/` is a genuine "agent produced nothing" signal, not a bug. Generated tests are cached per-task at `output/<backend>/<task>/data/tests/`.

## Conventions & gotchas

- **`/root/workspace/` is the only deliverable location** inside the container. Files the agent writes elsewhere (`/tmp/`, other `/root/` dirs) are not collected.
- **Keep `--parallel 1`.** Concurrent runs race on the shared mock image build and hit Bedrock `ThrottlingException`.
- **`.env` proxy vars must be left empty.** The agent image ships a baked-in poisoned proxy; the harness neutralizes it with empty-string overrides. If a run shows `LLM request timed out`, check those overrides first (RUNBOOK §9).
- **Prompt format strings.** `system_prompts/*.md` loaded with `**fmt` (e.g. `judge_user.md`) are Python format strings — literal braces must be doubled `{{ }}`. Prompts loaded without `**fmt` pass braces through.
- **Bedrock prompt caching is Anthropic-only** (council Sonnet caches; Kimi/GLM would 403 on `cachePoint`).
- The agent Docker image (`wildclawbench-ubuntu:v1.3`, ~13 GB) is gitignored and downloaded from HuggingFace; `kensei3-mocks:v1` and the LiteLLM image build/pull automatically.
