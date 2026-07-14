# Pinterest API v5 (Mock) - Full API Test Results

## 1. GET /health (Health check)

```
curl -s -X GET "http://localhost:8005/health"
```

**Status:** 200

```json
{
  "status": "ok"
}
```

---

## 2. GET /v5/user_account (Get user account)

```
curl -s -X GET "http://localhost:8005/v5/user_account"
```

**Status:** 200

```json
{
  "type": "user_account",
  "user_account": {
    "account_type": "BUSINESS",
    "username": "cozynestinteriors",
    "profile_image": "https://i.pinimg.com/avatars/cozynestinteriors_1680000000_150.jpg",
    "website_url": "https://www.cozynestinteriors.com",
    "business_name": "CozyNest Interiors",
    "board_count": 9,
    "pin_count": 127,
    "follower_count": 12043,
    "following_count": 340,
    "monthly_views": 285000,
    "created_at": "2023-03-12T08:15:00"
  }
}
```

---

## 3. GET /v5/user_account/analytics (Get user analytics - all)

```
curl -s -X GET "http://localhost:8005/v5/user_account/analytics"
```

**Status:** 200

```json
{
  "type": "user_analytics",
  "count": 30,
  "results": [
    {
      "date": "2026-03-27",
      "impressions": 8500,
      "saves": 620,
      "pin_clicks": 430,
      "outbound_clicks": 285,
      "profile_visits": 120,
      "follows": 8
    },
    {
      "date": "2026-03-28",
      "impressions": 9200,
      "saves": 680,
      "pin_clicks": 475,
      "outbound_clicks": 310,
      "profile_visits": 135,
      "follows": 12
    },
    {
      "date": "2026-03-29",
      "impressions": 7800,
      "saves": 560,
      "pin_clicks": 395,
      "outbound_clicks": 260,
      "profile_visits": 98,
      "follows": 5
    },
    {
      "date": "2026-03-30",
      "impressions": 8900,
      "saves": 640,
      "pin_clicks": 445,
      "outbound_clicks": 295,
      "profile_visits": 115,
      "follows": 9
    },
    {
      "date": "2026-03-31",
      "impressions": 10200,
      "saves": 750,
      "pin_clicks": 520,
      "outbound_clicks": 350,
      "profile_visits": 155,
      "follows": 15
    },
    {
      "date": "2026-04-01",
      "impressions": 9800,
      "saves": 720,
      "pin_clicks": 500,
      "outbound_clicks": 335,
      "profile_visits": 148,
      "follows": 11
    },
    {
      "date": "2026-04-02",
      "impressions": 10500,
      "saves": 780,
      "pin_clicks": 540,
      "outbound_clicks": 365,
      "profile_visits": 162,
      "follows": 14
    },
    {
      "date": "2026-04-03",
      "impressions": 8600,
      "saves": 610,
      "pin_clicks": 420,
      "outbound_clicks": 280,
      "profile_visits": 108,
      "follows": 7
    },
    {
      "date": "2026-04-04",
      "impressions": 11200,
      "saves": 830,
      "pin_clicks": 575,
      "outbound_clicks": 390,
      "profile_visits": 178,
      "follows": 18
    },
    {
      "date": "2026-04-05",
      "impressions": 10800,
      "saves": 795,
      "pin_clicks": 555,
      "outbound_clicks": 375,
      "profile_visits": 170,
      "follows": 16
    },
    {
      "date": "2026-04-06",
      "impressions": 9100,
      "saves": 650,
      "pin_clicks": 455,
      "outbound_clicks": 300,
      "profile_visits": 125,
      "follows": 10
    },
    {
      "date": "2026-04-07",
      "impressions": 8400,
      "saves": 595,
      "pin_clicks": 410,
      "outbound_clicks": 270,
      "profile_visits": 105,
      "follows": 6
    },
    {
      "date": "2026-04-08",
      "impressions": 9600,
      "saves": 700,
      "pin_clicks": 485,
      "outbound_clicks": 320,
      "profile_visits": 140,
      "follows": 12
    },
    {
      "date": "2026-04-09",
      "impressions": 10100,
      "saves": 740,
      "pin_clicks": 515,
      "outbound_clicks": 345,
      "profile_visits": 152,
      "follows": 13
    },
    {
      "date": "2026-04-10",
      "impressions": 11500,
      "saves": 850,
      "pin_clicks": 590,
      "outbound_clicks": 400,
      "profile_visits": 185,
      "follows": 20
    },
    {
      "date": "2026-04-11",
      "impressions": 10900,
      "saves": 810,
      "pin_clicks": 560,
      "outbound_clicks": 380,
      "profile_visits": 172,
      "follows": 17
    },
    {
      "date": "2026-04-12",
      "impressions": 9300,
      "saves": 670,
      "pin_clicks": 465,
      "outbound_clicks": 310,
      "profile_visits": 130,
      "follows": 9
    },
    {
      "date": "2026-04-13",
      "impressions": 8700,
      "saves": 620,
      "pin_clicks": 430,
      "outbound_clicks": 285,
      "profile_visits": 112,
      "follows": 7
    },
    {
      "date": "2026-04-14",
      "impressions": 9900,
      "saves": 725,
      "pin_clicks": 505,
      "outbound_clicks": 340,
      "profile_visits": 145,
      "follows": 11
    },
    {
      "date": "2026-04-15",
      "impressions": 10400,
      "saves": 770,
      "pin_clicks": 535,
      "outbound_clicks": 360,
      "profile_visits": 160,
      "follows": 14
    },
    {
      "date": "2026-04-16",
      "impressions": 11800,
      "saves": 880,
      "pin_clicks": 610,
      "outbound_clicks": 415,
      "profile_visits": 192,
      "follows": 22
    },
    {
      "date": "2026-04-17",
      "impressions": 11200,
      "saves": 835,
      "pin_clicks": 580,
      "outbound_clicks": 395,
      "profile_visits": 180,
      "follows": 19
    },
    {
      "date": "2026-04-18",
      "impressions": 9500,
      "saves": 690,
      "pin_clicks": 480,
      "outbound_clicks": 315,
      "profile_visits": 138,
      "follows": 10
    },
    {
      "date": "2026-04-19",
      "impressions": 8800,
      "saves": 630,
      "pin_clicks": 440,
      "outbound_clicks": 290,
      "profile_visits": 115,
      "follows": 8
    },
    {
      "date": "2026-04-20",
      "impressions": 10600,
      "saves": 785,
      "pin_clicks": 545,
      "outbound_clicks": 370,
      "profile_visits": 165,
      "follows": 15
    },
    {
      "date": "2026-04-21",
      "impressions": 10200,
      "saves": 750,
      "pin_clicks": 520,
      "outbound_clicks": 350,
      "profile_visits": 155,
      "follows": 13
    },
    {
      "date": "2026-04-22",
      "impressions": 11400,
      "saves": 845,
      "pin_clicks": 585,
      "outbound_clicks": 398,
      "profile_visits": 188,
      "follows": 21
    },
    {
      "date": "2026-04-23",
      "impressions": 10700,
      "saves": 795,
      "pin_clicks": 550,
      "outbound_clicks": 372,
      "profile_visits": 168,
      "follows": 16
    },
    {
      "date": "2026-04-24",
      "impressions": 9400,
      "saves": 680,
      "pin_clicks": 470,
      "outbound_clicks": 312,
      "profile_visits": 132,
      "follows": 9
    },
    {
      "date": "2026-04-25",
      "impressions": 10000,
      "saves": 735,
      "pin_clicks": 510,
      "outbound_clicks": 342,
      "profile_visits": 150,
      "follows": 12
    }
  ]
}
```

---

## 4. GET /v5/user_account/analytics?start_date=2026-04-01&end_date=2026-04-05 (Get user analytics - date range)

