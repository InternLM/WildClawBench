# Mock API Services Documentation

## Table of Contents

1. [Amazon Seller API](#1-amazon-seller-api)
2. [Etsy API](#2-etsy-api)
3. [Google Classroom API](#3-google-classroom-api)
4. [Instagram Graph API](#4-instagram-graph-api)
5. [Linear API](#5-linear-api)
6. [MyFitnessPal API](#6-myfitnesspal-api)
7. [Pinterest API](#7-pinterest-api)
8. [QuickBooks Online API](#8-quickbooks-online-api)
9. [Ring API](#9-ring-api)
10. [YouTube Data API](#10-youtube-data-api)

---

## Service Overview

| Service | Port | Env Var | App Title | Version |
|---------|------|---------|-----------|---------|
| amazon-seller-api | 8000 | `AMAZON_SELLER_API_URL` | Amazon Selling Partner API (Mock) | v1.0.0 |
| etsy-api | 8001 | `ETSY_API_URL` | Etsy Open API v3 (Mock) | v3.0.0 |
| google-classroom-api | 8002 | `GOOGLE_CLASSROOM_API_URL` | Google Classroom API (Mock) | v1.0 |
| instagram-api | 8003 | `INSTAGRAM_API_URL` | Instagram Graph API (Mock) | v18.0 |
| linear-api | 8004 | `LINEAR_API_URL` | Linear API (Mock) | v2024.01 |
| myfitnesspal-api | 8005 | `MYFITNESSPAL_API_URL` | MyFitnessPal API (Mock) | v1.0.0 |
| pinterest-api | 8006 | `PINTEREST_API_URL` | Pinterest API v5 (Mock) | v5.0.0 |
| quickbooks-api | 8007 | `QUICKBOOKS_API_URL` | QuickBooks Online API (Mock) | v3.0 |
| ring-api | 8008 | `RING_API_URL` | Ring API (Mock) | v1.0.0 |
| youtube-api | 8009 | `YOUTUBE_API_URL` | YouTube Data API v3 (Mock) | v3.0 |

---

## Shared Tracking/Audit Endpoints

All 10 services include tracking middleware that exposes these endpoints:

#### `GET /health`
Health check.

**Response:** `200`
```json
{"status": "ok"}
```

#### `GET /audit/requests`
Returns full audit log of all requests.

**Response:** `200`
```json
{"total": 42, "requests": [...]}
```

#### `GET /audit/requests/clear`
Clears the audit log.

**Response:** `200`
```json
{"cleared": 42}
```

#### `GET /audit/summary`
Aggregated request summary by endpoint.

**Response:** `200`
```json
{"total_requests": 42, "endpoints": {"GET /some/path": {"count": 10, "statuses": {"200": 8, "404": 2}}}}
```

Each value in `endpoints` is a dict with `count` (integer) and `statuses` (map of status code → count). Use `endpoint_data["count"]` to get the call count.

**Audit Log Entry Format:**
```json
{
  "timestamp": 1234567890.123,
  "timestamp_iso": "2026-05-07T10:30:00",
  "method": "GET",
  "path": "/some/path",
  "query_params": {"key": "value"},
  "request_body": "..." ,
  "status_code": 200,
  "response_body": "...",
  "duration_ms": 12.34
}
```

---

## 1. Amazon Seller API

**Port:** 8000 | **Env Var:** `AMAZON_SELLER_API_URL` | **Version:** v1.0.0

### Seller Account

#### `GET /sellers/v1/account`
Returns seller account information.

**Response:** `200`

#### `GET /sellers/v1/account/health`
Returns account health metrics.

**Response:** `200`

#### `GET /notifications/v1/notifications`
Lists seller notifications.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| severity | str | — | — | Filter by severity level |

**Response:** `200`

---

### Catalog Items

#### `GET /catalog/2022-04-01/items`
Search the Amazon catalog.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| keywords | str | — | — | Search keywords |
| identifiers | str | — | — | Product identifiers |
| identifiersType | str | — | — | Type of identifiers |
| pageSize | int | 10 | ge=1, le=20 | Results per page |
| marketplaceIds | str | "ATVPDKIKX0DER" | — | Marketplace ID |
| includedData | str | "summaries" | — | Data sets to include |

**Response:** `200`

#### `GET /catalog/2022-04-01/items/{asin}`
Get a single catalog item by ASIN.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| asin | str | Amazon Standard Identification Number |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| marketplaceIds | str | — | — | Marketplace ID |
| includedData | str | — | — | Data sets to include |

**Response:** `200`

---

### Listings Items

#### `GET /listings/2021-08-01/items/{sellerId}/{sku}`
Get a listing by seller ID and SKU.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerId | str | Seller identifier |
| sku | str | Stock Keeping Unit |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| marketplaceIds | str | — | — | Marketplace ID |
| includedData | str | "attributes,issues" | — | Data sets to include |

**Response:** `200`

#### `PUT /listings/2021-08-01/items/{sellerId}/{sku}`
Create or update a listing. Returns 201 if created, 200 if updated.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerId | str | Seller identifier |
| sku | str | Stock Keeping Unit |

**Request Body:**
```json
{
  "productType": "str (required)",
  "title": "str (optional)",
  "description": "str (optional)",
  "brand": "str (optional)",
  "bulletPoints": ["str"] ,
  "price": "float (optional)",
  "quantity": "int (optional)",
  "fulfillmentChannel": "str (optional)",
  "condition": "str (optional)",
  "mainImageUrl": "str (optional)",
  "category": "str (optional)",
  "asin": "str (optional)",
  "itemWeight": "float (optional)",
  "itemWeightUnit": "str (optional)",
  "itemLength": "str (optional)",
  "itemWidth": "str (optional)",
  "itemHeight": "str (optional)",
  "itemDimensionsUnit": "str (optional)"
}
```

**Response:** `200` (updated) or `201` (created)

#### `PATCH /listings/2021-08-01/items/{sellerId}/{sku}`
Partially update a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerId | str | Seller identifier |
| sku | str | Stock Keeping Unit |

**Request Body:**
```json
{
  "title": "str (optional)",
  "description": "str (optional)",
  "brand": "str (optional)",
  "bulletPoints": ["str"],
  "price": "float (optional)",
  "quantity": "int (optional)",
  "fulfillmentChannel": "str (optional)",
  "status": "str (optional)",
  "condition": "str (optional)",
  "mainImageUrl": "str (optional)",
  "category": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /listings/2021-08-01/items/{sellerId}/{sku}`
Delete a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerId | str | Seller identifier |
| sku | str | Stock Keeping Unit |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| marketplaceIds | str | — | — | Marketplace ID |

**Response:** `200`

---

### Orders

#### `GET /orders/v0/orders`
List orders with filters.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| CreatedAfter | str | — | — | Filter orders created after date |
| CreatedBefore | str | — | — | Filter orders created before date |
| OrderStatuses | str | — | — | Filter by order status |
| FulfillmentChannels | str | — | — | Filter by fulfillment channel |
| MarketplaceIds | str | "ATVPDKIKX0DER" | — | Marketplace ID |
| MaxResultsPerPage | int | 100 | ge=1, le=100 | Max results per page |

**Response:** `200`

#### `GET /orders/v0/orders/{orderId}`
Get a single order.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| orderId | str | Order identifier |

**Response:** `200`

#### `GET /orders/v0/orders/{orderId}/orderItems`
Get items for an order.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| orderId | str | Order identifier |

**Response:** `200`

#### `POST /orders/v0/orders/{orderId}/shipmentConfirmation`
Confirm shipment for an order.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| orderId | str | Order identifier |

**Request Body:**
```json
{
  "packageReferenceId": "str (optional)",
  "carrierCode": "str (optional)",
  "trackingNumber": "str (optional)",
  "shipDate": "str (optional)"
}
```

**Response:** `200`

---

### Inventory

#### `GET /fba/inventory/v1/summaries`
Get FBA inventory summaries.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| sellerSkus | str | — | — | Filter by seller SKUs |
| granularityType | str | "Marketplace" | — | Granularity type |
| granularityId | str | "ATVPDKIKX0DER" | — | Granularity ID |
| marketplaceIds | str | — | — | Marketplace ID |

**Response:** `200`

#### `PUT /fba/inventory/v1/items/{sellerSku}`
Update inventory for a SKU.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| sellerSku | str | Seller SKU |

**Request Body:**
```json
{
  "sellerSku": "str (required)",
  "quantity": "int (required)"
}
```

**Response:** `200`

---

### Reports

#### `GET /reports/2021-06-30/reports`
List reports.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| reportTypes | str | — | — | Filter by report type |
| processingStatuses | str | — | — | Filter by processing status |

**Response:** `200`

#### `GET /reports/2021-06-30/reports/{reportId}`
Get a single report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| reportId | str | Report identifier |

**Response:** `200`

#### `POST /reports/2021-06-30/reports`
Create a new report.

**Request Body:**
```json
{
  "reportType": "str (required)",
  "dataStartTime": "str (required)",
  "dataEndTime": "str (required)",
  "marketplaceIds": ["str"]
}
```

**Response:** `202`

---

### Product Pricing

#### `GET /products/pricing/v0/competitivePrice`
Get competitive pricing data.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| Asin | str | — | — | ASIN to look up |
| Sku | str | — | — | SKU to look up |
| MarketplaceId | str | — | — | Marketplace ID |
| ItemType | str | "Asin" | — | Item type for lookup |

**Response:** `200`

#### `GET /products/pricing/v0/items/{Asin}/offers`
Get offers for a product.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| Asin | str | Amazon Standard Identification Number |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| MarketplaceId | str | — | — | Marketplace ID |
| ItemCondition | str | "New" | — | Item condition filter |

**Response:** `200`

---

### Returns

#### `GET /returns/v0/returns`
List returns.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| status | str | — | — | Filter by return status |
| orderId | str | — | — | Filter by order ID |

**Response:** `200`

#### `GET /returns/v0/returns/{returnId}`
Get a single return.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| returnId | str | Return identifier |

**Response:** `200`

#### `POST /returns/v0/returns/{returnId}/authorize`
Authorize a return.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| returnId | str | Return identifier |

**Response:** `200`

#### `POST /returns/v0/returns/{returnId}/close`
Close a return.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| returnId | str | Return identifier |

**Response:** `200`

---

## 2. Etsy API

**Port:** 8001 | **Env Var:** `ETSY_API_URL` | **Version:** v3.0.0

### Shop

#### `GET /v3/application/shops/{shop_id}`
Get shop details.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Response:** `200`

#### `PUT /v3/application/shops/{shop_id}`
Update shop details.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Request Body:**
```json
{
  "title": "str (optional)",
  "announcement": "str (optional)",
  "sale_message": "str (optional)",
  "is_vacation": "bool (optional)",
  "vacation_message": "str (optional)",
  "accepts_custom_requests": "bool (optional)",
  "policy_welcome": "str (optional)",
  "policy_payment": "str (optional)",
  "policy_shipping": "str (optional)",
  "policy_refunds": "str (optional)"
}
```

**Response:** `200`

---

### Shop Sections

#### `GET /v3/application/shops/{shop_id}/sections`
List all sections for a shop.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/sections/{section_id}`
Get a single shop section.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| section_id | int | Section identifier |

**Response:** `200`

---

### Listings

#### `GET /v3/application/shops/{shop_id}/listings`
List shop listings with filters.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| state | str | "active" | — | Listing state filter |
| sort_on | str | "created" | — | Sort field |
| sort_order | str | "desc" | — | Sort direction |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |
| section_id | int | — | — | Filter by section |
| q | str | — | — | Search query |

**Response:** `200`

#### `GET /v3/application/listings/{listing_id}`
Get a single listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Response:** `200`

#### `POST /v3/application/shops/{shop_id}/listings`
Create a new listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Request Body:**
```json
{
  "title": "str (required)",
  "description": "str (required)",
  "price": "float (required)",
  "quantity": "int (required)",
  "who_made": "str (required)",
  "when_made": "str (required)",
  "taxonomy_id": "int (required)",
  "tags": ["str"],
  "materials": ["str"],
  "shop_section_id": "int (optional)",
  "shipping_profile_id": "int (optional)",
  "return_policy_id": "int (optional)",
  "processing_min": "int (optional)",
  "processing_max": "int (optional)",
  "item_weight": "optional",
  "item_weight_unit": "optional",
  "item_length": "optional",
  "item_width": "optional",
  "item_height": "optional",
  "item_dimensions_unit": "optional",
  "is_supply": "bool (optional, default=false)",
  "is_customizable": "bool (optional, default=false)",
  "is_personalizable": "bool (optional, default=false)"
}
```

**Response:** `201`

#### `PUT /v3/application/listings/{listing_id}`
Update a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Request Body:**
All fields from create body (all optional), plus:
```json
{
  "state": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v3/application/listings/{listing_id}`
Delete a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Response:** `200`

---

### Listing Images

#### `GET /v3/application/listings/{listing_id}/images`
List images for a listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Response:** `200`

#### `GET /v3/application/listings/{listing_id}/images/{image_id}`
Get a single listing image.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |
| image_id | int | Image identifier |

**Response:** `200`

#### `DELETE /v3/application/listings/{listing_id}/images/{image_id}`
Delete a listing image.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |
| image_id | int | Image identifier |

**Response:** `200`

---

### Receipts (Orders)

#### `GET /v3/application/shops/{shop_id}/receipts`
List shop receipts (orders).

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| status | str | — | — | Filter by status |
| min_created | str | — | — | Minimum creation date |
| max_created | str | — | — | Maximum creation date |
| sort_on | str | "created" | — | Sort field |
| sort_order | str | "desc" | — | Sort direction |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |
| was_shipped | bool | — | — | Filter by shipped status |
| was_paid | bool | — | — | Filter by paid status |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/receipts/{receipt_id}`
Get a single receipt.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| receipt_id | int | Receipt identifier |

**Response:** `200`

#### `PUT /v3/application/shops/{shop_id}/receipts/{receipt_id}`
Update a receipt (e.g., mark as shipped).

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| receipt_id | int | Receipt identifier |

**Request Body:**
```json
{
  "shipping_carrier": "str (optional)",
  "tracking_code": "str (optional)",
  "was_shipped": "bool (optional)"
}
```

**Response:** `200`

---

### Transactions

#### `GET /v3/application/shops/{shop_id}/receipts/{receipt_id}/transactions`
List transactions for a receipt.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| receipt_id | int | Receipt identifier |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/transactions/{transaction_id}`
Get a single transaction.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| transaction_id | int | Transaction identifier |

**Response:** `200`

---

### Reviews

#### `GET /v3/application/shops/{shop_id}/reviews`
List reviews for a shop.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| listing_id | int | — | — | Filter by listing |
| min_rating | int | — | ge=1, le=5 | Minimum rating |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v3/application/listings/{listing_id}/reviews`
List reviews for a specific listing.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| listing_id | int | Listing identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| min_rating | int | — | ge=1, le=5 | Minimum rating |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Shipping Profiles

#### `GET /v3/application/shops/{shop_id}/shipping-profiles`
List shipping profiles for a shop.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/shipping-profiles/{profile_id}`
Get a single shipping profile.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| profile_id | int | Profile identifier |

**Response:** `200`

---

### Return Policies

#### `GET /v3/application/shops/{shop_id}/return-policies`
List return policies for a shop.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |

**Response:** `200`

#### `GET /v3/application/shops/{shop_id}/return-policies/{policy_id}`
Get a single return policy.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| shop_id | int | Shop identifier |
| policy_id | int | Policy identifier |

**Response:** `200`

---

## 3. Google Classroom API

**Port:** 8002 | **Env Var:** `GOOGLE_CLASSROOM_API_URL` | **Version:** v1.0

### Courses

#### `GET /v1/courses`
List courses.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| courseStates | str | — | — | Filter by course state |
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token (parsed as int) |

**Response:** `200`

#### `GET /v1/courses/{course_id}`
Get a single course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Response:** `200`

#### `POST /v1/courses`
Create a new course.

**Request Body:**
```json
{
  "name": "str (required)",
  "section": "str (optional)",
  "descriptionHeading": "str (optional)",
  "description": "str (optional)",
  "room": "str (optional)",
  "ownerId": "str (optional)"
}
```

**Response:** `201`

#### `PATCH /v1/courses/{course_id}`
Update a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "name": "str (optional)",
  "section": "str (optional)",
  "descriptionHeading": "str (optional)",
  "description": "str (optional)",
  "room": "str (optional)",
  "courseState": "str (optional)"
}
```

**Response:** `200`

#### `POST /v1/courses/{course_id}:archive`
Archive a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Response:** `200`

---

### Course Work

#### `GET /v1/courses/{course_id}/courseWork`
List course work for a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| topicId | str | — | — | Filter by topic |
| courseWorkStates | str | — | — | Filter by state |
| orderBy | str | — | — | Order results |
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/courseWork/{coursework_id}`
Get a single course work item.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/courseWork`
Create course work.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "title": "str (required)",
  "description": "str (optional)",
  "workType": "str (required)",
  "state": "str (optional)",
  "maxPoints": "float (optional)",
  "topicId": "str (optional)",
  "dueDate": {
    "year": "int",
    "month": "int",
    "day": "int"
  },
  "dueTime": {
    "hours": "int",
    "minutes": "int"
  }
}
```

**Response:** `201`

#### `PATCH /v1/courses/{course_id}/courseWork/{coursework_id}`
Update course work.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |

**Request Body:**
```json
{
  "title": "str (optional)",
  "description": "str (optional)",
  "state": "str (optional)",
  "maxPoints": "float (optional)",
  "topicId": "str (optional)",
  "dueDate": "object (optional)",
  "dueTime": "object (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/courses/{course_id}/courseWork/{coursework_id}`
Delete course work.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |

**Response:** `200`

---

### Topics

#### `GET /v1/courses/{course_id}/topics`
List topics for a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/topics/{topic_id}`
Get a single topic.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| topic_id | str | Topic identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/topics`
Create a topic.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "name": "str (required)"
}
```

**Response:** `201`

#### `PATCH /v1/courses/{course_id}/topics/{topic_id}`
Update a topic.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| topic_id | str | Topic identifier |

**Request Body:**
```json
{
  "name": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/courses/{course_id}/topics/{topic_id}`
Delete a topic.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| topic_id | str | Topic identifier |

**Response:** `200`

---

### Student Submissions

#### `GET /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions`
List student submissions.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| states | str | — | — | Filter by submission state |
| late | bool | — | — | Filter late submissions |
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}`
Get a single submission.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |
| submission_id | str | Submission identifier |

**Response:** `200`

#### `PATCH /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}`
Grade a submission.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |
| submission_id | str | Submission identifier |

**Request Body:**
```json
{
  "assignedGrade": "float (optional)",
  "draftGrade": "float (optional)"
}
```

**Response:** `200`

#### `POST /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}:return`
Return a submission to the student.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |
| submission_id | str | Submission identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions/{submission_id}:reclaim`
Reclaim a submission.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| coursework_id | str | Course work identifier |
| submission_id | str | Submission identifier |

**Response:** `200`

---

### Students

#### `GET /v1/courses/{course_id}/students`
List students in a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| pageSize | int | 30 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/students/{user_id}`
Get a single student.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| user_id | str | User identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/students`
Enroll a student.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "emailAddress": "str (required)",
  "fullName": "str (optional)"
}
```

**Response:** `201`

#### `DELETE /v1/courses/{course_id}/students/{user_id}`
Remove a student from a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| user_id | str | User identifier |

**Response:** `200`

---

### Teachers

#### `GET /v1/courses/{course_id}/teachers`
List teachers for a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Response:** `200`

#### `GET /v1/courses/{course_id}/teachers/{user_id}`
Get a single teacher.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| user_id | str | User identifier |

**Response:** `200`

---

### Announcements

#### `GET /v1/courses/{course_id}/announcements`
List announcements for a course.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| announcementStates | str | — | — | Filter by state |
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/announcements/{announcement_id}`
Get a single announcement.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| announcement_id | str | Announcement identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/announcements`
Create an announcement.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "text": "str (required)",
  "state": "str (optional)"
}
```

**Response:** `201`

#### `PATCH /v1/courses/{course_id}/announcements/{announcement_id}`
Update an announcement.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| announcement_id | str | Announcement identifier |

**Request Body:**
```json
{
  "text": "str (optional)",
  "state": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/courses/{course_id}/announcements/{announcement_id}`
Delete an announcement.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| announcement_id | str | Announcement identifier |

**Response:** `200`

---

### Course Work Materials

#### `GET /v1/courses/{course_id}/courseWorkMaterials`
List course work materials.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| pageSize | int | 20 | ge=1, le=100 | Results per page |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `GET /v1/courses/{course_id}/courseWorkMaterials/{material_id}`
Get a single course work material.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |
| material_id | str | Material identifier |

**Response:** `200`

#### `POST /v1/courses/{course_id}/courseWorkMaterials`
Create a course work material.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| course_id | str | Course identifier |

**Request Body:**
```json
{
  "title": "str (required)",
  "description": "str (optional)",
  "topicId": "str (optional)",
  "materials": [
    {
      "link": {
        "url": "str (required)",
        "title": "str (optional)"
      }
    }
  ]
}
```

**Response:** `201`

---

## 4. Instagram Graph API

**Port:** 8003 | **Env Var:** `INSTAGRAM_API_URL` | **Version:** v18.0

### Hashtags

#### `GET /ig_hashtag_search`
Search for hashtags.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| q | str | — | required | Hashtag search query |

**Response:** `200`

#### `GET /hashtag/{hashtag_id}`
Get hashtag details.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| hashtag_id | str | Hashtag identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

#### `GET /hashtag/{hashtag_id}/recent_media`
Get recent media for a hashtag.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| hashtag_id | str | Hashtag identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| user_id | str | — | required | User ID for context |
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=50 | Results per page |

**Response:** `200`

---

### Media

#### `GET /media/{media_id}/children`
Get children of a carousel media.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

#### `GET /media/{media_id}/comments`
Get comments on a media object.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /media/{media_id}/insights`
Get insights for a media object.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| metric | str | — | — | Metric to retrieve |

**Response:** `200`

#### `GET /media/{media_id}`
Get a single media object.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

#### `DELETE /media/{media_id}`
Delete a media object.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Response:** `200`

---

### Comments

#### `POST /media/{media_id}/comments`
Post a comment on media.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Request Body:**
```json
{
  "message": "str (required)",
  "parent_id": "str (optional)"
}
```

**Response:** `201`

#### `DELETE /media/{media_id}/comments/{comment_id}`
Delete a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |
| comment_id | str | Comment identifier |

**Response:** `200`

#### `PUT /media/{media_id}/comments/{comment_id}/hide`
Hide or unhide a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |
| comment_id | str | Comment identifier |

**Request Body:**
```json
{
  "hide": "bool (optional, default=true)"
}
```

**Response:** `200`

#### `GET /comment/{comment_id}/replies`
Get replies to a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /comment/{comment_id}`
Get a single comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

---

### Stories

#### `GET /stories/{story_id}`
Get a single story.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| story_id | str | Story identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

---

### Container

#### `GET /container/{container_id}`
Get container publish status.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| container_id | str | Container identifier |

**Response:** `200`

---

### User

#### `GET /{user_id}/media`
Get media for a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| media_type | str | — | — | Filter by media type |
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /{user_id}/stories`
Get stories for a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

#### `GET /{user_id}/insights`
Get insights for a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| metric | str | — | — | Metric to retrieve |
| period | str | "day" | — | Time period |

**Response:** `200`

#### `GET /{user_id}/tags`
Get tagged media for a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `POST /{user_id}/media`
Create a media container.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Request Body:**
```json
{
  "image_url": "str (optional)",
  "video_url": "str (optional)",
  "caption": "str (optional)",
  "media_type": "str (optional, default='IMAGE')",
  "children": ["str"]
}
```

**Response:** `201`

#### `POST /{user_id}/media_publish`
Publish a media container.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Request Body:**
```json
{
  "creation_id": "str (required)"
}
```

**Response:** `201`

#### `GET /{user_id}`
Get user profile information.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| fields | str | — | — | Comma-separated field names |

**Response:** `200`

---

## 5. Linear API

**Port:** 8004 | **Env Var:** `LINEAR_API_URL` | **Version:** v2024.01

### Teams

#### `GET /v1/teams`
List all teams.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/teams/{team_id}`
Get a single team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/members`
List team members.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/issues`
List issues for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/teams/{team_id}/projects`
List projects for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/cycles`
List cycles for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/workflow-states`
List workflow states for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

#### `GET /v1/teams/{team_id}/labels`
List labels for a team.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| team_id | str | Team identifier |

**Response:** `200`

---

### Users

#### `GET /v1/users`
List all users.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/users/{user_id}`
Get a single user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Response:** `200`

#### `GET /v1/users/{user_id}/issues`
List issues assigned to a user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| user_id | str | User identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Workflow States

#### `GET /v1/workflow-states`
List all workflow states.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| teamId | str | — | — | Filter by team |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/workflow-states/{state_id}`
Get a single workflow state.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| state_id | str | State identifier |

**Response:** `200`

---

### Labels

#### `GET /v1/labels`
List all labels.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| teamId | str | — | — | Filter by team |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/labels/{label_id}`
Get a single label.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| label_id | str | Label identifier |

**Response:** `200`

#### `POST /v1/labels`
Create a label.

**Request Body:**
```json
{
  "name": "str (required)",
  "color": "str (required)",
  "description": "str (optional)",
  "teamId": "str (optional)"
}
```

**Response:** `201`

---

### Projects

#### `GET /v1/projects`
List all projects.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/projects/{project_id}`
Get a single project.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| project_id | str | Project identifier |

**Response:** `200`

#### `POST /v1/projects`
Create a project.

**Request Body:**
```json
{
  "name": "str (required)",
  "description": "str (optional)",
  "state": "str (optional)",
  "leadId": "str (optional)",
  "teamIds": ["str"],
  "startDate": "str (optional)",
  "targetDate": "str (optional)"
}
```

**Response:** `201`

#### `PUT /v1/projects/{project_id}`
Update a project.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| project_id | str | Project identifier |

**Request Body:**
Same fields as create, all optional.

**Response:** `200`

#### `GET /v1/projects/{project_id}/issues`
List issues for a project.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| project_id | str | Project identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Cycles

#### `GET /v1/cycles`
List all cycles.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| teamId | str | — | — | Filter by team |
| status | str | — | — | Filter by status |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/cycles/{cycle_id}`
Get a single cycle.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| cycle_id | str | Cycle identifier |

**Response:** `200`

#### `POST /v1/cycles`
Create a cycle.

**Request Body:**
```json
{
  "name": "str (required)",
  "teamId": "str (required)",
  "startsAt": "str (required)",
  "endsAt": "str (required)"
}
```

**Response:** `201`

#### `GET /v1/cycles/{cycle_id}/issues`
List issues in a cycle.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| cycle_id | str | Cycle identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Issues

#### `GET /v1/issues`
List all issues with filters.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| stateId | str | — | — | Filter by workflow state |
| assigneeId | str | — | — | Filter by assignee |
| projectId | str | — | — | Filter by project |
| cycleId | str | — | — | Filter by cycle |
| teamId | str | — | — | Filter by team |
| priority | int | — | — | Filter by priority |
| labelId | str | — | — | Filter by label |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/issues/search`
Search issues.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| q | str | — | required | Search query |
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/issues/{issue_id}`
Get a single issue.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| issue_id | str | Issue identifier |

**Response:** `200`

#### `POST /v1/issues`
Create an issue.

**Request Body:**
```json
{
  "title": "str (required)",
  "teamId": "str (required)",
  "description": "str (optional)",
  "priority": "int (optional)",
  "estimate": "int (optional)",
  "stateId": "str (optional)",
  "assigneeId": "str (optional)",
  "projectId": "str (optional)",
  "cycleId": "str (optional)",
  "labelIds": ["str"],
  "dueDate": "str (optional)"
}
```

**Response:** `201`

#### `PUT /v1/issues/{issue_id}`
Update an issue.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| issue_id | str | Issue identifier |

**Request Body:**
Same fields as create (all optional), plus:
```json
{
  "sortOrder": "float (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/issues/{issue_id}`
Delete an issue.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| issue_id | str | Issue identifier |

**Response:** `200`

---

### Comments

#### `GET /v1/issues/{issue_id}/comments`
List comments on an issue.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| issue_id | str | Issue identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 50 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/comments/{comment_id}`
Get a single comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Response:** `200`

#### `POST /v1/comments`
Create a comment.

**Request Body:**
```json
{
  "body": "str (required)",
  "issueId": "str (required)",
  "userId": "str (optional)"
}
```

**Response:** `201`

#### `PUT /v1/comments/{comment_id}`
Update a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Request Body:**
```json
{
  "body": "str (required)"
}
```

**Response:** `200`

#### `DELETE /v1/comments/{comment_id}`
Delete a comment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| comment_id | str | Comment identifier |

**Response:** `200`

---

## 6. MyFitnessPal API

**Port:** 8005 | **Env Var:** `MYFITNESSPAL_API_URL` | **Version:** v1.0.0

### User Profile

#### `GET /v1/user/profile`
Get user profile.

**Response:** `200`

#### `PUT /v1/user/profile`
Update user profile.

**Request Body:**
```json
{
  "display_name": "str (optional)",
  "daily_calorie_goal": "int (optional)",
  "activity_level": "str (optional)",
  "current_weight_lbs": "float (optional)",
  "goal_weight_lbs": "float (optional)",
  "weekly_weight_goal_lbs": "float (optional)"
}
```

**Response:** `200`

---

### Goals

#### `GET /v1/user/goals`
Get user goals.

**Response:** `200`

#### `PUT /v1/user/goals`
Update user goals.

**Request Body:**
```json
{
  "daily_calorie_goal": "int (optional)",
  "macro_goals": {
    "carbs_pct": "int",
    "fat_pct": "int",
    "protein_pct": "int"
  },
  "goal_weight_lbs": "float (optional)",
  "weekly_weight_goal_lbs": "float (optional)"
}
```

**Response:** `200`

---

### Food Database

#### `GET /v1/foods/search`
Search the food database.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| q | str | — | — | Search query |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/foods/{food_id}`
Get a single food item.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| food_id | int | Food identifier |

**Response:** `200`

---

### Food Diary

#### `GET /v1/user/diary/{date}`
Get diary entries for a specific date.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date | str | Date string |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| meal | str | — | — | Filter by meal |

**Response:** `200`

#### `GET /v1/user/diary`
Get diary entries for a date range.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | required | Start date |
| end_date | str | — | required | End date |

**Response:** `200`

#### `POST /v1/user/diary`
Log a food diary entry.

**Request Body:**
```json
{
  "date": "str (required)",
  "meal": "str (required)",
  "food_id": "int (required)",
  "servings": "float (required)"
}
```

**Response:** `201`

#### `PUT /v1/user/diary/{entry_id}`
Update a diary entry.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| entry_id | int | Diary entry identifier |

**Request Body:**
```json
{
  "servings": "float (optional)",
  "meal": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v1/user/diary/{entry_id}`
Delete a diary entry.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| entry_id | int | Diary entry identifier |

**Response:** `200`

---

### Nutrition Summary

#### `GET /v1/user/nutrition/{date}`
Get daily nutrition totals.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date | str | Date string |

**Response:** `200`

#### `GET /v1/user/nutrition/weekly/{end_date}`
Get weekly nutrition summary.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| end_date | str | End date for the week |

**Response:** `200`

#### `GET /v1/user/progress`
Get progress over time.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| days | int | 30 | ge=1, le=90 | Number of days |

**Response:** `200`

---

### Exercise Types

#### `GET /v1/exercises/types`
List exercise types.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| category | str | — | — | Filter by category |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/exercises/types/{exercise_type_id}`
Get a single exercise type.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| exercise_type_id | int | Exercise type identifier |

**Response:** `200`

---

### Exercise Log

#### `GET /v1/user/exercises`
List logged exercises.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Filter start date |
| end_date | str | — | — | Filter end date |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/user/exercises/{exercise_id}`
Get a single exercise log entry.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| exercise_id | int | Exercise log identifier |

**Response:** `200`

#### `POST /v1/user/exercises`
Log an exercise.

**Request Body:**
```json
{
  "date": "str (required)",
  "exercise_type_id": "int (required)",
  "duration_minutes": "int (required)",
  "calories_burned": "int (required)",
  "notes": "str (optional)"
}
```

**Response:** `201`

---

### Weight Log

#### `GET /v1/user/weight`
List weight entries.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v1/user/weight/{weight_id}`
Get a single weight entry.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| weight_id | int | Weight entry identifier |

**Response:** `200`

#### `POST /v1/user/weight`
Log a weight entry.

**Request Body:**
```json
{
  "date": "str (required)",
  "weight_lbs": "float (required)",
  "notes": "str (optional)"
}
```

**Response:** `201`

---

### Water Intake

#### `GET /v1/user/water/{date}`
Get water intake for a date.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date | str | Date string |

**Response:** `200`

#### `POST /v1/user/water`
Log water intake.

**Request Body:**
```json
{
  "date": "str (required)",
  "cups": "int (required)",
  "notes": "str (optional)"
}
```

**Response:** `201`

#### `PUT /v1/user/water/{date}`
Update water intake for a date.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| date | str | Date string |

**Request Body:**
```json
{
  "cups": "int (optional)",
  "notes": "str (optional)"
}
```

**Response:** `200`

---

## 7. Pinterest API

**Port:** 8006 | **Env Var:** `PINTEREST_API_URL` | **Version:** v5.0.0

### User Account

#### `GET /v5/user_account`
Get authenticated user account info.

**Response:** `200`

#### `GET /v5/user_account/analytics`
Get user account analytics.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Analytics start date |
| end_date | str | — | — | Analytics end date |

**Response:** `200`

---

### Boards

#### `GET /v5/boards`
List boards.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| privacy | str | — | — | Filter by privacy setting |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v5/boards/{board_id}`
Get a single board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Response:** `200`

#### `POST /v5/boards`
Create a board.

**Request Body:**
```json
{
  "name": "str (required)",
  "description": "str (optional)",
  "privacy": "str (optional)"
}
```

**Response:** `201`

#### `PATCH /v5/boards/{board_id}`
Update a board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Request Body:**
```json
{
  "name": "str (optional)",
  "description": "str (optional)",
  "privacy": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v5/boards/{board_id}`
Delete a board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Response:** `200`

#### `GET /v5/boards/{board_id}/pins`
List pins on a board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Board Sections

#### `GET /v5/boards/{board_id}/sections`
List sections on a board.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Response:** `200`

#### `POST /v5/boards/{board_id}/sections`
Create a board section.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |

**Request Body:**
```json
{
  "name": "str (required)"
}
```

**Response:** `201`

#### `GET /v5/boards/{board_id}/sections/{section_id}/pins`
List pins in a board section.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| board_id | str | Board identifier |
| section_id | str | Section identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Pins

#### `GET /v5/pins`
List user's pins.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v5/pins/{pin_id}`
Get a single pin.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pin_id | str | Pin identifier |

**Response:** `200`

#### `POST /v5/pins`
Create a pin.

**Request Body:**
```json
{
  "board_id": "str (required)",
  "title": "str (required)",
  "description": "str (optional)",
  "link": "str (optional)",
  "media_type": "str (optional)",
  "board_section_id": "str (optional)",
  "dominant_color": "str (optional)",
  "alt_text": "str (optional)"
}
```

**Response:** `201`

#### `PATCH /v5/pins/{pin_id}`
Update a pin.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pin_id | str | Pin identifier |

**Request Body:**
```json
{
  "title": "str (optional)",
  "description": "str (optional)",
  "link": "str (optional)",
  "board_id": "str (optional)",
  "board_section_id": "str (optional)",
  "alt_text": "str (optional)"
}
```

**Response:** `200`

#### `DELETE /v5/pins/{pin_id}`
Delete a pin.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pin_id | str | Pin identifier |

**Response:** `200`

#### `GET /v5/pins/{pin_id}/analytics`
Get analytics for a pin.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| pin_id | str | Pin identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Analytics start date |
| end_date | str | — | — | Analytics end date |

**Response:** `200`

---

### Search

#### `GET /v5/search/pins`
Search pins.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| query | str | — | required | Search query |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

### Media

#### `GET /v5/media/{media_id}`
Get media upload status.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| media_id | str | Media identifier |

**Response:** `200`

---

### Ad Accounts

#### `GET /v5/ad_accounts`
List ad accounts.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /v5/ad_accounts/{ad_account_id}`
Get a single ad account.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ad_account_id | str | Ad account identifier |

**Response:** `200`

#### `GET /v5/ad_accounts/{ad_account_id}/campaigns`
List campaigns for an ad account.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| ad_account_id | str | Ad account identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| status | str | — | — | Filter by campaign status |
| limit | int | 25 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

---

## 8. QuickBooks Online API

**Port:** 8007 | **Env Var:** `QUICKBOOKS_API_URL` | **Version:** v3.0

All entity endpoints use the path prefix `/v3/company/{realm_id}/`.

### Company Info

#### `GET /v3/company/{realm_id}/companyinfo/{company_id}`
Get company information.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| company_id | str | Company identifier |

**Response:** `200`

---

### Customers

#### `GET /v3/company/{realm_id}/customer/{customer_id}`
Get a single customer.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| customer_id | str | Customer identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/customer`
Create or update a customer. If `Id` is present in the body, it updates; otherwise it creates.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "Id": "str (optional, include to update)",
  "DisplayName": "str (optional)",
  "GivenName": "str (optional)",
  "FamilyName": "str (optional)",
  "CompanyName": "str (optional)",
  "PrimaryEmailAddr": {"Address": "str"},
  "PrimaryPhone": {"FreeFormNumber": "str"},
  "BillAddr": {"Line1": "str", "City": "str"},
  "Active": "bool (optional)",
  "Notes": "str (optional)",
  "SyncToken": "str (optional)"
}
```

**Response:** `201` (created) or `200` (updated)

---

### Vendors

#### `GET /v3/company/{realm_id}/vendor/{vendor_id}`
Get a single vendor.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| vendor_id | str | Vendor identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/vendor`
Create or update a vendor.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "Id": "str (optional, include to update)",
  "DisplayName": "str (optional)",
  "CompanyName": "str (optional)",
  "PrimaryEmailAddr": "object (optional)",
  "PrimaryPhone": "object (optional)",
  "BillAddr": "object (optional)",
  "Active": "bool (optional)",
  "AcctNum": "str (optional)",
  "Vendor1099": "bool (optional)",
  "SyncToken": "str (optional)"
}
```

**Response:** `201` (created) or `200` (updated)

---

### Items

#### `GET /v3/company/{realm_id}/item/{item_id}`
Get a single item.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| item_id | str | Item identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/item`
Create or update an item.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "Id": "str (optional, include to update)",
  "Name": "str (optional)",
  "Description": "str (optional)",
  "Type": "str (optional)",
  "UnitPrice": "float (optional)",
  "IncomeAccountRef": {"value": "str", "name": "str"},
  "Active": "bool (optional)",
  "Taxable": "bool (optional)",
  "SyncToken": "str (optional)"
}
```

**Response:** `201` (created) or `200` (updated)

---

### Accounts

#### `GET /v3/company/{realm_id}/account/{account_id}`
Get a single account.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| account_id | str | Account identifier |

**Response:** `200`

---

### Invoices

#### `GET /v3/company/{realm_id}/invoice/{invoice_id}`
Get a single invoice.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| invoice_id | str | Invoice identifier |

**Response:** `200`

#### `GET /v3/company/{realm_id}/invoice/{invoice_id}/pdf`
Get invoice as PDF.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| invoice_id | str | Invoice identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/invoice`
Create or update an invoice. If `Id` is present in the body, it updates.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "Id": "str (optional, include to update)",
  "CustomerRef": {"value": "str"},
  "Line": [{}],
  "TxnDate": "str (optional)",
  "DueDate": "str (optional)",
  "BillEmail": {"Address": "str"},
  "PrintStatus": "str (optional)",
  "EmailStatus": "str (optional)",
  "SyncToken": "str (optional)"
}
```

**Response:** `201` (created) or `200` (updated)

#### `POST /v3/company/{realm_id}/invoice/{invoice_id}`
Perform an operation on an invoice (void, delete, or send).

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| invoice_id | str | Invoice identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| operation | str | — | — | Operation: "void", "delete", or "send" |
| include | str | — | — | Set to "send" to email invoice |

**Response:** `200`

---

### Bills

#### `GET /v3/company/{realm_id}/bill/{bill_id}`
Get a single bill.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| bill_id | str | Bill identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/bill`
Create a bill.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "VendorRef": "dict (required)",
  "Line": "list (required)",
  "TxnDate": "str (optional)",
  "DueDate": "str (optional)",
  "DocNumber": "str (optional)"
}
```

**Response:** `201`

#### `POST /v3/company/{realm_id}/bill/{bill_id}`
Pay a bill.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| bill_id | str | Bill identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| operation | str | — | — | Set to "pay" |

**Response:** `200`

---

### Payments

#### `GET /v3/company/{realm_id}/payment/{payment_id}`
Get a single payment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| payment_id | str | Payment identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/payment`
Create a payment.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "CustomerRef": "dict (required)",
  "TotalAmt": "float (required)",
  "Line": "list (required)",
  "TxnDate": "str (optional)"
}
```

**Response:** `201`

---

### Estimates

#### `GET /v3/company/{realm_id}/estimate/{estimate_id}`
Get a single estimate.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| estimate_id | str | Estimate identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/estimate`
Create an estimate.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "CustomerRef": "dict (required)",
  "Line": "list (required)",
  "TxnDate": "str (optional)",
  "ExpirationDate": "str (optional)"
}
```

**Response:** `201`

#### `POST /v3/company/{realm_id}/estimate/{estimate_id}`
Convert an estimate to an invoice.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| estimate_id | str | Estimate identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| operation | str | — | — | Set to "convert" |

**Response:** `200`

---

### Expenses (Purchases)

#### `GET /v3/company/{realm_id}/purchase/{expense_id}`
Get a single expense/purchase.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |
| expense_id | str | Expense identifier |

**Response:** `200`

#### `POST /v3/company/{realm_id}/purchase`
Create an expense/purchase.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Request Body:**
```json
{
  "AccountRef": "dict (required)",
  "PaymentType": "str (optional, default='CreditCard')",
  "Line": "list (required)",
  "TxnDate": "str (optional)"
}
```

**Response:** `201`

---

### Query

#### `GET /v3/company/{realm_id}/query`
Execute a SQL-like query against QuickBooks entities.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| query | str | — | required | SQL-like query string |

**Response:** `200`

---

### Reports

#### `GET /v3/company/{realm_id}/reports/ProfitAndLoss`
Get Profit and Loss report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Report start date |
| end_date | str | — | — | Report end date |

**Response:** `200`

#### `GET /v3/company/{realm_id}/reports/BalanceSheet`
Get Balance Sheet report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| start_date | str | — | — | Report start date |
| end_date | str | — | — | Report end date |

**Response:** `200`

#### `GET /v3/company/{realm_id}/reports/AgedReceivableDetail`
Get Aged Receivable Detail report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Response:** `200`

#### `GET /v3/company/{realm_id}/reports/AgedPayableDetail`
Get Aged Payable Detail report.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| realm_id | str | Company realm ID |

**Response:** `200`

---

## 9. Ring API

**Port:** 8008 | **Env Var:** `RING_API_URL` | **Version:** v1.0.0

### Devices

#### `GET /clients_api/ring_devices`
List all Ring devices.

**Response:** `200`

#### `GET /clients_api/doorbots/{device_id}`
Get a single device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

#### `GET /clients_api/doorbots/{device_id}/health`
Get device health status.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

#### `PUT /clients_api/doorbots/{device_id}/settings`
Update device settings.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Request Body:**
```json
{
  "motion_sensitivity": "int (optional)",
  "motion_detection_enabled": "bool (optional)",
  "people_detection_enabled": "bool (optional)",
  "package_detection_enabled": "bool (optional)",
  "led_status": "str (optional)",
  "light_schedule_enabled": "bool (optional)",
  "light_on_duration_seconds": "int (optional)"
}
```

**Response:** `200`

---

### Locations

#### `GET /clients_api/locations/{location_id}`
Get a single location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Response:** `200`

#### `GET /clients_api/locations/{location_id}/devices`
List devices at a location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Response:** `200`

#### `GET /clients_api/locations/{location_id}/mode`
Get current mode for a location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Response:** `200`

#### `PUT /clients_api/locations/{location_id}/mode`
Set mode for a location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Request Body:**
```json
{
  "mode": "str (required)"
}
```

**Response:** `200`

---

### Active Dings

#### `GET /clients_api/dings/active`
Get currently active dings (live events).

**Response:** `200`

---

### Event History

#### `GET /clients_api/doorbots/{device_id}/history`
Get event history for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| kind | str | — | — | Filter by event kind |
| date_from | str | — | — | Start date filter |
| date_to | str | — | — | End date filter |
| limit | int | 20 | ge=1, le=100 | Results per page |
| offset | int | — | ge=0 | Pagination offset |

**Response:** `200`

#### `GET /clients_api/dings/{event_id}`
Get a single event.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| event_id | int | Event identifier |

**Response:** `200`

---

### Recordings

#### `GET /clients_api/dings/{event_id}/recording`
Get recording for an event.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| event_id | int | Event identifier |

**Response:** `200`

#### `GET /clients_api/doorbots/{device_id}/recordings`
List recordings for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| date_from | str | — | — | Start date filter |
| date_to | str | — | — | End date filter |

**Response:** `200`

---

### Shared Users

#### `GET /clients_api/locations/{location_id}/users`
List shared users at a location.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |

**Response:** `200`

#### `GET /clients_api/locations/{location_id}/users/{user_id}`
Get a single shared user.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| location_id | str | Location identifier |
| user_id | int | User identifier |

**Response:** `200`

---

### Chime Settings

#### `GET /clients_api/chimes/{device_id}/settings`
Get chime settings.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Chime device identifier |

**Response:** `200`

#### `PUT /clients_api/chimes/{device_id}/link`
Link a chime to a doorbell.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Chime device identifier |

**Request Body:**
```json
{
  "doorbell_id": "int (required)"
}
```

**Response:** `200`

#### `PUT /clients_api/chimes/{device_id}/unlink`
Unlink a chime from a doorbell.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Chime device identifier |

**Request Body:**
```json
{
  "doorbell_id": "int (required)"
}
```

**Response:** `200`

---

### Motion Zones

#### `GET /clients_api/doorbots/{device_id}/motion_zones`
Get motion zones for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

---

### Notification Preferences

#### `GET /clients_api/notifications`
Get all notification preferences.

**Response:** `200`

#### `GET /clients_api/notifications/{device_id}`
Get notification preferences for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

#### `PUT /clients_api/notifications/{device_id}`
Update notification preferences for a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Request Body:**
```json
{
  "motion_alerts": "bool (optional)",
  "ding_alerts": "bool (optional)",
  "person_alerts": "bool (optional)",
  "package_alerts": "bool (optional)"
}
```

**Response:** `200`

---

### Siren

#### `POST /clients_api/doorbots/{device_id}/siren_on`
Activate siren on a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Request Body:**
```json
{
  "duration_seconds": "int (optional, default=30)"
}
```

**Response:** `200`

#### `POST /clients_api/doorbots/{device_id}/siren_off`
Deactivate siren on a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Response:** `200`

---

### Floodlight

#### `PUT /clients_api/doorbots/{device_id}/floodlight_light_on`
Control floodlight on a device.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| device_id | int | Device identifier |

**Request Body:**
```json
{
  "on": "bool (required)"
}
```

**Response:** `200`

---

## 10. YouTube Data API

**Port:** 8009 | **Env Var:** `YOUTUBE_API_URL` | **Version:** v3.0

### Channels

#### `GET /youtube/v3/channels`
List channels.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | — | Channel ID |
| part | str | "snippet,contentDetails,statistics,brandingSettings" | — | Resource parts to include |

**Response:** `200`

---

### Videos

#### `GET /youtube/v3/videos`
List videos.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | — | Video ID |
| channelId | str | — | — | Filter by channel |
| part | str | "snippet,contentDetails,statistics,status" | — | Resource parts to include |
| maxResults | int | 25 | ge=1, le=50 | Max results |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `PUT /youtube/v3/videos`
Update a video.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts to update |

**Request Body:**
```json
{
  "id": "str (required)",
  "snippet": "dict (optional)",
  "status": "dict (optional)"
}
```

**Response:** `200`

#### `DELETE /youtube/v3/videos`
Delete a video.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Video ID to delete |

**Response:** `200`

---

### Playlists

#### `GET /youtube/v3/playlists`
List playlists.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | — | Playlist ID |
| channelId | str | — | — | Filter by channel |
| part | str | — | — | Resource parts to include |
| maxResults | int | 25 | ge=1, le=50 | Max results |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `POST /youtube/v3/playlists`
Create a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts |

**Request Body:**
```json
{
  "snippet": "dict (required)",
  "status": "dict (optional)"
}
```

**Response:** `201`

#### `PUT /youtube/v3/playlists`
Update a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts to update |

**Request Body:**
```json
{
  "id": "str (required)",
  "snippet": "dict (optional)",
  "status": "dict (optional)"
}
```

**Response:** `200`

#### `DELETE /youtube/v3/playlists`
Delete a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Playlist ID to delete |

**Response:** `200`

---

### Playlist Items

#### `GET /youtube/v3/playlistItems`
List items in a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| playlistId | str | — | required | Playlist ID |
| part | str | — | — | Resource parts to include |
| maxResults | int | 25 | ge=1, le=50 | Max results |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `POST /youtube/v3/playlistItems`
Add an item to a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts |

**Request Body:**
```json
{
  "snippet": "dict (required)"
}
```

**Response:** `201`

#### `PUT /youtube/v3/playlistItems`
Update a playlist item.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts to update |

**Request Body:**
```json
{
  "id": "str (required)",
  "snippet": "dict (optional)"
}
```

**Response:** `200`

#### `DELETE /youtube/v3/playlistItems`
Remove an item from a playlist.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Playlist item ID to delete |

**Response:** `200`

---

### Comment Threads

#### `GET /youtube/v3/commentThreads`
List comment threads.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| videoId | str | — | — | Filter by video |
| channelId | str | — | — | Filter by channel |
| part | str | — | — | Resource parts to include |
| maxResults | int | 20 | ge=1, le=100 | Max results |
| moderationStatus | str | "published" | — | Filter by moderation status |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `POST /youtube/v3/commentThreads`
Create a new top-level comment thread.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts |

**Request Body:**
```json
{
  "snippet": "dict (required)"
}
```

**Response:** `201`

---

### Comments

#### `GET /youtube/v3/comments`
List replies to a comment.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| parentId | str | — | required | Parent comment ID |
| part | str | — | — | Resource parts to include |
| maxResults | int | 20 | ge=1, le=100 | Max results |
| pageToken | str | — | — | Pagination token |

**Response:** `200`

#### `POST /youtube/v3/comments`
Post a reply to a comment.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts |

**Request Body:**
```json
{
  "snippet": "dict (required)"
}
```

**Response:** `201`

#### `PUT /youtube/v3/comments`
Update a comment.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| part | str | — | — | Resource parts to update |

**Request Body:**
```json
{
  "id": "str (required)",
  "snippet": "dict (optional)"
}
```

**Response:** `200`

#### `DELETE /youtube/v3/comments`
Delete a comment.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Comment ID to delete |

**Response:** `200`

#### `POST /youtube/v3/comments/setModerationStatus`
Set moderation status for one or more comments.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| id | str | — | required | Comma-separated comment IDs |
| moderationStatus | str | — | required | New moderation status |

**Response:** `200`

---

### Search

#### `GET /youtube/v3/search`
Search YouTube.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| q | str | — | — | Search query |
| channelId | str | — | — | Filter by channel |
| part | str | — | — | Resource parts to include |
| order | str | "relevance" | — | Sort order |
| maxResults | int | 25 | ge=1, le=50 | Max results |
| pageToken | str | — | — | Pagination token |
| type | str | "video" | — | Resource type filter |

**Response:** `200`

---

### Video Categories

#### `GET /youtube/v3/videoCategories`
List video categories.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| regionCode | str | "US" | — | Region code |
| part | str | — | — | Resource parts to include |

**Response:** `200`

---

### Captions

#### `GET /youtube/v3/captions`
List captions for a video.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| videoId | str | — | required | Video ID |
| part | str | — | — | Resource parts to include |

**Response:** `200`

---

### Channel Sections

#### `GET /youtube/v3/channelSections`
List channel sections.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| channelId | str | — | required | Channel ID |
| part | str | "snippet,contentDetails" | — | Resource parts to include |

**Response:** `200`

---

### Analytics

#### `GET /youtube/analytics/v2/reports`
Get YouTube Analytics reports.

**Query Parameters:**
| Name | Type | Default | Constraints | Description |
|------|------|---------|-------------|-------------|
| ids | str | "channel==UC_TechCraftAcademy" | — | Channel identifier |
| metrics | str | "views,estimatedMinutesWatched,subscribersGained" | — | Comma-separated metrics |
| dimensions | str | — | — | Report dimensions |
| filters | str | — | — | Filters (e.g. "video==VIDEO_ID") |
| startDate | str | — | — | Report start date |
| endDate | str | — | — | Report end date |

**Response:** `200`
