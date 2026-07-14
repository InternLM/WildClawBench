#!/usr/bin/env bash
# deliver.sh — one-shot deliverable pipeline: [run] -> convert -> stage -> push
#
# Pipeline phases (auto-numbered in the live log):
#   (optional)  [1/4] RUN       run eval task(s) via script/run.sh (Docker + .env)
#               [2/4] CONVERT   raw run output -> harbour CLI ("bundle") format
#                               (script/repackage_to_bundle.py)
#               [3/4] STAGE     clone delivery repo + copy bundles into deliverable dir
#               [4/4] PUSH      commit + push to the delivery repo branch
#
# Two modes:
#   CONVERT-ONLY (default): packages whatever already exists under output/.
#   RUN          (--run): runs the eval first to produce FRESH output, then packages.
#
# Requires: python3, git (+ push creds), and git-lfs (default on; --no-lfs to opt out).
# --run additionally needs Docker + a valid .env (same as script/run.sh).

set -euo pipefail

# ---- configuration (override via flags) ------------------------------------
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_REPO="https://github.com/Ethara-Ai/kensei-delievery.git"
TARGET_BRANCH="main"
DELIVERABLE_DIR="test_deliverables"
SOURCE_ROOT="output/openclaw"     # raw run-output tree to convert
INPUT_ROOT="input"                # where task dirs live (for --all-tasks)
PERSONA=""                        # convert-only: one persona (empty => --all)
DRY_RUN=0

DO_RUN=0                          # --run: run the eval before converting
ALL_TASKS=0                       # --all-tasks: run every task under input/
TASKS_FILE=""                     # --tasks-file: bulk list
MODEL=""                          # --model: passthrough to script/run.sh (empty => its default)
K_RUNS=""                         # -k: passthrough to script/run.sh (empty => its default)
declare -a RUN_TASKS=()           # --task (repeatable)

USE_LFS=1                         # default ON: track large binaries via git-lfs (--no-lfs to disable)
LFS_EXPLICIT=0                    # set when --lfs is passed explicitly (then a missing git-lfs is fatal)
# Non-interactive auth (EC2/headless): export GITHUB_TOKEN or GH_TOKEN before running.
GH_TOKEN_VAL="${GITHUB_TOKEN:-${GH_TOKEN:-}}"

# ---- shared logging library ------------------------------------------------
# All user-facing output goes through log:: helpers from script/lib/log.sh so
# tty rendering, NO_COLOR honor, and piped/file-redirected sinks stay coherent.
# shellcheck source=script/lib/log.sh
source "$REPO_ROOT/script/lib/log.sh"

