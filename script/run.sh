#!/usr/bin/env bash
# WildClawBench end-to-end runner. Handles docker preflight, image loading from
# local tar, leaked-network cleanup, single-task or bulk K-run loops, and one
# docker-error retry. Fails loud with one signal at a time.
#
# This header block is intentionally short. The full --help text is rendered by
# print_help() below (USAGE / FLAGS / EXAMPLES / ADVANCED sections).
#
# Always operates from the repo root regardless of invocation cwd. All relative
# paths below (Images/, logs/, environment/, eval/, script/, input/, output/)
# resolve against the repo root.

set -u
set -o pipefail

cd "$(dirname "$0")/.."

# Shared UX library: colors, step banners, progress bars, summary box.
# Single source of truth for terminal rendering; gated on NO_COLOR + isatty so
# tee'd log files stay ANSI-free. See script/lib/log.sh for the full contract.
# shellcheck source=script/lib/log.sh
source "$(dirname "$0")/lib/log.sh"

readonly AGENT_IMAGE="wildclawbench-ubuntu:v1.3"
readonly AGENT_IMAGE_SHA="60eec8752cb597e180780ff08d7569c1892c169521f1f2b069c2efeb006a4078"
# Custom LiteLLM sidecar image with headroom-ai baked in (agent prompt compression).
readonly HEADROOM_IMAGE="wildclawbench-litellm-headroom:v2"
readonly AGENT_TAR_PATH="Images/wildclawbench-ubuntu_v1.3.tar"
readonly DEFAULT_TASK="input/alden-croft_MB"
readonly DEFAULT_MODEL="claude-opus-4.7"
readonly DEFAULT_K=1
readonly LOG_DIR="logs"

# Absolute path to THIS script so the parallel-task launcher can re-invoke it
# per task — run.sh is the single entry point for everything.
SELF="${WCB_SELF:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")}"  # WCB_SELF: test hook
readonly SELF

# Configurable knobs (overridable via long flags below; defaults preserve the
# legacy invocation contract documented in (b10) — backend=openclaw, judge=on,
# tests=on, thinking=xhigh).
BACKEND="openclaw"
THINKING="xhigh"
JUDGE_COUNCIL=1          # 1 = --judge-council, 0 = omit
USE_TESTS=1              # 1 = --generate-tests --execute-tests, 0 = omit
USE_LITELLM=1            # 1 = --litellm, 0 = omit
USE_MOCK_STACK=1         # 1 = --mock-stack, 0 = omit
USE_CLAUDE_OAUTH=0       # 1 = --use-claude-oauth (route opus through OAuth bridge), 0 = Bedrock
USE_TUI=0                # 1 = --tui (full-screen Textual live dashboard)
SKIP_PREFLIGHT=0         # 1 = skip docker/agent-image/mock-image/.env checks
PARALLEL_REPS=0          # 1 = run all K reps of a (task,model) concurrently, 0 = sequential
PARALLEL_TASKS=1         # >1 = run that many TASKS concurrently via the failure-isolated launcher
INPUT_DIR=""             # --input-dir DIR: queue every task subdir under DIR
AUTO_BUNDLE=1            # 1 = auto-repackage to output_bundle/ after each task, 0 = omit
BUNDLE_ROOT="output_bundle"  # dest-root for the auto-bundler; overridable via KENSEI_BUNDLE_ROOT
STREAM=0                 # 1 = live-stream LLM output to the terminal (--stream). Single-run
                         # foreground only (1 task × 1 model × K=1 × -P 1); display-only
                         # observability — never touches grading/deliverables. See
                         # docs/STREAMING_PLAN.md.

print_help() {
    cat <<'EOF'
WildClawBench runner — docker preflight + fan-out + retry + aggregate

USAGE
  bash script/run.sh                                          # defaults: task=input/alden-croft_MB, model=claude-opus-4.7, K=1
  bash script/run.sh [TASK]                                   # one task, K=1
  bash script/run.sh [TASK] [MODEL[,MODEL2,...]] [K]          # positional
  bash script/run.sh --task TASK --model MODEL --reps K       # flag form
  bash script/run.sh --bulk TASKS_FILE [--model M] [--reps K] # bulk: tasks sequential, models parallel per task
  bash script/run.sh --input-dir DIR -P N [--reps K]          # run every task under DIR, N in parallel (failure-isolated)
  bash script/run.sh --regrade RUN_DIR [--rubric PATH]        # re-judge existing run; overwrites score.json

COMMON FLAGS
  -t, --task PATH           Task directory (e.g. input/alden-croft_MB)
  -m, --model NAME          Model id; comma-separate for parallel models (e.g. claude-opus-4.7,claude-sonnet-4.5)
  -k, --reps N              Repetitions per (task,model); sequential. Alias: --k
  -B, --bulk FILE           Read task paths from FILE (one per line, # comments ok)
      --input-dir DIR       Queue every task subdir under DIR
  -P, --parallel-tasks N    Run N tasks CONCURRENTLY, each failure-isolated (one failing never stops the rest)
                            (-j/--jobs are accepted as aliases)
  --no-subagents            Force sub-agent spawning OFF (model never granted sessions_spawn)
  -R, --regrade DIR         Re-run judge phase only against an existing run dir
      --rubric PATH         Override rubric for --regrade
  -h, --help                Show this help and exit

EXAMPLES
  # Default smoke test (one task, one model, one rep):
  bash script/run.sh

  # Custom task + model:
  bash script/run.sh --task input/amanda_hayes_01 --model claude-opus-4.7

  # Two models in parallel, 3 reps each:
  bash script/run.sh --model claude-opus-4.7,claude-sonnet-4.5 --reps 3

  # 2 reps of one task, both reps running at the same time (run_1 ∥ run_2):
  bash script/run.sh --task input/amanda_hayes_01 --reps 2 --parallel-reps

  # Bulk from a file (tasks sequential, models parallel):
  bash script/run.sh --bulk tasks.txt --model claude-opus-4.7 --reps 2

  # Run EVERY task in a folder, 3 in parallel, 4 reps each (a failing task never stops the others):
  bash script/run.sh --input-dir input_prafful --parallel-tasks 3 --reps 4

  # Regrade an existing run:
  bash script/run.sh --regrade output/openclaw/amanda_hayes_01/trajectories/claude-opus-4.7/run_1

ADVANCED
      --backend NAME        Agent backend (default: openclaw)
      --thinking LEVEL      Thinking budget (default: xhigh; e.g. medium|high|xhigh)
      --no-judge-council    Disable --judge-council (faster, single-judge)
      --no-tests            Disable --generate-tests/--execute-tests
      --no-litellm          Disable LiteLLM sidecar (direct Bedrock)
      --no-mock-stack       Disable mock-stack docker fleet
      --use-claude-oauth    Route opus through Claude Code OAuth bridge (Max plan) instead of Bedrock;
                            requires WCB_CC_ACCOUNT_POOL pointing at OAuth credential JSON file(s)
      --no-bundle           Skip auto-repackage to output_bundle/ after each task
      --bundle-root DIR     Destination for auto-bundle (default: output_bundle; env: KENSEI_BUNDLE_ROOT)
      --parallel-reps       Run all K reps of a (task,model) CONCURRENTLY (default: sequential)
      --stream              Live-stream LLM output (agent thinking+text, judge verdicts) to the
                            terminal while the run executes. Single-run only (1 task × 1 model ×
                            K=1 × -P 1) — silently downgraded otherwise. Display-only: never
                            affects grading, scores, or bundles. Default: off.
      --no-stream           Force streaming off (default)
      --skip-preflight      Skip docker/image/.env checks (DANGEROUS; for re-entry only)

NOTES
  * Tasks run SEQUENTIALLY by default; pass -P/--parallel-tasks N to run N tasks at
    once — FAILURE-ISOLATED, so a single task failing (even a crash) never stops the
    others. Models PARALLELIZE per task. K reps run SEQUENTIALLY unless --parallel-reps.
  * Peak docker load ≈ (parallel-tasks) × (models) × (parallel-reps ? K : 1) stacks.
    Mind RAM/CPU and Bedrock rate limits; lower -P if you hit ThrottlingException.
  * Per-run logs land in logs/<task>_<model>_run<i>_<TIMESTAMP>.log.
  * One automatic retry per run on docker-recoverable errors
    (No such image | manifest unknown | Container startup failed).
  * Set NO_COLOR=1 or pipe stdout to strip ANSI from your terminal.
EOF
}

preflight_docker() {
    log::step 1 6 "Docker daemon"
    if ! command -v docker >/dev/null 2>&1; then
        log::err "docker CLI not found in PATH"
        log::hint "Install Docker Desktop: https://www.docker.com/products/docker-desktop"
        return 1
    fi
    if ! docker info >/dev/null 2>&1; then
        log::err "Docker daemon not responding"
        log::hint "Start Docker Desktop (or 'systemctl start docker') and retry"
        return 1
    fi
    log::ok "Docker daemon up"
}

# Best-effort pv installer so the 13 GB `docker load` is not silent for minutes.
# Returns 0 if pv is already present OR after a successful install; non-zero if
# pv is absent and no supported package manager can install it without
# prompting. Caller MUST tolerate failure — bare `docker load -i` still works.
# Never elevates privileges silently: only invokes sudo if non-root AND sudo
# can run without password (`sudo -n true`). On macOS, only uses an existing
# Homebrew; never installs Homebrew itself.
ensure_pv_installed() {
    if command -v pv >/dev/null 2>&1; then
        return 0
    fi
    log::warn "pv not installed; attempting auto-install for progress display"

    local sudo_cmd=""
    if [[ $EUID -ne 0 ]]; then
        if command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
            sudo_cmd="sudo -n"
        fi
    fi

    case "$(uname -s)" in
        Darwin)
            if command -v brew >/dev/null 2>&1; then
                log::info "Installing pv via Homebrew"
                if brew install pv >/dev/null 2>&1; then
                    log::ok "pv installed"
                    return 0
                fi
                log::warn "brew install pv failed"
            else
                log::warn "Homebrew not present; install pv manually: brew install pv"
            fi
            ;;
        Linux)
            if command -v apt-get >/dev/null 2>&1; then
                log::info "Installing pv via apt-get"
                if ${sudo_cmd} apt-get update -qq >/dev/null 2>&1 && \
                   ${sudo_cmd} apt-get install -y -qq pv >/dev/null 2>&1; then
                    log::ok "pv installed"; return 0
                fi
                log::warn "apt-get install pv failed (need sudo without password)"
            elif command -v dnf >/dev/null 2>&1; then
                log::info "Installing pv via dnf"
                if ${sudo_cmd} dnf install -y -q pv >/dev/null 2>&1; then
                    log::ok "pv installed"; return 0
                fi
                log::warn "dnf install pv failed (need sudo without password)"
            elif command -v yum >/dev/null 2>&1; then
                log::info "Installing pv via yum"
                if ${sudo_cmd} yum install -y -q pv >/dev/null 2>&1; then
                    log::ok "pv installed"; return 0
                fi
                log::warn "yum install pv failed (need sudo without password)"
            elif command -v apk >/dev/null 2>&1; then
                log::info "Installing pv via apk"
                if ${sudo_cmd} apk add --quiet pv >/dev/null 2>&1; then
                    log::ok "pv installed"; return 0
                fi
                log::warn "apk add pv failed"
            else
                log::warn "No supported package manager found; install pv manually"
            fi
            ;;
        *)
            log::warn "Auto-install pv unsupported on $(uname -s); install manually"
            ;;
    esac
    return 1
}

