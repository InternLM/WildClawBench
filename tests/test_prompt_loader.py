"""Tests for src/utils/prompt_loader.py.

Pins the loader contract:
- Path resolution: `name`, `name.md`, and relative subpaths resolve inside
  `system_prompts/`; absolute paths and `..` traversal are rejected with
  PromptNotFoundError (a FileNotFoundError subclass).
- Format substitution: `str.format(**fmt)` is applied only when fmt kwargs are
  passed; literal braces must be doubled per str.format rules; without fmt the
  text passes through verbatim (braces untouched).
- Caching: `_read` is LRU-cached on the resolved path string, so edits to a
  prompt file are invisible until `clear_prompt_cache()` — unless
  WCB_PROMPT_NOCACHE=1 (exactly "1") is set, which flushes on every call.

No network, no docker, no subprocess: pure filesystem via pytest tmp_path
plus read-only reads of the real system_prompts/*.md files.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import prompt_loader  # noqa: E402
from src.utils.prompt_loader import (  # noqa: E402
    PromptNotFoundError,
    clear_prompt_cache,
    load_prompt,
    prompts_dir,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_prompts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the loader at a temp system_prompts dir with a clean cache.

    tmp_path is resolved first: on macOS pytest tmp dirs live behind the
    /var -> /private/var symlink, and load_prompt compares resolved paths.
    """
    pdir = tmp_path.resolve() / "system_prompts"
    pdir.mkdir()
    monkeypatch.setattr(prompt_loader, "_PROMPTS_DIR", pdir)
    monkeypatch.delenv("WCB_PROMPT_NOCACHE", raising=False)
    clear_prompt_cache()
    yield pdir
    clear_prompt_cache()


