# Documentation Faithfulness Check

## Sources Consulted
- Official MFP API v2 documentation: https://myfitnesspalapi.com/docs/
- Official Nutritional Contents data structure: https://myfitnesspalapi.com/docs/appendix-data-structures-nutritional-contents
- Official Collection Request docs: https://myfitnesspalapi.com/docs/collection-requests/
- python-myfitnesspal library (reverse-engineered): https://github.com/coddingtonbear/python-myfitnesspal
- python-myfitnesspal types: https://python-myfitnesspal.readthedocs.io/en/latest/api/types.html

## Key Design Decision

MyFitnessPal's official API (v2) is partner-access only (OAuth2 required). The task prompt explicitly states:
> "MyFitnessPal doesn't have a well-documented public REST API, so model endpoints after the data structures the app exposes"
> "Endpoint path style: Use RESTful paths like /v1/user/diary/{date}"
> "Simplify auth (no OAuth) but keep the domain model authentic"

Therefore our paths are intentionally custom REST (v1), while domain entities and field semantics match MFP's data model.

## Nutritional Field Names Comparison

| Official MFP Field | Our Field | Match? | Notes |
|---|---|---|---|
| `energy` (measured value) | `calories` (flat number) | ~ | Simplified; MFP uses `{"unit":"calories","value":N}` but we flatten to a number. Acceptable per task requirements. |
| `fat` | `total_fat_g` | ~ | We add `_g` suffix for clarity. MFP internally uses `fat` but displays "Total Fat (g)". |
| `saturated_fat` | `saturated_fat_g` | ✓ | Same name + unit suffix. |
| `carbohydrates` | `total_carbs_g` | ~ | MFP uses `carbohydrates`; we use the common abbreviation "carbs". Display in app says "Total Carbohydrates". |
| `fiber` | `dietary_fiber_g` | ~ | MFP uses `fiber`; app displays "Dietary Fiber". Both are standard. |
| `sugar` | `sugars_g` | ✓ | MFP uses `sugar`; FDA label uses "Total Sugars". Equivalent. |
| `protein` | `protein_g` | ✓ | Same name + unit suffix. |
| `cholesterol` | `cholesterol_mg` | ✓ | Same name + unit suffix. |
| `sodium` | `sodium_mg` | ✓ | Same name + unit suffix. |
| `potassium` | `potassium_mg` | ✓ | Same name + unit suffix. |

## Diary Structure Comparison

| Aspect | Official MFP | Our Implementation | Match? |
|---|---|---|---|
| Diary organized by date | ✓ `/diary?date=2014-07-15` | ✓ `GET /v1/user/diary/{date}` | ✓ |
| Meal slots | Breakfast, Lunch, Dinner, Snacks | Breakfast, Lunch, Dinner, Snacks | ✓ |
| Field name for meal | `diary_meal` | `meal` | ~ (simplified but equivalent) |
| Food entries per meal | Multiple entries per meal | Multiple entries per meal | ✓ |
| Each entry has nutritional data | ✓ `nutritional_contents` object | ✓ flat fields on entry | ~ (flattened for simplicity) |

## Endpoint Path Comparison

| # | Endpoint | Our Path | Official MFP v2 Path | Match? | Notes |
|---|---|---|---|---|---|
| 1 | Health check | GET /health | N/A | N/A | Mock-only endpoint |
| 2 | User profile | GET /v1/user/profile | GET /v2/users/:userId | ~ | Custom REST path per task spec |
| 3 | Update profile | PUT /v1/user/profile | PATCH /v2/users/:userId | ~ | Task says simplified |
| 4 | Get goals | GET /v1/user/goals | (embedded in user profile) | ~ | We separated goals as sub-resource |
| 5 | Update goals | PUT /v1/user/goals | PATCH /v2/users/:userId | ~ | Separated for clarity |
| 6 | Search foods | GET /v1/foods/search | (food database search via app) | ~ | No official REST endpoint for food DB |
| 7 | Get food | GET /v1/foods/{food_id} | N/A | ~ | Not in official API; modeled from app |
| 8 | Get diary | GET /v1/user/diary/{date} | GET /v2/diary?date=X | ~ | Ours uses path param vs query |
| 9 | Get diary range | GET /v1/user/diary?start_date&end_date | GET /v2/diary?date=X | ~ | Extended for range queries |
| 10 | Create diary entry | POST /v1/user/diary | POST /v2/diary | ✓ | Same concept |
| 11 | Update diary entry | PUT /v1/user/diary/{entry_id} | PATCH /v2/diary/:id | ~ | PUT vs PATCH |
| 12 | Delete diary entry | DELETE /v1/user/diary/{entry_id} | DELETE /v2/diary/:id | ✓ | Same |
| 13 | Daily totals | GET /v1/user/nutrition/{date} | (aggregated from diary) | ~ | Convenience endpoint |
| 14 | Weekly summary | GET /v1/user/nutrition/weekly/{end_date} | N/A | ~ | Convenience endpoint |
| 15 | Progress | GET /v1/user/progress | N/A | ~ | Convenience endpoint |
| 16 | Exercise types | GET /v1/exercises/types | (exercise DB in app) | ~ | Modeled from MFP exercise picker |
| 17 | Get exercise type | GET /v1/exercises/types/{id} | N/A | ~ | Detail endpoint |
| 18 | List exercises | GET /v1/user/exercises | GET /v2/exercises | ✓ | Same concept |
| 19 | Get exercise | GET /v1/user/exercises/{id} | (within exercises) | ✓ | Detail endpoint |
| 20 | Log exercise | POST /v1/user/exercises | POST /v2/exercises | ✓ | Same concept |
| 21 | List weight | GET /v1/user/weight | GET /v2/measurements | ~ | MFP uses "measurements" |
| 22 | Get weight entry | GET /v1/user/weight/{id} | (within measurements) | ~ | Same concept |
| 23 | Log weight | POST /v1/user/weight | POST /v2/measurements | ~ | MFP uses "measurements" |
| 24 | Get water | GET /v1/user/water/{date} | (tracked as diary item) | ~ | Separate resource for clarity |
| 25 | Log water | POST /v1/user/water | (via diary) | ~ | Separate resource for clarity |
| 26 | Update water | PUT /v1/user/water/{date} | (via diary) | ~ | Separate resource for clarity |

## Conclusion

**All domain entities match MFP's data model:**
- Diary organized by date → meal slots → food entries ✓
- Meal slots: Breakfast, Lunch, Dinner, Snacks ✓
- Nutritional fields match MFP's official list (with unit suffixes added for clarity) ✓
- Exercise logging with type, duration, calories burned ✓
- Weight/measurements tracking ✓
- Water intake tracking ✓

**Paths are intentionally simplified** per the task prompt directive. No changes needed — the domain model is authentic to MFP while the REST structure is custom (as specified).

**No fixes required.** Proceeding to Step 2.
