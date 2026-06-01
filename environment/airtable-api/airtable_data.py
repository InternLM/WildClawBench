"""Data access module for the Airtable API mock service.

Records are modeled generically as {id, createdTime, fields:{...}} where each
non-id / non-createdTime CSV column becomes a field. Field value casting is
driven by the field type declared in fields.csv (number -> float, checkbox ->
bool); everything else stays a string.
"""

import csv
import re
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load metadata
# ---------------------------------------------------------------------------

_bases = [dict(r) for r in _load("bases.csv")]
_tables = [dict(r) for r in _load("tables.csv")]
_fields_rows = [dict(r) for r in _load("fields.csv")]

# table_id -> {field_name: type}
_field_types = {}
# table_id -> [ {id, name, type}, ... ]  (declared order)
_field_meta = {}
for r in _fields_rows:
    _field_types.setdefault(r["tableId"], {})[r["name"]] = r["type"]
    _field_meta.setdefault(r["tableId"], []).append({
        "id": r["id"], "name": r["name"], "type": r["type"],
    })


def _cast_field(table_id, name, value):
    ftype = _field_types.get(table_id, {}).get(name)
    if value == "" or value is None:
        return None if ftype in ("number",) else value
    if ftype == "number":
        try:
            f = float(value)
            return int(f) if f.is_integer() else f
        except (TypeError, ValueError):
            return value
    if ftype == "checkbox":
        return _to_bool(value)
    return value


def _coerce_records(table_id, rows):
    out = []
    for r in rows:
        fields = {}
        for k, v in r.items():
            if k in ("id", "createdTime"):
                continue
            cast = _cast_field(table_id, k, v)
            if cast is None:
                continue
            fields[k] = cast
        out.append({
            "id": r["id"],
            "createdTime": r["createdTime"],
            "fields": fields,
        })
    return out


# base_id+table_id -> list of records ; also index tables for name resolution
_records_store = {}
for t in _tables:
    rows = _load(t["records_csv"])
    _records_store[t["id"]] = deepcopy(_coerce_records(t["id"], rows))

_bases_store = deepcopy(_bases)
_tables_store = deepcopy(_tables)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_record_id():
    return "rec" + uuid.uuid4().hex[:14]


def _resolve_table(base_id, table_id_or_name):
    for t in _tables_store:
        if t["baseId"] != base_id:
            continue
        if t["id"] == table_id_or_name or t["name"].lower() == str(table_id_or_name).lower():
            return t
    return None


# Very small filterByFormula support: {Field}='Value' (also "=" with double quotes)
_FORMULA_RE = re.compile(r"^\{(?P<field>[^}]+)\}\s*=\s*(['\"])(?P<value>.*)\2$")


def _apply_formula(records, formula):
    if not formula:
        return records
    m = _FORMULA_RE.match(formula.strip())
    if not m:
        return records
    field = m.group("field")
    value = m.group("value")
    out = []
    for rec in records:
        fv = rec["fields"].get(field)
        if fv is None:
            continue
        if str(fv) == value:
            out.append(rec)
    return out


# ---------------------------------------------------------------------------
# Meta
# ---------------------------------------------------------------------------

def list_bases():
    return {"bases": [{
        "id": b["id"], "name": b["name"], "permissionLevel": b["permissionLevel"],
    } for b in _bases_store]}


def list_tables(base_id):
    if not any(b["id"] == base_id for b in _bases_store):
        return {"error": f"Base {base_id} not found"}
    tables = []
    for t in _tables_store:
        if t["baseId"] != base_id:
            continue
        tables.append({
            "id": t["id"],
            "name": t["name"],
            "primaryFieldId": t["primaryFieldId"],
            "fields": _field_meta.get(t["id"], []),
        })
    return {"tables": tables}


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------

def list_records(base_id, table_id_or_name, page_size=100, offset=None, filter_by_formula=None):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    records = list(_records_store[table["id"]])
    records = _apply_formula(records, filter_by_formula)

    page_size = max(1, min(int(page_size), 100))
    try:
        start = int(offset) if offset is not None else 0
    except (TypeError, ValueError):
        start = 0
    page = records[start: start + page_size]
    resp = {"records": [deepcopy(r) for r in page]}
    next_offset = start + page_size
    if next_offset < len(records):
        resp["offset"] = str(next_offset)
    return resp


def get_record(base_id, table_id_or_name, record_id):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    for rec in _records_store[table["id"]]:
        if rec["id"] == record_id:
            return deepcopy(rec)
    return {"error": f"Record {record_id} not found"}


def create_records(base_id, table_id_or_name, records):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    created = []
    for item in records:
        fields = item.get("fields", {}) or {}
        rec = {
            "id": _new_record_id(),
            "createdTime": _now(),
            "fields": dict(fields),
        }
        _records_store[table["id"]].append(rec)
        created.append(deepcopy(rec))
    return {"records": created}


def update_record(base_id, table_id_or_name, record_id, fields):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    for rec in _records_store[table["id"]]:
        if rec["id"] == record_id:
            rec["fields"].update(fields or {})
            return deepcopy(rec)
    return {"error": f"Record {record_id} not found"}


def delete_record(base_id, table_id_or_name, record_id):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    bucket = _records_store[table["id"]]
    for i, rec in enumerate(bucket):
        if rec["id"] == record_id:
            bucket.pop(i)
            return {"id": record_id, "deleted": True}
    return {"error": f"Record {record_id} not found"}
