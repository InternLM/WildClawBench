#!/usr/bin/env bash
# WildClawBench shared shell UX library.
#
# Sourced by script/run.sh, script/prepare.sh, deliver.sh to provide a uniform
# look-and-feel for end-to-end runs: colored prefixes, step banners, progress
# bars, and summary boxes. Designed for:
#
#   - tty:    rich ANSI output (colors, progress bar redraws via \r)
#   - pipe:   plain ASCII, no escape codes, no carriage-return tricks
#   - file:   same as pipe (so tee'd logs/<...>.log stay readable)
#
# Respects NO_COLOR (https://no-color.org) and only emits ANSI when stdout is
# a tty AND NO_COLOR is unset.
#
# Public surface (namespaced under log::):
#
#   log::info <msg>                    Info line  (cyan [INFO] prefix)
#   log::ok   <msg>                    Success    (green [OK] prefix)
#   log::warn <msg>                    Warning    (yellow [WARN] prefix, stderr)
#   log::err  <msg>                    Error      (red [ERR] prefix, stderr)
#   log::die  <msg>                    Error then exit 1
#   log::hint <msg>                    Dim secondary line (no prefix; indented)
#
#   log::section <title>               Top-level banner (full-width rule + title)
#   log::step    <n> <total> <title>   Numbered step banner   "▶ [n/total] title"
#   log::substep <title>               Sub-step header        "  ↳ title"
#
#   log::progress <current> <total> <label>
#       Renders a progress bar. On tty: redraws in place via \r.
#       On non-tty: emits a single percentage line every 5% to keep logs small.
#       Always emits a final newline once <current> == <total>.
#
#   log::summary_box <title> <kv_pair...>
#       Renders a key/value summary box. Each kv_pair is "Key=Value".
#       Box widths auto-fit content. Used for end-of-run summaries.
#
#   log::kv <key> <value>              Single "  Key.... : Value" aligned line
#
#   log::rule [<title>]                Horizontal rule (optionally with title)
#
# Single-source-of-truth invariant:
#   ALL user-facing shell output in script/run.sh, script/prepare.sh, deliver.sh
#   MUST go through this library. Bare echo/printf are reserved for verbatim
#   command output (e.g. the tail of a failed log).

# Source guard (idempotent if sourced multiple times).
if [[ -n "${__WCB_LOG_SH_SOURCED:-}" ]]; then
    return 0 2>/dev/null || true
fi
__WCB_LOG_SH_SOURCED=1

# ---- color/tty detection ---------------------------------------------------
# Recompute on demand so tests can override TERM/NO_COLOR/stdout.
log::__color_enabled() {
    [[ -z "${NO_COLOR:-}" ]] && [[ -t 1 ]]
}

log::__init_colors() {
    if log::__color_enabled; then
        __WCB_C_DIM=$'\033[2m'
        __WCB_C_BOLD=$'\033[1m'
        __WCB_C_RED=$'\033[0;31m'
        __WCB_C_GREEN=$'\033[0;32m'
        __WCB_C_YELLOW=$'\033[0;33m'
        __WCB_C_BLUE=$'\033[0;34m'
        __WCB_C_MAGENTA=$'\033[0;35m'
        __WCB_C_CYAN=$'\033[0;36m'
        __WCB_C_GREY=$'\033[0;90m'
        __WCB_C_RESET=$'\033[0m'
    else
        __WCB_C_DIM=''   __WCB_C_BOLD=''
        __WCB_C_RED=''   __WCB_C_GREEN=''
        __WCB_C_YELLOW='' __WCB_C_BLUE=''
        __WCB_C_MAGENTA='' __WCB_C_CYAN=''
        __WCB_C_GREY=''  __WCB_C_RESET=''
    fi
}
log::__init_colors

# ---- terminal width --------------------------------------------------------
log::__width() {
    local w
    if [[ -t 1 ]] && command -v tput >/dev/null 2>&1; then
        w=$(tput cols 2>/dev/null || echo 80)
    else
        w=${COLUMNS:-80}
    fi
    # Clamp to [60, 120] — wide enough for banners, narrow enough for terminals.
    if   (( w < 60 ));  then w=60
    elif (( w > 120 )); then w=120
    fi
    printf '%s' "$w"
}

