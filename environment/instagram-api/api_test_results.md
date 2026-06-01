# Instagram Graph API (Mock) - Full API Test Results

**Total Endpoints Tested:** 65
**Server:** `uvicorn server:app --port 8007`
**Date:** 2026-05-07

---

## 1. GET /health (Health check)

**Command:**
```
curl -s http://localhost:8007/health
```

**Status:** 200

**Response:**
```json
{
  "status": "ok"
}
```

---

## 2. GET /17841400123456789 (Get user profile)

**Command:**
```
curl -s http://localhost:8007/17841400123456789
```

**Status:** 200

**Response:**
```json
{
  "id": "17841400123456789",
  "username": "brewedawakening_",
  "name": "Brewed Awakening ☕",
  "biography": "Specialty coffee roasters & cafe 🌿 Portland, OR\nSingle-origin beans • Latte art • Brewing tutorials\nOnline shop ⬇️ Fresh roasts shipped weekly",
  "website": "https://brewedawakening.co",
  "followers_count": 28500,
  "follows_count": 890,
  "media_count": 847,
  "profile_picture_url": "https://instagram.mock/profiles/brewedawakening_/avatar_hd.jpg",
  "ig_id": 5214783690,
  "account_type": "BUSINESS",
  "category": "Coffee Shop"
}
```

---

## 3. GET /17841400123456789?fields=id,username,name,followers_count,media_count (Get user - fields filter)

**Command:**
```
curl -s http://localhost:8007/17841400123456789?fields=id,username,name,followers_count,media_count
```

**Status:** 200

**Response:**
```json
{
  "id": "17841400123456789",
  "username": "brewedawakening_",
  "name": "Brewed Awakening ☕",
  "followers_count": 28500,
  "media_count": 847
}
```

---

## 4. GET /99999999 (Get user - 404)

