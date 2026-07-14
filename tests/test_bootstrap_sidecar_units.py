"""Unit tests for eval/bootstrap_sidecar.py — the shared-sidecar bootstrap.

`main()` drives the Docker-heavy setup (network, sidecar, cc-bridge) but every
side-effecting call is a function imported into the bootstrap_sidecar module
namespace, so we can monkeypatch them to run fully OFFLINE:
  * no docker, no network, no boto3/Bedrock, no sleeps.
  * Config.from_env is replaced with a hand-built fake config.
  * STDOUT `key=value` lines are captured via capsys and parsed back.

We drive `main()` by setting sys.argv and reading its int return code + the
emitted key=value contract lines. Style follows the sys.path-insert bootstrap
of tests/test_score_json_last_resort.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import eval.bootstrap_sidecar as bs  # noqa: E402


# ---------------------------------------------------------------------------
# Fake Config — mirrors the attributes bootstrap_sidecar.main() reads.
# ---------------------------------------------------------------------------


class _FakeConfig:
    def __init__(self, tmp_path, *, litellm_on=True, oauth=False, yaml_ok=True):
        self._litellm_on = litellm_on
        self.use_claude_oauth = oauth
        self.cc_account_pool = ""
        self.cc_bridge_secret = "secret-xyz"
        self.work_dir = tmp_path / "work"
        self.bedrock_sonnet_arn = "arn:sonnet"
        self.bedrock_inference_arn = "arn:opus"
        self.bedrock_region = "ap-south-1"
        self.aws_bearer_token = "aws-bearer"
        self.openai_api_key = ""
        self.openai_whisper_api_key = ""
        self.anthropic_api_key = "sk-ant-xxx"
        self.litellm_master_key = "sk-litellm-master"
        self._yaml_ok = yaml_ok

    def litellm_enabled(self) -> bool:
        return self._litellm_on


def _install_fake_config(monkeypatch, cfg):
    monkeypatch.setattr(bs.Config, "from_env", classmethod(lambda cls: cfg))


def _stub_all_sidecar_calls(monkeypatch, *, yaml="model_list: []\n",
                            healthy=True, upstream_ok=True):
    """Replace every Docker/LLM-touching function in the bs namespace with a
    no-op / configurable stub. Returns a dict recording which were called."""
    calls: dict = {"start_litellm": [], "create_network": [], "pull": 0}

    monkeypatch.setattr(bs, "pull_litellm_image", lambda *a, **k: calls.__setitem__("pull", calls["pull"] + 1))
    monkeypatch.setattr(bs, "ensure_litellm_headroom_image", lambda *a, **k: None)
    monkeypatch.setattr(bs, "create_network", lambda name, *a, **k: calls["create_network"].append(name))
    monkeypatch.setattr(bs, "build_litellm_config_yaml", lambda *a, **k: yaml)
    monkeypatch.setattr(bs, "start_litellm", lambda **k: calls["start_litellm"].append(k))
    monkeypatch.setattr(bs, "stop_litellm", lambda *a, **k: None)
    monkeypatch.setattr(bs, "wait_for_litellm_healthy", lambda *a, **k: healthy)
    monkeypatch.setattr(bs, "verify_litellm_upstream_reachable", lambda *a, **k: (upstream_ok, "detail"))
    # bridge functions (only reached under OAuth)
    monkeypatch.setattr(bs, "start_bridge", lambda **k: None)
    monkeypatch.setattr(bs, "stop_bridge", lambda *a, **k: None)
    monkeypatch.setattr(bs, "wait_for_bridge_healthy", lambda *a, **k: True)
    monkeypatch.setattr(bs, "wait_for_bridge_host_port", lambda *a, **k: True)
    return calls


def _run_main(monkeypatch, argv=("--name-suffix", "999-20260101_000000")):
    monkeypatch.setattr(sys, "argv", ["bootstrap_sidecar.py", *argv])
    return bs.main()


def _parse_emitted(capsys) -> dict:
    out = capsys.readouterr().out
    kv: dict = {}
    for line in out.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            kv[k] = v
    return kv


# ---------------------------------------------------------------------------
# _emit / _log helpers
# ---------------------------------------------------------------------------


class TestEmitAndLog:
    def test_emit_writes_keyvalue_to_stdout(self, capsys):
        bs._emit("name", "wcbsh-sidecar-1")
        out = capsys.readouterr().out
        assert out == "name=wcbsh-sidecar-1\n"

    def test_emit_empty_value(self, capsys):
        bs._emit("network", "")
        assert capsys.readouterr().out == "network=\n"

    def test_log_goes_to_stderr_not_stdout(self, capsys):
        bs._log("hello")
        cap = capsys.readouterr()
        assert cap.out == ""
        assert "[bootstrap_sidecar] hello" in cap.err


# ---------------------------------------------------------------------------
# litellm disabled -> emit 8 empty keys and return 0 (OpenRouter fallback mode)
# ---------------------------------------------------------------------------


class TestLitellmDisabledEarlyExit:
    def test_returns_zero_and_emits_empty_contract(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path, litellm_on=False)
        _install_fake_config(monkeypatch, cfg)
        # No sidecar stubs needed; the disabled branch never touches Docker.
        rc = _run_main(monkeypatch)
        assert rc == 0
        kv = _parse_emitted(capsys)
        # Contract: eight keys, all empty.
        for key in ("name", "network", "usage_log", "yaml_path", "master_key",
                    "cc_bridge", "cc_bridge_url", "cc_bridge_host_port",
                    "cc_bridge_host_url"):
            assert kv.get(key) == "", f"{key} should be empty in disabled mode"


# ---------------------------------------------------------------------------
# yaml build returns empty -> strict refusal, return 2
# ---------------------------------------------------------------------------


class TestYamlRefusal:
    def test_empty_yaml_returns_2(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path)
        _install_fake_config(monkeypatch, cfg)
        _stub_all_sidecar_calls(monkeypatch, yaml="")  # build_litellm_config_yaml -> ""
        rc = _run_main(monkeypatch)
        assert rc == 2
        # Nothing emitted on the parseable STDOUT contract (refusal precedes emit).
        assert _parse_emitted(capsys) == {}


# ---------------------------------------------------------------------------
# Non-OAuth happy path -> full contract emitted, return 0
# ---------------------------------------------------------------------------


class TestNonOauthHappyPath:
    def test_full_contract_emitted_and_files_written(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path)
        _install_fake_config(monkeypatch, cfg)
        calls = _stub_all_sidecar_calls(monkeypatch)
        rc = _run_main(monkeypatch, argv=("--name-suffix", "42-20260101_010101"))
        assert rc == 0

        kv = _parse_emitted(capsys)
        assert kv["name"] == "wcbsh-sidecar-42-20260101_010101"
        assert kv["network"] == "wcbsh-net-42-20260101_010101"
        assert kv["master_key"] == "sk-litellm-master"
        # OAuth off -> cc_bridge fields empty.
        assert kv["cc_bridge"] == ""
        assert kv["cc_bridge_url"] == ""
        assert kv["cc_bridge_host_port"] == ""
        assert kv["cc_bridge_host_url"] == ""

        # Names honor the cleanup-orphans invariants (no `ll-`, no `k3net-`).
        assert "ll-" not in kv["name"]
        assert "k3net-" not in kv["network"]

        # Config yaml + usage jsonl were actually written to work_dir.
        yaml_path = Path(kv["yaml_path"])
        usage_log = Path(kv["usage_log"])
        assert yaml_path.is_file()
        assert usage_log.is_file()
        assert yaml_path.read_text() == "model_list: []\n"

        # Sidecar was started exactly once with our chosen names.
        assert len(calls["start_litellm"]) == 1
        started = calls["start_litellm"][0]
        assert started["container_name"] == "wcbsh-sidecar-42-20260101_010101"
        assert started["network"] == "wcbsh-net-42-20260101_010101"
        assert calls["create_network"] == ["wcbsh-net-42-20260101_010101"]
        assert calls["pull"] == 1

    def test_usage_file_has_owner_only_perms(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path)
        _install_fake_config(monkeypatch, cfg)
        _stub_all_sidecar_calls(monkeypatch)
        rc = _run_main(monkeypatch)
        assert rc == 0
        kv = _parse_emitted(capsys)
        usage_log = Path(kv["usage_log"])
        # S-003 hardening: chmod 0o600 on the usage file.
        assert (usage_log.stat().st_mode & 0o777) == 0o600
        assert (usage_log.parent.stat().st_mode & 0o777) == 0o700

    def test_skip_upstream_verify_short_circuits_probe(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path)
        _install_fake_config(monkeypatch, cfg)
        called = {"verify": 0}

        def _boom(*a, **k):
            called["verify"] += 1
            return (False, "should not be called")

        _stub_all_sidecar_calls(monkeypatch)
        monkeypatch.setattr(bs, "verify_litellm_upstream_reachable", _boom)
        rc = _run_main(
            monkeypatch,
            argv=("--name-suffix", "7-20260101_020202", "--skip-upstream-verify"),
        )
        assert rc == 0
        assert called["verify"] == 0  # probe skipped entirely


# ---------------------------------------------------------------------------
# Failure ladders: start_litellm raises (3), health fails (4), upstream (5)
# ---------------------------------------------------------------------------


class TestFailureLadder:
    def test_start_litellm_failure_returns_3(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path)
        _install_fake_config(monkeypatch, cfg)
        _stub_all_sidecar_calls(monkeypatch)

        def _raise(**k):
            raise RuntimeError("docker run failed")

        stopped = {"n": 0}
        monkeypatch.setattr(bs, "start_litellm", _raise)
        monkeypatch.setattr(bs, "stop_litellm", lambda *a, **k: stopped.__setitem__("n", stopped["n"] + 1))
        rc = _run_main(monkeypatch)
        assert rc == 3
        assert stopped["n"] == 1  # cleanup attempted
        assert _parse_emitted(capsys) == {}  # no contract emitted

    def test_unhealthy_sidecar_returns_4(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path)
        _install_fake_config(monkeypatch, cfg)
        _stub_all_sidecar_calls(monkeypatch, healthy=False)
        rc = _run_main(monkeypatch)
        assert rc == 4
        assert _parse_emitted(capsys) == {}

    def test_upstream_unreachable_returns_5(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path)
        _install_fake_config(monkeypatch, cfg)
        _stub_all_sidecar_calls(monkeypatch, upstream_ok=False)
        rc = _run_main(monkeypatch)
        assert rc == 5
        assert _parse_emitted(capsys) == {}


# ---------------------------------------------------------------------------
# OAuth path — pool-resolution guards (no docker: bridge fns stubbed)
# ---------------------------------------------------------------------------


class TestOauthPoolGuards:
    def test_empty_pool_resolves_to_zero_files_returns_6(self, tmp_path, monkeypatch, capsys):
        cfg = _FakeConfig(tmp_path, oauth=True)
        cfg.cc_account_pool = str(tmp_path / "nonexistent.json")  # not a real file
        _install_fake_config(monkeypatch, cfg)
        _stub_all_sidecar_calls(monkeypatch)
        rc = _run_main(monkeypatch)
        # zero readable pool files -> return 6
        assert rc == 6

    def test_pool_files_in_multiple_dirs_returns_6(self, tmp_path, monkeypatch, capsys):
        d1 = tmp_path / "a"
        d2 = tmp_path / "b"
        d1.mkdir()
        d2.mkdir()
        f1 = d1 / "acct1.json"
        f2 = d2 / "acct2.json"
        f1.write_text("{}")
        f2.write_text("{}")
        cfg = _FakeConfig(tmp_path, oauth=True)
        cfg.cc_account_pool = f"{f1}:{f2}"  # two dirs
        _install_fake_config(monkeypatch, cfg)
        _stub_all_sidecar_calls(monkeypatch)
        rc = _run_main(monkeypatch)
        assert rc == 6

    def test_oauth_happy_path_emits_bridge_fields(self, tmp_path, monkeypatch, capsys):
        pool_dir = tmp_path / "oauth_pool"
        pool_dir.mkdir()
        acct = pool_dir / "acct.json"
        acct.write_text("{}")
        cfg = _FakeConfig(tmp_path, oauth=True)
        cfg.cc_account_pool = str(acct)
        _install_fake_config(monkeypatch, cfg)
        _stub_all_sidecar_calls(monkeypatch)
        # Pin the host port so we don't touch a real socket bind path decision;
        # main() reads WCB_CC_BRIDGE_HOST_PORT from env when preset.
        monkeypatch.setenv("WCB_CC_BRIDGE_HOST_PORT", "54321")
        rc = _run_main(monkeypatch, argv=("--name-suffix", "9-20260101_030303"))
        assert rc == 0
        kv = _parse_emitted(capsys)
        assert kv["cc_bridge"] == "wcbsh-cc-bridge-9-20260101_030303"
        assert kv["cc_bridge_url"].endswith(":" + str(bs.CC_BRIDGE_INTERNAL_PORT))
        assert kv["cc_bridge_host_port"] == "54321"
        assert kv["cc_bridge_host_url"] == "http://127.0.0.1:54321"
        # WCB_CC_BRIDGE_SECRET must have been published for child processes.
        import os
        assert os.environ.get("WCB_CC_BRIDGE_SECRET") == "secret-xyz"


# ---------------------------------------------------------------------------
# Argparse contract
# ---------------------------------------------------------------------------


class TestArgparse:
    def test_missing_required_name_suffix_exits(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["bootstrap_sidecar.py"])
        with pytest.raises(SystemExit) as exc:
            bs.main()
        assert exc.value.code != 0
