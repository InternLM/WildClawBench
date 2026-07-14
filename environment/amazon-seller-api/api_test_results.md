# Amazon Seller API - Full Automated Test Results

Generated: 2026-05-06T18:29:21Z

## 1. GET /health (Health check)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/health"
```

**HTTP Status:** 200

```json
{
    "status": "ok"
}
```

---

## 2. GET /sellers/v1/account (Get seller account)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/sellers/v1/account"
```

**HTTP Status:** 200

```json
{
    "type": "seller_account",
    "seller": {
        "sellerId": "A3EXAMPLE1SELLER",
        "marketplaceId": "ATVPDKIKX0DER",
        "businessName": "VoltEdge Tech LLC",
        "storeName": "VoltEdge Tech",
        "storeUrl": "https://www.amazon.com/stores/VoltEdgeTech/page/EXAMPLE-PAGE-ID",
        "registrationDate": "2024-02-15T08:00:00Z",
        "businessAddress": {
            "Name": "VoltEdge Tech LLC",
            "AddressLine1": "4521 Innovation Drive",
            "AddressLine2": "Suite 200",
            "City": "San Jose",
            "StateOrRegion": "CA",
            "PostalCode": "95134",
            "CountryCode": "US"
        },
        "primaryContactEmail": "seller@voltedgetech.com",
        "accountHealth": {
            "orderDefectRate": 0.8,
            "orderDefectRateTarget": 1.0,
            "lateShipmentRate": 2.1,
            "lateShipmentRateTarget": 4.0,
            "preFulfillmentCancelRate": 1.2,
            "preFulfillmentCancelRateTarget": 2.5,
            "validTrackingRate": 96.5,
            "validTrackingRateTarget": 95.0,
            "onTimeDeliveryRate": 94.8,
            "onTimeDeliveryRateTarget": 90.0,
            "returnDissatisfactionRate": 3.2,
            "returnDissatisfactionRateTarget": 10.0,
            "customerServiceDissatisfactionRate": 1.5,
            "customerServiceDissatisfactionRateTarget": 25.0,
            "policyViolations": 0,
            "accountStatus": "NORMAL"
        },
        "performanceNotifications": [
            {
                "notificationId": "NOTIF-001",
                "type": "PERFORMANCE_WARNING",
                "title": "Late Shipment Rate Approaching Threshold",
                "message": "Your late shipment rate of 2.1% is approaching the 4% target. Please ensure orders are shipped by the expected ship date.",
                "severity": "WARNING",
                "createdDate": "2026-04-20T14:30:00Z",
                "isRead": true
            },
            {
                "notificationId": "NOTIF-002",
                "type": "LISTING_DEACTIVATED",
                "title": "Listing Suppressed - Missing Product Image",
                "message": "Your listing for SKU VE-USBHUB-7P has been suppressed due to a missing main product image. Please upload a compliant image to reactivate.",
                "severity": "CRITICAL",
                "createdDate": "2026-04-25T09:15:00Z",
                "isRead": false
            },
            {
                "notificationId": "NOTIF-003",
                "type": "INFO",
                "title": "FBA Inventory Restock Recommendation",
                "message": "Based on your sales velocity, we recommend restocking VE-CASE-IP15 and VE-CHRG-USB3 within the next 14 days to avoid stockouts.",
                "severity": "INFO",
                "createdDate": "2026-04-28T11:00:00Z",
                "isRead": false
            }
        ]
    }
}
```

---

## 3. GET /sellers/v1/account/health (Get account health)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/sellers/v1/account/health"
```

**HTTP Status:** 200

```json
{
    "type": "account_health",
    "accountHealth": {
        "orderDefectRate": 0.8,
        "orderDefectRateTarget": 1.0,
        "lateShipmentRate": 2.1,
        "lateShipmentRateTarget": 4.0,
        "preFulfillmentCancelRate": 1.2,
        "preFulfillmentCancelRateTarget": 2.5,
        "validTrackingRate": 96.5,
        "validTrackingRateTarget": 95.0,
        "onTimeDeliveryRate": 94.8,
        "onTimeDeliveryRateTarget": 90.0,
        "returnDissatisfactionRate": 3.2,
        "returnDissatisfactionRateTarget": 10.0,
        "customerServiceDissatisfactionRate": 1.5,
        "customerServiceDissatisfactionRateTarget": 25.0,
        "policyViolations": 0,
        "accountStatus": "NORMAL"
    }
}
```

---

## 4. GET /notifications/v1/notifications (Get all notifications)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/notifications/v1/notifications"
```

**HTTP Status:** 200

```json
{
    "type": "notifications",
    "count": 3,
    "results": [
        {
            "notificationId": "NOTIF-001",
            "type": "PERFORMANCE_WARNING",
            "title": "Late Shipment Rate Approaching Threshold",
            "message": "Your late shipment rate of 2.1% is approaching the 4% target. Please ensure orders are shipped by the expected ship date.",
            "severity": "WARNING",
            "createdDate": "2026-04-20T14:30:00Z",
            "isRead": true
        },
        {
            "notificationId": "NOTIF-002",
            "type": "LISTING_DEACTIVATED",
            "title": "Listing Suppressed - Missing Product Image",
            "message": "Your listing for SKU VE-USBHUB-7P has been suppressed due to a missing main product image. Please upload a compliant image to reactivate.",
            "severity": "CRITICAL",
            "createdDate": "2026-04-25T09:15:00Z",
            "isRead": false
        },
        {
            "notificationId": "NOTIF-003",
            "type": "INFO",
            "title": "FBA Inventory Restock Recommendation",
            "message": "Based on your sales velocity, we recommend restocking VE-CASE-IP15 and VE-CHRG-USB3 within the next 14 days to avoid stockouts.",
            "severity": "INFO",
            "createdDate": "2026-04-28T11:00:00Z",
            "isRead": false
        }
    ]
}
```

---

## 5. GET /notifications/v1/notifications?severity=WARNING (Get notifications filtered by WARNING)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/notifications/v1/notifications?severity=WARNING"
```

**HTTP Status:** 200

```json
{
    "type": "notifications",
    "count": 1,
    "results": [
        {
            "notificationId": "NOTIF-001",
            "type": "PERFORMANCE_WARNING",
            "title": "Late Shipment Rate Approaching Threshold",
            "message": "Your late shipment rate of 2.1% is approaching the 4% target. Please ensure orders are shipped by the expected ship date.",
            "severity": "WARNING",
            "createdDate": "2026-04-20T14:30:00Z",
            "isRead": true
        }
    ]
}
```

---

## 6. GET /notifications/v1/notifications?severity=CRITICAL (Get notifications filtered by CRITICAL)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/notifications/v1/notifications?severity=CRITICAL"
```

**HTTP Status:** 200

```json
{
    "type": "notifications",
    "count": 1,
    "results": [
        {
            "notificationId": "NOTIF-002",
            "type": "LISTING_DEACTIVATED",
            "title": "Listing Suppressed - Missing Product Image",
            "message": "Your listing for SKU VE-USBHUB-7P has been suppressed due to a missing main product image. Please upload a compliant image to reactivate.",
            "severity": "CRITICAL",
            "createdDate": "2026-04-25T09:15:00Z",
            "isRead": false
        }
    ]
}
```

---

## 7. GET /catalog/2022-04-01/items?pageSize=20&marketplaceIds=ATVPDKIKX0DER (List all catalog items)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/catalog/2022-04-01/items?pageSize=20&marketplaceIds=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "catalog_items",
    "numberOfResults": 18,
    "pagination": {
        "nextToken": null,
        "previousToken": null
    },
    "items": [
        {
            "asin": "B0EXAMPLE01",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge Slim Armor Case for iPhone 15 - Matte Black",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Military-grade drop protection (MIL-STD-810G tested)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Slim profile at only 1.2mm thick",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Raised bezels protect camera and screen",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Compatible with MagSafe and wireless charging",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Precision cutouts for all ports and buttons",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 19.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.08,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 6.2
                        },
                        "width": {
                            "unit": "inches",
                            "value": 3.1
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "CELLULAR_PHONE_CASE",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example01.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge Slim Armor Case for iPhone 15 - Matte Black",
                    "productType": "CELLULAR_PHONE_CASE",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE02",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge Slim Armor Case for iPhone 15 Pro - Navy Blue",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Military-grade drop protection",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Anti-fingerprint matte coating",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Slim 1.2mm profile",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Full MagSafe compatibility",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Lifetime warranty included",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 21.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.09,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 6.3
                        },
                        "width": {
                            "unit": "inches",
                            "value": 3.2
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "CELLULAR_PHONE_CASE",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example02.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge Slim Armor Case for iPhone 15 Pro - Navy Blue",
                    "productType": "CELLULAR_PHONE_CASE",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE03",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge Tempered Glass Screen Protector for iPhone 15 (3-Pack)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "9H hardness tempered glass",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Oleophobic anti-fingerprint coating",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "99.9% HD clarity",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Easy install alignment frame included",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "3-pack value bundle",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 12.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.12,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 7.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 4.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.8
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "SCREEN_PROTECTOR",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example03.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge Tempered Glass Screen Protector for iPhone 15 (3-Pack)",
                    "productType": "SCREEN_PROTECTOR",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE04",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge 6ft USB-C to USB-C Fast Charging Cable (2-Pack)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "100W Power Delivery fast charging",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "USB 3.2 Gen 2 - 10Gbps data transfer",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Premium braided nylon - 10000+ bend tested",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Universal USB-C compatibility",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "2-pack 6ft cables",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 16.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.15,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 8.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 5.5
                        },
                        "height": {
                            "unit": "inches",
                            "value": 1.0
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "USB_CABLE",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example04.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge 6ft USB-C to USB-C Fast Charging Cable (2-Pack)",
                    "productType": "USB_CABLE",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE05",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge 3ft MFi Certified Lightning Cable - White",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Apple MFi Certified for reliability",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "30W fast charging support",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Reinforced strain relief connectors",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Premium TPE jacket",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Compatible with all Lightning devices",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 14.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.05,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 5.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 3.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "USB_CABLE",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example05.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge 3ft MFi Certified Lightning Cable - White",
                    "productType": "USB_CABLE",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE06",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Hybrid Active Noise Cancellation",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "36-hour total battery (8h + 28h case)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "IPX5 water and sweat resistant",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Bluetooth 5.3 with multipoint",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Premium 10mm drivers with deep bass",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 49.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.35,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 4.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 4.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 2.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "HEADPHONES",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example06.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                    "productType": "HEADPHONES",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE07",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge FitPulse Sport Wireless Earbuds - IPX7",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "IPX7 waterproof - swim-safe",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Secure over-ear hook design",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "10-hour single charge playback",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Ambient sound mode for safety",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Quick charge: 10 min = 2 hours",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 34.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.28,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 5.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 5.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 2.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "HEADPHONES",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example07.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge FitPulse Sport Wireless Earbuds - IPX7",
                    "productType": "HEADPHONES",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE08",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge ErgoRise Adjustable Laptop Stand - Silver Aluminum",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "6 adjustable height angles",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Premium aluminum alloy construction",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Supports up to 17 inch laptops (22 lbs)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Foldable portable design",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Silicone pads prevent scratches and sliding",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 29.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 1.8,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 10.5
                        },
                        "width": {
                            "unit": "inches",
                            "value": 9.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.6
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "LAPTOP_STAND",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example08.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge ErgoRise Adjustable Laptop Stand - Silver Aluminum",
                    "productType": "LAPTOP_STAND",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE09",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge ErgoRise Pro Laptop Stand with Cooling Fan - Black",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Dual quiet cooling fans (25dB)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Integrated USB 3.0 hub (2 ports)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Adjustable height and tilt angle",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Supports up to 17 inch laptops",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Built-in cable management",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 44.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 2.4,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 14.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 10.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 1.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "LAPTOP_STAND",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example09.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge ErgoRise Pro Laptop Stand with Cooling Fan - Black",
                    "productType": "LAPTOP_STAND",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE10",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge 7-in-1 USB-C Hub - HDMI 4K SD Card Reader",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "4K@60Hz HDMI output",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "100W USB-C Power Delivery passthrough",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "SD and microSD card reader",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "2x USB 3.0 ports (5Gbps)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Gigabit Ethernet port",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 39.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.22,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 4.5
                        },
                        "width": {
                            "unit": "inches",
                            "value": 2.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.6
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "USB_HUB",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example10.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge 7-in-1 USB-C Hub - HDMI 4K SD Card Reader",
                    "productType": "USB_HUB",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE11",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge PowerVault 10000mAh Portable Charger - USB-C PD 20W",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "20W USB-C Power Delivery",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "18W Quick Charge 3.0 output",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "10000mAh capacity (charges iPhone 2x)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Compact pocket-friendly size",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "LED battery level indicator",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 24.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.48,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 5.2
                        },
                        "width": {
                            "unit": "inches",
                            "value": 2.7
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.6
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "PORTABLE_POWER_BANK",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example11.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge PowerVault 10000mAh Portable Charger - USB-C PD 20W",
                    "productType": "PORTABLE_POWER_BANK",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE12",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge PowerVault Pro 20000mAh with 65W USB-C",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "65W USB-C PD - charges laptops",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "20000mAh high capacity",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Dual USB-C + USB-A (3 devices simultaneously)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Digital LED display shows exact %",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Airline approved (72Wh)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 44.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.92,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 6.5
                        },
                        "width": {
                            "unit": "inches",
                            "value": 3.2
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.9
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "PORTABLE_POWER_BANK",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example12.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge PowerVault Pro 20000mAh with 65W USB-C",
                    "productType": "PORTABLE_POWER_BANK",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE13",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge 65W GaN USB-C Wall Charger - Dual Port",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "65W GaN technology - 50% smaller than traditional",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Dual USB-C ports with smart power split",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Foldable prongs for easy travel",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Universal voltage (100-240V)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "PPS support for Samsung super fast charging",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 32.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.18,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 2.5
                        },
                        "width": {
                            "unit": "inches",
                            "value": 2.5
                        },
                        "height": {
                            "unit": "inches",
                            "value": 1.2
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "POWER_ADAPTER",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example13.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge 65W GaN USB-C Wall Charger - Dual Port",
                    "productType": "POWER_ADAPTER",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE14",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge Tempered Glass for Samsung Galaxy S24 Ultra (2-Pack)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Fingerprint sensor compatible",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "9H hardness tempered glass",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "UV blue light filter coating",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Full adhesive coverage",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Installation kit with alignment tool",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 15.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.1,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 7.5
                        },
                        "width": {
                            "unit": "inches",
                            "value": 4.5
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.6
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "SCREEN_PROTECTOR",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example14.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge Tempered Glass for Samsung Galaxy S24 Ultra (2-Pack)",
                    "productType": "SCREEN_PROTECTOR",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE15",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge Clear Hybrid Case for Samsung Galaxy S24 Ultra",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Anti-yellowing crystal clear design",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Military-grade corner protection",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Slim 1.5mm profile",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Raised bezels for camera module",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Wireless charging compatible",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 17.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.07,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 6.5
                        },
                        "width": {
                            "unit": "inches",
                            "value": 3.3
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "CELLULAR_PHONE_CASE",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example15.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge Clear Hybrid Case for Samsung Galaxy S24 Ultra",
                    "productType": "CELLULAR_PHONE_CASE",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE16",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge MagSnap 15W Wireless Charger Pad - Black",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "15W MagSafe fast charging",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Strong magnetic alignment",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Foreign object detection for safety",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "LED charging indicator",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Includes 4ft USB-C cable",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 22.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.25,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 3.5
                        },
                        "width": {
                            "unit": "inches",
                            "value": 3.5
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.4
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "WIRELESS_CHARGER",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example16.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge MagSnap 15W Wireless Charger Pad - Black",
                    "productType": "WIRELESS_CHARGER",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE17",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge 45W Dual USB-C Car Charger with LED",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "45W total output (30W + 15W)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Dual USB-C PD 3.0 ports",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Compact flush-mount design",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Blue LED power indicator",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Wide compatibility: phones tablets GPS",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 18.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.06,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 2.8
                        },
                        "width": {
                            "unit": "inches",
                            "value": 1.2
                        },
                        "height": {
                            "unit": "inches",
                            "value": 1.2
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "CAR_CHARGER",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example17.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge 45W Dual USB-C Car Charger with LED",
                    "productType": "CAR_CHARGER",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE18",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge Magnetic USB-C Charging Cable 6ft - 100W PD",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Magnetic breakaway connector",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "100W Power Delivery charging",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "10Gbps USB 3.2 data transfer",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Premium braided 6ft cable",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "LED connection indicator",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 27.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.18,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 8.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 4.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 1.0
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "USB_CABLE",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example18.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge Magnetic USB-C Charging Cable 6ft - 100W PD",
                    "productType": "USB_CABLE",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        }
    ]
}
```

---

## 8. GET /catalog/2022-04-01/items?keywords=earbuds&pageSize=10 (Search catalog by keyword)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/catalog/2022-04-01/items?keywords=earbuds&pageSize=10"
```