```
curl -s -X GET "http://localhost:8005/v5/user_account/analytics?start_date=2026-04-01&end_date=2026-04-05"
```

**Status:** 200

```json
{
  "type": "user_analytics",
  "count": 5,
  "results": [
    {
      "date": "2026-04-01",
      "impressions": 9800,
      "saves": 720,
      "pin_clicks": 500,
      "outbound_clicks": 335,
      "profile_visits": 148,
      "follows": 11
    },
    {
      "date": "2026-04-02",
      "impressions": 10500,
      "saves": 780,
      "pin_clicks": 540,
      "outbound_clicks": 365,
      "profile_visits": 162,
      "follows": 14
    },
    {
      "date": "2026-04-03",
      "impressions": 8600,
      "saves": 610,
      "pin_clicks": 420,
      "outbound_clicks": 280,
      "profile_visits": 108,
      "follows": 7
    },
    {
      "date": "2026-04-04",
      "impressions": 11200,
      "saves": 830,
      "pin_clicks": 575,
      "outbound_clicks": 390,
      "profile_visits": 178,
      "follows": 18
    },
    {
      "date": "2026-04-05",
      "impressions": 10800,
      "saves": 795,
      "pin_clicks": 555,
      "outbound_clicks": 375,
      "profile_visits": 170,
      "follows": 16
    }
  ]
}
```

---

## 5. GET /v5/boards (List all boards)

```
curl -s -X GET "http://localhost:8005/v5/boards"
```

**Status:** 200

```json
{
  "type": "boards",
  "count": 9,
  "total": 9,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "board_id": "board_1009",
      "name": "My Secret Mood Board",
      "description": "Private inspiration board for upcoming content planning",
      "privacy": "SECRET",
      "created_at": "2023-11-20T09:00:00",
      "updated_at": "2026-04-23T11:45:00",
      "pin_count": 5,
      "follower_count": 0,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1008",
      "name": "Budget Friendly Decor",
      "description": "Affordable home decor finds and styling tips that wont break the bank",
      "privacy": "PUBLIC",
      "created_at": "2023-10-05T13:00:00",
      "updated_at": "2026-04-17T15:20:00",
      "pin_count": 10,
      "follower_count": 987,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1007",
      "name": "Small Space Solutions",
      "description": "Smart storage and design ideas for apartments and small homes",
      "privacy": "PUBLIC",
      "created_at": "2023-09-12T10:15:00",
      "updated_at": "2026-04-21T08:00:00",
      "pin_count": 16,
      "follower_count": 1834,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1006",
      "name": "Before & After",
      "description": "Stunning room transformations and renovation reveals",
      "privacy": "PUBLIC",
      "created_at": "2023-08-01T15:45:00",
      "updated_at": "2026-04-19T10:30:00",
      "pin_count": 12,
      "follower_count": 2456,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1005",
      "name": "Holiday Decor",
      "description": "Seasonal and holiday decorating ideas for Christmas Easter Halloween and more",
      "privacy": "PUBLIC",
      "created_at": "2023-07-15T08:00:00",
      "updated_at": "2026-04-10T12:15:00",
      "pin_count": 14,
      "follower_count": 1290,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1004",
      "name": "Color Palettes",
      "description": "Curated color combinations for every room. Paint colors and accent ideas",
      "privacy": "PUBLIC",
      "created_at": "2023-06-20T11:30:00",
      "updated_at": "2026-04-22T16:00:00",
      "pin_count": 20,
      "follower_count": 3201,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1003",
      "name": "Kitchen Makeovers",
      "description": "Kitchen renovation ideas from budget-friendly updates to full remodels",
      "privacy": "PUBLIC",
      "created_at": "2023-05-10T14:00:00",
      "updated_at": "2026-04-15T09:45:00",
      "pin_count": 15,
      "follower_count": 1567,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1002",
      "name": "DIY Weekend Projects",
      "description": "Fun and easy DIY projects you can complete in a weekend. Home improvement made simple!",
      "privacy": "PUBLIC",
      "created_at": "2023-04-02T09:30:00",
      "updated_at": "2026-04-18T11:00:00",
      "pin_count": 18,
      "follower_count": 2103,
      "collaborator_count": 1
    },
    {
      "board_id": "board_1001",
      "name": "Living Room Inspo",
      "description": "Beautiful living room designs and cozy interior inspiration for every style and budget",
      "privacy": "PUBLIC",
      "created_at": "2023-03-15T10:00:00",
      "updated_at": "2026-04-20T14:30:00",
      "pin_count": 22,
      "follower_count": 1845,
      "collaborator_count": 0
    }
  ]
}
```

---

## 6. GET /v5/boards?privacy=PUBLIC (List boards - public only)

```
curl -s -X GET "http://localhost:8005/v5/boards?privacy=PUBLIC"
```

**Status:** 200

```json
{
  "type": "boards",
  "count": 8,
  "total": 8,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "board_id": "board_1008",
      "name": "Budget Friendly Decor",
      "description": "Affordable home decor finds and styling tips that wont break the bank",
      "privacy": "PUBLIC",
      "created_at": "2023-10-05T13:00:00",
      "updated_at": "2026-04-17T15:20:00",
      "pin_count": 10,
      "follower_count": 987,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1007",
      "name": "Small Space Solutions",
      "description": "Smart storage and design ideas for apartments and small homes",
      "privacy": "PUBLIC",
      "created_at": "2023-09-12T10:15:00",
      "updated_at": "2026-04-21T08:00:00",
      "pin_count": 16,
      "follower_count": 1834,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1006",
      "name": "Before & After",
      "description": "Stunning room transformations and renovation reveals",
      "privacy": "PUBLIC",
      "created_at": "2023-08-01T15:45:00",
      "updated_at": "2026-04-19T10:30:00",
      "pin_count": 12,
      "follower_count": 2456,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1005",
      "name": "Holiday Decor",
      "description": "Seasonal and holiday decorating ideas for Christmas Easter Halloween and more",
      "privacy": "PUBLIC",
      "created_at": "2023-07-15T08:00:00",
      "updated_at": "2026-04-10T12:15:00",
      "pin_count": 14,
      "follower_count": 1290,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1004",
      "name": "Color Palettes",
      "description": "Curated color combinations for every room. Paint colors and accent ideas",
      "privacy": "PUBLIC",
      "created_at": "2023-06-20T11:30:00",
      "updated_at": "2026-04-22T16:00:00",
      "pin_count": 20,
      "follower_count": 3201,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1003",
      "name": "Kitchen Makeovers",
      "description": "Kitchen renovation ideas from budget-friendly updates to full remodels",
      "privacy": "PUBLIC",
      "created_at": "2023-05-10T14:00:00",
      "updated_at": "2026-04-15T09:45:00",
      "pin_count": 15,
      "follower_count": 1567,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1002",
      "name": "DIY Weekend Projects",
      "description": "Fun and easy DIY projects you can complete in a weekend. Home improvement made simple!",
      "privacy": "PUBLIC",
      "created_at": "2023-04-02T09:30:00",
      "updated_at": "2026-04-18T11:00:00",
      "pin_count": 18,
      "follower_count": 2103,
      "collaborator_count": 1
    },
    {
      "board_id": "board_1001",
      "name": "Living Room Inspo",
      "description": "Beautiful living room designs and cozy interior inspiration for every style and budget",
      "privacy": "PUBLIC",
      "created_at": "2023-03-15T10:00:00",
      "updated_at": "2026-04-20T14:30:00",
      "pin_count": 22,
      "follower_count": 1845,
      "collaborator_count": 0
    }
  ]
}
```

---

## 7. GET /v5/boards?limit=3&offset=0 (List boards - paginated)

```
curl -s -X GET "http://localhost:8005/v5/boards?limit=3&offset=0"
```

**Status:** 200

