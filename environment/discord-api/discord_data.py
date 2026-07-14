"""Data access module for the Discord API mock service.

Mirrors a subset of the Discord REST API v10: users, guilds, channels,
messages, members, and roles. IDs are Discord-style snowflakes (numeric strings).
"""

import csv
import json
import random
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, opt_str, strict_bool, strict_int)

_store = get_store("discord-api")
_API = "discord-api"


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

_store.register("guilds", primary_key="id",
                initial_loader=lambda: _coerce_guilds(_load("guilds.json", "guilds")))
_store.register("channels", primary_key="id",
                initial_loader=lambda: _coerce_channels(_load("channels.json", "channels")))
_store.register("messages", primary_key="id",
                initial_loader=lambda: _coerce_messages(_load("messages.json", "messages")))
# members natural key (guild_id, user_id) -> synth composite pk
_store.register("members", primary_key="_pk",
                initial_loader=lambda: [
                    {**r, "_pk": f"{r['guild_id']}@{r['user']['id']}"}
                    for r in _coerce_members(_load("members.json", "members"))])
_store.register("roles", primary_key="id",
                initial_loader=lambda: _coerce_roles(_load("roles.json", "roles")))
_store.register_document("me", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "me.json", encoding="utf-8")))


def _guilds_rows():
    return _store.table("guilds").rows()


def _channels_rows():
    return _store.table("channels").rows()


def _messages_rows():
    return _store.table("messages").rows()


def _members_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("members").rows()]


def _roles_rows():
    return _store.table("roles").rows()


def _me_doc():
    return _store.document("me").get()


# Discord epoch (2015-01-01) in milliseconds, used for snowflake generation.
_DISCORD_EPOCH = 1420070400000
_seq = 0


def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000+00:00")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _snowflake():
    """Generate a ~18-19 digit snowflake-style numeric string ID."""
    global _seq
    _seq = (_seq + 1) % 4096
    ms = int(datetime.now(timezone.utc).timestamp() * 1000) - _DISCORD_EPOCH
    worker = random.randint(0, 31)
    return str((ms << 22) | (worker << 17) | _seq)


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_guilds(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "owner_id": r["owner_id"],
            "approximate_member_count": strict_int(r, "member_count"),
            "description": opt_str(r, "description", default="") or None,
            "icon": opt_str(r, "icon", default="") or None,
            "region": r["region"],
        })
    return out


def _coerce_channels(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "guild_id": r["guild_id"],
            "name": r["name"],
            "type": strict_int(r, "type"),
            "position": strict_int(r, "position"),
            "topic": opt_str(r, "topic", default="") or None,
            "nsfw": strict_bool(r, "nsfw"),
        })
    return out


def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "channel_id": r["channel_id"],
            "author": {"id": r["author_id"], "username": r["author_username"]},
            "content": r["content"],
            "timestamp": r["timestamp"],
            "pinned": strict_bool(r, "pinned"),
            "edited_timestamp": None,
        })
    return out


def _coerce_members(rows):
    out = []
    for r in rows:
        out.append({
            "guild_id": r["guild_id"],
            "user": {
                "id": r["user_id"],
                "username": r["username"],
                "global_name": opt_str(r, "global_name", default="") or None,
                "bot": strict_bool(r, "bot"),
            },
            "nick": opt_str(r, "nick", default="") or None,
            "joined_at": r["joined_at"],
            "roles": [x for x in opt_csv_list(r, "roles", sep=";") if x],
        })
    return out


def _coerce_roles(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "guild_id": r["guild_id"],
            "name": r["name"],
            "color": strict_int(r, "color"),
            "position": strict_int(r, "position"),
            "hoist": strict_bool(r, "hoist"),
            "mentionable": strict_bool(r, "mentionable"),
            "permissions": r["permissions"],
        })
    return out








# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_me():
    return _me_doc()


def list_my_guilds():
    return [
        {
            "id": g["id"],
            "name": g["name"],
            "icon": g["icon"],
            "owner": g["owner_id"] == _me_doc()["id"],
            "permissions": "104324673",
        }
        for g in _guilds_rows()
    ]


# ---------------------------------------------------------------------------
# Guilds
# ---------------------------------------------------------------------------

def get_guild(guild_id):
    for g in _guilds_rows():
        if g["id"] == guild_id:
            return g
    return {"error": f"Unknown Guild {guild_id}", "code": 10004}


def list_guild_channels(guild_id):
    if not any(g["id"] == guild_id for g in _guilds_rows()):
        return {"error": f"Unknown Guild {guild_id}", "code": 10004}
    chans = [c for c in _channels_rows() if c["guild_id"] == guild_id]
    chans.sort(key=lambda c: c["position"])
    return chans


def list_guild_members(guild_id, limit=100):
    if not any(g["id"] == guild_id for g in _guilds_rows()):
        return {"error": f"Unknown Guild {guild_id}", "code": 10004}
    members = [m for m in _members_rows() if m["guild_id"] == guild_id]
    return members[: max(1, limit)]


def list_guild_roles(guild_id):
    if not any(g["id"] == guild_id for g in _guilds_rows()):
        return {"error": f"Unknown Guild {guild_id}", "code": 10004}
    roles = [r for r in _roles_rows() if r["guild_id"] == guild_id]
    roles.sort(key=lambda r: r["position"], reverse=True)
    return roles


# ---------------------------------------------------------------------------
# Channels + messages
# ---------------------------------------------------------------------------

def get_channel(channel_id):
    for c in _channels_rows():
        if c["id"] == channel_id:
            return c
    return {"error": f"Unknown Channel {channel_id}", "code": 10003}


def list_channel_messages(channel_id, limit=50):
    if not any(c["id"] == channel_id for c in _channels_rows()):
        return {"error": f"Unknown Channel {channel_id}", "code": 10003}
    msgs = [m for m in _messages_rows() if m["channel_id"] == channel_id]
    msgs.sort(key=lambda m: m["timestamp"], reverse=True)
    return msgs[: max(1, limit)]


def create_message(channel_id, content, author_id=None):
    channel = next((c for c in _channels_rows() if c["id"] == channel_id), None)
    if not channel:
        return {"error": f"Unknown Channel {channel_id}", "code": 10003}
    if not content:
        return {"error": "Cannot send an empty message", "code": 50006}
    author_id = author_id or _me_doc()["id"]
    member = next((m for m in _members_rows()
                   if m["guild_id"] == channel["guild_id"] and m["user"]["id"] == author_id), None)
    username = member["user"]["username"] if member else _me_doc()["username"]
    msg = {
        "id": _snowflake(),
        "channel_id": channel_id,
        "author": {"id": author_id, "username": username},
        "content": content,
        "timestamp": _now(),
        "pinned": False,
        "edited_timestamp": None,
    }
    _store_insert("messages", msg)
    return msg

_store.eager_load()
