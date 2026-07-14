"""Data access module for the Slack API mock service.

Mirrors a subset of Slack's Web API method-style endpoints (e.g. conversations.list).
"""

import csv
import json
import time
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, # noqa: E402
    get_store,
    strict_int,
    strict_bool,
    opt_str,
)

_store = get_store("slack-api")
_API = "slack-api"



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
_store.register("channels", primary_key="id",
                initial_loader=lambda: _coerce_channels(_load("channels.json", "channels")))
_store.register("messages", primary_key="ts",
                initial_loader=lambda: _coerce_messages(_load("messages.json", "messages")))
_store.register("channel_members", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['channel_id']}@{r['user_id']}"} for r in (_strip_ctx(x) for x in _load("channel_members.json", "channel_members"))])
_store.register_document("team", initial_loader=lambda: json.load(open(DATA_DIR / "team.json", encoding="utf-8")))


def _users_rows():
    return _store.table("users").rows()


def _channels_rows():
    return _store.table("channels").rows()


def _messages_rows():
    return _store.table("messages").rows()


def _channel_members_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("channel_members").rows()]


def _team_doc():
    return _store.document("team").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "is_admin": strict_bool(r, "is_admin"),
            "is_bot": strict_bool(r, "is_bot"),
        })
    return out


def _coerce_channels(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "is_private": strict_bool(r, "is_private"),
            "is_archived": strict_bool(r, "is_archived"),
            "created": strict_int(r, "created"),
            "num_members": strict_int(r, "num_members"),
        })
    return out


def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "thread_ts": opt_str(r, "thread_ts", default="") or None,
            "reply_count": strict_int(r, "reply_count"),
            "reactions": _parse_reactions(opt_str(r, "reactions", default="")),
        })
    return out


def _parse_reactions(s):
    if not s:
        return []
    result = []
    for chunk in s.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" in chunk:
            name, users = chunk.split(":", 1)
            user_list = [u.strip() for u in users.split(",") if u.strip()]
            result.append({"name": name, "users": user_list, "count": len(user_list)})
    return result







def _next_ts():
    return f"{time.time():.6f}"


# Slack-style response envelope
def _ok(payload):
    return {"ok": True, **payload}


def _err(error):
    return {"ok": False, "error": error}


# ---------------------------------------------------------------------------
# auth / team
# ---------------------------------------------------------------------------

def auth_test():
    # Authenticate as the first admin
    admin = next((u for u in _users_rows() if u["is_admin"]), _users_rows()[0])
    return _ok({
        "url": f"https://{_team_doc()['domain']}.slack.com/",
        "team": _team_doc()["name"],
        "user": admin["name"],
        "team_id": _team_doc()["id"],
        "user_id": admin["id"],
    })


def team_info():
    return _ok({"team": _team_doc()})


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------

def users_list():
    return _ok({"members": _users_rows()})


def users_info(user_id):
    for u in _users_rows():
        if u["id"] == user_id:
            return _ok({"user": u})
    return _err("user_not_found")


def users_set_presence(user_id, presence):
    for u in _users_rows():
        if u["id"] == user_id:
            _changes = {"presence": "away" if presence == "away" else "auto"}
            u.update(_changes)
            _store_patch("users", u, _changes)
            return _ok({"presence": u["presence"]})
    return _err("user_not_found")


# ---------------------------------------------------------------------------
# conversations
# ---------------------------------------------------------------------------

def conversations_list(types="public_channel,private_channel", exclude_archived=True):
    type_set = {t.strip() for t in types.split(",")}
    results = []
    for c in _channels_rows():
        if exclude_archived and c["is_archived"]:
            continue
        if c["is_private"] and "private_channel" not in type_set:
            continue
        if not c["is_private"] and "public_channel" not in type_set:
            continue
        results.append(c)
    return _ok({"channels": results})


def conversations_info(channel_id):
    for c in _channels_rows():
        if c["id"] == channel_id:
            return _ok({"channel": c})
    return _err("channel_not_found")


def conversations_create(name, is_private=False, user_id="U01AMELIA"):
    if any(c["name"] == name for c in _channels_rows()):
        return _err("name_taken")
    channel = {
        "id": ("G" if is_private else "C") + "01" + uuid.uuid4().hex[:8].upper(),
        "name": name,
        "is_private": bool(is_private),
        "is_archived": False,
        "topic": "",
        "purpose": "",
        "creator": user_id,
        "created": int(time.time()),
        "num_members": 1,
    }
    _store_insert("channels", channel)
    _store_insert("channel_members", {"channel_id": channel["id"], "user_id": user_id})
    return _ok({"channel": channel})


