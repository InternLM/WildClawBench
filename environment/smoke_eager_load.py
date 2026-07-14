"""Eager-load smoke test across all 101 mock APIs.

RT-005: closes the static-audit gap that missed runtime defects in
`_store.eager_load()` paths (loader crashes, coerce-time KeyError on missing
seed columns, stale data-module renames).

Usage (from repo root):
    python3.12 WildClawBench/environment/smoke_eager_load.py

Exit code 0 iff every API's `<name>_data` module imports cleanly. Prints
`OK: <api>` per success and `BROKEN: <api>: <exception>` per failure.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


ENVIRONMENT_DIR = Path(__file__).resolve().parent


def _module_name(api_dir: Path) -> str:
    return api_dir.name.replace("-", "_").removesuffix("_api") + "_data"


def main() -> int:
    api_dirs = sorted(p for p in ENVIRONMENT_DIR.glob("*-api") if p.is_dir())
    if not api_dirs:
        print("ERROR: no <name>-api dirs found", file=sys.stderr)
        return 2

    # Shared plane on sys.path so loaders can import _mutable_store.
    sys.path.insert(0, str(ENVIRONMENT_DIR))

    broken: list[tuple[str, str]] = []
    for api in api_dirs:
        mod_name = _module_name(api)
        sys.path.insert(0, str(api))
        try:
            sys.modules.pop(mod_name, None)
            importlib.import_module(mod_name)
            print(f"OK: {api.name}")
        except Exception as e:
            broken.append((api.name, f"{type(e).__name__}: {e}"))
            print(f"BROKEN: {api.name}: {type(e).__name__}: {e}")
        finally:
            sys.path.remove(str(api))

    print()
    print(f"=== Loaded {len(api_dirs) - len(broken)}/{len(api_dirs)} APIs cleanly ===")
    if broken:
        print(f"=== {len(broken)} BROKEN: ===")
        for name, err in broken:
            print(f"  {name}: {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
