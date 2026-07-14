# WildClawBench — Custom Commands Reference

A single-source guide to **every** custom command / script / CLI entry point in this repository, why it exists, what it does, and every flag it accepts.

Commands fall into these tiers:

| Tier | Location | Purpose |
| --- | --- | --- |
| **Tier 1 – Pipeline drivers** | Repo root (`deliver.sh`) + `script/*.sh` | End-to-end orchestration you actually run by hand. |
| **Tier 2 – Integrated CLI** | `eval/run_batch.py` (args defined in `src/utils/cli_args.py`) | The single canonical benchmark entry point. Called by `script/run.sh` — you can also call it directly. |
| **Tier 3 – Standalone Python utilities** | `script/*.py` | Migrations, verification, repackagers, dashboards, and one-off maintenance tools. |
| **Tier 4 – Skill-embedded scripts** | `environment/skills/*/scripts/*` | Utility scripts shipped inside individual agent skills, plus 101 auto-generated per-connector fetch CLIs. |
| **Tier 5 – Environment fleet tools** | `environment/*.py`, `environment/scripts/*.py` | Cross-fleet smoke test + data/wiring audits for the 101 mock APIs. |
| **Tier 6 – CRUCIBLE audit CLI** | `audit/audit.py` (Typer, installable via `audit/pyproject.toml`) | Standalone security-audit harness (`audit scope | approve | run | verify | all`). |

> Conventions used below
> - `-x` = short flag, `--foo` = long flag. `<VALUE>` = argument to supply.
> - "flag" (no value) means a boolean switch (`store_true`/`store_false`).
> - "Required" means the CLI errors if it is missing. "One-of" means part of a mutually-exclusive required group.

---

## Table of Contents

