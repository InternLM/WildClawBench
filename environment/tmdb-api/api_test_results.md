# TMDB Mock API — Test Results

Base URL: `http://localhost:8059` (in docker-compose: `http://tmdb-api:8059`)

## Endpoints covered

| Method | Path                          | Status |
|--------|-------------------------------|--------|
| GET    | /health                       | 200    |
| GET    | /3/search/movie               | 200    |
| GET    | /3/movie/popular              | 200    |
| GET    | /3/movie/{movie_id}           | 200/404 |
| GET    | /3/movie/{movie_id}/credits   | 200/404 |
| GET    | /3/tv/{tv_id}                 | 200/404 |
| GET    | /3/genre/movie/list           | 200    |
| GET    | /3/trending/all/week          | 200    |

## Seed data summary

- Movies: 10 (id 101-110) with overview, release_date, vote_average/count, genre_ids, popularity.
- People: 8 (cast + crew) referenced by credits.
- Credits: 16 rows linking people to 5 movies (cast with character/order, crew with job).
- TV shows: 2 (id 201-202) with seasons/episodes counts.
- Genres: 10 (TMDB-style ids, e.g. 28 Action, 18 Drama, 878 Science Fiction).

## Notes

- List endpoints use TMDB paging envelope `{page, results, total_pages, total_results}` (20/page).
- `genre_ids` are stored as integer arrays; `get_movie`/`get_tv` also expand them into a `genres` array.
- `movie/popular` and `trending/all/week` sort by `popularity` descending; trending mixes movie + tv
  (each item carries a `media_type`).
- Not-found responses use TMDB-style `{success: false, status_code: 34, ...}`.
- Read-only mock; no mutations.
