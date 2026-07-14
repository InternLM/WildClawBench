#!/usr/bin/env python3
from __future__ import annotations
import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = REPO_ROOT / "environment"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from migrate_to_drift_plane import data_module_name

ok = fail = 0
failures = []
for api in sorted(ENV_DIR.iterdir()):
    if not api.is_dir() or not api.name.endswith("-api"):
        continue
    dm_name = data_module_name(api.name)
    dm_path = api / f"{dm_name}.py"
    if not dm_path.exists():
        continue
    if "from _mutable_store import get_store" not in dm_path.read_text(
        encoding="utf-8"
    ):
        continue
    prev_path = list(sys.path)
    prev_modules = set(sys.modules.keys())
    try:
        sys.path.insert(0, str(ENV_DIR))
        sys.path.insert(0, str(api))
        for cached in list(sys.modules.keys()):
            if cached in {dm_name, "server", "_mutable_store", "admin_plane",
                          "tracking_middleware"}:
                del sys.modules[cached]
        try:
            mod = importlib.import_module(dm_name)
            tables = mod._store.list_tables()
            docs = mod._store.list_documents()
            for t in tables:
                _ = mod._store.table(t).rows()
            for d in docs:
                _ = mod._store.document(d).get()
            print(f"  OK   {api.name:30s} ({len(tables)}t/{len(docs)}d)")
            ok += 1
        except Exception as exc:
            print(f"  FAIL {api.name:30s} {type(exc).__name__}: {exc}")
            fail += 1
            failures.append((api.name, str(exc)))
    finally:
        sys.path[:] = prev_path
        for k in list(sys.modules.keys()):
            if k not in prev_modules:
                del sys.modules[k]

print(f"\nTotal migrated: {ok + fail}  ok: {ok}  fail: {fail}")
if failures:
    print("\nFailures:")
    for name, msg in failures:
        print(f"  - {name}: {msg}")
    sys.exit(1)
