"""Data access module for the Algolia API mock service.

Models hosted-search objects: indices, records (objects with an ``objectID``),
and per-index settings. Query implements a case-insensitive substring match
across string fields and a simple ``attr:value`` equality filter syntax.
"""

import csv
import uuid
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _to_float(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _maybe_number(v):
    """Cast a CSV string to int/float when it looks numeric, else leave it."""
    if v is None or v == "":
        return v
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return v


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

_NUMERIC_FIELDS = {"price"}
_BOOL_FIELDS = {"in_stock"}


def _coerce_record(row):
    out = {}
    for k, v in row.items():
        if k in _BOOL_FIELDS:
            out[k] = _to_bool(v)
        elif k in _NUMERIC_FIELDS:
            out[k] = _maybe_number(v)
        else:
            out[k] = v
    return out


_indices_meta = [dict(r) for r in _load("indices.csv")]

_records_store = {}
for meta in _indices_meta:
    rows = _load(meta["records_csv"])
    _records_store[meta["name"]] = deepcopy([_coerce_record(r) for r in rows])

_indices_store = []
for meta in _indices_meta:
    _indices_store.append({
        "name": meta["name"],
        "entries": _to_int(meta["entries"]),
        "dataSize": _to_int(meta["data_size"]),
        "createdAt": meta["created_at"],
        "updatedAt": meta["updated_at"],
    })


def _coerce_settings(row):
    return {
        "searchableAttributes": [a.strip() for a in row["searchableAttributes"].split(",") if a.strip()],
        "attributesForFaceting": [a.strip() for a in row["attributesForFaceting"].split(",") if a.strip()],
        "hitsPerPage": _to_int(row["hitsPerPage"], 20),
        "ranking": [a.strip() for a in row["ranking"].split(",") if a.strip()],
    }


_settings_store = {r["index"]: _coerce_settings(r) for r in _load("settings.csv")}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_object_id():
    return uuid.uuid4().hex[:16]


def _index_exists(index):
    return index in _records_store


def _matches_query(record, query):
    if not query:
        return True
    q = query.lower()
    for v in record.values():
        if isinstance(v, str) and q in v.lower():
            return True
    return False


def _matches_filters(record, filters):
    """Support simple ``attr:value`` (optionally AND-joined) equality filters."""
    if not filters:
        return True
    clauses = [c.strip() for c in filters.replace(" AND ", "\n").split("\n") if c.strip()]
    for clause in clauses:
        if ":" not in clause:
            continue
        attr, _, value = clause.partition(":")
        attr = attr.strip()
        value = value.strip().strip('"')
        rv = record.get(attr)
        if rv is None:
            return False
        if str(rv).lower() != value.lower():
            return False
    return True


# ---------------------------------------------------------------------------
# Indices
# ---------------------------------------------------------------------------

def list_indexes():
    return {"items": deepcopy(_indices_store), "nbPages": 1}


def get_settings(index):
    if not _index_exists(index):
        return {"error": f"Index {index} not found"}
    return deepcopy(_settings_store.get(index, {
        "searchableAttributes": [],
        "attributesForFaceting": [],
        "hitsPerPage": 20,
        "ranking": [],
    }))


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def query_index(index, query=None, filters=None, hits_per_page=20, page=0):
    if not _index_exists(index):
        return {"error": f"Index {index} not found"}
    records = _records_store[index]
    hits = [r for r in records if _matches_query(r, query) and _matches_filters(r, filters)]
    nb_hits = len(hits)
    try:
        hits_per_page = max(1, int(hits_per_page))
    except (TypeError, ValueError):
        hits_per_page = 20
    try:
        page = max(0, int(page))
    except (TypeError, ValueError):
        page = 0
    nb_pages = (nb_hits + hits_per_page - 1) // hits_per_page if nb_hits else 0
    start = page * hits_per_page
    page_hits = [deepcopy(r) for r in hits[start: start + hits_per_page]]
    return {
        "hits": page_hits,
        "nbHits": nb_hits,
        "page": page,
        "nbPages": nb_pages,
        "hitsPerPage": hits_per_page,
        "query": query or "",
        "params": f"query={query or ''}&hitsPerPage={hits_per_page}&page={page}",
    }


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------

def get_object(index, object_id):
    if not _index_exists(index):
        return {"error": f"Index {index} not found"}
    for r in _records_store[index]:
        if r.get("objectID") == object_id:
            return deepcopy(r)
    return {"error": f"Object {object_id} not found in index {index}"}


def add_object(index, body):
    if not _index_exists(index):
        # Algolia auto-creates an index on first write.
        _records_store[index] = []
        _indices_store.append({
            "name": index, "entries": 0, "dataSize": 0,
            "createdAt": "", "updatedAt": "",
        })
    record = dict(body or {})
    object_id = record.get("objectID") or _new_object_id()
    record["objectID"] = object_id
    _records_store[index].append(record)
    return {"objectID": object_id, "createdAt": "", "taskID": _to_int(uuid.uuid4().int % 1000000)}


def update_object(index, object_id, body):
    if not _index_exists(index):
        return {"error": f"Index {index} not found"}
    for r in _records_store[index]:
        if r.get("objectID") == object_id:
            r.update(body or {})
            r["objectID"] = object_id
            return {"objectID": object_id, "updatedAt": "", "taskID": _to_int(uuid.uuid4().int % 1000000)}
    # PUT semantics: create if missing.
    record = dict(body or {})
    record["objectID"] = object_id
    _records_store[index].append(record)
    return {"objectID": object_id, "updatedAt": "", "taskID": _to_int(uuid.uuid4().int % 1000000)}


def delete_object(index, object_id):
    if not _index_exists(index):
        return {"error": f"Index {index} not found"}
    bucket = _records_store[index]
    for i, r in enumerate(bucket):
        if r.get("objectID") == object_id:
            bucket.pop(i)
            return {"objectID": object_id, "deletedAt": "", "taskID": _to_int(uuid.uuid4().int % 1000000)}
    return {"error": f"Object {object_id} not found in index {index}"}
