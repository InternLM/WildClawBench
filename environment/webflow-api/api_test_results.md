# Webflow Data Mock API — Test Results

Base URL: `http://localhost:8100` (in docker-compose: `http://webflow-api:8100`)

## Endpoints covered

| Method | Path                                          | Status  |
|--------|-----------------------------------------------|---------|
| GET    | /health                                       | 200     |
| GET    | /v2/sites                                      | 200     |
| GET    | /v2/sites/{site_id}                            | 200/404 |
| GET    | /v2/sites/{site_id}/collections               | 200/404 |
| GET    | /v2/collections/{collection_id}/items         | 200/404 |
| POST   | /v2/collections/{collection_id}/items         | 202/404 |

## Seed data summary

- Sites: 4 (Northwind Studio, Acme Docs, Lumen Bakery, Trailhead Outdoors) with
  workspace, time zone, preview URL, custom domains, created/published dates.
- Collections: 5 across the sites (Blog Posts, Authors, Help Articles, Menu
  Items, Products).
- Items: 8 CMS items spread over the collections (name, slug, draft/archived
  flags, summary), dated 2026-05.

## Notes

- Mirrors the Webflow Data API v2; all paths are under `/v2`.
- List sites/collections/items return Webflow's wrapper objects (`sites`,
  `collections`, `items`); item listings include a `pagination` block and accept
  `limit`/`offset` query params.
- Items expose a `fieldData` object (`name`, `slug`, `summary`, plus any extra
  fields supplied on create).
- `POST /v2/collections/{id}/items` creates an item from a JSON body
  `{"fieldData": {...}, "isDraft": bool, "isArchived": bool}` and returns 202
  (Accepted) like the real API; missing slug is derived from the name.
- Unknown site or collection ids return a 404 with an `error` message.
- Mutations are held in process memory and reset on container restart.
