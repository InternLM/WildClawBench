"""FastAPI server wrapping instacart_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import instacart_data
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

app = FastAPI(title="Instacart API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=instacart_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- User ---

@app.get("/v1/users/me")
def get_user():
    return instacart_data.get_user()


# --- Retailers ---

@app.get("/v1/retailers")
def list_retailers(zip_code: Optional[str] = Query(None, alias="zip")):
    return instacart_data.list_retailers(zip_code=zip_code)


@app.get("/v1/retailers/{retailer_id}")
def get_retailer(retailer_id: str):
    result = instacart_data.get_retailer(retailer_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Products ---

@app.get("/v1/products")
def search_products(
    retailer_id: Optional[str] = None,
    q: Optional[str] = None,
    category: Optional[str] = None,
    in_stock_only: bool = True,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return instacart_data.search_products(
        retailer_id=retailer_id, query=q, category=category,
        in_stock_only=in_stock_only, limit=limit, offset=offset,
    )


@app.get("/v1/products/{product_id}")
def get_product(product_id: str):
    result = instacart_data.get_product(product_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Cart ---

class CartCreateBody(BaseModel):
    user_id: str
    retailer_id: str


@app.post("/v1/carts", status_code=201)
def create_cart(body: CartCreateBody):
    result = instacart_data.create_cart(body.user_id, body.retailer_id)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/v1/carts/{cart_id}")
def get_cart(cart_id: str):
    result = instacart_data.get_cart(cart_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CartItemBody(BaseModel):
    product_id: str
    quantity: int


@app.post("/v1/carts/{cart_id}/items")
def add_to_cart(cart_id: str, body: CartItemBody):
    result = instacart_data.add_to_cart(cart_id, body.product_id, body.quantity)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class CartItemUpdateBody(BaseModel):
    quantity: int


@app.patch("/v1/carts/{cart_id}/items/{product_id}")
def update_cart_item(cart_id: str, product_id: str, body: CartItemUpdateBody):
    result = instacart_data.update_cart_item(cart_id, product_id, body.quantity)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class CheckoutBody(BaseModel):
    tip: float = 0.0
    delivery_window_start: Optional[str] = None
    delivery_window_end: Optional[str] = None


@app.post("/v1/carts/{cart_id}/checkout", status_code=201)
def checkout(cart_id: str, body: CheckoutBody):
    result = instacart_data.checkout(
        cart_id, tip=body.tip,
        delivery_window_start=body.delivery_window_start,
        delivery_window_end=body.delivery_window_end,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Orders ---

@app.get("/v1/orders")
def list_orders(user_id: Optional[str] = None, status: Optional[str] = None):
    return instacart_data.list_orders(user_id=user_id, status=status)


@app.get("/v1/orders/{order_id}")
def get_order(order_id: str):
    result = instacart_data.get_order(order_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/v1/orders/{order_id}/cancel")
def cancel_order(order_id: str):
    result = instacart_data.cancel_order(order_id)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result
