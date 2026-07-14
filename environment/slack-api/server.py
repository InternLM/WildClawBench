"""FastAPI server wrapping slack_data module as REST endpoints.

Uses Slack's method-name routes (e.g. /api/conversations.list) for familiarity.
"""

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional

import slack_data
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

app = FastAPI(title="Slack Web API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=slack_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- auth / team ---

@app.get("/api/auth.test")
@app.post("/api/auth.test")
def auth_test():
    return slack_data.auth_test()


@app.get("/api/team.info")
def team_info():
    return slack_data.team_info()


# --- users ---

@app.get("/api/users.list")
def users_list():
    return slack_data.users_list()


@app.get("/api/users.info")
def users_info(user: str = Query(...)):
    return slack_data.users_info(user)


class PresenceBody(BaseModel):
    user: str
    presence: str  # "away" or "auto"


@app.post("/api/users.setPresence")
def users_set_presence(body: PresenceBody):
    return slack_data.users_set_presence(body.user, body.presence)


# --- conversations ---

@app.get("/api/conversations.list")
def conversations_list(
    types: str = "public_channel,private_channel",
    exclude_archived: bool = True,
):
    return slack_data.conversations_list(types=types, exclude_archived=exclude_archived)


@app.get("/api/conversations.info")
def conversations_info(channel: str = Query(...)):
    return slack_data.conversations_info(channel)


class CreateChannelBody(BaseModel):
    name: str
    is_private: bool = False
    user_id: Optional[str] = "U01AMELIA"


@app.post("/api/conversations.create")
def conversations_create(body: CreateChannelBody):
    return slack_data.conversations_create(body.name, body.is_private, body.user_id)


class ChannelOnlyBody(BaseModel):
    channel: str


@app.post("/api/conversations.archive")
def conversations_archive(body: ChannelOnlyBody):
    return slack_data.conversations_archive(body.channel)


@app.get("/api/conversations.members")
def conversations_members(channel: str = Query(...)):
    return slack_data.conversations_members(channel)


class InviteBody(BaseModel):
    channel: str
    users: str  # comma-separated


@app.post("/api/conversations.invite")
def conversations_invite(body: InviteBody):
    results = []
    last = None
    for u in [s.strip() for s in body.users.split(",") if s.strip()]:
        last = slack_data.conversations_invite(body.channel, u)
        results.append({"user": u, "ok": last.get("ok", False), "error": last.get("error")})
    return {"ok": all(r["ok"] for r in results), "results": results, "channel": last and last.get("channel")}


@app.get("/api/conversations.history")
def conversations_history(
    channel: str = Query(...),
    limit: int = 20,
    oldest: Optional[str] = None,
    latest: Optional[str] = None,
):
    return slack_data.conversations_history(channel, limit=limit, oldest=oldest, latest=latest)


@app.get("/api/conversations.replies")
def conversations_replies(channel: str = Query(...), ts: str = Query(...)):
    return slack_data.conversations_replies(channel, ts)


# --- chat ---

class PostMessageBody(BaseModel):
    channel: str
    text: str
    user: str = "U01AMELIA"
    thread_ts: Optional[str] = None


@app.post("/api/chat.postMessage")
def chat_post_message(body: PostMessageBody):
    return slack_data.chat_post_message(body.channel, body.user, body.text, thread_ts=body.thread_ts)


class UpdateMessageBody(BaseModel):
    channel: str
    ts: str
    text: str


@app.post("/api/chat.update")
def chat_update(body: UpdateMessageBody):
    return slack_data.chat_update(body.channel, body.ts, body.text)


class DeleteMessageBody(BaseModel):
    channel: str
    ts: str


@app.post("/api/chat.delete")
def chat_delete(body: DeleteMessageBody):
    return slack_data.chat_delete(body.channel, body.ts)


# --- reactions ---

class ReactionAddBody(BaseModel):
    channel: str
    timestamp: str
    name: str
    user: str = "U01AMELIA"


@app.post("/api/reactions.add")
def reactions_add(body: ReactionAddBody):
    return slack_data.reactions_add(body.channel, body.timestamp, body.name, body.user)


# --- search ---

@app.get("/api/search.messages")
def search_messages(query: str = Query(...)):
    return slack_data.search_messages(query)
