# MyFitnessPal API Test Results

Generated: Thu May  7 00:13:23 IST 2026

## 1. GET /health (Health check)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/health
```

**Status:** 200

```json
{
    "status": "ok"
}
```

---

## 2. GET /v1/user/profile (Get user profile)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/profile
```

**Status:** 200

```json
{
    "type": "user_profile",
    "user_profile": {
        "user_id": 1,
        "username": "alexrivera32",
        "display_name": "Alex Rivera",
        "email": "alex.rivera@email.com",
        "date_of_birth": "1993-02-14",
        "sex": "male",
        "height_cm": 177.8,
        "current_weight_lbs": 192.0,
        "goal_weight_lbs": 175.0,
        "activity_level": "moderately_active",
        "profile_image_url": "https://mfp-static.example.com/avatars/alexrivera32.jpg",
        "location": "Austin, TX",
        "joined_date": "2024-11-15",
        "daily_calorie_goal": 1800,
        "macro_goals": {
            "carbs_pct": 40,
            "fat_pct": 25,
            "protein_pct": 35
        },
        "nutrient_goals": {
            "calories": 1800,
            "total_fat_g": 50,
            "saturated_fat_g": 16,
            "cholesterol_mg": 300,
            "sodium_mg": 2300,
            "total_carbs_g": 180,
            "dietary_fiber_g": 30,
            "sugars_g": 50,
            "protein_g": 158,
            "potassium_mg": 3500,
            "vitamin_a_pct": 100,
            "vitamin_c_pct": 100,
            "calcium_pct": 100,
            "iron_pct": 100
        },
        "weekly_weight_goal_lbs": -1.0,
        "units": {
            "weight": "lbs",
            "height": "inches",
            "water": "cups",
            "energy": "calories"
        }
    }
}
```

---

## 3. PUT /v1/user/profile (Update profile)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X PUT -H 'Content-Type: application/json' -d '{"activity_level": "very_active", "daily_calorie_goal": 2000}' http://localhost:8006/v1/user/profile
```

**Status:** 200

```json
{
    "type": "user_profile",
    "user_profile": {
        "user_id": 1,
        "username": "alexrivera32",
        "display_name": "Alex Rivera",
        "email": "alex.rivera@email.com",
        "date_of_birth": "1993-02-14",
        "sex": "male",
        "height_cm": 177.8,
        "current_weight_lbs": 192.0,
        "goal_weight_lbs": 175.0,
        "activity_level": "very_active",
        "profile_image_url": "https://mfp-static.example.com/avatars/alexrivera32.jpg",
        "location": "Austin, TX",
        "joined_date": "2024-11-15",
        "daily_calorie_goal": 2000,
        "macro_goals": {
            "carbs_pct": 40,
            "fat_pct": 25,
            "protein_pct": 35
        },
        "nutrient_goals": {
            "calories": 1800,
            "total_fat_g": 50,
            "saturated_fat_g": 16,
            "cholesterol_mg": 300,
            "sodium_mg": 2300,
            "total_carbs_g": 180,
            "dietary_fiber_g": 30,
            "sugars_g": 50,
            "protein_g": 158,
            "potassium_mg": 3500,
            "vitamin_a_pct": 100,
            "vitamin_c_pct": 100,
            "calcium_pct": 100,
            "iron_pct": 100
        },
        "weekly_weight_goal_lbs": -1.0,
        "units": {
            "weight": "lbs",
            "height": "inches",
            "water": "cups",
            "energy": "calories"
        }
    }
}
```

---

## 4. GET /v1/user/goals (Get goals)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/goals
```

**Status:** 200

```json
{
    "type": "goals",
    "goals": {
        "daily_calorie_goal": 2000,
        "macro_goals": {
            "carbs_pct": 40,
            "fat_pct": 25,
            "protein_pct": 35
        },
        "nutrient_goals": {
            "calories": 1800,
            "total_fat_g": 50,
            "saturated_fat_g": 16,
            "cholesterol_mg": 300,
            "sodium_mg": 2300,
            "total_carbs_g": 180,
            "dietary_fiber_g": 30,
            "sugars_g": 50,
            "protein_g": 158,
            "potassium_mg": 3500,
            "vitamin_a_pct": 100,
            "vitamin_c_pct": 100,
            "calcium_pct": 100,
            "iron_pct": 100
        },
        "weekly_weight_goal_lbs": -1.0,
        "goal_weight_lbs": 175.0
    }
}
```

---

## 5. PUT /v1/user/goals (Update goals)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X PUT -H 'Content-Type: application/json' -d '{"daily_calorie_goal": 1900, "macro_goals": {"protein_pct": 40, "carbs_pct": 35, "fat_pct": 25}}' http://localhost:8006/v1/user/goals
```

**Status:** 200

```json
{
    "type": "goals",
    "goals": {
        "daily_calorie_goal": 1900,
        "macro_goals": {
            "carbs_pct": 35,
            "fat_pct": 25,
            "protein_pct": 40
        },
        "nutrient_goals": {
            "calories": 1900,
            "total_fat_g": 50,
            "saturated_fat_g": 16,
            "cholesterol_mg": 300,
            "sodium_mg": 2300,
            "total_carbs_g": 180,
            "dietary_fiber_g": 30,
            "sugars_g": 50,
            "protein_g": 158,
            "potassium_mg": 3500,
            "vitamin_a_pct": 100,
            "vitamin_c_pct": 100,
            "calcium_pct": 100,
            "iron_pct": 100
        },
        "weekly_weight_goal_lbs": -1.0,
        "goal_weight_lbs": 175.0
    }
}
```

---

## 6. GET /v1/foods/search (Search all foods)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/foods/search
```

**Status:** 200

```json
{
    "type": "foods",
    "count": 25,
    "total": 45,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "food_id": 1,
            "food_name": "Grilled Chicken Breast",
            "brand": "",
            "serving_size": "4",
            "serving_unit": "oz",
            "calories": 165.0,
            "total_fat_g": 3.6,
            "saturated_fat_g": 1.0,
            "cholesterol_mg": 85.0,
            "sodium_mg": 74.0,
            "total_carbs_g": 0.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 0.0,
            "protein_g": 31.0,
            "potassium_mg": 256.0,
            "is_verified": true
        },
        {
            "food_id": 2,
            "food_name": "Brown Rice (cooked)",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "cup",
            "calories": 216.0,
            "total_fat_g": 1.8,
            "saturated_fat_g": 0.4,
            "cholesterol_mg": 0.0,
            "sodium_mg": 10.0,
            "total_carbs_g": 45.0,
            "dietary_fiber_g": 3.5,
            "sugars_g": 0.7,
            "protein_g": 5.0,
            "potassium_mg": 84.0,
            "is_verified": true
        },
        {
            "food_id": 3,
            "food_name": "Banana",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "medium (118g)",
            "calories": 105.0,
            "total_fat_g": 0.4,
            "saturated_fat_g": 0.1,
            "cholesterol_mg": 0.0,
            "sodium_mg": 1.0,
            "total_carbs_g": 27.0,
            "dietary_fiber_g": 3.1,
            "sugars_g": 14.4,
            "protein_g": 1.3,
            "potassium_mg": 422.0,
            "is_verified": true
        },
        {
            "food_id": 4,
            "food_name": "Large Egg",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "large",
            "calories": 72.0,
            "total_fat_g": 5.0,
            "saturated_fat_g": 1.6,
            "cholesterol_mg": 186.0,
            "sodium_mg": 71.0,
            "total_carbs_g": 0.4,
            "dietary_fiber_g": 0.0,
            "sugars_g": 0.2,
            "protein_g": 6.3,
            "potassium_mg": 69.0,
            "is_verified": true
        },
        {
            "food_id": 5,
            "food_name": "Chobani Greek Yogurt (Non-Fat Plain)",
            "brand": "Chobani",
            "serving_size": "1",
            "serving_unit": "container (150g)",
            "calories": 90.0,
            "total_fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "cholesterol_mg": 5.0,
            "sodium_mg": 60.0,
            "total_carbs_g": 6.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 4.0,
            "protein_g": 15.0,
            "potassium_mg": 240.0,
            "is_verified": true
        },
        {
            "food_id": 6,
            "food_name": "Dave's Killer Bread (21 Whole Grains)",
            "brand": "Dave's Killer Bread",
            "serving_size": "1",
            "serving_unit": "slice (45g)",
            "calories": 110.0,
            "total_fat_g": 1.5,
            "saturated_fat_g": 0.0,
            "cholesterol_mg": 0.0,
            "sodium_mg": 170.0,
            "total_carbs_g": 22.0,
            "dietary_fiber_g": 5.0,
            "sugars_g": 5.0,
            "protein_g": 5.0,
            "potassium_mg": 80.0,
            "is_verified": true
        },
        {
            "food_id": 7,
            "food_name": "Extra Virgin Olive Oil",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "tbsp",
            "calories": 119.0,
            "total_fat_g": 14.0,
            "saturated_fat_g": 1.9,
            "cholesterol_mg": 0.0,
            "sodium_mg": 0.0,
            "total_carbs_g": 0.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 0.0,
            "protein_g": 0.0,
            "potassium_mg": 0.0,
            "is_verified": true
        },
        {
            "food_id": 8,
            "food_name": "Broccoli (steamed)",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "cup",
            "calories": 55.0,
            "total_fat_g": 0.6,
            "saturated_fat_g": 0.1,
            "cholesterol_mg": 0.0,
            "sodium_mg": 64.0,
            "total_carbs_g": 11.0,
            "dietary_fiber_g": 5.1,
            "sugars_g": 2.2,
            "protein_g": 3.7,
            "potassium_mg": 457.0,
            "is_verified": true
        },
        {
            "food_id": 9,
            "food_name": "Sweet Potato (baked)",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "medium (130g)",
            "calories": 103.0,
            "total_fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "cholesterol_mg": 0.0,
            "sodium_mg": 41.0,
            "total_carbs_g": 24.0,
            "dietary_fiber_g": 3.8,
            "sugars_g": 7.4,
            "protein_g": 2.3,
            "potassium_mg": 542.0,
            "is_verified": true
        },
        {
            "food_id": 10,
            "food_name": "Salmon Fillet (baked)",
            "brand": "",
            "serving_size": "4",
            "serving_unit": "oz",
            "calories": 233.0,
            "total_fat_g": 14.0,
            "saturated_fat_g": 2.6,
            "cholesterol_mg": 63.0,
            "sodium_mg": 62.0,
            "total_carbs_g": 0.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 0.0,
            "protein_g": 25.0,
            "potassium_mg": 534.0,
            "is_verified": true
        },
        {
            "food_id": 11,
            "food_name": "Avocado",
            "brand": "",
            "serving_size": "0.5",
            "serving_unit": "medium",
            "calories": 120.0,
            "total_fat_g": 11.0,
            "saturated_fat_g": 1.5,
            "cholesterol_mg": 0.0,
            "sodium_mg": 5.0,
            "total_carbs_g": 6.0,
            "dietary_fiber_g": 5.0,
            "sugars_g": 0.5,
            "protein_g": 1.5,
            "potassium_mg": 345.0,
            "is_verified": true
        },
        {
            "food_id": 12,
            "food_name": "Almonds (raw)",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "oz (28g)",
            "calories": 164.0,
            "total_fat_g": 14.0,
            "saturated_fat_g": 1.1,
            "cholesterol_mg": 0.0,
            "sodium_mg": 0.0,
            "total_carbs_g": 6.0,
            "dietary_fiber_g": 3.5,
            "sugars_g": 1.2,
            "protein_g": 6.0,
            "potassium_mg": 208.0,
            "is_verified": true
        },
        {
            "food_id": 13,
            "food_name": "Oatmeal (cooked)",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "cup",
            "calories": 154.0,
            "total_fat_g": 2.6,
            "saturated_fat_g": 0.4,
            "cholesterol_mg": 0.0,
            "sodium_mg": 9.0,
            "total_carbs_g": 27.0,
            "dietary_fiber_g": 4.0,
            "sugars_g": 1.1,
            "protein_g": 5.4,
            "potassium_mg": 143.0,
            "is_verified": true
        },
        {
            "food_id": 14,
            "food_name": "Whole Milk",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "cup",
            "calories": 149.0,
            "total_fat_g": 8.0,
            "saturated_fat_g": 5.0,
            "cholesterol_mg": 24.0,
            "sodium_mg": 105.0,
            "total_carbs_g": 12.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 12.0,
            "protein_g": 8.0,
            "potassium_mg": 322.0,
            "is_verified": true
        },
        {
            "food_id": 15,
            "food_name": "Baby Spinach",
            "brand": "",
            "serving_size": "2",
            "serving_unit": "cups (60g)",
            "calories": 14.0,
            "total_fat_g": 0.2,
            "saturated_fat_g": 0.0,
            "cholesterol_mg": 0.0,
            "sodium_mg": 47.0,
            "total_carbs_g": 2.2,
            "dietary_fiber_g": 1.3,
            "sugars_g": 0.3,
            "protein_g": 1.7,
            "potassium_mg": 334.0,
            "is_verified": true
        },
        {
            "food_id": 16,
            "food_name": "Black Beans (canned)",
            "brand": "",
            "serving_size": "0.5",
            "serving_unit": "cup",
            "calories": 114.0,
            "total_fat_g": 0.5,
            "saturated_fat_g": 0.1,
            "cholesterol_mg": 0.0,
            "sodium_mg": 461.0,
            "total_carbs_g": 20.0,
            "dietary_fiber_g": 7.5,
            "sugars_g": 0.3,
            "protein_g": 7.6,
            "potassium_mg": 305.0,
            "is_verified": true
        },
        {
            "food_id": 17,
            "food_name": "Ground Turkey (93% lean)",
            "brand": "",
            "serving_size": "4",
            "serving_unit": "oz",
            "calories": 170.0,
            "total_fat_g": 9.0,
            "saturated_fat_g": 2.5,
            "cholesterol_mg": 80.0,
            "sodium_mg": 80.0,
            "total_carbs_g": 0.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 0.0,
            "protein_g": 21.0,
            "potassium_mg": 240.0,
            "is_verified": true
        },
        {
            "food_id": 18,
            "food_name": "Protein Shake (whey)",
            "brand": "Optimum Nutrition",
            "serving_size": "1",
            "serving_unit": "scoop (31g)",
            "calories": 120.0,
            "total_fat_g": 1.5,
            "saturated_fat_g": 0.5,
            "cholesterol_mg": 30.0,
            "sodium_mg": 130.0,
            "total_carbs_g": 3.0,
            "dietary_fiber_g": 1.0,
            "sugars_g": 1.0,
            "protein_g": 24.0,
            "potassium_mg": 160.0,
            "is_verified": true
        },
        {
            "food_id": 19,
            "food_name": "Apple",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "medium (182g)",
            "calories": 95.0,
            "total_fat_g": 0.3,
            "saturated_fat_g": 0.1,
            "cholesterol_mg": 0.0,
            "sodium_mg": 2.0,
            "total_carbs_g": 25.0,
            "dietary_fiber_g": 4.4,
            "sugars_g": 19.0,
            "protein_g": 0.5,
            "potassium_mg": 195.0,
            "is_verified": true
        },
        {
            "food_id": 20,
            "food_name": "Peanut Butter (natural)",
            "brand": "Smucker's Natural",
            "serving_size": "2",
            "serving_unit": "tbsp (32g)",
            "calories": 190.0,
            "total_fat_g": 16.0,
            "saturated_fat_g": 2.5,
            "cholesterol_mg": 0.0,
            "sodium_mg": 65.0,
            "total_carbs_g": 7.0,
            "dietary_fiber_g": 2.0,
            "sugars_g": 3.0,
            "protein_g": 7.0,
            "potassium_mg": 180.0,
            "is_verified": true
        },
        {
            "food_id": 21,
            "food_name": "Chipotle Burrito Bowl (Chicken)",
            "brand": "Chipotle",
            "serving_size": "1",
            "serving_unit": "bowl",
            "calories": 665.0,
            "total_fat_g": 22.0,
            "saturated_fat_g": 8.0,
            "cholesterol_mg": 120.0,
            "sodium_mg": 1695.0,
            "total_carbs_g": 60.0,
            "dietary_fiber_g": 12.0,
            "sugars_g": 5.0,
            "protein_g": 50.0,
            "potassium_mg": 820.0,
            "is_verified": true
        },
        {
            "food_id": 22,
            "food_name": "Quest Protein Bar (Chocolate Chip Cookie Dough)",
            "brand": "Quest Nutrition",
            "serving_size": "1",
            "serving_unit": "bar (60g)",
            "calories": 200.0,
            "total_fat_g": 9.0,
            "saturated_fat_g": 3.5,
            "cholesterol_mg": 10.0,
            "sodium_mg": 260.0,
            "total_carbs_g": 22.0,
            "dietary_fiber_g": 14.0,
            "sugars_g": 1.0,
            "protein_g": 21.0,
            "potassium_mg": 85.0,
            "is_verified": true
        },
        {
            "food_id": 23,
            "food_name": "Cottage Cheese (2% Low Fat)",
            "brand": "",
            "serving_size": "0.5",
            "serving_unit": "cup (113g)",
            "calories": 92.0,
            "total_fat_g": 2.5,
            "saturated_fat_g": 1.5,
            "cholesterol_mg": 15.0,
            "sodium_mg": 348.0,
            "total_carbs_g": 5.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 4.0,
            "protein_g": 12.0,
            "potassium_mg": 97.0,
            "is_verified": true
        },
        {
            "food_id": 24,
            "food_name": "White Rice (cooked)",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "cup",
            "calories": 206.0,
            "total_fat_g": 0.4,
            "saturated_fat_g": 0.1,
            "cholesterol_mg": 0.0,
            "sodium_mg": 2.0,
            "total_carbs_g": 45.0,
            "dietary_fiber_g": 0.6,
            "sugars_g": 0.1,
            "protein_g": 4.3,
            "potassium_mg": 55.0,
            "is_verified": true
        },
        {
            "food_id": 25,
            "food_name": "Canned Tuna (in water)",
            "brand": "StarKist",
            "serving_size": "1",
            "serving_unit": "can (142g)",
            "calories": 191.0,
            "total_fat_g": 1.4,
            "saturated_fat_g": 0.4,
            "cholesterol_mg": 60.0,
            "sodium_mg": 558.0,
            "total_carbs_g": 0.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 0.0,
            "protein_g": 42.0,
            "potassium_mg": 360.0,
            "is_verified": true
        }
    ]
}
```

