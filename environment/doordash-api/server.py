"""FastAPI server wrapping doordash_data module as REST endpoints.

Implements a subset of a food-delivery API surface. Base path: /v1
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import doordash_data
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

app = FastAPI(title="DoorDash API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=doordash_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Stores ---

@app.get("/v1/stores")
def list_stores(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    cuisine: Optional[str] = None,
    open_only: bool = False,
):
    return doordash_data.list_stores(
        latitude=latitude, longitude=longitude, cuisine=cuisine, open_only=open_only)


@app.get("/v1/stores/{store_id}")
def get_store(store_id: str):
    result = doordash_data.get_store(store_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v1/stores/{store_id}/menu")
def get_menu(store_id: str):
    result = doordash_data.get_menu(store_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Carts ---

class CartCreateBody(BaseModel):
    store_id: str


@app.post("/v1/carts", status_code=201)
def create_cart(body: CartCreateBody):
    result = doordash_data.create_cart(body.store_id)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.get("/v1/carts/{cart_id}")
def get_cart(cart_id: str):
    result = doordash_data.get_cart(cart_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class CartItemBody(BaseModel):
    item_id: str
    quantity: int = 1


@app.post("/v1/carts/{cart_id}/items")
def add_cart_item(cart_id: str, body: CartItemBody):
    result = doordash_data.add_cart_item(cart_id, body.item_id, body.quantity)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class CheckoutBody(BaseModel):
    customer_name: str = "Guest"
    tip: float = 0.0


@app.post("/v1/carts/{cart_id}/checkout", status_code=201)
def checkout(cart_id: str, body: CheckoutBody):
    result = doordash_data.checkout(cart_id, customer_name=body.customer_name, tip=body.tip)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Orders ---

@app.get("/v1/orders/{order_id}")
def get_order(order_id: str):
    result = doordash_data.get_order(order_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
