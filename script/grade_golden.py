#!/usr/bin/env python3
"""Grade a golden_trajectory.json with the real council judge.

Mirrors scripts/regrade.py but reads the golden trajectory file directly
instead of a run dir's output.json. Evidence = condensed transcript (the
golden's deliverables live inline in its toolCall args / toolResults).
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(REPO_ROOT / ".env")

from eval.run_batch import _condense_transcript_for_judge  # noqa: E402
from src.utils.grading import grade_with_rubric  # noqa: E402


def main() -> int:
    task = sys.argv[1] if len(sys.argv) > 1 else "ALDEN_002_haul_out_week"
    golden = REPO_ROOT / "golden_trajectories" / task / "golden_trajectory.json"
    rubric_path = REPO_ROOT / "input" / task / "rubric.json"
    prompt_path = REPO_ROOT / "input" / task / "prompt.txt"

    rubrics = json.loads(rubric_path.read_text(encoding="utf-8"))
    if isinstance(rubrics, dict):
        rubrics = rubrics.get("rubrics") or []
    traj = json.loads(golden.read_text(encoding="utf-8"))
    transcript = _condense_transcript_for_judge(traj)
    task_description = prompt_path.read_text(encoding="utf-8").strip() if prompt_path.is_file() else ""

    print(f"[golden] task        = {task}", file=sys.stderr)
    print(f"[golden] rubric      = {len(rubrics)} criteria", file=sys.stderr)
    print(f"[golden] transcript  = {len(transcript):,} chars", file=sys.stderr)
    print(f"[golden] grading with council …", file=sys.stderr)

    with tempfile.TemporaryDirectory() as tmp:
        scores = grade_with_rubric(
            rubrics,
            task_description,
            Path(tmp),               # empty workspace; evidence comes from transcript
            transcript_text=transcript,
            use_council=True,
        )

    out = golden.parent / "score_golden.json"
    out.write_text(json.dumps(scores, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n==================== GOLDEN GRADE ====================")
    if scores.get("error"):
        print(f"ERROR: {scores['error']}")
        return 1
    print(f"overall_score              = {scores.get('overall_score')}")
    print(f"rubric_weights_percentage  = {scores.get('rubric_weights_percentage')}%")
    print(f"criteria total={scores.get('criteria_total')} "
          f"passed={scores.get('criteria_passed')} "
          f"failed={scores.get('criteria_failed')} "
          f"abstained={scores.get('criteria_abstained')}")
    council = scores.get("judge_council") or {}
    if council:
        surv = council.get("surviving") or []
        fail = council.get("failed") or []
        print(f"council surviving = {len(surv)}/{len(surv)+len(fail)}")
        for f in fail:
            print(f"  FAILED member: {f.get('model','?')} — {str(f.get('error',''))[:200]}")
    # List any non-passing criteria so we can see what blocks 100%.
    miss = [c for c in (scores.get("criteria") or []) if not c.get("passed")]
    if miss:
        print(f"\n--- {len(miss)} non-passing criteria ---")
        for c in miss:
            pol = "NEG" if not c.get("is_positive") else "POS"
            print(f"  [{pol} w={c.get('weight')}] {c.get('criterion','')[:90]}")
            print(f"       → {str(c.get('rationale',''))[:200]}")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
