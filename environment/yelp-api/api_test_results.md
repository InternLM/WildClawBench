# Yelp Fusion Mock API — Test Results

Base URL: `http://localhost:8034` (in docker-compose: `http://yelp-api:8034`)

## Endpoints covered

| Method | Path                                   | Status  |
|--------|----------------------------------------|---------|
| GET    | /health                                | 200     |
| GET    | /v3/businesses/search                  | 200     |
| GET    | /v3/businesses/{id}                    | 200/404 |
| GET    | /v3/businesses/{id}/reviews            | 200/404 |
| GET    | /v3/categories                         | 200     |

## Seed data summary

- Businesses: 10 San Francisco spots (cafes, bakeries, restaurants, steak,
  seafood, etc.) with rating (1-5), price ($-$$$$), category, coordinates,
  review_count, and is_closed flag.
- Reviews: 10 across 4 businesses (The Grove, Tartine, House of Prime Rib,
  La Taqueria).
- Categories: 10 aliases mapped to titles and parent groups.

## Notes

- `search` filters by `term`, `location`, `categories` (comma list of aliases),
  and `price` (accepts `$`-`$$$$` symbols or numeric `1`-`4`, comma separated);
  `sort_by` supports `best_match`, `rating`, and `review_count`.
- Business lookups accept the id, which also serves as the alias.
- Responses follow Yelp Fusion shapes (`businesses`, `categories`, `reviews`,
  nested `coordinates`/`location`/`categories`).
- This service is read-only; no mutations.
