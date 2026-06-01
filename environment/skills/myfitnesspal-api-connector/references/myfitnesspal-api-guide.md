# MyFitnessPal API Guide

Detailed patterns and examples for working with the MyFitnessPal nutrition tracking API.

## Base URL

Set via the `MYFITNESSPAL_API_URL` environment variable (e.g. `http://myfitnesspal-api:8005`).

## User Profile

```bash
# Get user profile
curl "$MYFITNESSPAL_API_URL/v1/user/profile"

# Update profile
curl -X PUT "$MYFITNESSPAL_API_URL/v1/user/profile" \
  -H "Content-Type: application/json" \
  -d '{"activity_level": "very_active", "daily_calorie_goal": 2000}'
```

## Goals

```bash
# Get nutrition goals
curl "$MYFITNESSPAL_API_URL/v1/user/goals"

# Update goals (calorie target and macros)
curl -X PUT "$MYFITNESSPAL_API_URL/v1/user/goals" \
  -H "Content-Type: application/json" \
  -d '{"daily_calorie_goal": 1900, "macro_goals": {"protein_pct": 40, "carbs_pct": 35, "fat_pct": 25}}'
```

## Food Database

```bash
# Search all foods
curl "$MYFITNESSPAL_API_URL/v1/foods/search"

# Search by name
curl "$MYFITNESSPAL_API_URL/v1/foods/search?q=chicken"

# Search by brand
curl "$MYFITNESSPAL_API_URL/v1/foods/search?q=chobani"

# Paginate results
curl "$MYFITNESSPAL_API_URL/v1/foods/search?limit=10&offset=20"

# Get specific food with full nutrition data
curl "$MYFITNESSPAL_API_URL/v1/foods/1"
```

## Food Diary

```bash
# Get diary for a specific date (all meals)
curl "$MYFITNESSPAL_API_URL/v1/user/diary/2025-04-28"

# Filter by meal slot
curl "$MYFITNESSPAL_API_URL/v1/user/diary/2025-04-28?meal=Breakfast"

# Get diary for a date range
curl "$MYFITNESSPAL_API_URL/v1/user/diary?start_date=2025-04-25&end_date=2025-04-28"
```

## Logging Food Entries

```bash
# Log a food entry (Grilled Chicken Breast, 1.5 servings at lunch)
curl -X POST "$MYFITNESSPAL_API_URL/v1/user/diary" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-04-28",
    "meal": "Lunch",
    "food_id": 1,
    "servings": 1.5
  }'

# Log a snack (Quest Protein Bar)
curl -X POST "$MYFITNESSPAL_API_URL/v1/user/diary" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-04-28",
    "meal": "Snacks",
    "food_id": 22,
    "servings": 1.0
  }'
```

## Updating and Deleting Diary Entries

```bash
# Update servings on an entry
curl -X PUT "$MYFITNESSPAL_API_URL/v1/user/diary/1" \
  -H "Content-Type: application/json" \
  -d '{"servings": 2.0}'

# Move entry to a different meal
curl -X PUT "$MYFITNESSPAL_API_URL/v1/user/diary/5" \
  -H "Content-Type: application/json" \
  -d '{"meal": "Dinner"}'

# Delete an entry
curl -X DELETE "$MYFITNESSPAL_API_URL/v1/user/diary/291"
```

## Nutrition Summary

```bash
# Get daily nutrition totals with remaining budget
curl "$MYFITNESSPAL_API_URL/v1/user/nutrition/2025-04-28"

# Get weekly summary (7-day averages)
curl "$MYFITNESSPAL_API_URL/v1/user/nutrition/weekly/2025-04-28"

# Get progress over last 30 days
curl "$MYFITNESSPAL_API_URL/v1/user/progress?days=30"

# Get progress over last 7 days
curl "$MYFITNESSPAL_API_URL/v1/user/progress?days=7"
```

## Exercise Types Database

