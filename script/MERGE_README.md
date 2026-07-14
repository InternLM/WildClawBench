# `merge_pass_summaries.py` — How to Run

Standalone utility for merging two or more `pass_summary.json` files into a single consolidated summary. Useful when reps for the same conceptual task were produced in separate batches (e.g. 1 verification rep + 7 bulk reps) and you need a unified 8-rep view with recomputed aggregates.

---

## Prerequisites

- Python 3.9+ (stdlib only — no installs needed)
- Two or more `pass_summary.json` files you want to merge

---

## Script location

```
script/merge_pass_summaries.py
```

---

## Step-by-step usage

### Step 1 — View help

```bash
cd /Users/apple/Documents/WildClawBench
python3 script/merge_pass_summaries.py --help
```

Output:

```
usage: merge_pass_summaries.py [-h] [-o OUTPUT | --in-place] [--indent INDENT]
                               [--dedup] [--extended]
                               inputs [inputs ...]

Merge multiple pass_summary.json files into one consolidated summary.

positional arguments:
  inputs               Two or more pass_summary.json files to merge.

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Output path. Use '-' for stdout. Default: write to stdout.
  --in-place           Overwrite the FIRST input file with the merged result.
  --indent INDENT      JSON indent (default: 2)
  --dedup              Drop bit-identical reps (default = concat, 1+7=8).
  --extended           Emit rich schema with pass@K + reward averages + merged_from
                       audit trail. Default emits the legacy harness shape only.
```

**Default output** conforms strictly to the legacy `_pass_summary_doc()` shape from `eval/run_batch.py` — indistinguishable from a first-class harness emission. Use `--extended` when you want pass@K stats, the rich reward averages, and a `merged_from` audit trail.

---

## Common scenarios

### Scenario A — Canonical use case (1 rep + 7 reps = 8 reps)

```bash
python3 script/merge_pass_summaries.py \
    path/to/pass_summary.json \
    path/to/pass_summary_2-7.json \
    -o path/to/merged.json
```

**Output**: `merged.json` contains 8 reps, with recomputed averages and pass@K stats.

> Filenames are arbitrary — you can pass ANY two `pass_summary`-shaped JSON files.

### Scenario B — Print merged result to terminal

```bash
python3 script/merge_pass_summaries.py file1.json file2.json
```

(omits `-o` flag → writes to stdout)

Pipe-friendly:

```bash
python3 script/merge_pass_summaries.py file1.json file2.json | jq '.runs, .average_rubric_weights_percentage'
```

### Scenario C — Overwrite the first file in-place

```bash
python3 script/merge_pass_summaries.py file1.json file2.json --in-place
```

The merged result replaces `file1.json`. Useful when the canonical `pass_summary.json` should BECOME the merged version.

### Scenario D — Merge 3 or more files

```bash
python3 script/merge_pass_summaries.py file1.json file2.json file3.json file4.json -o merged.json
```

Works with any number of inputs ≥ 2.

### Scenario E — Dedup mode (advanced)

```bash
python3 script/merge_pass_summaries.py file1.json file2.json --dedup -o merged.json
```

Use `--dedup` **ONLY** when you suspect the same file was passed twice by accident. With `--dedup`, reps that are bit-for-bit identical (modulo `run_index`) are kept ONCE. Without it (the default), every input rep is kept as a distinct rep.

---

## Concrete walkthrough — aaron_garcia example

```bash
# Step 1: locate the two files
ls "/Users/apple/Documents/kensei-delivery/deliverables_2/aaron_garcia_a06e11f3-1b72-46ae-b494-62018ca3f97c/trajectories/Claude Opus 4.7/"
# pass_summary.json
# pass_summary_2-7.json

# Step 2: run the merger
cd /Users/apple/Documents/WildClawBench
python3 script/merge_pass_summaries.py \
    "/Users/apple/Documents/kensei-delivery/deliverables_2/aaron_garcia_a06e11f3-1b72-46ae-b494-62018ca3f97c/trajectories/Claude Opus 4.7/pass_summary.json" \
    "/Users/apple/Documents/kensei-delivery/deliverables_2/aaron_garcia_a06e11f3-1b72-46ae-b494-62018ca3f97c/trajectories/Claude Opus 4.7/pass_summary_2-7.json" \
    -o /tmp/aaron_merged.json

# Step 3: verify output
cat /tmp/aaron_merged.json | jq '{runs, average_test_weights_percentage, average_rubric_weights_percentage, pass_at_k_rubric_weights_percentage}'
```

Expected stderr line:

```
merged 2 file(s) into /tmp/aaron_merged.json (8 unique rep(s))
```

---

## Batch usage — process many tasks

For a folder structure like `<root>/<task>/trajectories/<model>/pass_summary*.json`:

