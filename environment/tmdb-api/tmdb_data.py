"""Data access module for the TMDB API mock service.

Mirrors a subset of The Movie Database (TMDB) v3 API: movies, TV shows,
people/credits, genres, search, popular, and trending.
"""

import csv
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent


def _load(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _genre_ids(s):
    return [int(x) for x in s.split(";") if x]


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_genres(rows):
    return [{"id": int(r["id"]), "name": r["name"]} for r in rows]


def _coerce_movies(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "title": r["title"],
            "original_title": r["title"],
            "overview": r["overview"],
            "release_date": r["release_date"],
            "vote_average": float(r["vote_average"]),
            "vote_count": int(r["vote_count"]),
            "genre_ids": _genre_ids(r["genre_ids"]),
            "popularity": float(r["popularity"]),
            "original_language": r["original_language"],
            "media_type": "movie",
            "adult": False,
        })
    return out


def _coerce_people(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "name": r["name"],
            "known_for_department": r["known_for_department"],
            "gender": int(r["gender"]),
            "popularity": float(r["popularity"]),
        })
    return out


def _coerce_credits(rows):
    out = []
    for r in rows:
        out.append({
            "movie_id": int(r["movie_id"]),
            "person_id": int(r["person_id"]),
            "credit_type": r["credit_type"],
            "character": r["character"],
            "job": r["job"],
            "order": int(r["order"]),
        })
    return out


def _coerce_tv(rows):
    out = []
    for r in rows:
        out.append({
            "id": int(r["id"]),
            "name": r["name"],
            "original_name": r["name"],
            "overview": r["overview"],
            "first_air_date": r["first_air_date"],
            "vote_average": float(r["vote_average"]),
            "vote_count": int(r["vote_count"]),
            "genre_ids": _genre_ids(r["genre_ids"]),
            "popularity": float(r["popularity"]),
            "number_of_seasons": int(r["number_of_seasons"]),
            "number_of_episodes": int(r["number_of_episodes"]),
            "media_type": "tv",
        })
    return out


_genres = _coerce_genres(_load("genres.csv"))
_movies = _coerce_movies(_load("movies.csv"))
_people = _coerce_people(_load("people.csv"))
_credits = _coerce_credits(_load("credits.csv"))
_tv = _coerce_tv(_load("tv.csv"))

_genres_store = deepcopy(_genres)
_movies_store = deepcopy(_movies)
_people_store = deepcopy(_people)
_credits_store = deepcopy(_credits)
_tv_store = deepcopy(_tv)

_people_by_id = {p["id"]: p for p in _people_store}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _page(results, page=1, page_size=20):
    page = max(1, page)
    start = (page - 1) * page_size
    sliced = results[start: start + page_size]
    total = len(results)
    return {
        "page": page,
        "results": sliced,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "total_results": total,
    }


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_movie(query, page=1):
    q = (query or "").lower()
    matches = [m for m in _movies_store if q in m["title"].lower()]
    matches.sort(key=lambda m: m["popularity"], reverse=True)
    return _page(matches, page=page)


# ---------------------------------------------------------------------------
# Movies
# ---------------------------------------------------------------------------

def get_movie(movie_id):
    m = next((x for x in _movies_store if x["id"] == movie_id), None)
    if not m:
        return {"success": False, "status_code": 34, "status_message": "The resource you requested could not be found.", "error": f"movie {movie_id} not found"}
    genre_lookup = {g["id"]: g["name"] for g in _genres_store}
    out = dict(m)
    out["genres"] = [{"id": gid, "name": genre_lookup.get(gid, "Unknown")} for gid in m["genre_ids"]]
    return out


def movie_credits(movie_id):
    if not any(x["id"] == movie_id for x in _movies_store):
        return {"success": False, "status_code": 34, "error": f"movie {movie_id} not found"}
    cast, crew = [], []
    for c in _credits_store:
        if c["movie_id"] != movie_id:
            continue
        person = _people_by_id.get(c["person_id"], {})
        base = {
            "id": c["person_id"],
            "name": person.get("name", "Unknown"),
            "known_for_department": person.get("known_for_department", ""),
            "popularity": person.get("popularity", 0.0),
        }
        if c["credit_type"] == "cast":
            cast.append({**base, "character": c["character"], "order": c["order"]})
        else:
            crew.append({**base, "job": c["job"], "department": person.get("known_for_department", "")})
    cast.sort(key=lambda c: c["order"])
    return {"id": movie_id, "cast": cast, "crew": crew}


def movie_popular(page=1):
    movies = sorted(_movies_store, key=lambda m: m["popularity"], reverse=True)
    return _page(movies, page=page)


# ---------------------------------------------------------------------------
# TV
# ---------------------------------------------------------------------------

def get_tv(tv_id):
    t = next((x for x in _tv_store if x["id"] == tv_id), None)
    if not t:
        return {"success": False, "status_code": 34, "error": f"tv {tv_id} not found"}
    genre_lookup = {g["id"]: g["name"] for g in _genres_store}
    out = dict(t)
    out["genres"] = [{"id": gid, "name": genre_lookup.get(gid, "Unknown")} for gid in t["genre_ids"]]
    return out


# ---------------------------------------------------------------------------
# Genres
# ---------------------------------------------------------------------------

def genre_movie_list():
    return {"genres": _genres_store}


# ---------------------------------------------------------------------------
# Trending
# ---------------------------------------------------------------------------

def trending_all_week(page=1):
    combined = list(_movies_store) + list(_tv_store)
    combined.sort(key=lambda x: x["popularity"], reverse=True)
    return _page(combined, page=page)
