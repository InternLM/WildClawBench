"""Pin the ignore_patterns + top-level skip behavior of env_overlay_snapshot.

Background: env_overlay_snapshot.stage_environment_with_overlays() mirrors
environment/<api>/ baseline into output/<backend>/<task>/data/environment/.
This module is the host-side parity partner of script/repackage_to_bundle.py
under the --stage-output-data contract (b53). When the bundler-side
ignore_patterns was extended at script/repackage_to_bundle.py:1864-1881 (b62)
to strip scripts/ + self-improving-agent-* + __pycache__/ + *.pyc, the
output-side mirror was left unfiltered, so output/<task>/data/environment/
leaked those entries. Diagnosed in m1046/m1049 against EC2 task
michael-torres-be963e68 + local darren_weston e2e.

These tests pin that the leak fix at env_overlay_snapshot.py:117-131 (the
_SKIP_TOPLEVEL_NAMES + _SKIP_TOPLEVEL_PREFIXES constants plus the
shutil.ignore_patterns on the per-api copytree) actually fires. Without
them, simplification + Harbor-template porting could silently re-introduce
the leak; the bundler-side guard is not sufficient because the bundler reads
from this output side.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from utils.env_overlay_snapshot import (  # noqa: E402
    _SKIP_TOPLEVEL_NAMES,
    _SKIP_TOPLEVEL_PREFIXES,
    _is_skipped_toplevel,
    stage_environment_with_overlays,
)


def _build_baseline(tmp_path: Path) -> Path:
    baseline = tmp_path / "baseline"
    (baseline / "gmail-api" / "__pycache__").mkdir(parents=True)
    (baseline / "gmail-api" / "server.py").write_text("# server\n")
    (baseline / "gmail-api" / "__pycache__" / "server.cpython-314.pyc").write_bytes(b"\x00")
    (baseline / "__pycache__").mkdir(parents=True)
    (baseline / "__pycache__" / "_mutable_store.cpython-314.pyc").write_bytes(b"\x00")
    (baseline / "scripts").mkdir(parents=True)
    (baseline / "scripts" / "audit_data_formats.py").write_text("# audit\n")
    (baseline / "scripts" / "wiring_report.py").write_text("# wiring\n")
    (baseline / "skills" / "self-improving-agent-3.0.5").mkdir(parents=True)
    (baseline / "skills" / "self-improving-agent-3.0.5" / "SKILL.md").write_text("# RD\n")
    (baseline / "skills" / "self-improving-agent-3.0.5" / "_meta.json").write_text("{}")
    (baseline / "skills" / "gmail-api-connector").mkdir(parents=True)
    (baseline / "skills" / "gmail-api-connector" / "SKILL.md").write_text("# gmail\n")
    return baseline


def test_skip_constants_present_and_typed():
    assert isinstance(_SKIP_TOPLEVEL_NAMES, frozenset)
    assert "scripts" in _SKIP_TOPLEVEL_NAMES
    assert isinstance(_SKIP_TOPLEVEL_PREFIXES, tuple)
    assert any(p.startswith("self-improving-agent") for p in _SKIP_TOPLEVEL_PREFIXES)


def test_is_skipped_toplevel_matches_names_and_prefixes():
    assert _is_skipped_toplevel("scripts")
    assert _is_skipped_toplevel("self-improving-agent-3.0.5")
    assert _is_skipped_toplevel("self-improving-agent-4.0.0")
    assert not _is_skipped_toplevel("gmail-api")
    assert not _is_skipped_toplevel("skills")


def test_stage_strips_toplevel_scripts_dir(tmp_path):
    baseline = _build_baseline(tmp_path)
    dest = tmp_path / "dest"
    stage_environment_with_overlays(baseline, {}, dest, write_manifest=False)
    assert not (dest / "scripts").exists(), "scripts/ leaked into output side"


def test_stage_strips_self_improving_agent_skill(tmp_path):
    baseline = _build_baseline(tmp_path)
    dest = tmp_path / "dest"
    stage_environment_with_overlays(baseline, {}, dest, write_manifest=False)
    assert not (dest / "skills" / "self-improving-agent-3.0.5").exists(), (
        "self-improving-agent-* leaked into output side"
    )
    assert (dest / "skills" / "gmail-api-connector" / "SKILL.md").is_file(), (
        "ignore_patterns over-stripped sibling skills/<api>-connector dir"
    )


def test_stage_strips_pycache_and_pyc(tmp_path):
    baseline = _build_baseline(tmp_path)
    dest = tmp_path / "dest"
    stage_environment_with_overlays(baseline, {}, dest, write_manifest=False)
    assert not list(dest.rglob("__pycache__")), "__pycache__/ leaked"
    assert not list(dest.rglob("*.pyc")), "*.pyc leaked"


def test_stage_strips_toplevel_pycache_even_when_empty(tmp_path):
    baseline = _build_baseline(tmp_path)
    dest = tmp_path / "dest"
    stage_environment_with_overlays(baseline, {}, dest, write_manifest=False)
    assert not (dest / "__pycache__").exists(), (
        "top-level __pycache__/ was created as an empty dir (pre-fix shape: "
        "per-api copytree treated __pycache__ as an api dir, mkdir'd dest "
        "then ignore_patterns stripped contents leaving empty dir)"
    )


def test_stage_preserves_legitimate_api_files(tmp_path):
    baseline = _build_baseline(tmp_path)
    dest = tmp_path / "dest"
    stage_environment_with_overlays(baseline, {}, dest, write_manifest=False)
    assert (dest / "gmail-api" / "server.py").is_file()


def test_stage_skips_overlay_for_skipped_toplevel(tmp_path):
    baseline = _build_baseline(tmp_path)
    overlay_csv = tmp_path / "overlay.csv"
    overlay_csv.write_text("col1,col2\n1,2\n")
    dest = tmp_path / "dest"
    overlays = {
        "scripts": {"audit_data_formats.py": str(overlay_csv)},
        "gmail-api": {"messages.csv": str(overlay_csv)},
    }
    manifest = stage_environment_with_overlays(baseline, overlays, dest, write_manifest=False)
    assert "scripts" not in manifest["apis"]
    assert "gmail-api" in manifest["apis"]
    assert "messages.csv" in manifest["apis"]["gmail-api"]["files"]
    assert not (dest / "scripts").exists()


def test_manifest_does_not_record_skipped_toplevel(tmp_path):
    baseline = _build_baseline(tmp_path)
    dest = tmp_path / "dest"
    manifest = stage_environment_with_overlays(baseline, {}, dest, write_manifest=False)
    assert "scripts" not in manifest["apis"]