# Handles three failure modes:
#   1. Tag present and resolves: pass-through.
#   2. Tag missing but content image (by SHA) present: re-tag from SHA.
#   3. Neither tag nor SHA present: try to load from AGENT_TAR_PATH; fail with HF hint.
preflight_agent_image() {
    log::step 2 6 "Agent image ${AGENT_IMAGE}"

    if docker image inspect "$AGENT_IMAGE" >/dev/null 2>&1; then
        log::ok "Image present"
        return 0
    fi

    log::warn "Tag not resolvable; checking for content image by SHA"
    if docker image inspect "sha256:${AGENT_IMAGE_SHA}" >/dev/null 2>&1; then
        log::warn "Content image present (sha256:${AGENT_IMAGE_SHA:0:16}…) but tag missing — re-tagging"
        if docker tag "sha256:${AGENT_IMAGE_SHA}" "$AGENT_IMAGE"; then
            log::ok "Re-tagged content image as ${AGENT_IMAGE}"
            return 0
        else
            log::err "docker tag failed"
            return 1
        fi
    fi

    log::warn "Content image also absent — looking for local tar at ${AGENT_TAR_PATH}"
    if [[ -f "$AGENT_TAR_PATH" ]]; then
        local tar_size
        tar_size=$(du -h "$AGENT_TAR_PATH" 2>/dev/null | awk '{print $1}')
        log::info "Loading ${AGENT_TAR_PATH} (${tar_size}) — can take 2–15 min depending on disk"
        ensure_pv_installed || true
        if command -v pv >/dev/null 2>&1; then
            pv "$AGENT_TAR_PATH" | docker load
        else
            log::warn "pv unavailable; loading without progress display (silent for several minutes)"
            docker load -i "$AGENT_TAR_PATH"
        fi
        if docker image inspect "$AGENT_IMAGE" >/dev/null 2>&1; then
            log::ok "Image loaded successfully"
            return 0
        fi
        log::err "docker load completed but tag still not resolvable; check tar integrity"
        return 1
    fi

    log::err "Image not present and tar not found at ${AGENT_TAR_PATH}"
    log::hint "Fetch the tar manually then re-run this script:"
    log::hint "  hf download internlm/WildClawBench ${AGENT_TAR_PATH} --repo-type dataset --local-dir ."
    return 1
}

preflight_mock_image() {
    log::step 3 6 "Mock-stack image kensei3-mocks:v1"
    if docker image inspect kensei3-mocks:v1 >/dev/null 2>&1; then
        log::ok "Mock image present (no rebuild needed)"
        return 0
    fi
    log::warn "Mock image absent — building sentinel before fan-out (~3–5 min first time)"
    if ! python3 -c '
import sys
from pathlib import Path
from src.utils.mock_stack import build_mock_image_if_needed
ok = build_mock_image_if_needed(Path("environment"))
sys.exit(0 if ok else 1)
'; then
        log::err "Mock image build failed — check Docker disk space and environment/ contents"
        return 1
    fi
    log::ok "Mock image built"
}

# Agent-side Headroom prompt compression is opt-in (KENSEI_AGENT_HEADROOM_ENABLED
# truthy in .env; see eval/run_batch.py). When enabled, start_litellm() runs the
# custom sidecar image HEADROOM_IMAGE (headroom-ai baked in) instead of the stock
# LiteLLM image. Nothing else builds it, so build it here if missing. Skipped
# entirely when Headroom is not enabled.
preflight_headroom_image() {
    log::step 4 6 "Headroom LiteLLM image ${HEADROOM_IMAGE}"
    local hr_val
    hr_val=$(grep -E '^KENSEI_AGENT_HEADROOM_ENABLED=' .env 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '[:space:]' | tr 'A-Z' 'a-z')
    if [[ ! "$hr_val" =~ ^(1|true|yes|on)$ ]]; then
        log::ok "Agent Headroom not enabled; stock LiteLLM image will be used (no build needed)"
        return 0
    fi
    if docker image inspect "$HEADROOM_IMAGE" >/dev/null 2>&1; then
        log::ok "Headroom image present (no rebuild needed)"
        return 0
    fi
    log::warn "Headroom image absent — building from docker/litellm-headroom.Dockerfile (~1-2 min)"
    if docker build -f docker/litellm-headroom.Dockerfile -t "$HEADROOM_IMAGE" . >/dev/null 2>&1; then
        log::ok "Headroom image built"
    else
        log::err "Headroom image build failed. Build it manually:"
        log::err "  docker build -f docker/litellm-headroom.Dockerfile -t ${HEADROOM_IMAGE} ."
        log::err "Or disable Headroom by setting KENSEI_AGENT_HEADROOM_ENABLED=false in .env"
        return 1
    fi
}

