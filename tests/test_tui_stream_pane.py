"""Tests for the dashboard's Live Stream pane (EV_TOKEN → RichLog#stream).

Covers: token_markup (pure, no textual needed), and a headless end-to-end of
the REAL dashboard — bus emit from a worker thread → call_from_thread marshal
→ #stream pane receives entries — using Textual's run_test pilot. The
headless test skips cleanly when textual is not installed.
"""
from __future__ import annotations

import asyncio
import sys
import threading
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.ui.tui import token_markup, textual_available  # noqa: E402
from src.utils.ui.events import EV_TOKEN, get_bus  # noqa: E402


# ------------------------------------------------------------- token_markup

def test_token_markup_styles():
    assert token_markup({"style": "text", "text": "hello"}) == "hello"
    got = token_markup({"style": "thinking", "text": "hmm"})
    assert got.startswith("[dim]") and "\\[thinking] hmm" in got and got.endswith("[/]")
    got = token_markup({"style": "judge", "text": "[judge:kimi] 1. Yes"})
    assert got.startswith("[cyan]") and "\\[judge:kimi] 1. Yes" in got
    got = token_markup({"style": "status", "text": "attempt 1/3"})
    assert got.startswith("[dim italic]")


def test_token_markup_escapes_model_output():
    """Model text must never inject live Rich markup into the pane."""
    evil = token_markup({"style": "text", "text": "[bold red]pwned[/]"})
    assert "\\[bold red]" in evil  # opening tags neutralized
    assert not evil.startswith("[bold red]")


def test_token_markup_defaults_and_junk():
    assert token_markup({}) == "[dim italic][/]"
    assert "42" in token_markup({"style": "text", "text": 42})  # non-str tolerated


# ------------------------------------------------- headless dashboard e2e

@pytest.mark.skipif(not textual_available(), reason="textual not installed")
def test_stream_pane_receives_tokens_headless():
    """Real HarnessDashboard, headless: EV_TOKEN emitted from a WORKER thread
    (production shape — call_from_thread rejects same-thread calls) lands in
    the #stream RichLog; the #log pane is untouched by token events."""
    from textual.widgets import RichLog
    from src.utils.ui.tui import HarnessDashboard

    async def scenario():
        done = threading.Event()

        def work():
            done.wait(timeout=5.0)  # keep the worker alive until we finish

        app = HarnessDashboard(work)
        async with app.run_test() as pilot:
            await pilot.pause()
            stream = app.query_one("#stream", RichLog)
            log = app.query_one("#log", RichLog)
            log_before = len(log.lines)
            assert len(stream.lines) == 0  # pane starts empty

            def emit_from_worker():
                get_bus().emit(EV_TOKEN, style="text", text="streamed inside the TUI")
                get_bus().emit(EV_TOKEN, style="thinking", text="pondering")
                get_bus().emit(EV_TOKEN, style="judge", text="[judge:glm] 1. Yes")

            # DO NOT t.join() here: call_from_thread blocks the emitter until
            # the UI loop (this thread!) processes the event — joining before
            # awaiting is a loop<->thread AB-BA deadlock (found via
            # faulthandler dump; production never blocks the UI loop on an
            # emitter, so this is a test-shape hazard only).
            t = threading.Thread(target=emit_from_worker, daemon=True)
            t.start()
            for _ in range(40):  # awaiting lets the loop drain the emits
                await pilot.pause(0.05)
                if len(stream.lines) >= 3:
                    break
            t.join(timeout=2.0)
            assert not t.is_alive()  # all three emits fully processed
            assert len(stream.lines) >= 3  # all three entries rendered
            pane_text = "\n".join(strip.text for strip in stream.lines)
            assert "streamed inside the TUI" in pane_text
            assert "pondering" in pane_text
            assert "1. Yes" in pane_text
            assert len(log.lines) == log_before  # tokens never leak to #log
            # Release the worker and WAIT for _on_work_done to land on the UI
            # thread BEFORE exiting run_test: exiting while the worker is
            # mid-call_from_thread deadlocks the shutdown (the app stops
            # pumping messages while its teardown awaits the worker).
            done.set()
            for _ in range(100):
                await pilot.pause(0.05)
                if app._done:
                    break
            assert app._done  # worker finished cleanly inside the app's lifetime

    asyncio.run(scenario())
