#!/usr/bin/env python3
"""One-time, reproducible migration of loaded CSV tables -> JSON.

Each `*_data.py` loads its seed tables through a uniform wrapper
``_load(filename, table) -> read_csv_with_ctx(...)`` and then coerces the
string-valued rows into the served (often nested) shape. This script converts
every *loaded* CSV into a flat **JSON array of row objects**, preserving each
cell exactly as the CSV reader produced it (strings, plus ``null`` only where a
row was genuinely short). Because the coercers receive byte-identical row dicts,
the in-memory store and every API response are unchanged.

It proves the round-trip before deleting anything: it reloads the freshly
written JSON via ``read_json_with_ctx`` and asserts the rows equal the original
CSV rows. The CSV is deleted ONLY when that passes and only under ``--apply``.

  python scripts/migrate_csv_to_json.py            # dry-run: write JSON + verify, keep CSV
  python scripts/migrate_csv_to_json.py --apply    # write JSON + verify, then delete CSV

The convert-list is derived mechanically (not hand-listed):
  * static  : every ``_load("X.csv")`` literal in any `*_data.py` -> that module's dir
  * dynamic : every filename named in a ``records_csv`` column of any CSV (airtable /
              algolia load per-table record files by name from data)
Any `.csv` on disk that is in neither set is reported as an orphan and skipped.
"""

import argparse
import csv as _csv
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import _mutable_store as ms  # noqa: E402

_CTX = {"__api__", "__table__", "__file__", "__row_index__"}
# Any "X.csv" / "X.json" filename literal in a data module -> the stem "X".
# We match both extensions so this is correct whether run before OR after the
# loader-literal rewrite (.csv -> .json). Broader than just _load("...") on
# purpose: some modules name files in a dict/mapping (e.g. salesforce
# {"Account": "accounts.csv"}) and pass the value to _load via a variable.
# A candidate is only acted on if its `<stem>.csv` actually exists on disk, so
# unrelated original document JSONs (e.g. balance.json with no balance.csv) and
# already-converted files are naturally excluded.
_LOAD_LITERAL = re.compile(r'"([^"]+)\.(?:csv|json)"')


def _strip(row):
    return {k: v for k, v in row.items() if k not in _CTX}


def _canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False)


def derive_loaded_set():
    """Return a set of absolute Paths to every loaded CSV (static + dynamic)."""
    candidates = set()  # (dir, stem)

    # static: filename literals in each data module, resolved against its dir
    for data_py in glob.glob(str(ROOT / "*-api" / "*_data.py")):
        d = Path(data_py).parent
        src = Path(data_py).read_text(encoding="utf-8")
        for stem in _LOAD_LITERAL.findall(src):
            candidates.add((d, stem))

    # dynamic: any filename listed in a `records_csv` column of any CSV
    for csv_path in glob.glob(str(ROOT / "*-api" / "*.csv")):
        p = Path(csv_path)
        try:
            with open(p, newline="", encoding="utf-8-sig") as f:
                reader = _csv.DictReader(f)
                if not reader.fieldnames or "records_csv" not in reader.fieldnames:
                    continue
                for r in reader:
                    val = (r.get("records_csv") or "").strip()
                    if val:
                        candidates.add((p.parent, Path(val).stem))
        except (OSError, UnicodeDecodeError, _csv.Error):
            continue

    # a candidate is a real loaded CSV only if <stem>.csv exists on disk
    loaded = set()
    for d, stem in candidates:
        csv_p = (d / f"{stem}.csv").resolve()
        if csv_p.exists():
            loaded.add(csv_p)
    return loaded


def migrate_one(csv_path: Path, apply: bool):
    if not csv_path.exists():
        return ("MISSING", csv_path, "referenced but not on disk")
    json_path = csv_path.with_suffix(".json")
    stem = csv_path.stem

    rows = [_strip(r) for r in ms.read_csv_with_ctx(csv_path, "migrate", stem)]
    json_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    back = [_strip(r) for r in ms.read_json_with_ctx(json_path, "migrate", stem)]
    if back != rows or _canon(back) != _canon(rows):
        json_path.unlink()
        return ("FAIL", csv_path, "round-trip mismatch (JSON not kept)")

    if apply:
        csv_path.unlink()
        return ("OK-APPLIED", csv_path, f"{len(rows)} row(s), csv deleted")
    return ("OK", csv_path, f"{len(rows)} row(s) -> {json_path.name}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="delete each CSV after its JSON round-trip is verified")
    args = ap.parse_args()

    loaded = derive_loaded_set()
    on_disk = {Path(p).resolve() for p in glob.glob(str(ROOT / "*-api" / "*.csv"))}
    orphans = sorted(on_disk - loaded)

    results = [migrate_one(p, args.apply) for p in sorted(loaded)]

    counts = {}
    for status, path, detail in results:
        counts[status] = counts.get(status, 0) + 1
        rel = path.relative_to(ROOT)
        if status not in ("OK", "OK-APPLIED"):
            print(f"  {status:11} {rel}  {detail}")
    print(f"\nconverted: {counts.get('OK',0)+counts.get('OK-APPLIED',0)}  "
          + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"loaded CSVs: {len(loaded)} | on disk: {len(on_disk)} | "
          f"orphans skipped: {len(orphans)}")
    for o in orphans:
        print(f"  ORPHAN (left as .csv): {o.relative_to(ROOT)}")

    failed = [r for r in results if r[0] in ("FAIL", "MISSING")]
    if failed:
        print(f"\n{len(failed)} file(s) did NOT convert; no CSV deleted for those.")
        return 1
    if not args.apply:
        print("\nDRY-RUN: JSON written + verified, CSV kept. Re-run with --apply to delete CSV.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