```json
{
  "type": "boards",
  "count": 3,
  "total": 9,
  "offset": 0,
  "limit": 3,
  "results": [
    {
      "board_id": "board_1009",
      "name": "My Secret Mood Board",
      "description": "Private inspiration board for upcoming content planning",
      "privacy": "SECRET",
      "created_at": "2023-11-20T09:00:00",
      "updated_at": "2026-04-23T11:45:00",
      "pin_count": 5,
      "follower_count": 0,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1008",
      "name": "Budget Friendly Decor",
      "description": "Affordable home decor finds and styling tips that wont break the bank",
      "privacy": "PUBLIC",
      "created_at": "2023-10-05T13:00:00",
      "updated_at": "2026-04-17T15:20:00",
      "pin_count": 10,
      "follower_count": 987,
      "collaborator_count": 0
    },
    {
      "board_id": "board_1007",
      "name": "Small Space Solutions",
      "description": "Smart storage and design ideas for apartments and small homes",
      "privacy": "PUBLIC",
      "created_at": "2023-09-12T10:15:00",
      "updated_at": "2026-04-21T08:00:00",
      "pin_count": 16,
      "follower_count": 1834,
      "collaborator_count": 0
    }
  ]
}
```

---

## 8. GET /v5/boards/board_1001 (Get board)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_1001"
```

**Status:** 200

```json
{
  "type": "board",
  "board": {
    "board_id": "board_1001",
    "name": "Living Room Inspo",
    "description": "Beautiful living room designs and cozy interior inspiration for every style and budget",
    "privacy": "PUBLIC",
    "created_at": "2023-03-15T10:00:00",
    "updated_at": "2026-04-20T14:30:00",
    "pin_count": 22,
    "follower_count": 1845,
    "collaborator_count": 0
  }
}
```

---

## 9. GET /v5/boards/board_99999 (Get board - 404)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_99999"
```

**Status:** 404

```json
{
  "error": "Board board_99999 not found"
}
```

---

## 10. POST /v5/boards (Create board)

```
curl -s -X POST "http://localhost:8005/v5/boards" -H "Content-Type: application/json" -d '{"name": "Outdoor Living", "description": "Patio ideas", "privacy": "PUBLIC"}'
```

**Status:** 201

```json
{
  "type": "board",
  "board": {
    "board_id": "board_1010",
    "name": "Outdoor Living",
    "description": "Patio ideas",
    "privacy": "PUBLIC",
    "created_at": "2026-05-06T18:43:14",
    "updated_at": "2026-05-06T18:43:14",
    "pin_count": 0,
    "follower_count": 0,
    "collaborator_count": 0
  }
}
```

---

## 11. PATCH /v5/boards/board_1001 (Update board)

```
curl -s -X PATCH "http://localhost:8005/v5/boards/board_1001" -H "Content-Type: application/json" -d '{"description": "Updated description"}'
```

**Status:** 200

```json
{
  "type": "board",
  "board": {
    "board_id": "board_1001",
    "name": "Living Room Inspo",
    "description": "Updated description",
    "privacy": "PUBLIC",
    "created_at": "2023-03-15T10:00:00",
    "updated_at": "2026-05-06T18:43:14",
    "pin_count": 22,
    "follower_count": 1845,
    "collaborator_count": 0
  }
}
```

---

## 12. DELETE /v5/boards/board_1009 (Delete board)

```
curl -s -X DELETE "http://localhost:8005/v5/boards/board_1009"
```

**Status:** 200

```json
{
  "type": "board",
  "deleted": true,
  "board_id": "board_1009"
}
```

---

## 13. GET /v5/boards/board_1001/pins (List board pins)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_1001/pins"
```

**Status:** 200

```json
{
  "type": "pins",
  "count": 4,
  "total": 4,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "pin_id": "pin_3015",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Cozy Reading Nook Ideas for Any Corner",
      "description": "Transform any unused corner into the perfect reading nook. Window seats built-in benches and more. #readingnook #cozyspaces",
      "link": "https://www.cozynestinteriors.com/blog/reading-nook-ideas",
      "media_type": "image",
      "created_at": "2025-05-01T10:00:00",
      "updated_at": "2026-04-25T15:00:00",
      "dominant_color": "#C8B8A4",
      "alt_text": "A window seat reading nook with cushions throw blanket and bookshelf",
      "is_promoted": false,
      "pin_metrics_impressions": 5430,
      "pin_metrics_saves": 389,
      "pin_metrics_clicks": 234
    },
    {
      "pin_id": "pin_3010",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Japandi Interior Design Guide",
      "description": "The ultimate guide to Japandi style - where Japanese minimalism meets Scandinavian functionality. #japandi #interiordesign #minimalism",
      "link": "https://www.cozynestinteriors.com/blog/japandi-guide",
      "media_type": "image",
      "created_at": "2025-03-01T10:00:00",
      "updated_at": "2026-04-15T09:00:00",
      "dominant_color": "#DED5C4",
      "alt_text": "A serene room with low wooden furniture and neutral textiles in Japandi style",
      "is_promoted": false,
      "pin_metrics_impressions": 9870,
      "pin_metrics_saves": 723,
      "pin_metrics_clicks": 456
    },
    {
      "pin_id": "pin_3002",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Mid-Century Modern Accent Chair Styling",
      "description": "How to style a mid-century modern accent chair in any room. Tips for placement and complementary decor. #midcenturymodern #interiordesign",
      "link": "https://www.cozynestinteriors.com/blog/accent-chair-styling",
      "media_type": "image",
      "created_at": "2024-07-02T11:30:00",
      "updated_at": "2026-03-18T10:00:00",
      "dominant_color": "#C4A882",
      "alt_text": "A teal mid-century modern accent chair next to a side table with a plant",
      "is_promoted": false,
      "pin_metrics_impressions": 8920,
      "pin_metrics_saves": 634,
      "pin_metrics_clicks": 412
    },
    {
      "pin_id": "pin_3001",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Scandinavian Living Room with Warm Neutrals",
      "description": "Create a cozy Scandinavian-inspired living room with warm neutral tones and natural textures. #livingroom #scandinavian #homedecor",
      "link": "https://www.cozynestinteriors.com/blog/scandi-living-room",
      "media_type": "image",
      "created_at": "2024-06-15T09:00:00",
      "updated_at": "2026-03-20T14:00:00",
      "dominant_color": "#E8DFD6",
      "alt_text": "A bright Scandinavian living room with beige sofa and wooden accents",
      "is_promoted": false,
      "pin_metrics_impressions": 15230,
      "pin_metrics_saves": 1245,
      "pin_metrics_clicks": 890
    }
  ]
}
```

---

## 14. GET /v5/boards/board_99999/pins (List board pins - 404)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_99999/pins"
```

**Status:** 404

```json
{
  "error": "Board board_99999 not found"
}
```

---

## 15. GET /v5/boards/board_1002/sections (List board sections)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_1002/sections"
```

**Status:** 200

```json
{
  "type": "board_sections",
  "count": 3,
  "results": [
    {
      "section_id": "section_2001",
      "board_id": "board_1002",
      "name": "Woodworking",
      "pin_count": 5
    },
    {
      "section_id": "section_2002",
      "board_id": "board_1002",
      "name": "Painting Projects",
      "pin_count": 4
    },
    {
      "section_id": "section_2003",
      "board_id": "board_1002",
      "name": "Organization Hacks",
      "pin_count": 3
    }
  ]
}
```

---

## 16. GET /v5/boards/board_99999/sections (List board sections - 404)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_99999/sections"
```

**Status:** 404

```json
{
  "error": "Board board_99999 not found"
}
```

---

## 17. POST /v5/boards/board_1002/sections (Create board section)

```
curl -s -X POST "http://localhost:8005/v5/boards/board_1002/sections" -H "Content-Type: application/json" -d '{"name": "Electrical Projects"}'
```

