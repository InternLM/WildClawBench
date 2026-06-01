---
name: myfitnesspal-api-connector
description: >
  MyFitnessPal API HTTP endpoints for nutrition tracking, food diary management,
  exercise logging, weight monitoring, and health goal configuration.
---

# MyFitnessPal API

## Base URL

| Variable | Purpose |
|----------|---------|
| `MYFITNESSPAL_API_URL` | Base URL for all requests |

All paths below are relative to `MYFITNESSPAL_API_URL`.

---

## Health

```
GET /health
```

Returns `{"status": "ok"}`.

---

## User Profile

### Get profile

Returns the authenticated user's profile, including display name, email, daily calorie goal, activity level, current weight, goal weight, weekly weight goal, height, age, gender, and account creation date.

```
GET /v1/user/profile
```

### Update profile

Partially updates the authenticated user's profile settings. Only the provided fields are modified. Returns the updated profile object.

```
PUT /v1/user/profile
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `display_name` | string | no | Display name |
| `daily_calorie_goal` | integer | no | Daily calorie intake target |
| `activity_level` | string | no | Activity level: `sedentary`, `lightly_active`, `active`, `very_active` |
| `current_weight_lbs` | number | no | Current weight in pounds |
| `goal_weight_lbs` | number | no | Target weight in pounds |
| `weekly_weight_goal_lbs` | number | no | Weekly weight change target in pounds (negative for loss, positive for gain) |

---

## Goals

### Get goals

Returns the user's nutrition and weight goals, including daily calorie target, macronutrient percentage targets (protein, carbs, fat), goal weight, and weekly weight change target.

```
GET /v1/user/goals
```

### Update goals

Updates the user's nutrition and weight goals. Only the provided fields are modified. Returns the updated goals object.

```
PUT /v1/user/goals
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `daily_calorie_goal` | integer | no | Daily calorie intake target |
| `macro_goals` | object | no | Macronutrient targets as `{"protein_pct": number, "carbs_pct": number, "fat_pct": number}`. Percentages should sum to 100. |
| `goal_weight_lbs` | number | no | Target weight in pounds |
| `weekly_weight_goal_lbs` | number | no | Weekly weight change target in pounds |

---

## Foods

### Search foods

Searches the food database by name or brand. Returns matching foods with their nutritional information per serving, including calories, protein, carbs, fat, fiber, sugar, and sodium.

