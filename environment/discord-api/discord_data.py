"""Data access module for the Discord API mock service.

Mirrors a subset of the Discord REST API v10: users, guilds, channels,
messages, members, and roles. IDs are Discord-style snowflakes (numeric strings).
"""

import csv
import json
import random
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent

# Discord epoch (2015-01-01) in milliseconds, used for snowflake generation.
_DISCORD_EPOCH = 1420070400000
_seq = 0


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            "approximate_member_count": int(r["member_count"]),
            "description": r["description"] or None,
            "icon": r["icon"] or None,
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
            "type": int(r["type"]),
            "position": int(r["position"]),
            "topic": r["topic"] or None,
            "nsfw": _to_bool(r["nsfw"]),
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
            "pinned": _to_bool(r["pinned"]),
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
                "global_name": r["global_name"] or None,
                "bot": _to_bool(r["bot"]),
            },
            "nick": r["nick"] or None,
            "joined_at": r["joined_at"],
            "roles": [x for x in r["roles"].split(";") if x],
        })
    return out


def _coerce_roles(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "guild_id": r["guild_id"],
            "name": r["name"],
            "color": int(r["color"]),
            "position": int(r["position"]),
            "hoist": _to_bool(r["hoist"]),
            "mentionable": _to_bool(r["mentionable"]),
            "permissions": r["permissions"],
        })
    return out


_guilds = _coerce_guilds(_load("guilds.csv"))
_channels = _coerce_channels(_load("channels.csv"))
_messages = _coerce_messages(_load("messages.csv"))
_members = _coerce_members(_load("members.csv"))
_roles = _coerce_roles(_load("roles.csv"))

with open(DATA_DIR / "me.json", encoding="utf-8") as _f:
    _me = json.load(_f)

_guilds_store = deepcopy(_guilds)
_channels_store = deepcopy(_channels)
_messages_store = deepcopy(_messages)
_members_store = deepcopy(_members)
_roles_store = deepcopy(_roles)
_me_store = deepcopy(_me)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_me():
    return _me_store


def list_my_guilds():
    return [
        {
            "id": g["id"],
            "name": g["name"],
            "icon": g["icon"],
            "owner": g["owner_id"] == _me_store["id"],
            "permissions": "104324673",
        }
        for g in _guilds_store
    ]


# ---------------------------------------------------------------------------
# Guilds
# ---------------------------------------------------------------------------

def get_guild(guild_id):
    for g in _guilds_store:
        if g["id"] == guild_id:
            return g
    return {"error": f"Unknown Guild {guild_id}", "code": 10004}


def list_guild_channels(guild_id):
    if not any(g["id"] == guild_id for g in _guilds_store):
        return {"error": f"Unknown Guild {guild_id}", "code": 10004}
    chans = [c for c in _channels_store if c["guild_id"] == guild_id]
    chans.sort(key=lambda c: c["position"])
    return chans


def list_guild_members(guild_id, limit=100):
    if not any(g["id"] == guild_id for g in _guilds_store):
        return {"error": f"Unknown Guild {guild_id}", "code": 10004}
    members = [m for m in _members_store if m["guild_id"] == guild_id]
    return members[: max(1, limit)]


def list_guild_roles(guild_id):
    if not any(g["id"] == guild_id for g in _guilds_store):
        return {"error": f"Unknown Guild {guild_id}", "code": 10004}
    roles = [r for r in _roles_store if r["guild_id"] == guild_id]
    roles.sort(key=lambda r: r["position"], reverse=True)
    return roles


# ---------------------------------------------------------------------------
# Channels + messages
# ---------------------------------------------------------------------------

def get_channel(channel_id):
    for c in _channels_store:
        if c["id"] == channel_id:
            return c
    return {"error": f"Unknown Channel {channel_id}", "code": 10003}


def list_channel_messages(channel_id, limit=50):
    if not any(c["id"] == channel_id for c in _channels_store):
        return {"error": f"Unknown Channel {channel_id}", "code": 10003}
    msgs = [m for m in _messages_store if m["channel_id"] == channel_id]
    msgs.sort(key=lambda m: m["timestamp"], reverse=True)
    return msgs[: max(1, limit)]


def create_message(channel_id, content, author_id=None):
    channel = next((c for c in _channels_store if c["id"] == channel_id), None)
    if not channel:
        return {"error": f"Unknown Channel {channel_id}", "code": 10003}
    if not content:
        return {"error": "Cannot send an empty message", "code": 50006}
    author_id = author_id or _me_store["id"]
    member = next((m for m in _members_store
                   if m["guild_id"] == channel["guild_id"] and m["user"]["id"] == author_id), None)
    username = member["user"]["username"] if member else _me_store["username"]
    msg = {
        "id": _snowflake(),
        "channel_id": channel_id,
        "author": {"id": author_id, "username": username},
        "content": content,
        "timestamp": _now(),
        "pinned": False,
        "edited_timestamp": None,
    }
    _messages_store.append(msg)
    return msg
