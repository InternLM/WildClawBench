#!/usr/bin/env python3
"""Backfill already-emitted run output with two fixes that the harness now does
natively (see eval/run_batch.py + scripts/repackage_to_bundle.py):

  FIX A (report.json rubric meta)
    rubric[].type and rubric[].evaluation_target (and importance) were emitted
    as "" because they live in the authoring rubric.json, not in score.json.
    This re-reads each task's rubric.json and merges those fields into every
    report.json rubric item, matched by R-number (falling back to criterion
    text).

  FIX B (score.json deterministic test counts)
    score.json.tests_total / tests_passed / tests_failed were written as a copy
    of the rubric criteria_* counts. The REAL deterministic counts live in the
    run's ctrf.json (task_output/logs/verifier/ctrf.json). This overwrites the
    tests_* fields with those real counts.

Both fixes are idempotent. Run with --dry-run first to preview.

USAGE
    python3 script/backfill_bundle_meta.py output_bundle output/openclaw
    python3 script/backfill_bundle_meta.py --dry-run output_bundle
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def _load(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _dump(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _norm(s: Any) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def _find_rubric_json(report_path: Path) -> Path | None:
    """Walk up from a report.json to the nearest ancestor holding rubric.json
    (the task dir: <root>/<task>/rubric.json)."""
    for ancestor in report_path.parents:
        cand = ancestor / "rubric.json"
        if cand.is_file():
            return cand
    return None


def _index_rubric(rubric: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    idx: dict[str, dict[str, Any]] = {}
    for r in rubric:
        if not isinstance(r, dict):
            continue
        num = str(r.get("number") or "").strip()
        if num:
            idx[f"num:{num}"] = r
        crit = _norm(r.get("criterion"))
        if crit:
            idx[f"crit:{crit}"] = r
    return idx


def fix_report(report_path: Path, dry_run: bool) -> tuple[int, int, str]:
    """Returns (items_updated, items_total, note)."""
    rep = _load(report_path)
    if not isinstance(rep, dict) or not isinstance(rep.get("rubric"), list):
        return (0, 0, "no rubric block")
    rubric_json_path = _find_rubric_json(report_path)
    if rubric_json_path is None:
        return (0, len(rep["rubric"]), "no rubric.json ancestor")
    src = _load(rubric_json_path)
    if not isinstance(src, list):
        return (0, len(rep["rubric"]), "rubric.json not a list")
    idx = _index_rubric(src)

    updated = 0
    for item in rep["rubric"]:
        if not isinstance(item, dict):
            continue
        num = str(item.get("number") or "").strip()
        s = idx.get(f"num:{num}") or idx.get(f"crit:{_norm(item.get('criterion'))}")
        if not s:
            continue
        new_type = str(s.get("type") or "")
        new_target = str(s.get("evaluation_target") or "")
        new_imp = str(s.get("importance") or item.get("importance") or "")
        changed = (
            item.get("type") != new_type
            or item.get("evaluation_target") != new_target
            or item.get("importance") != new_imp
        )
        if changed:
            item["type"] = new_type
            item["evaluation_target"] = new_target
            if new_imp:
                item["importance"] = new_imp
            updated += 1

    if updated and not dry_run:
        _dump(report_path, rep)
    return (updated, len(rep["rubric"]), f"src={rubric_json_path.name}")


def fix_score(score_path: Path, dry_run: bool) -> tuple[bool, str]:
    """Returns (changed, note)."""
    score = _load(score_path)
    if not isinstance(score, dict):
        return (False, "unreadable")
    ctrf_path = score_path.parent / "task_output" / "logs" / "verifier" / "ctrf.json"
    if not ctrf_path.is_file():
        return (False, "no ctrf.json (no deterministic suite ran)")
    ctrf = _load(ctrf_path)
    summary = (ctrf or {}).get("results", {}).get("summary", {}) if isinstance(ctrf, dict) else {}
    if not summary:
        return (False, "empty ctrf summary")
    new_total = int(summary.get("tests", 0) or 0)
    new_passed = int(summary.get("passed", 0) or 0)
    new_failed = int(summary.get("failed", 0) or 0)
    changed = (
        score.get("tests_total") != new_total
        or score.get("tests_passed") != new_passed
        or score.get("tests_failed") != new_failed
    )
    if changed:
        score["tests_total"] = new_total
        score["tests_passed"] = new_passed
        score["tests_failed"] = new_failed
        if not dry_run:
            _dump(score_path, score)
    return (changed, f"{new_passed}/{new_total} passed, {new_failed} failed")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="+", help="One or more roots to walk (e.g. output_bundle output/openclaw)")
    ap.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = ap.parse_args(argv)

    reports_changed = score_changed = 0
    reports_seen = scores_seen = 0

    for root in args.roots:
        root_path = Path(root)
        if not root_path.exists():
            print(f"!! skip (missing): {root}", file=sys.stderr)
            continue

        for report_path in sorted(root_path.rglob("report.json")):
            reports_seen += 1
            n, total, note = fix_report(report_path, args.dry_run)
            if n:
                reports_changed += 1
                print(f"[report] {n:>2}/{total} meta filled  {report_path}  ({note})")

        for score_path in sorted(root_path.rglob("score.json")):
            scores_seen += 1
            changed, note = fix_score(score_path, args.dry_run)
            if changed:
                score_changed += 1
                print(f"[score ] tests_* -> {note}  {score_path}")

    verb = "would update" if args.dry_run else "updated"
    print("-" * 70)
    print(f"report.json: {verb} {reports_changed}/{reports_seen}")
    print(f"score.json : {verb} {score_changed}/{scores_seen}")
    if args.dry_run:
        print("(dry-run — no files written; re-run without --dry-run to apply)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
