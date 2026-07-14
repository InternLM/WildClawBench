#!/usr/bin/env python3
"""Merge multiple pass_summary.json files into one consolidated summary.

USE CASE
--------
When a task is run in two (or more) separate places, each invocation writes
its own pass_summary.json with run indices starting from 1. Example:

    Place A: 1 rep        -> run_1                            -> pass_summary.json {runs: 1}
    Place B: 7 reps       -> run_1 .. run_7                   -> pass_summary.json {runs: 7}

Both files describe the SAME task, but neither is aware of the other. This
script merges them into a single pass_summary.json that:
  * renumbers run_index so every rep has a unique sequential index
  * deduplicates fully-identical per-run records (re-runs of merge are safe)
  * recomputes ALL aggregates from the merged per_run list (means + pass@K)
  * preserves both legacy and current per-run field shapes (forward-compatible)
  * is BACKWARD-COMPATIBLE with the legacy schema fields
    (average_test_weights_percentage / average_rubric_weights_percentage)

The output is STRICTLY indistinguishable from what `_pass_summary_doc()`
in eval/run_batch.py would have written if all reps had been done in one
place (legacy harness shape: model, runs, average_test_weights_percentage,
average_rubric_weights_percentage, per_run with run_index +
include_multimodal + test_weights_percentage + rubric_weights_percentage).
This makes merged files first-class pass_summary.json artifacts -- they
can be delivered as if produced by a single batch run.

Pass --extended to additionally emit pass@K stats (max-per-run) and
extra reward averages plus a merged_from audit trail.

USAGE
-----
    python3 script/merge_pass_summaries.py FILE1 FILE2 [FILE3 ...] -o OUT
    python3 script/merge_pass_summaries.py FILE1 FILE2 --in-place    # write to FILE1
    python3 script/merge_pass_summaries.py FILE1 FILE2 -o -          # to stdout

Two or more pass_summary.json files are accepted. If --in-place is used,
the first file is overwritten with the merged result. Otherwise -o
specifies an output path (or `-` for stdout).

CONFLICT POLICY
---------------
  * `model`: all inputs must agree; the script exits non-zero if not.
  * `run_index`: renumbered in the order the inputs are listed on the
    command line. Each input's reps are concatenated in input order, then
    re-indexed 1..N.
  * BY DEFAULT, every rep is treated as DISTINCT (concat semantics):
    1 rep + 7 reps -> 8 reps total. Identical-looking reps from
    genuinely independent runs are KEPT (coincidence != duplication).
  * `--dedup` enables content-based dedup (drops reps whose non-index
    fields are bit-for-bit identical). Use this only when you suspect
    the same pass_summary.json was passed twice by accident.
  * `include_multimodal` is preserved per record.

Stdlib-only; standalone script consistent with the rest of script/.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _f(v: Any) -> float | None:
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if f != f or f in (float("inf"), float("-inf")):
        return None
    return f


def _mean(values: list[float | None]) -> float | None:
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    return sum(clean) / len(clean)


def _pmax(values: list[float | None]) -> float | None:
    """pass@K = max of finite values; None when no finite value."""
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    return max(clean)


def _round_or_none(v: float | None, ndigits: int = 2) -> float | None:
    return round(v, ndigits) if v is not None else None


def _comparable_per_run(rec: dict) -> tuple:
    """Stable tuple identity for deduping reps across input files.

    Excludes run_index because that's exactly what differs between
    inputs writing the same rep twice (e.g. an accidental re-merge).
    """
    keys = sorted(k for k in rec.keys() if k != "run_index")
    return tuple((k, json.dumps(rec[k], sort_keys=True, default=str)) for k in keys)


def _load(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as exc:
        sys.stderr.write(f"error: cannot read {path}: {exc}\n")
        sys.exit(2)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"error: {path} is not valid JSON: {exc}\n")
        sys.exit(2)
    if not isinstance(data, dict):
        sys.stderr.write(f"error: {path} top-level is not a JSON object\n")
        sys.exit(2)
    if not isinstance(data.get("per_run"), list):
        sys.stderr.write(f"error: {path} missing list field 'per_run'\n")
        sys.exit(2)
    return data


LEGACY_TOP_KEYS = (
    "model",
    "runs",
    "average_test_weights_percentage",
    "average_rubric_weights_percentage",
    "per_run",
)
LEGACY_PER_RUN_KEYS = (
    "run_index",
    "include_multimodal",
    "test_weights_percentage",
    "rubric_weights_percentage",
)


def merge_pass_summaries(
    inputs: list[Path],
    dedup: bool = False,
    extended: bool = False,
) -> dict:
    """Merge two or more pass_summary.json dicts into one canonical doc.

    Returns the merged document. Does not write to disk.
    When dedup=False (default), every input rep is kept as a distinct rep
    (1+7 -> 8). When dedup=True, reps whose non-index fields are identical
    are kept ONCE (useful when the same file was passed twice by accident).

    Default output conforms STRICTLY to the legacy harness emission shape
    written by eval/run_batch.py::_pass_summary_doc() under the legacy
    schema -- the same 5 top-level keys and 4 per-run keys produced when
    the run was a single batch. Indistinguishable from a first-class
    pass_summary.json from the harness. Pass extended=True to additionally
    emit the rich schema (average_reward, average_combined_reward,
    average_rubric_reward, average_test_reward, pass_at_k_* fields,
    merged_from audit trail).
    """
    if len(inputs) < 2:
        sys.stderr.write("error: need at least 2 input files to merge\n")
        sys.exit(2)
    docs = [_load(p) for p in inputs]

    models = {d.get("model") for d in docs}
    models.discard(None)
    if len(models) > 1:
        sys.stderr.write(
            "error: refusing to merge across different models: "
            f"{sorted(str(m) for m in models)}\n"
        )
        sys.exit(2)
    model = next(iter(models), None) or "unknown"

    seen: set[tuple] = set()
    merged_runs: list[dict] = []
    for doc, src in zip(docs, inputs):
        for rec in doc.get("per_run", []):
            if not isinstance(rec, dict):
                sys.stderr.write(
                    f"warn: {src} has a non-object per_run entry; skipping\n"
                )
                continue
            if dedup:
                key = _comparable_per_run(rec)
                if key in seen:
                    continue
                seen.add(key)
            merged_runs.append(dict(rec))

    for new_index, rec in enumerate(merged_runs, start=1):
        rec["run_index"] = new_index

    def col(field: str) -> list[float | None]:
        return [_f(rec.get(field)) for rec in merged_runs]

    avg_rubric_pct = _mean(col("rubric_weights_percentage"))
    avg_test_pct = _mean(col("test_weights_percentage"))

    if not extended:
        legacy_per_run: list[dict] = []
        for rec in merged_runs:
            out: dict = {
                "run_index": rec.get("run_index"),
                "include_multimodal": bool(rec.get("include_multimodal", True)),
                "test_weights_percentage": rec.get("test_weights_percentage"),
                "rubric_weights_percentage": rec.get("rubric_weights_percentage"),
            }
            legacy_per_run.append(out)
        return {
            "model": model,
            "runs": len(legacy_per_run),
            "average_test_weights_percentage": _round_or_none(avg_test_pct),
            "average_rubric_weights_percentage": _round_or_none(avg_rubric_pct),
            "per_run": legacy_per_run,
        }

    avg_reward = _mean(col("reward")) or 0.0
    avg_combined = _mean(col("combined_reward"))
    avg_rubric = _mean(col("rubric_reward"))
    avg_test = _mean(col("test_reward"))
    pass_at_k_rubric_pct = _pmax(col("rubric_weights_percentage"))
    pass_at_k_test_pct = _pmax(col("test_weights_percentage"))
    pass_at_k_reward = _pmax(col("reward"))
    pass_at_k_combined = _pmax(col("combined_reward"))

    return {
        "model": model,
        "runs": len(merged_runs),
        "average_reward": avg_reward,
        "average_combined_reward": avg_combined,
        "average_rubric_reward": avg_rubric,
        "average_test_reward": avg_test,
        "average_rubric_weights_percentage": _round_or_none(avg_rubric_pct),
        "average_test_weights_percentage": _round_or_none(avg_test_pct),
        "pass_at_k_rubric_weights_percentage": _round_or_none(pass_at_k_rubric_pct),
        "pass_at_k_test_weights_percentage": _round_or_none(pass_at_k_test_pct),
        "pass_at_k_reward": pass_at_k_reward,
        "pass_at_k_combined_reward": pass_at_k_combined,
        "merged_from": [str(p) for p in inputs],
        "per_run": merged_runs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Merge multiple pass_summary.json files into one consolidated summary."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="Two or more pass_summary.json files to merge.",
    )
    out = parser.add_mutually_exclusive_group()
    out.add_argument(
        "-o", "--output",
        type=str,
        help="Output path. Use '-' for stdout. Default: write to stdout.",
    )
    out.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the FIRST input file with the merged result.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent (default: 2)",
    )
    parser.add_argument(
        "--dedup",
        action="store_true",
        help=(
            "Drop per-run records that are bit-for-bit identical (modulo run_index). "
            "Use only when the same file was likely passed twice; default behavior "
            "preserves every rep as a distinct rep (1 + 7 = 8)."
        ),
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help=(
            "Emit the rich (extended) schema with pass@K stats, additional reward "
            "averages, and a merged_from audit trail. Default output is the legacy "
            "harness shape -- indistinguishable from a first-class pass_summary.json "
            "emitted by eval/run_batch.py."
        ),
    )
    args = parser.parse_args()

    if len(args.inputs) < 2:
        parser.error("at least 2 input files are required")

    merged = merge_pass_summaries(args.inputs, dedup=args.dedup, extended=args.extended)
    text = json.dumps(merged, indent=args.indent) + "\n"

    if args.in_place:
        args.inputs[0].write_text(text, encoding="utf-8")
        sys.stderr.write(
            f"merged {len(args.inputs)} file(s) into {args.inputs[0]} "
            f"({merged['runs']} unique rep(s))\n"
        )
        return 0

    out_arg = args.output or "-"
    if out_arg == "-":
        sys.stdout.write(text)
    else:
        Path(out_arg).write_text(text, encoding="utf-8")
        sys.stderr.write(
            f"merged {len(args.inputs)} file(s) into {out_arg} "
            f"({merged['runs']} unique rep(s))\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