---

## 7. GET /v1/foods/search?q=chicken&limit=10 (Search foods - chicken)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/foods/search?q=chicken&limit=10
```

**Status:** 200

```json
{
    "type": "foods",
    "count": 3,
    "total": 3,
    "offset": 0,
    "limit": 10,
    "results": [
        {
            "food_id": 1,
            "food_name": "Grilled Chicken Breast",
            "brand": "",
            "serving_size": "4",
            "serving_unit": "oz",
            "calories": 165.0,
            "total_fat_g": 3.6,
            "saturated_fat_g": 1.0,
            "cholesterol_mg": 85.0,
            "sodium_mg": 74.0,
            "total_carbs_g": 0.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 0.0,
            "protein_g": 31.0,
            "potassium_mg": 256.0,
            "is_verified": true
        },
        {
            "food_id": 21,
            "food_name": "Chipotle Burrito Bowl (Chicken)",
            "brand": "Chipotle",
            "serving_size": "1",
            "serving_unit": "bowl",
            "calories": 665.0,
            "total_fat_g": 22.0,
            "saturated_fat_g": 8.0,
            "cholesterol_mg": 120.0,
            "sodium_mg": 1695.0,
            "total_carbs_g": 60.0,
            "dietary_fiber_g": 12.0,
            "sugars_g": 5.0,
            "protein_g": 50.0,
            "potassium_mg": 820.0,
            "is_verified": true
        },
        {
            "food_id": 43,
            "food_name": "Rotisserie Chicken Thigh (skin removed)",
            "brand": "",
            "serving_size": "1",
            "serving_unit": "thigh (95g)",
            "calories": 170.0,
            "total_fat_g": 8.0,
            "saturated_fat_g": 2.3,
            "cholesterol_mg": 95.0,
            "sodium_mg": 75.0,
            "total_carbs_g": 0.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 0.0,
            "protein_g": 23.0,
            "potassium_mg": 220.0,
            "is_verified": true
        }
    ]
}
```

---

## 8. GET /v1/foods/search?q=chobani (Search foods - brand)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/foods/search?q=chobani
```

**Status:** 200

```json
{
    "type": "foods",
    "count": 1,
    "total": 1,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "food_id": 5,
            "food_name": "Chobani Greek Yogurt (Non-Fat Plain)",
            "brand": "Chobani",
            "serving_size": "1",
            "serving_unit": "container (150g)",
            "calories": 90.0,
            "total_fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "cholesterol_mg": 5.0,
            "sodium_mg": 60.0,
            "total_carbs_g": 6.0,
            "dietary_fiber_g": 0.0,
            "sugars_g": 4.0,
            "protein_g": 15.0,
            "potassium_mg": 240.0,
            "is_verified": true
        }
    ]
}
```

---

## 9. GET /v1/foods/1 (Get food by ID)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/foods/1
```

**Status:** 200

```json
{
    "type": "food",
    "food": {
        "food_id": 1,
        "food_name": "Grilled Chicken Breast",
        "brand": "",
        "serving_size": "4",
        "serving_unit": "oz",
        "calories": 165.0,
        "total_fat_g": 3.6,
        "saturated_fat_g": 1.0,
        "cholesterol_mg": 85.0,
        "sodium_mg": 74.0,
        "total_carbs_g": 0.0,
        "dietary_fiber_g": 0.0,
        "sugars_g": 0.0,
        "protein_g": 31.0,
        "potassium_mg": 256.0,
        "is_verified": true
    }
}
```

---

## 10. GET /v1/foods/9999 (Get food - 404)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/foods/9999
```

**Status:** 404

```json
{
    "error": "Food 9999 not found"
}
```

---