**Status:** 201

```json
{
  "type": "board_section",
  "board_section": {
    "section_id": "section_2012",
    "board_id": "board_1002",
    "name": "Electrical Projects",
    "pin_count": 0
  }
}
```

---

## 18. GET /v5/boards/board_1002/sections/section_2001/pins (List section pins)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_1002/sections/section_2001/pins"
```

**Status:** 200

```json
{
  "type": "pins",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "pin_id": "pin_3003",
      "board_id": "board_1002",
      "board_section_id": "section_2001",
      "title": "DIY Floating Shelves Tutorial",
      "description": "Step-by-step guide to building floating shelves with hidden brackets. Perfect weekend project! #DIY #shelves #woodworking",
      "link": "https://www.cozynestinteriors.com/blog/floating-shelves-diy",
      "media_type": "image",
      "created_at": "2024-08-10T14:00:00",
      "updated_at": "2026-04-01T09:30:00",
      "dominant_color": "#8B6F4E",
      "alt_text": "Hands installing a floating shelf with level tool and drill",
      "is_promoted": false,
      "pin_metrics_impressions": 22450,
      "pin_metrics_saves": 2890,
      "pin_metrics_clicks": 1567
    }
  ]
}
```

---

## 19. GET /v5/boards/board_99999/sections/section_2001/pins (Section pins - 404 board)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_99999/sections/section_2001/pins"
```

**Status:** 404

```json
{
  "error": "Board board_99999 not found"
}
```

---

## 20. GET /v5/boards/board_1002/sections/section_99999/pins (Section pins - 404 section)

```
curl -s -X GET "http://localhost:8005/v5/boards/board_1002/sections/section_99999/pins"
```

**Status:** 404

```json
{
  "error": "Section section_99999 not found in board board_1002"
}
```

---

## 21. GET /v5/pins (List all pins)

```
curl -s -X GET "http://localhost:8005/v5/pins"
```

**Status:** 200

