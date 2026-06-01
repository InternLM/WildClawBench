"""Data access module for the monday.com API mock service.

The real monday.com API is GraphQL; this mock exposes a REST-shaped surface for
consistency with the other Kensei2 environments: workspaces, boards, groups,
columns, items, column values and users.
"""

import csv
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_workspaces(rows):
    return [dict(r) for r in rows]


def _coerce_boards(rows):
    return [dict(r) for r in rows]


def _coerce_groups(rows):
    out = []
    for r in rows:
        out.append({**r, "position": int(r["position"])})
    return out


def _coerce_columns(rows):
    out = []
    for r in rows:
        out.append({**r, "position": int(r["position"])})
    return out


def _coerce_items(rows):
    return [dict(r) for r in rows]


def _coerce_column_values(rows):
    out = []
    for r in rows:
        out.append({
            "item_id": r["item_id"],
            "column_id": r["column_id"],
            "text": r["text"],
            "value": r["value"] or None,
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({**r, "is_admin": _to_bool(r["is_admin"])})
    return out


_workspaces = _coerce_workspaces(_load("workspaces.csv"))
_boards = _coerce_boards(_load("boards.csv"))
_groups = _coerce_groups(_load("groups.csv"))
_columns = _coerce_columns(_load("columns.csv"))
_items = _coerce_items(_load("items.csv"))
_column_values = _coerce_column_values(_load("column_values.csv"))
_users = _coerce_users(_load("users.csv"))

_workspaces_store = deepcopy(_workspaces)
_boards_store = deepcopy(_boards)
_groups_store = deepcopy(_groups)
_columns_store = deepcopy(_columns)
_items_store = deepcopy(_items)
_column_values_store = deepcopy(_column_values)
_users_store = deepcopy(_users)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_board(board_id):
    return next((b for b in _boards_store if b["board_id"] == board_id), None)


def _find_item(item_id):
    return next((i for i in _items_store if i["item_id"] == item_id), None)


def _find_group(board_id, group_id):
    return next((g for g in _groups_store if g["board_id"] == board_id and g["group_id"] == group_id), None)


def _board_columns(board_id):
    cols = [c for c in _columns_store if c["board_id"] == board_id]
    return sorted(cols, key=lambda c: c["position"])


def _column_values_for(item_id):
    out = []
    for cv in _column_values_store:
        if cv["item_id"] == item_id:
            out.append({
                "id": cv["column_id"],
                "text": cv["text"],
                "value": cv["value"],
            })
    return out


def _item_view(item):
    return {
        "id": item["item_id"],
        "name": item["name"],
        "board_id": item["board_id"],
        "group": {"id": item["group_id"]},
        "created_at": item["created_at"],
        "column_values": _column_values_for(item["item_id"]),
    }


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------

def list_workspaces():
    return {
        "workspaces": [
            {"id": w["workspace_id"], "name": w["name"], "kind": w["kind"], "description": w["description"]}
            for w in _workspaces_store
        ]
    }


# ---------------------------------------------------------------------------
# Boards
# ---------------------------------------------------------------------------

def list_boards(workspace_id=None):
    boards = _boards_store
    if workspace_id:
        boards = [b for b in boards if b["workspace_id"] == workspace_id]
    return {
        "boards": [
            {
                "id": b["board_id"],
                "name": b["name"],
                "description": b["description"],
                "state": b["state"],
                "board_kind": b["board_kind"],
                "workspace_id": b["workspace_id"],
            }
            for b in boards
        ]
    }


def get_board(board_id):
    b = _find_board(board_id)
    if not b:
        return {"error": f"Board {board_id} not found"}
    groups = sorted(
        [g for g in _groups_store if g["board_id"] == board_id],
        key=lambda g: g["position"],
    )
    return {
        "id": b["board_id"],
        "name": b["name"],
        "description": b["description"],
        "state": b["state"],
        "board_kind": b["board_kind"],
        "workspace_id": b["workspace_id"],
        "groups": [
            {"id": g["group_id"], "title": g["title"], "color": g["color"], "position": g["position"]}
            for g in groups
        ],
        "columns": [
            {"id": c["column_id"], "title": c["title"], "type": c["type"], "position": c["position"]}
            for c in _board_columns(board_id)
        ],
    }


def get_board_items(board_id):
    if not _find_board(board_id):
        return {"error": f"Board {board_id} not found"}
    items = [i for i in _items_store if i["board_id"] == board_id]
    return {"items": [_item_view(i) for i in items]}


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

def list_items(board_id=None, group_id=None):
    items = _items_store
    if board_id:
        items = [i for i in items if i["board_id"] == board_id]
    if group_id:
        items = [i for i in items if i["group_id"] == group_id]
    return {"items": [_item_view(i) for i in items]}


def get_item(item_id):
    item = _find_item(item_id)
    if not item:
        return {"error": f"Item {item_id} not found"}
    return _item_view(item)


def create_item(board_id, name, group_id=None, column_values=None):
    b = _find_board(board_id)
    if not b:
        return {"error": f"Board {board_id} not found"}
    if group_id:
        if not _find_group(board_id, group_id):
            return {"error": f"Group {group_id} not found on board {board_id}"}
    else:
        board_groups = sorted(
            [g for g in _groups_store if g["board_id"] == board_id],
            key=lambda g: g["position"],
        )
        if not board_groups:
            return {"error": f"Board {board_id} has no groups"}
        group_id = board_groups[0]["group_id"]

    item = {
        "item_id": f"item-{uuid.uuid4().hex[:8]}",
        "board_id": board_id,
        "group_id": group_id,
        "name": name,
        "created_at": _now(),
    }
    _items_store.append(item)
    if column_values:
        for column_id, val in column_values.items():
            if isinstance(val, dict):
                text = val.get("text", "")
                value = val.get("value")
            else:
                text = str(val)
                value = None
            _column_values_store.append({
                "item_id": item["item_id"],
                "column_id": column_id,
                "text": text,
                "value": value,
            })
    return _item_view(item)


def update_item(item_id, column_id=None, text=None, value=None, group_id=None):
    item = _find_item(item_id)
    if not item:
        return {"error": f"Item {item_id} not found"}

    if group_id is not None:
        if not _find_group(item["board_id"], group_id):
            return {"error": f"Group {group_id} not found on board {item['board_id']}"}
        item["group_id"] = group_id

    if column_id is not None:
        existing = next(
            (cv for cv in _column_values_store if cv["item_id"] == item_id and cv["column_id"] == column_id),
            None,
        )
        if existing:
            if text is not None:
                existing["text"] = text
            if value is not None:
                existing["value"] = value
        else:
            _column_values_store.append({
                "item_id": item_id,
                "column_id": column_id,
                "text": text or "",
                "value": value,
            })
    return _item_view(item)


def delete_item(item_id):
    item = _find_item(item_id)
    if not item:
        return {"error": f"Item {item_id} not found"}
    _items_store.remove(item)
    global _column_values_store
    _column_values_store = [cv for cv in _column_values_store if cv["item_id"] != item_id]
    return {"id": item_id, "deleted": True}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def list_users():
    return {
        "users": [
            {
                "id": u["user_id"],
                "name": u["name"],
                "email": u["email"],
                "title": u["title"],
                "is_admin": u["is_admin"],
            }
            for u in _users_store
        ]
    }