## 11. GET /v1/user/diary/2025-04-28 (Get diary for date)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/diary/2025-04-28
```

**Status:** 200

```json
{
    "type": "diary",
    "date": "2025-04-28",
    "meals": {
        "Breakfast": [
            {
                "entry_id": 281,
                "date": "2025-04-28",
                "meal": "Breakfast",
                "food_id": 4,
                "food_name": "Large Egg",
                "brand": "",
                "serving_size": "1",
                "serving_unit": "large",
                "servings": 2.0,
                "calories": 144.0,
                "total_fat_g": 10.0,
                "saturated_fat_g": 3.2,
                "cholesterol_mg": 372.0,
                "sodium_mg": 142.0,
                "total_carbs_g": 0.8,
                "dietary_fiber_g": 0.0,
                "sugars_g": 0.4,
                "protein_g": 12.6
            },
            {
                "entry_id": 282,
                "date": "2025-04-28",
                "meal": "Breakfast",
                "food_id": 6,
                "food_name": "Dave's Killer Bread (21 Whole Grains)",
                "brand": "Dave's Killer Bread",
                "serving_size": "1",
                "serving_unit": "slice (45g)",
                "servings": 2.0,
                "calories": 220.0,
                "total_fat_g": 3.0,
                "saturated_fat_g": 0.0,
                "cholesterol_mg": 0.0,
                "sodium_mg": 340.0,
                "total_carbs_g": 44.0,
                "dietary_fiber_g": 10.0,
                "sugars_g": 10.0,
                "protein_g": 10.0
            },
            {
                "entry_id": 283,
                "date": "2025-04-28",
                "meal": "Breakfast",
                "food_id": 30,
                "food_name": "Cheddar Cheese",
                "brand": "",
                "serving_size": "1",
                "serving_unit": "oz (28g)",
                "servings": 1.0,
                "calories": 113.0,
                "total_fat_g": 9.3,
                "saturated_fat_g": 5.3,
                "cholesterol_mg": 28.0,
                "sodium_mg": 176.0,
                "total_carbs_g": 0.9,
                "dietary_fiber_g": 0.0,
                "sugars_g": 0.3,
                "protein_g": 7.0
            }
        ],
        "Lunch": [
            {
                "entry_id": 284,
                "date": "2025-04-28",
                "meal": "Lunch",
                "food_id": 1,
                "food_name": "Grilled Chicken Breast",
                "brand": "",
                "serving_size": "4",
                "serving_unit": "oz",
                "servings": 1.5,
                "calories": 248.0,
                "total_fat_g": 5.4,
                "saturated_fat_g": 1.5,
                "cholesterol_mg": 128.0,
                "sodium_mg": 111.0,
                "total_carbs_g": 0.0,
                "dietary_fiber_g": 0.0,
                "sugars_g": 0.0,
                "protein_g": 46.5
            },
            {
                "entry_id": 285,
                "date": "2025-04-28",
                "meal": "Lunch",
                "food_id": 2,
                "food_name": "Brown Rice (cooked)",
                "brand": "",
                "serving_size": "1",
                "serving_unit": "cup",
                "servings": 1.0,
                "calories": 216.0,
                "total_fat_g": 1.8,
                "saturated_fat_g": 0.4,
                "cholesterol_mg": 0.0,
                "sodium_mg": 10.0,
                "total_carbs_g": 45.0,
                "dietary_fiber_g": 3.5,
                "sugars_g": 0.7,
                "protein_g": 5.0
            },
            {
                "entry_id": 286,
                "date": "2025-04-28",
                "meal": "Lunch",
                "food_id": 8,
                "food_name": "Broccoli (steamed)",
                "brand": "",
                "serving_size": "1",
                "serving_unit": "cup",
                "servings": 1.0,
                "calories": 55.0,
                "total_fat_g": 0.6,
                "saturated_fat_g": 0.1,
                "cholesterol_mg": 0.0,
                "sodium_mg": 64.0,
                "total_carbs_g": 11.0,
                "dietary_fiber_g": 5.1,
                "sugars_g": 2.2,
                "protein_g": 3.7
            }
        ],
        "Dinner": [
            {
                "entry_id": 287,
                "date": "2025-04-28",
                "meal": "Dinner",
                "food_id": 17,
                "food_name": "Ground Turkey (93% lean)",
                "brand": "",
                "serving_size": "4",
                "serving_unit": "oz",
                "servings": 1.5,
                "calories": 255.0,
                "total_fat_g": 13.5,
                "saturated_fat_g": 3.8,
                "cholesterol_mg": 120.0,
                "sodium_mg": 120.0,
                "total_carbs_g": 0.0,
                "dietary_fiber_g": 0.0,
                "sugars_g": 0.0,
                "protein_g": 31.5
            },
            {
                "entry_id": 288,
                "date": "2025-04-28",
                "meal": "Dinner",
                "food_id": 28,
                "food_name": "Spaghetti (whole wheat cooked)",
                "brand": "",
                "serving_size": "1",
                "serving_unit": "cup",
                "servings": 1.0,
                "calories": 174.0,
                "total_fat_g": 0.8,
                "saturated_fat_g": 0.1,
                "cholesterol_mg": 0.0,
                "sodium_mg": 4.0,
                "total_carbs_g": 37.0,
                "dietary_fiber_g": 6.3,
                "sugars_g": 0.8,
                "protein_g": 7.5
            },
            {
                "entry_id": 289,
                "date": "2025-04-28",
                "meal": "Dinner",
                "food_id": 29,
                "food_name": "Marinara Sauce",
                "brand": "Rao's Homemade",
                "serving_size": "0.5",
                "serving_unit": "cup (125g)",
                "servings": 1.0,
                "calories": 80.0,
                "total_fat_g": 5.0,
                "saturated_fat_g": 0.5,
                "cholesterol_mg": 0.0,
                "sodium_mg": 390.0,
                "total_carbs_g": 7.0,
                "dietary_fiber_g": 2.0,
                "sugars_g": 5.0,
                "protein_g": 1.0
            }
        ],
        "Snacks": [
            {
                "entry_id": 290,
                "date": "2025-04-28",
                "meal": "Snacks",
                "food_id": 18,
                "food_name": "Protein Shake (whey)",
                "brand": "Optimum Nutrition",
                "serving_size": "1",
                "serving_unit": "scoop (31g)",
                "servings": 1.0,
                "calories": 120.0,
                "total_fat_g": 1.5,
                "saturated_fat_g": 0.5,
                "cholesterol_mg": 30.0,
                "sodium_mg": 130.0,
                "total_carbs_g": 3.0,
                "dietary_fiber_g": 1.0,
                "sugars_g": 1.0,
                "protein_g": 24.0
            },
            {
                "entry_id": 291,
                "date": "2025-04-28",
                "meal": "Snacks",
                "food_id": 19,
                "food_name": "Apple",
                "brand": "",
                "serving_size": "1",
                "serving_unit": "medium (182g)",
                "servings": 1.0,
                "calories": 95.0,
                "total_fat_g": 0.3,
                "saturated_fat_g": 0.1,
                "cholesterol_mg": 0.0,
                "sodium_mg": 2.0,
                "total_carbs_g": 25.0,
                "dietary_fiber_g": 4.4,
                "sugars_g": 19.0,
                "protein_g": 0.5
            }
        ]
    },
    "totals": {
        "calories": 1720.0,
        "total_fat_g": 51.2,
        "saturated_fat_g": 15.5,
        "cholesterol_mg": 678.0,
        "sodium_mg": 1489.0,
        "total_carbs_g": 173.7,
        "dietary_fiber_g": 32.3,
        "sugars_g": 39.4,
        "protein_g": 149.3
    }
}
```

---

## 12. GET /v1/user/diary/2025-04-28?meal=Breakfast (Get diary - meal filter)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/diary/2025-04-28?meal=Breakfast
```

**Status:** 200

```json
{
    "type": "diary",
    "date": "2025-04-28",
    "meals": {
        "Breakfast": [
            {
                "entry_id": 281,
                "date": "2025-04-28",
                "meal": "Breakfast",
                "food_id": 4,
                "food_name": "Large Egg",
                "brand": "",
                "serving_size": "1",
                "serving_unit": "large",
                "servings": 2.0,
                "calories": 144.0,
                "total_fat_g": 10.0,
                "saturated_fat_g": 3.2,
                "cholesterol_mg": 372.0,
                "sodium_mg": 142.0,
                "total_carbs_g": 0.8,
                "dietary_fiber_g": 0.0,
                "sugars_g": 0.4,
                "protein_g": 12.6
            },
            {
                "entry_id": 282,
                "date": "2025-04-28",
                "meal": "Breakfast",
                "food_id": 6,
                "food_name": "Dave's Killer Bread (21 Whole Grains)",
                "brand": "Dave's Killer Bread",
                "serving_size": "1",
                "serving_unit": "slice (45g)",
                "servings": 2.0,
                "calories": 220.0,
                "total_fat_g": 3.0,
                "saturated_fat_g": 0.0,
                "cholesterol_mg": 0.0,
                "sodium_mg": 340.0,
                "total_carbs_g": 44.0,
                "dietary_fiber_g": 10.0,
                "sugars_g": 10.0,
                "protein_g": 10.0
            },
            {
                "entry_id": 283,
                "date": "2025-04-28",
                "meal": "Breakfast",
                "food_id": 30,
                "food_name": "Cheddar Cheese",
                "brand": "",
                "serving_size": "1",
                "serving_unit": "oz (28g)",
                "servings": 1.0,
                "calories": 113.0,
                "total_fat_g": 9.3,
                "saturated_fat_g": 5.3,
                "cholesterol_mg": 28.0,
                "sodium_mg": 176.0,
                "total_carbs_g": 0.9,
                "dietary_fiber_g": 0.0,
                "sugars_g": 0.3,
                "protein_g": 7.0
            }
        ],
        "Lunch": [],
        "Dinner": [],
        "Snacks": []
    },
    "totals": {
        "calories": 477.0,
        "total_fat_g": 22.3,
        "saturated_fat_g": 8.5,
        "cholesterol_mg": 400.0,
        "sodium_mg": 658.0,
        "total_carbs_g": 45.7,
        "dietary_fiber_g": 10.0,
        "sugars_g": 10.7,
        "protein_g": 29.6
    }
}
```

---

## 13. GET /v1/user/diary/2020-01-01 (Get diary - no entries)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/diary/2020-01-01
```

**Status:** 200

```json
{
    "type": "diary",
    "date": "2020-01-01",
    "meals": {
        "Breakfast": [],
        "Lunch": [],
        "Dinner": [],
        "Snacks": []
    },
    "totals": {
        "calories": 0,
        "total_fat_g": 0,
        "saturated_fat_g": 0,
        "cholesterol_mg": 0,
        "sodium_mg": 0,
        "total_carbs_g": 0,
        "dietary_fiber_g": 0,
        "sugars_g": 0,
        "protein_g": 0
    }
}
```

---

## 14. GET /v1/user/diary?start_date=2025-04-25&end_date=2025-04-28 (Get diary range)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/diary?start_date=2025-04-25&end_date=2025-04-28
```

**Status:** 200

