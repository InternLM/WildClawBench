"""Data access module for the Trello API mock service."""

import csv
import secrets
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (  # noqa: E402
    read_seed_with_ctx, get_store, opt_csv_list, opt_float, opt_str, strict_bool)

_store = get_store("trello-api")
_API = "trello-api"



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

_store.register("members", primary_key="id",
                initial_loader=lambda: _coerce_members(_load("members.json", "members")))
_store.register("boards", primary_key="id",
                initial_loader=lambda: _coerce_boards(_load("boards.json", "boards")))
_store.register("lists", primary_key="id",
                initial_loader=lambda: _coerce_lists(_load("lists.json", "lists")))
_store.register("cards", primary_key="id",
                initial_loader=lambda: _coerce_cards(_load("cards.json", "cards")))
_store.register("checklists", primary_key="id",
                initial_loader=lambda: _coerce_checklists(_load("checklists.json", "checklists")))


def _members_rows():
    return _store.table("members").rows()


def _boards_rows():
    return _store.table("boards").rows()


def _lists_rows():
    return _store.table("lists").rows()


def _cards_rows():
    return _store.table("cards").rows()


def _checklists_rows():
    return _store.table("checklists").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# The member whose token is used (the "me" of /members/me).
_ME = "5f1a000000000000000000a1"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_members(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_boards(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "closed": strict_bool(r, "closed"),
            "member_ids": [x for x in opt_csv_list(r, "member_ids", sep=";") if x],
        })
    return out


def _coerce_lists(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "pos": opt_float(r, "pos", default=None),
            "closed": strict_bool(r, "closed"),
        })
    return out


def _coerce_cards(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "pos": opt_float(r, "pos", default=None),
            "closed": strict_bool(r, "closed"),
            "due": opt_str(r, "due", default="") or None,
            "member_ids": [x for x in opt_csv_list(r, "member_ids", sep=";") if x],
            "labels": [x for x in opt_csv_list(r, "labels", sep=";") if x],
        })
    return out


def _coerce_checklists(rows):
    out = []
    for r in rows:
        items = []
        for n, raw in enumerate(r["items"].split(";")):
            if not raw:
                continue
            name, _, state = raw.partition(":")
            items.append({
                "id": f"ci{r['id'][-4:]}{n:02d}",
                "name": name,
                "state": state or "incomplete",
                "pos": (n + 1) * 16384,
            })
        out.append({
            "id": r["id"],
            "name": r["name"],
            "id_card": r["id_card"],
            "id_board": r["id_board"],
            "check_items": items,
        })
    return out












# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _new_id():
    return secrets.token_hex(12)


def _serialize_board(b):
    return {
        "id": b["id"],
        "name": b["name"],
        "desc": b["desc"],
        "closed": b["closed"],
        "idOrganization": b["id_organization"],
        "url": b["url"],
        "idMembers": b["member_ids"],
    }


def _serialize_list(l):
    return {
        "id": l["id"],
        "name": l["name"],
        "idBoard": l["id_board"],
        "pos": l["pos"],
        "closed": l["closed"],
    }


def _serialize_card(c):
    return {
        "id": c["id"],
        "name": c["name"],
        "desc": c["desc"],
        "idBoard": c["id_board"],
        "idList": c["id_list"],
        "pos": c["pos"],
        "due": c["due"],
        "closed": c["closed"],
        "idMembers": c["member_ids"],
        "labels": [{"name": n} for n in c["labels"]],
    }


def _serialize_checklist(cl):
    return {
        "id": cl["id"],
        "name": cl["name"],
        "idCard": cl["id_card"],
        "idBoard": cl["id_board"],
        "checkItems": cl["check_items"],
    }


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

def get_me():
    me = next((m for m in _members_rows() if m["id"] == _ME), _members_rows()[0])
    return me


def list_my_boards():
    boards = [b for b in _boards_rows() if _ME in b["member_ids"] and not b["closed"]]
    return [_serialize_board(b) for b in boards]


# ---------------------------------------------------------------------------
# Boards
# ---------------------------------------------------------------------------

