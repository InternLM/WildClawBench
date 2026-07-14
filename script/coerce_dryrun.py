#!/usr/bin/env python3
"""Replicate per-task overlay CSV ingestion WITHOUT containers.

For each task under input/ (or one named task), copy environment/ to a temp
tree, lay the task's mock_data/<api>/*.csv files over it exactly as the
read-only bind mount would at runtime, then import each overlaid <api>_data.py
so its _store.eager_load() runs the same coercion the live mock performs.
A CoerceError (or any import failure) is reported per api; clean tasks pass.
Exit code is non-zero if any overlay would fail to load.
"""

from __future__ import annotations

import argparse
import importlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = REPO_ROOT / "environment"
INPUT_DIR = REPO_ROOT / "input"

_INFRA = ("_mutable_store.py", "admin_plane.py", "tracking_middleware.py")


def _tracked_task_dirs() -> list[Path]:
    """Git-tracked task dirs only (skips untracked scratch); dir-scan fallback if no git."""
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files", "input/"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return sorted(p for p in INPUT_DIR.iterdir()
                      if p.is_dir() and (p / "mock_data").is_dir())
    names = sorted({line.split("/", 2)[1] for line in out.splitlines()
                    if line.startswith("input/") and len(line.split("/")) > 2})
    return [INPUT_DIR / n for n in names if (INPUT_DIR / n / "mock_data").is_dir()]


def _overlaid_apis(task_dir: Path) -> list[Path]:
    mock_data = task_dir / "mock_data"
    if not mock_data.is_dir():
        return []
    return sorted(p for p in mock_data.iterdir() if p.is_dir())


def _check_api(api_name: str, overlay_dir: Path) -> tuple[bool, str]:
    src_api = ENV_DIR / api_name
    if not src_api.is_dir():
        return False, f"no such baseline api dir: environment/{api_name}"

    tmp = Path(tempfile.mkdtemp(prefix=f"coerce-{api_name}-"))
    prev_path = list(sys.path)
    prev_modules = set(sys.modules.keys())
    try:
        shutil.copytree(src_api, tmp / api_name)
        for infra in _INFRA:
            shutil.copy(ENV_DIR / infra, tmp)

        for csv_file in sorted(overlay_dir.iterdir()):
            if csv_file.is_file():
                shutil.copy(csv_file, tmp / api_name / csv_file.name)

        data_module = f"{api_name.replace('-', '_')}_data"
        if not (tmp / api_name / f"{data_module}.py").exists():
            cand = sorted((tmp / api_name).glob("*_data.py"))
            if not cand:
                return False, f"no *_data.py in environment/{api_name}"
            data_module = cand[0].stem

        sys.path.insert(0, str(tmp))
        sys.path.insert(0, str(tmp / api_name))
        for cached in list(sys.modules.keys()):
            if cached == data_module or cached in {
                "server", "_mutable_store", "admin_plane", "tracking_middleware",
            }:
                del sys.modules[cached]
        try:
            importlib.import_module(data_module)
        except Exception as exc:
            return False, f"{type(exc).__name__}: {exc}"
        return True, "ok"
    finally:
        sys.path[:] = prev_path
        for k in list(sys.modules.keys()):
            if k not in prev_modules:
                del sys.modules[k]
        shutil.rmtree(tmp, ignore_errors=True)


def _check_task(task_dir: Path) -> list[tuple[str, bool, str]]:
    out = []
    for overlay_dir in _overlaid_apis(task_dir):
        ok, info = _check_api(overlay_dir.name, overlay_dir)
        out.append((overlay_dir.name, ok, info))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("task", nargs="?", help="task name under input/ (default: all)")
    args = ap.parse_args()

    if args.task:
        tasks = [INPUT_DIR / args.task]
    else:
        tasks = _tracked_task_dirs()

    total_fail = 0
    for task_dir in tasks:
        if not task_dir.is_dir():
            print(f"SKIP {task_dir.name}: not a directory")
            continue
        rows = _check_task(task_dir)
        if not rows:
            continue
        print(f"\n{task_dir.name}")
        for api_name, ok, info in rows:
            print(f"  {'OK  ' if ok else 'FAIL'} {api_name:24s} {info}")
            if not ok:
                total_fail += 1

    print(f"\nfailures: {total_fail}")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