# ---- help ------------------------------------------------------------------
print_help() {
  cat <<'EOF'
deliver.sh — run the eval (optional), convert output, push to delivery repo.

USAGE:
  ./deliver.sh                                  # convert+push existing bundles
  ./deliver.sh --run --task <input/PATH>        # run task first, then publish
  ./deliver.sh --run --all-tasks                # run every task under input/
  ./deliver.sh --persona <NAME>                 # convert one existing persona

COMMON FLAGS:
  --run                          Run the eval before converting (default: skip).
  -t, --task <input/PATH>        Add a task to run (repeatable). Requires --run.
  --tasks-file <FILE>            File listing tasks (one path per line). Requires --run.
  --all-tasks                    Use every dir under input/ as a task. Requires --run.
  -m, --model <NAME>             Model for the eval (default: script/run.sh's default).
  -k <N>                         Repetitions per (task, model) (default: 1).
  --persona <NAME>               (Convert-only) Package this persona instead of --all.
  --dry-run                      Do everything except the final push (safe test).

ADVANCED:
  --source-root <PATH>           Raw output tree (default: output/openclaw).
  --deliverable <NAME>           Folder name inside delivery repo (default: test_deliverables).
  --branch <NAME>                Delivery repo branch (default: main).
  --repo <URL>                   Delivery repo URL (default: kensei-delievery on GitHub).
  --lfs / --no-lfs               Force/disable Git LFS for large binaries (default: on).
  -h, --help                     Show this help and exit.

EXAMPLES:
  # Convert all existing output and push:
  ./deliver.sh

  # Run a single task end-to-end (eval -> convert -> push):
  ./deliver.sh --run --task input/amanda_hayes_01

  # Run several tasks with a specific model and K=3, then push:
  ./deliver.sh --run --tasks-file my_tasks.txt --model claude-opus-4.7 -k 3

  # Convert one persona without pushing (preview the bundle):
  ./deliver.sh --persona "amanda hayes" --dry-run

NOTES:
  • Non-interactive auth: export GITHUB_TOKEN (or GH_TOKEN) before running.
  • Git LFS auto-falls-back to plain git if not installed (warns once).
  • Set NO_COLOR=1 to disable terminal colors.
EOF
}

# Inject a token into an https URL for non-interactive clone/push (EC2/headless).
_auth_url(){
    local url="$1"
    if [[ -n "$GH_TOKEN_VAL" && "$url" == https://* ]]; then
        printf 'https://x-access-token:%s@%s' "$GH_TOKEN_VAL" "${url#https://}"
    else
        printf '%s' "$url"
    fi
}

# ---- args ------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --run)              DO_RUN=1; shift ;;
        --lfs)              USE_LFS=1; LFS_EXPLICIT=1; shift ;;
        --no-lfs)           USE_LFS=0; shift ;;
        -t|--task)          RUN_TASKS+=("${2:?--task needs a path}"); shift 2 ;;
        --tasks-file)       TASKS_FILE="${2:?--tasks-file needs a path}"; shift 2 ;;
        --all-tasks)        ALL_TASKS=1; shift ;;
        -m|--model)         MODEL="${2:?--model needs a value}"; shift 2 ;;
        -k)                 K_RUNS="${2:?-k needs a value}"; shift 2 ;;
        --dry-run)          DRY_RUN=1; shift ;;
        --persona)          PERSONA="${2:?--persona needs a value}"; shift 2 ;;
        --source-root)      SOURCE_ROOT="${2:?--source-root needs a value}"; shift 2 ;;
        --deliverable)      DELIVERABLE_DIR="${2:?--deliverable needs a value}"; shift 2 ;;
        --branch)           TARGET_BRANCH="${2:?--branch needs a value}"; shift 2 ;;
        --repo)             TARGET_REPO="${2:?--repo needs a value}"; shift 2 ;;
        -h|--help)          print_help; exit 0 ;;
        *)                  log::err "Unknown arg: $1 (try --help)"; exit 2 ;;
    esac
done

command -v python3 >/dev/null || log::die "python3 not found in PATH"
command -v git >/dev/null     || log::die "git not found in PATH"
cd "$REPO_ROOT"

# ---- intro banner ----------------------------------------------------------
log::section "WildClawBench Delivery Pipeline"
if [[ "$DO_RUN" -eq 1 ]]; then
    MODE_LABEL="eval -> backfill -> convert -> stage -> push"
    TOTAL_STEPS=5
else
    MODE_LABEL="backfill -> convert -> stage -> push"
    TOTAL_STEPS=4
fi
log::kv "Mode"        "$MODE_LABEL"
log::kv "Repo"        "$REPO_ROOT"
log::kv "Source"      "$SOURCE_ROOT"
log::kv "Target"      "$TARGET_REPO ($TARGET_BRANCH)"
log::kv "Deliverable" "$DELIVERABLE_DIR/"
log::kv "Git LFS"     "$([[ $USE_LFS -eq 1 ]] && echo on || echo off)"
log::kv "Dry-run"     "$([[ $DRY_RUN -eq 1 ]] && echo yes || echo no)"
log::kv "Auth"        "$([[ -n $GH_TOKEN_VAL ]] && echo 'GITHUB_TOKEN (headless)' || echo 'interactive')"

