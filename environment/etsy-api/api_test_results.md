# Etsy Mock API - Full Endpoint Test Results
Generated: Wed May  6 23:03:57 IST 2026

---

## 1. GET /health
```json
{
    "status": "ok"
}
```

## 2. GET /v3/application/shops/29457183 (valid shop)
```json
{
    "type": "shop",
    "shop": {
        "shop_id": 29457183,
        "shop_name": "WillowAndClayStudio",
        "user_id": 81726354,
        "title": "Handmade Ceramic Pottery \u2022 Mugs, Bowls & Vases",
        "announcement": "Welcome to Willow & Clay Studio! Every piece is wheel-thrown by hand in my Portland, OR studio using locally-sourced stoneware clay. Please allow 1-2 weeks for made-to-order items. Custom glaze colors available\u2014just message me!",
        "currency_code": "USD",
        "is_vacation": false,
        "vacation_message": null,
        "sale_message": "Thank you so much for your order! I\u2019ll begin working on your piece within 2-3 business days. Each item is handmade, so slight variations in color and form are part of what makes it unique. Please don\u2019t hesitate to reach out if you have any questions!",
        "digital_sale_message": null,
        "listing_active_count": 18,
        "digital_listing_count": 0,
        "login_name": "ElenaWillow",
        "accepts_custom_requests": true,
        "policy_welcome": "Thanks for visiting Willow & Clay Studio!",
        "policy_payment": "I accept payments through Etsy's secure checkout system including credit cards, debit cards, Etsy gift cards, and PayPal.",
        "policy_shipping": "All items ship via USPS Priority Mail. Made-to-order items ship within 10-14 business days. Ready-to-ship items go out within 3-5 business days.",
        "policy_refunds": "I want you to love your piece! If it arrives damaged, please contact me within 48 hours with photos and I'll send a replacement. Due to the handmade nature of my work, I cannot accept returns for color/size variations.",
        "num_favorers": 4872,
        "url": "https://www.etsy.com/shop/WillowAndClayStudio",
        "image_url_760x100": "https://i.etsystatic.com/isbl/example/willow_banner.jpg",
        "icon_url_fullxfull": "https://i.etsystatic.com/iusa/example/willow_icon.jpg",
        "review_average": 4.89,
        "review_count": 623,
        "create_date": "2019-03-15T10:22:00",
        "update_date": "2025-04-28T14:05:00"
    }
}
```

## 3. GET /v3/application/shops/99999 (404 - invalid shop)
```json
{"error":"Shop 99999 not found"}
HTTP_STATUS: 404```

## 4. PUT /v3/application/shops/29457183 (update shop)
```json
{
    "type": "shop",
    "shop": {
        "shop_id": 29457183,
        "shop_name": "WillowAndClayStudio",
        "user_id": 81726354,
        "title": "Handmade Ceramic Pottery \u2022 Mugs, Bowls & Vases",
        "announcement": "TEST UPDATE: Summer sale on all mugs!",
        "currency_code": "USD",
        "is_vacation": false,
```

## 5. GET /v3/application/shops/29457183/sections
```json
{
    "type": "shop_sections",
    "count": 6,
    "results": [
        {
            "shop_section_id": 40001,
            "shop_id": 29457183,
            "title": "Mugs & Cups",
            "rank": 1,
            "active_listing_count": 6
        },
        {
            "shop_section_id": 40002,
            "shop_id": 29457183,
            "title": "Bowls & Dishes",
            "rank": 2,
            "active_listing_count": 5
        },
        {
            "shop_section_id": 40003,
            "shop_id": 29457183,
            "title": "Vases & Planters",
            "rank": 3,
            "active_listing_count": 4
        },
        {
            "shop_section_id": 40004,
            "shop_id": 29457183,
            "title": "Plates & Platters",
            "rank": 4,
            "active_listing_count": 2
        },
        {
            "shop_section_id": 40005,
            "shop_id": 29457183,
            "title": "Gift Sets",
            "rank": 5,
            "active_listing_count": 1
        },
        {
            "shop_section_id": 40006,
            "shop_id": 29457183,
            "title": "Sale Items",
            "rank": 6,
            "active_listing_count": 2
        }
    ]
}
```

## 6. GET /v3/application/shops/29457183/sections/40001 (single section)
```json
{
    "type": "shop_section",
    "shop_section": {
        "shop_section_id": 40001,
        "shop_id": 29457183,
        "title": "Mugs & Cups",
        "rank": 1,
        "active_listing_count": 6
    }
}
```