```json
{
    "type": "diary_range",
    "start_date": "2025-04-25",
    "end_date": "2025-04-28",
    "count": 4,
    "results": [
        {
            "date": "2025-04-25",
            "meals": {
                "Breakfast": [
                    {
                        "entry_id": 253,
                        "date": "2025-04-25",
                        "meal": "Breakfast",
                        "food_id": 33,
                        "food_name": "Protein Pancakes (homemade)",
                        "brand": "",
                        "serving_size": "3",
                        "serving_unit": "pancakes",
                        "servings": 1.0,
                        "calories": 320.0,
                        "total_fat_g": 8.0,
                        "saturated_fat_g": 2.0,
                        "cholesterol_mg": 95.0,
                        "sodium_mg": 480.0,
                        "total_carbs_g": 32.0,
                        "dietary_fiber_g": 3.0,
                        "sugars_g": 6.0,
                        "protein_g": 30.0
                    },
                    {
                        "entry_id": 254,
                        "date": "2025-04-25",
                        "meal": "Breakfast",
                        "food_id": 39,
                        "food_name": "Blueberries (fresh)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup (148g)",
                        "servings": 0.5,
                        "calories": 42.0,
                        "total_fat_g": 0.3,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 1.0,
                        "total_carbs_g": 10.5,
                        "dietary_fiber_g": 1.8,
                        "sugars_g": 7.5,
                        "protein_g": 0.6
                    }
                ],
                "Lunch": [
                    {
                        "entry_id": 255,
                        "date": "2025-04-25",
                        "meal": "Lunch",
                        "food_id": 32,
                        "food_name": "Turkey Sandwich (whole wheat)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "sandwich",
                        "servings": 1.0,
                        "calories": 350.0,
                        "total_fat_g": 8.0,
                        "saturated_fat_g": 2.5,
                        "cholesterol_mg": 45.0,
                        "sodium_mg": 890.0,
                        "total_carbs_g": 42.0,
                        "dietary_fiber_g": 5.0,
                        "sugars_g": 6.0,
                        "protein_g": 24.0
                    },
                    {
                        "entry_id": 256,
                        "date": "2025-04-25",
                        "meal": "Lunch",
                        "food_id": 19,
                        "food_name": "Apple",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "medium (182g)",
                        "servings": 1.0,
                        "calories": 95.0,
                        "total_fat_g": 0.3,
                        "saturated_fat_g": 0.1,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 2.0,
                        "total_carbs_g": 25.0,
                        "dietary_fiber_g": 4.4,
                        "sugars_g": 19.0,
                        "protein_g": 0.5
                    }
                ],
                "Dinner": [
                    {
                        "entry_id": 257,
                        "date": "2025-04-25",
                        "meal": "Dinner",
                        "food_id": 10,
                        "food_name": "Salmon Fillet (baked)",
                        "brand": "",
                        "serving_size": "4",
                        "serving_unit": "oz",
                        "servings": 1.0,
                        "calories": 233.0,
                        "total_fat_g": 14.0,
                        "saturated_fat_g": 2.6,
                        "cholesterol_mg": 63.0,
                        "sodium_mg": 62.0,
                        "total_carbs_g": 0.0,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.0,
                        "protein_g": 25.0
                    },
                    {
                        "entry_id": 258,
                        "date": "2025-04-25",
                        "meal": "Dinner",
                        "food_id": 2,
                        "food_name": "Brown Rice (cooked)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup",
                        "servings": 1.0,
                        "calories": 216.0,
                        "total_fat_g": 1.8,
                        "saturated_fat_g": 0.4,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 10.0,
                        "total_carbs_g": 45.0,
                        "dietary_fiber_g": 3.5,
                        "sugars_g": 0.7,
                        "protein_g": 5.0
                    },
                    {
                        "entry_id": 259,
                        "date": "2025-04-25",
                        "meal": "Dinner",
                        "food_id": 8,
                        "food_name": "Broccoli (steamed)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup",
                        "servings": 1.0,
                        "calories": 55.0,
                        "total_fat_g": 0.6,
                        "saturated_fat_g": 0.1,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 64.0,
                        "total_carbs_g": 11.0,
                        "dietary_fiber_g": 5.1,
                        "sugars_g": 2.2,
                        "protein_g": 3.7
                    }
                ],
                "Snacks": [
                    {
                        "entry_id": 260,
                        "date": "2025-04-25",
                        "meal": "Snacks",
                        "food_id": 18,
                        "food_name": "Protein Shake (whey)",
                        "brand": "Optimum Nutrition",
                        "serving_size": "1",
                        "serving_unit": "scoop (31g)",
                        "servings": 1.0,
                        "calories": 120.0,
                        "total_fat_g": 1.5,
                        "saturated_fat_g": 0.5,
                        "cholesterol_mg": 30.0,
                        "sodium_mg": 130.0,
                        "total_carbs_g": 3.0,
                        "dietary_fiber_g": 1.0,
                        "sugars_g": 1.0,
                        "protein_g": 24.0
                    },
                    {
                        "entry_id": 261,
                        "date": "2025-04-25",
                        "meal": "Snacks",
                        "food_id": 3,
                        "food_name": "Banana",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "medium (118g)",
                        "servings": 1.0,
                        "calories": 105.0,
                        "total_fat_g": 0.4,
                        "saturated_fat_g": 0.1,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 1.0,
                        "total_carbs_g": 27.0,
                        "dietary_fiber_g": 3.1,
                        "sugars_g": 14.4,
                        "protein_g": 1.3
                    }
                ]
            },
            "totals": {
                "calories": 1536.0,
                "total_fat_g": 34.9,
                "saturated_fat_g": 8.3,
                "cholesterol_mg": 233.0,
                "sodium_mg": 1640.0,
                "total_carbs_g": 195.5,
                "dietary_fiber_g": 26.9,
                "sugars_g": 56.8,
                "protein_g": 114.1
            }
        },
        {
            "date": "2025-04-26",
            "meals": {
                "Breakfast": [
                    {
                        "entry_id": 262,
                        "date": "2025-04-26",
                        "meal": "Breakfast",
                        "food_id": 4,
                        "food_name": "Large Egg",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "large",
                        "servings": 2.0,
                        "calories": 144.0,
                        "total_fat_g": 10.0,
                        "saturated_fat_g": 3.2,
                        "cholesterol_mg": 372.0,
                        "sodium_mg": 142.0,
                        "total_carbs_g": 0.8,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.4,
                        "protein_g": 12.6
                    },
                    {
                        "entry_id": 263,
                        "date": "2025-04-26",
                        "meal": "Breakfast",
                        "food_id": 6,
                        "food_name": "Dave's Killer Bread (21 Whole Grains)",
                        "brand": "Dave's Killer Bread",
                        "serving_size": "1",
                        "serving_unit": "slice (45g)",
                        "servings": 2.0,
                        "calories": 220.0,
                        "total_fat_g": 3.0,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 340.0,
                        "total_carbs_g": 44.0,
                        "dietary_fiber_g": 10.0,
                        "sugars_g": 10.0,
                        "protein_g": 10.0
                    },
                    {
                        "entry_id": 264,
                        "date": "2025-04-26",
                        "meal": "Breakfast",
                        "food_id": 11,
                        "food_name": "Avocado",
                        "brand": "",
                        "serving_size": "0.5",
                        "serving_unit": "medium",
                        "servings": 1.0,
                        "calories": 120.0,
                        "total_fat_g": 11.0,
                        "saturated_fat_g": 1.5,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 5.0,
                        "total_carbs_g": 6.0,
                        "dietary_fiber_g": 5.0,
                        "sugars_g": 0.5,
                        "protein_g": 1.5
                    }
                ],
                "Lunch": [
                    {
                        "entry_id": 265,
                        "date": "2025-04-26",
                        "meal": "Lunch",
                        "food_id": 21,
                        "food_name": "Chipotle Burrito Bowl (Chicken)",
                        "brand": "Chipotle",
                        "serving_size": "1",
                        "serving_unit": "bowl",
                        "servings": 1.0,
                        "calories": 665.0,
                        "total_fat_g": 22.0,
                        "saturated_fat_g": 8.0,
                        "cholesterol_mg": 120.0,
                        "sodium_mg": 1695.0,
                        "total_carbs_g": 60.0,
                        "dietary_fiber_g": 12.0,
                        "sugars_g": 5.0,
                        "protein_g": 50.0
                    }
                ],
                "Dinner": [
                    {
                        "entry_id": 266,
                        "date": "2025-04-26",
                        "meal": "Dinner",
                        "food_id": 35,
                        "food_name": "Beef Stir Fry (homemade)",
                        "brand": "",
                        "serving_size": "1.5",
                        "serving_unit": "cups",
                        "servings": 1.0,
                        "calories": 380.0,
                        "total_fat_g": 15.0,
                        "saturated_fat_g": 4.0,
                        "cholesterol_mg": 75.0,
                        "sodium_mg": 780.0,
                        "total_carbs_g": 22.0,
                        "dietary_fiber_g": 4.0,
                        "sugars_g": 8.0,
                        "protein_g": 35.0
                    },
                    {
                        "entry_id": 267,
                        "date": "2025-04-26",
                        "meal": "Dinner",
                        "food_id": 24,
                        "food_name": "White Rice (cooked)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup",
                        "servings": 1.0,
                        "calories": 206.0,
                        "total_fat_g": 0.4,
                        "saturated_fat_g": 0.1,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 2.0,
                        "total_carbs_g": 45.0,
                        "dietary_fiber_g": 0.6,
                        "sugars_g": 0.1,
                        "protein_g": 4.3
                    }
                ],
                "Snacks": [
                    {
                        "entry_id": 268,
                        "date": "2025-04-26",
                        "meal": "Snacks",
                        "food_id": 34,
                        "food_name": "Trail Mix",
                        "brand": "",
                        "serving_size": "0.25",
                        "serving_unit": "cup (35g)",
                        "servings": 1.0,
                        "calories": 175.0,
                        "total_fat_g": 11.0,
                        "saturated_fat_g": 1.5,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 45.0,
                        "total_carbs_g": 15.0,
                        "dietary_fiber_g": 2.0,
                        "sugars_g": 9.0,
                        "protein_g": 5.0
                    },
                    {
                        "entry_id": 269,
                        "date": "2025-04-26",
                        "meal": "Snacks",
                        "food_id": 37,
                        "food_name": "Iced Coffee (black)",
                        "brand": "",
                        "serving_size": "16",
                        "serving_unit": "oz",
                        "servings": 1.0,
                        "calories": 5.0,
                        "total_fat_g": 0.0,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 10.0,
                        "total_carbs_g": 0.0,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.0,
                        "protein_g": 0.5
                    }
                ]
            },
            "totals": {
                "calories": 1915.0,
                "total_fat_g": 72.4,
                "saturated_fat_g": 18.3,
                "cholesterol_mg": 567.0,
                "sodium_mg": 3019.0,
                "total_carbs_g": 192.8,
                "dietary_fiber_g": 33.6,
                "sugars_g": 33.0,
                "protein_g": 118.9
            }
        },
        {
            "date": "2025-04-27",
            "meals": {
                "Breakfast": [
                    {
                        "entry_id": 270,
                        "date": "2025-04-27",
                        "meal": "Breakfast",
                        "food_id": 13,
                        "food_name": "Oatmeal (cooked)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup",
                        "servings": 1.0,
                        "calories": 154.0,
                        "total_fat_g": 2.6,
                        "saturated_fat_g": 0.4,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 9.0,
                        "total_carbs_g": 27.0,
                        "dietary_fiber_g": 4.0,
                        "sugars_g": 1.1,
                        "protein_g": 5.4
                    },
                    {
                        "entry_id": 271,
                        "date": "2025-04-27",
                        "meal": "Breakfast",
                        "food_id": 20,
                        "food_name": "Peanut Butter (natural)",
                        "brand": "Smucker's Natural",
                        "serving_size": "2",
                        "serving_unit": "tbsp (32g)",
                        "servings": 1.0,
                        "calories": 190.0,
                        "total_fat_g": 16.0,
                        "saturated_fat_g": 2.5,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 65.0,
                        "total_carbs_g": 7.0,
                        "dietary_fiber_g": 2.0,
                        "sugars_g": 3.0,
                        "protein_g": 7.0
                    },
                    {
                        "entry_id": 272,
                        "date": "2025-04-27",
                        "meal": "Breakfast",
                        "food_id": 39,
                        "food_name": "Blueberries (fresh)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup (148g)",
                        "servings": 1.0,
                        "calories": 84.0,
                        "total_fat_g": 0.5,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 1.0,
                        "total_carbs_g": 21.0,
                        "dietary_fiber_g": 3.6,
                        "sugars_g": 15.0,
                        "protein_g": 1.1
                    }
                ],
                "Lunch": [
                    {
                        "entry_id": 273,
                        "date": "2025-04-27",
                        "meal": "Lunch",
                        "food_id": 1,
                        "food_name": "Grilled Chicken Breast",
                        "brand": "",
                        "serving_size": "4",
                        "serving_unit": "oz",
                        "servings": 1.5,
                        "calories": 248.0,
                        "total_fat_g": 5.4,
                        "saturated_fat_g": 1.5,
                        "cholesterol_mg": 128.0,
                        "sodium_mg": 111.0,
                        "total_carbs_g": 0.0,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.0,
                        "protein_g": 46.5
                    },
                    {
                        "entry_id": 274,
                        "date": "2025-04-27",
                        "meal": "Lunch",
                        "food_id": 26,
                        "food_name": "Mixed Greens Salad (no dressing)",
                        "brand": "",
                        "serving_size": "2",
                        "serving_unit": "cups",
                        "servings": 1.0,
                        "calories": 18.0,
                        "total_fat_g": 0.2,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 35.0,
                        "total_carbs_g": 3.5,
                        "dietary_fiber_g": 1.8,
                        "sugars_g": 0.8,
                        "protein_g": 1.5
                    },
                    {
                        "entry_id": 275,
                        "date": "2025-04-27",
                        "meal": "Lunch",
                        "food_id": 7,
                        "food_name": "Extra Virgin Olive Oil",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "tbsp",
                        "servings": 1.0,
                        "calories": 119.0,
                        "total_fat_g": 14.0,
                        "saturated_fat_g": 1.9,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 0.0,
                        "total_carbs_g": 0.0,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.0,
                        "protein_g": 0.0
                    }
                ],
                "Dinner": [
                    {
                        "entry_id": 276,
                        "date": "2025-04-27",
                        "meal": "Dinner",
                        "food_id": 10,
                        "food_name": "Salmon Fillet (baked)",
                        "brand": "",
                        "serving_size": "4",
                        "serving_unit": "oz",
                        "servings": 1.0,
                        "calories": 233.0,
                        "total_fat_g": 14.0,
                        "saturated_fat_g": 2.6,
                        "cholesterol_mg": 63.0,
                        "sodium_mg": 62.0,
                        "total_carbs_g": 0.0,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.0,
                        "protein_g": 25.0
                    },
                    {
                        "entry_id": 277,
                        "date": "2025-04-27",
                        "meal": "Dinner",
                        "food_id": 9,
                        "food_name": "Sweet Potato (baked)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "medium (130g)",
                        "servings": 1.0,
                        "calories": 103.0,
                        "total_fat_g": 0.1,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 41.0,
                        "total_carbs_g": 24.0,
                        "dietary_fiber_g": 3.8,
                        "sugars_g": 7.4,
                        "protein_g": 2.3
                    },
                    {
                        "entry_id": 278,
                        "date": "2025-04-27",
                        "meal": "Dinner",
                        "food_id": 15,
                        "food_name": "Baby Spinach",
                        "brand": "",
                        "serving_size": "2",
                        "serving_unit": "cups (60g)",
                        "servings": 1.0,
                        "calories": 14.0,
                        "total_fat_g": 0.2,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 47.0,
                        "total_carbs_g": 2.2,
                        "dietary_fiber_g": 1.3,
                        "sugars_g": 0.3,
                        "protein_g": 1.7
                    }
                ],
                "Snacks": [
                    {
                        "entry_id": 279,
                        "date": "2025-04-27",
                        "meal": "Snacks",
                        "food_id": 22,
                        "food_name": "Quest Protein Bar (Chocolate Chip Cookie Dough)",
                        "brand": "Quest Nutrition",
                        "serving_size": "1",
                        "serving_unit": "bar (60g)",
                        "servings": 1.0,
                        "calories": 200.0,
                        "total_fat_g": 9.0,
                        "saturated_fat_g": 3.5,
                        "cholesterol_mg": 10.0,
                        "sodium_mg": 260.0,
                        "total_carbs_g": 22.0,
                        "dietary_fiber_g": 14.0,
                        "sugars_g": 1.0,
                        "protein_g": 21.0
                    },
                    {
                        "entry_id": 280,
                        "date": "2025-04-27",
                        "meal": "Snacks",
                        "food_id": 37,
                        "food_name": "Iced Coffee (black)",
                        "brand": "",
                        "serving_size": "16",
                        "serving_unit": "oz",
                        "servings": 1.0,
                        "calories": 5.0,
                        "total_fat_g": 0.0,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 10.0,
                        "total_carbs_g": 0.0,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.0,
                        "protein_g": 0.5
                    }
                ]
            },
            "totals": {
                "calories": 1368.0,
                "total_fat_g": 62.0,
                "saturated_fat_g": 12.4,
                "cholesterol_mg": 201.0,
                "sodium_mg": 641.0,
                "total_carbs_g": 106.7,
                "dietary_fiber_g": 30.5,
                "sugars_g": 28.6,
                "protein_g": 112.0
            }
        },
        {
            "date": "2025-04-28",
            "meals": {
                "Breakfast": [
                    {
                        "entry_id": 281,
                        "date": "2025-04-28",
                        "meal": "Breakfast",
                        "food_id": 4,
                        "food_name": "Large Egg",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "large",
                        "servings": 2.0,
                        "calories": 144.0,
                        "total_fat_g": 10.0,
                        "saturated_fat_g": 3.2,
                        "cholesterol_mg": 372.0,
                        "sodium_mg": 142.0,
                        "total_carbs_g": 0.8,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.4,
                        "protein_g": 12.6
                    },
                    {
                        "entry_id": 282,
                        "date": "2025-04-28",
                        "meal": "Breakfast",
                        "food_id": 6,
                        "food_name": "Dave's Killer Bread (21 Whole Grains)",
                        "brand": "Dave's Killer Bread",
                        "serving_size": "1",
                        "serving_unit": "slice (45g)",
                        "servings": 2.0,
                        "calories": 220.0,
                        "total_fat_g": 3.0,
                        "saturated_fat_g": 0.0,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 340.0,
                        "total_carbs_g": 44.0,
                        "dietary_fiber_g": 10.0,
                        "sugars_g": 10.0,
                        "protein_g": 10.0
                    },
                    {
                        "entry_id": 283,
                        "date": "2025-04-28",
                        "meal": "Breakfast",
                        "food_id": 30,
                        "food_name": "Cheddar Cheese",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "oz (28g)",
                        "servings": 1.0,
                        "calories": 113.0,
                        "total_fat_g": 9.3,
                        "saturated_fat_g": 5.3,
                        "cholesterol_mg": 28.0,
                        "sodium_mg": 176.0,
                        "total_carbs_g": 0.9,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.3,
                        "protein_g": 7.0
                    }
                ],
                "Lunch": [
                    {
                        "entry_id": 284,
                        "date": "2025-04-28",
                        "meal": "Lunch",
                        "food_id": 1,
                        "food_name": "Grilled Chicken Breast",
                        "brand": "",
                        "serving_size": "4",
                        "serving_unit": "oz",
                        "servings": 1.5,
                        "calories": 248.0,
                        "total_fat_g": 5.4,
                        "saturated_fat_g": 1.5,
                        "cholesterol_mg": 128.0,
                        "sodium_mg": 111.0,
                        "total_carbs_g": 0.0,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.0,
                        "protein_g": 46.5
                    },
                    {
                        "entry_id": 285,
                        "date": "2025-04-28",
                        "meal": "Lunch",
                        "food_id": 2,
                        "food_name": "Brown Rice (cooked)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup",
                        "servings": 1.0,
                        "calories": 216.0,
                        "total_fat_g": 1.8,
                        "saturated_fat_g": 0.4,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 10.0,
                        "total_carbs_g": 45.0,
                        "dietary_fiber_g": 3.5,
                        "sugars_g": 0.7,
                        "protein_g": 5.0
                    },
                    {
                        "entry_id": 286,
                        "date": "2025-04-28",
                        "meal": "Lunch",
                        "food_id": 8,
                        "food_name": "Broccoli (steamed)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup",
                        "servings": 1.0,
                        "calories": 55.0,
                        "total_fat_g": 0.6,
                        "saturated_fat_g": 0.1,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 64.0,
                        "total_carbs_g": 11.0,
                        "dietary_fiber_g": 5.1,
                        "sugars_g": 2.2,
                        "protein_g": 3.7
                    }
                ],
                "Dinner": [
                    {
                        "entry_id": 287,
                        "date": "2025-04-28",
                        "meal": "Dinner",
                        "food_id": 17,
                        "food_name": "Ground Turkey (93% lean)",
                        "brand": "",
                        "serving_size": "4",
                        "serving_unit": "oz",
                        "servings": 1.5,
                        "calories": 255.0,
                        "total_fat_g": 13.5,
                        "saturated_fat_g": 3.8,
                        "cholesterol_mg": 120.0,
                        "sodium_mg": 120.0,
                        "total_carbs_g": 0.0,
                        "dietary_fiber_g": 0.0,
                        "sugars_g": 0.0,
                        "protein_g": 31.5
                    },
                    {
                        "entry_id": 288,
                        "date": "2025-04-28",
                        "meal": "Dinner",
                        "food_id": 28,
                        "food_name": "Spaghetti (whole wheat cooked)",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "cup",
                        "servings": 1.0,
                        "calories": 174.0,
                        "total_fat_g": 0.8,
                        "saturated_fat_g": 0.1,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 4.0,
                        "total_carbs_g": 37.0,
                        "dietary_fiber_g": 6.3,
                        "sugars_g": 0.8,
                        "protein_g": 7.5
                    },
                    {
                        "entry_id": 289,
                        "date": "2025-04-28",
                        "meal": "Dinner",
                        "food_id": 29,
                        "food_name": "Marinara Sauce",
                        "brand": "Rao's Homemade",
                        "serving_size": "0.5",
                        "serving_unit": "cup (125g)",
                        "servings": 1.0,
                        "calories": 80.0,
                        "total_fat_g": 5.0,
                        "saturated_fat_g": 0.5,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 390.0,
                        "total_carbs_g": 7.0,
                        "dietary_fiber_g": 2.0,
                        "sugars_g": 5.0,
                        "protein_g": 1.0
                    }
                ],
                "Snacks": [
                    {
                        "entry_id": 290,
                        "date": "2025-04-28",
                        "meal": "Snacks",
                        "food_id": 18,
                        "food_name": "Protein Shake (whey)",
                        "brand": "Optimum Nutrition",
                        "serving_size": "1",
                        "serving_unit": "scoop (31g)",
                        "servings": 1.0,
                        "calories": 120.0,
                        "total_fat_g": 1.5,
                        "saturated_fat_g": 0.5,
                        "cholesterol_mg": 30.0,
                        "sodium_mg": 130.0,
                        "total_carbs_g": 3.0,
                        "dietary_fiber_g": 1.0,
                        "sugars_g": 1.0,
                        "protein_g": 24.0
                    },
                    {
                        "entry_id": 291,
                        "date": "2025-04-28",
                        "meal": "Snacks",
                        "food_id": 19,
                        "food_name": "Apple",
                        "brand": "",
                        "serving_size": "1",
                        "serving_unit": "medium (182g)",
                        "servings": 1.0,
                        "calories": 95.0,
                        "total_fat_g": 0.3,
                        "saturated_fat_g": 0.1,
                        "cholesterol_mg": 0.0,
                        "sodium_mg": 2.0,
                        "total_carbs_g": 25.0,
                        "dietary_fiber_g": 4.4,
                        "sugars_g": 19.0,
                        "protein_g": 0.5
                    }
                ]
            },
            "totals": {
                "calories": 1720.0,
                "total_fat_g": 51.2,
                "saturated_fat_g": 15.5,
                "cholesterol_mg": 678.0,
                "sodium_mg": 1489.0,
                "total_carbs_g": 173.7,
                "dietary_fiber_g": 32.3,
                "sugars_g": 39.4,
                "protein_g": 149.3
            }
        }
    ]
}
```