```bash
for task_dir in /path/to/deliverables/*/; do
    model_dir="$task_dir/trajectories/Claude Opus 4.7"
    files=("$model_dir"/pass_summary*.json)
    if [ ${#files[@]} -ge 2 ]; then
        out="${task_dir}merged_pass_summary.json"
        python3 /Users/apple/Documents/WildClawBench/script/merge_pass_summaries.py "${files[@]}" -o "$out"
    fi
done
```

Auto-discovers all `pass_summary*.json` files per task, merges them, writes the result back into the task dir as `merged_pass_summary.json`.

---

## What the output looks like

### Default mode (legacy harness shape — indistinguishable from real `pass_summary.json`)

```json
{
  "model": "Claude Opus 4.7",
  "runs": 8,
  "average_test_weights_percentage": 6.82,
  "average_rubric_weights_percentage": 9.56,
  "per_run": [
    {"run_index": 1, "include_multimodal": true, "test_weights_percentage": 6.82, "rubric_weights_percentage": 14.71},
    {"run_index": 2, "include_multimodal": true, "test_weights_percentage": 6.82, "rubric_weights_percentage": 8.82},
    "...",
    {"run_index": 8, "include_multimodal": true, "test_weights_percentage": 6.82, "rubric_weights_percentage": 8.82}
  ]
}
```

This is byte-equivalent to what `eval/run_batch.py::_pass_summary_doc()` emits when all reps run in a single batch under the legacy schema. Drop-in replacement for a first-class `pass_summary.json`.

### Extended mode (`--extended`)

Adds pass@K stats, the rich reward averages, and a `merged_from` audit trail:

```json
{
  "model": "Claude Opus 4.7",
  "runs": 8,
  "average_reward": 0.0,
  "average_combined_reward": null,
  "average_rubric_reward": null,
  "average_test_reward": null,
  "average_rubric_weights_percentage": 9.56,
  "average_test_weights_percentage": 6.82,
  "pass_at_k_rubric_weights_percentage": 14.71,
  "pass_at_k_test_weights_percentage": 6.82,
  "pass_at_k_reward": null,
  "pass_at_k_combined_reward": null,
  "merged_from": [
    "/path/to/pass_summary.json",
    "/path/to/pass_summary_2-7.json"
  ],
  "per_run": [
    {"run_index": 1, "include_multimodal": true, "test_weights_percentage": 6.82, "rubric_weights_percentage": 14.71},
    "..."
  ]
}
```

### Field reference

| Field | Mode | Description |
|-------|------|-------------|
| `model` | both | Carried through from inputs (all inputs must agree, else error). |
| `runs` | both | Count of per-rep records in the merged result. |
| `average_test_weights_percentage` | both | Mean test % across all merged reps. |
| `average_rubric_weights_percentage` | both | Mean rubric % across all merged reps. |
| `average_reward`, `average_combined_reward`, `average_rubric_reward`, `average_test_reward` | extended only | Means from the current rich schema (`null` when source files only have legacy fields). |
| `pass_at_k_*` | extended only | Max of per-rep values (best-case = pass@K with K = total reps). |
| `merged_from` | extended only | Audit trail of source paths. |
| `per_run` | both | Concatenated per-rep records, renumbered `run_index` 1..N contiguous. In default mode, each rep carries the 4 legacy keys; in extended mode, the original rich fields are preserved verbatim. |

---

## Error handling — exit codes

| Exit code | Meaning |
|-----------|---------|
| `0` | Merge succeeded |
| `2` | Bad input: < 2 files, invalid JSON, missing `per_run`, or different `model` across inputs |

The script prints a descriptive error to stderr before exiting non-zero.

---

## Quick reference cheat sheet

```bash
# Merge to file (default: legacy harness shape)
python3 script/merge_pass_summaries.py A.json B.json -o merged.json

# Merge to stdout
python3 script/merge_pass_summaries.py A.json B.json

# Merge in-place (overwrites A.json)
python3 script/merge_pass_summaries.py A.json B.json --in-place

# Merge 3+ files
python3 script/merge_pass_summaries.py A.json B.json C.json -o merged.json

# Extended mode (pass@K, merged_from, full reward averages)
python3 script/merge_pass_summaries.py A.json B.json --extended -o merged.json

# Dedup mode (rarely needed)
python3 script/merge_pass_summaries.py A.json B.json --dedup -o merged.json

# Custom indent
python3 script/merge_pass_summaries.py A.json B.json --indent 4 -o merged.json
```

---

## Why this exists

When a task runs in two separate places (different output roots, different invocation, different machines), each invocation writes its own `pass_summary.json` with run indices that restart from 1. The two summaries are independently aware of their own reps, but downstream aggregators see only one tree at a time.

This script reconciles those splits into a single 8-rep (or N-rep) view with all aggregates recomputed from the merged per-run list. The output is structurally what `eval/run_batch.py::_pass_summary_doc()` would have written if all reps had been done in one batch — plus pass@K stats for both channels.