def conversations_archive(channel_id):
    for c in _channels_rows():
        if c["id"] == channel_id:
            _changes = {"is_archived": True}
            c.update(_changes)
            _store_patch("channels", c, _changes)
            return _ok({})
    return _err("channel_not_found")


def conversations_members(channel_id):
    members = [m["user_id"] for m in _channel_members_rows() if m["channel_id"] == channel_id]
    if not members and not any(c["id"] == channel_id for c in _channels_rows()):
        return _err("channel_not_found")
    return _ok({"members": members})


def conversations_invite(channel_id, user_id):
    if not any(c["id"] == channel_id for c in _channels_rows()):
        return _err("channel_not_found")
    if not any(u["id"] == user_id for u in _users_rows()):
        return _err("user_not_found")
    if any(m["channel_id"] == channel_id and m["user_id"] == user_id for m in _channel_members_rows()):
        return _err("already_in_channel")
    _store_insert("channel_members", {"channel_id": channel_id, "user_id": user_id})
    for c in _channels_rows():
        if c["id"] == channel_id:
            _changes = {"num_members": c["num_members"] + 1}
            c.update(_changes)
            _store_patch("channels", c, _changes)
    return _ok({"channel": next(c for c in _channels_rows() if c["id"] == channel_id)})


def conversations_history(channel_id, limit=20, oldest=None, latest=None):
    if not any(c["id"] == channel_id for c in _channels_rows()):
        return _err("channel_not_found")
    msgs = [m for m in _messages_rows() if m["channel_id"] == channel_id and m["thread_ts"] is None]
    if oldest:
        msgs = [m for m in msgs if float(m["ts"]) >= float(oldest)]
    if latest:
        msgs = [m for m in msgs if float(m["ts"]) <= float(latest)]
    msgs.sort(key=lambda m: float(m["ts"]), reverse=True)
    return _ok({"messages": msgs[:limit], "has_more": len(msgs) > limit})


def conversations_replies(channel_id, ts):
    parent = next((m for m in _messages_rows()
                   if m["channel_id"] == channel_id and m["ts"] == ts), None)
    if not parent:
        return _err("thread_not_found")
    replies = [m for m in _messages_rows()
               if m["channel_id"] == channel_id and m["thread_ts"] == ts]
    replies.sort(key=lambda m: float(m["ts"]))
    return _ok({"messages": [parent] + replies})


# ---------------------------------------------------------------------------
# chat
# ---------------------------------------------------------------------------

def chat_post_message(channel_id, user_id, text, thread_ts=None):
    if not any(c["id"] == channel_id for c in _channels_rows()):
        return _err("channel_not_found")
    ts = _next_ts()
    msg = {
        "ts": ts,
        "channel_id": channel_id,
        "user_id": user_id,
        "text": text,
        "thread_ts": thread_ts,
        "reply_count": 0,
        "reactions": [],
    }
    _store_insert("messages", msg)
    if thread_ts:
        for m in _messages_rows():
            if m["channel_id"] == channel_id and m["ts"] == thread_ts:
                _changes = {"reply_count": m["reply_count"] + 1}
                m.update(_changes)
                _store_patch("messages", m, _changes)
    return _ok({"channel": channel_id, "ts": ts, "message": msg})


def chat_update(channel_id, ts, text):
    for m in _messages_rows():
        if m["channel_id"] == channel_id and m["ts"] == ts:
            _changes = {"text": text}
            m.update(_changes)
            _store_patch("messages", m, _changes)
            return _ok({"channel": channel_id, "ts": ts, "text": text})
    return _err("message_not_found")


def chat_delete(channel_id, ts):
    for m in _messages_rows():
        if m["channel_id"] == channel_id and m["ts"] == ts:
            _store_delete("messages", m)
            return _ok({"channel": channel_id, "ts": ts})
    return _err("message_not_found")


# ---------------------------------------------------------------------------
# reactions
# ---------------------------------------------------------------------------

def reactions_add(channel_id, ts, name, user_id):
    for m in _messages_rows():
        if m["channel_id"] == channel_id and m["ts"] == ts:
            for r in m["reactions"]:
                if r["name"] == name:
                    if user_id not in r["users"]:
                        r["users"].append(user_id)
                        r["count"] = len(r["users"])
                    _store_patch("messages", m, {"reactions": m["reactions"]})
                    return _ok({})
            m["reactions"].append({"name": name, "users": [user_id], "count": 1})
            _store_patch("messages", m, {"reactions": m["reactions"]})
            return _ok({})
    return _err("message_not_found")


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def search_messages(query):
    q = query.lower()
    matches = [m for m in _messages_rows() if q in m["text"].lower()]
    return _ok({"messages": {"total": len(matches), "matches": matches}})


_store.eager_load()
