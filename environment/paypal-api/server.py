"""FastAPI server wrapping paypal_data module as REST endpoints.

Implements a subset of the PayPal REST API (Orders v2, Payments v2,
Invoicing v2, Payouts v1). Amounts are Money objects with string values.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import paypal_data
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

app = FastAPI(title="PayPal API (Mock)", version="v2")
install_tracker(app)
install_admin_plane(app, store=paypal_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Checkout Orders ---

class Amount(BaseModel):
    currency_code: Optional[str] = "USD"
    value: str


class Payee(BaseModel):
    email_address: Optional[str] = "merchant@orbit-labs.com"


class PurchaseUnit(BaseModel):
    amount: Amount
    payee: Optional[Payee] = None
    description: Optional[str] = ""


class OrderCreateBody(BaseModel):
    intent: Optional[str] = "CAPTURE"
    purchase_units: List[PurchaseUnit]


@app.post("/v2/checkout/orders", status_code=201)
def create_order(body: OrderCreateBody):
    pu = body.purchase_units[0]
    payee_email = pu.payee.email_address if pu.payee else "merchant@orbit-labs.com"
    return paypal_data.create_order(
        intent=body.intent, amount_value=pu.amount.value,
        currency_code=pu.amount.currency_code, payee_email=payee_email,
        description=pu.description or "",
    )


@app.get("/v2/checkout/orders/{order_id}")
def get_order(order_id: str):
    result = paypal_data.get_order(order_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v2/checkout/orders/{order_id}/capture", status_code=201)
def capture_order(order_id: str):
    result = paypal_data.capture_order(order_id)
    if "error" in result:
        status = 404 if "not found" in result["error"] else 422
        return JSONResponse(status_code=status, content=result)
    return result


# --- Refunds ---

class RefundCreateBody(BaseModel):
    capture_id: str
    amount: Optional[Amount] = None
    note_to_payer: Optional[str] = None


@app.post("/v2/payments/refunds", status_code=201)
def create_refund(body: RefundCreateBody):
    amount_value = body.amount.value if body.amount else None
    currency = body.amount.currency_code if body.amount else "USD"
    result = paypal_data.create_refund(
        capture_id=body.capture_id, amount_value=amount_value,
        currency_code=currency, note_to_payer=body.note_to_payer,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v2/payments/refunds/{refund_id}")
def get_refund(refund_id: str):
    result = paypal_data.get_refund(refund_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Invoices ---

@app.get("/v2/invoicing/invoices")
def list_invoices(status: Optional[str] = None, page_size: int = Query(20, ge=1, le=100)):
    return paypal_data.list_invoices(status=status, page_size=page_size)


class InvoiceDetail(BaseModel):
    invoice_number: Optional[str] = None
    currency_code: Optional[str] = "USD"
    note: Optional[str] = None


class InvoiceRecipientEmail(BaseModel):
    email_address: str


class InvoiceRecipient(BaseModel):
    billing_info: InvoiceRecipientEmail


class InvoiceCreateBody(BaseModel):
    detail: Optional[InvoiceDetail] = None
    primary_recipients: Optional[List[InvoiceRecipient]] = None
    amount: Optional[Amount] = None
    due_date: Optional[str] = None


@app.post("/v2/invoicing/invoices", status_code=201)
def create_invoice(body: InvoiceCreateBody):
    detail = body.detail or InvoiceDetail()
    recipient = None
    if body.primary_recipients:
        recipient = body.primary_recipients[0].billing_info.email_address
    amount_value = body.amount.value if body.amount else "0.00"
    currency = body.amount.currency_code if body.amount else detail.currency_code
    return paypal_data.create_invoice(
        invoice_number=detail.invoice_number, recipient_email=recipient,
        amount_value=amount_value, currency_code=currency,
        due_date=body.due_date, note=detail.note,
    )


# --- Payouts ---

class PayoutSenderHeader(BaseModel):
    sender_batch_id: Optional[str] = None
    email_subject: Optional[str] = None


class PayoutItem(BaseModel):
    amount: Amount
    receiver: Optional[str] = None


class PayoutCreateBody(BaseModel):
    sender_batch_header: Optional[PayoutSenderHeader] = None
    items: List[PayoutItem]


@app.post("/v1/payments/payouts", status_code=201)
def create_payout(body: PayoutCreateBody):
    item = body.items[0]
    header = body.sender_batch_header or PayoutSenderHeader()
    return paypal_data.create_payout(
        sender_batch_id=header.sender_batch_id, amount_value=item.amount.value,
        currency_code=item.amount.currency_code, recipient_email=item.receiver,
        note=header.email_subject,
    )
