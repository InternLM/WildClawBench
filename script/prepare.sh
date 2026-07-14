#!/usr/bin/env bash
# WildClawBench (LiteLLM/Bedrock fork) - Bootstrap script
#
# Replaces upstream's workspace/-video-fetcher prepare.sh entirely.
# This fork uses input/ persona tasks and a pre-built agent image, so the
# YouTube/SAM3/dot_git steps are gone. What remains is the host-side bootstrap
# needed before `bash script/run.sh ...` will work on a clean clone.
#
# Usage:
#   bash script/prepare.sh                         # full bootstrap
#   bash script/prepare.sh --skip-image-check      # skip Images/ LFS sanity
#   bash script/prepare.sh --skip-mocks            # skip kensei3-mocks:v1 build
#   bash script/prepare.sh --skip-tasks            # skip HF tasks/ clone
#   bash script/prepare.sh --validate-overlays     # ALSO walk input/*/mock_data/
#   bash script/prepare.sh --strict                # fail on overlay CSV warnings
#   bash script/prepare.sh -h | --help             # show this header
#
# Steps performed (in order; each is idempotent and skip-if-done):
#   [1/7] Host tool preflight   (python3 >= 3.10, docker, git, git-lfs, pv)
#   [2/7] Python deps           (wheelhouse/ offline install if populated, else pip)
#   [3/7] .env materialization  (cp .env.example .env if .env missing; no overwrite)
#   [4/7] Images/ LFS check     (resolve LFS pointers for Images/, input/*/data/,
#                                input/*/mock_data/*/file_blobs/)
#   [5/7] Mock-stack image      (eager build of kensei3-mocks:v1 via mock_stack.py)
#   [6/7] HF tasks/ clone       (idempotent; skipped if tasks/ non-empty)
#   [7/7] Overlay validation    (opt-in --validate-overlays)
#
# Exit codes: 0=ok, 1=fatal preflight or step failure, 2=arg validation.
#
# Cross-script consistency:
#   - cd to repo root mirrors script/run.sh's pattern (relative paths everywhere).
#   - Log helpers (info/ok/warn/err/die) mirror deliver.sh exactly.
#   - Install cascade (brew/apt-get/dnf/yum/apk) generalizes run.sh's _install_pv.
#   - Mock-image build uses the SAME inline python3 -c that run.sh:preflight_mock_image
#     uses. Source of truth stays src/utils/mock_stack.py.
#   - Overlay validation reuses environment/_mutable_store.read_csv_with_ctx for
#     byte-identical error messages with the in-container loader.

set -euo pipefail
cd "$(dirname "$0")/.."

# Shared UX library (colors, step banners, progress bars, summary box).
# Single source of truth; gated on NO_COLOR + isatty.
# shellcheck source=script/lib/log.sh
source "$(dirname "$0")/lib/log.sh"

