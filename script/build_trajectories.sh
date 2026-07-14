#!/usr/bin/env bash
#
# build_trajectories.sh — assemble a per-task `trajectories/` tree.
#
# For every task it can find, this creates:
#
#   trajectories/<task_id>/
#       input/          <- copy of input/<persona dir>/        (matched via task.yaml task_id)
#       output/         <- copy of output/openclaw/<task_id>/
#       output_bundle/  <- copy of output_bundle/<task_id>/
#
# Task identity is the `task_id` declared in input/<dir>/task.yaml. The input
# folder name (e.g. "Ruth Armstrong") often differs from the task_id
# (e.g. RUTH_001_october_consultation_crunch); outputs and bundles are keyed by
# task_id, so we resolve the mapping rather than assuming the names line up.
#
# The set of tasks is the UNION of: input task.yaml task_ids, output/openclaw/*,
# and output_bundle/*. A task missing one of the three pieces still gets a folder
# with whatever exists (and a warning).
#
# Usage:
#   scripts/build_trajectories.sh [DEST_DIR]
#
#   DEST_DIR   where to build the tree (default: <repo>/trajectories)
#
# Each task folder is also zipped to trajectories/<task_id>.zip so a single
# task can be shared on its own.
#
# Env:
#   CLEAN=1    remove DEST_DIR before building (default: merge into existing)
#   NOZIP=1    skip creating the per-task .zip archives

set -euo pipefail

# --- locate repo root (script lives in <repo>/scripts) --------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

INPUT_ROOT="$REPO_ROOT/input"
OUTPUT_ROOT="$REPO_ROOT/output/openclaw"
BUNDLE_ROOT="$REPO_ROOT/output_bundle"
DEST_DIR="${1:-$REPO_ROOT/trajectories}"

# copy command: prefer rsync (clean, handles re-runs), fall back to cp -R
copy_into() {  # copy_into <src_dir> <dst_dir>
  local src="$1" dst="$2"
  mkdir -p "$dst"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$src"/ "$dst"/
  else
    rm -rf "${dst:?}"/* 2>/dev/null || true
    cp -R "$src"/. "$dst"/
  fi
}

# read task_id from a task.yaml (first `task_id:` line); empty if absent
read_task_id() {  # read_task_id <task.yaml path>
  [ -f "$1" ] || return 0
  sed -n 's/^[[:space:]]*task_id:[[:space:]]*//p' "$1" | head -1 | tr -d '"'"'"' \t\r'
}

# --- discover tasks -------------------------------------------------------
# Portable to bash 3.2 (macOS default) -> no associative arrays. We use two
# temp files: a task_id<TAB>input_dir map, and the unique set of task_ids.
MAP_FILE="$(mktemp)"
IDS_FILE="$(mktemp)"
trap 'rm -f "$MAP_FILE" "$IDS_FILE"' EXIT

if [ -d "$INPUT_ROOT" ]; then
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    tid="$(read_task_id "$d/task.yaml")"
    [ -n "$tid" ] || tid="$(basename "$d")"   # fall back to dir name
    printf '%s\t%s\n' "$tid" "$d" >> "$MAP_FILE"
    printf '%s\n' "$tid" >> "$IDS_FILE"
  done < <(find "$INPUT_ROOT" -mindepth 1 -maxdepth 1 -type d)
fi

# add task_ids that only show up in output / bundle
for root in "$OUTPUT_ROOT" "$BUNDLE_ROOT"; do
  [ -d "$root" ] || continue
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    basename "$d" >> "$IDS_FILE"
  done < <(find "$root" -mindepth 1 -maxdepth 1 -type d)
done

# resolve input dir for a task_id from the map (first match)
input_dir_for() {  # input_dir_for <task_id>
  awk -F'\t' -v id="$1" '$1==id {print $2; exit}' "$MAP_FILE"
}

if [ ! -s "$IDS_FILE" ]; then
  echo "No tasks found under $INPUT_ROOT, $OUTPUT_ROOT, or $BUNDLE_ROOT" >&2
  exit 1
fi

# --- (re)build destination ------------------------------------------------
if [ "${CLEAN:-0}" = "1" ]; then
  echo "CLEAN=1 -> removing $DEST_DIR"
  rm -rf "$DEST_DIR"
fi
mkdir -p "$DEST_DIR"

echo "Building trajectories tree at: $DEST_DIR"
echo

built=0
while IFS= read -r tid; do
  [ -n "$tid" ] || continue
  task_dest="$DEST_DIR/$tid"
  in_src="$(input_dir_for "$tid")"
  out_src="$OUTPUT_ROOT/$tid"
  bun_src="$BUNDLE_ROOT/$tid"

  echo "• $tid"
  mkdir -p "$task_dest"

  if [ -n "$in_src" ] && [ -d "$in_src" ]; then
    copy_into "$in_src" "$task_dest/input"
    echo "    input         <- ${in_src#$REPO_ROOT/}"
  else
    echo "    input         (MISSING)"
  fi

  if [ -d "$out_src" ]; then
    copy_into "$out_src" "$task_dest/output"
    echo "    output        <- ${out_src#$REPO_ROOT/}"
  else
    echo "    output        (MISSING)"
  fi

  if [ -d "$bun_src" ]; then
    copy_into "$bun_src" "$task_dest/output_bundle"
    echo "    output_bundle <- ${bun_src#$REPO_ROOT/}"
  else
    echo "    output_bundle (MISSING)"
  fi

  # zip the task folder so it can be sent on its own: trajectories/<task_id>.zip
  if [ "${NOZIP:-0}" != "1" ]; then
    if command -v zip >/dev/null 2>&1; then
      rm -f "$DEST_DIR/$tid.zip"
      # run from DEST_DIR so the archive contains <task_id>/... at its root
      ( cd "$DEST_DIR" && zip -rq "$tid.zip" "$tid" )
      echo "    zip           -> ${DEST_DIR#$REPO_ROOT/}/$tid.zip"
    else
      echo "    zip           (SKIPPED: 'zip' not installed)"
    fi
  fi

  built=$((built + 1))
done < <(sort -u "$IDS_FILE")

echo
echo "Done. Assembled $built task folder(s) under $DEST_DIR"
