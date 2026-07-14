"""FastAPI server wrapping twitch_data module as REST endpoints.

Implements a subset of the Twitch Helix API surface. Base path: /helix
"""

from fastapi import FastAPI, Query
from typing import Optional, List

import twitch_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError as _shared_plane_err:  # standalone run without the shared module on sys.path
    import logging as _logging
    _logging.error("SHARED PLANE MISSING - audit + admin disabled: %s", _shared_plane_err)
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="Twitch Helix API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=twitch_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.get("/helix/users")
def get_users(login: Optional[List[str]] = Query(None), id: Optional[List[str]] = Query(None)):
    return twitch_data.get_users(logins=login, ids=id)


# --- Streams (live only) ---

@app.get("/helix/streams")
def get_streams(user_login: Optional[List[str]] = Query(None),
                user_id: Optional[List[str]] = Query(None),
                game_id: Optional[str] = None):
    return twitch_data.get_streams(user_logins=user_login, user_ids=user_id, game_id=game_id)


# --- Channels ---

@app.get("/helix/channels")
def get_channels(broadcaster_id: List[str] = Query(...)):
    return twitch_data.get_channels(broadcaster_ids=broadcaster_id)


@app.get("/helix/channels/followers")
def get_channel_followers(broadcaster_id: str = Query(...)):
    return twitch_data.get_channel_followers(broadcaster_id)


# --- Games ---

@app.get("/helix/games/top")
def get_top_games(first: int = Query(20, ge=1, le=100)):
    return twitch_data.get_top_games(first=first)


@app.get("/helix/games")
def get_games(name: Optional[List[str]] = Query(None), id: Optional[List[str]] = Query(None)):
    return twitch_data.get_games(names=name, ids=id)


# --- Clips ---

@app.get("/helix/clips")
def get_clips(broadcaster_id: Optional[str] = None, game_id: Optional[str] = None,
              first: int = Query(20, ge=1, le=100)):
    return twitch_data.get_clips(broadcaster_id=broadcaster_id, game_id=game_id, first=first)
