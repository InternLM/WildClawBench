"""Data access module for the Telegram Bot API mock service.

All public functions return the Telegram envelope: {"ok": true, "result": ...}
or {"ok": false, "error_code": int, "description": str} on failure.
"""

import csv
from copy import deepcopy
import json
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_int, opt_str, strict_bool, strict_int)

_store = get_store("telegram-api")
_API = "telegram-api"



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

_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("chats", primary_key="id",
                initial_loader=lambda: _coerce_chats(_load("chats.json", "chats")))
_store.register("messages", primary_key="message_id",
                initial_loader=lambda: _coerce_messages(_load("messages.json", "messages")))
_store.register("members", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['chat_id']}@{r['user_id']}"} for r in _coerce_members(_load("chat_members.json", "members"))])
_store.register_document("bot", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "bot.json", encoding="utf-8")))


def _users_rows():
    return _store.table("users").rows()


def _chats_rows():
    return _store.table("chats").rows()


def _messages_rows():
    return _store.table("messages").rows()


def _members_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("members").rows()]


def _bot_doc():
    return _store.document("bot").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "is_bot": strict_bool(r, "is_bot"),
            "first_name": r["first_name"],
            "last_name": opt_str(r, "last_name", default="") or None,
            "username": opt_str(r, "username", default="") or None,
            "language_code": opt_str(r, "language_code", default="") or None,
        })
    return out


def _coerce_chats(rows):
    out = []
    for r in rows:
        chat = {
            "id": strict_int(r, "id"),
            "type": r["type"],
        }
        if r["title"]:
            chat["title"] = r["title"]
        if r["username"]:
            chat["username"] = r["username"]
        if r["first_name"]:
            chat["first_name"] = r["first_name"]
        if r["last_name"]:
            chat["last_name"] = r["last_name"]
        if r["description"]:
            chat["description"] = r["description"]
        chat["member_count"] = strict_int(r, "member_count")
        out.append(chat)
    return out


def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            "message_id": strict_int(r, "message_id"),
            "chat_id": strict_int(r, "chat_id"),
            "from_id": strict_int(r, "from_id"),
            "text": r["text"],
            "date": strict_int(r, "date"),
            "reply_to_message_id": opt_int(r, "reply_to_message_id", default=None),
        })
    return out


def _coerce_members(rows):
    out = []
    for r in rows:
        out.append({
            "chat_id": strict_int(r, "chat_id"),
            "user_id": strict_int(r, "user_id"),
            "status": r["status"],
        })
    return out







# Monotonic message id counter for new messages.
_store.eager_load()
_next_message_id = max((m["message_id"] for m in _messages_rows()), default=0) + 1
# Update offset counter for getUpdates.
_next_update_id = 100001


def _ok(result):
    return {"ok": True, "result": result}


def _err(code, description):
    return {"ok": False, "error_code": code, "description": description}


def _find_user(user_id):
    return next((u for u in _users_rows() if u["id"] == int(user_id)), None)


def _find_chat(chat_id):
    return next((c for c in _chats_rows() if c["id"] == int(chat_id)), None)


def _from_user(user_id):
    u = _find_user(user_id)
    if u:
        return {k: u[k] for k in ("id", "is_bot", "first_name", "last_name", "username") if u.get(k) is not None}
    return {"id": int(user_id), "is_bot": False, "first_name": "Unknown"}


def _chat_stub(chat):
    return {k: v for k, v in chat.items() if k != "member_count"}


def _format_message(m):
    chat = _find_chat(m["chat_id"]) or {"id": m["chat_id"], "type": "private"}
    msg = {
        "message_id": m["message_id"],
        "from": _from_user(m["from_id"]),
        "chat": _chat_stub(chat),
        "date": m["date"],
        "text": m["text"],
    }
    if m.get("reply_to_message_id"):
        msg["reply_to_message_id"] = m["reply_to_message_id"]
    return msg


# ---------------------------------------------------------------------------
# Bot identity
# ---------------------------------------------------------------------------

def get_me():
    return _ok(_bot_doc())


# ---------------------------------------------------------------------------
# Sending / editing / deleting messages
# ---------------------------------------------------------------------------

def send_message(chat_id, text, reply_to_message_id=None):
    global _next_message_id
    if not _find_chat(chat_id):
        return _err(400, f"Bad Request: chat {chat_id} not found")
    msg = {
        "message_id": _next_message_id,
        "chat_id": int(chat_id),
        "from_id": _bot_doc()["id"],
        "text": text,
        "date": int(time.time()),
        "reply_to_message_id": int(reply_to_message_id) if reply_to_message_id else None,
    }
    _next_message_id += 1
    _store_insert("messages", msg)
    return _ok(_format_message(msg))


def send_photo(chat_id, photo, caption=None):
    global _next_message_id
    if not _find_chat(chat_id):
        return _err(400, f"Bad Request: chat {chat_id} not found")
    msg = {
        "message_id": _next_message_id,
        "chat_id": int(chat_id),
        "from_id": _bot_doc()["id"],
        "text": caption or "",
        "date": int(time.time()),
        "reply_to_message_id": None,
    }
    _next_message_id += 1
    _store_insert("messages", msg)
    formatted = _format_message(msg)
    formatted.pop("text", None)
    if caption:
        formatted["caption"] = caption
    formatted["photo"] = [{"file_id": photo, "width": 1280, "height": 720}]
    return _ok(formatted)


def edit_message_text(chat_id, message_id, text):
    for m in _messages_rows():
        if m["chat_id"] == int(chat_id) and m["message_id"] == int(message_id):
            _changes = {"text": text}
            m.update(_changes)
            _store_patch("messages", m, _changes)
            edited = _format_message(m)
            edited["edit_date"] = int(time.time())
            return _ok(edited)
    return _err(400, "Bad Request: message to edit not found")


def delete_message(chat_id, message_id):
    for m in _messages_rows():
        if m["chat_id"] == int(chat_id) and m["message_id"] == int(message_id):
            _store_delete("messages", m)
            return _ok(True)
    return _err(400, "Bad Request: message to delete not found")


# ---------------------------------------------------------------------------
# Chats / members / updates
# ---------------------------------------------------------------------------

def get_chat(chat_id):
    chat = _find_chat(chat_id)
    if not chat:
        return _err(400, f"Bad Request: chat {chat_id} not found")
    return _ok(deepcopy(chat))


def get_chat_member(chat_id, user_id):
    if not _find_chat(chat_id):
        return _err(400, f"Bad Request: chat {chat_id} not found")
    user = _find_user(user_id)
    if not user:
        return _err(400, f"Bad Request: user {user_id} not found")
    member = next((mb for mb in _members_rows()
                   if mb["chat_id"] == int(chat_id) and mb["user_id"] == int(user_id)), None)
    status = member["status"] if member else "left"
    return _ok({"user": _from_user(user_id), "status": status})


def get_updates(offset=None, limit=100):
    updates = []
    update_id = _next_update_id
    ordered = sorted(_messages_rows(), key=lambda m: (m["date"], m["message_id"]))
    for m in ordered:
        updates.append({
            "update_id": update_id,
            "message": _format_message(m),
        })
        update_id += 1
    if offset is not None:
        updates = [u for u in updates if u["update_id"] >= int(offset)]
    return _ok(updates[:limit])
