"""FastAPI server wrapping tmdb_data module as REST endpoints.

Implements a subset of The Movie Database (TMDB) v3 API. Base path: /3
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

import tmdb_data
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

app = FastAPI(title="TMDB API (Mock)", version="3")
install_tracker(app)
install_admin_plane(app, store=tmdb_data._store)
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Search ---

@app.get("/3/search/movie")
def search_movie(query: str = Query(...), page: int = Query(1, ge=1)):
    return tmdb_data.search_movie(query, page=page)


# --- Movies ---

@app.get("/3/movie/popular")
def movie_popular(page: int = Query(1, ge=1)):
    return tmdb_data.movie_popular(page=page)


@app.get("/3/movie/{movie_id}")
def get_movie(movie_id: int):
    result = tmdb_data.get_movie(movie_id)
    if isinstance(result, dict) and result.get("success") is False:
        return JSONResponse(status_code=404, content=result)
    return result


@app.get("/3/movie/{movie_id}/credits")
def movie_credits(movie_id: int):
    result = tmdb_data.movie_credits(movie_id)
    if isinstance(result, dict) and result.get("success") is False:
        return JSONResponse(status_code=404, content=result)
    return result


# --- TV ---

@app.get("/3/tv/{tv_id}")
def get_tv(tv_id: int):
    result = tmdb_data.get_tv(tv_id)
    if isinstance(result, dict) and result.get("success") is False:
        return JSONResponse(status_code=404, content=result)
    return result


# --- Genres ---

@app.get("/3/genre/movie/list")
def genre_movie_list():
    return tmdb_data.genre_movie_list()


# --- Trending ---

@app.get("/3/trending/all/week")
def trending_all_week(page: int = Query(1, ge=1)):
    return tmdb_data.trending_all_week(page=page)