## 7. GET /v3/application/shops/29457183/sections/99999 (404)
```json
{"error":"Shop section 99999 not found"}
HTTP_STATUS: 404```

## 8. GET /v3/application/shops/29457183/listings (default - active, limit 25)
```json
{
    "type": "listings",
    "count": 19,
    "total": 19,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "listing_id": 1019,
            "shop_id": 29457183,
            "title": "Oval Serving Platter - Earthy Brown Glaze",
            "description": "Large oval platter with a rich earthy brown glaze and subtle golden flecks. Perfect for charcuterie or as a decorative tray. 14 x 9 inches.",
            "price": 68.0,
            "currency_code": "USD",
            "quantity": 2,
            "taxonomy_id": 2094,
            "tags": [
                "serving platter",
                "oval platter",
                "ceramic platter",
                "charcuterie board",
                "pottery platter",
                "brown ceramic"
            ],
            "materials": [
                "stoneware clay",
                "tenmoku glaze"
            ],
            "who_made": "i_did",
            "when_made": "2020_2026",
... (truncated)
```

## 9. GET /v3/application/shops/29457183/listings?state=draft
```json
{
    "type": "listings",
    "count": 1,
    "total": 1,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "listing_id": 1020,
            "shop_id": 29457183,
            "title": "Ceramic Travel Mug with Silicone Lid - Draft",
            "description": "Double-walled ceramic travel mug with food-grade silicone lid. Keeps drinks warm longer. 16oz capacity. NOT YET AVAILABLE - testing prototypes.",
            "price": 40.0,
            "currency_code": "USD",
            "quantity": 0,
            "taxonomy_id": 2078,
            "tags": [
                "travel mug",
                "ceramic travel mug",
                "commuter mug",
                "to-go mug",
                "double wall mug"
            ],
            "materials": [
                "stoneware clay",
                "feldspar glaze",
                "silicone"
            ],
            "who_made": "i_did",
            "when_made": "2020_2026",
            "state": "draft",
            "shop_section_id": 40001,
            "processing_min": 14,
            "processing_max": 21,
            "item_weight": 1.1,
            "item_weight_unit": "lb",
            "item_length": 3.5,
            "item_width": 3.5,
            "item_height": 6.5,
            "item_dimensions_unit": "in",
            "views": 0,
            "num_favorers": 0,
            "shipping_profile_id": 50001,
            "return_policy_id": 60001,
            "is_supply": false,
            "is_customizable": false,
            "is_personalizable": false,
            "created_timestamp": "2025-04-01T09:00:00",
            "updated_timestamp": "2025-04-28T16:00:00",
            "ending_timestamp": "2025-10-01T09:00:00"
        }
    ]
}
```

## 10. GET /v3/application/shops/29457183/listings?q=vase&sort_on=price&sort_order=asc
```json
{
    "type": "listings",
    "count": 2,
    "total": 2,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "listing_id": 1003,
            "shop_id": 29457183,
            "title": "Minimalist Bud Vase - Sage Green",
            "description": "Simple and elegant bud vase in a soft sage green glaze. Perfect for a single stem or small wildflower arrangement. Height approximately 6 inches.",
            "price": 28.0,
            "currency_code": "USD",
            "quantity": 12,
            "taxonomy_id": 2101,
            "tags": [
                "bud vase",
                "ceramic vase",
                "minimalist vase",
                "sage green",
                "pottery vase",
                "flower vase",
                "small vase"
            ],
            "materials": [
                "stoneware clay",
                "celadon glaze"
            ],
            "who_made": "i_did",
            "when_made": "2020_2026",
            "state": "active",
            "shop_section_id": 40003,
            "processing_min": 5,
            "processing_max": 10,
            "item_weight": 0.6,
            "item_weight_unit": "lb",
            "item_length": 3.0,
            "item_width": 3.0,
            "item_height": 6.0,
            "item_dimensions_unit": "in",
            "views": 956,
            "num_favorers": 178,
            "shipping_profile_id": 50001,
            "return_policy_id": 60001,
            "is_supply": false,
            "is_customizable": true,
            "is_personalizable": false,
            "created_timestamp": "2024-03-10T16:45:00",
            "updated_timestamp": "2025-04-15T08:30:00",
            "ending_timestamp": "2025-09-10T16:45:00"
        },
        {
            "listing_id": 1011,
            "shop_id": 29457183,
            "title": "Tall Ceramic Vase - Textured White",
            "description": "Tall vase with hand-carved geometric texture under a matte white glaze. Approximately 10 inches tall. A stunning piece for dried flowers or branches.",
            "price": 65.0,
            "currency_code": "USD",
            "quantity": 3,
            "taxonomy_id": 2101,
            "tags": [
                "tall vase",
                "ceramic vase",
                "textured vase",
                "white vase",
                "pottery vase",
                "decorative vase",
                "carved ceramic"
            ],
            "materials": [
                "stoneware clay",
                "matte white glaze"
            ],
            "who_made": "i_did",
            "when_made": "2020_2026",
            "state": "active",
            "shop_section_id": 40003,
            "processing_min": 10,
            "processing_max": 14,
            "item_weight": 1.5,
            "item_weight_unit": "lb",
            "item_length": 4.5,
            "item_width": 4.5,
            "item_height": 10.0,
            "item_dimensions_unit": "in",
            "views": 892,
            "num_favorers": 201,
            "shipping_profile_id": 50001,
            "return_policy_id": 60001,
            "is_supply": false,
            "is_customizable": false,
            "is_personalizable": false,
            "created_timestamp": "2024-08-22T09:30:00",
            "updated_timestamp": "2025-04-05T14:00:00",
            "ending_timestamp": "2026-02-22T09:30:00"
        }
    ]
}
```