**HTTP Status:** 200

```json
{
    "type": "catalog_items",
    "numberOfResults": 2,
    "pagination": {
        "nextToken": null,
        "previousToken": null
    },
    "items": [
        {
            "asin": "B0EXAMPLE06",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Hybrid Active Noise Cancellation",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "36-hour total battery (8h + 28h case)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "IPX5 water and sweat resistant",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Bluetooth 5.3 with multipoint",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Premium 10mm drivers with deep bass",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 49.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.35,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 4.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 4.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 2.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "HEADPHONES",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example06.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                    "productType": "HEADPHONES",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE07",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge FitPulse Sport Wireless Earbuds - IPX7",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "IPX7 waterproof - swim-safe",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Secure over-ear hook design",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "10-hour single charge playback",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Ambient sound mode for safety",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Quick charge: 10 min = 2 hours",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 34.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.28,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 5.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 5.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 2.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "HEADPHONES",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example07.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge FitPulse Sport Wireless Earbuds - IPX7",
                    "productType": "HEADPHONES",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        }
    ]
}
```

---

## 9. GET /catalog/2022-04-01/items?identifiers=B0EXAMPLE01,B0EXAMPLE06&identifiersType=ASIN (Search catalog by ASIN identifiers)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/catalog/2022-04-01/items?identifiers=B0EXAMPLE01,B0EXAMPLE06&identifiersType=ASIN"
```

**HTTP Status:** 200

```json
{
    "type": "catalog_items",
    "numberOfResults": 2,
    "pagination": {
        "nextToken": null,
        "previousToken": null
    },
    "items": [
        {
            "asin": "B0EXAMPLE01",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge Slim Armor Case for iPhone 15 - Matte Black",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Military-grade drop protection (MIL-STD-810G tested)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Slim profile at only 1.2mm thick",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Raised bezels protect camera and screen",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Compatible with MagSafe and wireless charging",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Precision cutouts for all ports and buttons",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 19.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.08,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 6.2
                        },
                        "width": {
                            "unit": "inches",
                            "value": 3.1
                        },
                        "height": {
                            "unit": "inches",
                            "value": 0.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "CELLULAR_PHONE_CASE",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example01.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge Slim Armor Case for iPhone 15 - Matte Black",
                    "productType": "CELLULAR_PHONE_CASE",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        },
        {
            "asin": "B0EXAMPLE06",
            "attributes": {
                "item_name": [
                    {
                        "value": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "brand": [
                    {
                        "value": "VoltEdge Tech",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "bullet_point": [
                    {
                        "value": "Hybrid Active Noise Cancellation",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "36-hour total battery (8h + 28h case)",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "IPX5 water and sweat resistant",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Bluetooth 5.3 with multipoint",
                        "marketplace_id": "ATVPDKIKX0DER"
                    },
                    {
                        "value": "Premium 10mm drivers with deep bass",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "list_price": [
                    {
                        "currency": "USD",
                        "value": 49.99,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_weight": [
                    {
                        "unit": "pounds",
                        "value": 0.35,
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "item_dimensions": [
                    {
                        "length": {
                            "unit": "inches",
                            "value": 4.0
                        },
                        "width": {
                            "unit": "inches",
                            "value": 4.0
                        },
                        "height": {
                            "unit": "inches",
                            "value": 2.5
                        },
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "condition_type": [
                    {
                        "value": "NEW",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ],
                "product_type": [
                    {
                        "value": "HEADPHONES",
                        "marketplace_id": "ATVPDKIKX0DER"
                    }
                ]
            },
            "images": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "images": [
                        {
                            "variant": "MAIN",
                            "link": "https://m.media-amazon.com/images/I/example06.jpg",
                            "height": 1000,
                            "width": 1000
                        }
                    ]
                }
            ],
            "salesRanks": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "classificationRanks": [
                        {
                            "classificationId": "172282",
                            "title": "Electronics",
                            "rank": 5420
                        }
                    ]
                }
            ],
            "summaries": [
                {
                    "marketplaceId": "ATVPDKIKX0DER",
                    "brandName": "VoltEdge Tech",
                    "itemName": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                    "productType": "HEADPHONES",
                    "itemClassification": "BASE_PRODUCT"
                }
            ]
        }
    ]
}
```

---

## 10. GET /catalog/2022-04-01/items/B0EXAMPLE06 (Get catalog item by ASIN)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/catalog/2022-04-01/items/B0EXAMPLE06"
```

**HTTP Status:** 200

```json
{
    "type": "catalog_item",
    "item": {
        "asin": "B0EXAMPLE06",
        "attributes": {
            "item_name": [
                {
                    "value": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "brand": [
                {
                    "value": "VoltEdge Tech",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "bullet_point": [
                {
                    "value": "Hybrid Active Noise Cancellation",
                    "marketplace_id": "ATVPDKIKX0DER"
                },
                {
                    "value": "36-hour total battery (8h + 28h case)",
                    "marketplace_id": "ATVPDKIKX0DER"
                },
                {
                    "value": "IPX5 water and sweat resistant",
                    "marketplace_id": "ATVPDKIKX0DER"
                },
                {
                    "value": "Bluetooth 5.3 with multipoint",
                    "marketplace_id": "ATVPDKIKX0DER"
                },
                {
                    "value": "Premium 10mm drivers with deep bass",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "list_price": [
                {
                    "currency": "USD",
                    "value": 49.99,
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "item_weight": [
                {
                    "unit": "pounds",
                    "value": 0.35,
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "item_dimensions": [
                {
                    "length": {
                        "unit": "inches",
                        "value": 4.0
                    },
                    "width": {
                        "unit": "inches",
                        "value": 4.0
                    },
                    "height": {
                        "unit": "inches",
                        "value": 2.5
                    },
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "condition_type": [
                {
                    "value": "NEW",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "product_type": [
                {
                    "value": "HEADPHONES",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ]
        },
        "images": [
            {
                "marketplaceId": "ATVPDKIKX0DER",
                "images": [
                    {
                        "variant": "MAIN",
                        "link": "https://m.media-amazon.com/images/I/example06.jpg",
                        "height": 1000,
                        "width": 1000
                    }
                ]
            }
        ],
        "salesRanks": [
            {
                "marketplaceId": "ATVPDKIKX0DER",
                "classificationRanks": [
                    {
                        "classificationId": "172282",
                        "title": "Electronics",
                        "rank": 5420
                    }
                ]
            }
        ],
        "summaries": [
            {
                "marketplaceId": "ATVPDKIKX0DER",
                "brandName": "VoltEdge Tech",
                "itemName": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                "productType": "HEADPHONES",
                "itemClassification": "BASE_PRODUCT"
            }
        ]
    }
}
```

---

## 11. GET /catalog/2022-04-01/items/B0NONEXIST (Get catalog item - 404)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/catalog/2022-04-01/items/B0NONEXIST"
```

**HTTP Status:** 404

```json
{
    "error": "Item with ASIN B0NONEXIST not found"
}
```

---

## 12. GET /listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-CASE-IP15 (Get listing item)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-CASE-IP15"
```

**HTTP Status:** 200

```json
{
    "type": "listing_item",
    "listing": {
        "sku": "VE-CASE-IP15",
        "asin": "B0EXAMPLE01",
        "sellerId": "A3EXAMPLE1SELLER",
        "productType": "CELLULAR_PHONE_CASE",
        "status": "ACTIVE",
        "fulfillmentChannel": "AFN",
        "createdDate": "2024-08-10T14:30:00Z",
        "lastUpdatedDate": "2026-04-15T09:00:00Z",
        "attributes": {
            "item_name": [
                {
                    "value": "VoltEdge Slim Armor Case for iPhone 15 - Matte Black",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "description": [
                {
                    "value": "Premium slim-fit protective case with military-grade drop protection. Features raised bezels for camera and screen protection. Compatible with wireless charging.",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "brand": [
                {
                    "value": "VoltEdge Tech",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "bullet_point": [
                {
                    "value": "Military-grade drop protection (MIL-STD-810G tested)",
                    "marketplace_id": "ATVPDKIKX0DER"
                },
                {
                    "value": "Slim profile at only 1.2mm thick",
                    "marketplace_id": "ATVPDKIKX0DER"
                },
                {
                    "value": "Raised bezels protect camera and screen",
                    "marketplace_id": "ATVPDKIKX0DER"
                },
                {
                    "value": "Compatible with MagSafe and wireless charging",
                    "marketplace_id": "ATVPDKIKX0DER"
                },
                {
                    "value": "Precision cutouts for all ports and buttons",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "list_price": [
                {
                    "currency": "USD",
                    "value": 19.99,
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "quantity": [
                {
                    "value": 142,
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "fulfillment_channel": [
                {
                    "value": "AFN",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "condition_type": [
                {
                    "value": "NEW",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ],
            "main_image": [
                {
                    "link": "https://m.media-amazon.com/images/I/example01.jpg",
                    "marketplace_id": "ATVPDKIKX0DER"
                }
            ]
        },
        "issues": []
    }
}
```

---

## 13. GET /listings/2021-08-01/items/A3EXAMPLE1SELLER/NONEXIST-SKU (Get listing item - 404)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/listings/2021-08-01/items/A3EXAMPLE1SELLER/NONEXIST-SKU"
```

**HTTP Status:** 404

```json
{
    "error": "Listing with SKU NONEXIST-SKU not found for seller A3EXAMPLE1SELLER"
}
```

---

## 14. PUT /listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-NEW-TESTX (Create new listing)

```bash
curl -s -w '
%{http_code}' -X PUT "http://localhost:8004/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-NEW-TESTX" -H 'Content-Type: application/json' -d '{"productType":"USB_CABLE","title":"Test New Cable 240W","description":"A test cable","brand":"VoltEdge Tech","bulletPoints":["Fast charging","Durable"],"price":19.99,"quantity":50,"fulfillmentChannel":"MFN","condition":"NEW","category":"Electronics"}'
```

**HTTP Status:** 201

```json
{
    "type": "listing_item",
    "status": "ACCEPTED",
    "sku": "VE-NEW-TESTX",
    "issues": []
}
```

---

## 15. PUT /listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-CASE-IP15 (Update existing listing (price+qty))

```bash
curl -s -w '
%{http_code}' -X PUT "http://localhost:8004/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-CASE-IP15" -H 'Content-Type: application/json' -d '{"productType":"CELLULAR_PHONE_CASE","price":17.99,"quantity":200}'
```

**HTTP Status:** 200

```json
{
    "type": "listing_item",
    "status": "ACCEPTED",
    "sku": "VE-CASE-IP15",
    "issues": []
}
```

---

## 16. PATCH /listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-EARBUD-PRO (Patch listing price)

```bash
curl -s -w '
%{http_code}' -X PATCH "http://localhost:8004/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-EARBUD-PRO" -H 'Content-Type: application/json' -d '{"price":44.99,"quantity":60}'
```

**HTTP Status:** 200

```json
{
    "type": "listing_item",
    "status": "ACCEPTED",
    "sku": "VE-EARBUD-PRO",
    "issues": []
}
```

---

## 17. DELETE /listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-NEW-TESTX?marketplaceIds=ATVPDKIKX0DER (Delete listing)

```bash
curl -s -w '
%{http_code}' -X DELETE "http://localhost:8004/listings/2021-08-01/items/A3EXAMPLE1SELLER/VE-NEW-TESTX?marketplaceIds=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "listing_item",
    "status": "ACCEPTED",
    "sku": "VE-NEW-TESTX",
    "deleted": true
}
```

---

## 18. DELETE /listings/2021-08-01/items/A3EXAMPLE1SELLER/NONEXIST-DEL?marketplaceIds=ATVPDKIKX0DER (Delete listing - 404)

```bash
curl -s -w '
%{http_code}' -X DELETE "http://localhost:8004/listings/2021-08-01/items/A3EXAMPLE1SELLER/NONEXIST-DEL?marketplaceIds=ATVPDKIKX0DER"
```

**HTTP Status:** 404

```json
{
    "error": "Listing with SKU NONEXIST-DEL not found for seller A3EXAMPLE1SELLER"
}
```

---

## 19. GET /orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER (List all orders)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "orders",
    "count": 20,
    "total": 20,
    "offset": 0,
    "limit": 100,
    "payload": {
        "Orders": [
            {
                "AmazonOrderId": "114-1789012-5678900",
                "PurchaseDate": "2026-04-30T09:45:00Z",
                "LastUpdateDate": "2026-04-30T09:45:00Z",
                "OrderStatus": "Pending",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-30T10:00:00Z",
                "LatestShipDate": "2026-05-02T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Andrew Davis",
                    "AddressLine1": "927 Linden St",
                    "City": "Detroit",
                    "StateOrRegion": "MI",
                    "PostalCode": "48201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer20@email.com",
                    "BuyerName": "Andrew Davis"
                }
            },
            {
                "AmazonOrderId": "114-1678901-4567800",
                "PurchaseDate": "2026-04-28T14:15:00Z",
                "LastUpdateDate": "2026-04-28T14:15:00Z",
                "OrderStatus": "Unshipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "79.98"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 2,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-28T15:00:00Z",
                "LatestShipDate": "2026-04-29T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Samantha Clark",
                    "AddressLine1": "601 Birch Park Ln",
                    "City": "Tampa",
                    "StateOrRegion": "FL",
                    "PostalCode": "33601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer19@email.com",
                    "BuyerName": "Samantha Clark"
                }
            },
            {
                "AmazonOrderId": "114-1567890-3456700",
                "PurchaseDate": "2026-04-25T08:00:00Z",
                "LastUpdateDate": "2026-04-28T12:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "24.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-25T09:00:00Z",
                "LatestShipDate": "2026-04-27T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Tyler Scott",
                    "AddressLine1": "482 Chestnut Ave",
                    "City": "Nashville",
                    "StateOrRegion": "TN",
                    "PostalCode": "37201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer18@email.com",
                    "BuyerName": "Tyler Scott"
                }
            },
            {
                "AmazonOrderId": "114-1456789-2345600",
                "PurchaseDate": "2026-04-22T10:30:00Z",
                "LastUpdateDate": "2026-04-22T10:30:00Z",
                "OrderStatus": "Pending",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "16.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-22T12:00:00Z",
                "LatestShipDate": "2026-04-24T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Nicole Harris",
                    "AddressLine1": "159 Juniper Dr",
                    "City": "Raleigh",
                    "StateOrRegion": "NC",
                    "PostalCode": "27601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer17@email.com",
                    "BuyerName": "Nicole Harris"
                }
            },
            {
                "AmazonOrderId": "114-1345678-1234500",
                "PurchaseDate": "2026-04-20T16:00:00Z",
                "LastUpdateDate": "2026-04-23T10:00:00Z",
                "OrderStatus": "Unshipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "18.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-20T18:00:00Z",
                "LatestShipDate": "2026-04-22T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Brian Jackson",
                    "AddressLine1": "753 Aspen Way",
                    "City": "Dallas",
                    "StateOrRegion": "TX",
                    "PostalCode": "75201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer16@email.com",
                    "BuyerName": "Brian Jackson"
                }
            },
            {
                "AmazonOrderId": "114-1234567-0123400",
                "PurchaseDate": "2026-04-15T09:00:00Z",
                "LastUpdateDate": "2026-04-18T14:30:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "57.98"
                },
                "NumberOfItemsShipped": 2,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-15T10:00:00Z",
                "LatestShipDate": "2026-04-17T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Ashley Williams",
                    "AddressLine1": "864 Hickory Blvd",
                    "City": "Minneapolis",
                    "StateOrRegion": "MN",
                    "PostalCode": "55401",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer15@email.com",
                    "BuyerName": "Ashley Williams"
                }
            },
            {
                "AmazonOrderId": "114-1123456-9012300",
                "PurchaseDate": "2026-04-10T11:30:00Z",
                "LastUpdateDate": "2026-04-13T09:45:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "27.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-10T12:00:00Z",
                "LatestShipDate": "2026-04-12T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Kevin Nguyen",
                    "AddressLine1": "135 Walnut St",
                    "City": "San Diego",
                    "StateOrRegion": "CA",
                    "PostalCode": "92101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer14@email.com",
                    "BuyerName": "Kevin Nguyen"
                }
            },
            {
                "AmazonOrderId": "114-1012345-8901200",
                "PurchaseDate": "2026-04-05T14:00:00Z",
                "LastUpdateDate": "2026-04-08T10:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "49.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-05T15:00:00Z",
                "LatestShipDate": "2026-04-06T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Rachel Brown",
                    "AddressLine1": "246 Sycamore Ct",
                    "City": "Philadelphia",
                    "StateOrRegion": "PA",
                    "PostalCode": "19101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer13@email.com",
                    "BuyerName": "Rachel Brown"
                }
            },
            {
                "AmazonOrderId": "114-9901234-7890100",
                "PurchaseDate": "2026-04-01T08:45:00Z",
                "LastUpdateDate": "2026-04-04T15:20:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "32.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-01T10:00:00Z",
                "LatestShipDate": "2026-04-03T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Daniel Martinez",
                    "AddressLine1": "987 Poplar Lane",
                    "City": "Houston",
                    "StateOrRegion": "TX",
                    "PostalCode": "77001",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer12@email.com",
                    "BuyerName": "Daniel Martinez"
                }
            },
            {
                "AmazonOrderId": "114-8890123-6789000",
                "PurchaseDate": "2026-03-28T10:15:00Z",
                "LastUpdateDate": "2026-03-31T09:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "12.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-28T12:00:00Z",
                "LatestShipDate": "2026-03-30T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Megan Taylor",
                    "AddressLine1": "654 Magnolia Dr",
                    "City": "Phoenix",
                    "StateOrRegion": "AZ",
                    "PostalCode": "85001",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer11@email.com",
                    "BuyerName": "Megan Taylor"
                }
            },
            {
                "AmazonOrderId": "114-7789012-5678900",
                "PurchaseDate": "2026-03-22T13:00:00Z",
                "LastUpdateDate": "2026-03-26T11:30:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-22T14:00:00Z",
                "LatestShipDate": "2026-03-24T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Christopher Lee",
                    "AddressLine1": "321 Redwood Ave",
                    "City": "Atlanta",
                    "StateOrRegion": "GA",
                    "PostalCode": "30301",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer10@email.com",
                    "BuyerName": "Christopher Lee"
                }
            },
            {
                "AmazonOrderId": "114-6678901-4567800",
                "PurchaseDate": "2026-03-18T09:30:00Z",
                "LastUpdateDate": "2026-03-22T14:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "22.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-18T10:00:00Z",
                "LatestShipDate": "2026-03-20T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Jennifer Adams",
                    "AddressLine1": "789 Ash Street",
                    "City": "Boston",
                    "StateOrRegion": "MA",
                    "PostalCode": "02101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer9@email.com",
                    "BuyerName": "Jennifer Adams"
                }
            },
            {
                "AmazonOrderId": "114-5567890-3456700",
                "PurchaseDate": "2026-03-12T16:45:00Z",
                "LastUpdateDate": "2026-03-15T10:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "94.98"
                },
                "NumberOfItemsShipped": 2,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-12T18:00:00Z",
                "LatestShipDate": "2026-03-13T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Robert Wilson",
                    "AddressLine1": "4567 Spruce St Apt 12",
                    "City": "New York",
                    "StateOrRegion": "NY",
                    "PostalCode": "10001",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer8@email.com",
                    "BuyerName": "Robert Wilson"
                }
            },
            {
                "AmazonOrderId": "114-4456789-2345600",
                "PurchaseDate": "2026-03-08T11:20:00Z",
                "LastUpdateDate": "2026-03-08T11:20:00Z",
                "OrderStatus": "Canceled",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "39.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-08T12:00:00Z",
                "LatestShipDate": "2026-03-10T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Amanda Foster",
                    "AddressLine1": "1234 Cedar Blvd",
                    "City": "Miami",
                    "StateOrRegion": "FL",
                    "PostalCode": "33101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer7@email.com",
                    "BuyerName": "Amanda Foster"
                }
            },
            {
                "AmazonOrderId": "114-3345678-1234500",
                "PurchaseDate": "2026-03-02T14:30:00Z",
                "LastUpdateDate": "2026-03-05T09:15:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "29.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-02T16:00:00Z",
                "LatestShipDate": "2026-03-04T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": true,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "David Kim",
                    "AddressLine1": "567 Willow Way",
                    "City": "Chicago",
                    "StateOrRegion": "IL",
                    "PostalCode": "60601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer6@email.com",
                    "BuyerName": "David Kim"
                }
            },
            {
                "AmazonOrderId": "114-2234567-8901200",
                "PurchaseDate": "2026-02-25T09:00:00Z",
                "LastUpdateDate": "2026-03-01T10:30:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-25T10:00:00Z",
                "LatestShipDate": "2026-02-27T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Lisa Park",
                    "AddressLine1": "2104 Birch Lane",
                    "City": "Denver",
                    "StateOrRegion": "CO",
                    "PostalCode": "80202",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer5@email.com",
                    "BuyerName": "Lisa Park"
                }
            },
            {
                "AmazonOrderId": "114-9981234-5567800",
                "PurchaseDate": "2026-02-18T12:15:00Z",
                "LastUpdateDate": "2026-02-22T16:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "34.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-18T14:00:00Z",
                "LatestShipDate": "2026-02-20T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Michael Thompson",
                    "AddressLine1": "892 Pine Court",
                    "City": "Seattle",
                    "StateOrRegion": "WA",
                    "PostalCode": "98101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer4@email.com",
                    "BuyerName": "Michael Thompson"
                }
            },
            {
                "AmazonOrderId": "114-7723891-3345600",
                "PurchaseDate": "2026-02-12T08:30:00Z",
                "LastUpdateDate": "2026-02-14T11:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "62.98"
                },
                "NumberOfItemsShipped": 2,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-12T10:00:00Z",
                "LatestShipDate": "2026-02-14T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Emily Rodriguez",
                    "AddressLine1": "3847 Maple Drive",
                    "City": "Austin",
                    "StateOrRegion": "TX",
                    "PostalCode": "78701",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer3@email.com",
                    "BuyerName": "Emily Rodriguez"
                }
            },
            {
                "AmazonOrderId": "114-5578234-9921100",
                "PurchaseDate": "2026-02-08T15:45:00Z",
                "LastUpdateDate": "2026-02-12T09:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "49.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-08T16:00:00Z",
                "LatestShipDate": "2026-02-09T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "James Chen",
                    "AddressLine1": "1520 Oak Avenue Apt 4B",
                    "City": "San Francisco",
                    "StateOrRegion": "CA",
                    "PostalCode": "94102",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer2@email.com",
                    "BuyerName": "James Chen"
                }
            },
            {
                "AmazonOrderId": "114-3941689-8772200",
                "PurchaseDate": "2026-02-05T10:22:00Z",
                "LastUpdateDate": "2026-02-08T14:30:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "19.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-05T12:00:00Z",
                "LatestShipDate": "2026-02-07T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Sarah Mitchell",
                    "AddressLine1": "742 Elm Street",
                    "City": "Portland",
                    "StateOrRegion": "OR",
                    "PostalCode": "97201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer1@email.com",
                    "BuyerName": "Sarah Mitchell"
                }
            }
        ]
    }
}
```

---

## 20. GET /orders/v0/orders?OrderStatuses=Unshipped&MarketplaceIds=ATVPDKIKX0DER (List orders - filter Unshipped)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders?OrderStatuses=Unshipped&MarketplaceIds=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "orders",
    "count": 2,
    "total": 2,
    "offset": 0,
    "limit": 100,
    "payload": {
        "Orders": [
            {
                "AmazonOrderId": "114-1678901-4567800",
                "PurchaseDate": "2026-04-28T14:15:00Z",
                "LastUpdateDate": "2026-04-28T14:15:00Z",
                "OrderStatus": "Unshipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "79.98"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 2,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-28T15:00:00Z",
                "LatestShipDate": "2026-04-29T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Samantha Clark",
                    "AddressLine1": "601 Birch Park Ln",
                    "City": "Tampa",
                    "StateOrRegion": "FL",
                    "PostalCode": "33601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer19@email.com",
                    "BuyerName": "Samantha Clark"
                }
            },
            {
                "AmazonOrderId": "114-1345678-1234500",
                "PurchaseDate": "2026-04-20T16:00:00Z",
                "LastUpdateDate": "2026-04-23T10:00:00Z",
                "OrderStatus": "Unshipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "18.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-20T18:00:00Z",
                "LatestShipDate": "2026-04-22T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Brian Jackson",
                    "AddressLine1": "753 Aspen Way",
                    "City": "Dallas",
                    "StateOrRegion": "TX",
                    "PostalCode": "75201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer16@email.com",
                    "BuyerName": "Brian Jackson"
                }
            }
        ]
    }
}
```

---

## 21. GET /orders/v0/orders?OrderStatuses=Pending&MarketplaceIds=ATVPDKIKX0DER (List orders - filter Pending)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders?OrderStatuses=Pending&MarketplaceIds=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "orders",
    "count": 2,
    "total": 2,
    "offset": 0,
    "limit": 100,
    "payload": {
        "Orders": [
            {
                "AmazonOrderId": "114-1789012-5678900",
                "PurchaseDate": "2026-04-30T09:45:00Z",
                "LastUpdateDate": "2026-04-30T09:45:00Z",
                "OrderStatus": "Pending",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-30T10:00:00Z",
                "LatestShipDate": "2026-05-02T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Andrew Davis",
                    "AddressLine1": "927 Linden St",
                    "City": "Detroit",
                    "StateOrRegion": "MI",
                    "PostalCode": "48201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer20@email.com",
                    "BuyerName": "Andrew Davis"
                }
            },
            {
                "AmazonOrderId": "114-1456789-2345600",
                "PurchaseDate": "2026-04-22T10:30:00Z",
                "LastUpdateDate": "2026-04-22T10:30:00Z",
                "OrderStatus": "Pending",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "16.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-22T12:00:00Z",
                "LatestShipDate": "2026-04-24T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Nicole Harris",
                    "AddressLine1": "159 Juniper Dr",
                    "City": "Raleigh",
                    "StateOrRegion": "NC",
                    "PostalCode": "27601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer17@email.com",
                    "BuyerName": "Nicole Harris"
                }
            }
        ]
    }
}
```

---

## 22. GET /orders/v0/orders?FulfillmentChannels=AFN&MarketplaceIds=ATVPDKIKX0DER (List orders - filter AFN)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders?FulfillmentChannels=AFN&MarketplaceIds=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "orders",
    "count": 15,
    "total": 15,
    "offset": 0,
    "limit": 100,
    "payload": {
        "Orders": [
            {
                "AmazonOrderId": "114-1789012-5678900",
                "PurchaseDate": "2026-04-30T09:45:00Z",
                "LastUpdateDate": "2026-04-30T09:45:00Z",
                "OrderStatus": "Pending",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-30T10:00:00Z",
                "LatestShipDate": "2026-05-02T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Andrew Davis",
                    "AddressLine1": "927 Linden St",
                    "City": "Detroit",
                    "StateOrRegion": "MI",
                    "PostalCode": "48201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer20@email.com",
                    "BuyerName": "Andrew Davis"
                }
            },
            {
                "AmazonOrderId": "114-1678901-4567800",
                "PurchaseDate": "2026-04-28T14:15:00Z",
                "LastUpdateDate": "2026-04-28T14:15:00Z",
                "OrderStatus": "Unshipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "79.98"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 2,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-28T15:00:00Z",
                "LatestShipDate": "2026-04-29T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Samantha Clark",
                    "AddressLine1": "601 Birch Park Ln",
                    "City": "Tampa",
                    "StateOrRegion": "FL",
                    "PostalCode": "33601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer19@email.com",
                    "BuyerName": "Samantha Clark"
                }
            },
            {
                "AmazonOrderId": "114-1567890-3456700",
                "PurchaseDate": "2026-04-25T08:00:00Z",
                "LastUpdateDate": "2026-04-28T12:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "24.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-25T09:00:00Z",
                "LatestShipDate": "2026-04-27T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Tyler Scott",
                    "AddressLine1": "482 Chestnut Ave",
                    "City": "Nashville",
                    "StateOrRegion": "TN",
                    "PostalCode": "37201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer18@email.com",
                    "BuyerName": "Tyler Scott"
                }
            },
            {
                "AmazonOrderId": "114-1456789-2345600",
                "PurchaseDate": "2026-04-22T10:30:00Z",
                "LastUpdateDate": "2026-04-22T10:30:00Z",
                "OrderStatus": "Pending",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "16.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-22T12:00:00Z",
                "LatestShipDate": "2026-04-24T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Nicole Harris",
                    "AddressLine1": "159 Juniper Dr",
                    "City": "Raleigh",
                    "StateOrRegion": "NC",
                    "PostalCode": "27601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer17@email.com",
                    "BuyerName": "Nicole Harris"
                }
            },
            {
                "AmazonOrderId": "114-1234567-0123400",
                "PurchaseDate": "2026-04-15T09:00:00Z",
                "LastUpdateDate": "2026-04-18T14:30:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "57.98"
                },
                "NumberOfItemsShipped": 2,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-15T10:00:00Z",
                "LatestShipDate": "2026-04-17T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Ashley Williams",
                    "AddressLine1": "864 Hickory Blvd",
                    "City": "Minneapolis",
                    "StateOrRegion": "MN",
                    "PostalCode": "55401",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer15@email.com",
                    "BuyerName": "Ashley Williams"
                }
            },
            {
                "AmazonOrderId": "114-1012345-8901200",
                "PurchaseDate": "2026-04-05T14:00:00Z",
                "LastUpdateDate": "2026-04-08T10:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "49.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-05T15:00:00Z",
                "LatestShipDate": "2026-04-06T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Rachel Brown",
                    "AddressLine1": "246 Sycamore Ct",
                    "City": "Philadelphia",
                    "StateOrRegion": "PA",
                    "PostalCode": "19101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer13@email.com",
                    "BuyerName": "Rachel Brown"
                }
            },
            {
                "AmazonOrderId": "114-9901234-7890100",
                "PurchaseDate": "2026-04-01T08:45:00Z",
                "LastUpdateDate": "2026-04-04T15:20:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "32.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-01T10:00:00Z",
                "LatestShipDate": "2026-04-03T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Daniel Martinez",
                    "AddressLine1": "987 Poplar Lane",
                    "City": "Houston",
                    "StateOrRegion": "TX",
                    "PostalCode": "77001",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer12@email.com",
                    "BuyerName": "Daniel Martinez"
                }
            },
            {
                "AmazonOrderId": "114-8890123-6789000",
                "PurchaseDate": "2026-03-28T10:15:00Z",
                "LastUpdateDate": "2026-03-31T09:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "12.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-28T12:00:00Z",
                "LatestShipDate": "2026-03-30T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Megan Taylor",
                    "AddressLine1": "654 Magnolia Dr",
                    "City": "Phoenix",
                    "StateOrRegion": "AZ",
                    "PostalCode": "85001",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer11@email.com",
                    "BuyerName": "Megan Taylor"
                }
            },
            {
                "AmazonOrderId": "114-6678901-4567800",
                "PurchaseDate": "2026-03-18T09:30:00Z",
                "LastUpdateDate": "2026-03-22T14:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "22.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-18T10:00:00Z",
                "LatestShipDate": "2026-03-20T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Jennifer Adams",
                    "AddressLine1": "789 Ash Street",
                    "City": "Boston",
                    "StateOrRegion": "MA",
                    "PostalCode": "02101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer9@email.com",
                    "BuyerName": "Jennifer Adams"
                }
            },
            {
                "AmazonOrderId": "114-5567890-3456700",
                "PurchaseDate": "2026-03-12T16:45:00Z",
                "LastUpdateDate": "2026-03-15T10:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "94.98"
                },
                "NumberOfItemsShipped": 2,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-12T18:00:00Z",
                "LatestShipDate": "2026-03-13T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Robert Wilson",
                    "AddressLine1": "4567 Spruce St Apt 12",
                    "City": "New York",
                    "StateOrRegion": "NY",
                    "PostalCode": "10001",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer8@email.com",
                    "BuyerName": "Robert Wilson"
                }
            },
            {
                "AmazonOrderId": "114-4456789-2345600",
                "PurchaseDate": "2026-03-08T11:20:00Z",
                "LastUpdateDate": "2026-03-08T11:20:00Z",
                "OrderStatus": "Canceled",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "39.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-08T12:00:00Z",
                "LatestShipDate": "2026-03-10T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Amanda Foster",
                    "AddressLine1": "1234 Cedar Blvd",
                    "City": "Miami",
                    "StateOrRegion": "FL",
                    "PostalCode": "33101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer7@email.com",
                    "BuyerName": "Amanda Foster"
                }
            },
            {
                "AmazonOrderId": "114-2234567-8901200",
                "PurchaseDate": "2026-02-25T09:00:00Z",
                "LastUpdateDate": "2026-03-01T10:30:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-25T10:00:00Z",
                "LatestShipDate": "2026-02-27T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Lisa Park",
                    "AddressLine1": "2104 Birch Lane",
                    "City": "Denver",
                    "StateOrRegion": "CO",
                    "PostalCode": "80202",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer5@email.com",
                    "BuyerName": "Lisa Park"
                }
            },
            {
                "AmazonOrderId": "114-9981234-5567800",
                "PurchaseDate": "2026-02-18T12:15:00Z",
                "LastUpdateDate": "2026-02-22T16:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "34.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-18T14:00:00Z",
                "LatestShipDate": "2026-02-20T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Michael Thompson",
                    "AddressLine1": "892 Pine Court",
                    "City": "Seattle",
                    "StateOrRegion": "WA",
                    "PostalCode": "98101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer4@email.com",
                    "BuyerName": "Michael Thompson"
                }
            },
            {
                "AmazonOrderId": "114-5578234-9921100",
                "PurchaseDate": "2026-02-08T15:45:00Z",
                "LastUpdateDate": "2026-02-12T09:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "49.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-08T16:00:00Z",
                "LatestShipDate": "2026-02-09T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "James Chen",
                    "AddressLine1": "1520 Oak Avenue Apt 4B",
                    "City": "San Francisco",
                    "StateOrRegion": "CA",
                    "PostalCode": "94102",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer2@email.com",
                    "BuyerName": "James Chen"
                }
            },
            {
                "AmazonOrderId": "114-3941689-8772200",
                "PurchaseDate": "2026-02-05T10:22:00Z",
                "LastUpdateDate": "2026-02-08T14:30:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "19.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-02-05T12:00:00Z",
                "LatestShipDate": "2026-02-07T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Sarah Mitchell",
                    "AddressLine1": "742 Elm Street",
                    "City": "Portland",
                    "StateOrRegion": "OR",
                    "PostalCode": "97201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer1@email.com",
                    "BuyerName": "Sarah Mitchell"
                }
            }
        ]
    }
}
```

---

## 23. GET /orders/v0/orders?CreatedAfter=2026-03-01T00:00:00Z&CreatedBefore=2026-04-01T00:00:00Z (List orders - date range)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders?CreatedAfter=2026-03-01T00:00:00Z&CreatedBefore=2026-04-01T00:00:00Z"
```

