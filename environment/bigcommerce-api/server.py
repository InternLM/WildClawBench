"""FastAPI server wrapping bigcommerce_data module as REST endpoints.

Mirrors a subset of the BigCommerce APIs: Catalog/Customers (v3) and Orders
(v2). v3 list endpoints wrap data in `{"data": [...], "meta": {...}}`.
"""

from fastapi import FastAPI, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional

import bigcommerce_data
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

app = FastAPI(title="BigCommerce API (Mock)", version="v3")
install_tracker(app)
install_admin_plane(app, store=bigcommerce_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Catalog / Products (v3) ---

@app.get("/v3/catalog/products")
def list_products(
    name: Optional[str] = None,
    sku: Optional[str] = None,
    is_visible: Optional[bool] = None,
    page: int = Query(1),
    limit: int = Query(50),
):
    return bigcommerce_data.list_products(
        name=name, sku=sku, is_visible=is_visible, page=page, limit=limit,
    )


@app.get("/v3/catalog/products/{product_id}")
def get_product(product_id: int):
    result = bigcommerce_data.get_product(product_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Orders (v2) ---

@app.get("/v2/orders")
def list_orders(
    customer_id: Optional[int] = None,
    status_id: Optional[int] = None,
    page: int = Query(1),
    limit: int = Query(50),
):
    return bigcommerce_data.list_orders(
        customer_id=customer_id, status_id=status_id, page=page, limit=limit,
    )


@app.get("/v2/orders/{order_id}")
def get_order(order_id: int):
    result = bigcommerce_data.get_order(order_id)
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v2/orders", status_code=200)
def create_order(body: Optional[dict] = Body(default=None)):
    body = body or {}
    result = bigcommerce_data.create_order(
        customer_id=body.get("customer_id", 0),
        status_id=body.get("status_id", 1),
        payment_method=body.get("payment_method", "manual"),
        currency_code=body.get("currency_code", "USD"),
        billing_address=body.get("billing_address"),
        products=body.get("products"),
    )
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Customers (v3) ---

@app.get("/v3/customers")
def list_customers(
    email: Optional[str] = None,
    company: Optional[str] = None,
    page: int = Query(1),
    limit: int = Query(50),
):
    return bigcommerce_data.list_customers(
        email=email, company=company, page=page, limit=limit,
    )
