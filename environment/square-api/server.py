"""FastAPI server wrapping square_data module as REST endpoints.

Implements a subset of the Square API v2 surface. Base path: /v2
Amounts are integer cents inside Money objects {"amount", "currency"}.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import square_data
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:  # standalone run without the shared module on sys.path
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="Square API (Mock)", version="2024-06-04")
install_tracker(app)


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Merchant ---

@app.get("/v2/merchants/me")
def get_merchant():
    return square_data.get_merchant()


# --- Payments ---

@app.get("/v2/payments")
def list_payments(location_id: Optional[str] = None, limit: int = Query(50, ge=1, le=100)):
    return square_data.list_payments(location_id=location_id, limit=limit)


@app.get("/v2/payments/{payment_id}")
def get_payment(payment_id: str):
    result = square_data.get_payment(payment_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class Money(BaseModel):
    amount: int
    currency: Optional[str] = "USD"


class PaymentCreateBody(BaseModel):
    amount_money: Money
    source_id: Optional[str] = "cnon:card-nonce-ok"
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    location_id: Optional[str] = "LOC_MAIN"


@app.post("/v2/payments", status_code=201)
def create_payment(body: PaymentCreateBody):
    result = square_data.create_payment(
        amount=body.amount_money.amount, currency=body.amount_money.currency,
        source_id=body.source_id, customer_id=body.customer_id,
        order_id=body.order_id, location_id=body.location_id,
    )
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Refunds ---

class RefundCreateBody(BaseModel):
    payment_id: str
    amount_money: Optional[Money] = None
    reason: Optional[str] = None


@app.post("/v2/refunds", status_code=201)
def create_refund(body: RefundCreateBody):
    amount = body.amount_money.amount if body.amount_money else None
    currency = body.amount_money.currency if body.amount_money else "USD"
    result = square_data.create_refund(
        payment_id=body.payment_id, amount=amount, currency=currency, reason=body.reason,
    )
    if "error" in result:
        status = 404 if "not found" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Customers ---

@app.get("/v2/customers")
def list_customers(limit: int = Query(50, ge=1, le=100)):
    return square_data.list_customers(limit=limit)


@app.get("/v2/customers/{customer_id}")
def get_customer(customer_id: str):
    result = square_data.get_customer(customer_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CustomerCreateBody(BaseModel):
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None


@app.post("/v2/customers", status_code=201)
def create_customer(body: CustomerCreateBody):
    return square_data.create_customer(
        given_name=body.given_name, family_name=body.family_name,
        email_address=body.email_address, phone_number=body.phone_number,
        company_name=body.company_name,
    )


# --- Catalog ---

@app.get("/v2/catalog/list")
def list_catalog(types: Optional[str] = None):
    return square_data.list_catalog(types=types)


# --- Orders ---

class OrderLineItem(BaseModel):
    catalog_object_id: str
    quantity: Optional[int] = 1


class OrderCreateBody(BaseModel):
    customer_id: Optional[str] = None
    location_id: Optional[str] = "LOC_MAIN"
    line_items: List[OrderLineItem] = []


@app.post("/v2/orders", status_code=201)
def create_order(body: OrderCreateBody):
    return square_data.create_order(
        customer_id=body.customer_id, location_id=body.location_id,
        line_items=[li.model_dump() for li in body.line_items],
    )


@app.get("/v2/orders/{order_id}")
def get_order(order_id: str):
    result = square_data.get_order(order_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Inventory ---

@app.get("/v2/inventory/{catalog_object_id}")
def get_inventory(catalog_object_id: str):
    result = square_data.get_inventory(catalog_object_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
