"""Data access module for the monday.com API mock service.

The real monday.com API is GraphQL; this mock exposes a REST-shaped surface for
consistency with the other Kensei2 environments: workspaces, boards, groups,
columns, items, column values and users.
"""

import csv
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_bool, strict_int)
_store = get_store("monday-api")
_API = "monday-api"


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _coerce_workspaces(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_boards(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_groups(rows):
    out = []
    for r in rows:
        out.append({**_strip_ctx(r), "position": strict_int(r, "position")})
    return out


def _coerce_columns(rows):
    out = []
    for r in rows:
        out.append({**_strip_ctx(r), "position": strict_int(r, "position")})
    return out


def _coerce_items(rows):
    return [_strip_ctx(r) for r in rows]


def _coerce_column_values(rows):
    out = []
    for r in rows:
        out.append({
            "item_id": r["item_id"],
            "column_id": r["column_id"],
            "text": r["text"],
            "value": opt_str(r, "value", default="") or None,
            # synthesized composite PK
            "_pk": f"{r['item_id']}@{r['column_id']}",
        })
    return out


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({**_strip_ctx(r), "is_admin": strict_bool(r, "is_admin")})
    return out


_store.register("workspaces", primary_key="workspace_id",
                initial_loader=lambda: _coerce_workspaces(_load("workspaces.json", "workspaces")))
_store.register("boards", primary_key="board_id",
                initial_loader=lambda: _coerce_boards(_load("boards.json", "boards")))
# groups have group_id but it is not unique across boards -> synth pk
_store.register("groups", primary_key="_pk",
                initial_loader=lambda: [
                    {**g, "_pk": f"{g['board_id']}@{g['group_id']}"}
                    for g in _coerce_groups(_load("groups.json", "groups"))
                ])
_store.register("columns", primary_key="_pk",
                initial_loader=lambda: [
                    {**c, "_pk": f"{c['board_id']}@{c['column_id']}"}
                    for c in _coerce_columns(_load("columns.json", "columns"))
                ])
_store.register("items", primary_key="item_id",
                initial_loader=lambda: _coerce_items(_load("items.json", "items")))
_store.register("column_values", primary_key="_pk",
                initial_loader=lambda: _coerce_column_values(_load("column_values.json", "column_values")))
_store.register("users", primary_key="user_id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))


def _workspaces_rows(): return _store.table("workspaces").rows()
def _boards_rows(): return _store.table("boards").rows()
def _groups_rows(): return _store.table("groups").rows()
def _columns_rows(): return _store.table("columns").rows()
def _items_rows(): return _store.table("items").rows()
def _column_values_rows(): return _store.table("column_values").rows()
def _users_rows(): return _store.table("users").rows()


def _find_board(board_id):
    return next((b for b in _boards_rows() if b["board_id"] == board_id), None)


def _find_item(item_id):
    return next((i for i in _items_rows() if i["item_id"] == item_id), None)


def _find_group(board_id, group_id):
    return next((g for g in _groups_rows() if g["board_id"] == board_id and g["group_id"] == group_id), None)


def _board_columns(board_id):
    cols = [c for c in _columns_rows() if c["board_id"] == board_id]
    return sorted(cols, key=lambda c: c["position"])


def _column_values_for(item_id):
    out = []
    for cv in _column_values_rows():
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


def list_workspaces():
    return {
        "workspaces": [
            {"id": w["workspace_id"], "name": w["name"], "kind": w["kind"], "description": w["description"]}
            for w in _workspaces_rows()
        ]
    }


def list_boards(workspace_id=None):
    boards = _boards_rows()
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
        [g for g in _groups_rows() if g["board_id"] == board_id],
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
    items = [i for i in _items_rows() if i["board_id"] == board_id]
    return {"items": [_item_view(i) for i in items]}


def list_items(board_id=None, group_id=None):
    items = _items_rows()
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
            [g for g in _groups_rows() if g["board_id"] == board_id],
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
    _store.table("items").upsert(item)
    if column_values:
        for column_id, val in column_values.items():
            if isinstance(val, dict):
                text = val.get("text", "")
                value = val.get("value")
            else:
                text = str(val)
                value = None
            _store.table("column_values").upsert({
                "_pk": f"{item['item_id']}@{column_id}",
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
        _store.table("items").patch(item_id, {"group_id": group_id})
        item = _find_item(item_id) or item

    if column_id is not None:
        pk = f"{item_id}@{column_id}"
        existing = _store.table("column_values").get(pk)
        if existing:
            patch = {}
            if text is not None:
                patch["text"] = text
            if value is not None:
                patch["value"] = value
            if patch:
                _store.table("column_values").patch(pk, patch)
        else:
            _store.table("column_values").upsert({
                "_pk": pk,
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
    _store.table("items").delete(item_id)
    _store.table("column_values").delete_where(lambda cv: cv["item_id"] == item_id)
    return {"id": item_id, "deleted": True}


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
            for u in _users_rows()
        ]
    }

_store.eager_load()