## 11. GET /v3/application/shops/29457183/listings?section_id=40001&limit=3
```json
{
    "type": "listings",
    "count": 3,
    "total": 5,
    "offset": 0,
    "limit": 3,
    "results": [
        {
            "listing_id": 1014,
            "shop_id": 29457183,
            "title": "Ceramic Tumbler - No Handle - Wabi Sabi",
            "description": "Japanese-inspired tumbler with deliberate imperfections celebrating wabi-sabi aesthetic. Unglazed exterior with glazed interior. Holds 10oz.",
            "price": 24.0,
            "currency_code": "USD",
            "quantity": 7,
            "taxonomy_id": 2078,
            "tags": [
                "tumbler",
                "ceramic tumbler",
                "wabi sabi",
                "japanese pottery",
                "no handle cup",
                "yunomi",
                "handmade tumbler"
            ],
            "materials": [
                "stoneware clay",
                "shino glaze"
            ],
            "who_made": "i_did",
... (truncated)
```

## 12. GET /v3/application/shops/29457183/listings?limit=3&offset=3
```json
{
    "type": "listings",
    "count": 3,
    "total": 19,
    "offset": 3,
    "limit": 3,
    "results": [
        {
            "listing_id": 1016,
            "shop_id": 29457183,
            "title": "Wall-Mounted Ceramic Planter - Half Moon",
            "description": "Semi-circular wall planter with mounting hole. Perfect for trailing plants. Available in Midnight Blue or Forest Green.",
            "price": 34.0,
            "currency_code": "USD",
            "quantity": 5,
            "taxonomy_id": 2101,
            "tags": [
                "wall planter",
                "hanging planter",
                "ceramic planter",
                "half moon planter",
                "indoor planter",
                "trailing plants"
            ],
            "materials": [
                "stoneware clay",
                "cobalt glaze"
            ],
            "who_made": "i_did",
            "when_made": "2020_2026",
... (truncated)
```

## 13. GET /v3/application/listings/1001 (single listing)
```json
{
    "type": "listing",
    "listing": {
        "listing_id": 1001,
        "shop_id": 29457183,
        "title": "Handmade Ceramic Mug - Speckled White Glaze",
        "description": "Wheel-thrown stoneware mug with a creamy speckled white glaze. Holds approximately 12oz. Microwave and dishwasher safe. Each mug is unique due to the handmade process.",
        "price": 32.0,
        "currency_code": "USD",
        "quantity": 8,
        "taxonomy_id": 2078,
        "tags": [
            "ceramic mug",
            "handmade mug",
            "pottery mug",
            "stoneware",
            "speckled glaze",
            "coffee mug",
            "artisan mug"
        ],
        "materials": [
            "stoneware clay",
            "feldspar glaze"
        ],
        "who_made": "i_did",
        "when_made": "2020_2026",
        "state": "active",
        "shop_section_id": 40001,
        "processing_min": 7,
        "processing_max": 14,
        "item_weight": 0.85,
        "item_weight_unit": "lb",
        "item_length": 3.5,
        "item_width": 3.5,
        "item_height": 4.0,
        "item_dimensions_unit": "in",
        "views": 1847,
        "num_favorers": 312,
        "shipping_profile_id": 50001,
        "return_policy_id": 60001,
        "is_supply": false,
        "is_customizable": true,
        "is_personalizable": true,
        "created_timestamp": "2024-01-15T09:30:00",
        "updated_timestamp": "2025-04-20T11:15:00",
        "ending_timestamp": "2025-07-15T09:30:00"
    }
}
```

