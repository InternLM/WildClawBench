import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from src.agents.base import AgentTaskSpec
from src.agents.dsh.runner import DshAgent


def _spec(thinking=None):
    return AgentTaskSpec(task_id="t1", task={"env": ""}, workspace_path="/tmp/ws",
                         prompt="p", timeout_seconds=60, output_dir=Path("/tmp/out"),
                         model="qwen3.8-flash-next", thinking=thinking)


def test_interface_props():
    a = DshAgent()
    assert a.expects_gateway is False
    assert a.transcript_container_path == \
        "/root/.openclaw/agents/main/sessions/chat.jsonl"


def test_bad_rung_fails_before_docker(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("docker must not be touched")
    monkeypatch.setattr("subprocess.run", boom)
    with pytest.raises(ValueError, match="reasoning rung"):
        DshAgent().run_task(_spec(thinking="turbo"))


def test_validate_accepts_allowed_rungs():
    a = DshAgent()
    for t in (None, "off", "low", "medium", "XHIGH"):
        assert a.validate_config(_spec(thinking=t)) in {"off", "low", "medium", "xhigh"}