**HTTP Status:** 200

```json
{
    "type": "orders",
    "count": 6,
    "total": 6,
    "offset": 0,
    "limit": 100,
    "payload": {
        "Orders": [
            {
                "AmazonOrderId": "114-8890123-6789000",
                "PurchaseDate": "2026-03-28T10:15:00Z",
                "LastUpdateDate": "2026-03-31T09:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "12.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-28T12:00:00Z",
                "LatestShipDate": "2026-03-30T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Megan Taylor",
                    "AddressLine1": "654 Magnolia Dr",
                    "City": "Phoenix",
                    "StateOrRegion": "AZ",
                    "PostalCode": "85001",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer11@email.com",
                    "BuyerName": "Megan Taylor"
                }
            },
            {
                "AmazonOrderId": "114-7789012-5678900",
                "PurchaseDate": "2026-03-22T13:00:00Z",
                "LastUpdateDate": "2026-03-26T11:30:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-22T14:00:00Z",
                "LatestShipDate": "2026-03-24T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Christopher Lee",
                    "AddressLine1": "321 Redwood Ave",
                    "City": "Atlanta",
                    "StateOrRegion": "GA",
                    "PostalCode": "30301",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer10@email.com",
                    "BuyerName": "Christopher Lee"
                }
            },
            {
                "AmazonOrderId": "114-6678901-4567800",
                "PurchaseDate": "2026-03-18T09:30:00Z",
                "LastUpdateDate": "2026-03-22T14:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "22.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-18T10:00:00Z",
                "LatestShipDate": "2026-03-20T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Jennifer Adams",
                    "AddressLine1": "789 Ash Street",
                    "City": "Boston",
                    "StateOrRegion": "MA",
                    "PostalCode": "02101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer9@email.com",
                    "BuyerName": "Jennifer Adams"
                }
            },
            {
                "AmazonOrderId": "114-5567890-3456700",
                "PurchaseDate": "2026-03-12T16:45:00Z",
                "LastUpdateDate": "2026-03-15T10:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "94.98"
                },
                "NumberOfItemsShipped": 2,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-12T18:00:00Z",
                "LatestShipDate": "2026-03-13T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Robert Wilson",
                    "AddressLine1": "4567 Spruce St Apt 12",
                    "City": "New York",
                    "StateOrRegion": "NY",
                    "PostalCode": "10001",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer8@email.com",
                    "BuyerName": "Robert Wilson"
                }
            },
            {
                "AmazonOrderId": "114-4456789-2345600",
                "PurchaseDate": "2026-03-08T11:20:00Z",
                "LastUpdateDate": "2026-03-08T11:20:00Z",
                "OrderStatus": "Canceled",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "39.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-08T12:00:00Z",
                "LatestShipDate": "2026-03-10T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Amanda Foster",
                    "AddressLine1": "1234 Cedar Blvd",
                    "City": "Miami",
                    "StateOrRegion": "FL",
                    "PostalCode": "33101",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer7@email.com",
                    "BuyerName": "Amanda Foster"
                }
            },
            {
                "AmazonOrderId": "114-3345678-1234500",
                "PurchaseDate": "2026-03-02T14:30:00Z",
                "LastUpdateDate": "2026-03-05T09:15:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "29.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-03-02T16:00:00Z",
                "LatestShipDate": "2026-03-04T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": true,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "David Kim",
                    "AddressLine1": "567 Willow Way",
                    "City": "Chicago",
                    "StateOrRegion": "IL",
                    "PostalCode": "60601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer6@email.com",
                    "BuyerName": "David Kim"
                }
            }
        ]
    }
}
```