## 14. GET /v3/application/listings/99999 (404)
```json
{"error":"Listing 99999 not found"}
HTTP_STATUS: 404```

## 15. POST /v3/application/shops/29457183/listings (create listing)
```json
{
    "type": "listing",
    "listing": {
        "listing_id": 1021,
        "shop_id": 29457183,
        "title": "TEST: Ceramic Candle Holder",
        "description": "A test candle holder in matte black.",
        "price": 28.0,
        "currency_code": "USD",
        "quantity": 6,
        "taxonomy_id": 2078,
        "tags": [
            "candle holder",
            "ceramic",
            "black"
        ],
        "materials": [
            "stoneware clay"
        ],
        "who_made": "i_did",
        "when_made": "2020_2026",
        "state": "draft",
        "shop_section_id": null,
        "processing_min": null,
        "processing_max": null,
        "item_weight": null,
        "item_weight_unit": null,
        "item_length": null,
        "item_width": null,
        "item_height": null,
        "item_dimensions_unit": null,
        "views": 0,
        "num_favorers": 0,
        "shipping_profile_id": null,
        "return_policy_id": null,
        "is_supply": false,
        "is_customizable": false,
        "is_personalizable": false,
        "created_timestamp": "2026-05-06T17:33:57",
        "updated_timestamp": "2026-05-06T17:33:57",
        "ending_timestamp": null
    }
}
```

## 16. PUT /v3/application/listings/1001 (update listing price+quantity)
```json
{
    "type": "listing",
    "listing": {
        "listing_id": 1001,
        "shop_id": 29457183,
        "title": "Handmade Ceramic Mug - Speckled White Glaze",
        "description": "Wheel-thrown stoneware mug with a creamy speckled white glaze. Holds approximately 12oz. Microwave and dishwasher safe. Each mug is unique due to the handmade process.",
        "price": 36.0,
        "currency_code": "USD",
        "quantity": 15,
        "taxonomy_id": 2078,
        "tags": [
            "ceramic mug",
            "handmade mug",
            "pottery mug",
            "stoneware",
            "speckled glaze",
            "coffee mug",
            "artisan mug"
        ],
... (truncated)
```

## 17. DELETE /v3/application/listings/1017 (delete seconds sale listing)
```json
{
    "type": "listing",
    "deleted": true,
    "listing_id": 1017
}
```

## 18. DELETE /v3/application/listings/99999 (404)
```json
{"error":"Listing 99999 not found"}
HTTP_STATUS: 404```

## 19. GET /v3/application/listings/1001/images
```json
{
    "type": "listing_images",
    "count": 3,
    "results": [
        {
            "listing_image_id": 90001,
            "listing_id": 1001,
            "shop_id": 29457183,
            "rank": 1,
            "url_75x75": "https://i.etsystatic.com/example/il_75x75.90001.jpg",
            "url_170x135": "https://i.etsystatic.com/example/il_170x135.90001.jpg",
            "url_570xN": "https://i.etsystatic.com/example/il_570xN.90001.jpg",
            "url_fullxfull": "https://i.etsystatic.com/example/il_fullxfull.90001.jpg",
            "alt_text": "Speckled white ceramic mug on wooden table",
            "created_timestamp": "2024-01-15T09:35:00"
        },
        {
            "listing_image_id": 90002,
            "listing_id": 1001,
            "shop_id": 29457183,
            "rank": 2,
            "url_75x75": "https://i.etsystatic.com/example/il_75x75.90002.jpg",
            "url_170x135": "https://i.etsystatic.com/example/il_170x135.90002.jpg",
            "url_570xN": "https://i.etsystatic.com/example/il_570xN.90002.jpg",
            "url_fullxfull": "https://i.etsystatic.com/example/il_fullxfull.90002.jpg",
            "alt_text": "Close-up of speckled glaze detail on mug",
            "created_timestamp": "2024-01-15T09:36:00"
        },
        {
            "listing_image_id": 90003,
            "listing_id": 1001,
            "shop_id": 29457183,
            "rank": 3,
            "url_75x75": "https://i.etsystatic.com/example/il_75x75.90003.jpg",
            "url_170x135": "https://i.etsystatic.com/example/il_170x135.90003.jpg",
            "url_570xN": "https://i.etsystatic.com/example/il_570xN.90003.jpg",
            "url_fullxfull": "https://i.etsystatic.com/example/il_fullxfull.90003.jpg",
            "alt_text": "Hand holding speckled white mug filled with coffee",
            "created_timestamp": "2024-01-15T09:37:00"
        }
    ]
}
```

