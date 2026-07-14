"""FastAPI server wrapping amazon_seller_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

import amazon_seller_data
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

app = FastAPI(title="Amazon Selling Partner API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=amazon_seller_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Seller Account ---

@app.get("/sellers/v1/account")
def get_seller_account():
    return amazon_seller_data.get_seller_account()


@app.get("/sellers/v1/account/health")
def get_account_health():
    return amazon_seller_data.get_account_health()


@app.get("/sellers/v1/buying-notes")
def get_buying_notes():
    return amazon_seller_data.get_buying_notes()


@app.get("/notifications/v1/notifications")
def get_performance_notifications(
    severity: Optional[str] = Query(default=None),
):
    return amazon_seller_data.get_performance_notifications(severity=severity)


# --- Catalog Items ---

@app.get("/catalog/2022-04-01/items")
def search_catalog_items(
    keywords: Optional[str] = Query(default=None),
    identifiers: Optional[str] = Query(default=None),
    identifiersType: Optional[str] = Query(default=None),
    pageSize: int = Query(default=10, ge=1, le=20),
    marketplaceIds: str = Query(default="ATVPDKIKX0DER"),
    includedData: Optional[str] = Query(default="summaries"),
):
    return amazon_seller_data.search_catalog_items(
        keywords=keywords,
        identifiers=identifiers,
        identifiers_type=identifiersType,
        page_size=pageSize,
    )


@app.get("/catalog/2022-04-01/items/{asin}")
def get_catalog_item(
    asin: str,
    marketplaceIds: str = Query(default="ATVPDKIKX0DER"),
    includedData: Optional[str] = Query(default="summaries"),
):
    result = amazon_seller_data.get_catalog_item(asin)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Listings Items ---

@app.get("/listings/2021-08-01/items/{sellerId}/{sku}")
def get_listing_item(
    sellerId: str,
    sku: str,
    marketplaceIds: str = Query(default="ATVPDKIKX0DER"),
    includedData: Optional[str] = Query(default="attributes,issues"),
):
    result = amazon_seller_data.get_listing_item(sellerId, sku)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ListingCreateBody(BaseModel):
    productType: str
    title: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    bulletPoints: Optional[List[str]] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    fulfillmentChannel: Optional[str] = None
    condition: Optional[str] = None
    mainImageUrl: Optional[str] = None
    category: Optional[str] = None
    asin: Optional[str] = None
    itemWeight: Optional[float] = None
    itemWeightUnit: Optional[str] = None
    itemLength: Optional[float] = None
    itemWidth: Optional[float] = None
    itemHeight: Optional[float] = None
    itemDimensionsUnit: Optional[str] = None


@app.put("/listings/2021-08-01/items/{sellerId}/{sku}", status_code=200)
def put_listing_item(sellerId: str, sku: str, body: ListingCreateBody):
    existing = amazon_seller_data.get_listing_item(sellerId, sku)
    if "error" in existing:
        result = amazon_seller_data.create_listing_item(sellerId, sku, body.model_dump())
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        return JSONResponse(status_code=201, content=result)
    else:
        data = {k: v for k, v in body.model_dump().items() if v is not None}
        result = amazon_seller_data.update_listing_item(sellerId, sku, data)
        if "error" in result:
            return JSONResponse(status_code=400, content=result)
        return result


class ListingPatchBody(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    bulletPoints: Optional[List[str]] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    fulfillmentChannel: Optional[str] = None
    status: Optional[str] = None
    condition: Optional[str] = None
    mainImageUrl: Optional[str] = None
    category: Optional[str] = None


@app.patch("/listings/2021-08-01/items/{sellerId}/{sku}")
def patch_listing_item(sellerId: str, sku: str, body: ListingPatchBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = amazon_seller_data.update_listing_item(sellerId, sku, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/listings/2021-08-01/items/{sellerId}/{sku}")
def delete_listing_item(
    sellerId: str,
    sku: str,
    marketplaceIds: str = Query(default="ATVPDKIKX0DER"),
):
    result = amazon_seller_data.delete_listing_item(sellerId, sku)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Orders ---

@app.get("/orders/v0/orders")
def get_orders(
    CreatedAfter: Optional[str] = Query(default=None),
    CreatedBefore: Optional[str] = Query(default=None),
    OrderStatuses: Optional[str] = Query(default=None),
    FulfillmentChannels: Optional[str] = Query(default=None),
    MarketplaceIds: str = Query(default="ATVPDKIKX0DER"),
    MaxResultsPerPage: int = Query(default=100, ge=1, le=100),
):
    return amazon_seller_data.get_orders(
        created_after=CreatedAfter,
        created_before=CreatedBefore,
        order_statuses=OrderStatuses,
        fulfillment_channels=FulfillmentChannels,
        max_results=MaxResultsPerPage,
    )


@app.get("/orders/v0/orders/{orderId}")
def get_order(orderId: str):
    result = amazon_seller_data.get_order(orderId)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/orders/v0/orders/{orderId}/orderItems")
def get_order_items(orderId: str):
    result = amazon_seller_data.get_order_items(orderId)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ShipmentConfirmationBody(BaseModel):
    packageReferenceId: Optional[str] = None
    carrierCode: Optional[str] = None
    trackingNumber: Optional[str] = None
    shipDate: Optional[str] = None


@app.post("/orders/v0/orders/{orderId}/shipmentConfirmation")
def confirm_shipment(orderId: str, body: ShipmentConfirmationBody):
    result = amazon_seller_data.confirm_shipment(orderId, body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Inventory ---

@app.get("/fba/inventory/v1/summaries")
def get_inventory_summaries(
    sellerSkus: Optional[str] = Query(default=None),
    granularityType: str = Query(default="Marketplace"),
    granularityId: str = Query(default="ATVPDKIKX0DER"),
    marketplaceIds: str = Query(default="ATVPDKIKX0DER"),
):
    return amazon_seller_data.get_inventory_summaries(
        seller_skus=sellerSkus,
        granularity_type=granularityType,
        marketplace_id=granularityId,
    )


class InventoryUpdateBody(BaseModel):
    sellerSku: str
    quantity: int


@app.put("/fba/inventory/v1/items/{sellerSku}")
def update_inventory(sellerSku: str, body: InventoryUpdateBody):
    result = amazon_seller_data.update_inventory(sellerSku, body.quantity)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Reports ---

@app.get("/reports/2021-06-30/reports")
def get_reports(
    reportTypes: Optional[str] = Query(default=None),
    processingStatuses: Optional[str] = Query(default=None),
):
    return amazon_seller_data.get_reports(
        report_types=reportTypes,
        processing_statuses=processingStatuses,
    )


@app.get("/reports/2021-06-30/reports/{reportId}")
def get_report(reportId: str):
    result = amazon_seller_data.get_report(reportId)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ReportCreateBody(BaseModel):
    reportType: str
    dataStartTime: str
    dataEndTime: str
    marketplaceIds: Optional[List[str]] = None


@app.post("/reports/2021-06-30/reports", status_code=202)
def create_report(body: ReportCreateBody):
    result = amazon_seller_data.create_report(
        body.reportType, body.dataStartTime, body.dataEndTime,
    )
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Product Pricing ---

@app.get("/products/pricing/v0/competitivePrice")
def get_competitive_pricing(
    Asin: Optional[str] = Query(default=None),
    Sku: Optional[str] = Query(default=None),
    MarketplaceId: str = Query(default="ATVPDKIKX0DER"),
    ItemType: str = Query(default="Asin"),
):
    result = amazon_seller_data.get_competitive_pricing(asin=Asin, sku=Sku)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/products/pricing/v0/items/{Asin}/offers")
def get_item_offers(
    Asin: str,
    MarketplaceId: str = Query(default="ATVPDKIKX0DER"),
    ItemCondition: str = Query(default="New"),
):
    result = amazon_seller_data.get_item_offers(Asin)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Returns ---

@app.get("/returns/v0/returns")
def get_returns(
    status: Optional[str] = Query(default=None),
    orderId: Optional[str] = Query(default=None),
):
    return amazon_seller_data.get_returns(status=status, order_id=orderId)


@app.get("/returns/v0/returns/{returnId}")
def get_return(returnId: str):
    result = amazon_seller_data.get_return(returnId)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.post("/returns/v0/returns/{returnId}/authorize")
def authorize_return(returnId: str):
    result = amazon_seller_data.authorize_return(returnId)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


@app.post("/returns/v0/returns/{returnId}/close")
def close_return(returnId: str):
    result = amazon_seller_data.close_return(returnId)
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result
