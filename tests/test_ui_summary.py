"""Unit tests for the harness UI layer (src/utils/ui).

Pure, docker-free tests for the pieces that carry logic: pass/fail
classification, aggregate stats, tee-safety of the shared console, and the
event-bus no-op contract. Rendering (Rich tables/panels, Textual) is smoke-tested
for "does not raise", since its output is cosmetic.

    pytest tests/test_ui_summary.py -v
"""

import io
import logging
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils.ui import console, events, lifecycle, summary  # noqa: E402


def _r(task_id, score=None, error=None, out_tok=0, cost=0.0):
    scores = {}
    if score is not None:
        scores["overall_score"] = score
    if error and "grading" in error:
        scores["error"] = error
    rec = {"task_id": task_id, "scores": scores, "usage": {"output_tokens": out_tok, "cost_usd": cost}}
    if error and "grading" not in error:
        rec["error"] = error
    return rec


# --- classification ----------------------------------------------------------

def test_classify_pass_and_fail_by_threshold():
    ok, score, reason = summary.classify(_r("a", 0.83), threshold=0.5)
    assert ok is True and score == pytest.approx(0.83) and reason == ""

    ok, score, reason = summary.classify(_r("b", 0.20), threshold=0.5)
    assert ok is False and score == pytest.approx(0.20) and "0.50" in reason


def test_classify_agent_error_is_fail():
    ok, score, reason = summary.classify(_r("c", error="container startup failed"))
    assert ok is False and "agent error" in reason


def test_classify_grading_error_is_fail():
    ok, _, reason = summary.classify(_r("d", error="grading boom"))
    assert ok is False and "grading error" in reason


def test_classify_no_scores_is_fail():
    ok, score, reason = summary.classify({"task_id": "e", "scores": {}})
    assert ok is False and score is None and reason == "no scores"


def test_classify_threshold_from_env(monkeypatch):
    monkeypatch.setenv("WCB_PASS_THRESHOLD", "0.9")
    ok, _, _ = summary.classify(_r("f", 0.83))  # threshold now 0.9
    assert ok is False
    monkeypatch.setenv("WCB_PASS_THRESHOLD", "0.1")
    ok, _, _ = summary.classify(_r("g", 0.2))
    assert ok is True


def test_final_score_uses_overall_not_mean_of_counts():
    # Regression: the final score must be overall_score, NOT a blind mean of all
    # numeric values. A real judge scores dict carries counts and a scaled
    # duplicate alongside overall_score; averaging them would give ~11.9 here.
    rec = {"task_id": "h", "scores": {
        "overall_score": 0.6,
        "rubric_weights_percentage": 60.0,
        "criteria_total": 5,
        "criteria_passed": 3,
        "criteria_failed": 2,
    }}
    ok, score, _ = summary.classify(rec, threshold=0.5)
    assert score == pytest.approx(0.6) and ok is True


def test_classify_no_overall_score_is_no_scores():
    # When overall_score is absent (never happens in production, but is possible
    # for malformed input) we must degrade to "no scores" rather than fabricate a
    # mean of unrelated numeric keys.
    rec = {"task_id": "h", "scores": {"criteria_passed": 3, "criteria_total": 5}}
    ok, score, reason = summary.classify(rec, threshold=0.4)
    assert ok is False and score is None and reason == "no scores"


# --- aggregate stats ---------------------------------------------------------

def test_compute_stats_counts_and_rates():
    results = [_r("a", 0.9), _r("b", 0.1), _r("c", error="boom"), _r("d", 0.6)]
    stats = summary.compute_stats(results, threshold=0.5)
    assert stats["total"] == 4
    assert stats["passed"] == 2  # a, d
    assert stats["failed"] == 2  # b, c
    assert stats["pass_rate"] == pytest.approx(50.0)
    assert stats["fail_rate"] == pytest.approx(50.0)


def test_compute_stats_empty():
    stats = summary.compute_stats([], threshold=0.5)
    assert stats == {"total": 0, "passed": 0, "failed": 0,
                     "pass_rate": 0.0, "fail_rate": 0.0, "threshold": 0.5}


