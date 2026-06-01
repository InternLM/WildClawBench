"""Data access module for the Twitch Helix API mock service.

Helix collection responses wrap rows in {"data": [...]}.
"""

import csv
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _split_tags(s):
    return [t for t in (s or "").split(";") if t]


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_users(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "view_count": int(r["view_count"]),
        })
    return out


def _coerce_games(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "box_art_url": r["box_art_url"],
            "rank": int(r["rank"]),
            "viewer_count": int(r["viewer_count"]),
        })
    return out


def _coerce_channels(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "tags": _split_tags(r["tags"]),
            "follower_count": int(r["follower_count"]),
        })
    return out


def _coerce_streams(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "viewer_count": int(r["viewer_count"]),
            "is_live": _to_bool(r["is_live"]),
            "started_at": r["started_at"] or None,
        })
    return out


def _coerce_clips(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "view_count": int(r["view_count"]),
            "duration": float(r["duration"]),
        })
    return out


_users = _coerce_users(_load("users.csv"))
_games = _coerce_games(_load("games.csv"))
_channels = _coerce_channels(_load("channels.csv"))
_streams = _coerce_streams(_load("streams.csv"))
_clips = _coerce_clips(_load("clips.csv"))

_users_store = deepcopy(_users)
_games_store = deepcopy(_games)
_channels_store = deepcopy(_channels)
_streams_store = deepcopy(_streams)
_clips_store = deepcopy(_clips)


def _wrap(rows):
    return {"data": rows}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_users(logins=None, ids=None):
    results = list(_users_store)
    if logins:
        wanted = {l.strip().lower() for l in logins}
        results = [u for u in results if u["login"].lower() in wanted]
    if ids:
        wanted_ids = {i.strip() for i in ids}
        results = [u for u in results if u["id"] in wanted_ids]
    return _wrap(results)


# ---------------------------------------------------------------------------
# Streams (live only)
# ---------------------------------------------------------------------------

def get_streams(user_logins=None, user_ids=None, game_id=None):
    results = [s for s in _streams_store if s["is_live"]]
    if user_logins:
        wanted = {l.strip().lower() for l in user_logins}
        results = [s for s in results if s["user_login"].lower() in wanted]
    if user_ids:
        wanted_ids = {i.strip() for i in user_ids}
        results = [s for s in results if s["user_id"] in wanted_ids]
    if game_id:
        results = [s for s in results if s["game_id"] == game_id]
    results.sort(key=lambda s: s["viewer_count"], reverse=True)
    return _wrap(results)


# ---------------------------------------------------------------------------
# Channels
# ---------------------------------------------------------------------------

def get_channels(broadcaster_ids):
    wanted = {i.strip() for i in broadcaster_ids}
    results = [c for c in _channels_store if c["broadcaster_id"] in wanted]
    return _wrap(results)


# ---------------------------------------------------------------------------
# Games
# ---------------------------------------------------------------------------

def get_top_games(first=20):
    results = sorted(_games_store, key=lambda g: g["rank"])[:first]
    return _wrap(results)


def get_games(names=None, ids=None):
    results = list(_games_store)
    if names:
        wanted = {n.strip().lower() for n in names}
        results = [g for g in results if g["name"].lower() in wanted]
    if ids:
        wanted_ids = {i.strip() for i in ids}
        results = [g for g in results if g["id"] in wanted_ids]
    return _wrap(results)


# ---------------------------------------------------------------------------
# Clips
# ---------------------------------------------------------------------------

def get_clips(broadcaster_id=None, game_id=None, first=20):
    results = list(_clips_store)
    if broadcaster_id:
        results = [c for c in results if c["broadcaster_id"] == broadcaster_id]
    if game_id:
        results = [c for c in results if c["game_id"] == game_id]
    results.sort(key=lambda c: c["view_count"], reverse=True)
    return _wrap(results[:first])


# ---------------------------------------------------------------------------
# Followers
# ---------------------------------------------------------------------------

def get_channel_followers(broadcaster_id):
    channel = next((c for c in _channels_store if c["broadcaster_id"] == broadcaster_id), None)
    if not channel:
        return {"data": [], "total": 0}
    return {"data": [], "total": channel["follower_count"]}