**Command:**
```
curl -s http://localhost:8007/99999999
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "User 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 5. GET /17841400123456789/media (List user media (all))

**Command:**
```
curl -s http://localhost:8007/17841400123456789/media
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17900001001",
      "user_id": "17841400123456789",
      "caption": "Sunday morning pour-over ritual \\u2615\\n\\nOur new Ethiopian Yirgacheffe is giving us bright citrus notes with a silky body. Limited batch \\u2014 grab yours before it\\u2019s gone!\\n\\n#specialtycoffee #pourovercoffee #ethiopiancoffee #yirgacheffe #coffeeroasters #portland #pdxcoffee",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001001.jpg",
      "permalink": "https://instagram.mock/p/BA1cD2eF3g/",
      "thumbnail_url": null,
      "timestamp": "2026-05-04T07:15:00",
      "like_count": 487,
      "comments_count": 24,
      "is_comment_enabled": true
    },
    {
      "id": "17900001002",
      "user_id": "17841400123456789",
      "caption": "The rosetta that made us stop everything \\ud83c\\udf39\\n\\nOur barista @maria_pours has been perfecting her technique for months and THIS is the result. Creamy oat milk + our house espresso blend = pure art.\\n\\nWho wants to learn? Free latte art workshop this Saturday! Link in bio \\u2b06\\ufe0f\\n\\n#latteart #rosetta #oatmilklatte #baristalife #coffeeart #portland #lattearttutorial",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001002.jpg",
      "permalink": "https://instagram.mock/p/CB2dE3fG4h/",
      "thumbnail_url": null,
      "timestamp": "2026-05-02T12:30:00",
      "like_count": 5234,
      "comments_count": 187,
      "is_comment_enabled": true
    },
    {
      "id": "17900001003",
      "user_id": "17841400123456789",
      "caption": "NEW ARRIVAL \\ud83d\\udce6\\u2728\\n\\nJust landed: Guatemala Huehuetenango from Finca El Injerto. Notes of dark chocolate, toasted almond, and red grape. Washed process, roasted medium.\\n\\nAvailable in:\\n\\u2022 12oz whole bean ($22)\\n\\u2022 5lb wholesale ($85)\\n\\nShop link in bio or visit us in-store!\\n\\n#guatemalancoffee #singleorigin #newbeans #coffeeroasters #specialtycoffee #fincaelinjerto",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001003.jpg",
      "permalink": "https://instagram.mock/p/DC3eF4gH5i/",
      "thumbnail_url": null,
      "timestamp": "2026-04-30T17:00:00",
      "like_count": 612,
      "comments_count": 31,
      "is_comment_enabled": true
    },
    {
      "id": "17900001004",
      "user_id": "17841400123456789",
      "caption": "Behind the scenes at our roastery \\ud83d\\udd25\\n\\nWatch the full process from green bean to your morning cup. This batch of Colombian Supremo is hitting 2nd crack at exactly the right moment.\\n\\nFull video on our YouTube (link in bio)\\n\\n#coffeeroasting #roastery #behindthescenes #colombiancoffee #smallbatchcoffee #artisanroasting",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/media/17900001004.mp4",
      "permalink": "https://instagram.mock/p/ED4fG5hI6j/",
      "thumbnail_url": "https://instagram.mock/media/17900001004_thumb.jpg",
  
  ... (truncated)
```

---

## 6. GET /17841400123456789/media?limit=5 (List user media - limit=5)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/media?limit=5
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17900001001",
      "user_id": "17841400123456789",
      "caption": "Sunday morning pour-over ritual \\u2615\\n\\nOur new Ethiopian Yirgacheffe is giving us bright citrus notes with a silky body. Limited batch \\u2014 grab yours before it\\u2019s gone!\\n\\n#specialtycoffee #pourovercoffee #ethiopiancoffee #yirgacheffe #coffeeroasters #portland #pdxcoffee",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001001.jpg",
      "permalink": "https://instagram.mock/p/BA1cD2eF3g/",
      "thumbnail_url": null,
      "timestamp": "2026-05-04T07:15:00",
      "like_count": 487,
      "comments_count": 24,
      "is_comment_enabled": true
    },
    {
      "id": "17900001002",
      "user_id": "17841400123456789",
      "caption": "The rosetta that made us stop everything \\ud83c\\udf39\\n\\nOur barista @maria_pours has been perfecting her technique for months and THIS is the result. Creamy oat milk + our house espresso blend = pure art.\\n\\nWho wants to learn? Free latte art workshop this Saturday! Link in bio \\u2b06\\ufe0f\\n\\n#latteart #rosetta #oatmilklatte #baristalife #coffeeart #portland #lattearttutorial",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001002.jpg",
      "permalink": "https://instagram.mock/p/CB2dE3fG4h/",
      "thumbnail_url": null,
      "timestamp": "2026-05-02T12:30:00",
      "like_count": 5234,
      "comments_count": 187,
      "is_comment_enabled": true
    },
    {
      "id": "17900001003",
      "user_id": "17841400123456789",
      "caption": "NEW ARRIVAL \\ud83d\\udce6\\u2728\\n\\nJust landed: Guatemala Huehuetenango from Finca El Injerto. Notes of dark chocolate, toasted almond, and red grape. Washed process, roasted medium.\\n\\nAvailable in:\\n\\u2022 12oz whole bean ($22)\\n\\u2022 5lb wholesale ($85)\\n\\nShop link in bio or visit us in-store!\\n\\n#guatemalancoffee #singleorigin #newbeans #coffeeroasters #specialtycoffee #fincaelinjerto",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001003.jpg",
      "permalink": "https://instagram.mock/p/DC3eF4gH5i/",
      "thumbnail_url": null,
      "timestamp": "2026-04-30T17:00:00",
      "like_count": 612,
      "comments_count": 31,
      "is_comment_enabled": true
    },
    {
      "id": "17900001004",
      "user_id": "17841400123456789",
      "caption": "Behind the scenes at our roastery \\ud83d\\udd25\\n\\nWatch the full process from green bean to your morning cup. This batch of Colombian Supremo is hitting 2nd crack at exactly the right moment.\\n\\nFull video on our YouTube (link in bio)\\n\\n#coffeeroasting #roastery #behindthescenes #colombiancoffee #smallbatchcoffee #artisanroasting",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/media/17900001004.mp4",
      "permalink": "https://instagram.mock/p/ED4fG5hI6j/",
      "thumbnail_url": "https://instagram.mock/media/17900001004_thumb.jpg",
  
  ... (truncated)
```

---

## 7. GET /17841400123456789/media?media_type=VIDEO (List user media - VIDEO only)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/media?media_type=VIDEO
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17900001004",
      "user_id": "17841400123456789",
      "caption": "Behind the scenes at our roastery \\ud83d\\udd25\\n\\nWatch the full process from green bean to your morning cup. This batch of Colombian Supremo is hitting 2nd crack at exactly the right moment.\\n\\nFull video on our YouTube (link in bio)\\n\\n#coffeeroasting #roastery #behindthescenes #colombiancoffee #smallbatchcoffee #artisanroasting",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/media/17900001004.mp4",
      "permalink": "https://instagram.mock/p/ED4fG5hI6j/",
      "thumbnail_url": "https://instagram.mock/media/17900001004_thumb.jpg",
      "timestamp": "2026-04-28T09:00:00",
      "like_count": 1823,
      "comments_count": 56,
      "is_comment_enabled": true
    },
    {
      "id": "17900001008",
      "user_id": "17841400123456789",
      "caption": "The perfect V60 in 3 minutes \\u23f1\\ufe0f\\n\\nRecipe:\\n\\u2022 18g medium-fine grind\\n\\u2022 300ml water at 96\\u00b0C\\n\\u2022 30s bloom with 50ml\\n\\u2022 Slow spiral pour to 300ml\\n\\u2022 Total brew time: 2:45-3:00\\n\\nSave this for later! \\ud83d\\udd16\\n\\n#v60 #brewguide #cofferecipe #pourovercoffee #hario #homebrewing #coffeetutorial",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/media/17900001008.mp4",
      "permalink": "https://instagram.mock/p/IH8jK9lM0n/",
      "thumbnail_url": "https://instagram.mock/media/17900001008_thumb.jpg",
      "timestamp": "2026-04-19T08:00:00",
      "like_count": 4102,
      "comments_count": 163,
      "is_comment_enabled": true
    },
    {
      "id": "17900001014",
      "user_id": "17841400123456789",
      "caption": "How we dial in espresso every morning \\u2699\\ufe0f\\n\\nIt\\u2019s not just about the grind. Watch our head barista @jake_brews walk through the full process:\\n\\n1. Weigh dose (18.5g)\\n2. Distribute & tamp\\n3. Pull shot (target 36g in 28s)\\n4. Taste & adjust\\n\\nWe do this EVERY morning before opening. Consistency is everything.\\n\\n#espresso #dialingin #baristatraining #coffeeeducation #qualitycontrol",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/media/17900001014.mp4",
      "permalink": "https://instagram.mock/p/ON4pQ5rS6t/",
      "thumbnail_url": "https://instagram.mock/media/17900001014_thumb.jpg",
      "timestamp": "2026-04-07T06:30:00",
      "like_count": 3456,
      "comments_count": 121,
      "is_comment_enabled": true
    },
    {
      "id": "17900001024",
      "user_id": "17841400123456789",
      "caption": "POV: You ordered our house cold brew on a warm Portland afternoon \\u2600\\ufe0f\\n\\n20-hour steep. Smooth as butter. Zero bitterness.\\n\\nPro tip: Try it with a splash of our house-made vanilla oat creamer.\\n\\n#coldbrew #pov #summervibes #portlandsun #icedcoffee #smoothcoffee",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/media/17900001024.mp4",
      "permalink": "https:/
  ... (truncated)
```

---

## 8. GET /17841400123456789/media?media_type=CAROUSEL_ALBUM (List user media - CAROUSEL only)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/media?media_type=CAROUSEL_ALBUM
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17900001005",
      "user_id": "17841400123456789",
      "caption": "Our cafe through the seasons \\ud83c\\udf42\\u2744\\ufe0f\\ud83c\\udf38\\u2600\\ufe0f\\n\\nSwipe to see how our corner spot transforms throughout the year. Which vibe is your favorite?\\n\\n1. Autumn leaves + pumpkin spice\\n2. Cozy winter with fairy lights\\n3. Spring blooms on the patio\\n4. Summer golden hour\\n\\n#cafedecor #portlandcafe #coffeeshopvibes #interiordesign #cozyvibes",
      "media_type": "CAROUSEL_ALBUM",
      "media_url": "https://instagram.mock/media/17900001005_1.jpg",
      "permalink": "https://instagram.mock/p/FE5gH6iJ7k/",
      "thumbnail_url": null,
      "timestamp": "2026-04-25T18:30:00",
      "like_count": 3891,
      "comments_count": 142,
      "is_comment_enabled": true
    },
    {
      "id": "17900001007",
      "user_id": "17841400123456789",
      "caption": "COLLAB ALERT \\ud83c\\udfa8\\u2615\\n\\nWe\\u2019ve teamed up with local potter @clay_and_kiln to create these limited edition ceramic pour-over drippers. Handmade right here in Portland.\\n\\nOnly 50 made. Each one unique. Available Saturday at 10am in-store and online.\\n\\n#portlandmakers #collaboration #ceramics #pourover #localartists #handmade #limitededition",
      "media_type": "CAROUSEL_ALBUM",
      "media_url": "https://instagram.mock/media/17900001007_1.jpg",
      "permalink": "https://instagram.mock/p/HG7iJ8kL9m/",
      "thumbnail_url": null,
      "timestamp": "2026-04-21T12:00:00",
      "like_count": 2456,
      "comments_count": 98,
      "is_comment_enabled": true
    },
    {
      "id": "17900001011",
      "user_id": "17841400123456789",
      "caption": "Cupping session notes \\ud83d\\udcdd\\n\\nToday we\\u2019re evaluating 6 new samples from our importing partners. Swipe for our score cards!\\n\\nTop performer: Kenya AA Nyeri \\u2014 blackcurrant, brown sugar, juicy acidity. Coming to our menu next month.\\n\\n#cupping #coffeetasting #qualitycontrol #kenyacoffee #greenbuying #specialty",
      "media_type": "CAROUSEL_ALBUM",
      "media_url": "https://instagram.mock/media/17900001011_1.jpg",
      "permalink": "https://instagram.mock/p/LK1mN2oP3q/",
      "thumbnail_url": null,
      "timestamp": "2026-04-13T14:00:00",
      "like_count": 1567,
      "comments_count": 73,
      "is_comment_enabled": true
    },
    {
      "id": "17900001018",
      "user_id": "17841400123456789",
      "caption": "March recap \\ud83d\\udcc8\\n\\nWhat a month! Here\\u2019s what happened:\\n\\u2022 Launched 3 new single origins\\n\\u2022 Hosted our first cupping class (sold out!)\\n\\u2022 Hit 28K followers \\ud83c\\udf89\\n\\u2022 @jake_brews won the NW Barista Jam\\n\\u2022 Started our compost program \\ud83c\\udf31\\n\\nApril is looking even better. Stay tuned!\\n\\n#monthlyrecap #smallbusiness #growth #coffeebusiness #milestones",
      "media_type": "CAROUSEL_ALBUM",
      "media_url": "https://instagram.mock/media/17900001018_1.jpg",
 
  ... (truncated)
```

---

## 9. GET /17841400123456789/media?fields=id,caption,media_type,like_count,timestamp (List user media - fields filter)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/media?fields=id,caption,media_type,like_count,timestamp
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17900001001",
      "caption": "Sunday morning pour-over ritual \\u2615\\n\\nOur new Ethiopian Yirgacheffe is giving us bright citrus notes with a silky body. Limited batch \\u2014 grab yours before it\\u2019s gone!\\n\\n#specialtycoffee #pourovercoffee #ethiopiancoffee #yirgacheffe #coffeeroasters #portland #pdxcoffee",
      "media_type": "IMAGE",
      "timestamp": "2026-05-04T07:15:00",
      "like_count": 487
    },
    {
      "id": "17900001002",
      "caption": "The rosetta that made us stop everything \\ud83c\\udf39\\n\\nOur barista @maria_pours has been perfecting her technique for months and THIS is the result. Creamy oat milk + our house espresso blend = pure art.\\n\\nWho wants to learn? Free latte art workshop this Saturday! Link in bio \\u2b06\\ufe0f\\n\\n#latteart #rosetta #oatmilklatte #baristalife #coffeeart #portland #lattearttutorial",
      "media_type": "IMAGE",
      "timestamp": "2026-05-02T12:30:00",
      "like_count": 5234
    },
    {
      "id": "17900001003",
      "caption": "NEW ARRIVAL \\ud83d\\udce6\\u2728\\n\\nJust landed: Guatemala Huehuetenango from Finca El Injerto. Notes of dark chocolate, toasted almond, and red grape. Washed process, roasted medium.\\n\\nAvailable in:\\n\\u2022 12oz whole bean ($22)\\n\\u2022 5lb wholesale ($85)\\n\\nShop link in bio or visit us in-store!\\n\\n#guatemalancoffee #singleorigin #newbeans #coffeeroasters #specialtycoffee #fincaelinjerto",
      "media_type": "IMAGE",
      "timestamp": "2026-04-30T17:00:00",
      "like_count": 612
    },
    {
      "id": "17900001004",
      "caption": "Behind the scenes at our roastery \\ud83d\\udd25\\n\\nWatch the full process from green bean to your morning cup. This batch of Colombian Supremo is hitting 2nd crack at exactly the right moment.\\n\\nFull video on our YouTube (link in bio)\\n\\n#coffeeroasting #roastery #behindthescenes #colombiancoffee #smallbatchcoffee #artisanroasting",
      "media_type": "VIDEO",
      "timestamp": "2026-04-28T09:00:00",
      "like_count": 1823
    },
    {
      "id": "17900001005",
      "caption": "Our cafe through the seasons \\ud83c\\udf42\\u2744\\ufe0f\\ud83c\\udf38\\u2600\\ufe0f\\n\\nSwipe to see how our corner spot transforms throughout the year. Which vibe is your favorite?\\n\\n1. Autumn leaves + pumpkin spice\\n2. Cozy winter with fairy lights\\n3. Spring blooms on the patio\\n4. Summer golden hour\\n\\n#cafedecor #portlandcafe #coffeeshopvibes #interiordesign #cozyvibes",
      "media_type": "CAROUSEL_ALBUM",
      "timestamp": "2026-04-25T18:30:00",
      "like_count": 3891
    },
    {
      "id": "17900001006",
      "caption": "Morning light hits different here \\u2728\\n\\nOpen daily 6am-6pm. Come find your corner.\\n\\n#morningcoffee #cafelife #portlandmornings #goldenhour #coffeeshop",
      "media_type": "IMAGE",
      "timestamp": "2026-04-23T06:45:00",
      "like_count": 892
    },
    {
      "id": "17900001007",
      "caption": "COLLAB ALERT \
  ... (truncated)
```

---

## 10. GET /17841400123456789/media?limit=3&offset=5 (List user media - pagination)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/media?limit=3&offset=5
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17900001006",
      "user_id": "17841400123456789",
      "caption": "Morning light hits different here \\u2728\\n\\nOpen daily 6am-6pm. Come find your corner.\\n\\n#morningcoffee #cafelife #portlandmornings #goldenhour #coffeeshop",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001006.jpg",
      "permalink": "https://instagram.mock/p/GF6hI7jK8l/",
      "thumbnail_url": null,
      "timestamp": "2026-04-23T06:45:00",
      "like_count": 892,
      "comments_count": 18,
      "is_comment_enabled": true
    },
    {
      "id": "17900001007",
      "user_id": "17841400123456789",
      "caption": "COLLAB ALERT \\ud83c\\udfa8\\u2615\\n\\nWe\\u2019ve teamed up with local potter @clay_and_kiln to create these limited edition ceramic pour-over drippers. Handmade right here in Portland.\\n\\nOnly 50 made. Each one unique. Available Saturday at 10am in-store and online.\\n\\n#portlandmakers #collaboration #ceramics #pourover #localartists #handmade #limitededition",
      "media_type": "CAROUSEL_ALBUM",
      "media_url": "https://instagram.mock/media/17900001007_1.jpg",
      "permalink": "https://instagram.mock/p/HG7iJ8kL9m/",
      "thumbnail_url": null,
      "timestamp": "2026-04-21T12:00:00",
      "like_count": 2456,
      "comments_count": 98,
      "is_comment_enabled": true
    },
    {
      "id": "17900001008",
      "user_id": "17841400123456789",
      "caption": "The perfect V60 in 3 minutes \\u23f1\\ufe0f\\n\\nRecipe:\\n\\u2022 18g medium-fine grind\\n\\u2022 300ml water at 96\\u00b0C\\n\\u2022 30s bloom with 50ml\\n\\u2022 Slow spiral pour to 300ml\\n\\u2022 Total brew time: 2:45-3:00\\n\\nSave this for later! \\ud83d\\udd16\\n\\n#v60 #brewguide #cofferecipe #pourovercoffee #hario #homebrewing #coffeetutorial",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/media/17900001008.mp4",
      "permalink": "https://instagram.mock/p/IH8jK9lM0n/",
      "thumbnail_url": "https://instagram.mock/media/17900001008_thumb.jpg",
      "timestamp": "2026-04-19T08:00:00",
      "like_count": 4102,
      "comments_count": 163,
      "is_comment_enabled": true
    }
  ],
  "paging": {
    "cursors": {
      "after": "17900001008",
      "before": "17900001006"
    },
    "next": "https://graph.instagram.mock/17841400123456789/media?limit=3&after=17900001008"
  }
}
```

---

## 11. GET /media/17900001002 (Get media - viral latte art post)

**Command:**
```
curl -s http://localhost:8007/media/17900001002
```

**Status:** 200

**Response:**
```json
{
  "id": "17900001002",
  "user_id": "17841400123456789",
  "caption": "The rosetta that made us stop everything \\ud83c\\udf39\\n\\nOur barista @maria_pours has been perfecting her technique for months and THIS is the result. Creamy oat milk + our house espresso blend = pure art.\\n\\nWho wants to learn? Free latte art workshop this Saturday! Link in bio \\u2b06\\ufe0f\\n\\n#latteart #rosetta #oatmilklatte #baristalife #coffeeart #portland #lattearttutorial",
  "media_type": "IMAGE",
  "media_url": "https://instagram.mock/media/17900001002.jpg",
  "permalink": "https://instagram.mock/p/CB2dE3fG4h/",
  "thumbnail_url": null,
  "timestamp": "2026-05-02T12:30:00",
  "like_count": 5234,
  "comments_count": 187,
  "is_comment_enabled": true
}
```

---

## 12. GET /media/17900001002?fields=id,caption,like_count (Get media - fields filter)

**Command:**
```
curl -s http://localhost:8007/media/17900001002?fields=id,caption,like_count
```

**Status:** 200

**Response:**
```json
{
  "id": "17900001002",
  "caption": "The rosetta that made us stop everything \\ud83c\\udf39\\n\\nOur barista @maria_pours has been perfecting her technique for months and THIS is the result. Creamy oat milk + our house espresso blend = pure art.\\n\\nWho wants to learn? Free latte art workshop this Saturday! Link in bio \\u2b06\\ufe0f\\n\\n#latteart #rosetta #oatmilklatte #baristalife #coffeeart #portland #lattearttutorial",
  "like_count": 5234
}
```

---

## 13. GET /media/99999999 (Get media - 404)

**Command:**
```
curl -s http://localhost:8007/media/99999999
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 14. GET /media/17900001005/children (Get carousel children)

**Command:**
```
curl -s http://localhost:8007/media/17900001005/children
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17860001001",
      "media_id": "17900001005",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_1.jpg",
      "timestamp": "2026-04-25T18:30:00"
    },
    {
      "id": "17860001002",
      "media_id": "17900001005",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_2.jpg",
      "timestamp": "2026-04-25T18:30:00"
    },
    {
      "id": "17860001003",
      "media_id": "17900001005",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_3.jpg",
      "timestamp": "2026-04-25T18:30:00"
    },
    {
      "id": "17860001004",
      "media_id": "17900001005",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_4.jpg",
      "timestamp": "2026-04-25T18:30:00"
    }
  ]
}
```

---

## 15. GET /media/17900001005/children?fields=id,media_type,media_url (Get carousel children - fields)

**Command:**
```
curl -s http://localhost:8007/media/17900001005/children?fields=id,media_type,media_url
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17860001001",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_1.jpg"
    },
    {
      "id": "17860001002",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_2.jpg"
    },
    {
      "id": "17860001003",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_3.jpg"
    },
    {
      "id": "17860001004",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001005_4.jpg"
    }
  ]
}
```

---

## 16. GET /media/17900001001/children (Get children - non-carousel error)

**Command:**
```
curl -s http://localhost:8007/media/17900001001/children
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Media 17900001001 is not a carousel album",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 17. GET /media/99999999/children (Get children - media 404)

