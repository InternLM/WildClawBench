#!/usr/bin/env python3
"""Flatten a task's persona/home/ tree into a flat data/ folder at the task root.

Walks <task_dir>/persona/home/ recursively, collects every FILE (sub-directories
are traversed but never themselves emitted), and copies each into a freshly
populated <task_dir>/data/ directory WITHOUT any nested structure.

Collision handling is the non-obvious part: flattening a tree can land two files
with the same basename in one folder (e.g. Library/README.md and Public/README.md
both -> README.md). Silently overwriting would lose data, so on a basename clash
the colliding file is renamed using its source-relative path with separators
turned into '__' (Library/README.md -> Library__README.md). The first file to
claim a basename keeps the plain name; only later clashers get the prefixed form.

Standalone: stdlib only, no pipeline imports, no network. Safe to run repeatedly
(default wipes/recreates data/ so output is deterministic; --no-clean appends).
Pass --delete-home to remove persona/home/ after a successful copy.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def _flatten_name(rel_path: Path) -> str:
    return "__".join(rel_path.parts)


def extract(task_dir: Path, *, clean: bool, dry_run: bool, verbose: bool, delete_home: bool) -> int:
    home_dir = task_dir / "persona" / "home"
    if not home_dir.is_dir():
        print(f"ERROR: no persona/home directory under {task_dir}", file=sys.stderr)
        return 2

    data_dir = task_dir / "data"

    # Gather files first so we can resolve collisions deterministically (sorted).
    files = sorted(p for p in home_dir.rglob("*") if p.is_file())
    if not files:
        print(f"ERROR: persona/home contains no files: {home_dir}", file=sys.stderr)
        return 2

    if clean and data_dir.exists() and not dry_run:
        shutil.rmtree(data_dir)
    if not dry_run:
        data_dir.mkdir(parents=True, exist_ok=True)

    used: set[str] = set()
    copied = 0
    renamed = 0
    for src in files:
        rel = src.relative_to(home_dir)
        name = src.name
        if name in used:
            # Basename already taken by an earlier file -> use the flattened path.
            name = _flatten_name(rel)
            renamed += 1
            while name in used:
                name = f"_{name}"
        used.add(name)
        dest = data_dir / name
        if verbose or dry_run:
            tag = "DRY " if dry_run else ""
            print(f"{tag}{rel}  ->  data/{name}")
        if not dry_run:
            shutil.copy2(src, dest)
        copied += 1

    action = "would copy" if dry_run else "copied"
    print(
        f"\n{action} {copied} file(s) from {home_dir} -> {data_dir} "
        f"({renamed} renamed to avoid basename collisions)"
    )

    # Only remove the source tree once files are safely written, never on a dry run.
    if delete_home:
        if dry_run:
            print(f"DRY  would delete {home_dir}")
        else:
            shutil.rmtree(home_dir)
            print(f"deleted {home_dir}")

    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Flatten <task_dir>/persona/home/ files into <task_dir>/data/ (files only).",
    )
    ap.add_argument(
        "task_dir",
        nargs="+",
        help="One or more task directories (each containing persona/home/), e.g. 'input/alden-croft 2'.",
    )
    ap.add_argument(
        "--no-clean",
        dest="clean",
        action="store_false",
        help="Do NOT wipe an existing data/ first; append into it instead (default: wipe & recreate).",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied without writing anything.",
    )
    ap.add_argument("-v", "--verbose", action="store_true", help="List every file copied.")
    ap.add_argument(
        "--delete-home",
        action="store_true",
        help="Delete persona/home/ after a successful extraction (destructive; skipped on --dry-run).",
    )
    args = ap.parse_args(argv)

    # Process each task dir independently; a failure on one does not abort the rest.
    rc = 0
    multi = len(args.task_dir) > 1
    for raw in args.task_dir:
        task_dir = Path(raw).expanduser()
        if multi:
            print(f"\n=== {task_dir} ===")
        if not task_dir.is_dir():
            print(f"ERROR: task dir not found: {task_dir}", file=sys.stderr)
            rc = 2
            continue
        rc = extract(
            task_dir,
            clean=args.clean,
            dry_run=args.dry_run,
            verbose=args.verbose,
            delete_home=args.delete_home,
        ) or rc
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
