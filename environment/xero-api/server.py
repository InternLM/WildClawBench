"""FastAPI server wrapping xero_data as REST endpoints.

Mirrors a subset of the Xero Accounting API. Base path: /api.xro/2.0
Collections are wrapped under a PascalCase key like {"Invoices": [...]} as in
the real Xero API.
"""

from fastapi import FastAPI, Body, Query
from fastapi.responses import JSONResponse
from typing import Optional

import xero_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Xero Accounting API (Mock)", version="2.0")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Invoices ---

@app.get("/api.xro/2.0/Invoices")
def list_invoices(
    Status: Optional[str] = None,
    Type: Optional[str] = None,
):
    return xero_data.list_invoices(status=Status, type_=Type)


@app.get("/api.xro/2.0/Invoices/{invoice_id}")
def get_invoice(invoice_id: str):
    result = xero_data.get_invoice(invoice_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/api.xro/2.0/Invoices", status_code=200)
def create_invoice(body: dict = Body(...)):
    invoices = body.get("Invoices")
    payload = invoices[0] if isinstance(invoices, list) and invoices else body
    contact = payload.get("Contact") or {}
    contact_id = contact.get("ContactID")
    if not contact_id:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid request", "message": "Contact.ContactID is required"},
        )
    result = xero_data.create_invoice(
        contact_id=contact_id,
        line_items=payload.get("LineItems"),
        type_=payload.get("Type", "ACCREC"),
        date=payload.get("Date"),
        due_date=payload.get("DueDate"),
        status=payload.get("Status", "DRAFT"),
        reference=payload.get("Reference", ""),
        currency_code=payload.get("CurrencyCode", "USD"),
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Contacts ---

@app.get("/api.xro/2.0/Contacts")
def list_contacts():
    return xero_data.list_contacts()


# --- Accounts ---

@app.get("/api.xro/2.0/Accounts")
def list_accounts():
    return xero_data.list_accounts()
