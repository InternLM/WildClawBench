"""Data access module for the Open Library API mock service.

Mirrors a subset of openlibrary.org: search, works, editions, authors and
subjects, using Open Library style keys (/works/OL...W, /authors/OL...A).
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_int)

_store = get_store("openlibrary-api")
_API = "openlibrary-api"

_store.register("authors", primary_key="author_id",
                initial_loader=lambda: _coerce_authors(_load("authors.json", "authors")))
_store.register("works", primary_key="work_id",
                initial_loader=lambda: _coerce_works(_load("works.json", "works")))
_store.register("editions", primary_key="edition_id",
                initial_loader=lambda: _coerce_editions(_load("editions.json", "editions")))
_store.register("subjects", primary_key="subject",
                initial_loader=lambda: _coerce_subjects(_load("subjects.json", "subjects")))


def _authors_rows():
    return _store.table("authors").rows()


def _works_rows():
    return _store.table("works").rows()


def _editions_rows():
    return _store.table("editions").rows()


def _subjects_rows():
    return _store.table("subjects").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _split(s):
    return [x.strip() for x in (s or "").split(";") if x.strip()]


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_authors(rows):
    out = []
    for r in rows:
        out.append({
            "author_id": r["author_id"],
            "name": r["name"],
            "birth_date": opt_str(r, "birth_date", default="") or None,
            "death_date": opt_str(r, "death_date", default="") or None,
            "bio": r["bio"],
            "top_work": r["top_work"],
            "work_count": strict_int(r, "work_count"),
        })
    return out


def _coerce_works(rows):
    out = []
    for r in rows:
        out.append({
            "work_id": r["work_id"],
            "title": r["title"],
            "author_id": r["author_id"],
            "first_publish_year": strict_int(r, "first_publish_year"),
            "subjects": _split(r["subjects"]),
            "description": r["description"],
            "edition_count": strict_int(r, "edition_count"),
        })
    return out


def _coerce_editions(rows):
    out = []
    for r in rows:
        out.append({
            "edition_id": r["edition_id"],
            "work_id": r["work_id"],
            "title": r["title"],
            "isbn_13": r["isbn_13"],
            "isbn_10": r["isbn_10"],
            "publisher": r["publisher"],
            "publish_date": r["publish_date"],
            "number_of_pages": strict_int(r, "number_of_pages"),
            "language": r["language"],
        })
    return out


def _coerce_subjects(rows):
    return [_strip_ctx(r) for r in rows]










_authors_by_id = {a["author_id"]: a for a in _authors_rows()}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _author_name(author_id):
    a = _authors_by_id.get(author_id)
    return a["name"] if a else "Unknown"


def _work_doc(w):
    return {
        "key": f"/works/{w['work_id']}",
        "type": "work",
        "title": w["title"],
        "first_publish_year": w["first_publish_year"],
        "author_key": [w["author_id"]],
        "author_name": [_author_name(w["author_id"])],
        "subject": w["subjects"],
        "edition_count": w["edition_count"],
    }


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(q=None, author=None, title=None, page=1, limit=20):
    matches = list(_works_rows())
    if title:
        t = title.lower()
        matches = [w for w in matches if t in w["title"].lower()]
    if author:
        a = author.lower()
        matches = [w for w in matches if a in _author_name(w["author_id"]).lower()]
    if q:
        ql = q.lower()
        matches = [
            w for w in matches
            if ql in w["title"].lower()
            or ql in _author_name(w["author_id"]).lower()
            or any(ql in s.lower() for s in w["subjects"])
        ]
    matches.sort(key=lambda w: w["edition_count"], reverse=True)

    page = max(1, int(page or 1))
    limit = max(1, min(int(limit or 20), 100))
    start = (page - 1) * limit
    docs = [_work_doc(w) for w in matches[start:start + limit]]
    return {
        "numFound": len(matches),
        "start": start,
        "numFoundExact": True,
        "docs": docs,
    }


# ---------------------------------------------------------------------------
# Works
# ---------------------------------------------------------------------------

def _find_work(work_id):
    return next((w for w in _works_rows() if w["work_id"] == work_id), None)


def get_work(work_id):
    w = _find_work(work_id)
    if not w:
        return {"error": f"Work {work_id} not found"}
    return {
        "key": f"/works/{w['work_id']}",
        "title": w["title"],
        "description": w["description"],
        "first_publish_date": str(w["first_publish_year"]),
        "subjects": w["subjects"],
        "authors": [
            {"author": {"key": f"/authors/{w['author_id']}"}, "type": {"key": "/type/author_role"}}
        ],
        "type": {"key": "/type/work"},
    }


def get_work_editions(work_id):
    w = _find_work(work_id)
    if not w:
        return {"error": f"Work {work_id} not found"}
    eds = [e for e in _editions_rows() if e["work_id"] == work_id]
    entries = [_edition_doc(e) for e in eds]
    return {
        "links": {"work": f"/works/{work_id}"},
        "size": len(entries),
        "entries": entries,
    }


# ---------------------------------------------------------------------------
# Editions / ISBN
# ---------------------------------------------------------------------------

def _edition_doc(e):
    return {
        "key": f"/books/{e['edition_id']}",
        "title": e["title"],
        "works": [{"key": f"/works/{e['work_id']}"}],
        "isbn_13": [e["isbn_13"]],
        "isbn_10": [e["isbn_10"]],
        "publishers": [e["publisher"]],
        "publish_date": e["publish_date"],
        "number_of_pages": e["number_of_pages"],
        "languages": [{"key": f"/languages/{e['language']}"}],
        "type": {"key": "/type/edition"},
    }


def get_isbn(isbn):
    isbn = (isbn or "").replace("-", "")
    e = next((x for x in _editions_rows() if x["isbn_13"] == isbn or x["isbn_10"] == isbn), None)
    if not e:
        return {"error": f"No edition found for ISBN {isbn}"}
    return _edition_doc(e)


# ---------------------------------------------------------------------------
# Authors
# ---------------------------------------------------------------------------

def get_author(author_id):
    a = _authors_by_id.get(author_id)
    if not a:
        return {"error": f"Author {author_id} not found"}
    return {
        "key": f"/authors/{a['author_id']}",
        "name": a["name"],
        "birth_date": a["birth_date"],
        "death_date": a["death_date"],
        "bio": a["bio"],
        "top_work": a["top_work"],
        "work_count": a["work_count"],
        "type": {"key": "/type/author"},
    }


def get_author_works(author_id):
    if author_id not in _authors_by_id:
        return {"error": f"Author {author_id} not found"}
    works = [w for w in _works_rows() if w["author_id"] == author_id]
    entries = []
    for w in works:
        entries.append({
            "key": f"/works/{w['work_id']}",
            "title": w["title"],
            "first_publish_date": str(w["first_publish_year"]),
            "subjects": w["subjects"],
            "type": {"key": "/type/work"},
        })
    return {"size": len(entries), "entries": entries}


# ---------------------------------------------------------------------------
# Subjects
# ---------------------------------------------------------------------------

def get_subject(subject):
    key = (subject or "").lower().replace(" ", "_")
    meta = next((s for s in _subjects_rows() if s["subject"] == key), None)
    name = meta["name"] if meta else subject.replace("_", " ").title()
    works = [w for w in _works_rows() if key in [s.replace(" ", "_") for s in w["subjects"]]]
    works.sort(key=lambda w: w["edition_count"], reverse=True)
    return {
        "key": f"/subjects/{key}",
        "name": name,
        "subject_type": "subject",
        "work_count": len(works),
        "works": [
            {
                "key": f"/works/{w['work_id']}",
                "title": w["title"],
                "authors": [{"key": f"/authors/{w['author_id']}", "name": _author_name(w["author_id"])}],
                "first_publish_year": w["first_publish_year"],
                "edition_count": w["edition_count"],
            }
            for w in works
        ],
    }

_store.eager_load()