```
GET /v1/foods/search
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `q` | string | query | yes | Search query matching food name or brand |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get food

Returns the full nutritional details of a single food item, including name, brand, serving size, serving unit, and per-serving macros (calories, protein, carbs, fat, fiber, sugar, sodium, cholesterol, saturated fat).

```
GET /v1/foods/{food_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `food_id` | string | path | yes | Food identifier |

---

## Food Diary

### Get diary for date

Returns all food diary entries for a specific date, organized by meal slot. Each entry includes the food name, servings, calculated nutritional values, and meal assignment.

```
GET /v1/user/diary/{date}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `date` | string | path | yes | Date in YYYY-MM-DD format |
| `meal` | string | query | no | Filter by meal slot: `Breakfast`, `Lunch`, `Dinner`, `Snacks` |

### Get diary range

Returns all food diary entries across a date range. Entries are grouped by date and meal slot.

```
GET /v1/user/diary
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `start_date` | string | query | yes | Start date (YYYY-MM-DD) |
| `end_date` | string | query | yes | End date (YYYY-MM-DD) |

### Create diary entry

Logs a food item to the diary at a specific date and meal slot. The nutritional values are automatically calculated based on the food's per-serving data multiplied by the number of servings. Returns the created diary entry.

```
POST /v1/user/diary
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | yes | Date in YYYY-MM-DD format |
| `meal` | string | yes | Meal slot: `Breakfast`, `Lunch`, `Dinner`, `Snacks` |
| `food_id` | integer | yes | Food item ID from the food database |
| `servings` | number | yes | Number of servings |

### Update diary entry

Updates an existing diary entry's servings or meal assignment. Recalculates nutritional values if servings change. Returns the updated entry.

```
PUT /v1/user/diary/{entry_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `entry_id` | string | path | yes | Diary entry identifier |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `servings` | number | no | Updated number of servings |
| `meal` | string | no | Updated meal slot |

### Delete diary entry

Removes a food entry from the diary. The daily nutritional totals are recalculated.

```
DELETE /v1/user/diary/{entry_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `entry_id` | string | path | yes | Diary entry identifier |

---

## Nutrition Summary

### Get daily nutrition

Returns the aggregated nutritional summary for a single date, including total calories, macronutrients (protein, carbs, fat), and comparison against daily goals with remaining budget.

```
GET /v1/user/nutrition/{date}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `date` | string | path | yes | Date in YYYY-MM-DD format |

### Get weekly nutrition

Returns a 7-day nutritional summary ending on the specified date. Includes daily breakdowns and weekly averages for calories and macronutrients.

```
GET /v1/user/nutrition/weekly/{end_date}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `end_date` | string | path | yes | End date of the 7-day period (YYYY-MM-DD) |

### Get progress

Returns calorie and macronutrient tracking progress over a specified number of recent days. Includes daily totals, goal targets, and trend indicators.

```
GET /v1/user/progress
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `days` | integer | query | no | Number of days to include, 1-90. Default: 30 |

---

## Exercise Types

### List exercise types

Returns a paginated list of available exercise types from the database. Each type includes its ID, name, category, calories burned per minute (estimated), and MET value.

```
GET /v1/exercises/types
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `category` | string | query | no | Filter by category: `cardio`, `strength`, `flexibility` |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get exercise type

Returns the full details of a single exercise type, including its name, category, calories per minute, MET value, and description.

```
GET /v1/exercises/types/{exercise_type_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `exercise_type_id` | string | path | yes | Exercise type identifier |

---

## Exercise Log

### List exercises

Returns a paginated list of logged exercises. Results can be filtered by date range. Each exercise entry includes the type, date, duration, calories burned, and notes.

```
GET /v1/user/exercises
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `start_date` | string | query | no | Filter from date (YYYY-MM-DD) |
| `end_date` | string | query | no | Filter to date (YYYY-MM-DD) |
| `limit` | integer | query | no | Maximum results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get exercise

Returns the full details of a single logged exercise, including the exercise type, date, duration, calories burned, and notes.

```
GET /v1/user/exercises/{exercise_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `exercise_id` | string | path | yes | Exercise log entry identifier |

### Log exercise

Creates a new exercise log entry. The calorie burn can be specified manually or calculated from the exercise type's MET value and duration. Returns the created exercise entry.

```
POST /v1/user/exercises
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | yes | Exercise date (YYYY-MM-DD) |
| `exercise_type_id` | integer | yes | Exercise type ID from the types database |
| `duration_minutes` | integer | yes | Duration in minutes |
| `calories_burned` | integer | no | Manually specified calories burned |
| `notes` | string | no | Free-text notes |

---

## Weight Log

### List weight entries

Returns a paginated list of weight log entries, ordered by date descending. Each entry includes the date, weight value, notes, and entry ID.

```
GET /v1/user/weight
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `limit` | integer | query | no | Maximum results, 1-100. Default: 25 |
| `offset` | integer | query | no | Number of results to skip. Default: 0 |

### Get weight entry

Returns the details of a single weight log entry.

```
GET /v1/user/weight/{weight_id}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `weight_id` | string | path | yes | Weight entry identifier |

### Log weight

Records a new weight measurement. Returns the created weight entry.

```
POST /v1/user/weight
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | yes | Measurement date (YYYY-MM-DD) |
| `weight_lbs` | number | yes | Weight in pounds |
| `notes` | string | no | Free-text notes |

---

## Water Intake

### Get water intake

Returns the water intake record for a specific date, including total cups consumed and notes.

```
GET /v1/user/water/{date}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `date` | string | path | yes | Date in YYYY-MM-DD format |

### Log water intake

Creates a new water intake record for a date. Returns the created water entry.

```
POST /v1/user/water
```

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `date` | string | yes | Date in YYYY-MM-DD format |
| `cups` | number | yes | Number of cups consumed |
| `notes` | string | no | Free-text notes |

### Update water intake

Updates the water intake record for a specific date. Returns the updated water entry.

```
PUT /v1/user/water/{date}
```

| Parameter | Type | In | Required | Description |
|-----------|------|------|----------|-------------|
| `date` | string | path | yes | Date in YYYY-MM-DD format |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cups` | number | no | Updated number of cups |
| `notes` | string | no | Updated notes |

---

## Errors

Error responses follow this format:

```json
{
  "error": {
    "message": "Description of the error",
    "code": 404
  }
}
```

Common HTTP status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid parameters or malformed body) |
| 404 | Resource not found |
