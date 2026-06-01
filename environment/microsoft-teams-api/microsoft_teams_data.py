"""Data access module for the Microsoft Teams (Graph) mock service.

Mirrors a subset of the Microsoft Graph v1.0 API surface for Teams: joined
teams, teams, channels, and channel messages. Graph wraps collections as
{"value": [...]}. Sending a message appends to an in-memory store that resets
on restart.
"""

import csv
import secrets
import time
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            "isArchived": _to_bool(r["is_archived"]),
            "webUrl": r["web_url"],
            "member_ids": [x for x in r["member_ids"].split(";") if x],
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


_teams = _coerce_teams(_load("teams.csv"))
_channels = _coerce_channels(_load("channels.csv"))
_messages = _coerce_messages(_load("messages.csv"))

_teams_store = deepcopy(_teams)
_channels_store = deepcopy(_channels)
_messages_store = deepcopy(_messages)


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
    teams = [t for t in _teams_store if _ME in t["member_ids"] and not t["isArchived"]]
    return {"value": [_serialize_team(t) for t in teams]}


def get_team(team_id):
    for t in _teams_store:
        if t["id"] == team_id:
            return _serialize_team(t)
    return {"error": "team not found", "message": f"Team {team_id} not found"}


# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------

def list_channels(team_id):
    if not any(t["id"] == team_id for t in _teams_store):
        return {"error": "team not found", "message": f"Team {team_id} not found"}
    channels = [c for c in _channels_store if c["team_id"] == team_id]
    return {"value": [_serialize_channel(c) for c in channels]}


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def _channel(team_id, channel_id):
    return next(
        (c for c in _channels_store if c["id"] == channel_id and c["team_id"] == team_id),
        None,
    )


def list_messages(team_id, channel_id):
    if not _channel(team_id, channel_id):
        return {"error": "channel not found", "message": f"Channel {channel_id} not found"}
    msgs = [
        m for m in _messages_store
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
    _messages_store.append(msg)
    return _serialize_message(msg)