# --- render smoke ------------------------------------------------------------

def test_render_execution_summary_returns_stats():
    results = [_r("a", 0.9, out_tok=100, cost=0.01), _r("b", error="x")]
    buf = io.StringIO()
    from rich.console import Console
    stats = summary.render_execution_summary(results, 12.3, console=Console(file=buf, width=100))
    assert stats["total"] == 2 and stats["passed"] == 1 and stats["failed"] == 1
    out = buf.getvalue()
    assert "Execution Summary" in out and "Task Results" in out


# --- console tee-safety ------------------------------------------------------

def test_console_is_ansi_free_on_non_tty():
    # A StringIO sink is non-tty; Rich must emit no ANSI escape codes so that
    # run.sh's `tee` writes clean, greppable logs.
    from rich.console import Console
    buf = io.StringIO()
    c = Console(file=buf, width=80)  # not a tty
    summary.render_execution_summary([_r("a", 0.9)], 1.0, console=c)
    assert "\x1b[" not in buf.getvalue()


# --- event bus ---------------------------------------------------------------

def test_event_bus_emit_is_noop_without_subscribers():
    bus = events.EventBus()
    assert bus.has_subscribers() is False
    bus.emit(events.EV_STAGE, task_id="x", stage="CREATE")  # must not raise


def test_event_bus_delivers_and_unsubscribes():
    bus = events.EventBus()
    seen = []
    unsub = bus.subscribe(lambda e: seen.append(e))
    bus.emit(events.EV_LOG, message="hello")
    assert len(seen) == 1 and seen[0].payload["message"] == "hello"
    unsub()
    bus.emit(events.EV_LOG, message="bye")
    assert len(seen) == 1  # no delivery after unsubscribe


def test_event_bus_subscriber_exception_is_isolated():
    bus = events.EventBus()

    def boom(_e):
        raise RuntimeError("subscriber blew up")

    bus.subscribe(boom)
    # Emit must swallow subscriber errors so the harness never crashes.
    bus.emit(events.EV_STAGE, task_id="x", stage="FAIL")


# --- lifecycle ---------------------------------------------------------------

def test_emit_stage_publishes_event():
    bus = events.get_bus()
    seen = []
    unsub = bus.subscribe(lambda e: seen.append(e))
    try:
        lifecycle.emit_stage("task-1", lifecycle.STAGE_CREATE, "img:v1")
    finally:
        unsub()
    stage_events = [e for e in seen if e.kind == events.EV_STAGE]
    assert stage_events and stage_events[-1].payload["task_id"] == "task-1"
    assert stage_events[-1].payload["stage"] == "CREATE"


def test_install_rich_logging_idempotent():
    # Should not raise and should be safe to call twice.
    assert console.install_rich_logging(logging.INFO) in (True, False)
    assert console.install_rich_logging(logging.INFO) in (True, False)


# --- TUI exit-code propagation (regression for the swallowed-SystemExit bug) --
#
# The harness signals task failure with sys.exit(1). Under --tui that runs on a
# Textual worker thread, where a SystemExit is swallowed and the process would
# otherwise exit 0. These tests pin the fix: the worker captures the exit intent
# and run_with_dashboard re-raises it on the main thread.

from src.utils.ui import tui  # noqa: E402

textual_only = pytest.mark.skipif(
    not tui.textual_available(), reason="textual not installed"
)


def _drive_worker(work):
    """Mount the real dashboard headlessly, run ``work`` on the real worker
    thread, and return the captured ``app._exit_code``."""
    import asyncio

    async def go():
        app = tui.HarnessDashboard(work=work, total_hint=1)
        async with app.run_test() as pilot:
            # Wait for the worker thread ("harness-work") to finish so
            # _run_work has recorded the exit intent.
            for _ in range(200):
                await pilot.pause()
                if not any(w.name == "harness-work" and w.is_running
                           for w in app.workers):
                    break
            app.exit()
        return app._exit_code

    return asyncio.run(go())


