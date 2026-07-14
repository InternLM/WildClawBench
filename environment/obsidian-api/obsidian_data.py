"""Data access module for the Obsidian Local REST API mock service."""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (                       # noqa: E402
    read_seed_with_ctx, get_store, opt_csv_list, strict_int)

_store = get_store("obsidian-api")
_API = "obsidian-api"

_API = "obsidian-api"



def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

def _store_insert(_table, _row):
    """Persist a newly-created row into the shared store (drift/injection-safe).

    Synthesizes the table's registered primary key from the row's ``id`` field
    when the row doesn't already carry it, so creates work regardless of whether
    the table was registered with primary_key="id" or a domain-specific key.
    """
    _t = _store.table(_table)
    if _t.primary_key not in _row and "id" in _row:
        _row = {**_row, _t.primary_key: _row["id"]}
    return _t.upsert(_row)

_store.register("notes", primary_key="path",
                initial_loader=lambda: _coerce_notes(_load("notes.json", "notes")))
_store.register_document("contents", initial_loader=lambda: _coerce_contents(_load("note_contents.json", "contents")))
_store.register_document("vault", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "vault.json", encoding="utf-8")))


def _notes_rows():
    return _store.table("notes").rows()


def _contents_doc():
    return _store.document("contents").get()


def _vault_doc():
    return _store.document("vault").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _coerce_notes(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "size_bytes": strict_int(r, "size_bytes"),
            "tags": [t.strip() for t in opt_csv_list(r, "tags", sep=";") if t.strip()],
        })
    return out


def _coerce_contents(rows):
    out = {}
    for r in rows:
        # CSV escapes \n as literal backslash-n, restore real newlines
        out[r["path"]] = r["content"].replace("\\n", "\n")
    return out





_WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def _index_of(path):
    for i, n in enumerate(_notes_rows()):
        if n["path"] == path:
            return i
    return -1


# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------

def get_vault():
    return _vault_doc()


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def list_notes(folder=None, tag=None):
    results = list(_notes_rows())
    if folder:
        prefix = folder.rstrip("/") + "/"
        results = [n for n in results if n["path"].startswith(prefix)]
    if tag:
        results = [n for n in results if tag.lower() in [t.lower() for t in n["tags"]]]
    results.sort(key=lambda n: n["modified_at"], reverse=True)
    return {"count": len(results), "results": results}


def get_note(path):
    idx = _index_of(path)
    if idx < 0:
        return {"error": f"Note {path} not found"}
    note = dict(_notes_rows()[idx])
    note["content"] = _contents_doc().get(path, "")
    return note


def create_note(path, content):
    if _index_of(path) >= 0:
        return {"error": f"Note {path} already exists"}
    title = Path(path).stem
    note = {
        "path": path,
        "title": title,
        "size_bytes": len(content.encode("utf-8")),
        "modified_at": _now(),
        "tags": _extract_tags(content),
    }
    _store_insert("notes", note)
    _store.document("contents").merge({path: content})
    return {**note, "content": content}


def update_note(path, content=None, append=None):
    idx = _index_of(path)
    if idx < 0:
        return {"error": f"Note {path} not found"}
    if content is not None:
        new_body = content
    elif append is not None:
        new_body = _contents_doc().get(path, "") + append
    else:
        return {"error": "Either content or append must be provided"}
    _store.document("contents").merge({path: new_body})
    note = _notes_rows()[idx]
    _changes = {
        "size_bytes": len(new_body.encode("utf-8")),
        "modified_at": _now(),
        "tags": _extract_tags(new_body),
    }
    note.update(_changes)
    _store_patch("notes", note, _changes)
    return {**note, "content": new_body}


def delete_note(path):
    idx = _index_of(path)
    if idx < 0:
        return {"error": f"Note {path} not found"}
    _store_delete("notes", _notes_rows()[idx])
    _contents = _store.document("contents")
    _cv = _contents.get()
    _cv.pop(path, None)
    _contents.set(_cv)
    return {"deleted": True, "path": path}


def _extract_tags(content):
    return [m.group(1) for m in re.finditer(r"(?:^|\s)#([A-Za-z0-9_/-]+)", content)]


# ---------------------------------------------------------------------------
# Search / links / daily
# ---------------------------------------------------------------------------

def search(query, content=False):
    q = query.lower()
    results = []
    for n in _notes_rows():
        body = _contents_doc().get(n["path"], "")
        title_hit = q in n["title"].lower()
        path_hit = q in n["path"].lower()
        body_hit = q in body.lower()
        if title_hit or path_hit or body_hit:
            entry = {**n, "match_in": []}
            if title_hit:
                entry["match_in"].append("title")
            if path_hit:
                entry["match_in"].append("path")
            if body_hit:
                entry["match_in"].append("body")
            if content and body_hit:
                # Return first matching line as a snippet
                for line in body.splitlines():
                    if q in line.lower():
                        entry["snippet"] = line.strip()
                        break
            results.append(entry)
    return {"count": len(results), "query": query, "results": results}


def list_backlinks(path):
    target_title = Path(path).stem
    backlinks = []
    for n in _notes_rows():
        if n["path"] == path:
            continue
        body = _contents_doc().get(n["path"], "")
        for m in _WIKILINK.finditer(body):
            if m.group(1).strip() == target_title:
                backlinks.append({"path": n["path"], "title": n["title"]})
                break
    return {"path": path, "count": len(backlinks), "backlinks": backlinks}


def get_daily(date_str):
    path = f"Daily/{date_str}.md"
    return get_note(path)

_store.eager_load()
