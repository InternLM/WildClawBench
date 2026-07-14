#!/usr/bin/env python3
"""Audit the on-disk format of every file in every mock-API environment.

For each ``*-api/`` directory this script classifies every file, then for the
data files it confirms they are valid JSON in the shape the loaders expect:

  * seed table   -> JSON **array of row objects**            (read_json_with_ctx)
  * document     -> JSON object / array / scalar             (register_document)
  * config-json  -> ``*_postman_collection.json``            (test harness input)

Anything that is NOT one of the above is flagged so you can see, per API, where
each file is in JSON format and where it is "some other format for that specific
data" (e.g. a leftover ``.csv``, an invalid JSON blob, or a non-array seed file).

It also checks two repo conventions the migration tool enforces
(``scripts/migrate_csv_to_json.py``):
  * trailing newline on the file
  * seed-table cells are strings (the byte-fidelity contract)

Usage:
  python3 scripts/audit_data_formats.py                 # human-readable report
  python3 scripts/audit_data_formats.py --json out.json # also write a JSON report
  python3 scripts/audit_data_formats.py --only stripe-api,github-api
"""

import argparse
import glob
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Files that are expected and are NOT data (don't flag these as "wrong format").
NON_DATA_EXACT = {"Dockerfile", "requirements.txt", "service.toml", "server.py",
                  "api_test_results.md", ".test_server.log"}
NON_DATA_SUFFIX = {".py", ".pyc", ".toml", ".md", ".txt", ".log", ".cfg", ".ini"}
NON_DATA_DIRS = {"__pycache__"}


def classify_file(path: Path):
    """Return (category, detail). category in:
       data-json-table | data-json-doc | data-json-empty | config-json |
       BAD-JSON | NON-JSON-DATA | config | skip
    """
    name = path.name
    if name in NON_DATA_EXACT or path.suffix in NON_DATA_SUFFIX:
        return ("config", path.suffix or name)

    if path.suffix == ".json":
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except UnicodeDecodeError as e:
            return ("BAD-JSON", f"not utf-8: {e}")
        except json.JSONDecodeError as e:
            return ("BAD-JSON", f"invalid json: {e}")

        if name.endswith("postman_collection.json"):
            return ("config-json", "postman collection")

        trailing_nl = raw.endswith("\n")
        if isinstance(data, list):
            if len(data) == 0:
                return ("data-json-empty", f"empty array, trailing_nl={trailing_nl}")
            if all(isinstance(r, dict) for r in data):
                # byte-fidelity contract: seed cells should be strings
                non_str = _non_string_cells(data)
                detail = f"{len(data)} rows, trailing_nl={trailing_nl}"
                if non_str:
                    detail += f", NON-STRING cells in {sorted(non_str)[:5]}"
                return ("data-json-table", detail)
            return ("data-json-doc", f"array (not all objects), trailing_nl={trailing_nl}")
        return ("data-json-doc", f"{type(data).__name__}, trailing_nl={trailing_nl}")

    # any non-.json, non-config file sitting in an api dir is "other format"
    return ("NON-JSON-DATA", path.suffix or "no-ext")


def _non_string_cells(rows):
    cols = set()
    for r in rows:
        for k, v in r.items():
            if not isinstance(v, str) and v is not None:
                cols.add(k)
    return cols


def audit_dir(api_dir: Path):
    files = []
    for entry in sorted(api_dir.iterdir()):
        if entry.is_dir():
            if entry.name in NON_DATA_DIRS:
                continue
            continue
        cat, detail = classify_file(entry)
        files.append({"file": entry.name, "category": cat, "detail": detail})
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="comma-separated api dir names")
    ap.add_argument("--json", dest="json_out", help="write a machine-readable JSON report here")
    args = ap.parse_args()

    api_dirs = sorted(Path(p) for p in glob.glob(str(ROOT / "*-api")) if Path(p).is_dir())
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        api_dirs = [d for d in api_dirs if d.name in want]

    report = {}
    totals = {}
    problems = []   # real format problems: file is not valid JSON, or not JSON at all
    notes = []      # informational: style/convention only (does not affect format)

    for d in api_dirs:
        files = audit_dir(d)
        report[d.name] = files
        for f in files:
            totals[f["category"]] = totals.get(f["category"], 0) + 1
            if f["category"] in ("BAD-JSON", "NON-JSON-DATA"):
                problems.append((d.name, f["file"], f["category"], f["detail"]))
            elif f["category"] in ("data-json-table", "data-json-doc") and "trailing_nl=False" in f["detail"]:
                notes.append((d.name, f["file"], "no-trailing-newline", f["detail"]))
            elif f["category"] == "data-json-table" and "NON-STRING" in f["detail"]:
                # legitimate for natively-authored nested JSON; only worth noting
                notes.append((d.name, f["file"], "non-string-cells", f["detail"]))

    # ---- console report ----
    print(f"Audited {len(api_dirs)} api environments under {ROOT}\n")
    print("Per-category file counts:")
    for cat in sorted(totals):
        print(f"  {cat:18} {totals[cat]}")
    print()

    if problems:
        print(f"❌ FORMAT PROBLEMS: {len(problems)} file(s) are NOT valid JSON "
              f"or are a non-JSON format:\n")
        for api, fname, kind, detail in problems:
            print(f"  [{kind}] {api}/{fname}  -> {detail}")
    else:
        print("✅ FORMAT: every data file is valid JSON in the expected shape; "
              "no non-JSON data, no invalid JSON.")
    print()

    if notes:
        print(f"ℹ️  {len(notes)} style/convention note(s) (NOT format errors):\n")
        for api, fname, kind, detail in notes:
            print(f"  [{kind}] {api}/{fname}  -> {detail}")
    print()

    # show a compact per-API line so you can eyeball each environment
    print("Per-API breakdown (data files only):")
    for name in sorted(report):
        data_files = [f for f in report[name]
                      if f["category"].startswith("data-json") or
                      f["category"] in ("BAD-JSON", "NON-JSON-DATA")]
        if not data_files:
            continue
        bits = []
        for f in data_files:
            tag = {"data-json-table": "T", "data-json-doc": "D",
                   "data-json-empty": "∅", "BAD-JSON": "BAD!",
                   "NON-JSON-DATA": "OTHER!"}.get(f["category"], "?")
            bits.append(f"{f['file']}[{tag}]")
        print(f"  {name:24} {', '.join(bits)}")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({"totals": totals, "problems": problems,
                        "notes": notes, "report": report},
                       indent=2), encoding="utf-8")
        print(f"\nJSON report written: {args.json_out}")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
