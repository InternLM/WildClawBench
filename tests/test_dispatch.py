import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_cli_accepts_dsh_backend():
    from src.utils.cli_args import build_run_batch_parser
    p = build_run_batch_parser("m", 1)
    args = p.parse_args(["--task", "x.md", "--agent-backend", "dsh"])
    assert args.agent_backend == "dsh"


def test_run_sh_routes_dsh():
    text = (ROOT / "script" / "run.sh").read_text()
    assert "wildclawbench-dsh:v0.1" in text
    assert "--agent-backend dsh" in text


def test_run_batch_dispatches_dsh():
    text = (ROOT / "eval" / "run_batch.py").read_text()
    assert "DshAgent" in text
