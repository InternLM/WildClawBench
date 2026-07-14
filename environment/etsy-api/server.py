"""FastAPI server wrapping etsy_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import etsy_data
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

app = FastAPI(title="Etsy Open API v3 (Mock)", version="3.0.0")
install_tracker(app)
install_admin_plane(app, store=etsy_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- User ---

@app.get("/v3/application/users/me")
def get_current_user():
    return etsy_data.get_current_user()


# --- Shop ---

@app.get("/v3/application/shops/{shop_id}")
def get_shop(shop_id: int):
    result = etsy_data.get_shop(shop_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ShopUpdateBody(BaseModel):
    title: Optional[str] = None
    announcement: Optional[str] = None
    sale_message: Optional[str] = None
    is_vacation: Optional[bool] = None
    vacation_message: Optional[str] = None
    accepts_custom_requests: Optional[bool] = None
    policy_welcome: Optional[str] = None
    policy_payment: Optional[str] = None
    policy_shipping: Optional[str] = None
    policy_refunds: Optional[str] = None


@app.put("/v3/application/shops/{shop_id}")
def update_shop(shop_id: int, body: ShopUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = etsy_data.update_shop(shop_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Shop Sections ---

@app.get("/v3/application/shops/{shop_id}/sections")
def list_shop_sections(shop_id: int):
    result = etsy_data.list_shop_sections(shop_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v3/application/shops/{shop_id}/sections/{section_id}")
def get_shop_section(shop_id: int, section_id: int):
    result = etsy_data.get_shop_section(shop_id, section_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Listings ---

@app.get("/v3/application/shops/{shop_id}/listings")
def list_listings(
    shop_id: int,
    state: Optional[str] = Query(default="active"),
    sort_on: Optional[str] = Query(default="created"),
    sort_order: Optional[str] = Query(default="desc"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    section_id: Optional[int] = Query(default=None),
    q: Optional[str] = Query(default=None),
):
    return etsy_data.list_listings(
        shop_id=shop_id, state=state, sort_on=sort_on, sort_order=sort_order,
        limit=limit, offset=offset, section_id=section_id, q=q,
    )


@app.get("/v3/application/listings/{listing_id}")
def get_listing(listing_id: int):
    result = etsy_data.get_listing(listing_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ListingCreateBody(BaseModel):
    title: str
    description: str
    price: float
    quantity: int
    who_made: str
    when_made: str
    taxonomy_id: int
    tags: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    shop_section_id: Optional[int] = None
    shipping_profile_id: Optional[int] = None
    return_policy_id: Optional[int] = None
    processing_min: Optional[int] = None
    processing_max: Optional[int] = None
    item_weight: Optional[float] = None
    item_weight_unit: Optional[str] = None
    item_length: Optional[float] = None
    item_width: Optional[float] = None
    item_height: Optional[float] = None
    item_dimensions_unit: Optional[str] = None
    is_supply: Optional[bool] = False
    is_customizable: Optional[bool] = False
    is_personalizable: Optional[bool] = False


@app.post("/v3/application/shops/{shop_id}/listings", status_code=201)
def create_listing(shop_id: int, body: ListingCreateBody):
    result = etsy_data.create_listing(shop_id, body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class ListingUpdateBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    tags: Optional[List[str]] = None
    materials: Optional[List[str]] = None
    state: Optional[str] = None
    who_made: Optional[str] = None
    when_made: Optional[str] = None
    taxonomy_id: Optional[int] = None
    shop_section_id: Optional[int] = None
    shipping_profile_id: Optional[int] = None
    return_policy_id: Optional[int] = None
    processing_min: Optional[int] = None
    processing_max: Optional[int] = None
    item_weight: Optional[float] = None
    item_weight_unit: Optional[str] = None
    item_length: Optional[float] = None
    item_width: Optional[float] = None
    item_height: Optional[float] = None
    item_dimensions_unit: Optional[str] = None
    is_supply: Optional[bool] = None
    is_customizable: Optional[bool] = None
    is_personalizable: Optional[bool] = None


@app.put("/v3/application/listings/{listing_id}")
def update_listing(listing_id: int, body: ListingUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = etsy_data.update_listing(listing_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v3/application/listings/{listing_id}")
def delete_listing(listing_id: int):
    result = etsy_data.delete_listing(listing_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Listing Images ---

@app.get("/v3/application/listings/{listing_id}/images")
def list_listing_images(listing_id: int):
    result = etsy_data.list_listing_images(listing_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v3/application/listings/{listing_id}/images/{image_id}")
def get_listing_image(listing_id: int, image_id: int):
    result = etsy_data.get_listing_image(listing_id, image_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v3/application/listings/{listing_id}/images/{image_id}")
def delete_listing_image(listing_id: int, image_id: int):
    result = etsy_data.delete_listing_image(listing_id, image_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Receipts (Orders) ---

@app.get("/v3/application/shops/{shop_id}/receipts")
def list_receipts(
    shop_id: int,
    status: Optional[str] = Query(default=None),
    min_created: Optional[str] = Query(default=None),
    max_created: Optional[str] = Query(default=None),
    sort_on: Optional[str] = Query(default="created"),
    sort_order: Optional[str] = Query(default="desc"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    was_shipped: Optional[bool] = Query(default=None),
    was_paid: Optional[bool] = Query(default=None),
):
    return etsy_data.list_receipts(
        shop_id=shop_id, status=status, min_created=min_created,
        max_created=max_created, sort_on=sort_on, sort_order=sort_order,
        limit=limit, offset=offset, was_shipped=was_shipped, was_paid=was_paid,
    )


@app.get("/v3/application/shops/{shop_id}/receipts/{receipt_id}")
def get_receipt(shop_id: int, receipt_id: int):
    result = etsy_data.get_receipt(receipt_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ReceiptUpdateBody(BaseModel):
    shipping_carrier: Optional[str] = None
    tracking_code: Optional[str] = None
    was_shipped: Optional[bool] = None


@app.put("/v3/application/shops/{shop_id}/receipts/{receipt_id}")
def update_receipt(shop_id: int, receipt_id: int, body: ReceiptUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = etsy_data.update_receipt(receipt_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Transactions ---

@app.get("/v3/application/shops/{shop_id}/receipts/{receipt_id}/transactions")
def list_receipt_transactions(shop_id: int, receipt_id: int):
    result = etsy_data.list_receipt_transactions(receipt_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/v3/application/shops/{shop_id}/transactions/{transaction_id}")
def get_transaction(shop_id: int, transaction_id: int):
    result = etsy_data.get_transaction(transaction_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Reviews ---

@app.get("/v3/application/shops/{shop_id}/reviews")
def list_shop_reviews(
    shop_id: int,
    listing_id: Optional[int] = Query(default=None),
    min_rating: Optional[int] = Query(default=None, ge=1, le=5),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return etsy_data.list_reviews(
        shop_id=shop_id, listing_id=listing_id, min_rating=min_rating,
        limit=limit, offset=offset,
    )


@app.get("/v3/application/listings/{listing_id}/reviews")
def list_listing_reviews(
    listing_id: int,
    min_rating: Optional[int] = Query(default=None, ge=1, le=5),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return etsy_data.list_reviews(
        listing_id=listing_id, min_rating=min_rating,
        limit=limit, offset=offset,
    )


# --- Shipping Profiles ---

@app.get("/v3/application/shops/{shop_id}/shipping-profiles")
def list_shipping_profiles(shop_id: int):
    return etsy_data.list_shipping_profiles(shop_id)


@app.get("/v3/application/shops/{shop_id}/shipping-profiles/{profile_id}")
def get_shipping_profile(shop_id: int, profile_id: int):
    result = etsy_data.get_shipping_profile(shop_id, profile_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Return Policies ---

@app.get("/v3/application/shops/{shop_id}/return-policies")
def list_return_policies(shop_id: int):
    return etsy_data.list_return_policies(shop_id)


@app.get("/v3/application/shops/{shop_id}/return-policies/{policy_id}")
def get_return_policy(shop_id: int, policy_id: int):
    result = etsy_data.get_return_policy(shop_id, policy_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
