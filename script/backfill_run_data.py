#!/usr/bin/env python3
"""Backfill the harbor ``data/`` dir (task.toml + tests + solution + environment)
into ``output/<backend>/<task>/`` run dirs that are missing it.

WHY THIS EXISTS
---------------
Runs produced *before* commit 6e03e6b (2026-06-25 ~23:09 UTC) went through
harbor's in-process ``write_bundle`` and got a fully-populated ``data/`` --
including the mock-API ``environment/`` -- written into the run output dir.
``script/repackage_to_bundle.py`` then copied that ``data/`` verbatim into the
final bundle, so those bundles carry the mock APIs.

Runs produced *after* that commit route straight through
``repackage_to_bundle.py`` and never get a ``data/`` in the run output, so the
final bundle's ``data/environment/`` ends up with only persona + the 3 plane
files -- no mock-API services. (See the BATCH_1 barbara-kidd vs BATCH_7
amanda-hayes comparison.)

This script replays the *old* behavior for those newer runs: for every
``output/<backend>/<task>/`` that lacks ``data/environment/``, it re-derives the
task from its matching ``input/<task>/`` dir and calls the same
``harbor.write_bundle`` the harness used, writing ``data/`` into the run dir
in-place. After running this, re-run ``repackage_to_bundle.py`` (or deliver.sh)
and the resulting bundles will carry the mock APIs.

It is OFFLINE and IDEMPOTENT:
  * No docker / live mock stack needed -- the required/distractor API set is
    resolved from the prompt + ``mock_data/`` overlays via _resolve_task_apis.
  * Existing ``trajectories/`` are left untouched (write_bundle is called with
    no trajectories, so its per-run writer loops over an empty dict).
  * Dirs that already have ``data/environment/`` are skipped unless --force.

USAGE
-----
    # one batch (auto-detects temp/output/<backend> + temp/input under it)
    python3 script/backfill_run_data.py 25-JUNE-2026-Night/BATCH_7/temp

    # several batches at once
    python3 script/backfill_run_data.py 25-JUNE-2026-Night/BATCH_*/temp

    # explicit roots (when layout differs)
    python3 script/backfill_run_data.py \
        --output-root path/to/output/openclaw --input-root path/to/input

    # preview only -- prints what WOULD be backfilled, writes nothing
    python3 script/backfill_run_data.py 25-JUNE-2026-Night/BATCH_7/temp --dry-run

Exit status is non-zero if any task fails so it is safe to gate a pipeline on.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Reuse the SAME persona-core fuzzy matcher the repackager uses so input<->output
# resolution is identical to the rest of the pipeline.
from script.repackage_to_bundle import persona_core  # noqa: E402

from src.utils.config import Config  # noqa: E402
from src.utils.task_parser import load_task  # noqa: E402
from src.utils.store import Store, Task as StoreTask  # noqa: E402
from src.utils.harbor.bundle import write_bundle  # noqa: E402

# _augment_task_with_mocks lives in the orchestrator. Importing run_batch pulls
# in the full harness import graph, which is fine in the harness venv (the same
# venv that runs run_batch). Done lazily so --help works without the heavy deps.
def _load_augmenter():
    from eval.run_batch import _augment_task_with_mocks  # noqa: E402
    return _augment_task_with_mocks


# Backends whose run output lives under output/<backend>/. openclaw is the only
# one used in the 25-JUNE batches; others are listed so a parent output/ dir
# also works.
_BACKENDS = ("openclaw", "claudecode", "codex", "hermesagent")


def _resolve_input_dir(input_root: Path, out_task_dir: Path) -> Path | None:
    """Find the input task dir for an output run dir.

    Output and input dirs share a persona core but carry DIFFERENT uuid
    suffixes (e.g. barbara-kidd-73c78b73-... vs barbara-kidd-1259abc7-...), so
    exact-name matching fails. Match on persona core; when several input
    variants share that core, disambiguate by exact prompt.txt content so we
    pick the variant this run was actually produced from.
    """
    if not input_root.is_dir():
        return None
    want = persona_core(out_task_dir.name)
    if not want:
        return None
    cands = [
        p for p in input_root.iterdir()
        if p.is_dir() and persona_core(p.name) and (
            persona_core(p.name) == want
            or want in persona_core(p.name)
            or persona_core(p.name) in want
        )
    ]
    if not cands:
        return None
    if len(cands) == 1:
        return cands[0]

    out_prompt = out_task_dir / "prompt.txt"
    if out_prompt.is_file():
        otext = out_prompt.read_text(encoding="utf-8", errors="ignore").strip()
        exact = [
            c for c in cands
            if (c / "prompt.txt").is_file()
            and (c / "prompt.txt").read_text(encoding="utf-8", errors="ignore").strip() == otext
        ]
        if len(exact) == 1:
            return exact[0]
        if exact:
            cands = exact
    # Prefer the exact-core match over a substring match, then deterministic.
    cands.sort(key=lambda p: (persona_core(p.name) != want, p.name))
    return cands[0]


def _build_store_task(task: dict) -> StoreTask:
    """Convert a load_task() dict into the StoreTask write_bundle expects.

    Mirrors eval/run_batch.py's StoreTask construction (the old write_bundle
    call site) so the bundle is byte-comparable to the old harness path. The
    required_apis / distractor_apis come from _augment_task_with_mocks, which
    must have run on `task` before this is called.
    """
    return StoreTask(
        id=task["task_id"], task_id=task["task_id"],
        persona=task.get("persona", "") or "",
        initial_prompt=task.get("initial_prompt") or task.get("prompt") or "",
        task_type=task.get("task_type", "") or "",
        difficulty=task.get("difficulty", "") or "",
        l1=task.get("l1", "") or "", l2=task.get("l2", "") or "",
        system_prompt=task.get("system_prompt", "") or "",
        task_description=task.get("task_description", "") or "",
        rubrics_json=json.dumps(task.get("rubrics") or []),
        test_code=task.get("test_code", "") or "",
        test_weights=task.get("test_weights", "") or "",
        golden_trajectory=task.get("golden_trajectory", "") or "",
        extra={
            "required_apis": list(task.get("required_apis") or []),
            "distractor_apis": list(task.get("distractor_apis") or []),
        },
    )


def _iter_output_task_dirs(output_root: Path):
    """Yield <task> dirs under output_root.

    Accepts either an output/<backend> dir directly, or a parent output/ dir
    containing backend subdirs.
    """
    name = output_root.name
    if name in _BACKENDS:
        backends = [output_root]
    else:
        backends = [output_root / b for b in _BACKENDS if (output_root / b).is_dir()]
        if not backends and output_root.is_dir():
            # output_root may itself be a flat dir of task dirs.
            backends = [output_root]
    for backend_dir in backends:
        if not backend_dir.is_dir():
            continue
        for task_dir in sorted(backend_dir.iterdir()):
            if task_dir.is_dir() and (task_dir / "trajectories").is_dir():
                yield task_dir


def _discover_roots(args) -> list[tuple[Path, Path]]:
    """Return [(output_root, input_root), ...] from CLI args."""
    pairs: list[tuple[Path, Path]] = []
    if args.output_root and args.input_root:
        pairs.append((Path(args.output_root), Path(args.input_root)))
    for temp in args.temp_dirs:
        temp = Path(temp)
        out = temp / "output"
        inp = temp / "input"
        if out.is_dir() and inp.is_dir():
            pairs.append((out, inp))
        else:
            print(f"  ! {temp}: missing output/ or input/ (skipping)", file=sys.stderr)
    return pairs


def backfill_one(out_task_dir: Path, input_root: Path, augment, *,
                 force: bool, dry_run: bool, verbose: bool) -> str:
    """Backfill a single run dir. Returns 'skip' | 'done' | 'nomatch' | 'fail'."""
    env_dir = out_task_dir / "data" / "environment"
    if env_dir.is_dir() and any(env_dir.iterdir()) and not force:
        return "skip"

    input_dir = _resolve_input_dir(input_root, out_task_dir)
    if input_dir is None:
        print(f"  ! {out_task_dir.name}: no matching input dir under {input_root}",
              file=sys.stderr)
        return "nomatch"

    if dry_run:
        print(f"  WOULD backfill {out_task_dir.name}  <-  input {input_dir.name}")
        return "done"

    try:
        config = Config.from_env()
        task = load_task(input_dir)
        task.setdefault("task_dir", str(input_dir))
        # Resolve required + distractor APIs offline (prompt + mock_data overlays).
        augment(task, config, None)
        st = _build_store_task(task)
        write_bundle(
            task=st,
            out_dir=out_task_dir,
            store=Store(Path(":memory:")),
            config=config,
            trajectories_by_model=None,  # leave existing trajectories/ untouched
            attachments=task.get("attachments") or [],
            task_dir=input_dir,
        )
        n_api = sum(1 for p in env_dir.iterdir() if p.is_dir() and p.name.endswith("-api")) \
            if env_dir.is_dir() else 0
        req = len(task.get("required_apis") or [])
        dis = len(task.get("distractor_apis") or [])
        if verbose:
            print(f"  + {out_task_dir.name}: data/ written "
                  f"(required={req}, distractor={dis}, env *-api dirs={n_api})  "
                  f"<- input {input_dir.name}")
        return "done"
    except Exception as exc:  # noqa: BLE001 - report and continue
        print(f"  ! {out_task_dir.name}: backfill FAILED: {exc}", file=sys.stderr)
        return "fail"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("temp_dirs", nargs="*",
                    help="One or more 'temp' dirs, each containing output/ and input/.")
    ap.add_argument("--output-root", help="Explicit output/<backend> (or output/) dir.")
    ap.add_argument("--input-root", help="Explicit input/ dir (used with --output-root).")
    ap.add_argument("--force", action="store_true",
                    help="Rebuild data/ even when data/environment/ already exists.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print what would be backfilled; write nothing.")
    ap.add_argument("-q", "--quiet", action="store_true", help="Less per-task output.")
    args = ap.parse_args(argv)

    if (args.output_root and not args.input_root) or (args.input_root and not args.output_root):
        ap.error("--output-root and --input-root must be given together")

    pairs = _discover_roots(args)
    if not pairs:
        ap.error("nothing to do: pass one or more temp dirs, or --output-root/--input-root")

    augment = _load_augmenter() if not args.dry_run else None

    totals = {"skip": 0, "done": 0, "nomatch": 0, "fail": 0}
    for output_root, input_root in pairs:
        print(f"== scanning {output_root}  (inputs: {input_root}) ==")
        for out_task_dir in _iter_output_task_dirs(output_root):
            res = backfill_one(out_task_dir, input_root, augment,
                               force=args.force, dry_run=args.dry_run,
                               verbose=not args.quiet)
            totals[res] += 1

    print(f"\nbackfill summary: backfilled={totals['done']} "
          f"skipped(existing)={totals['skip']} "
          f"no-input-match={totals['nomatch']} failed={totals['fail']}")
    return 1 if totals["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
