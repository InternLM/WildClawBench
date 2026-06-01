"""Data access module for MyFitnessPal API simulation."""

import csv
import json
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_foods(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "food_id": int(r["food_id"]),
            "calories": float(r["calories"]),
            "total_fat_g": float(r["total_fat_g"]),
            "saturated_fat_g": float(r["saturated_fat_g"]),
            "cholesterol_mg": float(r["cholesterol_mg"]),
            "sodium_mg": float(r["sodium_mg"]),
            "total_carbs_g": float(r["total_carbs_g"]),
            "dietary_fiber_g": float(r["dietary_fiber_g"]),
            "sugars_g": float(r["sugars_g"]),
            "protein_g": float(r["protein_g"]),
            "potassium_mg": float(r["potassium_mg"]),
            "is_verified": r["is_verified"].lower() == "true",
        })
    return out


def _coerce_diary_entries(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "entry_id": int(r["entry_id"]),
            "food_id": int(r["food_id"]),
            "servings": float(r["servings"]),
            "calories": float(r["calories"]),
            "total_fat_g": float(r["total_fat_g"]),
            "saturated_fat_g": float(r["saturated_fat_g"]),
            "cholesterol_mg": float(r["cholesterol_mg"]),
            "sodium_mg": float(r["sodium_mg"]),
            "total_carbs_g": float(r["total_carbs_g"]),
            "dietary_fiber_g": float(r["dietary_fiber_g"]),
            "sugars_g": float(r["sugars_g"]),
            "protein_g": float(r["protein_g"]),
        })
    return out


def _coerce_exercise_types(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "exercise_type_id": int(r["exercise_type_id"]),
            "calories_per_minute_low": float(r["calories_per_minute_low"]),
            "calories_per_minute_high": float(r["calories_per_minute_high"]),
            "met_value": float(r["met_value"]),
        })
    return out


def _coerce_exercise_log(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "exercise_id": int(r["exercise_id"]),
            "exercise_type_id": int(r["exercise_type_id"]),
            "duration_minutes": int(r["duration_minutes"]),
            "calories_burned": int(r["calories_burned"]),
        })
    return out


def _coerce_weight_log(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "weight_id": int(r["weight_id"]),
            "weight_lbs": float(r["weight_lbs"]),
        })
    return out


def _coerce_water_log(rows):
    out = []
    for r in rows:
        out.append({
            **r,
            "water_id": int(r["water_id"]),
            "cups": int(r["cups"]),
        })
    return out


# Load all data at module init
_foods = _coerce_foods(_load("foods.csv"))
_diary_entries = _coerce_diary_entries(_load("diary_entries.csv"))
_exercise_types = _coerce_exercise_types(_load("exercise_types.csv"))
_exercise_log = _coerce_exercise_log(_load("exercise_log.csv"))
_weight_log = _coerce_weight_log(_load("weight_log.csv"))
_water_log = _coerce_water_log(_load("water_log.csv"))

with open(DATA_DIR / "user_profile.json", encoding="utf-8") as _f:
    _user_profile = json.load(_f)

# Mutable in-memory stores
_foods_store = deepcopy(_foods)
_diary_entries_store = deepcopy(_diary_entries)
_exercise_types_store = deepcopy(_exercise_types)
_exercise_log_store = deepcopy(_exercise_log)
_weight_log_store = deepcopy(_weight_log)
_water_log_store = deepcopy(_water_log)
_user_profile_store = deepcopy(_user_profile)

_next_entry_id = max(e["entry_id"] for e in _diary_entries_store) + 1
_next_exercise_id = max(e["exercise_id"] for e in _exercise_log_store) + 1
_next_weight_id = max(w["weight_id"] for w in _weight_log_store) + 1
_next_water_id = max(w["water_id"] for w in _water_log_store) + 1


# ---------------------------------------------------------------------------
# User Profile
# ---------------------------------------------------------------------------

def get_user_profile():
    return {"type": "user_profile", "user_profile": _user_profile_store}


