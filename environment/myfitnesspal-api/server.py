"""FastAPI server wrapping myfitnesspal_data module as REST endpoints."""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

import myfitnesspal_data
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError as _shared_plane_err:  # standalone run without the shared module on sys.path
    import logging as _logging
    _logging.error("SHARED PLANE MISSING - audit + admin disabled: %s", _shared_plane_err)
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="MyFitnessPal API (Mock)", version="1.0.0")
install_tracker(app)
install_admin_plane(app, store=myfitnesspal_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- User Profile ---

@app.get("/v1/user/profile")
def get_user_profile():
    return myfitnesspal_data.get_user_profile()


@app.get("/v1/user/scenario-profile")
def get_scenario_user_profile():
    return myfitnesspal_data.get_scenario_user_profile()


class ProfileUpdateBody(BaseModel):
    display_name: Optional[str] = None
    daily_calorie_goal: Optional[int] = None
    activity_level: Optional[str] = None
    current_weight_lbs: Optional[float] = None
    goal_weight_lbs: Optional[float] = None
    weekly_weight_goal_lbs: Optional[float] = None


@app.put("/v1/user/profile")
def update_user_profile(body: ProfileUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = myfitnesspal_data.update_user_profile(data)
    return result


# --- Goals ---

@app.get("/v1/user/goals")
def get_goals():
    return myfitnesspal_data.get_goals()


class MacroGoalsBody(BaseModel):
    carbs_pct: Optional[int] = None
    fat_pct: Optional[int] = None
    protein_pct: Optional[int] = None


class GoalsUpdateBody(BaseModel):
    daily_calorie_goal: Optional[int] = None
    macro_goals: Optional[MacroGoalsBody] = None
    goal_weight_lbs: Optional[float] = None
    weekly_weight_goal_lbs: Optional[float] = None


@app.put("/v1/user/goals")
def update_goals(body: GoalsUpdateBody):
    data = {}
    if body.daily_calorie_goal is not None:
        data["daily_calorie_goal"] = body.daily_calorie_goal
    if body.macro_goals is not None:
        data["macro_goals"] = {k: v for k, v in body.macro_goals.model_dump().items() if v is not None}
    if body.goal_weight_lbs is not None:
        data["goal_weight_lbs"] = body.goal_weight_lbs
    if body.weekly_weight_goal_lbs is not None:
        data["weekly_weight_goal_lbs"] = body.weekly_weight_goal_lbs
    result = myfitnesspal_data.update_goals(data)
    return result


# --- Food Database ---

@app.get("/v1/foods/search")
def search_foods(
    q: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return myfitnesspal_data.search_foods(q=q, limit=limit, offset=offset)


@app.get("/v1/foods/{food_id}")
def get_food(food_id: int):
    result = myfitnesspal_data.get_food(food_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Food Diary ---

@app.get("/v1/user/diary/{date}")
def get_diary(
    date: str,
    meal: Optional[str] = Query(default=None),
):
    return myfitnesspal_data.get_diary(date=date, meal=meal)


@app.get("/v1/user/diary")
def get_diary_range(
    start_date: str = Query(...),
    end_date: str = Query(...),
):
    return myfitnesspal_data.get_diary_range(start_date=start_date, end_date=end_date)


class DiaryEntryCreateBody(BaseModel):
    date: str
    meal: str
    food_id: int
    servings: float


@app.post("/v1/user/diary", status_code=201)
def create_diary_entry(body: DiaryEntryCreateBody):
    result = myfitnesspal_data.create_diary_entry(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class DiaryEntryUpdateBody(BaseModel):
    servings: Optional[float] = None
    meal: Optional[str] = None


@app.put("/v1/user/diary/{entry_id}")
def update_diary_entry(entry_id: int, body: DiaryEntryUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = myfitnesspal_data.update_diary_entry(entry_id, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


@app.delete("/v1/user/diary/{entry_id}")
def delete_diary_entry(entry_id: int):
    result = myfitnesspal_data.delete_diary_entry(entry_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Nutrition Summary ---

@app.get("/v1/user/nutrition/{date}")
def get_daily_totals(date: str):
    return myfitnesspal_data.get_daily_totals(date)


@app.get("/v1/user/nutrition/weekly/{end_date}")
def get_weekly_summary(end_date: str):
    try:
        return myfitnesspal_data.get_weekly_summary(end_date)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})


@app.get("/v1/user/progress")
def get_progress(
    days: int = Query(default=30, ge=1, le=90),
):
    return myfitnesspal_data.get_progress(days=days)


# --- Exercise Types ---

@app.get("/v1/exercises/types")
def list_exercise_types(
    category: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return myfitnesspal_data.list_exercise_types(category=category, limit=limit, offset=offset)


@app.get("/v1/exercises/types/{exercise_type_id}")
def get_exercise_type(exercise_type_id: int):
    result = myfitnesspal_data.get_exercise_type(exercise_type_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Exercise Log ---

@app.get("/v1/user/exercises")
def list_exercises(
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return myfitnesspal_data.list_exercises(
        start_date=start_date, end_date=end_date, limit=limit, offset=offset,
    )


@app.get("/v1/user/exercises/{exercise_id}")
def get_exercise(exercise_id: int):
    result = myfitnesspal_data.get_exercise(exercise_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class ExerciseCreateBody(BaseModel):
    date: str
    exercise_type_id: int
    duration_minutes: int
    calories_burned: int
    notes: Optional[str] = None


@app.post("/v1/user/exercises", status_code=201)
def create_exercise(body: ExerciseCreateBody):
    result = myfitnesspal_data.create_exercise(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Weight Log ---

@app.get("/v1/user/weight")
def list_weight_entries(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return myfitnesspal_data.list_weight_entries(limit=limit, offset=offset)


@app.get("/v1/user/weight/{weight_id}")
def get_weight_entry(weight_id: int):
    result = myfitnesspal_data.get_weight_entry(weight_id)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class WeightCreateBody(BaseModel):
    date: str
    weight_lbs: float
    notes: Optional[str] = None


@app.post("/v1/user/weight", status_code=201)
def create_weight_entry(body: WeightCreateBody):
    result = myfitnesspal_data.create_weight_entry(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


# --- Water Intake ---

@app.get("/v1/user/water/{date}")
def get_water(date: str):
    result = myfitnesspal_data.get_water(date)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result


class WaterCreateBody(BaseModel):
    date: str
    cups: int
    notes: Optional[str] = None


@app.post("/v1/user/water", status_code=201)
def create_water(body: WaterCreateBody):
    result = myfitnesspal_data.create_water(body.model_dump())
    if "error" in result:
        return JSONResponse(status_code=400, content=result)
    return result


class WaterUpdateBody(BaseModel):
    cups: Optional[int] = None
    notes: Optional[str] = None


@app.put("/v1/user/water/{date}")
def update_water(date: str, body: WaterUpdateBody):
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    result = myfitnesspal_data.update_water(date, data)
    if "error" in result:
        return JSONResponse(status_code=404, content=result)
    return result
