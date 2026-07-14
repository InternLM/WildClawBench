"""Shared Rich console + logging installation for the Kensei harness UI layer.

This module is the single source of truth for terminal rendering on the Python
side of the harness. It mirrors the intent of ``script/lib/log.sh`` (colors only
on a real tty, honoring ``NO_COLOR``) but for ``eval/run_batch.py`` and the agent
backends.

Design invariants:
  * ``get_console()`` returns ONE process-wide ``rich.console.Console``. Rich's
    own tty/``NO_COLOR`` detection means that when stdout is piped/``tee``'d
    (as ``script/run.sh`` does), the console emits plain, ANSI-free text — so
    ``logs/<...>.log`` stays readable and diff-able. Do not force ``force_terminal``.
  * ``install_rich_logging()`` swaps the root logger's handler for a
    ``RichHandler``. Because every harness module logs through
    ``logging.getLogger(__name__)``, this colorizes ALL existing call sites with
    zero edits. It is idempotent and safe to call more than once.
  * Nothing here is imported at ``eval/run_batch.py`` import time; it is wired in
    from ``main()`` so unit tests that import the harness are unaffected.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Optional

try:  # Rich is a declared dependency; degrade gracefully if somehow absent.
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.theme import Theme
    _RICH_AVAILABLE = True
except Exception:  # pragma: no cover - only hit if rich is not installed
    Console = None  # type: ignore
    RichHandler = None  # type: ignore
    Theme = None  # type: ignore
    _RICH_AVAILABLE = False


# Semantic colors shared across the UI layer. Kept close to log.sh conventions:
# info=cyan, ok/success=green, warn=yellow, err=red, plus a couple of accents.
_THEME_STYLES = {
    "info": "cyan",
    "success": "bold green",
    "warning": "yellow",
    "error": "bold red",
    "muted": "dim",
    "accent": "magenta",
    "stage": "bold cyan",
}

_console: "Optional[Console]" = None
_logging_installed = False


def rich_available() -> bool:
    """True when the ``rich`` package imported successfully."""
    return _RICH_AVAILABLE


def is_interactive() -> bool:
    """True when stdout is a real terminal and the user has not set NO_COLOR.

    Used to decide whether to launch the full-screen Textual dashboard and
    whether styled output is even meaningful. ``tee``/pipe sinks are non-tty and
    return False here, which is exactly what keeps ``run.sh`` logs clean.
    """
    if os.environ.get("NO_COLOR"):
        return False
    try:
        return bool(sys.stdout.isatty())
    except Exception:
        return False


def get_console() -> "Optional[Console]":
    """Return the process-wide Rich console (or None if rich is unavailable)."""
    global _console
    if not _RICH_AVAILABLE:
        return None
    if _console is None:
        theme = Theme(_THEME_STYLES) if Theme is not None else None
        # No force_terminal: let Rich auto-detect. On a non-tty sink it drops
        # ANSI, keeping tee'd logs plain. highlight=False avoids Rich mangling
        # arbitrary log payloads (paths, ids) with its auto-highlighter.
        _console = Console(theme=theme, highlight=False, soft_wrap=False)
    return _console


def install_rich_logging(level: int = logging.INFO) -> bool:
    """Attach a RichHandler to the root logger, replacing prior handlers.

    Returns True if the Rich handler was installed, False if rich is unavailable
    (caller then keeps the stdlib basicConfig formatting). Idempotent.
    """
    global _logging_installed
    if not _RICH_AVAILABLE:
        return False
    if _logging_installed:
        return True

    console = get_console()
    handler = RichHandler(
        console=console,
        show_time=True,
        show_level=True,
        show_path=False,
        rich_tracebacks=True,
        markup=False,
        omit_repeated_times=False,
        log_time_format="[%H:%M:%S]",
    )
    root = logging.getLogger()
    # Remove only the default stdout/stderr StreamHandlers (e.g. the one
    # logging.basicConfig installs) so we don't double-print through both them
    # and RichHandler. Any OTHER handler a caller attached — notably a
    # FileHandler — is preserved rather than silently dropped. (FileHandler is a
    # StreamHandler subclass, but its stream is the log file, not stdout/stderr,
    # so the stream check leaves it in place.)
    for h in list(root.handlers):
        if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) in (
            sys.stdout,
            sys.stderr,
        ):
            root.removeHandler(h)
    root.addHandler(handler)
    # Make sure INFO is visible, but never RAISE a level a caller set lower on
    # purpose (e.g. DEBUG) — that would silently hide their debug logs.
    if root.level == logging.NOTSET or root.level > level:
        root.setLevel(level)
    _logging_installed = True
    return True


# --- semantic one-line helpers ------------------------------------------------
# These are convenience wrappers for harness code that wants to print a styled
# status line directly (as opposed to going through `logging`). They no-op
# gracefully to plain print when rich is unavailable.

def _emit(style: str, prefix: str, message: str, *, err: bool = False) -> None:
    console = get_console()
    if console is None:
        stream = sys.stderr if err else sys.stdout
        print(f"{prefix} {message}", file=stream)
        return
    console.print(f"{prefix} {message}", style=style, stderr=err)


def ui_info(message: str) -> None:
    _emit("info", "•", message)


def ui_success(message: str) -> None:
    _emit("success", "✓", message)


def ui_warn(message: str) -> None:
    _emit("warning", "!", message, err=True)


def ui_error(message: str) -> None:
    _emit("error", "✗", message, err=True)
