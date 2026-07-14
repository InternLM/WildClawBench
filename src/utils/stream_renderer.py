"""Terminal renderer for the live-stream feed (stream.jsonl / agent.log).

Consumer half of the streaming feature (docs/STREAMING_PLAN.md §4). Runs as
a daemon thread inside eval/run_batch.py::run_single_task, strictly
display-only: it reads the observability feed and prints; nothing graded
depends on it (R1) and stopping it is bounded (stop() joins ≤5s, R3).

Output target resolution (in order):
  1. /dev/tty when openable — the primary case: under `script/run.sh` stdout
     is piped through `tee logs/<run>.log`, so isatty(stdout) is False even
     though a human is watching. Writing to the controlling terminal keeps
     the run log free of token spew while the operator still sees it live.
  2. sys.stdout when it is a tty (direct `python3 eval/run_batch.py` runs).
  3. Otherwise "summary mode": one aggregate line every ~5s via print() —
     tee'd logs stay small; full fidelity lives in stream.jsonl.

Modes:
  * token mode  — tail stream.jsonl (start offset = file EOF at start()):
      - agent text deltas of the MAIN session: printed raw as they arrive.
        Main session = first agent request seen; additional concurrent agent
        requests (openclaw sub-agents, image-tool calls) render as one
        status line each — token-interleaving them is unreadable.
      - agent thinking deltas: dim, prefixed [thinking] per block; hidden
        entirely when WCB_STREAM_THINKING is falsy.
      - judge:*/testgen: line-buffered with a [source] prefix.
      - while NO agent token has arrived yet (container setup, the wait
        before the first LLM call, or a dead sidecar hook), the pane shows
        agent.log turn narration instead; the FIRST agent feed row promotes
        to token rendering permanently. No staleness clock, no one-way
        fallback (the old 30s design missed a healthy feed — see
        _run_token_mode docstring).
  * turn mode   — tail agent.log (openclaw's real-time turn narration),
      printing whole lines. The primary mode when run_batch starts the
      renderer without a stream path (WCB_STREAM_LOG_PATH unset).
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Optional, TextIO

_TRUTHY = ("1", "true", "yes", "on")
_POLL_SECS = 0.2
_SUMMARY_EVERY_SECS = 5.0
_DIM = "\033[2m"
_RESET = "\033[0m"
# Bus-mode flush policy: agent deltas are batched into readable chunks for the
# dashboard's RichLog (which appends entries, not characters). A chunk flushes
# on newline, on reaching _BUS_CHUNK_CHARS (split at the last space when one
# exists past a minimum), or when the buffer sat unflushed for _BUS_STALE_SECS.
_BUS_CHUNK_CHARS = 80
_BUS_STALE_SECS = 0.4


def _thinking_enabled() -> bool:
    raw = os.environ.get("WCB_STREAM_THINKING", "1").strip().lower()
    return raw in _TRUTHY


def _publish_token(style: str, text: str) -> None:
    """Publish one display-ready chunk onto the TUI event bus (EV_TOKEN).

    Lazy import; raises to the caller, which latches the renderer's _bus_dead
    (R2 fail-open). Emitting with no subscriber is a documented bus no-op, so
    stray calls outside a dashboard display nothing and cost ~nothing.
    """
    from src.utils.ui.events import EV_TOKEN, get_bus
    get_bus().emit(EV_TOKEN, style=style, text=text)


class StreamRenderer(threading.Thread):
    """Display-only follower of the stream feed. Never raises out of run()."""

    def __init__(
        self,
        stream_path: Optional[Path],
        agent_log_path: Optional[Path],
        run_label: str = "",
        mode: str = "tty",
    ) -> None:
        super().__init__(name="wcb-stream-renderer", daemon=True)
        self._stream_path = Path(stream_path) if stream_path else None
        self._agent_log_path = Path(agent_log_path) if agent_log_path else None
        self._run_label = run_label
        # "tty": write to the terminal (default). "bus": publish EV_TOKEN
        # events for the Textual dashboard's Live Stream pane instead — used
        # when lifecycle.is_dashboard_active() (see start_renderer). Same
        # thread, same tail loops, same classification state; only the final
        # output primitive differs.
        self._mode = mode if mode in ("tty", "bus") else "tty"
        self._stop_event = threading.Event()
        self._out: Optional[TextIO] = None
        self._owns_out = False
        self._interactive = False
        self._color = False
        # display state
        self._main_request: Optional[str] = None
        self._open_requests: set[str] = set()
        self._cur_kind: Optional[str] = None  # last agent kind printed (text/thinking)
        self._line_buf: dict[str, str] = {}  # per-source partial lines (judges)
        self._delta_count = 0
        self._last_summary = 0.0
        # bus-mode state
        self._bus_buf = ""
        self._bus_kind: Optional[str] = None  # kind of the buffered agent chunk
        self._bus_last_append = 0.0
        self._bus_dead = False  # latched on first publish failure (fail-open)

    # ------------------------------------------------------------------ setup

    def _resolve_out(self) -> None:
        try:
            fh = open("/dev/tty", "w", encoding="utf-8", errors="replace")
            self._out, self._owns_out, self._interactive = fh, True, True
        except OSError:
            if sys.stdout.isatty():
                self._out, self._interactive = sys.stdout, True
            else:
                self._out, self._interactive = sys.stdout, False
        self._color = self._interactive and not os.environ.get("NO_COLOR")

    def _w(self, text: str) -> None:
        if self._mode == "bus":
            return  # bus mode never touches a terminal (belt over braces)
        try:
            assert self._out is not None
            self._out.write(text)
            self._out.flush()
        except Exception:
            # A dead terminal must never take the run down with it.
            self._stop_event.set()

    def _line(self, text: str, dim: bool = False, style: Optional[str] = None) -> None:
        if self._mode == "bus":
            # Whole-line entries map straight to bus events. Callers that
            # don't pass an explicit style get the historical semantics:
            # dim lines are status chatter, bright lines are judge content.
            self._bus_send(style or ("status" if dim else "judge"), text)
            return
        if dim and self._color:
            self._w(f"{_DIM}{text}{_RESET}\n")
        else:
            self._w(text + "\n")

    # ------------------------------------------------------------- bus output

    def _bus_send(self, style: str, text: str) -> None:
        """Publish one chunk; fail-open (first failure disables publishing)."""
        if self._bus_dead or not text:
            return
        try:
            _publish_token(style, text)
        except Exception:
            self._bus_dead = True

    def _bus_append(self, kind: str, delta: str) -> None:
        """Buffer an agent delta; flush in readable chunks (see policy above)."""
        if self._bus_kind != kind:
            self._bus_flush()
            self._bus_kind = kind
        self._bus_buf += delta
        self._bus_last_append = time.time()
        while "\n" in self._bus_buf:
            line, self._bus_buf = self._bus_buf.split("\n", 1)
            self._bus_send(self._bus_kind or "text", line)
        while len(self._bus_buf) >= _BUS_CHUNK_CHARS:
            cut = self._bus_buf.rfind(" ", 20, _BUS_CHUNK_CHARS)
            if cut == -1:
                cut = _BUS_CHUNK_CHARS
            chunk = self._bus_buf[:cut]
            self._bus_buf = self._bus_buf[cut:].lstrip(" ")
            self._bus_send(self._bus_kind or "text", chunk)

    def _bus_flush(self) -> None:
        if self._bus_buf.strip():
            self._bus_send(self._bus_kind or "text", self._bus_buf)
        self._bus_buf = ""

    def _bus_flush_if_stale(self) -> None:
        if (self._bus_buf
                and time.time() - self._bus_last_append >= _BUS_STALE_SECS):
            self._bus_flush()

    # ---------------------------------------------------------------- control

    def stop(self, timeout: float = 5.0) -> None:
        """Signal + bounded join (R3). Only teardown waits on this; grading
        never does. Never raises."""
        try:
            self._stop_event.set()
            self.join(timeout=timeout)
            self._flush_partial_lines()
            if self._owns_out and self._out is not None:
                self._out.close()
        except Exception:
            pass

    # ------------------------------------------------------------------- run

    def run(self) -> None:  # noqa: D102
        try:
            if self._mode == "bus":
                # No terminal: output goes to the event bus. Treat as
                # interactive so the full render path runs (not summary mode).
                self._interactive = True
                self._color = False
            else:
                self._resolve_out()
            if self._stream_path is not None:
                self._run_token_mode()
            elif self._agent_log_path is not None:
                self._run_turn_mode()
        except Exception:
            # Display-only thread: swallow everything (R2).
            pass

    # ------------------------------------------------------------ token mode

    def _run_token_mode(self) -> None:
        """Watch the token feed AND, until agent tokens arrive, agent.log.

        History: the first design switched ONE-WAY to agent.log tailing after
        a 30s staleness window. That clock started at renderer start — which
        is during container setup, minutes before the agent's first LLM call —
        so a perfectly healthy token feed was never rendered (matt_garcia
        run_1, 2026-07-13: 1,748 feed rows captured, pane stuck in narration
        mode). Now there is no clock and no one-way door: agent.log turn
        narration renders only WHILE no agent-source token has arrived; the
        first agent feed row promotes the pane to token rendering and stops
        the narration tail (narration duplicates each turn's final text, so
        showing both would double content). Non-agent feed rows (testgen
        status, judges) render in either state and do not end the narration.
        """
        assert self._stream_path is not None
        # Start at current EOF: prior reps' events in a shared batch feed are
        # behind this offset by construction (single-run foreground gate D6).
        feed_offset = self._stream_path.stat().st_size if self._stream_path.exists() else 0
        feed_carry = ""
        log_offset = 0
        log_carry = ""
        tokens_live = False
        showed_narration = False
        while not self._stop_event.is_set():
            if self._mode == "bus":
                # Time-based flush so a paused model (thinking gap) doesn't
                # hold the last chunk hostage in the buffer.
                self._bus_flush_if_stale()
            progressed = False

            # --- token feed: always read, always preferred -----------------
            if self._stream_path.exists():
                try:
                    with open(self._stream_path, "r", encoding="utf-8", errors="replace") as fh:
                        fh.seek(feed_offset)
                        data = fh.read()
                        feed_offset = fh.tell()
                except OSError:
                    data = ""
                if data:
                    progressed = True
                    feed_carry += data
                    lines = feed_carry.split("\n")
                    feed_carry = lines.pop()  # possibly-torn trailing fragment
                    for raw in lines:
                        raw = raw.strip()
                        if not raw:
                            continue
                        try:
                            evt = json.loads(raw)
                        except json.JSONDecodeError:
                            continue  # torn line — skip, never error
                        if not tokens_live and str(evt.get("source") or "") == "agent":
                            tokens_live = True
                            if showed_narration:
                                self._line("[stream] token feed live — switching "
                                           "from turn narration", dim=True)
                        self._render_event(evt)

            # --- agent.log narration: only while no agent tokens yet -------
            if (not tokens_live and self._agent_log_path is not None
                    and self._agent_log_path.exists()):
                try:
                    with open(self._agent_log_path, "r", encoding="utf-8", errors="replace") as fh:
                        fh.seek(log_offset)
                        data = fh.read()
                        log_offset = fh.tell()
                except OSError:
                    data = ""
                if data:
                    progressed = True
                    log_carry += data
                    lines = log_carry.split("\n")
                    log_carry = lines.pop()
                    for ln in lines:
                        if not ln.strip():
                            continue
                        showed_narration = True
                        if self._interactive:
                            self._line(f"[agent] {ln}", style="text")
                        else:
                            self._summary_tick("delta")

            if not progressed:
                self._stop_event.wait(_POLL_SECS)
        # drain nothing further; stop() flushes partial lines

    def _render_event(self, evt: dict) -> None:
        source = str(evt.get("source") or "")
        event = str(evt.get("event") or "")
        kind = str(evt.get("kind") or "text")
        delta = evt.get("delta") or ""
        req = str(evt.get("request_id") or "")

        if not self._interactive:
            self._summary_tick(event)
            return

        if source == "agent":
            self._render_agent(event, kind, str(delta), req)
        else:
            self._render_line_buffered(source, event, str(delta))

    def _render_agent(self, event: str, kind: str, delta: str, req: str) -> None:
        if event == "message_start":
            if req in self._open_requests or req == self._main_request:
                return  # duplicate start for an already-open request
            self._open_requests.add(req)
            if self._main_request is None:
                self._main_request = req
            else:
                self._line(f"[sub-agent {req[:8]}] started", dim=True)
            return
        if event in ("message_stop", "error"):
            self._open_requests.discard(req)
            if req == self._main_request:
                if self._mode == "bus":
                    self._bus_flush()  # a turn ended: release the tail chunk
                if self._cur_kind is not None:
                    self._w("\n")
                    self._cur_kind = None
                self._main_request = None  # next request becomes main (next turn)
                if event == "error":
                    self._line(f"[stream error] {delta}", dim=True)
            else:
                self._line(f"[sub-agent {req[:8]}] "
                           f"{'done' if event == 'message_stop' else 'error'}", dim=True)
            return
        if event != "delta":
            return
        if req != self._main_request:
            return  # sub-agent deltas: status lines only (D5)
        if kind == "thinking" and not _thinking_enabled():
            return
        if self._mode == "bus":
            # Same classification brain, different sink: batch into readable
            # chunks for the dashboard pane (style == kind: thinking|text).
            self._bus_append("thinking" if kind == "thinking" else "text", delta)
            return
        if kind == "thinking":
            if self._cur_kind != "thinking":
                if self._cur_kind is not None:
                    self._w("\n")
                self._w(f"{_DIM}[thinking] " if self._color else "[thinking] ")
                self._cur_kind = "thinking"
            self._w(delta if not self._color else delta)  # dim already open
            return
        # text
        if self._cur_kind != "text":
            if self._cur_kind == "thinking":
                self._w(f"{_RESET}\n" if self._color else "\n")
            self._cur_kind = "text"
        self._w(delta)

    def _render_line_buffered(self, source: str, event: str, delta: str) -> None:
        if event == "message_start":
            self._line(f"[{source}] …", dim=True)
            return
        if event in ("message_stop", "error", "status"):
            buf = self._line_buf.pop(source, "")
            if buf:
                self._line(f"[{source}] {buf}")
            if event == "error":
                self._line(f"[{source}] ERROR {delta}", dim=True)
            elif event == "status":
                self._line(f"[{source}] {delta}", dim=True)
            return
        # delta: flush complete lines only
        buf = self._line_buf.get(source, "") + delta
        *complete, rest = buf.split("\n")
        for ln in complete:
            self._line(f"[{source}] {ln}")
        self._line_buf[source] = rest

    def _flush_partial_lines(self) -> None:
        try:
            if self._mode == "bus":
                self._bus_flush()  # release any tail agent chunk
            if self._cur_kind is not None and self._interactive and self._mode == "tty":
                self._w(f"{_RESET}\n" if self._color else "\n")
                self._cur_kind = None
            for source, buf in list(self._line_buf.items()):
                if buf and self._interactive:
                    self._line(f"[{source}] {buf}")
            self._line_buf.clear()
        except Exception:
            pass

    def _summary_tick(self, event: str) -> None:
        if event == "delta":
            self._delta_count += 1
        now = time.time()
        if now - self._last_summary >= _SUMMARY_EVERY_SECS and self._delta_count:
            self._last_summary = now
            print(f"[stream] {self._run_label} +{self._delta_count} deltas", flush=True)
            self._delta_count = 0

    # ------------------------------------------------------------- turn mode

    def _run_turn_mode(self) -> None:
        """Tail agent.log (openclaw's live turn narration), whole lines."""
        if self._agent_log_path is None:
            return
        offset = 0
        carry = ""
        while not self._stop_event.is_set():
            if not self._agent_log_path.exists():
                self._stop_event.wait(_POLL_SECS)
                continue
            try:
                with open(self._agent_log_path, "r", encoding="utf-8", errors="replace") as fh:
                    fh.seek(offset)
                    data = fh.read()
                    offset = fh.tell()
            except OSError:
                self._stop_event.wait(_POLL_SECS)
                continue
            if not data:
                self._stop_event.wait(_POLL_SECS)
                continue
            carry += data
            lines = carry.split("\n")
            carry = lines.pop()
            for ln in lines:
                if not ln.strip():
                    continue
                if self._interactive:
                    # agent.log narration is agent output, not judge content —
                    # style it as plain text in the dashboard pane (bus mode).
                    self._line(f"[agent] {ln}", style="text")
                else:
                    self._summary_tick("delta")


def start_renderer(
    stream_path: Optional[Path],
    agent_log_path: Optional[Path],
    run_label: str = "",
) -> Optional[StreamRenderer]:
    """Create+start a renderer when streaming is enabled, else None.

    Gate matches stream_events: WCB_STREAM truthy. token mode needs
    WCB_STREAM_LOG_PATH (stream_path); otherwise turn mode over agent.log.

    Output routing: when the Textual dashboard owns the terminal
    (lifecycle.is_dashboard_active()), raw tty writes would corrupt its
    canvas — so the renderer runs in BUS mode instead, publishing EV_TOKEN
    events that the dashboard's Live Stream pane renders (single-terminal
    TUI + streaming). Otherwise it renders to the tty as before. Either way
    the feed/taps/grading are untouched (R1). Never raises."""
    try:
        if os.environ.get("WCB_STREAM", "").strip().lower() not in _TRUTHY:
            return None
        mode = "bus" if _dashboard_active() else "tty"
        r = StreamRenderer(stream_path, agent_log_path, run_label=run_label, mode=mode)
        r.start()
        return r
    except Exception:
        return None


def _dashboard_active() -> bool:
    """True while the Textual dashboard owns the terminal (src/utils/ui).

    Fail-open in BOTH directions: if the UI package is absent or broken there
    is no dashboard, so False (render normally) is always the safe answer."""
    try:
        from src.utils.ui import lifecycle as _lifecycle
        return bool(_lifecycle.is_dashboard_active())
    except Exception:
        return False