---

## 15. POST /v1/user/diary (Log food entry)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"date": "2025-04-28", "meal": "Snacks", "food_id": 3, "servings": 1.0}' http://localhost:8006/v1/user/diary
```

**Status:** 201

```json
{
    "type": "diary_entry",
    "diary_entry": {
        "entry_id": 292,
        "date": "2025-04-28",
        "meal": "Snacks",
        "food_id": 3,
        "food_name": "Banana",
        "brand": "",
        "serving_size": "1",
        "serving_unit": "medium (118g)",
        "servings": 1.0,
        "calories": 105.0,
        "total_fat_g": 0.4,
        "saturated_fat_g": 0.1,
        "cholesterol_mg": 0.0,
        "sodium_mg": 1.0,
        "total_carbs_g": 27.0,
        "dietary_fiber_g": 3.1,
        "sugars_g": 14.4,
        "protein_g": 1.3
    }
}
```

---

## 16. POST /v1/user/diary (Log food entry - bad food_id)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"date": "2025-04-28", "meal": "Lunch", "food_id": 9999, "servings": 1.0}' http://localhost:8006/v1/user/diary
```

**Status:** 400

```json
{
    "error": "Food 9999 not found in database"
}
```

---

## 17. PUT /v1/user/diary/1 (Update diary entry)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X PUT -H 'Content-Type: application/json' -d '{"servings": 2.0}' http://localhost:8006/v1/user/diary/1
```

**Status:** 200

```json
{
    "type": "diary_entry",
    "diary_entry": {
        "entry_id": 1,
        "date": "2025-03-30",
        "meal": "Breakfast",
        "food_id": 13,
        "food_name": "Oatmeal (cooked)",
        "brand": "",
        "serving_size": "1",
        "serving_unit": "cup",
        "servings": 2.0,
        "calories": 308.0,
        "total_fat_g": 5.2,
        "saturated_fat_g": 0.8,
        "cholesterol_mg": 0.0,
        "sodium_mg": 18.0,
        "total_carbs_g": 54.0,
        "dietary_fiber_g": 8.0,
        "sugars_g": 2.2,
        "protein_g": 10.8
    }
}
```

---

## 18. PUT /v1/user/diary/99999 (Update diary entry - 404)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X PUT -H 'Content-Type: application/json' -d '{"servings": 2.0}' http://localhost:8006/v1/user/diary/99999
```

**Status:** 404

```json
{
    "error": "Diary entry 99999 not found"
}
```

---

## 19. DELETE /v1/user/diary/291 (Delete diary entry)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X DELETE http://localhost:8006/v1/user/diary/291
```

**Status:** 200

```json
{
    "type": "diary_entry",
    "deleted": true,
    "entry_id": 291
}
```

---

## 20. DELETE /v1/user/diary/99999 (Delete diary entry - 404)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X DELETE http://localhost:8006/v1/user/diary/99999
```

**Status:** 404

```json
{
    "error": "Diary entry 99999 not found"
}
```

---

## 21. GET /v1/user/nutrition/2025-04-28 (Get daily totals)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/nutrition/2025-04-28
```

**Status:** 200

```json
{
    "type": "daily_totals",
    "date": "2025-04-28",
    "totals": {
        "calories": 1730.0,
        "total_fat_g": 51.3,
        "saturated_fat_g": 15.5,
        "cholesterol_mg": 678.0,
        "sodium_mg": 1488.0,
        "total_carbs_g": 175.7,
        "dietary_fiber_g": 31.0,
        "sugars_g": 34.8,
        "protein_g": 150.1
    },
    "goal": {
        "calories": 1900,
        "total_fat_g": 50,
        "saturated_fat_g": 16,
        "cholesterol_mg": 300,
        "sodium_mg": 2300,
        "total_carbs_g": 180,
        "dietary_fiber_g": 30,
        "sugars_g": 50,
        "protein_g": 158,
        "potassium_mg": 3500,
        "vitamin_a_pct": 100,
        "vitamin_c_pct": 100,
        "calcium_pct": 100,
        "iron_pct": 100
    },
    "remaining": {
        "calories": 170.0,
        "total_fat_g": -1.3,
        "saturated_fat_g": 0.5,
        "cholesterol_mg": -378.0,
        "sodium_mg": 812.0,
        "total_carbs_g": 4.3,
        "dietary_fiber_g": -1.0,
        "sugars_g": 15.2,
        "protein_g": 7.9
    }
}
```

---

## 22. GET /v1/user/nutrition/2020-01-01 (Get daily totals - no data)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/nutrition/2020-01-01
```

