"""Data access module for the Telegram Bot API mock service.

All public functions return the Telegram envelope: {"ok": true, "result": ...}
or {"ok": false, "error_code": int, "description": str} on failure.
"""

import csv
import json
import time
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "is_bot": _to_bool(r["is_bot"]),
            "first_name": r["first_name"],
            "last_name": r["last_name"] or None,
            "username": r["username"] or None,
            "language_code": r["language_code"] or None,
        })
    return out


def _coerce_chats(rows):
    out = []
    for r in rows:
        chat = {
            "id": int(r["id"]),
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
        chat["member_count"] = int(r["member_count"])
        out.append(chat)
    return out


def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            "message_id": int(r["message_id"]),
            "chat_id": int(r["chat_id"]),
            "from_id": int(r["from_id"]),
            "text": r["text"],
            "date": int(r["date"]),
            "reply_to_message_id": int(r["reply_to_message_id"]) if r["reply_to_message_id"] else None,
        })
    return out


def _coerce_members(rows):
    out = []
    for r in rows:
        out.append({
            "chat_id": int(r["chat_id"]),
            "user_id": int(r["user_id"]),
            "status": r["status"],
        })
    return out


_users = _coerce_users(_load("users.csv"))
_chats = _coerce_chats(_load("chats.csv"))
_messages = _coerce_messages(_load("messages.csv"))
_members = _coerce_members(_load("chat_members.csv"))

with open(DATA_DIR / "bot.json", encoding="utf-8") as _f:
    _bot = json.load(_f)

_users_store = deepcopy(_users)
_chats_store = deepcopy(_chats)
_messages_store = deepcopy(_messages)
_members_store = deepcopy(_members)
_bot_store = deepcopy(_bot)

# Monotonic message id counter for new messages.
_next_message_id = max((m["message_id"] for m in _messages_store), default=0) + 1
# Update offset counter for getUpdates.
_next_update_id = 100001


def _ok(result):
    return {"ok": True, "result": result}


def _err(code, description):
    return {"ok": False, "error_code": code, "description": description}


def _find_user(user_id):
    return next((u for u in _users_store if u["id"] == int(user_id)), None)


def _find_chat(chat_id):
    return next((c for c in _chats_store if c["id"] == int(chat_id)), None)


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
    return _ok(_bot_store)


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
        "from_id": _bot_store["id"],
        "text": text,
        "date": int(time.time()),
        "reply_to_message_id": int(reply_to_message_id) if reply_to_message_id else None,
    }
    _next_message_id += 1
    _messages_store.append(msg)
    return _ok(_format_message(msg))


def send_photo(chat_id, photo, caption=None):
    global _next_message_id
    if not _find_chat(chat_id):
        return _err(400, f"Bad Request: chat {chat_id} not found")
    msg = {
        "message_id": _next_message_id,
        "chat_id": int(chat_id),
        "from_id": _bot_store["id"],
        "text": caption or "",
        "date": int(time.time()),
        "reply_to_message_id": None,
    }
    _next_message_id += 1
    _messages_store.append(msg)
    formatted = _format_message(msg)
    formatted.pop("text", None)
    if caption:
        formatted["caption"] = caption
    formatted["photo"] = [{"file_id": photo, "width": 1280, "height": 720}]
    return _ok(formatted)


def edit_message_text(chat_id, message_id, text):
    for m in _messages_store:
        if m["chat_id"] == int(chat_id) and m["message_id"] == int(message_id):
            m["text"] = text
            edited = _format_message(m)
            edited["edit_date"] = int(time.time())
            return _ok(edited)
    return _err(400, "Bad Request: message to edit not found")


def delete_message(chat_id, message_id):
    for i, m in enumerate(_messages_store):
        if m["chat_id"] == int(chat_id) and m["message_id"] == int(message_id):
            _messages_store.pop(i)
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
    member = next((mb for mb in _members_store
                   if mb["chat_id"] == int(chat_id) and mb["user_id"] == int(user_id)), None)
    status = member["status"] if member else "left"
    return _ok({"user": _from_user(user_id), "status": status})


def get_updates(offset=None, limit=100):
    updates = []
    update_id = _next_update_id
    ordered = sorted(_messages_store, key=lambda m: (m["date"], m["message_id"]))
    for m in ordered:
        updates.append({
            "update_id": update_id,
            "message": _format_message(m),
        })
        update_id += 1
    if offset is not None:
        updates = [u for u in updates if u["update_id"] >= int(offset)]
    return _ok(updates[:limit])
