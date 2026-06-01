"""Data access module for the Salesforce REST API mock service.

Supports the four standard sObjects Account, Contact, Lead, Opportunity with
generic CRUD plus a simplified SOQL query parser. IDs use Salesforce-style
15/18-character identifiers. Mutations are held in process memory.
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
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000+0000")


_NUMERIC_FIELDS = {
    "AnnualRevenue", "NumberOfEmployees", "Amount", "Probability",
}


def _coerce(rows, sobject):
    out = []
    for r in rows:
        rec = dict(r)
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


# Object registry: sObject name -> in-memory list of records
_stores = {
    "Account": deepcopy(_coerce(_load("accounts.csv"), "Account")),
    "Contact": deepcopy(_coerce(_load("contacts.csv"), "Contact")),
    "Lead": deepcopy(_coerce(_load("leads.csv"), "Lead")),
    "Opportunity": deepcopy(_coerce(_load("opportunities.csv"), "Opportunity")),
}

# Salesforce ID key-prefix per object (first 3 chars of an Id)
_ID_PREFIX = {
    "Account": "001",
    "Contact": "003",
    "Lead": "00Q",
    "Opportunity": "006",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _canonical(sobject):
    if not sobject:
        return None
    for name in _stores:
        if name.lower() == sobject.lower():
            return name
    return None


def _new_id(sobject):
    prefix = _ID_PREFIX.get(sobject, "0XX")
    return f"{prefix}{uuid.uuid4().hex[:15].upper()}"[:18]


def _find(sobject, record_id):
    return next((r for r in _stores[sobject] if r["Id"] == record_id), None)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def list_records(sobject, limit=200):
    name = _canonical(sobject)
    if not name:
        return {"error": f"sObject type '{sobject}' is not supported"}
    records = _stores[name][:limit]
    return {
        "totalSize": len(records),
        "done": True,
        "records": [deepcopy(r) for r in records],
    }


def get_record(sobject, record_id):
    name = _canonical(sobject)
    if not name:
        return {"error": f"sObject type '{sobject}' is not supported"}
    rec = _find(name, record_id)
    if not rec:
        return {"error": f"Provided external ID field does not exist or is not accessible: {record_id}"}
    return deepcopy(rec)


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
    _stores[name].append(record)
    return {"id": rec_id, "success": True, "errors": []}


def update_record(sobject, record_id, fields):
    name = _canonical(sobject)
    if not name:
        return {"error": f"sObject type '{sobject}' is not supported"}
    rec = _find(name, record_id)
    if not rec:
        return {"error": f"Provided external ID field does not exist or is not accessible: {record_id}"}
    for k, v in (fields or {}).items():
        if k in ("Id", "attributes"):
            continue
        rec[k] = v
    rec["LastModifiedDate"] = _now()
    return {"updated": True, "id": record_id}


# ---------------------------------------------------------------------------
# SOQL query
# ---------------------------------------------------------------------------

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

    records = _stores[name]
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
            results.append(deepcopy(rec))
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