def get_board(board_id):
    for b in _boards_rows():
        if b["id"] == board_id:
            return _serialize_board(b)
    return {"error": "board not found", "message": f"Board {board_id} not found"}


def list_board_lists(board_id):
    if not any(b["id"] == board_id for b in _boards_rows()):
        return {"error": "board not found", "message": f"Board {board_id} not found"}
    lists = [l for l in _lists_rows() if l["id_board"] == board_id and not l["closed"]]
    lists = sorted(lists, key=lambda l: l["pos"])
    return [_serialize_list(l) for l in lists]


# ---------------------------------------------------------------------------
# Lists -> cards
# ---------------------------------------------------------------------------

def list_cards(list_id):
    if not any(l["id"] == list_id for l in _lists_rows()):
        return {"error": "list not found", "message": f"List {list_id} not found"}
    cards = [c for c in _cards_rows() if c["id_list"] == list_id and not c["closed"]]
    cards = sorted(cards, key=lambda c: c["pos"])
    return [_serialize_card(c) for c in cards]


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

def get_card(card_id):
    for c in _cards_rows():
        if c["id"] == card_id:
            return _serialize_card(c)
    return {"error": "card not found", "message": f"Card {card_id} not found"}


def create_card(id_list, name, desc="", due=None, member_ids=None):
    target = next((l for l in _lists_rows() if l["id"] == id_list), None)
    if not target:
        return {"error": "list not found", "message": f"List {id_list} not found"}
    siblings = [c for c in _cards_rows() if c["id_list"] == id_list and not c["closed"]]
    next_pos = max((c["pos"] for c in siblings), default=0) + 16384
    card = {
        "id": _new_id(),
        "name": name,
        "desc": desc or "",
        "id_board": target["id_board"],
        "id_list": id_list,
        "pos": next_pos,
        "due": due,
        "closed": False,
        "member_ids": member_ids or [],
        "labels": [],
    }
    _store_insert("cards", card)
    return _serialize_card(card)


def update_card(card_id, name=None, desc=None, id_list=None, due=None, closed=None, pos=None):
    for c in _cards_rows():
        if c["id"] == card_id:
            _changes = {}
            if name is not None:
                _changes["name"] = name
            if desc is not None:
                _changes["desc"] = desc
            if id_list is not None:
                target = next((l for l in _lists_rows() if l["id"] == id_list), None)
                if not target:
                    return {"error": "list not found", "message": f"List {id_list} not found"}
                _changes["id_list"] = id_list
                _changes["id_board"] = target["id_board"]
            if due is not None:
                _changes["due"] = due or None
            if closed is not None:
                _changes["closed"] = bool(closed)
            if pos is not None:
                _changes["pos"] = float(pos)
            c.update(_changes)
            _store_patch("cards", c, _changes)
            return _serialize_card(c)
    return {"error": "card not found", "message": f"Card {card_id} not found"}


def delete_card(card_id):
    for c in _cards_rows():
        if c["id"] == card_id:
            _store_delete("cards", c)
            for cl in [cl for cl in _checklists_rows() if cl["id_card"] == card_id]:
                _store_delete("checklists", cl)
            return {"_value": None, "deleted": True, "id": card_id}
    return {"error": "card not found", "message": f"Card {card_id} not found"}


# ---------------------------------------------------------------------------
# Checklists
# ---------------------------------------------------------------------------

def list_card_checklists(card_id):
    if not any(c["id"] == card_id for c in _cards_rows()):
        return {"error": "card not found", "message": f"Card {card_id} not found"}
    return [_serialize_checklist(cl) for cl in _checklists_rows() if cl["id_card"] == card_id]


def create_checklist(id_card, name):
    card = next((c for c in _cards_rows() if c["id"] == id_card), None)
    if not card:
        return {"error": "card not found", "message": f"Card {id_card} not found"}
    checklist = {
        "id": _new_id(),
        "name": name or "Checklist",
        "id_card": id_card,
        "id_board": card["id_board"],
        "check_items": [],
    }
    _store_insert("checklists", checklist)
    return _serialize_checklist(checklist)

_store.eager_load()