```json
{
  "type": "pins",
  "count": 20,
  "total": 20,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "pin_id": "pin_3016",
      "board_id": "board_1009",
      "board_section_id": null,
      "title": "Content Calendar May 2026",
      "description": "Planning pins for May - focus on outdoor spaces and spring refresh content",
      "link": null,
      "media_type": "image",
      "created_at": "2025-05-02T08:00:00",
      "updated_at": "2026-04-25T08:00:00",
      "dominant_color": "#FFFFFF",
      "alt_text": null,
      "is_promoted": false,
      "pin_metrics_impressions": 0,
      "pin_metrics_saves": 0,
      "pin_metrics_clicks": 0
    },
    {
      "pin_id": "pin_3015",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Cozy Reading Nook Ideas for Any Corner",
      "description": "Transform any unused corner into the perfect reading nook. Window seats built-in benches and more. #readingnook #cozyspaces",
      "link": "https://www.cozynestinteriors.com/blog/reading-nook-ideas",
      "media_type": "image",
      "created_at": "2025-05-01T10:00:00",
      "updated_at": "2026-04-25T15:00:00",
      "dominant_color": "#C8B8A4",
      "alt_text": "A window seat reading nook with cushions throw blanket and bookshelf",
      "is_promoted": false,
      "pin_metrics_impressions": 5430,
      "pin_metrics_saves": 389,
      "pin_metrics_clicks": 234
    },
    {
      "pin_id": "pin_3014",
      "board_id": "board_1002",
      "board_section_id": "section_2003",
      "title": "Pantry Organization System Under $100",
      "description": "Complete pantry makeover using affordable containers from Target and Amazon. Free printable labels included! #pantry #organization #budgetfriendly",
      "link": "https://www.cozynestinteriors.com/blog/pantry-org-budget",
      "media_type": "image",
      "created_at": "2025-04-18T09:15:00",
      "updated_at": "2026-04-23T08:30:00",
      "dominant_color": "#F0E6D3",
      "alt_text": "Neatly organized pantry with clear containers matching labels and baskets",
      "is_promoted": false,
      "pin_metrics_impressions": 28900,
      "pin_metrics_saves": 3200,
      "pin_metrics_clicks": 2100
    },
    {
      "pin_id": "pin_3013",
      "board_id": "board_1006",
      "board_section_id": null,
      "title": "Kitchen Open Shelving Transformation",
      "description": "Removed upper cabinets and installed open shelving. Complete tutorial and styling tips included! #openshelving #kitchenreno #beforeandafter",
      "link": "https://www.cozynestinteriors.com/blog/open-shelving-kitchen",
      "media_type": "video",
      "created_at": "2025-04-10T14:30:00",
      "updated_at": "2026-04-22T11:00:00",
      "dominant_color": "#F5F0EB",
      "alt_text": "Kitchen with styled open wooden shelves showing dishes and plants",
      "is_promoted": false,
      "pin_metrics_impressions": 19200,
      "pin_metrics_saves": 1456,
      "pin_metrics_clicks": 1023
    },
    {
      "pin_id": "pin_3012",
      "board_id": "board_1004",
      "board_section_id": "section_2011",
      "title": "Bold Jewel Tone Living Room Palette",
      "description": "Embrace color with this rich jewel-toned palette. Emerald teal and sapphire create a luxurious living space. #jeweltones #colorpalette #boldcolors",
      "link": "https://www.cozynestinteriors.com/blog/jewel-tone-palette",
      "media_type": "image",
      "created_at": "2025-04-01T08:30:00",
      "updated_at": "2026-04-20T16:45:00",
      "dominant_color": "#1B4332",
      "alt_text": "Three fabric swatches in emerald green teal and deep sapphire blue",
      "is_promoted": false,
      "pin_metrics_impressions": 7650,
      "pin_metrics_saves": 534,
      "pin_metrics_clicks": 312
    },
    {
      "pin_id": "pin_3017",
      "board_id": "board_1007",
      "board_section_id": "section_2009",
      "title": "Closet Organization on a Budget",
      "description": "Maximize your closet space with these affordable organization hacks. No custom systems needed! #closetorganization #smallspace",
      "link": "https://www.cozynestinteriors.com/blog/closet-budget-org",
      "media_type": "image",
      "created_at": "2025-03-20T12:00:00",
      "updated_at": "2026-04-14T10:15:00",
      "dominant_color": "#E8E0D8",
      "alt_text": "A well-organized closet with shelf dividers hanging organizers and labeled bins",
      "is_promoted": false,
      "pin_metrics_impressions": 11200,
      "pin_metrics_saves": 876,
      "pin_metrics_clicks": 543
    },
    {
      "pin_id": "pin_3011",
      "board_id": "board_1002",
      "board_section_id": "section_2002",
      "title": "How to Paint an Accent Wall Like a Pro",
      "description": "Pro tips for getting crisp lines and even coverage on your accent wall. Includes prep and color selection guide. #accentwall #paintingtips #DIY",
      "link": "https://www.cozynestinteriors.com/blog/accent-wall-guide",
      "media_type": "image",
      "created_at": "2025-03-15T11:45:00",
      "updated_at": "2026-04-12T14:20:00",
      "dominant_color": "#6B4E3D",
      "alt_text": "Person taping off an accent wall with blue painters tape and paint roller",
      "is_promoted": false,
      "pin_metrics_impressions": 14500,
      "pin_metrics_saves": 1100,
      "pin_metrics_clicks": 780
    },
    {
      "pin_id": "pin_3010",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Japandi Interior Design Guide",
      "description": "The ultimate guide to Japandi style - where Japanese minimalism meets Scandinavian functionality. #japandi #interiordesign #minimalism",
      "link": "https://www.cozynestinteriors.com/blog/japandi-guide",
      "media_type": "image",
      "created_at": "2025-03-01T10:00:00",
      "updated_at": "2026-04-15T09:00:00",
      "dominant_color": "#DED5C4",
      "alt_text": "A serene room with low wooden furniture and neutral textiles in Japandi style",
      "is_promoted": false,
      "pin_metrics_impressions": 9870,
      "pin_metrics_saves": 723,
      "pin_metrics_clicks": 456
    },
    {
      "pin_id": "pin_3018",
      "board_id": "board_1003",
      "board_section_id": "section_2005",
      "title": "Farmhouse Kitchen Sink Styling Guide",
      "description": "How to style the area around your farmhouse sink. From soap dispensers to cutting boards. #farmhousekitchen #styling",
      "link": "https://www.cozynestinteriors.com/blog/farmhouse-sink-styling",
      "media_type": "image",
      "created_at": "2025-02-28T15:30:00",
      "updated_at": "2026-04-09T13:00:00",
      "dominant_color": "#DED0C0",
      "alt_text": "A white farmhouse sink area with wooden cutting board brass faucet and potted herbs",
      "is_promoted": false,
      "pin_metrics_impressions": 16700,
      "pin_metrics_saves": 1234,
      "pin_metrics_clicks": 867
    },
    {
      "pin_id": "pin_3009",
      "board_id": "board_1008",
      "board_section_id": null,
      "title": "Thrift Store Furniture Flip - Dresser Makeover",
      "description": "Turned a $30 thrift store dresser into a stunning statement piece with chalk paint and new hardware. #thriftflip #furnituremakeover #budgetdecor",
      "link": "https://www.cozynestinteriors.com/blog/dresser-flip",
      "media_type": "image",
      "created_at": "2025-02-14T16:00:00",
      "updated_at": "2026-04-08T10:30:00",
      "dominant_color": "#5B7C6A",
      "alt_text": "Before and after of a painted dresser in sage green with brass knobs",
      "is_promoted": true,
      "pin_metrics_impressions": 67800,
      "pin_metrics_saves": 4120,
      "pin_metrics_clicks": 3890
    },
    {
      "pin_id": "pin_3019",
      "board_id": "board_1008",
      "board_section_id": null,
      "title": "Dollar Store Decor Hacks That Look Expensive",
      "description": "10 amazing decor pieces you can make with dollar store supplies. Nobody will believe these cost $5 or less! #dollarstore #decorhacks #budgetdecor",
      "link": "https://www.cozynestinteriors.com/blog/dollar-store-hacks",
      "media_type": "image",
      "created_at": "2025-01-25T11:00:00",
      "updated_at": "2026-04-06T09:45:00",
      "dominant_color": "#F8F2ED",
      "alt_text": "Collage of four elevated-looking decor items made from dollar store materials",
      "is_promoted": true,
      "pin_metrics_impressions": 43200,
      "pin_metrics_saves": 3567,
      "pin_metrics_clicks": 2890
    },
    {
      "pin_id": "pin_3008",
      "board_id": "board_1007",
      "board_section_id": "section_2008",
      "title": "Small Bathroom Storage Solutions",
      "description": "10 genius storage ideas for tiny bathrooms. Maximize every inch of space! #smallbathroom #storage #organization",
      "link": "https://www.cozynestinteriors.com/blog/small-bath-storage",
      "media_type": "image",
      "created_at": "2025-01-08T09:20:00",
      "updated_at": "2026-04-10T12:00:00",
      "dominant_color": "#B8C5D4",
      "alt_text": "Organized bathroom shelving with matching containers and rolled towels",
      "is_promoted": false,
      "pin_metrics_impressions": 12890,
      "pin_metrics_saves": 987,
      "pin_metrics_clicks": 645
    },
    {
      "pin_id": "pin_3007",
      "board_id": "board_1006",
      "board_section_id": null,
      "title": "Bathroom Renovation Before and After",
      "description": "From dated 1990s bathroom to modern spa-inspired oasis. Full renovation reveal with budget breakdown. #beforeandafter #bathroom",
      "link": "https://www.cozynestinteriors.com/blog/bathroom-reno-reveal",
      "media_type": "video",
      "created_at": "2024-12-20T13:00:00",
      "updated_at": "2026-03-15T14:45:00",
      "dominant_color": "#4A6741",
      "alt_text": "Split image showing old pink tile bathroom and new modern white bathroom",
      "is_promoted": false,
      "pin_metrics_impressions": 52300,
      "pin_metrics_saves": 3890,
      "pin_metrics_clicks": 2450
    },
    {
      "pin_id": "pin_3006",
      "board_id": "board_1005",
      "board_section_id": "section_2006",
      "title": "Minimalist Christmas Mantel Decor",
      "description": "Less is more! Create a stunning minimalist Christmas mantel with greenery and candles. #christmas #minimalist #manteldecor",
      "link": "https://www.cozynestinteriors.com/blog/minimalist-christmas-mantel",
      "media_type": "image",
      "created_at": "2024-11-01T15:30:00",
      "updated_at": "2026-01-10T08:00:00",
      "dominant_color": "#2D5016",
      "alt_text": "A simple fireplace mantel decorated with eucalyptus garland and white candles",
      "is_promoted": false,
      "pin_metrics_impressions": 45600,
      "pin_metrics_saves": 5230,
      "pin_metrics_clicks": 3200
    },
    {
      "pin_id": "pin_3005",
      "board_id": "board_1004",
      "board_section_id": "section_2010",
      "title": "Earthy Neutral Color Palette for Bedrooms",
      "description": "5 earthy neutral color combinations perfect for creating a calming bedroom retreat. Includes paint codes! #colorpalette #bedroom",
      "link": "https://www.cozynestinteriors.com/blog/earthy-palette-bedroom",
      "media_type": "image",
      "created_at": "2024-10-12T08:45:00",
      "updated_at": "2026-04-05T11:20:00",
      "dominant_color": "#C9B99A",
      "alt_text": "Color swatches showing five neutral earth tone combinations",
      "is_promoted": false,
      "pin_metrics_impressions": 31200,
      "pin_metrics_saves": 4521,
      "pin_metrics_clicks": 2100
    },
    {
      "pin_id": "pin_3020",
      "board_id": "board_1005",
      "board_section_id": "section_2007",
      "title": "Spooky Chic Halloween Porch Decor",
      "description": "Elegant Halloween decorating that is spooky but still stylish. Black white and gold theme. #halloween #porchdecor #spookychic",
      "link": "https://www.cozynestinteriors.com/blog/halloween-porch",
      "media_type": "image",
      "created_at": "2024-09-28T14:00:00",
      "updated_at": "2025-11-01T08:00:00",
      "dominant_color": "#1A1A1A",
      "alt_text": "A front porch decorated with black and gold pumpkins white mums and elegant lanterns",
      "is_promoted": false,
      "pin_metrics_impressions": 35400,
      "pin_metrics_saves": 2780,
      "pin_metrics_clicks": 1890
    },
    {
      "pin_id": "pin_3004",
      "board_id": "board_1003",
      "board_section_id": "section_2004",
      "title": "White Kitchen with Gold Hardware Refresh",
      "description": "Transform your kitchen with a simple hardware swap. Gold pulls and knobs on white cabinets for an instant upgrade. #kitchenmakeover #gold",
      "link": "https://www.cozynestinteriors.com/blog/gold-hardware-refresh",
      "media_type": "image",
      "created_at": "2024-09-05T10:15:00",
      "updated_at": "2026-03-25T16:00:00",
      "dominant_color": "#FFFFFF",
      "alt_text": "Close-up of white kitchen cabinets with brushed gold handles",
      "is_promoted": false,
      "pin_metrics_impressions": 18760,
      "pin_metrics_saves": 1567,
      "pin_metrics_clicks": 923
    },
    {
      "pin_id": "pin_3003",
      "board_id": "board_1002",
      "board_section_id": "section_2001",
      "title": "DIY Floating Shelves Tutorial",
      "description": "Step-by-step guide to building floating shelves with hidden brackets. Perfect weekend project! #DIY #shelves #woodworking",
      "link": "https://www.cozynestinteriors.com/blog/floating-shelves-diy",
      "media_type": "image",
      "created_at": "2024-08-10T14:00:00",
      "updated_at": "2026-04-01T09:30:00",
      "dominant_color": "#8B6F4E",
      "alt_text": "Hands installing a floating shelf with level tool and drill",
      "is_promoted": false,
      "pin_metrics_impressions": 22450,
      "pin_metrics_saves": 2890,
      "pin_metrics_clicks": 1567
    },
    {
      "pin_id": "pin_3002",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Mid-Century Modern Accent Chair Styling",
      "description": "How to style a mid-century modern accent chair in any room. Tips for placement and complementary decor. #midcenturymodern #interiordesign",
      "link": "https://www.cozynestinteriors.com/blog/accent-chair-styling",
      "media_type": "image",
      "created_at": "2024-07-02T11:30:00",
      "updated_at": "2026-03-18T10:00:00",
      "dominant_color": "#C4A882",
      "alt_text": "A teal mid-century modern accent chair next to a side table with a plant",
      "is_promoted": false,
      "pin_metrics_impressions": 8920,
      "pin_metrics_saves": 634,
      "pin_metrics_clicks": 412
    },
    {
      "pin_id": "pin_3001",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Scandinavian Living Room with Warm Neutrals",
      "description": "Create a cozy Scandinavian-inspired living room with warm neutral tones and natural textures. #livingroom #scandinavian #homedecor",
      "link": "https://www.cozynestinteriors.com/blog/scandi-living-room",
      "media_type": "image",
      "created_at": "2024-06-15T09:00:00",
      "updated_at": "2026-03-20T14:00:00",
      "dominant_color": "#E8DFD6",
      "alt_text": "A bright Scandinavian living room with beige sofa and wooden accents",
      "is_promoted": false,
      "pin_metrics_impressions": 15230,
      "pin_metrics_saves": 1245,
      "pin_metrics_clicks": 890
    }
  ]
}
```