**Status:** 200

```json
{
    "type": "daily_totals",
    "date": "2020-01-01",
    "totals": {
        "calories": 0,
        "total_fat_g": 0,
        "saturated_fat_g": 0,
        "cholesterol_mg": 0,
        "sodium_mg": 0,
        "total_carbs_g": 0,
        "dietary_fiber_g": 0,
        "sugars_g": 0,
        "protein_g": 0
    },
    "goal": {
        "calories": 1900,
        "total_fat_g": 50,
        "saturated_fat_g": 16,
        "cholesterol_mg": 300,
        "sodium_mg": 2300,
        "total_carbs_g": 180,
        "dietary_fiber_g": 30,
        "sugars_g": 50,
        "protein_g": 158,
        "potassium_mg": 3500,
        "vitamin_a_pct": 100,
        "vitamin_c_pct": 100,
        "calcium_pct": 100,
        "iron_pct": 100
    },
    "remaining": {
        "calories": 1900,
        "total_fat_g": 50,
        "saturated_fat_g": 16,
        "cholesterol_mg": 300,
        "sodium_mg": 2300,
        "total_carbs_g": 180,
        "dietary_fiber_g": 30,
        "sugars_g": 50,
        "protein_g": 158,
        "potassium_mg": 3500,
        "vitamin_a_pct": 100,
        "vitamin_c_pct": 100,
        "calcium_pct": 100,
        "iron_pct": 100
    }
}
```

---

## 23. GET /v1/user/nutrition/weekly/2025-04-28 (Get weekly summary)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/nutrition/weekly/2025-04-28
```

**Status:** 200

```json
{
    "type": "weekly_summary",
    "start_date": "2025-04-22",
    "end_date": "2025-04-28",
    "averages": {
        "calories": 1559.6,
        "protein_g": 122.1,
        "total_carbs_g": 155.4,
        "total_fat_g": 52.7
    },
    "days": [
        {
            "date": "2025-04-22",
            "totals": {
                "calories": 1608.0,
                "total_fat_g": 39.1,
                "saturated_fat_g": 7.8,
                "cholesterol_mg": 530.0,
                "sodium_mg": 1624.0,
                "total_carbs_g": 196.8,
                "dietary_fiber_g": 49.0,
                "sugars_g": 42.8,
                "protein_g": 126.8
            },
            "entry_count": 10
        },
        {
            "date": "2025-04-23",
            "totals": {
                "calories": 1446.0,
                "total_fat_g": 65.9,
                "saturated_fat_g": 16.7,
                "cholesterol_mg": 210.0,
                "sodium_mg": 1582.0,
                "total_carbs_g": 110.5,
                "dietary_fiber_g": 19.2,
                "sugars_g": 25.1,
                "protein_g": 111.2
            },
            "entry_count": 10
        },
        {
            "date": "2025-04-24",
            "totals": {
                "calories": 1314.0,
                "total_fat_g": 43.0,
                "saturated_fat_g": 5.9,
                "cholesterol_mg": 388.0,
                "sodium_mg": 1526.0,
                "total_carbs_g": 109.9,
                "dietary_fiber_g": 18.8,
                "sugars_g": 29.0,
                "protein_g": 121.5
            },
            "entry_count": 10
        },
        {
            "date": "2025-04-25",
            "totals": {
                "calories": 1536.0,
                "total_fat_g": 34.9,
                "saturated_fat_g": 8.3,
                "cholesterol_mg": 233.0,
                "sodium_mg": 1640.0,
                "total_carbs_g": 195.5,
                "dietary_fiber_g": 26.9,
                "sugars_g": 56.8,
                "protein_g": 114.1
            },
            "entry_count": 9
        },
        {
            "date": "2025-04-26",
            "totals": {
                "calories": 1915.0,
                "total_fat_g": 72.4,
                "saturated_fat_g": 18.3,
                "cholesterol_mg": 567.0,
                "sodium_mg": 3019.0,
                "total_carbs_g": 192.8,
                "dietary_fiber_g": 33.6,
                "sugars_g": 33.0,
                "protein_g": 118.9
            },
            "entry_count": 8
        },
        {
            "date": "2025-04-27",
            "totals": {
                "calories": 1368.0,
                "total_fat_g": 62.0,
                "saturated_fat_g": 12.4,
                "cholesterol_mg": 201.0,
                "sodium_mg": 641.0,
                "total_carbs_g": 106.7,
                "dietary_fiber_g": 30.5,
                "sugars_g": 28.6,
                "protein_g": 112.0
            },
            "entry_count": 11
        },
        {
            "date": "2025-04-28",
            "totals": {
                "calories": 1730.0,
                "total_fat_g": 51.3,
                "saturated_fat_g": 15.5,
                "cholesterol_mg": 678.0,
                "sodium_mg": 1488.0,
                "total_carbs_g": 175.7,
                "dietary_fiber_g": 31.0,
                "sugars_g": 34.8,
                "protein_g": 150.1
            },
            "entry_count": 11
        }
    ]
}
```

---

## 24. GET /v1/user/progress?days=30 (Get progress (30 days))

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/progress?days=30
```

**Status:** 200

```json
{
    "type": "progress",
    "period_days": 30,
    "calorie_goal": 1900,
    "results": [
        {
            "date": "2025-03-30",
            "calories_consumed": 1631.0,
            "calories_burned": 385,
            "net_calories": 1246.0,
            "protein_g": 117.8,
            "total_carbs_g": 200.2,
            "total_fat_g": 42.0
        },
        {
            "date": "2025-03-31",
            "calories_consumed": 1638.0,
            "calories_burned": 270,
            "net_calories": 1368.0,
            "protein_g": 119.6,
            "total_carbs_g": 165.8,
            "total_fat_g": 59.1
        },
        {
            "date": "2025-04-01",
            "calories_consumed": 1811.0,
            "calories_burned": 320,
            "net_calories": 1491.0,
            "protein_g": 159.3,
            "total_carbs_g": 189.5,
            "total_fat_g": 48.6
        },
        {
            "date": "2025-04-02",
            "calories_consumed": 1543.0,
            "calories_burned": 0,
            "net_calories": 1543.0,
            "protein_g": 102.0,
            "total_carbs_g": 146.5,
            "total_fat_g": 61.0
        },
        {
            "date": "2025-04-03",
            "calories_consumed": 1413.0,
            "calories_burned": 330,
            "net_calories": 1083.0,
            "protein_g": 100.5,
            "total_carbs_g": 168.5,
            "total_fat_g": 39.8
        },
        {
            "date": "2025-04-04",
            "calories_consumed": 1460.0,
            "calories_burned": 300,
            "net_calories": 1160.0,
            "protein_g": 127.6,
            "total_carbs_g": 130.0,
            "total_fat_g": 54.3
        },
        {
            "date": "2025-04-05",
            "calories_consumed": 1905.0,
            "calories_burned": 285,
            "net_calories": 1620.0,
            "protein_g": 148.1,
            "total_carbs_g": 191.2,
            "total_fat_g": 59.3
        },
        {
            "date": "2025-04-06",
            "calories_consumed": 1971.0,
            "calories_burned": 0,
            "net_calories": 1971.0,
            "protein_g": 134.9,
            "total_carbs_g": 159.7,
            "total_fat_g": 88.3
        },
        {
            "date": "2025-04-07",
            "calories_consumed": 1490.0,
            "calories_burned": 440,
            "net_calories": 1050.0,
            "protein_g": 103.5,
            "total_carbs_g": 166.0,
            "total_fat_g": 48.5
        },
        {
            "date": "2025-04-08",
            "calories_consumed": 1409.0,
            "calories_burned": 270,
            "net_calories": 1139.0,
            "protein_g": 132.6,
            "total_carbs_g": 81.8,
            "total_fat_g": 63.8
        },
        {
            "date": "2025-04-09",
            "calories_consumed": 1574.0,
            "calories_burned": 0,
            "net_calories": 1574.0,
            "protein_g": 110.3,
            "total_carbs_g": 214.0,
            "total_fat_g": 29.6
        },
        {
            "date": "2025-04-10",
            "calories_consumed": 1431.0,
            "calories_burned": 280,
            "net_calories": 1151.0,
            "protein_g": 123.3,
            "total_carbs_g": 102.9,
            "total_fat_g": 60.3
        },
        {
            "date": "2025-04-11",
            "calories_consumed": 1777.0,
            "calories_burned": 300,
            "net_calories": 1477.0,
            "protein_g": 136.1,
            "total_carbs_g": 173.8,
            "total_fat_g": 62.0
        },
        {
            "date": "2025-04-12",
            "calories_consumed": 2248.0,
            "calories_burned": 585,
            "net_calories": 1663.0,
            "protein_g": 130.7,
            "total_carbs_g": 215.0,
            "total_fat_g": 95.6
        },
        {
            "date": "2025-04-13",
            "calories_consumed": 2192.0,
            "calories_burned": 0,
            "net_calories": 2192.0,
            "protein_g": 151.9,
            "total_carbs_g": 231.5,
            "total_fat_g": 71.3
        },
        {
            "date": "2025-04-14",
            "calories_consumed": 1590.0,
            "calories_burned": 385,
            "net_calories": 1205.0,
            "protein_g": 129.7,
            "total_carbs_g": 180.6,
            "total_fat_g": 40.9
        },
        {
            "date": "2025-04-15",
            "calories_consumed": 1449.0,
            "calories_burned": 270,
            "net_calories": 1179.0,
            "protein_g": 128.7,
            "total_carbs_g": 134.4,
            "total_fat_g": 49.7
        },
        {
            "date": "2025-04-16",
            "calories_consumed": 1510.0,
            "calories_burned": 0,
            "net_calories": 1510.0,
            "protein_g": 106.3,
            "total_carbs_g": 177.7,
            "total_fat_g": 42.5
        },
        {
            "date": "2025-04-17",
            "calories_consumed": 1462.0,
            "calories_burned": 495,
            "net_calories": 967.0,
            "protein_g": 132.1,
            "total_carbs_g": 103.3,
            "total_fat_g": 60.4
        },
        {
            "date": "2025-04-18",
            "calories_consumed": 1482.0,
            "calories_burned": 240,
            "net_calories": 1242.0,
            "protein_g": 103.9,
            "total_carbs_g": 149.2,
            "total_fat_g": 55.1
        },
        {
            "date": "2025-04-19",
            "calories_consumed": 2420.0,
            "calories_burned": 0,
            "net_calories": 2420.0,
            "protein_g": 152.9,
            "total_carbs_g": 252.5,
            "total_fat_g": 87.2
        },
        {
            "date": "2025-04-20",
            "calories_consumed": 2611.0,
            "calories_burned": 214,
            "net_calories": 2397.0,
            "protein_g": 162.7,
            "total_carbs_g": 280.5,
            "total_fat_g": 93.6
        },
        {
            "date": "2025-04-21",
            "calories_consumed": 1400.0,
            "calories_burned": 330,
            "net_calories": 1070.0,
            "protein_g": 127.1,
            "total_carbs_g": 154.0,
            "total_fat_g": 35.4
        },
        {
            "date": "2025-04-22",
            "calories_consumed": 1608.0,
            "calories_burned": 300,
            "net_calories": 1308.0,
            "protein_g": 126.8,
            "total_carbs_g": 196.8,
            "total_fat_g": 39.1
        },
        {
            "date": "2025-04-23",
            "calories_consumed": 1446.0,
            "calories_burned": 0,
            "net_calories": 1446.0,
            "protein_g": 111.2,
            "total_carbs_g": 110.5,
            "total_fat_g": 65.9
        },
        {
            "date": "2025-04-24",
            "calories_consumed": 1314.0,
            "calories_burned": 360,
            "net_calories": 954.0,
            "protein_g": 121.5,
            "total_carbs_g": 109.9,
            "total_fat_g": 43.0
        },
        {
            "date": "2025-04-25",
            "calories_consumed": 1536.0,
            "calories_burned": 270,
            "net_calories": 1266.0,
            "protein_g": 114.1,
            "total_carbs_g": 195.5,
            "total_fat_g": 34.9
        },
        {
            "date": "2025-04-26",
            "calories_consumed": 1915.0,
            "calories_burned": 0,
            "net_calories": 1915.0,
            "protein_g": 118.9,
            "total_carbs_g": 192.8,
            "total_fat_g": 72.4
        },
        {
            "date": "2025-04-27",
            "calories_consumed": 1368.0,
            "calories_burned": 440,
            "net_calories": 928.0,
            "protein_g": 112.0,
            "total_carbs_g": 106.7,
            "total_fat_g": 62.0
        },
        {
            "date": "2025-04-28",
            "calories_consumed": 1730.0,
            "calories_burned": 270,
            "net_calories": 1460.0,
            "protein_g": 150.1,
            "total_carbs_g": 175.7,
            "total_fat_g": 51.3
        }
    ]
}
```