---

## 24. GET /orders/v0/orders?MaxResultsPerPage=5 (List orders - paginated)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders?MaxResultsPerPage=5"
```

**HTTP Status:** 200

```json
{
    "type": "orders",
    "count": 5,
    "total": 20,
    "offset": 0,
    "limit": 5,
    "payload": {
        "Orders": [
            {
                "AmazonOrderId": "114-1789012-5678900",
                "PurchaseDate": "2026-04-30T09:45:00Z",
                "LastUpdateDate": "2026-04-30T09:45:00Z",
                "OrderStatus": "Pending",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-30T10:00:00Z",
                "LatestShipDate": "2026-05-02T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Andrew Davis",
                    "AddressLine1": "927 Linden St",
                    "City": "Detroit",
                    "StateOrRegion": "MI",
                    "PostalCode": "48201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer20@email.com",
                    "BuyerName": "Andrew Davis"
                }
            },
            {
                "AmazonOrderId": "114-1678901-4567800",
                "PurchaseDate": "2026-04-28T14:15:00Z",
                "LastUpdateDate": "2026-04-28T14:15:00Z",
                "OrderStatus": "Unshipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Expedited",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "79.98"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 2,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Expedited",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-28T15:00:00Z",
                "LatestShipDate": "2026-04-29T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Samantha Clark",
                    "AddressLine1": "601 Birch Park Ln",
                    "City": "Tampa",
                    "StateOrRegion": "FL",
                    "PostalCode": "33601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer19@email.com",
                    "BuyerName": "Samantha Clark"
                }
            },
            {
                "AmazonOrderId": "114-1567890-3456700",
                "PurchaseDate": "2026-04-25T08:00:00Z",
                "LastUpdateDate": "2026-04-28T12:00:00Z",
                "OrderStatus": "Shipped",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "24.99"
                },
                "NumberOfItemsShipped": 1,
                "NumberOfItemsUnshipped": 0,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-25T09:00:00Z",
                "LatestShipDate": "2026-04-27T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Tyler Scott",
                    "AddressLine1": "482 Chestnut Ave",
                    "City": "Nashville",
                    "StateOrRegion": "TN",
                    "PostalCode": "37201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer18@email.com",
                    "BuyerName": "Tyler Scott"
                }
            },
            {
                "AmazonOrderId": "114-1456789-2345600",
                "PurchaseDate": "2026-04-22T10:30:00Z",
                "LastUpdateDate": "2026-04-22T10:30:00Z",
                "OrderStatus": "Pending",
                "FulfillmentChannel": "AFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "16.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-22T12:00:00Z",
                "LatestShipDate": "2026-04-24T23:59:59Z",
                "IsPrime": true,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Nicole Harris",
                    "AddressLine1": "159 Juniper Dr",
                    "City": "Raleigh",
                    "StateOrRegion": "NC",
                    "PostalCode": "27601",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer17@email.com",
                    "BuyerName": "Nicole Harris"
                }
            },
            {
                "AmazonOrderId": "114-1345678-1234500",
                "PurchaseDate": "2026-04-20T16:00:00Z",
                "LastUpdateDate": "2026-04-23T10:00:00Z",
                "OrderStatus": "Unshipped",
                "FulfillmentChannel": "MFN",
                "SalesChannel": "Amazon.com",
                "ShipServiceLevel": "Standard",
                "OrderTotal": {
                    "CurrencyCode": "USD",
                    "Amount": "18.99"
                },
                "NumberOfItemsShipped": 0,
                "NumberOfItemsUnshipped": 1,
                "PaymentMethod": "Other",
                "MarketplaceId": "ATVPDKIKX0DER",
                "ShipmentServiceLevelCategory": "Standard",
                "OrderType": "StandardOrder",
                "EarliestShipDate": "2026-04-20T18:00:00Z",
                "LatestShipDate": "2026-04-22T23:59:59Z",
                "IsPrime": false,
                "IsBusinessOrder": false,
                "IsSoldByAB": false,
                "ShippingAddress": {
                    "Name": "Brian Jackson",
                    "AddressLine1": "753 Aspen Way",
                    "City": "Dallas",
                    "StateOrRegion": "TX",
                    "PostalCode": "75201",
                    "CountryCode": "US"
                },
                "BuyerInfo": {
                    "BuyerEmail": "buyer16@email.com",
                    "BuyerName": "Brian Jackson"
                }
            }
        ]
    }
}
```

---

## 25. GET /orders/v0/orders/114-5578234-9921100 (Get order by ID)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders/114-5578234-9921100"
```

