#!/usr/bin/env python3
"""Re-run a trajectory's deterministic pytest suite against its captured state.

Rebuilds `input/agent_state.json` from the run's post-injection store snapshot
(+ the assistant's response text from output.json), then runs pytest on
`input/test_outputs.py`. No Docker, mock stack, or agent run required — works
fully offline from a published trajectory folder.

LIMITATION: the API *audit* log (which endpoints the agent called) is not
persisted in the trajectory, so audit-dependent checkers cannot pass. The
resulting score is therefore a FLOOR (store-state + response-text checks only).

Usage:
    python3 script/regrade_trajectory.py trajectories/Dinesh_Ives_01
    python3 script/regrade_trajectory.py trajectories/*           # all of them
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.state_extractor import build_agent_state  # noqa: E402


def _assistant_text(output_json: Path) -> str:
    """Concatenate assistant text from an OpenClaw output.json (messages[].message)."""
    if not output_json.is_file():
        return ""
    try:
        msgs = json.loads(output_json.read_text(encoding="utf-8")).get("messages", [])
    except (OSError, json.JSONDecodeError):
        return ""

    def text_of(content):
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            out = []
            for b in content:
                if isinstance(b, dict) and isinstance(b.get("text"), str):
                    out.append(b["text"])
                elif isinstance(b, str):
                    out.append(b)
            return "\n".join(out)
        return ""

    parts = []
    for row in msgs:
        msg = row.get("message") if isinstance(row, dict) else None
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            parts.append(text_of(msg.get("content")))
    return "\n".join(p for p in parts if p)


def rebuild_state(traj: Path) -> Path | None:
    """Write input/agent_state.json from the trajectory's after-injection snapshot."""
    runs = sorted(traj.glob("output-raw/trajectories/*/run_*"))
    if not runs:
        return None
    run = runs[-1]
    snap = run / "snapshot" / "workspace_after" / "mock_data"
    if not snap.is_dir():
        return None
    state = build_agent_state(
        store_snapshot_dir=snap,
        last_response=_assistant_text(run / "output.json"),
    )
    dest = traj / "input" / "agent_state.json"
    dest.write_text(json.dumps(state, ensure_ascii=False, default=str), encoding="utf-8")
    return dest


def regrade(traj: Path) -> str:
    suite = traj / "input" / "test_outputs.py"
    if not suite.is_file():
        return f"{traj.name:<28} SKIP (no test_outputs.py)"
    if rebuild_state(traj) is None:
        return f"{traj.name:<28} SKIP (no usable snapshot — likely a stack-killed run)"
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", suite.name, "-q", "--no-header"],
        cwd=suite.parent, capture_output=True, text=True,
    )
    last = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout.strip() else "(no output)"
    return f"{traj.name:<28} {last}"


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv] or sorted(Path("trajectories").glob("*"))
    targets = [t for t in targets if t.is_dir()]
    if not targets:
        print("no trajectory directories found", file=sys.stderr)
        return 2
    print(f"Re-grading {len(targets)} trajectory(ies) — score is a FLOOR (no audit log):\n")
    for t in targets:
        print("  " + regrade(t))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