---

## 25. GET /v1/user/progress?days=7 (Get progress (7 days))

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/progress?days=7
```

**Status:** 200

```json
{
    "type": "progress",
    "period_days": 7,
    "calorie_goal": 1900,
    "results": [
        {
            "date": "2025-04-22",
            "calories_consumed": 1608.0,
            "calories_burned": 300,
            "net_calories": 1308.0,
            "protein_g": 126.8,
            "total_carbs_g": 196.8,
            "total_fat_g": 39.1
        },
        {
            "date": "2025-04-23",
            "calories_consumed": 1446.0,
            "calories_burned": 0,
            "net_calories": 1446.0,
            "protein_g": 111.2,
            "total_carbs_g": 110.5,
            "total_fat_g": 65.9
        },
        {
            "date": "2025-04-24",
            "calories_consumed": 1314.0,
            "calories_burned": 360,
            "net_calories": 954.0,
            "protein_g": 121.5,
            "total_carbs_g": 109.9,
            "total_fat_g": 43.0
        },
        {
            "date": "2025-04-25",
            "calories_consumed": 1536.0,
            "calories_burned": 270,
            "net_calories": 1266.0,
            "protein_g": 114.1,
            "total_carbs_g": 195.5,
            "total_fat_g": 34.9
        },
        {
            "date": "2025-04-26",
            "calories_consumed": 1915.0,
            "calories_burned": 0,
            "net_calories": 1915.0,
            "protein_g": 118.9,
            "total_carbs_g": 192.8,
            "total_fat_g": 72.4
        },
        {
            "date": "2025-04-27",
            "calories_consumed": 1368.0,
            "calories_burned": 440,
            "net_calories": 928.0,
            "protein_g": 112.0,
            "total_carbs_g": 106.7,
            "total_fat_g": 62.0
        },
        {
            "date": "2025-04-28",
            "calories_consumed": 1730.0,
            "calories_burned": 270,
            "net_calories": 1460.0,
            "protein_g": 150.1,
            "total_carbs_g": 175.7,
            "total_fat_g": 51.3
        }
    ]
}
```

---

## 26. GET /v1/exercises/types (List all exercise types)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/exercises/types
```

**Status:** 200

```json
{
    "type": "exercise_types",
    "count": 18,
    "total": 18,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "category": "cardio",
            "calories_per_minute_low": 10.0,
            "calories_per_minute_high": 12.0,
            "met_value": 9.8
        },
        {
            "exercise_type_id": 2,
            "exercise_name": "Running (7.5 mph / 8 min mile)",
            "category": "cardio",
            "calories_per_minute_low": 12.5,
            "calories_per_minute_high": 15.0,
            "met_value": 11.5
        },
        {
            "exercise_type_id": 3,
            "exercise_name": "Cycling (moderate 12-14 mph)",
            "category": "cardio",
            "calories_per_minute_low": 7.0,
            "calories_per_minute_high": 9.0,
            "met_value": 8.0
        },
        {
            "exercise_type_id": 4,
            "exercise_name": "Cycling (vigorous 14-16 mph)",
            "category": "cardio",
            "calories_per_minute_low": 9.5,
            "calories_per_minute_high": 12.0,
            "met_value": 10.0
        },
        {
            "exercise_type_id": 5,
            "exercise_name": "Walking (3.5 mph brisk)",
            "category": "cardio",
            "calories_per_minute_low": 4.0,
            "calories_per_minute_high": 5.5,
            "met_value": 4.3
        },
        {
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "category": "strength",
            "calories_per_minute_low": 5.0,
            "calories_per_minute_high": 7.0,
            "met_value": 5.0
        },
        {
            "exercise_type_id": 7,
            "exercise_name": "Weight Training (vigorous)",
            "category": "strength",
            "calories_per_minute_low": 7.0,
            "calories_per_minute_high": 9.5,
            "met_value": 6.0
        },
        {
            "exercise_type_id": 8,
            "exercise_name": "Swimming (moderate laps)",
            "category": "cardio",
            "calories_per_minute_low": 7.5,
            "calories_per_minute_high": 10.0,
            "met_value": 7.0
        },
        {
            "exercise_type_id": 9,
            "exercise_name": "Elliptical Trainer (moderate)",
            "category": "cardio",
            "calories_per_minute_low": 7.0,
            "calories_per_minute_high": 9.0,
            "met_value": 7.0
        },
        {
            "exercise_type_id": 10,
            "exercise_name": "Yoga (Vinyasa)",
            "category": "flexibility",
            "calories_per_minute_low": 4.5,
            "calories_per_minute_high": 6.5,
            "met_value": 4.0
        },
        {
            "exercise_type_id": 11,
            "exercise_name": "Jump Rope (moderate)",
            "category": "cardio",
            "calories_per_minute_low": 10.0,
            "calories_per_minute_high": 13.0,
            "met_value": 10.0
        },
        {
            "exercise_type_id": 12,
            "exercise_name": "Rowing Machine (moderate)",
            "category": "cardio",
            "calories_per_minute_low": 7.0,
            "calories_per_minute_high": 9.5,
            "met_value": 7.0
        },
        {
            "exercise_type_id": 13,
            "exercise_name": "HIIT (High Intensity Interval Training)",
            "category": "cardio",
            "calories_per_minute_low": 10.0,
            "calories_per_minute_high": 14.0,
            "met_value": 12.0
        },
        {
            "exercise_type_id": 14,
            "exercise_name": "Hiking (moderate terrain)",
            "category": "cardio",
            "calories_per_minute_low": 5.5,
            "calories_per_minute_high": 8.0,
            "met_value": 6.0
        },
        {
            "exercise_type_id": 15,
            "exercise_name": "Basketball (recreational)",
            "category": "cardio",
            "calories_per_minute_low": 6.5,
            "calories_per_minute_high": 9.0,
            "met_value": 6.5
        },
        {
            "exercise_type_id": 16,
            "exercise_name": "Stretching (general)",
            "category": "flexibility",
            "calories_per_minute_low": 2.0,
            "calories_per_minute_high": 3.0,
            "met_value": 2.3
        },
        {
            "exercise_type_id": 17,
            "exercise_name": "Stair Climbing",
            "category": "cardio",
            "calories_per_minute_low": 8.0,
            "calories_per_minute_high": 11.0,
            "met_value": 9.0
        },
        {
            "exercise_type_id": 18,
            "exercise_name": "Push-ups (moderate effort)",
            "category": "strength",
            "calories_per_minute_low": 5.5,
            "calories_per_minute_high": 7.5,
            "met_value": 5.0
        }
    ]
}
```

---

## 27. GET /v1/exercises/types?category=cardio (Exercise types - cardio)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/exercises/types?category=cardio
```

**Status:** 200

```json
{
    "type": "exercise_types",
    "count": 13,
    "total": 13,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "category": "cardio",
            "calories_per_minute_low": 10.0,
            "calories_per_minute_high": 12.0,
            "met_value": 9.8
        },
        {
            "exercise_type_id": 2,
            "exercise_name": "Running (7.5 mph / 8 min mile)",
            "category": "cardio",
            "calories_per_minute_low": 12.5,
            "calories_per_minute_high": 15.0,
            "met_value": 11.5
        },
        {
            "exercise_type_id": 3,
            "exercise_name": "Cycling (moderate 12-14 mph)",
            "category": "cardio",
            "calories_per_minute_low": 7.0,
            "calories_per_minute_high": 9.0,
            "met_value": 8.0
        },
        {
            "exercise_type_id": 4,
            "exercise_name": "Cycling (vigorous 14-16 mph)",
            "category": "cardio",
            "calories_per_minute_low": 9.5,
            "calories_per_minute_high": 12.0,
            "met_value": 10.0
        },
        {
            "exercise_type_id": 5,
            "exercise_name": "Walking (3.5 mph brisk)",
            "category": "cardio",
            "calories_per_minute_low": 4.0,
            "calories_per_minute_high": 5.5,
            "met_value": 4.3
        },
        {
            "exercise_type_id": 8,
            "exercise_name": "Swimming (moderate laps)",
            "category": "cardio",
            "calories_per_minute_low": 7.5,
            "calories_per_minute_high": 10.0,
            "met_value": 7.0
        },
        {
            "exercise_type_id": 9,
            "exercise_name": "Elliptical Trainer (moderate)",
            "category": "cardio",
            "calories_per_minute_low": 7.0,
            "calories_per_minute_high": 9.0,
            "met_value": 7.0
        },
        {
            "exercise_type_id": 11,
            "exercise_name": "Jump Rope (moderate)",
            "category": "cardio",
            "calories_per_minute_low": 10.0,
            "calories_per_minute_high": 13.0,
            "met_value": 10.0
        },
        {
            "exercise_type_id": 12,
            "exercise_name": "Rowing Machine (moderate)",
            "category": "cardio",
            "calories_per_minute_low": 7.0,
            "calories_per_minute_high": 9.5,
            "met_value": 7.0
        },
        {
            "exercise_type_id": 13,
            "exercise_name": "HIIT (High Intensity Interval Training)",
            "category": "cardio",
            "calories_per_minute_low": 10.0,
            "calories_per_minute_high": 14.0,
            "met_value": 12.0
        },
        {
            "exercise_type_id": 14,
            "exercise_name": "Hiking (moderate terrain)",
            "category": "cardio",
            "calories_per_minute_low": 5.5,
            "calories_per_minute_high": 8.0,
            "met_value": 6.0
        },
        {
            "exercise_type_id": 15,
            "exercise_name": "Basketball (recreational)",
            "category": "cardio",
            "calories_per_minute_low": 6.5,
            "calories_per_minute_high": 9.0,
            "met_value": 6.5
        },
        {
            "exercise_type_id": 17,
            "exercise_name": "Stair Climbing",
            "category": "cardio",
            "calories_per_minute_low": 8.0,
            "calories_per_minute_high": 11.0,
            "met_value": 9.0
        }
    ]
}
```

---

## 28. GET /v1/exercises/types/1 (Get exercise type by ID)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/exercises/types/1
```

**Status:** 200

```json
{
    "type": "exercise_type",
    "exercise_type": {
        "exercise_type_id": 1,
        "exercise_name": "Running (6 mph / 10 min mile)",
        "category": "cardio",
        "calories_per_minute_low": 10.0,
        "calories_per_minute_high": 12.0,
        "met_value": 9.8
    }
}
```

---

## 29. GET /v1/exercises/types/999 (Get exercise type - 404)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/exercises/types/999
```

**Status:** 404

```json
{
    "error": "Exercise type 999 not found"
}
```

---

## 30. GET /v1/user/exercises (List all exercises)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/exercises
```

**Status:** 200