**HTTP Status:** 200

```json
{
    "type": "order",
    "payload": {
        "AmazonOrderId": "114-5578234-9921100",
        "PurchaseDate": "2026-02-08T15:45:00Z",
        "LastUpdateDate": "2026-02-12T09:00:00Z",
        "OrderStatus": "Shipped",
        "FulfillmentChannel": "AFN",
        "SalesChannel": "Amazon.com",
        "ShipServiceLevel": "Expedited",
        "OrderTotal": {
            "CurrencyCode": "USD",
            "Amount": "49.99"
        },
        "NumberOfItemsShipped": 1,
        "NumberOfItemsUnshipped": 0,
        "PaymentMethod": "Other",
        "MarketplaceId": "ATVPDKIKX0DER",
        "ShipmentServiceLevelCategory": "Expedited",
        "OrderType": "StandardOrder",
        "EarliestShipDate": "2026-02-08T16:00:00Z",
        "LatestShipDate": "2026-02-09T23:59:59Z",
        "IsPrime": true,
        "IsBusinessOrder": false,
        "IsSoldByAB": false,
        "ShippingAddress": {
            "Name": "James Chen",
            "AddressLine1": "1520 Oak Avenue Apt 4B",
            "City": "San Francisco",
            "StateOrRegion": "CA",
            "PostalCode": "94102",
            "CountryCode": "US"
        },
        "BuyerInfo": {
            "BuyerEmail": "buyer2@email.com",
            "BuyerName": "James Chen"
        }
    }
}
```

---

## 26. GET /orders/v0/orders/999-0000000-0000000 (Get order - 404)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders/999-0000000-0000000"
```

**HTTP Status:** 404

```json
{
    "error": "Order 999-0000000-0000000 not found"
}
```

---

## 27. GET /orders/v0/orders/114-5567890-3456700/orderItems (Get order items (multi-item))

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders/114-5567890-3456700/orderItems"
```

**HTTP Status:** 200

```json
{
    "type": "order_items",
    "payload": {
        "AmazonOrderId": "114-5567890-3456700",
        "OrderItems": [
            {
                "OrderItemId": "OI-009",
                "ASIN": "B0EXAMPLE06",
                "SellerSKU": "VE-EARBUD-PRO",
                "Title": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                "QuantityOrdered": 1,
                "QuantityShipped": 1,
                "ItemPrice": {
                    "CurrencyCode": "USD",
                    "Amount": "49.99"
                },
                "ItemTax": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "PromotionDiscount": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "IsGift": true,
                "ConditionId": "New"
            },
            {
                "OrderItemId": "OI-010",
                "ASIN": "B0EXAMPLE12",
                "SellerSKU": "VE-PWR-20K",
                "Title": "VoltEdge PowerVault Pro 20000mAh with 65W USB-C",
                "QuantityOrdered": 1,
                "QuantityShipped": 1,
                "ItemPrice": {
                    "CurrencyCode": "USD",
                    "Amount": "44.99"
                },
                "ItemTax": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "PromotionDiscount": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "IsGift": false,
                "ConditionId": "New"
            }
        ]
    }
}
```

---

