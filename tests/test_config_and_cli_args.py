"""Behavioral coverage for src/utils/config.py and src/utils/cli_args.py.

config.py — the Config dataclass, its Config.from_env() env parser (with the
s()/b()/i()/f() coercion helpers, multi-key precedence, env-file discovery,
and os.environ overlay), litellm_enabled() routing predicate, and ensure_dirs().

cli_args.py — build_run_batch_parser() flag surface: defaults (that must match
RUNBOOK conventions such as --parallel default and the tri-state store_true/
store_false groups), choices validation, mutually-exclusive groups, and the
parse_run_batch_args() thin wrapper.

All tests are offline and deterministic. Config.from_env() overlays os.environ,
so tests that assert defaults scrub the relevant keys via a fixture. Env files
are written only under tmp_path. No docker / network / AWS.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import config as config_mod  # noqa: E402
from src.utils.config import Config  # noqa: E402
from src.utils.cli_args import (  # noqa: E402
    build_run_batch_parser,
    parse_run_batch_args,
)


# ---------------------------------------------------------------------------
# Fixture: a clean environment so from_env() default assertions are hermetic.
# from_env() does `env.update(os.environ)`, so any real KENSEI_*/AWS_*/S3_*/
# OPENAI_*/etc. var in the host process would otherwise bleed into results.
# ---------------------------------------------------------------------------

_ENV_KEYS = [
    "KENSEI_BEDROCK_MODEL_ARN", "KENSEI2_BEDROCK_MODEL_ARN", "BEDROCK_MODEL_ARN",
    "KENSEI_BEDROCK_SONNET_ARN", "BEDROCK_SONNET_ARN",
    "KENSEI_AWS_REGION", "AWS_REGION",
    "KENSEI_AWS_BEARER_TOKEN", "AWS_BEARER_TOKEN_BEDROCK",
    "S3_BUCKET", "S3_PREFIX", "S3_REGION",
    "KENSEI_S3_ACCESS_KEY_ID", "AWS_ACCESS_KEY_ID",
    "KENSEI_S3_SECRET_ACCESS_KEY", "AWS_SECRET_ACCESS_KEY",
    "KENSEI_OPENAI_API_KEY", "OPENAI_API_KEY",
    "KENSEI_OPENAI_WHISPER_API_KEY", "OPENAI_WHISPER_API_KEY",
    "KENSEI_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY",
    "OPENROUTER_API_KEY", "OPENROUTER_BASE_URL",
    "BRAVE_API_KEY", "DOCKER_IMAGE", "TMP_WORKSPACE", "GATEWAY_PORT",
    "UPLOAD_MEDIA_TO_S3", "WILDCLAW_SKILLS_DIR",
    "WILDCLAW_DEFAULT_SKILLS", "KENSEI3_DEFAULT_SKILLS",
    "KENSEI_LITELLM_MASTER_KEY", "KENSEI3_LITELLM_MASTER_KEY", "LITELLM_MASTER_KEY",
    "KENSEI3_LITELLM_PORT", "LITELLM_PORT",
    "MIN_HARBOR_SCORE",
    "WCB_USE_CLAUDE_OAUTH", "WCB_CC_ACCOUNT_POOL",
    "WCB_CC_BRIDGE_SECRET", "WCB_CC_STUB_KEY",
]


@pytest.fixture
def clean_env(monkeypatch):
    """Delete every env key from_env() consults so defaults are observable."""
    for k in _ENV_KEYS:
        monkeypatch.delenv(k, raising=False)
    return monkeypatch


def _from_env_no_file(monkeypatch, tmp_path):
    """Call from_env with cwd pointed at an empty dir so no repo .env is picked up.

    env_file=None triggers discovery of ROOT_DIR/.env and cwd/.env. We pass an
    explicit non-existent env_file to skip discovery entirely and keep it hermetic.
    """
    return Config.from_env(env_file=tmp_path / "does_not_exist.env")


# ===========================================================================
# config.py — Config dataclass literal defaults (no env involved)
# ===========================================================================


class TestConfigDataclassDefaults:
    def test_scalar_defaults(self):
        c = Config()
        assert c.bedrock_region == "ap-south-1"
        assert c.s3_prefix == "WildClaw"
        assert c.s3_region == "us-east-1"
        assert c.brave_api_key == "placeholder"
        assert c.docker_image == "wildclawbench-ubuntu:v1.3"
        assert c.litellm_master_key == "sk-talos-litellm"
        assert c.litellm_port == 4000
        assert c.tmp_workspace == "/tmp_workspace"
        assert c.gateway_port == 18789
        assert c.openrouter_base_url == "https://openrouter.ai/api/v1"

    def test_empty_secret_defaults(self):
        c = Config()
        assert c.bedrock_inference_arn == ""
        assert c.aws_bearer_token == ""
        assert c.openai_api_key == ""
        assert c.anthropic_api_key == ""
        assert c.s3_bucket == ""

    def test_oauth_defaults(self):
        c = Config()
        assert c.use_claude_oauth is False
        assert c.cc_account_pool == ""
        assert c.cc_bridge_secret == ""
        assert c.cc_stub_key == "sk-wcb-oauth-stub"

    def test_min_harbor_score_default_is_none(self):
        assert Config().min_harbor_score is None

    def test_upload_media_default_false(self):
        assert Config().upload_media_to_s3 is False

    def test_path_field_defaults_are_independent_instances(self):
        # default_factory must yield fresh objects, not a shared mutable.
        a = Config()
        b = Config()
        assert a.default_skills == []
        assert a.default_skills is not b.default_skills
        a.default_skills.append("x")
        assert b.default_skills == []

    def test_path_fields_anchor_on_root_dir(self):
        c = Config()
        assert c.environment_dir == config_mod.ENVIRONMENT_DIR
        assert c.state_db == config_mod.ROOT_DIR / "state.db"
        assert c.work_dir == config_mod.ROOT_DIR / "work"
        assert c.output_dir == config_mod.ROOT_DIR / "output"


# ===========================================================================
# config.py — from_env() defaults when no env keys are set
# ===========================================================================


class TestFromEnvDefaults:
    def test_returns_config_instance(self, clean_env, tmp_path):
        c = _from_env_no_file(clean_env, tmp_path)
        assert isinstance(c, Config)

    def test_defaults_match_when_env_absent(self, clean_env, tmp_path):
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.bedrock_region == "ap-south-1"
        assert c.s3_prefix == "WildClaw"
        assert c.s3_region == "us-east-1"
        assert c.brave_api_key == "placeholder"
        assert c.docker_image == "wildclawbench-ubuntu:v1.3"
        assert c.tmp_workspace == "/tmp_workspace"
        assert c.gateway_port == 18789
        assert c.litellm_master_key == "sk-talos-litellm"
        assert c.litellm_port == 4000
        assert c.openrouter_base_url == "https://openrouter.ai/api/v1"
        assert c.cc_stub_key == "sk-wcb-oauth-stub"

    def test_empty_secrets_when_env_absent(self, clean_env, tmp_path):
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.bedrock_inference_arn == ""
        assert c.aws_bearer_token == ""
        assert c.openai_api_key == ""
        assert c.anthropic_api_key == ""
        assert c.min_harbor_score is None
        assert c.upload_media_to_s3 is False
        assert c.use_claude_oauth is False
        assert c.cc_account_pool == ""

    def test_default_skills_default_list(self, clean_env, tmp_path):
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.default_skills == ["video-frames", "pdf-extract", "audio-extract"]

    def test_skills_dir_defaults_to_environment_skills(self, clean_env, tmp_path):
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.wildclaw_skills_dir == config_mod.ENVIRONMENT_DIR / "skills"


# ===========================================================================
# config.py — the s() string helper: precedence + empty-string skip
# ===========================================================================


class TestStringHelper:
    def test_single_key_read(self, clean_env, tmp_path):
        clean_env.setenv("S3_BUCKET", "my-bucket")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.s3_bucket == "my-bucket"

    def test_first_key_wins_over_later(self, clean_env, tmp_path):
        # bedrock_inference_arn reads KENSEI_..., then KENSEI2_..., then BEDROCK_...
        clean_env.setenv("KENSEI_BEDROCK_MODEL_ARN", "arn-primary")
        clean_env.setenv("BEDROCK_MODEL_ARN", "arn-legacy")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.bedrock_inference_arn == "arn-primary"

    def test_falls_through_to_second_key(self, clean_env, tmp_path):
        clean_env.setenv("BEDROCK_MODEL_ARN", "arn-legacy")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.bedrock_inference_arn == "arn-legacy"

    def test_empty_string_key_is_skipped_for_next(self, clean_env, tmp_path):
        # An empty first key must not shadow a populated later key.
        clean_env.setenv("KENSEI_BEDROCK_MODEL_ARN", "")
        clean_env.setenv("BEDROCK_MODEL_ARN", "arn-legacy")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.bedrock_inference_arn == "arn-legacy"

    def test_empty_string_falls_back_to_default(self, clean_env, tmp_path):
        clean_env.setenv("S3_REGION", "")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.s3_region == "us-east-1"

    def test_value_is_stripped(self, clean_env, tmp_path):
        clean_env.setenv("S3_BUCKET", "  spaced-bucket  ")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.s3_bucket == "spaced-bucket"


# ===========================================================================
# config.py — the b() bool helper
# ===========================================================================


class TestBoolHelper:
    @pytest.mark.parametrize("truthy", ["1", "true", "TRUE", "Yes", "on", " on ", "True"])
    def test_recognized_truthy(self, clean_env, tmp_path, truthy):
        clean_env.setenv("UPLOAD_MEDIA_TO_S3", truthy)
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.upload_media_to_s3 is True

    @pytest.mark.parametrize("falsy", ["0", "false", "no", "off", "", "nope", "2"])
    def test_unrecognized_is_false(self, clean_env, tmp_path, falsy):
        clean_env.setenv("UPLOAD_MEDIA_TO_S3", falsy)
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.upload_media_to_s3 is False

    def test_absent_uses_default_false(self, clean_env, tmp_path):
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.upload_media_to_s3 is False

    def test_oauth_flag_truthy(self, clean_env, tmp_path):
        clean_env.setenv("WCB_USE_CLAUDE_OAUTH", "yes")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.use_claude_oauth is True


# ===========================================================================
# config.py — the i() int helper (used for gateway_port + nested litellm_port)
# ===========================================================================


class TestIntHelper:
    def test_valid_int_parsed(self, clean_env, tmp_path):
        clean_env.setenv("GATEWAY_PORT", "12345")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.gateway_port == 12345

    def test_invalid_int_falls_back_to_default(self, clean_env, tmp_path):
        clean_env.setenv("GATEWAY_PORT", "not-a-number")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.gateway_port == 18789

    def test_negative_int_is_accepted(self, clean_env, tmp_path):
        # i() does a plain int() with no range check; pin current behavior.
        clean_env.setenv("GATEWAY_PORT", "-1")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.gateway_port == -1

    def test_zero_int_is_accepted(self, clean_env, tmp_path):
        clean_env.setenv("GATEWAY_PORT", "0")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.gateway_port == 0

    def test_litellm_port_primary_key(self, clean_env, tmp_path):
        # litellm_port = i("KENSEI3_LITELLM_PORT", i("LITELLM_PORT", 4000))
        clean_env.setenv("KENSEI3_LITELLM_PORT", "5555")
        clean_env.setenv("LITELLM_PORT", "6666")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.litellm_port == 5555

    def test_litellm_port_falls_to_secondary_key(self, clean_env, tmp_path):
        clean_env.setenv("LITELLM_PORT", "6666")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.litellm_port == 6666

    def test_litellm_port_invalid_primary_uses_secondary_as_default(self, clean_env, tmp_path):
        # KENSEI3 present but non-numeric -> i() returns its default arg, which is
        # the (already-resolved) LITELLM_PORT value.
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        clean_env.setenv("KENSEI3_LITELLM_PORT", "bad")
        clean_env.setenv("LITELLM_PORT", "6666")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.litellm_port == 6666

    def test_litellm_port_both_absent_default(self, clean_env, tmp_path):
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.litellm_port == 4000


# ===========================================================================
# config.py — the f() float helper (min_harbor_score)
# ===========================================================================


class TestFloatHelper:
    def test_valid_float_parsed(self, clean_env, tmp_path):
        clean_env.setenv("MIN_HARBOR_SCORE", "0.75")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.min_harbor_score == 0.75

    def test_absent_returns_none(self, clean_env, tmp_path):
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.min_harbor_score is None

    def test_empty_string_returns_none(self, clean_env, tmp_path):
        clean_env.setenv("MIN_HARBOR_SCORE", "")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.min_harbor_score is None

    def test_invalid_float_falls_back_to_none_default(self, clean_env, tmp_path):
        clean_env.setenv("MIN_HARBOR_SCORE", "high")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.min_harbor_score is None

    def test_zero_is_preserved(self, clean_env, tmp_path):
        clean_env.setenv("MIN_HARBOR_SCORE", "0")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.min_harbor_score == 0.0

    def test_negative_float_is_accepted(self, clean_env, tmp_path):
        clean_env.setenv("MIN_HARBOR_SCORE", "-0.5")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.min_harbor_score == -0.5


# ===========================================================================
# config.py — default_skills CSV parsing
# ===========================================================================


class TestDefaultSkillsParsing:
    def test_custom_csv(self, clean_env, tmp_path):
        clean_env.setenv("WILDCLAW_DEFAULT_SKILLS", "alpha,beta,gamma")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.default_skills == ["alpha", "beta", "gamma"]

    def test_whitespace_and_empty_items_filtered(self, clean_env, tmp_path):
        clean_env.setenv("WILDCLAW_DEFAULT_SKILLS", " a , , b ,,")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.default_skills == ["a", "b"]

    def test_empty_string_yields_empty_list(self, clean_env, tmp_path):
        # An explicit empty value -> s() returns its default CSV, so this is NOT
        # empty. Set to a comma-only string to actually produce [].
        clean_env.setenv("WILDCLAW_DEFAULT_SKILLS", ",,,")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.default_skills == []

    def test_secondary_kensei3_key(self, clean_env, tmp_path):
        clean_env.setenv("KENSEI3_DEFAULT_SKILLS", "only-this")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.default_skills == ["only-this"]

    def test_wildclaw_key_wins_over_kensei3(self, clean_env, tmp_path):
        clean_env.setenv("WILDCLAW_DEFAULT_SKILLS", "primary")
        clean_env.setenv("KENSEI3_DEFAULT_SKILLS", "legacy")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.default_skills == ["primary"]

    def test_custom_skills_dir(self, clean_env, tmp_path):
        clean_env.setenv("WILDCLAW_SKILLS_DIR", "/custom/skills")
        c = _from_env_no_file(clean_env, tmp_path)
        assert c.wildclaw_skills_dir == Path("/custom/skills")


# ===========================================================================
# config.py — env-file discovery and os.environ overlay
# ===========================================================================


class TestEnvFileLoading:
    def test_explicit_env_file_is_read(self, clean_env, tmp_path):
        envf = tmp_path / "custom.env"
        envf.write_text('S3_BUCKET=from-file\nBRAVE_API_KEY="quoted-brave"\n')
        c = Config.from_env(env_file=envf)
        assert c.s3_bucket == "from-file"
        assert c.brave_api_key == "quoted-brave"

    def test_os_environ_overrides_env_file(self, clean_env, tmp_path):
        # env.update(dotenv) then env.update(os.environ): process env wins.
        envf = tmp_path / "custom.env"
        envf.write_text("S3_BUCKET=from-file\n")
        clean_env.setenv("S3_BUCKET", "from-process")
        c = Config.from_env(env_file=envf)
        assert c.s3_bucket == "from-process"

    def test_nonexistent_explicit_env_file_is_ignored(self, clean_env, tmp_path):
        c = Config.from_env(env_file=tmp_path / "nope.env")
        assert c.s3_bucket == ""

    def test_env_file_comment_and_blank_lines_ignored(self, clean_env, tmp_path):
        envf = tmp_path / "custom.env"
        envf.write_text("# a comment\n\nS3_BUCKET=real\n")
        c = Config.from_env(env_file=envf)
        assert c.s3_bucket == "real"

    def test_auto_discovers_cwd_dotenv_when_env_file_none(self, clean_env, tmp_path, monkeypatch):
        # env_file=None triggers discovery of ROOT_DIR/.env then cwd/.env.
        # The repo root has no .env, so chdir'ing to a tmp dir with one makes
        # the cwd candidate the winner.
        (tmp_path / ".env").write_text("S3_BUCKET=discovered\n")
        monkeypatch.chdir(tmp_path)
        c = Config.from_env(env_file=None)
        assert c.s3_bucket == "discovered"

    def test_no_dotenv_anywhere_uses_defaults(self, clean_env, tmp_path, monkeypatch):
        # env_file=None and neither candidate exists: discovery loop finds
        # nothing, env stays empty, defaults hold.
        empty = tmp_path / "empty_cwd"
        empty.mkdir()
        monkeypatch.chdir(empty)
        c = Config.from_env(env_file=None)
        assert c.s3_bucket == ""
        assert c.s3_prefix == "WildClaw"


# ===========================================================================
# config.py — litellm_enabled() routing predicate (5 branches)
# ===========================================================================


class TestLitellmEnabled:
    def test_bedrock_arn_plus_bearer_enables(self):
        c = Config(bedrock_inference_arn="arn:x", aws_bearer_token="tok")
        assert c.litellm_enabled() is True

    def test_bedrock_arn_without_bearer_does_not_enable(self):
        c = Config(bedrock_inference_arn="arn:x", aws_bearer_token="")
        assert c.litellm_enabled() is False

    def test_bearer_without_arn_does_not_enable(self):
        c = Config(bedrock_inference_arn="", aws_bearer_token="tok")
        assert c.litellm_enabled() is False

    def test_openai_key_enables(self):
        c = Config(openai_api_key="sk-openai")
        assert c.litellm_enabled() is True

    def test_anthropic_key_enables(self):
        c = Config(anthropic_api_key="sk-ant")
        assert c.litellm_enabled() is True

    def test_oauth_with_pool_enables(self):
        c = Config(use_claude_oauth=True, cc_account_pool="/oauth/a.json")
        assert c.litellm_enabled() is True

    def test_oauth_without_pool_does_not_enable(self):
        c = Config(use_claude_oauth=True, cc_account_pool="")
        assert c.litellm_enabled() is False

    def test_pool_without_oauth_flag_does_not_enable(self):
        c = Config(use_claude_oauth=False, cc_account_pool="/oauth/a.json")
        assert c.litellm_enabled() is False

    def test_bare_config_disabled(self):
        assert Config().litellm_enabled() is False


# ===========================================================================
# config.py — ensure_dirs()
# ===========================================================================


class TestEnsureDirs:
    def test_creates_work_and_output_dirs(self, tmp_path):
        c = Config()
        c.work_dir = tmp_path / "w"
        c.output_dir = tmp_path / "o"
        assert not c.work_dir.exists()
        assert not c.output_dir.exists()
        c.ensure_dirs()
        assert c.work_dir.is_dir()
        assert c.output_dir.is_dir()

    def test_idempotent_when_dirs_exist(self, tmp_path):
        c = Config()
        c.work_dir = tmp_path / "w"
        c.output_dir = tmp_path / "o"
        c.work_dir.mkdir()
        c.output_dir.mkdir()
        c.ensure_dirs()  # exist_ok=True -> no error
        assert c.work_dir.is_dir()
        assert c.output_dir.is_dir()

    def test_creates_nested_parents(self, tmp_path):
        c = Config()
        c.work_dir = tmp_path / "a" / "b" / "w"
        c.output_dir = tmp_path / "a" / "b" / "o"
        c.ensure_dirs()  # parents=True
        assert c.work_dir.is_dir()
        assert c.output_dir.is_dir()


# ===========================================================================
# config.py — module-level path anchoring
# ===========================================================================


def test_root_dir_is_repo_root():
    # config.py lives at src/utils/config.py; parents[2] is the repo root.
    assert config_mod.ROOT_DIR == REPO_ROOT
    assert config_mod.ENVIRONMENT_DIR == REPO_ROOT / "environment"


def test_fallback_dotenv_values_parses_file(clean_env, tmp_path):
    # Exercise the built-in fallback dotenv_values parser (only reached when
    # python-dotenv is absent) directly against a sample file.
    envf = tmp_path / "f.env"
    envf.write_text(
        "# comment\n"
        "\n"
        "KEY1=value1\n"
        'KEY2="quoted"\n'
        "KEY3='single'\n"
        "NOEQUALS_LINE\n"
        "  SPACED_KEY  =  spaced value  \n"
    )
    # config_mod.dotenv_values may be python-dotenv's or the local fallback;
    # both agree that KEY=VALUE lines parse with quote-stripping. A line with
    # no '=' is handled differently by the two impls (dropped by the fallback,
    # kept as None by python-dotenv), so its presence is not asserted here.
    parsed = config_mod.dotenv_values(str(envf))
    assert parsed.get("KEY1") == "value1"
    assert parsed.get("KEY2") == "quoted"
    assert parsed.get("KEY3") == "single"


def test_fallback_dotenv_values_missing_file_returns_empty():
    # The local fallback returns {} for a missing path. python-dotenv also
    # returns {} for a missing path, so this holds regardless of which is active.
    assert config_mod.dotenv_values("/no/such/file/at/all.env") == {}


# ===========================================================================
# cli_args.py — parser defaults
# ===========================================================================


class TestParserDefaults:
    def test_parallel_default_from_argument(self):
        parser = build_run_batch_parser("claude-opus-4.7", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.parallel == 1

    def test_parallel_default_honors_caller_value(self):
        parser = build_run_batch_parser("m", 4)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.parallel == 4

    def test_model_default_from_argument(self):
        parser = build_run_batch_parser("claude-opus-4.7", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.model == "claude-opus-4.7"

    def test_agent_backend_default_openclaw(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.agent_backend == "openclaw"

    def test_thinking_default_xhigh(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.thinking == "xhigh"

    def test_testgen_max_attempts_default(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.testgen_max_attempts == 3

    def test_testexec_timeout_default(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.testexec_timeout == 600

    def test_tri_state_flags_default_none(self):
        # These stay None so the orchestrator can distinguish "unset" (auto)
        # from an explicit on/off. Load-bearing per RUNBOOK auto-enable rules.
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.litellm is None
        assert ns.generate_tests is None
        assert ns.execute_tests is None
        assert ns.judge_council is None
        assert ns.use_claude_oauth is None

    def test_store_true_flags_default_false(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.mock_stack is False
        assert ns.force_testgen is False
        assert ns.rebuild_mocks is False

    def test_optional_string_flags_default_none(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "input/x"])
        assert ns.lobster_name is None
        assert ns.lobster_workspace is None
        assert ns.lobster_env is None
        assert ns.models_config is None
        assert ns.openclaw_image_model is None
        assert ns.bedrock_arn is None
        assert ns.aws_region is None
        assert ns.category is None


# ===========================================================================
# cli_args.py — required mode group
# ===========================================================================


class TestModeGroup:
    def test_task_mode_accepted(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "input/foo"])
        assert ns.task == "input/foo"
        assert ns.category is None

    def test_category_mode_accepted(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--category", "01_Productivity_Flow"])
        assert ns.category == "01_Productivity_Flow"
        assert ns.task is None

    def test_short_task_flag(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["-t", "input/foo"])
        assert ns.task == "input/foo"

    def test_missing_mode_exits(self):
        parser = build_run_batch_parser("m", 1)
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_task_and_category_mutually_exclusive(self):
        parser = build_run_batch_parser("m", 1)
        with pytest.raises(SystemExit):
            parser.parse_args(["--task", "x", "--category", "y"])


# ===========================================================================
# cli_args.py — choices validation
# ===========================================================================


class TestChoicesValidation:
    @pytest.mark.parametrize("backend", ["openclaw", "claudecode", "codex", "hermesagent"])
    def test_valid_backends(self, backend):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--agent-backend", backend])
        assert ns.agent_backend == backend

    def test_invalid_backend_exits(self):
        parser = build_run_batch_parser("m", 1)
        with pytest.raises(SystemExit):
            parser.parse_args(["--task", "x", "--agent-backend", "nonsense"])


# ===========================================================================
# cli_args.py — tri-state mutually-exclusive on/off groups
# ===========================================================================


class TestTriStateGroups:
    def test_litellm_on(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--litellm"])
        assert ns.litellm is True

    def test_litellm_off(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--no-litellm"])
        assert ns.litellm is False

    def test_litellm_and_no_litellm_conflict(self):
        parser = build_run_batch_parser("m", 1)
        with pytest.raises(SystemExit):
            parser.parse_args(["--task", "x", "--litellm", "--no-litellm"])

    def test_generate_tests_on_off(self):
        parser = build_run_batch_parser("m", 1)
        assert parser.parse_args(["--task", "x", "--generate-tests"]).generate_tests is True
        parser2 = build_run_batch_parser("m", 1)
        assert parser2.parse_args(["--task", "x", "--no-generate-tests"]).generate_tests is False

    def test_generate_tests_conflict(self):
        parser = build_run_batch_parser("m", 1)
        with pytest.raises(SystemExit):
            parser.parse_args(["--task", "x", "--generate-tests", "--no-generate-tests"])

    def test_execute_tests_on_off(self):
        parser = build_run_batch_parser("m", 1)
        assert parser.parse_args(["--task", "x", "--execute-tests"]).execute_tests is True
        parser2 = build_run_batch_parser("m", 1)
        assert parser2.parse_args(["--task", "x", "--no-execute-tests"]).execute_tests is False

    def test_judge_council_on_off(self):
        parser = build_run_batch_parser("m", 1)
        assert parser.parse_args(["--task", "x", "--judge-council"]).judge_council is True
        parser2 = build_run_batch_parser("m", 1)
        assert parser2.parse_args(["--task", "x", "--no-judge-council"]).judge_council is False

    def test_judge_council_not_mutually_exclusive_last_wins(self):
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # Unlike --litellm / --generate-tests / --execute-tests, the
        # --judge-council / --no-judge-council pair is NOT wrapped in a
        # mutually-exclusive group (two plain add_argument calls sharing dest).
        # So passing both does not error; argparse applies them left-to-right
        # and the last flag on the line wins.
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--judge-council", "--no-judge-council"])
        assert ns.judge_council is False
        parser2 = build_run_batch_parser("m", 1)
        ns2 = parser2.parse_args(["--task", "x", "--no-judge-council", "--judge-council"])
        assert ns2.judge_council is True

    def test_use_claude_oauth_on(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--use-claude-oauth"])
        assert ns.use_claude_oauth is True


# ===========================================================================
# cli_args.py — value-taking flags and type coercion
# ===========================================================================


class TestValueFlags:
    def test_parallel_int_coercion(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--parallel", "8"])
        assert ns.parallel == 8
        assert isinstance(ns.parallel, int)

    def test_parallel_short_flag(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "-p", "3"])
        assert ns.parallel == 3

    def test_parallel_non_int_exits(self):
        parser = build_run_batch_parser("m", 1)
        with pytest.raises(SystemExit):
            parser.parse_args(["--task", "x", "--parallel", "two"])

    def test_testgen_max_attempts_override(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--testgen-max-attempts", "7"])
        assert ns.testgen_max_attempts == 7

    def test_testexec_timeout_override(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--testexec-timeout", "120"])
        assert ns.testexec_timeout == 120

    def test_model_override(self):
        parser = build_run_batch_parser("default-m", 1)
        ns = parser.parse_args(["--task", "x", "--model", "gpt-5.5"])
        assert ns.model == "gpt-5.5"

    def test_model_short_flag(self):
        parser = build_run_batch_parser("default-m", 1)
        ns = parser.parse_args(["--task", "x", "-m", "gpt-5.5"])
        assert ns.model == "gpt-5.5"

    def test_lobster_env_string_passthrough(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(["--task", "x", "--lobster-env", "A,B,C"])
        assert ns.lobster_env == "A,B,C"

    def test_bedrock_arn_and_region(self):
        parser = build_run_batch_parser("m", 1)
        ns = parser.parse_args(
            ["--task", "x", "--bedrock-arn", "arn:aws:bedrock", "--aws-region", "us-west-2"]
        )
        assert ns.bedrock_arn == "arn:aws:bedrock"
        assert ns.aws_region == "us-west-2"


# ===========================================================================
# cli_args.py — combined realistic invocation (RUNBOOK §5.3 style)
# ===========================================================================


def test_full_orchestrator_flag_combo():
    parser = build_run_batch_parser("claude-opus-4.7", 1)
    ns = parser.parse_args([
        "--task", "input/alden-croft_MB",
        "--agent-backend", "openclaw",
        "--model", "claude-opus-4.7",
        "--litellm",
        "--mock-stack",
        "--generate-tests",
        "--execute-tests",
        "--judge-council",
        "--parallel", "1",
    ])
    assert ns.task == "input/alden-croft_MB"
    assert ns.agent_backend == "openclaw"
    assert ns.model == "claude-opus-4.7"
    assert ns.litellm is True
    assert ns.mock_stack is True
    assert ns.generate_tests is True
    assert ns.execute_tests is True
    assert ns.judge_council is True
    assert ns.parallel == 1


# ===========================================================================
# cli_args.py — parse_run_batch_args() thin wrapper delegates to sys.argv
# ===========================================================================


class TestParseRunBatchArgs:
    def test_delegates_to_parser_and_reads_argv(self, monkeypatch):
        monkeypatch.setattr(
            sys, "argv", ["run_batch.py", "--task", "input/y", "--parallel", "2"]
        )
        ns = parse_run_batch_args("default-m", 1)
        assert ns.task == "input/y"
        assert ns.parallel == 2
        assert ns.model == "default-m"
        assert ns.agent_backend == "openclaw"

    def test_wrapper_uses_supplied_defaults(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["run_batch.py", "--task", "input/y"])
        ns = parse_run_batch_args("special-model", 9)
        assert ns.model == "special-model"
        assert ns.parallel == 9

    def test_wrapper_exits_on_missing_mode(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["run_batch.py"])
        with pytest.raises(SystemExit):
            parse_run_batch_args("m", 1)
