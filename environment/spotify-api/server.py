"""FastAPI server wrapping spotify_data module as REST endpoints.

Implements a subset of the Spotify Web API surface. Base path: /v1
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import spotify_data
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

app = FastAPI(title="Spotify API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=spotify_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Current user ---

@app.get("/v1/me")
def get_me():
    return spotify_data.get_me()


@app.get("/v1/me/playlists")
def list_my_playlists():
    return spotify_data.list_my_playlists()


# --- Playlists ---

@app.get("/v1/playlists/{playlist_id}")
def get_playlist(playlist_id: str):
    result = spotify_data.get_playlist(playlist_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/playlists/{playlist_id}/tracks")
def get_playlist_tracks(playlist_id: str):
    result = spotify_data.get_playlist_tracks(playlist_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class PlaylistCreateBody(BaseModel):
    name: str
    description: Optional[str] = ""
    public: bool = True
    collaborative: bool = False


@app.post("/v1/users/{user_id}/playlists", status_code=201)
def create_playlist(user_id: str, body: PlaylistCreateBody):
    return spotify_data.create_playlist(
        user_id=user_id,
        name=body.name,
        description=body.description or "",
        public=body.public,
        collaborative=body.collaborative,
    )


class AddTracksBody(BaseModel):
    uris: List[str]


@app.post("/v1/playlists/{playlist_id}/tracks", status_code=201)
def add_tracks(playlist_id: str, body: AddTracksBody):
    result = spotify_data.add_tracks(playlist_id, body.uris)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Search ---

@app.get("/v1/search")
def search(q: str = Query(...), type: Optional[str] = None):
    types = [t.strip() for t in type.split(",")] if type else None
    return spotify_data.search(q, types=types)


# --- Player ---

@app.get("/v1/me/player")
def get_player():
    return spotify_data.get_player()


class PlayBody(BaseModel):
    uris: Optional[List[str]] = None
    context_uri: Optional[str] = None


@app.put("/v1/me/player/play")
def start_playback(body: Optional[PlayBody] = None):
    body = body or PlayBody()
    return spotify_data.start_playback(uris=body.uris, context_uri=body.context_uri)