---

## 22. GET /v5/pins?limit=5&offset=0 (List pins - paginated)

```
curl -s -X GET "http://localhost:8005/v5/pins?limit=5&offset=0"
```

**Status:** 200

```json
{
  "type": "pins",
  "count": 5,
  "total": 20,
  "offset": 0,
  "limit": 5,
  "results": [
    {
      "pin_id": "pin_3016",
      "board_id": "board_1009",
      "board_section_id": null,
      "title": "Content Calendar May 2026",
      "description": "Planning pins for May - focus on outdoor spaces and spring refresh content",
      "link": null,
      "media_type": "image",
      "created_at": "2025-05-02T08:00:00",
      "updated_at": "2026-04-25T08:00:00",
      "dominant_color": "#FFFFFF",
      "alt_text": null,
      "is_promoted": false,
      "pin_metrics_impressions": 0,
      "pin_metrics_saves": 0,
      "pin_metrics_clicks": 0
    },
    {
      "pin_id": "pin_3015",
      "board_id": "board_1001",
      "board_section_id": null,
      "title": "Cozy Reading Nook Ideas for Any Corner",
      "description": "Transform any unused corner into the perfect reading nook. Window seats built-in benches and more. #readingnook #cozyspaces",
      "link": "https://www.cozynestinteriors.com/blog/reading-nook-ideas",
      "media_type": "image",
      "created_at": "2025-05-01T10:00:00",
      "updated_at": "2026-04-25T15:00:00",
      "dominant_color": "#C8B8A4",
      "alt_text": "A window seat reading nook with cushions throw blanket and bookshelf",
      "is_promoted": false,
      "pin_metrics_impressions": 5430,
      "pin_metrics_saves": 389,
      "pin_metrics_clicks": 234
    },
    {
      "pin_id": "pin_3014",
      "board_id": "board_1002",
      "board_section_id": "section_2003",
      "title": "Pantry Organization System Under $100",
      "description": "Complete pantry makeover using affordable containers from Target and Amazon. Free printable labels included! #pantry #organization #budgetfriendly",
      "link": "https://www.cozynestinteriors.com/blog/pantry-org-budget",
      "media_type": "image",
      "created_at": "2025-04-18T09:15:00",
      "updated_at": "2026-04-23T08:30:00",
      "dominant_color": "#F0E6D3",
      "alt_text": "Neatly organized pantry with clear containers matching labels and baskets",
      "is_promoted": false,
      "pin_metrics_impressions": 28900,
      "pin_metrics_saves": 3200,
      "pin_metrics_clicks": 2100
    },
    {
      "pin_id": "pin_3013",
      "board_id": "board_1006",
      "board_section_id": null,
      "title": "Kitchen Open Shelving Transformation",
      "description": "Removed upper cabinets and installed open shelving. Complete tutorial and styling tips included! #openshelving #kitchenreno #beforeandafter",
      "link": "https://www.cozynestinteriors.com/blog/open-shelving-kitchen",
      "media_type": "video",
      "created_at": "2025-04-10T14:30:00",
      "updated_at": "2026-04-22T11:00:00",
      "dominant_color": "#F5F0EB",
      "alt_text": "Kitchen with styled open wooden shelves showing dishes and plants",
      "is_promoted": false,
      "pin_metrics_impressions": 19200,
      "pin_metrics_saves": 1456,
      "pin_metrics_clicks": 1023
    },
    {
      "pin_id": "pin_3012",
      "board_id": "board_1004",
      "board_section_id": "section_2011",
      "title": "Bold Jewel Tone Living Room Palette",
      "description": "Embrace color with this rich jewel-toned palette. Emerald teal and sapphire create a luxurious living space. #jeweltones #colorpalette #boldcolors",
      "link": "https://www.cozynestinteriors.com/blog/jewel-tone-palette",
      "media_type": "image",
      "created_at": "2025-04-01T08:30:00",
      "updated_at": "2026-04-20T16:45:00",
      "dominant_color": "#1B4332",
      "alt_text": "Three fabric swatches in emerald green teal and deep sapphire blue",
      "is_promoted": false,
      "pin_metrics_impressions": 7650,
      "pin_metrics_saves": 534,
      "pin_metrics_clicks": 312
    }
  ]
}
```

---

## 23. GET /v5/pins/pin_3001 (Get pin)

```
curl -s -X GET "http://localhost:8005/v5/pins/pin_3001"
```

**Status:** 200

```json
{
  "type": "pin",
  "pin": {
    "pin_id": "pin_3001",
    "board_id": "board_1001",
    "board_section_id": null,
    "title": "Scandinavian Living Room with Warm Neutrals",
    "description": "Create a cozy Scandinavian-inspired living room with warm neutral tones and natural textures. #livingroom #scandinavian #homedecor",
    "link": "https://www.cozynestinteriors.com/blog/scandi-living-room",
    "media_type": "image",
    "created_at": "2024-06-15T09:00:00",
    "updated_at": "2026-03-20T14:00:00",
    "dominant_color": "#E8DFD6",
    "alt_text": "A bright Scandinavian living room with beige sofa and wooden accents",
    "is_promoted": false,
    "pin_metrics_impressions": 15230,
    "pin_metrics_saves": 1245,
    "pin_metrics_clicks": 890
  }
}
```

---

## 24. GET /v5/pins/pin_99999 (Get pin - 404)

```
curl -s -X GET "http://localhost:8005/v5/pins/pin_99999"
```

**Status:** 404

```json
{
  "error": "Pin pin_99999 not found"
}
```

---

## 25. POST /v5/pins (Create pin)