def update_user_profile(data: dict):
    updatable = {
        "display_name", "daily_calorie_goal", "activity_level",
        "current_weight_lbs", "goal_weight_lbs", "weekly_weight_goal_lbs",
    }
    for k, v in data.items():
        if k in updatable:
            _user_profile_store[k] = v
    return {"type": "user_profile", "user_profile": _user_profile_store}


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

def get_goals():
    return {
        "type": "goals",
        "goals": {
            "daily_calorie_goal": _user_profile_store["daily_calorie_goal"],
            "macro_goals": _user_profile_store["macro_goals"],
            "nutrient_goals": _user_profile_store["nutrient_goals"],
            "weekly_weight_goal_lbs": _user_profile_store["weekly_weight_goal_lbs"],
            "goal_weight_lbs": _user_profile_store["goal_weight_lbs"],
        },
    }


def update_goals(data: dict):
    if "daily_calorie_goal" in data:
        _user_profile_store["daily_calorie_goal"] = int(data["daily_calorie_goal"])
        _user_profile_store["nutrient_goals"]["calories"] = int(data["daily_calorie_goal"])
    if "macro_goals" in data:
        _user_profile_store["macro_goals"].update(data["macro_goals"])
    if "nutrient_goals" in data:
        _user_profile_store["nutrient_goals"].update(data["nutrient_goals"])
    if "weekly_weight_goal_lbs" in data:
        _user_profile_store["weekly_weight_goal_lbs"] = float(data["weekly_weight_goal_lbs"])
    if "goal_weight_lbs" in data:
        _user_profile_store["goal_weight_lbs"] = float(data["goal_weight_lbs"])
    return get_goals()


# ---------------------------------------------------------------------------
# Food Database
# ---------------------------------------------------------------------------

def search_foods(q: str = None, limit: int = 25, offset: int = 0):
    results = list(_foods_store)
    if q:
        q_l = q.lower()
        results = [f for f in results if q_l in f["food_name"].lower() or q_l in f.get("brand", "").lower()]

    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "foods",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_food(food_id: int):
    for f in _foods_store:
        if f["food_id"] == food_id:
            return {"type": "food", "food": f}
    return {"error": f"Food {food_id} not found"}


# ---------------------------------------------------------------------------
# Food Diary
# ---------------------------------------------------------------------------

def get_diary(date: str, meal: str = None):
    entries = [e for e in _diary_entries_store if e["date"] == date]
    if meal:
        entries = [e for e in entries if e["meal"].lower() == meal.lower()]

    if not entries and not any(e["date"] == date for e in _diary_entries_store):
        return {
            "type": "diary",
            "date": date,
            "meals": {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []},
            "totals": _empty_totals(),
        }

    meals = {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []}
    for e in entries:
        slot = e["meal"]
        if slot in meals:
            meals[slot].append(e)

    totals = _compute_totals(entries)
    return {
        "type": "diary",
        "date": date,
        "meals": meals,
        "totals": totals,
    }


def get_diary_range(start_date: str, end_date: str):
    entries = [
        e for e in _diary_entries_store
        if start_date <= e["date"] <= end_date
    ]
    dates = sorted(set(e["date"] for e in entries))
    days = []
    for d in dates:
        day_entries = [e for e in entries if e["date"] == d]
        meals = {"Breakfast": [], "Lunch": [], "Dinner": [], "Snacks": []}
        for e in day_entries:
            slot = e["meal"]
            if slot in meals:
                meals[slot].append(e)
        days.append({
            "date": d,
            "meals": meals,
            "totals": _compute_totals(day_entries),
        })
    return {
        "type": "diary_range",
        "start_date": start_date,
        "end_date": end_date,
        "count": len(days),
        "results": days,
    }


