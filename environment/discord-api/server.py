"""FastAPI server wrapping discord_data module as REST endpoints.

Implements a subset of the Discord REST API v10. Base path: /api/v10
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import discord_data
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

app = FastAPI(title="Discord API (Mock)", version="v10")
install_tracker(app)
install_admin_plane(app, store=discord_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Users ---

@app.get("/api/v10/users/@me")
def get_me():
    return discord_data.get_me()


@app.get("/api/v10/users/@me/guilds")
def list_my_guilds():
    return discord_data.list_my_guilds()


# --- Guilds ---

@app.get("/api/v10/guilds/{guild_id}")
def get_guild(guild_id: str):
    result = discord_data.get_guild(guild_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/v10/guilds/{guild_id}/channels")
def list_guild_channels(guild_id: str):
    result = discord_data.list_guild_channels(guild_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/v10/guilds/{guild_id}/members")
def list_guild_members(guild_id: str, limit: int = Query(100, ge=1, le=1000)):
    result = discord_data.list_guild_members(guild_id, limit=limit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/v10/guilds/{guild_id}/roles")
def list_guild_roles(guild_id: str):
    result = discord_data.list_guild_roles(guild_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Channels ---

@app.get("/api/v10/channels/{channel_id}")
def get_channel(channel_id: str):
    result = discord_data.get_channel(channel_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/api/v10/channels/{channel_id}/messages")
def list_channel_messages(channel_id: str, limit: int = Query(50, ge=1, le=100)):
    result = discord_data.list_channel_messages(channel_id, limit=limit)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class MessageBody(BaseModel):
    content: str
    author_id: Optional[str] = None


@app.post("/api/v10/channels/{channel_id}/messages", status_code=201)
def create_message(channel_id: str, body: MessageBody):
    result = discord_data.create_message(channel_id, body.content, author_id=body.author_id)
    if isinstance(result, dict) and "error" in result:
        code = 404 if result.get("code") == 10003 else 400
        return JSONResponse(status_code=code, content=result)
    return result
