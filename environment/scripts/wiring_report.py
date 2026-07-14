#!/usr/bin/env python3
"""Comprehensive wiring report for every mock-API environment.

For each ``*-api/`` directory it answers three questions:

  1. FILES   - list every file and its kind (data-json / document / postman /
               code / config).
  2. WIRED?  - does the API actually LOAD each JSON data file? This is measured,
               not guessed: we import the data module with ``open`` and the
               store's JSON/CSV readers instrumented, run ``eager_load()``, and
               record exactly which files were read. A data file that is never
               read is an ORPHAN.
  3. ENDPOINTS - cross-references the latest ``api_test_responses.json`` so each
               environment shows how many endpoints the test client reached and
               their PASS/WARN/FAIL/SKIP outcome.

Usage:
  python3 scripts/wiring_report.py                 # full console report
  python3 scripts/wiring_report.py --json out.json # also write machine report
  python3 scripts/wiring_report.py --only stripe-api,github-api
"""

import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYEXE = str(ROOT / ".venv" / "bin" / "python")
if not Path(PYEXE).exists():
    PYEXE = sys.executable

# Code run inside each api dir to record which files the module actually reads.
PROBE = r'''
import builtins, json, sys, glob
from pathlib import Path
_read = set()
_orig_open = builtins.open
def _spy_open(file, *a, **k):
    try:
        p = str(file)
        if p.endswith(".json"):
            _read.add(Path(p).name)
    except Exception:
        pass
    return _orig_open(file, *a, **k)
builtins.open = _spy_open

# wrap the store readers too (tables go through these, not plain open)
import _mutable_store as ms
for fn in ("read_json_with_ctx", "read_csv_with_ctx"):
    if hasattr(ms, fn):
        _o = getattr(ms, fn)
        def _mk(orig):
            def w(path, *a, **k):
                try: _read.add(Path(str(path)).name)
                except Exception: pass
                return orig(path, *a, **k)
            return w
        setattr(ms, fn, _mk(_o))

import importlib
mods = [Path(p).stem for p in glob.glob("*_data.py")]
err = ""
for m in mods:
    try:
        mod = importlib.import_module(m)
        # force any lazy tables/documents to load
        for attr in ("_store",):
            st = getattr(mod, attr, None)
            if st is not None and hasattr(st, "eager_load"):
                st.eager_load()
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
builtins.open = _orig_open
print(json.dumps({"read": sorted(_read), "error": err}))
'''


def probe_dir(api_dir: Path):
    """Return dict {read:[names], error:str} of files the module actually loads."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    try:
        out = subprocess.run([PYEXE, "-c", PROBE], cwd=str(api_dir), env=env,
                             capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return {"read": [], "error": "probe timeout"}
    line = (out.stdout.strip().splitlines() or ["{}"])[-1]
    try:
        return json.loads(line)
    except Exception:
        return {"read": [], "error": f"probe failed: {out.stderr.strip()[-200:]}"}


def kind_of(name: str):
    if name.endswith("postman_collection.json"):
        return "postman"
    if name.endswith(".json"):
        return "data-json"
    if name.endswith(".py"):
        return "code"
    if name in ("Dockerfile", "requirements.txt", "service.toml") or \
       name.endswith((".toml", ".md", ".txt", ".log", ".cfg", ".ini")):
        return "config"
    return "other"


def load_endpoint_results():
    """name -> counts dict, from the latest api_test_responses.json."""
    p = ROOT / "api_test_responses.json"
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    out = {}
    for e in data.get("environments", []):
        out[e["name"]] = {"server": e["server"], "counts": e["counts"],
                          "dir": Path(e["dir"]).name}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only")
    ap.add_argument("--json", dest="json_out")
    args = ap.parse_args()

    api_dirs = sorted(Path(p) for p in glob.glob(str(ROOT / "*-api")) if Path(p).is_dir())
    if args.only:
        want = {s.strip() for s in args.only.split(",") if s.strip()}
        api_dirs = [d for d in api_dirs if d.name in want]

    ep = load_endpoint_results()
    # endpoint results are keyed by service name; map dir-name -> counts
    ep_by_dir = {v["dir"]: v for v in ep.values()}

    report = {}
    tot = {"data": 0, "wired": 0, "orphan": 0, "doc": 0}
    all_orphans = []

    for d in api_dirs:
        probe = probe_dir(d)
        read = set(probe.get("read", []))
        files = []
        for entry in sorted(d.iterdir()):
            if entry.is_dir():
                continue
            name = entry.name
            k = kind_of(name)
            wired = None
            if k == "data-json":
                wired = name in read
                tot["data"] += 1
                tot["wired" if wired else "orphan"] += 1
                if not wired:
                    all_orphans.append(f"{d.name}/{name}")
            files.append({"file": name, "kind": k, "wired": wired})
        report[d.name] = {"files": files, "probe_error": probe.get("error", ""),
                          "endpoints": ep_by_dir.get(d.name, {}).get("counts"),
                          "server": ep_by_dir.get(d.name, {}).get("server")}

    # ---- console ----
    print(f"Wiring report for {len(api_dirs)} environments\n")
    for name in sorted(report):
        r = report[name]
        c = r["endpoints"]
        eps = (f"endpoints: PASS {c['PASS']} WARN {c['WARN']} FAIL {c['FAIL']} SKIP {c['SKIP']}"
               if c else "endpoints: (no test data)")
        srv = r["server"] or "?"
        print(f"### {name}   server={srv}   {eps}")
        if r["probe_error"]:
            print(f"    ⚠ probe error: {r['probe_error']}")
        for f in r["files"]:
            if f["kind"] == "data-json":
                mark = "✅ wired" if f["wired"] else "❌ ORPHAN (not loaded)"
                print(f"    [data] {f['file']:42} {mark}")
            elif f["kind"] == "postman":
                print(f"    [postman] {f['file']}")
        print()

    print("=" * 70)
    print(f"TOTAL data-json files : {tot['data']}")
    print(f"  ✅ wired (loaded)   : {tot['wired']}")
    print(f"  ❌ orphan (not used): {tot['orphan']}")
    if all_orphans:
        print("\nOrphan data files (present on disk, never loaded by the API):")
        for o in all_orphans:
            print(f"  - {o}")

    # global endpoint tally
    if ep:
        g = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
        for v in ep.values():
            for k in g:
                g[k] += v["counts"][k]
        print(f"\nEndpoints (latest run): PASS {g['PASS']} | WARN {g['WARN']} "
              f"| FAIL {g['FAIL']} | SKIP {g['SKIP']}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(
            {"totals": tot, "orphans": all_orphans, "report": report}, indent=2),
            encoding="utf-8")
        print(f"\nJSON report: {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
