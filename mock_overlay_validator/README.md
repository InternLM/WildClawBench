# Mock Overlay Validator

A simple, self-contained auditor for the mock-API overlay seed files that go
into `input/<task>/mock_data/<api>-api/`.

It works by **example matching**: for every supported API we ship a reference
copy of the shape the runtime expects under `examples/<api>-api/`. The script
matches your overlay file against the example with the same stem and reports
anything that drifts.

No FastAPI, no Docker, no install. One Python script, stdlib only, Python 3.10+.

## The one command you actually need

```bash
python3 /Users/apple/Documents/WildClawBench/mock_overlay_validator/validate.py /Users/apple/Documents/WildClawBench/input
```

That validates every task under `input/`. Swap the second path for a single
task folder (`input/<task_id>`) or a single overlay file to narrow the scope —
the script auto-detects what you gave it. Exit code is `0` if clean, `1` if any
errors were found.

## Layout

```
mock_overlay_validator/
├── validate.py                # the only entry point
├── README.md                  # this file
└── examples/
    ├── gmail-api/
    │   ├── drafts.json
    │   ├── labels.json
    │   └── messages.json
    ├── slack-api/
    │   └── ...
    └── ... 101 APIs total
```

Each `examples/<api>-api/<name>.{csv,json}` is the canonical reference for that
table or document. Your overlay file with the matching **stem** (filename minus
extension) is compared against it.

## Quick start

Just point `validate.py` at whatever you have — it figures out what to do:

```bash
# Validate one overlay file
python3 validate.py /path/to/mock_data/gmail-api/messages.csv

# Validate a task folder (works on the task root OR its mock_data/ child)
python3 validate.py /path/to/input/<task_id>
python3 validate.py /path/to/input/<task_id>/mock_data

# Validate EVERY task under an input root
python3 validate.py /path/to/input

# Validate one *-api dir inside a task
python3 validate.py /path/to/input/<task_id>/mock_data/gmail-api
```

Extra flags:

```bash
# Force the api name for a loose file outside any *-api folder
python3 validate.py --api gmail-api /tmp/messages.csv

# Machine-readable JSON
python3 validate.py /path/to/input --json > report.json

# Treat warnings as failures (CI mode)
python3 validate.py /path/to/input --exit-on-warning

# List all known APIs
python3 validate.py --list-apis
```

`--task <mock_data_dir>` and `--input <input_root>` still work if you want to
force a specific mode.

Exit code is `0` on success, `1` on errors (or warnings with
`--exit-on-warning`).

## How matching works

1. The script figures out which API your overlay file belongs to. If the path
   contains a `<name>-api/` segment we use that. Otherwise pass `--api <name>`.
2. It looks up `examples/<api>-api/<stem>.{csv,json}` (your overlay
   `messages.csv` matches example `messages.json` — extensions may differ,
   stems must match). This is intentional: the runtime accepts CSV overlays on
   top of JSON baselines.
3. The example tells us whether this seed is a **table** (array of rows) or a
   **document** (single object). Tables wrapped in an envelope like
   `{"QueryResponse": {"Customer": [...]}}` (QuickBooks-style) are detected
   and treated as tables.
4. We compare shape: columns/keys present and value types per column.

## Diagnostic codes

### Setup / pathing

| Code | Severity | What it means | What to do |
|---|---|---|---|
| `UNKNOWN_API` | error | No `examples/<api>-api/` directory exists | Check spelling (use the full `<name>-api` form). Run `--list-apis`. |
| `API_UNDETECTABLE` | error | Could not infer api from path and `--api` not given | Pass `--api <name>-api`. |
| `UNREGISTERED_FILENAME` | warn | No example has this stem for this API | The runtime ignores files whose name doesn't match a registered table — rename or delete. |
| `UNKNOWN_EXTENSION` | warn | File is not `.csv` or `.json` | The runtime loader only reads `.csv` and `.json`. Move blob content to `file_blobs/`. |
| `FILE_UNREADABLE` | error | OS-level read failure | Check perms / path. |
| `DIR_NOT_FOUND` | error | Passed-in directory doesn't exist | Fix the path. |
| `DIR_NAMING` | error | Subdir inside `mock_data/` isn't named `<name>-api` | Rename it. |
| `OVERLAY_DIR_EMPTY` | warn | API overlay dir has no files | Add overlays or remove the dir. |
| `EMPTY_MOCK_DATA` | warn | Task's `mock_data/` has no API subdirs | Add at least one `<name>-api/` dir. |
| `NO_TASKS` | warn | `--input <root>` found no task dirs | Check the root path. |