## 28. GET /orders/v0/orders/114-1234567-0123400/orderItems (Get order items (3 items))

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/orders/v0/orders/114-1234567-0123400/orderItems"
```

**HTTP Status:** 200

```json
{
    "type": "order_items",
    "payload": {
        "AmazonOrderId": "114-1234567-0123400",
        "OrderItems": [
            {
                "OrderItemId": "OI-017",
                "ASIN": "B0EXAMPLE01",
                "SellerSKU": "VE-CASE-IP15",
                "Title": "VoltEdge Slim Armor Case for iPhone 15 - Matte Black",
                "QuantityOrdered": 1,
                "QuantityShipped": 1,
                "ItemPrice": {
                    "CurrencyCode": "USD",
                    "Amount": "19.99"
                },
                "ItemTax": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "PromotionDiscount": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "IsGift": false,
                "ConditionId": "New"
            },
            {
                "OrderItemId": "OI-018",
                "ASIN": "B0EXAMPLE03",
                "SellerSKU": "VE-SCRN-IP15",
                "Title": "VoltEdge Tempered Glass Screen Protector for iPhone 15 (3-Pack)",
                "QuantityOrdered": 1,
                "QuantityShipped": 1,
                "ItemPrice": {
                    "CurrencyCode": "USD",
                    "Amount": "12.99"
                },
                "ItemTax": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "PromotionDiscount": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "IsGift": false,
                "ConditionId": "New"
            },
            {
                "OrderItemId": "OI-019",
                "ASIN": "B0EXAMPLE11",
                "SellerSKU": "VE-PWR-10K",
                "Title": "VoltEdge PowerVault 10000mAh Portable Charger - USB-C PD 20W",
                "QuantityOrdered": 1,
                "QuantityShipped": 1,
                "ItemPrice": {
                    "CurrencyCode": "USD",
                    "Amount": "24.99"
                },
                "ItemTax": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "PromotionDiscount": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "IsGift": false,
                "ConditionId": "New"
            }
        ]
    }
}
```

---

## 29. POST /orders/v0/orders/114-1678901-4567800/shipmentConfirmation (Confirm shipment - Unshipped)

```bash
curl -s -w '
%{http_code}' -X POST "http://localhost:8004/orders/v0/orders/114-1678901-4567800/shipmentConfirmation" -H 'Content-Type: application/json' -d '{"carrierCode":"UPS","trackingNumber":"1Z999AA10123456784","shipDate":"2026-04-29T10:00:00Z"}'
```

**HTTP Status:** 200

```json
{
    "type": "shipment_confirmation",
    "status": "SUCCESS",
    "orderId": "114-1678901-4567800"
}
```

---

## 30. POST /orders/v0/orders/114-3941689-8772200/shipmentConfirmation (Confirm shipment - already shipped (error))

```bash
curl -s -w '
%{http_code}' -X POST "http://localhost:8004/orders/v0/orders/114-3941689-8772200/shipmentConfirmation" -H 'Content-Type: application/json' -d '{"carrierCode":"USPS","trackingNumber":"9400111899223100456789"}'
```

**HTTP Status:** 400

```json
{
    "error": "Order 114-3941689-8772200 cannot be shipped (status: Shipped)"
}
```

---

## 31. GET /fba/inventory/v1/summaries?granularityType=Marketplace&granularityId=ATVPDKIKX0DER (List all inventory)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/fba/inventory/v1/summaries?granularityType=Marketplace&granularityId=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "inventory_summaries",
    "payload": {
        "granularity": {
            "granularityType": "Marketplace",
            "granularityId": "ATVPDKIKX0DER"
        },
        "inventorySummaries": [
            {
                "asin": "B0EXAMPLE01",
                "fnSku": "X001EXAMPLE1",
                "sellerSku": "VE-CASE-IP15",
                "productName": "VoltEdge Slim Armor Case for iPhone 15 - Matte Black",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 130,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 142,
                    "reservedQuantity": 8,
                    "unfulfillableQuantity": 4
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE02",
                "fnSku": "X001EXAMPLE2",
                "sellerSku": "VE-CASE-IP15P",
                "productName": "VoltEdge Slim Armor Case for iPhone 15 Pro - Navy Blue",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 82,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 89,
                    "reservedQuantity": 5,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE03",
                "fnSku": "X001EXAMPLE3",
                "sellerSku": "VE-SCRN-IP15",
                "productName": "VoltEdge Tempered Glass Screen Protector for iPhone 15 (3-Pack)",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 220,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 234,
                    "reservedQuantity": 12,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE04",
                "fnSku": "X001EXAMPLE4",
                "sellerSku": "VE-CHRG-USB3",
                "productName": "VoltEdge 6ft USB-C to USB-C Fast Charging Cable (2-Pack)",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 14,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 50,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 18,
                    "reservedQuantity": 3,
                    "unfulfillableQuantity": 1
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE05",
                "fnSku": "X001EXAMPLE5",
                "sellerSku": "VE-CHRG-LTN",
                "productName": "VoltEdge 3ft MFi Certified Lightning Cable - White",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 67,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 67,
                    "reservedQuantity": 0,
                    "unfulfillableQuantity": 0
                },
                "lastUpdatedTime": "2026-04-27T14:00:00Z"
            },
            {
                "asin": "B0EXAMPLE06",
                "fnSku": "X001EXAMPLE6",
                "sellerSku": "VE-EARBUD-PRO",
                "productName": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 38,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 45,
                    "reservedQuantity": 5,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE07",
                "fnSku": "X001EXAMPLE7",
                "sellerSku": "VE-EARBUD-SPT",
                "productName": "VoltEdge FitPulse Sport Wireless Earbuds - IPX7",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 28,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 31,
                    "reservedQuantity": 2,
                    "unfulfillableQuantity": 1
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE08",
                "fnSku": "X001EXAMPLE8",
                "sellerSku": "VE-STAND-LSA",
                "productName": "VoltEdge ErgoRise Adjustable Laptop Stand - Silver Aluminum",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 56,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 56,
                    "reservedQuantity": 0,
                    "unfulfillableQuantity": 0
                },
                "lastUpdatedTime": "2026-04-26T09:00:00Z"
            },
            {
                "asin": "B0EXAMPLE09",
                "fnSku": "X001EXAMPLE9",
                "sellerSku": "VE-STAND-LSB",
                "productName": "VoltEdge ErgoRise Pro Laptop Stand with Cooling Fan - Black",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 22,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 22,
                    "reservedQuantity": 0,
                    "unfulfillableQuantity": 0
                },
                "lastUpdatedTime": "2026-04-26T09:00:00Z"
            },
            {
                "asin": "B0EXAMPLE10",
                "fnSku": "X001EXAMPLE10",
                "sellerSku": "VE-USBHUB-7P",
                "productName": "VoltEdge 7-in-1 USB-C Hub - HDMI 4K SD Card Reader",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 0,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 0,
                    "reservedQuantity": 0,
                    "unfulfillableQuantity": 0
                },
                "lastUpdatedTime": "2026-04-25T09:15:00Z"
            },
            {
                "asin": "B0EXAMPLE11",
                "fnSku": "X001EXAMPLE11",
                "sellerSku": "VE-PWR-10K",
                "productName": "VoltEdge PowerVault 10000mAh Portable Charger - USB-C PD 20W",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 70,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 78,
                    "reservedQuantity": 6,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE12",
                "fnSku": "X001EXAMPLE12",
                "sellerSku": "VE-PWR-20K",
                "productName": "VoltEdge PowerVault Pro 20000mAh with 65W USB-C",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 30,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 35,
                    "reservedQuantity": 4,
                    "unfulfillableQuantity": 1
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE13",
                "fnSku": "X001EXAMPLE13",
                "sellerSku": "VE-CHRG-WALL",
                "productName": "VoltEdge 65W GaN USB-C Wall Charger - Dual Port",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 85,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 92,
                    "reservedQuantity": 5,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE14",
                "fnSku": "X001EXAMPLE14",
                "sellerSku": "VE-SCRN-S24U",
                "productName": "VoltEdge Tempered Glass for Samsung Galaxy S24 Ultra (2-Pack)",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 148,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 156,
                    "reservedQuantity": 6,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE15",
                "fnSku": "X001EXAMPLE15",
                "sellerSku": "VE-CASE-S24U",
                "productName": "VoltEdge Clear Hybrid Case for Samsung Galaxy S24 Ultra",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 100,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 108,
                    "reservedQuantity": 6,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE16",
                "fnSku": "X001EXAMPLE16",
                "sellerSku": "VE-CHRG-MAG",
                "productName": "VoltEdge MagSnap 15W Wireless Charger Pad - Black",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 58,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 64,
                    "reservedQuantity": 4,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE17",
                "fnSku": "X001EXAMPLE17",
                "sellerSku": "VE-CHRG-CAR",
                "productName": "VoltEdge 45W Dual USB-C Car Charger with LED",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 43,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 43,
                    "reservedQuantity": 0,
                    "unfulfillableQuantity": 0
                },
                "lastUpdatedTime": "2026-04-27T14:00:00Z"
            },
            {
                "asin": "B0EXAMPLE18",
                "fnSku": "X001EXAMPLE18",
                "sellerSku": "VE-CABLE-MAG",
                "productName": "VoltEdge Magnetic USB-C Charging Cable 6ft - 100W PD",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 29,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 29,
                    "reservedQuantity": 0,
                    "unfulfillableQuantity": 0
                },
                "lastUpdatedTime": "2026-04-27T14:00:00Z"
            }
        ]
    },
    "pagination": {
        "nextToken": null
    }
}
```

---

## 32. GET /fba/inventory/v1/summaries?sellerSkus=VE-CASE-IP15,VE-EARBUD-PRO (List inventory - filter by SKU)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/fba/inventory/v1/summaries?sellerSkus=VE-CASE-IP15,VE-EARBUD-PRO"
```

**HTTP Status:** 200

```json
{
    "type": "inventory_summaries",
    "payload": {
        "granularity": {
            "granularityType": "Marketplace",
            "granularityId": "ATVPDKIKX0DER"
        },
        "inventorySummaries": [
            {
                "asin": "B0EXAMPLE01",
                "fnSku": "X001EXAMPLE1",
                "sellerSku": "VE-CASE-IP15",
                "productName": "VoltEdge Slim Armor Case for iPhone 15 - Matte Black",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 130,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 142,
                    "reservedQuantity": 8,
                    "unfulfillableQuantity": 4
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            },
            {
                "asin": "B0EXAMPLE06",
                "fnSku": "X001EXAMPLE6",
                "sellerSku": "VE-EARBUD-PRO",
                "productName": "VoltEdge AirPulse Pro Wireless Earbuds - Active Noise Cancelling",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 38,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 45,
                    "reservedQuantity": 5,
                    "unfulfillableQuantity": 2
                },
                "lastUpdatedTime": "2026-04-28T10:00:00Z"
            }
        ]
    },
    "pagination": {
        "nextToken": null
    }
}
```

---

## 33. GET /fba/inventory/v1/summaries?sellerSkus=VE-USBHUB-7P (Get inventory - out of stock item)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/fba/inventory/v1/summaries?sellerSkus=VE-USBHUB-7P"
```

**HTTP Status:** 200

```json
{
    "type": "inventory_summaries",
    "payload": {
        "granularity": {
            "granularityType": "Marketplace",
            "granularityId": "ATVPDKIKX0DER"
        },
        "inventorySummaries": [
            {
                "asin": "B0EXAMPLE10",
                "fnSku": "X001EXAMPLE10",
                "sellerSku": "VE-USBHUB-7P",
                "productName": "VoltEdge 7-in-1 USB-C Hub - HDMI 4K SD Card Reader",
                "condition": "NewItem",
                "granularity": {
                    "granularityType": "Marketplace",
                    "granularityId": "ATVPDKIKX0DER"
                },
                "inventoryDetails": {
                    "fulfillableQuantity": 0,
                    "inboundWorkingQuantity": 0,
                    "inboundShippedQuantity": 0,
                    "inboundReceivingQuantity": 0,
                    "totalQuantity": 0,
                    "reservedQuantity": 0,
                    "unfulfillableQuantity": 0
                },
                "lastUpdatedTime": "2026-04-25T09:15:00Z"
            }
        ]
    },
    "pagination": {
        "nextToken": null
    }
}
```

---

## 34. PUT /fba/inventory/v1/items/VE-CHRG-USB3 (Update inventory quantity)

```bash
curl -s -w '
%{http_code}' -X PUT "http://localhost:8004/fba/inventory/v1/items/VE-CHRG-USB3" -H 'Content-Type: application/json' -d '{"sellerSku":"VE-CHRG-USB3","quantity":75}'
```

**HTTP Status:** 200

```json
{
    "type": "inventory_update",
    "status": "SUCCESS",
    "sellerSku": "VE-CHRG-USB3"
}
```

---

## 35. PUT /fba/inventory/v1/items/NONEXIST-SKU (Update inventory - 404)