**Command:**
```
curl -s http://localhost:8007/media/99999999/children
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 18. GET /media/17900001002/comments (List comments on viral post)

**Command:**
```
curl -s http://localhost:8007/media/17900001002/comments
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17800001007",
      "media_id": "17900001002",
      "user_id": "17841400999005",
      "username": "maria_pours",
      "text": "Ahh thank you for posting this!! Still can\\u2019t believe I nailed it \\ud83e\\udd29",
      "timestamp": "2026-05-02T16:00:00",
      "like_count": 23,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001005",
      "media_id": "17900001002",
      "user_id": "17841400123456789",
      "username": "brewedawakening_",
      "text": "@coffeenerd_pdx We use Oatly Barista Edition! It steams beautifully \\ud83d\\udc4c",
      "timestamp": "2026-05-02T14:30:00",
      "like_count": 9,
      "hidden": false,
      "parent_id": "17800001004"
    },
    {
      "id": "17800001004",
      "media_id": "17900001002",
      "user_id": "17841400999003",
      "username": "coffeenerd_pdx",
      "text": "The symmetry is insane. What milk are you using?",
      "timestamp": "2026-05-02T14:00:00",
      "like_count": 6,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001003",
      "media_id": "17900001002",
      "user_id": "17841400999002",
      "username": "portland_foodie",
      "text": "Best latte art in Portland, hands down \\ud83d\\ude4c",
      "timestamp": "2026-05-02T13:15:00",
      "like_count": 15,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001002",
      "media_id": "17900001002",
      "user_id": "17841400123456789",
      "username": "brewedawakening_",
      "text": "@latteart_lover Thank you! Maria has been practicing for about 8 months. Come to our workshop Saturday!",
      "timestamp": "2026-05-02T13:00:00",
      "like_count": 8,
      "hidden": false,
      "parent_id": "17800001001"
    },
    {
      "id": "17800001001",
      "media_id": "17900001002",
      "user_id": "17841400999001",
      "username": "latteart_lover",
      "text": "OMG this is STUNNING! How long did it take to learn this? \\ud83d\\ude0d",
      "timestamp": "2026-05-02T12:45:00",
      "like_count": 12,
      "hidden": false,
      "parent_id": null
    }
  ],
  "paging": {}
}
```

---

## 19. GET /media/17900001002/comments?limit=3 (List comments - limit=3)

**Command:**
```
curl -s http://localhost:8007/media/17900001002/comments?limit=3
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17800001007",
      "media_id": "17900001002",
      "user_id": "17841400999005",
      "username": "maria_pours",
      "text": "Ahh thank you for posting this!! Still can\\u2019t believe I nailed it \\ud83e\\udd29",
      "timestamp": "2026-05-02T16:00:00",
      "like_count": 23,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001005",
      "media_id": "17900001002",
      "user_id": "17841400123456789",
      "username": "brewedawakening_",
      "text": "@coffeenerd_pdx We use Oatly Barista Edition! It steams beautifully \\ud83d\\udc4c",
      "timestamp": "2026-05-02T14:30:00",
      "like_count": 9,
      "hidden": false,
      "parent_id": "17800001004"
    },
    {
      "id": "17800001004",
      "media_id": "17900001002",
      "user_id": "17841400999003",
      "username": "coffeenerd_pdx",
      "text": "The symmetry is insane. What milk are you using?",
      "timestamp": "2026-05-02T14:00:00",
      "like_count": 6,
      "hidden": false,
      "parent_id": null
    }
  ],
  "paging": {
    "cursors": {
      "after": "17800001004"
    }
  }
}
```

---

## 20. GET /media/17900001017/comments (List comments on tulip post)

**Command:**
```
curl -s http://localhost:8007/media/17900001017/comments
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17800001027",
      "media_id": "17900001017",
      "user_id": "17841400999020",
      "username": "wannabe_barista",
      "text": "I\\u2019ve been trying for weeks and mine looks like a blob \\ud83d\\ude02 teach me your ways!",
      "timestamp": "2026-04-01T12:00:00",
      "like_count": 11,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001026",
      "media_id": "17900001017",
      "user_id": "17841400999019",
      "username": "coffee_art_daily",
      "text": "How many layers? This is insane detail!",
      "timestamp": "2026-04-01T10:00:00",
      "like_count": 5,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001025",
      "media_id": "17900001017",
      "user_id": "17841400123456789",
      "username": "brewedawakening_",
      "text": "@barista_magazine Absolutely! We\\u2019d be honored \\ud83d\\ude4f",
      "timestamp": "2026-04-01T09:30:00",
      "like_count": 14,
      "hidden": false,
      "parent_id": "17800001024"
    },
    {
      "id": "17800001024",
      "media_id": "17900001017",
      "user_id": "17841400999018",
      "username": "barista_magazine",
      "text": "Mind if we share this on our page? Full credit of course!",
      "timestamp": "2026-04-01T09:00:00",
      "like_count": 19,
      "hidden": false,
      "parent_id": null
    },
    {
      "id": "17800001023",
      "media_id": "17900001017",
      "user_id": "17841400999017",
      "username": "latte_art_world",
      "text": "This might be the most perfect tulip I\\u2019ve ever seen on IG \\ud83c\\udf37\\ud83d\\ude4c",
      "timestamp": "2026-04-01T08:30:00",
      "like_count": 28,
      "hidden": false,
      "parent_id": null
    }
  ],
  "paging": {}
}
```

---

## 21. GET /media/99999999/comments (List comments - media 404)

**Command:**
```
curl -s http://localhost:8007/media/99999999/comments
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 22. GET /comment/17800001001 (Get single comment)