print_usage(){
    cat <<'EOF'
WildClawBench bootstrap — host preflight + python deps + .env + agent image + mock fleet + tasks/

USAGE
  bash script/prepare.sh                       # full bootstrap (idempotent)
  bash script/prepare.sh --skip-image-check    # skip Images/ + input/ LFS sanity
  bash script/prepare.sh --skip-mocks          # skip kensei3-mocks:v1 eager build
  bash script/prepare.sh --skip-tasks          # skip HF tasks/ clone
  bash script/prepare.sh --validate-overlays   # also walk input/*/mock_data/ CSVs
  bash script/prepare.sh --strict              # treat overlay shape warnings as fatal
  bash script/prepare.sh -h | --help           # show this help

STEPS (each idempotent and skip-if-done)
  [1/7] Host tool preflight   python3 >=3.10, docker, git, git-lfs, pv
  [2/7] Python deps           wheelhouse/ offline if populated, else PyPI
  [3/7] .env materialization  cp .env.example → .env if .env missing
  [4/7] Images/ LFS check     resolve LFS pointers for Images/ + input/*/data/ + input/*/mock_data/*/file_blobs/
  [5/7] Mock-stack image      eager build of kensei3-mocks:v1
  [6/7] HF tasks/ clone       skipped if tasks/ non-empty; HF_TASKS_REPO env overrides default repo
  [7/7] Overlay validation    opt-in --validate-overlays

EXIT CODES
  0  success
  1  fatal preflight or step failure
  2  invalid argument

NOTES
  * NO_COLOR=1 or piped stdout strips ANSI from your terminal.
  * Run BEFORE bash script/run.sh on a fresh clone.
EOF
}

# ---- flag parsing ----------------------------------------------------------
SKIP_IMAGE_CHECK=0
SKIP_MOCKS=0
SKIP_TASKS=0
VALIDATE_OVERLAYS=0
STRICT=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)            print_usage; exit 0 ;;
        --skip-image-check)   SKIP_IMAGE_CHECK=1; shift ;;
        --skip-mocks)         SKIP_MOCKS=1; shift ;;
        --skip-tasks)         SKIP_TASKS=1; shift ;;
        --validate-overlays)  VALIDATE_OVERLAYS=1; shift ;;
        --strict)             STRICT=1; shift ;;
        *) err "unknown flag: $1"; print_usage; exit 2 ;;
    esac
done

# ---- shared install cascade (generalized from run.sh:_install_pv) ----------
# Best-effort installer for a single package; tries brew/apt-get/dnf/yum/apk in
# order. sudo only if passwordless. Returns 0 on success, 1 if unavailable.
# Usage: _install_pkg <pkgname> [<brew-name>] [<apt-name>] [<dnf-name>] [<apk-name>]
# Per-manager name overrides default to the canonical name.
_install_pkg(){
    local canon="$1"; shift || true
    local brew_n="${1:-$canon}";  [[ $# -gt 0 ]] && shift || true
    local apt_n="${1:-$canon}";   [[ $# -gt 0 ]] && shift || true
    local dnf_n="${1:-$canon}";   [[ $# -gt 0 ]] && shift || true
    local apk_n="${1:-$canon}";   [[ $# -gt 0 ]] && shift || true
    local sudo_cmd=""
    if [[ $EUID -ne 0 ]] && command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; then
        sudo_cmd="sudo"
    fi
    case "$(uname -s)" in
        Darwin)
            if command -v brew >/dev/null 2>&1; then
                if brew install "$brew_n" >/dev/null 2>&1; then return 0; fi
                warn "brew install $brew_n failed"
            else
                warn "Homebrew not present; install '$canon' manually: brew install $brew_n"
            fi
            ;;
        Linux)
            if command -v apt-get >/dev/null 2>&1; then
                if ${sudo_cmd} apt-get update -qq >/dev/null 2>&1 && \
                   ${sudo_cmd} apt-get install -y -qq "$apt_n" >/dev/null 2>&1; then return 0; fi
                warn "apt-get install $apt_n failed (need sudo without password)"
            elif command -v dnf >/dev/null 2>&1; then
                if ${sudo_cmd} dnf install -y -q "$dnf_n" >/dev/null 2>&1; then return 0; fi
                warn "dnf install $dnf_n failed (need sudo without password)"
            elif command -v yum >/dev/null 2>&1; then
                if ${sudo_cmd} yum install -y -q "$dnf_n" >/dev/null 2>&1; then return 0; fi
                warn "yum install $dnf_n failed (need sudo without password)"
            elif command -v apk >/dev/null 2>&1; then
                if ${sudo_cmd} apk add --no-cache "$apk_n" >/dev/null 2>&1; then return 0; fi
                warn "apk add $apk_n failed (need sudo without password)"
            else
                warn "no supported package manager found for '$canon'"
            fi
            ;;
        *)
            warn "unsupported OS '$(uname -s)' for auto-install of '$canon'"
            ;;
    esac
    return 1
}


# [1/7] Host tool preflight
step_host_preflight(){
    log::step 1 7 "Host tool preflight"

    # python3 >= 3.10 (run_batch.py uses dict-union, typed generics, PEP 604)
    if ! command -v python3 >/dev/null 2>&1; then
        die "python3 not on PATH; install Python >= 3.10 before running this script"
    fi
    local py_ver
    py_ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    case "$py_ver" in
        3.10|3.11|3.12|3.13|3.14|3.15) ok "python3 $py_ver" ;;
        *) die "python3 $py_ver < 3.10 required by eval/run_batch.py; upgrade Python" ;;
    esac

    # pip
    if ! python3 -m pip --version >/dev/null 2>&1; then
        die "pip not available for python3; install python3-pip and re-run"
    fi
    ok "pip available"

    # docker (run.sh:preflight_docker re-verifies; we only check CLI presence)
    if ! command -v docker >/dev/null 2>&1; then
        die "docker CLI not on PATH; install Docker Desktop / docker-ce before running"
    fi
    if ! docker info >/dev/null 2>&1; then
        warn "docker daemon not reachable; run.sh's preflight will fail until it is"
    else
        ok "docker daemon reachable"
    fi

    # git (we use it for the HF clone)
    command -v git >/dev/null 2>&1 || die "git not on PATH; install git and re-run"
    ok "git $(git --version | awk '{print $3}')"

    # git-lfs (Images/wildclawbench-ubuntu_v1.3.tar is LFS-tracked; HF dataset
    # is too). We treat absence as a fatal error here -- a fresh clone without
    # LFS would silently leave 134-byte pointer files in place of the agent
    # image tarball, which is a much worse failure mode than installing now.
    if ! command -v git-lfs >/dev/null 2>&1; then
        warn "git-lfs missing; installing ..."
        if _install_pkg git-lfs; then
            git lfs install --skip-repo >/dev/null 2>&1 || true
            ok "git-lfs installed"
        else
            die "git-lfs install failed; install it manually (https://git-lfs.com) and re-run"
        fi
    else
        ok "git-lfs $(git-lfs version | awk '{print $1}' | head -1)"
    fi

    # pv (run.sh would also try to install this; we front-load it so the first
    # `docker load` shows progress instead of going dark for ~10 minutes).
    if ! command -v pv >/dev/null 2>&1; then
        info "pv missing; trying to install (used by run.sh for docker-load progress) ..."
        if _install_pkg pv; then ok "pv installed"; else warn "pv unavailable; docker-load will be silent"; fi
    else
        ok "pv $(pv --version | head -1 | awk '{print $2}')"
    fi
}


# [2/7] Python deps (wheelhouse offline -> pip online fallback)
step_python_deps(){
    log::step 2 7 "Python deps"
    if [[ ! -f requirements.txt ]]; then
        warn "requirements.txt not found at repo root; skipping Python deps install"
        return 0
    fi

    # wheelhouse/ is reserved for offline installs on air-gapped EC2 boxes.
    # If it contains .whl files we use --no-index; otherwise we fall back to
    # online pip. (debhouse/skill-deps/ is build-time for the agent image, not
    # for the host orchestrator, so we don't touch it here.)
    local wheels
    wheels="$(find wheelhouse -maxdepth 1 -name '*.whl' 2>/dev/null | head -1 || true)"
    if [[ -n "$wheels" ]]; then
        info "installing from wheelhouse/ (offline) ..."
        python3 -m pip install --no-index --find-links=wheelhouse -r requirements.txt \
            || die "wheelhouse install failed; ensure all wheels for requirements.txt are present"
    else
        info "installing from PyPI (online) ..."
        python3 -m pip install -r requirements.txt \
            || die "pip install failed; re-run with network access or populate wheelhouse/"
    fi
    ok "Python deps installed"
}


# [3/7] .env materialization (no overwrite)
step_env_file(){
    log::step 3 7 ".env materialization"
    if [[ -f .env ]]; then
        ok ".env already exists (not overwriting); run.sh:preflight_env_file will validate keys"
        return 0
    fi
    if [[ ! -f .env.example ]]; then
        warn ".env.example missing; create a .env manually before running script/run.sh"
        return 0
    fi
    cp .env.example .env
    warn ".env created from .env.example -- EDIT IT to fill in KENSEI_AWS_BEARER_TOKEN,"
    warn "  KENSEI_AWS_REGION, KENSEI_BEDROCK_MODEL_ARN, and any *_API_KEY values you need."
    warn "  run.sh's preflight will WARN (not fail) on missing values, by design."
}


# [4/7] Images/ LFS sanity (also resolves input/ media + mock_data blobs)
# git-lfs leaves a tiny pointer file (~134 bytes) when LFS isn't installed at
# clone time. We detect the pointer shape by size, not content, because the
# user may have installed git-lfs after cloning and we want a single
# `git lfs pull` to rescue everything.
_looks_like_lfs_pointer(){
    local f="$1"
    [[ -f "$f" ]] || return 1
    local sz
    sz="$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null || echo 0)"
    [[ "$sz" -lt 1024 ]]
}

step_image_check(){
    log::step 4 7 "LFS sanity — Images/ + input/*/data/ + input/*/mock_data/"

    local need_pull=0
    local tar="Images/wildclawbench-ubuntu_v1.3.tar"
    if [[ -f "$tar" ]] && _looks_like_lfs_pointer "$tar"; then
        warn "$tar looks like an LFS pointer (<1KB); will git lfs pull"
        need_pull=1
    elif [[ ! -f "$tar" ]]; then
        warn "$tar missing -- run.sh will try to docker-load from tag/SHA instead;"
        warn "  see https://huggingface.co/datasets/<your-fork>/Images if you need the tarball"
    fi

    # Sample a handful of input/ media + overlay file_blobs/ files for pointer shape.
    # Non-recursive: same scope as eval/run_batch.py:_resolve_task_apis (which only
    # bind-mounts top-level files under input/<task>/mock_data/<api>/) plus the
    # one-level-up file_blobs/ fallback that _mutable_store.extract_file_content_text
    # honors (the per-API DATA_DIR/file_blobs/ -> blob_dir.parent fallback at L982).
    local sample
    sample="$(
        { find input -maxdepth 3 -type f \( -name '*.pdf' -o -name '*.mp4' -o -name '*.mp3' -o -name '*.wav' -o -name '*.png' -o -name '*.jpg' -o -name '*.zip' \) 2>/dev/null
          find input -maxdepth 5 -type d -name file_blobs 2>/dev/null | while read -r d; do find "$d" -maxdepth 1 -type f 2>/dev/null; done
        } | head -40
    )"
    local saw_pointer=0
    while IFS= read -r f; do
        [[ -z "$f" ]] && continue
        if _looks_like_lfs_pointer "$f"; then
            saw_pointer=1
            warn "  $f looks like an LFS pointer"
        fi
    done <<< "$sample"
    [[ $saw_pointer -eq 1 ]] && need_pull=1

    if [[ $need_pull -eq 1 ]]; then
        info "running 'git lfs pull' for Images/ + input/* ..."
        git lfs pull --include='Images/*' --include='input/*' \
            || warn "git lfs pull partial; some pointers may remain. Inspect manually."
        ok "LFS resolution attempted"
    else
        ok "no LFS pointers detected in Images/ or input/ media sample"
    fi
}


# [5/7] Eager mock-stack image build (kensei3-mocks:v1)
step_mock_stack(){
    log::step 5 7 "Mock-stack image (kensei3-mocks:v1, content-hash cached)"
    # SAME call run.sh:preflight_mock_image makes. Idempotent: src/utils/mock_stack
    # short-circuits if the image already exists at the current content hash.
    # We invoke it eagerly so first-run latency is paid at bootstrap time rather
    # than at the first `bash script/run.sh`.
    if ! python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '.')
from src.utils.mock_stack import build_mock_image_if_needed
build_mock_image_if_needed(Path('environment'))
" 2>&1; then
        die "mock-stack image build failed; see error above"
    fi
    ok "kensei3-mocks:v1 ready"
}


# [6/7] HuggingFace tasks/ clone (skipped if non-empty)
step_tasks_clone(){
    log::step 6 7 "tasks/ dataset (HuggingFace)"
    # eval/run_batch.py:80 reads TASKS_DIR = ROOT_DIR / os.environ.get("TASKS_SUBDIR", "tasks").
    # If tasks/ is missing or empty we clone the public HF dataset.
    # HF_TASKS_REPO env var lets operators point at a fork that matches the
    # input/<task>/ persona shape instead of the upstream public dataset.
    local hf_repo="${HF_TASKS_REPO:-https://huggingface.co/datasets/internlm/WildClawBench}"
    if [[ -d tasks ]] && [[ -n "$(ls -A tasks 2>/dev/null)" ]]; then
        ok "tasks/ already populated; not re-cloning ($hf_repo)"
        return 0
    fi
    info "cloning $hf_repo -> tasks/"
    git lfs install --skip-repo >/dev/null 2>&1 || true
    if ! git clone --depth 1 "$hf_repo" tasks 2>&1; then
        warn "git clone failed (network or auth issue?); tasks/ may be needed by some categories"
        warn "  for offline boxes, manually rsync the dataset to tasks/ before running script/run.sh"
        return 0
    fi
    ok "tasks/ cloned ($(find tasks -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ') categories)"
}


# [7/7] Overlay validation (opt-in --validate-overlays)
# Walks input/*/mock_data/<api>/*.csv and runs the SAME csv shape check the
# mock containers do at boot, via environment/_mutable_store.read_csv_with_ctx.
# Catches: duplicate header columns, ragged rows (unquoted commas), non-utf-8,
# csv.Error. PK collision warnings are handled inside each <api>_data.py via
# _populate_table and require the registered schema to surface -- they're out
# of scope here (would need per-API import to run, which is expensive). Shape
# errors are the high-value, cheap subset.
step_validate_overlays(){
    if [[ $VALIDATE_OVERLAYS -eq 0 ]]; then
        log::step 7 7 "Overlay validation (skipped; pass --validate-overlays to enable)"
        return 0
    fi
    log::step 7 7 "Overlay validation"

    local errs=0
    local out
    out="$(python3 - <<'PY' 2>&1
import sys
from pathlib import Path
sys.path.insert(0, 'environment')
try:
    from _mutable_store import read_csv_with_ctx, CoerceError
except Exception as exc:  # pragma: no cover
    print(f"FATAL: could not import _mutable_store: {exc}", file=sys.stderr)
    sys.exit(2)

errs = 0
checked = 0
for task_dir in sorted(Path("input").glob("*/")):
    mock_dir = task_dir / "mock_data"
    if not mock_dir.is_dir():
        continue
    for api_dir in sorted(mock_dir.glob("*/")):
        api = api_dir.name
        for csv_path in sorted(api_dir.glob("*.csv")):
            table = csv_path.stem
            checked += 1
            try:
                read_csv_with_ctx(csv_path, api=api, table=table)
            except CoerceError as exc:
                errs += 1
                print(f"ERROR: {csv_path}: {exc}")
            except Exception as exc:
                errs += 1
                print(f"ERROR: {csv_path}: unexpected {type(exc).__name__}: {exc}")
print(f"checked={checked} errors={errs}")
sys.exit(1 if errs else 0)
PY
)"
    local rc=$?
    printf '%s\n' "$out"
    if [[ $rc -eq 0 ]]; then
        ok "all overlay CSVs pass shape check"
    elif [[ $STRICT -eq 1 ]]; then
        die "overlay validation found errors and --strict was set"
    else
        warn "overlay validation found errors (pass --strict to make this fatal)"
    fi
}

log::section "WildClawBench Bootstrap"
log::kv "Repo" "$(pwd)"
log::kv "Skip" "image-check=$SKIP_IMAGE_CHECK mocks=$SKIP_MOCKS tasks=$SKIP_TASKS strict=$STRICT overlays=$VALIDATE_OVERLAYS"

step_host_preflight
step_python_deps
step_env_file
[[ $SKIP_IMAGE_CHECK -eq 0 ]] && step_image_check
[[ $SKIP_MOCKS       -eq 0 ]] && step_mock_stack
[[ $SKIP_TASKS       -eq 0 ]] && step_tasks_clone
step_validate_overlays

log::section "Bootstrap complete"
log::summary_box "Next steps" \
    "Edit=.env (fill credentials)" \
    "Smoke=bash script/run.sh" \
    "Single=bash script/run.sh --task input/amanda_hayes_01" \
    "Bulk=bash script/run.sh --bulk my_tasks.txt"
