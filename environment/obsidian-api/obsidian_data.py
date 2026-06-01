"""Data access module for the Obsidian Local REST API mock service."""

import csv
import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _coerce_notes(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "size_bytes": int(r["size_bytes"]),
            "tags": [t.strip() for t in r["tags"].split(";") if t.strip()],
        })
    return out


def _coerce_contents(rows):
    out = {}
    for r in rows:
        # CSV escapes \n as literal backslash-n, restore real newlines
        out[r["path"]] = r["content"].replace("\\n", "\n")
    return out


_notes = _coerce_notes(_load("notes.csv"))
_contents = _coerce_contents(_load("note_contents.csv"))

with open(DATA_DIR / "vault.json", encoding="utf-8") as _f:
    _vault = json.load(_f)

_notes_store = deepcopy(_notes)
_contents_store = deepcopy(_contents)
_vault_store = deepcopy(_vault)


_WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def _index_of(path):
    for i, n in enumerate(_notes_store):
        if n["path"] == path:
            return i
    return -1


# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------

def get_vault():
    return _vault_store


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def list_notes(folder=None, tag=None):
    results = list(_notes_store)
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
    note = dict(_notes_store[idx])
    note["content"] = _contents_store.get(path, "")
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
    _notes_store.append(note)
    _contents_store[path] = content
    return {**note, "content": content}


def update_note(path, content=None, append=None):
    idx = _index_of(path)
    if idx < 0:
        return {"error": f"Note {path} not found"}
    if content is not None:
        _contents_store[path] = content
    elif append is not None:
        _contents_store[path] = _contents_store.get(path, "") + append
    else:
        return {"error": "Either content or append must be provided"}
    new_body = _contents_store[path]
    _notes_store[idx]["size_bytes"] = len(new_body.encode("utf-8"))
    _notes_store[idx]["modified_at"] = _now()
    _notes_store[idx]["tags"] = _extract_tags(new_body)
    return {**_notes_store[idx], "content": new_body}


def delete_note(path):
    idx = _index_of(path)
    if idx < 0:
        return {"error": f"Note {path} not found"}
    _notes_store.pop(idx)
    _contents_store.pop(path, None)
    return {"deleted": True, "path": path}


def _extract_tags(content):
    return [m.group(1) for m in re.finditer(r"(?:^|\s)#([A-Za-z0-9_/-]+)", content)]


# ---------------------------------------------------------------------------
# Search / links / daily
# ---------------------------------------------------------------------------

def search(query, content=False):
    q = query.lower()
    results = []
    for n in _notes_store:
        body = _contents_store.get(n["path"], "")
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
    for n in _notes_store:
        if n["path"] == path:
            continue
        body = _contents_store.get(n["path"], "")
        for m in _WIKILINK.finditer(body):
            if m.group(1).strip() == target_title:
                backlinks.append({"path": n["path"], "title": n["title"]})
                break
    return {"path": path, "count": len(backlinks), "backlinks": backlinks}


def get_daily(date_str):
    path = f"Daily/{date_str}.md"
    return get_note(path)