preflight_env_file() {
    log::step 5 6 ".env credentials"
    if [[ ! -f .env ]]; then
        log::err ".env not found in $(pwd)"
        log::hint "Copy .env.example → .env and fill in credentials"
        return 1
    fi

    local missing=()
    for key in KENSEI_AWS_BEARER_TOKEN KENSEI_AWS_REGION; do
        if ! grep -qE "^${key}=.+" .env; then
            missing+=("$key")
        fi
    done
    if (( ${#missing[@]} > 0 )); then
        log::warn ".env missing/empty: ${missing[*]} (Bedrock calls will fail if not set elsewhere)"
    fi
    log::ok ".env present"
}

# Removes containers and networks that survived a prior crashed batch.
# Names match conventions used by start_litellm/start_mock_stack/_start_task_mock_stack.
# --- active-run registry (concurrency safety for cleanup_orphans) -------------
# Each run.sh registers a PID marker so cleanup_orphans() can tell whether OTHER
# run.sh processes are live. The global orphan sweep removes ALL k3net-*/ll-/
# mocks-/t_ resources BY NAME, so under `xargs -P N` it would tear down a
# concurrent run's LIVE stack (seen as 'No such container: mocks-task-...' and
# 'network k3net-... not found'). We therefore sweep ONLY when this is the sole
# active run; concurrent runs skip it and leave any leftovers for the last run
# to finish (or stale-PID pruning) to reap.
readonly RUN_REGISTRY="${TMPDIR:-/tmp}/wcb-active-runs"
RUN_MARKER=""

register_run() {
    mkdir -p "$RUN_REGISTRY" 2>/dev/null || true
    RUN_MARKER="$RUN_REGISTRY/$$"
    : > "$RUN_MARKER" 2>/dev/null || true
}

cleanup_run_marker() {
    [[ -n "$RUN_MARKER" ]] && rm -f "$RUN_MARKER" 2>/dev/null || true
}

# Returns 0 if ANOTHER live run.sh holds a marker; prunes markers of dead PIDs.
other_runs_active() {
    [[ -d "$RUN_REGISTRY" ]] || return 1
    local m pid rc=1
    for m in "$RUN_REGISTRY"/*; do
        [[ -e "$m" ]] || continue
        pid="${m##*/}"
        [[ "$pid" == "$$" ]] && continue
        if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
            rc=0                                   # a live peer exists
        else
            rm -f "$m" 2>/dev/null || true         # stale marker from a dead run
        fi
    done
    return $rc
}

cleanup_orphans() {
    log::step 6 6 "Orphan cleanup"

    # Concurrency guard: never run the destructive global sweep while a peer
    # run.sh is alive — it would force-remove the peer's live containers/network.
    if other_runs_active; then
        log::warn "Other run.sh process(es) active — SKIPPING global orphan sweep"
        log::info "(concurrency-safe: avoids tearing down a peer's live stack)"
        log::ok "Cleanup skipped"
        return 0
    fi

    local containers
    containers=$(docker ps -aq --filter 'name=ll-' --filter 'name=mocks-' --filter 'name=t_' 2>/dev/null || true)
    if [[ -n "$containers" ]]; then
        local count
        count=$(echo "$containers" | wc -l | tr -d ' ')
        log::warn "Found ${count} orphan container(s) — removing"
        echo "$containers" | xargs -r docker rm -f >/dev/null 2>&1 || true
    else
        log::info "No orphan containers"
    fi

    local networks
    networks=$(docker network ls --filter 'name=k3net-' -q 2>/dev/null || true)
    if [[ -n "$networks" ]]; then
        local count
        count=$(echo "$networks" | wc -l | tr -d ' ')
        log::warn "Found ${count} leaked k3net-* network(s) — removing"
        echo "$networks" | xargs -r -n1 docker network rm >/dev/null 2>&1 || true
    else
        log::info "No leaked networks"
    fi

    log::ok "Cleanup complete"
}

# --- shared infra: one sidecar + one network per batch -----------------------
# Replaces per-rep sidecar/network setup. See docs/reps-failure-diagnosis.md
# §B1-B9 and src/utils/AGENTS.md for the python-side short-circuit contract.
# Globals written: WCB_SHARED_NETWORK, WCB_SHARED_SIDECAR (exported); also
# the supporting WCB_SHARED_SIDECAR_USAGE_LOG / WCB_SHARED_SIDECAR_YAML /
# WCB_SHARED_LITELLM_MASTER_KEY for the python side to reuse the same paths.
# Initialize ONLY if unset/empty. Under -P >1, run_parallel_tasks fans out
# `bash $SELF --task ... --skip-preflight` workers that inherit the parent's
# exported WCB_SHARED_* env vars. Bare `VAR=""` at script-load would clobber
# the inherited value with empty string before the bootstrap-gate at line
# ~1011 could read it, defeating the entire shared-sidecar fix. Use
# parameter-default expansion so the assignment is a no-op when the var is
# already non-empty.
: "${WCB_SHARED_NETWORK:=}"
: "${WCB_SHARED_SIDECAR:=}"
: "${WCB_SHARED_SIDECAR_USAGE_LOG:=}"
: "${WCB_SHARED_SIDECAR_YAML:=}"
: "${WCB_SHARED_LITELLM_MASTER_KEY:=}"
: "${WCB_SHARED_CC_BRIDGE:=}"
: "${WCB_SHARED_CC_BRIDGE_URL:=}"
: "${WCB_SHARED_CC_BRIDGE_HOST_URL:=}"
: "${WCB_SHARED_SIDECAR_STREAM_LOG:=}"
# WCB_SHARED_OWNER_PID is the PID of the process that ran bootstrap_shared_sidecar
# (always the parent run.sh). Workers under -P >1 inherit this via export. The
# teardown_shared_sidecar guard at the top of that function uses this to refuse
# to tear down infra that the worker does NOT own — without this guard, the
# tmpdir-trap installed in every process (parent AND worker) at run.sh:~1029
# fires teardown_shared_sidecar on worker exit, and the first finishing worker
# yanks the shared sidecar out from under slower siblings. The reps still
# "succeeded" in real testing only because Docker's `docker rm -f` race with
# in-flight TCP completed in time on a fast laptop — load-dependent latent
# race that would bite on slower hardware. Reproduced + fixed 2026-06-27.
: "${WCB_SHARED_OWNER_PID:=}"

bootstrap_shared_sidecar() {
    log::rule "Bootstrap shared LiteLLM sidecar (one per batch, not per rep)"
    local suffix tmpfile rc=0
    suffix="$$-$(date +%Y%m%d_%H%M%S)"
    tmpfile="$(mktemp -t wcb_bootstrap.XXXXXX)"

    # python writes key=value to stdout; progress to stderr (tee'd to the
    # user terminal). On non-zero exit, we fail loud and abort the batch —
    # without the sidecar no reps can talk to Bedrock anyway.
    if python3 eval/bootstrap_sidecar.py --name-suffix "$suffix" > "$tmpfile" 2> >(while read -r ln; do log::info "$ln"; done); then
        rc=0
    else
        rc=$?
    fi
    if (( rc != 0 )); then
        log::err "bootstrap_sidecar.py exited rc=$rc — aborting batch"
        rm -f "$tmpfile"
        return $rc
    fi

    # Parse the key=value lines. Empty values mean the bootstrap declined
    # (e.g. no creds → OpenRouter fallback); we just don't export anything.
    local k v
    while IFS='=' read -r k v; do
        case "$k" in
            name)        WCB_SHARED_SIDECAR="$v" ;;
            network)     WCB_SHARED_NETWORK="$v" ;;
            usage_log)   WCB_SHARED_SIDECAR_USAGE_LOG="$v" ;;
            yaml_path)   WCB_SHARED_SIDECAR_YAML="$v" ;;
            master_key)  WCB_SHARED_LITELLM_MASTER_KEY="$v" ;;
            cc_bridge)     WCB_SHARED_CC_BRIDGE="$v" ;;
            cc_bridge_url) WCB_SHARED_CC_BRIDGE_URL="$v" ;;
            cc_bridge_host_url) WCB_SHARED_CC_BRIDGE_HOST_URL="$v" ;;
            stream_log)  WCB_SHARED_SIDECAR_STREAM_LOG="$v" ;;
        esac
    done < "$tmpfile"
    rm -f "$tmpfile"

    if [[ -z "$WCB_SHARED_SIDECAR" || -z "$WCB_SHARED_NETWORK" ]]; then
        log::warn "Shared sidecar declined by bootstrap (no creds?); reps will fall back per-process"
        return 0
    fi

    WCB_SHARED_OWNER_PID=$$
    export WCB_SHARED_NETWORK WCB_SHARED_SIDECAR \
           WCB_SHARED_SIDECAR_USAGE_LOG WCB_SHARED_SIDECAR_YAML \
           WCB_SHARED_LITELLM_MASTER_KEY WCB_SHARED_OWNER_PID \
           WCB_SHARED_CC_BRIDGE WCB_SHARED_CC_BRIDGE_URL \
           WCB_SHARED_CC_BRIDGE_HOST_URL WCB_SHARED_SIDECAR_STREAM_LOG
    log::ok "Shared sidecar=$WCB_SHARED_SIDECAR network=$WCB_SHARED_NETWORK owner_pid=$WCB_SHARED_OWNER_PID"

    # Route the HOST-side Sonnet judge through the OAuth subscription bridge.
    # bootstrap published the in-network cc-bridge on a loopback host port
    # (cc_bridge_host_url); the host-side grading step (run_batch.py) can only
    # reach it via 127.0.0.1. Auto-export the judge env only when the OAuth
    # path is active so Bedrock judging is left untouched otherwise. The judge's
    # own family=='sonnet' gate + x-wcb-bridge-secret still apply downstream.
    if [[ -n "$WCB_SHARED_CC_BRIDGE_HOST_URL" && "${USE_CLAUDE_OAUTH:-0}" == "1" ]]; then
        export KENSEI_JUDGE_OAUTH_BRIDGE_URL="$WCB_SHARED_CC_BRIDGE_HOST_URL"
        export KENSEI_JUDGE_USE_LITELLM=1
        log::ok "Sonnet judge -> OAuth bridge $WCB_SHARED_CC_BRIDGE_HOST_URL"
    fi

    # Install teardown trap that fires on normal exit + Ctrl-C + SIGTERM,
    # so an interrupted batch does not leak the sidecar/network. We REPLACE
    # the existing EXIT trap (which only wiped the run marker) and chain
    # cleanup_run_marker at the end so its prior contract is preserved.
    trap 'teardown_shared_sidecar; cleanup_run_marker' EXIT
    trap 'teardown_shared_sidecar; cleanup_run_marker; exit 130' INT
    trap 'teardown_shared_sidecar; cleanup_run_marker; exit 143' TERM
}

