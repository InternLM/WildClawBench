"""Data access module for the Microsoft Teams (Graph) mock service.

Mirrors a subset of the Microsoft Graph v1.0 API surface for Teams: joined
teams, teams, channels, and channel messages. Graph wraps collections as
{"value": [...]}. Sending a message appends to an in-memory store that resets
on restart.
"""

import csv
import secrets
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_csv_list, strict_bool)

_store = get_store("microsoft-teams-api")
_API = "microsoft-teams-api"


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

_store.register("teams", primary_key="id",
                initial_loader=lambda: _coerce_teams(_load("teams.json", "teams")))
_store.register("channels", primary_key="id",
                initial_loader=lambda: _coerce_channels(_load("channels.json", "channels")))
_store.register("messages", primary_key="id",
                initial_loader=lambda: _coerce_messages(_load("messages.json", "messages")))


def _teams_rows():
    return _store.table("teams").rows()


def _channels_rows():
    return _store.table("channels").rows()


def _messages_rows():
    return _store.table("messages").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _to_bool(v):
    return str(v).strip().lower() == "true"


# The signed-in user (the "me" of /me/joinedTeams).
_ME = "user-001"


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_teams(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "displayName": r["display_name"],
            "description": r["description"],
            "visibility": r["visibility"],
            "isArchived": strict_bool(r, "is_archived"),
            "webUrl": r["web_url"],
            "member_ids": [x for x in opt_csv_list(r, "member_ids", sep=";") if x],
        })
    return out


def _coerce_channels(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "team_id": r["team_id"],
            "displayName": r["display_name"],
            "description": r["description"],
            "membershipType": r["membership_type"],
            "webUrl": r["web_url"],
            "createdDateTime": r["created_date"],
        })
    return out


def _coerce_messages(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "channel_id": r["channel_id"],
            "team_id": r["team_id"],
            "from_user_id": r["from_user_id"],
            "from_display_name": r["from_display_name"],
            "content": r["content"],
            "contentType": r["content_type"],
            "importance": r["importance"],
            "createdDateTime": r["created_date"],
        })
    return out








# ---------------------------------------------------------------------------
# Serializers (Graph resource shapes)
# ---------------------------------------------------------------------------

def _serialize_team(t):
    return {
        "id": t["id"],
        "displayName": t["displayName"],
        "description": t["description"],
        "visibility": t["visibility"],
        "isArchived": t["isArchived"],
        "webUrl": t["webUrl"],
    }


def _serialize_channel(c):
    return {
        "id": c["id"],
        "displayName": c["displayName"],
        "description": c["description"],
        "membershipType": c["membershipType"],
        "webUrl": c["webUrl"],
        "createdDateTime": c["createdDateTime"],
    }


def _serialize_message(m):
    return {
        "id": m["id"],
        "messageType": "message",
        "createdDateTime": m["createdDateTime"],
        "importance": m["importance"],
        "channelIdentity": {
            "teamId": m["team_id"],
            "channelId": m["channel_id"],
        },
        "from": {
            "user": {
                "id": m["from_user_id"],
                "displayName": m["from_display_name"],
            }
        },
        "body": {
            "contentType": m["contentType"],
            "content": m["content"],
        },
    }


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------

def list_joined_teams():
    teams = [t for t in _teams_rows() if _ME in t["member_ids"] and not t["isArchived"]]
    return {"value": [_serialize_team(t) for t in teams]}


def get_team(team_id):
    for t in _teams_rows():
        if t["id"] == team_id:
            return _serialize_team(t)
    return {"error": "team not found", "message": f"Team {team_id} not found"}


# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------

def list_channels(team_id):
    if not any(t["id"] == team_id for t in _teams_rows()):
        return {"error": "team not found", "message": f"Team {team_id} not found"}
    channels = [c for c in _channels_rows() if c["team_id"] == team_id]
    return {"value": [_serialize_channel(c) for c in channels]}


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def _channel(team_id, channel_id):
    return next(
        (c for c in _channels_rows() if c["id"] == channel_id and c["team_id"] == team_id),
        None,
    )


def list_messages(team_id, channel_id):
    if not _channel(team_id, channel_id):
        return {"error": "channel not found", "message": f"Channel {channel_id} not found"}
    msgs = [
        m for m in _messages_rows()
        if m["channel_id"] == channel_id and m["team_id"] == team_id
    ]
    msgs = sorted(msgs, key=lambda m: m["createdDateTime"], reverse=True)
    return {"value": [_serialize_message(m) for m in msgs]}


def send_message(team_id, channel_id, content, content_type="html", importance="normal"):
    if not _channel(team_id, channel_id):
        return {"error": "channel not found", "message": f"Channel {channel_id} not found"}
    if not content:
        return {"error": "invalid request", "message": "body.content is required"}
    msg = {
        "id": str(int(time.time() * 1000)) + secrets.token_hex(2),
        "channel_id": channel_id,
        "team_id": team_id,
        "from_user_id": _ME,
        "from_display_name": "Alex Carter",
        "content": content,
        "contentType": content_type or "html",
        "importance": importance or "normal",
        "createdDateTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _store_insert("messages", msg)
    return _serialize_message(msg)

_store.eager_load()