@textual_only
def test_worker_captures_sys_exit_failure():
    # sys.exit(1) on the worker thread must be captured as exit code 1.
    assert _drive_worker(lambda: sys.exit(1)) == 1


@textual_only
def test_worker_captures_clean_completion():
    # A work function that returns normally captures success (0).
    assert _drive_worker(lambda: None) == 0


@textual_only
def test_worker_captures_unhandled_exception_as_failure():
    # An unhandled exception is a failure too (mirrors the main-thread path).
    def boom():
        raise ValueError("kaboom")
    assert _drive_worker(boom) == 1


@textual_only
def test_run_with_dashboard_reraises_failure_on_main_thread(monkeypatch):
    # run_with_dashboard must sys.exit(code) after the UI closes on failure.
    def fake_run(self):
        self._exit_code = 1  # as if a failed worker finished
    monkeypatch.setattr(tui.HarnessDashboard, "run", fake_run)
    with pytest.raises(SystemExit) as ei:
        tui.run_with_dashboard(lambda: None)
    assert ei.value.code == 1


@textual_only
def test_run_with_dashboard_success_returns_true(monkeypatch):
    # On success it does NOT exit and returns True (so main() finishes cleanly).
    def fake_run(self):
        self._exit_code = 0
    monkeypatch.setattr(tui.HarnessDashboard, "run", fake_run)
    assert tui.run_with_dashboard(lambda: None) is True


def test_run_with_dashboard_returns_false_without_textual(monkeypatch):
    # Unavailable-textual contract is unchanged: return False so the caller
    # falls back to the plain Rich logging path.
    monkeypatch.setattr(tui, "_TEXTUAL_AVAILABLE", False)
    assert tui.run_with_dashboard(lambda: None) is False


# --- install_rich_logging: don't clobber unrelated handlers / lower levels -----
#
# Regression for the "replaces ALL root handlers + forces INFO" side effect.

@pytest.fixture
def _isolated_root_logger():
    """Snapshot/restore the root logger + install flag so these tests don't leak
    global logging state into the rest of the suite."""
    root = logging.getLogger()
    saved_handlers = list(root.handlers)
    saved_level = root.level
    saved_flag = console._logging_installed
    try:
        yield root
    finally:
        for h in list(root.handlers):
            root.removeHandler(h)
        for h in saved_handlers:
            root.addHandler(h)
        root.setLevel(saved_level)
        console._logging_installed = saved_flag


def _reset_root(root, handlers, level):
    for h in list(root.handlers):
        root.removeHandler(h)
    for h in handlers:
        root.addHandler(h)
    root.setLevel(level)
    console._logging_installed = False


def test_install_rich_logging_preserves_file_handler(tmp_path, _isolated_root_logger):
    root = _isolated_root_logger
    fh = logging.FileHandler(tmp_path / "run.log")
    stderr_h = logging.StreamHandler(sys.stderr)
    _reset_root(root, [stderr_h, fh], logging.INFO)
    try:
        console.install_rich_logging(logging.INFO)
        # FileHandler survives; the stdout/stderr handler is removed (no dupes).
        assert any(isinstance(h, logging.FileHandler) for h in root.handlers)
        assert stderr_h not in root.handlers
    finally:
        fh.close()


def test_install_rich_logging_does_not_raise_lower_level(_isolated_root_logger):
    root = _isolated_root_logger
    _reset_root(root, [logging.StreamHandler(sys.stderr)], logging.DEBUG)
    console.install_rich_logging(logging.INFO)
    # An intentionally-verbose DEBUG level must not be silently raised to INFO.
    assert root.level == logging.DEBUG


def test_install_rich_logging_default_setup_unchanged(_isolated_root_logger):
    # The current harness setup (basicConfig INFO + a stderr handler) must end up
    # with exactly the RichHandler at INFO, same as before the fix.
    root = _isolated_root_logger
    _reset_root(root, [logging.StreamHandler(sys.stderr)], logging.INFO)
    console.install_rich_logging(logging.INFO)
    assert [type(h).__name__ for h in root.handlers] == ["RichHandler"]
    assert root.level == logging.INFO


