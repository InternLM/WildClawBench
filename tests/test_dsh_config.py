import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
import yaml
from src.agents.dsh.config import ALLOWED_RUNGS, patch_entry_yaml, resolve_rung


def test_default_xhigh():
    assert resolve_rung(None) == "xhigh"


def test_case_insensitive():
    assert resolve_rung("MEDIUM") == "medium"


def test_exact_rung_set():
    assert ALLOWED_RUNGS == {"off", "low", "medium", "xhigh"}


def test_unsupported_raises():
    with pytest.raises(ValueError, match="reasoning rung"):
        resolve_rung("max")


def test_patch_yaml_is_loader_array():
    parsed = yaml.safe_load(patch_entry_yaml("wcb-lb", "qwen3.8-flash-next", "xhigh"))
    assert isinstance(parsed, list)
    assert parsed[0]["id"] == "agent-default-model"
    assert parsed[0]["config"]["provider"] == "wcb-lb"
    assert parsed[0]["config"]["reasoningEffort"] == "xhigh"
