"""FastAPI server wrapping stripe_data module as REST endpoints.

Implements a subset of the Stripe API surface. Base path: /v1
Amounts are integer cents.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import stripe_data
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

app = FastAPI(title="Stripe API (Mock)", version="2024-06-20")
install_tracker(app)
install_admin_plane(app, store=stripe_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Customers ---

@app.get("/v1/customers")
def list_customers(limit: int = Query(10, ge=1, le=100), email: Optional[str] = None):
    return stripe_data.list_customers(limit=limit, email=email)


@app.get("/v1/customers/{customer_id}")
def get_customer(customer_id: str):
    result = stripe_data.get_customer(customer_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CustomerCreateBody(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    currency: Optional[str] = "usd"
    phone: Optional[str] = None


@app.post("/v1/customers", status_code=201)
def create_customer(body: CustomerCreateBody):
    return stripe_data.create_customer(
        name=body.name, email=body.email, description=body.description,
        currency=body.currency, phone=body.phone,
    )


# --- Products / Prices ---

@app.get("/v1/products")
def list_products(limit: int = Query(10, ge=1, le=100)):
    return stripe_data.list_products(limit=limit)


@app.get("/v1/prices")
def list_prices(limit: int = Query(10, ge=1, le=100), product: Optional[str] = None):
    return stripe_data.list_prices(limit=limit, product=product)


# --- Payment Intents ---

class PaymentIntentBody(BaseModel):
    amount: int
    currency: Optional[str] = "usd"
    customer: Optional[str] = None
    description: Optional[str] = None
    confirm: Optional[bool] = False


@app.post("/v1/payment_intents", status_code=201)
def create_payment_intent(body: PaymentIntentBody):
    result = stripe_data.create_payment_intent(
        amount=body.amount, currency=body.currency, customer=body.customer,
        description=body.description, confirm=body.confirm,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/v1/payment_intents/{pi_id}")
def get_payment_intent(pi_id: str):
    result = stripe_data.get_payment_intent(pi_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Charges ---

@app.get("/v1/charges")
def list_charges(limit: int = Query(10, ge=1, le=100), customer: Optional[str] = None):
    return stripe_data.list_charges(limit=limit, customer=customer)


@app.get("/v1/charges/{charge_id}")
def get_charge(charge_id: str):
    result = stripe_data.get_charge(charge_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ChargeCreateBody(BaseModel):
    amount: int
    currency: Optional[str] = "usd"
    customer: Optional[str] = None
    description: Optional[str] = None


@app.post("/v1/charges", status_code=201)
def create_charge(body: ChargeCreateBody):
    result = stripe_data.create_charge(
        amount=body.amount, currency=body.currency,
        customer=body.customer, description=body.description,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Refunds ---

class RefundCreateBody(BaseModel):
    charge: str
    amount: Optional[int] = None
    reason: Optional[str] = None


@app.post("/v1/refunds", status_code=201)
def create_refund(body: RefundCreateBody):
    result = stripe_data.create_refund(charge=body.charge, amount=body.amount, reason=body.reason)
    if "error" in result:
        status = 404 if "No such charge" in result["error"] else 400
        return JSONResponse(status_code=status, content=result)
    return result


# --- Invoices ---

@app.get("/v1/invoices")
def list_invoices(limit: int = Query(10, ge=1, le=100),
                  customer: Optional[str] = None, status: Optional[str] = None):
    return stripe_data.list_invoices(limit=limit, customer=customer, status=status)


@app.get("/v1/invoices/{invoice_id}")
def get_invoice(invoice_id: str):
    result = stripe_data.get_invoice(invoice_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class InvoiceCreateBody(BaseModel):
    customer: str
    amount_due: Optional[int] = 0
    currency: Optional[str] = "usd"
    subscription: Optional[str] = None


@app.post("/v1/invoices", status_code=201)
def create_invoice(body: InvoiceCreateBody):
    result = stripe_data.create_invoice(
        customer=body.customer, amount_due=body.amount_due,
        currency=body.currency, subscription=body.subscription,
    )
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Subscriptions ---

@app.get("/v1/subscriptions")
def list_subscriptions(limit: int = Query(10, ge=1, le=100),
                       customer: Optional[str] = None, status: Optional[str] = None):
    return stripe_data.list_subscriptions(limit=limit, customer=customer, status=status)


@app.get("/v1/subscriptions/{sub_id}")
def get_subscription(sub_id: str):
    result = stripe_data.get_subscription(sub_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class SubscriptionCreateBody(BaseModel):
    customer: str
    price: str
    quantity: Optional[int] = 1


@app.post("/v1/subscriptions", status_code=201)
def create_subscription(body: SubscriptionCreateBody):
    result = stripe_data.create_subscription(
        customer=body.customer, price=body.price, quantity=body.quantity,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Balance ---

@app.get("/v1/balance")
def get_balance():
    return stripe_data.get_balance()
