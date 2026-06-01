"""Data access module for the Trello API mock service."""

import csv
import secrets
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
    return [dict(r) for r in rows]


def _coerce_boards(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "closed": _to_bool(r["closed"]),
            "member_ids": [x for x in r["member_ids"].split(";") if x],
        })
    return out


def _coerce_lists(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "pos": _to_float(r["pos"]),
            "closed": _to_bool(r["closed"]),
        })
    return out


def _coerce_cards(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "pos": _to_float(r["pos"]),
            "closed": _to_bool(r["closed"]),
            "due": r["due"] or None,
            "member_ids": [x for x in r["member_ids"].split(";") if x],
            "labels": [x for x in r["labels"].split(";") if x],
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


_members = _coerce_members(_load("members.csv"))
_boards = _coerce_boards(_load("boards.csv"))
_lists = _coerce_lists(_load("lists.csv"))
_cards = _coerce_cards(_load("cards.csv"))
_checklists = _coerce_checklists(_load("checklists.csv"))

_members_store = deepcopy(_members)
_boards_store = deepcopy(_boards)
_lists_store = deepcopy(_lists)
_cards_store = deepcopy(_cards)
_checklists_store = deepcopy(_checklists)


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
    me = next((m for m in _members_store if m["id"] == _ME), _members_store[0])
    return me


def list_my_boards():
    boards = [b for b in _boards_store if _ME in b["member_ids"] and not b["closed"]]
    return [_serialize_board(b) for b in boards]


# ---------------------------------------------------------------------------
# Boards
# ---------------------------------------------------------------------------

def get_board(board_id):
    for b in _boards_store:
        if b["id"] == board_id:
            return _serialize_board(b)
    return {"error": "board not found", "message": f"Board {board_id} not found"}


def list_board_lists(board_id):
    if not any(b["id"] == board_id for b in _boards_store):
        return {"error": "board not found", "message": f"Board {board_id} not found"}
    lists = [l for l in _lists_store if l["id_board"] == board_id and not l["closed"]]
    lists = sorted(lists, key=lambda l: l["pos"])
    return [_serialize_list(l) for l in lists]


# ---------------------------------------------------------------------------
# Lists -> cards
# ---------------------------------------------------------------------------

def list_cards(list_id):
    if not any(l["id"] == list_id for l in _lists_store):
        return {"error": "list not found", "message": f"List {list_id} not found"}
    cards = [c for c in _cards_store if c["id_list"] == list_id and not c["closed"]]
    cards = sorted(cards, key=lambda c: c["pos"])
    return [_serialize_card(c) for c in cards]


# ---------------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------------

def get_card(card_id):
    for c in _cards_store:
        if c["id"] == card_id:
            return _serialize_card(c)
    return {"error": "card not found", "message": f"Card {card_id} not found"}


def create_card(id_list, name, desc="", due=None, member_ids=None):
    target = next((l for l in _lists_store if l["id"] == id_list), None)
    if not target:
        return {"error": "list not found", "message": f"List {id_list} not found"}
    siblings = [c for c in _cards_store if c["id_list"] == id_list and not c["closed"]]
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
    _cards_store.append(card)
    return _serialize_card(card)


def update_card(card_id, name=None, desc=None, id_list=None, due=None, closed=None, pos=None):
    for i, c in enumerate(_cards_store):
        if c["id"] == card_id:
            if name is not None:
                _cards_store[i]["name"] = name
            if desc is not None:
                _cards_store[i]["desc"] = desc
            if id_list is not None:
                target = next((l for l in _lists_store if l["id"] == id_list), None)
                if not target:
                    return {"error": "list not found", "message": f"List {id_list} not found"}
                _cards_store[i]["id_list"] = id_list
                _cards_store[i]["id_board"] = target["id_board"]
            if due is not None:
                _cards_store[i]["due"] = due or None
            if closed is not None:
                _cards_store[i]["closed"] = bool(closed)
            if pos is not None:
                _cards_store[i]["pos"] = float(pos)
            return _serialize_card(_cards_store[i])
    return {"error": "card not found", "message": f"Card {card_id} not found"}


def delete_card(card_id):
    for i, c in enumerate(_cards_store):
        if c["id"] == card_id:
            _cards_store.pop(i)
            _checklists_store[:] = [cl for cl in _checklists_store if cl["id_card"] != card_id]
            return {"_value": None, "deleted": True, "id": card_id}
    return {"error": "card not found", "message": f"Card {card_id} not found"}


# ---------------------------------------------------------------------------
# Checklists
# ---------------------------------------------------------------------------

def list_card_checklists(card_id):
    if not any(c["id"] == card_id for c in _cards_store):
        return {"error": "card not found", "message": f"Card {card_id} not found"}
    return [_serialize_checklist(cl) for cl in _checklists_store if cl["id_card"] == card_id]


def create_checklist(id_card, name):
    card = next((c for c in _cards_store if c["id"] == id_card), None)
    if not card:
        return {"error": "card not found", "message": f"Card {id_card} not found"}
    checklist = {
        "id": _new_id(),
        "name": name or "Checklist",
        "id_card": id_card,
        "id_board": card["id_board"],
        "check_items": [],
    }
    _checklists_store.append(checklist)
    return _serialize_checklist(checklist)