```bash
curl -s -w '
%{http_code}' -X PUT "http://localhost:8004/fba/inventory/v1/items/NONEXIST-SKU" -H 'Content-Type: application/json' -d '{"sellerSku":"NONEXIST-SKU","quantity":10}'
```

**HTTP Status:** 404

```json
{
    "error": "Inventory for SKU NONEXIST-SKU not found"
}
```

---

## 36. GET /reports/2021-06-30/reports (List all reports)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/reports/2021-06-30/reports"
```

**HTTP Status:** 200

```json
{
    "type": "reports",
    "payload": {
        "reports": [
            {
                "reportId": "REP-010",
                "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
                "processingStatus": "IN_QUEUE",
                "dataStartTime": "2026-05-01T00:00:00Z",
                "dataEndTime": "2026-05-05T23:59:59Z",
                "createdTime": "2026-05-06T01:30:00Z",
                "processingEndTime": null,
                "reportDocumentId": null
            },
            {
                "reportId": "REP-009",
                "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
                "processingStatus": "IN_PROGRESS",
                "dataStartTime": "2026-05-01T00:00:00Z",
                "dataEndTime": "2026-05-05T23:59:59Z",
                "createdTime": "2026-05-06T01:00:00Z",
                "processingEndTime": null,
                "reportDocumentId": null
            },
            {
                "reportId": "REP-008",
                "reportType": "GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE",
                "processingStatus": "DONE",
                "dataStartTime": "2026-03-01T00:00:00Z",
                "dataEndTime": "2026-04-30T23:59:59Z",
                "createdTime": "2026-05-01T06:00:00Z",
                "processingEndTime": "2026-05-01T06:03:00Z",
                "reportDocumentId": "DOC-REP-008"
            },
            {
                "reportId": "REP-006",
                "reportType": "GET_SALES_AND_TRAFFIC_REPORT",
                "processingStatus": "DONE",
                "dataStartTime": "2026-04-01T00:00:00Z",
                "dataEndTime": "2026-04-30T23:59:59Z",
                "createdTime": "2026-05-01T05:00:00Z",
                "processingEndTime": "2026-05-01T05:04:00Z",
                "reportDocumentId": "DOC-REP-006"
            },
            {
                "reportId": "REP-005",
                "reportType": "GET_FBA_FULFILLMENT_INVENTORY_HEALTH_DATA",
                "processingStatus": "DONE",
                "dataStartTime": "2026-04-01T00:00:00Z",
                "dataEndTime": "2026-04-30T23:59:59Z",
                "createdTime": "2026-05-01T04:00:00Z",
                "processingEndTime": "2026-05-01T04:12:00Z",
                "reportDocumentId": "DOC-REP-005"
            },
            {
                "reportId": "REP-004",
                "reportType": "GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL",
                "processingStatus": "DONE",
                "dataStartTime": "2026-04-01T00:00:00Z",
                "dataEndTime": "2026-04-30T23:59:59Z",
                "createdTime": "2026-05-01T03:00:00Z",
                "processingEndTime": "2026-05-01T03:08:00Z",
                "reportDocumentId": "DOC-REP-004"
            },
            {
                "reportId": "REP-001",
                "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
                "processingStatus": "DONE",
                "dataStartTime": "2026-04-01T00:00:00Z",
                "dataEndTime": "2026-04-30T23:59:59Z",
                "createdTime": "2026-05-01T02:00:00Z",
                "processingEndTime": "2026-05-01T02:05:00Z",
                "reportDocumentId": "DOC-REP-001"
            },
            {
                "reportId": "REP-002",
                "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
                "processingStatus": "DONE",
                "dataStartTime": "2026-04-01T00:00:00Z",
                "dataEndTime": "2026-04-30T23:59:59Z",
                "createdTime": "2026-05-01T02:00:00Z",
                "processingEndTime": "2026-05-01T02:06:00Z",
                "reportDocumentId": "DOC-REP-002"
            },
            {
                "reportId": "REP-007",
                "reportType": "GET_FBA_INVENTORY_PLANNING_DATA",
                "processingStatus": "DONE",
                "dataStartTime": "2026-04-15T00:00:00Z",
                "dataEndTime": "2026-04-28T23:59:59Z",
                "createdTime": "2026-04-29T02:00:00Z",
                "processingEndTime": "2026-04-29T02:05:00Z",
                "reportDocumentId": "DOC-REP-007"
            },
            {
                "reportId": "REP-003",
                "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
                "processingStatus": "DONE",
                "dataStartTime": "2026-04-28T00:00:00Z",
                "dataEndTime": "2026-04-28T23:59:59Z",
                "createdTime": "2026-04-29T01:00:00Z",
                "processingEndTime": "2026-04-29T01:03:00Z",
                "reportDocumentId": "DOC-REP-003"
            }
        ]
    }
}
```

---

## 37. GET /reports/2021-06-30/reports?reportTypes=GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA (List reports - filter by type)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/reports/2021-06-30/reports?reportTypes=GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA"
```

**HTTP Status:** 200

```json
{
    "type": "reports",
    "payload": {
        "reports": [
            {
                "reportId": "REP-010",
                "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
                "processingStatus": "IN_QUEUE",
                "dataStartTime": "2026-05-01T00:00:00Z",
                "dataEndTime": "2026-05-05T23:59:59Z",
                "createdTime": "2026-05-06T01:30:00Z",
                "processingEndTime": null,
                "reportDocumentId": null
            },
            {
                "reportId": "REP-003",
                "reportType": "GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA",
                "processingStatus": "DONE",
                "dataStartTime": "2026-04-28T00:00:00Z",
                "dataEndTime": "2026-04-28T23:59:59Z",
                "createdTime": "2026-04-29T01:00:00Z",
                "processingEndTime": "2026-04-29T01:03:00Z",
                "reportDocumentId": "DOC-REP-003"
            }
        ]
    }
}
```

---

## 38. GET /reports/2021-06-30/reports?processingStatuses=IN_PROGRESS (List reports - filter by status)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/reports/2021-06-30/reports?processingStatuses=IN_PROGRESS"
```

**HTTP Status:** 200

```json
{
    "type": "reports",
    "payload": {
        "reports": [
            {
                "reportId": "REP-009",
                "reportType": "GET_MERCHANT_LISTINGS_ALL_DATA",
                "processingStatus": "IN_PROGRESS",
                "dataStartTime": "2026-05-01T00:00:00Z",
                "dataEndTime": "2026-05-05T23:59:59Z",
                "createdTime": "2026-05-06T01:00:00Z",
                "processingEndTime": null,
                "reportDocumentId": null
            }
        ]
    }
}
```

---

## 39. GET /reports/2021-06-30/reports/REP-001 (Get report by ID)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/reports/2021-06-30/reports/REP-001"
```

**HTTP Status:** 200

```json
{
    "type": "report",
    "payload": {
        "reportId": "REP-001",
        "reportType": "GET_FLAT_FILE_OPEN_LISTINGS_DATA",
        "processingStatus": "DONE",
        "dataStartTime": "2026-04-01T00:00:00Z",
        "dataEndTime": "2026-04-30T23:59:59Z",
        "createdTime": "2026-05-01T02:00:00Z",
        "processingEndTime": "2026-05-01T02:05:00Z",
        "reportDocumentId": "DOC-REP-001"
    }
}
```

---

## 40. GET /reports/2021-06-30/reports/REP-999 (Get report - 404)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/reports/2021-06-30/reports/REP-999"
```

**HTTP Status:** 404

```json
{
    "error": "Report REP-999 not found"
}
```

---

## 41. POST /reports/2021-06-30/reports (Create report)

```bash
curl -s -w '
%{http_code}' -X POST "http://localhost:8004/reports/2021-06-30/reports" -H 'Content-Type: application/json' -d '{"reportType":"GET_FLAT_FILE_OPEN_LISTINGS_DATA","dataStartTime":"2026-05-01T00:00:00Z","dataEndTime":"2026-05-06T23:59:59Z","marketplaceIds":["ATVPDKIKX0DER"]}'
```

**HTTP Status:** 202

```json
{
    "type": "report_created",
    "payload": {
        "reportId": "REP-011"
    }
}
```

---

## 42. GET /products/pricing/v0/competitivePrice?Asin=B0EXAMPLE06&MarketplaceId=ATVPDKIKX0DER (Get competitive pricing by ASIN)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/products/pricing/v0/competitivePrice?Asin=B0EXAMPLE06&MarketplaceId=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "competitive_pricing",
    "payload": {
        "ASIN": "B0EXAMPLE06",
        "Product": {
            "CompetitivePricing": {
                "CompetitivePrices": [
                    {
                        "CompetitivePriceId": "1",
                        "Price": {
                            "ListingPrice": {
                                "CurrencyCode": "USD",
                                "Amount": "47.99"
                            },
                            "LandedPrice": {
                                "CurrencyCode": "USD",
                                "Amount": "49.99"
                            },
                            "Shipping": {
                                "CurrencyCode": "USD",
                                "Amount": "0.0"
                            }
                        },
                        "condition": "New",
                        "belongsToRequester": true
                    }
                ],
                "NumberOfOfferListings": [
                    {
                        "condition": "New",
                        "Count": 6
                    }
                ]
            },
            "Offers": [
                {
                    "BuyBoxPrices": [
                        {
                            "condition": "New",
                            "LandedPrice": {
                                "CurrencyCode": "USD",
                                "Amount": "49.99"
                            },
                            "ListingPrice": {
                                "CurrencyCode": "USD",
                                "Amount": "49.99"
                            },
                            "Shipping": {
                                "CurrencyCode": "USD",
                                "Amount": "0.00"
                            }
                        }
                    ],
                    "NumberOfOffers": [
                        {
                            "condition": "New",
                            "fulfillmentChannel": "Amazon",
                            "Count": 6
                        }
                    ]
                }
            ]
        }
    }
}
```

---

## 43. GET /products/pricing/v0/competitivePrice?Sku=VE-CASE-IP15&MarketplaceId=ATVPDKIKX0DER (Get competitive pricing by SKU)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/products/pricing/v0/competitivePrice?Sku=VE-CASE-IP15&MarketplaceId=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "competitive_pricing",
    "payload": {
        "ASIN": "B0EXAMPLE01",
        "Product": {
            "CompetitivePricing": {
                "CompetitivePrices": [
                    {
                        "CompetitivePriceId": "1",
                        "Price": {
                            "ListingPrice": {
                                "CurrencyCode": "USD",
                                "Amount": "17.99"
                            },
                            "LandedPrice": {
                                "CurrencyCode": "USD",
                                "Amount": "19.99"
                            },
                            "Shipping": {
                                "CurrencyCode": "USD",
                                "Amount": "0.0"
                            }
                        },
                        "condition": "New",
                        "belongsToRequester": false
                    }
                ],
                "NumberOfOfferListings": [
                    {
                        "condition": "New",
                        "Count": 12
                    }
                ]
            },
            "Offers": [
                {
                    "BuyBoxPrices": [
                        {
                            "condition": "New",
                            "LandedPrice": {
                                "CurrencyCode": "USD",
                                "Amount": "17.99"
                            },
                            "ListingPrice": {
                                "CurrencyCode": "USD",
                                "Amount": "17.99"
                            },
                            "Shipping": {
                                "CurrencyCode": "USD",
                                "Amount": "0.00"
                            }
                        }
                    ],
                    "NumberOfOffers": [
                        {
                            "condition": "New",
                            "fulfillmentChannel": "Amazon",
                            "Count": 12
                        }
                    ]
                }
            ]
        }
    }
}
```

---

## 44. GET /products/pricing/v0/competitivePrice?Asin=B0NONEXIST (Get competitive pricing - 404)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/products/pricing/v0/competitivePrice?Asin=B0NONEXIST"
```

**HTTP Status:** 404

```json
{
    "error": "Pricing not found for B0NONEXIST"
}
```

---