## 20. GET /v3/application/listings/1001/images/90001 (single image)
```json
{
    "type": "listing_image",
    "listing_image": {
        "listing_image_id": 90001,
        "listing_id": 1001,
        "shop_id": 29457183,
        "rank": 1,
        "url_75x75": "https://i.etsystatic.com/example/il_75x75.90001.jpg",
        "url_170x135": "https://i.etsystatic.com/example/il_170x135.90001.jpg",
        "url_570xN": "https://i.etsystatic.com/example/il_570xN.90001.jpg",
        "url_fullxfull": "https://i.etsystatic.com/example/il_fullxfull.90001.jpg",
        "alt_text": "Speckled white ceramic mug on wooden table",
        "created_timestamp": "2024-01-15T09:35:00"
    }
}
```

## 21. GET /v3/application/listings/1001/images/99999 (404)
```json
{"error":"Image 99999 not found for listing 1001"}
HTTP_STATUS: 404```

## 22. DELETE /v3/application/listings/1001/images/90003 (delete image)
```json
{
    "type": "listing_image",
    "deleted": true,
    "listing_image_id": 90003
}
```

## 23. GET /v3/application/shops/29457183/receipts (all receipts)
```json
{
    "type": "receipts",
    "count": 3,
    "total": 15,
    "offset": 0,
    "limit": 3,
    "results": [
        {
            "receipt_id": 2014,
            "shop_id": 29457183,
            "buyer_user_id": 55013,
            "buyer_email": "chris.doyle55@gmail.com",
            "name": "Chris Doyle",
            "address_first_line": "1100 Summit Blvd",
            "address_city": "Atlanta",
            "address_state": "GA",
            "address_zip": "30301",
            "address_country": "US",
            "status": "open",
            "payment_method": "cc",
            "grandtotal": 26.0,
            "subtotal": 26.0,
            "total_shipping_cost": 0.0,
            "total_tax_cost": 0.0,
            "discount_amt": 0.0,
            "gift_message": null,
            "is_gift": false,
            "shipping_carrier": null,
            "tracking_code": null,
            "created_timestamp": "2025-04-25T17:00:00",
            "updated_timestamp": "2025-04-25T17:00:00",
            "shipped_timestamp": null,
            "estimated_delivery": null,
            "transactions": [
                {
                    "transaction_id": 3014,
                    "receipt_id": 2014,
                    "listing_id": 1007,
                    "shop_id": 29457183,
                    "buyer_user_id": 55013,
... (truncated)
```

## 24. GET /v3/application/shops/29457183/receipts?status=paid
```json
{
    "type": "receipts",
    "count": 3,
    "total": 3,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "receipt_id": 2011,
            "shop_id": 29457183,
            "buyer_user_id": 55001,
            "buyer_email": "marissa.chen@email.com",
            "name": "Marissa Chen",
            "address_first_line": "742 Evergreen Terrace",
            "address_city": "San Francisco",
            "address_state": "CA",
            "address_zip": "94102",
            "address_country": "US",
            "status": "paid",
            "payment_method": "cc",
            "grandtotal": 83.99,
            "subtotal": 78.0,
            "total_shipping_cost": 5.99,
            "total_tax_cost": 0.0,
            "discount_amt": 0.0,
            "gift_message": null,
            "is_gift": false,
            "shipping_carrier": null,
            "tracking_code": null,
            "created_timestamp": "2025-04-15T19:30:00",
... (truncated)
```

## 25. GET /v3/application/shops/29457183/receipts?was_shipped=false
```json
{
    "type": "receipts",
    "count": 5,
    "total": 5,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "receipt_id": 2014,
            "shop_id": 29457183,
            "buyer_user_id": 55013,
            "buyer_email": "chris.doyle55@gmail.com",
            "name": "Chris Doyle",
            "address_first_line": "1100 Summit Blvd",
            "address_city": "Atlanta",
            "address_state": "GA",
            "address_zip": "30301",
            "address_country": "US",
            "status": "open",
            "payment_method": "cc",
... (truncated)
```

