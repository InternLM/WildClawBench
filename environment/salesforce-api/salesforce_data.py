"""Data access module for the Salesforce REST API mock service.

Supports the four standard sObjects Account, Contact, Lead, Opportunity with
generic CRUD plus a simplified SOQL query parser. IDs use Salesforce-style
15/18-character identifiers. Mutations are held in process memory.
"""

import csv
import re
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import read_seed_with_ctx, get_store

_store = get_store("salesforce-api")
_API = "salesforce-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000+0000")


_NUMERIC_FIELDS = {
    "AnnualRevenue", "NumberOfEmployees", "Amount", "Probability",
}


def _coerce(rows, sobject):
    out = []
    for r in rows:
        rec = _strip_ctx(r)
        for k, v in list(rec.items()):
            if k in _NUMERIC_FIELDS and v not in (None, ""):
                try:
                    rec[k] = float(v) if "." in str(v) else int(v)
                except (TypeError, ValueError):
                    pass
            elif v == "":
                rec[k] = None
        rec["attributes"] = {"type": sobject, "url": f"/services/data/v59.0/sobjects/{sobject}/{rec['Id']}"}
        out.append(rec)
    return out


_SOBJECT_CSV = {
    "Account": "accounts.json",
    "Contact": "contacts.json",
    "Lead": "leads.json",
    "Opportunity": "opportunities.json",
}

for _name, _csv in _SOBJECT_CSV.items():
    _store.register(
        _name,
        primary_key="Id",
        initial_loader=(lambda n=_name, c=_csv: _coerce(_load(c, n), n)),
    )


_ID_PREFIX = {
    "Account": "001",
    "Contact": "003",
    "Lead": "00Q",
    "Opportunity": "006",
}


def _canonical(sobject):
    if not sobject:
        return None
    for name in _SOBJECT_CSV:
        if name.lower() == sobject.lower():
            return name
    return None


def _new_id(sobject):
    prefix = _ID_PREFIX.get(sobject, "0XX")
    return f"{prefix}{uuid.uuid4().hex[:15].upper()}"[:18]


def _records(sobject):
    return _store.table(sobject).rows()


def _find(sobject, record_id):
    return _store.table(sobject).get(record_id)


def list_records(sobject, limit=200):
    name = _canonical(sobject)
    if not name:
        return {"error": f"sObject type '{sobject}' is not supported"}
    records = _records(name)[:limit]
    return {
        "totalSize": len(records),
        "done": True,
        "records": records,
    }


def get_record(sobject, record_id):
    name = _canonical(sobject)
    if not name:
        return {"error": f"sObject type '{sobject}' is not supported"}
    rec = _find(name, record_id)
    if not rec:
        return {"error": f"Provided external ID field does not exist or is not accessible: {record_id}"}
    return rec


def create_record(sobject, fields):
    name = _canonical(sobject)
    if not name:
        return {"error": f"sObject type '{sobject}' is not supported"}
    rec_id = _new_id(name)
    record = {"Id": rec_id}
    for k, v in (fields or {}).items():
        if k == "Id":
            continue
        record[k] = v
    record["attributes"] = {
        "type": name,
        "url": f"/services/data/v59.0/sobjects/{name}/{rec_id}",
    }
    record.setdefault("CreatedDate", _now())
    _store.table(name).upsert(record)
    return {"id": rec_id, "success": True, "errors": []}


def update_record(sobject, record_id, fields):
    name = _canonical(sobject)
    if not name:
        return {"error": f"sObject type '{sobject}' is not supported"}
    rec = _find(name, record_id)
    if not rec:
        return {"error": f"Provided external ID field does not exist or is not accessible: {record_id}"}
    patch = {}
    for k, v in (fields or {}).items():
        if k in ("Id", "attributes"):
            continue
        patch[k] = v
    patch["LastModifiedDate"] = _now()
    _store.table(name).patch(record_id, patch)
    return {"updated": True, "id": record_id}


_SOQL_RE = re.compile(
    r"^\s*SELECT\s+(?P<fields>.+?)\s+FROM\s+(?P<object>\w+)"
    r"(?:\s+WHERE\s+(?P<field>\w+)\s*=\s*'(?P<value>[^']*)')?\s*$",
    re.IGNORECASE | re.DOTALL,
)


def query(soql):
    if not soql:
        return {"error": "MALFORMED_QUERY: empty query string"}
    m = _SOQL_RE.match(soql.strip())
    if not m:
        return {"error": f"MALFORMED_QUERY: unable to parse '{soql}'"}
    name = _canonical(m.group("object"))
    if not name:
        return {"error": f"INVALID_TYPE: sObject type '{m.group('object')}' is not supported"}

    raw_fields = m.group("fields").strip()
    if raw_fields == "*" or raw_fields.upper() == "FIELDS(ALL)":
        fields = None
    else:
        fields = [f.strip() for f in raw_fields.split(",") if f.strip()]

    records = _records(name)
    where_field = m.group("field")
    where_value = m.group("value")
    if where_field:
        def _match(rec):
            actual = rec.get(where_field)
            return str(actual) == where_value
        records = [r for r in records if _match(r)]

    results = []
    for rec in records:
        if fields is None:
            results.append(rec)
        else:
            projected = {"attributes": rec["attributes"]}
            for f in fields:
                projected[f] = rec.get(f)
            results.append(projected)

    return {
        "totalSize": len(results),
        "done": True,
        "records": results,
    }

_store.eager_load()
