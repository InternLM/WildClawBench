"""Static wiring invariants for the backfill integration in run.sh + deliver.sh.

The backfill scripts themselves (script/backfill_run_data.py,
script/backfill_pass_summary.py, script/backfill_connector_docs.py) are
unit-tested elsewhere (test_scripts_misc_units.py, test_rollup_scripts.py,
test_regrade_and_rerun_units.py). These tests pin the OTHER half: that the
shell pipelines actually invoke them, at the right points, with the right
failure posture:

  run.sh      preflight        -> connector docs generate (before mock image)
  run.sh      bundle_task      -> run-data + pass-summary BEFORE repackage,
                                  bundle enrich AFTER a successful repackage,
                                  all fail-soft (warn, never die/exit)
  run.sh      both aggregates  -> pass-summary repair BEFORE aggregate_runs.py
  deliver.sh  BACKFILL step    -> before CONVERT; run-data + pass-summary are
                                  FATAL (publishing), connector docs warn-only;
                                  staging enrich after convert, before clone

Same posture as tests/test_shared_sidecar_invariants.py: STATIC (no docker,
no network, no subprocess) so they run on any host.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_SH = REPO_ROOT / "script" / "run.sh"
DELIVER_SH = REPO_ROOT / "deliver.sh"
BF_RUN_DATA = REPO_ROOT / "script" / "backfill_run_data.py"
BF_PASS_SUMMARY = REPO_ROOT / "script" / "backfill_pass_summary.py"
BF_CONNECTOR = REPO_ROOT / "script" / "backfill_connector_docs.py"


# ---------- helpers ----------


def _read(path: Path) -> str:
    assert path.is_file(), f"required file missing: {path}"
    return path.read_text(encoding="utf-8")


def _fn_body(src: str, name: str) -> str:
    """Extract a top-level bash function body: `name() {` .. first column-0 `}`."""
    m = re.search(rf"^{re.escape(name)}\(\)\s*\{{\n(.*?)^\}}", src, re.M | re.S)
    assert m, f"function {name}() not found"
    return m.group(1)


def _call_lines(src: str, token: str) -> list[str]:
    """Non-comment, non-definition lines mentioning token."""
    return [
        ln for ln in src.splitlines()
        if token in ln
        and not ln.lstrip().startswith("#")
        and not re.match(rf"^\s*{re.escape(token)}\s*\(\)\s*\{{", ln)
    ]


# ---------- targets exist & flag contracts match ----------


def test_backfill_scripts_exist() -> None:
    """The three wiring targets must exist — a rename would silently turn every
    hook into a warn-and-continue no-op in run.sh."""
    for p in (BF_RUN_DATA, BF_PASS_SUMMARY, BF_CONNECTOR):
        assert p.is_file(), f"wiring target missing: {p}"


def test_shell_flags_exist_in_target_scripts() -> None:
    """Every flag the shell passes must be declared by the target argparse —
    an unknown flag exits 2, which the fail-soft hooks would swallow silently."""
    assert "--output-root" in _read(BF_RUN_DATA)
    assert "--input-root" in _read(BF_RUN_DATA)
    assert "--bundle-root" in _read(BF_CONNECTOR)
    assert "--skills-root" in _read(BF_CONNECTOR)


# ---------- run.sh: preflight connector docs ----------


def test_run_sh_defines_and_invokes_preflight_connector_docs() -> None:
    src = _read(RUN_SH)
    assert re.search(r"^\s*preflight_connector_docs\s*\(\)\s*\{", src, re.M), (
        "script/run.sh must define preflight_connector_docs()"
    )
    assert _call_lines(src, "preflight_connector_docs"), (
        "script/run.sh must INVOKE preflight_connector_docs (not only define it)"
    )


def test_run_sh_connector_docs_runs_before_mock_image_preflight() -> None:
    """Ordering: a first-time docs backfill changes the environment/ content
    hash, so it must land before the mock-image check — a preflight build
    (image absent) then picks up the enriched tree immediately."""
    src = _read(RUN_SH)
    calls = _call_lines(src, "preflight_connector_docs")
    assert calls, "preflight_connector_docs never invoked"
    docs_pos = src.index(calls[0])
    mock_calls = [
        ln for ln in _call_lines(src, "preflight_mock_image") if "exit 1" in ln
    ]
    assert mock_calls, "preflight_mock_image call site not found"
    assert docs_pos < src.index(mock_calls[0]), (
        "preflight_connector_docs must run BEFORE preflight_mock_image"
    )


# ---------- run.sh: bundle_task hooks ----------


def test_bundle_task_backfills_run_data_and_pass_summary_before_repackage() -> None:
    body = _fn_body(_read(RUN_SH), "bundle_task")
    repack = body.index("repackage_to_bundle.py")
    assert "backfill_run_data.py" in body, (
        "bundle_task must invoke backfill_run_data.py (bundles ship without "
        "mock APIs otherwise — post-6e03e6b regression)"
    )
    assert body.index("backfill_run_data.py") < repack, (
        "run-data backfill must run BEFORE repackage_to_bundle.py"
    )
    assert "backfill_pass_summary.py" in body
    assert body.index("backfill_pass_summary.py") < repack, (
        "pass_summary backfill must run BEFORE repackage_to_bundle.py"
    )


def test_bundle_task_enriches_bundle_after_repackage() -> None:
    body = _fn_body(_read(RUN_SH), "bundle_task")
    m = re.search(r"backfill_connector_docs\.py[\s\S]{0,120}?--bundle-root", body)
    assert m, "bundle_task must run the connector enrich pass (--bundle-root)"
    assert m.start() > body.index("repackage_to_bundle.py"), (
        "bundle enrich must run AFTER repackage_to_bundle.py"
    )


def test_bundle_task_backfill_hooks_are_fail_soft() -> None:
    """bundle_task's contract: the eval already succeeded; downstream repair
    must never fail the run. Backfill failures warn, never die/exit."""
    body = _fn_body(_read(RUN_SH), "bundle_task")
    assert "log::die" not in body, "bundle_task must not log::die"
    assert not re.search(r"^\s*exit\b", body, re.M), "bundle_task must not exit"
    for hook in ("backfill_run_data.py", "backfill_pass_summary.py",
                 "backfill_connector_docs.py"):
        # Anchor on the invocation, not the first mention (comments name the
        # scripts too).
        m = re.search(rf"python3 script/{re.escape(hook)}", body)
        assert m, f"bundle_task must invoke {hook}"
        # Each hook's failure branch must surface a warn within its guard.
        assert "log::warn" in body[m.start():m.start() + 400], (
            f"{hook} failure in bundle_task must log::warn (fail-soft)"
        )


# ---------- run.sh: aggregate sites ----------


def test_run_sh_repairs_pass_summaries_before_both_aggregate_sites() -> None:
    """Both rollup call sites (sequential main + parallel launcher) must
    rebuild pass_summary.json first so aggregate reads real tests_* counts."""
    src = _read(RUN_SH)
    # Invocations only — each site also names the script in its failure warn.
    agg_sites = [
        m.start() for m in re.finditer(r"python3 script/aggregate_runs\.py", src)
    ]
    assert len(agg_sites) == 2, (
        f"expected exactly 2 aggregate_runs.py call sites, found {len(agg_sites)}"
    )
    repair_sites = [
        m.start()
        for m in re.finditer(r'backfill_pass_summary\.py "output/\$\{BACKEND\}"', src)
    ]
    assert len(repair_sites) == 2, (
        "expected a pass_summary repair before EACH aggregate site"
    )
    for agg in agg_sites:
        assert any(0 < agg - r < 600 for r in repair_sites), (
            "each aggregate_runs.py call must be immediately preceded by a "
            'backfill_pass_summary.py "output/${BACKEND}" repair'
        )


# ---------- deliver.sh: BACKFILL step ----------


def test_deliver_sh_backfill_step_before_convert() -> None:
    src = _read(DELIVER_SH)
    m_backfill = re.search(r'next_step "Backfill', src)
    m_convert = re.search(r'next_step "Convert', src)
    assert m_backfill, "deliver.sh must have a BACKFILL next_step"
    assert m_convert, "deliver.sh must have a CONVERT next_step"
    assert m_backfill.start() < m_convert.start(), (
        "BACKFILL step must precede CONVERT"
    )


def test_deliver_sh_data_backfills_are_fatal_but_connector_docs_warn() -> None:
    """Delivery publishes: shipping bundles without mock APIs or with stale
    summaries is the original bug, so those two die. Thin connector docs only
    degrade quality, so that one warns."""
    src = _read(DELIVER_SH)
    assert re.search(r"backfill_run_data\.py[\s\S]{0,300}?\|\|\s*log::die", src), (
        "run-data backfill failure must be FATAL in deliver.sh"
    )
    assert re.search(r"backfill_pass_summary\.py[\s\S]{0,300}?\|\|\s*log::die", src), (
        "pass_summary backfill failure must be FATAL in deliver.sh"
    )
    gen = re.search(
        r"backfill_connector_docs\.py\"?\s*>/dev/null[\s\S]{0,120}?\|\|\s*log::warn", src
    )
    assert gen, "connector-docs generation failure must be warn-only in deliver.sh"


def test_deliver_sh_enriches_staging_after_convert_before_clone() -> None:
    src = _read(DELIVER_SH)
    m = re.search(r'--bundle-root "\$STAGING"', src)
    assert m, "deliver.sh must enrich the STAGING bundles (--bundle-root \"$STAGING\")"
    assert m.start() > src.index("repackage_to_bundle.py"), (
        "staging enrich must run AFTER conversion"
    )
    assert m.start() < src.index("git clone"), (
        "staging enrich must run BEFORE the delivery-repo clone (cwd is still "
        "REPO_ROOT there; bundles are copied into the clone afterwards)"
    )


def test_deliver_sh_step_totals_count_backfill() -> None:
    """next_step auto-numbers against TOTAL_STEPS; adding the BACKFILL phase
    means 5 with --run, 4 convert-only."""
    src = _read(DELIVER_SH)
    assert "TOTAL_STEPS=5" in src and "TOTAL_STEPS=4" in src, (
        "TOTAL_STEPS must be 5 (--run) / 4 (convert-only) with the BACKFILL step"
    )