**Command:**
```
curl -s http://localhost:8007/comment/17800001001
```

**Status:** 200

**Response:**
```json
{
  "id": "17800001001",
  "media_id": "17900001002",
  "user_id": "17841400999001",
  "username": "latteart_lover",
  "text": "OMG this is STUNNING! How long did it take to learn this? \\ud83d\\ude0d",
  "timestamp": "2026-05-02T12:45:00",
  "like_count": 12,
  "hidden": false,
  "parent_id": null
}
```

---

## 23. GET /comment/17800001001?fields=id,text,username (Get comment - fields)

**Command:**
```
curl -s http://localhost:8007/comment/17800001001?fields=id,text,username
```

**Status:** 200

**Response:**
```json
{
  "id": "17800001001",
  "username": "latteart_lover",
  "text": "OMG this is STUNNING! How long did it take to learn this? \\ud83d\\ude0d"
}
```

---

## 24. GET /comment/99999999 (Get comment - 404)

**Command:**
```
curl -s http://localhost:8007/comment/99999999
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Comment 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 25. GET /comment/17800001001/replies (Get comment replies)

**Command:**
```
curl -s http://localhost:8007/comment/17800001001/replies
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17800001002",
      "media_id": "17900001002",
      "user_id": "17841400123456789",
      "username": "brewedawakening_",
      "text": "@latteart_lover Thank you! Maria has been practicing for about 8 months. Come to our workshop Saturday!",
      "timestamp": "2026-05-02T13:00:00",
      "like_count": 8,
      "hidden": false,
      "parent_id": "17800001001"
    }
  ],
  "paging": {}
}
```

---

## 26. GET /comment/17800001004/replies (Get comment replies (has reply))

**Command:**
```
curl -s http://localhost:8007/comment/17800001004/replies
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17800001005",
      "media_id": "17900001002",
      "user_id": "17841400123456789",
      "username": "brewedawakening_",
      "text": "@coffeenerd_pdx We use Oatly Barista Edition! It steams beautifully \\ud83d\\udc4c",
      "timestamp": "2026-05-02T14:30:00",
      "like_count": 9,
      "hidden": false,
      "parent_id": "17800001004"
    }
  ],
  "paging": {}
}
```

---

## 27. POST /media/17900001002/comments (Create comment reply)

**Command:**
```
curl -s -X POST -H 'Content-Type: application/json' -d '{"message": "Great post! Love the latte art!", "parent_id": "17800001003"}' http://localhost:8007/media/17900001002/comments
```

**Status:** 201

**Response:**
```json
{
  "id": "17800001051",
  "media_id": "17900001002",
  "user_id": "17841400123456789",
  "username": "brewedawakening_",
  "text": "Great post! Love the latte art!",
  "timestamp": "2026-05-06T18:43:22+0000",
  "like_count": 0,
  "hidden": false,
  "parent_id": "17800001003"
}
```

---

## 28. POST /media/17900001001/comments (Create top-level comment)

**Command:**
```
curl -s -X POST -H 'Content-Type: application/json' -d '{"message": "Fresh beans are amazing!"}' http://localhost:8007/media/17900001001/comments
```

**Status:** 201

**Response:**
```json
{
  "id": "17800001052",
  "media_id": "17900001001",
  "user_id": "17841400123456789",
  "username": "brewedawakening_",
  "text": "Fresh beans are amazing!",
  "timestamp": "2026-05-06T18:43:22+0000",
  "like_count": 0,
  "hidden": false,
  "parent_id": null
}
```

---

## 29. DELETE /media/17900001002/comments/17800001006 (Delete spam comment)

**Command:**
```
curl -s -X DELETE http://localhost:8007/media/17900001002/comments/17800001006
```

**Status:** 200

**Response:**
```json
{
  "success": true
}
```

---

## 30. DELETE /media/17900001002/comments/99999999 (Delete comment - 404)

**Command:**
```
curl -s -X DELETE http://localhost:8007/media/17900001002/comments/99999999
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Comment 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 31. PUT /media/17900001002/comments/17800001003/hide (Hide comment)