# --- print_summary/global keep a greppable log anchor under quiet -------------
#
# Regression for the log-scraper break: quiet mode suppresses the ASCII report
# but must still leave the "Summary Report — <category>" anchor in the log, and
# must still write the summary JSON.

def test_quiet_summary_keeps_greppable_anchor_and_writes_json(tmp_path):
    from src.utils import grading

    buf = io.StringIO()
    h = logging.StreamHandler(buf)
    h.setLevel(logging.INFO)
    grading.logger.addHandler(h)
    saved_level = grading.logger.level
    grading.logger.setLevel(logging.INFO)
    try:
        results = [{"task_id": "t1", "scores": {"overall_score": 0.6},
                    "usage": {"output_tokens": 10, "cost_usd": 0.01}}]
        grading.print_summary(results, "alden-croft_MB", tmp_path,
                              "claude-opus-4.7", quiet=True)
        grading.print_global_summary(results, tmp_path, "claude-opus-4.7", quiet=True)
    finally:
        grading.logger.removeHandler(h)
        grading.logger.setLevel(saved_level)

    out = buf.getvalue()
    assert "Summary Report — alden-croft_MB" in out
    assert "Global Summary Report — ALL CATEGORIES" in out
    # JSON artifacts are still produced (scoring output is untouched).
    assert (tmp_path / "summary_all_claude-opus-4.7.json").exists()
    assert (tmp_path / "alden-croft_MB" / "summary_claude-opus-4.7.json").exists()


# --- criteria table: abstention renders as HUMAN, matching grading.py schema ---

def _render(renderable, width=100):
    from rich.console import Console
    buf = io.StringIO()
    Console(file=buf, width=width).print(renderable)
    return buf.getvalue()


def test_criteria_table_marks_real_abstention_as_human():
    # grading.py records an abstention as resolved_by="human_eval",
    # human_eval="required" (NOT the literal "abstain"). The table must show it
    # as HUMAN, not FAIL.
    criteria = [
        {"id": 0, "weight": 3, "is_positive": True, "passed": True,
         "resolved_by": "unanimous", "human_eval": "", "criterion": "ok"},
        {"id": 1, "weight": 5, "is_positive": True, "passed": False,
         "resolved_by": "human_eval", "human_eval": "required",
         "criterion": "needs a human"},
    ]
    out = _render(summary.build_criteria_table({"criteria": criteria}))
    assert "HUMAN" in out


def test_criteria_abstention_detection_matches_grading_schema():
    # Behaviour parity check on the three real resolved_by values: only the
    # human_eval one is treated as an abstention.
    def render_has_human(resolved_by, human_eval):
        c = [{"id": 0, "weight": 1, "is_positive": True, "passed": False,
              "resolved_by": resolved_by, "human_eval": human_eval,
              "criterion": "c"}]
        return "HUMAN" in _render(summary.build_criteria_table({"criteria": c}))
    assert render_has_human("human_eval", "required") is True
    assert render_has_human("unanimous", "") is False
    assert render_has_human("sonnet", "") is False


# --- summary labels flag PASS/FAIL as a UI threshold, not a harness verdict ----

def test_summary_clarifies_pass_is_a_ui_threshold():
    results = [{"task_id": "t1", "scores": {"overall_score": 0.8},
                "usage": {"output_tokens": 10, "cost_usd": 0.01}}]
    from rich.console import Console
    buf = io.StringIO()
    stats = summary.render_execution_summary(
        results, 1.0, console=Console(file=buf, width=110))
    out = buf.getvalue()
    # The clarifier is present so readers don't mistake it for a harness score.
    assert "UI threshold" in out and "not a harness verdict" in out
    # ...and the stats data/keys are unchanged (no scoring or key drift).
    assert set(stats) == {"total", "passed", "failed",
                          "pass_rate", "fail_rate", "threshold"}
