"""Data access module for the Twitch Helix API mock service.

Helix collection responses wrap rows in {"data": [...]}.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store, opt_str, strict_bool, strict_float, strict_int)

_store = get_store("twitch-api")
_API = "twitch-api"

_store.register("users", primary_key="id",
                initial_loader=lambda: _coerce_users(_load("users.json", "users")))
_store.register("games", primary_key="id",
                initial_loader=lambda: _coerce_games(_load("games.json", "games")))
_store.register("channels", primary_key="broadcaster_id",
                initial_loader=lambda: _coerce_channels(_load("channels.json", "channels")))
_store.register("streams", primary_key="id",
                initial_loader=lambda: _coerce_streams(_load("streams.json", "streams")))
_store.register("clips", primary_key="id",
                initial_loader=lambda: _coerce_clips(_load("clips.json", "clips")))


def _users_rows():
    return _store.table("users").rows()


def _games_rows():
    return _store.table("games").rows()


def _channels_rows():
    return _store.table("channels").rows()


def _streams_rows():
    return _store.table("streams").rows()


def _clips_rows():
    return _store.table("clips").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


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
            **_strip_ctx(r),
            "view_count": strict_int(r, "view_count"),
        })
    return out


def _coerce_games(rows):
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "name": r["name"],
            "box_art_url": r["box_art_url"],
            "rank": strict_int(r, "rank"),
            "viewer_count": strict_int(r, "viewer_count"),
        })
    return out


def _coerce_channels(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "tags": _split_tags(r["tags"]),
            "follower_count": strict_int(r, "follower_count"),
        })
    return out


def _coerce_streams(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "viewer_count": strict_int(r, "viewer_count"),
            "is_live": strict_bool(r, "is_live"),
            "started_at": opt_str(r, "started_at", default="") or None,
        })
    return out


def _coerce_clips(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "view_count": strict_int(r, "view_count"),
            "duration": strict_float(r, "duration"),
        })
    return out












def _wrap(rows):
    return {"data": rows}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

def get_users(logins=None, ids=None):
    results = list(_users_rows())
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
    results = [s for s in _streams_rows() if s["is_live"]]
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
    results = [c for c in _channels_rows() if c["broadcaster_id"] in wanted]
    return _wrap(results)


# ---------------------------------------------------------------------------
# Games
# ---------------------------------------------------------------------------

def get_top_games(first=20):
    results = sorted(_games_rows(), key=lambda g: g["rank"])[:first]
    return _wrap(results)


def get_games(names=None, ids=None):
    results = list(_games_rows())
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
    results = list(_clips_rows())
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
    channel = next((c for c in _channels_rows() if c["broadcaster_id"] == broadcaster_id), None)
    if not channel:
        return {"data": [], "total": 0}
    return {"data": [], "total": channel["follower_count"]}

_store.eager_load()