```
curl -s -X POST "http://localhost:8005/v5/pins" -H "Content-Type: application/json" -d '{"board_id": "board_1001", "title": "Boho Makeover", "description": "Boho tips", "link": "https://example.com", "media_type": "image", "alt_text": "Boho room"}'
```

**Status:** 201

```json
{
  "type": "pin",
  "pin": {
    "pin_id": "pin_3021",
    "board_id": "board_1001",
    "board_section_id": null,
    "title": "Boho Makeover",
    "description": "Boho tips",
    "link": "https://example.com",
    "media_type": "image",
    "created_at": "2026-05-06T18:43:14",
    "updated_at": "2026-05-06T18:43:14",
    "dominant_color": null,
    "alt_text": "Boho room",
    "is_promoted": false,
    "pin_metrics_impressions": 0,
    "pin_metrics_saves": 0,
    "pin_metrics_clicks": 0
  }
}
```

---

## 26. PATCH /v5/pins/pin_3001 (Update pin)

```
curl -s -X PATCH "http://localhost:8005/v5/pins/pin_3001" -H "Content-Type: application/json" -d '{"title": "Updated Scandi Guide", "description": "Updated 2026"}'
```

**Status:** 200

```json
{
  "type": "pin",
  "pin": {
    "pin_id": "pin_3001",
    "board_id": "board_1001",
    "board_section_id": null,
    "title": "Updated Scandi Guide",
    "description": "Updated 2026",
    "link": "https://www.cozynestinteriors.com/blog/scandi-living-room",
    "media_type": "image",
    "created_at": "2024-06-15T09:00:00",
    "updated_at": "2026-05-06T18:43:14",
    "dominant_color": "#E8DFD6",
    "alt_text": "A bright Scandinavian living room with beige sofa and wooden accents",
    "is_promoted": false,
    "pin_metrics_impressions": 15230,
    "pin_metrics_saves": 1245,
    "pin_metrics_clicks": 890
  }
}
```

---

## 27. DELETE /v5/pins/pin_3016 (Delete pin)

```
curl -s -X DELETE "http://localhost:8005/v5/pins/pin_3016"
```

**Status:** 200

```json
{
  "type": "pin",
  "deleted": true,
  "pin_id": "pin_3016"
}
```

---

## 28. DELETE /v5/pins/pin_99999 (Delete pin - 404)

```
curl -s -X DELETE "http://localhost:8005/v5/pins/pin_99999"
```

**Status:** 404

```json
{
  "error": "Pin pin_99999 not found"
}
```

---

## 29. GET /v5/pins/pin_3001/analytics (Get pin analytics)

```
curl -s -X GET "http://localhost:8005/v5/pins/pin_3001/analytics"
```

**Status:** 200

```json
{
  "type": "pin_analytics",
  "count": 5,
  "pin_id": "pin_3001",
  "results": [
    {
      "pin_id": "pin_3001",
      "date": "2026-04-01",
      "impressions": 520,
      "saves": 42,
      "pin_clicks": 30,
      "outbound_clicks": 18
    },
    {
      "pin_id": "pin_3001",
      "date": "2026-04-02",
      "impressions": 485,
      "saves": 38,
      "pin_clicks": 28,
      "outbound_clicks": 15
    },
    {
      "pin_id": "pin_3001",
      "date": "2026-04-03",
      "impressions": 612,
      "saves": 51,
      "pin_clicks": 35,
      "outbound_clicks": 22
    },
    {
      "pin_id": "pin_3001",
      "date": "2026-04-04",
      "impressions": 498,
      "saves": 40,
      "pin_clicks": 25,
      "outbound_clicks": 14
    },
    {
      "pin_id": "pin_3001",
      "date": "2026-04-05",
      "impressions": 534,
      "saves": 45,
      "pin_clicks": 32,
      "outbound_clicks": 20
    }
  ]
}
```

---

## 30. GET /v5/pins/pin_3005/analytics?start_date=2026-04-01&end_date=2026-04-03 (Pin analytics - date range)

```
curl -s -X GET "http://localhost:8005/v5/pins/pin_3005/analytics?start_date=2026-04-01&end_date=2026-04-03"
```

**Status:** 200

```json
{
  "type": "pin_analytics",
  "count": 3,
  "pin_id": "pin_3005",
  "results": [
    {
      "pin_id": "pin_3005",
      "date": "2026-04-01",
      "impressions": 1050,
      "saves": 150,
      "pin_clicks": 72,
      "outbound_clicks": 45
    },
    {
      "pin_id": "pin_3005",
      "date": "2026-04-02",
      "impressions": 1120,
      "saves": 162,
      "pin_clicks": 80,
      "outbound_clicks": 52
    },
    {
      "pin_id": "pin_3005",
      "date": "2026-04-03",
      "impressions": 980,
      "saves": 140,
      "pin_clicks": 68,
      "outbound_clicks": 40
    }
  ]
}
```

---

## 31. GET /v5/pins/pin_99999/analytics (Pin analytics - 404)

```
curl -s -X GET "http://localhost:8005/v5/pins/pin_99999/analytics"
```

**Status:** 404

```json
{
  "error": "Pin pin_99999 not found"
}
```

---

## 32. GET /v5/search/pins?query=DIY (Search pins - DIY)

```
curl -s -X GET "http://localhost:8005/v5/search/pins?query=DIY"
```

**Status:** 200

```json
{
  "type": "pins",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "pin_id": "pin_3011",
      "board_id": "board_1002",
      "board_section_id": "section_2002",
      "title": "How to Paint an Accent Wall Like a Pro",
      "description": "Pro tips for getting crisp lines and even coverage on your accent wall. Includes prep and color selection guide. #accentwall #paintingtips #DIY",
      "link": "https://www.cozynestinteriors.com/blog/accent-wall-guide",
      "media_type": "image",
      "created_at": "2025-03-15T11:45:00",
      "updated_at": "2026-04-12T14:20:00",
      "dominant_color": "#6B4E3D",
      "alt_text": "Person taping off an accent wall with blue painters tape and paint roller",
      "is_promoted": false,
      "pin_metrics_impressions": 14500,
      "pin_metrics_saves": 1100,
      "pin_metrics_clicks": 780
    },
    {
      "pin_id": "pin_3003",
      "board_id": "board_1002",
      "board_section_id": "section_2001",
      "title": "DIY Floating Shelves Tutorial",
      "description": "Step-by-step guide to building floating shelves with hidden brackets. Perfect weekend project! #DIY #shelves #woodworking",
      "link": "https://www.cozynestinteriors.com/blog/floating-shelves-diy",
      "media_type": "image",
      "created_at": "2024-08-10T14:00:00",
      "updated_at": "2026-04-01T09:30:00",
      "dominant_color": "#8B6F4E",
      "alt_text": "Hands installing a floating shelf with level tool and drill",
      "is_promoted": false,
      "pin_metrics_impressions": 22450,
      "pin_metrics_saves": 2890,
      "pin_metrics_clicks": 1567
    }
  ]
}
```

---

## 33. GET /v5/search/pins?query=kitchen (Search pins - kitchen)

```
curl -s -X GET "http://localhost:8005/v5/search/pins?query=kitchen"
```

**Status:** 200

