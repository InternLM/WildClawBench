"""Data module for the Google Docs API (Mock) mock service.

Schema-agnostic: rows are served as generic dicts with no column-specific
coercion, so a task's overlaid CSV (any columns) loads cleanly under the admin
plane's baseline capture. A synthetic primary key is generated when the source
row lacks one.
"""

import uuid
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import get_store, read_seed_with_ctx  # noqa: E402

_store = get_store("google-docs-api")
_API = "google-docs-api"


def _load(filename, table):
    # Optional seed: keep returning [] when neither the .csv nor a sibling
    # .json exists (read_seed_with_ctx raises CoerceError for a missing file,
    # which would break these born-optional tables).
    p = DATA_DIR / filename
    if not p.is_file() and not p.with_suffix(".json").is_file():
        return []
    rows = read_seed_with_ctx(p, _API, table)
    return [{k: v for k, v in r.items() if not k.startswith("__")} for r in rows]


def _ensure_pk(rows, pk, synth=None):
    out = []
    for r in rows:
        r = dict(r)
        if not r.get(pk):
            r[pk] = synth(r) if synth else uuid.uuid4().hex[:12]
        out.append(r)
    return out


_store.register("documents", primary_key="id",
                initial_loader=lambda: _ensure_pk(_load("documents.csv", "documents"), "id"))

_PK = {"documents": "id"}

_TABLES = ["documents"]


def list_table(name):
    return _store.table(name).rows()


def get_row(name, pk_value):
    for r in _store.table(name).rows():
        if str(r.get(_PK[name])) == str(pk_value):
            return r
    return None


def create_row(name, body):
    r = dict(body)
    if not r.get(_PK[name]):
        r[_PK[name]] = uuid.uuid4().hex[:12]
    return _store.table(name).upsert(r)


def update_row(name, pk_value, patch):
    t = _store.table(name)
    for r in t.rows():
        if str(r.get(_PK[name])) == str(pk_value):
            fields = {k: v for k, v in patch.items()
                      if v is not None and k != _PK[name]}
            return t.patch(r[_PK[name]], fields) if fields else r
    return None