## 26. GET /v3/application/shops/29457183/receipts?min_created=2025-04-01&max_created=2025-04-30
```json
{
    "type": "receipts",
    "count": 5,
    "total": 5,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "receipt_id": 2014,
            "shop_id": 29457183,
            "buyer_user_id": 55013,
            "buyer_email": "chris.doyle55@gmail.com",
            "name": "Chris Doyle",
            "address_first_line": "1100 Summit Blvd",
            "address_city": "Atlanta",
            "address_state": "GA",
            "address_zip": "30301",
            "address_country": "US",
            "status": "open",
            "payment_method": "cc",
... (truncated)
```

## 27. GET /v3/application/shops/29457183/receipts/2003 (single receipt with transactions)
```json
{
    "type": "receipt",
    "receipt": {
        "receipt_id": 2003,
        "shop_id": 29457183,
        "buyer_user_id": 55003,
        "buyer_email": "katie.yamamoto@outlook.com",
        "name": "Katie Yamamoto",
        "address_first_line": "89 Pine Street",
        "address_city": "Seattle",
        "address_state": "WA",
        "address_zip": "98101",
        "address_country": "US",
        "status": "completed",
        "payment_method": "cc",
        "grandtotal": 70.0,
        "subtotal": 64.0,
        "total_shipping_cost": 5.99,
        "total_tax_cost": 0.0,
        "discount_amt": 0.0,
        "gift_message": "Happy Housewarming! Love Katie",
        "is_gift": true,
        "shipping_carrier": "USPS",
        "tracking_code": "9400111899223100456791",
        "created_timestamp": "2025-02-02T18:30:00",
        "updated_timestamp": "2025-02-14T09:00:00",
        "shipped_timestamp": "2025-02-10T10:30:00",
        "estimated_delivery": "2025-02-14T00:00:00",
        "transactions": [
            {
                "transaction_id": 3003,
                "receipt_id": 2003,
                "listing_id": 1001,
                "shop_id": 29457183,
                "buyer_user_id": 55003,
                "title": "Handmade Ceramic Mug - Speckled White Glaze",
                "quantity": 2,
                "price": 32.0,
                "shipping_cost": 5.99,
                "is_digital": false,
                "variations": "",
                "created_timestamp": "2025-02-02T18:30:00"
            }
        ]
    }
}
```

## 28. GET /v3/application/shops/29457183/receipts/2010 (cancelled order)
```json
{
    "type": "receipt",
    "receipt": {
        "receipt_id": 2010,
        "shop_id": 29457183,
        "buyer_user_id": 55010,
        "buyer_email": "danielle.martinez99@gmail.com",
        "name": "Danielle Martinez",
        "address_first_line": "1234 Elm Street",
        "address_city": "Phoenix",
        "address_state": "AZ",
        "address_zip": "85001",
        "address_country": "US",
        "status": "cancelled",
        "payment_method": "cc",
        "grandtotal": 32.0,
        "subtotal": 32.0,
        "total_shipping_cost": 0.0,
        "total_tax_cost": 0.0,
        "discount_amt": 0.0,
        "gift_message": null,
        "is_gift": false,
        "shipping_carrier": null,
        "tracking_code": null,
        "created_timestamp": "2025-04-10T08:20:00",
        "updated_timestamp": "2025-04-11T09:00:00",
        "shipped_timestamp": null,
        "estimated_delivery": null,
        "transactions": [
            {
                "transaction_id": 3010,
                "receipt_id": 2010,
                "listing_id": 1001,
                "shop_id": 29457183,
                "buyer_user_id": 55010,
                "title": "Handmade Ceramic Mug - Speckled White Glaze",
                "quantity": 1,
                "price": 32.0,
                "shipping_cost": 0.0,
                "is_digital": false,
                "variations": "",
                "created_timestamp": "2025-04-10T08:20:00"
            }
        ]
    }
}
```

## 29. GET /v3/application/shops/29457183/receipts/99999 (404)
```json
{"error":"Receipt 99999 not found"}
HTTP_STATUS: 404```

## 30. PUT /v3/application/shops/29457183/receipts/2007 (mark shipped)
```json
{
    "type": "receipt",
    "receipt": {
        "receipt_id": 2007,
        "shop_id": 29457183,
        "buyer_user_id": 55007,
        "buyer_email": "priya.patel.design@gmail.com",
        "name": "Priya Patel",
        "address_first_line": "2105 Willow Way",
        "address_city": "Nashville",
        "address_state": "TN",
        "address_zip": "37201",
        "address_country": "US",
        "status": "shipped",
        "payment_method": "cc",
        "grandtotal": 48.99,
        "subtotal": 42.0,
        "total_shipping_cost": 5.99,
        "total_tax_cost": 1.0,
        "discount_amt": 0.0,
... (truncated)
```