teardown_shared_sidecar() {
    # Owner-PID guard: under -P >1, workers fork via `bash $SELF --task ...`
    # and inherit WCB_SHARED_* exports. Each worker's tmpdir-trap at
    # run.sh:~1029 fires teardown_shared_sidecar on worker exit. Without this
    # guard, the first finishing worker would `docker rm -f` the SHARED sidecar
    # while slower siblings are still mid-flight, causing load-dependent
    # failures. Only the process that bootstrapped (PID == owner) may tear down.
    if [[ -n "${WCB_SHARED_OWNER_PID:-}" && "$$" != "$WCB_SHARED_OWNER_PID" ]]; then
        return 0
    fi
    # Idempotent: blank-out the env vars so a re-entrant trap (e.g. EXIT
    # firing after INT already ran) does not docker-rm twice.
    [[ -z "${WCB_SHARED_SIDECAR:-}${WCB_SHARED_NETWORK:-}" ]] && return 0
    local sc="${WCB_SHARED_SIDECAR:-}"
    local nw="${WCB_SHARED_NETWORK:-}"
    local yp="${WCB_SHARED_SIDECAR_YAML:-}"
    local cb="${WCB_SHARED_CC_BRIDGE:-}"
    WCB_SHARED_SIDECAR=""; WCB_SHARED_NETWORK=""
    WCB_SHARED_SIDECAR_USAGE_LOG=""; WCB_SHARED_SIDECAR_YAML=""
    WCB_SHARED_LITELLM_MASTER_KEY=""
    WCB_SHARED_CC_BRIDGE=""; WCB_SHARED_CC_BRIDGE_URL=""
    WCB_SHARED_CC_BRIDGE_HOST_URL=""
    unset KENSEI_JUDGE_OAUTH_BRIDGE_URL 2>/dev/null || true
    log::info "Tearing down shared sidecar=${sc} network=${nw}${cb:+ cc_bridge=$cb}"
    [[ -n "$sc" ]] && docker rm -f "$sc" >/dev/null 2>&1 || true
    [[ -n "$cb" ]] && docker rm -f "$cb" >/dev/null 2>&1 || true
    [[ -n "$nw" ]] && docker network rm "$nw" >/dev/null 2>&1 || true
    [[ -n "$yp" && -f "$yp" ]] && rm -f "$yp" 2>/dev/null || true
}

# Stamps "$RUN_RC" and "$RUN_LOG" globals so the retry loop can inspect.
RUN_RC=0
RUN_LOG=""
# Set to "1" by the --no-subagents CLI flag; forwarded to run_batch.py so the
# model is never granted sessions_spawn (no sub-agent fan-out for the whole run).
NO_SUBAGENTS=""

run_one() {
    local task_path="$1"
    local model="$2"
    local run_index="$3"
    local total_runs="$4"

    local task_name
    task_name=$(basename "$task_path")
    local ts
    ts=$(date +%Y%m%d_%H%M%S)
    local model_safe="${model//\//_}"
    RUN_LOG="${LOG_DIR}/${task_name}_${model_safe}_run${run_index}_${ts}.log"
    mkdir -p "$LOG_DIR"

    log::substep "Run ${run_index}/${total_runs} — ${task_name} × ${model}"
    log::kv "Log file" "$RUN_LOG"

    # Build python invocation respecting feature toggles.
    local cmd=(
        python3 eval/run_batch.py
        --task "$task_path"
        --agent-backend "$BACKEND"
        --model "$model"
        --thinking "$THINKING"
        --parallel 1
    )
    (( USE_LITELLM == 1 )) && cmd+=(--litellm)
    (( USE_MOCK_STACK == 1 )) && cmd+=(--mock-stack)
    (( USE_CLAUDE_OAUTH == 1 )) && cmd+=(--use-claude-oauth)
    if (( USE_TESTS == 1 )); then
        cmd+=(--generate-tests --testgen-max-attempts 3 --execute-tests --testexec-timeout 600)
    fi
    (( JUDGE_COUNCIL == 1 )) && cmd+=(--judge-council)
    (( USE_TUI == 1 )) && cmd+=(--tui)
    [[ -n "$NO_SUBAGENTS" ]] && cmd+=(--no-subagents)

    set +e
    "${cmd[@]}" 2>&1 | tee "$RUN_LOG"
    RUN_RC=${PIPESTATUS[0]}
    set -e
}

