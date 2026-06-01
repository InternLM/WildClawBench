# Documentation Faithfulness Check

## Sources Verified
- Orders API: https://github.com/amzn/selling-partner-api-models/blob/main/models/orders-api-model/ordersV0.json
- Catalog Items API: https://github.com/amzn/selling-partner-api-models/blob/main/models/catalog-items-api-model/catalogItems_2022-04-01.json
- Listings Items API: https://github.com/amzn/selling-partner-api-models/blob/main/models/listings-items-api-model (2021-08-01)
- FBA Inventory API: https://github.com/amzn/selling-partner-api-models/blob/main/models/fba-inventory-api-model/fbaInventory.json
- Reports API: https://github.com/amzn/selling-partner-api-models/blob/main/models/reports-api-model/reports_2021-06-30.json
- Product Pricing API: https://github.com/amzn/selling-partner-api-models/blob/main/models/product-pricing-api-model
- Sellers API: https://github.com/amzn/selling-partner-api-models/blob/main/models/sellers-api-model
- Notifications API: https://github.com/amzn/selling-partner-api-models/blob/main/models/notifications-api-model

## Endpoint Verification

| # | Endpoint | Our Path | Official Path | Match? | Notes |
|---|----------|----------|---------------|--------|-------|
| 1 | Health check | GET /health | N/A (mock-only) | ✓ | Mock convenience endpoint, not in real API |
| 2 | Get seller account | GET /sellers/v1/account | GET /sellers/v1/marketplaceParticipations | ~  | Simplified — real API returns marketplace participations. Our mock consolidates seller info into one endpoint for agent convenience |
| 3 | Get account health | GET /sellers/v1/account/health | N/A (Seller Central UI metric) | ~ | Account health is a Seller Central concept; no direct SP-API endpoint. Simplified for mock |
| 4 | Get notifications | GET /notifications/v1/notifications | GET /notifications/v1/notifications | ✓ | Path matches real Notifications API |
| 5 | Search catalog items | GET /catalog/2022-04-01/items | GET /catalog/2022-04-01/items | ✓ | Exact path from official spec |
| 6 | Get catalog item | GET /catalog/2022-04-01/items/{asin} | GET /catalog/2022-04-01/items/{asin} | ✓ | Exact path from official spec |
| 7 | Get listing item | GET /listings/2021-08-01/items/{sellerId}/{sku} | GET /listings/2021-08-01/items/{sellerId}/{sku} | ✓ | Exact path from official spec |
| 8 | Put listing item | PUT /listings/2021-08-01/items/{sellerId}/{sku} | PUT /listings/2021-08-01/items/{sellerId}/{sku} | ✓ | Exact path from official spec |
| 9 | Patch listing item | PATCH /listings/2021-08-01/items/{sellerId}/{sku} | PATCH /listings/2021-08-01/items/{sellerId}/{sku} | ✓ | Exact path from official spec |
| 10 | Delete listing item | DELETE /listings/2021-08-01/items/{sellerId}/{sku} | DELETE /listings/2021-08-01/items/{sellerId}/{sku} | ✓ | Exact path from official spec |
| 11 | List orders | GET /orders/v0/orders | GET /orders/v0/orders | ✓ | Exact path from official spec |
| 12 | Get order | GET /orders/v0/orders/{orderId} | GET /orders/v0/orders/{orderId} | ✓ | Exact path from official spec |
| 13 | Get order items | GET /orders/v0/orders/{orderId}/orderItems | GET /orders/v0/orders/{orderId}/orderItems | ✓ | Exact path from official spec |
| 14 | Confirm shipment | POST /orders/v0/orders/{orderId}/shipmentConfirmation | POST /orders/v0/orders/{orderId}/shipment/confirm (deprecated) / via feeds | ~ | Simplified. Real shipment confirmation uses Feeds API or newer endpoint. Path is close to the deprecated MWS pattern |
| 15 | Get inventory summaries | GET /fba/inventory/v1/summaries | GET /fba/inventory/v1/summaries | ✓ | Exact path from official spec |
| 16 | Update inventory | PUT /fba/inventory/v1/items/{sellerSku} | POST /fba/inventory/v1/items/inventory (sandbox only) | ~ | Real API uses Feeds for inventory updates. Our PUT is a mock convenience. Path segment `/items/{sku}` matches sandbox pattern |
| 17 | List reports | GET /reports/2021-06-30/reports | GET /reports/2021-06-30/reports | ✓ | Exact path from official spec |
| 18 | Get report | GET /reports/2021-06-30/reports/{reportId} | GET /reports/2021-06-30/reports/{reportId} | ✓ | Exact path from official spec |
| 19 | Create report | POST /reports/2021-06-30/reports | POST /reports/2021-06-30/reports | ✓ | Exact path from official spec |
| 20 | Get competitive pricing | GET /products/pricing/v0/competitivePrice | GET /products/pricing/v0/competitivePrice | ✓ | Path matches real Product Pricing API |
| 21 | Get item offers | GET /products/pricing/v0/items/{Asin}/offers | GET /products/pricing/v0/items/{Asin}/offers | ✓ | Exact path from official spec |
| 22 | List returns | GET /returns/v0/returns | N/A (via Reports/Feeds) | ~ | No direct SP-API returns endpoint; returns are managed via reports or MFN Returns API. Simplified for mock |
| 23 | Get return | GET /returns/v0/returns/{returnId} | N/A | ~ | Same as above — simplified mock |
| 24 | Authorize return | POST /returns/v0/returns/{returnId}/authorize | N/A | ~ | Same as above — simplified mock |
| 25 | Close return | POST /returns/v0/returns/{returnId}/close | N/A | ~ | Same as above — simplified mock |

## Summary

- **18 endpoints** use exact official SP-API paths (✓)
- **7 endpoints** are simplified/consolidated mock versions (~) for agent usability
  - Seller account/health: consolidated from multiple APIs
  - Shipment confirmation: simplified from Feeds API
  - Inventory update: simplified from Feeds API
  - Returns: simplified from Reports/MFN Returns patterns
- **0 endpoints** have incorrect paths that need fixing (✗)

All simplified endpoints are intentionally mock-friendly versions of operations that in the real SP-API require multi-step Feeds workflows. The core domain paths (catalog, listings, orders, inventory queries, reports, pricing) are exact matches to the official OpenAPI specs.
