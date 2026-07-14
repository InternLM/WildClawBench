# Contentful Mock API — Test Results

Base URL: `http://localhost:8066` (in docker-compose: `http://contentful-api:8066`)

## Endpoints covered

| Method | Path                                                            | Status  |
|--------|-----------------------------------------------------------------|---------|
| GET    | /health                                                         | 200     |
| GET    | /spaces/{space_id}                                              | 200     |
| GET    | /spaces/{space_id}/environments/{env_id}/content_types          | 200     |
| GET    | /spaces/{space_id}/environments/{env_id}/content_types/{id}     | 200/404 |
| GET    | /spaces/{space_id}/environments/{env_id}/entries                | 200     |
| GET    | /spaces/{space_id}/environments/{env_id}/entries/{id}           | 200/404 |
| POST   | /spaces/{space_id}/environments/{env_id}/entries                | 201/400 |
| PUT    | /spaces/{space_id}/environments/{env_id}/entries/{id}           | 200/404 |
| DELETE | /spaces/{space_id}/environments/{env_id}/entries/{id}           | 200/404 |
| GET    | /spaces/{space_id}/environments/{env_id}/assets                 | 200     |
| GET    | /spaces/{space_id}/environments/{env_id}/assets/{id}            | 200/404 |

## Seed data summary

- Space: `space-orbit-cms` (Orbit Labs CMS), default environment `master`
- Content types: 3 (blogPost, author, category)
- Entries: 7 (2 authors, 2 categories, 3 blog posts incl. 1 draft) linking
  authors and assets via `sys` Link references
- Assets: 4 (hero images + author headshots)

## Notes

- Objects use a Contentful-style `sys` envelope plus a `fields` payload.
- `GET /entries` supports `content_type=` filtering, simple `fields.X=value`
  equality, and `limit`/`skip` pagination; the response is an `Array` collection
  with `total`, `skip`, `limit`.
- Mutations are held in process memory and reset on container restart.