1. [Pipeline shell scripts](#1-pipeline-shell-scripts)
   - [`deliver.sh`](#11-deliversh--run--convert--stage--push)
   - [`script/prepare.sh`](#12-scriptpreparesh--host-bootstrap)
   - [`script/run.sh`](#13-scriptrunsh--end-to-end-eval-runner)
   - [`script/lib/log.sh`](#14-scriptliblogsh--shared-ux-library-sourced-only)
2. [The integrated benchmark CLI](#2-the-integrated-benchmark-cli-evalrun_batchpy)
3. [Standalone Python utilities in `script/`](#3-standalone-python-utilities-in-script)
   - [`aggregate_runs.py`](#31-aggregate_runspy)
   - [`backfill_connector_docs.py`](#32-backfill_connector_docspy)
   - [`coerce_dryrun.py`](#33-coerce_dryrunpy)
   - [`coerce_malformed_test.py`](#34-coerce_malformed_testpy)
   - [`extract_home_to_data.py`](#35-extract_home_to_datapy)
   - [`kensei_tui.py`](#36-kensei_tuipy)
   - [`migrate_to_drift_plane.py`](#37-migrate_to_drift_planepy)
   - [`reconstruct_input_from_bundle.py`](#38-reconstruct_input_from_bundlepy)
   - [`regrade.py`](#39-regradepy)
   - [`repackage_to_bundle.py`](#310-repackage_to_bundlepy)
   - [`rerun_tests.py`](#311-rerun_testspy)
   - [`verify_applied.py`](#312-verify_appliedpy)
   - [`verify_migration_dryrun.py`](#313-verify_migration_dryrunpy)
   - [`rebuild_pass_summary.py`](#314-rebuild_pass_summarypy)
4. [Skill-embedded scripts](#4-skill-embedded-scripts)
5. [Environment fleet tools](#5-environment-fleet-tools)
6. [CRUCIBLE audit CLI (`audit/`)](#6-crucible-audit-cli-audit)
7. [Environment variables at a glance](#7-environment-variables-at-a-glance)

---

## 1. Pipeline shell scripts

### 1.1 `deliver.sh` — run → convert → stage → push

**Path:** `deliver.sh` (repo root)
**Purpose:** One-shot deliverable pipeline. Optionally runs the eval, converts raw run output into the harbour "bundle" format, stages it into a clone of a delivery repo, then commits + pushes.

Four phases:
1. *(optional)* **RUN** — invokes `script/run.sh` for one or more tasks.
2. **CONVERT** — raw run output → bundle via `script/repackage_to_bundle.py`.
3. **STAGE** — clones the delivery repo, copies bundles in.
4. **PUSH** — commits and pushes to the delivery branch.

Two operating modes:
- **CONVERT-ONLY (default):** packages what already exists under `output/`.
- **RUN (`--run`):** runs the eval first, then packages.

**Flags:**

| Flag | Arg | Purpose |
| --- | --- | --- |
| `-h`, `--help` | — | Print help and exit. |
| `--run` | — | Run the eval before converting. Turns on phase 1. |
| `--lfs` | — | Force Git LFS on; missing `git-lfs` becomes fatal. |
| `--no-lfs` | — | Disable Git LFS. |
| `-t`, `--task` | `<input/PATH>` | Add one task to run (repeatable). Requires `--run`. |
| `--tasks-file` | `<FILE>` | File of tasks (one path per line, `#` comments allowed). Requires `--run`. |
| `--all-tasks` | — | Use every immediate subdir of `input/` as a task. Requires `--run`. |
| `-m`, `--model` | `<NAME>` | Model to pass through to `run.sh` (default = `run.sh`'s default). |
| `-k` | `<N>` | Repetitions per (task, model). Default `1`. |
| `--dry-run` | — | Do everything except the final `git push`. |
| `--persona` | `<NAME>` | (Convert-only) Package a single persona instead of `--all`. |
| `--source-root` | `<PATH>` | Raw run-output tree to convert. Default `output/openclaw`. |
| `--deliverable` | `<NAME>` | Folder name inside delivery repo. Default `test_deliverables`. |
| `--branch` | `<NAME>` | Delivery repo branch. Default `main`. |
| `--repo` | `<URL>` | Delivery repo URL. Default `https://github.com/Ethara-Ai/kensei-delievery.git`. |

**Env vars read:** `GITHUB_TOKEN` (or `GH_TOKEN`) for non-interactive push auth, `GIT_TERMINAL_PROMPT`, `NO_COLOR`.

**Examples:**
```bash
./deliver.sh                                                            # convert+push existing bundles
./deliver.sh --run --task input/amanda_hayes_01                         # run one task end-to-end
./deliver.sh --run --tasks-file my_tasks.txt --model claude-opus-4.7 -k 3
./deliver.sh --persona "amanda hayes" --dry-run                         # preview a persona bundle
./deliver.sh --run --all-tasks
```

---

### 1.2 `script/prepare.sh` — host bootstrap

**Path:** `script/prepare.sh`
**Purpose:** Host-side bootstrap that must succeed before `script/run.sh` will work on a fresh clone. Replaces the upstream YouTube/SAM3/dot_git workspace fetcher because this fork uses `input/` persona tasks + a pre-built agent image.

Steps (each idempotent, skip-if-done):

1. Host tool preflight (`python3 ≥ 3.10`, `docker`, `git`, `git-lfs`, `pv`).
2. Python deps (offline wheelhouse if populated, else `pip install -r requirements.txt`).
3. `.env` materialization (copies `.env.example → .env` if missing; never overwrites).
4. LFS sanity on `Images/`, `input/*/data/`, `input/*/mock_data/*/file_blobs/`.
5. Mock-stack image (`kensei3-mocks:v1`) eager build.
6. `tasks/` HF dataset clone (`--depth 1` from `$HF_TASKS_REPO`).
7. **Opt-in** overlay CSV validation across `input/*/mock_data/`.

**Flags:**

| Flag | Purpose |
| --- | --- |
| `-h`, `--help` | Print usage and exit `0`. |
| `--skip-image-check` | Skip step 4 (LFS sanity). |
| `--skip-mocks` | Skip step 5 (mock-stack image build). |
| `--skip-tasks` | Skip step 6 (HF `tasks/` clone). |
| `--validate-overlays` | Enable step 7 (overlay CSV shape check). |
| `--strict` | Treat overlay warnings as fatal (combined with `--validate-overlays`). |

**Exit codes:** `0` success, `1` fatal step failure, `2` invalid argument.

**Env vars read:** `HF_TASKS_REPO`, `NO_COLOR`, `EUID`.

**Examples:**
```bash
bash script/prepare.sh                       # full bootstrap
bash script/prepare.sh --skip-image-check
bash script/prepare.sh --skip-mocks --skip-tasks
bash script/prepare.sh --validate-overlays --strict
```

---

### 1.3 `script/run.sh` — end-to-end eval runner

**Path:** `script/run.sh`
**Purpose:** The heavyweight orchestration wrapper around `eval/run_batch.py`. Handles docker preflight, image loading, leaked-network cleanup, single-task or bulk K-run loops, one automatic docker-error retry, aggregation, and the Kensei TUI. Always `cd`s to repo root regardless of invocation cwd.

**Preflight stages (in order):**

1. Docker CLI + daemon.
2. Agent image `wildclawbench-ubuntu:v1.3` (loads from `Images/wildclawbench-ubuntu_v1.3.tar` via `pv` if missing).
3. Mock image `kensei3-mocks:v1` (builds via `src.utils.mock_stack` if missing).
4. `.env` sanity (warns on missing `KENSEI_AWS_BEARER_TOKEN` / `KENSEI_AWS_REGION`).
5. Orphan cleanup (`ll-*`, `mocks-*`, `t_*` containers, `k3net-*` networks). Skipped if a peer `run.sh` is alive.

**Mode-selecting flags** (mutually exclusive; exactly one active per invocation):

- `--task` / positional `TASK` → **single** mode.
- `-A`, `--all-input` → **all-input** mode.
- `-B`, `--bulk <FILE>` → **bulk** mode.
- `-R`, `--regrade <DIR>` → **regrade** mode (short-circuits everything else; re-runs only the judge).

**Common flags:**

| Flag | Arg | Purpose |
| --- | --- | --- |
| `-h`, `--help` | — | Print help and exit `0`. |
| `-t`, `--task` | `PATH` | Task directory (repeatable). |
| `-m`, `--model`, `--models` | `NAME[,NAME...]` | Comma list; models run in parallel per task. |
| `-k`, `--reps`, `--k` | `N` | Repetitions per (task, model). Sequential by default. |
| `-B`, `--bulk` | `FILE` | Read tasks from file (one per line, `#` comments/blanks stripped). |
| `-A`, `--all-input` | — | Every immediate subdir of `input/` becomes a task. |
| `-R`, `--regrade` | `DIR` | Re-run judge phase only on an existing run dir. |
| `--rubric` | `PATH` | Override rubric for `--regrade`. |

**Feature-toggle flags:**

| Flag | Arg | Purpose |
| --- | --- | --- |
| `--backend` | `NAME` | Agent backend (default `openclaw`). Forwarded as `--agent-backend`. |
| `--thinking` | `LEVEL` | Thinking budget (default `xhigh`; e.g. `medium`, `high`, `xhigh`). |
| `--provider` | `auto\|bedrock\|anthropic\|vertex` | LiteLLM upstream provider for opus/sonnet aliases. `auto` = env-detect. |
| `--gcp`, `--vertex` | — | Shortcut for `--provider vertex`. |
| `--vertex-project` | `ID` | Override GCP project. |
| `--vertex-location` | `REGION` | Override Vertex region (default `us-east5`). |
| `--vertex-credentials` | `PATH` | Path to GCP SA JSON. |
| `--no-judge-council` | — | Disable `--judge-council` (faster, single-judge). |
| `--no-tests` | — | Disable `--generate-tests`/`--execute-tests`. |
| `--no-litellm` | — | Disable LiteLLM sidecar (direct Bedrock). |
| `--no-mock-stack` | — | Disable mock-stack docker fleet. |
| `--no-bundle` | — | Skip auto-repackage to `output_bundle/` after each task. |
| `--bundle-root` | `DIR` | Destination for auto-bundle (default `output_bundle`; env `KENSEI_BUNDLE_ROOT`). |
| `--parallel-reps` | — | Run all K reps of a (task, model) concurrently. |
| `--no-tui` | — | Skip the Kensei live TUI. |
| `--skip-preflight` | — | Skip docker/image/mock/.env checks (dangerous). |
| `--` | — | End of options; remaining args are positional. |

**Legacy positional shortcut:** `bash script/run.sh [TASK] [MODEL[,MODEL2,...]] [K]`, with defaults `TASK=input/alden-croft_MB`, `MODEL=claude-opus-4.7`, `K=1`.

**Env vars read:** `KENSEI_BUNDLE_ROOT`, `KENSEI_NO_TUI`, `KENSEI_HOLD_TUI`, `KENSEI_QUIT_SENTINEL` (exported for the TUI), `WCB_QUIET`, `NO_COLOR`, `TMPDIR`, `KENSEI_AWS_BEARER_TOKEN`, `KENSEI_AWS_REGION`.

**Notable behavior:**
- Logs at `logs/<task>_<model>_run<i>_<TS>.log`.
- Tasks always sequential; models parallel per task; reps sequential (or concurrent with `--parallel-reps`).
- One automatic docker-recoverable retry per run.
- Post-batch invokes `python3 script/aggregate_runs.py --backend <BACKEND>` if `K > 1` or multi-task/multi-model.
- Post-task auto-bundle to `--bundle-root` unless `--no-bundle`.
- Regrade path delegates to `python3 script/regrade.py --run <dir> [--rubric <path>]`.

**Examples:**
```bash
bash script/run.sh                                                         # defaults
bash script/run.sh --task input/amanda_hayes_01 --model claude-opus-4.7
bash script/run.sh --model claude-opus-4.7,claude-sonnet-4.5 --reps 3      # 2 models × K=3 parallel
bash script/run.sh --task input/amanda_hayes_01 --reps 2 --parallel-reps
bash script/run.sh --bulk tasks.txt --model claude-opus-4.7 --reps 2
bash script/run.sh --all-input --model claude-opus-4.7
bash script/run.sh --regrade output/openclaw/amanda_hayes_01/trajectories/claude-opus-4.7/run_1
bash script/run.sh --provider vertex --vertex-project my-gcp-proj --model claude-opus-4.7
```

---

### 1.4 `script/lib/log.sh` — shared UX library (sourced only)

**Path:** `script/lib/log.sh`
**Purpose:** Shared shell-UX library sourced by `run.sh`, `prepare.sh`, and `deliver.sh`. Uniform colors, banners, progress bars, and summary boxes across TTY / pipe / file sinks. Respects `NO_COLOR` and `WCB_QUIET`.

**Not an executable — no CLI flags.** Public functions:

| Function | Purpose |
| --- | --- |
| `log::info <msg>` | Cyan `[INFO]` line. |
| `log::ok <msg>` | Green `[OK]` line. |
| `log::warn <msg>` | Yellow `[WARN]` line (stderr). |
| `log::err <msg>` | Red `[ERR]` line (stderr). |
| `log::die <msg>` | `log::err` then `exit 1`. |
| `log::hint <msg>` | Dim indented secondary line. |
| `log::kv <key> <value>` | Aligned `Key : Value`. |
| `log::rule [<title>]` | Horizontal rule with optional title. |
| `log::section <title>` | Full-width blue banner. |
| `log::step <n> <total> <title>` | `▶ [n/total] title` step marker. |
| `log::substep <title>` | Indented `↳ title`. |
| `log::progress <cur> <total> [<label>]` | Progress bar (TTY-aware). |
| `log::summary_box <title> "Key=Val"...` | Rendered summary box. |

**Back-compat aliases:** `info`, `ok`, `warn`, `err`, `die`.

**Env vars:** `NO_COLOR`, `WCB_QUIET`, `TERM`, `COLUMNS`, `__WCB_LOG_SH_SOURCED` (internal guard).

---

## 2. The integrated benchmark CLI (`eval/run_batch.py`)

**Path:** `eval/run_batch.py`
**Argument definitions:** `src/utils/cli_args.py` (`build_run_batch_parser`, `parse_run_batch_args`).
**Invocation:**
```bash
python eval/run_batch.py <flags>
# — or —
bash script/run.sh --task ... [flags]     # which shells out to run_batch.py
```

Single canonical benchmark entry point. Everything else in the repo either wraps this (`script/run.sh`), pre-flights for it (`script/prepare.sh`), or post-processes what it produced (`aggregate_runs.py`, `repackage_to_bundle.py`, `regrade.py`, ...).

### 2.1 Task selection (required, mutually exclusive)

Exactly one of:

| Flag | Arg | Purpose |
| --- | --- | --- |
| `-t`, `--task` | `<PATH>` | Path to a single `task.md` file. |
| `-c`, `--category` | `<NAME>` | Category (`01_Productivity_Flow`, `02_Code_Intelligence`, `03_Social_Interaction`, `04_Search_Retrieval`, `05_Creative_Synthesis`, `06_Safety_Alignment`). |

### 2.2 Top-level flags

| Flag | Arg | Default | Purpose |
| --- | --- | --- | --- |
| `--agent-backend` | `openclaw\|claudecode\|codex\|hermesagent` | `openclaw` | Agent backend implementation. |
| `-m`, `--model` | `<NAME>` | env `DEFAULT_MODEL` or `openrouter/anthropic/claude-sonnet-4.6` | Model id. |
| `-p`, `--parallel` | `N` | env `DEFAULT_PARALLEL` or `1` | Number of parallel containers. |
| `--lobster-name` | `<STR>` | `None` | Lobster name (used in output dir). |
| `--lobster-workspace` | `<PATH>` | `None` | Personal OpenClaw workspace path (SOUL.md, USER.md, ...). |
| `--lobster-env` | `<CSV>` | `None` | Comma-separated env-var names to pass through (e.g. `GEMINI_API_KEY,FIRECRAWL_API_KEY`). |
| `--models-config` | `<PATH>` | `None` | JSON file to replace the top-level `models` field in `~/.openclaw/openclaw.json` before each task. |
| `--thinking` | `<LEVEL>` | `xhigh` | Reasoning level (`agents.defaults.thinkingDefault`). Use `off` to disable. |
| `--openclaw-image-model` | `<NAME>` | `None` | Optional OpenClaw image tool model (falls back to `--model`). |

### 2.3 LiteLLM / Bedrock routing (openclaw backend)

Mutually exclusive pair on `dest=litellm`:

| Flag | Purpose |
| --- | --- |
| `--litellm` | Force LiteLLM sidecar routing. |
| `--no-litellm` | Force OpenRouter routing even if Bedrock/OpenAI env is set. |

Plus:

| Flag | Arg | Default | Purpose |
| --- | --- | --- | --- |
| `--bedrock-arn` | `<ARN>` | env `BEDROCK_MODEL_ARN` | Override Bedrock inference-profile ARN. |
| `--aws-region` | `<REGION>` | env `AWS_REGION` or `ap-south-1` | Override AWS region for Bedrock. |
| `--provider` | `auto\|bedrock\|anthropic\|vertex` | `auto` | LiteLLM upstream for Claude opus/sonnet aliases. |
| `--vertex-project` | `<ID>` | env `VERTEX_PROJECT`/`VERTEXAI_PROJECT` | Required when `--provider=vertex`. |
| `--vertex-location` | `<REGION>` | env `VERTEXAI_LOCATION` or `us-east5` | Override Vertex region. |
| `--vertex-credentials` | `<PATH>` | env `GOOGLE_APPLICATION_CREDENTIALS` | GCP SA JSON path. Falls back to gcloud ADC. |
| `--mock-stack` | — | off | Run all required mock APIs in one shared container. |

### 2.4 Test generation

Mutually exclusive pair on `dest=generate_tests`:

| Flag | Purpose |
| --- | --- |
| `--generate-tests` | Run kensei2 test generation via Bedrock before the agent runs. Default: auto-enabled when Bedrock env is present. |
| `--no-generate-tests` | Skip test generation even when Bedrock env is present. |

Plus:

| Flag | Arg | Default | Purpose |
| --- | --- | --- | --- |
| `--testgen-max-attempts` | `N` | `3` | Max LLM retries for the testgen lint loop. |
| `--force-testgen` | — | off | Bypass the on-disk testgen cache and regenerate. |

### 2.5 Test execution

Mutually exclusive pair on `dest=execute_tests`:

| Flag | Purpose |
| --- | --- |
| `--execute-tests` | After the agent finishes, run generated tests to compute real reward + ctrf. Auto-on when `--generate-tests` and `--mock-stack` are both on. |
| `--no-execute-tests` | Skip test execution (rubric judge only). |

Plus:

| Flag | Arg | Default | Purpose |
| --- | --- | --- | --- |
| `--testexec-timeout` | `SEC` | `600` | Outer cap on the test runner subprocess. |
| `--rebuild-mocks` | — | off | Force-rebuild the mock-API image even if cached. |

### 2.6 Judge council

Two flags share `dest=judge_council`:

| Flag | Purpose |
| --- | --- |
| `--judge-council` | Use a 3-judge council (Sonnet 4.6 + GLM 5 + Kimi k2.5). Aggregates by per-criterion mean; quorum of 2. Equivalent to `JUDGE_COUNCIL=1`. |
| `--no-judge-council` | Force-disable even if `JUDGE_COUNCIL=1` in env. |

### 2.7 Env-var contract (read by the harness at runtime)

Runtime env-var → dataclass mapping is in `src/utils/config.py::Config.from_env()`. First non-empty alias wins per field.

| Config field | Aliases (in priority order) | Default |
| --- | --- | --- |
| `bedrock_inference_arn` | `KENSEI_BEDROCK_MODEL_ARN`, `KENSEI2_BEDROCK_MODEL_ARN`, `BEDROCK_MODEL_ARN` | `""` |
| `bedrock_sonnet_arn` | `KENSEI_BEDROCK_SONNET_ARN`, `BEDROCK_SONNET_ARN` | `""` |
| `bedrock_region` | `KENSEI_AWS_REGION`, `AWS_REGION` | `ap-south-1` |
| `aws_bearer_token` | `KENSEI_AWS_BEARER_TOKEN`, `AWS_BEARER_TOKEN_BEDROCK` | `""` |
| `s3_bucket` | `S3_BUCKET` | `""` |
| `s3_prefix` | `S3_PREFIX` | `WildClaw` |
| `s3_region` | `S3_REGION` | `us-east-1` |
| `s3_access_key_id` | `KENSEI_S3_ACCESS_KEY_ID`, `AWS_ACCESS_KEY_ID` | `""` |
| `s3_secret_access_key` | `KENSEI_S3_SECRET_ACCESS_KEY`, `AWS_SECRET_ACCESS_KEY` | `""` |
| `openai_api_key` | `KENSEI_OPENAI_API_KEY`, `OPENAI_API_KEY` | `""` |
| `openai_whisper_api_key` | `KENSEI_OPENAI_WHISPER_API_KEY`, `OPENAI_WHISPER_API_KEY` | `""` |
| `anthropic_api_key` | `KENSEI_ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY` | `""` |
| `vertex_project` | `KENSEI_VERTEX_PROJECT`, `VERTEXAI_PROJECT`, `VERTEX_PROJECT` | `""` |
| `vertex_location` | `KENSEI_VERTEX_LOCATION`, `VERTEXAI_LOCATION`, `VERTEX_LOCATION` | `us-east5` |
| `vertex_credentials` | `KENSEI_VERTEX_CREDENTIALS`, `GOOGLE_APPLICATION_CREDENTIALS` | `""` |
| `openrouter_api_key` | `OPENROUTER_API_KEY` | `""` |
| `openrouter_base_url` | `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |
| `brave_api_key` | `BRAVE_API_KEY` | `placeholder` |
| `docker_image` | `DOCKER_IMAGE` | `wildclawbench-ubuntu:v1.3` |
| `tmp_workspace` | `TMP_WORKSPACE` | `/tmp_workspace` |
| `gateway_port` | `GATEWAY_PORT` | `18789` |
| `upload_media_to_s3` | `UPLOAD_MEDIA_TO_S3` (bool) | `false` |
| `wildclaw_skills_dir` | `WILDCLAW_SKILLS_DIR` | `<repo>/environment/skills` |
| `default_skills` | `WILDCLAW_DEFAULT_SKILLS`, `KENSEI3_DEFAULT_SKILLS` | `video-frames,pdf-extract,audio-extract` |
| `litellm_master_key` | `KENSEI_LITELLM_MASTER_KEY`, `KENSEI3_LITELLM_MASTER_KEY`, `LITELLM_MASTER_KEY` | `sk-talos-litellm` |
| `litellm_port` | `KENSEI3_LITELLM_PORT`, `LITELLM_PORT` | `4000` |
| `min_harbor_score` | `MIN_HARBOR_SCORE` | `None` |

Additional runtime env-vars:
- Judge council: `JUDGE_MODEL`, `JUDGE_COUNCIL`, `JUDGE_COUNCIL_MEMBERS`.
- Test executor: `WCB_PER_TEST_TIMEOUT` (default `30` s per test).
- Codex backend: `DOCKER_IMAGE_CODEX`, `OPENROUTER_IMAGE_MODEL`, `WILDCLAW_IMAGE_MODEL`, `HTTP_PROXY_INNER`, `HTTPS_PROXY_INNER`, `NO_PROXY_INNER`, `CODEX_REASONING_EFFORT`, `CODEX_WIRE_API`, `WILDCLAW_IMAGE_HELPER_CALL_LIMIT`.
- Hermes backend: `HERMES_DOCKER_IMAGE`.

### 2.8 Not a real CLI: in-container helpers

Two files under `src/agents/hermesagent/` look like scripts but take **no CLI flags** — they are piped over stdin into a Python interpreter inside a running Docker container by the Hermes runner:

| File | How it's invoked |
| --- | --- |
| `src/agents/hermesagent/bench_runner.py` | `docker exec -i <task_id> /opt/hermes/.venv/bin/python3 -` with stdin=this file. Reads `/tmp/hermes_bench_config.json`. |
| `src/agents/hermesagent/compat_transcript.py` | Same pattern. Merges Hermes session logs into `chat.jsonl` for the harness-agnostic grader. |

`src/agents/codex/runner.py` contains an embedded `if __name__ == "__main__":` **inside a string literal** — that string is written into the container as `/tmp_workspace/.wildclaw_image.py`. It is not a real host-side CLI on the codex runner.

---

## 3. Standalone Python utilities in `script/`

All paths below are relative to `script/`.

### 3.1 `aggregate_runs.py`

**Purpose:** Aggregates `score.json` files produced by `eval/run_batch.py` into per-(model, task) and per-model rollups. Implements the "average rubric weights percentage" reward. Also computes per-task `pass@K` (best-of-K) and per-model `average_pass_at_k`. Walks the layout `output/<backend>/<task_id>/trajectories/<model>/run_N/score.json`. Writes an aggregate JSON summary and optionally prints a stdout table. Called automatically by `script/run.sh` when `K > 1` or multi-task/multi-model.

**CLI library:** argparse.

| Flag | Type | Default | Purpose |
| --- | --- | --- | --- |
| `--output-root` | str | `output` | Harness output directory. |
| `--backend` | str | `None` | Filter to a single backend dir name (e.g. `openclaw`). |
| `--write` | str | `<output-root>/<backend|all>_aggregate_summary.json` | Write summary JSON to this path. |
| `--json-only` | flag | `False` | Suppress stdout table, only write JSON. |

**Examples:**
```bash
python3 script/aggregate_runs.py
python3 script/aggregate_runs.py --backend openclaw
python3 script/aggregate_runs.py --json-only
```

---

### 3.2 `backfill_connector_docs.py`

**Purpose:** Backfills richer `references/` and `scripts/` documentation for the "thin" mock-API connectors under `environment/skills/<name>-api-connector/`. There are two connector shapes: 10 "RICH" curated (never touched), and 91 "THIN" (`SKILL.md`-only). This tool parses each THIN connector's endpoint table plus its sibling `environment/<name>-api/service.toml` and emits `references/<name>-api-guide.md` (curl examples grouped by resource) and `scripts/fetch_<name>_data.py` (a stdlib-only argparse CLI with one flag per GET/POST/DELETE endpoint). Idempotent (skips connectors that already have `references/`). Has an "enrich mode" (`--bundle-root`) that copies `references/` + `scripts/` from the live tree into every connector dir inside an already-built bundle.

**CLI library:** argparse.

| Flag | Type | Default | Purpose |
| --- | --- | --- | --- |
| `--skills-root` | str | `environment/skills` | Dir holding `<name>-api-connector/`. |
| `--env-root` | str | `environment` | Dir holding `<name>-api/service.toml`. |
| `--only` | CSV | `""` | Restrict to these API names (e.g. `gmail,outlook`). |
| `--force` | flag | `False` | Regenerate even if `references/` already exists. |
| `--include-rich` | flag | `False` | Also regenerate the 10 curated connectors (not recommended). |
| `--bundle-root` | str | `""` | Enrich mode: copy live docs into an already-built bundle. |
| `--dry-run` | flag | `False` | List what would be written; write nothing. |
| `-v`, `--verbose` | flag | `False` | Verbose logging. |

---

### 3.3 `coerce_dryrun.py`

**Purpose:** Replicates the per-task overlay-CSV ingestion **without containers**. For each task under `input/`, copies `environment/` to a temp tree, overlays `mock_data/<api>/*.csv` exactly as the read-only bind mount would at runtime, then imports each overlaid `<api>_data.py` so its `_store.eager_load()` runs the real coercion. Reports `CoerceError` (or any import failure) per API. Exits non-zero if any overlay fails to load.

**CLI library:** argparse.

| Positional | nargs | Purpose |
| --- | --- | --- |
| `task` | optional | Single task name under `input/`. Omit to check all tracked tasks. |

**Examples:**
```bash
python3 script/coerce_dryrun.py                        # all tasks
python3 script/coerce_dryrun.py amanda_hayes_01        # single task
```

---

### 3.4 `coerce_malformed_test.py`

**Purpose:** Container-free unit-style verification that `read_csv_with_ctx` + `strict_*` helpers correctly raise `CoerceError` on each malformed-CSV class (ragged rows, duplicate headers, non-UTF-8 bytes). Empty and header-only files must yield empty tables; short rows defer to per-field helpers. Writes fixture CSVs into a temp dir, runs each check, prints `OK`/`FAIL` per case, and exits non-zero on any failure.

**No CLI arguments.** Run with:

```bash
python3 script/coerce_malformed_test.py
```

---

### 3.5 `extract_home_to_data.py`

**Purpose:** Flattens a task's `persona/home/` tree into a flat `data/` folder at the task root. Every file under `persona/home/**` is copied into `<task>/data/`. On basename collision the later file is renamed using its source-relative path with separators turned into `__` (e.g. `Library/README.md` → `Library__README.md`). Stdlib-only, no pipeline imports, safe to re-run.

**CLI library:** argparse.

| Positional | nargs | Purpose |
| --- | --- | --- |
| `task_dir` | `+` (one or more) | Task directories (each containing `persona/home/`). |

| Flag | Purpose |
| --- | --- |
| `--no-clean` | Do not wipe existing `data/` first; append into it. |
| `--dry-run` | Show what would be copied without writing. |
| `-v`, `--verbose` | List every file copied. |
| `--delete-home` | Delete `persona/home/` after a successful extraction (destructive). |

**Example:**
```bash
python3 script/extract_home_to_data.py input/alden-croft_MB --verbose
```

---

### 3.6 `kensei_tui.py`

**Purpose:** The Kensei TUI — a Textual-based live dashboard for `bash script/run.sh …`. Launched by `run.sh` as a sibling process. Reads a `plan.json` describing the batch plus per-run log files and `output/<backend>/<task>/trajectories/<model>/run_N/` artifacts (`score.json`, `ctrf.json`, `usage.json`, `mock_health.jsonl`). Tabs: Overview (with progress + live log), Rubric, Tests, Usage, Judge, Mock Health. Falls back to a no-op sleep loop when stdout is not a TTY or when `KENSEI_NO_TUI=1`. Pressing `q`/`Esc`/`Ctrl+C`/`Ctrl+Q` writes `$KENSEI_QUIT_SENTINEL` so `run.sh`'s INT trap can tear down docker/LiteLLM/mocks.

**CLI library:** argparse.

| Flag | Type | Default | Required | Purpose |
| --- | --- | --- | --- | --- |
| `--plan` | Path | — | **Yes** | Path to `plan.json` emitted by `script/run.sh`. |
| `--watch` | Path | `logs` | No | Bash log directory. Overridable via `KENSEI_LOG_DIR`. |
| `--no-tui` | flag | `False` | No | Force plain no-op fallback. |

**Env vars:** `KENSEI_NO_TUI`, `KENSEI_LOG_DIR`, `KENSEI_QUIT_SENTINEL`.

---

### 3.7 `migrate_to_drift_plane.py`

**Purpose:** Mechanical migration of `<api>_data.py` + `server.py` to the "drift plane" (mutable store) architecture. Parses each data module with regex, rewrites CSV/JSON eager-loads and shadow-copy `_store` variables into `_store.register(...)` calls + `_xxx_rows()`/`_xxx_doc()` accessor helpers, and injects `install_admin_plane(app, store=<mod>._store)` into `server.py`. Skips already-migrated modules and a hard-coded list of idiosyncratic ones (algolia, quickbooks, youtube, ring). PK heuristics with per-api / per-table overrides. **Dry-run by default; `--apply` writes changes.**

**CLI library:** argparse.

| Flag | Type | Default | Purpose |
| --- | --- | --- | --- |
| `--apply` | flag | `False` | Write changes to disk. Without it, prints the plan only. |
| `--only` | list | `None` | Limit to these API dirs. |

> Note: the docstring mentions "run with `--dry-run` first", but there is no `--dry-run` flag — dry-run is simply the *default* when `--apply` is omitted.

---

### 3.8 `reconstruct_input_from_bundle.py`

**Purpose:** Reverses the bundle writer — reconstructs an `input/<task>/` folder from a harbor `output_bundle`. Recovers `prompt.txt` (fallback `data/instruction.md`), `rubric.json`, `persona/`, flat `data/` (from `data/environment/artifacts/inputs/files/`), `test_outputs.py`, `test_weights.json`, and `mock_data/<api>/` (by byte-diffing each `.json`/`.csv` seed against a pristine baseline `environment/<api>/<f>` — identical files are baked defaults, differences/new files are the task overlay). Writes a `RECONSTRUCTION_NOTES.md` per task documenting recovery. Cannot recover `gt/`, original nested directory structure, or the pre-overlay default a given overlay replaced.

**CLI library:** argparse.

| Positional | Type | Purpose |
| --- | --- | --- |
| `bundle_path` | Path | An `output_bundle` task dir OR a root containing several. |

| Flag | Type | Default | Purpose |
| --- | --- | --- | --- |
| `--out` | Path | `reconstructed_input` | Output root; each task lands in `<out>/<task>/`. |
| `--baseline-env` | Path | `<repo>/environment` | Pristine harness `environment/` for overlay diffing. |
| `-v`, `--verbose` | flag | `False` | Verbose logging. |

---

### 3.9 `regrade.py`

**Purpose:** Re-runs **only the judge phase** against an existing completed run dir, using the rubric currently at `input/<task>/rubric.json`. Overwrites the run's `score.json` in place. Does NOT re-run the agent, testgen, or testexec. Council mode only. Also patches `usage.json` to reflect the new judge cost while preserving other keys. Called by `script/run.sh --regrade`.

**CLI library:** argparse.

| Flag | Type | Default | Required | Purpose |
| --- | --- | --- | --- | --- |
| `--run` | str | — | **Yes** | Path to run dir (`output/<backend>/<task>/trajectories/<model>/run_N`). |
| `--rubric` | str | `None` | No | Override rubric path (default: `input/<task>/rubric.json`). |
| `--quiet` | flag | `False` | No | Suppress final summary table. |

**Example:**
```bash
python3 script/regrade.py --run output/openclaw/amanda_hayes_01/trajectories/claude-opus-4.7/run_1
```

---

### 3.10 `repackage_to_bundle.py`

**Purpose:** Standalone repackager — raw run output → published "bundle" structure matching the `amanda_webb_01` reference layout: `prompt.txt`, `rubric.json`, `data/`, and `trajectories/<Pretty Model>/run_N/` containing `output.json`, `logs/verifier/`, `report.json`, and `output_media/`. Also stages `persona/`, input artifacts, and harness-runtime env files. Matches source task dirs against destination bundles by "persona core name" (strip emoji, drop uuid/hex/numeric suffix tokens, collapse separators). Called automatically by `script/run.sh` per task unless `--no-bundle`.

**CLI library:** argparse.

| Flag | Type | Default | Required | Purpose |
| --- | --- | --- | --- | --- |
| `--source-root` | str | `output/openclaw` | No | Root containing raw `<task_id>/` dirs. |
| `--dest-root` | str | — | **Yes** | Destination root (created if absent). |
| `--input-root` | str | `input` | No | Root of original task input dirs. |
| `--persona` | str | — | **One-of** | Persona core name (fuzzy-matched, e.g. `"ben cox"`). |
| `--all` | flag | — | **One-of** | Convert every task under `--source-root`. |
| `--infer-rubric-meta` | flag | `False` | No | Heuristically fill rubric `type`/`evaluation_target`. |
| `-v`, `--verbose` | flag | `False` | No | Per-run detail. |

`--persona` and `--all` form a mutually-exclusive required group.

---

### 3.11 `rerun_tests.py`

**Purpose:** Re-executes **only the test suite** (testexec phase) against an already-completed trajectory — no agent re-run, no testgen, no LLM judge. Mirrors `eval/run_batch.py`'s `--execute-tests` step by reusing `src.utils.test_executor.execute_tests`. Mounts a run's `task_output/workspace_full` read-only into a throwaway docker container, runs the task's `test_outputs.py` + `test_weights.json`, then rewrites the run's verifier artifacts (`reward.txt`, `ctrf.json`, `test_function_outputs.json`, `test_output.log`) plus a standalone `regrade_test_result.json`. Leaves `score.json` untouched. For faithful audit-based tests, requires pointing at a live mock stack via `--network` + env vars.

**CLI library:** argparse.

| Flag | Type | Default | Required | Purpose |
| --- | --- | --- | --- | --- |
| `--run` | str | — | **One-of** | A single run dir. |
| `--task` | str | — | **One-of** | A task dir; re-grades all its runs. |
| `--latest` | flag | `False` | No | With `--task`, only the highest `run_N` per model. |
| `--network` | str | `None` | No | Docker network of a RUNNING mock stack (for `audit/*` tests). |
| `--env-json` | str | `None` | No | JSON of `{<SVC>_URL: http://host:port}` for the mock stack. |
| `--env` | list (`append`) | `[]` | No | Extra `SVC_URL=...` env var (repeatable). |
| `--image` | str | `wildclawbench-ubuntu:v1.3` | No | Runner image. |
| `--timeout` | int | `600` | No | Outer testexec timeout (seconds). |

`--run` and `--task` form a mutually-exclusive required group.

**Examples:**
```bash
python3 script/rerun_tests.py --run output/openclaw/amanda_hayes_01/trajectories/claude/run_1
python3 script/rerun_tests.py --run <run_dir> --network wildclawbench-mocknet --env-json mock_env.json
python3 script/rerun_tests.py --task output/openclaw/amanda_hayes_01
```

---

### 3.12 `verify_applied.py`

**Purpose:** Verifies that already-migrated data modules (those containing the `from _mutable_store import get_store` marker) can be imported cleanly against the live `environment/` tree, that `_store.list_tables()` and `_store.list_documents()` succeed, and that every registered table's `.rows()` and every document's `.get()` return without exception. Prints `OK`/`FAIL` per API and a totals line; exits non-zero on any failure.

**No CLI arguments.** Run with:

```bash
python3 script/verify_applied.py
```

> Known caveat: this file `sys.path.insert(0, REPO_ROOT / "scripts")` (plural) to import `migrate_to_drift_plane`, while the containing directory is `script/` (singular). The import will fail unless the plural path also exists.

---

### 3.13 `verify_migration_dryrun.py`

**Purpose:** Verifies the migration script produces importable code **without** writing to the live tree. For every non-skipped API (skipping `ALREADY_DONE | IDIOSYNCRATIC`), it calls `plan_module`/`apply_data_module`/`apply_server` from `migrate_to_drift_plane`, writes the generated code to a temp copy of the API dir, then attempts to `importlib.import_module` both, queries `_store.list_tables()`/`.list_documents()`, calls `.rows()`/`.get()` on each, and verifies `server.app` exists. Reports `OK`/`FAIL` per API plus a totals line and failures list; exits non-zero on any failure.

**No CLI arguments.** Run with:

```bash
python3 script/verify_migration_dryrun.py
```

> Same `scripts/` (plural) import-path caveat as `verify_applied.py`.

---

### 3.14 `rebuild_pass_summary.py`

**Purpose:** Rebuild a `pass_summary.json` from the per-rep artifacts (`run_N/score.json` + `run_N/task_output/logs/verifier/{ctrf.json,reward.txt}`) already sitting under a `trajectories/<model>/` folder. This is a **byte-for-byte faithful** reimplementation of the harness's `_pass_summary_doc()` + `_pass_summary_entry()` pipeline from `eval/run_batch.py` — same keys, same order, same rounding, same `_finite_float` semantics, same `None`-tolerant means. **The output is indistinguishable from what the harness itself would have written if all N reps had run in a single batch.** No extra keys, no `merged_from`, no `pass_at_k_*`.

Use this when reps for the same task were produced in separate places (e.g. 1 verification rep + 7 bulk reps) and you need one consolidated `pass_summary.json` covering all of them. Auto-discovers `run_1, run_2, ..., run_N` under the given model dir.

**CLI library:** argparse.

| Flag | Type | Default | Required | Purpose |
| --- | --- | --- | --- | --- |
| `model_dir` (positional) | Path | — | **Yes** | Path to `trajectories/<model>/` containing `run_1, run_2, ..., run_N/`. |
| `--model` | str | `<model_dir.name>` | No | Override the `model` field. Defaults to the model dir basename. |
| `-o`, `--output` | str | `<model_dir>/pass_summary_new.json` | **One-of** | Output path. Use `-` for stdout. |
| `--in-place` | flag | `False` | **One-of** | Overwrite `<model_dir>/pass_summary.json` in place. |
| `--indent` | int | `2` | No | JSON indent. |

`--output` and `--in-place` are mutually exclusive.

**Examples:**

```bash
# Default: writes trajectories/<model>/pass_summary_new.json alongside the existing one
python3 script/rebuild_pass_summary.py output/openclaw/<task>/trajectories/claude

# Overwrite pass_summary.json in place with the recomputed doc
python3 script/rebuild_pass_summary.py output/openclaw/<task>/trajectories/claude --in-place

# Write to a specific location
python3 script/rebuild_pass_summary.py output/openclaw/<task>/trajectories/claude -o /tmp/rebuilt.json

# Print to stdout
python3 script/rebuild_pass_summary.py output/openclaw/<task>/trajectories/claude -o -

# Point at a path with spaces (quote it)
python3 script/rebuild_pass_summary.py "/path with spaces/trajectories/claude"
```

**Verified byte-equivalent** against real harness output for barbara-kidd (1 rep), brandon-wright (1 rep), darren_weston (1 rep), and matt_garcia (3 reps) — the recomputed file `diff -q` cleanly against the harness-produced `pass_summary.json`.

---

## 4. Skill-embedded scripts

These are utility shell scripts shipped inside individual agent-skill packages. They are not part of the top-level pipeline but are documented for completeness.

### 4.1 `environment/skills/video-frames/scripts/frame.sh`

**Purpose:** Extract a single frame from a video file using `ffmpeg` (by timestamp, by frame index, or the first frame). Prints the output path on success.

| Arg | Purpose |
| --- | --- |
| `<video-file>` (positional) | Input video. Required. |
| `-h`, `--help` | Print usage and exit `2`. |
| `--time HH:MM:SS` | Seek to timestamp and grab one frame. |
| `--index N` | Extract frame at 0-based index N. |
| `--out /path/to/frame.jpg` | Output image path. **Required.** Parent dir auto-created. |

If neither `--time` nor `--index` is given, extracts frame 0.

### 4.2 `environment/skills/self-improving-agent-3.0.5/scripts/error-detector.sh`

**Purpose:** PostToolUse hook. Reads `$CLAUDE_TOOL_OUTPUT` and, if any error pattern matches, emits an `<error-detected>` reminder XML block suggesting the agent log a learning entry to `.learnings/ERRORS.md` using format `[ERR-YYYYMMDD-XXX]`.
**No CLI args.** Env var: `CLAUDE_TOOL_OUTPUT`.

### 4.3 `environment/skills/self-improving-agent-3.0.5/scripts/extract-skill.sh`

**Purpose:** Skill Extraction Helper — scaffolds a new skill under `./skills/<name>/` with a templated `SKILL.md`. Enforces slug format (lowercase/digits/hyphens) and prevents writes outside the current directory.

| Arg | Purpose |
| --- | --- |
| `<skill-name>` (positional) | Slug. Must match `^[a-z0-9]+(-[a-z0-9]+)*$`. Required. |
| `--dry-run` | Show what would be created; write nothing. |
| `--output-dir <PATH>` | Relative output dir (default `./skills`). Absolute paths and `..` components rejected. |
| `-h`, `--help` | Show help and exit `0`. |

### 4.4 `environment/skills/self-improving-agent-3.0.5/scripts/activator.sh`

**Purpose:** UserPromptSubmit hook. Prints a small `<self-improvement-reminder>` XML block on each user prompt so the model logs extractable knowledge to `.learnings/` after finishing.
**No CLI args, no env vars.**

### 4.5 `environment/skills/audio-extract/scripts/extract.sh`

**Purpose:** Extract a mono 16 kHz WAV audio track from a media file using `ffmpeg`, and/or probe file metadata via `ffprobe`.

| Arg | Purpose |
| --- | --- |
| `--probe <media>` | Probe only — no extraction. Exit `0`. |
| `<media>` (positional #1) | Input media file. Required in default mode. |
| `[out.wav]` (positional #2) | Output WAV path (default `/tmp/audio.wav`). |

### 4.6 `environment/skills/pdf-extract/scripts/extract.py`

**Purpose:** Extract text (and optionally embedded images) from a PDF using PyMuPDF (`fitz`). Ships inside the `pdf-extract` skill, which is one of the three default skills (`Config.default_skills = "video-frames,pdf-extract,audio-extract"`). Text can be streamed to stdout (`--out -`) or a file; embedded images are written as PNGs named `p<page>_x<xref>.png`.

**CLI library:** argparse.

| Arg | Type | Default | Purpose |
| --- | --- | --- | --- |
| `pdf` (positional) | path | — (required) | Input PDF. |
| `--out` | str | `-` | Text output file; `-` = stdout. |
| `--images-dir` | str | `""` (off) | If set, write embedded images to this dir. |
| `--pages` | str | `""` (all) | 1-based inclusive range, e.g. `1-5`. |

**Exit codes:** `0` success · `1` input PDF not found · `2` PyMuPDF not installed.

### 4.7 `environment/skills/audio-extract/scripts/transcribe.sh`

**Purpose:** Transcribe an audio/video file to text via the harness's LiteLLM sidecar (`/v1/audio/transcriptions`). Auto-extracts a 16 kHz mono WAV (unless input is already `.wav`) and POSTs it to the sidecar. Prints transcript on stdout, step markers on stderr.

| Arg | Purpose |
| --- | --- |
| `<media>` (positional #1) | Audio or video input file. Required. |
| `--raw` (positional #2) | Also echo the raw sidecar JSON to stderr. |
| `-h`, `--help` | Print usage and exit `2`. |

**Exit codes:** `0` success · `1` input not found · `2` usage · `3` `WCB_AUDIO_TRANSCRIBE_URL` unset · `4` ffmpeg produced no audio · `5` curl transport error · `6` sidecar non-200 · `7` response missing `text` field.

**Env vars:** `WCB_AUDIO_TRANSCRIBE_URL` (required, injected by the harness), `WCB_AUDIO_TRANSCRIBE_AUTH` (optional bearer token).

### 4.8 Auto-generated per-connector CLIs — 101 `fetch_<name>_data.py`

**Path:** `environment/skills/<name>-api-connector/scripts/fetch_<name>_data.py` (**101 files**, one per mock API).
**Purpose:** Stdlib-only argparse HTTP helpers that expose one flag per REST endpoint of the matching mock API. Each script is regenerated by [`script/backfill_connector_docs.py`](#32-backfill_connector_docspy) from the connector's `SKILL.md` endpoint table plus the sibling `environment/<name>-api/service.toml`. They are the agents' primary way to hit the mock fleet.

Common shape (identical across all 101):

| Arg | Purpose |
| --- | --- |
| `--<method>-<path-with-dashes>` | One flag per endpoint. `store_true` for parameter-less endpoints; `nargs=1` (with `metavar` = path param name) for endpoints with `{placeholder}`s; path params are URL-quoted then substituted in order. |
| `--data <JSON>` | Request body for POST/PUT/PATCH endpoints. |
| `--data-file <PATH>` | Request body loaded from a JSON file. |
| `--url <BASE>` | Override the base URL. Default is `$<NAME>_API_URL` (injected by the harness) or `http://localhost:<port>` from `service.toml`. |

**Exit codes:** `0` success · `1` HTTP error or connection failure.

Because the shape is identical, this document does not enumerate every flag of every connector — instead, use `python3 environment/skills/<name>-api-connector/scripts/fetch_<name>_data.py --help` (or read the connector's `references/<name>-api-guide.md`) to see its per-endpoint flag list.

Example (see the ActiveCampaign connector for a canonical shape):
```bash
python3 environment/skills/activecampaign-api-connector/scripts/fetch_activecampaign_data.py \
    --get-api-3-contacts
python3 environment/skills/activecampaign-api-connector/scripts/fetch_activecampaign_data.py \
    --post-api-3-contacts --data '{"email":"x@y.com"}'
```

---

## 5. Environment fleet tools

Four custom commands live under `environment/` (and `environment/scripts/`) that operate across all 101 mock APIs at once. They are peers of `script/migrate_to_drift_plane.py` but scoped to the mock fleet rather than the eval harness. All are stdlib-only where possible and safe to run against a working tree.

### 5.1 `environment/test_all_apis.py`

**Purpose:** End-to-end smoke harness for the entire mock-API fleet. For every `<name>-api/` that has both a `service.toml` and a `server.py`, it: (1) boots the FastAPI app via `uvicorn` on the port declared in `service.toml`, (2) waits for the healthcheck, (3) fires every request in that env's `*_postman_collection.json` (rewriting the base URL variable to the local port), (4) records HTTP status + response body, (5) shuts the server down. Emits `api_test_report.md` + `api_test_responses.json` (the latter is consumed by `wiring_report.py`).

Result classes per endpoint: `PASS` (2xx/3xx), `WARN` (4xx — deliberate error path or runtime-dependent id), `FAIL` (5xx / connection error / server-didn't-start), `SKIP` (unresolved `{{variable}}`, not sent).

**CLI library:** argparse.

| Flag | Type | Default | Purpose |
| --- | --- | --- | --- |
| `--only` | CSV | `""` | Restrict to these API names. |
| `--skip` | CSV | `""` | Exclude these API names. |
| `--dry-run` | flag | `False` | Parse collections and print a plan; boot no servers. |
| `--install-deps` | flag | `False` | `pip install fastapi==0.115.5 uvicorn==0.32.1` into the current interpreter if missing, then run. |
| `--report` | path | `<env>/api_test_report.md` | Output Markdown path. |
| `--responses` | path | `<env>/api_test_responses.json` | Output JSON path. |

**Exit codes:** `0` if no `FAIL`, `1` if any `FAIL`, `2` if dependency setup failed. `HEALTH_TIMEOUT_S=25`, `REQUEST_TIMEOUT_S=15` are module constants (not flags).

### 5.2 `environment/scripts/audit_data_formats.py`

**Purpose:** Classifies every file inside every `<name>-api/` and confirms the data files are valid JSON in the shape the loaders expect. Enforces two migration-tool conventions: trailing newlines on data files and string-typed cells in seed tables (byte-fidelity contract). Prints per-category counts, hard `FORMAT PROBLEMS` (BAD-JSON / NON-JSON-DATA), and soft style notes.

**CLI library:** argparse.

| Flag | Type | Default | Purpose |
| --- | --- | --- | --- |
| `--only` | CSV | `""` | Comma-separated api-dir names to audit. |
| `--json <PATH>` | str | `None` | Also write a machine-readable JSON report to this path. |

**Exit codes:** `0` if no format problems, `1` otherwise.

### 5.3 `environment/scripts/migrate_csv_to_json.py`

**Purpose:** One-time, reproducible migration of every loaded seed CSV to JSON. Derives the convert-set mechanically: every `"X.csv"`/`"X.json"` literal in each `*_data.py` + every filename listed in a `records_csv` column of any CSV. Writes `<stem>.json` as a JSON array of row objects, then round-trips it via `read_json_with_ctx` and asserts equality with the original CSV rows. Deletes the CSV **only** under `--apply` and only after a successful round-trip. Reports orphan CSVs (present on disk but never loaded) without touching them.

**CLI library:** argparse.

| Flag | Type | Default | Purpose |
| --- | --- | --- | --- |
| `--apply` | flag | `False` | Delete each CSV after its JSON round-trip is verified. Without `--apply`, JSON is written + verified but every CSV is kept (dry-run). |

**Exit codes:** `0` success (all conversions round-tripped), `1` if any file failed to convert (in which case no CSV was deleted for those).

### 5.4 `environment/scripts/wiring_report.py`

**Purpose:** Per-API "does this API actually load the data files sitting on its disk?" report. For each `<name>-api/`, it spawns a subprocess with `builtins.open` and `_mutable_store.read_json_with_ctx/read_csv_with_ctx` instrumented, imports each `*_data.py` and calls `_store.eager_load()`, then records exactly which files were opened. Cross-references the latest `api_test_responses.json` (from `test_all_apis.py`) for endpoint PASS/WARN/FAIL/SKIP counts. Files present but never loaded are flagged as ORPHANs.

**CLI library:** argparse.

| Flag | Type | Default | Purpose |
| --- | --- | --- | --- |
| `--only` | CSV | `""` | Restrict to these API names. |
| `--json <PATH>` | str | `None` | Also write a machine-readable JSON report. |

**Exit codes:** `0` (informational — orphans do not cause a non-zero exit).

### 5.5 `environment/smoke_eager_load.py`

**Purpose:** Cross-fleet eager-load smoke test — imports every `<name>-api/`'s `<name>_data` module (which triggers `_store.eager_load()` inside each) and reports OK/BROKEN per API. Closes the RT-005 gap where static audits missed runtime defects in the loader paths (crashes, coerce-time `KeyError` on missing seed columns, stale data-module renames after `<name>-api` directory renames). Prints per-API status lines plus a `Loaded N/M APIs cleanly` summary and a `BROKEN` list on failure.

**No CLI arguments.** Run from the repo root:

```bash
python3 environment/smoke_eager_load.py
```

**Exit codes:** `0` if every API's data module imports cleanly · `1` if any API is broken · `2` if no `<name>-api/` directories are found under `environment/`.

**Side effects:** temporarily inserts each `<name>-api/` on `sys.path` (removed in a `finally`) and pops `<name>_data` from `sys.modules` before each import so the check is idempotent.

---

## 6. CRUCIBLE audit CLI (`audit/`)

**Path:** `audit/audit.py`
**Package layout:** `audit/pyproject.toml` declares `[project] name = "audit"` and `[project.scripts] audit = "audit:app"`. After `pip install -e audit/`, the command `audit` is on `$PATH`. Direct invocation also works: `python3 audit/audit.py`.
**Purpose:** Standalone deterministic security-audit harness ("CRUCIBLE") for WildClawBench. Enforces a three-phase pipeline (Phase 0 scope → Phase 0.5 approve → Phase 1 run → Phase 3 verify) with a hard sentinel: Phase 1 will refuse to run unless `sha256(scope.json)` matches the contents of `scope.approved`. Emits `audit/results/grounded_context.json` — the only artifact Phase 2 (the model writing `findings.json`) is permitted to build on. Phase 3 verifies findings against that context and exits non-zero on any invalid claim.

**Runtime deps:** `typer>=0.9`, `rich>=13.0`. Optional `[project.optional-dependencies] scanners`: `ruff`, `bandit`, `semgrep`, `pip-audit`, `radon`, `vulture` (the actual scanners Phase 1 orchestrates). Optional `dev`: `pytest>=7.0`.

**Global CLI conventions:** Typer with `add_completion=False`, `no_args_is_help=True`. Every subcommand exits `0` on success, non-zero on documented failure conditions.

### 6.1 `audit scope` — Phase 0

**Purpose:** Detect the project's surfaces, ecosystems, product types, and per-language LOC via `recon.collect_recon`. Derives the set of required scanner instruments and coverage gaps, then writes:
- `audit/scope.json` — canonical (sort_keys, indent=2) JSON with schema_version, policy_version, git SHA, ecosystems, surfaces, required instruments, per-tool argv template + timeouts, and coverage gaps.
- `audit/SCOPE.md` — human-readable summary including the `scope.json` sha256 and Phase 0.5 sign-off instructions.

**Flags:** none.

**Follow-up:** Phase 0.5 signs off by writing `sha256(scope.json)` into `audit/scope.approved` (see `audit approve` below).

### 6.2 `audit approve` — Phase 0.5 auto-signoff

**Purpose:** Computes `sha256(scope.json)` and writes it to `audit/scope.approved`. For self-contained runs and CI only — in production, an out-of-band reviewer produces `scope.approved`.

**Flags:** none.

**Errors:** raises `typer.BadParameter` if `scope.json` is missing.

### 6.3 `audit run` — Phase 1

**Purpose:** Recon-driven scanner execution. First calls the sentinel `_check_scope_sentinel(scope.json, scope.approved)` — refuses to proceed unless their sha256 matches. Then re-runs recon, filters `applicable_tools()` by ecosystems, applies `--only`/`--skip`, runs each tool with `--timeout` cap (`min(tool.timeout_sec, --timeout)`), normalizes each run's output into issues (via `normalize.normalize_run`), and collects coverage gaps (tool blocked / timeout / unparseable / surface-with-no-instrument). Writes `audit/results/grounded_context.json` — the immutable evidence base for Phase 2/3.

**CLI library:** Typer.

| Flag | Short | Type | Default | Purpose |
| --- | --- | --- | --- | --- |
| `--timeout` | `-t` | int | `900` | Per-tool timeout cap in seconds. |
| `--only` | | list[str] | `None` | Run only these tool names (repeatable). |
| `--skip` | | list[str] | `None` | Skip these tool names (repeatable). |

**Errors:** raises `typer.BadParameter` if the scope sentinel fails.

### 6.4 `audit verify` — Phase 3

**Purpose:** Deterministic verification of a model-produced `findings.json` against the Phase 1 `grounded_context.json`. Runs `verifier.verify_findings` and prints the JSON verification result. Exits `0` if every finding verifies, `1` otherwise. The exit code is the gate for shipping the audit report.

**CLI library:** Typer.

| Flag | Type | Default | Required | Purpose |
| --- | --- | --- | --- | --- |
| `--findings` | Path | — | **Yes** | Path to the model-produced `findings.json`. |
| `--context` | Path | `audit/results/grounded_context.json` | No | Override the grounded-context input. |

**Errors:** raises `typer.BadParameter` if either file is missing.

### 6.5 `audit all` — orchestrator

**Purpose:** Runs the full pipeline in one shot: `scope` → (`approve` unless `--no-approve`) → `run` → optional `verify`. Designed for self-contained CI runs and adversarial testing (the `--no-approve` path proves the sentinel actually blocks).

**CLI library:** Typer.

| Flag | Short | Type | Default | Purpose |
| --- | --- | --- | --- | --- |
| `--timeout` | `-t` | int | `900` | Passed through to `audit run`. |
| `--no-approve` | | flag | `False` | Skip auto-approve step (adversarial test — expects the sentinel to block Phase 1). |
| `--verify` | | flag | `False` | If set, also run Phase 3 verification against `--findings` at the end. |
| `--findings` | | Path | `findings.json` | Relative paths resolve against the project root. |

**Behavior when `--verify` is on but `findings.json` is absent:** prints "findings are UNGATED until `audit verify` exits 0" and returns without failure (a clean Phase 1 does not by itself gate anything).

---

## 7. Environment variables at a glance

Comprehensive map of env vars honored by the pipeline. Only the *first non-empty* alias per row is used.

### Shell / UX

| Var | Consumers | Purpose |
| --- | --- | --- |
| `NO_COLOR` | `log.sh`, all three shell drivers | Disable ANSI colors even on a TTY. |
| `WCB_QUIET` | `log.sh`, `run.sh` | `1` suppresses non-error output (auto-set when the Kensei TUI is active). |
| `COLUMNS`, `TERM` | `log.sh` | Terminal width detection. |
| `TMPDIR` | `run.sh` | Run-marker registry (`$TMPDIR/wcb-active-runs`) and `mktemp` scratch. |
| `GIT_TERMINAL_PROMPT` | `deliver.sh` | Set to `0` when a token is present to fail fast rather than prompt-hang. |
| `GITHUB_TOKEN` / `GH_TOKEN` | `deliver.sh` | Non-interactive HTTPS auth for the delivery repo. |
| `HF_TASKS_REPO` | `prepare.sh` | Override the HF `tasks/` dataset URL. |

### Kensei TUI

| Var | Purpose |
| --- | --- |
| `KENSEI_NO_TUI` | Disable the TUI even on TTY (`kensei_tui.py`, `run.sh`). |
| `KENSEI_HOLD_TUI` | Keep the TUI open after runs finish (`run.sh`). |
| `KENSEI_LOG_DIR` | Override `--watch` for the log dir (`kensei_tui.py`). |
| `KENSEI_QUIT_SENTINEL` | Path the TUI writes on quit so `run.sh` can shut things down (`run.sh`, `kensei_tui.py`). |
| `KENSEI_BUNDLE_ROOT` | Default destination for the auto-bundler (`run.sh`, overridable by `--bundle-root`). |

### Harness runtime (`src/utils/config.py`)

See [§ 2.7 above](#27-env-var-contract-read-by-the-harness-at-runtime) for the full alias table.

### Backend-specific

| Var | Backend | Purpose |
| --- | --- | --- |
| `DOCKER_IMAGE_CODEX` | codex | Override codex agent image (default `wildclawbench-codex-ubuntu:v0.0`). |
| `HERMES_DOCKER_IMAGE` | hermes | Override hermes agent image (default `wildclawbench-hermes-agent:v0.5`). |
| `CODEX_REASONING_EFFORT` | codex | Reasoning effort (default `medium`). |
| `CODEX_WIRE_API` | codex | Wire API override. `chat` is ignored with a warning. |
| `OPENROUTER_IMAGE_MODEL`, `WILDCLAW_IMAGE_MODEL` | codex | Image tool model override. |
| `WILDCLAW_IMAGE_HELPER_CALL_LIMIT` | codex (in-container) | Image helper max calls (default `2`). |
| `HTTP_PROXY_INNER`, `HTTPS_PROXY_INNER`, `NO_PROXY_INNER` | codex | Forwarded proxy vars into container. |
| `BEDROCK_MODEL_ARN`, `AWS_REGION`, `AWS_BEARER_TOKEN_BEDROCK` | openclaw (LiteLLM) | Bedrock routing. |
| `ANTHROPIC_API_KEY` | openclaw (LiteLLM) | Anthropic direct routing. |
| `VERTEX_PROJECT`, `VERTEXAI_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS` | openclaw (LiteLLM) | Vertex routing. |
| `JUDGE_MODEL`, `JUDGE_COUNCIL`, `JUDGE_COUNCIL_MEMBERS` | judge phase | Judge configuration. |
| `WCB_PER_TEST_TIMEOUT` | test executor | Per-test cap (default `30` s). |
| `WCB_AUDIO_TRANSCRIBE_URL`, `WCB_AUDIO_TRANSCRIBE_AUTH` | audio-extract skill | LiteLLM sidecar endpoint injected by harness. |

---

## Quick reference — "which command do I want?"

| Goal | Command |
| --- | --- |
| First-time setup on a fresh clone | `bash script/prepare.sh` |
| Run one task end-to-end | `bash script/run.sh --task input/<name>` |
| Run every task under `input/` | `bash script/run.sh --all-input` |
| K reps × N models per task | `bash script/run.sh --model m1,m2 --reps 3` |
| Re-judge an existing run (no re-execution) | `bash script/run.sh --regrade <run_dir>` or `python3 script/regrade.py --run <run_dir>` |
| Re-run only the tests | `python3 script/rerun_tests.py --run <run_dir>` |
| Aggregate per-model / per-task scores | `python3 script/aggregate_runs.py --backend openclaw` |
| Convert run output to publishable bundle | `python3 script/repackage_to_bundle.py --dest-root output_bundle --all` |
| Reverse a bundle back to `input/` layout | `python3 script/reconstruct_input_from_bundle.py <bundle_path> --out reconstructed_input` |
| Ship deliverables to the delivery repo | `./deliver.sh` (or `./deliver.sh --run …` for the full pipeline) |
| Backfill connector docs (thin connectors only) | `python3 script/backfill_connector_docs.py --only <api1,api2>` |
| Migrate a data module to the drift-plane store | `python3 script/migrate_to_drift_plane.py --only <api>` (dry-run), then `--apply` |
| Verify already-migrated data modules import cleanly | `python3 script/verify_applied.py` |
| Verify migration output (without writing) | `python3 script/verify_migration_dryrun.py` |
| Dry-run overlay-CSV ingestion | `python3 script/coerce_dryrun.py [task]` |
| Unit-check the coerce/strict helpers | `python3 script/coerce_malformed_test.py` |
| Flatten `persona/home/` → `data/` for a task | `python3 script/extract_home_to_data.py <task_dir>` |
| Standalone benchmark run (no `run.sh`) | `python3 eval/run_batch.py --task <path> --agent-backend openclaw [...]` |
| Smoke-test the entire mock-API fleet (HTTP) | `python3 environment/test_all_apis.py --install-deps` |
| Smoke-load every mock API's data module | `python3 environment/smoke_eager_load.py` |
| Audit on-disk data formats across the fleet | `python3 environment/scripts/audit_data_formats.py` |
| Migrate seed CSVs → JSON (fleet-wide) | `python3 environment/scripts/migrate_csv_to_json.py` (dry-run) → `--apply` |
| Report which data files are actually loaded | `python3 environment/scripts/wiring_report.py` |
| Extract text/images from a PDF | `python3 environment/skills/pdf-extract/scripts/extract.py <pdf> --out - --pages 1-5` |
| Call a mock API from the shell (per-connector) | `python3 environment/skills/<name>-api-connector/scripts/fetch_<name>_data.py --help` |
| Run the CRUCIBLE security audit (self-contained) | `pip install -e audit/ && audit all` |
| Only Phase 1 (evidence) | `audit scope && audit approve && audit run` |
| Verify a model-produced `findings.json` | `audit verify --findings findings.json` |

---

*Generated by a manual analysis pass covering: every `.sh` file (repo-wide), every Python file in `script/`, `environment/`, `environment/scripts/`, `environment/skills/*/scripts/`, `audit/*.py`, and every argparse/Typer/Click CLI hook under `src/` and `eval/`. The 101 auto-generated `fetch_*_data.py` connector CLIs are documented by shape (in §4.8) rather than enumerated individually. If you add a new command or flag, update the matching section.*