@pytest.fixture()
def real_prompts(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Unpatched loader against the repo's real system_prompts/ (read-only)."""
    monkeypatch.delenv("WCB_PROMPT_NOCACHE", raising=False)
    clear_prompt_cache()
    yield prompts_dir()
    clear_prompt_cache()


# ---------------------------------------------------------------------------
# Section A — path resolution
# ---------------------------------------------------------------------------


def test_bare_name_gets_md_suffix(tmp_prompts: Path) -> None:
    (tmp_prompts / "hello.md").write_text("hi there", encoding="utf-8")
    assert load_prompt("hello") == "hi there"


def test_explicit_md_suffix_not_doubled(tmp_prompts: Path) -> None:
    (tmp_prompts / "hello.md").write_text("hi there", encoding="utf-8")
    assert load_prompt("hello.md") == "hi there"
    assert not (tmp_prompts / "hello.md.md").exists()


def test_relative_subpath_resolves_inside_prompts_dir(tmp_prompts: Path) -> None:
    sub = tmp_prompts / "sub"
    sub.mkdir()
    (sub / "inner.md").write_text("nested", encoding="utf-8")
    assert load_prompt("sub/inner") == "nested"


def test_missing_prompt_raises_prompt_not_found(tmp_prompts: Path) -> None:
    with pytest.raises(PromptNotFoundError, match="not found"):
        load_prompt("does_not_exist")


def test_prompt_not_found_is_file_not_found_subclass(tmp_prompts: Path) -> None:
    # Callers catching FileNotFoundError keep working.
    with pytest.raises(FileNotFoundError):
        load_prompt("does_not_exist")


def test_empty_name_raises_not_found(tmp_prompts: Path) -> None:
    with pytest.raises(PromptNotFoundError):
        load_prompt("")


def test_directory_name_raises_not_found(tmp_prompts: Path) -> None:
    (tmp_prompts / "adir.md").mkdir()
    with pytest.raises(PromptNotFoundError, match="not found"):
        load_prompt("adir")


def test_dotdot_traversal_rejected(tmp_prompts: Path) -> None:
    # File genuinely exists one level above the prompts dir — still refused.
    (tmp_prompts.parent / "evil.md").write_text("secret", encoding="utf-8")
    with pytest.raises(PromptNotFoundError, match="resolves outside"):
        load_prompt("../evil")
    with pytest.raises(PromptNotFoundError, match="resolves outside"):
        load_prompt("../evil.md")


def test_absolute_path_rejected(tmp_prompts: Path) -> None:
    outside = tmp_prompts.parent / "abs_target.md"
    outside.write_text("secret", encoding="utf-8")
    with pytest.raises(PromptNotFoundError, match="resolves outside"):
        load_prompt(str(outside))


def test_symlink_escaping_prompts_dir_rejected(tmp_prompts: Path) -> None:
    outside = tmp_prompts.parent / "outside.md"
    outside.write_text("secret", encoding="utf-8")
    (tmp_prompts / "sneaky.md").symlink_to(outside)
    # resolve() follows the link, landing outside the whitelist.
    with pytest.raises(PromptNotFoundError, match="resolves outside"):
        load_prompt("sneaky")


# ---------------------------------------------------------------------------
# Section B — format substitution
# ---------------------------------------------------------------------------


def test_fmt_substitutes_placeholders(tmp_prompts: Path) -> None:
    (tmp_prompts / "t.md").write_text(
        "Hello {agent}, weight={weight}", encoding="utf-8"
    )
    assert load_prompt("t", agent="kensei", weight=5) == "Hello kensei, weight=5"


def test_fmt_key_named_name_collides_with_positional_param(
    tmp_prompts: Path,
) -> None:
    # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md. A prompt
    # placeholder called {name} is unusable via kwargs because it collides
    # with load_prompt's first positional parameter.
    (tmp_prompts / "t.md").write_text("Hello {name}", encoding="utf-8")
    with pytest.raises(TypeError):
        load_prompt("t", name="kensei")


def test_fmt_double_braces_escape_to_literal(tmp_prompts: Path) -> None:
    (tmp_prompts / "t.md").write_text(
        '{{"verdict": "{verdict}"}}', encoding="utf-8"
    )
    assert load_prompt("t", verdict="Yes") == '{"verdict": "Yes"}'


def test_no_fmt_passes_braces_through_verbatim(tmp_prompts: Path) -> None:
    raw = "{unfilled} and {{still-doubled}}"
    (tmp_prompts / "t.md").write_text(raw, encoding="utf-8")
    # Without fmt kwargs, str.format is never applied: no substitution, no
    # de-escaping of doubled braces.
    assert load_prompt("t") == raw


def test_fmt_missing_placeholder_key_raises_keyerror(tmp_prompts: Path) -> None:
    (tmp_prompts / "t.md").write_text("{a} {b}", encoding="utf-8")
    with pytest.raises(KeyError):
        load_prompt("t", a="only-a")


def test_fmt_on_unescaped_single_brace_raises_valueerror(tmp_prompts: Path) -> None:
    (tmp_prompts / "t.md").write_text("dangling { brace {x}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_prompt("t", x=1)


def test_fmt_extra_keys_are_ignored(tmp_prompts: Path) -> None:
    (tmp_prompts / "t.md").write_text("just {one}", encoding="utf-8")
    assert load_prompt("t", one=1, unused="ignored") == "just 1"


def test_fmt_non_string_values_stringified(tmp_prompts: Path) -> None:
    (tmp_prompts / "t.md").write_text("k={k} n={n}", encoding="utf-8")
    assert load_prompt("t", k=[1, 2], n=None) == "k=[1, 2] n=None"


# ---------------------------------------------------------------------------
# Section C — cache behavior and WCB_PROMPT_NOCACHE
# ---------------------------------------------------------------------------


def test_cache_serves_stale_content_after_edit(tmp_prompts: Path) -> None:
    f = tmp_prompts / "p.md"
    f.write_text("v1", encoding="utf-8")
    assert load_prompt("p") == "v1"
    f.write_text("v2", encoding="utf-8")
    # Cached: edit is invisible.
    assert load_prompt("p") == "v1"


def test_clear_prompt_cache_picks_up_edit(tmp_prompts: Path) -> None:
    f = tmp_prompts / "p.md"
    f.write_text("v1", encoding="utf-8")
    assert load_prompt("p") == "v1"
    f.write_text("v2", encoding="utf-8")
    clear_prompt_cache()
    assert load_prompt("p") == "v2"


def test_nocache_env_bypasses_cache_every_call(
    tmp_prompts: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = tmp_prompts / "p.md"
    f.write_text("v1", encoding="utf-8")
    assert load_prompt("p") == "v1"
    monkeypatch.setenv("WCB_PROMPT_NOCACHE", "1")
    f.write_text("v2", encoding="utf-8")
    assert load_prompt("p") == "v2"
    f.write_text("v3", encoding="utf-8")
    assert load_prompt("p") == "v3"


def test_nocache_env_must_be_exactly_one(
    tmp_prompts: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # NOTE: pins current behavior — only the literal string "1" disables the
    # cache; "true"/"0"/"yes" leave it enabled.
    f = tmp_prompts / "p.md"
    f.write_text("v1", encoding="utf-8")
    assert load_prompt("p") == "v1"
    f.write_text("v2", encoding="utf-8")
    for value in ("true", "0", "yes", ""):
        monkeypatch.setenv("WCB_PROMPT_NOCACHE", value)
        assert load_prompt("p") == "v1"  # still stale => cache intact


def test_cache_is_keyed_per_path(tmp_prompts: Path) -> None:
    (tmp_prompts / "a.md").write_text("alpha", encoding="utf-8")
    (tmp_prompts / "b.md").write_text("beta", encoding="utf-8")
    assert load_prompt("a") == "alpha"
    assert load_prompt("b") == "beta"
    # Caching one file must not shadow the other.
    assert load_prompt("a") == "alpha"


def test_fmt_applies_even_on_cached_read(tmp_prompts: Path) -> None:
    (tmp_prompts / "t.md").write_text("hi {who}", encoding="utf-8")
    assert load_prompt("t", who="first") == "hi first"
    # Second call hits the cache but formats with fresh kwargs.
    assert load_prompt("t", who="second") == "hi second"
    # And the cached raw text (with placeholder) is what no-fmt returns.
    assert load_prompt("t") == "hi {who}"


# ---------------------------------------------------------------------------
# Section D — real system_prompts/ files (read-only)
# ---------------------------------------------------------------------------


def test_prompts_dir_points_at_repo_system_prompts(real_prompts: Path) -> None:
    assert real_prompts == REPO_ROOT / "system_prompts"
    assert real_prompts.is_dir()


def test_real_prompt_loads_and_matches_disk(real_prompts: Path) -> None:
    on_disk = (real_prompts / "judge_system.md").read_text(encoding="utf-8")
    assert on_disk  # sanity: repo file is non-empty
    assert load_prompt("judge_system") == on_disk
    assert load_prompt("judge_system.md") == on_disk


def test_real_fmt_prompt_passes_placeholders_through_without_fmt(
    real_prompts: Path,
) -> None:
    # judge_user.md is a **fmt prompt; loaded WITHOUT kwargs its placeholders
    # must survive verbatim (format is only applied when fmt is non-empty).
    text = load_prompt("judge_user")
    assert "{task_description}" in text