# ---- simple log lines ------------------------------------------------------
log::info() { printf '%s[INFO]%s  %s\n' "$__WCB_C_CYAN" "$__WCB_C_RESET" "$*"; }
log::ok()   { printf '%s[OK]%s    %s\n' "$__WCB_C_GREEN" "$__WCB_C_RESET" "$*"; }
log::warn() { printf '%s[WARN]%s  %s\n' "$__WCB_C_YELLOW" "$__WCB_C_RESET" "$*" >&2; }
log::err()  { printf '%s[ERR]%s   %s\n' "$__WCB_C_RED" "$__WCB_C_RESET" "$*" >&2; }
log::die()  { log::err "$*"; exit 1; }
log::hint() { printf '       %s%s%s\n' "$__WCB_C_GREY" "$*" "$__WCB_C_RESET"; }

log::kv() {
    local key="$1"; shift
    local value="$*"
    printf '       %s%-22s%s : %s\n' "$__WCB_C_GREY" "$key" "$__WCB_C_RESET" "$value"
}

# ---- banners ---------------------------------------------------------------
log::__repeat() {
    # log::__repeat <char> <count>
    local ch="$1" n="$2" s=""
    while (( n > 0 )); do s+="$ch"; n=$(( n - 1 )); done
    printf '%s' "$s"
}

