"""Data access module for the TMDB API mock service.

Mirrors a subset of The Movie Database (TMDB) v3 API: movies, TV shows,
people/credits, genres, search, popular, and trending.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent

import sys as _sys
_sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import (
    read_seed_with_ctx, get_store,
    strict_int,
    strict_float,
)

_store = get_store("tmdb-api")
_API = "tmdb-api"

_store.register("genres", primary_key="id",
                initial_loader=lambda: _coerce_genres(_load("genres.json", "genres")))
_store.register("movies", primary_key="id",
                initial_loader=lambda: _coerce_movies(_load("movies.json", "movies")))
_store.register("people", primary_key="id",
                initial_loader=lambda: _coerce_people(_load("people.json", "people")))
_store.register("credits", primary_key="_pk",
                initial_loader=lambda: [{**r, "_pk": f"{r['movie_id']}@{r['person_id']}@{r['credit_type']}"}
                                        for r in _coerce_credits(_load("credits.json", "credits"))])
_store.register("tv", primary_key="id",
                initial_loader=lambda: _coerce_tv(_load("tv.json", "tv")))


def _genres_rows():
    return _store.table("genres").rows()


def _movies_rows():
    return _store.table("movies").rows()


def _people_rows():
    return _store.table("people").rows()


def _credits_rows():
    return [{k: v for k, v in r.items() if k != "_pk"} for r in _store.table("credits").rows()]


def _tv_rows():
    return _store.table("tv").rows()



def _load(filename, table):
    return read_seed_with_ctx(DATA_DIR / filename, _API, table)


def _strip_ctx(r):
    return {k: v for k, v in r.items() if not k.startswith("__")}


def _genre_ids(s):
    return [int(x) for x in s.split(";") if x]


# ---------------------------------------------------------------------------
# Load + coerce
# ---------------------------------------------------------------------------

def _coerce_genres(rows):
    return [{"id": strict_int(r, "id"), "name": r["name"]} for r in rows]


def _coerce_movies(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "title": r["title"],
            "original_title": r["title"],
            "overview": r["overview"],
            "release_date": r["release_date"],
            "vote_average": strict_float(r, "vote_average"),
            "vote_count": strict_int(r, "vote_count"),
            "genre_ids": _genre_ids(r["genre_ids"]),
            "popularity": strict_float(r, "popularity"),
            "original_language": r["original_language"],
            "media_type": "movie",
            "adult": False,
        })
    return out


def _coerce_people(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "name": r["name"],
            "known_for_department": r["known_for_department"],
            "gender": strict_int(r, "gender"),
            "popularity": strict_float(r, "popularity"),
        })
    return out


def _coerce_credits(rows):
    out = []
    for r in rows:
        out.append({
            "movie_id": strict_int(r, "movie_id"),
            "person_id": strict_int(r, "person_id"),
            "credit_type": r["credit_type"],
            "character": r["character"],
            "job": r["job"],
            "order": strict_int(r, "order"),
        })
    return out


def _coerce_tv(rows):
    out = []
    for r in rows:
        out.append({
            "id": strict_int(r, "id"),
            "name": r["name"],
            "original_name": r["name"],
            "overview": r["overview"],
            "first_air_date": r["first_air_date"],
            "vote_average": strict_float(r, "vote_average"),
            "vote_count": strict_int(r, "vote_count"),
            "genre_ids": _genre_ids(r["genre_ids"]),
            "popularity": strict_float(r, "popularity"),
            "number_of_seasons": strict_int(r, "number_of_seasons"),
            "number_of_episodes": strict_int(r, "number_of_episodes"),
            "media_type": "tv",
        })
    return out












_people_by_id = {p["id"]: p for p in _people_rows()}


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
    matches = [m for m in _movies_rows() if q in m["title"].lower()]
    matches.sort(key=lambda m: m["popularity"], reverse=True)
    return _page(matches, page=page)


# ---------------------------------------------------------------------------
# Movies
# ---------------------------------------------------------------------------

def get_movie(movie_id):
    m = next((x for x in _movies_rows() if x["id"] == movie_id), None)
    if not m:
        return {"success": False, "status_code": 34, "status_message": "The resource you requested could not be found.", "error": f"movie {movie_id} not found"}
    genre_lookup = {g["id"]: g["name"] for g in _genres_rows()}
    out = dict(m)
    out["genres"] = [{"id": gid, "name": genre_lookup.get(gid, "Unknown")} for gid in m["genre_ids"]]
    return out


def movie_credits(movie_id):
    if not any(x["id"] == movie_id for x in _movies_rows()):
        return {"success": False, "status_code": 34, "error": f"movie {movie_id} not found"}
    cast, crew = [], []
    for c in _credits_rows():
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
    movies = sorted(_movies_rows(), key=lambda m: m["popularity"], reverse=True)
    return _page(movies, page=page)


# ---------------------------------------------------------------------------
# TV
# ---------------------------------------------------------------------------

def get_tv(tv_id):
    t = next((x for x in _tv_rows() if x["id"] == tv_id), None)
    if not t:
        return {"success": False, "status_code": 34, "error": f"tv {tv_id} not found"}
    genre_lookup = {g["id"]: g["name"] for g in _genres_rows()}
    out = dict(t)
    out["genres"] = [{"id": gid, "name": genre_lookup.get(gid, "Unknown")} for gid in t["genre_ids"]]
    return out


# ---------------------------------------------------------------------------
# Genres
# ---------------------------------------------------------------------------

def genre_movie_list():
    return {"genres": _genres_rows()}


# ---------------------------------------------------------------------------
# Trending
# ---------------------------------------------------------------------------

def trending_all_week(page=1):
    combined = list(_movies_rows()) + list(_tv_rows())
    combined.sort(key=lambda x: x["popularity"], reverse=True)
    return _page(combined, page=page)

_store.eager_load()
