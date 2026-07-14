#!/usr/bin/env python3
"""
Mock-overlay validator.

Compares a candidate mock-data file (or a whole task's mock_data/ tree) against
a known-good example for the same API+filename living under examples/<api>/.

It checks structural shape (CSV/JSON well-formed), schema (same field set as
the example), and inferred field types (does each column parse the same way
as the example?).

Usage:
    python3 validate.py FILE [FILE ...]
    python3 validate.py --api gmail-api path/to/overlay/dir
    python3 validate.py --task path/to/input/<task>/mock_data
    python3 validate.py --input path/to/input
    python3 validate.py --list-apis
    python3 validate.py --json ...        # machine-readable output

Exit codes:
    0  no errors (warnings allowed)
    1  one or more errors
    2  bad CLI usage
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
EXAMPLES_DIR = HERE / "examples"

# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

SEV_ERROR = "ERROR"
SEV_WARN = "WARN"
SEV_INFO = "INFO"


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    api: str | None = None
    file: str | None = None
    hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "api": self.api,
            "file": self.file,
            "hint": self.hint,
        }


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)
    files_checked: int = 0
    apis_seen: set[str] = field(default_factory=set)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == SEV_ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == SEV_WARN]

    @property
    def infos(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == SEV_INFO]

    def add(self, issue: Issue) -> None:
        self.issues.append(issue)

    def to_dict(self) -> dict[str, Any]:
        return {
            "files_checked": self.files_checked,
            "apis_seen": sorted(self.apis_seen),
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "infos": len(self.infos),
            },
            "issues": [i.to_dict() for i in self.issues],
        }

    def format_human(self) -> str:
        lines: list[str] = []
        for i in self.issues:
            head = f"[{i.severity:<5}] {i.code}: {i.message}"
            lines.append(head)
            ctx_bits = []
            if i.api:
                ctx_bits.append(f"api={i.api}")
            if i.file:
                ctx_bits.append(f"file={i.file}")
            if ctx_bits:
                lines.append("        " + " ".join(ctx_bits))
            if i.hint:
                lines.append(f"        hint: {i.hint}")
        if not self.issues:
            lines.append("OK: no issues found")
        lines.append("")
        lines.append(
            f"  files_checked={self.files_checked} "
            f"apis_seen={len(self.apis_seen)} "
            f"errors={len(self.errors)} "
            f"warnings={len(self.warnings)} "
            f"infos={len(self.infos)}"
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# File loading + structural checks
# ---------------------------------------------------------------------------


def _read_text(path: Path) -> tuple[str | None, Issue | None]:
    try:
        raw = path.read_bytes()
    except OSError as e:
        return None, Issue(
            severity=SEV_ERROR,
            code="FILE_UNREADABLE",
            message=f"could not read file: {e}",
            file=str(path),
        )
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        return None, Issue(
            severity=SEV_ERROR,
            code="NOT_UTF8",
            message=f"file is not valid UTF-8: {e}",
            file=str(path),
            hint="re-save the file with UTF-8 encoding (no BOM preferred)",
        )
    return text, None


def _load_csv_rows(path: Path) -> tuple[list[str] | None, list[dict[str, str]] | None, list[Issue]]:
    issues: list[Issue] = []
    text, err = _read_text(path)
    if err is not None:
        return None, None, [err]
    assert text is not None
    if not text.strip():
        issues.append(
            Issue(
                severity=SEV_WARN,
                code="CSV_EMPTY",
                message="CSV file is empty",
                file=str(path),
            )
        )
        return None, None, issues

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        issues.append(
            Issue(
                severity=SEV_WARN,
                code="CSV_EMPTY",
                message="CSV has no header row",
                file=str(path),
            )
        )
        return None, None, issues
    except csv.Error as e:
        issues.append(
            Issue(
                severity=SEV_ERROR,
                code="CSV_MALFORMED",
                message=f"CSV parser error: {e}",
                file=str(path),
            )
        )
        return None, None, issues

    seen: dict[str, int] = {}
    blanks: list[int] = []
    for idx, col in enumerate(header):
        if col == "":
            blanks.append(idx)
            continue
        seen[col] = seen.get(col, 0) + 1
    dups = sorted([c for c, n in seen.items() if n > 1])
    if dups:
        issues.append(
            Issue(
                severity=SEV_ERROR,
                code="CSV_DUPLICATE_HEADER",
                message=f"duplicate column header(s): {', '.join(dups)}",
                file=str(path),
                hint="each column must have a unique name",
            )
        )
        return header, None, issues
    if blanks:
        issues.append(
            Issue(
                severity=SEV_WARN,
                code="CSV_BLANK_HEADER",
                message=f"blank column header at position(s): {', '.join(str(b) for b in blanks)}",
                file=str(path),
            )
        )

    rows: list[dict[str, str]] = []
    width = len(header)
    try:
        for row_idx, raw_row in enumerate(reader, start=2):
            if len(raw_row) > width:
                issues.append(
                    Issue(
                        severity=SEV_ERROR,
                        code="CSV_RAGGED_ROW",
                        message=(
                            f"row {row_idx} has {len(raw_row)} fields but header has {width}"
                        ),
                        file=str(path),
                        hint="check for unquoted commas or stray columns",
                    )
                )
                return header, None, issues
            if len(raw_row) < width:
                raw_row = raw_row + [""] * (width - len(raw_row))
            rows.append({header[i]: raw_row[i] for i in range(width)})
    except csv.Error as e:
        issues.append(
            Issue(
                severity=SEV_ERROR,
                code="CSV_MALFORMED",
                message=f"CSV parser error: {e}",
                file=str(path),
            )
        )
        return header, None, issues

    return header, rows, issues


def _load_json(path: Path) -> tuple[Any | None, list[Issue]]:
    text, err = _read_text(path)
    if err is not None:
        return None, [err]
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return None, [
            Issue(
                severity=SEV_ERROR,
                code="JSON_MALFORMED",
                message=f"JSON parse error: {e.msg} (line {e.lineno} col {e.colno})",
                file=str(path),
            )
        ]
    return data, []


# ---------------------------------------------------------------------------
# Field-type inference
# ---------------------------------------------------------------------------

_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+(?:[eE][+-]?\d+)?$")


def _infer_field_type(value: Any) -> str:
    # Coarse type label used for schema comparison. Designed to be CONSERVATIVE:
    # the runtime stores every CSV cell as a string and only narrows via explicit
    # strict_int/strict_bool/etc, so "string-ish" values (incl. ones that contain
    # commas) all collapse to 'str' to avoid spurious drift errors from prose.
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, list):
        return "json_list"
    if isinstance(value, dict):
        return "json_dict"
    if not isinstance(value, str):
        return type(value).__name__
    s = value.strip()
    if s == "":
        return "blank"
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
        try:
            parsed = json.loads(s)
            return "json_list" if isinstance(parsed, list) else "json_dict"
        except json.JSONDecodeError:
            pass
    if _INT_RE.match(s):
        return "int_str"
    if _FLOAT_RE.match(s):
        return "float_str"
    return "str"


def _summarise_field_types(values: Iterable[Any]) -> set[str]:
    types: set[str] = set()
    for v in values:
        t = _infer_field_type(v)
        if t in ("blank", "null"):
            continue
        types.add(t)
    return types


# Compatibility classes — values in the same group are interchangeable because
# the runtime coercers (strict_int / opt_int / etc) parse any matching string
# into the target type. We deliberately put int_str / float_str / str in one
# group: a CSV cell is always read as str by csv.reader, so column-level
# 'drift' between '42' and 'forty-two' is just a per-row coercion problem, not
# a schema problem.
_TYPE_GROUPS = [
    {"int", "float", "int_str", "float_str", "str"},
    {"json_list", "json_dict"},
    {"bool"},
]


def _types_compatible(example_types: set[str], overlay_types: set[str]) -> bool:
    if not overlay_types:
        return True
    if not example_types:
        return True
    for ot in overlay_types:
        if ot in example_types:
            continue
        matched = False
        for group in _TYPE_GROUPS:
            if ot in group and example_types & group:
                matched = True
                break
        if not matched:
            return False
    return True


def _container_kind(value: Any) -> str:
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, list):
        return "list"
    return "scalar"


DeepFinding = tuple[str, str, str]


@dataclass(frozen=True)
class _ListShape:
    # Per-list shape derived from the raw example siblings. required_keys is
    # the intersection (must appear in every sibling); known_keys is the union
    # (may appear in some siblings). kinds_per_key carries container-kind
    # polymorphism per key (dict/list/scalar/null). dict_elements holds the
    # raw sibling dicts so a deeper recursion can gather per-key sibling
    # values and preserve ragged-tolerance at every nesting level.
    required_keys: frozenset
    known_keys: frozenset
    kinds_per_key: dict
    dict_element_count: int
    dict_elements: tuple


def _element_kind(value: Any) -> str:
    if value is None:
        return "null"
    return _container_kind(value)


def _compute_list_shape(example_list: list) -> _ListShape:
    dict_elems = [e for e in example_list if isinstance(e, dict)]
    if not dict_elems:
        return _ListShape(frozenset(), frozenset(), {}, 0, tuple())
    key_sets = [set(e.keys()) for e in dict_elems]
    required = frozenset(set.intersection(*key_sets)) if key_sets else frozenset()
    known = frozenset(set.union(*key_sets))
    kinds: dict[str, set[str]] = {}
    for e in dict_elems:
        for k, v in e.items():
            kinds.setdefault(k, set()).add(_element_kind(v))
    frozen_kinds = {k: frozenset(v) for k, v in kinds.items()}
    return _ListShape(required, known, frozen_kinds, len(dict_elems), tuple(dict_elems))


def _merge_dicts_for_values(dicts: list[dict]) -> dict:
    if not dicts:
        return {}
    return _merge_canonical(dicts) if all(isinstance(d, dict) for d in dicts) else {}


def _deep_compare_field(
    example_values: list,
    actual_value: Any,
    path: str,
) -> list[DeepFinding]:
    # Per-field entrypoint: example_values is the raw collection of that
    # field's value across all example rows. For dict siblings the intersection
    # defines required keys and the union defines known keys (ragged parents
    # never over-constrain). For list siblings the flattened concatenation
    # feeds the same intersection semantics one level deeper.
    non_null = [v for v in example_values if v is not None]
    if not non_null:
        return []
    all_dicts = all(isinstance(v, dict) for v in non_null)
    all_lists = all(isinstance(v, list) for v in non_null)
    if all_dicts and len(non_null) >= 1:
        shape = _compute_list_shape(non_null)
        canonical = _merge_dicts_for_values(non_null)
        if not isinstance(actual_value, dict):
            return _deep_compare(canonical, actual_value, path)
        return _deep_compare(canonical, actual_value, path, parent_shape=shape)
    if all_lists:
        flat = [item for lst in non_null for item in lst]
        return _deep_compare(flat if flat else non_null[0], actual_value, path)
    return _deep_compare(non_null[0], actual_value, path)


def _deep_compare(
    example: Any,
    actual: Any,
    path: str,
    *,
    parent_shape: _ListShape | None = None,
) -> list[DeepFinding]:
    # Recursive structural comparison between an example (canonical) and an
    # actual JSON value. When called from a list branch, parent_shape carries
    # the intersection/union/kinds computed from raw sibling example dicts, so
    # the dict branch can (a) only flag KEY_MISSING for keys present in EVERY
    # example sibling and (b) accept container-kind polymorphism the seed
    # itself displays. RAGGED_OBJECT_KEYS is reported once per list level.
    findings: list[DeepFinding] = []
    ex_kind = _container_kind(example)
    ac_kind = _container_kind(actual)

    if ex_kind != ac_kind:
        if ex_kind == "scalar" and ac_kind == "scalar":
            pass
        else:
            findings.append((
                "TYPE_MISMATCH",
                SEV_ERROR,
                f"type mismatch at '{path}': canonical={ex_kind}, actual={ac_kind}",
            ))
            return findings

    if ex_kind == "dict":
        ex_keys = set(example.keys())
        ac_keys = set(actual.keys())
        if parent_shape is not None and parent_shape.dict_element_count > 0:
            required_keys = set(parent_shape.required_keys)
            known_keys = set(parent_shape.known_keys)
        else:
            required_keys = ex_keys
            known_keys = ex_keys
        for k in sorted(ex_keys - ac_keys):
            if k in required_keys:
                findings.append((
                    "KEY_MISSING",
                    SEV_ERROR,
                    f"missing canonical key '{path}.{k}'",
                ))
        for k in sorted(ac_keys - ex_keys):
            if k not in known_keys:
                findings.append((
                    "KEY_EXTRA",
                    SEV_WARN,
                    f"extra key '{path}.{k}' not in canonical",
                ))
        for k in sorted(ex_keys & ac_keys):
            if parent_shape is not None and k in parent_shape.kinds_per_key:
                seen_kinds = parent_shape.kinds_per_key[k]
                actual_kind = _element_kind(actual[k])
                if actual_kind in seen_kinds:
                    if actual_kind in {"scalar", "null"}:
                        # Polymorphism includes this kind; skip container-vs-container
                        # nested recursion when both sides land on the same accepted
                        # scalar/null kind (nothing meaningful to compare deeper).
                        continue
                else:
                    canonical_kind = _element_kind(example[k])
                    findings.append((
                        "TYPE_MISMATCH",
                        SEV_ERROR,
                        f"type mismatch at '{path}.{k}': canonical={canonical_kind}, actual={actual_kind}",
                    ))
                    continue
            if parent_shape is not None and parent_shape.dict_elements:
                sibling_values = [e[k] for e in parent_shape.dict_elements if k in e]
                findings.extend(_deep_compare_field(sibling_values, actual[k], f"{path}.{k}"))
            else:
                findings.extend(_deep_compare(example[k], actual[k], f"{path}.{k}"))
        return findings

    if ex_kind == "list":
        if not example or not actual:
            return findings
        shape = _compute_list_shape(example)
        dict_elems = [e for e in example if isinstance(e, dict)]
        if dict_elems:
            canonical_item: Any = _merge_dicts_for_values(dict_elems)
        else:
            canonical_item = example[0]
        canonical_is_dict = isinstance(canonical_item, dict)
        if shape.dict_element_count > 1 and shape.known_keys != shape.required_keys:
            optional = sorted(shape.known_keys - shape.required_keys)
            findings.append((
                "RAGGED_OBJECT_KEYS",
                SEV_INFO,
                f"ragged object keys at '{path}': "
                f"required={sorted(shape.required_keys)}, "
                f"optional={optional} "
                "-- harness tolerates this; only required-key absences are FAIL",
            ))
        ragged_reported = False
        first_actual_keys: set[str] | None = None
        for idx, item in enumerate(actual):
            if canonical_is_dict and isinstance(item, dict):
                if first_actual_keys is None:
                    first_actual_keys = set(item.keys())
                elif not ragged_reported and set(item.keys()) != first_actual_keys:
                    ragged_indices = [
                        i for i, r in enumerate(actual)
                        if isinstance(r, dict) and set(r.keys()) != first_actual_keys
                    ]
                    findings.append((
                        "RAGGED_OBJECT_KEYS",
                        SEV_INFO,
                        f"Class B: ragged object keys vs first object at row(s) {ragged_indices} "
                        "-- harness tolerates this; required-key absences are reported separately as FAIL",
                    ))
                    ragged_reported = True
            findings.extend(
                _deep_compare(canonical_item, item, f"{path}[]", parent_shape=shape)
            )
        return findings

    ex_type = _infer_field_type(example)
    ac_type = _infer_field_type(actual)
    ex_types = {ex_type} - {"blank", "null"}
    ac_types = {ac_type} - {"blank", "null"}
    if not _types_compatible(ex_types, ac_types):
        findings.append((
            "TYPE_MISMATCH",
            SEV_ERROR,
            f"type mismatch at '{path}': canonical={ex_type}, actual={ac_type}",
        ))
    return findings


def _merge_canonical(values: list[Any]) -> Any:
    # Top-level dict-key union is the "advertised surface" used for
    # SCHEMA_MISSING_COLUMNS diffing. Nested list[dict] values are preserved
    # RAW (not collapsed to a single merged exemplar) so _deep_compare's list
    # branch can compute the real intersection/union across raw siblings.
    dict_values = [v for v in values if isinstance(v, dict)]
    if dict_values and len(dict_values) == len([v for v in values if v is not None]):
        merged: dict[str, Any] = {}
        for d in dict_values:
            for k, v in d.items():
                if k not in merged:
                    merged[k] = v
                    continue
                existing = merged[k]
                if existing is None and v is not None:
                    merged[k] = v
                    continue
                if isinstance(existing, dict) and isinstance(v, dict):
                    merged[k] = _merge_canonical([existing, v])
                elif isinstance(existing, list) and isinstance(v, list):
                    if not existing and v:
                        merged[k] = v
        return merged
    list_values = [v for v in values if isinstance(v, list)]
    if list_values and len(list_values) == len([v for v in values if v is not None]):
        for lst in list_values:
            if lst:
                return lst
        return []
    for v in values:
        if v is not None and (not isinstance(v, str) or v.strip()):
            return v
    for v in values:
        if v is not None:
            return v
    return None


def _dedupe_findings(findings: list[DeepFinding]) -> list[DeepFinding]:
    seen: set[tuple[str, str]] = set()
    out: list[DeepFinding] = []
    for code, sev, msg in findings:
        key = (code, msg)
        if key in seen:
            continue
        seen.add(key)
        out.append((code, sev, msg))
    return out


# ---------------------------------------------------------------------------
# Normalisation: turn either CSV-rows-of-strings or JSON-list-of-dicts into the
# same shape — list[dict[str, value]] — so schema comparison is format-agnostic.
# ---------------------------------------------------------------------------


def _peel_wrapped_table(data: Any) -> list[dict[str, Any]] | None:
    # Some APIs (notably QuickBooks) wrap table arrays in an envelope dict, e.g.
    # {"QueryResponse": {"Customer": [ {...}, {...} ]}}. The runtime data loader
    # peels those envelopes before iterating rows, so the validator must too —
    # otherwise we mis-classify these tables as documents and reject overlays.
    # Accepted shapes: {wrap: [rows]} OR {wrap: {inner: [rows]}} where rows are
    # objects. Returns the inner row list, or None if not a wrapped table.
    if not isinstance(data, dict) or len(data) != 1:
        return None
    inner = next(iter(data.values()))
    if isinstance(inner, list):
        if inner and all(isinstance(r, dict) for r in inner):
            return inner
        return None
    if isinstance(inner, dict):
        list_valued = [
            v for v in inner.values()
            if isinstance(v, list) and v and all(isinstance(r, dict) for r in v)
        ]
        dict_valued = [v for v in inner.values() if isinstance(v, dict)]
        if len(list_valued) == 1 and not dict_valued:
            return list_valued[0]
    return None


def _load_table(path: Path) -> tuple[list[dict[str, Any]] | None, list[Issue]]:
    ext = path.suffix.lower()
    if ext == ".csv":
        header, rows, issues = _load_csv_rows(path)
        if rows is None:
            return None, issues
        return rows, issues
    if ext == ".json":
        data, issues = _load_json(path)
        if data is None:
            return None, issues
        if not isinstance(data, list):
            peeled = _peel_wrapped_table(data)
            if peeled is not None:
                return peeled, issues
            issues.append(
                Issue(
                    severity=SEV_ERROR,
                    code="JSON_NOT_ARRAY",
                    message=f"expected a JSON array (table), got {type(data).__name__}",
                    file=str(path),
                    hint="tables must be a top-level JSON array of objects",
                )
            )
            return None, issues
        for ridx, row in enumerate(data):
            if not isinstance(row, dict):
                issues.append(
                    Issue(
                        severity=SEV_ERROR,
                        code="JSON_ROW_NOT_OBJECT",
                        message=f"row {ridx} is {type(row).__name__}, expected object",
                        file=str(path),
                    )
                )
                return None, issues
        return data, issues
    return None, [
        Issue(
            severity=SEV_WARN,
            code="UNKNOWN_EXTENSION",
            message=f"unrecognised extension '{ext}' — only .csv and .json are loaded by the runtime",
            file=str(path),
        )
    ]


def _load_document(path: Path) -> tuple[dict[str, Any] | None, list[Issue]]:
    if path.suffix.lower() != ".json":
        return None, [
            Issue(
                severity=SEV_ERROR,
                code="DOCUMENT_BAD_EXTENSION",
                message=f"expected .json for a document, got '{path.suffix}'",
                file=str(path),
            )
        ]
    data, issues = _load_json(path)
    if data is None:
        return None, issues
    if not isinstance(data, dict):
        issues.append(
            Issue(
                severity=SEV_ERROR,
                code="JSON_NOT_OBJECT",
                message=f"expected a JSON object (document), got {type(data).__name__}",
                file=str(path),
            )
        )
        return None, issues
    return data, issues


# ---------------------------------------------------------------------------
# Example catalog
# ---------------------------------------------------------------------------


def list_apis() -> list[str]:
    if not EXAMPLES_DIR.exists():
        return []
    return sorted(p.name for p in EXAMPLES_DIR.iterdir() if p.is_dir())


def example_files_for_api(api: str) -> dict[str, Path]:
    # Stem (filename minus extension) is the join key so overlay messages.csv
    # matches example messages.json — CSV-overlay-wins semantics in the runtime.
    api_dir = EXAMPLES_DIR / api
    if not api_dir.is_dir():
        return {}
    result: dict[str, Path] = {}
    for f in api_dir.iterdir():
        if f.is_file() and f.suffix.lower() in {".csv", ".json"}:
            result[f.stem] = f
    return result


# ---------------------------------------------------------------------------
# Core: compare one overlay file against its example
# ---------------------------------------------------------------------------


def _validate_table(
    overlay_path: Path,
    example_path: Path,
    api: str,
) -> list[Issue]:
    issues: list[Issue] = []

    overlay_rows, ovl_issues = _load_table(overlay_path)
    issues.extend(ovl_issues)
    if overlay_rows is None:
        return issues

    example_rows, ex_issues = _load_table(example_path)
    # Don't surface example issues to the team — that would be our bug.
    if example_rows is None:
        issues.append(
            Issue(
                severity=SEV_ERROR,
                code="EXAMPLE_BROKEN",
                message="example file failed to load — please report this to the validator maintainers",
                api=api,
                file=str(overlay_path),
                hint=f"example={example_path}",
            )
        )
        return issues

    if not example_rows:
        # Empty example — nothing to compare schema against. Best we can do is warn.
        issues.append(
            Issue(
                severity=SEV_INFO,
                code="EXAMPLE_EMPTY",
                message="example has no rows — schema check is skipped for this file",
                api=api,
                file=str(overlay_path),
            )
        )
        return issues

    canonical_row = _merge_canonical(example_rows)
    example_cols = list(canonical_row.keys())
    example_col_set = set(example_cols)

    if not overlay_rows:
        issues.append(
            Issue(
                severity=SEV_WARN,
                code="OVERLAY_EMPTY",
                message="overlay has no rows — table will be empty at runtime",
                api=api,
                file=str(overlay_path),
            )
        )
        return issues

    # Required columns = intersection of example row key-sets (present in EVERY
    # example row = genuinely required by the runtime loader). Known columns =
    # union (may appear on some rows; safe to include, not an error when absent).
    # We check required columns per-row so a column dropped from any overlay row
    # surfaces even if another row still carries it (the runtime loader reads
    # row-by-row; a missing key crashes with KeyError on that row).
    example_shape = _compute_list_shape(example_rows)
    required_cols = set(example_shape.required_keys) if example_shape.dict_element_count else example_col_set
    known_cols = set(example_shape.known_keys) if example_shape.dict_element_count else example_col_set

    overlay_col_set: set[str] = set()
    for row in overlay_rows:
        if isinstance(row, dict):
            overlay_col_set.update(row.keys())

    missing_per_col: dict[str, list[int]] = {}
    for col in sorted(required_cols):
        offenders = [
            i for i, row in enumerate(overlay_rows)
            if isinstance(row, dict) and col not in row
        ]
        if offenders:
            missing_per_col[col] = offenders

    extra = sorted(overlay_col_set - known_cols)

    if missing_per_col:
        total_rows = sum(1 for r in overlay_rows if isinstance(r, dict))
        parts: list[str] = []
        for col in sorted(missing_per_col.keys()):
            offenders = missing_per_col[col]
            preview = offenders if len(offenders) <= 10 else offenders[:10] + ["..."]
            parts.append(
                f"'{col}' missing in {len(offenders)}/{total_rows} row(s) {preview}"
            )
        issues.append(
            Issue(
                severity=SEV_ERROR,
                code="SCHEMA_MISSING_COLUMNS",
                message="overlay rows missing required column(s): " + "; ".join(parts),
                api=api,
                file=str(overlay_path),
                hint=(
                    "the runtime loader reads each row individually; a required key "
                    "absent from any row crashes that row's coercion. "
                    f"required columns: {', '.join(sorted(required_cols))}"
                ),
            )
        )
    if extra:
        issues.append(
            Issue(
                severity=SEV_WARN,
                code="SCHEMA_EXTRA_COLUMNS",
                message=f"overlay has unexpected column(s): {', '.join(extra)}",
                api=api,
                file=str(overlay_path),
                hint=(
                    "extra columns are ignored by the runtime and usually mean a typo; "
                    f"example columns: {', '.join(example_cols)}"
                ),
            )
        )

    shared = sorted(example_col_set & overlay_col_set)
    for col in shared:
        example_types = _summarise_field_types(r.get(col) for r in example_rows)
        overlay_types = _summarise_field_types(r.get(col) for r in overlay_rows)
        if not _types_compatible(example_types, overlay_types):
            issues.append(
                Issue(
                    severity=SEV_ERROR,
                    code="SCHEMA_TYPE_DRIFT",
                    message=(
                        f"column '{col}' values don't parse like the example "
                        f"(example types={sorted(example_types) or ['blank']}, "
                        f"overlay types={sorted(overlay_types) or ['blank']})"
                    ),
                    api=api,
                    file=str(overlay_path),
                    hint=(
                        "make sure each value uses the same shape as the example "
                        "(e.g. integers stay integers, ISO datetimes stay ISO, "
                        "comma-lists keep using commas)"
                    ),
                )
            )

    if overlay_path.suffix.lower() == ".json" and example_path.suffix.lower() == ".json":
        root = f"{overlay_path.name}[]"
        findings: list[DeepFinding] = []
        top_shape = _compute_list_shape(example_rows)
        first_actual_keys: set[str] | None = None
        ragged_reported = False
        for idx, row in enumerate(overlay_rows):
            if not isinstance(row, dict):
                continue
            if first_actual_keys is None:
                first_actual_keys = set(row.keys())
            elif not ragged_reported and set(row.keys()) != first_actual_keys:
                ragged_indices = [
                    i for i, r in enumerate(overlay_rows)
                    if isinstance(r, dict) and set(r.keys()) != first_actual_keys
                ]
                findings.append((
                    "RAGGED_OBJECT_KEYS",
                    SEV_INFO,
                    f"Class B: ragged object keys vs first object at row(s) {ragged_indices} "
                    "-- harness tolerates this; required-key absences are reported separately as FAIL",
                ))
                ragged_reported = True
            for k in sorted(set(canonical_row.keys()) & set(row.keys())):
                if k in top_shape.kinds_per_key:
                    seen_kinds = top_shape.kinds_per_key[k]
                    actual_kind = _element_kind(row[k])
                    if actual_kind in seen_kinds and actual_kind in {"scalar", "null"}:
                        continue
                example_values_for_k = [r.get(k) for r in example_rows if isinstance(r, dict) and k in r]
                findings.extend(_deep_compare_field(example_values_for_k, row[k], f"{root}.{k}"))
        for code, sev, msg in _dedupe_findings(findings):
            issues.append(
                Issue(
                    severity=sev,
                    code=code,
                    message=msg,
                    api=api,
                    file=str(overlay_path),
                )
            )

    return issues


def _validate_document(
    overlay_path: Path,
    example_path: Path,
    api: str,
) -> list[Issue]:
    issues: list[Issue] = []
    overlay_doc, ovl_issues = _load_document(overlay_path)
    issues.extend(ovl_issues)
    if overlay_doc is None:
        return issues
    example_doc, _ex_issues = _load_document(example_path)
    if example_doc is None:
        issues.append(
            Issue(
                severity=SEV_ERROR,
                code="EXAMPLE_BROKEN",
                message="example file failed to load — please report this to the validator maintainers",
                api=api,
                file=str(overlay_path),
            )
        )
        return issues

    root = overlay_path.name
    for code, sev, msg in _dedupe_findings(_deep_compare(example_doc, overlay_doc, root)):
        issues.append(
            Issue(
                severity=sev,
                code=code,
                message=msg,
                api=api,
                file=str(overlay_path),
            )
        )
    return issues


def _example_is_document(example_path: Path) -> bool:
    if example_path.suffix.lower() != ".json":
        return False
    try:
        with example_path.open("r", encoding="utf-8-sig") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    return _peel_wrapped_table(data) is None


def validate_file(overlay_path: Path, api: str, report: Report) -> None:
    report.files_checked += 1
    report.apis_seen.add(api)

    ext = overlay_path.suffix.lower()
    if ext not in {".csv", ".json"}:
        report.add(
            Issue(
                severity=SEV_WARN,
                code="UNKNOWN_EXTENSION",
                message=(
                    f"file extension '{ext}' is not loaded by the runtime; only .csv and .json "
                    "seed files are picked up"
                ),
                api=api,
                file=str(overlay_path),
            )
        )
        return

    examples = example_files_for_api(api)
    if not examples:
        hint = f"expected dir: {EXAMPLES_DIR / api}. Run with --list-apis to see all known APIs."
        if not api.endswith("-api") and (EXAMPLES_DIR / f"{api}-api").is_dir():
            hint = f"did you mean '{api}-api'? API names always include the '-api' suffix."
        report.add(
            Issue(
                severity=SEV_ERROR,
                code="UNKNOWN_API",
                message=f"no examples folder for api '{api}'",
                api=api,
                file=str(overlay_path),
                hint=hint,
            )
        )
        return

    stem = overlay_path.stem
    example_path = examples.get(stem)
    if example_path is None:
        report.add(
            Issue(
                severity=SEV_WARN,
                code="UNREGISTERED_FILENAME",
                message=(
                    f"no example named '{stem}' for api '{api}' — the runtime loader "
                    "only consults files whose stem matches a registered table/document, so this overlay will be ignored"
                ),
                api=api,
                file=str(overlay_path),
                hint=f"valid stems: {', '.join(sorted(examples.keys()))}",
            )
        )
        return

    if _example_is_document(example_path):
        for issue in _validate_document(overlay_path, example_path, api):
            report.add(issue)
    else:
        for issue in _validate_table(overlay_path, example_path, api):
            report.add(issue)


# ---------------------------------------------------------------------------
# Path walkers
# ---------------------------------------------------------------------------

_API_DIR_RE = re.compile(r"^[a-z0-9][a-z0-9-]*-api$")


def _infer_api_from_path(path: Path) -> str | None:
    for parent in [path] + list(path.parents):
        if _API_DIR_RE.match(parent.name):
            return parent.name
    return None


def validate_overlay_dir(overlay_dir: Path, api: str, report: Report) -> None:
    if not overlay_dir.is_dir():
        report.add(
            Issue(
                severity=SEV_ERROR,
                code="DIR_NOT_FOUND",
                message=f"overlay dir does not exist or is not a directory: {overlay_dir}",
                api=api,
            )
        )
        return
    files = sorted(p for p in overlay_dir.iterdir() if p.is_file())
    if not files:
        report.add(
            Issue(
                severity=SEV_WARN,
                code="OVERLAY_DIR_EMPTY",
                message="overlay directory has no files",
                api=api,
                file=str(overlay_dir),
            )
        )
        return
    for f in files:
        validate_file(f, api, report)


def validate_task_dir(task_mock_data_dir: Path, report: Report) -> None:
    if not task_mock_data_dir.is_dir():
        report.add(
            Issue(
                severity=SEV_ERROR,
                code="DIR_NOT_FOUND",
                message=f"mock_data dir does not exist: {task_mock_data_dir}",
            )
        )
        return
    api_dirs: list[Path] = []
    misnamed: list[Path] = []
    for sub in sorted(task_mock_data_dir.iterdir()):
        if not sub.is_dir():
            continue
        if _API_DIR_RE.match(sub.name):
            api_dirs.append(sub)
        else:
            misnamed.append(sub)
    for m in misnamed:
        report.add(
            Issue(
                severity=SEV_ERROR,
                code="DIR_NAMING",
                message=f"subdir '{m.name}' is not named like '<api>-api' and will be ignored at runtime",
                file=str(m),
                hint="rename to match the API folder name, e.g. gmail-api",
            )
        )
    if not api_dirs and not misnamed:
        report.add(
            Issue(
                severity=SEV_WARN,
                code="EMPTY_MOCK_DATA",
                message="mock_data/ has no api subdirs",
                file=str(task_mock_data_dir),
            )
        )
        return
    known = set(list_apis())
    for d in api_dirs:
        if d.name not in known:
            report.add(
                Issue(
                    severity=SEV_ERROR,
                    code="UNKNOWN_API",
                    message=f"api '{d.name}' has no examples folder — typo?",
                    api=d.name,
                    file=str(d),
                    hint="run with --list-apis to see valid api names",
                )
            )
            continue
        validate_overlay_dir(d, d.name, report)


def validate_input_root(input_root: Path, report: Report) -> None:
    if not input_root.is_dir():
        report.add(
            Issue(
                severity=SEV_ERROR,
                code="DIR_NOT_FOUND",
                message=f"input root does not exist: {input_root}",
            )
        )
        return
    found_any = False
    for task in sorted(input_root.iterdir()):
        if not task.is_dir():
            continue
        md = task / "mock_data"
        if md.is_dir():
            found_any = True
            validate_task_dir(md, report)
    if not found_any:
        report.add(
            Issue(
                severity=SEV_INFO,
                code="NO_TASKS",
                message=f"no task directories with mock_data/ found under {input_root}",
            )
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _classify_dir(path: Path) -> str:
    # Decision order matters: an api dir wins over its task ancestor because we
    # may be passed input/<task>/mock_data/gmail-api directly; a mock_data dir
    # wins over an input root because input/<task>/mock_data also has *-api
    # children but is conceptually one task, not many.
    if _API_DIR_RE.match(path.name):
        return "api"
    if path.name == "mock_data":
        return "task_mock_data"
    if (path / "mock_data").is_dir():
        return "task_root"
    has_api_child = any(
        c.is_dir() and _API_DIR_RE.match(c.name) for c in path.iterdir()
    )
    if has_api_child:
        return "task_mock_data"
    has_task_child = any(
        c.is_dir() and (c / "mock_data").is_dir() for c in path.iterdir()
    )
    if has_task_child:
        return "input_root"
    return "unknown"


def _dispatch_path(path: Path, forced_api: str | None, report: Report) -> None:
    if not path.exists():
        report.add(
            Issue(
                severity=SEV_ERROR,
                code="PATH_NOT_FOUND",
                message=f"path does not exist: {path}",
            )
        )
        return
    if path.is_file():
        api = forced_api or _infer_api_from_path(path)
        if not api:
            report.add(
                Issue(
                    severity=SEV_ERROR,
                    code="API_UNDETECTABLE",
                    message=(
                        f"cannot infer api for file '{path}' \u2014 pass --api or put the "
                        "file inside a '<name>-api' parent directory"
                    ),
                )
            )
            return
        validate_file(path, api, report)
        return
    kind = _classify_dir(path)
    if kind == "api":
        api = forced_api or path.name
        validate_overlay_dir(path, api, report)
    elif kind == "task_root":
        validate_task_dir(path / "mock_data", report)
    elif kind == "task_mock_data":
        validate_task_dir(path, report)
    elif kind == "input_root":
        validate_input_root(path, report)
    else:
        report.add(
            Issue(
                severity=SEV_ERROR,
                code="API_UNDETECTABLE",
                message=(
                    f"cannot determine what '{path}' is \u2014 expected an overlay file, a "
                    "'<api>-api' dir, a task folder containing mock_data/, or an input root"
                ),
                hint="pass --api, --task, or --input to force the mode",
            )
        )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="validate",
        description=(
            "Validate mock-data overlay files against the canonical examples in "
            "mock_overlay_validator/examples/."
        ),
    )
    p.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help=(
            "One or more paths. Each path is auto-classified: an overlay file is "
            "validated directly; a *-api dir is validated as that API; a task "
            "folder (containing mock_data/) validates the whole task; a folder "
            "containing many task subdirs (with mock_data/) validates them all. "
            "Use --api to force an api name; --task or --input to force a mode."
        ),
    )
    p.add_argument(
        "--api",
        help=(
            "Force a specific API name (e.g. 'gmail-api') when validating loose "
            "files that aren't inside a *-api folder."
        ),
    )
    p.add_argument(
        "--task",
        type=Path,
        help="Path to a task's mock_data/ directory; validates every overlay it contains.",
    )
    p.add_argument(
        "--input",
        type=Path,
        help="Path to an input/ root; validates every task's mock_data/ inside.",
    )
    p.add_argument(
        "--list-apis",
        action="store_true",
        help="Print every API name with an examples folder and exit.",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable JSON report on stdout instead of human text.",
    )
    p.add_argument(
        "--exit-on-warning",
        action="store_true",
        help="Exit non-zero even if only warnings were emitted.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_apis:
        for a in list_apis():
            print(a)
        return 0

    report = Report()

    if args.input:
        validate_input_root(args.input.resolve(), report)
    if args.task:
        validate_task_dir(args.task.resolve(), report)
    for path in args.paths:
        _dispatch_path(path.resolve(), args.api, report)

    if not args.paths and not args.task and not args.input:
        _build_parser().print_help(sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.format_human())

    if report.errors:
        return 1
    if args.exit_on_warning and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
