"""Single source of truth for LLM system / user prompts.

All prompts live under `<repo_root>/system_prompts/` as `.md` files. Code reads
them via `load_prompt(name, **fmt)`. Edits do not require restarting the
process: the LRU cache is keyed on the file path, and `clear_prompt_cache()`
flushes it (called automatically when `WCB_PROMPT_NOCACHE=1`).

See `system_prompts/README.md` for the loader contract and naming convention.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

# Repo-root anchored — this file lives at src/utils/prompt_loader.py, the
# system_prompts/ dir lives at the repo root, hence parents[2]. Resolving via
# anchor (not Path.cwd()) so behavior is identical whether the harness is
# invoked from the repo root, from eval/, or from a tmp working dir during
# test_executor subprocess runs.
_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "system_prompts"


class PromptNotFoundError(FileNotFoundError):
    pass


def prompts_dir() -> Path:
    return _PROMPTS_DIR


@lru_cache(maxsize=64)
def _read(path_str: str) -> str:
    return Path(path_str).read_text(encoding="utf-8")


def clear_prompt_cache() -> None:
    _read.cache_clear()


def load_prompt(name: str, **fmt: object) -> str:
    """Return the contents of `system_prompts/<name>.md`.

    If `fmt` is non-empty, `str.format(**fmt)` is applied. Placeholders in the
    file use Python's `{name}` syntax. Literal braces must be doubled (`{{` /
    `}}`) per `str.format` rules.

    `WCB_PROMPT_NOCACHE=1` in env disables the cache (useful when iterating on
    prompts without restarting a long-running harness).
    """
    if os.environ.get("WCB_PROMPT_NOCACHE") == "1":
        clear_prompt_cache()
    # Accept `name`, `name.md`, or a relative subpath. We DO NOT accept
    # absolute paths or anything containing `..` — the loader is purely a
    # whitelist into the prompts dir. This is defensive: a future caller
    # passing untrusted input cannot read /etc/passwd through here.
    if name.endswith(".md"):
        rel = name
    else:
        rel = f"{name}.md"
    target = (_PROMPTS_DIR / rel).resolve()
    try:
        target.relative_to(_PROMPTS_DIR)
    except ValueError as exc:
        raise PromptNotFoundError(
            f"prompt name {name!r} resolves outside system_prompts/"
        ) from exc
    if not target.is_file():
        raise PromptNotFoundError(
            f"prompt {name!r} not found at {target}"
        )
    text = _read(str(target))
    if fmt:
        return text.format(**fmt)
    return text
