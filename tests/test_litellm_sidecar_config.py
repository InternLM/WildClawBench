"""Config-generation + health/upstream probe tests for src/utils/litellm_sidecar.py.

Complements tests/test_docker_env_validation.py Section E (which already covers
start_litellm's docker-run argv and flag-injection hardening). This file covers
the *other* public surface of the sidecar module:

  * build_litellm_config_yaml — model-list routing across the four upstream
    branches (OAuth bridge / Bedrock / Anthropic-direct / OpenAI), the always-on
    embedding + image-alias fallback blocks, callback wiring, and the global
    litellm_settings / general_settings envelope. We call the function and parse
    the emitted YAML (import yaml), asserting structure rather than raw strings.

  * wait_for_litellm_healthy / wait_for_bridge_healthy — the docker-exec probe
    loops. subprocess.run + time are monkeypatched to simulate healthy,
    unhealthy (non-zero rc), and timeout paths deterministically (no real sleep,
    no docker, no network).

  * verify_litellm_upstream_reachable — the single docker-exec synthetic
    round-trip; success / HTTP-error / connection-error return shapes.

  * wait_for_bridge_host_port — the ONLY host-side urllib probe; urllib.request
    .urlopen is monkeypatched for healthy / refused / empty-port paths.

These tests do NOT spawn containers or touch the network. They are fully offline
and deterministic. Where a branch pins a quirk of the CURRENT implementation
(e.g. the `if not model_blocks: return ""` guard is unreachable because embedding
blocks are appended unconditionally) the assertion is annotated so a future
refactor knows the pin is intentional, not incidental.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import litellm_sidecar as sidecar  # noqa: E402


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _parse(cfg_yaml: str) -> dict:
    """Parse the emitted config and sanity-check it is a mapping."""
    doc = yaml.safe_load(cfg_yaml)
    assert isinstance(doc, dict), f"config did not parse to a dict: {doc!r}"
    return doc


def _model_names(doc: dict) -> list[str]:
    return [m["model_name"] for m in doc["model_list"]]


def _block(doc: dict, name: str) -> dict | None:
    for m in doc["model_list"]:
        if m["model_name"] == name:
            return m
    return None


def _params(doc: dict, name: str) -> dict:
    blk = _block(doc, name)
    assert blk is not None, f"model {name!r} not in {_model_names(doc)}"
    return blk["litellm_params"]


# Names that build_litellm_config_yaml ALWAYS appends regardless of inputs
# (mock embedding routes — see module lines 309-321).
_ALWAYS_EMBEDDINGS = [
    "text-embedding-3-small",
    "text-embedding-3-large",
    "text-embedding-ada-002",
]


# ===========================================================================
# Section A — build_litellm_config_yaml: envelope + always-present blocks
# ===========================================================================


class TestConfigEnvelope:
    def test_no_inputs_still_returns_nonempty_config(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # The `if not model_blocks: return ""` guard (module ~line 360) is
        # unreachable: the three embedding routes are appended unconditionally
        # before that check, so model_blocks is never empty and the function
        # never returns "". A truly empty config would need that guard reachable.
        cfg = sidecar.build_litellm_config_yaml()
        assert cfg != "", "current impl never returns empty (embedding blocks always added)"
        doc = _parse(cfg)
        assert _model_names(doc) == _ALWAYS_EMBEDDINGS

    def test_embedding_routes_are_mock_mode(self):
        doc = _parse(sidecar.build_litellm_config_yaml())
        for name in _ALWAYS_EMBEDDINGS:
            blk = _block(doc, name)
            assert blk is not None
            assert blk["litellm_params"]["mock_response"] == [0.0]
            assert blk["model_info"]["mode"] == "embedding"

    def test_global_litellm_settings_present_and_stable(self):
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:x"))
        ls = doc["litellm_settings"]
        assert ls["drop_params"] is True
        assert ls["modify_params"] is True
        assert ls["telemetry"] is False
        # Max-extension timeouts (user policy m1386) — pinned so a future
        # "normalize back down" edit trips this test.
        assert ls["num_retries"] == 10
        assert ls["request_timeout"] == 86400
        assert ls["stream_timeout"] == 86400
        assert ls["reasoning_auto_summary"] is True

    def test_transcription_cache_scoped_to_transcription_only(self):
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:x"))
        ls = doc["litellm_settings"]
        assert ls["cache"] is True
        assert ls["cache_params"]["type"] == "local"
        # Must stay scoped to (a)transcription so judge-council determinism and
        # chat/opus caching are untouched.
        assert ls["cache_params"]["supported_call_types"] == [
            "transcription",
            "atranscription",
        ]

    def test_general_settings_present(self):
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:x"))
        gs = doc["general_settings"]
        assert gs["master_key"] == "os.environ/LITELLM_MASTER_KEY"
        assert gs["store_model_in_db"] is False


# ===========================================================================
# Section B — build_litellm_config_yaml: Bedrock branch
# ===========================================================================


class TestBedrockBranch:
    def test_opus_aliases_both_registered(self):
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:foo"))
        names = _model_names(doc)
        assert "claude-opus-4.7" in names
        assert "claude-opus-4-6" in names

    def test_opus_model_id_split_carries_arn(self):
        # The RECOGNIZABLE name lives in `model:` (so adaptive-thinking detection
        # fires) while the real ARN lives in `model_id:` for routing.
        arn = "arn:aws:bedrock:ap-south-1:1:application-inference-profile/abc123"
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn=arn, aws_region="us-east-1"))
        p = _params(doc, "claude-opus-4.7")
        assert p["model"] == "bedrock/anthropic.claude-opus-4-6-v1"
        assert p["model_id"] == arn
        assert p["aws_region_name"] == "us-east-1"

    def test_opus_default_region_when_blank(self):
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:x", aws_region=""))
        assert _params(doc, "claude-opus-4.7")["aws_region_name"] == "ap-south-1"

    def test_opus_thinking_shape_is_adaptive_summarized(self):
        # Bedrock 400s enabled+budget_tokens on this ARN; adaptive+summarized is
        # the only shape that yields populated thinking.
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:x"))
        p = _params(doc, "claude-opus-4.7")
        assert p["thinking"] == {"type": "adaptive", "display": "summarized"}
        assert p["output_config"] == {"effort": "high"}

    def test_opus_cache_control_injection_and_costs(self):
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:x"))
        p = _params(doc, "claude-opus-4.7")
        assert p["cache_control_injection_points"] == [
            {"location": "message", "role": "system"}
        ]
        assert p["input_cost_per_token"] == 0.000005
        assert p["output_cost_per_token"] == 0.000025
        assert p["cache_read_input_token_cost"] == 0.0000005
        assert p["cache_creation_input_token_cost"] == 0.00000625
        assert p["stream_options"] == {"include_usage": True}

    def test_bedrock_adds_image_alias_via_converse(self):
        # With Bedrock but no OpenAI, the gpt-4o* fallback ids alias to the
        # bedrock/converse route (not the opus /v1/messages route).
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:img"))
        for fid in ("anthropic/gpt-4o", "anthropic/gpt-4o-mini", "gpt-4o", "gpt-4o-mini"):
            p = _params(doc, fid)
            assert p["model"] == "bedrock/converse/arn:img"
            assert p["aws_region_name"] == "ap-south-1"


# ===========================================================================
# Section C — build_litellm_config_yaml: OAuth-bridge branch (highest priority)
# ===========================================================================


class TestOAuthBranch:
    def test_oauth_route_when_url_present(self):
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                use_claude_oauth=True, bridge_url="http://bridge:8765"
            )
        )
        p = _params(doc, "claude-opus-4.7")
        assert p["model"] == "anthropic/claude-opus-4-8"
        assert p["api_base"] == "http://bridge:8765"
        assert p["api_key"] == "os.environ/WCB_CC_STUB_KEY"

    def test_oauth_thinking_shape_is_enabled_budget(self):
        # Anthropic-direct requires enabled+budget_tokens (NOT the Bedrock
        # adaptive shape) — pins the deliberate per-branch divergence.
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                use_claude_oauth=True, bridge_url="http://b"
            )
        )
        p = _params(doc, "claude-opus-4.7")
        assert p["thinking"] == {"type": "enabled", "budget_tokens": 32000}

    def test_oauth_bridge_secret_header_and_zero_cost(self):
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                use_claude_oauth=True, bridge_url="http://b"
            )
        )
        p = _params(doc, "claude-opus-4.7")
        assert p["extra_headers"] == {
            "x-wcb-bridge-secret": "os.environ/WCB_CC_BRIDGE_SECRET"
        }
        # Subscription usage reports $0 in litellm; audit cost is emitted
        # separately by the oauth usage callback.
        assert p["input_cost_per_token"] == 0
        assert p["output_cost_per_token"] == 0
        assert p["cache_read_input_token_cost"] == 0
        assert p["cache_creation_input_token_cost"] == 0

    def test_oauth_beats_bedrock_when_both_present(self):
        # use_claude_oauth+bridge_url is the FIRST branch; Bedrock ARN present
        # simultaneously must NOT win.
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                use_claude_oauth=True, bridge_url="http://b", bedrock_arn="arn:x"
            )
        )
        assert _params(doc, "claude-opus-4.7")["model"] == "anthropic/claude-opus-4-8"

    def test_oauth_flag_without_bridge_url_falls_through_to_bedrock(self):
        # The branch guard is `use_claude_oauth AND bridge_url`; a missing
        # bridge_url must fall through to the Bedrock branch, not silently skip.
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                use_claude_oauth=True, bridge_url="", bedrock_arn="arn:x"
            )
        )
        assert (
            _params(doc, "claude-opus-4.7")["model"]
            == "bedrock/anthropic.claude-opus-4-6-v1"
        )


# ===========================================================================
# Section D — build_litellm_config_yaml: Anthropic-direct fallback branch
# ===========================================================================


class TestAnthropicFallbackBranch:
    def test_anthropic_direct_model_and_key(self):
        doc = _parse(sidecar.build_litellm_config_yaml(anthropic_api_key="sk-ant"))
        p = _params(doc, "claude-opus-4.7")
        assert p["model"] == "anthropic/claude-opus-4-20250514"
        assert p["api_key"] == "os.environ/ANTHROPIC_API_KEY"

    def test_anthropic_direct_omits_thinking(self):
        # /v1/messages on the direct API 400s the Bedrock-specific adaptive
        # thinking shape, so this branch intentionally requests no thinking.
        doc = _parse(sidecar.build_litellm_config_yaml(anthropic_api_key="sk-ant"))
        assert "thinking" not in _params(doc, "claude-opus-4.7")

    def test_anthropic_branch_loses_to_bedrock(self):
        # Bedrock branch precedes the anthropic elif; ARN present must win.
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                bedrock_arn="arn:x", anthropic_api_key="sk-ant"
            )
        )
        assert (
            _params(doc, "claude-opus-4.7")["model"]
            == "bedrock/anthropic.claude-opus-4-6-v1"
        )

    def test_anthropic_only_registers_no_image_alias(self):
        # image_alias is "" when neither OpenAI nor Bedrock is configured, so
        # the gpt-4o* fallback blocks are absent on the anthropic-only path.
        doc = _parse(sidecar.build_litellm_config_yaml(anthropic_api_key="sk-ant"))
        for fid in ("anthropic/gpt-4o", "gpt-4o", "gpt-4o-mini"):
            assert _block(doc, fid) is None


# ===========================================================================
# Section E — build_litellm_config_yaml: OpenAI branch (gpt-5.5 / whisper / audio)
# ===========================================================================


class TestOpenAIBranch:
    def test_gpt55_routes_through_responses_bridge(self):
        doc = _parse(sidecar.build_litellm_config_yaml(openai_api_key="sk-oai"))
        p = _params(doc, "gpt-5.5")
        assert p["model"] == "openai/responses/gpt-5.5"
        assert p["reasoning_effort"] == {"effort": "high", "summary": "auto"}

    def test_whisper_route_uses_default_openai_key(self):
        doc = _parse(sidecar.build_litellm_config_yaml(openai_api_key="sk-oai"))
        assert _params(doc, "whisper-1")["api_key"] == "os.environ/OPENAI_API_KEY"

    def test_whisper_route_uses_dedicated_whisper_key_when_provided(self):
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                openai_api_key="sk-oai", openai_whisper_api_key="sk-whis"
            )
        )
        p = _params(doc, "whisper-1")
        assert p["api_key"] == "os.environ/OPENAI_API_KEY_WHISPER"
        # The transcribe fallback aliases pick up the same dedicated key ref.
        assert (
            _params(doc, "gpt-4o-mini-transcribe")["api_key"]
            == "os.environ/OPENAI_API_KEY_WHISPER"
        )

    def test_audio_fallback_aliases_registered_to_whisper(self):
        doc = _parse(sidecar.build_litellm_config_yaml(openai_api_key="sk-oai"))
        for fid in ("gpt-4o-mini-transcribe", "gpt-4o-transcribe"):
            assert _params(doc, fid)["model"] == "openai/whisper-1"

    def test_openai_image_alias_prefers_gpt55(self):
        # When OpenAI is configured the image-fallback ids alias to gpt-5.5
        # (OpenAI preferred over Bedrock).
        doc = _parse(
            sidecar.build_litellm_config_yaml(openai_api_key="sk-oai", bedrock_arn="arn:x")
        )
        for fid in ("anthropic/gpt-4o", "anthropic/gpt-4o-mini", "gpt-4o", "gpt-4o-mini"):
            p = _params(doc, fid)
            assert p["model"] == "openai/responses/gpt-5.5"
            assert p["api_key"] == "os.environ/OPENAI_API_KEY"


# ===========================================================================
# Section F — build_litellm_config_yaml: Sonnet judge route + callback wiring
# ===========================================================================


class TestSonnetAndCallbacks:
    def test_sonnet_route_keeps_converse_infix(self):
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_sonnet_arn="arn:sonnet"))
        p = _params(doc, "claude-sonnet-4-6")
        assert p["model"] == "bedrock/converse/anthropic.claude-sonnet-4-6"
        assert p["model_id"] == "arn:sonnet"
        assert p["thinking"] == {"type": "adaptive", "display": "summarized"}
        assert p["input_cost_per_token"] == 0.000003
        assert p["cache_read_input_token_cost"] == 0.0000003

    def test_no_callbacks_key_when_none_enabled(self):
        doc = _parse(sidecar.build_litellm_config_yaml(bedrock_arn="arn:x"))
        assert "callbacks" not in doc["litellm_settings"]

    def test_usage_callback_only(self):
        doc = _parse(
            sidecar.build_litellm_config_yaml(bedrock_arn="arn:x", enable_usage_callback=True)
        )
        assert doc["litellm_settings"]["callbacks"] == [
            "litellm_usage_callback.proxy_handler_instance"
        ]

    def test_all_three_callbacks_ordered(self):
        # Order is load-bearing: usage, then headroom (pre-call compressor),
        # then oauth usage. Pins the append sequence.
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                bedrock_arn="arn:x",
                enable_usage_callback=True,
                enable_headroom_callback=True,
                enable_oauth_usage_callback=True,
            )
        )
        assert doc["litellm_settings"]["callbacks"] == [
            "litellm_usage_callback.proxy_handler_instance",
            "litellm_headroom_callback.headroom_callback_instance",
            "litellm_usage_oauth_callback.oauth_usage_callback_instance",
        ]

    def test_headroom_and_oauth_callback_without_usage(self):
        doc = _parse(
            sidecar.build_litellm_config_yaml(
                bedrock_arn="arn:x",
                enable_headroom_callback=True,
                enable_oauth_usage_callback=True,
            )
        )
        assert doc["litellm_settings"]["callbacks"] == [
            "litellm_headroom_callback.headroom_callback_instance",
            "litellm_usage_oauth_callback.oauth_usage_callback_instance",
        ]


# ===========================================================================
# Section G — wait_for_litellm_healthy (docker-exec probe loop)
# ===========================================================================


class _FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture
def fast_clock(monkeypatch):
    """Deterministic monotonic clock + no-op sleep so timeout loops never block.

    time.time() advances by `step` on every call; time.sleep() is a no-op that
    records the requested interval.
    """
    state = {"t": 1000.0}
    slept: list[float] = []

    def fake_time():
        state["t"] += 10.0
        return state["t"]

    def fake_sleep(secs):
        slept.append(secs)

    monkeypatch.setattr(sidecar.time, "time", fake_time)
    monkeypatch.setattr(sidecar.time, "sleep", fake_sleep)
    return slept


class TestWaitForLitellmHealthy:
    def test_returns_true_on_first_successful_probe(self, monkeypatch, fast_clock):
        seen = []

        def fake_run(cmd, *a, **k):
            seen.append(list(cmd))
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(sidecar.subprocess, "run", fake_run)
        assert sidecar.wait_for_litellm_healthy("c1", port=4000, timeout=30) is True
        # Probes via docker exec ... python3 -c <probe>, and the probe embeds the port.
        assert seen[0][0:3] == ["docker", "exec", "c1"]
        assert "4000" in seen[0][-1]

    def test_returns_false_when_never_healthy(self, monkeypatch, fast_clock):
        monkeypatch.setattr(
            sidecar.subprocess, "run", lambda cmd, *a, **k: _FakeCompleted(returncode=1)
        )
        assert sidecar.wait_for_litellm_healthy("c1", timeout=25) is False
        # The loop slept at least once (unhealthy retries before deadline).
        assert fast_clock, "expected at least one retry sleep"

    def test_explicit_timeout_arg_overrides_env(self, monkeypatch, fast_clock):
        # An explicit timeout must be honored even if the env override is set.
        monkeypatch.setenv("KENSEI_LITELLM_HEALTH_TIMEOUT", "999")
        monkeypatch.setattr(
            sidecar.subprocess, "run", lambda cmd, *a, **k: _FakeCompleted(returncode=1)
        )
        # With the fast clock advancing 10s/tick and timeout=5, the deadline is
        # already passed on the first while-check -> immediate False, no probe.
        assert sidecar.wait_for_litellm_healthy("c1", timeout=5) is False

    def test_invalid_env_timeout_falls_back_to_default(self, monkeypatch, fast_clock):
        # Non-numeric env override must not raise; it falls back to 120s default.
        monkeypatch.setenv("KENSEI_LITELLM_HEALTH_TIMEOUT", "not-a-number")
        monkeypatch.setattr(
            sidecar.subprocess, "run", lambda cmd, *a, **k: _FakeCompleted(returncode=1)
        )
        # timeout=None -> env parse path exercised; returns bool without raising.
        assert sidecar.wait_for_litellm_healthy("c1") is False


# ===========================================================================
# Section H — wait_for_bridge_healthy (same loop, /healthz probe)
# ===========================================================================


class TestWaitForBridgeHealthy:
    def test_returns_true_on_healthy(self, monkeypatch, fast_clock):
        seen = []

        def fake_run(cmd, *a, **k):
            seen.append(list(cmd))
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(sidecar.subprocess, "run", fake_run)
        assert sidecar.wait_for_bridge_healthy("br1", port=8765, timeout=30) is True
        assert seen[0][0:3] == ["docker", "exec", "br1"]
        # Bridge probes /healthz (not /health/liveliness).
        assert "/healthz" in seen[0][-1]
        assert "8765" in seen[0][-1]

    def test_returns_false_on_timeout(self, monkeypatch, fast_clock):
        monkeypatch.setattr(
            sidecar.subprocess, "run", lambda cmd, *a, **k: _FakeCompleted(returncode=1)
        )
        assert sidecar.wait_for_bridge_healthy("br1", timeout=25) is False

    def test_invalid_env_timeout_falls_back(self, monkeypatch, fast_clock):
        monkeypatch.setenv("WCB_CC_BRIDGE_HEALTH_TIMEOUT", "garbage")
        monkeypatch.setattr(
            sidecar.subprocess, "run", lambda cmd, *a, **k: _FakeCompleted(returncode=1)
        )
        assert sidecar.wait_for_bridge_healthy("br1") is False


# ===========================================================================
# Section I — verify_litellm_upstream_reachable (single docker-exec round-trip)
# ===========================================================================


class TestVerifyUpstreamReachable:
    def test_success_returns_true_and_output(self, monkeypatch):
        def fake_run(cmd, *a, **k):
            assert cmd[0:3] == ["docker", "exec", "cX"]
            # The probe body must carry the model name + master key + port.
            probe = cmd[-1]
            assert "claude-opus-4.7" in probe
            assert "Bearer mk-secret" in probe
            assert "4000" in probe
            return _FakeCompleted(returncode=0, stdout="OK status=200")

        monkeypatch.setattr(sidecar.subprocess, "run", fake_run)
        ok, out = sidecar.verify_litellm_upstream_reachable(
            "cX", "mk-secret", "claude-opus-4.7", port=4000
        )
        assert ok is True
        assert out == "OK status=200"

    def test_http_error_returns_false_with_detail(self, monkeypatch):
        monkeypatch.setattr(
            sidecar.subprocess,
            "run",
            lambda cmd, *a, **k: _FakeCompleted(returncode=1, stdout="HTTP 403: AccessDenied"),
        )
        ok, out = sidecar.verify_litellm_upstream_reachable("cX", "mk", "m")
        assert ok is False
        assert "403" in out

    def test_connection_error_returns_false(self, monkeypatch):
        # rc=2 is the generic-exception exit code from the in-container probe.
        monkeypatch.setattr(
            sidecar.subprocess,
            "run",
            lambda cmd, *a, **k: _FakeCompleted(returncode=2, stderr="ERR: URLError"),
        )
        ok, out = sidecar.verify_litellm_upstream_reachable("cX", "mk", "m")
        assert ok is False
        assert "ERR" in out

    def test_combines_stdout_and_stderr(self, monkeypatch):
        monkeypatch.setattr(
            sidecar.subprocess,
            "run",
            lambda cmd, *a, **k: _FakeCompleted(returncode=1, stdout="out-part", stderr="err-part"),
        )
        ok, out = sidecar.verify_litellm_upstream_reachable("cX", "mk", "m")
        assert ok is False
        assert "out-part" in out and "err-part" in out

    def test_passes_timeout_to_subprocess(self, monkeypatch):
        captured = {}

        def fake_run(cmd, *a, **k):
            captured["timeout"] = k.get("timeout")
            return _FakeCompleted(returncode=0, stdout="OK status=200")

        monkeypatch.setattr(sidecar.subprocess, "run", fake_run)
        sidecar.verify_litellm_upstream_reachable("cX", "mk", "m", timeout=15.0)
        # subprocess timeout is the probe budget + a 10s cushion.
        assert captured["timeout"] == pytest.approx(25.0)


# ===========================================================================
# Section J — wait_for_bridge_host_port (host-side urllib probe)
# ===========================================================================


class TestWaitForBridgeHostPort:
    def test_empty_port_returns_true_without_probing(self, monkeypatch):
        # No publish requested -> nothing to verify -> True immediately, and it
        # must NOT attempt a urllib call.
        import urllib.request

        def _boom(*a, **k):
            raise AssertionError("urlopen must not be called for empty host_port")

        monkeypatch.setattr(urllib.request, "urlopen", _boom)
        assert sidecar.wait_for_bridge_host_port("") is True

    def test_healthy_returns_true(self, monkeypatch):
        import urllib.request

        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        seen = {}

        def fake_urlopen(url, timeout=2):
            seen["url"] = url
            return _Resp()

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        assert sidecar.wait_for_bridge_host_port("18765", timeout=5) is True
        assert seen["url"] == "http://127.0.0.1:18765/healthz"

    def test_refused_returns_false_after_deadline(self, monkeypatch):
        import urllib.request

        attempts = {"n": 0}

        def fake_urlopen(url, timeout=2):
            attempts["n"] += 1
            raise OSError("[Errno 61] Connection refused")

        # Fine-grained clock: advance 0.5s per call so the deadline (timeout=1)
        # is NOT already passed at the first while-check — this forces at least
        # one loop iteration through the except-branch retry `time.sleep(1.0)`
        # (module lines 959-960) before the deadline is finally crossed.
        state = {"t": 100.0}

        def fake_time():
            state["t"] += 0.5
            return state["t"]

        slept: list[float] = []
        monkeypatch.setattr(sidecar.time, "time", fake_time)
        monkeypatch.setattr(sidecar.time, "sleep", lambda s: slept.append(s))
        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

        assert sidecar.wait_for_bridge_host_port("18765", timeout=1) is False
        # Proves the exception retry path (urlopen tried, then slept 1.0s) ran.
        assert attempts["n"] >= 1
        assert 1.0 in slept


# ===========================================================================
# Section K — module constants (pin the load-bearing digests / ports)
# ===========================================================================


class TestModuleConstants:
    def test_litellm_image_is_digest_pinned(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # Pinned by digest, NOT a floating tag (main-stable rolled forward and
        # produced empty thinking). If this constant changes, the paired FROM in
        # docker/litellm-headroom.Dockerfile must change too.
        assert sidecar.LITELLM_IMAGE.startswith("ghcr.io/berriai/litellm@sha256:")

    def test_internal_ports(self):
        assert sidecar.LITELLM_INTERNAL_PORT == 4000
        assert sidecar.CC_BRIDGE_INTERNAL_PORT == 8765