**Command:**
```
curl -s -X PUT -H 'Content-Type: application/json' -d '{"hide": true}' http://localhost:8007/media/17900001002/comments/17800001003/hide
```

**Status:** 200

**Response:**
```json
{
  "success": true
}
```

---

## 32. PUT /media/17900001002/comments/17800001003/hide (Unhide comment)

**Command:**
```
curl -s -X PUT -H 'Content-Type: application/json' -d '{"hide": false}' http://localhost:8007/media/17900001002/comments/17800001003/hide
```

**Status:** 200

**Response:**
```json
{
  "success": true
}
```

---

## 33. GET /17841400123456789/stories (List user stories)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/stories
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17950001007",
      "user_id": "17841400123456789",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/stories/17950001007.jpg",
      "timestamp": "2026-05-06T06:30:00",
      "expiring_at": "2026-05-07T06:30:00",
      "caption": "Good morning Portland! Doors open in 30 mins \\ud83d\\udeaa",
      "link": null,
      "poll_question": null,
      "poll_options": null
    },
    {
      "id": "17950001006",
      "user_id": "17841400123456789",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/stories/17950001006.mp4",
      "timestamp": "2026-05-05T17:30:00",
      "expiring_at": "2026-05-06T17:30:00",
      "caption": "Golden hour at the shop \\u2728 Open til 6!",
      "link": null,
      "poll_question": null,
      "poll_options": null
    },
    {
      "id": "17950001005",
      "user_id": "17841400123456789",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/stories/17950001005.jpg",
      "timestamp": "2026-05-05T16:00:00",
      "expiring_at": "2026-05-06T16:00:00",
      "caption": "What\\u2019s your go-to afternoon pick-me-up?",
      "link": null,
      "poll_question": "Afternoon order?",
      "poll_options": [
        "Espresso shot",
        "Iced latte",
        "Cold brew",
        "Matcha"
      ]
    },
    {
      "id": "17950001004",
      "user_id": "17841400123456789",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/stories/17950001004.jpg",
      "timestamp": "2026-05-05T14:30:00",
      "expiring_at": "2026-05-06T14:30:00",
      "caption": "NEW: Fresh batch of Guatemala Huehuetenango just finished cooling \\ud83c\\udf1f",
      "link": "https://brewedawakening.co/shop/guatemala-huehuetenango",
      "poll_question": null,
      "poll_options": null
    },
    {
      "id": "17950001003",
      "user_id": "17841400123456789",
      "media_type": "VIDEO",
      "media_url": "https://instagram.mock/stories/17950001003.mp4",
      "timestamp": "2026-05-05T12:00:00",
      "expiring_at": "2026-05-06T12:00:00",
      "caption": "Lunch rush vibes \\ud83c\\udfb6",
      "link": null,
      "poll_question": null,
      "poll_options": null
    },
    {
      "id": "17950001002",
      "user_id": "17841400123456789",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/stories/17950001002.jpg",
      "timestamp": "2026-05-05T09:30:00",
      "expiring_at": "2026-05-06T09:30:00",
      "caption": "Which drink should we feature this weekend?",
      "link": null,
      "poll_question": "Weekend feature?",
      "poll_options": [
        "Honey Lavender Latte",
        "Strawberry Matcha",
        "Meyer Lemon Cold Brew",
        "Classic Cortado"
      ]
    },
    {
      "id": "17950001001",
      "user_id": "17841400123456789",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/stories/17950001001.jpg",
      "timestamp": "2026-05-05T07:00:00",
      "expiring_at": "20
  ... (truncated)
```

---

## 34. GET /17841400123456789/stories?fields=id,media_type,timestamp (List stories - fields)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/stories?fields=id,media_type,timestamp
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17950001007",
      "media_type": "IMAGE",
      "timestamp": "2026-05-06T06:30:00"
    },
    {
      "id": "17950001006",
      "media_type": "VIDEO",
      "timestamp": "2026-05-05T17:30:00"
    },
    {
      "id": "17950001005",
      "media_type": "IMAGE",
      "timestamp": "2026-05-05T16:00:00"
    },
    {
      "id": "17950001004",
      "media_type": "IMAGE",
      "timestamp": "2026-05-05T14:30:00"
    },
    {
      "id": "17950001003",
      "media_type": "VIDEO",
      "timestamp": "2026-05-05T12:00:00"
    },
    {
      "id": "17950001002",
      "media_type": "IMAGE",
      "timestamp": "2026-05-05T09:30:00"
    },
    {
      "id": "17950001001",
      "media_type": "IMAGE",
      "timestamp": "2026-05-05T07:00:00"
    }
  ]
}
```

---

## 35. GET /99999999/stories (List stories - user 404)

**Command:**
```
curl -s http://localhost:8007/99999999/stories
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "User 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 36. GET /stories/17950001001 (Get single story)

**Command:**
```
curl -s http://localhost:8007/stories/17950001001
```

**Status:** 200

**Response:**
```json
{
  "id": "17950001001",
  "user_id": "17841400123456789",
  "media_type": "IMAGE",
  "media_url": "https://instagram.mock/stories/17950001001.jpg",
  "timestamp": "2026-05-05T07:00:00",
  "expiring_at": "2026-05-06T07:00:00",
  "caption": "Morning prep \\u2615 First batch going in!",
  "link": null,
  "poll_question": null,
  "poll_options": null
}
```

---

## 37. GET /stories/17950001001?fields=id,caption,media_type (Get story - fields)

**Command:**
```
curl -s http://localhost:8007/stories/17950001001?fields=id,caption,media_type
```

**Status:** 200

**Response:**
```json
{
  "id": "17950001001",
  "media_type": "IMAGE",
  "caption": "Morning prep \\u2615 First batch going in!"
}
```

---

## 38. GET /stories/99999999 (Get story - 404)

**Command:**
```
curl -s http://localhost:8007/stories/99999999
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Story 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 39. GET /17841400123456789/insights (Get user insights (all metrics))

**Command:**
```
curl -s http://localhost:8007/17841400123456789/insights
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "name": "impressions",
      "period": "day",
      "values": [
        {
          "value": 530520,
          "end_time": "2026-05-06T18:43:22+0000"
        }
      ],
      "title": "Impressions",
      "description": "Total number of times your posts have been seen"
    },
    {
      "name": "reach",
      "period": "day",
      "values": [
        {
          "value": 433170,
          "end_time": "2026-05-06T18:43:22+0000"
        }
      ],
      "title": "Reach",
      "description": "Total number of unique accounts that have seen your posts"
    },
    {
      "name": "follower_count",
      "period": "day",
      "values": [
        {
          "value": 28500,
          "end_time": "2026-05-06T18:43:22+0000"
        }
      ],
      "title": "Follower Count",
      "description": "Total number of followers"
    },
    {
      "name": "profile_views",
      "period": "day",
      "values": [
        {
          "value": 7806,
          "end_time": "2026-05-06T18:43:22+0000"
        }
      ],
      "title": "Profile Views",
      "description": "Total number of profile views"
    },
    {
      "name": "website_clicks",
      "period": "day",
      "values": [
        {
          "value": 936,
          "end_time": "2026-05-06T18:43:22+0000"
        }
      ],
      "title": "Website Clicks",
      "description": "Total number of taps on the website link"
    }
  ]
}
```

---

## 40. GET /17841400123456789/insights?metric=impressions,reach (Get user insights - filtered)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/insights?metric=impressions,reach
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "name": "impressions",
      "period": "day",
      "values": [
        {
          "value": 530520,
          "end_time": "2026-05-06T18:43:22+0000"
        }
      ],
      "title": "Impressions",
      "description": "Total number of times your posts have been seen"
    },
    {
      "name": "reach",
      "period": "day",
      "values": [
        {
          "value": 433170,
          "end_time": "2026-05-06T18:43:22+0000"
        }
      ],
      "title": "Reach",
      "description": "Total number of unique accounts that have seen your posts"
    }
  ]
}
```

---

## 41. GET /99999999/insights (Get user insights - 404)

**Command:**
```
curl -s http://localhost:8007/99999999/insights
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "User 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 42. GET /media/17900001002/insights (Get media insights)

