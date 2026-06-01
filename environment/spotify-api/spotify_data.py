"""Data access module for the Spotify API mock service."""

import csv
import json
import random
import string
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent

_BASE62 = string.ascii_letters + string.digits


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _to_bool(v):
    return str(v).strip().lower() == "true"


def _spotify_id():
    """Generate a Spotify-style 22-char base62 identifier."""
    return "".join(random.choice(_BASE62) for _ in range(22))


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_artists(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "genres": [g.strip() for g in r["genres"].split(",")],
            "followers": int(r["followers"]),
            "popularity": int(r["popularity"]),
        })
    return out


def _coerce_albums(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "total_tracks": int(r["total_tracks"]),
        })
    return out


def _coerce_tracks(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "duration_ms": int(r["duration_ms"]),
            "popularity": int(r["popularity"]),
            "explicit": _to_bool(r["explicit"]),
            "track_number": int(r["track_number"]),
        })
    return out


def _coerce_playlists(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "public": _to_bool(r["public"]),
            "collaborative": _to_bool(r["collaborative"]),
        })
    return out


def _coerce_playlist_tracks(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "position": int(r["position"]),
        })
    return out


_artists = _coerce_artists(_load("artists.csv"))
_albums = _coerce_albums(_load("albums.csv"))
_tracks = _coerce_tracks(_load("tracks.csv"))
_playlists = _coerce_playlists(_load("playlists.csv"))
_playlist_tracks = _coerce_playlist_tracks(_load("playlist_tracks.csv"))

with open(DATA_DIR / "user.json", encoding="utf-8") as _f:
    _user = json.load(_f)

_artists_store = deepcopy(_artists)
_albums_store = deepcopy(_albums)
_tracks_store = deepcopy(_tracks)
_playlists_store = deepcopy(_playlists)
_playlist_tracks_store = deepcopy(_playlist_tracks)
_user_store = deepcopy(_user)