```bash
# List all exercise types
curl "$MYFITNESSPAL_API_URL/v1/exercises/types"

# Filter by category
curl "$MYFITNESSPAL_API_URL/v1/exercises/types?category=cardio"

# Get specific exercise type
curl "$MYFITNESSPAL_API_URL/v1/exercises/types/1"
```

## Exercise Log

```bash
# List all logged exercises
curl "$MYFITNESSPAL_API_URL/v1/user/exercises"

# Filter by date range
curl "$MYFITNESSPAL_API_URL/v1/user/exercises?start_date=2025-04-20&end_date=2025-04-28"

# Get specific exercise entry
curl "$MYFITNESSPAL_API_URL/v1/user/exercises/1"
```

## Logging Exercises

```bash
# Log a cycling session
curl -X POST "$MYFITNESSPAL_API_URL/v1/user/exercises" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-04-28",
    "exercise_type_id": 3,
    "duration_minutes": 30,
    "calories_burned": 240,
    "notes": "Evening ride around the neighborhood"
  }'
```

## Weight Log

```bash
# List all weight entries (newest first)
curl "$MYFITNESSPAL_API_URL/v1/user/weight"

# Get specific weight entry
curl "$MYFITNESSPAL_API_URL/v1/user/weight/1"

# Log new weight
curl -X POST "$MYFITNESSPAL_API_URL/v1/user/weight" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-04-29",
    "weight_lbs": 191.5,
    "notes": "Morning weigh-in"
  }'
```

## Water Intake

```bash
# Get water for a date
curl "$MYFITNESSPAL_API_URL/v1/user/water/2025-04-28"

# Log water for a new day
curl -X POST "$MYFITNESSPAL_API_URL/v1/user/water" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-04-29",
    "cups": 8,
    "notes": "Good hydration day"
  }'

# Update water for an existing day
curl -X PUT "$MYFITNESSPAL_API_URL/v1/user/water/2025-04-28" \
  -H "Content-Type: application/json" \
  -d '{"cups": 10, "notes": "Updated after workout"}'
```

## Common Patterns

### Check Daily Progress Against Goals

```python
import json
import os
import urllib.request

BASE = os.environ["MYFITNESSPAL_API_URL"]

def api_get(path):
    with urllib.request.urlopen(f"{BASE}{path}") as r:
        return json.loads(r.read())

totals = api_get("/v1/user/nutrition/2025-04-28")
remaining = totals["remaining"]
consumed = totals["totals"]
goal = totals["goal"]

print(f"Calories: {consumed['calories']:.0f} / {goal['calories']} ({remaining['calories']:.0f} remaining)")
print(f"Protein:  {consumed['protein_g']:.1f}g / {goal['protein_g']}g")
if remaining["calories"] < 200:
    print("Warning: Very close to calorie limit!")
```

### Find High-Protein Foods for Remaining Budget

```python
foods = api_get("/v1/foods/search")
totals = api_get("/v1/user/nutrition/2025-04-28")
cals_left = totals["remaining"]["calories"]

suggestions = []
for food in foods["results"]:
    if food["calories"] <= cals_left and food["protein_g"] >= 20:
        suggestions.append(food)

suggestions.sort(key=lambda f: f["protein_g"], reverse=True)
for s in suggestions[:5]:
    print(f"{s['food_name']}: {s['calories']} cal, {s['protein_g']}g protein")
```

### Weekly Exercise and Weight Summary

```python
exercises = api_get("/v1/user/exercises?start_date=2025-04-22&end_date=2025-04-28")
weight_log = api_get("/v1/user/weight")

total_burned = sum(e["calories_burned"] for e in exercises["results"])
total_minutes = sum(e["duration_minutes"] for e in exercises["results"])
print(f"This week: {exercises['count']} workouts, {total_minutes} min, {total_burned} cal burned")

entries = weight_log["results"]
if len(entries) >= 2:
    latest = entries[0]["weight_lbs"]
    oldest = entries[-1]["weight_lbs"]
    print(f"Weight trend: {oldest} -> {latest} lbs ({latest - oldest:+.1f})")
```