log::rule() {
    local title="${1:-}"
    local w; w=$(log::__width)
    if [[ -z "$title" ]]; then
        printf '%s%s%s\n' "$__WCB_C_GREY" "$(log::__repeat '─' "$w")" "$__WCB_C_RESET"
    else
        local label=" $title "
        local pad=$(( w - ${#label} - 4 ))
        (( pad < 4 )) && pad=4
        printf '%s── %s%s%s%s %s%s\n' \
            "$__WCB_C_GREY" \
            "$__WCB_C_BOLD" "$title" "$__WCB_C_RESET" "$__WCB_C_GREY" \
            "$(log::__repeat '─' "$pad")" \
            "$__WCB_C_RESET"
    fi
}

log::section() {
    local title="$*"
    local w; w=$(log::__width)
    printf '\n%s%s%s\n' "$__WCB_C_BLUE" "$(log::__repeat '━' "$w")" "$__WCB_C_RESET"
    printf '%s%s %s%s\n' "$__WCB_C_BOLD" "$__WCB_C_BLUE" "$title" "$__WCB_C_RESET"
    printf '%s%s%s\n\n' "$__WCB_C_BLUE" "$(log::__repeat '━' "$w")" "$__WCB_C_RESET"
}

log::step() {
    local n="$1" total="$2"
    shift 2
    local title="$*"
    printf '\n%s▶%s %s[%s/%s]%s %s%s%s\n' \
        "$__WCB_C_MAGENTA" "$__WCB_C_RESET" \
        "$__WCB_C_BOLD" "$n" "$total" "$__WCB_C_RESET" \
        "$__WCB_C_BOLD" "$title" "$__WCB_C_RESET"
}

log::substep() {
    printf '  %s↳%s %s\n' "$__WCB_C_CYAN" "$__WCB_C_RESET" "$*"
}

# ---- progress bar ----------------------------------------------------------
# log::progress <current> <total> [<label>]
#
# Renders a single-line bar:
#   [████████████░░░░░░░░] 60% (6/10)  label
# tty: redraws via \r; emits newline on completion.
# non-tty: emits a "[N/total] label (PCT%)" line only when PCT crosses a 5%
# boundary, to avoid log spam.
__WCB_LAST_PROGRESS_PCT=-1
log::progress() {
    local current="$1" total="$2"
    shift 2 || true
    local label="${*:-}"
    (( total <= 0 )) && total=1
    (( current > total )) && current=$total
    local pct=$(( current * 100 / total ))
    local bar_w=24
    local filled=$(( current * bar_w / total ))
    local empty=$(( bar_w - filled ))
    local bar_filled bar_empty
    bar_filled=$(log::__repeat '█' "$filled")
    bar_empty=$(log::__repeat '░' "$empty")

    if [[ -t 1 ]] && [[ -z "${NO_COLOR:-}" ]]; then
        printf '\r  %s[%s%s%s]%s %3d%% (%d/%d) %s%s%s\033[K' \
            "$__WCB_C_GREY" \
            "$__WCB_C_GREEN" "$bar_filled" "$__WCB_C_GREY$bar_empty" "$__WCB_C_GREY" \
            "$pct" "$current" "$total" \
            "$__WCB_C_DIM" "$label" "$__WCB_C_RESET"
        if (( current >= total )); then
            printf '\n'
            __WCB_LAST_PROGRESS_PCT=-1
        fi
    else
        # Non-tty: emit a line only on 5%-boundary crossings.
        local bucket=$(( pct / 5 * 5 ))
        if (( bucket != __WCB_LAST_PROGRESS_PCT )) || (( current >= total )); then
            printf '  [progress] %d/%d (%d%%) %s\n' "$current" "$total" "$pct" "$label"
            __WCB_LAST_PROGRESS_PCT=$bucket
            (( current >= total )) && __WCB_LAST_PROGRESS_PCT=-1
        fi
    fi
}

# ---- summary box -----------------------------------------------------------
# log::summary_box <title> <kv_pair...>
# Each kv_pair = "Key=Value". Renders:
#
#   ┌─ Summary ────────────────────┐
#   │ Total runs ........... : 12  │
#   │ Succeeded ............ : 11  │
#   │ Failed ............... :  1  │
#   └──────────────────────────────┘
log::summary_box() {
    local title="$1"; shift
    local -a pairs=("$@")

    # Compute widths.
    local max_key=0 max_val=0 pair k v
    for pair in ${pairs[@]+"${pairs[@]}"}; do
        k="${pair%%=*}"
        v="${pair#*=}"
        (( ${#k} > max_key )) && max_key=${#k}
        (( ${#v} > max_val )) && max_val=${#v}
    done
    # Width math (must be exact so top and bottom borders align):
    #   top row    = "┌─ " + title + " " + top_pad('─') + "┐"  -> visible width = top_pad + len(title) + 5
    #   bottom row = "└" + (box_w - 1)*'─' + "┘"               -> visible width = box_w + 1
    # For top == bottom: top_pad = box_w - len(title) - 4.
    # To keep top_pad >= 2 WITHOUT clamping (which would desync widths), ensure
    # box_w >= len(title) + 6.
    local content_w=$(( max_key + max_val + 6 ))   # "Key" + " : " + "Value" + 2 pad
    local title_min=$(( ${#title} + 6 ))           # guarantees top_pad >= 2
    local box_w=$content_w
    (( title_min > box_w )) && box_w=$title_min
    (( box_w < 40 )) && box_w=40

    local top_pad=$(( box_w - ${#title} - 4 ))

    printf '\n%s┌─ %s%s%s%s %s┐%s\n' \
        "$__WCB_C_BLUE" \
        "$__WCB_C_BOLD" "$title" "$__WCB_C_RESET" "$__WCB_C_BLUE" \
        "$(log::__repeat '─' "$top_pad")" "$__WCB_C_RESET"

    for pair in ${pairs[@]+"${pairs[@]}"}; do
        k="${pair%%=*}"
        v="${pair#*=}"
        # "│ <key padded to max_key> : <value padded to box_w-max_key-5> │"
        local inside_w=$(( box_w - max_key - 6 ))
        (( inside_w < ${#v} )) && inside_w=${#v}
        printf '%s│%s %s%-*s%s : %-*s %s│%s\n' \
            "$__WCB_C_BLUE" "$__WCB_C_RESET" \
            "$__WCB_C_GREY" "$max_key" "$k" "$__WCB_C_RESET" \
            "$inside_w" "$v" \
            "$__WCB_C_BLUE" "$__WCB_C_RESET"
    done

    printf '%s└%s┘%s\n\n' \
        "$__WCB_C_BLUE" "$(log::__repeat '─' $(( box_w - 1 )))" "$__WCB_C_RESET"
}

# ---- back-compat shims for existing scripts --------------------------------
# Old scripts use info/ok/warn/err/die unprefixed. Provide them as aliases so
# the migration is mechanical and reversible. The new code should prefer the
# log:: namespace for explicit intent.
info() { log::info "$@"; }
ok()   { log::ok   "$@"; }
warn() { log::warn "$@"; }
err()  { log::err  "$@"; }
die()  { log::die  "$@"; }
