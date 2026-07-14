#!/usr/bin/env bash
# make_golden.sh — one command for the complete golden-trajectory flow.
#
#   Phase A (generate)  generate_golden_v3.py  --llm --trajectory=<run> --max-calls
#   Phase B (refine)    refine_golden.py       --repair --rounds  (cleanup + grade-gated repair loop)
#
# Usage:
#   scripts/make_golden.sh "<task name>" <run_number> [rounds] [max_calls]
#
# Examples:
#   scripts/make_golden.sh "Gloria Wiggins --Sumit gupta 2" 2
#   scripts/make_golden.sh "ALDEN_002_haul_out_week" 1 4 4
#
# Notes:
#   - <task name> is the folder name under input/ and output/openclaw/.
#   - Phase A needs Bedrock (--llm); the 503 ARN fallback chain is built in.
#   - Set GENERATE=0 to skip Phase A and only (re)refine an existing golden.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TASK_NAME="${1:?usage: make_golden.sh \"<task name>\" <run_number> [rounds] [max_calls]}"
RUN="${2:?missing run_number}"
ROUNDS="${3:-4}"
MAX_CALLS="${4:-4}"

TASK_DIR="input/${TASK_NAME}"
TRAJ="output/openclaw/${TASK_NAME}/trajectories/claude/run_${RUN}/output.json"
GOLDEN="golden_trajectories/${TASK_NAME}/golden_trajectory.json"

[ -d "$TASK_DIR" ] || { echo "✗ task dir not found: $TASK_DIR" >&2; exit 1; }

echo "════════════════════════════════════════════════════════════════"
echo " make_golden : ${TASK_NAME}  (run ${RUN}, rounds ${ROUNDS}, max-calls ${MAX_CALLS})"
echo "════════════════════════════════════════════════════════════════"

if [ "${GENERATE:-1}" = "1" ]; then
  [ -f "$TRAJ" ] || { echo "✗ reference run not found: $TRAJ" >&2; exit 1; }
  echo "▶ Phase A — generate (LLM + graft real tools from run ${RUN})"
  GOLDEN_LLM_ATTEMPTS="${GOLDEN_LLM_ATTEMPTS:-4}" \
    python3 system_prompts/generate_golden_v3.py "$TASK_DIR" \
      --llm --trajectory="$TRAJ" --max-calls="$MAX_CALLS"
else
  echo "▶ Phase A — skipped (GENERATE=0); refining existing golden"
fi

echo
echo "▶ Phase B — refine (cleanup + grade-gated repair loop)"
python3 system_prompts/refine_golden.py "$GOLDEN" \
  --task="$TASK_DIR" --repair --rounds="$ROUNDS"

echo
echo "✓ done → $GOLDEN"
echo "  score → golden_trajectories/${TASK_NAME}/score_golden.json"
