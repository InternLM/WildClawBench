"""Data access module for the Airtable API mock service.

Records are modeled generically as {id, createdTime, fields:{...}} where each
non-id / non-createdTime column becomes a field. Field value casting is
driven by the field type declared in fields.json (number -> float, checkbox ->
bool); everything else stays a string.
"""

import csv
import re
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store)

_store = get_store("airtable-api")
_API = "airtable-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _to_bool(v):
    return str(v).strip().lower() == "true"


_bases = [_strip_ctx(r) for r in _load("bases.json", "bases")]
_tables = [_strip_ctx(r) for r in _load("tables.json", "tables")]
_fields_rows = [_strip_ctx(r) for r in _load("fields.json", "fields")]

_field_types: dict[str, dict[str, str]] = {}
_field_meta: dict[str, list[dict]] = {}
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
        # Deliberately tolerant: Airtable schemas are user-defined at runtime,
        # so this path intentionally diverges from the fleet-wide strict_*/opt_*
        # guarantee (mirrors the number branch's try/except). Do not "harden".
        return _to_bool(value)
    return value


def _coerce_records(table_id, rows):
    out = []
    for r in rows:
        fields = {}
        for k, v in _strip_ctx(r).items():
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


_store.register("bases", primary_key="id",
                initial_loader=lambda: [dict(b) for b in _bases])
_store.register("tables", primary_key="id",
                initial_loader=lambda: [dict(t) for t in _tables])


def _records_table_name(table_id: str) -> str:
    return f"records_{table_id}"


# one mutable Table per airtable table_id, keyed by record id "recXXX"
for _t in _tables:
    _store.register(
        _records_table_name(_t["id"]),
        primary_key="id",
        initial_loader=(lambda tid=_t["id"], json_name=_t["records_csv"], tname=_records_table_name(_t["id"]):
                        _coerce_records(tid, _load(json_name, tname))),
    )


def _records(table_id):
    return _store.table(_records_table_name(table_id)).rows()


def _bases_rows(): return _store.table("bases").rows()
def _tables_rows(): return _store.table("tables").rows()


def _new_record_id():
    return "rec" + uuid.uuid4().hex[:14]


def _resolve_table(base_id, table_id_or_name):
    for t in _tables_rows():
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


def list_bases():
    return {"bases": [{
        "id": b["id"], "name": b["name"], "permissionLevel": b["permissionLevel"],
    } for b in _bases_rows()]}


def list_tables(base_id):
    if not _store.table("bases").get(base_id):
        return {"error": f"Base {base_id} not found"}
    tables = []
    for t in _tables_rows():
        if t["baseId"] != base_id:
            continue
        tables.append({
            "id": t["id"],
            "name": t["name"],
            "primaryFieldId": t["primaryFieldId"],
            "fields": _field_meta.get(t["id"], []),
        })
    return {"tables": tables}


def list_records(base_id, table_id_or_name, page_size=100, offset=None, filter_by_formula=None):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    records = _records(table["id"])
    records = _apply_formula(records, filter_by_formula)

    page_size = max(1, min(int(page_size), 100))
    try:
        start = int(offset) if offset is not None else 0
    except (TypeError, ValueError):
        start = 0
    page = records[start: start + page_size]
    resp = {"records": page}
    next_offset = start + page_size
    if next_offset < len(records):
        resp["offset"] = str(next_offset)
    return resp


def get_record(base_id, table_id_or_name, record_id):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    rec = _store.table(_records_table_name(table["id"])).get(record_id)
    if rec:
        return rec
    return {"error": f"Record {record_id} not found"}


def create_records(base_id, table_id_or_name, records):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    created = []
    tbl = _store.table(_records_table_name(table["id"]))
    for item in records:
        fields = item.get("fields", {}) or {}
        rec = {
            "id": _new_record_id(),
            "createdTime": _now(),
            "fields": dict(fields),
        }
        tbl.upsert(rec)
        created.append(rec)
    return {"records": created}


def update_record(base_id, table_id_or_name, record_id, fields):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    tbl = _store.table(_records_table_name(table["id"]))
    rec = tbl.get(record_id)
    if not rec:
        return {"error": f"Record {record_id} not found"}
    merged = {**rec["fields"], **(fields or {})}
    tbl.patch(record_id, {"fields": merged})
    return tbl.get(record_id) or rec


def delete_record(base_id, table_id_or_name, record_id):
    table = _resolve_table(base_id, table_id_or_name)
    if not table:
        return {"error": f"Table {table_id_or_name} not found in base {base_id}"}
    tbl = _store.table(_records_table_name(table["id"]))
    if tbl.delete(record_id):
        return {"id": record_id, "deleted": True}
    return {"error": f"Record {record_id} not found"}

_store.eager_load()
