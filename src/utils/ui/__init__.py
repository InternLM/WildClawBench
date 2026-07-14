"""Kensei harness terminal UI layer (Rich default + opt-in Textual dashboard).

Public surface:
  * ``console`` — shared Rich console + ``install_rich_logging`` + ``is_interactive``
  * ``events``  — process-wide event bus (``get_bus``)
  * ``lifecycle`` — container/task lifecycle stage rendering (``emit_stage``, STAGE_*)
  * ``summary`` — execution summary rendering (``render_execution_summary``, ``compute_stats``)
  * ``tui``    — opt-in Textual dashboard (``run_with_dashboard``, ``textual_available``)

Importing this package is side-effect free and never requires ``textual``.
"""
from __future__ import annotations

from . import console, events, lifecycle, summary, tui  # noqa: F401

__all__ = ["console", "events", "lifecycle", "summary", "tui"]
