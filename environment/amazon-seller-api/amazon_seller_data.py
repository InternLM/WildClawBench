"""Data access module for Amazon Selling Partner API simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_catalog_items(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "price": float(r["price"]),
            "quantity": int(r["quantity"]),
            "itemWeight": float(r["itemWeight"]) if r["itemWeight"] else None,
            "itemLength": float(r["itemLength"]) if r["itemLength"] else None,
            "itemWidth": float(r["itemWidth"]) if r["itemWidth"] else None,
            "itemHeight": float(r["itemHeight"]) if r["itemHeight"] else None,
            "bulletPoints": r["bulletPoints"].split("|") if r["bulletPoints"] else [],
        })
    return out


def _coerce_orders(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "OrderTotal_Amount": float(r["OrderTotal_Amount"]),
            "NumberOfItemsShipped": int(r["NumberOfItemsShipped"]),
            "NumberOfItemsUnshipped": int(r["NumberOfItemsUnshipped"]),
            "IsPrime": r["IsPrime"].lower() == "true",
            "IsBusinessOrder": r["IsBusinessOrder"].lower() == "true",
            "IsSoldByAB": r["IsSoldByAB"].lower() == "true",
        })
    return out


def _coerce_order_items(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "QuantityOrdered": int(r["QuantityOrdered"]),
            "QuantityShipped": int(r["QuantityShipped"]),
            "ItemPrice_Amount": float(r["ItemPrice_Amount"]),
            "ItemTax_Amount": float(r["ItemTax_Amount"]),
            "PromotionDiscount_Amount": float(r["PromotionDiscount_Amount"]),
            "IsGift": r["IsGift"].lower() == "true",
        })
    return out


def _coerce_inventory(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "totalQuantity": int(r["totalQuantity"]),
            "inStockSupplyQuantity": int(r["inStockSupplyQuantity"]),
            "inboundWorkingQuantity": int(r["inboundWorkingQuantity"]),
            "inboundShippedQuantity": int(r["inboundShippedQuantity"]),
            "inboundReceivingQuantity": int(r["inboundReceivingQuantity"]),
            "reservedQuantity": int(r["reservedQuantity"]),
            "unfulfillableQuantity": int(r["unfulfillableQuantity"]),
        })
    return out


def _coerce_returns(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "returnQuantity": int(r["returnQuantity"]),
            "refundAmount": float(r["refundAmount"]),
        })
    return out


def _coerce_reports(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "processingEndTime": r["processingEndTime"] if r["processingEndTime"] else None,
            "reportDocumentId": r["reportDocumentId"] if r["reportDocumentId"] else None,
        })
    return out


def _coerce_pricing(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "competitivePrice_Amount": float(r["competitivePrice_Amount"]),
            "listingPrice_Amount": float(r["listingPrice_Amount"]),
            "landedPrice_Amount": float(r["landedPrice_Amount"]),
            "shipping_Amount": float(r["shipping_Amount"]),
            "numberOfOffers": int(r["numberOfOffers"]),
            "buyBoxPrice_Amount": float(r["buyBoxPrice_Amount"]),
            "buyBoxWinner": r["buyBoxWinner"].lower() == "true",
        })
    return out


# Load all data at module init
_catalog_items = _coerce_catalog_items(_load("catalog_items.csv"))
_orders = _coerce_orders(_load("orders.csv"))
_order_items = _coerce_order_items(_load("order_items.csv"))
_inventory = _coerce_inventory(_load("inventory.csv"))
_returns = _coerce_returns(_load("returns.csv"))
_reports = _coerce_reports(_load("reports.csv"))
_pricing = _coerce_pricing(_load("pricing.csv"))

with open(DATA_DIR / "seller_account.json", encoding="utf-8") as _f:
    _seller_account = json.load(_f)

# Mutable in-memory stores
_catalog_store = deepcopy(_catalog_items)
_orders_store = deepcopy(_orders)
_order_items_store = deepcopy(_order_items)
_inventory_store = deepcopy(_inventory)
_returns_store = deepcopy(_returns)
_reports_store = deepcopy(_reports)
_pricing_store = deepcopy(_pricing)
_seller_store = deepcopy(_seller_account)

_next_report_id = 11
_next_return_id = 6


# ---------------------------------------------------------------------------
# Seller Account
# ---------------------------------------------------------------------------

def get_seller_account():
    return {"type": "seller_account", "seller": _seller_store}


def get_account_health():
    return {"type": "account_health", "accountHealth": _seller_store["accountHealth"]}


def get_performance_notifications(severity=None):
    results = list(_seller_store["performanceNotifications"])
    if severity:
        results = [n for n in results if n["severity"].upper() == severity.upper()]
    return {"type": "notifications", "count": len(results), "results": results}


# ---------------------------------------------------------------------------
# Catalog Items / Listings
# ---------------------------------------------------------------------------

def search_catalog_items(
    keywords=None,
    identifiers=None,
    identifiers_type=None,
    page_size=10,
    status=None,
):
    results = list(_catalog_store)

    if status:
        results = [r for r in results if r["status"].upper() == status.upper()]
    if identifiers:
        id_list = [i.strip() for i in identifiers.split(",")]
        if identifiers_type and identifiers_type.upper() == "ASIN":
            results = [r for r in results if r["asin"] in id_list]
        elif identifiers_type and identifiers_type.upper() == "SKU":
            results = [r for r in results if r["sku"] in id_list]
        else:
            results = [r for r in results if r["asin"] in id_list or r["sku"] in id_list]
    elif keywords:
        kw = keywords.lower()
        results = [r for r in results if kw in r["title"].lower() or kw in r["description"].lower()]

    total = len(results)
    page_results = results[:page_size]
    return {
        "type": "catalog_items",
        "numberOfResults": total,
        "pagination": {"nextToken": None, "previousToken": None},
        "items": [_format_catalog_item(item) for item in page_results],
    }


def _format_catalog_item(item):
    return {
        "asin": item["asin"],
        "attributes": {
            "item_name": [{"value": item["title"], "marketplace_id": "ATVPDKIKX0DER"}],
            "brand": [{"value": item["brand"], "marketplace_id": "ATVPDKIKX0DER"}],
            "bullet_point": [{"value": bp, "marketplace_id": "ATVPDKIKX0DER"} for bp in (item["bulletPoints"] or [])],
            "list_price": [{"currency": item["currency"], "value": item["price"], "marketplace_id": "ATVPDKIKX0DER"}],
            "item_weight": [{"unit": item["itemWeightUnit"], "value": item["itemWeight"], "marketplace_id": "ATVPDKIKX0DER"}] if item["itemWeight"] else [],
            "item_dimensions": [{
                "length": {"unit": item["itemDimensionsUnit"], "value": item["itemLength"]},
                "width": {"unit": item["itemDimensionsUnit"], "value": item["itemWidth"]},
                "height": {"unit": item["itemDimensionsUnit"], "value": item["itemHeight"]},
                "marketplace_id": "ATVPDKIKX0DER",
            }] if item["itemLength"] else [],
            "condition_type": [{"value": item["condition"], "marketplace_id": "ATVPDKIKX0DER"}],
            "product_type": [{"value": item["productType"], "marketplace_id": "ATVPDKIKX0DER"}],
        },
        "images": [{"marketplaceId": "ATVPDKIKX0DER", "images": [{"variant": "MAIN", "link": item["mainImageUrl"], "height": 1000, "width": 1000}]}],
        "salesRanks": [{"marketplaceId": "ATVPDKIKX0DER", "classificationRanks": [{"classificationId": "172282", "title": "Electronics", "rank": 5420}]}],
        "summaries": [{
            "marketplaceId": "ATVPDKIKX0DER",
            "brandName": item["brand"],
            "itemName": item["title"],
            "productType": item["productType"],
            "itemClassification": "BASE_PRODUCT",
        }],
    }


def get_catalog_item(asin):
    for item in _catalog_store:
        if item["asin"] == asin:
            return {"type": "catalog_item", "item": _format_catalog_item(item)}
    return {"error": f"Item with ASIN {asin} not found"}


def get_listing_item(seller_id, sku):
    for item in _catalog_store:
        if item["sku"] == sku and item["sellerId"] == seller_id:
            return {"type": "listing_item", "listing": {
                "sku": item["sku"],
                "asin": item["asin"],
                "sellerId": item["sellerId"],
                "productType": item["productType"],
                "status": item["status"],
                "fulfillmentChannel": item["fulfillmentChannel"],
                "createdDate": item["createdDate"],
                "lastUpdatedDate": item["lastUpdatedDate"],
                "attributes": {
                    "item_name": [{"value": item["title"], "marketplace_id": "ATVPDKIKX0DER"}],
                    "description": [{"value": item["description"], "marketplace_id": "ATVPDKIKX0DER"}],
                    "brand": [{"value": item["brand"], "marketplace_id": "ATVPDKIKX0DER"}],
                    "bullet_point": [{"value": bp, "marketplace_id": "ATVPDKIKX0DER"} for bp in (item["bulletPoints"] or [])],
                    "list_price": [{"currency": item["currency"], "value": item["price"], "marketplace_id": "ATVPDKIKX0DER"}],
                    "quantity": [{"value": item["quantity"], "marketplace_id": "ATVPDKIKX0DER"}],
                    "fulfillment_channel": [{"value": item["fulfillmentChannel"], "marketplace_id": "ATVPDKIKX0DER"}],
                    "condition_type": [{"value": item["condition"], "marketplace_id": "ATVPDKIKX0DER"}],
                    "main_image": [{"link": item["mainImageUrl"], "marketplace_id": "ATVPDKIKX0DER"}],
                },
                "issues": [],
            }}
    return {"error": f"Listing with SKU {sku} not found for seller {seller_id}"}


def create_listing_item(seller_id, sku, data):
    for item in _catalog_store:
        if item["sku"] == sku and item["sellerId"] == seller_id:
            return {"error": f"Listing with SKU {sku} already exists"}

    now = _now()
    new_item = {
        "sku": sku,
        "asin": data.get("asin", f"B0NEW{len(_catalog_store):05d}"),
        "sellerId": seller_id,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "brand": data.get("brand", ""),
        "bulletPoints": data.get("bulletPoints") or [],
        "price": float(data.get("price", 0)),
        "currency": "USD",
        "quantity": int(data.get("quantity", 0)),
        "fulfillmentChannel": data.get("fulfillmentChannel", "MFN"),
        "status": "ACTIVE",
        "condition": data.get("condition", "NEW"),
        "productType": data.get("productType", ""),
        "itemWeight": data.get("itemWeight"),
        "itemWeightUnit": data.get("itemWeightUnit", "pounds"),
        "itemLength": data.get("itemLength"),
        "itemWidth": data.get("itemWidth"),
        "itemHeight": data.get("itemHeight"),
        "itemDimensionsUnit": data.get("itemDimensionsUnit", "inches"),
        "mainImageUrl": data.get("mainImageUrl", ""),
        "category": data.get("category", ""),
        "createdDate": now,
        "lastUpdatedDate": now,
    }
    _catalog_store.append(new_item)
    return {"type": "listing_item", "status": "ACCEPTED", "sku": sku, "issues": []}


def update_listing_item(seller_id, sku, data):
    for i, item in enumerate(_catalog_store):
        if item["sku"] == sku and item["sellerId"] == seller_id:
            updatable = {
                "title", "description", "brand", "bulletPoints", "price",
                "quantity", "fulfillmentChannel", "status", "condition",
                "productType", "mainImageUrl", "category",
            }
            for k, v in data.items():
                if k in updatable:
                    if k == "price" and v is not None:
                        _catalog_store[i][k] = float(v)
                    elif k == "quantity" and v is not None:
                        _catalog_store[i][k] = int(v)
                    else:
                        _catalog_store[i][k] = v
            _catalog_store[i]["lastUpdatedDate"] = _now()
            return {"type": "listing_item", "status": "ACCEPTED", "sku": sku, "issues": []}
    return {"error": f"Listing with SKU {sku} not found for seller {seller_id}"}


def delete_listing_item(seller_id, sku):
    for i, item in enumerate(_catalog_store):
        if item["sku"] == sku and item["sellerId"] == seller_id:
            _catalog_store.pop(i)
            return {"type": "listing_item", "status": "ACCEPTED", "sku": sku, "deleted": True}
    return {"error": f"Listing with SKU {sku} not found for seller {seller_id}"}


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def _format_order(order):
    return {
        "AmazonOrderId": order["AmazonOrderId"],
        "PurchaseDate": order["PurchaseDate"],
        "LastUpdateDate": order["LastUpdateDate"],
        "OrderStatus": order["OrderStatus"],
        "FulfillmentChannel": order["FulfillmentChannel"],
        "SalesChannel": order["SalesChannel"],
        "ShipServiceLevel": order["ShipServiceLevel"],
        "OrderTotal": {
            "CurrencyCode": order["OrderTotal_CurrencyCode"],
            "Amount": str(order["OrderTotal_Amount"]),
        },
        "NumberOfItemsShipped": order["NumberOfItemsShipped"],
        "NumberOfItemsUnshipped": order["NumberOfItemsUnshipped"],
        "PaymentMethod": order["PaymentMethod"],
        "MarketplaceId": order["MarketplaceId"],
        "ShipmentServiceLevelCategory": order["ShipmentServiceLevelCategory"],
        "OrderType": order["OrderType"],
        "EarliestShipDate": order["EarliestShipDate"],
        "LatestShipDate": order["LatestShipDate"],
        "IsPrime": order["IsPrime"],
        "IsBusinessOrder": order["IsBusinessOrder"],
        "IsSoldByAB": order["IsSoldByAB"],
        "ShippingAddress": {
            "Name": order["ShippingAddress_Name"],
            "AddressLine1": order["ShippingAddress_AddressLine1"],
            "City": order["ShippingAddress_City"],
            "StateOrRegion": order["ShippingAddress_StateOrRegion"],
            "PostalCode": order["ShippingAddress_PostalCode"],
            "CountryCode": order["ShippingAddress_CountryCode"],
        },
        "BuyerInfo": {
            "BuyerEmail": order["BuyerEmail"],
            "BuyerName": order["BuyerName"],
        },
    }


def get_orders(
    created_after=None,
    created_before=None,
    order_statuses=None,
    fulfillment_channels=None,
    max_results=100,
):
    results = list(_orders_store)

    if created_after:
        results = [r for r in results if r["PurchaseDate"] >= created_after]
    if created_before:
        results = [r for r in results if r["PurchaseDate"] <= created_before]
    if order_statuses:
        statuses = [s.strip() for s in order_statuses.split(",")]
        results = [r for r in results if r["OrderStatus"] in statuses]
    if fulfillment_channels:
        channels = [c.strip() for c in fulfillment_channels.split(",")]
        results = [r for r in results if r["FulfillmentChannel"] in channels]

    results = sorted(results, key=lambda x: x["PurchaseDate"], reverse=True)

    total = len(results)
    page_results = results[:max_results]
    return {
        "type": "orders",
        "count": len(page_results),
        "total": total,
        "offset": 0,
        "limit": max_results,
        "payload": {
            "Orders": [_format_order(o) for o in page_results],
        },
    }


def get_order(order_id):
    for o in _orders_store:
        if o["AmazonOrderId"] == order_id:
            return {"type": "order", "payload": _format_order(o)}
    return {"error": f"Order {order_id} not found"}


def get_order_items(order_id):
    items = [oi for oi in _order_items_store if oi["AmazonOrderId"] == order_id]
    if not items:
        if not any(o["AmazonOrderId"] == order_id for o in _orders_store):
            return {"error": f"Order {order_id} not found"}
    formatted = []
    for oi in items:
        formatted.append({
            "OrderItemId": oi["OrderItemId"],
            "ASIN": oi["ASIN"],
            "SellerSKU": oi["SellerSKU"],
            "Title": oi["Title"],
            "QuantityOrdered": oi["QuantityOrdered"],
            "QuantityShipped": oi["QuantityShipped"],
            "ItemPrice": {"CurrencyCode": oi["ItemPrice_CurrencyCode"], "Amount": str(oi["ItemPrice_Amount"])},
            "ItemTax": {"CurrencyCode": oi["ItemPrice_CurrencyCode"], "Amount": str(oi["ItemTax_Amount"])},
            "PromotionDiscount": {"CurrencyCode": oi["ItemPrice_CurrencyCode"], "Amount": str(oi["PromotionDiscount_Amount"])},
            "IsGift": oi["IsGift"],
            "ConditionId": oi["Condition"],
        })
    return {
        "type": "order_items",
        "payload": {
            "AmazonOrderId": order_id,
            "OrderItems": formatted,
        },
    }


def confirm_shipment(order_id, data):
    for i, o in enumerate(_orders_store):
        if o["AmazonOrderId"] == order_id:
            if o["OrderStatus"] not in ("Unshipped", "PartiallyShipped"):
                return {"error": f"Order {order_id} cannot be shipped (status: {o['OrderStatus']})"}
            _orders_store[i]["OrderStatus"] = "Shipped"
            _orders_store[i]["LastUpdateDate"] = _now()
            shipped = o["NumberOfItemsShipped"] + o["NumberOfItemsUnshipped"]
            _orders_store[i]["NumberOfItemsShipped"] = shipped
            _orders_store[i]["NumberOfItemsUnshipped"] = 0
            for j, oi in enumerate(_order_items_store):
                if oi["AmazonOrderId"] == order_id:
                    _order_items_store[j]["QuantityShipped"] = oi["QuantityOrdered"]
            return {"type": "shipment_confirmation", "status": "SUCCESS", "orderId": order_id}
    return {"error": f"Order {order_id} not found"}


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

def get_inventory_summaries(
    seller_skus=None,
    granularity_type="Marketplace",
    marketplace_id="ATVPDKIKX0DER",
):
    results = list(_inventory_store)

    if seller_skus:
        sku_list = [s.strip() for s in seller_skus.split(",")]
        results = [r for r in results if r["sellerSku"] in sku_list]

    formatted = []
    for inv in results:
        formatted.append({
            "asin": inv["asin"],
            "fnSku": inv["fnSku"],
            "sellerSku": inv["sellerSku"],
            "productName": inv["productName"],
            "condition": inv["condition"],
            "granularity": {"granularityType": granularity_type, "granularityId": marketplace_id},
            "inventoryDetails": {
                "fulfillableQuantity": inv["inStockSupplyQuantity"],
                "inboundWorkingQuantity": inv["inboundWorkingQuantity"],
                "inboundShippedQuantity": inv["inboundShippedQuantity"],
                "inboundReceivingQuantity": inv["inboundReceivingQuantity"],
                "totalQuantity": inv["totalQuantity"],
                "reservedQuantity": inv["reservedQuantity"],
                "unfulfillableQuantity": inv["unfulfillableQuantity"],
            },
            "lastUpdatedTime": inv["lastUpdatedTime"],
        })
    return {
        "type": "inventory_summaries",
        "payload": {
            "granularity": {"granularityType": granularity_type, "granularityId": marketplace_id},
            "inventorySummaries": formatted,
        },
        "pagination": {"nextToken": None},
    }


def update_inventory(seller_sku, quantity):
    for i, inv in enumerate(_inventory_store):
        if inv["sellerSku"] == seller_sku:
            _inventory_store[i]["totalQuantity"] = int(quantity)
            _inventory_store[i]["inStockSupplyQuantity"] = int(quantity)
            _inventory_store[i]["lastUpdatedTime"] = _now()
            return {"type": "inventory_update", "status": "SUCCESS", "sellerSku": seller_sku}
    return {"error": f"Inventory for SKU {seller_sku} not found"}


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def get_reports(report_types=None, processing_statuses=None):
    results = list(_reports_store)

    if report_types:
        type_list = [t.strip() for t in report_types.split(",")]
        results = [r for r in results if r["reportType"] in type_list]
    if processing_statuses:
        status_list = [s.strip() for s in processing_statuses.split(",")]
        results = [r for r in results if r["reportStatus"] in status_list]

    results = sorted(results, key=lambda x: x["createdTime"], reverse=True)
    return {
        "type": "reports",
        "payload": {
            "reports": [{
                "reportId": r["reportId"],
                "reportType": r["reportType"],
                "processingStatus": r["reportStatus"],
                "dataStartTime": r["dataStartTime"],
                "dataEndTime": r["dataEndTime"],
                "createdTime": r["createdTime"],
                "processingEndTime": r["processingEndTime"],
                "reportDocumentId": r["reportDocumentId"],
            } for r in results],
        },
    }


def get_report(report_id):
    for r in _reports_store:
        if r["reportId"] == report_id:
            return {
                "type": "report",
                "payload": {
                    "reportId": r["reportId"],
                    "reportType": r["reportType"],
                    "processingStatus": r["reportStatus"],
                    "dataStartTime": r["dataStartTime"],
                    "dataEndTime": r["dataEndTime"],
                    "createdTime": r["createdTime"],
                    "processingEndTime": r["processingEndTime"],
                    "reportDocumentId": r["reportDocumentId"],
                },
            }
    return {"error": f"Report {report_id} not found"}


def create_report(report_type, data_start_time, data_end_time):
    global _next_report_id
    now = _now()
    report = {
        "reportId": f"REP-{_next_report_id:03d}",
        "reportType": report_type,
        "reportStatus": "IN_QUEUE",
        "dataStartTime": data_start_time,
        "dataEndTime": data_end_time,
        "createdTime": now,
        "processingEndTime": None,
        "reportDocumentId": None,
    }
    _reports_store.append(report)
    _next_report_id += 1
    return {
        "type": "report_created",
        "payload": {"reportId": report["reportId"]},
    }


# ---------------------------------------------------------------------------
# Product Pricing
# ---------------------------------------------------------------------------

def get_competitive_pricing(asin=None, sku=None):
    results = list(_pricing_store)

    if asin:
        results = [r for r in results if r["asin"] == asin]
    elif sku:
        results = [r for r in results if r["sellerSku"] == sku]

    if not results:
        identifier = asin or sku
        return {"error": f"Pricing not found for {identifier}"}

    formatted = []
    for p in results:
        formatted.append({
            "ASIN": p["asin"],
            "Product": {
                "CompetitivePricing": {
                    "CompetitivePrices": [{
                        "CompetitivePriceId": "1",
                        "Price": {
                            "ListingPrice": {"CurrencyCode": p["competitivePrice_CurrencyCode"], "Amount": str(p["competitivePrice_Amount"])},
                            "LandedPrice": {"CurrencyCode": p["competitivePrice_CurrencyCode"], "Amount": str(p["landedPrice_Amount"])},
                            "Shipping": {"CurrencyCode": p["competitivePrice_CurrencyCode"], "Amount": str(p["shipping_Amount"])},
                        },
                        "condition": p["competitivePrice_Condition"],
                        "belongsToRequester": p["buyBoxWinner"],
                    }],
                    "NumberOfOfferListings": [{"condition": "New", "Count": p["numberOfOffers"]}],
                },
                "Offers": [{
                    "BuyBoxPrices": [{
                        "condition": "New",
                        "LandedPrice": {"CurrencyCode": p["buyBoxPrice_CurrencyCode"], "Amount": str(p["buyBoxPrice_Amount"])},
                        "ListingPrice": {"CurrencyCode": p["buyBoxPrice_CurrencyCode"], "Amount": str(p["buyBoxPrice_Amount"])},
                        "Shipping": {"CurrencyCode": p["buyBoxPrice_CurrencyCode"], "Amount": "0.00"},
                    }],
                    "NumberOfOffers": [{"condition": "New", "fulfillmentChannel": "Amazon", "Count": p["numberOfOffers"]}],
                }],
            },
        })
    return {
        "type": "competitive_pricing",
        "payload": formatted if len(formatted) > 1 else formatted[0],
    }


def get_item_offers(asin):
    pricing = [p for p in _pricing_store if p["asin"] == asin]
    if not pricing:
        return {"error": f"Offers not found for ASIN {asin}"}
    p = pricing[0]
    return {
        "type": "item_offers",
        "payload": {
            "ASIN": asin,
            "status": "Success",
            "ItemCondition": "New",
            "Summary": {
                "LowestPrices": [{
                    "condition": "New",
                    "fulfillmentChannel": "Amazon",
                    "LandedPrice": {"CurrencyCode": "USD", "Amount": str(p["competitivePrice_Amount"])},
                    "ListingPrice": {"CurrencyCode": "USD", "Amount": str(p["competitivePrice_Amount"])},
                    "Shipping": {"CurrencyCode": "USD", "Amount": str(p["shipping_Amount"])},
                }],
                "BuyBoxPrices": [{
                    "condition": "New",
                    "LandedPrice": {"CurrencyCode": "USD", "Amount": str(p["buyBoxPrice_Amount"])},
                    "ListingPrice": {"CurrencyCode": "USD", "Amount": str(p["buyBoxPrice_Amount"])},
                    "Shipping": {"CurrencyCode": "USD", "Amount": "0.00"},
                }],
                "NumberOfOffers": [{"condition": "New", "fulfillmentChannel": "Amazon", "Count": p["numberOfOffers"]}],
                "BuyBoxEligibleOffers": [{"condition": "New", "fulfillmentChannel": "Amazon", "Count": p["numberOfOffers"]}],
            },
            "Offers": [{
                "SellerFeedbackRating": {"SellerPositiveFeedbackRating": 96.5, "FeedbackCount": 1247},
                "ListingPrice": {"CurrencyCode": "USD", "Amount": str(p["listingPrice_Amount"])},
                "Shipping": {"CurrencyCode": "USD", "Amount": str(p["shipping_Amount"])},
                "IsBuyBoxWinner": p["buyBoxWinner"],
                "IsFulfilledByAmazon": True,
            }],
        },
    }


# ---------------------------------------------------------------------------
# Returns
# ---------------------------------------------------------------------------

def get_returns(status=None, order_id=None):
    results = list(_returns_store)

    if status:
        results = [r for r in results if r["returnStatus"].upper() == status.upper()]
    if order_id:
        results = [r for r in results if r["AmazonOrderId"] == order_id]

    results = sorted(results, key=lambda x: x["returnDate"], reverse=True)
    return {
        "type": "returns",
        "count": len(results),
        "total": len(results),
        "offset": 0,
        "limit": 100,
        "results": results,
    }


def get_return(return_id):
    for r in _returns_store:
        if r["returnId"] == return_id:
            return {"type": "return", "return": r}
    return {"error": f"Return {return_id} not found"}


def authorize_return(return_id):
    for i, r in enumerate(_returns_store):
        if r["returnId"] == return_id:
            if r["returnStatus"] != "Authorized":
                return {"error": f"Return {return_id} is not in Authorized status"}
            _returns_store[i]["returnStatus"] = "Completed"
            _returns_store[i]["resolution"] = "REFUND"
            return {"type": "return_authorization", "status": "SUCCESS", "returnId": return_id}
    return {"error": f"Return {return_id} not found"}


def close_return(return_id):
    for i, r in enumerate(_returns_store):
        if r["returnId"] == return_id:
            _returns_store[i]["returnStatus"] = "Closed"
            _returns_store[i]["resolution"] = "CLOSED"
            return {"type": "return_close", "status": "SUCCESS", "returnId": return_id}
    return {"error": f"Return {return_id} not found"}
