"""FastAPI server wrapping twilio_data module as REST endpoints.

Mirrors a subset of the Twilio programmable SMS/Voice/Lookup API.
Base paths follow Twilio conventions: /2010-04-01/Accounts/{AccountSid}/...
and /v1/PhoneNumbers/{PhoneNumber} for lookups.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

import twilio_data
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

app = FastAPI(title="Twilio API (Mock)", version="2010-04-01")
install_tracker(app)
install_admin_plane(app, store=twilio_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Messages ---

@app.get("/2010-04-01/Accounts/{account_sid}/Messages.json")
def list_messages(
    account_sid: str,
    To: Optional[str] = None,
    From: Optional[str] = None,
    Status: Optional[str] = None,
    PageSize: int = Query(50, ge=1, le=100),
):
    return twilio_data.list_messages(to=To, from_=From, status=Status, page_size=PageSize)


@app.get("/2010-04-01/Accounts/{account_sid}/Messages/{sid}.json")
def get_message(account_sid: str, sid: str):
    result = twilio_data.get_message(sid)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/2010-04-01/Accounts/{account_sid}/Messages.json", status_code=201)
def create_message(
    account_sid: str,
    To: str,
    From: str,
    Body: str = "",
):
    result = twilio_data.create_message(to=To, from_=From, body=Body)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Calls ---

@app.get("/2010-04-01/Accounts/{account_sid}/Calls.json")
def list_calls(
    account_sid: str,
    To: Optional[str] = None,
    From: Optional[str] = None,
    Status: Optional[str] = None,
    PageSize: int = Query(50, ge=1, le=100),
):
    return twilio_data.list_calls(to=To, from_=From, status=Status, page_size=PageSize)


@app.post("/2010-04-01/Accounts/{account_sid}/Calls.json", status_code=201)
def create_call(
    account_sid: str,
    To: str,
    From: str,
):
    result = twilio_data.create_call(to=To, from_=From)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Incoming phone numbers ---

@app.get("/2010-04-01/Accounts/{account_sid}/IncomingPhoneNumbers.json")
def list_phone_numbers(
    account_sid: str,
    PhoneNumber: Optional[str] = None,
    PageSize: int = Query(50, ge=1, le=100),
):
    return twilio_data.list_phone_numbers(phone_number=PhoneNumber, page_size=PageSize)


# --- Lookup ---

@app.get("/v1/PhoneNumbers/{phone_number}")
def lookup(phone_number: str):
    return twilio_data.lookup(phone_number)