# ---- temp workspace (cleaned on exit) --------------------------------------
STAGING="$(mktemp -d)"
CLONE_DIR="$(mktemp -d)"
cleanup(){ rm -rf "$STAGING" "$CLONE_DIR"; }
trap cleanup EXIT

# ---- step numbering helpers ------------------------------------------------
STEP_IDX=0
next_step() { STEP_IDX=$((STEP_IDX + 1)); log::step "$STEP_IDX" "$TOTAL_STEPS" "$1"; }

# ---- [optional] RUN the eval to produce fresh output -----------------------
declare -a CONVERT_PERSONAS=()    # personas to convert after a run

if [[ "$DO_RUN" -eq 1 ]]; then
    next_step "Run eval(s) via script/run.sh"
    [[ -x "$REPO_ROOT/script/run.sh" ]] || log::die "script/run.sh not found/executable in $REPO_ROOT"

    # Build the effective task list from --task / --tasks-file / --all-tasks.
    declare -a TASKS=()
    if [[ "$ALL_TASKS" -eq 1 ]]; then
        shopt -s nullglob
        for d in "$INPUT_ROOT"/*/; do TASKS+=("${d%/}"); done
        shopt -u nullglob
    fi
    if [[ -n "$TASKS_FILE" ]]; then
        [[ -f "$TASKS_FILE" ]] || log::die "--tasks-file not found: $TASKS_FILE"
        while IFS= read -r line; do
            line="${line%%#*}"; line="${line#"${line%%[![:space:]]*}"}"; line="${line%"${line##*[![:space:]]}"}"
            [[ -n "$line" ]] && TASKS+=("$line")
        done < "$TASKS_FILE"
    fi
    (( ${#RUN_TASKS[@]} > 0 )) && TASKS+=("${RUN_TASKS[@]}")

    [[ ${#TASKS[@]} -gt 0 ]] || log::die "--run needs tasks: use --task <path> (repeatable), --tasks-file <file>, or --all-tasks"

    log::kv "Tasks"  "${#TASKS[@]}"
    log::kv "Model"  "${MODEL:-default (claude-opus-4.7)}"
    log::kv "Reps"   "${K_RUNS:-1}"

    # script/run.sh single mode takes ONE task; for >1 we hand it a temp --bulk file.
    if [[ ${#TASKS[@]} -eq 1 ]]; then
        log::substep "Single-task mode: ${TASKS[0]}"
        RUN_ARGS=("${TASKS[0]}")
        [[ -n "$MODEL" ]] && RUN_ARGS+=("$MODEL")
        # script/run.sh K is positional after model; if -k set without --model, fall back to its default model.
        if [[ -n "$K_RUNS" ]]; then
            [[ -n "$MODEL" ]] || RUN_ARGS+=("claude-opus-4.7")
            RUN_ARGS+=("$K_RUNS")
        fi
        "$REPO_ROOT/script/run.sh" "${RUN_ARGS[@]}" || log::die "script/run.sh failed for ${TASKS[0]}"
    else
        log::substep "Bulk mode: ${#TASKS[@]} tasks"
        BULK_FILE="$STAGING/.tasks.txt"
        printf '%s\n' "${TASKS[@]}" > "$BULK_FILE"
        RUN_ARGS=(--bulk "$BULK_FILE")
        [[ -n "$MODEL" ]] && RUN_ARGS+=("$MODEL")
        if [[ -n "$K_RUNS" ]]; then
            [[ -n "$MODEL" ]] || RUN_ARGS+=("claude-opus-4.7")
            RUN_ARGS+=("$K_RUNS")
        fi
        "$REPO_ROOT/script/run.sh" "${RUN_ARGS[@]}" || log::die "script/run.sh --bulk failed"
        rm -f "$BULK_FILE"
    fi
    log::ok "Eval run(s) complete"

    # Convert exactly the tasks we just ran (basename -> fuzzy persona match).
    for t in "${TASKS[@]}"; do CONVERT_PERSONAS+=("$(basename "$t")"); done
fi

[[ -d "$REPO_ROOT/$SOURCE_ROOT" ]] || log::die "source root not found: $SOURCE_ROOT (nothing to convert)"

# ---- BACKFILL: repair graded output before converting ------------------------
# Delivery publishes; unlike run.sh's fail-soft auto-bundle, missing run data
# here means shipping bundles without mock APIs — so the first two are fatal.
# All three scripts are offline + idempotent (see their headers).
next_step "Backfill graded output (run data + pass summaries + connector docs)"
log::substep "Run-data backfill: data/environment/ into run dirs missing it"
python3 "$REPO_ROOT/script/backfill_run_data.py" \
    --output-root "$SOURCE_ROOT" --input-root "$INPUT_ROOT" \
    || log::die "backfill_run_data.py failed — bundles would ship without mock APIs"
log::substep "pass_summary.json rebuild (real tests_* counts + combined_reward)"
python3 "$REPO_ROOT/script/backfill_pass_summary.py" "$SOURCE_ROOT" >/dev/null \
    || log::die "backfill_pass_summary.py failed"
log::substep "Connector docs: generate references/+scripts/ for thin connectors"
python3 "$REPO_ROOT/script/backfill_connector_docs.py" >/dev/null \
    || log::warn "connector-docs generation failed; bundles may ship thin connectors"
log::ok "Backfill complete"

# ---- CONVERT raw output -> harbour/bundle format ---------------------------
next_step "Convert raw output -> harbour CLI bundles"
log::kv "Source root" "$SOURCE_ROOT"
log::kv "Staging dir" "$STAGING"

if [[ "${#CONVERT_PERSONAS[@]}" -gt 0 ]]; then
    # Run mode: convert each freshly-run task individually by persona, with a progress bar.
    total_p=${#CONVERT_PERSONAS[@]}
    log::kv "Personas" "$total_p"
    idx=0
    for p in "${CONVERT_PERSONAS[@]}"; do
        idx=$((idx + 1))
        log::progress "$idx" "$total_p" "converting $p"
        python3 "$REPO_ROOT/script/repackage_to_bundle.py" \
            --source-root "$SOURCE_ROOT" --dest-root "$STAGING" --persona "$p" \
            >/dev/null 2>&1 \
            || log::die "conversion failed for persona '$p'"
    done
else
    # Convert-only mode: --persona (one) or --all.
    if [[ -n "$PERSONA" ]]; then
        log::substep "Convert single persona: $PERSONA"
    else
        log::substep "Convert all personas under $SOURCE_ROOT"
    fi
    REPACKAGE_ARGS=(--source-root "$SOURCE_ROOT" --dest-root "$STAGING")
    if [[ -n "$PERSONA" ]]; then REPACKAGE_ARGS+=(--persona "$PERSONA"); else REPACKAGE_ARGS+=(--all); fi
    python3 "$REPO_ROOT/script/repackage_to_bundle.py" "${REPACKAGE_ARGS[@]}"
fi

shopt -s nullglob dotglob
converted=("$STAGING"/*)
# Don't count the temp bulk file if it lingered.
converted=("${converted[@]/$STAGING\/.tasks.txt}")
[[ ${#converted[@]} -gt 0 ]] || log::die "conversion produced no bundles under staging dir"
log::ok "Converted ${#converted[@]} bundle(s)"

# Bundles snapshot data/environment/skills/ from run output frozen at run time;
# enrich any thin connector dirs from the (now rich) live tree before staging.
log::substep "Enriching bundle connector docs from live skills tree"
python3 "$REPO_ROOT/script/backfill_connector_docs.py" \
    --bundle-root "$STAGING" --skills-root "$REPO_ROOT/environment/skills" >/dev/null \
    || log::warn "bundle connector enrich failed; thin connectors may remain"

# ---- STAGE: clone delivery repo & copy bundles in --------------------------
next_step "Clone delivery repo + stage bundles"
log::kv "Repo"         "$TARGET_REPO"
log::kv "Branch"       "$TARGET_BRANCH"
log::kv "Deliverable"  "$DELIVERABLE_DIR/"

# With a token present, fail fast instead of hanging on a prompt (headless/EC2).
[[ -n "$GH_TOKEN_VAL" ]] && export GIT_TERMINAL_PROMPT=0
log::substep "Cloning${GH_TOKEN_VAL:+ (token auth)}"
git clone --depth 1 --branch "$TARGET_BRANCH" "$(_auth_url "$TARGET_REPO")" "$CLONE_DIR" 2>&1 \
    | sed 's/^/  /' \
    || log::die "clone failed (check access/credentials and that branch '$TARGET_BRANCH' exists)"

cd "$CLONE_DIR"

# Optional: route large binaries through Git LFS so git history stays lean.
if [[ "$USE_LFS" -eq 1 ]] && ! command -v git-lfs >/dev/null; then
    if [[ "$LFS_EXPLICIT" -eq 1 ]]; then
        log::die "git-lfs not installed (macOS: brew install git-lfs ; Ubuntu/EC2: sudo apt-get install -y git-lfs)"
    fi
    log::warn "git-lfs not installed — falling back to plain git (install git-lfs to enable LFS, or pass --no-lfs to silence)"
    USE_LFS=0
fi
if [[ "$USE_LFS" -eq 1 ]]; then
    log::substep "Enabling Git LFS for large binary artifacts"
    git lfs install --local >/dev/null
    git lfs track "*.jpg" "*.jpeg" "*.png" "*.gif" "*.webp" "*.pdf" "*.zip" \
                  "*.m4a" "*.mp3" "*.wav" "*.mp4" "*.mov" "*.docx" "*.xlsx" "*.pptx" >/dev/null
    git add .gitattributes
fi

DEST="$CLONE_DIR/$DELIVERABLE_DIR"
mkdir -p "$DEST"            # create folder if it doesn't exist
log::substep "Copying ${#converted[@]} bundle(s) -> $DELIVERABLE_DIR/"
rm -f "$STAGING/.tasks.txt" 2>/dev/null || true
cp -R "$STAGING"/. "$DEST"/
log::ok "Bundles staged in clone"

# ---- COMMIT + PUSH ---------------------------------------------------------
next_step "Commit + push to delivery repo"

git add "$DELIVERABLE_DIR"
if git diff --cached --quiet; then
    log::warn "No changes to commit (delivery repo already up to date)."
    log::section "Done"
    log::summary_box "Delivery summary" \
        "Personas=${#converted[@]}" \
        "Deliverable=$DELIVERABLE_DIR/" \
        "Pushed=no (no changes)"
    exit 0
fi

STAMP="$(date -u '+%Y-%m-%d %H:%M:%SZ')"
COMMIT_MSG="Add ${DELIVERABLE_DIR} (harbour CLI bundles, ${#converted[@]} item(s)) — ${STAMP}"
log::substep "Committing: $COMMIT_MSG"
git commit -m "$COMMIT_MSG" 2>&1 | sed 's/^/  /'

if [[ "$DRY_RUN" -eq 1 ]]; then
    log::warn "--dry-run set: committed locally in the clone but NOT pushing."
    log::hint "Re-run without --dry-run to push to '$TARGET_BRANCH'."
    log::section "Done (dry-run)"
    log::summary_box "Delivery summary" \
        "Personas=${#converted[@]}" \
        "Deliverable=$DELIVERABLE_DIR/" \
        "Pushed=no (dry-run)"
    exit 0
fi

log::substep "Pushing -> $TARGET_BRANCH"
git push origin "$TARGET_BRANCH" 2>&1 | sed 's/^/  /' \
    || log::die "push failed (check push access to the delivery repo)"
log::ok "Pushed ${DELIVERABLE_DIR}/ to $TARGET_BRANCH"

log::section "Done"
log::summary_box "Delivery summary" \
    "Personas=${#converted[@]}" \
    "Deliverable=$DELIVERABLE_DIR/" \
    "Branch=$TARGET_BRANCH" \
    "Pushed=yes"