# Single Docker-error retry: detects "Container startup failed", "manifest unknown",
# "Required Docker image not present", "No such image" in the log, attempts a
# tag fix + cleanup, and reruns ONCE.
is_docker_recoverable_error() {
    local log_file="$1"
    [[ -f "$log_file" ]] || return 1
    grep -qE 'Required Docker image not present|Container startup failed|No such image|manifest unknown' "$log_file" 2>/dev/null
}

attempt_docker_recovery() {
    log::warn "Docker-recoverable error detected — attempting recovery"

    if docker image inspect "sha256:${AGENT_IMAGE_SHA}" >/dev/null 2>&1 && ! docker image inspect "$AGENT_IMAGE" >/dev/null 2>&1; then
        log::warn "Tag table appears corrupted — re-tagging from SHA"
        docker tag "sha256:${AGENT_IMAGE_SHA}" "$AGENT_IMAGE" || return 1
    fi

    cleanup_orphans
    log::ok "Recovery complete"
}

run_regrade() {
    local run_dir="$1"
    shift
    local rubric_override=""
    while (( $# > 0 )); do
        case "$1" in
            --rubric)
                rubric_override="${2:-}"
                if [[ -z "$rubric_override" ]]; then
                    log::err "--rubric requires a path argument"
                    return 2
                fi
                shift 2
                ;;
            *)
                log::err "Unknown --regrade option: $1"
                return 2
                ;;
        esac
    done

    if [[ ! -d "$run_dir" ]]; then
        log::err "Run directory not found: $run_dir"
        return 2
    fi

    mkdir -p "$LOG_DIR"
    local ts
    ts=$(date +%Y%m%d_%H%M%S)
    local safe_run_id
    safe_run_id=$(echo "$run_dir" | tr '/' '_' | tr -cd 'a-zA-Z0-9_.-')
    local log_file="${LOG_DIR}/regrade_${safe_run_id}_${ts}.log"

    log::section "Regrade"
    log::kv "Run dir" "$run_dir"
    log::kv "Log file" "$log_file"
    [[ -n "$rubric_override" ]] && log::kv "Rubric override" "$rubric_override"

    local cmd=(python3 script/regrade.py --run "$run_dir")
    [[ -n "$rubric_override" ]] && cmd+=(--rubric "$rubric_override")

    "${cmd[@]}" 2>&1 | tee "$log_file"
    local rc=${PIPESTATUS[0]}

    if (( rc == 0 )); then
        log::ok "Regrade complete; score.json overwritten in $run_dir"
    else
        log::err "Regrade failed (rc=$rc); see $log_file"
    fi
    return "$rc"
}

# Run a single rep (with the one-shot docker-recovery retry) and write its
# outcome (failed/recovered/failure) to $frag. Reads/writes only the RUN_RC and
# RUN_LOG globals set by run_one — safe to background because each rep, when run
# under `&`, gets its own process-local copy of those globals (no cross-rep
# clobber). The actual run_N directory is claimed atomically Python-side, so
# concurrent reps never share a slot.
run_one_rep() {
    local task_path="$1"
    local model="$2"
    local i="$3"
    local current="$4"
    local total="$5"
    local frag="$6"

    local task_name
    task_name=$(basename "$task_path")
    local rep_failed=0
    local rep_recovered=0
    local rep_failure=""

    run_one "$task_path" "$model" "$current" "$total"

    if (( RUN_RC != 0 )); then
        if is_docker_recoverable_error "$RUN_LOG"; then
            attempt_docker_recovery
            log::warn "Retrying run $current/$total after recovery (${model})"
            run_one "$task_path" "$model" "$current" "$total"
            if (( RUN_RC == 0 )); then
                rep_recovered=1
                log::ok "Run $current (${model}) succeeded after recovery"
            else
                log::err "Run $current (${model}) failed after recovery (rc=$RUN_RC)"
                rep_failed=1
                rep_failure="${task_name}#${i}/${model} (rc=$RUN_RC after retry)"
            fi
        else
            log::err "Run $current (${model}) failed (rc=$RUN_RC) — no retry"
            log::hint "Tail of log ($RUN_LOG):"
            tail -n 20 "$RUN_LOG" >&2 || true
            rep_failed=1
            rep_failure="${task_name}#${i}/${model} (rc=$RUN_RC)"
        fi
    else
        log::ok "Run $current (${model}) completed"
    fi

    # Use `if` rather than `[[ -n ... ]] && printf` because the latter returns
    # exit-code 1 on the success path (when $rep_failure is empty) — and that
    # exit code becomes the brace group's exit code, which propagates as the
    # function's exit code. Under `set -e` (run_one sets it at line 497 and
    # never disables it) running inside a backgrounded subshell (run_one_rep
    # is invoked from run_k_for_model_bg which is itself `&`-backgrounded by
    # main()), bash errexit can terminate the for-loop at line 641 after rep 1
    # succeeds, so reps 2..K never fire. Use `if` so the brace group's last
    # command is always a successful printf.
    {
        printf 'failed=%d\n' "$rep_failed"
        printf 'recovered=%d\n' "$rep_recovered"
        if [[ -n "$rep_failure" ]]; then
            printf 'failure=%s\n' "$rep_failure"
        fi
    } > "$frag"
}

