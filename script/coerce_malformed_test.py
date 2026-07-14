#!/usr/bin/env python3
"""Assert read_csv_with_ctx + strict_* raise CoerceError on each malformed-CSV class.

Container-free verification that the load-time guards behave as designed:
ragged rows, duplicate headers, and non-UTF-8 bytes raise CoerceError; empty and
header-only files yield an empty table; short rows defer to the per-field helpers
(strict_* raises on the resulting None, opt_* returns its default).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "environment"))

from _mutable_store import (  # noqa: E402
    CoerceError, read_csv_with_ctx, strict_int, opt_int,
)


def _write(tmp: Path, name: str, data: bytes) -> Path:
    p = tmp / name
    p.write_bytes(data)
    return p


def _expect_coerce(label: str, fn) -> bool:
    try:
        fn()
    except CoerceError as e:
        msg = str(e)
        ok = all(tok in msg for tok in ("api=", "table=", "file="))
        print(f"  {'OK  ' if ok else 'FAIL'} {label}: CoerceError ({'has ctx' if ok else 'MISSING ctx: ' + msg})")
        return ok
    except Exception as e:  # noqa: BLE001
        print(f"  FAIL {label}: wrong type {type(e).__name__}: {e}")
        return False
    print(f"  FAIL {label}: no exception raised")
    return False


def _expect_ok(label: str, fn, check) -> bool:
    try:
        result = fn()
    except Exception as e:  # noqa: BLE001
        print(f"  FAIL {label}: unexpected {type(e).__name__}: {e}")
        return False
    ok = check(result)
    print(f"  {'OK  ' if ok else 'FAIL'} {label}: {result!r}")
    return ok


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="coerce-malformed-"))
    api, table = "test-api", "widgets"
    results: list[bool] = []

    good = _write(tmp, "good.csv", b"id,qty\nw1,5\nw2,7\n")
    ragged = _write(tmp, "ragged.csv", b"id,name,qty\nw1,sequin curtain, flower wall,5\n")
    dup = _write(tmp, "dup.csv", b"id,qty,id\nw1,5,w2\n")
    empty = _write(tmp, "empty.csv", b"")
    header_only = _write(tmp, "header_only.csv", b"id,qty\n")
    short = _write(tmp, "short.csv", b"id,qty,note\nw1\n")
    non_utf8 = _write(tmp, "non_utf8.csv", b"id,name\nw1,\xff\xfe bad bytes\n")

    print("read_csv_with_ctx guards:")
    results.append(_expect_ok("good -> rows + ctx",
                              lambda: read_csv_with_ctx(good, api, table),
                              lambda r: len(r) == 2 and r[0]["__api__"] == api
                              and r[0]["__row_index__"] == 0 and r[0]["id"] == "w1"))
    results.append(_expect_coerce("ragged -> raise",
                                  lambda: read_csv_with_ctx(ragged, api, table)))
    results.append(_expect_coerce("duplicate header -> raise",
                                  lambda: read_csv_with_ctx(dup, api, table)))
    results.append(_expect_coerce("non-utf8 -> raise",
                                  lambda: read_csv_with_ctx(non_utf8, api, table)))
    results.append(_expect_ok("empty -> []",
                              lambda: read_csv_with_ctx(empty, api, table),
                              lambda r: r == []))
    results.append(_expect_ok("header-only -> []",
                              lambda: read_csv_with_ctx(header_only, api, table),
                              lambda r: r == []))

    print("short-row asymmetry (defers to per-field helpers):")
    short_rows = read_csv_with_ctx(short, api, table)
    results.append(_expect_coerce("short row + strict_int(missing) -> raise",
                                  lambda: strict_int(short_rows[0], "qty")))
    results.append(_expect_ok("short row + opt_int(missing) -> default",
                              lambda: opt_int(short_rows[0], "qty", default=0),
                              lambda v: v == 0))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} checks passed")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