**Command:**
```
curl -s http://localhost:8007/media/17900001002/insights
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "name": "impressions",
      "period": "lifetime",
      "values": [
        {
          "value": 52800
        }
      ],
      "title": "Impressions"
    },
    {
      "name": "reach",
      "period": "lifetime",
      "values": [
        {
          "value": 41200
        }
      ],
      "title": "Reach"
    },
    {
      "name": "engagement",
      "period": "lifetime",
      "values": [
        {
          "value": 5608
        }
      ],
      "title": "Engagement"
    },
    {
      "name": "saved",
      "period": "lifetime",
      "values": [
        {
          "value": 890
        }
      ],
      "title": "Saves"
    },
    {
      "name": "shares",
      "period": "lifetime",
      "values": [
        {
          "value": 456
        }
      ],
      "title": "Shares"
    },
    {
      "name": "profile_visits",
      "period": "lifetime",
      "values": [
        {
          "value": 1230
        }
      ],
      "title": "Profile Visits"
    },
    {
      "name": "follows",
      "period": "lifetime",
      "values": [
        {
          "value": 345
        }
      ],
      "title": "Follows"
    }
  ]
}
```

---

## 43. GET /media/17900001002/insights?metric=impressions,reach,saved (Get media insights - filtered)

**Command:**
```
curl -s http://localhost:8007/media/17900001002/insights?metric=impressions,reach,saved
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "name": "impressions",
      "period": "lifetime",
      "values": [
        {
          "value": 52800
        }
      ],
      "title": "Impressions"
    },
    {
      "name": "reach",
      "period": "lifetime",
      "values": [
        {
          "value": 41200
        }
      ],
      "title": "Reach"
    },
    {
      "name": "saved",
      "period": "lifetime",
      "values": [
        {
          "value": 890
        }
      ],
      "title": "Saves"
    }
  ]
}
```

---

## 44. GET /media/17900001017/insights (Get media insights - tulip post)

**Command:**
```
curl -s http://localhost:8007/media/17900001017/insights
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "name": "impressions",
      "period": "lifetime",
      "values": [
        {
          "value": 56700
        }
      ],
      "title": "Impressions"
    },
    {
      "name": "reach",
      "period": "lifetime",
      "values": [
        {
          "value": 45200
        }
      ],
      "title": "Reach"
    },
    {
      "name": "engagement",
      "period": "lifetime",
      "values": [
        {
          "value": 6084
        }
      ],
      "title": "Engagement"
    },
    {
      "name": "saved",
      "period": "lifetime",
      "values": [
        {
          "value": 1456
        }
      ],
      "title": "Saves"
    },
    {
      "name": "shares",
      "period": "lifetime",
      "values": [
        {
          "value": 678
        }
      ],
      "title": "Shares"
    },
    {
      "name": "profile_visits",
      "period": "lifetime",
      "values": [
        {
          "value": 890
        }
      ],
      "title": "Profile Visits"
    },
    {
      "name": "follows",
      "period": "lifetime",
      "values": [
        {
          "value": 234
        }
      ],
      "title": "Follows"
    }
  ]
}
```

---

## 45. GET /media/99999999/insights (Get media insights - 404)