```json
{
    "type": "exercises",
    "count": 22,
    "total": 22,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "exercise_id": 22,
            "date": "2025-04-28",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 45,
            "calories_burned": 270,
            "notes": "Upper body and core"
        },
        {
            "exercise_id": 21,
            "date": "2025-04-27",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 40,
            "calories_burned": 440,
            "notes": "Sunday morning run - new PR on 5K segment"
        },
        {
            "exercise_id": 20,
            "date": "2025-04-25",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 45,
            "calories_burned": 270,
            "notes": "Push pull combo"
        },
        {
            "exercise_id": 19,
            "date": "2025-04-24",
            "exercise_type_id": 3,
            "exercise_name": "Cycling (moderate 12-14 mph)",
            "duration_minutes": 45,
            "calories_burned": 360,
            "notes": "Evening bike ride"
        },
        {
            "exercise_id": 18,
            "date": "2025-04-22",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 50,
            "calories_burned": 300,
            "notes": "Leg day"
        },
        {
            "exercise_id": 17,
            "date": "2025-04-21",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 30,
            "calories_burned": 330,
            "notes": "Quick morning run"
        },
        {
            "exercise_id": 16,
            "date": "2025-04-20",
            "exercise_type_id": 5,
            "exercise_name": "Walking (3.5 mph brisk)",
            "duration_minutes": 45,
            "calories_burned": 214,
            "notes": "Sunday walk with dog"
        },
        {
            "exercise_id": 15,
            "date": "2025-04-18",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 40,
            "calories_burned": 240,
            "notes": "Upper body focus"
        },
        {
            "exercise_id": 14,
            "date": "2025-04-17",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 45,
            "calories_burned": 495,
            "notes": "Long run - felt great"
        },
        {
            "exercise_id": 13,
            "date": "2025-04-15",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 45,
            "calories_burned": 270,
            "notes": "Full body circuit"
        },
        {
            "exercise_id": 12,
            "date": "2025-04-14",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 35,
            "calories_burned": 385,
            "notes": "Recovery pace run"
        },
        {
            "exercise_id": 11,
            "date": "2025-04-12",
            "exercise_type_id": 14,
            "exercise_name": "Hiking (moderate terrain)",
            "duration_minutes": 90,
            "calories_burned": 585,
            "notes": "Weekend trail hike"
        },
        {
            "exercise_id": 10,
            "date": "2025-04-11",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 50,
            "calories_burned": 300,
            "notes": "Pull day - back and biceps"
        },
        {
            "exercise_id": 9,
            "date": "2025-04-10",
            "exercise_type_id": 3,
            "exercise_name": "Cycling (moderate 12-14 mph)",
            "duration_minutes": 35,
            "calories_burned": 280,
            "notes": "Morning spin class"
        },
        {
            "exercise_id": 8,
            "date": "2025-04-08",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 45,
            "calories_burned": 270,
            "notes": "Push day - shoulders and chest"
        },
        {
            "exercise_id": 7,
            "date": "2025-04-07",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 40,
            "calories_burned": 440,
            "notes": "Tempo run intervals"
        },
        {
            "exercise_id": 6,
            "date": "2025-04-05",
            "exercise_type_id": 5,
            "exercise_name": "Walking (3.5 mph brisk)",
            "duration_minutes": 60,
            "calories_burned": 285,
            "notes": "Weekend hike at Barton Creek"
        },
        {
            "exercise_id": 5,
            "date": "2025-04-04",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 50,
            "calories_burned": 300,
            "notes": "Leg day - squats and deadlifts"
        },
        {
            "exercise_id": 4,
            "date": "2025-04-03",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 30,
            "calories_burned": 330,
            "notes": "Easy pace neighborhood run"
        },
        {
            "exercise_id": 3,
            "date": "2025-04-01",
            "exercise_type_id": 3,
            "exercise_name": "Cycling (moderate 12-14 mph)",
            "duration_minutes": 40,
            "calories_burned": 320,
            "notes": "Stationary bike at gym"
        },
        {
            "exercise_id": 2,
            "date": "2025-03-31",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 45,
            "calories_burned": 270,
            "notes": "Upper body - bench press and rows"
        },
        {
            "exercise_id": 1,
            "date": "2025-03-30",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 35,
            "calories_burned": 385,
            "notes": "Morning run around the lake"
        }
    ]
}
```

---

## 31. GET /v1/user/exercises?start_date=2025-04-20&end_date=2025-04-28 (Exercises - date range)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/exercises?start_date=2025-04-20&end_date=2025-04-28
```

**Status:** 200

```json
{
    "type": "exercises",
    "count": 7,
    "total": 7,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "exercise_id": 22,
            "date": "2025-04-28",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 45,
            "calories_burned": 270,
            "notes": "Upper body and core"
        },
        {
            "exercise_id": 21,
            "date": "2025-04-27",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 40,
            "calories_burned": 440,
            "notes": "Sunday morning run - new PR on 5K segment"
        },
        {
            "exercise_id": 20,
            "date": "2025-04-25",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 45,
            "calories_burned": 270,
            "notes": "Push pull combo"
        },
        {
            "exercise_id": 19,
            "date": "2025-04-24",
            "exercise_type_id": 3,
            "exercise_name": "Cycling (moderate 12-14 mph)",
            "duration_minutes": 45,
            "calories_burned": 360,
            "notes": "Evening bike ride"
        },
        {
            "exercise_id": 18,
            "date": "2025-04-22",
            "exercise_type_id": 6,
            "exercise_name": "Weight Training (moderate)",
            "duration_minutes": 50,
            "calories_burned": 300,
            "notes": "Leg day"
        },
        {
            "exercise_id": 17,
            "date": "2025-04-21",
            "exercise_type_id": 1,
            "exercise_name": "Running (6 mph / 10 min mile)",
            "duration_minutes": 30,
            "calories_burned": 330,
            "notes": "Quick morning run"
        },
        {
            "exercise_id": 16,
            "date": "2025-04-20",
            "exercise_type_id": 5,
            "exercise_name": "Walking (3.5 mph brisk)",
            "duration_minutes": 45,
            "calories_burned": 214,
            "notes": "Sunday walk with dog"
        }
    ]
}
```

---

## 32. GET /v1/user/exercises/1 (Get exercise by ID)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/exercises/1
```

**Status:** 200

```json
{
    "type": "exercise",
    "exercise": {
        "exercise_id": 1,
        "date": "2025-03-30",
        "exercise_type_id": 1,
        "exercise_name": "Running (6 mph / 10 min mile)",
        "duration_minutes": 35,
        "calories_burned": 385,
        "notes": "Morning run around the lake"
    }
}
```

---

## 33. GET /v1/user/exercises/999 (Get exercise - 404)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/exercises/999
```

**Status:** 404

```json
{
    "error": "Exercise 999 not found"
}
```

---

## 34. POST /v1/user/exercises (Log exercise)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"date": "2025-04-28", "exercise_type_id": 3, "duration_minutes": 30, "calories_burned": 240, "notes": "Evening ride"}' http://localhost:8006/v1/user/exercises
```

**Status:** 201

```json
{
    "type": "exercise",
    "exercise": {
        "exercise_id": 23,
        "date": "2025-04-28",
        "exercise_type_id": 3,
        "exercise_name": "Cycling (moderate 12-14 mph)",
        "duration_minutes": 30,
        "calories_burned": 240,
        "notes": "Evening ride"
    }
}
```

---

## 35. POST /v1/user/exercises (Log exercise - bad type_id)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"date": "2025-04-28", "exercise_type_id": 999, "duration_minutes": 30, "calories_burned": 200}' http://localhost:8006/v1/user/exercises
```

**Status:** 400

```json
{
    "error": "Exercise type 999 not found"
}
```

---

## 36. GET /v1/user/weight (List all weight entries)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/weight
```

**Status:** 200

```json
{
    "type": "weight_entries",
    "count": 15,
    "total": 15,
    "offset": 0,
    "limit": 25,
    "results": [
        {
            "weight_id": 15,
            "date": "2025-04-28",
            "weight_lbs": 192.0,
            "notes": "Slight fluctuation but trend is good"
        },
        {
            "weight_id": 14,
            "date": "2025-04-25",
            "weight_lbs": 191.8,
            "notes": ""
        },
        {
            "weight_id": 13,
            "date": "2025-04-23",
            "weight_lbs": 192.0,
            "notes": "New low!"
        },
        {
            "weight_id": 12,
            "date": "2025-04-21",
            "weight_lbs": 192.2,
            "notes": "Back on track"
        },
        {
            "weight_id": 11,
            "date": "2025-04-19",
            "weight_lbs": 192.8,
            "notes": "Weekend splurge effect"
        },
        {
            "weight_id": 10,
            "date": "2025-04-17",
            "weight_lbs": 192.6,
            "notes": "Breaking through plateau"
        },
        {
            "weight_id": 9,
            "date": "2025-04-15",
            "weight_lbs": 193.0,
            "notes": ""
        },
        {
            "weight_id": 8,
            "date": "2025-04-13",
            "weight_lbs": 193.2,
            "notes": ""
        },
        {
            "weight_id": 7,
            "date": "2025-04-11",
            "weight_lbs": 193.8,
            "notes": "Slight bounce after rest day"
        },
        {
            "weight_id": 6,
            "date": "2025-04-09",
            "weight_lbs": 193.6,
            "notes": "Good week of consistency"
        },
        {
            "weight_id": 5,
            "date": "2025-04-07",
            "weight_lbs": 194.1,
            "notes": ""
        },
        {
            "weight_id": 4,
            "date": "2025-04-05",
            "weight_lbs": 194.4,
            "notes": ""
        },
        {
            "weight_id": 3,
            "date": "2025-04-03",
            "weight_lbs": 195.0,
            "notes": "Water retention from salty dinner"
        },
        {
            "weight_id": 2,
            "date": "2025-04-01",
            "weight_lbs": 194.8,
            "notes": ""
        },
        {
            "weight_id": 1,
            "date": "2025-03-30",
            "weight_lbs": 195.2,
            "notes": "Starting fresh - recommitting to tracking"
        }
    ]
}
```

---

## 37. GET /v1/user/weight/1 (Get weight entry by ID)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/weight/1
```

**Status:** 200

```json
{
    "type": "weight_entry",
    "weight_entry": {
        "weight_id": 1,
        "date": "2025-03-30",
        "weight_lbs": 195.2,
        "notes": "Starting fresh - recommitting to tracking"
    }
}
```

---

## 38. GET /v1/user/weight/999 (Get weight entry - 404)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/weight/999
```

**Status:** 404

```json
{
    "error": "Weight entry 999 not found"
}
```

---

## 39. POST /v1/user/weight (Log weight)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"date": "2025-04-29", "weight_lbs": 191.5, "notes": "Morning weigh-in"}' http://localhost:8006/v1/user/weight
```

**Status:** 201

```json
{
    "type": "weight_entry",
    "weight_entry": {
        "weight_id": 16,
        "date": "2025-04-29",
        "weight_lbs": 191.5,
        "notes": "Morning weigh-in"
    }
}
```

---

## 40. GET /v1/user/water/2025-04-28 (Get water for date)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/water/2025-04-28
```

**Status:** 200

```json
{
    "type": "water",
    "water": {
        "water_id": 30,
        "date": "2025-04-28",
        "cups": 8,
        "notes": ""
    }
}
```

---

## 41. GET /v1/user/water/2020-01-01 (Get water - 404)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X GET http://localhost:8006/v1/user/water/2020-01-01
```

**Status:** 404

```json
{
    "error": "Water entry for 2020-01-01 not found"
}
```

---

## 42. POST /v1/user/water (Log water)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"date": "2025-04-29", "cups": 8, "notes": "Good day"}' http://localhost:8006/v1/user/water
```

**Status:** 201

```json
{
    "type": "water",
    "water": {
        "water_id": 31,
        "date": "2025-04-29",
        "cups": 8,
        "notes": "Good day"
    }
}
```

---

## 43. POST /v1/user/water (Log water - duplicate)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X POST -H 'Content-Type: application/json' -d '{"date": "2025-04-28", "cups": 10}' http://localhost:8006/v1/user/water
```

**Status:** 400

```json
{
    "error": "Water entry for 2025-04-28 already exists. Use PUT to update."
}
```

---

## 44. PUT /v1/user/water/2025-04-28 (Update water)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X PUT -H 'Content-Type: application/json' -d '{"cups": 10, "notes": "Updated after workout"}' http://localhost:8006/v1/user/water/2025-04-28
```

**Status:** 200

```json
{
    "type": "water",
    "water": {
        "water_id": 30,
        "date": "2025-04-28",
        "cups": 10,
        "notes": "Updated after workout"
    }
}
```

---

## 45. PUT /v1/user/water/2020-01-01 (Update water - 404)

```
curl -s -w '
HTTP_STATUS:%{http_code}' -X PUT -H 'Content-Type: application/json' -d '{"cups": 5}' http://localhost:8006/v1/user/water/2020-01-01
```

**Status:** 404

```json
{
    "error": "Water entry for 2020-01-01 not found"
}
```

---


**Total tests: 45**
