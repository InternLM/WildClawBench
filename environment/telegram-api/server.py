"""FastAPI server wrapping telegram_data module as REST endpoints.

Mirrors the Telegram Bot API method-style routes under /bot. Every response
uses the {"ok": true, "result": ...} envelope.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import telegram_data
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

app = FastAPI(title="Telegram Bot API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=telegram_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


def _respond(result):
    if not result.get("ok", False):
        return JSONResponse(status_code=400, content=result)
    return result


# --- Bot identity ---

@app.get("/bot/getMe")
def get_me():
    return telegram_data.get_me()


# --- Messages ---

class SendMessageBody(BaseModel):
    chat_id: int
    text: str
    reply_to_message_id: Optional[int] = None


@app.post("/bot/sendMessage")
def send_message(body: SendMessageBody):
    return _respond(telegram_data.send_message(
        body.chat_id, body.text, reply_to_message_id=body.reply_to_message_id))


class SendPhotoBody(BaseModel):
    chat_id: int
    photo: str
    caption: Optional[str] = None


@app.post("/bot/sendPhoto")
def send_photo(body: SendPhotoBody):
    return _respond(telegram_data.send_photo(body.chat_id, body.photo, caption=body.caption))


class EditMessageTextBody(BaseModel):
    chat_id: int
    message_id: int
    text: str


@app.post("/bot/editMessageText")
def edit_message_text(body: EditMessageTextBody):
    return _respond(telegram_data.edit_message_text(body.chat_id, body.message_id, body.text))


class DeleteMessageBody(BaseModel):
    chat_id: int
    message_id: int


@app.post("/bot/deleteMessage")
def delete_message(body: DeleteMessageBody):
    return _respond(telegram_data.delete_message(body.chat_id, body.message_id))


# --- Chats / members / updates ---

@app.get("/bot/getUpdates")
def get_updates(offset: Optional[int] = None, limit: int = Query(100, ge=1, le=100)):
    return telegram_data.get_updates(offset=offset, limit=limit)


@app.get("/bot/getChat")
def get_chat(chat_id: int = Query(...)):
    return _respond(telegram_data.get_chat(chat_id))


@app.get("/bot/getChatMember")
def get_chat_member(chat_id: int = Query(...), user_id: int = Query(...)):
    return _respond(telegram_data.get_chat_member(chat_id, user_id))