run_k_for_model_bg() {
    local task_path="$1"
    local model="$2"
    local k="$3"
    local current_base="$4"
    local total="$5"
    local result_file="$6"

    local frag_dir
    frag_dir=$(mktemp -d -t wildclaw_reps.XXXXXX)
    local frags=()
    local rep_pids=()

    # Dispatch K reps. PARALLEL_REPS=1 fans all K out at once (each rep lands in
    # its own atomically-claimed run_N); =0 keeps the legacy sequential loop.
    for (( i=1; i<=k; i++ )); do
        local current=$(( current_base + i ))
        local frag="${frag_dir}/rep_${i}.frag"
        frags+=("$frag")
        if (( PARALLEL_REPS == 1 )); then
            run_one_rep "$task_path" "$model" "$i" "$current" "$total" "$frag" &
            rep_pids+=($!)
        else
            run_one_rep "$task_path" "$model" "$i" "$current" "$total" "$frag"
        fi
    done

    if (( PARALLEL_REPS == 1 )); then
        for pid in "${rep_pids[@]}"; do
            wait "$pid" || true
        done
    fi

    # Fold per-rep fragments into the per-model result file consumed by main().
    local local_failed=0
    local local_recovered=0
    local local_failures=()
    for frag in "${frags[@]}"; do
        [[ -f "$frag" ]] || continue
        while IFS='=' read -r key value; do
            case "$key" in
                failed)    local_failed=$(( local_failed + value )) ;;
                recovered) local_recovered=$(( local_recovered + value )) ;;
                failure)   local_failures+=("$value") ;;
            esac
        done < "$frag"
    done
    rm -rf "$frag_dir"

    {
        printf 'failed=%d\n' "$local_failed"
        printf 'recovered=%d\n' "$local_recovered"
        if (( ${#local_failures[@]} > 0 )); then
            for f in "${local_failures[@]}"; do
                printf 'failure=%s\n' "$f"
            done
        fi
    } > "$result_file"
}

# Auto-repackage one task into BUNDLE_ROOT after all K reps × models finish.
# Fail-soft: never propagates a non-zero exit (the eval already succeeded;
# bundling is a downstream convenience). Skipped when AUTO_BUNDLE=0 or for
# tasks that produced zero trajectories under output/<backend>/.
#
# Input-root resolution: a hardcoded `--input-root input` silently produces
# trajectories-only bundles when run.sh's CWD does not contain an `input/`
# subtree with the task — `repackage_to_bundle.py::_find_input_task_dir`
# returns None on no match, which silently skips prompt/persona/ground-truth
# staging (warning is gated on --verbose). Derive --input-root from the
# actual on-disk task_path so this auto path converges with the
# eval/run_batch.py b3 fix (`input_root = Path(task["task_dir"]).parent`),
# honoring the script/AGENTS.md convergence invariant. KENSEI_INPUT_ROOT
# remains as an override; falls back to "input" only when task_path is a
# bare relative name (legacy positional CLI form).
bundle_task() {
    local task_path="$1"
    (( AUTO_BUNDLE == 1 )) || return 0

    local task_name
    task_name=$(basename "$task_path")
    local source_root="output/${BACKEND}"
    local bundle_root="${KENSEI_BUNDLE_ROOT:-$BUNDLE_ROOT}"

    # Resolve input-root from the on-disk task path. Fall back to
    # KENSEI_INPUT_ROOT → "input" only when task_path is not a real
    # directory (e.g. legacy positional form `bash script/run.sh alden-croft_MB`
    # where the caller passed just the basename).
    local input_root
    if [[ -d "$task_path" ]]; then
        input_root="$(cd "$(dirname "$task_path")" && pwd)"
    else
        input_root="${KENSEI_INPUT_ROOT:-input}"
    fi

    if [[ ! -d "${source_root}/${task_name}/trajectories" ]]; then
        log::warn "bundle: no trajectories for ${task_name} under ${source_root}/ — skipping"
        return 0
    fi

    # Backfill pass before repackaging (both idempotent, both fail-soft like
    # the bundler itself — the eval already succeeded):
    #   (a) run-data: writes data/environment/ (mock APIs) into run dirs that
    #       lack it — the post-6e03e6b pipeline never writes it, so without
    #       this the bundle ships persona + plane files only, no mock-API
    #       services (see script/backfill_run_data.py header).
    #   (b) pass_summary: rebuilds pass_summary.json from score.json +
    #       ctrf.json so real tests_* counts and combined_reward survive into
    #       the bundle and the later aggregate step.
    # Under -P >1 concurrent workers may both scan the whole ${source_root};
    # benign — skip-existing plus identical generated content make the race
    # harmless.
    local backfill_log="${LOG_DIR}/backfill_${task_name}_$(date +%Y%m%d_%H%M%S).log"
    if ! python3 script/backfill_run_data.py \
            --output-root "$source_root" --input-root "$input_root" \
            >> "$backfill_log" 2>&1; then
        log::warn "bundle: run-data backfill failed for ${task_name} (see ${backfill_log}); bundle may lack mock APIs"
    fi
    if ! python3 script/backfill_pass_summary.py "${source_root}/${task_name}" \
            >> "$backfill_log" 2>&1; then
        log::warn "bundle: pass_summary backfill failed for ${task_name} (see ${backfill_log}); continuing"
    fi

    log::substep "Bundling → ${bundle_root}/${task_name} (input_root=${input_root})"
    mkdir -p "$bundle_root"
    local bundle_log="${LOG_DIR}/bundle_${task_name}_$(date +%Y%m%d_%H%M%S).log"
    # --verbose so silent skips (no input match, missing ground-truth source,
    # missing harness env files) surface in $bundle_log instead of vanishing
    # into a clean exit 0 with empty stderr.
    if python3 script/repackage_to_bundle.py \
            --source-root "$source_root" \
            --dest-root   "$bundle_root" \
            --input-root  "$input_root" \
            --persona     "$task_name" \
            --verbose \
            > "$bundle_log" 2>&1; then
        log::ok "Bundled ${task_name} → ${bundle_root}/${task_name} (log: ${bundle_log})"
        # Enrich mode: copy live references/+scripts/ into the bundle's
        # connector dirs (bundles snapshot skills/ from run output, which may
        # predate the docs generator). Whole ${bundle_root} rather than just
        # this task because the repackager's fuzzy persona match may name the
        # dest dir differently; already-rich bundles are skipped, so the wider
        # scan stays idempotent.
        if ! python3 script/backfill_connector_docs.py \
                --bundle-root "$bundle_root" \
                >> "$bundle_log" 2>&1; then
            log::warn "bundle: connector-docs enrich failed (see ${bundle_log}); thin connectors may remain"
        fi
    else
        log::warn "bundle: repackage failed for ${task_name} (see ${bundle_log}); continuing"
    fi
}

# Parses CLI args into module globals. Supports:
#   * legacy positional form  (task [model[,model2]] [K])
#   * new long-flag form      (--task / --model / --reps / ...)
#   * --bulk + --regrade subcommands
# Sets globals: MODE, TASKS[], MODELS_ARG, K, REGRADE_DIR, REGRADE_EXTRA[]
parse_args() {
    MODE="single"
    TASKS=()
    MODELS_ARG="$DEFAULT_MODEL"
    K="$DEFAULT_K"
    REGRADE_DIR=""
    REGRADE_EXTRA=()
    local tasks_file=""
    local positional=()

    while (( $# > 0 )); do
        case "$1" in
            -h|--help)
                print_help; exit 0 ;;
            -t|--task)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a value"; exit 2; }
                TASKS+=("$2"); shift 2 ;;
            -m|--model|--models)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a value"; exit 2; }
                MODELS_ARG="$2"; shift 2 ;;
            -k|--reps|--k)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a value"; exit 2; }
                K="$2"; shift 2 ;;
            -B|--bulk)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a tasks file"; exit 2; }
                MODE="bulk"; tasks_file="$2"; shift 2 ;;
            -R|--regrade)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a run dir"; exit 2; }
                MODE="regrade"; REGRADE_DIR="$2"; shift 2 ;;
            --rubric)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a path"; exit 2; }
                REGRADE_EXTRA+=(--rubric "$2"); shift 2 ;;
            --backend)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a value"; exit 2; }
                BACKEND="$2"; shift 2 ;;
            --thinking)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a value"; exit 2; }
                THINKING="$2"; shift 2 ;;
            --no-judge-council)   JUDGE_COUNCIL=0; shift ;;
            --tui)                USE_TUI=1; shift ;;
            --no-tests)           USE_TESTS=0; shift ;;
            --no-litellm)         USE_LITELLM=0; shift ;;
            --no-mock-stack)      USE_MOCK_STACK=0; shift ;;
            --use-claude-oauth)   USE_CLAUDE_OAUTH=1; shift ;;
            --no-bundle)          AUTO_BUNDLE=0; shift ;;
            --bundle-root)        BUNDLE_ROOT="$2"; shift 2 ;;
            --stream)             STREAM=1; shift ;;
            --no-stream)          STREAM=0; shift ;;
            --parallel-reps)      PARALLEL_REPS=1; shift ;;
            -j|--jobs|-P|--parallel-tasks)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a value"; exit 2; }
                PARALLEL_TASKS="$2"; shift 2 ;;
            --input-dir)
                [[ -n "${2:-}" ]] || { log::err "$1 requires a value"; exit 2; }
                INPUT_DIR="$2"; shift 2 ;;
            --no-subagents)       NO_SUBAGENTS=1; shift ;;
            --skip-preflight)     SKIP_PREFLIGHT=1; shift ;;
            --) shift; while (( $# > 0 )); do positional+=("$1"); shift; done ;;
            -*) log::err "Unknown flag: $1"; log::hint "Run 'bash script/run.sh --help' for usage"; exit 2 ;;
            *)  positional+=("$1"); shift ;;
        esac
    done

    # --input-dir DIR: queue every immediate task subdir under DIR. Combined with
    # -P/--parallel-tasks it fans them out concurrently; otherwise they run
    # sequentially through the normal loop.
    if [[ -n "$INPUT_DIR" ]]; then
        if [[ ! -d "$INPUT_DIR" ]]; then
            log::err "--input-dir not found: $INPUT_DIR"; exit 2
        fi
        local _d
        while IFS= read -r _d; do
            [[ -n "$_d" ]] && TASKS+=("$_d")
        done < <(find "$INPUT_DIR" -mindepth 1 -maxdepth 1 -type d | sort)
        (( ${#TASKS[@]} > 0 )) || { log::err "no task dirs under --input-dir $INPUT_DIR"; exit 2; }
    fi

    # If --regrade, bypass bulk/single handling.
    if [[ "$MODE" == "regrade" ]]; then
        return 0
    fi

    # If --bulk, read tasks file (positional 1 = model, 2 = K when in legacy bulk form).
    if [[ "$MODE" == "bulk" ]]; then
        if [[ ! -f "$tasks_file" ]]; then
            log::err "Bulk tasks file not found: $tasks_file"; exit 2
        fi
        while IFS= read -r line; do
            line="${line%%#*}"
            line="${line#"${line%%[![:space:]]*}"}"
            line="${line%"${line##*[![:space:]]}"}"
            [[ -n "$line" ]] && TASKS+=("$line")
        done < "$tasks_file"
        # Allow legacy: --bulk file MODEL K
        (( ${#positional[@]} >= 1 )) && MODELS_ARG="${positional[0]}"
        (( ${#positional[@]} >= 2 )) && K="${positional[1]}"
        return 0
    fi

    # Legacy positional form: task [model[,m2]] [K]. Flag-form --task accumulates separately.
    if (( ${#TASKS[@]} == 0 )); then
        if (( ${#positional[@]} >= 1 )); then
            TASKS+=("${positional[0]}")
        else
            TASKS+=("$DEFAULT_TASK")
        fi
    fi
    (( ${#positional[@]} >= 2 )) && MODELS_ARG="${positional[1]}"
    (( ${#positional[@]} >= 3 )) && K="${positional[2]}"
}

# Launcher mode: run ${#TASKS[@]} tasks, PARALLEL_TASKS at a time, each FULLY
# ISOLATED — a task failing/crashing (even exit 255 or a signal-kill) never stops
# the others. Re-invokes THIS script per task with --skip-preflight (the launcher
# already validated docker/images/.env once); concurrency-safe cleanup +
# flock-serialized mock build make the concurrent worker runs race-free.
run_parallel_tasks() {
    local par="$PARALLEL_TASKS"
    local status_dir
    status_dir="$(mktemp -d "${TMPDIR:-/tmp}/wcb_partasks.XXXXXX")"

    # Per-task worker flags reconstructed from the parsed globals so each run
    # matches what the user asked for.
    local -a wargs=(--model "$MODELS_ARG" --reps "$K" --backend "$BACKEND"
                    --thinking "$THINKING" --skip-preflight)
    (( USE_LITELLM == 0 ))    && wargs+=(--no-litellm)
    (( USE_MOCK_STACK == 0 )) && wargs+=(--no-mock-stack)
    (( USE_CLAUDE_OAUTH == 1 )) && wargs+=(--use-claude-oauth)
    (( USE_TESTS == 0 ))      && wargs+=(--no-tests)
    (( JUDGE_COUNCIL == 0 ))  && wargs+=(--no-judge-council)
    (( AUTO_BUNDLE == 0 ))    && wargs+=(--no-bundle)
    (( PARALLEL_REPS == 1 ))  && wargs+=(--parallel-reps)

    log::rule "Parallel launch: ${#TASKS[@]} task(s), ${par} at a time (failure-isolated)"

    local -a pids=()
    local t name
    for t in "${TASKS[@]}"; do
        name="$(basename "$t")"
        # Subshell: run one task, record PASS/FAIL, and ALWAYS exit 0 so a single
        # task's failure can never abort the launcher (no xargs-style 255/signal
        # propagation). Per-task output goes to its own logs/ file via run.sh.
        (
            if bash "$SELF" --task "$t" "${wargs[@]}"; then
                echo "PASS" > "$status_dir/$name"
            else
                echo "FAIL(rc=$?)" > "$status_dir/$name"
            fi
        ) &
        pids+=("$!")
        log::info "launched [${#pids[@]}/${#TASKS[@]}]: $name"
        # Bound concurrency portably (no `wait -n`, which is bash 4.3+): when at
        # capacity, block on the OLDEST job, then free its slot.
        if (( ${#pids[@]} >= par )); then
            wait "${pids[0]}" 2>/dev/null || true
            pids=("${pids[@]:1}")
        fi
    done
    wait  # drain the remaining workers

    local pass=0 fail=0 s
    for t in "${TASKS[@]}"; do
        name="$(basename "$t")"; s="$status_dir/$name"
        if [[ -f "$s" && "$(cat "$s")" == "PASS" ]]; then
            pass=$(( pass + 1 ))
        else
            fail=$(( fail + 1 ))
        fi
    done
    log::summary_box "Parallel run summary" \
        "Tasks=${#TASKS[@]}" "Passed=$pass" "Failed=$fail" "Parallelism=$par"
    if (( fail > 0 )); then
        log::err "Failed/incomplete task(s) — see logs/ for each:"
        for t in "${TASKS[@]}"; do
            name="$(basename "$t")"; s="$status_dir/$name"
            if [[ ! -f "$s" || "$(cat "$s")" != "PASS" ]]; then
                log::err "  - ${name} $([[ -f "$s" ]] && cat "$s" || echo '(no status — worker killed)')"
            fi
        done
    fi
    rm -rf "$status_dir"

    log::substep "Aggregating pass@K across all tasks"
    # Rebuild every pass_summary.json first so the rollup reads real tests_*
    # counts + combined_reward, including tasks graded before the schema fix.
    python3 script/backfill_pass_summary.py "output/${BACKEND}" >/dev/null 2>&1 || \
        log::warn "pass_summary backfill failed; aggregate may read stale summaries"
    if python3 script/aggregate_runs.py --backend "$BACKEND" >/dev/null 2>&1; then
        log::ok "Aggregated → output/${BACKEND}_aggregate_summary.json"
    else
        log::warn "aggregate_runs.py failed; pass@K rollup unavailable"
    fi
    (( fail == 0 ))
}

main() {
    parse_args "$@"

    # --regrade short-circuits everything else.
    if [[ "$MODE" == "regrade" ]]; then
        preflight_env_file || exit 1
        run_regrade "$REGRADE_DIR" ${REGRADE_EXTRA[@]+"${REGRADE_EXTRA[@]}"}
        exit $?
    fi

    # Validate models + K.
    local models=()
    IFS=',' read -ra models <<< "$MODELS_ARG"
    if (( ${#models[@]} == 0 )); then
        log::err "No models specified"; exit 2
    fi
    if ! [[ "$K" =~ ^[0-9]+$ ]] || (( K < 1 )); then
        log::err "--reps must be a positive integer, got: $K"; exit 2
    fi
    if ! [[ "$PARALLEL_TASKS" =~ ^[0-9]+$ ]] || (( PARALLEL_TASKS < 1 )); then
        log::err "--parallel-tasks must be a positive integer, got: $PARALLEL_TASKS"; exit 2
    fi

    # Live-stream gate (docs/STREAMING_PLAN.md D6/R6). Token streaming is
    # single-run foreground only: with fan-out (multi task/model/rep) the
    # shared feed interleaves runs unreadably, so the flag downgrades with a
    # warning instead of half-working. Must be decided (and exported) BEFORE
    # bootstrap_shared_sidecar below — the gate is batch-scoped: it controls
    # whether the shared sidecar mounts the stream callback at all.
    if (( STREAM == 1 )) && (( K == 1 && ${#models[@]} == 1 && ${#TASKS[@]} == 1 && PARALLEL_TASKS == 1 )); then
        export WCB_STREAM=1
    else
        if (( STREAM == 1 )); then
            log::warn "--stream: live token streaming is single-run only (1 task × 1 model × K=1 × -P 1); disabled for this batch"
        fi
        STREAM=0
        # run.sh is AUTHORITATIVE over the gate: a stale WCB_STREAM inherited
        # from the caller's environment must not leak token-mode into fan-out
        # batches (D6) or into flag-off runs (R6 byte-identical contract).
        unset WCB_STREAM 2>/dev/null || true
    fi

    log::section "WildClawBench runner"
    log::kv "Mode"     "$MODE"
    log::kv "Tasks"    "${#TASKS[@]}"
    log::kv "Models"   "${models[*]}"
    log::kv "Reps"     "$K per (task,model)"
    log::kv "Backend"  "$BACKEND"
    log::kv "Thinking" "$THINKING"
    local feats=()
    (( USE_LITELLM == 1 ))    && feats+=("litellm")
    (( USE_MOCK_STACK == 1 )) && feats+=("mock-stack")
    (( USE_TESTS == 1 ))      && feats+=("tests")
    (( JUDGE_COUNCIL == 1 ))  && feats+=("judge-council")
    (( PARALLEL_REPS == 1 ))  && feats+=("parallel-reps")
    (( AUTO_BUNDLE == 1 ))    && feats+=("auto-bundle→${KENSEI_BUNDLE_ROOT:-$BUNDLE_ROOT}/")
    (( STREAM == 1 ))         && feats+=("stream")
    log::kv "Features" "${feats[*]:-none}"
    log::kv "Cwd"      "$(pwd)"

    # Register this run so concurrent run.sh processes don't sweep each other's
    # live docker resources (see cleanup_orphans / other_runs_active).
    register_run
    trap 'cleanup_run_marker' EXIT

    if (( SKIP_PREFLIGHT == 0 )); then
        log::rule "Preflight checks"
        preflight_docker || exit 1
        preflight_agent_image || exit 1
        # Before the mock-image check: a first-time docs backfill changes the
        # environment/ content hash, and this order lets a preflight build
        # (image absent) pick the enriched tree up immediately.
        preflight_connector_docs
        preflight_mock_image || exit 1
        preflight_headroom_image || exit 1
        preflight_env_file || exit 1
        cleanup_orphans
    else
        log::warn "Skipping preflight (--skip-preflight)"
    fi

    # Shared infra: bring up ONE litellm sidecar + ONE docker network for the
    # whole batch (all tasks × models × reps), instead of one per rep python
    # process. See docs/reps-failure-diagnosis.md §B1-B9 (THIRTEEN unwrapped
    # raise sites in the per-rep python setup) — making the sidecar a batch-
    # singleton eliminates those raise sites from the rep loop entirely.
    # Skipped under --skip-preflight (worker children inherit our exported
    # WCB_SHARED_* env vars) AND when SKIP_SHARED_SIDECAR=1 is set (manual
    # bypass for the rare direct `python3 eval/run_batch.py` invocation that
    # needs its own sidecar lifecycle).
    if (( SKIP_PREFLIGHT == 0 )) && (( USE_LITELLM == 1 )) \
       && [[ "${SKIP_SHARED_SIDECAR:-0}" != "1" ]] \
       && [[ -z "${WCB_SHARED_SIDECAR:-}" ]]; then
        bootstrap_shared_sidecar || exit 1
    elif [[ -n "${WCB_SHARED_SIDECAR:-}" ]]; then
        log::info "Inheriting shared sidecar from parent: ${WCB_SHARED_SIDECAR}"
    fi

    # Parallel-task launcher: fan THIS script out per task, failure-isolated.
    # Each worker is a normal single-task run.sh (made concurrency-safe by the
    # cleanup registry + flock-serialized mock-image build).
    if (( PARALLEL_TASKS > 1 )) && (( ${#TASKS[@]} > 1 )); then
        run_parallel_tasks
        exit $?
    fi

    local total=$(( ${#TASKS[@]} * ${#models[@]} * K ))
    local current_base=0
    local failed_count=0
    local recovered_count=0
    local failed_runs=()
    local completed=0

    local tmpdir
    tmpdir=$(mktemp -d -t wildclaw_runsh.XXXXXX)
    # Invariant: every exit path (normal / Ctrl-C / SIGTERM) MUST call
    # teardown_shared_sidecar OR the batch-singleton sidecar+network leak.
    # teardown_shared_sidecar is idempotent and a no-op when no shared
    # sidecar was set up.
    trap 'rm -rf "$tmpdir"; teardown_shared_sidecar; cleanup_run_marker' EXIT
    trap 'rm -rf "$tmpdir"; teardown_shared_sidecar; cleanup_run_marker; exit 130' INT
    trap 'rm -rf "$tmpdir"; teardown_shared_sidecar; cleanup_run_marker; exit 143' TERM

    log::rule "Executing ${total} run(s)"

    for task in "${TASKS[@]}"; do
        if [[ ! -d "$task" && ! -f "$task" ]]; then
            log::err "Task path not found: $task — skipping ($(( ${#models[@]} * K )) runs)"
            failed_count=$(( failed_count + ${#models[@]} * K ))
            failed_runs+=("$task (path missing)")
            current_base=$(( current_base + ${#models[@]} * K ))
            completed=$(( completed + ${#models[@]} * K ))
            log::progress "$completed" "$total" "skipped: $(basename "$task")"
            continue
        fi

        log::substep "Task: $(basename "$task") — fanning out to ${#models[@]} model(s)"

        local pids=()
        local result_files=()
        local m_idx=0
        for m in "${models[@]}"; do
            local m_current_base=$(( current_base + m_idx * K ))
            local result_file="${tmpdir}/$(basename "$task")_${m//\//_}_${m_idx}.result"
            result_files+=("$result_file")
            run_k_for_model_bg "$task" "$m" "$K" "$m_current_base" "$total" "$result_file" &
            pids+=($!)
            m_idx=$(( m_idx + 1 ))
        done

        for pid in "${pids[@]}"; do
            wait "$pid" || true
        done

        for rf in "${result_files[@]}"; do
            [[ -f "$rf" ]] || continue
            local m_failed=0
            local m_recovered=0
            while IFS='=' read -r key value; do
                case "$key" in
                    failed)    m_failed="$value" ;;
                    recovered) m_recovered="$value" ;;
                    failure)   failed_runs+=("$value") ;;
                esac
            done < "$rf"
            failed_count=$(( failed_count + m_failed ))
            recovered_count=$(( recovered_count + m_recovered ))
        done

        current_base=$(( current_base + ${#models[@]} * K ))
        completed=$(( current_base ))
        log::progress "$completed" "$total" "task done: $(basename "$task")"

        bundle_task "$task"
    done

    local succeeded=$(( total - failed_count ))

    log::section "Summary"
    log::summary_box "Run summary" \
        "Total runs=$total" \
        "Succeeded=$succeeded" \
        "Recovered=$recovered_count" \
        "Failed=$failed_count"

    if (( failed_count > 0 )) && (( ${#failed_runs[@]} > 0 )); then
        log::err "Failed runs:"
        for r in "${failed_runs[@]}"; do
            log::err "  - $r"
        done
    fi

    if (( K > 1 || ${#TASKS[@]} > 1 || ${#models[@]} > 1 )); then
        log::substep "Aggregating pass@K"
        # Same repair as the parallel-launcher path: the rollup must read the
        # rebuilt (real tests_* + combined_reward) summaries, not stale ones.
        python3 script/backfill_pass_summary.py "output/${BACKEND}" >/dev/null 2>&1 || \
            log::warn "pass_summary backfill failed; aggregate may read stale summaries"
        if python3 script/aggregate_runs.py --backend "$BACKEND" 2>&1; then
            log::ok "Aggregated → output/${BACKEND}_aggregate_summary.json"
        else
            log::warn "aggregate_runs.py failed; pass@K rollup unavailable"
        fi
    fi

    if (( failed_count > 0 )); then
        exit 1
    fi
    log::ok "All runs completed successfully"
    exit 0
}

main "$@"