**Command:**
```
curl -s http://localhost:8007/media/99999999/insights
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 46. GET /ig_hashtag_search?q=coffee (Search hashtags - coffee)

**Command:**
```
curl -s http://localhost:8007/ig_hashtag_search?q=coffee
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17840001001",
      "name": "specialtycoffee",
      "media_count": 12450000
    },
    {
      "id": "17840001004",
      "name": "coffeeroasters",
      "media_count": 2340000
    },
    {
      "id": "17840001005",
      "name": "pourovercoffee",
      "media_count": 1890000
    },
    {
      "id": "17840001006",
      "name": "pdxcoffee",
      "media_count": 234000
    },
    {
      "id": "17840001007",
      "name": "coffeeshop",
      "media_count": 15600000
    },
    {
      "id": "17840001010",
      "name": "coffeeart",
      "media_count": 2890000
    },
    {
      "id": "17840001013",
      "name": "portlandcoffee",
      "media_count": 456000
    },
    {
      "id": "17840001014",
      "name": "coffeeeducation",
      "media_count": 345000
    },
    {
      "id": "17840001015",
      "name": "smallbatchcoffee",
      "media_count": 234000
    }
  ]
}
```

---

## 47. GET /ig_hashtag_search?q=latteart (Search hashtags - latteart)

**Command:**
```
curl -s http://localhost:8007/ig_hashtag_search?q=latteart
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17840001002",
      "name": "latteart",
      "media_count": 4560000
    }
  ]
}
```

---

## 48. GET /ig_hashtag_search?q=portland (Search hashtags - portland)

**Command:**
```
curl -s http://localhost:8007/ig_hashtag_search?q=portland
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17840001003",
      "name": "portland",
      "media_count": 8900000
    },
    {
      "id": "17840001013",
      "name": "portlandcoffee",
      "media_count": 456000
    }
  ]
}
```

---

## 49. GET /hashtag/17840001001 (Get hashtag by ID)

**Command:**
```
curl -s http://localhost:8007/hashtag/17840001001
```

**Status:** 200

**Response:**
```json
{
  "id": "17840001001",
  "name": "specialtycoffee",
  "media_count": 12450000
}
```

---

## 50. GET /hashtag/17840001001?fields=id,name (Get hashtag - fields)

**Command:**
```
curl -s http://localhost:8007/hashtag/17840001001?fields=id,name
```

**Status:** 200

**Response:**
```json
{
  "id": "17840001001",
  "name": "specialtycoffee"
}
```

---

## 51. GET /hashtag/99999999 (Get hashtag - 404)

**Command:**
```
curl -s http://localhost:8007/hashtag/99999999
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Hashtag 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 52. GET /hashtag/17840001001/recent_media?user_id=17841400123456789 (Hashtag recent media)

**Command:**
```
curl -s http://localhost:8007/hashtag/17840001001/recent_media?user_id=17841400123456789
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17900001001",
      "user_id": "17841400123456789",
      "caption": "Sunday morning pour-over ritual \\u2615\\n\\nOur new Ethiopian Yirgacheffe is giving us bright citrus notes with a silky body. Limited batch \\u2014 grab yours before it\\u2019s gone!\\n\\n#specialtycoffee #pourovercoffee #ethiopiancoffee #yirgacheffe #coffeeroasters #portland #pdxcoffee",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001001.jpg",
      "permalink": "https://instagram.mock/p/BA1cD2eF3g/",
      "thumbnail_url": null,
      "timestamp": "2026-05-04T07:15:00",
      "like_count": 487,
      "comments_count": 25,
      "is_comment_enabled": true
    },
    {
      "id": "17900001003",
      "user_id": "17841400123456789",
      "caption": "NEW ARRIVAL \\ud83d\\udce6\\u2728\\n\\nJust landed: Guatemala Huehuetenango from Finca El Injerto. Notes of dark chocolate, toasted almond, and red grape. Washed process, roasted medium.\\n\\nAvailable in:\\n\\u2022 12oz whole bean ($22)\\n\\u2022 5lb wholesale ($85)\\n\\nShop link in bio or visit us in-store!\\n\\n#guatemalancoffee #singleorigin #newbeans #coffeeroasters #specialtycoffee #fincaelinjerto",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001003.jpg",
      "permalink": "https://instagram.mock/p/DC3eF4gH5i/",
      "thumbnail_url": null,
      "timestamp": "2026-04-30T17:00:00",
      "like_count": 612,
      "comments_count": 31,
      "is_comment_enabled": true
    }
  ]
}
```

---

## 53. GET /hashtag/17840001002/recent_media?user_id=17841400123456789 (Hashtag recent media - latteart)

**Command:**
```
curl -s http://localhost:8007/hashtag/17840001002/recent_media?user_id=17841400123456789
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17900001002",
      "user_id": "17841400123456789",
      "caption": "The rosetta that made us stop everything \\ud83c\\udf39\\n\\nOur barista @maria_pours has been perfecting her technique for months and THIS is the result. Creamy oat milk + our house espresso blend = pure art.\\n\\nWho wants to learn? Free latte art workshop this Saturday! Link in bio \\u2b06\\ufe0f\\n\\n#latteart #rosetta #oatmilklatte #baristalife #coffeeart #portland #lattearttutorial",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001002.jpg",
      "permalink": "https://instagram.mock/p/CB2dE3fG4h/",
      "thumbnail_url": null,
      "timestamp": "2026-05-02T12:30:00",
      "like_count": 5234,
      "comments_count": 187,
      "is_comment_enabled": true
    },
    {
      "id": "17900001016",
      "user_id": "17841400123456789",
      "caption": "Latte art throwdown TONIGHT! \\ud83c\\udfc6\\n\\n8 baristas. 3 rounds. 1 champion.\\n\\nDoors open at 7pm. $5 entry includes your first drink.\\nJudges: @nw_coffee_alliance @portland_barista_guild\\n\\nWho\\u2019s coming? \\ud83d\\ude4b\\n\\n#latteartthtrowdown #baristacompetition #portlandevents #coffeecommunity #liveevents",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001016.jpg",
      "permalink": "https://instagram.mock/p/QP6rS7tU8v/",
      "thumbnail_url": null,
      "timestamp": "2026-04-03T17:00:00",
      "like_count": 1034,
      "comments_count": 89,
      "is_comment_enabled": true
    },
    {
      "id": "17900001017",
      "user_id": "17841400123456789",
      "caption": "The tulip. Our most-requested latte art design \\ud83c\\udf37\\n\\nPerfect layers. Satisfying symmetry. Endless practice.\\n\\nDouble-tap if this makes you want coffee right now \\u2764\\ufe0f\\n\\n#latteart #tulip #coffeeart #baristalife #milkart #satisfying",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001017.jpg",
      "permalink": "https://instagram.mock/p/RQ7sT8uV9w/",
      "thumbnail_url": null,
      "timestamp": "2026-04-01T08:00:00",
      "like_count": 5678,
      "comments_count": 203,
      "is_comment_enabled": true
    },
    {
      "id": "17900001022",
      "user_id": "17841400123456789",
      "caption": "This corner. This light. This latte. \\u2728\\n\\n#minimalist #cafeaesthetic #latteart #interiordesign #coffeemoment",
      "media_type": "IMAGE",
      "media_url": "https://instagram.mock/media/17900001022.jpg",
      "permalink": "https://instagram.mock/p/WV2xY3zA4b/",
      "thumbnail_url": null,
      "timestamp": "2026-03-22T15:45:00",
      "like_count": 756,
      "comments_count": 16,
      "is_comment_enabled": true
    }
  ]
}
```

---

## 54. GET /hashtag/99999999/recent_media?user_id=17841400123456789 (Hashtag recent media - 404)