## 45. GET /products/pricing/v0/items/B0EXAMPLE06/offers?MarketplaceId=ATVPDKIKX0DER&ItemCondition=New (Get item offers)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/products/pricing/v0/items/B0EXAMPLE06/offers?MarketplaceId=ATVPDKIKX0DER&ItemCondition=New"
```

**HTTP Status:** 200

```json
{
    "type": "item_offers",
    "payload": {
        "ASIN": "B0EXAMPLE06",
        "status": "Success",
        "ItemCondition": "New",
        "Summary": {
            "LowestPrices": [
                {
                    "condition": "New",
                    "fulfillmentChannel": "Amazon",
                    "LandedPrice": {
                        "CurrencyCode": "USD",
                        "Amount": "47.99"
                    },
                    "ListingPrice": {
                        "CurrencyCode": "USD",
                        "Amount": "47.99"
                    },
                    "Shipping": {
                        "CurrencyCode": "USD",
                        "Amount": "0.0"
                    }
                }
            ],
            "BuyBoxPrices": [
                {
                    "condition": "New",
                    "LandedPrice": {
                        "CurrencyCode": "USD",
                        "Amount": "49.99"
                    },
                    "ListingPrice": {
                        "CurrencyCode": "USD",
                        "Amount": "49.99"
                    },
                    "Shipping": {
                        "CurrencyCode": "USD",
                        "Amount": "0.00"
                    }
                }
            ],
            "NumberOfOffers": [
                {
                    "condition": "New",
                    "fulfillmentChannel": "Amazon",
                    "Count": 6
                }
            ],
            "BuyBoxEligibleOffers": [
                {
                    "condition": "New",
                    "fulfillmentChannel": "Amazon",
                    "Count": 6
                }
            ]
        },
        "Offers": [
            {
                "SellerFeedbackRating": {
                    "SellerPositiveFeedbackRating": 96.5,
                    "FeedbackCount": 1247
                },
                "ListingPrice": {
                    "CurrencyCode": "USD",
                    "Amount": "49.99"
                },
                "Shipping": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "IsBuyBoxWinner": true,
                "IsFulfilledByAmazon": true
            }
        ]
    }
}
```

---

## 46. GET /products/pricing/v0/items/B0EXAMPLE01/offers?MarketplaceId=ATVPDKIKX0DER (Get item offers - another ASIN)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/products/pricing/v0/items/B0EXAMPLE01/offers?MarketplaceId=ATVPDKIKX0DER"
```

**HTTP Status:** 200

```json
{
    "type": "item_offers",
    "payload": {
        "ASIN": "B0EXAMPLE01",
        "status": "Success",
        "ItemCondition": "New",
        "Summary": {
            "LowestPrices": [
                {
                    "condition": "New",
                    "fulfillmentChannel": "Amazon",
                    "LandedPrice": {
                        "CurrencyCode": "USD",
                        "Amount": "17.99"
                    },
                    "ListingPrice": {
                        "CurrencyCode": "USD",
                        "Amount": "17.99"
                    },
                    "Shipping": {
                        "CurrencyCode": "USD",
                        "Amount": "0.0"
                    }
                }
            ],
            "BuyBoxPrices": [
                {
                    "condition": "New",
                    "LandedPrice": {
                        "CurrencyCode": "USD",
                        "Amount": "17.99"
                    },
                    "ListingPrice": {
                        "CurrencyCode": "USD",
                        "Amount": "17.99"
                    },
                    "Shipping": {
                        "CurrencyCode": "USD",
                        "Amount": "0.00"
                    }
                }
            ],
            "NumberOfOffers": [
                {
                    "condition": "New",
                    "fulfillmentChannel": "Amazon",
                    "Count": 12
                }
            ],
            "BuyBoxEligibleOffers": [
                {
                    "condition": "New",
                    "fulfillmentChannel": "Amazon",
                    "Count": 12
                }
            ]
        },
        "Offers": [
            {
                "SellerFeedbackRating": {
                    "SellerPositiveFeedbackRating": 96.5,
                    "FeedbackCount": 1247
                },
                "ListingPrice": {
                    "CurrencyCode": "USD",
                    "Amount": "19.99"
                },
                "Shipping": {
                    "CurrencyCode": "USD",
                    "Amount": "0.0"
                },
                "IsBuyBoxWinner": false,
                "IsFulfilledByAmazon": true
            }
        ]
    }
}
```

---

## 47. GET /products/pricing/v0/items/B0NONEXIST/offers (Get item offers - 404)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/products/pricing/v0/items/B0NONEXIST/offers"
```

**HTTP Status:** 404

```json
{
    "error": "Offers not found for ASIN B0NONEXIST"
}
```

---

## 48. GET /returns/v0/returns (List all returns)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/returns/v0/returns"
```

**HTTP Status:** 200

```json
{
    "type": "returns",
    "count": 5,
    "total": 5,
    "offset": 0,
    "limit": 100,
    "results": [
        {
            "returnId": "RET-005",
            "AmazonOrderId": "114-8890123-6789000",
            "sellerSKU": "VE-SCRN-IP15",
            "asin": "B0EXAMPLE03",
            "returnDate": "2026-04-10T16:00:00Z",
            "returnReason": "DEFECTIVE",
            "returnStatus": "Authorized",
            "returnQuantity": 1,
            "resolution": "PENDING",
            "refundAmount": 12.99,
            "refundCurrency": "USD",
            "buyerComments": "Screen protector has tiny bubbles that won't go away even with the alignment frame."
        },
        {
            "returnId": "RET-004",
            "AmazonOrderId": "114-9981234-5567800",
            "sellerSKU": "VE-EARBUD-SPT",
            "asin": "B0EXAMPLE07",
            "returnDate": "2026-03-05T11:00:00Z",
            "returnReason": "NO_LONGER_NEEDED",
            "returnStatus": "Completed",
            "returnQuantity": 1,
            "resolution": "REFUND",
            "refundAmount": 34.99,
            "refundCurrency": "USD",
            "buyerComments": "Changed my mind. Got a different brand."
        },
        {
            "returnId": "RET-003",
            "AmazonOrderId": "114-7723891-3345600",
            "sellerSKU": "VE-CHRG-USB3",
            "asin": "B0EXAMPLE04",
            "returnDate": "2026-02-25T09:00:00Z",
            "returnReason": "SWITCHEROO",
            "returnStatus": "Authorized",
            "returnQuantity": 1,
            "resolution": "PENDING",
            "refundAmount": 16.99,
            "refundCurrency": "USD",
            "buyerComments": "Received only one cable instead of 2-pack."
        },
        {
            "returnId": "RET-002",
            "AmazonOrderId": "114-5578234-9921100",
            "sellerSKU": "VE-EARBUD-PRO",
            "asin": "B0EXAMPLE06",
            "returnDate": "2026-02-20T14:30:00Z",
            "returnReason": "NOT_AS_DESCRIBED",
            "returnStatus": "Completed",
            "returnQuantity": 1,
            "resolution": "REFUND",
            "refundAmount": 49.99,
            "refundCurrency": "USD",
            "buyerComments": "ANC is not as strong as described. Can still hear traffic clearly."
        },
        {
            "returnId": "RET-001",
            "AmazonOrderId": "114-3941689-8772200",
            "sellerSKU": "VE-CASE-IP15",
            "asin": "B0EXAMPLE01",
            "returnDate": "2026-02-18T10:00:00Z",
            "returnReason": "DEFECTIVE",
            "returnStatus": "Completed",
            "returnQuantity": 1,
            "resolution": "REFUND",
            "refundAmount": 19.99,
            "refundCurrency": "USD",
            "buyerComments": "Case cracked on first drop. Not what I expected from military grade protection."
        }
    ]
}
```

---

## 49. GET /returns/v0/returns?status=Authorized (List returns - filter Authorized)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/returns/v0/returns?status=Authorized"
```

**HTTP Status:** 200

```json
{
    "type": "returns",
    "count": 2,
    "total": 2,
    "offset": 0,
    "limit": 100,
    "results": [
        {
            "returnId": "RET-005",
            "AmazonOrderId": "114-8890123-6789000",
            "sellerSKU": "VE-SCRN-IP15",
            "asin": "B0EXAMPLE03",
            "returnDate": "2026-04-10T16:00:00Z",
            "returnReason": "DEFECTIVE",
            "returnStatus": "Authorized",
            "returnQuantity": 1,
            "resolution": "PENDING",
            "refundAmount": 12.99,
            "refundCurrency": "USD",
            "buyerComments": "Screen protector has tiny bubbles that won't go away even with the alignment frame."
        },
        {
            "returnId": "RET-003",
            "AmazonOrderId": "114-7723891-3345600",
            "sellerSKU": "VE-CHRG-USB3",
            "asin": "B0EXAMPLE04",
            "returnDate": "2026-02-25T09:00:00Z",
            "returnReason": "SWITCHEROO",
            "returnStatus": "Authorized",
            "returnQuantity": 1,
            "resolution": "PENDING",
            "refundAmount": 16.99,
            "refundCurrency": "USD",
            "buyerComments": "Received only one cable instead of 2-pack."
        }
    ]
}
```

---

## 50. GET /returns/v0/returns?status=Completed (List returns - filter Completed)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/returns/v0/returns?status=Completed"
```

**HTTP Status:** 200

```json
{
    "type": "returns",
    "count": 3,
    "total": 3,
    "offset": 0,
    "limit": 100,
    "results": [
        {
            "returnId": "RET-004",
            "AmazonOrderId": "114-9981234-5567800",
            "sellerSKU": "VE-EARBUD-SPT",
            "asin": "B0EXAMPLE07",
            "returnDate": "2026-03-05T11:00:00Z",
            "returnReason": "NO_LONGER_NEEDED",
            "returnStatus": "Completed",
            "returnQuantity": 1,
            "resolution": "REFUND",
            "refundAmount": 34.99,
            "refundCurrency": "USD",
            "buyerComments": "Changed my mind. Got a different brand."
        },
        {
            "returnId": "RET-002",
            "AmazonOrderId": "114-5578234-9921100",
            "sellerSKU": "VE-EARBUD-PRO",
            "asin": "B0EXAMPLE06",
            "returnDate": "2026-02-20T14:30:00Z",
            "returnReason": "NOT_AS_DESCRIBED",
            "returnStatus": "Completed",
            "returnQuantity": 1,
            "resolution": "REFUND",
            "refundAmount": 49.99,
            "refundCurrency": "USD",
            "buyerComments": "ANC is not as strong as described. Can still hear traffic clearly."
        },
        {
            "returnId": "RET-001",
            "AmazonOrderId": "114-3941689-8772200",
            "sellerSKU": "VE-CASE-IP15",
            "asin": "B0EXAMPLE01",
            "returnDate": "2026-02-18T10:00:00Z",
            "returnReason": "DEFECTIVE",
            "returnStatus": "Completed",
            "returnQuantity": 1,
            "resolution": "REFUND",
            "refundAmount": 19.99,
            "refundCurrency": "USD",
            "buyerComments": "Case cracked on first drop. Not what I expected from military grade protection."
        }
    ]
}
```

---

## 51. GET /returns/v0/returns?orderId=114-3941689-8772200 (List returns - filter by order ID)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/returns/v0/returns?orderId=114-3941689-8772200"
```

**HTTP Status:** 200

```json
{
    "type": "returns",
    "count": 1,
    "total": 1,
    "offset": 0,
    "limit": 100,
    "results": [
        {
            "returnId": "RET-001",
            "AmazonOrderId": "114-3941689-8772200",
            "sellerSKU": "VE-CASE-IP15",
            "asin": "B0EXAMPLE01",
            "returnDate": "2026-02-18T10:00:00Z",
            "returnReason": "DEFECTIVE",
            "returnStatus": "Completed",
            "returnQuantity": 1,
            "resolution": "REFUND",
            "refundAmount": 19.99,
            "refundCurrency": "USD",
            "buyerComments": "Case cracked on first drop. Not what I expected from military grade protection."
        }
    ]
}
```

---

## 52. GET /returns/v0/returns/RET-001 (Get return by ID)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/returns/v0/returns/RET-001"
```

**HTTP Status:** 200

```json
{
    "type": "return",
    "return": {
        "returnId": "RET-001",
        "AmazonOrderId": "114-3941689-8772200",
        "sellerSKU": "VE-CASE-IP15",
        "asin": "B0EXAMPLE01",
        "returnDate": "2026-02-18T10:00:00Z",
        "returnReason": "DEFECTIVE",
        "returnStatus": "Completed",
        "returnQuantity": 1,
        "resolution": "REFUND",
        "refundAmount": 19.99,
        "refundCurrency": "USD",
        "buyerComments": "Case cracked on first drop. Not what I expected from military grade protection."
    }
}
```

---

## 53. GET /returns/v0/returns/RET-999 (Get return - 404)

```bash
curl -s -w '
%{http_code}' -X GET "http://localhost:8004/returns/v0/returns/RET-999"
```

**HTTP Status:** 404

```json
{
    "error": "Return RET-999 not found"
}
```

---

## 54. POST /returns/v0/returns/RET-003/authorize (Authorize return)

```bash
curl -s -w '
%{http_code}' -X POST "http://localhost:8004/returns/v0/returns/RET-003/authorize"
```

**HTTP Status:** 200

```json
{
    "type": "return_authorization",
    "status": "SUCCESS",
    "returnId": "RET-003"
}
```

---

## 55. POST /returns/v0/returns/RET-005/close (Close return)

```bash
curl -s -w '
%{http_code}' -X POST "http://localhost:8004/returns/v0/returns/RET-005/close"
```

**HTTP Status:** 200

```json
{
    "type": "return_close",
    "status": "SUCCESS",
    "returnId": "RET-005"
}
```

---

Total tests: 55
