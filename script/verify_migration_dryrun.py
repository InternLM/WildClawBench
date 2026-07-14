#!/usr/bin/env python3
"""Verify the migration script produces importable code without writing.

Picks every non-skipped module, generates the migrated files in a temp dir,
attempts to import both data + server, queries each registered table, and
reports failures.
"""

from __future__ import annotations

import importlib
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = REPO_ROOT / "environment"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from migrate_to_drift_plane import (
    ALREADY_DONE, IDIOSYNCRATIC, apply_data_module, apply_server,
    discover_apis, plan_module,
)


def verify_one(api: Path) -> tuple[bool, str]:
    try:
        mig = plan_module(api)
        if mig.issues:
            return False, f"PLAN: {mig.issues}"
        dm_out = apply_data_module(mig)
        sv_out = apply_server(api, mig.data_module_name)
        if dm_out is None or sv_out is None:
            return False, f"APPLY: dm={dm_out is not None} sv={sv_out is not None}"
    except Exception as exc:
        return False, f"PLAN_EXC: {exc}"

    tmp = Path(tempfile.mkdtemp(prefix=f"mig-{api.name}-"))
    try:
        shutil.copytree(api, tmp / api.name)
        shutil.copy(ENV_DIR / "_mutable_store.py", tmp)
        shutil.copy(ENV_DIR / "admin_plane.py", tmp)
        shutil.copy(ENV_DIR / "tracking_middleware.py", tmp)
        (tmp / api.name / f"{mig.data_module_name}.py").write_text(
            dm_out, encoding="utf-8"
        )
        (tmp / api.name / "server.py").write_text(sv_out, encoding="utf-8")

        prev_path = list(sys.path)
        prev_modules = set(sys.modules.keys())
        try:
            sys.path.insert(0, str(tmp))
            sys.path.insert(0, str(tmp / api.name))
            for cached in list(sys.modules.keys()):
                if cached in {mig.data_module_name, "server", "_mutable_store",
                              "admin_plane", "tracking_middleware"}:
                    del sys.modules[cached]
            try:
                data_mod = importlib.import_module(mig.data_module_name)
            except Exception as exc:
                return False, f"IMPORT_DATA: {exc}"
            tables = data_mod._store.list_tables()
            documents = data_mod._store.list_documents()
            for t in tables:
                try:
                    rows = data_mod._store.table(t).rows()
                except Exception as exc:
                    return False, f"TABLE[{t}]: {exc}"
                assert isinstance(rows, list), f"table {t} returned {type(rows)}"
            for d in documents:
                try:
                    _ = data_mod._store.document(d).get()
                except Exception as exc:
                    return False, f"DOC[{d}]: {exc}"
            try:
                server_mod = importlib.import_module("server")
            except Exception as exc:
                return False, f"IMPORT_SERVER: {exc}"
            assert hasattr(server_mod, "app"), "server.app missing"
            return True, f"ok ({len(tables)}t/{len(documents)}d)"
        finally:
            sys.path[:] = prev_path
            for k in list(sys.modules.keys()):
                if k not in prev_modules:
                    del sys.modules[k]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    skip = ALREADY_DONE | IDIOSYNCRATIC
    apis = [a for a in discover_apis() if a.name not in skip]
    ok = fail = 0
    failures: list[tuple[str, str]] = []
    for api in apis:
        success, info = verify_one(api)
        prefix = "OK  " if success else "FAIL"
        print(f"  {prefix} {api.name:30s} {info}")
        if success:
            ok += 1
        else:
            fail += 1
            failures.append((api.name, info))
    print(f"\nTotal: {len(apis)}  ok: {ok}  fail: {fail}")
    if failures:
        print("\nFailures:")
        for name, info in failures:
            print(f"  - {name}: {info}")
        sys.exit(1)


if __name__ == "__main__":
    main()
