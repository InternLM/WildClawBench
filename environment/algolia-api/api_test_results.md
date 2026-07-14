# Algolia Mock API — Test Results

Base URL: `http://localhost:8067` (in docker-compose: `http://algolia-api:8067`)

## Endpoints covered

| Method | Path                                  | Status  |
|--------|---------------------------------------|---------|
| GET    | /health                               | 200     |
| GET    | /1/indexes                            | 200     |
| POST   | /1/indexes/{index}/query              | 200/404 |
| GET    | /1/indexes/{index}/{objectID}         | 200/404 |
| POST   | /1/indexes/{index}                    | 201/400 |
| PUT    | /1/indexes/{index}/{objectID}         | 200/404 |
| DELETE | /1/indexes/{index}/{objectID}         | 200/404 |
| GET    | /1/indexes/{index}/settings           | 200/404 |

## Seed data summary

- Indices: 2 (`products` with 8 records, `docs` with 6 records)
- Products carry name/description/category/brand/price/in_stock
- Docs carry title/body/section/tags
- Per-index settings (searchableAttributes, attributesForFaceting, ranking)

## Notes

- `POST /query` body accepts `query`, optional `filters`, `hitsPerPage`, `page`
  and returns `{hits, nbHits, page, nbPages, hitsPerPage}`.
- `query` performs a case-insensitive substring match across all string fields.
- `filters` supports simple `attr:value` equality, optionally AND-joined
  (e.g. `category:displays AND brand:Nimbus`).
- `POST /1/indexes/{index}` auto-generates an `objectID` if none is supplied and
  auto-creates the index on first write. `PUT` creates the object if missing.
- Mutations are held in process memory and reset on container restart.