```json
{
  "type": "pins",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "pin_id": "pin_3013",
      "board_id": "board_1006",
      "board_section_id": null,
      "title": "Kitchen Open Shelving Transformation",
      "description": "Removed upper cabinets and installed open shelving. Complete tutorial and styling tips included! #openshelving #kitchenreno #beforeandafter",
      "link": "https://www.cozynestinteriors.com/blog/open-shelving-kitchen",
      "media_type": "video",
      "created_at": "2025-04-10T14:30:00",
      "updated_at": "2026-04-22T11:00:00",
      "dominant_color": "#F5F0EB",
      "alt_text": "Kitchen with styled open wooden shelves showing dishes and plants",
      "is_promoted": false,
      "pin_metrics_impressions": 19200,
      "pin_metrics_saves": 1456,
      "pin_metrics_clicks": 1023
    },
    {
      "pin_id": "pin_3018",
      "board_id": "board_1003",
      "board_section_id": "section_2005",
      "title": "Farmhouse Kitchen Sink Styling Guide",
      "description": "How to style the area around your farmhouse sink. From soap dispensers to cutting boards. #farmhousekitchen #styling",
      "link": "https://www.cozynestinteriors.com/blog/farmhouse-sink-styling",
      "media_type": "image",
      "created_at": "2025-02-28T15:30:00",
      "updated_at": "2026-04-09T13:00:00",
      "dominant_color": "#DED0C0",
      "alt_text": "A white farmhouse sink area with wooden cutting board brass faucet and potted herbs",
      "is_promoted": false,
      "pin_metrics_impressions": 16700,
      "pin_metrics_saves": 1234,
      "pin_metrics_clicks": 867
    },
    {
      "pin_id": "pin_3004",
      "board_id": "board_1003",
      "board_section_id": "section_2004",
      "title": "White Kitchen with Gold Hardware Refresh",
      "description": "Transform your kitchen with a simple hardware swap. Gold pulls and knobs on white cabinets for an instant upgrade. #kitchenmakeover #gold",
      "link": "https://www.cozynestinteriors.com/blog/gold-hardware-refresh",
      "media_type": "image",
      "created_at": "2024-09-05T10:15:00",
      "updated_at": "2026-03-25T16:00:00",
      "dominant_color": "#FFFFFF",
      "alt_text": "Close-up of white kitchen cabinets with brushed gold handles",
      "is_promoted": false,
      "pin_metrics_impressions": 18760,
      "pin_metrics_saves": 1567,
      "pin_metrics_clicks": 923
    }
  ]
}
```

---

## 34. GET /v5/search/pins?query=xyznonexistent (Search pins - no results)

```
curl -s -X GET "http://localhost:8005/v5/search/pins?query=xyznonexistent"
```

**Status:** 200

```json
{
  "type": "pins",
  "count": 0,
  "total": 0,
  "offset": 0,
  "limit": 25,
  "results": []
}
```

---

## 35. GET /v5/media/pin_3001 (Get media status)

```
curl -s -X GET "http://localhost:8005/v5/media/pin_3001"
```

**Status:** 200

```json
{
  "type": "media_upload",
  "media_id": "pin_3001",
  "status": "succeeded",
  "media_type": "image"
}
```

---

## 36. GET /v5/media/media_99999 (Get media status - 404)

```
curl -s -X GET "http://localhost:8005/v5/media/media_99999"
```

**Status:** 404

```json
{
  "error": "Media media_99999 not found"
}
```

---

## 37. GET /v5/ad_accounts (List ad accounts)

```
curl -s -X GET "http://localhost:8005/v5/ad_accounts"
```

**Status:** 200

```json
{
  "type": "ad_accounts",
  "count": 1,
  "total": 1,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "ad_account_id": "ad_acct_7001",
      "name": "CozyNest Interiors Ads",
      "currency": "USD",
      "country": "US",
      "status": "ACTIVE",
      "created_at": "2024-01-10T09:00:00"
    }
  ]
}
```

---

## 38. GET /v5/ad_accounts/ad_acct_7001 (Get ad account)

```
curl -s -X GET "http://localhost:8005/v5/ad_accounts/ad_acct_7001"
```

**Status:** 200

```json
{
  "type": "ad_account",
  "ad_account": {
    "ad_account_id": "ad_acct_7001",
    "name": "CozyNest Interiors Ads",
    "currency": "USD",
    "country": "US",
    "status": "ACTIVE",
    "created_at": "2024-01-10T09:00:00"
  }
}
```

---

## 39. GET /v5/ad_accounts/ad_acct_99999 (Get ad account - 404)

```
curl -s -X GET "http://localhost:8005/v5/ad_accounts/ad_acct_99999"
```

**Status:** 404

```json
{
  "error": "Ad account ad_acct_99999 not found"
}
```

---

## 40. GET /v5/ad_accounts/ad_acct_7001/campaigns (List campaigns)

```
curl -s -X GET "http://localhost:8005/v5/ad_accounts/ad_acct_7001/campaigns"
```

**Status:** 200

```json
{
  "type": "campaigns",
  "count": 3,
  "total": 3,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "campaign_id": "camp_8001",
      "ad_account_id": "ad_acct_7001",
      "name": "Spring Home Refresh 2026",
      "status": "ACTIVE",
      "objective_type": "TRAFFIC",
      "daily_spend_cap_micro": 5000000,
      "lifetime_spend_cap_micro": 150000000,
      "start_time": "2026-03-01T00:00:00",
      "end_time": "2026-05-31T23:59:59",
      "created_at": "2026-02-20T10:00:00",
      "updated_at": "2026-04-15T08:30:00"
    },
    {
      "campaign_id": "camp_8002",
      "ad_account_id": "ad_acct_7001",
      "name": "DIY Content Boost Q2",
      "status": "ACTIVE",
      "objective_type": "AWARENESS",
      "daily_spend_cap_micro": 3000000,
      "lifetime_spend_cap_micro": 90000000,
      "start_time": "2026-04-01T00:00:00",
      "end_time": "2026-06-30T23:59:59",
      "created_at": "2026-03-25T14:00:00",
      "updated_at": "2026-04-20T11:00:00"
    },
    {
      "campaign_id": "camp_8003",
      "ad_account_id": "ad_acct_7001",
      "name": "Budget Decor Holiday Push",
      "status": "PAUSED",
      "objective_type": "TRAFFIC",
      "daily_spend_cap_micro": 8000000,
      "lifetime_spend_cap_micro": 200000000,
      "start_time": "2025-11-01T00:00:00",
      "end_time": "2025-12-31T23:59:59",
      "created_at": "2025-10-15T09:00:00",
      "updated_at": "2025-12-31T23:59:59"
    }
  ]
}
```

---

## 41. GET /v5/ad_accounts/ad_acct_7001/campaigns?status=ACTIVE (List campaigns - active)

```
curl -s -X GET "http://localhost:8005/v5/ad_accounts/ad_acct_7001/campaigns?status=ACTIVE"
```

**Status:** 200

```json
{
  "type": "campaigns",
  "count": 2,
  "total": 2,
  "offset": 0,
  "limit": 25,
  "results": [
    {
      "campaign_id": "camp_8001",
      "ad_account_id": "ad_acct_7001",
      "name": "Spring Home Refresh 2026",
      "status": "ACTIVE",
      "objective_type": "TRAFFIC",
      "daily_spend_cap_micro": 5000000,
      "lifetime_spend_cap_micro": 150000000,
      "start_time": "2026-03-01T00:00:00",
      "end_time": "2026-05-31T23:59:59",
      "created_at": "2026-02-20T10:00:00",
      "updated_at": "2026-04-15T08:30:00"
    },
    {
      "campaign_id": "camp_8002",
      "ad_account_id": "ad_acct_7001",
      "name": "DIY Content Boost Q2",
      "status": "ACTIVE",
      "objective_type": "AWARENESS",
      "daily_spend_cap_micro": 3000000,
      "lifetime_spend_cap_micro": 90000000,
      "start_time": "2026-04-01T00:00:00",
      "end_time": "2026-06-30T23:59:59",
      "created_at": "2026-03-25T14:00:00",
      "updated_at": "2026-04-20T11:00:00"
    }
  ]
}
```

---

## 42. GET /v5/ad_accounts/ad_acct_99999/campaigns (List campaigns - 404)

```
curl -s -X GET "http://localhost:8005/v5/ad_accounts/ad_acct_99999/campaigns"
```

**Status:** 404

```json
{
  "error": "Ad account ad_acct_99999 not found"
}
```

---

