"""Data access module for MyFitnessPal API simulation."""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    strict_float,
)

_store = get_store("myfitnesspal-api")
_API = "myfitnesspal-api"



def _store_patch(_table, _row_or_pk, _updates):
    """Persist field updates to a stored row (was: in-place mutation of a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.patch(_pk, _updates)


def _store_delete(_table, _row_or_pk):
    """Persist a row deletion (was: pop/remove on a copy)."""
    _t = _store.table(_table)
    _pk = _row_or_pk.get(_t.primary_key, _row_or_pk.get("id")) if isinstance(_row_or_pk, dict) else _row_or_pk
    return _t.delete(_pk)

def _store_insert(_table, _row):
    """Persist a newly-created row into the shared store (drift/injection-safe).

    Synthesizes the table's registered primary key from the row's ``id`` field
    when the row doesn't already carry it, so creates work regardless of whether
    the table was registered with primary_key="id" or a domain-specific key.
    """
    _t = _store.table(_table)
    if _t.primary_key not in _row and "id" in _row:
        _row = {**_row, _t.primary_key: _row["id"]}
    return _t.upsert(_row)

_store.register("foods", primary_key="food_id",
                initial_loader=lambda: _coerce_foods(_load("foods.json", "foods")))
_store.register("diary_entries", primary_key="entry_id",
                initial_loader=lambda: _coerce_diary_entries(_load("diary_entries.json", "diary_entries")))
_store.register("exercise_types", primary_key="exercise_type_id",
                initial_loader=lambda: _coerce_exercise_types(_load("exercise_types.json", "exercise_types")))
_store.register("exercise_log", primary_key="exercise_id",
                initial_loader=lambda: _coerce_exercise_log(_load("exercise_log.json", "exercise_log")))
_store.register("weight_log", primary_key="weight_id",
                initial_loader=lambda: _coerce_weight_log(_load("weight_log.json", "weight_log")))
_store.register("water_log", primary_key="water_id",
                initial_loader=lambda: _coerce_water_log(_load("water_log.json", "water_log")))
_store.register_document("user_profile", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "user_profile.json", encoding="utf-8")))
_store.register_document("scenario_user_profile", initial_loader=lambda: __import__('json').load(open(DATA_DIR / "myfitnesspal_user_profile.json", encoding="utf-8")))


def _foods_rows():
    return _store.table("foods").rows()


def _diary_entries_rows():
    return _store.table("diary_entries").rows()


def _exercise_types_rows():
    return _store.table("exercise_types").rows()


def _exercise_log_rows():
    return _store.table("exercise_log").rows()


def _weight_log_rows():
    return _store.table("weight_log").rows()


def _water_log_rows():
    return _store.table("water_log").rows()


def _user_profile_doc():
    return _store.document("user_profile").get()


def get_scenario_user_profile():
    # myfitnesspal_user_profile.json wraps {"user_profile": {...}}; served verbatim.
    return _store.document("scenario_user_profile").get()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


# ---------------------------------------------------------------------------
# Load and coerce data
# ---------------------------------------------------------------------------

def _coerce_foods(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "food_id": strict_int(r, "food_id"),
            "calories": strict_float(r, "calories"),
            "total_fat_g": strict_float(r, "total_fat_g"),
            "saturated_fat_g": strict_float(r, "saturated_fat_g"),
            "cholesterol_mg": strict_float(r, "cholesterol_mg"),
            "sodium_mg": strict_float(r, "sodium_mg"),
            "total_carbs_g": strict_float(r, "total_carbs_g"),
            "dietary_fiber_g": strict_float(r, "dietary_fiber_g"),
            "sugars_g": strict_float(r, "sugars_g"),
            "protein_g": strict_float(r, "protein_g"),
            "potassium_mg": strict_float(r, "potassium_mg"),
            "is_verified": r["is_verified"].lower() == "true",
        })
    return out


def _coerce_diary_entries(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "entry_id": strict_int(r, "entry_id"),
            "food_id": strict_int(r, "food_id"),
            "servings": strict_float(r, "servings"),
            "calories": strict_float(r, "calories"),
            "total_fat_g": strict_float(r, "total_fat_g"),
            "saturated_fat_g": strict_float(r, "saturated_fat_g"),
            "cholesterol_mg": strict_float(r, "cholesterol_mg"),
            "sodium_mg": strict_float(r, "sodium_mg"),
            "total_carbs_g": strict_float(r, "total_carbs_g"),
            "dietary_fiber_g": strict_float(r, "dietary_fiber_g"),
            "sugars_g": strict_float(r, "sugars_g"),
            "protein_g": strict_float(r, "protein_g"),
        })
    return out


def _coerce_exercise_types(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "exercise_type_id": strict_int(r, "exercise_type_id"),
            "calories_per_minute_low": strict_float(r, "calories_per_minute_low"),
            "calories_per_minute_high": strict_float(r, "calories_per_minute_high"),
            "met_value": strict_float(r, "met_value"),
        })
    return out


def _coerce_exercise_log(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "exercise_id": strict_int(r, "exercise_id"),
            "exercise_type_id": strict_int(r, "exercise_type_id"),
            "duration_minutes": strict_int(r, "duration_minutes"),
            "calories_burned": strict_int(r, "calories_burned"),
        })
    return out


def _coerce_weight_log(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "weight_id": strict_int(r, "weight_id"),
            "weight_lbs": strict_float(r, "weight_lbs"),
        })
    return out


def _coerce_water_log(rows):
    out = []
    for r in rows:
        out.append({
            **_strip_ctx(r),
            "water_id": strict_int(r, "water_id"),
            "cups": strict_int(r, "cups"),
        })
    return out


# Load all data at module init







# Mutable in-memory stores







_store.eager_load()
_next_entry_id = max(e["entry_id"] for e in _diary_entries_rows()) + 1
_next_exercise_id = max(e["exercise_id"] for e in _exercise_log_rows()) + 1
_next_weight_id = max(w["weight_id"] for w in _weight_log_rows()) + 1
_next_water_id = max(w["water_id"] for w in _water_log_rows()) + 1


# ---------------------------------------------------------------------------
# User Profile
# ---------------------------------------------------------------------------

def get_user_profile():
    return {"type": "user_profile", "user_profile": _user_profile_doc()}


def update_user_profile(data: dict):
    updatable = {
        "display_name", "daily_calorie_goal", "activity_level",
        "current_weight_lbs", "goal_weight_lbs", "weekly_weight_goal_lbs",
    }
    _changes = {}
    for k, v in data.items():
        if k in updatable:
            _changes[k] = v
    profile = _store.document("user_profile").merge(_changes) if _changes else _user_profile_doc()
    return {"type": "user_profile", "user_profile": profile}


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

def get_goals():
    return {
        "type": "goals",
        "goals": {
            "daily_calorie_goal": _user_profile_doc()["daily_calorie_goal"],
            "macro_goals": _user_profile_doc()["macro_goals"],
            "nutrient_goals": _user_profile_doc()["nutrient_goals"],
            "weekly_weight_goal_lbs": _user_profile_doc()["weekly_weight_goal_lbs"],
            "goal_weight_lbs": _user_profile_doc()["goal_weight_lbs"],
        },
    }


def update_goals(data: dict):
    _doc = _store.document("user_profile")
    _v = _doc.get()
    if "daily_calorie_goal" in data:
        _v["daily_calorie_goal"] = int(data["daily_calorie_goal"])
        _v["nutrient_goals"]["calories"] = int(data["daily_calorie_goal"])
    if "macro_goals" in data:
        _v["macro_goals"].update(data["macro_goals"])
    if "nutrient_goals" in data:
        _v["nutrient_goals"].update(data["nutrient_goals"])
    if "weekly_weight_goal_lbs" in data:
        _v["weekly_weight_goal_lbs"] = float(data["weekly_weight_goal_lbs"])
    if "goal_weight_lbs" in data:
        _v["goal_weight_lbs"] = float(data["goal_weight_lbs"])
    _doc.set(_v)
    return get_goals()


# ---------------------------------------------------------------------------
# Food Database
# ---------------------------------------------------------------------------

def search_foods(q: str = None, limit: int = 25, offset: int = 0):
    results = list(_foods_rows())
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
    for f in _foods_rows():
        if f["food_id"] == food_id:
            return {"type": "food", "food": f}
    return {"error": f"Food {food_id} not found"}


# ---------------------------------------------------------------------------
# Food Diary
# ---------------------------------------------------------------------------

def get_diary(date: str, meal: str = None):
    entries = [e for e in _diary_entries_rows() if e["date"] == date]
    if meal:
        entries = [e for e in entries if e["meal"].lower() == meal.lower()]

    if not entries and not any(e["date"] == date for e in _diary_entries_rows()):
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
        e for e in _diary_entries_rows()
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
    for f in _foods_rows():
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
    _store_insert("diary_entries", entry)
    _next_entry_id += 1
    return {"type": "diary_entry", "diary_entry": entry}


def update_diary_entry(entry_id: int, data: dict):
    for entry in _diary_entries_rows():
        if entry["entry_id"] == entry_id:
            _changes = {}
            if "servings" in data:
                new_servings = float(data["servings"])
                food_id = entry["food_id"]
                food = None
                for f in _foods_rows():
                    if f["food_id"] == food_id:
                        food = f
                        break
                if food:
                    _changes["servings"] = new_servings
                    _changes["calories"] = round(food["calories"] * new_servings, 1)
                    _changes["total_fat_g"] = round(food["total_fat_g"] * new_servings, 1)
                    _changes["saturated_fat_g"] = round(food["saturated_fat_g"] * new_servings, 1)
                    _changes["cholesterol_mg"] = round(food["cholesterol_mg"] * new_servings, 1)
                    _changes["sodium_mg"] = round(food["sodium_mg"] * new_servings, 1)
                    _changes["total_carbs_g"] = round(food["total_carbs_g"] * new_servings, 1)
                    _changes["dietary_fiber_g"] = round(food["dietary_fiber_g"] * new_servings, 1)
                    _changes["sugars_g"] = round(food["sugars_g"] * new_servings, 1)
                    _changes["protein_g"] = round(food["protein_g"] * new_servings, 1)
            if "meal" in data:
                _changes["meal"] = data["meal"]
            entry.update(_changes)
            _store_patch("diary_entries", entry, _changes)
            return {"type": "diary_entry", "diary_entry": entry}
    return {"error": f"Diary entry {entry_id} not found"}


def delete_diary_entry(entry_id: int):
    for entry in _diary_entries_rows():
        if entry["entry_id"] == entry_id:
            _store_delete("diary_entries", entry)
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
    entries = [e for e in _diary_entries_rows() if e["date"] == date]
    if not entries:
        return {
            "type": "daily_totals",
            "date": date,
            "totals": _empty_totals(),
            "goal": _user_profile_doc()["nutrient_goals"],
            "remaining": _user_profile_doc()["nutrient_goals"].copy(),
        }
    totals = _compute_totals(entries)
    goal = _user_profile_doc()["nutrient_goals"]
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
        entries = [e for e in _diary_entries_rows() if e["date"] == d]
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
        entries = [e for e in _diary_entries_rows() if e["date"] == d]
        totals = _compute_totals(entries) if entries else _empty_totals()

        exercises = [ex for ex in _exercise_log_rows() if ex["date"] == d]
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
        "calorie_goal": _user_profile_doc()["daily_calorie_goal"],
        "results": daily_data,
    }


# ---------------------------------------------------------------------------
# Exercise Types (Database)
# ---------------------------------------------------------------------------

def list_exercise_types(category: str = None, limit: int = 25, offset: int = 0):
    results = list(_exercise_types_rows())
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
    for e in _exercise_types_rows():
        if e["exercise_type_id"] == exercise_type_id:
            return {"type": "exercise_type", "exercise_type": e}
    return {"error": f"Exercise type {exercise_type_id} not found"}


# ---------------------------------------------------------------------------
# Exercise Log
# ---------------------------------------------------------------------------

def list_exercises(start_date: str = None, end_date: str = None, limit: int = 25, offset: int = 0):
    results = list(_exercise_log_rows())
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
    for e in _exercise_log_rows():
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
    for e in _exercise_types_rows():
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
    _store_insert("exercise_log", exercise)
    _next_exercise_id += 1
    return {"type": "exercise", "exercise": exercise}


# ---------------------------------------------------------------------------
# Weight Log
# ---------------------------------------------------------------------------

def list_weight_entries(limit: int = 25, offset: int = 0):
    results = sorted(_weight_log_rows(), key=lambda x: x["date"], reverse=True)
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
    for w in _weight_log_rows():
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
    _store_insert("weight_log", entry)
    _next_weight_id += 1
    return {"type": "weight_entry", "weight_entry": entry}


# ---------------------------------------------------------------------------
# Water Intake
# ---------------------------------------------------------------------------

def get_water(date: str):
    for w in _water_log_rows():
        if w["date"] == date:
            return {"type": "water", "water": w}
    return {"error": f"Water entry for {date} not found"}


def create_water(data: dict):
    global _next_water_id
    required = ["date", "cups"]
    for f in required:
        if f not in data or data[f] is None:
            return {"error": f"Missing required field: {f}"}

    for w in _water_log_rows():
        if w["date"] == data["date"]:
            return {"error": f"Water entry for {data['date']} already exists. Use PUT to update."}

    entry = {
        "water_id": _next_water_id,
        "date": data["date"],
        "cups": int(data["cups"]),
        "notes": data.get("notes", ""),
    }
    _store_insert("water_log", entry)
    _next_water_id += 1
    return {"type": "water", "water": entry}


def update_water(date: str, data: dict):
    for w in _water_log_rows():
        if w["date"] == date:
            _changes = {}
            if "cups" in data:
                _changes["cups"] = int(data["cups"])
            if "notes" in data:
                _changes["notes"] = data["notes"]
            w.update(_changes)
            _store_patch("water_log", w, _changes)
            return {"type": "water", "water": w}
    return {"error": f"Water entry for {date} not found"}