**Command:**
```
curl -s http://localhost:8007/hashtag/99999999/recent_media?user_id=17841400123456789
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Hashtag 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 55. GET /17841400123456789/tags (List user mentions/tags)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/tags
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17870001001",
      "media_id": "17900100001",
      "mentioned_by_user_id": "17841400999040",
      "mentioned_by_username": "pdx_coffee_crawl",
      "media_url": "https://instagram.mock/media/mention_001.jpg",
      "timestamp": "2026-05-01T14:00:00",
      "caption": "Best cortado in Portland goes to @brewedawakening_ \\ud83c\\udfc6 Fight me. #pdxcoffee"
    },
    {
      "id": "17870001002",
      "media_id": "17900100002",
      "mentioned_by_user_id": "17841400999041",
      "mentioned_by_username": "sarah_eats_pdx",
      "media_url": "https://instagram.mock/media/mention_002.jpg",
      "timestamp": "2026-04-28T10:30:00",
      "caption": "Saturday morning ritual at @brewedawakening_ \\u2615 The honey lavender latte is *chef's kiss*"
    },
    {
      "id": "17870001003",
      "media_id": "17900100003",
      "mentioned_by_user_id": "17841400999042",
      "mentioned_by_username": "portland_date_ideas",
      "media_url": "https://instagram.mock/media/mention_003.jpg",
      "timestamp": "2026-04-22T16:00:00",
      "caption": "Date spot #47: @brewedawakening_ in SE Portland. Cozy vibes, incredible coffee, great pastries from @pdx_sourdough \\ud83c\\udf5e\\u2764\\ufe0f"
    },
    {
      "id": "17870001007",
      "media_id": "17900100007",
      "mentioned_by_user_id": "17841400999021",
      "mentioned_by_username": "clay_and_kiln",
      "media_url": "https://instagram.mock/media/mention_007.jpg",
      "timestamp": "2026-04-20T10:00:00",
      "caption": "Sneak peek of our collab with @brewedawakening_ \\ud83e\\udec2 Handmade pour-over drippers dropping this Saturday!"
    },
    {
      "id": "17870001004",
      "media_id": "17900100004",
      "mentioned_by_user_id": "17841400999005",
      "mentioned_by_username": "maria_pours",
      "media_url": "https://instagram.mock/media/mention_004.jpg",
      "timestamp": "2026-04-18T09:00:00",
      "caption": "Grateful to work with the best team @brewedawakening_ \\ud83d\\udc9c New latte art designs dropping soon!"
    },
    {
      "id": "17870001005",
      "media_id": "17900100005",
      "mentioned_by_user_id": "17841400999043",
      "mentioned_by_username": "nw_coffee_alliance",
      "media_url": "https://instagram.mock/media/mention_005.jpg",
      "timestamp": "2026-04-10T11:00:00",
      "caption": "Congrats to @brewedawakening_ on the 92-point @coffeereview score! Well deserved recognition for Portland's finest."
    },
    {
      "id": "17870001006",
      "media_id": "17900100006",
      "mentioned_by_user_id": "17841400999044",
      "mentioned_by_username": "coffee_review_weekly",
      "media_url": "https://instagram.mock/media/mention_006.jpg",
      "timestamp": "2026-04-05T15:00:00",
      "caption": "Our latest reviews are in! @brewedawakening_ Ethiopian Sidamo Natural scored 92. Floral, berry-forward, silky body."
    }
  ],
  "paging": {}
}
```

---

## 56. GET /17841400123456789/tags?limit=3 (List mentions - limit=3)

**Command:**
```
curl -s http://localhost:8007/17841400123456789/tags?limit=3
```

**Status:** 200

**Response:**
```json
{
  "data": [
    {
      "id": "17870001001",
      "media_id": "17900100001",
      "mentioned_by_user_id": "17841400999040",
      "mentioned_by_username": "pdx_coffee_crawl",
      "media_url": "https://instagram.mock/media/mention_001.jpg",
      "timestamp": "2026-05-01T14:00:00",
      "caption": "Best cortado in Portland goes to @brewedawakening_ \\ud83c\\udfc6 Fight me. #pdxcoffee"
    },
    {
      "id": "17870001002",
      "media_id": "17900100002",
      "mentioned_by_user_id": "17841400999041",
      "mentioned_by_username": "sarah_eats_pdx",
      "media_url": "https://instagram.mock/media/mention_002.jpg",
      "timestamp": "2026-04-28T10:30:00",
      "caption": "Saturday morning ritual at @brewedawakening_ \\u2615 The honey lavender latte is *chef's kiss*"
    },
    {
      "id": "17870001003",
      "media_id": "17900100003",
      "mentioned_by_user_id": "17841400999042",
      "mentioned_by_username": "portland_date_ideas",
      "media_url": "https://instagram.mock/media/mention_003.jpg",
      "timestamp": "2026-04-22T16:00:00",
      "caption": "Date spot #47: @brewedawakening_ in SE Portland. Cozy vibes, incredible coffee, great pastries from @pdx_sourdough \\ud83c\\udf5e\\u2764\\ufe0f"
    }
  ],
  "paging": {
    "cursors": {
      "after": "17870001003"
    }
  }
}
```

---

## 57. GET /99999999/tags (List mentions - user 404)

**Command:**
```
curl -s http://localhost:8007/99999999/tags
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "User 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 58. POST /17841400123456789/media (Create media container (IMAGE))

**Command:**
```
curl -s -X POST -H 'Content-Type: application/json' -d '{"image_url": "https://example.com/new_coffee.jpg", "caption": "Fresh roast Friday! #specialtycoffee", "media_type": "IMAGE"}' http://localhost:8007/17841400123456789/media
```

**Status:** 201

**Response:**
```json
{
  "id": "17920001001"
}
```

---

## 59. POST /17841400123456789/media (Create media container (VIDEO))

**Command:**
```
curl -s -X POST -H 'Content-Type: application/json' -d '{"video_url": "https://example.com/reel.mp4", "caption": "Latte art reel #latteart", "media_type": "VIDEO"}' http://localhost:8007/17841400123456789/media
```

**Status:** 201

**Response:**
```json
{
  "id": "17920001002"
}
```

---

## 60. GET /container/17920001001 (Get container status)

**Command:**
```
curl -s http://localhost:8007/container/17920001001
```

**Status:** 200

**Response:**
```json
{
  "id": "17920001001",
  "status": "FINISHED",
  "status_code": "PUBLISHED"
}
```

---

## 61. POST /17841400123456789/media_publish (Publish media container)

**Command:**
```
curl -s -X POST -H 'Content-Type: application/json' -d '{"creation_id": "17920001001"}' http://localhost:8007/17841400123456789/media_publish
```

**Status:** 201

**Response:**
```json
{
  "id": "17900001029"
}
```

---

## 62. POST /17841400123456789/media_publish (Publish - container 404)

**Command:**
```
curl -s -X POST -H 'Content-Type: application/json' -d '{"creation_id": "99999999"}' http://localhost:8007/17841400123456789/media_publish
```

**Status:** 400

**Response:**
```json
{
  "error": {
    "message": "Container 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 63. GET /container/99999999 (Get container - 404)

**Command:**
```
curl -s http://localhost:8007/container/99999999
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Container 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

## 64. DELETE /media/17900001028 (Delete media post)

**Command:**
```
curl -s -X DELETE http://localhost:8007/media/17900001028
```

**Status:** 200

**Response:**
```json
{
  "success": true
}
```

---

## 65. DELETE /media/99999999 (Delete media - 404)

**Command:**
```
curl -s -X DELETE http://localhost:8007/media/99999999
```

**Status:** 404

**Response:**
```json
{
  "error": {
    "message": "Media 99999999 not found",
    "type": "IGApiException",
    "code": 100
  }
}
```

---