## 31. GET /v3/application/shops/29457183/receipts/2003/transactions
```json
{
    "type": "transactions",
    "count": 1,
    "results": [
        {
            "transaction_id": 3003,
            "receipt_id": 2003,
            "listing_id": 1001,
            "shop_id": 29457183,
            "buyer_user_id": 55003,
            "title": "Handmade Ceramic Mug - Speckled White Glaze",
            "quantity": 2,
            "price": 32.0,
            "shipping_cost": 5.99,
            "is_digital": false,
            "variations": "",
            "created_timestamp": "2025-02-02T18:30:00"
        }
    ]
}
```

## 32. GET /v3/application/shops/29457183/transactions/3001 (single transaction)
```json
{
    "type": "transaction",
    "transaction": {
        "transaction_id": 3001,
        "receipt_id": 2001,
        "listing_id": 1001,
        "shop_id": 29457183,
        "buyer_user_id": 55001,
        "title": "Handmade Ceramic Mug - Speckled White Glaze",
        "quantity": 1,
        "price": 32.0,
        "shipping_cost": 5.99,
        "is_digital": false,
        "variations": "",
        "created_timestamp": "2025-01-08T14:22:00"
    }
}
```

## 33. GET /v3/application/shops/29457183/transactions/99999 (404)
```json
{"error":"Transaction 99999 not found"}
HTTP_STATUS: 404```

## 34. GET /v3/application/shops/29457183/reviews (all reviews)
```json
{
    "type": "reviews",
    "count": 12,
    "total": 12,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "review_id": 7009,
            "shop_id": 29457183,
            "listing_id": 1006,
            "buyer_user_id": 55009,
            "rating": 5,
            "review": "Perfect size for my kitchen herbs! The drainage works great and the saucers protect my windowsill. The forest green glaze is rich and beautiful. Already planning to buy more for gifts.",
            "language": "en",
            "image_url": "https://i.etsystatic.com/example/review_7009.jpg",
            "created_timestamp": "2025-04-20T16:00:00",
            "updated_timestamp": "2025-04-20T16:00:00"
        },
        {
            "review_id": 7012,
            "shop_id": 29457183,
            "listing_id": 1004,
            "buyer_user_id": 55002,
            "rating": 5,
            "review": "As a coffee nerd I'm picky about pour overs and this one delivers! Great flow rate and it fits perfectly on my favorite mug. The charcoal glaze matches my kitchen perfectly.",
            "language": "en",
            "image_url": null,
            "created_timestamp": "2025-04-10T07:45:00",
            "updated_timestamp": "2025-04-10T07:45:00"
... (truncated)
```

## 35. GET /v3/application/shops/29457183/reviews?min_rating=5
```json
{
    "type": "reviews",
    "count": 3,
    "total": 9,
    "offset": 0,
    "limit": 3,
    "results": [
        {
            "review_id": 7009,
            "shop_id": 29457183,
            "listing_id": 1006,
            "buyer_user_id": 55009,
            "rating": 5,
            "review": "Perfect size for my kitchen herbs! The drainage works great and the saucers protect my windowsill. The forest green glaze is rich and beautiful. Already planning to buy more for gifts.",
            "language": "en",
            "image_url": "https://i.etsystatic.com/example/review_7009.jpg",
            "created_timestamp": "2025-04-20T16:00:00",
            "updated_timestamp": "2025-04-20T16:00:00"
        },
        {
            "review_id": 7012,
            "shop_id": 29457183,
            "listing_id": 1004,
            "buyer_user_id": 55002,
            "rating": 5,
            "review": "As a coffee nerd I'm picky about pour overs and this one delivers! Great flow rate and it fits perfectly on my favorite mug. The charcoal glaze matches my kitchen perfectly.",
            "language": "en",
            "image_url": null,
            "created_timestamp": "2025-04-10T07:45:00",
            "updated_timestamp": "2025-04-10T07:45:00"
... (truncated)
```

