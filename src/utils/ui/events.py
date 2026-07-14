"""A tiny thread-safe event bus decoupling harness instrumentation from renderers.

The harness emits lifecycle / progress / log events (see ``lifecycle.py``) at
various points. Those events must reach *whichever* renderer is active — the Rich
console by default, or the Textual dashboard when ``--tui`` is used — without the
harness code knowing which one is listening.

Contract:
  * Emitting when nobody is subscribed is a safe no-op. This is what lets the
    agent backends call ``lifecycle.emit_stage(...)`` unconditionally without
    breaking non-UI code paths or unit tests.
  * Subscribers receive ``Event`` objects on the emitting thread. The Textual
    app subscribes with a callback that marshals onto its own event loop
    (``App.call_from_thread``), so subscriber callbacks must be cheap and
    non-blocking.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

# Event kinds.
EV_STAGE = "stage"        # container / task lifecycle stage transition
EV_PROGRESS = "progress"  # completed / total counter update
EV_LOG = "log"            # a free-form log line (level, message)
EV_SUMMARY = "summary"    # final execution summary payload
EV_TOKEN = "token"        # live LLM stream chunk for the dashboard's stream pane
                          # payload: {style: thinking|text|judge|status, text: str}
                          # producer: src/utils/stream_renderer.py in bus mode
                          # (docs/STREAMING_PLAN.md — display-only, fail-open)


@dataclass
class Event:
    kind: str
    payload: Dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


Subscriber = Callable[[Event], None]


class EventBus:
    def __init__(self) -> None:
        self._subs: List[Subscriber] = []
        self._lock = threading.Lock()

    def subscribe(self, fn: Subscriber) -> Callable[[], None]:
        """Register a subscriber. Returns an unsubscribe callable."""
        with self._lock:
            self._subs.append(fn)

        def _unsub() -> None:
            with self._lock:
                if fn in self._subs:
                    self._subs.remove(fn)

        return _unsub

    def has_subscribers(self) -> bool:
        with self._lock:
            return bool(self._subs)

    def emit(self, kind: str, **payload: Any) -> None:
        with self._lock:
            subs = list(self._subs)
        evt = Event(kind=kind, payload=payload)
        for fn in subs:
            try:
                fn(evt)
            except Exception:
                # A misbehaving renderer must never break the harness.
                pass


_bus = EventBus()


def get_bus() -> EventBus:
    """Return the process-wide event bus."""
    return _bus