_playback_state = {
    "is_playing": False,
    "device": {"id": "device-web-001", "name": "Web Player", "type": "Computer", "volume_percent": 65},
    "shuffle_state": False,
    "repeat_state": "off",
    "progress_ms": 0,
    "item": None,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _artist_brief(artist_id):
    a = next((x for x in _artists_store if x["artist_id"] == artist_id), None)
    if not a:
        return None
    return {"id": a["artist_id"], "name": a["name"]}


def _album_brief(album_id):
    al = next((x for x in _albums_store if x["album_id"] == album_id), None)
    if not al:
        return None
    return {"id": al["album_id"], "name": al["name"], "release_date": al["release_date"]}


def _track_obj(t):
    return {
        "id": t["track_id"],
        "name": t["name"],
        "duration_ms": t["duration_ms"],
        "popularity": t["popularity"],
        "explicit": t["explicit"],
        "track_number": t["track_number"],
        "artist": _artist_brief(t["artist_id"]),
        "album": _album_brief(t["album_id"]),
        "uri": f"spotify:track:{t['track_id']}",
    }


def _playlist_obj(p, with_tracks=False):
    obj = {
        "id": p["playlist_id"],
        "name": p["name"],
        "description": p["description"],
        "owner": {"id": p["owner_id"]},
        "public": p["public"],
        "collaborative": p["collaborative"],
        "uri": f"spotify:playlist:{p['playlist_id']}",
    }
    pts = sorted(
        [pt for pt in _playlist_tracks_store if pt["playlist_id"] == p["playlist_id"]],
        key=lambda x: x["position"],
    )
    obj["tracks"] = {"total": len(pts)}
    if with_tracks:
        items = []
        for pt in pts:
            t = next((x for x in _tracks_store if x["track_id"] == pt["track_id"]), None)
            if t:
                items.append({"added_at": pt["added_at"], "track": _track_obj(t)})
        obj["tracks"] = {"total": len(items), "items": items}
    return obj


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

def get_me():
    return _user_store


def list_my_playlists():
    items = [_playlist_obj(p) for p in _playlists_store
             if p["owner_id"] == _user_store["id"]]
    return {"items": items, "total": len(items)}


# ---------------------------------------------------------------------------
# Playlists
# ---------------------------------------------------------------------------

def get_playlist(playlist_id):
    for p in _playlists_store:
        if p["playlist_id"] == playlist_id:
            return _playlist_obj(p, with_tracks=True)
    return {"error": f"Playlist {playlist_id} not found"}


def get_playlist_tracks(playlist_id):
    p = next((x for x in _playlists_store if x["playlist_id"] == playlist_id), None)
    if not p:
        return {"error": f"Playlist {playlist_id} not found"}
    obj = _playlist_obj(p, with_tracks=True)
    return {"total": obj["tracks"]["total"], "items": obj["tracks"]["items"]}


def create_playlist(user_id, name, description="", public=True, collaborative=False):
    playlist_id = _spotify_id()
    playlist = {
        "playlist_id": playlist_id,
        "name": name,
        "description": description,
        "owner_id": user_id,
        "public": bool(public),
        "collaborative": bool(collaborative),
    }
    _playlists_store.append(playlist)
    return _playlist_obj(playlist, with_tracks=True)


def add_tracks(playlist_id, uris):
    p = next((x for x in _playlists_store if x["playlist_id"] == playlist_id), None)
    if not p:
        return {"error": f"Playlist {playlist_id} not found"}
    existing = [pt for pt in _playlist_tracks_store if pt["playlist_id"] == playlist_id]
    next_pos = max((pt["position"] for pt in existing), default=-1) + 1
    added = 0
    for uri in uris:
        track_id = uri.split(":")[-1] if ":" in uri else uri
        if not any(t["track_id"] == track_id for t in _tracks_store):
            continue
        _playlist_tracks_store.append({
            "playlist_id": playlist_id,
            "track_id": track_id,
            "position": next_pos,
            "added_at": _now_iso(),
        })
        next_pos += 1
        added += 1
    return {"playlist_id": playlist_id, "added": added,
            "snapshot_id": _spotify_id()}


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search(query, types=None):
    if not types:
        types = ["track", "album", "artist"]
    q = (query or "").lower()
    result = {}
    if "track" in types:
        hits = [_track_obj(t) for t in _tracks_store if q in t["name"].lower()]
        result["tracks"] = {"items": hits, "total": len(hits)}
    if "album" in types:
        hits = [{
            "id": a["album_id"], "name": a["name"], "album_type": a["album_type"],
            "release_date": a["release_date"], "total_tracks": a["total_tracks"],
            "artist": _artist_brief(a["artist_id"]),
        } for a in _albums_store if q in a["name"].lower()]
        result["albums"] = {"items": hits, "total": len(hits)}
    if "artist" in types:
        hits = [{
            "id": a["artist_id"], "name": a["name"], "genres": a["genres"],
            "followers": a["followers"], "popularity": a["popularity"],
        } for a in _artists_store if q in a["name"].lower()]
        result["artists"] = {"items": hits, "total": len(hits)}
    return result


# ---------------------------------------------------------------------------
# Playback
# ---------------------------------------------------------------------------

def get_player():
    return deepcopy(_playback_state)


def start_playback(uris=None, context_uri=None):
    item = None
    if uris:
        track_id = uris[0].split(":")[-1]
        t = next((x for x in _tracks_store if x["track_id"] == track_id), None)
        if t:
            item = _track_obj(t)
    elif context_uri and context_uri.startswith("spotify:playlist:"):
        pid = context_uri.split(":")[-1]
        pts = sorted(
            [pt for pt in _playlist_tracks_store if pt["playlist_id"] == pid],
            key=lambda x: x["position"],
        )
        if pts:
            t = next((x for x in _tracks_store if x["track_id"] == pts[0]["track_id"]), None)
            if t:
                item = _track_obj(t)
    _playback_state["is_playing"] = True
    _playback_state["progress_ms"] = 0
    if item is not None:
        _playback_state["item"] = item
    return deepcopy(_playback_state)
