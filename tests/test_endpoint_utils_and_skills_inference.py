"""Unit tests for src/utils/endpoint_utils.py and src/utils/skills_inference.py.

endpoint_utils: pure-string normalization of OpenRouter base URLs for the
openclaw (/api/v1 form) and claudecode (/api form) backends.

skills_inference: dynamic API-catalog discovery from an environment dir
(`<name>-api/` + `service.toml`), keyword derivation from slugs, curated
keyword/tag enrichment, prompt -> required-API inference with the
"strong single hit OR >=2 generic hits" rule, and the all-minus-required
distractor policy (with optional deterministic seeded truncation).

All tests are offline and hermetic: catalog tests build synthetic
environment dirs under tmp_path; the lru_cache on _build_catalog is
cleared around every test.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils.endpoint_utils import (  # noqa: E402
    normalize_openrouter_base_url,
    normalize_openrouter_base_url_for_claudecode,
    normalize_openrouter_base_url_for_openclaw,
)
from src.utils import skills_inference as si  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_catalog_cache():
    """_build_catalog is lru_cached on the env-dir string; keep tests isolated."""
    si._build_catalog.cache_clear()
    yield
    si._build_catalog.cache_clear()


def _make_env(tmp_path: Path, api_names: list[str]) -> Path:
    """Create a synthetic environment dir with <name>/service.toml per entry."""
    env = tmp_path / "environment"
    env.mkdir(exist_ok=True)
    for name in api_names:
        d = env / name
        d.mkdir()
        (d / "service.toml").write_text('[service]\nname = "%s"\n' % name)
    return env


# ---------------------------------------------------------------------------
# Section A — endpoint_utils.normalize_openrouter_base_url (openclaw form)
# ---------------------------------------------------------------------------

def test_none_url_returns_default_v1() -> None:
    assert normalize_openrouter_base_url(None) == "https://openrouter.ai/api/v1"


def test_empty_string_returns_default_v1() -> None:
    assert normalize_openrouter_base_url("") == "https://openrouter.ai/api/v1"


def test_api_suffix_gets_v1_appended() -> None:
    assert (
        normalize_openrouter_base_url("https://openrouter.ai/api")
        == "https://openrouter.ai/api/v1"
    )


def test_api_trailing_slash_gets_v1_appended() -> None:
    assert (
        normalize_openrouter_base_url("https://openrouter.ai/api/")
        == "https://openrouter.ai/api/v1"
    )


def test_api_multiple_trailing_slashes_collapse() -> None:
    assert (
        normalize_openrouter_base_url("https://openrouter.ai/api///")
        == "https://openrouter.ai/api/v1"
    )


def test_already_v1_is_idempotent() -> None:
    assert (
        normalize_openrouter_base_url("https://openrouter.ai/api/v1")
        == "https://openrouter.ai/api/v1"
    )


def test_v1_with_trailing_slash_is_stripped_not_doubled() -> None:
    assert (
        normalize_openrouter_base_url("https://openrouter.ai/api/v1/")
        == "https://openrouter.ai/api/v1"
    )


def test_surrounding_whitespace_is_stripped() -> None:
    assert (
        normalize_openrouter_base_url("  https://openrouter.ai/api  ")
        == "https://openrouter.ai/api/v1"
    )


def test_non_api_url_passes_through_unchanged() -> None:
    assert (
        normalize_openrouter_base_url("https://proxy.example.com/v2")
        == "https://proxy.example.com/v2"
    )


def test_path_segment_ending_in_api_word_not_treated_as_api() -> None:
    # 'xapi' does not end with the '/api' segment, so no /v1 is appended.
    assert (
        normalize_openrouter_base_url("https://host/xapi")
        == "https://host/xapi"
    )


def test_whitespace_only_url_returns_empty_string() -> None:
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md.
    # A whitespace-only URL is truthy, so the default is NOT substituted;
    # strip()/rstrip() reduce it to "" which is returned verbatim.
    assert normalize_openrouter_base_url("   ") == ""


def test_openclaw_wrapper_delegates_to_base_normalizer() -> None:
    assert (
        normalize_openrouter_base_url_for_openclaw("https://openrouter.ai/api")
        == "https://openrouter.ai/api/v1"
    )
    assert (
        normalize_openrouter_base_url_for_openclaw(None)
        == "https://openrouter.ai/api/v1"
    )


# ---------------------------------------------------------------------------
# Section B — endpoint_utils.normalize_openrouter_base_url_for_claudecode
# ---------------------------------------------------------------------------

def test_claudecode_none_returns_default_api() -> None:
    assert (
        normalize_openrouter_base_url_for_claudecode(None)
        == "https://openrouter.ai/api"
    )


def test_claudecode_empty_returns_default_api() -> None:
    assert (
        normalize_openrouter_base_url_for_claudecode("")
        == "https://openrouter.ai/api"
    )


def test_claudecode_strips_v1_suffix() -> None:
    assert (
        normalize_openrouter_base_url_for_claudecode("https://openrouter.ai/api/v1")
        == "https://openrouter.ai/api"
    )


def test_claudecode_strips_v1_suffix_with_trailing_slash() -> None:
    assert (
        normalize_openrouter_base_url_for_claudecode("https://openrouter.ai/api/v1/")
        == "https://openrouter.ai/api"
    )


def test_claudecode_api_form_unchanged() -> None:
    assert (
        normalize_openrouter_base_url_for_claudecode("https://openrouter.ai/api")
        == "https://openrouter.ai/api"
    )


def test_claudecode_whitespace_and_trailing_slash_stripped() -> None:
    assert (
        normalize_openrouter_base_url_for_claudecode(" https://openrouter.ai/api/ ")
        == "https://openrouter.ai/api"
    )


def test_claudecode_non_openrouter_url_passes_through() -> None:
    assert (
        normalize_openrouter_base_url_for_claudecode("https://proxy.example.com/v2")
        == "https://proxy.example.com/v2"
    )


def test_claudecode_whitespace_only_returns_empty_string() -> None:
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md.
    # Same truthy-whitespace quirk as the openclaw normalizer.
    assert normalize_openrouter_base_url_for_claudecode("  ") == ""


def test_roundtrip_openclaw_then_claudecode() -> None:
    v1 = normalize_openrouter_base_url_for_openclaw("https://openrouter.ai/api")
    assert normalize_openrouter_base_url_for_claudecode(v1) == "https://openrouter.ai/api"


# ---------------------------------------------------------------------------
# Section C — skills_inference internals (_env_dir, _slug_keywords,
#             _compile_pattern, _compile_matchers)
# ---------------------------------------------------------------------------

def test_env_dir_defaults_to_repo_environment() -> None:
    assert si._env_dir(None) == si.DEFAULT_ENVIRONMENT_DIR
    assert si.DEFAULT_ENVIRONMENT_DIR == REPO_ROOT / "environment"


def test_env_dir_wraps_explicit_path() -> None:
    assert si._env_dir("/some/where") == Path("/some/where")


def test_slug_keywords_multiword_slug() -> None:
    tokens, phrases = si._slug_keywords("amazon-seller-api")
    assert tokens == {"amazon", "seller"}
    assert phrases == {"amazon seller", "amazonseller"}


def test_slug_keywords_single_word_slug_has_no_phrases() -> None:
    tokens, phrases = si._slug_keywords("etsy-api")
    assert tokens == {"etsy"}
    assert phrases == set()


def test_slug_keywords_filters_stopwords_and_short_tokens() -> None:
    tokens, phrases = si._slug_keywords("the-app-api")
    assert tokens == set()  # 'the' and 'app' are stopwords
    assert phrases == {"the app", "theapp"}

    tokens2, phrases2 = si._slug_keywords("x-y-api")
    assert tokens2 == set()  # both below _MIN_TOKEN_LEN
    assert phrases2 == {"x y", "xy"}


def test_slug_keywords_without_api_suffix_uses_full_name() -> None:
    tokens, phrases = si._slug_keywords("notion")
    assert tokens == {"notion"}
    assert phrases == set()


def test_slug_keywords_bare_api_suffix_yields_nothing() -> None:
    tokens, phrases = si._slug_keywords("-api")
    assert tokens == set()
    assert phrases == set()


def test_compile_pattern_empty_or_blank_keys_returns_none() -> None:
    assert si._compile_pattern(set()) is None
    assert si._compile_pattern({"", "   "}) is None


def test_compile_pattern_word_boundary_matching() -> None:
    pat = si._compile_pattern({"notion"})
    assert pat is not None
    assert pat.search("open my notion workspace")
    assert pat.search("notion") is not None
    assert pat.search("notional analysis") is None  # substring only, no \b match
    assert pat.search("promotion") is None


def test_compile_pattern_escapes_regex_metacharacters() -> None:
    pat = si._compile_pattern({"c.d"})
    assert pat is not None
    assert pat.search("use c.d here")
    assert pat.search("use cxd here") is None  # '.' must be literal, not wildcard


def test_compile_matchers_strong_includes_slug_and_curated() -> None:
    strong, generic = si._compile_matchers("quickbooks-api")
    assert strong is not None and generic is not None
    assert strong.search("sync with quickbooks now")   # slug token
    assert strong.search("check the ledger")           # curated strong keyword
    assert generic.search("send an invoice")           # curated generic keyword
    assert strong.search("send an invoice") is None    # invoice is generic-only


def test_compile_matchers_no_generic_map_returns_none_generic() -> None:
    strong, generic = si._compile_matchers("notion-api")
    assert strong is not None
    assert generic is None  # notion-api has no _GENERIC_KEYWORDS entry


# ---------------------------------------------------------------------------
# Section D — catalog discovery (available_apis / _build_catalog)
# ---------------------------------------------------------------------------

def test_available_apis_discovers_only_valid_service_dirs(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["notion-api", "stripe-api"])
    # -api dir WITHOUT service.toml -> excluded
    (env / "ghost-api").mkdir()
    # dir with service.toml but no -api suffix -> excluded
    bad = env / "notes"
    bad.mkdir()
    (bad / "service.toml").write_text("[service]\n")
    # plain FILE named like an api -> excluded
    (env / "file-api").write_text("not a dir")

    assert si.available_apis(env) == ["notion-api", "stripe-api"]


def test_available_apis_sorted_deterministically(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["zulip-api", "asana-api", "miro-api"])
    assert si.available_apis(env) == ["asana-api", "miro-api", "zulip-api"]


def test_available_apis_falls_back_to_curated_on_missing_dir(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist"
    apis = si.available_apis(missing)
    assert apis == sorted(si._CURATED_KEYWORDS.keys())
    assert "quickbooks-api" in apis and len(apis) == 10


def test_available_apis_falls_back_to_curated_on_empty_dir(tmp_path: Path) -> None:
    env = tmp_path / "environment"
    env.mkdir()
    assert si.available_apis(env) == sorted(si._CURATED_KEYWORDS.keys())


def test_keywordless_api_dirs_are_dropped_from_catalog(tmp_path: Path) -> None:
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md.
    # A valid service dir whose slug yields no usable keywords (single token
    # shorter than _MIN_TOKEN_LEN, or stopword-only) compiles to (None, None)
    # matchers and is silently excluded from the catalog — so it can never be
    # inferred as required NOR selected as a distractor.
    env = _make_env(tmp_path, ["a-api", "notion-api"])
    assert si.available_apis(env) == ["notion-api"]


def test_all_keywordless_dirs_trigger_curated_fallback(tmp_path: Path) -> None:
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md.
    # If EVERY discovered dir is keyword-less, the catalog ends up empty and
    # the curated fallback kicks in even though the environment dir is populated.
    env = _make_env(tmp_path, ["a-api", "io-api"])
    assert si.available_apis(env) == sorted(si._CURATED_KEYWORDS.keys())


def test_available_apis_real_repo_environment_contains_flagships() -> None:
    apis = si.available_apis()  # default: repo environment/ (checked in, offline)
    for flagship in ("amazon-seller-api", "quickbooks-api", "linear-api"):
        assert flagship in apis
    assert len(apis) > len(si._CURATED_KEYWORDS)  # dynamic discovery, not fallback


def test_domain_tags_alias_is_curated_tags() -> None:
    assert si.DOMAIN_TAGS is si._CURATED_TAGS


# ---------------------------------------------------------------------------
# Section E — infer_required_apis
# ---------------------------------------------------------------------------

def test_infer_empty_prompt_returns_empty_list(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["notion-api"])
    assert si.infer_required_apis("", env) == []
    assert si.infer_required_apis(None, env) == []


def test_infer_single_strong_slug_hit_qualifies(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["notion-api", "stripe-api"])
    assert si.infer_required_apis("Please update my Notion pages", env) == ["notion-api"]


def test_infer_is_case_insensitive(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["notion-api"])
    assert si.infer_required_apis("EXPORT EVERYTHING FROM NOTION", env) == ["notion-api"]


def test_infer_word_boundary_prevents_substring_false_positive(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["notion-api"])
    assert si.infer_required_apis("a notional promotion analysis", env) == []


def test_infer_multiple_matches_sorted(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["notion-api", "stripe-api", "asana-api"])
    out = si.infer_required_apis("move stripe payouts into notion", env)
    assert out == ["notion-api", "stripe-api"]


def test_infer_single_generic_hit_is_not_enough(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["quickbooks-api"])
    # 'invoice' is a generic keyword for quickbooks-api; one hit must not match.
    assert si.infer_required_apis("please send the invoice today", env) == []


def test_infer_two_generic_hits_qualify(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["quickbooks-api"])
    prompt = "send the invoice and file the expense report"
    assert si.infer_required_apis(prompt, env) == ["quickbooks-api"]


def test_infer_same_generic_word_twice_counts_as_two_hits(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["quickbooks-api"])
    # findall counts occurrences, so repeating one generic word reaches the
    # >=2 threshold even though only one distinct domain word appears.
    prompt = "attach invoice A and invoice B"
    assert si.infer_required_apis(prompt, env) == ["quickbooks-api"]


def test_infer_strong_hit_wins_even_with_generic_noise(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["quickbooks-api"])
    assert si.infer_required_apis("log this invoice in quickbooks", env) == ["quickbooks-api"]


def test_infer_curated_phrase_counts_as_strong(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["ring-api"])
    # 'ring doorbell' is a curated strong phrase for ring-api.
    assert si.infer_required_apis("check the ring doorbell feed", env) == ["ring-api"]


def test_infer_generic_pair_for_ring(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["ring-api"])
    assert si.infer_required_apis("the doorbell caught some motion", env) == ["ring-api"]
    assert si.infer_required_apis("there was motion outside", env) == []


def test_infer_multiword_slug_phrase_match(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["google-classroom-api"])
    out = si.infer_required_apis("post the syllabus to google classroom", env)
    assert out == ["google-classroom-api"]


def test_infer_no_match_returns_empty(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["notion-api", "stripe-api"])
    assert si.infer_required_apis("water the plants and walk the dog", env) == []


# ---------------------------------------------------------------------------
# Section F — compute_distractor_skills
# ---------------------------------------------------------------------------

def test_distractors_default_is_full_pool_minus_required(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["alpha-api", "beta-api", "gamma-api", "delta-api"])
    out = si.compute_distractor_skills(["beta-api"], "task-1", environment_dir=env)
    assert out == ["alpha-api", "delta-api", "gamma-api"]


def test_distractors_empty_required_returns_everything(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["alpha-api", "beta-api"])
    assert si.compute_distractor_skills([], "t", environment_dir=env) == ["alpha-api", "beta-api"]


def test_distractors_unknown_required_ignored(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["alpha-api", "beta-api"])
    out = si.compute_distractor_skills(["zzz-api"], "t", environment_dir=env)
    assert out == ["alpha-api", "beta-api"]


def test_distractors_count_zero_or_negative_means_full_pool(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["alpha-api", "beta-api", "gamma-api"])
    full = ["alpha-api", "beta-api", "gamma-api"]
    assert si.compute_distractor_skills([], "t", count=0, environment_dir=env) == full
    assert si.compute_distractor_skills([], "t", count=-3, environment_dir=env) == full


def test_distractors_count_at_or_above_pool_size_returns_full_pool(tmp_path: Path) -> None:
    env = _make_env(tmp_path, ["alpha-api", "beta-api", "gamma-api"])
    full = ["alpha-api", "beta-api", "gamma-api"]
    assert si.compute_distractor_skills([], "t", count=3, environment_dir=env) == full
    assert si.compute_distractor_skills([], "t", count=99, environment_dir=env) == full


def test_distractors_truncation_is_seeded_and_deterministic(tmp_path: Path) -> None:
    names = [f"svc{c}-api" for c in "abcdefgh"]
    env = _make_env(tmp_path, names)
    first = si.compute_distractor_skills(["svca-api"], "task-42", count=3, environment_dir=env)
    second = si.compute_distractor_skills(["svca-api"], "task-42", count=3, environment_dir=env)
    assert first == second
    assert len(first) == 3
    assert first == sorted(first)
    assert set(first) <= set(names) - {"svca-api"}


def test_distractors_empty_task_id_uses_default_seed(tmp_path: Path) -> None:
    names = [f"svc{c}-api" for c in "abcdefgh"]
    env = _make_env(tmp_path, names)
    a = si.compute_distractor_skills([], "", count=2, environment_dir=env)
    b = si.compute_distractor_skills([], "", count=2, environment_dir=env)
    assert a == b and len(a) == 2


def test_distractor_count_hint_constant_retained() -> None:
    # Non-binding legacy hint documented in the module; pin its value.
    assert si.DISTRACTOR_COUNT == 4