## 36. GET /v3/application/listings/1001/reviews (listing-specific reviews)
```json
{
    "type": "reviews",
    "count": 2,
    "total": 2,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "review_id": 7003,
            "shop_id": 29457183,
            "listing_id": 1001,
            "buyer_user_id": 55003,
            "rating": 4,
            "review": "Beautiful mugs! I ordered two as a housewarming gift and they loved them. Giving 4 stars only because one arrived with a tiny chip on the bottom - not visible when using it but I noticed. Seller offered to replace but it really is minor.",
            "language": "en",
            "image_url": null,
            "created_timestamp": "2025-02-18T12:00:00",
            "updated_timestamp": "2025-02-18T12:00:00"
        },
        {
            "review_id": 7001,
            "shop_id": 29457183,
            "listing_id": 1001,
            "buyer_user_id": 55001,
            "rating": 5,
            "review": "Absolutely gorgeous mug! The speckled glaze is even more beautiful in person. It's the perfect size for my morning coffee and feels so nice to hold. Will definitely be ordering more!",
            "language": "en",
            "image_url": null,
            "created_timestamp": "2025-01-20T08:30:00",
            "updated_timestamp": "2025-01-20T08:30:00"
        }
    ]
}
```

## 37. GET /v3/application/listings/1011/reviews (listing with low rating review)
```json
{
    "type": "reviews",
    "count": 1,
    "total": 1,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "review_id": 7010,
            "shop_id": 29457183,
            "listing_id": 1011,
            "buyer_user_id": 55014,
            "rating": 2,
            "review": "The vase arrived with a crack running down one side. I reached out to the seller who was responsive and offered a replacement but I'm disappointed with the original packaging. The texture is beautiful though so I'm hopeful the replacement will arrive safely.",
            "language": "en",
            "image_url": "https://i.etsystatic.com/example/review_7010.jpg",
            "created_timestamp": "2025-04-01T10:30:00",
            "updated_timestamp": "2025-04-01T10:30:00"
        }
    ]
}
```

## 38. GET /v3/application/shops/29457183/shipping-profiles
```json
{
    "type": "shipping_profiles",
    "count": 3,
    "results": [
        {
            "shipping_profile_id": 50001,
            "shop_id": 29457183,
            "title": "Standard Shipping - Small Items",
            "origin_country": "US",
            "origin_postal_code": "97201",
            "processing_min": 5,
            "processing_max": 10,
            "min_delivery_days": 3,
            "max_delivery_days": 5,
            "cost": 5.99,
            "secondary_cost": 3.99
        },
        {
            "shipping_profile_id": 50002,
            "shop_id": 29457183,
            "title": "Standard Shipping - Large/Heavy Items",
            "origin_country": "US",
            "origin_postal_code": "97201",
            "processing_min": 10,
            "processing_max": 21,
            "min_delivery_days": 3,
            "max_delivery_days": 7,
            "cost": 11.99,
            "secondary_cost": 7.99
        },
        {
            "shipping_profile_id": 50003,
            "shop_id": 29457183,
            "title": "Express Shipping - Priority Mail Express",
            "origin_country": "US",
            "origin_postal_code": "97201",
            "processing_min": 5,
            "processing_max": 10,
            "min_delivery_days": 1,
            "max_delivery_days": 2,
            "cost": 24.99,
            "secondary_cost": 18.99
        }
    ]
}
```

## 39. GET /v3/application/shops/29457183/shipping-profiles/50001 (single profile)
```json
{
    "type": "shipping_profile",
    "shipping_profile": {
        "shipping_profile_id": 50001,
        "shop_id": 29457183,
        "title": "Standard Shipping - Small Items",
        "origin_country": "US",
        "origin_postal_code": "97201",
        "processing_min": 5,
        "processing_max": 10,
        "min_delivery_days": 3,
        "max_delivery_days": 5,
        "cost": 5.99,
        "secondary_cost": 3.99
    }
}
```

## 40. GET /v3/application/shops/29457183/shipping-profiles/99999 (404)
```json
{"error":"Shipping profile 99999 not found"}
HTTP_STATUS: 404```

## 41. GET /v3/application/shops/29457183/return-policies
```json
{
    "type": "return_policies",
    "count": 1,
    "results": [
        {
            "return_policy_id": 60001,
            "shop_id": 29457183,
            "accepts_returns": true,
            "accepts_exchanges": true,
            "return_deadline": 30
        }
    ]
}
```

## 42. GET /v3/application/shops/29457183/return-policies/60001
```json
{
    "type": "return_policy",
    "return_policy": {
        "return_policy_id": 60001,
        "shop_id": 29457183,
        "accepts_returns": true,
        "accepts_exchanges": true,
        "return_deadline": 30
    }
}
```

## 43. GET /v3/application/shops/29457183/return-policies/99999 (404)
```json
{"error":"Return policy 99999 not found"}
HTTP_STATUS: 404```

---

## SUMMARY
Total endpoints tested: 43
Test completed: Wed May  6 23:03:58 IST 2026