def create_diary_entry(data: dict):
    global _next_entry_id
    required = ["date", "meal", "food_id", "servings"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    food_id = int(data["food_id"])
    food = None
    for f in _foods_store:
        if f["food_id"] == food_id:
            food = f
            break

    if not food:
        return {"error": f"Food {food_id} not found in database"}

    servings = float(data["servings"])
    entry = {
        "entry_id": _next_entry_id,
        "date": data["date"],
        "meal": data["meal"],
        "food_id": food_id,
        "food_name": food["food_name"],
        "brand": food.get("brand", ""),
        "serving_size": food["serving_size"],
        "serving_unit": food["serving_unit"],
        "servings": servings,
        "calories": round(food["calories"] * servings, 1),
        "total_fat_g": round(food["total_fat_g"] * servings, 1),
        "saturated_fat_g": round(food["saturated_fat_g"] * servings, 1),
        "cholesterol_mg": round(food["cholesterol_mg"] * servings, 1),
        "sodium_mg": round(food["sodium_mg"] * servings, 1),
        "total_carbs_g": round(food["total_carbs_g"] * servings, 1),
        "dietary_fiber_g": round(food["dietary_fiber_g"] * servings, 1),
        "sugars_g": round(food["sugars_g"] * servings, 1),
        "protein_g": round(food["protein_g"] * servings, 1),
    }
    _diary_entries_store.append(entry)
    _next_entry_id += 1
    return {"type": "diary_entry", "diary_entry": entry}


def update_diary_entry(entry_id: int, data: dict):
    for i, entry in enumerate(_diary_entries_store):
        if entry["entry_id"] == entry_id:
            if "servings" in data:
                new_servings = float(data["servings"])
                food_id = entry["food_id"]
                food = None
                for f in _foods_store:
                    if f["food_id"] == food_id:
                        food = f
                        break
                if food:
                    _diary_entries_store[i]["servings"] = new_servings
                    _diary_entries_store[i]["calories"] = round(food["calories"] * new_servings, 1)
                    _diary_entries_store[i]["total_fat_g"] = round(food["total_fat_g"] * new_servings, 1)
                    _diary_entries_store[i]["saturated_fat_g"] = round(food["saturated_fat_g"] * new_servings, 1)
                    _diary_entries_store[i]["cholesterol_mg"] = round(food["cholesterol_mg"] * new_servings, 1)
                    _diary_entries_store[i]["sodium_mg"] = round(food["sodium_mg"] * new_servings, 1)
                    _diary_entries_store[i]["total_carbs_g"] = round(food["total_carbs_g"] * new_servings, 1)
                    _diary_entries_store[i]["dietary_fiber_g"] = round(food["dietary_fiber_g"] * new_servings, 1)
                    _diary_entries_store[i]["sugars_g"] = round(food["sugars_g"] * new_servings, 1)
                    _diary_entries_store[i]["protein_g"] = round(food["protein_g"] * new_servings, 1)
            if "meal" in data:
                _diary_entries_store[i]["meal"] = data["meal"]
            return {"type": "diary_entry", "diary_entry": _diary_entries_store[i]}
    return {"error": f"Diary entry {entry_id} not found"}


def delete_diary_entry(entry_id: int):
    for i, entry in enumerate(_diary_entries_store):
        if entry["entry_id"] == entry_id:
            _diary_entries_store.pop(i)
            return {"type": "diary_entry", "deleted": True, "entry_id": entry_id}
    return {"error": f"Diary entry {entry_id} not found"}


# ---------------------------------------------------------------------------
# Nutrition Summary
# ---------------------------------------------------------------------------

def _empty_totals():
    return {
        "calories": 0, "total_fat_g": 0, "saturated_fat_g": 0,
        "cholesterol_mg": 0, "sodium_mg": 0, "total_carbs_g": 0,
        "dietary_fiber_g": 0, "sugars_g": 0, "protein_g": 0,
    }


def _compute_totals(entries):
    totals = _empty_totals()
    for e in entries:
        totals["calories"] += e["calories"]
        totals["total_fat_g"] += e["total_fat_g"]
        totals["saturated_fat_g"] += e["saturated_fat_g"]
        totals["cholesterol_mg"] += e["cholesterol_mg"]
        totals["sodium_mg"] += e["sodium_mg"]
        totals["total_carbs_g"] += e["total_carbs_g"]
        totals["dietary_fiber_g"] += e["dietary_fiber_g"]
        totals["sugars_g"] += e["sugars_g"]
        totals["protein_g"] += e["protein_g"]
    for k in totals:
        totals[k] = round(totals[k], 1)
    return totals


def get_daily_totals(date: str):
    entries = [e for e in _diary_entries_store if e["date"] == date]
    if not entries:
        return {
            "type": "daily_totals",
            "date": date,
            "totals": _empty_totals(),
            "goal": _user_profile_store["nutrient_goals"],
            "remaining": _user_profile_store["nutrient_goals"].copy(),
        }
    totals = _compute_totals(entries)
    goal = _user_profile_store["nutrient_goals"]
    remaining = {}
    for k in totals:
        if k in goal:
            remaining[k] = round(goal[k] - totals[k], 1)
    return {
        "type": "daily_totals",
        "date": date,
        "totals": totals,
        "goal": goal,
        "remaining": remaining,
    }


def get_weekly_summary(end_date: str):
    end = datetime.strptime(end_date, "%Y-%m-%d")
    start = end - timedelta(days=6)
    start_str = start.strftime("%Y-%m-%d")

    days = []
    current = start
    while current <= end:
        d = current.strftime("%Y-%m-%d")
        entries = [e for e in _diary_entries_store if e["date"] == d]
        totals = _compute_totals(entries) if entries else _empty_totals()
        days.append({"date": d, "totals": totals, "entry_count": len(entries)})
        current += timedelta(days=1)

    avg_calories = round(sum(d["totals"]["calories"] for d in days) / 7, 1)
    avg_protein = round(sum(d["totals"]["protein_g"] for d in days) / 7, 1)
    avg_carbs = round(sum(d["totals"]["total_carbs_g"] for d in days) / 7, 1)
    avg_fat = round(sum(d["totals"]["total_fat_g"] for d in days) / 7, 1)

    return {
        "type": "weekly_summary",
        "start_date": start_str,
        "end_date": end_date,
        "averages": {
            "calories": avg_calories,
            "protein_g": avg_protein,
            "total_carbs_g": avg_carbs,
            "total_fat_g": avg_fat,
        },
        "days": days,
    }


def get_progress(days: int = 30):
    end = datetime.strptime("2025-04-28", "%Y-%m-%d")
    start = end - timedelta(days=days - 1)

    daily_data = []
    current = start
    while current <= end:
        d = current.strftime("%Y-%m-%d")
        entries = [e for e in _diary_entries_store if e["date"] == d]
        totals = _compute_totals(entries) if entries else _empty_totals()

        exercises = [ex for ex in _exercise_log_store if ex["date"] == d]
        exercise_cals = sum(ex["calories_burned"] for ex in exercises)

        daily_data.append({
            "date": d,
            "calories_consumed": totals["calories"],
            "calories_burned": exercise_cals,
            "net_calories": round(totals["calories"] - exercise_cals, 1),
            "protein_g": totals["protein_g"],
            "total_carbs_g": totals["total_carbs_g"],
            "total_fat_g": totals["total_fat_g"],
        })
        current += timedelta(days=1)

    return {
        "type": "progress",
        "period_days": days,
        "calorie_goal": _user_profile_store["daily_calorie_goal"],
        "results": daily_data,
    }


# ---------------------------------------------------------------------------
# Exercise Types (Database)
# ---------------------------------------------------------------------------

def list_exercise_types(category: str = None, limit: int = 25, offset: int = 0):
    results = list(_exercise_types_store)
    if category:
        results = [e for e in results if e["category"].lower() == category.lower()]

    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "exercise_types",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_exercise_type(exercise_type_id: int):
    for e in _exercise_types_store:
        if e["exercise_type_id"] == exercise_type_id:
            return {"type": "exercise_type", "exercise_type": e}
    return {"error": f"Exercise type {exercise_type_id} not found"}


# ---------------------------------------------------------------------------
# Exercise Log
# ---------------------------------------------------------------------------

def list_exercises(start_date: str = None, end_date: str = None, limit: int = 25, offset: int = 0):
    results = list(_exercise_log_store)
    if start_date:
        results = [e for e in results if e["date"] >= start_date]
    if end_date:
        results = [e for e in results if e["date"] <= end_date]

    results = sorted(results, key=lambda x: x["date"], reverse=True)
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "exercises",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_exercise(exercise_id: int):
    for e in _exercise_log_store:
        if e["exercise_id"] == exercise_id:
            return {"type": "exercise", "exercise": e}
    return {"error": f"Exercise {exercise_id} not found"}


def create_exercise(data: dict):
    global _next_exercise_id
    required = ["date", "exercise_type_id", "duration_minutes", "calories_burned"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    exercise_type_id = int(data["exercise_type_id"])
    ex_type = None
    for e in _exercise_types_store:
        if e["exercise_type_id"] == exercise_type_id:
            ex_type = e
            break

    if not ex_type:
        return {"error": f"Exercise type {exercise_type_id} not found"}

    exercise = {
        "exercise_id": _next_exercise_id,
        "date": data["date"],
        "exercise_type_id": exercise_type_id,
        "exercise_name": ex_type["exercise_name"],
        "duration_minutes": int(data["duration_minutes"]),
        "calories_burned": int(data["calories_burned"]),
        "notes": data.get("notes", ""),
    }
    _exercise_log_store.append(exercise)
    _next_exercise_id += 1
    return {"type": "exercise", "exercise": exercise}


# ---------------------------------------------------------------------------
# Weight Log
# ---------------------------------------------------------------------------

def list_weight_entries(limit: int = 25, offset: int = 0):
    results = sorted(_weight_log_store, key=lambda x: x["date"], reverse=True)
    total = len(results)
    page_results = results[offset: offset + limit]
    return {
        "type": "weight_entries",
        "count": len(page_results),
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": page_results,
    }


def get_weight_entry(weight_id: int):
    for w in _weight_log_store:
        if w["weight_id"] == weight_id:
            return {"type": "weight_entry", "weight_entry": w}
    return {"error": f"Weight entry {weight_id} not found"}


def create_weight_entry(data: dict):
    global _next_weight_id
    required = ["date", "weight_lbs"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    entry = {
        "weight_id": _next_weight_id,
        "date": data["date"],
        "weight_lbs": float(data["weight_lbs"]),
        "notes": data.get("notes", ""),
    }
    _weight_log_store.append(entry)
    _next_weight_id += 1
    return {"type": "weight_entry", "weight_entry": entry}


# ---------------------------------------------------------------------------
# Water Intake
# ---------------------------------------------------------------------------

def get_water(date: str):
    for w in _water_log_store:
        if w["date"] == date:
            return {"type": "water", "water": w}
    return {"error": f"Water entry for {date} not found"}


def create_water(data: dict):
    global _next_water_id
    required = ["date", "cups"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    for w in _water_log_store:
        if w["date"] == data["date"]:
            return {"error": f"Water entry for {data['date']} already exists. Use PUT to update."}

    entry = {
        "water_id": _next_water_id,
        "date": data["date"],
        "cups": int(data["cups"]),
        "notes": data.get("notes", ""),
    }
    _water_log_store.append(entry)
    _next_water_id += 1
    return {"type": "water", "water": entry}


def update_water(date: str, data: dict):
    for i, w in enumerate(_water_log_store):
        if w["date"] == date:
            if "cups" in data:
                _water_log_store[i]["cups"] = int(data["cups"])
            if "notes" in data:
                _water_log_store[i]["notes"] = data["notes"]
            return {"type": "water", "water": _water_log_store[i]}
    return {"error": f"Water entry for {date} not found"}