### File-shape problems

| Code | Severity | What it means | What to do |
|---|---|---|---|
| `NOT_UTF8` | error | File isn't UTF-8 decodable (covers CSV and JSON; UTF-8 BOM is auto-stripped) | Re-save as UTF-8. |
| `CSV_MALFORMED` | error | Could not parse CSV | Open in a strict CSV tool; check for unbalanced quotes. |
| `CSV_DUPLICATE_HEADER` | error | Same column name appears twice | Rename one. |
| `CSV_RAGGED_ROW` | error | A row has more cells than the header | Re-quote fields containing commas. |
| `CSV_BLANK_HEADER` | warn | A header cell is empty | Name the column. |
| `CSV_EMPTY` | warn | No rows / empty file | Add rows, or delete the file. |
| `JSON_MALFORMED` | error | Invalid JSON | Lint your JSON. |
| `JSON_NOT_ARRAY` | error | Table seed must be a top-level JSON array (or a recognised wrapped envelope) | Wrap rows in `[ ... ]`. |
| `JSON_NOT_OBJECT` | error | Document seed must be a top-level JSON object | Use `{ ... }`. |
| `JSON_ROW_NOT_OBJECT` | error | A row in a JSON table is not an object | Each row must be `{ ... }`. |
| `DOCUMENT_BAD_EXTENSION` | error | This seed is a document; only `.json` accepted | Convert to JSON. |

### Schema drift

| Code | Severity | What it means | What to do |
|---|---|---|---|
| `SCHEMA_MISSING_COLUMNS` | error | Overlay lacks columns present in example | Add them, even if blank. |
| `SCHEMA_EXTRA_COLUMNS` | warn | Overlay has columns not in example | The runtime ignores them — usually a typo. |
| `SCHEMA_TYPE_DRIFT` | error | A column's values don't parse like the example (e.g. `bool` example, `str` overlay) | Match the example's value shape. |
| `KEY_MISSING` | error | A nested JSON key that exists in the canonical example is absent in the overlay (path is dotted, e.g. `identity.json.owners.acc_chk_001`) | Add the missing key. |
| `KEY_EXTRA` | warn | Overlay has a nested key the canonical example doesn't have | The runtime ignores it — usually a typo or a stale field. |
| `TYPE_MISMATCH` | error | At a nested path, canonical is `scalar` but overlay is `dict`/`list` (or vice versa). Path uses `[]` inside arrays. | Match the canonical shape (e.g. don't wrap a scalar in an object). |
| `RAGGED_OBJECT_KEYS` | info | Objects inside a JSON array have inconsistent key-sets among themselves. The harness tolerates this; missing required keys are reported separately as errors. | Make row objects uniform for cleaner data. |
| `OVERLAY_EMPTY` | warn | Overlay file has zero rows | Table will be empty at runtime — confirm that's intentional. |
| `EXAMPLE_BROKEN` | warn | Validator's own example is broken (not your fault) | Report this to the validator maintainers. |
| `EXAMPLE_EMPTY` | warn | Validator's example has zero rows so type checks are skipped | Informational. |

## Ground rules for mock-data authors

1. **Filenames are load-bearing.** `messages.csv`, not `messages_v2.csv` or
   `messages backup.csv`. Stems must match a registered table/document.
2. **CSV-overlay-wins.** You can ship `messages.csv` to shadow a baseline
   `messages.json`. The runtime picks CSV when both exist. The validator
   accepts this and compares against whichever example exists.
3. **Tables vs documents.** Tables are arrays. Documents are single objects
   (e.g. `profile.json`, `workspace.json`). The example tells you which.
4. **Columns are a contract.** Don't rename, don't drop. Missing columns
   become loader-time `KeyError`s. Extra columns are silently dropped, which
   is almost never what you want.
5. **Types matter.** If the example column has integers, send integers. If
   it has ISO datetimes, send ISO datetimes. The validator flags drift.
6. **No prose, no comments inside data files.** It's all going through a
   strict loader.

## Updating examples

The reference shapes were copied from `environment/<api>-api/*.{csv,json}` in
the parent repo at a fixed snapshot. When the environment schema evolves,
re-snapshot the examples directory.

## Limitations

The validator inspects file shape, not semantics. It can't tell you whether
`messages.csv` contains the *right* messages for the task — only whether the
schema is structurally compatible with the runtime loader.
